# Switch Toggle

In Figma: **Switch Toggle**, code: `SSwitch` in `src/components/SSwitch.vue`.

Approved (approve) by pipeline test (not the Slalom team's ruling) on 2026-10-22.

## What it's for

Controls a binary setting that can be turned on or off. Set Toggle Status to Off or On to reflect the current value, and set State to Enabled when the control is available or Disabled when it cannot be changed. Keep the visual status synchronized with the underlying setting.

## When to use it

• Enabling or disabling settings, preferences, features, or visibility.
• Providing an immediate binary choice without a separate submit action.
• Showing an existing on or off value that is temporarily unavailable with the disabled state.

## Variants in Figma

| Property | Options |
|---|---|
| Toggle Status | Off, On |
| State | Enabled, Disabled |

## Props in code

| Prop | Type | Values | Default |
|---|---|---|---|
| `modelValue` | boolean |  | false |
| `label` | string |  | '' |
| `disabled` | boolean |  | false |
| `forceState` | '' / 'on' / 'off' / 'disabled' |  | '' |

## How Figma maps to code

| Figma property | Code prop | Notes |
|---|---|---|
| Toggle Status |  | on/off in Figma; code has no matching prop |
| State |  | no matching code prop |
