# Unifying Requirements — Foundation (Concepts, Verbs, Levels)

The shared foundation under user stories, use cases, and story maps, from Cockburn's *Unifying User Stories, Use Cases, and Story Maps: The Power of Verbs* (The Simplifying Series, 2nd ed. 2025). Load this when the user asks how the three techniques relate, which to use when, or about verbs/levels/precision. For authoring each technique and converting between them, see `requirements-techniques.md`. For slicing/incremental delivery, see `slicing-techniques.md` and `core-concepts.md`.

## Contents
- The problem the book solves
- The power of verbs
- The key concepts (the foundation)
- Verbs imply durations → altitude / goal levels
- Managing precision
- How the three techniques relate
- What each is good for / which to use when
- Tie to fine-grained incremental development

## The Problem the Book Solves
User stories, use cases, and story maps "have been circling like comets, competing for the same energy of the same people at the same time." Each is incomplete alone:
- **User stories** — quick and convenient, but *not complete* (a placeholder, easy to lose context).
- **Use cases** — *complete*, but awkward in fine-grained incremental environments (a whole goal at once).
- **Story maps** — great for *collaborative discussion*, but hard to send around the company.

The result is confusion, rework, and expensive missed requirements. The book shows they **complete and complement each other** — they are different views of the same verb-based needs — so you can move freely among them. This resolves the persistent agile tension: *how to capture requirements clearly and completely while doing fine-grained incremental development.*

## The Power of Verbs
The unifying insight: **all three techniques are verb-based.** A requirement is fundamentally an *action a user wants to take* — a verb. User stories, use cases, and story maps are just the same verbs "with varying degrees of elaboration, or placed on the wall differently."

The most powerful lever for clarity in all three is to **think and write from the verb.** Master the skill of phrasing any user need as a verb-based request and decomposing it into arbitrarily fine slices, and you can fit requirements into any cadence and switch models at will.

## The Key Concepts (the foundation)
The book opens with the key concepts "without which none of them can be written well, and with mastery of which you can move freely between them." Cockburn's own talk enumerates **eight** (the 2nd-edition book frames them as **seven** — likely merging or dropping one; defer to the user's copy for the exact seven):

1. **Verbs imply durations.** Every verb consumes time; readers share rough expectations of how long. (See altitude, below.)
2. **Decompose verbs into 'smaller' (shorter-duration) verbs.** A high-level action breaks into shorter-duration steps, each itself a verb.
3. **Manage precision.** Choose how exact to be for the situation; don't over- or under-specify.
4. **Decompose everything, not just the verbs.** Data, UI, performance, and security all decompose too — and much of it lives *outside* the verb text.
5. **Write jointly, business & dev.** These artifacts are conversation tools written together, not handed over a wall.
6. **Write from the user's perspective.** Frame around what the user is trying to achieve, not the system internals.
7. **Write just the needs, not the encyclopedia.** Capture the requirement, not exhaustive documentation.
8. **Sacrifice perfection for readability.** A readable, slightly imperfect artifact beats a precise, unreadable one.

Concepts 5–8 are as much about **team morale and cooperation** as about correctness: used well, these techniques strengthen collaboration; used as hand-off documents, they damage it.

## Verbs Imply Durations → Altitude / Goal Levels
Because verbs have durations, they sit on a **gradient of altitude** (Cockburn's goal levels, from *Writing Effective Use Cases*). Going **up** answers *"Why?"*; going **down** answers *"How?"*

| Level | Icon | Duration / scope |
|---|---|---|
| Very high / summary / strategic | **kite** (and cloud/sky above) | days–months; business/strategic goals |
| **User goal / user task** | **sea-level** | **~2–20 minutes**; one sitting, one user achieving one goal |
| Subfunction | **fish** | seconds–minutes; a sub-step |
| Lowest detail | **clam** | the finest steps |

The **action verb is always 'higher' than its steps.** Sea level is the anchor: a *user task* is the thing a user sits down to accomplish in one go (2–20 min). Strategic goals are kite-level; subfunctions are fish-level. Getting the level right is "choosing the right level of detail for your situation."

## Managing Precision
Precision is a dial, not a maximum. Decompose and elaborate *only as far as the situation needs* — enough to act and to slice for the next iteration, no more. Over-precision creates the "encyclopedia"; under-precision loses the requirement. This is how you decide how thin to slice and how much to write down.

## How the Three Techniques Relate
All three express verb-based needs; they differ in elaboration and placement:
- A **use case** gives a verb its *structure and context* — the main success scenario plus the failure/variation extensions for one sea-level goal.
- A **user story** is a *slice* of that — a thin, trackable verb-based request, decomposed as fine as needed.
- A **story map** is the *spatial layout* — a 2D arrangement (actors across the top as columns, the process backbone along the top row) that holds both the large-scale context and the fine-grained stories in one picture.

So: use case = the structured story; user story = a slice/tag of it; story map = the wall layout that shows many of them together. Mastering the key concepts lets you move among these views fluidly. (Details and conversion recipes: `requirements-techniques.md`.)

## What Each Is Good For / Which to Use When
- **User story** — *a tag.* Useful for tracking where a request is during development up to delivery. Reach for it when slicing work for an iteration.
- **Use case** — *tells a story easily read across the org;* gives context around specific requests and a structure for discovering oddball cases (the extensions). Reach for it when you need completeness and to surface failure modes.
- **Story map** — *a conversation-holder* showing both large-scale context and fine-grained stories at once. Reach for it for collaborative planning and release shaping.

The techniques work for **any kind of project, not only agile ones** (including business-process improvement). Choose the best tool for the moment rather than being locked into one.

## Tie to Fine-Grained Incremental Development
This book is the *requirements engine* for the slicing method in `core-concepts.md` / `slicing-techniques.md`. The core skill — "phrase any user need as a verb-based request and decompose it into arbitrarily fine slices" — is exactly what lets you produce the thin vertical slices and walking skeletons the *Slice the Problem, Grow the Solution* book asks for. Verbs decompose; slices come from decomposed verbs.
