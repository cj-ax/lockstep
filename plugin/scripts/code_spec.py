"""Specs for building code components in Figma (lockstep:learn, code to Figma).

For each component that's in code but not in Figma, reads its source (never runs it) and
writes what a Figma build needs:

  - its props, and which of them become variant properties (finite values, booleans)
  - its slots, which become Figma slots
  - the UI-library components it wraps (their look comes from that library's defaults, not the
    repo: the spec says so, so whoever builds it marks what came from where)
  - every style value it sets, resolved, and the Figma variable to bind it to: through the
    coverage when the code token matched a Figma token, else by value and property kind

  python3 code_spec.py --code code.json --coverage coverage.json --variables inventory.variables.json
                       --repo <repo path> [--components SSkeletonLoader,SExpansionPanels] --out <folder>

Writes specs.json and SPECS.md. With --approved, it takes the code-only components a person
ruled "Add it to Figma"; that's how lockstep:learn runs it. --components names them directly.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from harvest_code import color, length  # noqa: E402
from scan_repo import read, strip_comments  # noqa: E402

PROP_KIND = {"padding": "spacing", "margin": "spacing", "gap": "spacing", "row-gap": "spacing", "column-gap": "spacing",
             "border-radius": "radius", "border-width": "stroke", "font-size": "fontSize", "font-weight": "fontWeight",
             "line-height": "lineHeight", "letter-spacing": "letterSpacing", "width": "size", "height": "size",
             "max-width": "size", "min-width": "size", "max-height": "size", "min-height": "size"}
COLOR_PROPS = ("color", "background", "background-color", "border-color", "border", "fill", "stroke", "outline-color")


def jsdoc_summary(text):
    m = re.search(r"/\*\*\s*\n\s*\*\s*(\w+)\s*--\s*(.+?)(?:\n\s*\*\s*\n|\*/)", text, re.S)
    if not m:
        return None
    return " ".join(l.strip(" *") for l in m.group(2).splitlines()).strip()


def style_rules(text):
    """[(selector, property, value)] from the component's <style> blocks, nesting flattened."""
    out = []
    for block in re.findall(r"<style[^>]*>(.*?)</style>", text, re.S):
        block = strip_comments(block)
        stack, buf = [], ""

        def flush(decls):
            for decl in decls.split(";"):
                if ":" in decl and stack:
                    k, v = decl.split(":", 1)
                    if re.fullmatch(r"\s*[a-z-]+\s*", k):
                        out.append((" ".join(stack).replace(" &", ""), k.strip(), v.strip()))
        for ch in block:
            if ch == "{":
                # declarations written before a nested rule belong to the enclosing selector
                head, _, sel = buf.rpartition(";")
                flush(head)
                stack.append(sel.strip())
                buf = ""
            elif ch == "}":
                flush(buf)
                if stack:
                    stack.pop()
                buf = ""
            elif ch == ";" and stack:
                buf += ch
            else:
                buf += ch
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--code", required=True)
    ap.add_argument("--coverage", required=True)
    ap.add_argument("--variables", help="inventory.variables.json, for the keys build binds to")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--components")
    ap.add_argument("--approved", help="approved.json: only components a person ruled \"Add it to Figma\"")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    code = json.loads(Path(a.code).read_text())
    cov = json.loads(Path(a.coverage).read_text())
    repo = Path(a.repo).expanduser()
    if a.components:
        names = [n.strip() for n in a.components.split(",")]
    elif a.approved:
        approved = json.loads(Path(a.approved).read_text())
        names = [d["payload"]["code"] for d in approved.get("decisions", []) if d["payload"].get("type") == "code-only-component" and d["decision"] == "build"]
    else:
        names = [r["code"] for r in cov["components"] if r["status"] == "code-only"]

    # Figma variables: name -> key, kind, light value (from the library inventory).
    fig = {}
    if a.variables:
        inv = json.loads(Path(a.variables).read_text())
        for col, rows in inv["collections"].items():
            cname = col.split(" [")[0].strip()
            for row in rows:
                name, key, value, binds = row[:4]
                modes = row[4] if len(row) > 4 else {"default": value}
                light = next((v for m, v in modes.items() if "light" in m.lower()), value)
                if isinstance(light, (str, int, float)):
                    # two collections can share a name (Slalom has two "Radius"): keep both
                    fig.setdefault(f"{cname}/{name}", []).append({"key": key, "value": light, "binds": binds})
    # Code token -> Figma variable, from the coverage (exact matches and drift).
    by_code = {}
    for r in cov["tokens"]:
        if r["status"] in ("complete", "drift") and r.get("code"):
            for cn in [r["code"]] + (r.get("alsoMatches") or []):
                by_code.setdefault(cn, {"figma": r["design"], "status": r["status"]})
    code_tokens = {t["name"]: t for t in code["tokens"]}

    def figma_for(prop, raw, resolved):
        """The Figma variable to bind for a style value, and how it was found."""
        m = re.search(r"var\((--[\w-]+)", raw) or re.search(r"(\$[\w-]+)", raw)
        if m and m.group(1) in code_tokens and isinstance(resolved, str) and not resolved.startswith("#") and m.group(1) not in by_code:
            return {"variable": None, "via": f"code token {m.group(1)} is '{resolved}' here, so the UI library's default applies"}
        if m and m.group(1) in by_code:
            f = by_code[m.group(1)]
            return {"variable": f["figma"], "key": (fig.get(f["figma"]) or [{}])[0].get("key"), "via": f"code token {m.group(1)} ({f['status']})"}
        if resolved is None or (isinstance(resolved, str) and not resolved.startswith("#")):
            return None
        kind = "color" if isinstance(resolved, str) and resolved.startswith("#") else PROP_KIND.get(prop)
        if kind in (None, "size"):
            return None
        cands = []  # (name, entry)
        for name, entries in fig.items():
            for v in entries:
                if kind == "color" and isinstance(v["value"], str) and v["value"].lower() == resolved.lower():
                    cands.append((name, v))
                elif kind != "color" and isinstance(v["value"], (int, float)) and abs(v["value"] - resolved) < 0.01:
                    binds = v["binds"] or ""
                    if (kind == "spacing" and ("padding" in binds or "itemSpacing" in binds)) or (kind == "radius" and "radius" in binds) \
                            or (kind == "stroke" and "stroke" in binds) or (kind in ("fontWeight", "fontSize") and kind in binds):
                        cands.append((name, v))
        if not cands:
            return {"variable": None, "via": f"no Figma variable has {resolved} for {prop}"}
        # Prefer a name that says what it's for (a gap token for gap), then variables the
        # library's own components bind this way, then the shortest name.
        want = {"gap": ("gap",), "row-gap": ("gap",), "column-gap": ("gap",), "padding": ("padding", "pa-"), "margin": ("space", "margin"),
                "border-radius": ("radius",), "border-width": ("border", "stroke")}.get(prop, ())
        own = lambda n: n.split("/", 1)[-1].lower()  # the name without its collection ("space variables/...")
        cands.sort(key=lambda c: (0 if any(w in own(c[0]) for w in want) else 1, 0 if c[1]["binds"] else 1, len(c[0])))
        (best, entry), others = cands[0], [c[0] for c in cands[1:3]]
        return {"variable": best, "key": entry["key"], "via": "same value" + (f"; also {', '.join(others)}" if others else "")}

    def resolve(raw):
        def sub(m):
            t = code_tokens.get(m.group(1))
            if not t:
                return m.group(0)
            v = t["values"].get("slalomLight") if "slalomLight" in t["values"] else next(iter(t["values"].values()))
            return str(v)
        val = re.sub(r"var\((--[\w-]+)[^)]*\)", sub, raw)
        val = re.sub(r"(\$[\w-]+)", sub, val)
        val = val.replace("!important", "").strip()
        c = color(val)
        if c:
            return c
        first = val.split()[0] if val.split() else val
        n = length(first)
        return n if n is not None else val

    specs = []
    for name in names:
        comp = next((c for c in code["components"] if c["name"] == name), None)
        if not comp:
            continue
        text = read(repo / comp["file"])
        props = comp.get("props") or []
        variants = [{"name": p["name"], "values": p["values"], "default": p.get("default")} for p in props if p.get("values")]
        booleans = [{"name": p["name"], "default": p.get("default")} for p in props if (p.get("type") or "").strip() == "boolean"]
        texts = [{"name": p["name"], "default": p.get("default")} for p in props if (p.get("type") or "").strip() == "string"]
        styles = []
        for sel, prop, raw in style_rules(text):
            r = resolve(raw)
            styles.append({"selector": sel, "property": prop, "value": raw, "resolved": r, "bind": figma_for(prop, raw, r)})
        wraps = comp.get("wraps") or []
        specs.append({"name": name, "file": comp["file"], "summary": jsdoc_summary(text), "variants": variants, "booleans": booleans,
                      "texts": texts, "slots": comp.get("slots") or [], "wraps": wraps, "styles": styles,
                      "lookFrom": f"{', '.join(wraps)} (the UI library's defaults): read its documentation for the inner layout" if wraps else "this repo's template and styles"})
    od = Path(a.out)
    od.mkdir(parents=True, exist_ok=True)
    (od / "specs.json").write_text(json.dumps(specs, indent=1) + "\n")
    L = ["# Code components to build in Figma", "", "From the source, read without running it. Bind every value to the variable named here; "
         "where a value has none, say so in your report rather than leaving it raw silently.", ""]
    for s in specs:
        L += [f"## {s['name']}", "", f"`{s['file']}`. {s['summary'] or ''}", ""]
        if s["variants"]:
            L += ["Variant properties: " + "; ".join(f"**{v['name']}**: {', '.join(v['values'])} (default {v['default'] or v['values'][0]})" for v in s["variants"]) + "."]
        if s["booleans"]:
            L += ["Boolean properties: " + ", ".join(f"**{b['name']}** (default {b['default']})" for b in s["booleans"]) + "."]
        if s["texts"]:
            L += ["Text properties: " + ", ".join(f"**{t['name']}**" + (f" (default {t['default']})" if t["default"] else "") for t in s["texts"]) + "."]
        if s["slots"]:
            L += ["Slots: " + ", ".join(s["slots"]) + "."]
        L += [f"Look comes from: {s['lookFrom']}.", ""]
        if s["styles"]:
            L += ["| Selector | Property | Value | Bind to |", "|---|---|---|---|"]
            for st in s["styles"]:
                b = st["bind"]
                bind = f"{b['variable']} ({b['via']})" if b and b.get("variable") else (b["via"] if b else "")
                L.append(f"| `{st['selector']}` | {st['property']} | `{st['value']}` | {bind} |")
            L.append("")
    (od / "SPECS.md").write_text("\n".join(L))
    print(f"{len(specs)} component specs ({', '.join(s['name'] for s in specs)}). Wrote specs.json and SPECS.md in {od}.")


if __name__ == "__main__":
    main()
