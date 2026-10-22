"""Code harvest for lockstep:learn: token values and component facts from a repository.

Reads files only, like scan_repo.py, and starts from the stack.json that scan_repo wrote. It
writes code.json:

  tokens       every token the token sources define, with its value per theme, resolved to
               plain data (colours as #rrggbb[aa], lengths as px numbers, shadows as
               "x y blur spread #colour"), its kind, where it's defined, and how often the
               rest of the code uses it
  typography   type tokens grouped into styles (size, weight, line height, letter spacing,
               case), when they're defined as related variables (heading-6-size, heading-6-weight)
  themes       the theme names the tokens are scoped to
  components   stack.json's components plus facts from their styles: text-transform, the
               tokens they use and colours they hard-code

Usage:
  python3 harvest_code.py <repo> --stack <folder>/stack.json --out <folder>/code.json
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from scan_repo import Repo, matching, read, strip_comments  # noqa: E402

DEFAULT_THEME = "default"
NAMED_COLORS = {"white": "#ffffff", "black": "#000000", "transparent": "#00000000"}


# --- values -----------------------------------------------------------------------------
def _h(n):
    return format(max(0, min(255, round(n))), "02x")


def color(v):
    """CSS colour -> #rrggbb or #rrggbbaa, else None."""
    v = v.strip().lower()
    if v in NAMED_COLORS:
        return NAMED_COLORS[v]
    m = re.fullmatch(r"#([0-9a-f]{3,8})", v)
    if m:
        x = m.group(1)
        if len(x) in (3, 4):
            x = "".join(c * 2 for c in x)
        if len(x) == 8 and x.endswith("ff"):
            x = x[:6]
        return "#" + x if len(x) in (6, 8) else None
    m = re.fullmatch(r"rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)(?:\s*[,/]\s*([\d.]+%?))?\s*\)", v)
    if m:
        r, g, b = (float(x) for x in m.groups()[:3])
        a = m.group(4)
        alpha = 1.0 if a is None else (float(a[:-1]) / 100 if a.endswith("%") else float(a))
        return "#" + _h(r) + _h(g) + _h(b) + ("" if alpha >= 0.999 else _h(alpha * 255))
    return None


def length(v):
    v = v.strip().lower()
    m = re.fullmatch(r"(-?[\d.]+)(px|rem|em)?", v)
    if not m:
        return None
    n = float(m.group(1)) * (16 if m.group(2) in ("rem", "em") else 1)
    return int(n) if n.is_integer() else round(n, 3)


def shadow(v):
    parts = []
    for one in re.split(r",(?![^(]*\))", v):
        m = re.fullmatch(r"\s*(inset\s+)?(-?[\d.]+(?:px)?)\s+(-?[\d.]+(?:px)?)\s+([\d.]+(?:px)?)(?:\s+(-?[\d.]+(?:px)?))?\s+(.+?)\s*", one)
        if not m:
            return None
        c = color(m.group(6))
        if not c:
            return None
        nums = [length(x) for x in m.group(2, 3, 4)] + [length(m.group(5)) if m.group(5) else 0]
        parts.append(("inset " if m.group(1) else "") + " ".join(str(x) for x in nums) + " " + c)
    return ", ".join(parts) if parts else None


def normalize(v):
    """(kind of value, value)."""
    v = v.strip().rstrip(";").strip()
    c = color(v)
    if c:
        return "color", c
    n = length(v)
    if n is not None:
        return "number", n
    s = shadow(v)
    if s:
        return "shadow", s
    return "text", v.strip("'\"")


NAME_KINDS = [  # first match wins; checked against the token's name words
    ("effect", {"shadow", "elevation"}), ("radius", {"radius", "rounded", "corner"}),
    ("lineHeight", {"line-height", "lineheight", "leading"}), ("letterSpacing", {"letter-spacing", "tracking"}),
    ("fontWeight", {"weight"}), ("fontSize", {"font-size", "fontsize"}), ("fontFamily", {"font-family", "family"}),
    ("stroke", {"border-width", "stroke"}), ("spacing", {"space", "spacing", "gap", "padding", "margin", "gutter"}),
]
TYPE_PARTS = {"size": "fontSize", "weight": "fontWeight", "line-height": "lineHeight", "spacing": "letterSpacing",
              "case": "textCase", "family": "fontFamily", "transform": "textCase"}


def kind_of(name, vkind, value):
    if vkind == "color":
        return "color"
    if vkind == "shadow":
        return "effect"
    n = name.lower()
    for kind, words in NAME_KINDS:
        if any(w in n for w in words):
            if kind == "stroke" and vkind != "number":
                continue
            return kind
    if re.search(r"(^|-)border(-|$)", n) and vkind == "number":
        return "stroke"
    if re.search(r"(^|-)size$", n):
        return "fontSize" if vkind == "number" else "size"
    return "number" if vkind == "number" else "text"


# --- sources ----------------------------------------------------------------------------
def theme_of(selector):
    s = selector.strip()
    m = re.search(r"theme--?([\w-]+)", s) or re.search(r"\[data-(?:theme|mode|color-scheme)=['\"]?([\w-]+)", s)
    if m:
        return m.group(1)
    if re.fullmatch(r"\.?(dark|light)(-theme|-mode)?", s.split()[-1] if s else ""):
        return s.split()[-1].lstrip(".")
    if s in (":root", "html", ":host", "") or s.startswith(":root"):
        return DEFAULT_THEME
    return None


def css_blocks(text):
    """Yield (selector, body) for each innermost rule, tracking nesting so SCSS works too."""
    text = strip_comments(text)
    stack, i, start = [], 0, 0
    while i < len(text):
        c = text[i]
        if c == "{":
            sel = text[start:i].strip().split(";")[-1].strip()
            stack.append((sel, i + 1))
            start = i + 1
        elif c == "}":
            if stack:
                sel, b = stack.pop()
                body = text[b:i]
                yield " ".join(s for s, _ in stack) + (" " if stack else "") + sel, re.sub(r"\{[^{}]*\}", "", body)
            start = i + 1
        elif c == ";":
            start = i + 1
        i += 1


def harvest_tokens(repo, stack):
    tokens = {}  # name -> {defs: {theme: raw}, file}
    order = []
    files = sorted({t["file"] for t in stack["tokens"]})
    for f in files:
        text = read(repo.root / f)
        if not text:
            continue
        # CSS custom properties, per theme scope
        for sel, body in css_blocks(text):
            props = re.findall(r"(?m)(?:^|;)\s*(--[\w-]+)\s*:\s*([^;]+)", body)
            if not props:
                continue
            theme = theme_of(sel)
            if theme is None:
                continue  # a component-scoped override, not a token
            for name, raw in props:
                t = tokens.setdefault(name, {"defs": {}, "file": f, "syntax": "css"})
                t["defs"][theme] = raw.strip()
                if name not in order:
                    order.append(name)
        # Sass and Less variables at the top level
        depth_free = re.sub(r"\{[^{}]*\}", "", re.sub(r"\{[^{}]*\{[^{}]*\}[^{}]*\}", "", strip_comments(text)))
        for sigil, name, raw in re.findall(r"(?m)^\s*([$@])([\w-]+)\s*:\s*([^;]+);", depth_free):
            if raw.strip().startswith("("):
                continue  # a map
            key = sigil + name
            tokens.setdefault(key, {"defs": {}, "file": f, "syntax": "scss" if sigil == "$" else "less"})["defs"][DEFAULT_THEME] = raw.split("!")[0].strip()
            if key not in order:
                order.append(key)
        # Theme objects: colours inside `const <theme> ... = { ... colors: { k: 'v' } }`
        for m in re.finditer(r"const\s+(\w+)\s*(?::\s*\w+)?\s*=\s*\{", text):
            b = m.end() - 1
            body = text[b + 1:matching(text, b) - 1]
            cm = re.search(r"\b(colors|palette)\s*:\s*\{", body)
            if not cm:
                continue
            cb = cm.end() - 1
            for k, v in re.findall(r"['\"]?([\w-]+)['\"]?\s*:\s*['\"]([^'\"]+)['\"]", body[cb + 1:matching(body, cb) - 1]):
                key = f"theme.{k}"
                tokens.setdefault(key, {"defs": {}, "file": f, "syntax": "theme-object"})["defs"][m.group(1)] = v
                if key not in order:
                    order.append(key)

    def resolve(name, theme, depth=0):
        t = tokens.get(name)
        if not t or depth > 8:
            return None
        raw = t["defs"].get(theme, t["defs"].get(DEFAULT_THEME, next(iter(t["defs"].values()))))
        raw = re.sub(r"var\((--[\w-]+)(?:\s*,\s*([^)]+))?\)", lambda m: resolve(m.group(1), theme, depth + 1) or (m.group(2) or m.group(0)), raw)
        raw = re.sub(r"\$([\w-]+)", lambda m: resolve("$" + m.group(1), theme, depth + 1) or m.group(0), raw)
        return raw

    themes = sorted({th for t in tokens.values() for th in t["defs"]} - {DEFAULT_THEME})
    out = []
    for name in order:
        t = tokens[name]
        scope = sorted(t["defs"]) if t["syntax"] == "theme-object" else (themes if any(th != DEFAULT_THEME for th in t["defs"]) else [DEFAULT_THEME])
        values = {}
        vkind = None
        for th in scope:
            raw = resolve(name, th)
            if raw is None:
                continue
            vk, v = normalize(raw)
            vkind = vkind or vk
            values[th] = v
        if not values:
            continue
        first = next(iter(values.values()))
        if vkind == "text" and re.search(r"famil", name):
            values = {th: v.split(",")[0].strip().strip("'\"") for th, v in values.items()}
        out.append({"name": name, "kind": kind_of(name, vkind, first), "values": values, "file": t["file"], "syntax": t["syntax"]})
    return out, themes


def typography(tokens):
    """Group `<group>-<part>` variables (heading-6-size, heading-6-weight, heading-6-spacing) into
    type styles. A group counts when it has a size plus a weight or line height; its members
    take their kind from the part, so heading-6-spacing is a letter spacing, not a space."""
    groups = defaultdict(dict)
    members = defaultdict(list)
    for t in tokens:
        m = re.fullmatch(r"(.+?)-(size|weight|line-height|spacing|case|family|transform)", t["name"].lstrip("$@-"))
        if m:
            groups[m.group(1)][TYPE_PARTS[m.group(2)]] = next(iter(t["values"].values()))
            members[m.group(1)].append((t, TYPE_PARTS[m.group(2)]))
    styles = []
    for g, parts in groups.items():
        if "fontSize" in parts and ("fontWeight" in parts or "lineHeight" in parts):
            styles.append({"name": g, **parts})
            for t, kind in members[g]:
                t["kind"] = kind
    return styles


def usage(repo, tokens):
    counts = Counter()
    names = {t["name"] for t in tokens if t["syntax"] in ("css", "scss", "less")}
    pattern = re.compile(r"var\((--[\w-]+)|(\$[\w-]+)")
    defining = {t["file"] for t in tokens}
    for p in repo.files:
        if p.suffix not in {".vue", ".svelte", ".css", ".scss", ".sass", ".less", ".ts", ".tsx", ".js", ".jsx"}:
            continue
        rel = repo.rel(p)
        text = read(p)
        for m in pattern.finditer(text):
            n = m.group(1) or m.group(2)
            if n in names and not (rel in defining and re.search(re.escape(n) + r"\s*:", text[m.start():m.start() + len(n) + 3])):
                counts[n] += 1
    return counts


def component_facts(repo, comps):
    out = []
    for c in comps:
        if c.get("page"):
            continue
        text = read(repo.root / c["file"])
        style = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", text, re.S)) or text
        style = strip_comments(style)
        raw = Counter(x for x in (color(m) for m in re.findall(r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)", style)) if x)
        families = {f.split(",")[0].strip().strip("'\"") for f in re.findall(r"font-family\s*:\s*([^;}]+)", style)}
        out.append({**c, "textTransform": sorted(set(re.findall(r"text-transform\s*:\s*([\w-]+)", style))) or None,
                    "fontFamilies": sorted(f for f in families if not f.startswith(("$", "var(", "inherit"))) or None,
                    "tokensUsed": sorted(set(re.findall(r"var\((--[\w-]+)", text)) | set(re.findall(r"\$[a-z][\w-]+", style)))[:40],
                    "hardCodedColors": dict(raw.most_common(10)) or None})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo")
    ap.add_argument("--stack", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    repo = Repo(Path(a.repo).expanduser().resolve())
    stack = json.loads(Path(a.stack).read_text())
    tokens, themes = harvest_tokens(repo, stack)
    counts = usage(repo, tokens)
    for t in tokens:
        if t["syntax"] in ("css", "scss", "less"):
            t["uses"] = counts.get(t["name"], 0)
    comps = component_facts(repo, stack["components"])
    styles = typography(tokens)
    out = {"repo": str(repo.root), "name": stack.get("name"), "themes": themes, "tokens": tokens,
           "typography": styles, "components": comps}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, indent=1))
    kinds = Counter(t["kind"] for t in tokens)
    print(f"{len(tokens)} tokens ({', '.join(f'{k} {n}' for k, n in kinds.most_common())}), themes {', '.join(themes) or 'none'}, "
          f"{len(out['typography'])} type styles, {len(comps)} components. Wrote {a.out}.")


if __name__ == "__main__":
    main()
