# Official [Business@Slalom] Design System
- File key: LMgKpbsEmxRpiHBKd9YGlw (protected, ~/.claude/lockstep.json)
- Library key: lk-4d32c666c34b7ce0dae25581cacff4a609a205cd71ddc196d008cb5e22966ce3df6bc93078611a04dfe06f7397d47f85e7fd2866b77bad437a53bac83581f180
- Fonts: Slalom Sans (Regular, Bold)
- Read on: 2026-10-22

## Components
| Label | Name | Variant axes (options) | Other properties | Slots | Default size | Usage rules from the description |
|---|---|---|---|---|---|---|
| header | Header | Version: Default, Taxonomy | none | none | 1728×64 | App shell header with nested avatar menu. |
| container | container | type: general container, table container | none | header, Table slot | 1400×145 | Page section surface, 32px padding, min width 460. |
| card | card | type tonal/elevated/small; status Default/hover/banner; primary color true/false | has header, has CTA | header slot, content Slot, CTA slot | 400×351 | One coherent topic per card. Ships at a fixed sample height. |
| cardHeader | card header | Property 1: center-header, left-header | title lg, Title sm, left/right icon, has subtitle | none | 334×40 | Only inside card. Title via text layers named "Title". |
| button | button | size lg/md/sm; variant contained_button/outlined/text/Plain/neutral_outlined/icon/icon contained; status enabled/disabled/hover/pressed/sync | Text, icon-left, icon right, title case | none | 156×48 | md default. contained = primary, neutral_outlined = Cancel. Title Case. |
| semanticButton | semantic Buttons | semantic negative/positive; variant contained_button/outlined; Size; status | label, icons | none | 156×48 | negative for destructive; contained only when standalone, outlined in action groups. |
| textField | input/textField | state; has value false/true/textField; Label style | field label, content, assistive text, icon-left/right, is required | none | 332×104 | Names, titles, dates. Empty = enabled + has value=false + label on. Default icon is a calendar. |
| textArea | text area | type label on/in; status; has value | label text, content, assistive content, is required, drag handles | none | 332×192 | Descriptions, notes. |
| singleSelect | single-select | status; has value; type | label text, dropdown text, is Required (true!) | none | 332×104 | Predefined list. |
| autocomplete | autocomplete | status enable/hover/filled/focus/error/disable; type; has value | label content, content, has arrow, has icon, clear icon, chips | none | 414×104 | Long lists such as people. |
| datePicker | date picker | sections; status; rounded border | mm/yy label | none | 340×374 | Calendar popover, not a field. |
| radio | radio button | status default/selected; Size lg/md/sm | label is a text layer, no property | none | 113×48 | One choice per group. |
| switch | Switch Toggle | Toggle Status Off/On; State | none | none | 52×32 | Binary setting. |
| listItem / listSection | list item / list-section | status / type | label, bottom description, has toggle, has icon, directional | list container slot | 912 wide | Settings and menu lists; toggle inside list item. |
| avatar | v-avatar | size xs–xl; image version | Collegue initials | none | 28×28 | Initials when no image. |
| modal | modal | type alert/data/announcement; rounded corner | close, has icon, Show CTA Section | content slot, CTA Section | 600×353 | alert for urgent decisions. rounded corner=true only; title is layer "Modal content". |

## Tokens
- Colour: text-regular #000, text-medium-emphasis, text-error #d2023f; background-page #fafafa, background-surface #fff; primary #0c62fb; neutral-border-color #dbdbdb.
- Spacing: pa-0/2/4/6/8 = 0/8/16/24/32; px-*, pt-*, pb-*; gap ga-0/1/2/3/4/6 = 0/4/8/12/16/24.
- Radius: radius-0, radius-m 4, radius-l 8, radius-xl 24, radius-pill. Stroke: border-sm 1, border-md 2.
- Text styles: Heading 4, Heading 6, Subtitle-2, Body-1 (16), Body-2 (14), Caption (12). Effect: surface-shadow.
- Keys: inventory.variables.json.

## Shape of the library
- Text components: no. Titles and guidance are styled text layers (text style + bound colour), so instance share stays below 100%.
- Containers with slots: container, card, modal, list-section. Card and container ship at sample sizes: set slots and instances to HUG after filling.
- No radio group or fieldset with a group label: build a labelled group from radio instances.
- No date-input component: use input/textField (its default icon is a calendar).
- No people picker: use autocomplete with a value.
- Radio labels aren't a component property, unlike every other form control.
- Casing: buttons force Title Case, modal titles Sentence Case.
