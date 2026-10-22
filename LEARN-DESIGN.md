# lockstep:learn: design

`learn` turns DS-AI-Bridge's manual workflow into a command that works for any organisation. That workflow was "How To Reproduce", 8 steps, done by hand over 2–3 days.

It starts from whatever exists: a half-built Figma library, product files nobody tidied, a partial codebase, or just someone who knows what framework the developers use. It ends with a design system that Lockstep's `build` can use faithfully, and that a documentation programme can publish.

This document refines the brief (`lockstep-learn-brief.md`, 2026-10-22) against what Lockstep already does. Milestone 1 builds the first two steps and the test fixture. Everything after that is design for review.

## Who it's for

- **The first real pilot** is Josh's programme, which is pivoting to "full documentation mode" and wants a code-to-Figma flow "as we get the house in order".
- **The general case** is any team with:
  - a half-finished system: some components published, the rest drawn or detached in product files;
  - no documentation;
  - little or no codebase.

## What it produces, by tier

Every combination of sources produces something useful. Precision rises as sources arrive, as in DS-AI-Bridge, where you can start at Tier 1 and move right.

| Sources available | Tier | What learn can produce |
|---|---|---|
| Nothing but a framework name, or not even that | 0 | An architect questionnaire, and a skeleton STACK.md |
| Product files only | 1a | Proposed tokens (clustered raw values) and de facto components from repeated structures, both with usage counts |
| A partial library (with or without product files) | 1b | All of 1a, plus the library's own components and variables, a coverage matrix, and drift between the library and how files use it |
| Plus Storybook or component docs | 2 | Component names, props and import paths mapped to the design side |
| Plus the design-system repo | 3 | Real token values and component APIs; code-only components; drift between code and design |

## Principles carried over

- **The org's files are read-only.** Lockstep writes only to drafts it creates. Every source file named at intake (library and product files) is added to the protected list, not just the library.
- **Nothing is generated from unapproved proposals.** A person reviews every token and component proposal (step 6).
- **Show the evidence.** Every proposal carries usage counts and example node IDs, so a reviewer can click through to what it came from.
- **What you see wins**, as in `build` and `score`. Visual checks use screenshots, not only layer data.
- **The architect is a person, not a guess.** When there's no repo, learn writes questions for whoever knows the stack. It doesn't infer the framework from screenshots.

## Pipeline

All state lives in the user's project under `lockstep/<org>/`, so a run can stop at any step and resume.

```
1 Intake ──▶ 2 Stack discovery ──▶ 3 Design harvest ──▶ 4 Code harvest ──▶ 5 Reconcile
                 │ (confirmed by a person)    │ (usage audit)                     │
                 ▼                            ▼                                   ▼
          STACK.md, stack.json       audit/*.json                coverage.json, proposals.json
                                                                                  │
                         8 Gate ◀── 7 Generate ◀── 6 Review (approve, rename, merge)
```

### 1. Intake (milestone 1)

This is a plain-words interview, one question at a time, each with an "I don't know" answer. It asks for:
- the organisation's name, which sets the `lockstep/<org>/` folder;
- the library link, if any;
- product-file links (2–5 representative files, not every file);
- the repository path or URL, a Storybook URL, and other documentation links;
- who the architect is, or who knows the stack, and how to reach them;
- what the user wants first: documentation, faithful builds, or both.

**Output:** `SOURCES.md`, which holds the answers, every Figma file key with its role, and the computed tier. Every Figma file key is also merged into `.claude/lockstep.json` as protected, named by role ("source: library", "source: product file").

### 2. Stack discovery (milestone 1)

**With a repo:** `scripts/scan_repo.py <path>` reads it without running anything or installing dependencies. It finds:
- frameworks and UI libraries, from `package.json` and lockfiles: React, Vue, Angular, Svelte, Solid, Web Components; MUI, Vuetify, Chakra, Ant, Radix, shadcn/ui, Headless UI, Mantine, Bootstrap, Tailwind, styled-components, Emotion, Vanilla Extract;
- token sources:
  - CSS custom properties;
  - SCSS variables;
  - the `theme` in a Tailwind config;
  - theme objects (`createTheme`, `createVuetify({ theme })`, `extendTheme`);
  - DTCG or Style Dictionary JSON;
- the components a package exports, with their props:
  - TypeScript `Props` interfaces and types;
  - Vue `defineProps`;
  - `propTypes`;
- Storybook configuration and story titles;
- a docs site (Docusaurus, VitePress, Storybook docs) if one is checked in.

It writes `stack.json` (the machine-readable result) and a draft `STACK.md`. The draft says what was found, where, and how confident each finding is, and asks the questions only a person can answer, such as "Is `SButton` the only button the product uses, or do some screens still use `v-btn`?".

**Without a repo:** `scan_repo.py --no-repo --hint "…"` writes a short questionnaire, `ARCHITECT-QUESTIONS.md`, in plain words, that the designer forwards. It's pre-filled with what the Figma side suggests, such as "The library's components look like Vuetify's (`v-btn` variants); is that right?". When the answers come back, learn folds them into STACK.md.

**Gate:** a person confirms STACK.md before any step that depends on it. Learn records the confirmation and its date in the file.

### 3. Design harvest (milestone 2)

**Library inventory.** This uses the existing `inventory.js` (components, variables and structure) for a **published** library. Half-built libraries are often unpublished, and importing by key fails for local components. So there's a separate read-only script, `inventory_local.js` (built in milestone 2). It runs in the library file itself, so `inventory.js`, which imports, never has to. It has two parts:
- **components:** walks each page's COMPONENT and COMPONENT_SET nodes (loading pages with `page.loadAsync`, never switching the current page) and records each one's properties, publish status, instance count in the file, and a structure signature;
- **variables:** reads local variable collections and styles in place.

Pages can be fanned out across calls with `--pages`.

**Usage audit**, the new `audit.js` (built in milestone 2), runs on each product file. It reuses `score.js`'s walk, which already separates authored nodes, library internals and slot contents, and raw values from bound ones. It records:
- **instances:** per component, the count, the variant combinations used, and which overrides were made;
- **detached frames:** the count, and the original `detachedInfo.componentKey`. This is direct evidence of which component they came from, and the strongest signal for both de facto and deleted components. The key is the *variant's* key, not the set's, so learn groups detached copies by name and keeps the keys as evidence;
- **library internals:** the variables bound inside library instances, with their values and the properties they drive. This names values the product layers left raw: `#1e1e1e` is `Text/Default/Default` because the library's own text uses it;
- **raw values:** every colour, type style (family, size, weight, line height), spacing, radius, stroke width and effect, with whether it's bound, to which variable or style, and the node it's on;
- **repeated structures:** a structural signature of each frame subtree, at two depths. It covers node types, auto-layout direction, padding and gap (rounded to 4, so drift doesn't split a pattern), paint presence, text style and child order. It ignores text content, sizes and sizing modes, because a component hugs and its placed copies stretch. The *full* signature (3 levels) matches identical parts. The *shell* signature (1 level) matches containers with different contents, such as cards. Clusters of three or more become de facto component candidates. A slot counts as one node, whatever it holds.

Output is aggregated (values with counts and example node IDs, not every node), so it fits `use_figma`'s 48 KB. Large files are paged with `--offset`. Reading these files needs the guard change in **"Reading protected files"** below.

### 4. Code harvest (milestone 3)

- **Tier 3 (built: `harvest_code.py`):** `stack.json` already lists components and props. This step adds token values per theme, resolved from CSS custom properties (scoped by theme selector), Sass and Less variables and theme objects, following `var()` and `$` references. It also groups type variables into styles (`heading-6-size`, `-weight`, `-line-height`, `-spacing`), counts each token's uses, and records per component its `text-transform`, its hard-coded font families and its hard-coded colours. Not yet: Tailwind config values, DTCG files, import paths and default props.
- **Tier 2 (not built):** the same from Storybook. Its `index.json` gives story titles and args, so neither a repo nor a running Storybook is needed if the static build is available.
- **Tier 0–1:** the framework's public API, as in DS-AI-Bridge Tier 1, mapped from the questionnaire's answer.

### 5. Reconcile (milestone 3; built as `reconcile.py`)

**What it compares.** The design side is a published library's inventory or learn's proposals; the code side is `code.json`. Tokens are compared within a kind. Modes pair with themes by name (`Light` with `slalomLight`, `BuildDark` with `slalomBuild`). Letter spacing in percent is converted with the font size. Components pair by name after dropping prefixes (`SButton`, `v-avatar`) and a short synonym list (`modal` = `dialog`, `Status Alert Bar` = `alert`). Their variant axes are compared value by value after removing words shared with the axis, prop and component names (`label in` against `labelType: in`, `Error Toast` against `error`).

Interaction-state axes (hover, pressed, focused) and on/off axes are listed but not compared: code styles states in CSS.

**What milestone 3 changed from the plan.**
- **A token is drift only if the name matches word for word, or closely with one mode agreeing.** A loose name match produced false drift on Slalom (`success` against `theme.primary`, because the folder "Primary Colors" counted).
- **Every code token with the same value is covered,** not just the best-named one. Otherwise `--slm-primary` came out code-only next to an exact Figma match.
- **The design side has to be complete for "code-only" to mean anything.** `inventory.js` only sees variables and styles the inventoried components use. So learn searches the library for each unmatched code component and style, and reads styles by key (`inventory --part styles`). On Slalom, that turned 9 code-only components into matches and 4 code-only type styles into 3 complete and 1 drift.

**Token proposals** (`propose.py`, built early, in milestone 2). These group raw and bound values across all sources:
- **Evidence is never merged.** A value bound to a variable or style anywhere, or defined as a local variable, is a token of its own. The milestone 2 fixture showed why: SDS's own greys sit within OKLab ΔE 2 of each other (`#2c2c2c` and `#303030` are 1.6 apart; `#757575` and `#767676` are 0.3 apart). "ΔE under 2 is the same token" would have merged real tokens.
- **Drift is an unbound value near a token** (colour: ΔE under 2; numbers: within 1), used a third as often or less. It's attached to that token. A near tie goes to the value designers place most, and the alternative is listed.
- **Unbound values with nothing near them** are proposals of their own.
- **Type** is grouped by the tuple (family, style, size, line height, letter spacing).

Each cluster becomes a proposal with:
- a suggested name. It's taken from the library variables bound to that value, choosing the one whose words fit how designers use it: a value used on shapes and frames gets `Background/…` over `Text/…`. WIP names are used when there's no library name. Role names (`color/text/default`) for unnamed values come in milestone 3;
- its usage count;
- the drift values it absorbed;
- example node IDs.

**Coverage matrix** (`coverage.json`, with a readable `COVERAGE.md`). Every component and token is marked as one of:

| Status | Meaning |
|---|---|
| complete | In design and code, and they agree |
| design-only | In Figma, not in code |
| code-only | In code, not in Figma |
| de facto | A repeated structure or a detached-from component that no published component covers |
| drift | In both, but the values differ (for example `#2C2C2C` in Figma, `#2B2B2B` in `_tokens.scss`) |

**Conflicts list.** Rules the sources disagree on, such as Slalom's button casing: Title Case in Figma, uppercase in code. Each conflict names both sources and needs a ruling.

### 6. Review (milestone 4; built as `review.py` and a review page)

`review.py build` turns proposals or coverage into decisions, each with its evidence, options and Lockstep's suggestion:
- **From proposals:** tokens (approve, rename, reject), component candidates, WIP variables and local components.
- **From coverage:** each conflict (Figma is right, code is right, something else), each component on only one side, and one item for everything both sides already agree on.

It writes `REVIEW.md`, a checklist that works anywhere, and `review.html`, a page published as an artifact. The page stores each ruling in its database (`rulings/<item id>`: decision, name, note, who, when). It resolves people's names when it renders and never stores them. It degrades to read-only for viewers who can't write, and shows a notice where there's no database.

`review.py apply` reads rulings from the page's database or a ticked checklist and writes `approved.json`. Only approved items go in; everything else is listed as rejected or still open.

### 7. Generate (milestone 4 builds (a) and (b); the rest is milestone 5)

- **(a) Tokens (built: `generate.py`):** `tokens.json` in DTCG 2025.10 format, and `tokens.css` with `:root` and one `[data-theme]` block per mode.
  - Modes from different collections ("Dark mode", "Dark", "BuildDark") are normalised to one theme each (dark, build).
  - Type styles become DTCG typography tokens and `.type-<name>` classes.
  - Each token's `$extensions` record where it came from, who approved it, its code name and the drift it absorbed.
- **(a) Draft Figma variables (built in milestone 5: `variables.js`):** the same tokens as a "Learned tokens" collection in a **new draft file**, one mode per theme. Each variable is scoped by kind, so spacing is offered only for gaps and padding. Its description records the drift values it absorbed. Approved type styles become local text styles.
- **(b) Component docs (built):** one Markdown page per approved component. Each covers:
  - its purpose and when to use it, from the Figma description;
  - its Figma variants;
  - its code props;
  - how the two map;
  - the decisions and open questions that touch it.

  Pages say what the sources say and nothing more. With no description, a page says one is needed. A description cut at the inventory's 1,500 characters is marked. Do/don't examples and accessibility notes need sources Lockstep doesn't read yet.
- **(c) AI context (built: `context.py`):** `DESIGN_SYSTEM_CONTEXT.md` and `design-system-registry.json`, in DS-AI-Bridge's shape, for code generation. The content:
  - rules from what was decided;
  - tokens with their CSS names (code's own name only when the names match, otherwise the generated name with a "same value as" note);
  - each component's code API and Figma mapping;
  - open conflicts, listed with both sides so a generator asks instead of picking one.
- **(d) Lockstep files (built: `library.py`):** `LIBRARY.md`, `keys.json` and `variables.json` for a learned library. Learned components and variables are referenced as `local:<id>`, and published ones by key. `LIBRARY.md` lists every component's properties, so `build` needs no inventory files.
- **(d') Components approved as new ones (built: `snapshot.js` and `rebuild.js`):** the org's files are protected, and the plugin API can't copy layers between files. So a read-only snapshot records an approved example's layers as data in the source file, and a rebuild recreates it in the draft:
  - every colour, spacing, radius and stroke is bound to a learned variable, and drift values snap to the token that absorbed them;
  - text gets its text style and becomes a role-named text property;
  - library parts inside are exposed instances;
  - slots become real, empty slots.

  Rebuilt components have one variant: detached copies don't say which variant they came from.
- **(e) Code to Figma (milestone 6):** for code-only components a person ruled "Add it to Figma".
  - `code_spec.py` reads each one's source without running it. It records props (finite values become variants), booleans, text props, slots, the UI-library parts it wraps, and every style value with the Figma variable to bind it to. Variables are found through the coverage, or by value and the property's purpose, so a gap prefers a gap token.
  - An agent then builds the component set in a draft (learn step 9), binding every value. Where the look comes from the wrapped library's defaults rather than the repo, the description says so.
  - De facto components are rebuilt from Figma examples instead (step 8).

**A wrinkle for `build` (handled in milestone 5).** `build` imports components by key from a *published* library, and draft components are local to their file. Until the org publishes the draft library, `build` works inside that draft file. It reaches learned components and variables by local ID, and `score --local-library-page` counts them as library instances.

### 8. Gate (milestone 2 onwards, on the fixture)

See "Proving it" below. Each milestone reports its numbers the way REPORT.md does.

## Reading protected files

Today the write guard blocks every `use_figma` call on a protected file, including reads. Learn has to read the library and product files, and protecting them is right, so the guard needs a read-only allowance.

**Built in milestone 2:**
- `render.py` stamps Lockstep's read-only scripts (`score`, `audit`, `inventory_local`) with a first line, `// lockstep-readonly {"script": …, "values": …}`, naming the script and the values it was filled with.
- The guard allows `use_figma` on a protected file only when it can **re-render the script from that line and get exactly the same code**. A hash alone wouldn't do: anyone can compute a hash of edited code. Each value must be plain JSON, so a value can't smuggle code in.
- Any other code, a hand-edited copy, code appended to a render, or a stamp naming a write script stays blocked. So does the allowance on any tool but `use_figma`.
- `tests/test_readonly.py` checks this, and checks that the read-only scripts call none of a list of mutating Plugin API calls. The list does flag `fix.js`, `settle.js`, `inventory.js` (it imports) and the fixture's `degrade.js`.

**Fallback:** the user duplicates each source file to their Drafts ("Duplicate to your drafts" in Figma), and learn reads the copies. This needs one manual step per file, which is why it's the fallback.

Read-only MCP tools (`search_design_system`, `get_metadata`, `get_variable_defs`, `get_screenshot`) aren't matched by the guard and need no change.

## Proving it: degrade and recover

**Fixture:** a draft built from Figma's Simple Design System (SDS) and then broken on purpose, in a way that's deterministic and logged. It's built by `capture_truth.js`, `degrade.js` and `census.js` in `learn/fixture/`, and `learn/fixture/ground-truth.json` records the truth. See `learn/fixture/README.md`. It contains:
- **product pages:** the settings page (four frames) from Lockstep's SDS build, with:
  - every instance of five "unpublished" components detached;
  - half the remaining instances detached;
  - 80% of variable bindings replaced by raw values;
  - ten raw values nudged to simulate drift;
- **a half-built token collection:** a local "Tokens (WIP)" collection with nine renamed SDS tokens and two unused ones;
- **a started-and-abandoned library page:** three local components that duplicate deleted parts, used nowhere.

**Metrics, scored by `learn/fixture/score_recovery.py` from milestone 2:**

| Metric | Definition |
|---|---|
| Token recall | Ground-truth tokens used in the original frames that appear among approved token proposals, matched by value |
| Token precision | Approved proposals that match a ground-truth token, out of all approved proposals |
| Drift detection | Injected drift values that are flagged and attached to the right token |
| Component recall | Deleted or detached components found as de facto or detached-from candidates |
| WIP mapping | WIP variables correctly mapped to their SDS token despite renaming |
| Names | Suggested names that are a library name for that value and use, and that are exactly the designer's token |
| Build faithfulness | `build` on the learned system: Lockstep's usual score plus a screenshot check |

Recall is measured before review, against all proposals, to test the harvest. Precision is measured after a scripted review that approves everything, which makes it a worst case.

## Milestones

| # | Scope | Done means |
|---|---|---|
| **1** | This design; the degraded SDS fixture and its ground truth; intake and stack discovery | `learn` runs steps 1–2 on a real repo (Slalom DS), a non-DS app and no repo; the fixture exists in a draft with its ground truth committed |
| **2** | `inventory_local.js`; `audit.js`; read-only guard allowance; token and component proposals (`propose.py`); `score_recovery.py` | Token and component recall on the fixture, reported: see `learn/fixture/RECOVERY.md` and REPORT.md |
| **3** | Code harvest (tier 3), reconcile, coverage matrix, conflicts | Coverage and conflicts for Slalom (Figma plus `design-system-beta`): `learn/slalom/COVERAGE.md`; the fixture's design-only coverage, since SDS's code isn't in hand. Tier 2 (Storybook) and the review page move to milestone 4 |
| **4** | Review page and checklist; apply rulings; generate DTCG tokens, CSS and component docs | Both runs generated from approved items only: the fixture from a scripted take-every-suggestion review, Slalom with only the agreed item approved and all 31 contested items left open. The Slalom review page is published for the team |
| **5** | Draft Figma variables, rebuilt components, AI context, LIBRARY.md for `build`; `build` on the learned system, scored | A fresh agent with only the plugin built an unseen Billing page on the fixture's learned library. Rescored independently: Overview 100, Dialog 90. See REPORT.md |
| **6** | Code to Figma: specs from code (`code_spec.py`), then an agent builds draft components for code-only parts | A fresh agent built Slalom's SSkeletonLoader (4 types) and SExpansionPanels from the code in a draft: every value bound (324/324), no hard-coded colours, auto layout throughout. See REPORT.md |
| 7 | Pilot on Josh's programme | Whatever that programme needs first, most likely documentation |

## Open questions for review

1. ~~The read-only allowance in the guard, or duplicate-to-drafts only?~~ Built in milestone 2, with the fallback documented.
2. **One `lockstep:learn` command, or one per step?** Recommendation: one command that resumes from `SOURCES.md`, plus the existing `init` for a finished library.
3. **Token naming:** propose names from roles (`color/text/default`) or keep whatever names exist, however messy? Recommendation: keep existing names when there's a match, and use role names only for unnamed values.
4. ~~Where the review page lives~~ Both, built in milestone 4: an artifact page with a database for reviewers, and REVIEW.md as the fallback.
