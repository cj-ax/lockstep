# Lockstep (working name)

An org-agnostic tool for writing to Figma faithfully with an organization's own design library,
then scoring and fixing the result. It started as a spike on the Business@Slalom library and was
then tested on Figma's Simple Design System. Results are in [REPORT.md](REPORT.md).

## Use it

Lockstep ships as a Claude Code plugin in [`plugin/`](plugin/README.md): a `lockstep` skill that
runs the build → score → fix loop, plus a write guard for protected library files.

```bash
claude --plugin-dir ./plugin
```

Set your protected library keys before the first build. [plugin/README.md](plugin/README.md)
covers setup.

## Layout

| Path | What it is |
|---|---|
| `plugin/skills/lockstep/SKILL.md` | The workflow Claude follows |
| `plugin/skills/lockstep/scripts/` | The scripts: `inventory.js`, `score.js` and `fix.js`, plus `render.py`, which fills their placeholders |
| `plugin/skills/lockstep/references/` | Build patterns and traps; example builds for both test libraries, with their keys and the page brief |
| `plugin/hooks/` | The write guard (PreToolUse) |
| `research/` | Raw search output and notes from the Slalom spike |
| `REPORT.md` | Scores, what the Figma MCP can and can't do, and the gaps |
