# Lockstep (working name)

An org-agnostic tool for writing to Figma faithfully with an organization's own design library,
then scoring and fixing the result. It started as a spike on the Business@Slalom library and was
then tested on Figma's Simple Design System. Results are in [REPORT.md](REPORT.md).

## Use it

Lockstep ships as a Claude Code plugin in [`plugin/`](plugin/README.md) with four commands:
`lockstep:init` (set up a library), `lockstep:build` (build a page and loop until it passes),
`lockstep:score` (measure any frame, read-only) and `lockstep:fix` (bind raw values to tokens).
It also has a write guard for protected library files.

To try it, follow **Start here** in [plugin/README.md](plugin/README.md): connect Figma, install
the plugin, then tell Claude "Set up Lockstep for our design library" with a link. To work on
Lockstep itself, `claude --plugin-dir ./plugin` loads your local copy.

## Layout

| Path | What it is |
|---|---|
| `plugin/skills/{init,build,score,fix}/` | The four commands; `build` also holds the build patterns and the example builds |
| `plugin/scripts/` | Shared scripts: `inventory.js`, `score.js` and `fix.js`, plus `render.py`, which fills their placeholders |
| `plugin/hooks/` | The write guard (PreToolUse) |
| `site/` | The companion site: `index.html` (one self-contained page), its images exported from the Figma drafts, and `NOTES.md` from studying impeccable.style |
| `research/` | Raw search output and notes from the Slalom spike, and the fresh-agent trial's artefacts |
| `REPORT.md` | Scores, what the Figma MCP can and can't do, and the gaps |
