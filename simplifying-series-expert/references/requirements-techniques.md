# Unifying Requirements — The Three Techniques & Moving Between Them

How to write user stories, use cases, and story maps well, and how to convert among them — from Cockburn's *Unifying User Stories, Use Cases, and Story Maps: The Power of Verbs* (2nd ed.). Load this for authoring requirements or decomposing/converting. For the shared concepts (verbs, durations, altitude, precision, which to use when), see `requirements-foundation.md`.

## Contents
- User stories
- Use cases
- Story maps
- Relating user stories and use cases
- Decomposition recipes (the practical engine)
- Moving back and forth between the three
- Common mistakes

## User Stories
**Definition:** a short, verb-based request for a capability — in Cockburn's framing, *"a tag."* Its real job is to be a trackable unit: useful for tracking where a request is during development, up to delivery. It is a placeholder for a conversation, not a specification.
- Verb-first: name the action the user takes and the goal behind it ("As a … I want to *verb* … so that …" is one common shape, but the verb and goal are what matter).
- A story is typically a **slice** of a larger goal (a sliver of a use case), decomposable down to **clam** level and "almost indefinitely."
- Keep them small enough to fit an iteration; each should be demoable/releasable (ties to thin vertical slices — see `slicing-techniques.md`).

**Common mistakes:** stories with no verb (noun/CRUD-screen stories); stories that are really whole goals (too big); stories detached from any context so the "so that" / failure cases are lost.

## Use Cases
**Definition (Jacobson, via Cockburn):** *an enumeration of all the ways for a user to achieve a goal — including the ways they fail.* It supplies the **context and structure** a bare user story lacks.

**Structure:**
- **Goal** at **sea level** (a user task, ~2–20 min), with the **actor** who wants it.
- **Main success scenario** — the numbered steps of the normal, everything-works path.
- **Extensions** — the conditions that branch off each step (failures, alternatives, oddball cases), each handled. This is where use cases earn their keep: they are *a structure for discovering oddball cases.*
- References back-end and external systems as needed.

**Levels rule when writing use cases:** keep the use case at sea level; **don't decompose below fish level**, and **keep the use case shape** (main success scenario + extensions). Going finer is the job of user stories, not the use case.

**Example shape** (sea-level goal "Register for Courses"): main scenario = student requests schedule → system prepares form → gets courses → student selects → system verifies prerequisites & enrolls → student confirms, system saves. Extensions = "already has a schedule," "semester closed," "catalog system doesn't respond," "course full / prerequisites unmet."

**Common mistakes:** writing UI/clicks instead of intent; decomposing into tiny sub-use-cases (drop to user stories instead); skipping the extensions (losing the main value); pitching above or below sea level.

> For the full use-case deep dive — anatomy (actors, stakeholders, design scope), the extensions notation (`5a`/`5b`), goal levels, slicing a use case, and the eight writing techniques — see `use-cases-minibook.md` (Book 4).

## Story Maps
**Definition (Jeff Patton, via Cockburn):** *a 2D card layout showing processes left-to-right* — a mix of use case and user stories on a wall.
- **Columns = actors / user types** — each type of user gets their own column.
- **Top row(s) = the backbone:** the overall business process, left to right — essentially the **use case main success scenario(s)** as big cards (epics/user tasks). E.g., *Capture inventory → Handle sale → … → Run daily rollup → Reorder stock.*
- **Down each column:** all the **user stories** needed to deliver the cards above (the slices — epics broken into use cases, failures, data, and individual user stories).
- **Horizontal bands = release slices:** group cards into the thin end-to-end releases you'll ship (ties to staged value-earning releases in `core-concepts.md`).

**Strength:** holds large-scale context *and* fine-grained stories in one picture — a conversation-holder for collaborative planning. **Weakness:** lives on a wall, so it's hard to send around the company (pair with use cases for that).

## Relating User Stories and Use Cases
- A **use case** = the structured, complete account of one sea-level goal (main + extensions).
- A **user story** = a **slice** of that account, sized to flow through development.
- So a use case is, roughly, *a coherent set of related user stories with the connective structure made explicit* — the main path, the failure branches, and the goal context that loose stories drop.
- Use the use case to **find** the stories (every step and every extension is a candidate story), and use the stories to **deliver** the use case incrementally.

## Decomposition Recipes (the practical engine)
This is the "how" that powers fine-grained incremental development.

**Decompose verbs (how far?):**
- *For use cases:* don't go below **fish** level; preserve the main-scenario + extensions shape.
- *For user stories:* decompose down to **clam** level as needed — almost indefinitely.

**Decompose a use case into user stories:**
1. **Choose the thinnest full transaction as slice 1.** (A complete end-to-end path doing the least possible — the requirements-side of a *walking skeleton*.)
2. **Choose any action/extension that fits an iteration** as the next slice.
3. **Subset any action/extension until it's small enough** to fit.

**Decompose also by action variations** — each alternative way of doing a step (e.g., "cash sale" vs "credit-card sale") is its own slice.

**Decompose the non-verb parts too** (these usually are *not* written in the use case): **data** (Name → first/middle/last; Address → street/city/zip/state), **UI**, **performance**, **security**. Each refinement is a further slice. This is concept 4 — "decompose everything, not just the verbs."

## Moving Back and Forth Between the Three
The payoff of the shared concepts: shift models as the conversation or project needs change.
- **Use case → user stories:** apply the recipe above (thinnest transaction first, then actions/extensions, subset as needed).
- **User stories → use case:** when loose stories lose context or you're missing failure cases, gather related stories under one sea-level goal and lay out the main scenario + extensions to expose the gaps.
- **Use case / stories → story map:** put actors as columns, the main success scenario(s) as the top backbone, and the stories down the columns; band into releases.
- **Story map → stories/use cases:** read a column as the stories for an epic; read the backbone as the use case main scenarios.

Because all three are verb-based at different elaborations, none of this is translation between foreign languages — it's re-viewing the same verbs at a different altitude or layout.

## Common Mistakes (across all three)
- Treating the three as rivals and picking one forever, instead of moving among them.
- Writing nouns/screens instead of **verbs** (loses the action and the slicing lever).
- Use cases without extensions (throws away their main benefit — finding oddball cases).
- Stories with no goal context (can't tell why, can't find failures).
- Over-precision ("the encyclopedia") instead of *just the needs*, readable, written jointly.
- Decomposing use cases below fish level instead of switching to user stories.
