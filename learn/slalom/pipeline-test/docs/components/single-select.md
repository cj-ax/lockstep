# single-select

In Figma: **single-select**, code: `SSelect` in `src/components/SSelect.vue`.

Approved (approve) by pipeline test (not the Slalom team's ruling) on 2026-10-22.

## What it's for

Lets users choose one option from a predefined list. Use type=label on when the label sits above the field and label-in when it is integrated into the field. Set has value to true or false where available, and choose status=enable, hover, focused, error, or disable to match the current state. Configure the label, dropdown, assistive, and error text; use show text or show chip group for the selected-value treatment. Control required status, user guidance, and the optional left icon with the available properties.

## When to use it

• Forms and settings where exactly one predefined option can be selected.
• Filters, categories, statuses, locations, or assignment choices.
• Showing selected values as text or an approved chip treatment.
• Providing guidance, validation feedback, and disabled states.

## Variants in Figma

| Property | Options |
|---|---|
| status | disable, enable, error, focused, hover |
| has value | false, true |
| type | label on, label-in |

Other properties: has label (boolean), assistive text (boolean), label text (text), dropdown text (text), select assistive text (text), error text (boolean), Error Text (text), has user guidance (boolean), is Required (boolean), left icon (boolean), show text (boolean), show chip group (boolean).

## Props in code

| Prop | Type | Values | Default |
|---|---|---|---|
| `modelValue` | string |  | '' |
| `label` | string |  | 'Label' |
| `placeholder` | string |  | 'Dropdown Text' |
| `assistiveText` | string |  | 'Assistive text' |
| `errorText` | string |  | '' |
| `error` | boolean |  | false |
| `disabled` | boolean |  | false |
| `mandatory` | boolean |  | false |
| `labelType` | 'on' / 'in' | on, in | 'on' |
| `options` | SelectOption[] |  | () => [ |
| `forceState` | '' / 'enabled' / 'hover' / 'focused' / 'error' / 'disabled' |  |  |

## How Figma maps to code

| Figma property | Code prop | Notes |
|---|---|---|
| status | `forceState` | interaction states: code styles these in CSS |
| has value |  | on/off in Figma; code has no matching prop |
| type | `labelType` | same options |

## Decisions and open questions

- **Component fonts.** Still open.
