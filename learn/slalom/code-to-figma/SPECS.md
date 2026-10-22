# Code components to build in Figma

From the source, read without running it. Bind every value to the variable named here; where a value has none, say so in your report rather than leaving it raw silently.

## SExpansionPanels

`src/components/SExpansionPanels.vue`. Slalom Design System accordion container component.

Boolean properties: **multiple** (default false).
Slots: default.
Look comes from: v-expansion-panels (the UI library's defaults): read its documentation for the inner layout.

| Selector | Property | Value | Bind to |
|---|---|---|---|
| `.s-expansion-panels` | display | `flex` |  |
| `.s-expansion-panels` | flex-direction | `column` |  |
| `.s-expansion-panels` | gap | `8px` | space variables/gap/ga-2 (same value; also Radius/radius-l, space variables/padding/uniform/pa-2) |
| `.s-expansion-panels` | width | `100%` |  |
| `.s-expansion-panels` | max-width | `370px` |  |
| `.s-expansion-panels .v-expansion-panel` | border-radius | `4px !important` | Radius/radius-m (same value; also Radius/radius-m, Corner radius/Medium) |
| `.s-expansion-panels .v-expansion-panel` | margin | `0 !important` | space variables/gap/ga-0 (same value; also space variables/padding/top/pt-0, space variables/padding/bottom/pb-0) |
| `.s-expansion-panels .v-expansion-panel` | background | `transparent` | no Figma variable has #00000000 for background |
| `.s-expansion-panels .v-expansion-panel::after` | display | `none` |  |
| `.s-expansion-panels .v-expansion-panel-title` | padding | `0` | space variables/padding/top/pt-0 (same value; also space variables/padding/bottom/pb-0, space variables/padding/uniform/pa-0) |
| `.s-expansion-panels .v-expansion-panel-title` | min-height | `unset` |  |
| `.s-expansion-panels .v-expansion-panel-title` | font-size | `inherit` |  |
| `.s-expansion-panels .v-expansion-panel-title__overlay` | display | `none` |  |
| `.s-expansion-panels .v-expansion-panel-text__wrapper` | padding | `0` | space variables/padding/top/pt-0 (same value; also space variables/padding/bottom/pb-0, space variables/padding/uniform/pa-0) |

## SSkeletonLoader

`src/components/SSkeletonLoader.vue`. Slalom Design System skeleton placeholder component.

Variant properties: **type**: text, card, list, table (default 'text').
Text properties: **ariaLabel** (default 'Loading content').
Look comes from: v-skeleton-loader (the UI library's defaults): read its documentation for the inner layout.

| Selector | Property | Value | Bind to |
|---|---|---|---|
| `.s-skeleton` | width | `100%` |  |
| `.s-skeleton.v-skeleton-loader--type-image` | max-width | `340px` |  |
| `.s-skeleton.v-skeleton-loader--type-image` | border-radius | `8px` | Radius/radius-l (same value) |
| `.s-skeleton.v-skeleton-loader--type-image` | overflow | `hidden` |  |
| `.s-skeleton :deep(.v-skeleton-loader__bone)` | background | `var(--slm-skeleton-bone)` | code token --slm-skeleton-bone is 'inherit' here, so the UI library's default applies |
| `.s-skeleton :deep(.v-skeleton-loader__bone)::after` | background | `linear-gradient(90deg, transparent, var(--slm-skeleton-shimmer), transparent)` | code token --slm-skeleton-shimmer is 'linear-gradient(90deg, transparent, inherit, transparent)' here, so the UI library's default applies |
