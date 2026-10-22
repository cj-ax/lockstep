I built both components as draft component sets in a new Figma file, and the library file was never written to.

**Link:** https://www.figma.com/design/C43HHid9PjGoM2PYXITDtT, page "Code components"

- **SSkeletonLoader** has a `type` property with the code's values: text (the default), card, list and table.
- **SExpansionPanels** has a `multiple` property (false by default, true) and a `default` slot. The slot holds four of the library's own Accordion Row instances, with the panels from `PanelGroup.vue`. When `multiple` is false one panel is open; when it's true, two are.
- A review frame next to them shows every variant in Light and Dark mode. Both modes render correctly.

## What came from our code and what from Vuetify
**From our code:**
- **Skeleton:** the four types and how they map to Vuetify's loader types, full width, and the card's 340px max width and 8px corners.
- **Panels:** the vertical column with an 8px gap, 370px max width, no padding, transparent background, 4px panel corners, Vuetify's dividers and hover overlay removed, and the sample panel data.

**From Vuetify's defaults:**
- **Skeleton:** the code just wraps Vuetify's loader, so all of its inner layout comes from Vuetify. That covers the heading and text-line sizes and widths, the 16px margins, 8px between lines, the 150px card image, 48px avatars in 72px rows, the table's header, six rows and footer, the 4px loader corners and the surface background.
- **Panels:** only the open/close behaviour. Each panel's look comes from the library's Accordion Row.

I couldn't open Vuetify's source because web access was blocked, so the Vuetify sizes are from my knowledge of Vuetify 3. The table layout is the part I'm least sure of. Please compare against the live showcase.

## How faithfully it uses our tokens
I scored it with Lockstep:
- Every colour, padding, gap and corner radius is bound to a library variable (324 of 324). There are no hard-coded colours, everything uses auto layout, and nothing is detached.
- Every panel is a real library instance. The skeleton shapes are drawn, because the library has nothing to build them from.
- **One stand-in token:** the skeleton's grey shapes use `background-disable-field`. In Light mode it matches Vuetify's grey exactly. In Dark it comes out about #636363, where the code uses #555555. It's a disabled-field colour, so I'd propose a dedicated skeleton token.
- Sizes like the 24px heading and 48px avatar stay as plain numbers because the library has no size tokens.

## Decisions I made
- I made a new file, "Slalom code components (draft)", rather than building anywhere near the library.
- **ariaLabel** isn't a Figma property because it's never visible. It's noted in the component description.
- **multiple** is a true/false variant rather than a boolean property, because a boolean can only show or hide layers. The variant shows one panel open against two.
- The panels use the Accordion Row's "custom" type because it matches the code's structured panel body. The library itself recommends "general" outside the Engagement Summary screen.
- I renamed the first panel from "Accordion Row Name" to "Engagement Summary", because the code's title reads as placeholder text.
- The skeleton is 452px wide by default: the showcase's 500px surface minus its padding.

## Not finished
- **The shimmer animation isn't modelled, and neither is the Build theme.** The library's colour collection only has Light and Dark modes.
- **The skeleton's shorter lines have fixed widths**, so they won't scale if someone resizes the component.
- **Panel 1's last row still shows the library's sample** ("SOW Date" with a tick, not "Another Type: Info"). The instance has no layer for that value, so changing it would mean detaching.
- **The library's Accordion Row doesn't match the code when open.** It has a light-tinted header and shows Contract type as a chip. The code uses a solid primary-blue header with white text and a plain value. That's a gap in the library's component; I didn't change it.
- **The sign-offs aren't the team's.** The build/skip rulings in `review/approved.json` are tagged "pipeline test (not the Slalom team's ruling)". I went ahead because you said the team agreed, but they should be recorded properly.
- **Two likely bugs in the code (I read it, didn't run it):**
  - `SSkeletonLoader.vue` uses `:deep()` in a style block that isn't scoped, so the Dark and Build skeleton colours probably never apply.
  - Its card rule targets a class name from Vuetify 2, so the 340px / 8px card styling may not apply either.
- **Not reviewed or published:** both components stay in the draft until your team reviews and publishes them.

**Dependencies:** nothing new. It uses the library's Slalom Sans fonts, variables and Accordion Row. The Figma build scripts are in `lockstep/build-skeleton.js` and `lockstep/build-expansion-panels.js`, and the component specs are in `lockstep/slalom/code-to-figma/`.