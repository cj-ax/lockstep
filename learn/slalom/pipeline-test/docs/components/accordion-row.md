# Accordion Row

In Figma: **Accordion Row**, code: `SExpansionPanel` in `src/components/SExpansionPanel.vue`.

Approved (approve) by pipeline test (not the Slalom team's ruling) on 2026-10-22.

## What it's for

Organizes related information into a row with a visible header and an expandable content area.

Its primary use is progressive disclosure: keep the section title visible while showing detailed content only when the row is expanded, reducing clutter without leaving the current view.

Variants:
• Type=custom: a preconfigured detail layout with status information, a progress ring, labeled detail rows, and a comments/notes group this is the version only for engagement summary.

• Type=general: a flexible layout with a header slot and content slot for context-specific content. The content slot is empty by default and must be populated for a meaningful expanded view.

• status=Collapsed: header visible; content hidden.

• status=Collapsed Hover: collapsed presentation with pointer-over feedback.

• status=Expanded: header and content visible.

• status=Expanded Hover: expanded presentation with pointer-over feedback.

• Both types support all four statuses, for eight variants. The current Figma default is Type=custom, status=Collapsed.

## When to use it

The custom version is only for Engagement Summary section. For all the other applications the recommended version is the general version.

## Variants in Figma

| Property | Options |
|---|---|
| status | Collapsed, Collapsed Hover, Expanded, Expanded Hover |
| Type | custom, general |

Other properties: Accordion Row Name (text), Show Progress Ring (boolean), Show Row 1 (boolean), Show Row 2 (boolean), Show Row 3 (boolean), Show Row 4 (boolean), Show Comments Group (boolean), header slot (slot), content slot (slot), engagement dates (boolean).

## Props in code

| Prop | Type | Values | Default |
|---|---|---|---|
| `title` | string |  |  |
| `progress` | number |  |  |
| `statusRows` | DataField[] |  |  |
| `dataRows` | DataRow[] |  |  |
| `notes` | PanelNotes |  |  |

Slots: default, icon, secondary-icon.

## How Figma maps to code

| Figma property | Code prop | Notes |
|---|---|---|
| status |  | no matching code prop |
| Type |  | no matching code prop |
