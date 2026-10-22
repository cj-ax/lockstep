"""AI context for code generation, from what a person approved in lockstep:learn's review.

Writes the two files DS-AI-Bridge introduced, so a coding agent (Claude Code, Cursor) builds
with the team's own components and tokens:

  DESIGN_SYSTEM_CONTEXT.md     rules, tokens, components and the decisions still open, to load
                               as a system prompt, a skill or a rules file
  design-system-registry.json  the same as data: tokens, and per component the code API and how
                               each Figma property maps to a code prop

  python3 context.py --approved approved.json [--coverage coverage.json] [--code code.json]
                     [--design-components inventory.components.json] [--review review.json]
                     [--tokens-css tokens.css] --out <folder>

Only approved items are described as the system. Open conflicts are listed as open, with both
sides, so a generator asks instead of picking one. Without --code, the context describes the
Figma side and the generated CSS tokens only.
"""
import argparse
import json
import re
from datetime import date
from pathlib import Path


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"\(.*?\)", "", s).lower()).strip("-")


def short(text, n=400):
    text = " ".join((text or "").split())
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + " …"


def what_it_does(desc):
    m = re.search(r"What the Component Does\??\s*(.+?)(?:\n\s*\n|Variants and Controls|Use Cases|$)", desc or "", re.S)
    return short(m.group(1) if m else (desc or "").split("\n\n")[0], 300)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--approved", required=True)
    ap.add_argument("--coverage")
    ap.add_argument("--code")
    ap.add_argument("--design-components")
    ap.add_argument("--review")
    ap.add_argument("--tokens-css", help="generate.py's tokens.css, for CSS names when code has none")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    approved = json.loads(Path(a.approved).read_text())
    code = json.loads(Path(a.code).read_text()) if a.code else None
    design = {c["name"]: c for c in (json.loads(Path(a.design_components).read_text())["components"] if a.design_components else [])}
    review = json.loads(Path(a.review).read_text()) if a.review else {"items": []}
    code_comps = {c["name"]: c for c in (code or {}).get("components", [])}
    code_tokens = {t["name"]: t for t in (code or {}).get("tokens", [])}
    pkg = (code or {}).get("name")
    framework = None
    if code:
        stack = json.loads((Path(a.code).parent / "stack.json").read_text()) if (Path(a.code).parent / "stack.json").exists() else {}
        fw = [x["name"] for x in stack.get("stack", {}).get("frameworks", [])] + [x["name"] for x in stack.get("stack", {}).get("uiLibraries", [])]
        framework = " + ".join(fw) or None

    # Tokens: the code name when code has one, else the generated CSS name.
    css_names = {}
    if a.tokens_css and Path(a.tokens_css).exists():
        for name in re.findall(r"^\s*(--[\w-]+):", Path(a.tokens_css).read_text(), re.M):
            css_names[name] = True
    tokens = []
    for t in approved["tokens"]:
        # Use code's name only when the names matched too: a token that merely shares a value
        # with a code token (white is white) would point code at the wrong meaning.
        cn = t.get("code") if t.get("nameMatch", True) else None
        same = t.get("code") if t.get("code") and not cn else None
        ref = (f"var({cn})" if cn.startswith("--") else f"theme colour `{cn[6:]}`" if cn.startswith("theme.") else cn) if cn else None
        if not ref:
            path = [slug(p) for p in t["name"].split("/") if slug(p)]
            path = path[1:] if len(path) >= 3 else path
            guess = "--" + "-".join(path)
            ref = f"var({guess})" if guess in css_names or not css_names else None
        tokens.append({"name": t["name"], "kind": t["kind"], "values": t["values"], "use": ref, **({"same_value_in_code": same} if same else {})})

    # Open conflicts and decisions, from the review.
    open_ids = {o["id"] for o in approved.get("open", [])}
    conflicts = [it for it in review["items"] if it["group"] == "Conflicts"]
    decided = {d["id"]: d for d in approved.get("decisions", [])}

    # Components: approved ones, with their code API when there is code.
    comps = []
    for c in approved["components"]:
        cc = code_comps.get(c.get("code") or "")
        dd = design.get(c["name"], {})
        mapping = []
        for ax in c.get("axes") or []:
            if ax.get("codeProp") and not ax.get("note"):
                mapping.append({"figma_property": ax["axis"], "code_prop": ax["codeProp"], "shared_values": ax.get("both", []),
                                "figma_only": ax.get("designOnly", []), "code_only": ax.get("codeOnly", [])})
        touching = [it for it in conflicts if re.search(rf"\b({re.escape(c['name'])}|{re.escape(c.get('code') or '@@')})\b", it["title"] + json.dumps(it.get("payload", {})), re.I)]
        comps.append({
            "id": slug(c["name"]), "figma_name": c["name"], "code_component": c.get("code"), "file": c.get("codeFile") or (cc or {}).get("file"),
            "import": f"import {{ {c['code']} }} from '{pkg}'" if pkg and c.get("code") and (cc or {}).get("exported") else None,
            "description": what_it_does(dd.get("description")) or None,
            "props": [{k: p.get(k) for k in ("name", "type", "values", "default") if p.get(k) is not None} for p in (cc or {}).get("props") or []],
            "slots": (cc or {}).get("slots"), "figma_to_code": mapping,
            "open_questions": [it["title"] for it in touching if it["id"] in open_ids],
            "decisions": [f"{it['title']}: {decided[it['id']]['decision']}" for it in touching if it["id"] in decided],
        })

    registry = {
        "meta": {"system_name": approved["title"], "generated": date.today().isoformat(), "generator": "Lockstep learn (context.py)",
                 "framework": framework, "package": pkg, "source": "approved review items only",
                 "open_items": len(approved.get("open", []))},
        "tokens": tokens, "components": comps,
        "open_conflicts": [{"topic": it["title"], "figma": it.get("figma"), "code": it.get("code")} for it in conflicts if it["id"] in open_ids],
        "decisions": [{"topic": it["title"], "ruling": decided[it["id"]]["decision"], "note": decided[it["id"]].get("note")} for it in conflicts if it["id"] in decided],
    }
    od = Path(a.out)
    od.mkdir(parents=True, exist_ok=True)
    (od / "design-system-registry.json").write_text(json.dumps(registry, indent=1) + "\n")

    L = [f"# Design system context: {approved['title']}", "",
         f"> Load this as a system prompt, a skill or a rules file when generating UI code. Generated by Lockstep on {date.today().isoformat()} "
         "from the items people approved in review. Anything not listed here isn't part of the system yet.", "",
         "## Rules", ""]
    rules = []
    if pkg and comps:
        rules.append(f"Build with the components from `{pkg}`. Don't use raw HTML elements or the underlying UI library directly when one of these components covers the need.")
    if framework:
        rules.append(f"The stack is {framework}.")
    rules.append("Never hard-code colours, spacing, radii or shadows. Use the tokens below by their CSS name.")
    families = sorted({s.get("values", {}).get("fontFamily") for s in approved.get("typeStyles", []) if (s.get("values") or {}).get("fontFamily")})
    if families:
        rules.append(f"The font is {', '.join(families)}.")
    for d in registry["decisions"]:
        rules.append(f"Decided: {d['topic']}: {d['ruling']}" + (f" ({d['note']})" if d.get("note") else "") + ".")
    if registry["open_conflicts"]:
        rules.append(f"{len(registry['open_conflicts'])} questions are still open (listed at the end). Where your code touches one, ask instead of picking a side.")
    L += [f"{i}. {r}" for i, r in enumerate(rules, 1)] + [""]
    L += ["## Tokens", "", "| Token | Kind | Values | Use |", "|---|---|---|---|"]
    for t in tokens:
        vals = ", ".join(f"{m}: {v}" for m, v in t["values"].items())
        use = (t["use"] if t["use"] and t["use"].startswith("theme") else f"`{t['use']}`") if t["use"] else ""
        if t.get("same_value_in_code"):
            use += f" (same value as `{t['same_value_in_code']}` in code, a different name)"
        L.append(f"| {t['name']} | {t['kind']} | {vals} | {use} |")
    L += ["", "## Components", ""]
    for c in comps:
        L += [f"### {c['figma_name']}" + (f" → `{c['code_component']}`" if c["code_component"] else ""), ""]
        if c["description"]:
            L += [c["description"], ""]
        if c["import"]:
            L += ["```js", c["import"], "```", ""]
        if c["props"]:
            L += ["| Prop | Type | Values | Default |", "|---|---|---|---|"]
            L += [f"| `{p['name']}` | {(p.get('type') or '').replace('|', '/')} | {', '.join(p.get('values') or [])} | {p.get('default', '')} |" for p in c["props"]] + [""]
        for m in c["figma_to_code"]:
            extra = "; ".join(x for x in (f"Figma only: {', '.join(m['figma_only'])}" if m["figma_only"] else "", f"code only: {', '.join(m['code_only'])}" if m["code_only"] else "") if x)
            L.append(f"- Figma **{m['figma_property']}** → `{m['code_prop']}`" + (f" ({extra})" if extra else ""))
        if c["figma_to_code"]:
            L.append("")
        for q in c["open_questions"]:
            L.append(f"- **Open:** {q}. Ask before relying on it.")
        if c["open_questions"]:
            L.append("")
    if registry["open_conflicts"]:
        L += ["## Open questions", ""] + [f"- **{o['topic']}.** Figma: {o['figma']}. Code: {o['code']}." for o in registry["open_conflicts"]] + [""]
    (od / "DESIGN_SYSTEM_CONTEXT.md").write_text("\n".join(L))
    print(f"{len(tokens)} tokens, {len(comps)} components, {len(registry['decisions'])} decisions, {len(registry['open_conflicts'])} open questions. "
          f"Wrote DESIGN_SYSTEM_CONTEXT.md and design-system-registry.json in {od}.")


if __name__ == "__main__":
    main()
