# Lockstep plugin for Claude Code

Ask Claude to build a page in Figma "with our design system", and Lockstep makes it do that
faithfully. The page is built from your library's real component instances, with every colour,
spacing and radius bound to your library's variables and auto layout throughout. Then Claude
scores the result, fixes what fails, and shows you before and after.

It works with any organization's published Figma library. It has been tested on Business@Slalom
and on Figma's Simple Design System.

## Start here

Three steps, about five minutes. You need a Figma seat that can edit files (a **Full** seat).

**1. Connect Figma to Claude Code (once).** In a terminal:

```bash
claude plugin install figma@claude-plugins-official
```

Restart Claude Code, type `/plugin`, open the **Installed** tab, select **figma** and sign in.
Figma's guide: https://developers.figma.com/docs/figma-mcp-server/remote-server-installation/

**2. Install Lockstep (once).** In a terminal:

```bash
claude plugin marketplace add cj-ax/lockstep
```

```bash
claude plugin install lockstep@lockstep
```

The repository is private for now: ask Chris to add you to it, and make sure your Git sign-in
for GitHub works (for example, run `gh auth login` once).

Or, inside Claude Code: `/plugin install lockstep --marketplace cj-ax/lockstep`. In the Claude
desktop app, once the marketplace is added, Lockstep also appears under **+**, then **Add
plugins**, in the Code tab.

**3. Point it at your library.** In Claude Code, paste a link to your design library's Figma
file:

> Set up Lockstep for our design library: https://www.figma.com/design/…

Lockstep checks that everything is connected and explains any fix in plain words. It then
protects the library file, so nothing writes to it, and reads its components and tokens. After
that, just ask:

> Build our team members page in Figma with our design system.

## Updating

```bash
claude plugin marketplace update lockstep
```

```bash
claude plugin update lockstep@lockstep
```

## For a whole team

To have Lockstep switch on for everyone working in a repository, commit this to that
repository's `.claude/settings.json`. Each person is asked to trust the folder once.

```json
{
  "extraKnownMarketplaces": {
    "lockstep": { "source": { "source": "github", "repo": "cj-ax/lockstep" } }
  },
  "enabledPlugins": { "lockstep@lockstep": true }
}
```

## Working on Lockstep itself

From a clone of this repository, `claude --plugin-dir ./plugin` loads your local copy instead
of the installed one.

## How the library is protected

Step 3 does this for you. Lockstep only writes to draft files, and keeps a list of files it
must never write to (usually your published library) in `.claude/lockstep.json` in your
project, or in `~/.claude/lockstep.json` to cover every project.

```json
{ "protectedFileKeys": { "LMgKpbsEmxRpiHBKd9YGlw": "Official [Business@Slalom] Design System" } }
```

You can also set `LOCKSTEP_PROTECTED_FILE_KEYS=key1,key2` in the environment. Keys from all
three places are combined.

Three layers enforce it:
1. A **PreToolUse hook** blocks any Figma write tool whose target names a protected file.
2. Every **write script** checks `figma.fileKey` inside Figma and refuses to run in a protected
   file.
3. Every **skill that writes** tells Claude to check the key before each write.

Reading is allowed: `lockstep:score` and `lockstep:learn` read protected files with read-only
scripts. The hook lets one through only when its code is exactly what `render.py` printed, so
edited or hand-written code is still blocked.

If a settings file exists but can't be read, every Figma write is blocked until you fix it, so a
typo can't quietly turn the protection off. The hook can't see which file Figma desktop has open,
so it doesn't cover the third-party figma-console MCP; don't run that against your library.

## Commands

Five skills. Claude picks the right one from what you ask, or you can name it.

| Command | What it does | Ask it like |
|---|---|---|
| `lockstep:init` | One-time setup per library. Protects the library file, finds its components and tokens, reads their variants, slots and values from Figma, and saves a summary to `lockstep/<library>/` in your project. | "Set up Lockstep for our design library: <figma link>" |
| `lockstep:build` | Builds a page in a draft from library instances and tokens, then scores, looks at screenshots and fixes until it passes. Runs `init` first if needed. | "Build our team members page in Figma with our design system" |
| `lockstep:score` | Read-only. Measures how faithfully any frame uses its library and lists the offending layers. | "How faithfully does this frame use our library? <link>" |
| `lockstep:fix` | Clones frames and binds raw values to exact-match library tokens, so nothing looks different. Then rescores and lists the values that have no token. | "Bind this design's spacing and colours to our tokens" |
| `lockstep:learn` (early) | For a design system that isn't finished. Protects every source file, works out the front-end stack from a repository (or writes questions for whoever knows it), audits how your Figma files use colours, spacing, type and components, and drafts token and component proposals for review. Generating the system comes next. | "Learn our design system: here's the Figma library, two product files and the repo" |

## What "faithful" means here

| Measure | Pass |
|---|---|
| Library instances (share of content) | at your library's ceiling: 100% if it has text components |
| Properties bound to variables | 100% |
| Detached instances | 0% |
| Hard-coded colours | 0% |
| Auto layout | 100% |
| Integrity issues: clipped content or text, sample text left in | 0 |

Claude also looks at a screenshot of every frame, because the score can't judge everything.

## Contents

- `skills/init`, `skills/build`, `skills/score`, `skills/fix`, `skills/learn`: the five commands.
  `build` also holds the build-patterns reference and two worked example builds.
- `scripts/`: shared by all of them.
  - `inventory.js` reads a library.
  - `score.js` scores frames.
  - `fix.js` binds raw values to exact-match tokens.
  - `settle.js` makes Figma re-lay-out library instances a script resized, so they render at
    their real size.
  - `render.py` fills a script's placeholders.
  - `lockstep_config.py` loads the protected keys, and adds one with `protect`.
  - `scan_repo.py` reads a front-end repository (without running it) and drafts STACK.md, or
    writes questions for an architect when there's no repository.
  - `audit.js` records what a product file uses; `inventory_local.js` reads an unpublished
    library in place. Both are read-only.
  - `propose.py` turns those into draft tokens and components.
- `hooks/`: the write guard.

## Known limits

- Finding components depends on `search_design_system`. Figma has no API to list every component
  in a library from another file.
- The build script is written fresh for each page and library; only scoring and fixing are
  generic. Expect a few passes on a new library.
- Usage judgement (which variant means Cancel, which casing to use) comes from your library's
  component descriptions. If they're thin, Claude asks you.
