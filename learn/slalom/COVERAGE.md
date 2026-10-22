# Coverage: Business@Slalom library and design-system-beta

Drafted by `reconcile.py`. Statuses: complete (same in Figma and code), drift (same thing, different values), design-only, code-only, de facto (a pattern with no component). Conflicts need a person's ruling before anything is generated.

| Area | Complete | Drift | Design-only | Code-only | De facto |
|---|---|---|---|---|---|
| Components | 13 | 2 | 13 | 3 | 0 |
| Tokens | 87 | 10 | 72 | 72 | 0 |
| Type styles | 14 | 1 | 0 | 0 | 0 |

Tokens by kind:

| Kind | Complete | Drift | Design-only | Code-only |
|---|---|---|---|---|
| color | 46 | 7 | 61 | 48 |
| spacing | 29 | 0 | 0 | 10 |
| effect | 4 | 3 | 5 | 11 |
| radius | 3 | 0 | 5 | 0 |
| stroke | 2 | 0 | 0 | 3 |
| fontWeight | 3 | 0 | 1 | 0 |

## Conflicts (15)

1. **Component fonts.** Figma: Slalom Sans in every text style. Code: DM Sans hard-coded in SAutocomplete, SButton, SCombobox, SDatePicker, SEmptyState, SSelect, SStepper, STextArea, STextField; Roboto hard-coded in SProgressRing. Should these components use the system font token instead?
2. **SButton label case.** Figma: Title Case by default (button). Code: text-transform: uppercase in src/components/SButton.vue. Which casing is right for labels?
3. **button variant.** Figma: icon, icon contained, neutral_outlined. Code: nothing extra. Should Figma's variant and code's variant offer the same options?
4. **semantic Buttons variant.** Figma: nothing extra. Code: plain, text. Should Figma's variant and code's variant offer the same options?
5. **text-disabled / --slm-disabled-text.** Figma: Color Semantic Variables (updated)/Font Colors/text-disabled, Light: #00000066; Dark: #ffffff80. Code: --slm-disabled-text, slalomLight: #00000061; slalomDark: #ffffff61. Which value is right?
6. **text-error / theme.error.** Figma: Color Semantic Variables (updated)/Font Colors/text-error, Dark: #ffdbdf. Code: theme.error, slalomDark: #ff6b6b. Which value is right?
7. **success / theme.success.** Figma: Color Semantic Variables (updated)/Primary Colors/success, Light: #5cb85c; Dark: #5cb85c. Code: theme.success, slalomLight: #2e7d32; slalomDark: #4caf50. Which value is right?
8. **error-element / theme.error.** Figma: Color Semantic Variables (updated)/Primary Colors/error-element, Dark: #ffdbdf. Code: theme.error, slalomDark: #ff6b6b. Which value is right?
9. **neutral-border-color / --slm-border.** Figma: Color Semantic Variables (updated)/Border Colors/neutral-border-color, Dark: #757575. Code: --slm-border, slalomDark: #eaeaea. Which value is right?
10. **card-bg-secondary / --slm-app-card-bg.** Figma: Color Semantic Variables (updated)/card color/card-bg-secondary, Dark: #424242. Code: --slm-app-card-bg, slalomDark: #444444. Which value is right?
11. **text-disabled / --slm-disabled-text.** Figma: Colors/Font Colors/text-disabled, Dark: #ffffff80; BuildDark: #ffffff80. Code: --slm-disabled-text, slalomDark: #ffffff61; slalomBuild: #ffffff61. Which value is right?
12. **button_shadow-1 / $slm-shadow-button-1.** Figma: button_shadow-1, default: 0 0 2 0 #73a6ff1a. Code: $slm-shadow-button-1, default: 0 0 2 0 #0000001f. Which value is right?
13. **button_shadow-4 / $slm-shadow-button-4.** Figma: button_shadow-4, default: 0 3 4 0 #0000001a. Code: $slm-shadow-button-4, default: 0 3 4 0 #0000001f. Which value is right?
14. **button_shadow-7 / $slm-shadow-button-7.** Figma: button_shadow-7, default: 0 4 5 0 #0000001a. Code: $slm-shadow-button-7, default: 0 4 5 0 #0000001f. Which value is right?
15. **Heading 5 / slm-heading-5.** Figma: Heading 5, letterSpacing: 0.0. Code: slm-heading-5, letterSpacing: 1.92. Which value is right?

## Components

| Figma | Code | Status | Variant differences |
|---|---|---|---|
| Header |  | design-only |  |
| container |  | design-only |  |
| card |  | design-only |  |
| card header |  | design-only |  |
| button | SButton | drift | variant → variant: Figma only icon, icon contained, neutral_outlined |
| semantic Buttons | SButton | drift | variant → variant: code only plain, text |
| input/textField | STextField | complete |  |
| text area | STextArea | complete |  |
| single-select | SSelect | complete |  |
| autocomplete | SAutocomplete | complete |  |
| date picker | SDatePicker | complete |  |
| radio button |  | design-only |  |
| Switch Toggle | SSwitch | complete |  |
| list item |  | design-only |  |
| list-section |  | design-only |  |
| v-avatar |  | design-only |  |
| modal |  | design-only |  |
| divider |  | design-only |  |
| content-slot |  | design-only |  |
| Status Alert Bar | SAlert | complete |  |
| Toast Notifications | SToast | complete |  |
| step | SStepper | complete |  |
| step counter |  | design-only |  |
| loading_1 |  | design-only |  |
| Accordion Row | SExpansionPanel | complete |  |
| empty State | SEmptyState | complete |  |
| loading | SProgressRing | complete |  |
| combobox | SCombobox | complete |  |
|  | SExpansionPanels | code-only | props: multiple |
|  | SIcon | code-only | props: name, size, ariaLabel |
|  | SSkeletonLoader | code-only | props: type, ariaLabel |

Interaction-state axes (hover, pressed, focused) and on/off axes aren't compared: code styles states in CSS. They're listed per component in coverage.json.

## Type styles

| Figma | Code | Status | Differences |
|---|---|---|---|
| Subtitle-2 | slm-subtitle-2 | complete |  |
| Body-2 | slm-body-2 | complete |  |
| Body-1 | slm-body-1 | complete |  |
| Caption | slm-caption | complete |  |
| button-lg-upcase | slm-btn-lg | complete |  |
| button-lg-ttlcase | slm-btn-lg | complete |  |
| button-md-upcase | slm-btn-md | complete |  |
| button-md-ttlcase | slm-btn-md | complete |  |
| button-sm-upcase | slm-btn-sm | complete |  |
| button-sm-ttlcase | slm-btn-sm | complete |  |
| Heading 6 | slm-heading-6 | complete |  |
| Heading 3 | slm-heading-3 | complete |  |
| Heading 4 | slm-heading-4 | complete |  |
| Heading 5 | slm-heading-5 | drift | letterSpacing 0.0 vs 1.92 |
| Subtitle-1 | slm-subtitle-1 | complete |  |

## Token drift

| Figma | Code | Differences |
|---|---|---|
| Color Semantic Variables (updated)/Font Colors/text-disabled | --slm-disabled-text | Light/slalomLight: #00000066 vs #00000061; Dark/slalomDark: #ffffff80 vs #ffffff61 |
| Color Semantic Variables (updated)/Font Colors/text-error | theme.error | Dark/slalomDark: #ffdbdf vs #ff6b6b |
| Color Semantic Variables (updated)/Primary Colors/success | theme.success | Light/slalomLight: #5cb85c vs #2e7d32; Dark/slalomDark: #5cb85c vs #4caf50 |
| Color Semantic Variables (updated)/Primary Colors/error-element | theme.error | Dark/slalomDark: #ffdbdf vs #ff6b6b |
| Color Semantic Variables (updated)/Border Colors/neutral-border-color | --slm-border | Dark/slalomDark: #757575 vs #eaeaea |
| Color Semantic Variables (updated)/card color/card-bg-secondary | --slm-app-card-bg | Dark/slalomDark: #424242 vs #444444 |
| Colors/Font Colors/text-disabled | --slm-disabled-text | Dark/slalomDark: #ffffff80 vs #ffffff61; BuildDark/slalomBuild: #ffffff80 vs #ffffff61 |
| button_shadow-1 | $slm-shadow-button-1 | default/default: 0 0 2 0 #73a6ff1a vs 0 0 2 0 #0000001f |
| button_shadow-4 | $slm-shadow-button-4 | default/default: 0 3 4 0 #0000001a vs 0 3 4 0 #0000001f |
| button_shadow-7 | $slm-shadow-button-7 | default/default: 0 4 5 0 #0000001a vs 0 4 5 0 #0000001f |

## Code-only tokens

| Token | Kind | Values | Uses in code |
|---|---|---|---|
| `theme.secondary` | color | slalomBuild: #0c62fb, slalomDark: #0c62fb, slalomLight: #86b1fd |  |
| `theme.background` | color | slalomBuild: #09091c, slalomDark: #333333, slalomLight: #f5f5f5 |  |
| `theme.warning` | color | slalomBuild: #ffc107, slalomDark: #ffc107, slalomLight: #b28600 |  |
| `--slm-on-surface` | color | slalomBuild: #ffffffde, slalomDark: #ffffffde, slalomLight: #000000de | 24 |
| `--slm-hover-bg` | color | slalomBuild: #0d1b2a, slalomDark: #757575, slalomLight: #f1f3f7 | 9 |
| `--slm-disabled-bg` | color | slalomBuild: #e0e0e0, slalomDark: #e0e0e0, slalomLight: #e0e0e0 | 3 |
| `--slm-hover-overlay` | color | slalomBuild: #ffffff26, slalomDark: #ffffff26, slalomLight: #ffffff26 | 4 |
| `--slm-press-overlay` | color | slalomBuild: #0000001f, slalomDark: #0000001f, slalomLight: #0000001f | 11 |
| `--slm-subtle-overlay` | color | slalomBuild: #0000000f, slalomDark: #0000000f, slalomLight: #0000000f | 6 |
| `--slm-hover-tint` | color | slalomBuild: #ffffff0a, slalomDark: #ffffff0a, slalomLight: #0000000a | 2 |
| `--slm-text-secondary` | color | slalomBuild: #ffffff99, slalomDark: #ffffff99, slalomLight: #00000099 | 18 |
| `--slm-error` | color | slalomBuild: #ff6b6b, slalomDark: #ff6b6b, slalomLight: #d2023f | 14 |
| `--slm-error-hover` | color | slalomBuild: #ff6b6bcc, slalomDark: #ff6b6bcc, slalomLight: #d2023fcc | 3 |
| `--slm-error-outline-hover` | color | slalomBuild: #ff6b6b1a, slalomDark: #ff6b6b1a, slalomLight: #f1f3f7 | 1 |
| `--slm-error-subtle` | color | slalomBuild: #ff6b6b1a, slalomDark: #ff6b6b1a, slalomLight: #d2023f1a | 2 |
| `--slm-warning` | color | slalomBuild: #f57c00, slalomDark: #f57c00, slalomLight: #b28600 | 1 |
| `--slm-success` | color | slalomBuild: #5cb85c, slalomDark: #5cb85c, slalomLight: #2e7d32 | 16 |
| `--slm-success-press-overlay` | color | slalomBuild: #00000052, slalomDark: #00000052, slalomLight: #00000052 | 3 |
| `--slm-success-outline-hover` | color | slalomBuild: #5cb85c1a, slalomDark: #5cb85c1a, slalomLight: #f1f3f7 | 1 |
| `--slm-success-subtle` | color | slalomBuild: #5cb85c1a, slalomDark: #5cb85c1a, slalomLight: #2e7d321a | 2 |
| `--slm-ring-fill` | color | slalomBuild: #0ed3eb, slalomDark: #0ed3eb, slalomLight: #0ed3eb | 0 |
| `--slm-ring-bg` | color | slalomBuild: #e6e6e6, slalomDark: #e6e6e6, slalomLight: #e6e6e6 | 0 |
| `--slm-accordion-expanded-header-hover` | color | slalomBuild: #3fe7f5, slalomDark: #97bbfd, slalomLight: #2a75fb | 1 |
| `--slm-accordion-collapsed-hover` | color | slalomBuild: #0f0f2e, slalomDark: #4e4e4e, slalomLight: #f0f3f8 | 1 |
| `--slm-accordion-content-border` | color | slalomBuild: #ffffff1f, slalomDark: #ffffff26, slalomLight: #dbdbdb | 2 |
| `--slm-input-outline` | color | slalomBuild: #eaeaea, slalomDark: #eaeaea, slalomLight: #090f20 | 5 |
| `--slm-mandatory` | color | slalomBuild: #ff6b6b, slalomDark: #ff6b6b, slalomLight: #d2023f | 5 |
| `--slm-switch-track-off` | color | slalomBuild: #808080, slalomDark: #808080, slalomLight: #9c9c9c | 1 |
| `--slm-switch-track-on` | color | slalomBuild: #1be1f2, slalomDark: #86b1fd, slalomLight: #79a3fa | 1 |
| `--slm-switch-track-border` | color | slalomBuild: #79747e, slalomDark: #79747e, slalomLight: #79747e | 0 |
| `--slm-switch-thumb` | color | slalomBuild: #ccbfd6, slalomDark: #ccbfd6, slalomLight: #ffffff | 1 |
| `--slm-skeleton-bone` | color | slalomBuild: #1a1a3c, slalomDark: #555555, slalomLight: inherit | 1 |
| `--slm-skeleton-shimmer` | color | slalomBuild: #ffffff08, slalomDark: #ffffff0d, slalomLight: inherit | 1 |
| `--slm-toast-error-bg` | color | slalomBuild: #c97a8f, slalomDark: #e89aaf, slalomLight: #f8bbd0 | 1 |
| `--slm-toast-error-text` | color | slalomBuild: #000000de, slalomDark: #000000de, slalomLight: #000000de | 1 |
| `--slm-dp-icon-bg` | color | slalomBuild: #00000000, slalomDark: #00000000, slalomLight: #ffffff | 1 |
| `--slm-dp-sel-gray` | color | slalomBuild: #1a1a3c, slalomDark: #616161, slalomLight: #e0e0e0 | 2 |
| `--slm-stepper-connector` | color | slalomBuild: #333333, slalomDark: #666666, slalomLight: #dbdbdb | 3 |
| `--slm-primary-subtle` | color | slalomBuild: #1be1f20d, slalomDark: #86b1fd14, slalomLight: #0c62fb0d | 1 |
| `--slm-app-bg` | color | slalomBuild: #09091c, slalomDark: #333333, slalomLight: #fafafa | 0 |
| `--slm-app-tab-border` | color | slalomBuild: #1a1a3c, slalomDark: #555555, slalomLight: #e8e8e8 | 0 |
| `--slm-app-tab-text` | color | slalomBuild: #ffffff99, slalomDark: #ffffff99, slalomLight: #666666 | 6 |
| `--slm-app-tab-active-text` | color | slalomBuild: #ffffffde, slalomDark: #ffffffde, slalomLight: #333333 | 0 |
| `--slm-grid-divider` | color | slalomBuild: #80808014, slalomDark: #80808014, slalomLight: #80808014 | 6 |
| `--slm-grid-section-divider` | color | slalomBuild: #80808026, slalomDark: #80808026, slalomLight: #80808026 | 5 |
| `--slm-showcase-label-title` | color | slalomBuild: #ffffffde, slalomDark: #ffffffde, slalomLight: #000000de | 1 |
| `--slm-showcase-label-text` | color | slalomBuild: #ffffff8c, slalomDark: #ffffff8c, slalomLight: #0000008c | 4 |
| `--slm-showcase-code-bg` | color | slalomBuild: #131330, slalomDark: #333333, slalomLight: #f0f0f0 | 5 |
| `$slm-space-5` | spacing | default: 20 | 1 |
| `$slm-space-7` | spacing | default: 28 | 1 |
| `$slm-space-9` | spacing | default: 36 | 1 |
| `$slm-space-10` | spacing | default: 40 | 1 |
| `$slm-space-11` | spacing | default: 44 | 1 |
| `$slm-space-12` | spacing | default: 48 | 1 |
| `$slm-space-13` | spacing | default: 52 | 1 |
| `$slm-space-14` | spacing | default: 56 | 1 |
| `$slm-space-15` | spacing | default: 60 | 1 |
| `$slm-space-16` | spacing | default: 64 | 1 |
| `$slm-border-0` | stroke | default: 0 | 1 |
| `$slm-border-lg` | stroke | default: 4 | 1 |
| `$slm-border-xl` | stroke | default: 8 | 1 |
| `$slm-elevation-0` | effect | default: 0 0 2 0 #00000024 | 0 |
| `$slm-elevation-1` | effect | default: 0 1 2 0 #00000024 | 0 |
| `$slm-elevation-2` | effect | default: 0 2 2 0 #00000024 | 0 |
| `$slm-elevation-3` | effect | default: 0 3 2 0 #00000024 | 0 |
| `$slm-elevation-4` | effect | default: 0 4 2 0 #00000024 | 0 |
| `$slm-elevation-5` | effect | default: 0 5 2 0 #00000024 | 0 |
| `$slm-elevation-6` | effect | default: 0 6 2 0 #00000024 | 0 |
| `$slm-elevation-7` | effect | default: 0 7 2 0 #00000024 | 0 |
| `$slm-elevation-8` | effect | default: 0 8 2 0 #00000024 | 0 |
| `$slm-shadow-button-2` | effect | default: 0 2 2 0 #0000003d | 1 |
| `$slm-shadow-header` | effect | default: 0 4 4 0 #00000026 | 1 |

## Design-only tokens

| Token | Kind | Values | Close code value |
|---|---|---|---|
| Color Semantic Variables (updated)/Font Colors/text-high-emphasis | color | Light: #000000e6, Dark: #ffffff | |
| Color Semantic Variables (updated)/Font Colors/text-medium-emphasis | color | Light: #00000099, Dark: #ffffffb3 | |
| Color Semantic Variables (updated)/Font Colors/text-icon-fill | color | Light: #000000, Dark: #000000 | |
| Color Semantic Variables (updated)/Font Colors/text-high-contrast-bg-1 | color | Light: #000000, Dark: #000000 | |
| Color Semantic Variables (updated)/Primary Colors/background-disable-field | color | Light: #e0e0e0, Dark: #e0e0e033 | |
| Color Semantic Variables (updated)/Primary Colors/background-table cell | color | Light: #fafafa, Dark: #424242 | nearly `--slm-app-card-bg` |
| Color Semantic Variables (updated)/Primary Colors/primary-fill-hover | color | Light: #0c62fb1a, Dark: #86b1fd4d | |
| Color Semantic Variables (updated)/Primary Colors/menu-icon | color | Light: #00000099, Dark: #ffffffb3 | |
| Color Semantic Variables (updated)/Primary Colors/toggle-background-off | color | Light: #9b9b9b, Dark: #757575 | |
| Color Semantic Variables (updated)/Primary Colors/toggle-background-on | color | Light: #73a6ff, Dark: #86b1fd99 | |
| Color Semantic Variables (updated)/Primary Colors/toggle-thumb | color | Light: #ffffff, Dark: #e0e0e0 | |
| Color Semantic Variables (updated)/Primary Colors/background-chip-emphasis-1 | color | Light: #deff4d66, Dark: #9488f066 | |
| Color Semantic Variables (updated)/Primary Colors/background-chip-emphasis-2 | color | Light: #0c62fb1a, Dark: #86b1fd4d | |
| Color Semantic Variables (updated)/Border Colors/primary-border-reduced | color | Light: #86b1fd, Dark: #86b1fd80 | |
| Color Semantic Variables (updated)/Border Colors/table-neutral-border-color | color | Light: #dbdbdb, Dark: #616161 | nearly `--slm-dp-sel-gray` |
| Color Semantic Variables (updated)/Border Colors/field-border-default | color | Light: #757575, Dark: #ffffff80 | |
| Color Semantic Variables (updated)/Border Colors/field-border-error | color | Light: #d2023f, Dark: #ffa6af | |
| Color Semantic Variables (updated)/semantic button color/outline/positive-outlined-txt | color | Light: #5cb85c, Dark: #5cb85c | |
| Color Semantic Variables (updated)/semantic button color/outline/positive-outlined-stroke-default | color | Light: #5cb85c, Dark: #5cb85c | |
| Color Semantic Variables (updated)/semantic button color/outline/positive-outlined-stroke-hover | color | Light: #5cb85c, Dark: #5cb85c | |
| Color Semantic Variables (updated)/semantic button color/outline/positive-outlined-overlay-pressed | color | Light: #0000004d, Dark: #ffffff1a | |
| Color Semantic Variables (updated)/semantic button color/outline/positive-outlined-stroke-pressed | color | Light: #5cb85c, Dark: #5cb85c | |
| Color Semantic Variables (updated)/semantic button color/outline/positive-outlined-stroke-disable | color | Light: #9b9b9b, Dark: #9b9b9b | |
| Color Semantic Variables (updated)/semantic button color/outline/positive-outlined-txt-disable | color | Light: #9b9b9b, Dark: #9b9b9b | |
| Color Semantic Variables (updated)/semantic button color/outline/negative-outlined-txt | color | Light: #d2023f, Dark: #ffa6af | |
| Color Semantic Variables (updated)/semantic button color/outline/negative-outlined-txt-disable | color | Light: #00000066, Dark: #ffffff80 | |
| Color Semantic Variables (updated)/semantic button color/outline/negative-outlined-stroke-default | color | Light: #d2023f66, Dark: #ffa6af | |
| Color Semantic Variables (updated)/semantic button color/outline/negative-outlined-stroke-hover | color | Light: #d2023f66, Dark: #ffa6af | |
| Color Semantic Variables (updated)/semantic button color/outline/negative-outlined-overlay-pressed | color | Light: #0000004d, Dark: #ffffff1a | |
| Color Semantic Variables (updated)/semantic button color/outline/negative-outlined-stroke-pressed | color | Light: #d2023f66, Dark: #ffa6af | |
| Color Semantic Variables (updated)/semantic button color/outline/negative-outlined-stroke-disable | color | Light: #9b9b9b, Dark: #757575 | |
| Color Semantic Variables (updated)/semantic button color/contained/negative-contained-bg-default | color | Light: #d2023f, Dark: #ffa6af | |
| Color Semantic Variables (updated)/semantic button color/contained/negative-contained-bg-hover | color | Light: #d2023fcc, Dark: #ffa6af | |
| Color Semantic Variables (updated)/semantic button color/contained/negative-contained-bg-pressed | color | Light: #d2023f, Dark: #ffa6af | |
| Color Semantic Variables (updated)/semantic button color/contained/negative-contained-overlay-pressed | color | Light: #0000004d, Dark: #0000001a | |
| Color Semantic Variables (updated)/semantic button color/contained/negative-contained-bg-disable | color | Light: #9b9b9b, Dark: #757575 | |
| Color Semantic Variables (updated)/semantic button color/contained/negative-contained-txt-disable | color | Light: #d3d3d3, Dark: #424242 | |
| Color Semantic Variables (updated)/button Colors/contained/contained-btn-pressed-overlay | color | Light: #ffffff4d, Dark: #0000004d | |
| Color Semantic Variables (updated)/button Colors/contained/contained-btn-disabled-bg | color | Light: #0c62fb4d, Dark: #86b1fd4d | |
| Color Semantic Variables (updated)/button Colors/neutral-outlined/outlined-neutral-btn-default-stroke | color | Light: #000000e6, Dark: #ffffff | |
| Color Semantic Variables (updated)/button Colors/neutral-outlined/outlined-neutral-btn-txt | color | Light: #000000e6, Dark: #ffffffb3 | |
| Color Semantic Variables (updated)/button Colors/neutral-outlined/outlined-neutral-btn-hover-overlay | color | Light: #0000001a, Dark: #ffffff1a | |
| Color Semantic Variables (updated)/button Colors/neutral-outlined/outlined-neutral-btn-pressed-overlay | color | Light: #0000004d, Dark: #ffffff4d | |
| Color Semantic Variables (updated)/button Colors/neutral-outlined/outlined-neutra-btn-disable-stroke | color | Light: #00000066, Dark: #757575 | |
| Color Semantic Variables (updated)/button Colors/neutral-outlined/outlined-neutra-btn-disable-txt | color | Light: #00000066, Dark: #ffffff80 | |
| Color Semantic Variables (updated)/button Colors/outlined/outlined-btn-default-stroke | color | Light: #86b1fd, Dark: #86b1fd66 | |
| Color Semantic Variables (updated)/button Colors/outlined/outlined-btn-hover-border | color | Light: #86b1fd, Dark: #86b1fd80 | |
| Color Semantic Variables (updated)/button Colors/outlined/outlined-btn-pressed-overlay | color | Light: #bdbdbd4d, Dark: #0000001a | |
| Color Semantic Variables (updated)/button Colors/outlined/outlined-btn-pressed-stroke | color | Light: #86b1fd, Dark: #86b1fd80 | |
| Color Semantic Variables (updated)/button Colors/outlined/outlined-btn-disable-txt | color | Light: #00000066, Dark: #ffffff80 | |
| Color Semantic Variables (updated)/button Colors/text/text-btn-overlay-pressed | color | Light: #0c62fb33, Dark: #86b1fd33 | |
| Color Semantic Variables (updated)/button Colors/plain/plain-txt | color | Light: #00000099, Dark: #ffffffb3 | |
| Color Semantic Variables (updated)/button Colors/plain/plain-txt-overlay-pressed | color | Light: #00000033, Dark: #ffffff1a | |
| Color Semantic Variables (updated)/button Colors/plain/plain-txt-disable | color | Light: #00000066, Dark: #ffffff80 | |
| Color Semantic Variables (updated)/shadow colors/shadow-1 | color | Light: #0000001a, Dark: #0000001a | nearly `--slm-press-overlay` |
| Color Semantic Variables (updated)/shadow colors/shadow-2 | color | Light: #00000024, Dark: #00000024 | nearly `--slm-press-overlay` |
| Color Semantic Variables (updated)/shadow colors/shadow-3 | color | Light: #00000026, Dark: #00000026 | nearly `--slm-press-overlay` |
| Color Semantic Variables (updated)/shadow colors/shadow-5 | color | Light: #0000003d, Dark: #0000003d | |
| Color Semantic Variables (updated)/shadow colors/shadow-6 | color | Light: #00000040, Dark: #00000040 | |
| Color Semantic Variables (updated)/card color/card-stroke-primary | color | Light: #dbdbdb, Dark: #757575 | |
| Color Semantic Variables (updated)/card color/card-stroke-secondary | color | Light: #dbdbdb, Dark: #eaeaea4d | |
| Radius/radius-0 | radius | default: 0 | |
| Radius/radius-l | radius | default: 8 | |
| Radius/radius-xl | radius | default: 24 | |
| Radius/radius-pill | radius | default: 9999 | |
| Radius/radius-pill | radius | Business @ Slalom: 9999, Me @ Slalom: 9999 | |
| Text/weight-500 | fontWeight | default: 500 | |
| space variables/elevation/Elevation-0 | effect | default: 0 | |
| space variables/elevation/Elevation-1 | effect | default: 1 | |
| space variables/elevation/Elevation-2 | effect | default: 2 | |
| space variables/elevation/Elevation-3 | effect | default: 3 | |
| space variables/elevation/Elevation-4 | effect | default: 4 | |
