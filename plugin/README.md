# Lockstep plugin for Claude Code

Ask Claude to build a page in Figma "with our design system", and Lockstep makes it do that
faithfully. The page is built from your library's real component instances, with every colour,
spacing and radius bound to your library's variables and auto layout throughout. Then Claude
scores the result, fixes what fails, and shows you before and after.

It works with any organization's published Figma library. It has been tested on Business@Slalom
and on Figma's Simple Design System.

## What you need

- Claude Code (CLI, desktop app or IDE extension) with the official **Figma MCP server**
  connected and signed in, on a Figma seat that can create files.
- `python3` on your path. The scripts and the write guard use it.
- Your library's **file key**: the part after `/design/` in its URL.

## Install

From a clone of this repository:

```bash
claude --plugin-dir ./plugin
```

Or add it through your team's plugin marketplace once it's published there.

## Protect your library (do this first)

Lockstep only writes to draft files. List the files it must never write to, usually your
published library, in `.claude/lockstep.json` in your project. Use `~/.claude/lockstep.json`
to cover every project.

```json
{ "protectedFileKeys": { "LMgKpbsEmxRpiHBKd9YGlw": "Official [Business@Slalom] Design System" } }
```

You can also set `LOCKSTEP_PROTECTED_FILE_KEYS=key1,key2` in the environment. Keys from all
three places are combined.

Three layers enforce it:
1. A **PreToolUse hook** blocks any Figma write tool whose target names a protected file.
2. Every **write script** checks `figma.fileKey` inside Figma and refuses to run in a protected
   file.
3. Every **skill that writes** tells Claude to check the key before each write.

If a settings file exists but can't be read, every Figma write is blocked until you fix it, so a
typo can't quietly turn the protection off. The hook can't see which file Figma desktop has open,
so it doesn't cover the third-party figma-console MCP; don't run that against your library.

## Commands

Four skills. Claude picks the right one from what you ask, or you can name it.

| Command | What it does | Ask it like |
|---|---|---|
| `lockstep:init` | One-time setup per library. Protects the library file, finds its components and tokens, reads their variants, slots and values from Figma, and saves a summary to `lockstep/<library>/` in your project. | "Set up Lockstep for our design library: <figma link>" |
| `lockstep:build` | Builds a page in a draft from library instances and tokens, then scores, looks at screenshots and fixes until it passes. Runs `init` first if needed. | "Build our team members page in Figma with our design system" |
| `lockstep:score` | Read-only. Measures how faithfully any frame uses its library and lists the offending layers. | "How faithfully does this frame use our library? <link>" |
| `lockstep:fix` | Clones frames and binds raw values to exact-match library tokens, so nothing looks different. Then rescores and lists the values that have no token. | "Bind this design's spacing and colours to our tokens" |

## What "faithful" means here

| Measure | Pass |
|---|---|
| Library instances (share of content) | at your library's ceiling: 100% if it has text components |
| Properties bound to variables | 100% |
| Detached instances | 0% |
| Hard-coded colours | 0% |
| Auto layout | 100% |
| Integrity issues: clipped content or text, sample text left in | 0 |

Claude also looks at a screenshot of every frame, because the score can't judge everything.

## Contents

- `skills/init`, `skills/build`, `skills/score`, `skills/fix`: the four commands. `build` also
  holds the build-patterns reference and two worked example builds.
- `scripts/`: shared by all four.
  - `inventory.js` reads a library.
  - `score.js` scores frames.
  - `fix.js` binds raw values to exact-match tokens.
  - `settle.js` makes Figma re-lay-out library instances a script resized, so they render at
    their real size.
  - `render.py` fills a script's placeholders.
  - `lockstep_config.py` loads the protected keys.
- `hooks/`: the write guard.

## Known limits

- Finding components depends on `search_design_system`. Figma has no API to list every component
  in a library from another file.
- The build script is written fresh for each page and library; only scoring and fixing are
  generic. Expect a few passes on a new library.
- Usage judgement (which variant means Cancel, which casing to use) comes from your library's
  component descriptions. If they're thin, Claude asks you.
