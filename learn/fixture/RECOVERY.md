# Recovery on the learn fixture

Scored by `score_recovery.py` against `ground-truth.json` (fixture `bgsOIiq7b6ToKhhGPSjkvY`).

| Metric | Result |
|---|---|
| Token recall: tokens the frames' own layers used | 24/24 (100%) |
| Token recall: all tokens used, including inside library components | 52/52 (100%) |
| Token precision, approving every proposal | 44/44 (100%) |
| Suggested names: a library name for that value and use | 20/24 (83%) |
| Suggested names: exactly the token the designer used | 18/24 (75%) |
| Text styles found | 4/4 (100%) |
| Drift edits flagged and attached to the right token | 10/10 (100%) |
| Components found (all evidence) | 10/10 (100%) |
| Components found from structure alone | 7/10 (70%) |
| Components classified correctly (de facto vs published) | 9/10 (90%) |
| WIP variables mapped to the right library token | 9/9 (100%) |
| Noise variables flagged as unused | 2/2 (100%) |
| Local components linked to what they duplicate, and flagged unused | 3/3 (100%) |

## Tokens missed

None.

## Names that aren't a library name for that value

- Background/Utilities/Scrim (#ffffffcc): proposed no name
- Body/Font Family (Inter): proposed no name
- Heading/Font Family (Inter): proposed no name
- Heading/Font Weight (600): proposed no name

## Proposals that match no token in the original frames

None.

## Drift edits missed

None.

## Components

| Component | In the fixture | Detached copies | Found | Found from structure alone | Status given |
|---|---|---|---|---|---|
| Card (Slot) | unpublished | 5 | yes | yes | de facto: only detached copies, no live instances |
| Text Heading | unpublished | 7 | yes | yes | de facto: only detached copies, no live instances |
| Switch Field | unpublished | 6 | yes | yes | de facto: only detached copies, no live instances |
| Button Group | unpublished | 4 | yes | no | de facto: only detached copies, no live instances |
| Tabs | unpublished | 3 | yes | yes | de facto: only detached copies, no live instances |
| Input Field | published | 6 | yes | yes | published, but detached in places |
| Tab | published | 5 | yes | yes | published, but detached in places |
| Text | published | 3 | yes | yes | published, but detached in places |
| Text Title Page | published | 2 | yes | no | published, but detached in places |
| Dialog | published | 1 | yes | no | de facto: only detached copies, no live instances (wrong) |
