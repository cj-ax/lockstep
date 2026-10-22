# SDS learned library (draft)

- **File:** `iuJn7Ziu80PUNh9gVTM3LK` (a draft). The learned components and variables are local to this file until the org publishes it, so **build here**, on a new page. Don't create another draft: local components can't be used from another file.
- **Components** are on the page "Learned library". Refs in `keys.json`: `local:<node id>` for learned components, a key for published ones.
- **Variables** are in the collection "Learned tokens" (modes: light); refs in `variables.json`. Text styles are local too.
- **Score** with `render.py score --roots <frames> --local-library-page "Learned library"`, so learned components count as library instances.

```js
// Learned (local) and published refs side by side.
const component = async (ref) => ref.startsWith('local:') ? figma.getNodeByIdAsync(ref.slice(6))
  : figma.importComponentSetByKeyAsync(ref).catch(() => figma.importComponentByKeyAsync(ref));
const variable = async (ref) => figma.variables.getVariableByIdAsync(ref.slice(6));
const textStyle = async (ref) => figma.getStyleByIdAsync(ref.slice(6));
```

## Components

| Label | Component | From | Properties | Notes |
|---|---|---|---|---|
| `textHeading` | Text Heading | learned (rebuilt from approved copies) | Heading |  |
| `switchField` | Switch Field | learned (rebuilt from approved copies) | Label, Description |  |
| `cardSlot` | Card (Slot) | learned (rebuilt from approved copies) | Slot | put content in its slot; the slot starts empty |
| `buttonGroup` | Button Group | learned (rebuilt from approved copies) | none of its own | its library parts are exposed: set their properties through the instance |
| `tabs` | Tabs | learned (rebuilt from approved copies) | Slot | put content in its slot; the slot starts empty |
| `dialog` | Dialog | learned (rebuilt from approved copies) | none of its own | its library parts are exposed: set their properties through the instance |
| `header` | Header | published library | Platform: Desktop / Mobile; State: Open / Default |  |
| `navigationPill` | Navigation Pill | published library | Label (text, default "Link"); State: Default / Active / Hover |  |
| `text` | Text | published library | Text (text, default "Text") |  |
| `inputField` | Input Field | published library | Has Label (boolean); Has Error (boolean); Label (text, default "Label"); Error (text, default "Error"); Has Description (boolean); Description (text, default "Description"); Value (text, default "Value"); State: Disabled / Default / Error; Value Type: Default / Placeholder |  |
| `button` | Button | published library | Label (text, default "Button"); Icon End (instance_swap); Has Icon End (boolean); Has Icon Start (boolean); Icon Start (instance_swap); Variant: Primary / Neutral / Subtle; State: Default / Hover / Disabled; Size: Medium / Small |  |
| `tab` | Tab | published library | Label (text, default "Label"); State: Default / Hover; Active: Off / On |  |
| `textTitlePage` | Text Title Page | published library | Text (text, default "Text Title Page") |  |
| `buttonDanger` | Button Danger | published library | Label (text, default "Button"); Icon End (instance_swap); Has Icon End (boolean); Has Icon Start (boolean); Icon Start (instance_swap); Variant: Primary / Subtle; State: Default / Hover / Disabled; Size: Medium / Small | Keywords: action, negative, destructive |
| `dialogBody` | Dialog Body | published library | Dismissible (boolean); Body (text, default "Body text"); Heading (text, default "Text Heading"); Slot (slot); Slot 2 (slot); Type: Card / Sheet | Overlays have a maximum width of 600, to prevent long lines of text. |

Learned components have one variant: the one their examples showed. If a page needs another state (a switch that's off), say so in your report rather than detaching or redrawing it.

## Tokens

- **color:** `text/default/default`, `background/default/default`, `border/default/default`, `background/brand/default`, `text/neutral/tertiary`, `background/brand/tertiary`, `color/757575`, `border/neutral/default`, `border/neutral/tertiary`, `background/neutral/tertiary`, `background/danger/default`, `border/danger/secondary`, `text/danger/on-danger`, `color/ffffffcc`, `black/100`, `black/200`
- **spacing:** `space/200`, `space/300`, `space/800`, `space/600`, `space/400`, `space/100`
- **radius:** `radius/200`, `radius/9999`, `radius/100`, `typography-primitives/scale-06`
- **stroke:** `stroke/border`
- **effect:** `depth/100`, `depth/negative-100`, `depth/0`, `effect/bg-blur-4`, `depth/800`, `depth/400`
- **fontFamily:** `fontfamily/inter`
- **fontSize:** `body/size-medium`, `heading/size-base`, `title-page/size-base`
- **fontWeight:** `body/font-weight-regular`, `fontweight/600`, `title-page/font-weight`

Text styles: Body Base, Heading, type/inter-regular-16-100-0, Title Page.

## Decisions from review

- bg/white: map
- spacing-xl: map
- spacing-l: map
- border-w: map
- spacing-m: map
- spacing-xs: map
- text/primary: map
- radius-md: map
- border/light: map
- Card / Base: merge
- Section Heading: merge
- Toggle row: merge
