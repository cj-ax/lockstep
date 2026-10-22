# Coverage: SDS fixture (no code yet)

Drafted by `reconcile.py`. Statuses: complete (same in Figma and code), drift (same thing, different values), design-only, code-only, de facto (a pattern with no component). Conflicts need a person's ruling before anything is generated.

| Area | Complete | Drift | Design-only | Code-only | De facto |
|---|---|---|---|---|---|
| Components | 0 | 0 | 4 | 0 | 7 |
| Tokens | 0 | 0 | 40 | 0 | 0 |
| Type styles | 0 | 0 | 4 | 0 | 0 |

Tokens by kind:

| Kind | Complete | Drift | Design-only | Code-only |
|---|---|---|---|---|
| color | 0 | 0 | 16 | 0 |
| spacing | 0 | 0 | 6 | 0 |
| effect | 0 | 0 | 6 | 0 |
| radius | 0 | 0 | 4 | 0 |
| fontSize | 0 | 0 | 3 | 0 |
| fontWeight | 0 | 0 | 3 | 0 |
| stroke | 0 | 0 | 1 | 0 |
| fontFamily | 0 | 0 | 1 | 0 |

## Conflicts (0)


## Components

| Figma | Code | Status | Variant differences |
|---|---|---|---|
| Text Heading |  | de facto |  |
| Input Field |  | design-only |  |
| Switch Field |  | de facto |  |
| Tab |  | design-only |  |
| Card (Slot) |  | de facto |  |
| Button Group |  | de facto |  |
| Tabs |  | de facto |  |
| Text |  | design-only |  |
| Text Title Page |  | design-only |  |
| Dialog |  | de facto |  |
| Card title |  | de facto |  |

Interaction-state axes (hover, pressed, focused) and on/off axes aren't compared: code styles states in CSS. They're listed per component in coverage.json.

## Type styles

| Figma | Code | Status | Differences |
|---|---|---|---|
| Body Base |  | design-only |  |
| Heading |  | design-only |  |
| Inter|Regular|16|100%|0 |  | design-only |  |
| Title Page |  | design-only |  |

## Token drift

| Figma | Code | Differences |
|---|---|---|

## Code-only tokens

| Token | Kind | Values | Uses in code |
|---|---|---|---|

## Design-only tokens

| Token | Kind | Values | Close code value |
|---|---|---|---|
| Color/Text/Default/Default | color | default: #1e1e1e | |
| Color/Background/Default/Default | color | default: #ffffff | |
| Color/Border/Default/Default | color | default: #d9d9d9 | |
| Color/Background/Brand/Default | color | default: #2c2c2c | |
| Color/Text/Neutral/Tertiary | color | default: #767676 | |
| Color/Background/Brand/Tertiary | color | default: #f5f5f5 | |
| color #757575 | color | default: #757575 | |
| Color/Border/Neutral/Default | color | default: #303030 | |
| Color/Border/Neutral/tertiary | color | default: #b2b2b2 | |
| Color/Background/Neutral/Tertiary | color | default: #e3e3e3 | |
| Color/Background/Danger/Default | color | default: #ec221f | |
| Color/Border/Danger/Secondary | color | default: #c00f0c | |
| Color/Text/Danger/On Danger | color | default: #fee9e7 | |
| color #ffffffcc | color | default: #ffffffcc | |
| Color Primitives/Black/100 | color | default: #0c0c0d0d | |
| Color Primitives/Black/200 | color | default: #0c0c0d1a | |
| Size/Space/200 | spacing | default: 8.0 | |
| Size/Space/300 | spacing | default: 12.0 | |
| Size/Space/800 | spacing | default: 32.0 | |
| Size/Space/600 | spacing | default: 24.0 | |
| Size/Space/400 | spacing | default: 16.0 | |
| Size/Space/100 | spacing | default: 4.0 | |
| Size/Radius/200 | radius | default: 8.0 | |
| radius 9999.0 | radius | default: 9999.0 | |
| Size/Radius/100 | radius | default: 4.0 | |
| Typography Primitives/Scale 06 | radius | default: 32.0 | |
| Size/Stroke/Border | stroke | default: 1.0 | |
| Size/Depth/100 | effect | default: 4.0 | |
| Size/Depth/Negative 100 | effect | default: -4.0 | |
| Size/Depth/0 | effect | default: 0.0 | |
| effect bg-blur:4 | effect | default: bg-blur:4 | |
| Size/Depth/800 | effect | default: 32.0 | |
| Size/Depth/400 | effect | default: 16.0 | |
| fontFamily Inter | fontFamily | default: Inter | |
| Typography/Body/Size Medium | fontSize | default: 16.0 | |
| Typography/Heading/Size Base | fontSize | default: 24.0 | |
| Typography/Title Page/Size Base | fontSize | default: 48.0 | |
| Typography/Body/Font Weight Regular | fontWeight | default: 400.0 | |
| fontWeight 600.0 | fontWeight | default: 600.0 | |
| Typography/Title Page/Font Weight | fontWeight | default: 700.0 | |
