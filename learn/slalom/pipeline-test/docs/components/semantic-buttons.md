# semantic Buttons

In Figma: **semantic Buttons**, code: `SButton` in `src/components/SButton.vue`.

Approved (approve) by pipeline test (not the Slalom team's ruling) on 2026-10-22.

## What it's for

Provides action buttons with negative or positive semantic emphasis. Use negative for destructive actions such as Remove or Delete; use positive when an action needs positive semantic emphasis.

As with the main buttons, contained_button provides the highest visual hierarchy and is used only when the action is standalone. Outlined provides lower emphasis for actions within tables, lists, and action groups.

Available variants and controls:
• semantic: negative, positive.
• variant: contained_button, outlined.
• Size: lg, md, sm.
• status: default (available action), hover (pointer-over feedback), pressed (active press feedback), disable (unavailable action).
• All 48 combinations of semantic, variant, Size, and status are available.
• label controls the button text (default: “Button”). icon left and icon right control optional icons; both default to true.
• Labels are Title Case by default (Title Case=true; Upper Case=false), consistent with the main buttons.
• Status variants represent visual states; application behavior must be implemented separately.

## When to use it

Hierarchy and size guidance:
• Standalone actions: use contained_button only when the action stands alone and requires the highest emphasis.
• lg: use only when the button is beside a field, consistent with the main buttons.

Negative actions:
• Highlighted Remove or Delete action in a section: use negative + contained_button + md when the action is standalone and needs promi …

The Figma description is longer than Lockstep reads (1,500 characters); see the full text on the component in Figma.

## Variants in Figma

| Property | Options |
|---|---|
| semantic | negative, positive |
| status | default, disable, hover, pressed |
| variant | contained_button, outlined |
| Size | lg, md, sm |

Other properties: label (text), icon left (boolean), icon right (boolean), Upper Case (boolean), Title Case (boolean).

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
| semantic | `semantic` | same options |
| status | `forceState` | interaction states: code styles these in CSS |
| variant | `variant` | code only: plain, text |
| Size | `size` | same options |

## Decisions and open questions

- **Component fonts.** Still open.
- **SButton label case.** Still open.
- **semantic Buttons variant.** Still open.
