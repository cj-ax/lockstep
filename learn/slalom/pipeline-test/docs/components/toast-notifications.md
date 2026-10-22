# Toast Notifications

In Figma: **Toast Notifications**, code: `SToast` in `src/components/SToast.vue`.

Approved (approve) by pipeline test (not the Slalom team's ruling) on 2026-10-22.

## What it's for

Displays a brief status notification without interrupting the current workflow. Choose State=Information for neutral updates, Error Toast for failed actions or problems, and Success for completed actions. Update the corresponding message text property, use Has CTA to show or hide the action, and use Show Icon to control the leading status icon.

## When to use it

• Confirming that an action completed successfully.
• Brief message display that typically will disappear after a few seconds. The time parameter can be adjusted as needed.
• Reporting an error after a user or system action.
• Sharing short, non-blocking informational updates.
• Including a relevant follow-up action when the user can immediately respond.

## Variants in Figma

| Property | Options |
|---|---|
| State | Error Toast, Information, Success |

Other properties: Has CTA (boolean), Error Toast Messaging (text), Success Toast (text), Info Toast Messaging (text), Show Icon (boolean).

## Props in code

| Prop | Type | Values | Default |
|---|---|---|---|
| `type` | ToastType | info, error, success | 'info' |
| `message` | string |  | 'This is informative!' |
| `dismissible` | boolean |  | true |

## How Figma maps to code

| Figma property | Code prop | Notes |
|---|---|---|
| State | `type` | same options |
