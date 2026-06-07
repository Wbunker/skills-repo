# Slicing Techniques — How to Cut Thin Vertical Slices

The practical "how." Load this whenever the user needs to actually break an initiative, feature, epic, or story into slices — including running an Elephant Carpaccio exercise. For the underlying *why* and vocabulary, see `core-concepts.md`.

## Contents
- Vertical vs horizontal (the cardinal rule)
- The Elephant Carpaccio exercise
- A repeatable slicing procedure
- Slicing heuristics / patterns (SPIDR + value angles)
- Sizing: how thin is thin enough
- Sequencing the slices
- Worked example
- Anti-patterns

## Vertical vs Horizontal — The Cardinal Rule

A real slice is **vertical**: a thin, complete path from one real end to the other (e.g., user action → through every layer → observable result/value). It can be demoed and ideally released on its own.

A **horizontal** "slice" is a layer or phase — "the database," "the API," "the design phase." It delivers nothing usable alone and validates no end-to-end decision. Horizontal decomposition is just big-bang in disguise: everything must finish before anything works.

> Test for a good slice: *Could you show it to a user and could it, in principle, be released?* If not, it's probably a layer, not a slice.

## The Elephant Carpaccio Exercise

The mental image behind the book's title. The **elephant** is the big feature/initiative; **carpaccio** is meat sliced paper-thin. The skill is cutting business requests into slices thin enough to fit in *any* iteration — and far thinner than feels natural.

How to run it (classic Cockburn/Kniberg facilitation):
1. Take a small-seeming feature (the classic kata: a checkout price calculator with quantity, price, state tax, and discount tiers).
2. Challenge the group to produce **15–20 vertical slices**, each a runnable, demoable increment, each adding one observable behavior.
3. Each slice must be **end-to-end** (input → calculation → output), shippable, and tiny — often a single rule or a single hard-coded value made real.
4. Demo after every slice. Feel how much earlier value and feedback arrive versus building it "properly" in one go.

The lesson transfers: if you can find 15–20 slices in a price calculator, you can find them in almost anything. Thinness is a skill that improves with practice.

## A Repeatable Slicing Procedure

1. **State the whole and its value.** One sentence: the outcome and who benefits. This is the elephant.
2. **List the open decisions and risks.** What's uncertain, scary, or unknown? Mark the riskiest — they get sliced out and done first (pay to learn).
3. **Define the walking skeleton.** The thinnest end-to-end path that touches every major component and actually runs. That's slice #1.
4. **Enumerate behaviors/variations.** Brainstorm every distinct behavior, rule, data variation, input type, user, step, or quality level. Each is a candidate slice.
5. **Make each candidate vertical and small.** For every candidate, force it end-to-end and strip it to one observable change. Split anything with "and" in it.
6. **Sequence** by Pay → Grow → Trim (see below).
7. **Mark the tail.** Identify which slices are low-value candidates to *not* build.

## Slicing Heuristics / Patterns

When a slice is still too big, split along one of these axes. (SPIDR is a handy mnemonic — Spike, Path, Interface, Data, Rules — extended here with value-oriented angles.)

- **Spike** — carve out a tiny research/learning slice to retire an unknown (a literal "pay to learn" slice). Time-box it.
- **Workflow steps / Path** — ship one step or one path through a multi-step flow; one happy path first, alternates/errors as later slices.
- **Interface / channel** — one input method, one device, one screen, or even CLI-before-UI first.
- **Data variations** — one data type, one format, one currency/locale, one record before many.
- **Business rules** — implement one rule now; each additional rule/edge case is its own slice. (Start with a hard-coded result, then make it computed.)
- **Operations (CRUD)** — Create first; Read/Update/Delete as separate slices.
- **Happy path vs handling** — correct-input path first; validation, errors, and recovery later.
- **Zero / one / many** — handle zero, then exactly one, then the general case.
- **Manual before automated** — do the step by hand (or hard-coded) to deliver value now; automate it in a later slice.
- **Quality / non-functional later** — make it *work* thin first; performance, scale, polish, and hardening are their own slices once the path is validated.
- **Defer the fancy** — strip every "nice to have" out of the first version of a behavior; each is a separate, optional, trimmable slice.

The split must always keep the slice **end-to-end**. Splitting by layer is not on this list for a reason.

## Sizing — How Thin Is Thin Enough?

- Aim for slices that are *uncomfortably* small — if a slice feels trivially tiny, it's probably right.
- Rule of thumb from the exercise: where you'd plan **1–2** pieces, look for **15–20**.
- A slice should change *one observable thing* and be completable well within a single iteration (often hours, not weeks).
- If you can't demo it, or it has an "and," split again.
- Different sized initiatives → different sized slices, **same thinking** (a day's coding task and a multi-year program both get sliced this way).

## Sequencing the Slices

Order with **Pay to learn → Grow business value → Trim the tail** (full treatment in `core-concepts.md`):
1. **First:** walking skeleton + the slices that retire the biggest risks/unknowns.
2. **Then:** slices ordered so value and income arrive as early as possible, each release producing a learning point that updates the plan.
3. **Watch the tail:** as marginal value drops, stop. Plan to *not* build the low-value tail.

Re-sequence after each release — what you learn changes what's most valuable or risky next.

## Worked Example (non-software, to show generality)

**Elephant:** "Launch a paid online course."
- **Skeleton (pay to learn):** sell *one* lesson to *one* real buyer via a hand-made payment link and an emailed PDF. End-to-end: money in, content out. Validates demand + the riskiest decision (will anyone pay?).
- **Grow value:** add a second lesson; add a simple landing page; add a second payment option; add an automated delivery email; add a cohort of 10.
- **Trim the tail:** the polished LMS, mobile app, and certification engine may never be worth building if the early stages show modest demand — that's the tail, deliberately left uncut.

Same pattern as the price-calculator kata — just bigger slices.

## Anti-Patterns

- **Layer cake:** "DB slice, then API slice, then UI slice." Nothing works until the end. Not slicing.
- **Phase gates:** analysis → design → build → test as "increments." Same big-bang, renamed.
- **Hidden bigness:** a "slice" containing the word *and* (it's two slices), or one that can't be demoed (it's a fragment).
- **De-risking the easy stuff first:** slicing by size only, ignoring which decisions are uncertain, so you happily validate the parts that were never in doubt.
- **Gold-plating slice one:** loading the first slice with nice-to-haves instead of stripping to the spine.
- **No tail discipline:** treating the entire backlog as mandatory, so the "more value from the same work" never materializes.
