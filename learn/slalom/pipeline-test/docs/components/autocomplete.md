# autocomplete

In Figma: **autocomplete**, code: `SAutocomplete` in `src/components/SAutocomplete.vue`.

Approved (approve) by pipeline test (not the Slalom team's ruling) on 2026-10-22.

## What it's for

Lets users type to find and select a value from a suggested set of options. Use type=label on when the label sits above the field and label in when it is integrated into the field. Set has value to true or false where available, and choose status=enable, hover, focus, filled, error, or disable to match the current state. Configure labels, input, assistive, and error text; use text response or chips for the selected-value treatment. Control required status, guidance, icons, dropdown arrow, and clear action with the available properties.

## When to use it

• Searching and selecting from long option lists such as people, projects, locations, or categories.
• Supporting single-value text selections or chip-based selections.
• Showing focus, filled, error, and disabled form states.
• Providing guidance, validation, clearing, and dropdown affordances.

## Variants in Figma

| Property | Options |
|---|---|
| status | disable, enable, error, filled, focus, hover |
| type | label in, label on |
| has value | false, true |

Other properties: has label (boolean), is required (boolean), assistive text (boolean), error text (boolean), has icon (boolean), has arrow (boolean), clear icon (boolean), content (text), label content (text), assistive content (text), error content (text), text response (boolean), chips (boolean), left icon (boolean), user guidance (boolean).

## Props in code

| Prop | Type | Values | Default |
|---|---|---|---|
| `modelValue` | string / string[] |  | '' |
| `label` | string |  | 'Label' |
| `placeholder` | string |  | 'Input text' |
| `assistiveText` | string |  | 'Assistive text' |
| `errorText` | string |  | '' |
| `error` | boolean |  | false |
| `disabled` | boolean |  | false |
| `mandatory` | boolean |  | false |
| `labelType` | 'on' / 'in' | on, in | 'on' |
| `options` | string[] |  | () => ['Option A' |
| `chips` | boolean |  |  |
| `forceState` | '' / 'enabled' / 'hover' / 'focused' / 'error' / 'disabled' |  |  |
| `forceOpen` | boolean |  |  |

## How Figma maps to code

| Figma property | Code prop | Notes |
|---|---|---|
| status | `forceState` | interaction states: code styles these in CSS |
| type | `labelType` | same options |
| has value |  | on/off in Figma; code has no matching prop |

## Decisions and open questions

- **Component fonts.** Still open.
