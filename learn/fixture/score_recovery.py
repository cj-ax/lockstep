"""Score what lockstep:learn recovered from the degraded fixture against ground-truth.json.

  python3 score_recovery.py --proposals harvest/proposals.json --audit harvest/audit.json [--out RECOVERY.md]

Metrics (see LEARN-DESIGN.md, "Proving it"):
  token recall      ground-truth tokens whose value (for the way they're used) appears among the
                    token proposals; reported for tokens the frames' own layers used, and for all
                    tokens used including those only inside library components
  token precision   proposals that match a token the original frames used, out of all proposals,
                    as if a reviewer approved everything (the worst case)
  names             for tokens the frames' layers used, whether the suggested name is a library
                    name for that value and use, and whether it's exactly the one the designer used
  text styles       ground-truth text styles found as type proposals (font, size, line height)
  drift detection   injected drift edits flagged and attached to the token they drifted from
  component recall  the ten detached or deleted components found as candidates, from all
                    evidence and from structure alone (no detachedInfo)
  WIP mapping       WIP variables mapped to the right library token; noise variables flagged
  local library     local components linked to the pattern they duplicate, and flagged unused
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).parent

PROP_KIND = {"fills": "color", "strokes": "color", "padding": "spacing", "itemSpacing": "spacing", "counterAxisSpacing": "spacing",
             "radius": "radius", "strokeWeight": "stroke", "fontSize": "fontSize", "fontWeight": "fontWeight",
             "fontFamily": "fontFamily", "effects": "effect", "lineHeight": "lineHeight", "letterSpacing": "letterSpacing"}
COLLECTIONS = {"Color", "Size", "Responsive", "Typography", "Typography Primitives", "Color Primitives"}


def norm(v):
    if isinstance(v, str) and v.startswith("#"):
        return v.lower()
    if isinstance(v, str):
        try:
            return float(v.split(":")[-1].split(",")[0]) if ":" in v else v
        except ValueError:
            return v
    return float(v)


def pct(a, b):
    return f"{a}/{b} ({round(100 * a / b) if b else 100}%)"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--proposals", required=True)
    ap.add_argument("--audit", required=True)
    ap.add_argument("--truth", default=str(HERE / "ground-truth.json"))
    ap.add_argument("--out")
    a = ap.parse_args()
    truth = json.loads(Path(a.truth).read_text())
    prop = json.loads(Path(a.proposals).read_text())
    audit = json.loads(Path(a.audit).read_text())
    tokens = prop["tokens"]
    have = {(t["kind"], norm(t["value"])) for t in tokens if t["kind"] != "type"}
    R = {}
    L = ["# Recovery on the learn fixture", "",
         f"Scored by `score_recovery.py` against `ground-truth.json` (fixture `{truth['fixture']['figmaFile']}`).", ""]

    # Tokens.
    def kinds(t):
        # The capture records raw property names: strokeTopWeight is a stroke width, and an
        # effect's colour is a colour.
        if t["type"] == "COLOR":
            return {"color"}
        return {PROP_KIND.get("strokeWeight" if p.startswith("stroke") and p.endswith("Weight") else p, p) for p in t.get("props", [])} or {"unknown"}

    def found(t):
        return any((k, norm(t["value"])) in have for k in kinds(t))

    used = truth["pristine"]["tokensUsed"]
    authored = [t for t in used if t["authored"]]
    miss_auth = [t["name"] for t in authored if not found(t)]
    miss_all = [t["name"] for t in used if not found(t)]
    R["tokenRecallAuthored"] = (len(authored) - len(miss_auth), len(authored))
    R["tokenRecallAll"] = (len(used) - len(miss_all), len(used))
    truth_vals = {(k, norm(t["value"])) for t in used for k in kinds(t)}
    styles = truth["pristine"]["textStyles"]
    style_keys = {(s["font"].split(" ", 1)[1], float(s["size"]), round(float(s["lineHeight"]))) for s in styles}

    def type_key(v):
        family, style, size, lh, _ = v.split("|")
        return (style, float(size), round(float(lh.rstrip("%"))) if lh.endswith("%") else lh)

    matched, unmatched = 0, []
    for t in tokens:
        ok = type_key(t["value"]) in style_keys if t["kind"] == "type" else (t["kind"], norm(t["value"])) in truth_vals
        matched += ok
        if not ok:
            unmatched.append(f"{t['kind']} {t['value']}")
    R["tokenPrecision"] = (matched, len(tokens))

    # Names: for each token the frames' own layers used, is the proposal's suggested name that
    # token's name, or another token's with the same value and use? (Values are often shared.)
    short = lambda n: n.split("/", 1)[1] if n and n.split("/", 1)[0] in COLLECTIONS else n
    by_val = {}
    for t in used:
        for k in kinds(t):
            by_val.setdefault((k, norm(t["value"])), set()).add(t["name"])
    named = exact = 0
    wrong_names = []
    for t in authored:
        p_ = next((x for k in kinds(t) for x in tokens if (x["kind"], norm(x["value"])) == (k, norm(t["value"]))), None)
        if not p_:
            continue
        nm = short(p_["suggestedName"])
        if nm == t["name"]:
            exact += 1
        elif nm in by_val.get((p_["kind"], norm(p_["value"])), set()):
            named += 1
        else:
            wrong_names.append(f"{t['name']} ({t['value']}): proposed {p_['suggestedName'] or 'no name'}")
    R["tokenNames"] = (exact + named, len(authored))
    R["tokenNamesExact"] = (exact, len(authored))
    found_styles = {type_key(t["value"]) for t in tokens if t["kind"] == "type"}
    R["textStyles"] = (len(style_keys & found_styles), len(style_keys))

    # Drift.
    drift_hits, drift_miss = 0, []
    for d in truth["degradation"]["drift"]:
        kind = "color" if d["prop"] in ("fills", "strokes") else "spacing"
        ok = any(t["kind"] == kind and norm(t["value"]) == norm(d["from"]) and any(norm(x["value"]) == norm(d["to"]) for x in t["drift"]) for t in tokens)
        drift_hits += ok
        if not ok:
            drift_miss.append(f"{d['node']} {d['prop']} {d['from']}→{d['to']}")
    R["drift"] = (drift_hits, len(truth["degradation"]["drift"]))

    # Components.
    truth_comps = truth["final"]["detachedByOrigin"]
    cands = prop["components"]
    unpublished = set(truth["degradation"]["unpublished"])
    comp_rows = []
    any_found = struct_found = classified = 0
    for name, g in truth_comps.items():
        nodes = set(g["nodes"])
        c = next((c for c in cands if c["name"] == name or nodes & set(c["nodes"])), None)
        clusters = [s for s in audit["structures"] if len(nodes & set(s["ids"])) * 2 >= len(nodes)]
        right_class = c is not None and (c["status"].startswith("de facto") == (name in unpublished))
        any_found += c is not None
        struct_found += bool(clusters)
        classified += right_class
        comp_rows.append(f"| {name} | {'unpublished' if name in unpublished else 'published'} | {g['count']} | {'yes' if c else 'no'} | {'yes' if clusters else 'no'} | {c['status'] if c else ''}{'' if right_class else ' (wrong)'} |")
    n = len(truth_comps)
    R["componentRecall"] = (any_found, n)
    R["componentRecallStructureOnly"] = (struct_found, n)
    R["componentClassification"] = (classified, n)

    # WIP mapping.
    wmap = truth["degradation"]["wipCollection"]["mapsToSds"]
    noise = truth["degradation"]["wipCollection"]["noise"]
    got = {w["name"]: w for w in prop["wipVariables"]}
    wip_ok = [k for k, sds in wmap.items() if got.get(k) and got[k]["mapsTo"] and got[k]["mapsTo"].split("/", 1)[-1] == sds or (got.get(k) and got[k]["mapsTo"] == sds)]
    noise_ok = [k for k in noise if got.get(k) and got[k]["status"].startswith("unused")]
    R["wipMapping"] = (len(wip_ok), len(wmap))
    R["wipNoiseFlagged"] = (len(noise_ok), len(noise))

    # Local library.
    local_ok = 0
    for lc in truth["degradation"]["localLibrary"]:
        got_lc = next((x for x in prop["localComponents"] if x["name"] == lc["name"]), None)
        local_ok += bool(got_lc and lc["from"] in got_lc["duplicates"] and got_lc["instancesInFile"] == 0)
    R["localLibrary"] = (local_ok, len(truth["degradation"]["localLibrary"]))

    L += ["| Metric | Result |", "|---|---|",
          f"| Token recall: tokens the frames' own layers used | {pct(*R['tokenRecallAuthored'])} |",
          f"| Token recall: all tokens used, including inside library components | {pct(*R['tokenRecallAll'])} |",
          f"| Token precision, approving every proposal | {pct(*R['tokenPrecision'])} |",
          f"| Suggested names: a library name for that value and use | {pct(*R['tokenNames'])} |",
          f"| Suggested names: exactly the token the designer used | {pct(*R['tokenNamesExact'])} |",
          f"| Text styles found | {pct(*R['textStyles'])} |",
          f"| Drift edits flagged and attached to the right token | {pct(*R['drift'])} |",
          f"| Components found (all evidence) | {pct(*R['componentRecall'])} |",
          f"| Components found from structure alone | {pct(*R['componentRecallStructureOnly'])} |",
          f"| Components classified correctly (de facto vs published) | {pct(*R['componentClassification'])} |",
          f"| WIP variables mapped to the right library token | {pct(*R['wipMapping'])} |",
          f"| Noise variables flagged as unused | {pct(*R['wipNoiseFlagged'])} |",
          f"| Local components linked to what they duplicate, and flagged unused | {pct(*R['localLibrary'])} |", ""]
    L += ["## Tokens missed", ""]
    L += [f"- {m}" + ("" if m in miss_auth else " (used only inside library components)") for m in miss_all] or ["None."]
    L += ["", "## Names that aren't a library name for that value", ""]
    L += [f"- {w}" for w in wrong_names] or ["None."]
    L += ["", "## Proposals that match no token in the original frames", ""]
    L += [f"- {u}" for u in unmatched] or ["None."]
    L += ["", "## Drift edits missed", ""]
    L += [f"- {m}" for m in drift_miss] or ["None."]
    L += ["", "## Components", "", "| Component | In the fixture | Detached copies | Found | Found from structure alone | Status given |", "|---|---|---|---|---|---|"]
    L += comp_rows
    L += [""]
    text = "\n".join(L)
    if a.out:
        Path(a.out).write_text(text)
    print(text)


if __name__ == "__main__":
    main()
