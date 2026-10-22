# Proposals

Drafted by `propose.py` from the audit. Nothing here is approved yet: a person accepts, renames or rejects each line before anything is generated.

## Tokens

| Kind | Value | Suggested name | Uses (internal) | Drift absorbed |
|---|---|---|---|---|
| color | `#1e1e1e` | Color/Text/Default/Default | 29 (43) | #201e1e ×3 |
| color | `#ffffff` | Color/Background/Default/Default | 17 (7) |  |
| color | `#d9d9d9` | Color/Border/Default/Default | 11 (7) |  |
| color | `#2c2c2c` | Color/Background/Brand/Default | 7 (10) | #2e2c2c ×1 |
| color | `#767676` | Color/Text/Neutral/Tertiary | 3 (9) |  |
| color | `#f5f5f5` | Color/Background/Brand/Tertiary | 4 (8) |  |
| color | `#757575` | (none yet) | 8 (0) | #777575 ×2 (or #767676) |
| color | `#303030` | Color/Border/Neutral/Default | 4 (2) |  |
| color | `#b2b2b2` | Color/Border/Neutral/tertiary | 3 (3) |  |
| color | `#e3e3e3` | Color/Background/Neutral/Tertiary | 0 (6) |  |
| color | `#ec221f` | Color/Background/Danger/Default | 0 (2) |  |
| color | `#c00f0c` | Color/Border/Danger/Secondary | 0 (2) |  |
| color | `#fee9e7` | Color/Text/Danger/On Danger | 0 (2) |  |
| color | `#ffffffcc` | (none yet) | 1 (0) |  |
| color | `#0c0c0d0d` | Color Primitives/Black/100 | 0 (1) |  |
| color | `#0c0c0d1a` | Color Primitives/Black/200 | 0 (1) |  |
| spacing | `8` | Size/Space/200 | 14 (152) |  |
| spacing | `12` | Size/Space/300 | 29 (45) |  |
| spacing | `32` | Size/Space/800 | 15 (16) |  |
| spacing | `24` | Size/Space/600 | 23 (4) | 25 ×3, 23 ×1 |
| spacing | `16` | Size/Space/400 | 21 (6) |  |
| spacing | `4` | Size/Space/100 | 10 (8) |  |
| radius | `8` | Size/Radius/200 | 44 (152) |  |
| radius | `9999` | (none yet) | 24 (0) |  |
| radius | `4` | Size/Radius/100 | 10 (8) |  |
| radius | `32` | Typography Primitives/Scale 06 | 0 (4) |  |
| stroke | `1` | Size/Stroke/Border | 17 (91) |  |
| effect | `4` | Size/Depth/100 | 1 (2) |  |
| effect | `-4` | Size/Depth/Negative 100 | 0 (2) |  |
| effect | `0` | Size/Depth/0 | 0 (2) |  |
| effect | `bg-blur:4` | (none yet) | 1 (0) |  |
| effect | `32` | Size/Depth/800 | 0 (1) |  |
| effect | `16` | Size/Depth/400 | 0 (1) |  |
| type | `Inter|Regular|16|140%|0` | Body Base | 27 (0) |  |
| type | `Inter|Semi Bold|24|120%|-2%` | Heading | 8 (0) |  |
| type | `Inter|Regular|16|100%|0` | (none yet) | 6 (0) |  |
| type | `Inter|Bold|48|120%|-2%` | Title Page | 2 (0) |  |
| fontFamily | `Inter` | (none yet) | 43 (0) |  |
| fontSize | `16` | Typography/Body/Size Medium | 33 (49) |  |
| fontSize | `24` | Typography/Heading/Size Base | 8 (0) |  |
| fontSize | `48` | Typography/Title Page/Size Base | 2 (1) |  |
| fontWeight | `400` | Typography/Body/Font Weight Regular | 33 (49) |  |
| fontWeight | `600` | (none yet) | 8 (0) |  |
| fontWeight | `700` | Typography/Title Page/Font Weight | 2 (1) |  |

## WIP variables

| Variable | Value | Maps to | Status |
|---|---|---|---|
| bg/white | `#ffffff` | Color/Background/Default/Default | maps to a library token |
| spacing-xl | `32` | Size/Space/800 | maps to a library token |
| spacing-l | `24` | Size/Space/600 | maps to a library token |
| border-w | `1` | Size/Stroke/Border | maps to a library token |
| spacing-m | `16` | Size/Space/400 | maps to a library token |
| spacing-xs | `8` | Size/Space/200 | maps to a library token |
| text/primary | `#1e1e1e` | Color/Text/Default/Default | maps to a library token |
| radius-md | `8` | Size/Radius/200 | maps to a library token |
| border/light | `#d9d9d9` | Color/Border/Default/Default | maps to a library token |
| blue-accent | `#3b82f6` |  | unused: bound nowhere in the audited files |
| spacing-s | `6` |  | unused: bound nowhere in the audited files |

## Components

| Candidate | Evidence | Status |
|---|---|---|
| Text Heading | 7 detached, 0 live | de facto: only detached copies, no live instances |
| Input Field | 6 detached, 3 live | published, but detached in places |
| Switch Field | 6 detached, 0 live | de facto: only detached copies, no live instances |
| Tab | 5 detached, 4 live | published, but detached in places |
| Card (Slot) | 5 detached, 0 live | de facto: only detached copies, no live instances |
| Button Group | 4 detached, 0 live | de facto: only detached copies, no live instances |
| Tabs | 3 detached, 0 live | de facto: only detached copies, no live instances |
| Text | 3 detached, 5 live | published, but detached in places |
| Text Title Page | 2 detached, 1 live | published, but detached in places |
| Dialog | 1 detached, 0 live | de facto: only detached copies, no live instances |
| Card title | repeats 4× | de facto: a repeated pattern that isn't a component |

## Local components

| Component | Status | Note |
|---|---|---|
| Card / Base | unpublished | unused; looks like Card (Slot) |
| Section Heading | unpublished | unused; looks like Text Heading |
| Toggle row | unpublished | unused; looks like Switch Field |
