# combobox

In Figma: **combobox**, code: `SCombobox` in `src/components/SCombobox.vue`.

Approved (approve) by pipeline test (not the Slalom team's ruling) on 2026-10-22.

## What it's for

Combines text entry with option selection and optional adjacent actions. Set Status to enable, hover, focused, filled, error, or disable to match the current interaction and validation state. Configure the label, description, and assistive content; use mandatory, user guidance, has label, assistive text, error text, and has icon to control supporting information. Use button1 and button2 to show or hide the available companion actions.

## When to use it

• Forms where users can type a value or choose from suggested options.
• Selecting known items while still supporting direct text entry.
• Showing one or two related actions beside the field.
• Providing required status, guidance, validation feedback, and disabled states.

## Variants in Figma

| Property | Options |
|---|---|
| Status | disable, enable, error, filled, focused, hover |

Other properties: mandatory (boolean), user guidance (boolean), has label (boolean), button1 (boolean), button2 (boolean), assistive text (boolean), error text (boolean), has icon (boolean), label text (text), description text (text), assistive content (text).

## Props in code

| Prop | Type | Values | Default |
|---|---|---|---|
| `modelValue` | string[] |  | () => [], label: 'Label', placeholder: 'Combobox Label', ass |
| `label` | string |  |  |
| `placeholder` | string |  |  |
| `assistiveText` | string |  |  |
| `errorText` | string |  |  |
| `error` | boolean |  |  |
| `disabled` | boolean |  |  |
| `mandatory` | boolean |  |  |
| `labelType` | 'on' / 'in' | on, in |  |
| `options` | string[] |  |  |
| `forceState` | '' / 'enabled' / 'hover' / 'focused' / 'error' / 'disabled' |  |  |
| `forceOpen` | boolean |  |  |

## How Figma maps to code

| Figma property | Code prop | Notes |
|---|---|---|
| Status | `forceState` | interaction states: code styles these in CSS |

## Decisions and open questions

- **Component fonts.** Still open.
