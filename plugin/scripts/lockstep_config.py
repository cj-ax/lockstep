"""Protected Figma file keys for Lockstep: files nothing may write to (usually the org's
published library). Shared by the write-guard hook and render.py.

Keys are merged from three places, so a team can set them once and a person can add more:
  1. LOCKSTEP_PROTECTED_FILE_KEYS, comma-separated
  2. ~/.claude/lockstep.json
  3. <project>/.claude/lockstep.json (project = CLAUDE_PROJECT_DIR, else the working directory)

Each file looks like:
  {"protectedFileKeys": {"LMgKpbsEmxRpiHBKd9YGlw": "Official [Business@Slalom] Design System"}}
A plain list of keys also works. A file that exists but can't be read raises ConfigError, so
the guard fails closed instead of silently protecting nothing.

From a shell:  python3 lockstep_config.py protect <fileKey> "<name>"   (adds to the project file)
               python3 lockstep_config.py list
"""
import json
import os
from pathlib import Path


class ConfigError(Exception):
    pass


def config_paths():
    project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    return [Path.home() / ".claude" / "lockstep.json", project / ".claude" / "lockstep.json"]


def protected_file_keys():
    """Return {file_key: name or None} for every protected file."""
    keys = {}
    for key in filter(None, (k.strip() for k in os.environ.get("LOCKSTEP_PROTECTED_FILE_KEYS", "").split(","))):
        keys[key] = None
    for path in config_paths():
        if not path.exists():
            continue
        try:
            entries = json.loads(path.read_text()).get("protectedFileKeys", {})
        except (OSError, ValueError, AttributeError) as e:
            raise ConfigError(f"Can't read {path}: {e}. Fix it, or remove it if you don't need it.")
        if isinstance(entries, list):
            entries = {k: None for k in entries}
        if not isinstance(entries, dict):
            raise ConfigError(f'{path}: "protectedFileKeys" must be an object or a list of file keys.')
        for k, name in entries.items():
            if name or k not in keys:
                keys[k] = name
    return keys


def protect(key, name, path=None):
    """Add a file key to <project>/.claude/lockstep.json (or `path`), keeping what's there."""
    path = Path(path) if path else config_paths()[1]
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text())
        except ValueError as e:
            raise ConfigError(f"Can't read {path}: {e}. Fix it before adding keys.")
    entries = data.get("protectedFileKeys", {})
    if isinstance(entries, list):
        entries = {k: None for k in entries}
    entries[key] = entries.get(key) or name
    data["protectedFileKeys"] = entries
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")
    return path, entries[key]


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 4 and sys.argv[1] == "protect":
        try:
            where, name = protect(sys.argv[2], sys.argv[3])
        except ConfigError as e:
            sys.exit(str(e))
        print(f"Protected {sys.argv[2]} ({name}) in {where}.")
    elif len(sys.argv) == 2 and sys.argv[1] == "list":
        for k, n in protected_file_keys().items():
            print(f"{k}  {n or ''}")
    else:
        sys.exit('Usage: lockstep_config.py protect <fileKey> "<name>"  |  lockstep_config.py list')
