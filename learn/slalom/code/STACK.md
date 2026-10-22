# Stack: @slalom/design-system

A draft from `scan_repo.py`, run 2026-10-22 on `/Users/chrisaxelson/Downloads/design-system-beta-main`. The scan reads files only, so check each line. Fix what's wrong, answer the questions at the end, then fill in **Confirmed**.

**Confirmed:** not yet (name and date when a person has checked this)

## What this repository is

**A component library** (high confidence). Evidence: the package entry exports 18 capitalised names; it declares peer dependencies; package.json lists what it publishes.

package.json describes it as: Slalom Design System - A Vue 3 + Vuetify 3 component library derived from Figma design tokens

## Frameworks and libraries

| Kind | Name | Version | Declared in |
|---|---|---|---|
| Framework | Vue | ^3.5.25 | package.json (devDependencies) |
| UI library | Vuetify | ^3.11.8 | package.json (devDependencies) |
| Styling | Sass | ^1.97.3 | package.json (dependencies) |
| Build tool | Vite | ^7.3.1 | package.json (devDependencies) |

Package manager: npm.

## Design tokens

- **css-custom-properties** in `src/styles/_tokens.scss`: 198 definitions (66 unique); prefixes `--slm-`; themes `.v-theme--slalomBuild`, `.v-theme--slalomDark`, `.v-theme--slalomLight`
- **scss-variables** in `src/styles/_tokens.scss`: 94 definitions; maps `$slm-spaces`
- **theme-object** in `src/plugins/vuetify.ts`: themes `slalomLight`, `slalomDark`, `slalomBuild`

## Components (17)

Package entry: `src/index.ts`. It exports 17 of these components, plus SlalomDS.

| Component | File | Props | Variant-like props | Slots |
|---|---|---|---|---|
| SAlert | `src/components/SAlert.vue` | type, variant, message, actionText | type: warning / error / info; variant: close / button / more-info |  |
| SAutocomplete | `src/components/SAutocomplete.vue` | modelValue, label, placeholder, assistiveText, errorText, error, disabled, mandatory, labelType, options … | labelType: on / in |  |
| SButton | `src/components/SButton.vue` | variant, size, semantic, disabled, prependIcon, appendIcon, label, href, type, forceState | variant: contained / outlined / text / plain; size: lg / md / sm; semantic: negative / positive; type: button / submit / reset | default, append, prepend |
| SCombobox | `src/components/SCombobox.vue` | modelValue, label, placeholder, assistiveText, errorText, error, disabled, mandatory, labelType, options … | labelType: on / in |  |
| SDatePicker | `src/components/SDatePicker.vue` | modelValue, rounded |  |  |
| SEmptyState | `src/components/SEmptyState.vue` | title, description, layout, primaryText, secondaryText, showActions, illustration | layout: horizontal / vertical; illustration: workstream / chat / invite-only |  |
| SExpansionPanel | `src/components/SExpansionPanel.vue` | title, progress, statusRows, dataRows, notes |  | default, icon, secondary-icon |
| SExpansionPanels | `src/components/SExpansionPanels.vue` | multiple |  | default |
| SIcon | `src/components/SIcon.vue` | name, size, ariaLabel |  |  |
| SProgressRing | `src/components/SProgressRing.vue` | value, size, strokeWidth, fillColor, trackColor, ariaLabel |  | default |
| SSelect | `src/components/SSelect.vue` | modelValue, label, placeholder, assistiveText, errorText, error, disabled, mandatory, labelType, options … | labelType: on / in |  |
| SSkeletonLoader | `src/components/SSkeletonLoader.vue` | type, ariaLabel | type: text / card / list / table |  |
| SStepper | `src/components/SStepper.vue` | steps, currentStep, orientation, ariaLabel | orientation: horizontal / vertical |  |
| SSwitch | `src/components/SSwitch.vue` | modelValue, label, disabled, forceState |  |  |
| STextArea | `src/components/STextArea.vue` | modelValue, label, placeholder, assistiveText, errorText, error, disabled, mandatory, labelType, rows … | labelType: on / in |  |
| STextField | `src/components/STextField.vue` | modelValue, label, placeholder, assistiveText, errorText, error, disabled, mandatory, labelType, forceState | labelType: on / in |  |
| SToast | `src/components/SToast.vue` | type, message, dismissible | type: info / error / success |  |

## Storybook and docs

- Storybook: not configured, 0 story files.
- Showcase pages: `18 files, e.g. src/pages/AlertShowcase.vue`

**Tier:** 3. The repository has components with props, so learn can map code components to Figma ones.

## Questions for whoever knows the stack

1. Is this the library product teams actually install, or a prototype? Which product repos consume it, and at what version?
   - Answer:
2. Your components sit on top of Vuetify. When a screen needs a control the library lacks, do people use the Vuetify one directly, or build a new component? (13 components wrap Vuetify parts, e.g. SAlert, SAutocomplete, SCombobox.)
   - Answer:
3. We found these themes: slalomBuild, slalomDark, slalomLight. Which ship to customers, and does Figma model each one as a variable mode?
   - Answer:
4. Does each Figma component name match a code component (for example Figma's "Button" and code's "SButton")? Where don't they line up?
   - Answer:
5. Which components are deprecated, or about to change?
   - Answer:
