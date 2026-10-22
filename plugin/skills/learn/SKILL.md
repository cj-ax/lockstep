---
name: learn
description: Learn an organization's design system when it isn't finished. It gathers the sources (Figma library and product files, a repository, Storybook, docs), protects every source file, works out the front-end stack from the repository or from questions for an architect, audits how the Figma files actually use colours, spacing, type and components, and drafts token and component proposals with evidence for a person to review. Use when someone has a half-built, unpublished or undocumented design system, has only product files and no library, wants design-system documentation, or wants to match their Figma files to their code.
---

# lockstep:learn: learn a design system that isn't finished

`lockstep:init` sets up a finished, published library. `learn` is for everything short of
that: some product files, a partial library, a repository, a Storybook, or only a framework
name. It works out what exists, shows the evidence, and lets a person decide what becomes
the system.

Shared scripts live in the plugin's `scripts/` folder, two levels up from this skill's base
directory (shown when the skill loads). Below, `$LOCKSTEP` is that plugin folder.

**Built so far: steps 1–5**: intake, stack discovery, design harvest with proposals, code
harvest, and reconcile (a coverage matrix and the conflicts to rule on). Steps 6–8 (review,
generate, gate) aren't built yet. When you finish step 5, show the user `COVERAGE.md` and say
the review and generate steps are coming. Don't improvise them.

Everything goes in `lockstep/<org-slug>/` in the user's project:

| File | Step | What it holds |
|---|---|---|
| `SOURCES.md` | 1 | The intake answers, every source with its role, and the tier |
| `stack.json`, `STACK.md` | 2 | The stack, found by `scan_repo.py`, then confirmed by a person |
| `ARCHITECT-QUESTIONS.md` | 2 | Only when there's no repository: questions to forward |
| `harvest/audit-<file>.json` | 3 | What each product file uses: instances, detached copies, values, repeated structures |
| `harvest/inventory-*.json` | 3 | The library file's own components, variables and styles |
| `proposals.json`, `PROPOSALS.md` | 3 | Draft tokens, de facto components, WIP mapping, unused local parts |
| `code.json` | 4 | Code tokens resolved per theme, type styles, component facts |
| `coverage.json`, `COVERAGE.md` | 5 | What's in Figma, code, both or neither, and the conflicts |

## Rules

- **The org's files are read-only.** Every Figma file named at intake, library and product
  files alike, is protected before anything else happens. Lockstep only writes to drafts.
  Learn reads protected files with read-only scripts, which the guard lets through only when
  the code is exactly what `render.py` printed. Never edit a rendered script, and never write
  your own `use_figma` code against a protected file: the guard blocks it, and it should.
- **Read repositories, never run them.** No installs, builds, scripts or tests. `scan_repo.py`
  only reads files.
- **The architect is a person.** Don't guess the stack from screenshots or file names. When
  you can't read it from a repository, ask.
- **Shell commands:** one simple command per call with literal paths: no `cd … &&` chains,
  shell variables or heredocs. Write files with the Write tool.

## 0. Check you're ready

Do `lockstep:init`'s step 0 checks (Figma connected, a Full seat, `python3`), with one
difference: steps 1 and 2 only need Figma links, not Figma access, so a missing seat isn't a
blocker yet. Mention it, because later steps need one.

## 1. Intake

Ask one question at a time, in plain words. Every question accepts "I don't know" or "none",
and you move on. Ask for:

1. The organization's name. It sets `<org-slug>`: lowercase, with hyphens.
2. The Figma library link, if there is one, even half-built or unpublished.
3. Two to five product files that show the design system in use: real screens, not
   explorations. Not every file.
4. The code: a repository path on this machine, or a URL. If it's only a URL, ask them to
   clone it and give you the path, or treat it as no repository.
5. A Storybook URL, and any other documentation links (Zeroheight, Confluence, a docs site).
6. Who knows the stack (the architect or a lead engineer), and how to reach them.
7. What they want first: documentation, faithful builds in Figma, or both.

**Protect every Figma file as soon as you have its link.** The file key is the part after
`/design/` (or after `/branch/` for a branch). Run:

```bash
python3 "$LOCKSTEP/scripts/lockstep_config.py" protect <fileKey> "source: library (<file name>)"
```

Use `source: product file (<file name>)` for product files. Then run
`python3 "$LOCKSTEP/scripts/lockstep_config.py" list` and check that every key is there.

**Work out the tier.** Pick the highest row that applies:

| Tier | They have | learn can produce |
|---|---|---|
| 3 | A repository with components | Everything below, plus code components and props mapped to the design side |
| 2 | A Storybook or component docs, no repository | Component names and props from docs, mapped to the design side |
| 1b | A Figma library, even partial | The library's own components and tokens, a coverage matrix, and drift between library and product files |
| 1a | Product files only | Proposed tokens from clustered raw values; de facto components from repeated structures |
| 0 | A framework name, or nothing | A questionnaire and a skeleton STACK.md |

Tiers combine. Record the highest code tier and the highest design tier, for example
"design 1b, code 3".

Write `SOURCES.md` from [references/SOURCES.md](references/SOURCES.md) with the Write tool.

## 2. Stack discovery

**With a repository:**

```bash
python3 "$LOCKSTEP/scripts/scan_repo.py" <repo path> --out lockstep/<org-slug>
```

It reads the repository and writes `stack.json` and a draft `STACK.md` covering:

- frameworks, UI libraries, styling and build tools;
- token sources: CSS custom properties, Sass variables, Tailwind config or `@theme`, theme
  objects, DTCG or Style Dictionary JSON;
- components with their props and variant values: Vue `defineProps`, TypeScript props types,
  `propTypes`, `cva` variants;
- Storybook, docs and showcase pages;
- questions only a person can answer.

Then:

1. Read `STACK.md` yourself and spot-check two or three findings against the files. Correct
   anything wrong directly in `STACK.md`, and say what you changed.
2. If the repository has several apps or packages and the scan picked the wrong one, rerun it
   on the right sub-folder.
3. Give the user the summary (what the repository is, the framework and UI library, where the
   tokens live, and how many components) and the open questions from the end of `STACK.md`.
   Offer to forward the questions to whoever knows the stack.

**Without a repository:**

```bash
python3 "$LOCKSTEP/scripts/scan_repo.py" --no-repo --name "<org name>" --out lockstep/<org-slug> --hint "<what Figma suggests>"
```

Add one `--hint` for each thing the Figma side suggests about the code, phrased so a person
can confirm or correct it. If you've looked at the library, a hint might be "Component names
match Vuetify's (v-btn, v-text-field)". Only add hints you have evidence for; none is fine.
The command writes `ARCHITECT-QUESTIONS.md` for the user to forward, and a stub
`stack.json`. When the answers come back, write `STACK.md` from them in the same shape a scan
produces.

**Gate.** A person confirms `STACK.md` before any later step relies on it. When the user, or
the architect through them, says it's right, fill in the **Confirmed** line with their name
and the date, and set `"confirmed"` in `stack.json` to the same.

## 3. Design harvest and proposals

Load `/figma-use` (or `skill://figma/figma-use/SKILL.md`) and call `create_session` first.
Each `use_figma` call below gets the rendered script **unedited**, with the `fileKey` of the
file it reads. Save each result to its file with the Write tool. If a result was saved to a
file because it's large, copy that file instead.

**Each product file** from SOURCES.md. Audit whole pages, or the frames that show the system
in use (`get_metadata` on the page lists them):

```bash
python3 "$LOCKSTEP/scripts/render.py" audit --roots <page or frame IDs>
```

Save to `lockstep/<org-slug>/harvest/audit-<short file name>.json`. If the result has
`"next": <n>`, the file was too big for one call: render again with `--offset <n>` and save
each part (`audit-<name>-2.json`, …).

**The library file**, if there is one, and only if it's half-built or unpublished (a published
library goes through `lockstep:init`):

```bash
python3 "$LOCKSTEP/scripts/render.py" inventory_local --part components
python3 "$LOCKSTEP/scripts/render.py" inventory_local --part variables
```

Save to `harvest/inventory-components.json` and `harvest/inventory-variables.json`. A product
file can hold local components and variables too; run these on it when the audit shows local
variables (`local:` labels) or the user mentions a library page.

**Then propose:**

```bash
python3 "$LOCKSTEP/scripts/propose.py" --audit lockstep/<org-slug>/harvest/audit-a.json --audit lockstep/<org-slug>/harvest/audit-b.json --components lockstep/<org-slug>/harvest/inventory-components.json --variables lockstep/<org-slug>/harvest/inventory-variables.json --out lockstep/<org-slug>
```

Leave out flags for files you don't have. Read `PROPOSALS.md` before showing it, and check
two or three proposals against screenshots (`get_screenshot` on an example node). Then tell
the user, in plain words:

- how many tokens were found, how many already have a library name, and which drift values
  were found (a hair off a token, probably by accident);
- the de facto components: patterns people rebuild or detach, with no live component behind
  them. These are the strongest candidates for the library;
- what the WIP variables map to, and which ones nothing uses;
- local components nobody uses, and what they duplicate.

Everything here is a proposal. Say so: nothing is generated until a person has reviewed it.

## 4. Code harvest

Only with a repository (tier 3), after STACK.md is confirmed:

```bash
python3 "$LOCKSTEP/scripts/harvest_code.py" <repo path> --stack lockstep/<org-slug>/stack.json --out lockstep/<org-slug>/code.json
```

It resolves every token in the sources STACK.md lists to a value per theme (`var()` and `$`
references followed, rgba turned into hex with alpha), groups type variables into styles, counts
where each token is used, and notes each component's casing, fonts and hard-coded colours. Read
its one-line summary: if a token source you expected is missing, check STACK.md's token list.

## 5. Reconcile

**The design side** is one of:
- a **published library**: run `lockstep:init`'s inventory (components and variables) in a draft.
  The variables part only sees variables and styles that the inventoried components use, so:
  - for each code component with no Figma match, search the library for it
    (`search_design_system`, one query per name) and add the sets you find to `keys.json`
    before inventorying components;
  - for code type styles and shadows with no Figma match, search for the style names and read
    them with `render.py inventory --style-keys <file> --part styles`, then add the result to
    the variables file's `styles`.
  Otherwise "code-only" means "not inventoried", which is wrong.
- **proposals** from step 3, when there's no finished library.

```bash
python3 "$LOCKSTEP/scripts/reconcile.py" --components <inventory.components.json> --variables <inventory.variables.json> --code lockstep/<org-slug>/code.json --title "<library> and <repo>" --out lockstep/<org-slug>
python3 "$LOCKSTEP/scripts/reconcile.py" --proposals lockstep/<org-slug>/proposals.json --code lockstep/<org-slug>/code.json --out lockstep/<org-slug>
```

Leave out `--code` with no repository. Then check before showing anything:
- open the code files behind three conflicts and confirm the values;
- look at two "complete" rows whose names don't match (`nameMatch: false` in coverage.json):
  same value, different meaning is possible;
- any "code-only" component: search the library once more under another name.

Tell the user, in plain words: how much of Figma is in code and the reverse, the conflicts
(each is a question for the team, not a bug report), and the near misses listed as "close code
value". Everything is still a proposal until a person rules on the conflicts.

## What comes next (not built yet)

6. **Review:** a person accepts, renames or rejects each proposal.
7. **Generate:** tokens, component docs, AI context, and a LIBRARY.md that `lockstep:build`
   can use.
8. **Gate:** build a page from the learned system and score it.

The design is in `LEARN-DESIGN.md` in the Lockstep repository.
