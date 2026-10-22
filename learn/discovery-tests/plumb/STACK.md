# Stack: plumb

A draft from `scan_repo.py`, run 2026-10-22 on `/Users/chrisaxelson/projects/plumb`. The scan reads files only, so check each line. Fix what's wrong, answer the questions at the end, then fill in **Confirmed**.

**Confirmed:** not yet (name and date when a person has checked this)

## What this repository is

**An app with no component layer** (medium confidence). Evidence: package.json says "private": true.

package.json describes it as: Plan an alcove built-in from three measurements: 3D model, steps, cut list, priced shopping list.

## Frameworks and libraries

No UI framework: the interface is plain JavaScript, HTML and CSS.

| Kind | Name | Version | Declared in |
|---|---|---|---|
| Build tool | Vite | ^8.3.4 | package.json (devDependencies) |

Package manager: npm.

## Design tokens

- **css-custom-properties** in `src/ui/styles.css`: 14 definitions; prefixes `--alert-`, `--rule-`, `--orange-`

## Components (0)

No reusable components found: no component folder and no package exports.

## Storybook and docs

- Storybook: not configured, 0 story files.

**Tier:** below 2. No component layer in code, so learn works from the Figma side and this file only records the stack.

## Questions for whoever knows the stack

1. Do your product teams use a shared component library from another repository or package? If so, where is it?
   - Answer:
2. This app builds its interface without a component layer we could find. Is a shared component library planned, and in which framework?
   - Answer:
