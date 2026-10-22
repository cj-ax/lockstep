# empty State

In Figma: **empty State**, code: `SEmptyState` in `src/components/SEmptyState.vue`.

Approved (approve) by pipeline test (not the Slalom team's ruling) on 2026-10-22.

## What it's for

Communicates that a page, section, or collection has no content yet by pairing an illustration with a title, supporting message, and optional call to action. Use Type=horizontal for a compact side-by-side arrangement and Type=vertical for a centered stacked arrangement. Use has CTA to show or hide the action.

## When to use it

• First-use experiences where content has not been created yet.
• Search, filter, or data views that return no results.
• Empty sections that need explanation and a clear next step.
• Horizontal layouts in shorter or wider spaces, and vertical layouts in larger centered spaces.

## Variants in Figma

| Property | Options |
|---|---|
| Type | horizontal, vertical |

Other properties: has CTA (boolean).

## Props in code

| Prop | Type | Values | Default |
|---|---|---|---|
| `title` | string |  | 'PLACE A TITLE FOR THE EMPTY SPACE' |
| `description` | string |  | 'Write a text for your empty space' |
| `layout` | 'horizontal' / 'vertical' | horizontal, vertical | 'vertical' |
| `primaryText` | string |  | 'Click to Change the Button text' |
| `secondaryText` | string |  | 'Click to Change the Button text' |
| `showActions` | boolean |  | true |
| `illustration` | 'workstream' / 'chat' / 'invite-only' | workstream, chat, invite-only | 'workstream' |

## How Figma maps to code

| Figma property | Code prop | Notes |
|---|---|---|
| Type | `layout` | same options |

## Decisions and open questions

- **Component fonts.** Still open.
