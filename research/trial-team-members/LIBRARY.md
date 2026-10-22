# Official [Business@Slalom] Design System
- File key: LMgKpbsEmxRpiHBKd9YGlw (protected, ~/.claude/lockstep.json)
- Library key: lk-4d32c666c34b7ce0dae25581cacff4a609a205cd71ddc196d008cb5e22966ce3df6bc93078611a04dfe06f7397d47f85e7fd2866b77bad437a53bac83581f180
- Fonts: Slalom Sans (Regular, Bold)
- Read on: 2026-10-22

## Components
| Label | Name | Variant axes (options) | Other properties | Slots | Default size | Usage rules from the description |
|---|---|---|---|---|---|---|
| header | Header | Version: Default, Taxonomy | none | none | 1728×64 | App shell header; nested avatar menu. |
| container | container | type: general container, table container | none | header, Table slot | 1400×145 | Page section surface, 32px padding, min width 460. Use table container when there's a table: table in Table slot, heading and controls in header. |
| card | card | type: tonal/elevated/small; status: Default/hover/banner; primary color: true/false | has header, has CTA | header slot, content Slot, CTA slot | 400×351 | One coherent topic per card. |
| button | button | size lg/md/sm; variant contained_button, outlined, text, Plain, neutral_outlined, icon, icon contained; status enabled/disabled/hover/pressed/sync | Text, icon-left, icon right, title case (true), uppercase | none | 156×48 | md is default. contained = primary, neutral_outlined = Cancel, icon = toolbar or repeated-row icon action. Labels are Title Case. |
| semanticButton | semantic Buttons | semantic negative/positive; variant contained_button/outlined; Size lg/md/sm; status default/disable/hover/pressed | label, icon left, icon right, Title Case | none | 156×48 | negative for Remove/Delete. Outlined inside tables, lists and action groups; contained only when the action stands alone. |
| textField | input/textField | state; has value false/true/textField; Label style label on/label in | field label, content, assistive text, icon-left, icon-right, Assistive Text, is required | none | 332×104 | Not every combination exists: empty fields use enabled + has value=false + label on. |
| singleSelect | single-select | status enable/hover/focused/error/disable; has value; type label on/label-in | label text, dropdown text, assistive text (bool + text), is Required (true!), left icon | none | 332×104 | Filters, categories, assignment choices. |
| avatar | v-avatar | size xs/s/m/lg/xl; image version | Collegue initials | none | 28×28 | Initials when no image. |
| chip | Chip | Chip Type (Traditional, Traditional Neutral, Highlight Primary/Secondary/Tertiary, Tool Badge, Color Tag); Size; Density | Show Color Tag, Show Close Icon, Show Left Icon, right icon | none | 133×38 | Labels, tags, statuses. Text is a plain layer, not a property. |
| tableCell | Clean and Highlight Table Cell | Size 40/48/56 Cell or Last; Table Cell Type Regular/Clean Heading/Highlight Heading | Cell Content, Cell Content 2, Clean Heading Text, Show Avatar, Avatar Initials, Show Label Group, Has Right/Left Icon, has slot | Slot (Regular only) | 110×40 | Standard tables; Last variant for the final row. |
| dataTableCell | Data Heavy Table Cell | Height Size, Type, Status Bar, State | many | Slot, Slot2 | 76×40 | Only for complex, data-heavy tables. |
| modal | modal | type alert/data/announcement; rounded corner | close, has icon, Show CTA Section, Sentence Case | content slot, CTA Section | 600×353 (data: 1200×928) | alert = warnings/urgent decisions; data = data entry and tasks. rounded corner=true only; 24 radius and 24 padding, don't override. Title is text layer "Modal content". |
| listSection / listItem | list-section / list item | type / status | label, toggle, icons, descriptions | list container slot | 912 wide | Menus and settings lists. |
| emptyState | empty State | Type horizontal/vertical | has CTA | none | 1152×264 | No-content and no-results views. |
| divider | divider | Property 1: Alpha/Gamma/beta/new | none | none | 965×111 | No description. |
| icons | plus, delete 1, close, icon/action/search, magnify 1, filter 1, account-multiple-plus-outline 1 | n/a | n/a | n/a | 24×24 | Plain icon components. |

## Tokens
- Colour: text-regular #000, text-medium-emphasis (black, medium opacity), text-error #d2023f; background-page #fafafa, background-surface #fff, background-table default #fff; primary #0c62fb; success #5cb85c; neutral-border-color #dbdbdb.
- Spacing: pa-0/1/2/3/4/6/8 = 0/4/8/12/16/24/32 (uniform padding); px-*, pt-*, pb-* sides; gap ga-0…ga-16 = 0…64 in 4s.
- Radius: radius-0 0, radius-m 4, radius-l 8, radius-xl 24, radius-pill 9999.
- Stroke: border-sm 1, border-md 2.
- Text styles: Heading 3–6, Subtitle-1/2, Body-1 (16), Body-2 (14), Caption (12); all Slalom Sans.
- Effects: surface-shadow (cards, surfaces, containers), header-shadow.
- Keys: inventory.variables.json.

## Shape of the library
- Text components: no. Page titles and descriptions are styled text layers (text style + bound colour), so instance share is capped below 100%.
- Containers with slots: container, card, modal, list-section, table cell. Card, modal (data: 1200×928) and container ship at fixed sample sizes: set slots and instances to HUG after filling.
- No table/row component: tables are rows of table-cell instances in auto-layout frames.
- No search-field variant: use input/textField with a search icon.
- No status badge: use Chip.
- Casing conflict: buttons force Title Case ("Invite Member") and modal titles Sentence Case.
