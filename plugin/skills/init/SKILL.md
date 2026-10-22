---
name: init
description: First-time Lockstep setup for an organization's Figma design library. It protects the library file, finds the library's components and design tokens, reads their variants, slots and token values through Figma, and saves a library summary that lockstep:build uses. Use when someone wants to start building in Figma with their design system or library, connect or set up a library for Lockstep, or when lockstep:build finds no saved library files.
---

# lockstep:init: set up a library

Leaves a `lockstep/<library-slug>/` folder in the user's project, which `lockstep:build` reads:

| File | What it holds |
|---|---|
| `keys.json` | `{label: key}` for every component (set) and icon the pages will need |
| `inventory.components.json` | Variant axes, boolean, text, instance-swap and slot properties, default sizes and descriptions |
| `inventory.variables.json` | Every token collection components bind, with names, keys and first-mode values; text and effect styles |
| `inventory.structure.json` | Each component's layer tree: which layer each property drives, slots, sizing (fix, hug, fill) |
| `LIBRARY.md` | The short summary build works from (template below) |

Shared scripts live in the plugin's `scripts/` folder, two levels up from this skill's base
directory (shown when the skill loads). Below, `$LOCKSTEP` is that plugin folder.

## Write only to drafts

Lockstep never writes to the library or any other protected file. Before **every** Figma write
call (`use_figma`, `generate_figma_design`, `upload_assets`, ...), check that the target
`fileKey` isn't protected. A hook and the rendered scripts check too; don't rely on them. All
`use_figma` work, including reading the library, happens in a draft. Importing by key works
there even when the library isn't added to the file.

## 1. Protect the library

Ask for the library's Figma link if you don't have it. Its file key is the part after
`/design/`. Add the key to `.claude/lockstep.json` in the project, merging with anything
already there; `~/.claude/lockstep.json` covers every project:

```json
{ "protectedFileKeys": { "<fileKey>": "<library name>" } }
```

`python3 "$LOCKSTEP/scripts/render.py" score --roots 0:1 > /dev/null` must run without the "no
protected file keys" warning.

## 2. Open a draft and a session

Load Figma's skills first: `/figma-use` and `/figma-generate-design`. If they aren't installed
as skills, read them as MCP resources (`skill://figma/figma-use/SKILL.md`,
`skill://figma/figma-generate-design/SKILL.md`). Use the user's draft, or create one with
`create_new_file` (call `whoami` for the `planKey`). Then call `create_session` and pass the
`sessionId` on every call.

## 3. Find components and the library key

- `get_libraries` may not list the org's library. Take its `libraryKey` from any
  `search_design_system` result whose `libraryName` matches.
- Make one batched search, one intent per query, with `includeLibraryKeys` and
  `disableCodeConnect: true`. Search the usual building blocks: button, destructive button,
  text field, select, checkbox, switch, tabs, card, list item, table, avatar, chip, dialog,
  header, page container, heading and body text, divider. Add the icons pages commonly need
  (search, add, delete, close, edit, eye) and a few token names (background, space, radius).
- Results often run to 100K+ characters and get saved to a file. Write the parsing to a small
  `.py` file and run `python3 that-file.py`; a heredoc full of `{"` can be refused by the shell
  checker. Keep only the org's library and record name, asset type, key and a short
  description for each result.
- Write `keys.json` with the Write tool, not a shell heredoc or a redirect built from `$`
  variables: Claude Code's command checker refuses both, and both trial runs lost turns to
  it. Labels are short camelCase roles (`button`, `destructiveButton`, `textField`,
  `iconSearch`).

## 4. Inventory

```bash
python3 "$LOCKSTEP/scripts/render.py" inventory --keys lockstep/<slug>/keys.json --part components
python3 "$LOCKSTEP/scripts/render.py" inventory --keys lockstep/<slug>/keys.json --part variables
python3 "$LOCKSTEP/scripts/render.py" inventory --keys lockstep/<slug>/keys.json --part structure
```

Run each through `use_figma` in the draft, and save each result to its file with the Write
tool. These are three calls because `use_figma` returns at most 48 KB. Build reads the
structure file instead of probing component internals with one-off scripts. If a part still overflows, split
`keys.json` into halves and merge the results.

## 5. Write LIBRARY.md

Keep it under ~150 lines; it's what build reads first:

```markdown
# <Library name>
- File key: <fileKey> (protected)
- Library key: <lk-...>
- Fonts: <families>
- Read on: <date>

## Components
| Label | Name | Variant axes (options) | Other properties | Slots | Default size | Usage rules from the description |

## Tokens
Colour by role (background / text / border / status), spacing scale, radius scale, stroke widths,
text styles, effect styles: name, key, value.

## Shape of the library
- Text components: yes/no (if no, styled text layers are allowed and cap instance share below 100%)
- Containers with slots, and anything that ships at a fixed sample size
- Missing pieces and conflicts worth asking about (casing, which variant means Cancel)
```

Finish by telling the user what's saved, what the library lacks, and any conflicts they
should rule on.
