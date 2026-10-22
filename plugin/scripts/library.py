"""Write the files lockstep:build reads for a learned library: LIBRARY.md, keys.json, variables.json.

A learned library lives in a draft file until the org publishes it, so its rebuilt components
and variables are local to that file: build has to work in that file, and reaches them by node
ID (`local:<id>`). Library components that were already published are reached by key, as usual.

  python3 library.py --figma-dir <learned>/figma --file-key <draft key> --approved approved.json --out lockstep/<org-slug>/learned

Reads from --figma-dir:
  variables.result.json   variables.js's result
  rebuild.result.json     rebuild.js's result
  library.components.json inventory.js's components part for the published components in use
  library-keys.json       the keys that inventory was run with
"""
import argparse
import json
import re
from pathlib import Path


def label(name):
    ws = re.findall(r"[A-Za-z0-9]+", name)
    return (ws[0].lower() + "".join(w.capitalize() for w in ws[1:])) if ws else "component"


def props_text(props):
    out = []
    for k, v in props.items():
        base = k.split("#")[0]
        if isinstance(v, list):
            out.append(f"{base}: {' / '.join(v)}")
        elif v == "SLOT":
            out.append(f"{base} (slot)")
        else:
            kind, _, default = str(v).partition("=")
            out.append(f"{base} ({kind.lower()}{', default ' + default if default and kind == 'TEXT' else ''})")
    return "; ".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--figma-dir", required=True)
    ap.add_argument("--file-key", required=True)
    ap.add_argument("--approved", required=True)
    ap.add_argument("--library-page", default="Learned library")
    ap.add_argument("--title", default="Learned library")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    fd = Path(a.figma_dir)
    variables = json.loads((fd / "variables.result.json").read_text())
    rebuilt = json.loads((fd / "rebuild.result.json").read_text())
    published = json.loads((fd / "library.components.json").read_text())["components"] if (fd / "library.components.json").exists() else []
    approved = json.loads(Path(a.approved).read_text())
    od = Path(a.out)
    od.mkdir(parents=True, exist_ok=True)

    # Published components: their keys, from the keys file the inventory was run with.
    published_keys = json.loads((fd / "library-keys.json").read_text()) if (fd / "library-keys.json").exists() else {}
    keys = {c["label"]: published_keys[c["label"]] for c in published if c["label"] in published_keys}
    for name, r in rebuilt["components"].items():
        keys[label(name)] = f"local:{r['id']}"
    (od / "keys.json").write_text(json.dumps(keys, indent=1) + "\n")
    var_refs = {name: f"local:{v['id']}" for name, v in variables["variables"].items()}
    (od / "variables.json").write_text(json.dumps({"variables": var_refs, "textStyles": {n: f"local:{i}" for n, i in variables["styles"].items()}}, indent=1) + "\n")

    notes = {c["name"]: c for c in approved.get("components", [])}
    L = [f"# {a.title}", "",
         f"- **File:** `{a.file_key}` (a draft). The learned components and variables are local to this file until the org publishes it, "
         f"so **build here**, on a new page. Don't create another draft: local components can't be used from another file.",
         f"- **Components** are on the page \"{a.library_page}\". Refs in `keys.json`: `local:<node id>` for learned components, a key for published ones.",
         f"- **Variables** are in the collection \"Learned tokens\" (modes: {', '.join(variables['modes'])}); refs in `variables.json`. Text styles are local too.",
         f"- **Score** with `render.py score --roots <frames> --local-library-page \"{a.library_page}\"`, so learned components count as library instances.",
         "",
         "```js",
         "// Learned (local) and published refs side by side.",
         "const component = async (ref) => ref.startsWith('local:') ? figma.getNodeByIdAsync(ref.slice(6))",
         "  : figma.importComponentSetByKeyAsync(ref).catch(() => figma.importComponentByKeyAsync(ref));",
         "const variable = async (ref) => figma.variables.getVariableByIdAsync(ref.slice(6));",
         "const textStyle = async (ref) => figma.getStyleByIdAsync(ref.slice(6));",
         "```", "",
         "## Components", "",
         "| Label | Component | From | Properties | Notes |", "|---|---|---|---|---|"]
    for name, r in rebuilt["components"].items():
        n = notes.get(name, {})
        note = []
        if "Slot" in (r.get("props") or []):
            note.append("put content in its slot; the slot starts empty")
        if not r.get("props"):
            note.append("its library parts are exposed: set their properties through the instance")
        L.append(f"| `{label(name)}` | {name} | learned (rebuilt from approved copies) | {', '.join(r.get('props') or []) or 'none of its own'} | {'; '.join(note)} |")
    for c in published:
        L.append(f"| `{c['label']}` | {c['name']} | published library | {props_text(c['props'])} | {(c.get('description') or '').splitlines()[0][:120] if c.get('description') else ''} |")
    L += ["", "Learned components have one variant: the one their examples showed. If a page needs another state "
          "(a switch that's off), say so in your report rather than detaching or redrawing it.", ""]
    by_kind = {}
    for name, v in variables["variables"].items():
        by_kind.setdefault(v["kind"], []).append(name)
    L += ["## Tokens", ""]
    for kind, names in by_kind.items():
        L.append(f"- **{kind}:** " + ", ".join(f"`{n}`" for n in names))
    L += ["", "Text styles: " + ", ".join(variables["styles"]) + ".", ""]
    decided = [d for d in approved.get("decisions", [])]
    if decided:
        L += ["## Decisions from review", ""] + [f"- {d['title']}: {d['decision']}" + (f" ({d['note']})" if d.get("note") else "") for d in decided] + [""]
    if approved.get("open"):
        L += ["## Still open", "", "Not decided yet; don't rely on these:", ""] + [f"- {o['title']}" for o in approved["open"]] + [""]
    (od / "LIBRARY.md").write_text("\n".join(L))
    print(f"{len(keys)} components ({len(rebuilt['components'])} learned, {len(keys) - len(rebuilt['components'])} published), "
          f"{len(var_refs)} variables. Wrote LIBRARY.md, keys.json and variables.json in {od}.")


if __name__ == "__main__":
    main()
