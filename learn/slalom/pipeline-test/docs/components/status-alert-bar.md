# Status Alert Bar

In Figma: **Status Alert Bar**, code: `SAlert` in `src/components/SAlert.vue`.

Approved (approve) by pipeline test (not the Slalom team's ruling) on 2026-10-22.

## What it's for

Displays a full-width status message using warning, error, or informative styling. Choose Type based on message severity. Choose Function=Closeable for dismissible alerts, Info for an informational affordance, Button Action for a labeled button, or Hyperlink Action for an inline link where that combination is available. Update the corresponding message and CTA text properties, use Show Icon to control the leading status icon, and use Show Modal Pop-up when the configured action should expose a modal.

## When to use it

• Warning users about conditions that may require attention.
• Reporting errors that block or interrupt a task.
• Sharing neutral system or workflow information.
• Providing dismissal, more information, a button action, or a hyperlink action when supported by the selected type.

## Variants in Figma

| Property | Options |
|---|---|
| Type | Error Alert, Warning Alert, informative |
| Function | Closeable, Info, Button Action, Hyperlink Action |

Other properties: Warning CTA Hyperlink (text), Show Modal Pop-up (boolean), Error CTA Hyperlink (text), Error Message (text), Show Icon (boolean), Warning Alert Message (text), informative message (text).

## Props in code

| Prop | Type | Values | Default |
|---|---|---|---|
| `type` | AlertType | warning, error, info | 'warning' |
| `variant` | AlertVariant | close, button, more-info | 'close' |
| `message` | string |  | 'Alert Message' |
| `actionText` | string |  | 'BUTTON' |

## How Figma maps to code

| Figma property | Code prop | Notes |
|---|---|---|
| Type | `type` | same options |
| Function |  | no matching code prop |
