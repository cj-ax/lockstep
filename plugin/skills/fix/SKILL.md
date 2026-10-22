---
name: fix
description: Repair an existing Figma design's faithfulness to its library without changing how it looks. It clones the frames, binds raw spacing, radius, stroke and colour values to library variables with exactly the same value, rescores, and lists the values that have no matching token as decisions. Use when someone wants a Figma design brought in line with their design system's tokens, or after lockstep:score finds unbound values.
---

# lockstep:fix: bind raw values to library tokens

Shared scripts live in the plugin's `scripts/` folder, two levels up from this skill's base
directory (shown when the skill loads). Below, `$LOCKSTEP` is that plugin folder.

## Write only to drafts

Lockstep never writes to the library or any other protected file. Before **every** Figma write
call (`use_figma`, `generate_figma_design`, `upload_assets`, ...), check that the target
`fileKey` isn't protected (`.claude/lockstep.json`, `~/.claude/lockstep.json`). A hook and the
rendered scripts check too; don't rely on them. Never modify the user's original frames: work
on clones.

## Steps

1. Load `/figma-use` (or `skill://figma/figma-use/SKILL.md`) and call `create_session` on the
   file. Check its key isn't protected.
2. **Score first** (lockstep:score) to get the before numbers.
3. **Clone** the frames into a new row below the originals, named `<original> / Lockstep fix`,
   with a small `use_figma` script: `n.clone()`, then `y = n.y + n.height + 200`. Return the
   clone IDs.
4. **Fix** the clones:
   ```bash
   python3 "$LOCKSTEP/scripts/render.py" fix --roots <clone ids>
   ```
   Pass the output as `use_figma`'s `code`. It learns the library's tokens from the library
   instances already in the frames, then binds raw values that exactly match a token. It never
   snaps a value to a different one, so the design looks the same. It returns what it bound
   (`fixed`) and what it couldn't (`decisions`).
5. **Rescore** the clones (lockstep:score), and screenshot them to confirm nothing moved.

## Report

Give:
- a before/after table of the measures;
- how many values were bound, grouped (for example "24px gap → gap/ga-6 ×8");
- the decisions, grouped by value: a 48px padding with no token, a 50% black scrim. For each,
  name the nearest token and ask whether to use it or add a token to the library.

Some problems need a rebuild, not a fix: hand-drawn cards, wrong components, clipped content,
sample text. The fix pass can't change which components are used. Point to lockstep:build for
those.
