"""Turn learn's harvest into proposals: tokens, de facto components, and what the WIP library holds.

Reads the JSON that audit.js and inventory_local.js return (saved to files) and writes
proposals.json plus a readable PROPOSALS.md. Nothing here touches Figma.

  python3 propose.py --audit audit.json [--audit more.json ...]
                     [--components inventory-components.json] [--variables inventory-variables.json]
                     --out lockstep/<org>/

Tokens
  A value with evidence is a token proposal of its own: it's bound to a variable or style
  somewhere (in product files or inside library components), or it's a local variable's value.
  Real systems keep near-identical values apart on purpose (SDS has #757575 and #767676), so
  evidence is never merged. An unbound value close to a token (colour: OKLab ΔE under 2;
  numbers: within 1) and used a third as often or less is drift, attached to that token; a
  near tie goes to the token designers place most, and the other is listed. Unbound values with nothing close
  become proposals of their own. Names come from the variables bound to the value, preferring
  the library's names over WIP names, and names whose words fit how the value is used.

Components
  - Detached copies, grouped by name. A detached frame's detachedInfo names the component it
    came from, which survives even when the component was deleted.
  - Repeated structures (3+ matches) that no detached group or live component covers.
  - Local components, matched by structure to the patterns they duplicate, with their usage.

WIP variables are mapped to the library token with the same value and use; variables bound
nowhere are listed as unused rather than proposed.
"""
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

DE_DRIFT = 2.0
DE_TIE = 0.1


# --- colour ---------------------------------------------------------------------------
def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def oklab(h):
    r, g, b = (_lin(int(h[i:i + 2], 16)) for i in (1, 3, 5))
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def alpha(h):
    return int(h[7:9], 16) / 255 if len(h) == 9 else 1.0


def delta_e(a, b):
    """OKLab distance x100; colours with different alpha never match."""
    if abs(alpha(a) - alpha(b)) > 0.02:
        return 999.0
    return 100 * sum((x - y) ** 2 for x, y in zip(oklab(a), oklab(b))) ** 0.5


# --- kinds ----------------------------------------------------------------------------
NUMBER_KIND = {"padding": "spacing", "itemSpacing": "spacing", "counterAxisSpacing": "spacing", "radius": "radius",
               "strokeWeight": "stroke", "fontSize": "fontSize", "fontWeight": "fontWeight", "lineHeight": "lineHeight",
               "letterSpacing": "letterSpacing", "paragraphSpacing": "spacing", "fontFamily": "fontFamily", "fontStyle": "fontStyle"}
COLOR_PROPS = {"fill", "text", "stroke", "effect.color"}


def kind_of_prop(prop):
    if prop.startswith("effect."):
        return "color" if prop == "effect.color" else "effect"
    if prop in COLOR_PROPS:
        return "color"
    return NUMBER_KIND.get(prop, prop)


WEIGHTS = {"Thin": 100, "Extra Light": 200, "Light": 300, "Regular": 400, "Medium": 500, "Semi Bold": 600, "Bold": 700, "Extra Bold": 800, "Black": 900}


def words(name):
    return {w for w in re.split(r"[^a-z0-9]+", name.lower()) if w}


ROLE_WORDS = {"text": {"text"}, "fill": {"background", "bg", "surface", "fill"}, "frame": {"background", "bg", "surface", "fill"},
              "shape": {"icon", "background", "fill"}, "effect.color": {"shadow", "black", "elevation"}, "stroke": {"border", "stroke", "outline"},
              "padding": {"space", "spacing", "padding"}, "itemSpacing": {"space", "spacing", "gap"},
              "radius": {"radius", "corner", "rounded"}, "strokeWeight": {"stroke", "border"}}


def stem_overlap(a, b):
    return any(x[:4] == y[:4] for x in a for y in b if len(x) >= 4 and len(y) >= 4) or bool(a & b)


# --- harvest --------------------------------------------------------------------------
class Token:
    def __init__(self, kind, value):
        self.kind, self.value = kind, value
        self.n = 0                    # authored uses
        self.internal = 0             # uses inside library components
        self.roles = Counter()        # how designers use it (authored layers)
        self.internal_roles = Counter()  # how library components use it
        self.names = Counter()        # library variable / style names
        self.wip = Counter()          # local (WIP) variable names
        self.examples = []
        self.drift = []
        self.evidence = False

    def name(self):
        """The library name that fits how the value is mostly used, else the most used one."""
        pool = self.names or self.wip
        if not pool:
            return None
        roles = self.roles or self.internal_roles
        role = roles.most_common(1)[0][0] if roles else None
        fit = ROLE_WORDS.get(role, set())
        fits = [n for n in pool if fit & words(n)]
        return max(fits or pool, key=lambda n: pool[n])

    def as_json(self, tid):
        return {"id": tid, "kind": self.kind, "value": self.value, "uses": self.n, "internalUses": self.internal,
                "roles": dict(self.roles), "internalRoles": dict(self.internal_roles), "suggestedName": self.name(), "libraryNames": dict(self.names.most_common(6)),
                "wipNames": dict(self.wip), "evidence": "bound or defined" if self.evidence else "raw values only",
                "examples": self.examples[:4], "drift": self.drift}


def strip_collection(label):
    """'local:Tokens (WIP)/bg/white' -> (True, 'bg/white'); 'Color/Text/Default/Default' -> (False, same)."""
    if label.startswith("local:"):
        rest = label[len("local:"):]
        return True, rest.split("/", 1)[1] if "/" in rest and "(" in rest.split("/", 1)[0] else rest
    return False, label


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audit", action="append", required=True)
    ap.add_argument("--components")
    ap.add_argument("--variables")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    audits = [json.loads(Path(p).read_text()) for p in a.audit]
    comps = json.loads(Path(a.components).read_text())["components"] if a.components else []
    variables = json.loads(Path(a.variables).read_text()) if a.variables else {"collections": []}

    tokens = {}

    def tok(kind, value):
        key = (kind, value)
        if key not in tokens:
            tokens[key] = Token(kind, value)
        return tokens[key]

    wip_bound = Counter()
    for au in audits:
        for value, e in au["colors"].items():
            t = tok("color", value)
            t.n += e["n"]
            t.roles.update(e.get("role", {}))
            t.examples += e["ex"]
            for label, c in {**e.get("bound", {}), **e.get("style", {})}.items():
                is_wip, nm = strip_collection(label)
                (t.wip if is_wip else t.names)[nm] += c
                wip_bound[nm] += c if is_wip else 0
                t.evidence = True
        for key, e in au["numbers"].items():
            kind, value = key.split(":")
            t = tok(kind, float(value))
            t.n += e["n"]
            t.roles.update(e.get("prop", {}))
            t.examples += e["ex"]
            for label, c in e.get("bound", {}).items():
                is_wip, nm = strip_collection(label)
                (t.wip if is_wip else t.names)[nm] += c
                wip_bound[nm] += c if is_wip else 0
                t.evidence = True
        for key, e in au["type"].items():
            family, style, size, lh, ls = key.split("|")
            t = tok("type", key)
            t.n += e["n"]
            t.examples += e["ex"]
            for label, c in e.get("style", {}).items():
                t.names[label] += c
                t.evidence = True
            for kind, value in (("fontFamily", family), ("fontSize", float(size)), ("fontWeight", float(WEIGHTS.get(style, 400)))):
                sub = tok(kind, value)
                sub.n += e["n"]
                sub.examples += e["ex"]
                for label, c in e.get("bound", {}).items():
                    if kind == "fontSize":
                        sub.names[label] += c
                        sub.evidence = True
        for key, e in au["effects"].items():
            t = tok("effect", key)
            t.n += e["n"]
            t.examples += e["ex"]
            if key.startswith(("blur:", "bg-blur:")):
                sub = tok("effect", float(key.split(":")[1]))
                sub.n += e["n"]
        for label, e in au["internal"].items():
            is_wip, nm = strip_collection(label)
            props = e.get("props", {})
            kind = kind_of_prop(max(props, key=props.get)) if props else "unknown"
            for value, c in e["values"].items():
                if kind == "color" or str(value).startswith("#"):
                    t = tok("color", value)
                elif kind in ("fontFamily", "fontStyle"):
                    continue  # recorded by property name, not value; the type tuples carry these
                else:
                    try:
                        t = tok(kind, float(value))
                    except ValueError:
                        continue
                t.internal += c
                t.internal_roles.update({p: c for p in props})
                (t.wip if is_wip else t.names)[nm] += c
                t.evidence = True

    # Local variables: every value is evidence, but unused ones are listed, not proposed.
    wip_vars = []
    for col in variables.get("collections", []):
        for name, vtype, values, scopes, *_ in col["variables"]:
            value = values[0]
            used = wip_bound.get(name, 0)
            wip_vars.append({"collection": col["name"], "name": name, "type": vtype, "value": value, "boundUses": used})
            if used and vtype == "COLOR":
                tok("color", value).wip[name] += 0

    # Drift: attach unbound, nearby values to tokens with evidence.
    anchors = [t for t in tokens.values() if t.evidence]
    drifted = set()
    for t in sorted(tokens.values(), key=lambda t: -t.n):
        if t.evidence or t.kind in ("type",):
            continue
        cands = []
        for a_ in anchors:
            if a_.kind != t.kind:
                continue
            if t.n * 3 > a_.n + a_.internal:
                continue  # too common to be a slip: a token of its own
            if t.kind == "color":
                d = delta_e(t.value, a_.value)
                if d < DE_DRIFT:
                    cands.append((d, a_))
            elif isinstance(t.value, float) and isinstance(a_.value, float) and 0 < abs(t.value - a_.value) <= 1:
                cands.append((abs(t.value - a_.value), a_))
        if not cands:
            anchors.append(t)  # a raw value that stands on its own; later slips can attach to it
            continue
        best_d = min(d for d, _ in cands)
        tied = [x for d, x in cands if d - best_d <= DE_TIE]
        # Drift is an authoring slip, so a near tie goes to the value designers place most.
        target = max(tied, key=lambda x: (x.n, x.internal))
        target.drift.append({"value": t.value, "uses": t.n, "examples": t.examples[:4], "distance": round(best_d, 2),
                             "alternatives": [x.value for x in tied if x is not target]})
        drifted.add((t.kind, t.value))

    proposals = [t for t in tokens.values() if (t.kind, t.value) not in drifted]
    order = {"color": 0, "spacing": 1, "radius": 2, "stroke": 3, "effect": 4, "type": 5, "fontFamily": 6, "fontSize": 7, "fontWeight": 8, "lineHeight": 9}
    proposals.sort(key=lambda t: (order.get(t.kind, 10), -(t.n + t.internal)))
    token_json = [t.as_json(f"t{i + 1}") for i, t in enumerate(proposals)]

    # WIP mapping: a used WIP variable maps to the library name on its token, picking the
    # name whose words fit the WIP name or how it's used.
    def best_library_name(t, wip_name):
        if not t.names:
            return None
        w = words(wip_name)
        fits = [n for n in t.names if stem_overlap(w, words(n))]
        pool = fits or list(t.names)
        return max(pool, key=lambda n: t.names[n])

    wip_map = []
    for v in wip_vars:
        if not v["boundUses"]:
            wip_map.append({**v, "mapsTo": None, "status": "unused: bound nowhere in the audited files"})
            continue
        t = next((t for t in proposals if v["name"] in t.wip), None)
        target = best_library_name(t, v["name"]) if t else None
        wip_map.append({**v, "mapsTo": target, "token": t.value if t else None,
                        "status": "maps to a library token" if target else "no library token with this value"})

    # Components.
    instances = Counter()
    for au in audits:
        for name, e in au["instances"].items():
            instances[name] += e["n"]
    groups = defaultdict(lambda: {"nodes": [], "keys": set(), "frames": set()})
    for au in audits:
        for d in au["detached"]:
            g = groups[d["name"]]
            g["nodes"].append(d["id"])
            if d.get("key"):
                g["keys"].add(d["key"])
            g["frames"].add(d["frame"])
    structures = [s for au in audits for s in au["structures"]]
    candidates = []
    for name, g in sorted(groups.items(), key=lambda kv: -len(kv[1]["nodes"])):
        live = instances.get(name, 0)
        shapes = [s for s in structures if set(s["ids"]) & set(g["nodes"])]
        candidates.append({"name": name, "source": "detached copies", "detached": len(g["nodes"]), "liveInstances": live,
                           "status": "published, but detached in places" if live else "de facto: only detached copies, no live instances",
                           "componentKeys": sorted(g["keys"]), "frames": sorted(g["frames"]), "nodes": g["nodes"],
                           "structureMatches": [s["sig"] for s in shapes][:2]})
    covered = {i for c in candidates for i in c["nodes"]}
    for s in structures:
        ids = set(s["ids"])
        # Skip patterns already covered, and parts that only occur inside detached copies
        # (a detached Switch Field's inner row): the copy they sit in is the candidate.
        if ids & covered or s.get("insideDetached", 0) >= s["n"] or s["detached"]:
            continue
        name = max(s["names"], key=s["names"].get)
        same = next((c for c in candidates if c["source"] == "repeated structure" and c["name"] == name), None)
        if same:
            same["repeats"] = max(same["repeats"], s["n"])
            same["nodes"] = sorted(set(same["nodes"]) | ids)
            covered |= ids
            continue
        candidates.append({"name": name, "source": "repeated structure", "detached": 0, "liveInstances": 0,
                           "status": "de facto: a repeated pattern that isn't a component", "repeats": s["n"],
                           "names": s["names"], "nodes": s["ids"], "signature": s["sig"]})
        covered |= ids

    norm_sig = lambda s: s.replace("[]", "")
    local = []
    for c in comps:
        matches = []
        for s in structures:
            if norm_sig(s["sig"]) in (norm_sig(c["sig"]["full"]), norm_sig(c["sig"]["shell"])):
                for cand in candidates:
                    if set(cand["nodes"]) & set(s["ids"]) and cand["name"] not in matches:
                        matches.append(cand["name"])
        local.append({"name": c["name"], "id": c["id"], "page": c["page"], "status": c["status"],
                      "instancesInFile": c["instancesInFile"], "duplicates": matches,
                      "note": ("unused" if not c["instancesInFile"] else "in use") + (f"; looks like {', '.join(matches)}" if matches else "; matches no pattern in the audited files")})

    out = {"tokens": token_json, "wipVariables": wip_map, "components": candidates, "localComponents": local,
           "sources": [au.get("file") for au in audits]}
    od = Path(a.out)
    od.mkdir(parents=True, exist_ok=True)
    (od / "proposals.json").write_text(json.dumps(out, indent=1))
    write_md(od / "PROPOSALS.md", out)
    drift_n = sum(len(t["drift"]) for t in token_json)
    print(f"{len(token_json)} token proposals ({drift_n} drift values attached), {len(candidates)} component candidates, "
          f"{sum(1 for w in wip_map if w['mapsTo'])}/{len(wip_map)} WIP variables mapped, {len(local)} local components. Wrote {od / 'proposals.json'} and PROPOSALS.md.")


def fmt(v):
    return str(int(v)) if isinstance(v, float) and v.is_integer() else str(v)


def write_md(path, out):
    L = ["# Proposals", "", "Drafted by `propose.py` from the audit. Nothing here is approved yet: a person accepts, renames or rejects each line before anything is generated.", ""]
    L += ["## Tokens", "", "| Kind | Value | Suggested name | Uses (internal) | Drift absorbed |", "|---|---|---|---|---|"]
    for t in out["tokens"]:
        drift = ", ".join(f"{fmt(d['value'])} ×{d['uses']}" + (f" (or {', '.join(map(fmt, d['alternatives']))})" if d["alternatives"] else "") for d in t["drift"])
        L.append(f"| {t['kind']} | `{fmt(t['value'])}` | {t['suggestedName'] or '(none yet)'} | {t['uses']} ({t['internalUses']}) | {drift} |")
    L += ["", "## WIP variables", "", "| Variable | Value | Maps to | Status |", "|---|---|---|---|"]
    for w in out["wipVariables"]:
        L.append(f"| {w['name']} | `{fmt(w['value'])}` | {w['mapsTo'] or ''} | {w['status']} |")
    L += ["", "## Components", "", "| Candidate | Evidence | Status |", "|---|---|---|"]
    for c in out["components"]:
        ev = f"{c['detached']} detached, {c['liveInstances']} live" if c["source"] == "detached copies" else f"repeats {c['repeats']}×"
        L.append(f"| {c['name']} | {ev} | {c['status']} |")
    L += ["", "## Local components", "", "| Component | Status | Note |", "|---|---|---|"]
    for c in out["localComponents"]:
        L.append(f"| {c['name']} | {c['status'].lower()} | {c['note']} |")
    path.write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
