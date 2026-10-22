# What makes impeccable.style work (studied 2026-10-22)

Reference only. Lockstep's page takes the lessons, not the look: none of Impeccable's CSS, copy,
logo, fonts or colours.

## Structure
1. **Hero**: a one-line claim, one sentence of support, one primary CTA (Install) and one quiet
   secondary link. The before/after demo sits *in* the hero, not below the fold. You see the
   product's effect before you read about it.
2. **Social proof**: a scrolling strip of short quotes. It's cheap, and it sits right after the proof.
3. **"Detects slop"**: a gallery of specific failure patterns, each tagged with its name. This
   turns an abstract quality ("AI slop") into named, recognisable defects.
4. **Command explorer**: commands grouped by intent (create / evaluate / refine / simplify /
   harden / system). Pick one and the sample interface changes, with a copyable invocation and
   a short "what it does".
5. **In action**: an agent transcript beside the result, so you see the process, not just the
   output.
6. **Feature rows**: "respects your design system", "tell it about your users", "keep your
   decisions". Each claim comes with a concrete artifact: a scan log, a PRODUCT.md, a DESIGN.md.
7. **Install**: a stepped accordion (1 install, 2 initialise and hooks, 3 stay in the loop),
   with tabs per tool and one copyable command.
8. **Footer**: docs links (getting started, command reference, changelog, FAQ). The docs live
   on separate pages; the homepage only routes to them.

## Why it works
- **Show, then tell.** Every claim is paired with a real artifact: a before/after, a log, a
  file, a finding count. Nothing is asserted without something to look at.
- **Defects get names.** The annotated tells (side-tab border, italic serif, AI beige) give
  readers a vocabulary, and the product owns that vocabulary.
- **Commands as vocabulary.** Short verbs, grouped by intent, each with one example. It reads
  like a toolset you can hold in your head.
- **Rhythm.** Generous space *between* sections and dense detail *inside* the demos. Calm page,
  busy proof.
- **Type.** A condensed display face at very light weight for headlines, a light humanist sans
  for body (16/25.6), and mono only for commands and code. Three roles, clearly separated.
- **One accent.** A single bright annotation colour, used only for tags that point at things.
- **Install is one command.** Everything else is optional and comes later.

## What Lockstep should take
- Put the before/after in the hero, with real numbers (77 → 98) and real screenshots, not a mock.
- Name the defects the score catches: hand-drawn card, unbound spacing, sample text, clipped
  text.
- Four commands as a small vocabulary, each with a prompt and a real output.
- Pair every claim with an artifact: score JSON, a LIBRARY.md excerpt, a guard message.
- Make install two steps, and say so.
