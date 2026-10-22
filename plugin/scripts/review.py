"""Review for lockstep:learn: turn proposals or coverage into decisions a person makes, then
collect those decisions into the approved set that generate.py reads.

  python3 review.py build --proposals proposals.json --out <folder> [--title "..."]
  python3 review.py build --coverage coverage.json --out <folder> [--title "..."]
  python3 review.py apply --review <folder>/review.json --rulings <rulings.json or REVIEW.md> --out <folder>/approved.json

build writes:
  review.json   the items, each with its evidence, options and Lockstep's suggestion
  REVIEW.md     the same as a checklist: tick one option per item (works anywhere)
  review.html   the review page, published as an artifact; rulings are saved to its database

apply reads rulings from the page's database (saved as JSON by Claude: {item id: {decision,
name, note, by, at}}) or from a ticked REVIEW.md, and writes approved.json. Only approved items
go into it; everything else is listed as rejected or still open, so nothing unreviewed is
generated.

What gets reviewed:
  proposals  each token (approve, rename, reject), each component candidate (make it a
             component or not), each WIP variable (map, keep or delete), each local component
  coverage   each conflict (Figma is right, code is right, or something else), each component
             that's only in Figma or only in code, and one item for everything both sides agree on
"""
import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
TEMPLATE = HERE.parent / "skills" / "learn" / "references" / "review-page.html"


def item_id(*parts):
    """A stable id that is also a valid database path segment."""
    slug = re.sub(r"[^a-z0-9]+", "-", " ".join(str(p) for p in parts).lower()).strip("-")[:40]
    return f"{slug}-{hashlib.sha1('|'.join(map(str, parts)).encode()).hexdigest()[:6]}"


def fmt(v):
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    if isinstance(v, dict):
        return ", ".join(f"{k}: {fmt(x)}" for k, x in v.items())
    return str(v)


TOKEN_OPTIONS = [{"value": "approve", "label": "Approve"}, {"value": "rename", "label": "Rename", "name": True}, {"value": "reject", "label": "Reject"}]


def from_proposals(p):
    items = []
    for t in p["tokens"]:
        evidence = [f"Used {t['uses']} times in product files" + (f", {t['internalUses']} times inside library components" if t["internalUses"] else "")]
        if t["libraryNames"]:
            evidence.append("Bound to " + ", ".join(f"{n} ×{c}" for n, c in list(t["libraryNames"].items())[:3]))
        if t["wipNames"]:
            evidence.append("WIP variable " + ", ".join(t["wipNames"]))
        for d in t["drift"]:
            evidence.append(f"Absorbs {fmt(d['value'])} ×{d['uses']}, probably a slip" + (f" (or it belongs to {', '.join(map(fmt, d['alternatives']))})" if d["alternatives"] else ""))
        items.append({"id": item_id("token", t["kind"], t["value"]), "group": "Tokens", "kind": t["kind"], "value": t["value"],
                      "title": f"{t['kind']} {fmt(t['value'])}", "name": t["suggestedName"] or "", "evidence": evidence,
                      "examples": t["examples"], "options": TOKEN_OPTIONS, "suggestion": "approve" if t["suggestedName"] else "rename",
                      "payload": {"type": "token", "kind": t["kind"], "value": t["value"], "values": {"default": t["value"]}, "drift": t["drift"]}})
    for c in p["components"]:
        de_facto = c["status"].startswith("de facto")
        ev = [c["status"]]
        if c["source"] == "detached copies":
            ev.append(f"{c['detached']} detached copies, {c['liveInstances']} live instances, in {', '.join(c['frames'])}")
        else:
            ev.append(f"Repeats {c['repeats']} times: " + ", ".join(f"{k} ×{v}" for k, v in c["names"].items()))
        opts = [{"value": "component", "label": "Make it a component", "name": True}, {"value": "reject", "label": "Not a component"}] if de_facto else \
               [{"value": "relink", "label": "Relink the detached copies"}, {"value": "reject", "label": "Leave them"}]
        items.append({"id": item_id("component", c["name"]), "group": "Components", "title": c["name"], "name": c["name"], "evidence": ev,
                      "examples": c["nodes"][:4], "options": opts, "suggestion": "component" if de_facto else "relink",
                      "payload": {"type": "component", **{k: c[k] for k in ("name", "source", "status", "nodes") if k in c}}})
    for w in p["wipVariables"]:
        if w["mapsTo"]:
            opts = [{"value": "map", "label": f"Map to {w['mapsTo']}"}, {"value": "keep", "label": "Keep as its own token", "name": True}, {"value": "delete", "label": "Delete"}]
            sug = "map"
        else:
            opts = [{"value": "delete", "label": "Delete"}, {"value": "keep", "label": "Keep", "name": True}]
            sug = "delete" if w["status"].startswith("unused") else "keep"
        items.append({"id": item_id("wip", w["name"]), "group": "WIP variables", "title": w["name"], "name": w["name"], "value": w["value"],
                      "kind": "color" if w["type"] == "COLOR" else "number", "evidence": [w["status"], f"Bound {w['boundUses']} times"],
                      "options": opts, "suggestion": sug, "payload": {"type": "wip", **w}})
    for lc in p["localComponents"]:
        dup = lc["duplicates"]
        opts = ([{"value": "merge", "label": f"Merge into {dup[0]}"}] if dup else []) + [{"value": "keep", "label": "Keep"}, {"value": "delete", "label": "Delete"}]
        items.append({"id": item_id("local", lc["name"]), "group": "Local components", "title": lc["name"], "name": lc["name"],
                      "evidence": [lc["note"], f"{lc['status'].lower()}, {lc['instancesInFile']} instances in its file"], "examples": [lc["id"]],
                      "options": opts, "suggestion": "merge" if dup else "keep", "payload": {"type": "local", **lc}})
    return items


def from_coverage(cov):
    """Conflicts first, then components missing on one side, then one item for what agrees."""
    items, agreed = [], []
    complete = [r for r in cov["tokens"] if r["status"] == "complete"]
    types = [r for r in cov["typography"] if r["status"] == "complete"]
    comps = [r for r in cov["components"] if r["status"] in ("complete", "drift")]
    if complete or types or comps:
        agreed.append({"id": item_id("agreed", len(complete), len(types), len(comps)), "group": "Agreed",
                      "title": f"{len(complete)} tokens, {len(types)} type styles and {len(comps)} components in both Figma and code",
                      "evidence": [f"{sum(1 for r in complete if r['nameMatch'])} tokens with matching names",
                                   f"{sum(1 for r in complete if not r['nameMatch'])} tokens matched by value alone: check these in COVERAGE.md",
                                   "Type styles: " + ", ".join(r["design"] for r in types),
                                   "Components: " + ", ".join(f"{r['design']} = {r['code']}" for r in comps) + ". Their differences are listed as conflicts."],
                      "options": [{"value": "approve", "label": "Approve all"}, {"value": "reject", "label": "Hold for line-by-line review"}], "suggestion": "approve",
                      "payload": {"type": "agreed", "rows": complete, "types": types, "components": comps}})
    for i, c in enumerate(cov["conflicts"]):
        items.append({"id": item_id("conflict", c["topic"]), "group": "Conflicts", "title": c["topic"], "figma": c["design"], "code": c["code"],
                      "evidence": [c["question"]], "options": [{"value": "figma", "label": "Figma is right"}, {"value": "code", "label": "Code is right"},
                                                               {"value": "other", "label": "Something else", "note": True}],
                      "suggestion": None, "payload": {"type": "conflict", **c}})
    for r in cov["components"]:
        if r["status"] == "design-only":
            items.append({"id": item_id("design-only", r["design"]), "group": "Missing in code", "title": r["design"],
                          "evidence": ["In Figma, no code component found"] + [f"{k}: {', '.join(v)}" for k, v in (r.get("designAxes") or {}).items()][:3],
                          "options": [{"value": "build", "label": "Build it in code"}, {"value": "figma-only", "label": "Figma only is fine"}],
                          "suggestion": None, "payload": {"type": "design-only-component", **r}})
        elif r["status"] == "code-only":
            items.append({"id": item_id("code-only", r["code"]), "group": "Missing in Figma", "title": r["code"],
                          "evidence": [f"In code ({r['codeFile']}), no Figma component found", "props: " + ", ".join(r.get("props") or [])],
                          "options": [{"value": "build", "label": "Add it to Figma"}, {"value": "code-only", "label": "Code only is fine"}],
                          "suggestion": None, "payload": {"type": "code-only-component", **r}})
    return items + agreed


def write_md(path, review):
    L = [f"# Review: {review['title']}", "", "Tick one option per item (`[x]`). Write a new name after `rename to:` or `name:` where an option allows it, "
         "and anything else on the `Note:` line. Items left unticked stay open and nothing is generated from them.", ""]
    group = None
    for it in review["items"]:
        if it["group"] != group:
            group = it["group"]
            L += [f"## {group}", ""]
        L.append(f"### {it['title']}  `{it['id']}`")
        if it.get("figma"):
            L += [f"- Figma: {it['figma']}", f"- Code: {it['code']}"]
        if it.get("name"):
            L.append(f"- Suggested name: {it['name']}")
        L += [f"- {e}" for e in it["evidence"]]
        if it.get("suggestion"):
            L.append(f"- Lockstep suggests: {next(o['label'] for o in it['options'] if o['value'] == it['suggestion'])}")
        L.append("")
        for o in it["options"]:
            L.append(f"- [ ] {o['label']}" + (" (name: )" if o.get("name") else ""))
        L += ["", "Note:", ""]
    path.write_text("\n".join(L))


def build(a):
    if a.proposals:
        items, source = from_proposals(json.loads(Path(a.proposals).read_text())), "proposals"
    else:
        items, source = from_coverage(json.loads(Path(a.coverage).read_text())), "coverage"
    review = {"title": a.title, "source": source, "built": date.today().isoformat(), "items": items}
    od = Path(a.out)
    od.mkdir(parents=True, exist_ok=True)
    (od / "review.json").write_text(json.dumps(review, indent=1))
    write_md(od / "REVIEW.md", review)
    page = {**review, "items": [{k: v for k, v in it.items() if k != "payload"} for it in items]}
    html = TEMPLATE.read_text().replace("__REVIEW_TITLE__", a.title.replace("<", "&lt;")).replace("__REVIEW_DATA__", json.dumps(page).replace("</", "<\\/"))
    (od / "review.html").write_text(html)
    print(f"{len(items)} items to review ({', '.join(f'{g} {sum(1 for i in items if i['group'] == g)}' for g in dict.fromkeys(i['group'] for i in items))}). "
          f"Wrote review.json, REVIEW.md and review.html in {od}.")


def parse_md(text, review):
    """{id: {decision, name, note}} from a ticked REVIEW.md."""
    out = {}
    by_id = {it["id"]: it for it in review["items"]}
    for block in re.split(r"(?m)^### ", text)[1:]:
        m = re.search(r"`([a-z0-9-]+)`", block.splitlines()[0])
        if not m or m.group(1) not in by_id:
            continue
        it = by_id[m.group(1)]
        for o in it["options"]:
            hit = re.search(rf"(?m)^- \[[xX]\] {re.escape(o['label'])}(?: \(name: ?(.*?)\))?\s*$", block)
            if hit:
                note = re.search(r"(?ms)^Note:\s*\n(.*?)(?=^#|\Z)", block)
                out[it["id"]] = {"decision": o["value"], "name": (hit.group(1) or "").strip() or None, "note": (note.group(1).strip() if note else "") or None, "by": "REVIEW.md"}
                break
    return out


WEIGHTS = {"Thin": 100, "Light": 300, "Regular": 400, "Medium": 500, "Semi Bold": 600, "Bold": 700, "Black": 900}


def type_values(tuple_value):
    """'Inter|Semi Bold|24|120%|-2%' -> type style fields in px."""
    family, style, size, lh, ls = tuple_value.split("|")
    size = float(size)
    px = lambda v: None if v == "auto" else round(float(v[:-1]) * size / 100, 3) if v.endswith("%") else float(v.rstrip("px") or 0)
    return {"fontFamily": family, "fontWeight": WEIGHTS.get(style, 400), "fontSize": size, "lineHeight": px(lh), "letterSpacing": px(ls)}


def apply(a):
    review = json.loads(Path(a.review).read_text())
    src = Path(a.rulings)
    if src.is_dir():
        # ArtifactData's out_dir: one JSON file per ruling, named by item id
        rulings = {}
        for f in sorted(src.rglob("*.json")):
            doc = json.loads(f.read_text())
            rulings[f.stem] = doc.get("data", doc) if isinstance(doc, dict) else doc
    elif src.suffix == ".md":
        rulings = parse_md(src.read_text(), review)
    else:
        rulings = json.loads(src.read_text())
    approved = {"title": review["title"], "source": review["source"], "tokens": [], "typeStyles": [], "components": [], "decisions": [],
                "rejected": [], "open": []}
    for it in review["items"]:
        r = rulings.get(it["id"])
        p = it["payload"]
        if not r or not r.get("decision"):
            approved["open"].append({"id": it["id"], "title": it["title"]})
            continue
        d, name = r["decision"], r.get("name") or it.get("name")
        if not name and p["type"] == "token":
            # approved without a name: name it by what it is, so it can't collide or vanish
            name = f"{p['kind']}/{re.sub(r'[^a-z0-9]+', '-', fmt(p['value']).lower()).strip('-')}"
        rec = {"id": it["id"], "decision": d, "by": r.get("by"), "at": r.get("at"), "note": r.get("note")}
        if d in ("reject", "delete", "figma-only", "code-only"):
            approved["rejected"].append({**rec, "title": it["title"]})
            continue
        if p["type"] == "token" and d in ("approve", "rename") and p["kind"] == "type":
            approved["typeStyles"].append({**rec, "name": name, "values": type_values(p["value"])})
        elif p["type"] == "token" and d in ("approve", "rename"):
            approved["tokens"].append({**rec, "name": name, "kind": p["kind"], "values": p["values"], "drift": p["drift"]})
        elif p["type"] == "wip" and d == "keep":
            approved["tokens"].append({**rec, "name": name, "kind": it.get("kind", "number"), "values": {"default": p["value"]}, "drift": []})
        elif p["type"] == "agreed" and d == "approve":
            for row in p["rows"]:
                approved["tokens"].append({**rec, "name": row["design"], "kind": row["kind"], "values": row["values"], "code": row["code"], "drift": []})
            for row in p["types"]:
                approved["typeStyles"].append({**rec, "name": row["design"], "code": row["code"], "values": row.get("values")})
            for row in p.get("components", []):
                approved["components"].append({**rec, "name": row["design"], "code": row["code"], "codeFile": row.get("codeFile"), "axes": row.get("axes")})
        elif p["type"] == "component" and d in ("component", "relink"):
            approved["components"].append({**rec, "name": name, "evidence": it["evidence"], "nodes": p.get("nodes"), "status": p.get("status")})
        else:
            approved["decisions"].append({**rec, "title": it["title"], "payload": p})
    Path(a.out).write_text(json.dumps(approved, indent=1))
    print(f"{len(approved['tokens'])} tokens, {len(approved['typeStyles'])} type styles and {len(approved['components'])} components approved; "
          f"{len(approved['decisions'])} other decisions, {len(approved['rejected'])} rejected, {len(approved['open'])} still open. Wrote {a.out}.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    src = b.add_mutually_exclusive_group(required=True)
    src.add_argument("--proposals")
    src.add_argument("--coverage")
    b.add_argument("--title", default="Design system review")
    b.add_argument("--out", required=True)
    p = sub.add_parser("apply")
    p.add_argument("--review", required=True)
    p.add_argument("--rulings", required=True)
    p.add_argument("--out", required=True)
    a = ap.parse_args()
    build(a) if a.cmd == "build" else apply(a)


if __name__ == "__main__":
    main()
