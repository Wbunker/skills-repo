# Role: The Programmer

Load when advising the person **writing the code** — turning a slice into a thin, end-to-end, releasable implementation. Their lever is *how the code is grown*. Pair with `slicing-techniques.md` for cutting a story into code-sized slices; `core-concepts.md` for incremental-vs-iterative discipline.

## What the Programmer Cares About
Shipping working code, keeping integration honest, avoiding rework, and not building infrastructure for needs that never arrive. Their big-bang trap is **build-it-all-then-wire-it-up**: writing the data layer, then the logic, then the UI, integrating last, and discovering at the end that the pieces don't fit or the design was wrong.

## The Reframe
Grow software as a **walking skeleton thickened by thin vertical slices.** Get one trivial path running end-to-end through every layer first, then make each commit/PR a small slice that goes all the way through and could be released. Code grows by **adding capability (incremental)** and is **refined in place (iterative)** — do both deliberately.

## Core Moves
- **Build the walking skeleton first.** A minimal end-to-end path: real entry point → through each major component → real output, even if it returns a hard-coded value. Wire the seams before fleshing out any one part. This makes integration a day-one fact, not an end-of-project gamble.
- **Slice vertically in code.** Implement one rule, one input, one path at a time, each end-to-end. Start with a hard-coded result, then make it computed (a literal "pay to learn" step proving the path before investing in the logic). Use the SPIDR-style patterns in `slicing-techniques.md`.
- **Keep every slice releasable.** Each slice should leave the system runnable and shippable — hide unfinished work behind a flag or a trivial default rather than breaking the path. Small, integrated, green.
- **Defer infrastructure to need.** Don't build frameworks, abstractions, or scale for demand you haven't hit. Let the slices pull abstractions into existence; refactor *iteratively* when a second/third case justifies it.
- **Architect to keep slices thin.** A clean boundary between domain logic and the outside world (Cockburn's Hexagonal Architecture / Ports & Adapters) lets you slice through the core with stub adapters and test each slice end-to-end without the full stack. Thin slices are easiest when the architecture isn't layer-locked.
- **Iterate within a slice; increment across slices.** Refine/refactor the slice you just built (iterative), then add the next capability (incremental). Name which you're doing — endless refactoring with no new capability, or new features with no refactoring, are both failure modes.
- **Test end-to-end per slice.** Each slice gets a test that exercises its whole path, so the skeleton stays walking as it thickens.

## Questions a Programmer Should Ask
- "What's the thinnest path I can make run end-to-end right now?"
- "Can I ship this slice with a hard-coded value first, then compute it next slice?"
- "Does this commit keep the system releasable?"
- "Am I building this abstraction for a need that exists yet, or speculatively?"
- "Is this work new capability (increment) or improving existing code (iterate)? Both planned?"

## Anti-Patterns
- **Horizontal build order:** finish the DB, then the API, then the UI; integrate last.
- **Speculative generality:** frameworks and abstractions for cases that never come.
- **Broken-trunk slices:** changes that leave the system unrunnable until "it's all done."
- **Skeleton-as-limb:** building one rich component and calling it a walking skeleton.
- **Refactor-forever or never-refactor:** confusing iterative polish with incremental delivery (or skipping one entirely).

## What Good Looks Like
A walking skeleton running on day one; each PR a thin vertical slice that goes end-to-end, keeps the build green and releasable, and validates a small set of decisions; abstractions introduced only when a real second case demands them; a hexagonal boundary that makes slicing and end-to-end testing cheap; and deliberate alternation between incrementing (new slices) and iterating (refining) — delivering more working value from the same coding effort.
