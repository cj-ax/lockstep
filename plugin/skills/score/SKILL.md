---
name: score
description: Score how faithfully Figma frames use their design library, read-only. It reports the share of library instances, design properties bound to variables, detached instances, hard-coded colours, auto layout, and integrity issues (clipped content or text, sample text left in), with a ranked list of offending layers, and looks at screenshots. Use on any existing Figma design, or as the check step after lockstep:build.
---

# lockstep:score: measure faithfulness (read-only)

Shared scripts live in the plugin's `scripts/` folder, two levels up from this skill's base
directory (shown when the skill loads). Below, `$LOCKSTEP` is that plugin folder.

Scoring changes nothing. It still runs through `use_figma`, and the write guard blocks every
`use_figma` call on a protected file. To score frames that live in the library itself, duplicate
them into a draft first.

## Steps

1. Get the file key and frame node IDs. From a link, `node-id=12-345` means `12:345`. Load
   `/figma-use` (or `skill://figma/figma-use/SKILL.md`) and call `create_session` if you
   haven't already.
2. Render and run the scorer:
   ```bash
   python3 "$LOCKSTEP/scripts/render.py" score --roots 12:345,12:400
   ```
   Pass the output as `use_figma`'s `code`.
3. Take a screenshot of every frame (`get_screenshot`, `maxDimension` around 1000) and look for
   what the score can't judge:
   - wrong components or variants for the context;
   - a control narrower or shorter than its siblings, such as one field in a form drawn at half
     width. If its layer reports the right width, that's Figma's stale layout after a scripted
     resize: `settle.js` fixes it (lockstep:build runs it; lockstep:fix runs it on clones);
   - edges that don't line up, such as a table running to the container's edge while the title
     above it is inset;
   - overlap;
   - odd spacing;
   - placeholder icons;
   - anything that looks broken.

   **What you see wins.** A defect visible in a screenshot is a defect, even when the layer
   sizes look right. Don't explain it away as a rendering artifact. If you doubt
   `get_screenshot`, also render the frame with `node.screenshot()` in `use_figma`. Report the
   defect if either render shows it.

## What the numbers mean

| Measure | What it counts | Pass |
|---|---|---|
| Library instances | Content nodes (instances, text, shapes, painted frames) that are instances of a remote library component | At the library's ceiling: 100% if it has text components, lower if styled text layers are the only option |
| Bound properties | Solid fills and strokes, padding, gap, radius and stroke weight on authored nodes bound to variables; text with a text style or bound size | 100% |
| Detached | Frames that were once library instances | 0% |
| Hard-coded colours | Visible paints with no variable or style, including overrides inside instances | 0% |
| Auto layout | Frames you made that use auto layout | 100% |
| **Integrity issues** | Content clipped by its container; text cut off by a container further up; library sample text still showing, including inside nested components | **0** |

Faithfulness is the mean of the five percentages, with detached and hard-coded inverted. Every
measure matters more than the mean. Library internals are the library's business: the scorer
skips them, except slot contents and paints overridden on an instance.

## Report

Give:
- a table of the measures per frame and in total;
- the integrity issues;
- the top offenders, grouped by rule (`offendersByRule` plus the first entries of `offenders`);
- what the screenshots show.

Point to `lockstep:fix` for raw values that could be bound, and to `lockstep:build` for
structural problems.
