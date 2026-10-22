# input/textField

In Figma: **input/textField**, code: `STextField` in `src/components/STextField.vue`.

Approved (approve) by pipeline test (not the Slalom team's ruling) on 2026-10-22.

## What it's for

Collects a single line of user-entered text with a visible label and optional supporting feedback. Use type=label on when the label sits above the field and type=label in when the label is integrated into the field. Choose has value=true for populated fields and false for empty fields where available. Set state to enabled, hover, focused, error, or disabled to match the current interaction and validation state.

## When to use it

• Forms that collect names, titles, dates, search terms, or other short values.
• Showing hover and focus feedback during entry.
• Communicating validation problems with the error state and supporting message.
• Displaying read-only unavailable controls with the disabled state.

## Variants in Figma

| Property | Options |
|---|---|
| state | enabled, focused, error, disabled, hover, input |
| has value | false, true, textField |
| Label style | label on, label in |

Other properties: icon-left (boolean), has label (boolean), content (text), field label (text), assistive text (text), error text (text), has user guidance (boolean), is required (boolean), icon-right (boolean), Assistive Text (boolean).

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
| `forceState` | '' / 'enabled' / 'hover' / 'focused' / 'error' / 'disabled' |  | '' |

## How Figma maps to code

| Figma property | Code prop | Notes |
|---|---|---|
| state | `forceState` | interaction states: code styles these in CSS |
| has value |  | no matching code prop |
| Label style | `labelType` | same options |

## Decisions and open questions

- **Component fonts.** Still open.
