"""Generate a design system's files from what a person approved in lockstep:learn's review.

  python3 generate.py --approved approved.json --out <folder>
                      [--coverage coverage.json] [--design-components inventory.components.json] [--code code.json]

Reads only approved.json's approved items: nothing still open or rejected is generated. Writes:

  tokens/tokens.json   DTCG tokens (2025.10 format). The first mode (light) is the $value; other
                       modes are in $extensions["com.lockstep"].modes, with where each token came from
  tokens/tokens.css    the same as CSS custom properties: :root for the first mode, then one
                       [data-theme="..."] block per other mode, plus a .type-<name> class per type style
  docs/README.md       an index: what's in the system, and every decision still open
  docs/tokens.md       every token with its values per mode
  docs/components/*.md one page per approved component: what it's for, its variants in Figma, its
                       props in code, how the two map, and the conflicts that still need a ruling

Docs say only what the sources say. Where a source is missing (no code yet, no Figma description),
the page says so instead of filling the gap.
"""
import argparse
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

DIMENSION = {"spacing", "radius", "stroke", "fontSize", "lineHeight", "letterSpacing", "size"}


def slug(s):
    s = re.sub(r"\(.*?\)", "", s)
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "token"


def token_path(name):
    """'Color Semantic Variables (updated)/Font Colors/text-regular' -> ['font-colors', 'text-regular'].
    The first segment is the Figma collection; it's dropped when the name is still specific without it."""
    parts = [slug(p) for p in re.split(r"/", name) if slug(p)]
    return parts[1:] if len(parts) >= 3 else parts


def theme(mode):
    """One theme name for the many ways collections name a mode: 'Dark mode', 'Dark' -> dark;
    'Build Mode', 'BuildDark' -> build; 'Light mode', 'default' -> light."""
    ws = [w for w in re.split(r"[^a-z0-9]+", re.sub(r"([a-z])([A-Z])", r"\1 \2", mode).lower()) if w and w != "mode"]
    if not ws or ws == ["default"]:
        return "light"
    rest = [w for w in ws if w not in ("light", "dark")]
    if rest:
        return "-".join(rest)  # a brand or product mode: build, mobile, me-slalom
    return "dark" if "dark" in ws else "light"


def first_mode(values):
    for k in values:
        if theme(k) == "light":
            return k
    return next(iter(values))


BLUR = re.compile(r"^(bg-)?blur:([\d.]+)$")


def dtcg_value(kind, v):
    if kind == "effect" and isinstance(v, str) and BLUR.match(v):
        return {"value": float(BLUR.match(v).group(2)), "unit": "px"}
    if kind == "effect" and isinstance(v, (int, float)):
        return {"value": v, "unit": "px"}  # a shadow's offset, blur or spread
    if kind == "color":
        return v
    if kind in DIMENSION and isinstance(v, (int, float)):
        return {"value": v, "unit": "px"}
    if kind == "effect" and isinstance(v, str):
        shadows = []
        for one in v.split(", "):
            parts = one.replace("inset ", "").split()
            if len(parts) == 5:
                x, y, blur, spread, color = parts
                shadows.append({"color": color, "offsetX": {"value": float(x), "unit": "px"}, "offsetY": {"value": float(y), "unit": "px"},
                                "blur": {"value": float(blur), "unit": "px"}, "spread": {"value": float(spread), "unit": "px"}, "inset": one.startswith("inset")})
        return shadows[0] if len(shadows) == 1 else shadows or v
    return v


DTCG_TYPE = {"color": "color", "fontWeight": "fontWeight", "fontFamily": "fontFamily", "effect": "shadow", "number": "number"}


def css_value(kind, v):
    if kind == "effect" and isinstance(v, str) and BLUR.match(v):
        return f"blur({float(BLUR.match(v).group(2)):g}px)"  # use with filter or backdrop-filter
    if kind == "effect" and isinstance(v, (int, float)):
        return f"{v:g}px" if v else "0"
    if kind == "effect" and isinstance(v, str):
        return ", ".join(re.sub(r"(-?[\d.]+) (-?[\d.]+) ([\d.]+) (-?[\d.]+) (#\w+)", r"\1px \2px \3px \4px \5", s) for s in v.split(", "))
    if kind in DIMENSION and isinstance(v, (int, float)):
        return f"{v:g}px" if v else "0"
    if kind == "fontFamily":
        return f"'{v}', sans-serif"
    return str(v) if not isinstance(v, float) else f"{v:g}"


def build_tokens(approved):
    tree, css_modes, rows = {}, defaultdict(list), []
    seen = {}
    for t in approved["tokens"]:
        path = token_path(t["name"])
        key = "-".join(path)
        distinct = sorted({json.dumps(v) for v in t["values"].values()})
        if seen.get(key) == distinct:
            continue  # the same token in two collections: one is enough
        n = 2
        while key in seen:  # two approved names that slug the same with different values: keep both
            path = path[:-1] + [f"{token_path(t['name'])[-1]}-{n}"]
            key = "-".join(path)
            n += 1
        seen[key] = distinct
        values = t["values"]
        primary = first_mode(values)
        node = tree
        for part in path[:-1]:
            node = node.setdefault(part, {})
        ext = {"source": approved["source"], "ruling": {k: t.get(k) for k in ("decision", "by", "at") if t.get(k)}}
        if t.get("code"):
            ext["code"] = t["code"]
        if t.get("drift"):
            ext["absorbedDrift"] = [d["value"] for d in t["drift"]]
        others = {theme(m): dtcg_value(t["kind"], v) for m, v in values.items() if m != primary and theme(m) != "light"}
        if others:
            ext["modes"] = others
        entry = {"$value": dtcg_value(t["kind"], values[primary]), "$extensions": {"com.lockstep": ext}}
        numeric_effect = t["kind"] == "effect" and (isinstance(values[primary], (int, float)) or BLUR.match(str(values[primary])))
        if numeric_effect or t["kind"] in DIMENSION:
            entry = {"$type": "dimension", **entry}
        elif t["kind"] in DTCG_TYPE:
            entry = {"$type": DTCG_TYPE[t["kind"]], **entry}
        node[path[-1]] = entry
        for m, v in values.items():
            th = "" if m == primary else theme(m)
            if th == "light":
                continue  # a second light mode adds nothing to :root
            css_modes[th].append((f"--{key}", css_value(t["kind"], v)))
        rows.append((t["name"], t["kind"], values, t.get("code")))
    return tree, css_modes, rows


def build_type(approved):
    styles = []
    for s in approved["typeStyles"]:
        v = s.get("values") or {}
        if not v.get("fontSize"):
            continue
        styles.append({"name": s["name"], "code": s.get("code"), **v})
    return styles


def write_css(path, css_modes, styles):
    L = ["/* Generated by Lockstep from approved items. Edit the review, not this file. */", ":root {"]
    L += [f"  {n}: {v};" for n, v in css_modes.get("", [])]
    L.append("}")
    for mode, decls in css_modes.items():
        if mode:
            L += ["", f'[data-theme="{slug(mode)}"] {{'] + [f"  {n}: {v};" for n, v in decls] + ["}"]
    for s in styles:
        L += ["", f".type-{slug(s['name'])} {{", f"  font-family: '{s.get('fontFamily', 'inherit')}', sans-serif;", f"  font-size: {s['fontSize']:g}px;"]
        if s.get("fontWeight"):
            L.append(f"  font-weight: {s['fontWeight']};")
        if s.get("lineHeight"):
            L.append(f"  line-height: {s['lineHeight']:g}px;")
        if s.get("letterSpacing") is not None:
            L.append(f"  letter-spacing: {s['letterSpacing']:g}px;")
        if s.get("textCase") in ("uppercase", "lowercase", "capitalize"):
            L.append(f"  text-transform: {s['textCase']};")
        L.append("}")
    path.write_text("\n".join(L) + "\n")


def description_sections(text):
    """Split a Figma component description into its headed sections."""
    out, current = {}, "About"
    for line in (text or "").splitlines():
        h = line.strip().rstrip("?:")
        if h in ("What the Component Does", "Variants and Controls", "Use Cases", "Use Cases and Exceptions", "Exceptions", "Properties", "Use Case and exceptions"):
            current = h
            continue
        out.setdefault(current, []).append(line)
    return {k: "\n".join(v).strip() for k, v in out.items() if "\n".join(v).strip()}


def component_doc(c, design, code, conflicts, approved):
    name = c["name"]
    L = [f"# {name}", ""]
    where = []
    if design:
        where.append(f"Figma: **{design['name']}**")
    if c.get("code"):
        where.append(f"code: `{c['code']}` in `{c.get('codeFile') or (code or {}).get('file', '')}`")
    if where:
        L += ["In " + ", ".join(where) + ".", ""]
    if c.get("status"):
        L += [f"Status from the audit: {c['status']}.", ""]
    ruling = f"Approved ({c.get('decision')})" + (f" by {c['by']}" if c.get("by") else "") + (f" on {c['at'][:10]}" if c.get("at") else "") + "."
    L += [ruling, ""]
    secs = description_sections(design.get("description")) if design else {}
    cut = design and len(design.get("description") or "") >= 1500  # inventory.js keeps 1,500 characters
    what = secs.get("What the Component Does") or secs.get("About")
    L += ["## What it's for", "", what if what else "No description yet: Figma's component has none, and neither does the code. Write one before publishing these docs.", ""]
    use = secs.get("Use Cases") or secs.get("Use Cases and Exceptions") or secs.get("Use Case and exceptions")
    if use:
        L += ["## When to use it", "", use + (" …" if cut else ""), ""]
    if cut:
        L += ["The Figma description is longer than Lockstep reads (1,500 characters); see the full text on the component in Figma.", ""]
    if design and design.get("axes"):
        L += ["## Variants in Figma", "", "| Property | Options |", "|---|---|"]
        L += [f"| {k} | {', '.join(v)} |" for k, v in design["axes"].items()]
        other = {k: v for k, v in design["props"].items() if not isinstance(v, list)}
        if other:
            L += ["", "Other properties: " + ", ".join(f"{k} ({str(v).split('=')[0].lower()})" for k, v in other.items()) + "."]
        L.append("")
    if code and code.get("props"):
        L += ["## Props in code", "", "| Prop | Type | Values | Default |", "|---|---|---|---|"]
        for p in code["props"]:
            L.append(f"| `{p['name']}` | {(p.get('type') or '').replace('|', '/')} | {', '.join(p.get('values') or [])} | {p.get('default', '')} |")
        if code.get("slots"):
            L += ["", "Slots: " + ", ".join(code["slots"]) + "."]
        L.append("")
    axes = [a for a in c.get("axes") or [] if a.get("codeProp") or a.get("note")]
    if axes:
        L += ["## How Figma maps to code", "", "| Figma property | Code prop | Notes |", "|---|---|---|"]
        for a in axes:
            note = a.get("note") or ("; ".join(x for x in (f"Figma only: {', '.join(a['designOnly'])}" if a.get("designOnly") else "",
                                                           f"code only: {', '.join(a['codeOnly'])}" if a.get("codeOnly") else "") if x) or "same options")
            L.append(f"| {a['axis']} | {('`' + a['codeProp'] + '`') if a.get('codeProp') else ''} | {note} |")
        L.append("")
    if c.get("nodes"):
        L += ["## Where it's used", "", "Example layers in the audited files: " + ", ".join(f"`{n}`" for n in c["nodes"][:6]) + ".", ""]
    mine = [x for x in conflicts if re.search(rf"\b({re.escape(name)}|{re.escape(c.get('code') or '@@')})\b", x["title"] + " " + json.dumps(x.get("payload", {})), re.I)]
    if mine:
        L += ["## Decisions and open questions", ""]
        for x in mine:
            state = "Still open" if x.get("open") else f"Ruled: {x['decision']}" + (f" ({x['note']})" if x.get("note") else "")
            L.append(f"- **{x['title']}.** {state}.")
        L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--approved", required=True)
    ap.add_argument("--coverage")
    ap.add_argument("--design-components")
    ap.add_argument("--code")
    ap.add_argument("--review", help="review.json, to list open conflicts on component pages")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    approved = json.loads(Path(a.approved).read_text())
    design = {c["name"]: {**c, "props": {k.split("#")[0]: v for k, v in c["props"].items()},
                          "axes": {k.split("#")[0]: v for k, v in c["props"].items() if isinstance(v, list)}}
              for c in (json.loads(Path(a.design_components).read_text())["components"] if a.design_components else [])}
    code = {c["name"]: c for c in (json.loads(Path(a.code).read_text())["components"] if a.code else [])}
    od = Path(a.out)
    (od / "tokens").mkdir(parents=True, exist_ok=True)
    (od / "docs" / "components").mkdir(parents=True, exist_ok=True)

    tree, css_modes, rows = build_tokens(approved)
    styles = build_type(approved)
    for s in styles:
        node = tree.setdefault("typography", {})
        node[slug(s["name"])] = {"$type": "typography", "$value": {
            "fontFamily": s.get("fontFamily"), "fontSize": {"value": s["fontSize"], "unit": "px"}, "fontWeight": s.get("fontWeight"),
            **({"lineHeight": round(s["lineHeight"] / s["fontSize"], 4)} if s.get("lineHeight") else {}),
            **({"letterSpacing": {"value": s["letterSpacing"], "unit": "px"}} if s.get("letterSpacing") is not None else {})},
            "$extensions": {"com.lockstep": {"code": s.get("code")}}}
    (od / "tokens" / "tokens.json").write_text(json.dumps(tree, indent=2) + "\n")
    write_css(od / "tokens" / "tokens.css", css_modes, styles)

    # Decisions and open conflicts, for the component pages and the index
    review = json.loads(Path(a.review).read_text()) if a.review else {"items": []}
    open_ids = {o["id"] for o in approved["open"]}
    conflicts = [{"title": it["title"], "open": it["id"] in open_ids, "payload": it.get("payload", {}),
                  **next((d for d in approved["decisions"] if d["id"] == it["id"]), {})}
                 for it in review["items"] if it["group"] == "Conflicts"]

    pages = []
    for c in approved["components"]:
        d = design.get(c["name"])
        k = code.get(c.get("code") or "")
        fname = slug(c["name"]) + ".md"
        (od / "docs" / "components" / fname).write_text(component_doc(c, d, k, conflicts, approved))
        pages.append((c["name"], fname, c.get("code")))

    modes = sorted({m for _, _, v, _ in rows for m in v})
    T = ["# Tokens", "", f"{len(rows)} tokens. Values per mode; the first column is the default.", "",
         "| Token | Kind | " + " | ".join(modes) + " | Code |", "|---|---|" + "---|" * len(modes) + "---|"]
    for name, kind, values, codename in rows:
        T.append(f"| `{'-'.join(token_path(name))}` | {kind} | " + " | ".join(str(values.get(m, "")) for m in modes) + f" | {('`' + codename + '`') if codename else ''} |")
    if styles:
        T += ["", "## Type styles", "", "| Style | Size | Weight | Line height | Letter spacing | Code |", "|---|---|---|---|---|---|"]
        for s in styles:
            T.append(f"| {s['name']} | {s['fontSize']:g}px | {s.get('fontWeight', '')} | {s.get('lineHeight') or ''} | {s.get('letterSpacing', '')} | {s.get('code') or ''} |")
    (od / "docs" / "tokens.md").write_text("\n".join(T) + "\n")

    R = [f"# {approved['title']}", "", f"Generated by Lockstep on {date.today().isoformat()} from the items a person approved in review. "
         "To change anything, change the ruling and generate again.", "",
         f"- **Tokens:** {len(rows)} in `tokens/tokens.json` (DTCG) and `tokens/tokens.css`. See [tokens.md](tokens.md).",
         f"- **Type styles:** {len(styles)}.", f"- **Components:** {len(pages)}.", ""]
    if pages:
        R += ["## Components", ""] + [f"- [{n}](components/{f})" + (f" (code: `{c}`)" if c else "") for n, f, c in pages] + [""]
    if approved["open"]:
        R += [f"## Still open ({len(approved['open'])})", "", "Nothing below was generated. Each needs a ruling first.", ""]
        R += [f"- {o['title']}" for o in approved["open"]] + [""]
    if approved["rejected"]:
        R += [f"## Rejected ({len(approved['rejected'])})", ""] + [f"- {r['title']} ({r['decision']})" for r in approved["rejected"]] + [""]
    if approved["decisions"]:
        R += ["## Other decisions", ""] + [f"- {d['title']}: {d['decision']}" + (f" ({d['note']})" if d.get("note") else "") for d in approved["decisions"]] + [""]
    (od / "docs" / "README.md").write_text("\n".join(R))
    print(f"{len(rows)} tokens ({len(css_modes) - 1 if '' in css_modes else len(css_modes)} extra modes), {len(styles)} type styles, {len(pages)} component pages; "
          f"{len(approved['open'])} items still open. Wrote {od / 'tokens'} and {od / 'docs'}.")


if __name__ == "__main__":
    main()
