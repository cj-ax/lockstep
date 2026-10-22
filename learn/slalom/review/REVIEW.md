# Review: Slalom design system review

Tick one option per item (`[x]`). Write a new name after `rename to:` or `name:` where an option allows it, and anything else on the `Note:` line. Items left unticked stay open and nothing is generated from them.

## Conflicts

### Component fonts  `conflict-component-fonts-a23d8a`
- Figma: Slalom Sans in every text style
- Code: DM Sans hard-coded in SAutocomplete, SButton, SCombobox, SDatePicker, SEmptyState, SSelect, SStepper, STextArea, STextField; Roboto hard-coded in SProgressRing
- Should these components use the system font token instead?

- [ ] Figma is right
- [ ] Code is right
- [ ] Something else

Note:

### SButton label case  `conflict-sbutton-label-case-50c3fb`
- Figma: Title Case by default (button)
- Code: text-transform: uppercase in src/components/SButton.vue
- Which casing is right for labels?

- [ ] Figma is right
- [ ] Code is right
- [ ] Something else

Note:

### button variant  `conflict-button-variant-06380a`
- Figma: icon, icon contained, neutral_outlined
- Code: nothing extra
- Should Figma's variant and code's variant offer the same options?

- [ ] Figma is right
- [ ] Code is right
- [ ] Something else

Note:

### semantic Buttons variant  `conflict-semantic-buttons-variant-ee88e2`
- Figma: nothing extra
- Code: plain, text
- Should Figma's variant and code's variant offer the same options?

- [ ] Figma is right
- [ ] Code is right
- [ ] Something else

Note:

### text-disabled / --slm-disabled-text  `conflict-text-disabled-slm-disabled-text-b1dffa`
- Figma: Color Semantic Variables (updated)/Font Colors/text-disabled, Light: #00000066; Dark: #ffffff80
- Code: --slm-disabled-text, slalomLight: #00000061; slalomDark: #ffffff61
- Which value is right?

- [ ] Figma is right
- [ ] Code is right
- [ ] Something else

Note:

### text-error / theme.error  `conflict-text-error-theme-error-2bb341`
- Figma: Color Semantic Variables (updated)/Font Colors/text-error, Dark: #ffdbdf
- Code: theme.error, slalomDark: #ff6b6b
- Which value is right?

- [ ] Figma is right
- [ ] Code is right
- [ ] Something else

Note:

### success / theme.success  `conflict-success-theme-success-505284`
- Figma: Color Semantic Variables (updated)/Primary Colors/success, Light: #5cb85c; Dark: #5cb85c
- Code: theme.success, slalomLight: #2e7d32; slalomDark: #4caf50
- Which value is right?

- [ ] Figma is right
- [ ] Code is right
- [ ] Something else

Note:

### error-element / theme.error  `conflict-error-element-theme-error-a23bc3`
- Figma: Color Semantic Variables (updated)/Primary Colors/error-element, Dark: #ffdbdf
- Code: theme.error, slalomDark: #ff6b6b
- Which value is right?

- [ ] Figma is right
- [ ] Code is right
- [ ] Something else

Note:

### neutral-border-color / --slm-border  `conflict-neutral-border-color-slm-border-98df06`
- Figma: Color Semantic Variables (updated)/Border Colors/neutral-border-color, Dark: #757575
- Code: --slm-border, slalomDark: #eaeaea
- Which value is right?

- [ ] Figma is right
- [ ] Code is right
- [ ] Something else

Note:

### card-bg-secondary / --slm-app-card-bg  `conflict-card-bg-secondary-slm-app-card--c73669`
- Figma: Color Semantic Variables (updated)/card color/card-bg-secondary, Dark: #424242
- Code: --slm-app-card-bg, slalomDark: #444444
- Which value is right?

- [ ] Figma is right
- [ ] Code is right
- [ ] Something else

Note:

### text-disabled / --slm-disabled-text  `conflict-text-disabled-slm-disabled-text-b1dffa`
- Figma: Colors/Font Colors/text-disabled, Dark: #ffffff80; BuildDark: #ffffff80
- Code: --slm-disabled-text, slalomDark: #ffffff61; slalomBuild: #ffffff61
- Which value is right?

- [ ] Figma is right
- [ ] Code is right
- [ ] Something else

Note:

### button_shadow-1 / $slm-shadow-button-1  `conflict-button-shadow-1-slm-shadow-butt-2431d3`
- Figma: button_shadow-1, default: 0 0 2 0 #73a6ff1a
- Code: $slm-shadow-button-1, default: 0 0 2 0 #0000001f
- Which value is right?

- [ ] Figma is right
- [ ] Code is right
- [ ] Something else

Note:

### button_shadow-4 / $slm-shadow-button-4  `conflict-button-shadow-4-slm-shadow-butt-a8bc2b`
- Figma: button_shadow-4, default: 0 3 4 0 #0000001a
- Code: $slm-shadow-button-4, default: 0 3 4 0 #0000001f
- Which value is right?

- [ ] Figma is right
- [ ] Code is right
- [ ] Something else

Note:

### button_shadow-7 / $slm-shadow-button-7  `conflict-button-shadow-7-slm-shadow-butt-3a856e`
- Figma: button_shadow-7, default: 0 4 5 0 #0000001a
- Code: $slm-shadow-button-7, default: 0 4 5 0 #0000001f
- Which value is right?

- [ ] Figma is right
- [ ] Code is right
- [ ] Something else

Note:

### Heading 5 / slm-heading-5  `conflict-heading-5-slm-heading-5-8d1c8a`
- Figma: Heading 5, letterSpacing: 0.0
- Code: slm-heading-5, letterSpacing: 1.92
- Which value is right?

- [ ] Figma is right
- [ ] Code is right
- [ ] Something else

Note:

## Missing in code

### Header  `design-only-header-938e23`
- In Figma, no code component found
- Version: Default, Taxonomy

- [ ] Build it in code
- [ ] Figma only is fine

Note:

### container  `design-only-container-1e838e`
- In Figma, no code component found
- type: general container, table container

- [ ] Build it in code
- [ ] Figma only is fine

Note:

### card  `design-only-card-d862aa`
- In Figma, no code component found
- primary color: true, false
- status: Default, hover, banner
- type: tonal, elevated, small

- [ ] Build it in code
- [ ] Figma only is fine

Note:

### card header  `design-only-card-header-196749`
- In Figma, no code component found
- Property 1: center-header, left-header

- [ ] Build it in code
- [ ] Figma only is fine

Note:

### radio button  `design-only-radio-button-21d5a5`
- In Figma, no code component found
- status: default, selected
- Size: lg, md, sm

- [ ] Build it in code
- [ ] Figma only is fine

Note:

### list item  `design-only-list-item-3b28c2`
- In Figma, no code component found
- status: Default, secondary, errored, queued

- [ ] Build it in code
- [ ] Figma only is fine

Note:

### list-section  `design-only-list-section-6bde3a`
- In Figma, no code component found
- type: menu lists, modal lists

- [ ] Build it in code
- [ ] Figma only is fine

Note:

### v-avatar  `design-only-v-avatar-7c2add`
- In Figma, no code component found
- size: lg, m, s, xl, xs
- image version: false, true

- [ ] Build it in code
- [ ] Figma only is fine

Note:

### modal  `design-only-modal-11644e`
- In Figma, no code component found
- type: alert, data, announcement
- rounded corner: false, true

- [ ] Build it in code
- [ ] Figma only is fine

Note:

### divider  `design-only-divider-ec8b27`
- In Figma, no code component found
- Property 1: Alpha, Gamma, beta, new

- [ ] Build it in code
- [ ] Figma only is fine

Note:

### content-slot  `design-only-content-slot-a1e989`
- In Figma, no code component found
- type: content-centered, content-left

- [ ] Build it in code
- [ ] Figma only is fine

Note:

### step counter  `design-only-step-counter-9357b6`
- In Figma, no code component found
- status: completed, current, next

- [ ] Build it in code
- [ ] Figma only is fine

Note:

### loading_1  `design-only-loading-1-26692c`
- In Figma, no code component found
- Property 1: start, step1, step2, step3

- [ ] Build it in code
- [ ] Figma only is fine

Note:

## Missing in Figma

### SExpansionPanels  `code-only-sexpansionpanels-e193f9`
- In code (src/components/SExpansionPanels.vue), no Figma component found
- props: multiple

- [ ] Add it to Figma
- [ ] Code only is fine

Note:

### SIcon  `code-only-sicon-568562`
- In code (src/components/SIcon.vue), no Figma component found
- props: name, size, ariaLabel

- [ ] Add it to Figma
- [ ] Code only is fine

Note:

### SSkeletonLoader  `code-only-sskeletonloader-eb3cb8`
- In code (src/components/SSkeletonLoader.vue), no Figma component found
- props: type, ariaLabel

- [ ] Add it to Figma
- [ ] Code only is fine

Note:

## Agreed

### 87 tokens, 14 type styles and 15 components in both Figma and code  `agreed-87-14-15-4ff2f0`
- 13 tokens with matching names
- 74 tokens matched by value alone: check these in COVERAGE.md
- Type styles: Subtitle-2, Body-2, Body-1, Caption, button-lg-upcase, button-lg-ttlcase, button-md-upcase, button-md-ttlcase, button-sm-upcase, button-sm-ttlcase, Heading 6, Heading 3, Heading 4, Subtitle-1
- Components: button = SButton, semantic Buttons = SButton, input/textField = STextField, text area = STextArea, single-select = SSelect, autocomplete = SAutocomplete, date picker = SDatePicker, Switch Toggle = SSwitch, Status Alert Bar = SAlert, Toast Notifications = SToast, step = SStepper, Accordion Row = SExpansionPanel, empty State = SEmptyState, loading = SProgressRing, combobox = SCombobox. Their differences are listed as conflicts.
- Lockstep suggests: Approve all

- [ ] Approve all
- [ ] Hold for line-by-line review

Note:
