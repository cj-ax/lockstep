# text area

In Figma: **text area**, code: `STextArea` in `src/components/STextArea.vue`.

Approved (approve) by pipeline test (not the Slalom team's ruling) on 2026-10-22.

## What it's for

Collects multi-line text with configurable labeling, guidance, validation, and resize affordances. Use type=label on when the label sits above the field and label in when it is integrated into the field. Set has value to true or false where available, and choose status=enable, hover, focused, error, or disable to match the current interaction state. Configure the label, content, assistive, and error text; use is required, user guidance, assistive text, error text, and has label to control supporting information. Use drag horizontal and drag corner to show the appropriate resize affordances.

## When to use it

• Collecting descriptions, comments, notes, feedback, or other longer responses.
• Showing assistive guidance, required status, and validation errors.
• Providing hover, focus, and disabled feedback during form entry.
• Allowing users to resize the field when the experience supports it.

## Variants in Figma

| Property | Options |
|---|---|
| type | label in, label on |
| status | disable, enable, error, focused, hover |
| has value | false, true |

Other properties: user guidance (boolean), is required (boolean), assistive text (boolean), error text (boolean), drag horizontal (boolean), drag corner (boolean), has label (boolean), content (text), label text (text), assistive content (text), error content (text).

## Props in code

| Prop | Type | Values | Default |
|---|---|---|---|
| `modelValue` | string |  | '' |
| `label` | string |  | 'Label' |
| `placeholder` | string |  | 'Input text' |
| `assistiveText` | string |  | 'Assistive text' |
| `errorText` | string |  | '' |
| `error` | boolean |  | false |
| `disabled` | boolean |  | false |
| `mandatory` | boolean |  | true |
| `labelType` | 'on' / 'in' | on, in | 'on' |
| `rows` | number |  | 5 |
| `forceState` | '' / 'enabled' / 'hover' / 'focused' / 'error' / 'disabled' |  | '' |

## How Figma maps to code

| Figma property | Code prop | Notes |
|---|---|---|
| type | `labelType` | same options |
| status | `forceState` | interaction states: code styles these in CSS |
| has value |  | on/off in Figma; code has no matching prop |

## Decisions and open questions

- **Component fonts.** Still open.
