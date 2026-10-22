# step

In Figma: **step**, code: `SStepper` in `src/components/SStepper.vue`.

Approved (approve) by pipeline test (not the Slalom team's ruling) on 2026-10-22.

## What it's for

Combines a step indicator, label, and optional connector into one stepper item. Update the step description text property for the label. Use status=current step for the active step, completed for a finished step, and Next Step for an upcoming step. Set horizontal label to control the label orientation, horizontal line to control the connector orientation, and connector line to show or hide the connector—typically hiding it on the final step.

## When to use it

• Building horizontal or vertical steppers for forms, onboarding, setup, and checkout.
• Showing completed, active, and upcoming steps with descriptive labels.
• Mixing label and connector orientations to fit the available layout.
• Removing the connector from the final item in a sequence.

## Variants in Figma

| Property | Options |
|---|---|
| horizontal label | true, false |
| horizontal line | true, false |
| status | current step, completed, Next Step |

Other properties: step description (text), connector line (boolean).

## Props in code

| Prop | Type | Values | Default |
|---|---|---|---|
| `steps` | string[] |  | () => ['Step 1' |
| `currentStep` | number |  |  |
| `orientation` | 'horizontal' / 'vertical' | horizontal, vertical |  |
| `ariaLabel` | string |  |  |

## How Figma maps to code

| Figma property | Code prop | Notes |
|---|---|---|
| horizontal label |  | on/off in Figma; code has no matching prop |
| horizontal line |  | on/off in Figma; code has no matching prop |
| status |  | no matching code prop |

## Decisions and open questions

- **Component fonts.** Still open.
