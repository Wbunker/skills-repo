# The Mini-Book on Use Cases — All You Need, but Short

Cockburn's *The Mini-Book on Use Cases: All You Need, but Short!* (The Simplifying Series, 2025) — an 82-page, example-first guide to writing and using use cases. Load this when the user is **writing, structuring, or teaching use cases specifically** (anatomy, goal levels, main scenario, extensions, writing quality). For use cases *in relation to* stories and story maps, see `requirements-techniques.md` / `requirements-foundation.md`; for slicing technique generally, see `slicing-techniques.md`.

> Two distinct numbered lists in this book (don't conflate them): the **7 key concepts** (the structure of a use case) and the **8 writing techniques** (for clarity and flow). The exact members of each list aren't published in the description — the items below are Cockburn's documented use-case method; verify the precise 7 and 8 against the user's copy.

## Contents
- What this book is and how it differs
- The four parts
- Anatomy of a use case (the 7 key concepts)
- Goal levels
- Writing the main success scenario
- Writing extensions (the notation)
- Slicing use cases for incremental delivery
- The eight writing techniques
- Common mistakes
- Relationship to the other books

## What This Book Is and How It Differs
A portable, example-driven introduction: get productive on use cases fast, skipping the jargon. It opens with examples, then minimal theory.
- **vs *Writing Effective Use Cases* (Cockburn, 2000):** that book is theory-rich; this one opens with a dozen examples and minimizes theory. For the full template, scope/goal-level theory, formats, and scaling, see `writing-effective-use-cases.md`.
- **vs *Unifying User Stories, Use Cases, Story Maps* (Book 2):** that book positions use cases among three techniques; this one focuses on *what you need to begin writing and using use cases* in modern agile settings.
- **New here:** **slicing use cases for incremental delivery** — a technique not in the earlier books. This is the bridge to Book 1 (*Slice the Problem, Grow the Solution*).

## The Four Parts
1. **Complete examples first** — a dozen annotated use cases, simple→complex, low-level→"kite"-level, before any theory.
2. **The theory / structure** — defines all terms and the use-case structure compactly (the core explanations are done by ~page 38). The **7 key concepts** live here.
3. **The incremental-development method** — how to **slice** use cases for agile, incremental delivery.
4. **The eight writing techniques** — phrasing, perspective, and completeness that "dramatically improve clarity and precision."

## Anatomy of a Use Case (the 7 key concepts)
The structural elements the book defines (Cockburn's canonical set; confirm the exact seven):
- **Actor** — the one with the goal (primary actor) plus supporting actors/systems.
- **Stakeholders & interests** — who cares about this goal and what each needs protected; the use case guarantees their interests.
- **Goal** — what the primary actor wants to accomplish (named as a verb phrase).
- **Design scope (SuD)** — the system under discussion; what's inside vs outside the boundary.
- **Goal level** — the altitude of the goal (see below).
- **Main success scenario** — the typical, everything-works sequence of steps.
- **Extensions** — the conditions that branch off the main scenario (failures/alternatives) and how each is handled.

(Often paired with preconditions and guarantees/postconditions — state before and after.)

## Goal Levels
The book uses Cockburn's altitude levels (also in Book 2):
- **Summary** level — **kite** (and higher): broad, multi-step, spanning context.
- **User-goal / primary-task** level — **sea level**: one actor accomplishing one goal in one sitting (~2–20 min). *This is the default, most important level to write at.*
- **Subfunction** level — **fish**: a sub-step that supports user goals.

Examples in the book deliberately range from low-level up to kite-level so you can feel the difference.

## Writing the Main Success Scenario
- The steps when the goal **succeeds in a fairly typical situation.**
- Each step: **who does what** — an actor (or the system) performs one action that moves the story forward.
- May be **numbered** (better traceability) or written as **flowing paragraphs** (easier reading) — your choice.
- Keep steps at a consistent level; keep the GUI/technology out (intent, not mechanism).

## Writing Extensions (the notation)
- Extensions capture the **"but what if…"** situations.
- Each entry = a **condition** that might be encountered + **how it's handled.**
- In the formal style, the **number** indicates *which step* of the main scenario the condition is discovered at; the **letter suffix** (`a`, `b`, `c`, …) distinguishes different conditions at the same step. (e.g., `5a`, `5b` = two conditions arising at step 5.)
- Extensions are where use cases earn their keep — a structure for systematically discovering oddball cases.

## Slicing Use Cases for Incremental Delivery
The book's signature addition: turn a complete use case into thin, shippable slices (feeding Book 1's fine-grained incremental development). The recipe matches Book 2's:
1. Take the **thinnest full transaction** as slice 1 (a complete path doing the least — a requirements-side walking skeleton).
2. Take any **action/extension that fits an iteration** as the next slice.
3. **Subset** any action/extension until it's small enough.
Also slice by **action variations** and by **data / UI / performance / security** (which usually aren't written into the use-case text). See `slicing-techniques.md`.

## The Eight Writing Techniques
Techniques for clarity, flow, perspective, and completeness (Cockburn's well-known use-case writing guidance; confirm the exact eight against the book). In spirit they include: write from the **actor's intent** (not the UI); use simple **subject-verb-object** sentences in the **active voice**; make every step **show forward progress** ("ever-unfolding story"); keep a **consistent goal level**; keep **technology/GUI out**; name goals and steps with **strong verbs**; write **just enough** (readable over exhaustive); and put each "what if" in an **extension** rather than tangling the main scenario.

## Common Mistakes
- Writing UI clicks/screens instead of actor **intent**.
- Skipping **extensions** (losing the main benefit — finding oddball cases).
- Mixing **goal levels** within one scenario (dipping into sub-steps mid-flow).
- Treating a use case as a big upfront document instead of **slicing** it for delivery.
- Confusing the **7 key concepts** (structure) with the **8 writing techniques** (style) — they're different lists.

## Relationship to the Other Books
- **Book 1 (Slice the Problem):** the mini-book's slicing recipe produces the thin vertical slices Book 1 delivers.
- **Book 2 (Unifying):** the mini-book is the deep dive on the *use case* leg of Book 2's three-technique unification; concepts (verbs, goal levels) are shared.
- **Book 3 (Software Design):** use cases describe externally-visible behavior; responsibility-driven design decides where the code implementing them lives.
