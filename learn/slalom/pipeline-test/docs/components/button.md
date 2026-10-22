# button

In Figma: **button**, code: `SButton` in `src/components/SButton.vue`.

Approved (approve) by pipeline test (not the Slalom team's ruling) on 2026-10-22.

## What it's for

Provides a reusable button for initiating a user action, with labeled and icon-only presentations. Variants control visual emphasis, size, and interaction-state appearance.

## When to use it

Recommended usage:
• contained_button: a prominent primary action, such as Save or Submit.
• outlined: a secondary action that needs a visible boundary without a filled background.
• neutral_outlined: a secondary or supporting action with neutral visual emphasis, such as Cancel.
• text: a low-emphasis action alongside more prominent buttons.
• Plain: a minimal, neutral action within supporting content.
• icon: a compact icon-only action in a toolbar or repeated row.
• icon contained: an icon-only action that needs stronger filled emphasis.
• md: the default button size. Use for action …

The Figma description is longer than Lockstep reads (1,500 characters); see the full text on the component in Figma.

## Variants in Figma

| Property | Options |
|---|---|
| size | lg, md, sm |
| variant | contained_button, outlined, text, Plain, neutral_outlined, icon, icon contained |
| status | enabled, disabled, hover, pressed, sync |

Other properties: icon right (boolean), title case (boolean), uppercase (boolean), Text (text), icon-left (boolean).

## Props in code

| Prop | Type | Values | Default |
|---|---|---|---|
| `variant` | ButtonVariant | contained, outlined, text, plain | 'contained' |
| `size` | ButtonSize | lg, md, sm | 'md' |
| `semantic` | ButtonSemantic | negative, positive |  |
| `disabled` | boolean |  | false |
| `prependIcon` | boolean |  | false |
| `appendIcon` | boolean |  | false |
| `label` | string |  | 'Button' |
| `href` | string |  |  |
| `type` | 'button' / 'submit' / 'reset' | button, submit, reset | 'button' |
| `forceState` | '' / 'hover' / 'pressed' / 'disabled' |  | '' |

Slots: default, append, prepend.

## How Figma maps to code

| Figma property | Code prop | Notes |
|---|---|---|
| size | `size` | same options |
| variant | `variant` | Figma only: icon, icon contained, neutral_outlined |
| status | `forceState` | interaction states: code styles these in CSS |

## Decisions and open questions

- **Component fonts.** Still open.
- **SButton label case.** Still open.
- **button variant.** Still open.
- **button_shadow-1 / $slm-shadow-button-1.** Still open.
- **button_shadow-4 / $slm-shadow-button-4.** Still open.
- **button_shadow-7 / $slm-shadow-button-7.** Still open.
