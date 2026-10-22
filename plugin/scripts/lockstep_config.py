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
