# Lockstep spike: faithful Figma writes, scored

Run 2026-10-21 on the Business@Slalom library, using the settings-page prompt (`figma/PAGE_BRIEF.md`). Every write went to a new draft file, and nothing was written to the production library (`LMgKpbsEmxRpiHBKd9YGlw`).

**Result.**
- An agent can build the page in Figma almost entirely from the org's own library: library instances with real variant properties, every authored value bound to a library variable, auto layout throughout, and nothing detached.
- It can then score the result and fix it itself.
- The Lockstep build reached a faithfulness score of **98**, against **77** for a plain Figma-MCP build of the same prompt.

## Scores

Each arm was scored over all four frames: Profile, Notifications, Account and the delete dialog. The scorer is `figma/score.js`.

| Arm | Library instances | Bound properties | Detached | Hard-coded colours | Auto layout | **Faithfulness** | Integrity issues |
|---|---|---|---|---|---|---|---|
| A. Plain Figma MCP | 42% | 45% | 0% | 1.5% | 100% | **77** | 0 |
| A + Lockstep fix pass | 42% | 77% | 0% | 1.5% | 100% | **84** | 0 |
| B. Figma MCP + DS-AI-Bridge context | 74% | 59% | 0% | 2.4% | 100% | **86** | 0 |
| C. B + Lockstep fix pass | 74% | 87% | 0% | 2.4% | 100% | **92** | 0 |
| L. Lockstep build, pass 1 (Profile only) | 91% | 100% | 0% | 0% | 100% | 98 | **2** (clipped cards) |
| **L. Lockstep build, pass 2** | **88%** | **100%** | **0%** | **0%** | **100%** | **98** | **0** |

How to read the table:
- **Faithfulness** is the mean of the five columns, with detached and hard-coded inverted.
- Every arm scored 0% detached and 100% auto layout, so the headline number compresses the spread. The first two columns carry the real difference.
- **Integrity issues** count visible breakage: content clipped by a container, or a component still showing its sample text. A frame with any integrity issue isn't done, whatever its faithfulness score.
- L's remaining 12% "non-instance" is 7 text layers: the page title, its subtitle and the dialog message. Each uses a library text style and a bound colour variable. The library has no component for them.

**The loop in practice.**
- L pass 1 scored 98 but looked wrong. The library `card` ships at a fixed 351px height, so its content slot clipped "Job title" and hid the third password field.
- That clipping is why the integrity checks now exist. Pass 2 made cards and slots hug their content: score 98, integrity 0, and screenshots confirm it.
- On A and C, the fix pass bound 80 and 29 raw values respectively to library tokens with exactly the same value, so nothing looks different. It left 69 and 9 values as human decisions, for example A's 12px radii and 240px margins, and B's 50% black scrim. There are no tokens for those values.

**The finding that matters most.**
- Binding tokens can be fixed after the fact. Choosing components can't.
- A stays at 42% library instances because it drew its cards, rows and tab bar by hand.
- Faithfulness comes from knowing the library's structure before building: which components exist, their slots and their variant axes. That's what the inventory step supplies.

## Second library: Figma's Simple Design System (2026-10-22)

This run repeated the same page on a library that has nothing to do with Slalom, to find what was secretly Slalom-specific.

| Pass | Library instances | Bound properties | Faithfulness | Integrity issues |
|---|---|---|---|---|
| v1 | 100% | 100% | 100 | 0 reported, but the screenshot showed a button still reading "Button" |
| v1, rescored with the nested-text check | 100% | 100% | 100 | 3 (sample text in button groups) |
| v2 | 100% | 100% | 100 | 1 (body text cut off, caught by the new clipped-text check) |
| **v3** | **100%** | **100%** | **100** | **0**, confirmed by screenshot |

**What carried over unchanged:**
- `score.js` and `fix.js` ran as written. The fix pass had nothing to do, because every value was already bound.
- `inventory.js` read all 16 components and 7 token collections with values, after one change: it now splits its output into two calls, because the full inventory doesn't fit in `use_figma`'s 48 KB return limit.

**What had to be written for this library:** the build script, `build-settings-sds.js`. It maps the page's intent onto this library's components:
- Card (Slot)
- Tabs as a slot of Tab instances
- Button Group with nested buttons
- the full-screen Dialog
- text components for titles and body copy

This mapping is the per-org work that `init` has to automate. Here I wrote it myself, in about 200 lines.

**What the second library exposed:**
1. **Plugin API traps the Slalom build never hit.**
   - `findAllWithCriteria({ types: ['SLOT'] })` misses slots inside an instance nested in another instance.
   - Node wrappers can't be compared with `===`; compare IDs.
   - I fixed both in every script.
2. **Two scorer blind spots.** Both builds scored 100 while visibly broken, so the headline number can't be the only gate:
   - sample text left in a component nested inside another component (a button inside a button group)
   - text overflowing a frame and being cut off by a container further up
   The scorer now flags both. Rerun against the Slalom build, it still gives 98 with no issues.
3. **The ceiling depends on the library.** This library has text components, so 100% library instances is reachable. Slalom has none, which caps it at about 88%. Instance share should be compared against what the library makes possible, not against 100.
4. **Thin descriptions didn't block the build.** This library's descriptions are mostly "Keywords: toggle". Component names, variant axes and slots were enough to build correctly. Usage judgement came from me, not the library: Cancel as Neutral, a danger button for delete, switches saving immediately. For a thinly documented library, that judgement is what `fill-gaps` would have to supply.
5. **Search behaved differently.** With this library's key, `includeLibraryKeys` filtered correctly and results were small. Slalom's oversized results come from its long descriptions; why its filtering failed is still unexplained.

## Links
- L, the Lockstep build: <https://www.figma.com/design/J1IErNfcAsPZYi3MF0cexq>. Pass 2 is the second row (frames `7:922`, `7:1302`, `7:1721`, `7:1862`); pass 1 Profile is at the top left.
- A, plain MCP, and A + fix (second row): <https://www.figma.com/design/Hhsm5yFqnvvtTAKNjEgCOm>
- B, MCP + DS-AI-Bridge, and C = B + fix (second row): <https://www.figma.com/design/w3v1epae69aKLLEOKCkr88>
- Simple Design System build, v1 to v3 in rows (v3 is the bottom row: `12:625`, `12:824`, `12:954`, `12:1079`): <https://www.figma.com/design/LVUpC4NepsxIO2nxGnI5RM>

## What the Figma MCP could and couldn't do

**Could** (all through `use_figma` and the Plugin API, from a draft file, without adding the library to that file):
- Import components, component sets, variables and text styles by key.
- Read every component's variant axes, boolean, text, instance-swap and slot properties, and its full description.
- Read **variable values**, which `search_design_system` doesn't return. Importing one variable exposes its whole collection through `getVariableCollectionByIdAsync(...).variableIds`, with Light and Dark values. Walking the bindings of the components a page uses reached 9 collections: colour, space, radius, border and font weight.
- Fill library **slots** by appending into the instance's SLOT node, so cards and modals stay real instances.
- Give the scorer everything it needs: `getMainComponentAsync().remote`, `detachedInfo`, `instance.overrides`, bound variables, text and fill styles, and `clipsContent`.

**Couldn't, or only with friction:**
- **Search output is too big.** `search_design_system` returned 84–183K characters per batch, and every arm had to save it to disk and parse it. It never returns variant property names or variable values. In my runs, `includeLibraryKeys` didn't stop results from 5–10 other libraries.
- **The library is hard to find.** `get_libraries` doesn't list the Business@Slalom library at all, either as added or as available. Its key only shows up inside search results.
- **No way to list a library's components.** `teamLibrary` returns only variable collections, and only for libraries enabled in the file; here it returned nothing. Finding component keys depends on searching.
- **`use_figma` has tight limits.** Return values are capped at 48 KB, scripts at 50K characters, and no state carries between calls. The scorer (~8K characters) and the builder (~13K) are re-sent on every run, and that is the main token cost of the loop.
- **Figma's own skills didn't reach the subagents.** `figma-use` and `figma-generate-design` are served as MCP resources, and the subagents had no resource reader. Arms A and B ran without them; the L build had them.
- **No Code Connect**, the same as in the October 19 test.

## Library issues the build ran into (for the Slalom DS team)
- **`card`:** it is fixed at 351px with a fixed-height content slot, so every builder hit clipping (B's subagent hit it too). Its `card header` names both text layers `Title`.
- **`input/textField`:** it has no `enabled + has value=true + label on` variant.
- **`Tabs`:** the default variant is Disabled.
- **Missing tokens:** there is no 4px gap token and no scrim or overlay colour. Several overlapping or deprecated collections are still bound by components: two `Radius` collections, `Colors`, and `Brand Color tokens (to be deleted)`.
- **Button casing is still unresolved.** L followed the library (Title Case). B followed DS-AI-Bridge (UPPERCASE) and used a `text` Cancel button where the library says `neutral_outlined`.

## Gaps that matter for generalizing to any org
1. **Component discovery.** A complete inventory needs either the REST API (`GET /v1/files/:key/components`, read-only and safe on the library) or a crawl that follows nested instances out from search seeds. `init` should do this once and cache it, instead of searching every session.
2. **Token discovery.** Reading the tokens that components bind works on any plan, but it misses tokens no component uses. The Variables REST API needs an Enterprise plan. `init` should combine both and mark deprecated collections, so the fixer never binds to them.
3. **Mapping intent to components.** Slalom's descriptions are rich, and the build leaned on them for slots, the switch in list item, and which button variant to use. Many orgs' libraries have empty descriptions. `fill-gaps` would need to write that guidance, or the registry would have to carry it.
4. **Rules for conflicts.** Code and Figma disagree (casing, Cancel variant). Each org needs a declared source of truth per rule, and `init`'s conflict list is where that gets decided.
5. **Packaging.** `use_figma` is the only way to run code inside Figma, so the scripts must travel with the tool. A skill that holds `inventory.js`, `score.js` and `fix.js` and sends them is realistic. A write guard should be a configurable hook (protected file keys), not one hard-coded key.
6. **The scorer still needs to grow.** It catches binding, instance use, detachment, colour, auto layout, clipped content and clipped text, and sample text (including in nested components). It doesn't yet catch overlap, a wrong variant for the context (for example a destructive action that isn't negative), or uninformative placeholder icons.

## Caveats
- **Small sample.** There was one run per arm, with the same model. Read differences of a few points as directional.
- **Who built what.** I built L myself and also wrote the scorer, so L may be tuned to what the scorer measures. A and B were built by independent subagents that never saw the scorer.
- **The score doesn't judge design quality.** A high score means the page is built *from* the library, not that it's a good page. Screenshots were checked by eye: L pass 2 looks right. Two cosmetic problems remain: the Notifications card doesn't fill the full width, and the Account cards have spare height.

## Files
- `figma/score.js`: the faithfulness score. It is read-only and org-agnostic; set `ROOT_IDS`.
- `figma/fix.js`: the auto-fix pass. It binds only raw values that exactly match a library token and lists the rest as decisions.
- `figma/build-settings.js`: the Lockstep build. Set `WHICH` and `VERSION`; it is safe to rerun.
- `figma/build-settings-sds.js`, `figma/keys.sds.json`: the same page built on Simple Design System.
- `figma/inventory.js`, `figma/keys.slalom.json`, `research/`: how the library was read, and the raw search output.
- `figma/PAGE_BRIEF.md`: the shared prompt given to every arm.
