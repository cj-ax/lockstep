"""Fill a Lockstep script's placeholders and print code ready to pass as use_figma's `code`.

  render.py score --roots 7:922,7:1302
  render.py fix --roots 8:517,8:559
  render.py inventory --keys keys.json --part components   (or variables, structure)
  render.py path/to/build.js --which Profile,Account --version 2

score, fix and inventory are the scripts next to this file; anything else is a path to a build
script. Every script gets __PROTECTED_FILE_KEYS__ from lockstep_config, so a write script
refuses to run inside a protected file even if the hook isn't installed. Full-line comments
are stripped to save tokens. It exits non-zero if a placeholder is left unfilled or the code
is over use_figma's 50,000-character limit.
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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script", help="score | fix | inventory | path to a build script")
    ap.add_argument("--roots", help="comma-separated frame node IDs (score, fix)")
    ap.add_argument("--keys", help="JSON file of {label: component or component set key} (inventory)")
    ap.add_argument("--part", choices=["components", "variables", "structure"], help="inventory part")
    ap.add_argument("--which", help="comma-separated frame names (build scripts)")
    ap.add_argument("--version", type=int, help="canvas row for this pass (build scripts)")
    args = ap.parse_args()

    path = HERE / f"{args.script}.js" if args.script in ("score", "fix", "inventory") else Path(args.script)
    source = path.read_text()

    try:
        protected = sorted(protected_file_keys())
    except ConfigError as e:
        sys.exit(str(e))
    values = {"PROTECTED_FILE_KEYS": json.dumps(protected)}
    if args.roots:
        values["ROOT_IDS"] = json.dumps([r.strip() for r in args.roots.split(",") if r.strip()])
    if args.keys:
        values["COMPONENT_KEYS"] = json.dumps(json.loads(Path(args.keys).read_text()))
    if args.part:
        values["PART"] = json.dumps(args.part)
    if args.which:
        values["WHICH"] = json.dumps([w.strip() for w in args.which.split(",") if w.strip()])
    if args.version is not None:
        values["VERSION"] = str(args.version)

    lines = [l for l in source.splitlines() if not l.strip().startswith("//")]
    code = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"
    for name, value in values.items():
        code = code.replace(f"__{name}__", value)
    missing = sorted(set(re.findall(r"__([A-Z_]+)__", code)))
    if missing:
        sys.exit(f"{path.name} still needs: {', '.join(missing)}. See render.py --help.")
    if len(code) > CODE_LIMIT:
        sys.exit(f"{path.name} renders to {len(code):,} characters, over use_figma's {CODE_LIMIT:,} limit. Build fewer frames per call.")
    if not protected:
        print("Warning: no protected file keys are configured, so nothing guards the library. See the skill's setup step.", file=sys.stderr)
    sys.stdout.write(code)


if __name__ == "__main__":
    main()
