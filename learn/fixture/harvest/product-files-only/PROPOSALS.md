# Proposals

Drafted by `propose.py` from the audit. Nothing here is approved yet: a person accepts, renames or rejects each line before anything is generated.

## Tokens

| Kind | Value | Suggested name | Uses (internal) | Drift absorbed |
|---|---|---|---|---|
| color | `#1e1e1e` | text/primary | 29 (0) | #201e1e ×3 |
| color | `#ffffff` | bg/white | 17 (0) |  |
| color | `#d9d9d9` | border/light | 11 (0) |  |
| color | `#757575` | (none yet) | 8 (0) | #777575 ×2 |
| color | `#2c2c2c` | (none yet) | 7 (0) | #2e2c2c ×1 |
| color | `#303030` | (none yet) | 4 (0) |  |
| color | `#f5f5f5` | (none yet) | 4 (0) |  |
| color | `#b2b2b2` | (none yet) | 3 (0) |  |
| color | `#767676` | (none yet) | 3 (0) |  |
| color | `#ffffffcc` | (none yet) | 1 (0) |  |
| spacing | `12` | (none yet) | 29 (0) |  |
| spacing | `24` | spacing-l | 23 (0) | 25 ×3, 23 ×1 |
| spacing | `16` | spacing-m | 21 (0) |  |
| spacing | `32` | spacing-xl | 15 (0) |  |
| spacing | `8` | spacing-xs | 14 (0) |  |
| spacing | `4` | (none yet) | 10 (0) |  |
| radius | `8` | radius-md | 44 (0) |  |
| radius | `9999` | (none yet) | 24 (0) |  |
| radius | `4` | (none yet) | 10 (0) |  |
| stroke | `1` | border-w | 17 (0) |  |
| effect | `bg-blur:4` | (none yet) | 1 (0) |  |
| effect | `4` | (none yet) | 1 (0) |  |
| type | `Inter|Regular|16|140%|0` | (none yet) | 27 (0) |  |
| type | `Inter|Semi Bold|24|120%|-2%` | (none yet) | 8 (0) |  |
| type | `Inter|Regular|16|100%|0` | (none yet) | 6 (0) |  |
| type | `Inter|Bold|48|120%|-2%` | (none yet) | 2 (0) |  |
| fontFamily | `Inter` | (none yet) | 43 (0) |  |
| fontSize | `16` | (none yet) | 33 (0) |  |
| fontSize | `24` | (none yet) | 8 (0) |  |
| fontSize | `48` | (none yet) | 2 (0) |  |
| fontWeight | `400` | (none yet) | 33 (0) |  |
| fontWeight | `600` | (none yet) | 8 (0) |  |
| fontWeight | `700` | (none yet) | 2 (0) |  |

## WIP variables

| Variable | Value | Maps to | Status |
|---|---|---|---|
| bg/white | `#ffffff` |  | no library token with this value |
| spacing-xl | `32` |  | no library token with this value |
| spacing-l | `24` |  | no library token with this value |
| border-w | `1` |  | no library token with this value |
| spacing-m | `16` |  | no library token with this value |
| spacing-xs | `8` |  | no library token with this value |
| text/primary | `#1e1e1e` |  | no library token with this value |
| radius-md | `8` |  | no library token with this value |
| border/light | `#d9d9d9` |  | no library token with this value |
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
