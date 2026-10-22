"""Fill a Lockstep script's placeholders and print code ready to pass as use_figma's `code`.

  render.py score --roots 7:922,7:1302
  render.py fix --roots 8:517,8:559
  render.py settle --roots 7:922,7:1302
  render.py inventory --keys keys.json --part components   (or variables, structure; --offset N resumes variables)
  render.py inventory --style-keys style-keys.json --part styles
  render.py inventory_local --part components [--pages 0:1,5:2]   (or variables)
  render.py audit --roots 0:1 [--offset 0]
  render.py variables --tokens generated/tokens/tokens.figma.json        (a draft only)
  render.py snapshot --spec components.json      (read-only: {name: example node id})
  render.py rebuild --spec snapshot.json         (a draft only)
  render.py score --roots 1:2 --local-library-page "Learned library"
  render.py path/to/build.js --which Profile,Account --version 2

Named scripts are the ones next to this file; anything else is a path to a build script.
Every script gets __PROTECTED_FILE_KEYS__ from lockstep_config, so a write script refuses to
run inside a protected file even if the hook isn't installed. Full-line comments are stripped
to save tokens. It exits non-zero if a placeholder is left unfilled or the code is over
use_figma's 50,000-character limit.

Read-only scripts (READONLY below) get a first line, `// lockstep-readonly {...}`, naming the
script and its filled-in values. The write guard re-renders from that line and lets the call
reach a protected file only if the result is identical, so learn can read an org's library
and product files while any other code, or an edited copy, stays blocked.
"""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from lockstep_config import ConfigError, protected_file_keys  # noqa: E402

CODE_LIMIT = 50_000
NAMED = ("score", "fix", "settle", "inventory", "inventory_local", "audit", "variables", "snapshot", "rebuild")
READONLY = ("score", "inventory_local", "audit", "snapshot")
MARKER = "// lockstep-readonly "


class RenderError(Exception):
    pass


def render(script, values):
    """Code for `script` (a NAMED script or a path) with `values` ({PLACEHOLDER: JSON text}) filled in."""
    path = HERE / f"{script}.js" if script in NAMED else Path(script)
    source = path.read_text()
    values = {"PROTECTED_FILE_KEYS": json.dumps(sorted(protected_file_keys())), **values}
    lines = [l for l in source.splitlines() if not l.strip().startswith("//")]
    code = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"
    for name, value in values.items():
        code = code.replace(f"__{name}__", value)
    missing = sorted(set(re.findall(r"__([A-Z_]+)__", code)))
    if missing:
        raise RenderError(f"{path.name} still needs: {', '.join(missing)}. See render.py --help.")
    if script in READONLY:
        stamp = {"script": script, "values": {k: v for k, v in values.items() if k != "PROTECTED_FILE_KEYS"}}
        code = MARKER + json.dumps(stamp, separators=(",", ":")) + "\n" + code
    if len(code) > CODE_LIMIT:
        raise RenderError(f"{path.name} renders to {len(code):,} characters, over use_figma's {CODE_LIMIT:,} limit. Build fewer frames per call.")
    return code


def is_lockstep_readonly(code):
    """True only if `code` is exactly what render() produces for a read-only script."""
    if not isinstance(code, str) or not code.startswith(MARKER):
        return False
    try:
        stamp = json.loads(code[len(MARKER):code.index("\n")])
        script = stamp["script"]
        # Values must be plain JSON data, so a value can't smuggle code into the script.
        values = {str(k): json.dumps(json.loads(v)) for k, v in stamp["values"].items()}
    except (ValueError, KeyError, TypeError, AttributeError):
        return False
    if script not in READONLY or "PROTECTED_FILE_KEYS" in values:
        return False
    try:
        return render(script, values) == code
    except (RenderError, ConfigError, OSError):
        return False


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script", help=" | ".join(NAMED) + " | path to a build script")
    ap.add_argument("--roots", help="comma-separated node IDs: frames, or pages for audit")
    ap.add_argument("--keys", help="JSON file of {label: component or component set key} (inventory)")
    ap.add_argument("--part", choices=["components", "variables", "structure", "styles"], help="inventory part")
    ap.add_argument("--style-keys", help="JSON file of {label: style key} (inventory --part styles)")
    ap.add_argument("--pages", help="comma-separated page IDs (inventory_local; default all pages)")
    ap.add_argument("--offset", type=int, help="where to resume when a result says `next` (audit, inventory variables)")
    ap.add_argument("--tokens", help="generate.py's tokens.figma.json (variables)")
    ap.add_argument("--spec", help="JSON spec (snapshot: {name: node id}; rebuild: snapshot.js's result)")
    ap.add_argument("--local-library-page", help="score: count instances of components on this page of the same file as library instances (a learned draft library)")
    ap.add_argument("--which", help="comma-separated frame names (build scripts)")
    ap.add_argument("--version", type=int, help="canvas row for this pass (build scripts)")
    args = ap.parse_args()

    split = lambda s: [x.strip() for x in s.split(",") if x.strip()]
    values = {}
    if args.roots:
        values["ROOT_IDS"] = json.dumps(split(args.roots))
    if args.keys:
        values["COMPONENT_KEYS"] = json.dumps(json.loads(Path(args.keys).read_text()))
    if args.script == "inventory":
        values["STYLE_KEYS"] = json.dumps(json.loads(Path(args.style_keys).read_text()) if args.style_keys else {})
        values.setdefault("COMPONENT_KEYS", "{}")
    if args.part:
        values["PART"] = json.dumps(args.part)
    if args.script == "inventory_local":
        values["PAGE_IDS"] = json.dumps(split(args.pages) if args.pages else [])
    if args.script in ("audit", "inventory"):
        values["OFFSET"] = json.dumps(args.offset or 0)
    if args.tokens:
        values["TOKENS"] = json.dumps(json.loads(Path(args.tokens).read_text()))
    if args.spec:
        values["SPEC"] = json.dumps(json.loads(Path(args.spec).read_text()))
    if args.script == "score":
        values["LOCAL_LIBRARY_PAGE"] = json.dumps(args.local_library_page or "")
    if args.which:
        values["WHICH"] = json.dumps(split(args.which))
    if args.version is not None:
        values["VERSION"] = str(args.version)

    try:
        code = render(args.script, values)
        protected = protected_file_keys()
    except (RenderError, ConfigError) as e:
        sys.exit(str(e))
    if not protected:
        print("Warning: no protected file keys are configured, so nothing guards the library. See the skill's setup step.", file=sys.stderr)
    sys.stdout.write(code)


if __name__ == "__main__":
    main()
