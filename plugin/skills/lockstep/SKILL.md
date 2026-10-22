---
name: lockstep
description: Build a page, screen, form, dialog or other UI in Figma faithfully from the user's own design library (real library component instances with correct variants, every colour, spacing and radius bound to library variables, auto layout, nothing detached), then score the result and fix it until it passes. Also use to check how faithfully an existing Figma frame uses its library, or to clean one up. Trigger when the user wants something built "in Figma with our design system/library", asks whether a Figma design follows the library, mentions design-system faithfulness or token binding, or names Lockstep.
---

# Lockstep: faithful Figma builds from the org's own library

You build in Figma with the org's published library and prove it with a score. The loop is
**inventory → build → score + screenshot → fix → rescore**, and it ends when the score and the
screenshots both pass. Everything runs through the official Figma MCP's `use_figma` tool.

Scripts live in `scripts/` in this skill's directory (the base directory shown when the skill
loads; `$SKILL` below). `render.py` fills a script's placeholders and prints code to pass as
`use_figma`'s `code`; never hand-edit placeholders.

```bash
python3 "$SKILL/scripts/render.py" score --roots 7:922,7:1302
```

## The one hard rule: write only to drafts

Never write to the org's library file or any other protected file. Before **every** write call
(`use_figma`, `generate_figma_design`, `upload_assets`, ...), compare the target `fileKey` with the
protected keys. Three layers back this up: your check, the plugin's PreToolUse hook, and a
guard that `render.py` puts in every write script. Don't rely on the last two.

**Setup, once per org:** if `render.py` warns that no protected keys are configured, ask the
user for the library's file key (from its URL: `figma.com/design/<fileKey>/...`) and write it to
`.claude/lockstep.json` in their project (or `~/.claude/lockstep.json` for all projects):

```json
{ "protectedFileKeys": { "<fileKey>": "<library name>" } }
```

## Before you start

1. Load Figma's skills: `/figma-use` and `/figma-generate-design`. If they aren't installed as
   skills, read them as MCP resources (`skill://figma/figma-use/SKILL.md`,
   `skill://figma/figma-generate-design/SKILL.md`). Pass their names in `skillNames`.
2. Pick the target: the user's draft (check its key isn't protected), or a new file from
   `create_new_file` (call `whoami` for the `planKey`). Then `create_session` on it and pass the
   `sessionId` on every call.

## 1. Find the library's components and tokens

- `get_libraries` may not list the org's library. Get its `libraryKey` from any
  `search_design_system` result instead.
- Search once, batched, one intent per query, with `includeLibraryKeys` and
  `disableCodeConnect: true`. Search the parts the page needs (button, text field, switch, tabs,
  card, dialog, header, heading/text) and a few token names (background, space, radius).
- Results can run to 100K+ characters. When the tool saves output to a file, parse it with
  Python or `jq`: keep only results from the org's library, with name, asset type and key. Don't
  read it raw.
- Save `{label: key}` to a keys file in the user's project, for example `lockstep/keys.<library>.json`.

## 2. Inventory: read the library itself

Search results have no variant names and no token values. The Plugin API has both. Run each
part (it's two calls because of the 48 KB return limit); importing by key works even when the
library isn't added to the draft:

```bash
python3 "$SKILL/scripts/render.py" inventory --keys lockstep/keys.<library>.json --part components
python3 "$SKILL/scripts/render.py" inventory --keys lockstep/keys.<library>.json --part variables
```

From the results, note:
- each component's variant axes, boolean, text and instance-swap properties, slots, default
  size, and its description's usage rules;
- token names, keys and values: colour (by role: background, text, border), spacing, radius,
  stroke, and text styles;
- whether the library has text components (title, heading, body). If it has none, styled text
  layers are allowed, and they cap the instance share below 100%.

If two components could serve a part, or the library and the user's code disagree (button
casing, which button variant means Cancel), ask the user rather than guessing.

## 3. Build

Write a build script for this page in the user's project. Start from the closer example in
`references/examples/`: `build-settings-slalom.js` for a library with slot-based cards and no
text components, `build-settings-sds.js` for one with text components and a Button Group.
**Read `references/build-patterns.md` before writing it**: it lists the helpers and the traps
that broke earlier builds.

Rules for the build:
- Every visible part is a library instance with explicit variant properties. Draw nothing the
  library has.
- Bind every fill, stroke, padding, gap and radius on frames you create to a library variable.
  Use library text components, or else a library text style plus a bound colour variable.
- Use auto layout everywhere. Never detach an instance. Put content into slots by appending.
- Replace every piece of sample text ("Button", "Label", "Title").
- One top-level frame per screen, named `<Page> / <Screen> / v<VERSION>`. Each pass goes on its
  own canvas row, and the script removes a frame with the same name first, so it's safe to retry.

```bash
python3 "$SKILL/scripts/render.py" lockstep/build-<page>.js --which Profile,Account --version 1
```

## 4. Score, and look

```bash
python3 "$SKILL/scripts/render.py" score --roots <frame ids from the build>
```

The score is read-only. It reports five percentages and a headline faithfulness score (their
mean). Detached and hard-coded colours are inverted in the mean.

| Measure | Pass |
|---|---|
| Library instances (of content nodes) | at the library's ceiling: 100% if it has text components |
| Bound properties | 100% (95% at the very least) |
| Detached instances | 0% |
| Hard-coded colours | 0% |
| Auto layout | 100% |
| **Integrity issues** (clipped content or text, sample text) | **0** |

Then take a screenshot of every frame (`get_screenshot`) and look at each one. A frame can
score 100 and still be broken. Both test builds did: a button still read "Button", and text was
cut off mid-word. If you see a defect the score missed, fix the build, and say what the scorer
should learn.

## 5. Fix, then rescore

- **Build problems** (wrong component, clipped content, sample text, broken layout): fix the
  build script, run it with `--version` one higher, then score and screenshot again.
- **Raw values on someone else's frame:** clone it first, then run
  `render.py fix --roots <clone ids>`. It binds only values that exactly match a library token,
  so nothing changes visually. It lists the rest as decisions.
- **Decisions** (a 48px gap with no token, a scrim colour the library lacks): ask the user. Don't
  snap to the nearest token silently.

Stop when every measure passes and the screenshots are clean, or after three passes. Then
report what's left.

## 6. Report

Give the user:
- the draft link;
- the scores before and after each pass, as a table;
- what each pass fixed;
- decisions still open;
- library gaps worth telling the design-system team (missing tokens, components that clip,
  confusing defaults).

Say plainly if any frame isn't done.

## Scoring an existing design only

Skip steps 1–3. Run step 4 on the user's frames, and step 5's `fix` on a clone if they want the
tokens bound. Don't modify their originals.
