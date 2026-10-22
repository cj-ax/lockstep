I've built the Team members page and the Invite member dialog in a new draft file. Nearly everything comes from your library, and both frames are finished.

**Draft:** https://www.figma.com/design/AJVkj6T0kHAdomFSk0p7bP
The final frames are `TeamMembers / List / v2` and `TeamMembers / Dialog / v2` (node 5:458 and 5:1214). The v1 frames from the first pass sit in the row above.

Your library had no saved setup, so I ran Lockstep setup first. Its files are in `lockstep/slalom/` (`LIBRARY.md`, `keys.json` and two inventory files), and the build script is `lockstep/build-team-members.js`. The library file itself was never written to.

## How faithfully it uses the library

| Pass | Frame | Library instances | Bound to tokens | Detached | Hard-coded colours | Auto layout | Integrity issues | Score |
|---|---|---|---|---|---|---|---|---|
| 1 | List | 95.7% | 100% | 0% | 0% | 100% | 0 | 99 |
| 1 | Dialog | 85.7% | 100% | 0% | 0% | 100% | 0 | 97 |
| 2 | List | 95.7% | 100% | 0% | 0% | 100% | 0 | 99 |
| 2 | Dialog | 85.7% | 100% | 0% | 0% | 100% | 0 | 97 |

- **Library components:** everything visible is a library instance with its variants set explicitly. That covers the header, page container, search field, role select, buttons, table cells, chips and dialog. Nothing is detached and no sample text is left.
- **The three exceptions:** the page title, the page description and the dialog's intro sentence are plain text layers. Your library has no text components, so this is as high as the score can go. Each one uses a library text style and a library colour token.
- **Pass 2 fixed:** the table cells centre their content by default, so I left-aligned Member, Role and Status, headings included, and right-aligned Actions.
- **Screenshots:** in Figma's server screenshot the dialog's email box looks only half as wide as the dialog. The plugin's own render and the layer sizes show it at full width, so the file itself is correct.

## Decisions I made
- **Member list:** a table built from rows of "Clean and Highlight Table Cell", because the library has no table component. Each member cell uses the cell's built-in avatar with initials, the name, and the email as a second line. The last row uses the "Last" variant.
- **Status:** a Chip, because there's no status badge. Active uses the Traditional style and Invited uses Traditional Neutral.
- **Remove action:** a small outlined negative button labelled "Remove". The library says to use outlined, not filled, for actions inside tables.
- **Toolbar:**
  - The search box is a text field with the search icon, since there's no dedicated search component.
  - The role filter is a single-select showing "All roles".
  - The Invite button is large, the size the library allows next to a field.
- **Dialog:**
  - It's the modal's "data" type, which the library reserves for data entry, at the required rounded corners.
  - The library's sample is 1200 px wide, so I set it to 640 px to suit a two-field form.
  - Email and Role are required, and the Role field's help line explains what each role can do.
  - Buttons are Cancel (neutral outlined) and Send invite (primary).
- **Button labels:** the library forces Title Case, so they show "Invite Member" and "Send Invite", not "Invite member" as you wrote. The dialog title is "Invite member", in the sentence case the library uses for titles.
- **Page and members:** the page is 1440 px wide. The six members are made up with @example.com emails, four Active and two Invited, across all three roles.
- **Dialog frame:** it shows the header and the dialog on the page background, without the member list dimmed behind it. The library has no backdrop colour to dim it with.

## Not finished, and gaps to pass to the design-system team
- **No overlay token:** a dialog shown over the page can't be built with the library alone.
- **Missing components:** a table or row, a search field, a status badge, and text components for titles and body copy.
- **Fixed sample sizes:** the modal's data type ships at 1200 × 928, and the card and container ship at sample sizes too. Each needs resizing after it's filled.
- **Casing:** forcing Title Case on buttons conflicts with the sentence-case copy in your brief. Someone should decide which wins.
- **Not shown:** empty, loading, and no-search-results states.
