"""PreToolUse hook: block Figma write tools aimed at a protected file (see lockstep_config.py).

The tool call arrives as JSON on stdin. If a protected file key appears in any of its input
fields (fileKey, URLs, ...), the call is blocked (exit 2, reason on stderr, which Claude sees).
The `code` field is skipped: Lockstep's rendered scripts carry the protected keys in their own
guard, and that guard checks figma.fileKey inside Figma. An unreadable config also blocks, so a
typo can't switch the protection off.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).parent.parent)) / "skills" / "lockstep" / "scripts"))
from lockstep_config import ConfigError, protected_file_keys  # noqa: E402


def main():
    try:
        call = json.load(sys.stdin)
    except ValueError:
        return 0  # Not a tool call we can read; nothing to guard.
    try:
        keys = protected_file_keys()
    except ConfigError as e:
        print(f"Blocked: Lockstep's write guard can't load its settings. {e}", file=sys.stderr)
        return 2
    tool_input = call.get("tool_input", {})
    fields = json.dumps({k: v for k, v in tool_input.items() if k != "code"} if isinstance(tool_input, dict) else tool_input)
    for key, name in keys.items():
        if key in fields:
            target = f"{name} (file key {key})" if name else f"file {key}"
            print(
                f"Blocked: this would write to {target}, which is protected. "
                "Lockstep only writes to draft files: create one with create_new_file, or use a copy in your Drafts.",
                file=sys.stderr,
            )
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
