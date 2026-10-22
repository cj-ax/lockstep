---
name: build
description: Build a page, screen, form, dialog or other UI in Figma faithfully from the organization's own design library. It uses real library component instances with correct variants, binds every colour, spacing and radius to library variables, uses auto layout throughout and detaches nothing. Then it scores the result and fixes it until it passes. Use when someone asks for something to be designed, mocked up or built in Figma "with our design system/library/components".
---

# lockstep:build: build a page from the library

The loop is **build → score + screenshot → fix → rescore**. It ends when the score and the
screenshots both pass.

Shared scripts live in the plugin's `scripts/` folder, two levels up from this skill's base
directory (shown when the skill loads). Below, `$LOCKSTEP` is that plugin folder, and `$BUILD`
is this skill's base directory.

## Write only to drafts

Lockstep never writes to the library or any other protected file. Before **every** Figma write
call (`use_figma`, `generate_figma_design`, `upload_assets`, ...), check that the target
`fileKey` isn't protected (`.claude/lockstep.json`, `~/.claude/lockstep.json`). A hook and the
rendered scripts check too; don't rely on them. Build in the user's draft or a new file from
`create_new_file`, never in the library.

## 0. Prerequisites

- `lockstep/<library-slug>/` must hold `keys.json`, the inventory files and `LIBRARY.md`. If
  it's missing, run **lockstep:init** first. If `inventory.structure.json` is missing, run
  that inventory part before writing the build: it shows where each component's text, icons
  and slots live.
- Load Figma's skills: `/figma-use` and `/figma-generate-design`, or the MCP resources
  `skill://figma/figma-use/SKILL.md` and `skill://figma/figma-generate-design/SKILL.md`.
- Call `create_session` on the target file and pass the `sessionId` on every call.

## Shell commands

Run each shell command as one simple command with literal paths: no `cd … &&` chains, no shell
variables, no heredocs. Claude Code's command checker refuses those, and both fresh-agent trials
lost turns to it. Write files with the Write tool.

## 1. Plan the page against the library

Read `LIBRARY.md`, then `$BUILD/references/build-patterns.md`. For each part of the page, pick
the library component and its exact variant values; a short table is enough. Then:

- If a part has no obvious component, search for it (`search_design_system`), add its key to
  `keys.json`, and rerun the components inventory for the new keys. Don't draw it while the
  library might have it.
- If the library truly lacks it, build it from library pieces: bound frames, text components
  or styles, icons. Name the layer `Not in library: <part>` and list it in the report.
- If two components fit, or the library disagrees with the user's code or brief, choose the
  one the descriptions recommend and list the choice. In an interactive session, ask instead.

## 2. Write the build script

Write it in the project as `lockstep/build-<page>.js`, with the Write tool. Shell heredocs and
redirects built from `$` variables get refused by Claude Code's command checker. Start from the closer example in
`$BUILD/references/examples/`:
- `build-settings-slalom.js`: slot-based cards, no text components;
- `build-settings-sds.js`: text components, a Button Group, a full-screen Dialog.

Rules:
- Every visible part is a library instance with explicit variant properties. Draw nothing the
  library has.
- Bind every fill, stroke, padding, gap and radius on frames you create to a library variable.
  Use library text components, or else a library text style plus a bound colour variable.
- Use auto layout everywhere. Never detach an instance. Put content into slots by appending.
- Replace every piece of sample text ("Button", "Label", "Title").
- One top-level frame per screen, named `<Page> / <Screen> / v<VERSION>`. Each pass goes on its
  own canvas row, and the script removes a frame with the same name first, so it's safe to retry.

```bash
python3 "$LOCKSTEP/scripts/render.py" lockstep/build-<page>.js --which List,Dialog --version 1
```

Pass the output as `use_figma`'s `code`. Never hand-edit placeholders.

Then **settle** the frames the build returned, before you score or screenshot them:

```bash
python3 "$LOCKSTEP/scripts/render.py" settle --roots <frame ids from the build>
```

A library instance that a script sizes differently from its component can keep drawing its
insides at the component's original width. A text field's outline stops halfway; a dropdown
arrow floats past its box. Its layers report the right size, so the score can't see it.
Settle forces Figma to lay those instances out again without changing any size. Run it after
every build pass.

## 3. Score and look

Follow **lockstep:score** on the frame IDs the build returned: score, then screenshot every
frame and look at each one. A frame can score 100 and still be broken.

**What you see wins.** If a screenshot shows a defect, the defect is real, even when the layer
data says otherwise: a field whose layer is full width but renders at half width is broken.
Never report a visible defect as "a screenshot artifact". If you doubt `get_screenshot`, also
render the frame with `node.screenshot()` inside `use_figma`. If either render shows the
problem, fix it (for example swap to another variant of the component). If you can't fix it,
list it as not finished.

## 4. Fix and repeat

- **Build problems** (wrong component or variant, clipped content, sample text, broken
  layout): fix the build script, rerun it with `--version` one higher, and score again.
- **A raw value with no matching token:** it's a decision. Ask, or in unattended runs pick the
  nearest token and list it. Don't hide it.

Stop when every measure passes and the screenshots are clean, or after three passes.

## 5. Report

Give the user:
- the draft link;
- a table of each pass's scores;
- what each pass fixed;
- decisions and choices made;
- parts not in the library;
- library gaps worth passing to the design-system team.

Say plainly if any frame isn't done.
