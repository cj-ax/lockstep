"""Reconcile design and code for lockstep:learn: a coverage matrix and the conflicts to rule on.

Design comes from either a published library's inventory (lockstep:init's
inventory.components.json and inventory.variables.json) or learn's proposals.json. Code comes
from harvest_code.py's code.json, or is absent. Writes coverage.json and COVERAGE.md.

  python3 reconcile.py --components inventory.components.json --variables inventory.variables.json --code code.json --out <folder>
  python3 reconcile.py --proposals proposals.json [--code code.json] --out <folder>

Every token, type style and component gets one status:
  complete     in design and code, and the values agree in every mode both sides have
  drift        the same thing on both sides (by name), but the values differ
  design-only  in Figma, with nothing in code that has its value or its name
  code-only    in code, with nothing in Figma that has its value or its name
  de facto     (proposals only) a repeated or detached pattern that no component covers

Matching. Tokens are compared within a kind (colour, spacing, radius, ...). A design token
matches the code token with the same value in every shared mode, preferring the closest name;
failing that, a code token with the same name words is drift. Many design tokens can match
one code token (Figma's pa-2, px-2 and ga-2 are all code's space-2). Modes pair with themes by
name (Light with slalomLight). Letter spacing in percent is converted with the font size.
Components match by name after dropping prefixes (SButton, v-avatar) and known synonyms
(modal = dialog, toggle = switch), then their variant axes are compared value by value.
"""
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

STOP = {"slm", "color", "colors", "variables", "variable", "semantic", "updated", "theme", "the", "font", "var", "tokens", "token", "value", "mode", "uniform"}
WEIGHTS = {"thin": 100, "extra light": 200, "light": 300, "regular": 400, "medium": 500, "semi bold": 600, "semibold": 600, "bold": 700, "extra bold": 800, "black": 900}
SYNONYMS = {"modal": "dialog", "dialog": "dialog", "switchtoggle": "switch", "toggle": "switch", "textfield": "textfield", "inputtextfield": "textfield",
            "input": "textfield", "singleselect": "select", "dropdown": "select", "accordionrow": "expansionpanel", "accordion": "expansionpanels",
            "expansionpanel": "expansionpanel", "statusalertbar": "alert", "toastnotifications": "toast", "snackbar": "toast",
            "loading": "progressring", "spinner": "progressring", "step": "stepper", "emptystate": "emptystate", "semanticbuttons": "button",
            "datepicker": "datepicker", "radiobutton": "radio", "avatar": "avatar"}
INTERACTION = {"hover", "hovered", "pressed", "active", "focus", "focused", "disabled", "disable", "enabled", "enable", "default", "selected",
               "rest", "resting", "sync", "loading", "input", "filled", "error", "current", "next", "completed"}


def words(name):
    name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    return [w for w in re.split(r"[^a-z0-9]+", name.lower()) if w and w not in STOP]


def leaf(name):
    """The token's own name: 'Color Semantic Variables (updated)/Font Colors/text-error' -> 'text-error'."""
    return re.split(r"[/.]", name)[-1]


def name_sim(a, b):
    wa, wb = set(words(leaf(a))), set(words(leaf(b)))
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def delta_e(a, b):
    """OKLab distance x100, with alpha difference counted on the same scale."""
    def lab(h):
        r, g, bl = (_lin(int(h[i:i + 2], 16)) for i in (1, 3, 5))
        l, m, s = ((0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * bl) ** (1 / 3), (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * bl) ** (1 / 3),
                   (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * bl) ** (1 / 3))
        return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s, 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
                0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)
    alpha = lambda h: int(h[7:9], 16) / 255 if len(h) == 9 else 1.0
    if not (a.startswith("#") and b.startswith("#")):
        return 999.0
    return 100 * (sum((x - y) ** 2 for x, y in zip(lab(a), lab(b))) ** 0.5) + 100 * abs(alpha(a) - alpha(b))


def same(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) < 0.011
    if isinstance(a, str) and isinstance(b, str):
        return a.lower() == b.lower()
    return False


# --- design side -----------------------------------------------------------------------------
BIND_KIND = [("fills", "color"), ("strokes", "color"), ("textRangeFills", "color"), ("padding", "spacing"), ("itemSpacing", "spacing"),
             ("radius", "radius"), ("stroke", "stroke"), ("fontWeight", "fontWeight"), ("fontSize", "fontSize"), ("effects", "effect")]


def design_kind(name, value, binds):
    if isinstance(value, str) and value.startswith("#"):
        return "color"
    for b, k in BIND_KIND:
        if b in binds:
            return k
    n = name.lower()
    for k, ws in (("radius", ("radius",)), ("spacing", ("space", "padding", "gap", "pa-", "px-", "ga-")), ("stroke", ("border",)),
                  ("fontWeight", ("weight",)), ("effect", ("elevation", "shadow"))):
        if any(w in n for w in ws):
            return k
    return "number" if isinstance(value, (int, float)) else "text"


def parse_text_style(name, spec):
    # "Slalom Sans Bold 20 / 32px / 0.15%"
    head, lh, ls = (spec.split(" / ") + ["", ""])[:3]
    m = re.match(r"(.+?) ((?:Extra |Semi )?(?:Thin|Light|Regular|Medium|Bold|Black|SemiBold))\s+([\d.]+)$", head)
    if not m:
        return None
    size = float(m.group(3))

    def px(v):
        if v.endswith("%"):
            return round(float(v[:-1]) * size / 100, 3)
        return None if v in ("", "auto") else round(float(v.rstrip("px")), 3)
    return {"name": name, "fontFamily": m.group(1), "fontWeight": WEIGHTS.get(m.group(2).lower(), 400), "fontSize": size,
            "lineHeight": px(lh) if not lh.endswith("%") else round(float(lh[:-1]) * size / 100, 3), "letterSpacing": px(ls)}


def load_inventory(components_path, variables_path):
    tokens, styles, effects = [], [], []
    v = json.loads(Path(variables_path).read_text()) if variables_path else {"collections": {}, "styles": []}
    for col, rows in v["collections"].items():
        cname = col.split(" [")[0].strip()
        for row in rows:
            name, key, value, binds = row[:4]
            modes = row[4] if len(row) > 4 else {"default": value}
            if value is None or isinstance(value, dict):
                continue
            tokens.append({"name": f"{cname}/{name}", "kind": design_kind(name, value, binds), "values": modes, "binds": binds, "key": key})
    seen = set()
    for typ, name, key, spec in v.get("styles") or []:
        if name in seen:
            continue
        seen.add(name)
        if typ == "TEXT":
            s = parse_text_style(name, spec)
            if s:
                styles.append(s)
        elif typ == "EFFECT" and spec:
            effects.append({"name": name, "kind": "effect", "values": {"default": spec}, "binds": "style"})
    comps = []
    for c in json.loads(Path(components_path).read_text())["components"] if components_path else []:
        props = {k.split("#")[0]: val for k, val in c["props"].items()}
        comps.append({"name": c["name"], "label": c.get("label"), "axes": {k: val for k, val in props.items() if isinstance(val, list)},
                      "props": props, "description": c.get("description", "")})
    return tokens + effects, styles, comps


def load_proposals(path):
    p = json.loads(Path(path).read_text())
    tokens, styles, comps = [], [], []
    for t in p["tokens"]:
        if t["kind"] == "type":
            family, style, size, lh, ls = t["value"].split("|")
            size = float(size)
            styles.append({"name": t["suggestedName"] or t["value"], "fontFamily": family, "fontWeight": WEIGHTS.get(style.lower(), 400), "fontSize": size,
                           "lineHeight": round(float(lh[:-1]) * size / 100, 3) if lh.endswith("%") else (None if lh == "auto" else float(lh[:-2])),
                           "letterSpacing": round(float(ls[:-1]) * size / 100, 3) if ls.endswith("%") else (0.0 if ls == "0" else float(ls.rstrip("px")))})
        else:
            tokens.append({"name": t["suggestedName"] or f"{t['kind']} {t['value']}", "kind": "effect" if t["kind"] == "effect" else t["kind"],
                           "values": {"default": t["value"]}, "binds": "proposal", "uses": t["uses"]})
    for c in p["components"]:
        comps.append({"name": c["name"], "axes": {}, "props": {}, "description": "", "status": c["status"]})
    return tokens, styles, comps


# --- matching ---------------------------------------------------------------------------------
def mode_pairs(dvalues, cvalues):
    """[(design mode, code theme)] that describe the same theme."""
    dm, ct = list(dvalues), list(cvalues)
    if len(dm) == 1 or len(ct) == 1:
        # A single-mode side compares with the other side's light/default/first theme.
        def primary(names):
            return next((n for n in names if "light" in n.lower() or n == "default"), names[0])
        return [(primary(dm), primary(ct))]
    pairs = []
    for m in dm:
        w = [x for x in words(m) if x != "mode"]
        # earlier words weigh more: 'BuildDark' is a build theme first
        score = lambda t: sum(2 ** -i for i, x in enumerate(w) if x in t.lower())
        t = max(ct, key=score)
        if score(t) > 0:
            pairs.append((m, t))
    return pairs


def compare(d, c):
    pairs = mode_pairs(d["values"], c["values"])
    diffs = [(m, t, d["values"][m], c["values"][t]) for m, t in pairs if not same(d["values"][m], c["values"][t])]
    return pairs, diffs


KIND_GROUP = {"letterSpacing": "letterSpacing", "lineHeight": "lineHeight", "fontSize": "fontSize", "fontWeight": "fontWeight"}


def reconcile_tokens(dtokens, ctokens):
    rows = []
    used_code = Counter()
    by_kind = defaultdict(list)
    for c in ctokens:
        by_kind[c["kind"]].append(c)
    for d in dtokens:
        cands = by_kind.get(d["kind"], [])
        exact = []
        for c in cands:
            pairs, diffs = compare(d, c)
            if pairs and not diffs:
                exact.append((name_sim(d["name"], c["name"]), c))
        if exact:
            sim, c = max(exact, key=lambda x: x[0])
            for _, x in exact:
                used_code[x["name"]] += 1  # every code token with this value is covered, not just the best-named
            rows.append({"status": "complete", "kind": d["kind"], "design": d["name"], "code": c["name"], "values": d["values"],
                         "nameMatch": sim > 0, "alsoMatches": [x["name"] for s, x in exact if x is not c][:4]})
            continue
        # Drift: the same thing by name, with values of the same type that differ. The name must
        # match word for word, or closely with at least one mode agreeing (light the same, dark not).
        named = []
        for c in cands:
            sim = name_sim(d["name"], c["name"])
            pairs, diffs = compare(d, c)
            if not pairs or not diffs or any(type(dv) is not type(cv) for _, _, dv, cv in diffs):
                continue
            if sim == 1.0 or (sim >= 0.5 and len(diffs) < len(pairs)):
                named.append((sim, c))
        if named:
            sim, c = max(named, key=lambda x: x[0])
            pairs, diffs = compare(d, c)
            if pairs:
                used_code[c["name"]] += 1
                rows.append({"status": "drift", "kind": d["kind"], "design": d["name"], "code": c["name"],
                             "differences": [{"designMode": m, "codeTheme": t, "design": dv, "code": cv} for m, t, dv, cv in diffs]})
                continue
        row = {"status": "design-only", "kind": d["kind"], "design": d["name"], "values": d["values"]}
        if d["kind"] == "color":
            # a near miss is worth a reviewer's look: 87% black in code vs 90% in Figma
            near = []
            for c in cands:
                pairs, diffs = compare(d, c)
                if pairs and all(isinstance(dv, str) and isinstance(cv, str) for _, _, dv, cv in diffs):
                    dist = max(delta_e(dv, cv) for _, _, dv, cv in diffs)
                    if dist < 3:
                        near.append((dist, c["name"]))
            if near:
                row["nearest"] = min(near)[1]
        rows.append(row)
    for c in ctokens:
        if not used_code[c["name"]]:
            rows.append({"status": "code-only", "kind": c["kind"], "code": c["name"], "values": c["values"], "uses": c.get("uses")})
    return rows


def type_key(name):
    w = words(name.replace("btn", "button"))
    return " ".join(x for x in w if x not in ("upcase", "ttlcase", "uppercase", "titlecase"))


def reconcile_type(dstyles, cstyles):
    rows, matched = [], set()
    for d in dstyles:
        c = next((c for c in cstyles if type_key(c["name"]) == type_key(d["name"])), None)
        if not c:
            c = next((c for c in cstyles if all(same(c.get(f), d.get(f)) for f in ("fontSize", "fontWeight", "lineHeight"))), None)
        if not c:
            rows.append({"status": "design-only", "kind": "type", "design": d["name"], "values": d})
            continue
        matched.add(c["name"])
        diffs = [{"field": f, "design": d.get(f), "code": c.get(f)} for f in ("fontSize", "fontWeight", "lineHeight", "letterSpacing")
                 if d.get(f) is not None and c.get(f) is not None and not same(d[f], c[f])]
        rows.append({"status": "drift" if diffs else "complete", "kind": "type", "design": d["name"], "code": c["name"], "differences": diffs,
                     "codeCase": c.get("textCase"), "values": d})
    for c in cstyles:
        if c["name"] not in matched:
            rows.append({"status": "code-only", "kind": "type", "code": c["name"], "values": c})
    return rows


def comp_key(name):
    n = re.sub(r"^(S|V|Mui|Ant|Chakra)(?=[A-Z])", "", name)
    n = re.sub(r"^v-", "", n)
    n = re.sub(r"[^a-z0-9]", "", n.lower())
    return SYNONYMS.get(n, n)


def norm_value(v, *contexts):
    """A variant value without the words it shares with its axis, prop or component name:
    'label in' on axis 'type' vs 'in' on prop 'labelType'; 'Error Toast' vs 'error'."""
    drop = {w for c in contexts for w in words(c)} | {"button"}
    ws = [w for w in words(v.replace("_button", "")) if w not in drop] or words(v)
    v = "-".join(ws)
    return {"disable": "disabled", "enable": "enabled", "default": "enabled", "information": "info", "informative": "info"}.get(v, v)


def values_match(dv, cv):
    """Shared normalized values, allowing a prefix ('info' / 'informative')."""
    both = set()
    for a in dv:
        for b in cv:
            if a == b or (min(len(a), len(b)) >= 3 and (a.startswith(b) or b.startswith(a))):
                both.add((a, b))
    return both


BOOLEAN = {"true", "false", "on", "off", "yes", "no"}


def casing(d):
    """Figma's default label case, from boolean props such as 'title case' / 'uppercase'."""
    for k, v in d["props"].items():
        if isinstance(v, str) and v.startswith("BOOLEAN=true") and re.search(r"case", k, re.I):
            return k.strip().lower()
    return None


def reconcile_components(dcomps, ccomps):
    rows, used = [], set()
    by_key = defaultdict(list)
    for c in ccomps:
        by_key[comp_key(c["name"])].append(c)
    for d in dcomps:
        cs = by_key.get(comp_key(d["name"]), [])
        if not cs:
            rows.append({"status": "de facto" if str(d.get("status", "")).startswith("de facto") else "design-only", "design": d["name"], "designAxes": d["axes"]})
            continue
        c = cs[0]
        used.add(c["name"])
        props = {p["name"]: p for p in (c.get("props") or [])}
        ctx = (d["name"], c["name"])
        axes = []
        for axis, values in d["axes"].items():
            # Interaction states (hover, pressed, focused...) are styled in CSS, not passed as props.
            state = sum(any(w in INTERACTION for w in words(v)) for v in values) * 2 > len(values) and \
                any(w in {"hover", "hovered", "pressed", "focus", "focused", "active"} for v in values for w in words(v))
            boolean = {v.lower() for v in values} <= BOOLEAN
            cp, best = None, set()
            for p in props.values():
                if not p.get("values"):
                    continue
                dv = {norm_value(v, axis, p["name"], *ctx) for v in values}
                cv = {norm_value(v, axis, p["name"], *ctx) for v in p["values"]}
                both = values_match(dv, cv)
                # overlap must cover half the smaller side, so one shared word ('info') isn't enough
                if len(both) * 2 >= min(len(dv), len(cv)) and len(both) > len(best):
                    cp, best = p, both
            if not cp:
                cp = next((p for n, p in props.items() if comp_key(n) == comp_key(axis) or (state and "state" in n.lower())), None)
            if state or boolean or not cp or not cp.get("values"):
                note = ("interaction states: code styles these in CSS" + (f"; {cp['name']} previews {', '.join(cp['values'])}" if cp and cp.get("values") else "")) if state \
                    else (f"on/off: code prop {cp['name']}" if cp else "on/off in Figma; code has no matching prop") if boolean \
                    else (f"code prop {cp['name']} takes free values" if cp else "no matching code prop")
                axes.append({"axis": axis, "codeProp": cp["name"] if cp else None, "designOnly": values, "note": note})
                continue
            dv = {norm_value(v, axis, cp["name"], *ctx): v for v in values}
            cv = {norm_value(v, axis, cp["name"], *ctx): v for v in cp["values"]}
            pairs = values_match(set(dv), set(cv))
            matched_d, matched_c = {a for a, _ in pairs}, {b for _, b in pairs}
            axes.append({"axis": axis, "codeProp": cp["name"], "both": sorted(dv[a] for a in matched_d),
                         "designOnly": [dv[k] for k in sorted(set(dv) - matched_d)], "codeOnly": [cv[k] for k in sorted(set(cv) - matched_c)]})
        mismatched = [a for a in axes if (a.get("designOnly") or a.get("codeOnly")) and not a.get("note")]
        rows.append({"status": "drift" if mismatched else "complete", "design": d["name"], "code": c["name"], "codeFile": c["file"], "axes": axes,
                     "designCase": casing(d), "codeTextTransform": c.get("textTransform"), "codeFontFamilies": c.get("fontFamilies")})
    for key, cs in by_key.items():
        for c in cs:
            if c["name"] not in used:
                rows.append({"status": "code-only", "code": c["name"], "codeFile": c["file"], "props": [p["name"] for p in c.get("props") or []]})
    return rows


def conflicts_of(tokens, type_rows, comp_rows, dthemes, cthemes, dfamilies):
    out = []
    fonts, cases = defaultdict(set), {}
    for r in comp_rows:
        for f in r.get("codeFontFamilies") or []:
            if dfamilies and f.lower() not in {x.lower() for x in dfamilies}:
                fonts[f].add(r["code"])
        if r.get("designCase") and r.get("codeTextTransform"):
            dc, tt = r["designCase"], r["codeTextTransform"]
            if ("title" in dc or "sentence" in dc) and "uppercase" in tt and r["codeFile"] not in cases:
                cases[r["codeFile"]] = {"topic": f"{r['code']} label case", "design": f"{dc.title()} by default ({r['design']})",
                                        "code": f"text-transform: {', '.join(tt)} in {r['codeFile']}", "question": "Which casing is right for labels?"}
    if fonts:
        out.append({"topic": "Component fonts", "design": ", ".join(sorted(dfamilies)) + " in every text style",
                    "code": "; ".join(f"{f} hard-coded in {', '.join(sorted(cs))}" for f, cs in sorted(fonts.items(), key=lambda kv: -len(kv[1]))),
                    "question": "Should these components use the system font token instead?"})
    out += cases.values()
    for r in comp_rows:
        for a in r.get("axes", []):
            if a.get("note") or not (a.get("designOnly") or a.get("codeOnly")):
                continue
            out.append({"topic": f"{r['design']} {a['axis']}", "design": ", ".join(a.get("designOnly") or []) or "nothing extra",
                        "code": ", ".join(a.get("codeOnly") or []) or "nothing extra",
                        "question": f"Should Figma's {a['axis']} and code's {a['codeProp'] or 'props'} offer the same options?"})
    for r in tokens + type_rows:
        if r["status"] != "drift":
            continue
        diffs = r.get("differences") or []
        d = "; ".join(f"{x.get('designMode') or x.get('field')}: {x['design']}" for x in diffs)
        c = "; ".join(f"{x.get('codeTheme') or x.get('field')}: {x['code']}" for x in diffs)
        out.append({"topic": f"{leaf(r['design'])} / {r['code']}", "design": f"{r['design']}, {d}", "code": f"{r['code']}, {c}", "question": "Which value is right?"})
    extra = [t for t in cthemes if not any(w in t.lower() for m in dthemes for w in words(m) if w not in ("mode",))]
    if extra:
        out.append({"topic": "Themes", "design": f"modes: {', '.join(dthemes) or 'one'}", "code": f"themes: {', '.join(cthemes)}",
                    "question": f"Code has {', '.join(extra)} with no matching Figma mode. Should Figma get a mode for it?"})
    return out


def write_md(path, out, title):
    L = [f"# Coverage: {title}", "", "Drafted by `reconcile.py`. Statuses: complete (same in Figma and code), drift (same thing, different values), "
         "design-only, code-only, de facto (a pattern with no component). Conflicts need a person's ruling before anything is generated.", ""]
    L += ["| Area | Complete | Drift | Design-only | Code-only | De facto |", "|---|---|---|---|---|---|"]
    for area, rows in (("Components", out["components"]), ("Tokens", out["tokens"]), ("Type styles", out["typography"])):
        c = Counter(r["status"] for r in rows)
        L.append(f"| {area} | {c['complete']} | {c['drift']} | {c['design-only']} | {c['code-only']} | {c['de facto']} |")
    kinds = defaultdict(Counter)
    for r in out["tokens"]:
        kinds[r["kind"]][r["status"]] += 1
    L += ["", "Tokens by kind:", "", "| Kind | Complete | Drift | Design-only | Code-only |", "|---|---|---|---|---|"]
    for k, c in sorted(kinds.items(), key=lambda kv: -sum(kv[1].values())):
        L.append(f"| {k} | {c['complete']} | {c['drift']} | {c['design-only']} | {c['code-only']} |")
    L += ["", f"## Conflicts ({len(out['conflicts'])})", ""]
    for i, c in enumerate(out["conflicts"], 1):
        L.append(f"{i}. **{c['topic']}.** Figma: {c['design']}. Code: {c['code']}. {c['question']}")
    L += ["", "## Components", "", "| Figma | Code | Status | Variant differences |", "|---|---|---|---|"]
    for r in out["components"]:
        diff = "; ".join(f"{a['axis']} → {a['codeProp']}: " + ", ".join(x for x in (f"Figma only {', '.join(a['designOnly'])}" if a.get("designOnly") else "",
                                                                                      f"code only {', '.join(a['codeOnly'])}" if a.get("codeOnly") else "") if x)
                         for a in r.get("axes", []) if (a.get("designOnly") or a.get("codeOnly")) and not a.get("note"))
        if r["status"] == "code-only":
            diff = "props: " + ", ".join(r.get("props") or [])
        L.append(f"| {r.get('design', '')} | {r.get('code', '')} | {r['status']} | {diff} |")
    L += ["", "Interaction-state axes (hover, pressed, focused) and on/off axes aren't compared: code styles states in CSS. They're listed per component in coverage.json."]
    L += ["", "## Type styles", "", "| Figma | Code | Status | Differences |", "|---|---|---|---|"]
    for r in out["typography"]:
        diff = "; ".join(f"{x['field']} {x['design']} vs {x['code']}" for x in r.get("differences") or [])
        L.append(f"| {r.get('design', '')} | {r.get('code', '')} | {r['status']} | {diff} |")
    L += ["", "## Token drift", "", "| Figma | Code | Differences |", "|---|---|---|"]
    for r in out["tokens"]:
        if r["status"] == "drift":
            L.append(f"| {r['design']} | {r['code']} | " + "; ".join(f"{x['designMode']}/{x['codeTheme']}: {x['design']} vs {x['code']}" for x in r["differences"]) + " |")
    show = lambda v: ", ".join(f"{k}: {x}" for k, x in v.items()) if isinstance(v, dict) else str(v)
    L += ["", "## Code-only tokens", "", "| Token | Kind | Values | Uses in code |", "|---|---|---|---|"]
    for r in out["tokens"]:
        if r["status"] == "code-only":
            L.append(f"| `{r['code']}` | {r['kind']} | {show(r['values'])} | {'' if r.get('uses') is None else r['uses']} |")
    L += ["", "## Design-only tokens", "", "| Token | Kind | Values | Close code value |", "|---|---|---|---|"]
    for r in out["tokens"]:
        if r["status"] == "design-only":
            L.append(f"| {r['design']} | {r['kind']} | {show(r['values'])} |" + (f" nearly `{r['nearest']}` |" if r.get("nearest") else " |"))
    path.write_text("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--components")
    ap.add_argument("--variables")
    ap.add_argument("--proposals")
    ap.add_argument("--code")
    ap.add_argument("--title", default="design and code")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.proposals:
        dtokens, dstyles, dcomps = load_proposals(a.proposals)
    else:
        dtokens, dstyles, dcomps = load_inventory(a.components, a.variables)
    code = json.loads(Path(a.code).read_text()) if a.code else {"tokens": [], "typography": [], "components": [], "themes": []}
    ctokens = [t for t in code["tokens"] if t["kind"] in {d["kind"] for d in dtokens} | {"color", "spacing", "radius", "stroke", "effect", "fontWeight"}]
    dthemes = sorted({m for d in dtokens for m in d["values"] if m != "default"})
    out = {"tokens": reconcile_tokens(dtokens, ctokens), "typography": reconcile_type(dstyles, code["typography"]),
           "components": reconcile_components(dcomps, code["components"]), "designModes": dthemes, "codeThemes": code["themes"]}
    families = {s["fontFamily"] for s in dstyles if s.get("fontFamily")}
    out["conflicts"] = conflicts_of(out["tokens"], out["typography"], out["components"], dthemes, code["themes"], families)
    od = Path(a.out)
    od.mkdir(parents=True, exist_ok=True)
    (od / "coverage.json").write_text(json.dumps(out, indent=1))
    write_md(od / "COVERAGE.md", out, a.title)
    c = {k: Counter(r["status"] for r in out[k]) for k in ("components", "tokens", "typography")}
    print(f"components {dict(c['components'])}; tokens {dict(c['tokens'])}; type {dict(c['typography'])}; {len(out['conflicts'])} conflicts. Wrote {od / 'COVERAGE.md'}.")


if __name__ == "__main__":
    main()
