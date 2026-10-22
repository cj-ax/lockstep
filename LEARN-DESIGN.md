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

**Library inventory.** This uses the existing `inventory.js` (components, variables and structure) for a **published** library. Half-built libraries are often unpublished, and importing by key fails for local components. So `inventory.js` gains a `local` mode: it walks the library file's own COMPONENT and COMPONENT_SET nodes, and reads its local variable collections (`getLocalVariableCollectionsAsync`) in place. It switches to each page once per call and fans pages out across calls, following Figma's page rule.

**Usage audit**, the new `audit.js`, runs on each product file. It reuses `score.js`'s walk, which already separates authored nodes, library internals and slot contents, and raw values from bound ones. It records:
- **instances:** per component, the count, the variant combinations used, and which overrides were made;
- **detached frames:** the count, and the original `detachedInfo.componentKey`. This is direct evidence of which component they came from, and the strongest signal for both de facto and deleted components;
- **raw values:** every colour, type style (family, size, weight, line height), spacing, radius, stroke width and effect, with whether it's bound, to which variable or style, and the node it's on;
- **repeated structures:** a structural hash of each frame subtree. The hash covers node types, auto-layout direction, sizing modes, padding and gap, and child order, and ignores text content and exact sizes. Clusters of three or more matching subtrees become de facto component candidates.

Output goes to `audit/<file>.json`, capped per call, with pagination for large files. Reading these files needs the guard change in **"Reading protected files"** below.

### 4. Code harvest (milestone 2–3)

- **Tier 3:** `stack.json` already lists components and props. This step adds token values, resolved from SCSS, CSS variables, the Tailwind theme or a theme object to concrete values, plus import paths and default props.
- **Tier 2:** the same from Storybook. Its `index.json` gives story titles and args, so neither a repo nor a running Storybook is needed if the static build is available.
- **Tier 0–1:** the framework's public API, as in DS-AI-Bridge Tier 1, mapped from the questionnaire's answer.

### 5. Reconcile (milestone 3)

**Token proposals.** These cluster raw and bound values across all sources:
- colours by OKLab distance (ΔE under 2 is the same token);
- spacing and radius by exact value, with ±1px drift flagged against the nearest 4px step;
- type by the tuple (family, size, weight, line height).

Each cluster becomes a proposal with:
- a suggested name, taken from existing variable or code names where any match, otherwise from role, such as `color/text/default`;
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

### 6. Review (milestone 3)

A review page, published as an artifact, using the database capability so rulings persist and can be shared. A person can approve, rename, merge or reject each token proposal, de facto component and conflict. `proposals.json` records each ruling with who made it and when. Steps 7–8 read only approved items.

### 7. Generate (milestone 4–5)

- **(a) Tokens:** DTCG JSON (`tokens.json`) is the code-side source of truth, exported to CSS custom properties. The same tokens become Figma variables in a **new draft file**, with modes where the sources had them, such as light and dark.
- **(b) Component docs:** one Markdown page per component, covering purpose, variants and when to use each, props mapped to Figma properties, do and don't with real examples from the audit, and accessibility notes. This is the documentation deliverable for Josh's programme.
- **(c) AI context:** `DESIGN_SYSTEM_CONTEXT.md` and `design-system-registry.json`, in DS-AI-Bridge's existing format, for code generation.
- **(d) Lockstep files:** `LIBRARY.md`, `keys.json` and the three inventory files, in the format `build` already reads.
- **(e) Code to Figma:** for code-only and de facto components, draft Figma components in the draft library file, using Figma's `figma-generate-library` skill. They're bound to the generated variables, with variant properties taken from the code props.

**A wrinkle for `build`.** `build` imports components by key from a *published* library, and draft components are local to their file. Until the org publishes the draft library, `build` works inside that draft file. Its helpers need to accept local components by node ID as well as by key, which is a small change.

### 8. Gate (milestone 2 onwards, on the fixture)

See "Proving it" below. Each milestone reports its numbers the way REPORT.md does.

## Reading protected files

Today the write guard blocks every `use_figma` call on a protected file, including reads. Learn has to read the library and product files, and protecting them is right, so the guard needs a read-only allowance.

**Proposal for milestone 2:**
- `render.py` stamps Lockstep's read-only scripts (`inventory`, `score`, `audit`) with a first-line marker: `// lockstep-readonly sha256=<hash of the rest of the code>`.
- The guard allows `use_figma` on a protected file only when the code carries that marker, the hash matches, and the script is on the read-only list.
- Any other code, including a hand-edited copy of a read-only script, stays blocked.
- The read-only scripts never call a mutating API, and a unit test lists every mutating Plugin API call to enforce that.

**Fallback:** the user duplicates each source file to their Drafts ("Duplicate to your drafts" in Figma), and learn reads the copies. This needs one manual step per file, which is why it's the fallback.

Read-only MCP tools (`search_design_system`, `get_metadata`, `get_variable_defs`, `get_screenshot`) aren't matched by the guard and need no change.

## Proving it: degrade and recover

**Fixture:** a draft built from Figma's Simple Design System (SDS) and then broken on purpose, in a way that's deterministic and logged. It's built by `learn/fixture/make_fixture.js`, and `learn/fixture/ground-truth.json` records the truth. See `learn/fixture/README.md`. It contains:
- **half a library:** some SDS components turned into local, unpublished components on a Library page, and the rest deleted;
- **product pages:** the settings page (four frames) from Lockstep's SDS build, with:
  - instances of deleted components detached;
  - half the remaining instances detached;
  - most variable bindings replaced by raw values;
  - a few raw values nudged to simulate drift;
- **a half-built token collection:** a local "Tokens (WIP)" collection holding about a third of SDS's tokens, some under different names.

**Metrics, scored by `learn/fixture/score_recovery.py` from milestone 2:**

| Metric | Definition |
|---|---|
| Token recall | Ground-truth tokens used in the original frames that appear among approved token proposals, matched by value |
| Token precision | Approved proposals that match a ground-truth token, out of all approved proposals |
| Drift detection | Injected drift values that are flagged and attached to the right token |
| Component recall | Deleted or detached components found as de facto or detached-from candidates |
| WIP mapping | WIP variables correctly mapped to their SDS token despite renaming |
| Build faithfulness | `build` on the learned system: Lockstep's usual score plus a screenshot check |

Recall is measured before review, against all proposals, to test the harvest. Precision is measured after a scripted review that approves everything, which makes it a worst case.

## Milestones

| # | Scope | Done means |
|---|---|---|
| **1** | This design; the degraded SDS fixture and its ground truth; intake and stack discovery | `learn` runs steps 1–2 on a real repo (Slalom DS), a non-DS app and no repo; the fixture exists in a draft with its ground truth committed |
| 2 | `inventory.js` local mode; `audit.js`; read-only guard allowance; token clustering; `score_recovery.py` | Token and component recall on the fixture, reported |
| 3 | Code harvest (Tier 2–3), reconcile, coverage matrix, review page | Coverage and conflicts for the fixture and for Slalom (Figma plus `design-system-beta`) |
| 4 | Generate tokens, docs, context and draft variables; `build` reads learned files | `build` on the fixture's learned system, scored |
| 5 | Code to Figma: draft components for code-only and de facto parts | Draft library components scored by `score` and a screenshot check |
| 6 | Pilot on Josh's programme | Whatever that programme needs first, most likely documentation |

## Open questions for review

1. **The read-only allowance in the guard**, or duplicate-to-drafts only? Recommendation: the allowance, with the fallback documented.
2. **One `lockstep:learn` command, or one per step?** Recommendation: one command that resumes from `SOURCES.md`, plus the existing `init` for a finished library.
3. **Token naming:** propose names from roles (`color/text/default`) or keep whatever names exist, however messy? Recommendation: keep existing names when there's a match, and use role names only for unnamed values.
4. **Where the review page lives:** an artifact with the database capability (shareable, persistent), or a Markdown checklist in the repo (simplest)? Recommendation: start with Markdown in milestone 3, and make it a page if reviewers aren't technical.
