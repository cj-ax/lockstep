# The learn fixture

A half-built design system with a known answer. `lockstep:learn` is scored on how much of the answer it recovers.

**File:** [SDS learn fixture](https://www.figma.com/design/bgsOIiq7b6ToKhhGPSjkvY) (a draft, `bgsOIiq7b6ToKhhGPSjkvY`).
It has two pages:

- **Product: Settings** holds four frames: Settings / Profile, Notifications, Account and Dialog.
- **Library (WIP)** holds three local components.

## What it imitates

An org whose design system exists mostly in product files:

- **Five components were never published.** Card (Slot), Button Group, Switch Field, Text Heading and Tabs exist only as detached copies.
- **Other components are half adopted.** About half the placements of published components (Input Field, Tab, Text, Text Title Page, Dialog) are detached anyway.
- **Most values are raw.** 80% of token bindings on authored layers were replaced by raw values.
  - The rest point at a local `Tokens (WIP)` collection: nine renamed copies of SDS tokens plus two unused noise tokens.
  - 39 of 43 text layers lost their text style.
- **Some values have drifted.** Six colours and four spacings are a hair off, as eyedropped or hand-typed values are.
- **A local library was started and then abandoned.** Three local components duplicate deleted parts, and no product frame uses them.

The frames still look exactly like the pristine build. The damage is structural, not visual.

## How it was built

Each step is reproducible. Paste the scripts into `use_figma` with the placeholders filled in.

1. **Build the pristine frames.** Render `plugin/skills/build/references/examples/build-settings-sds.js` with `--version 0` into a new draft.
2. **Capture the truth.** Run `capture_truth.js` (read-only) on the four frame IDs. It records every variable bound, authored versus library-internal, every collection's full token list, the text styles and the component placements.
3. **Degrade.** Run `degrade.js` (seed `20261022`). It does five things, in order, and logs every change:
   1. detaches;
   2. creates the WIP collection;
   3. unbinds or rebinds values;
   4. adds drift;
   5. builds the local library page.

   It refuses to run on protected files. Re-running it needs fresh pristine frames.
4. **Census.** Run `census.js` (read-only) on the degraded frames. It records the final state with current node IDs, because detaching renumbers nodes and makes some IDs in the degrade log stale.

## ground-truth.json

| Section | What it holds |
|---|---|
| `fixture` | File key, frame IDs, how it was made |
| `pristine` | Straight from the capture: `tokensUsed` (52, with authored and internal counts), `tokensAll` (124 across six collections), `textStyles`, `components` |
| `degradation` | Seed, the unpublished set, the WIP mapping and noise, change counts, all 10 drift edits, the local components |
| `final` | Census: 42 detached frames by origin, the library instances left, and the raw, bound and WIP value counts |
| `expectedRecovery` | What a perfect learn run finds. `score_recovery.py` (milestone 2) scores against this |

### Known quirks

- **The planned WIP token `brand/dark` was never created.** No binding to Background/Brand/Default survived on an authored layer, so the WIP collection has 9 mapped tokens, not 10.
- **The census counts 4 detached Button Groups, not 5.** The Dialog's Button Group sits inside the Dialog instance's nested slot, and the census doesn't descend there.
- **Detached frames keep a `detachedInfo.componentKey` that still resolves**, because the community SDS library still publishes all five "unpublished" parts. learn must treat them as de facto components, not import them by key.

## Recovering it (milestone 2)

`harvest/` holds what learn read from the degraded file and what it proposed:

| File | Made by |
|---|---|
| `audit.json` | `render.py audit --roots 1:605,1:843,1:973,1:1098`, run through `use_figma` |
| `inventory-components.json`, `inventory-variables.json` | `render.py inventory_local --part components` (and `variables`) |
| `proposals.json`, `PROPOSALS.md` | `propose.py --audit harvest/audit.json --components … --variables … --out harvest` |
| `audit-product-files-only.json`, `product-files-only/` | The same audit with every library binding and style removed, and its proposals: an org with no library |

Score them:

```bash
python3 learn/fixture/score_recovery.py --proposals learn/fixture/harvest/proposals.json --audit learn/fixture/harvest/audit.json --out learn/fixture/RECOVERY.md
```

The results and their caveats are in `RECOVERY.md` and REPORT.md.
