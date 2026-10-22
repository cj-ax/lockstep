# date picker

In Figma: **date picker**, code: `SDatePicker` in `src/components/SDatePicker.vue`.

Approved (approve) by pipeline test (not the Slalom team's ruling) on 2026-10-22.

## What it's for

Provides a calendar control for choosing a day, month, or year. Use the sections property to display the day selector, month selector, or year selector. Use status to show default, hover, selected, or current selected states where available. Use rounded border to switch between square and rounded containers, and update the mm/yy label text property for the displayed month or year label.

## When to use it

• Selecting a date in forms, filters, scheduling, booking, or reporting flows.
• Moving between day, month, and year selection views.
• Showing hover feedback, a chosen value, or the currently selected date.
• Matching layouts that require either rounded or square picker containers.

## Variants in Figma

| Property | Options |
|---|---|
| sections | day selector, month selector, year selector |
| status | default, hover, selected, current selected |
| rounded border | false, true |

Other properties: mm/yy label (text).

## Props in code

| Prop | Type | Values | Default |
|---|---|---|---|
| `modelValue` | string |  | '' |
| `rounded` | boolean |  | false |

## How Figma maps to code

| Figma property | Code prop | Notes |
|---|---|---|
| sections |  | no matching code prop |
| status |  | interaction states: code styles these in CSS |
| rounded border |  | on/off in Figma; code has no matching prop |

## Decisions and open questions

- **Component fonts.** Still open.
