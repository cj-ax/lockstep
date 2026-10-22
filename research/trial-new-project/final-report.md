I built both frames in a new draft, but **the form frame isn't finished.** Four of its input boxes render too narrow, and I couldn't fix that within the three build passes the skill allows. The confirmation dialog is done.

**Draft:** https://www.figma.com/design/CTIj3A4tvG2KnY3eSqXX66

- **Latest form:** `NewProject / Form / v3` (node 6:348)
- **Dialog:** `NewProject / Discard dialog / v1` (node 2:2521)
- Forms v1 and v2 are earlier attempts with the same defect. They sit on their own rows as a record and can be deleted.

## What isn't finished

On the form, the outlines of **Project name**, **Description**, **Owner** and **End date** draw at the library component's default width (about 332–414px) instead of the full column. On Description and Owner, the resize handle and dropdown arrow end up floating off to the right of the box. The layers themselves are full width. Both of Figma's renderers show the defect, so it's real.

What I found while testing:
- A field on its own, or directly inside a library container, stretches correctly.
- Inside the full page structure it doesn't, whichever variant, fill or fixed width, or nesting I used. (A screenshot taken inside the build script looked right, but the later renders still showed the defect.)
- Start date is unaffected.

The next things to try: check in the Figma desktop editor whether it's only a rendering fault, or ask the design-system team why the field's outline doesn't follow the instance width at this depth.

## How faithfully it uses your library

| Pass | Frame | Library instances | Bound properties | Detached | Hard-coded colours | Auto layout | Integrity issues | What I saw |
|---|---|---|---|---|---|---|---|---|
| 1 | Form | 78.9% | 100% | 0% | 0% | 100% | 0 | Four fields render too narrow |
| 1 | Dialog | 80% | 100% | 0% | 0% | 100% | 0 | Clean |
| 2 | Form | 78.9% | 100% | 0% | 0% | 100% | 0 | Same defect (unchanged rebuild) |
| 3 | Form | 78.9% | 100% | 0% | 0% | 100% | 0 | Same defect (fields moved straight into the container) |

- **Everything is a library part except five text layers.** All of it uses library variables, text styles or auto layout, with no detached instances and no hard-coded colours. That's an overall score of 96.
- **The five plain text layers** are the page title, the guidance line, the Visibility label and help text, and the dialog message. The library has no text components, so these use library text styles and colour variables. That's why library instances can't reach 100%.
- **The score didn't catch the visible defect.** It scores 96 with zero integrity issues anyway, which is why the screenshots matter.

## Decisions I made

- **Owner:** the library's autocomplete field, pre-filled with "Chris Axelson" from your Figma account, with the hint "Defaults to you. Search to pick someone else." There's no dedicated people picker.
- **Dates:** text fields with the library's calendar icon, showing an MM/DD/YYYY hint. The library's date picker is a calendar pop-up, not a field.
- **Visibility:** all three options start unselected, following "fields start empty", with one line explaining each option. Say if you'd rather default to Private.
- **Notify the team:** a list section with two toggle rows, both off. Your brief didn't say whether they start on or off.
- **Required fields:** Project name and Owner are marked required.
- **Button wording:** the library forces Title Case, so the buttons read "Create Project" and "Keep Editing".
- **Button styles:** Cancel uses the neutral outlined style, as the library recommends. Discard uses the outlined negative style, because the library reserves the filled version for actions that stand alone.
- **Dialog:** the "alert" type with its warning icon and close button. It's centred over an empty page because the library has no scrim colour token.
- **Layout:** a 1440px desktop frame with the form in an 880px library container. The gap between fields is 24px, the slot's own spacing.

## Not in the library

These are worth raising with the design-system team:
- The text field outline not following the instance width, described above.
- No radio group with its own label. I built the Visibility group from radio instances and styled text.
- Radio labels are a plain text layer rather than a component property, unlike every other form control.
- No date-input field.
- No people picker.
- No scrim colour token for dialogs.
- Title Case is forced on buttons while dialog titles use sentence case.

**Library setup:** the setup the build needs was missing, so I created it first. The library summary and component, token and layer-structure inventories are in `lockstep/business-slalom/`, and the build script is `lockstep/build-new-project.js`. No fonts or libraries were added beyond your design system and its Slalom Sans.
