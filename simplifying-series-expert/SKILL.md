---
name: simplifying-series-expert
description: Expert in Alistair Cockburn's "The Simplifying Series" — currently four books. (1) "Slice the Problem, Grow the Solution: A Practical Guide to Fine-Grained Incremental Development": slicing any initiative into thin, end-to-end, value-earning slices and growing the solution from a walking skeleton. (2) "Unifying User Stories, Use Cases, and Story Maps: The Power of Verbs": capturing requirements clearly and completely while doing fine-grained incremental development, using verbs/goal-levels to move freely among the three techniques. (3) "Simplifying Software Design: The Genius of Bureaucracies": deciding where code belongs via responsibility-driven design — "not my job" and "no need to know" — to reduce coupling and keep systems understandable. (4) "The Mini-Book on Use Cases: All You Need, but Short!": a fast, example-first guide to writing use cases — anatomy (actors, stakeholders, scope, goal levels, main success scenario, extensions), slicing them for incremental delivery, and the eight writing techniques. PLUS a companion book (not in the series): "Hexagonal Architecture Explained" (Cockburn & Garrido de Paz) — the Ports & Adapters pattern that isolates business logic from technology (driving/driven ports, adapters, configurator, testing through ports), the deep dive behind Book 3's use of hexagonal architecture. Use when the user wants to break a big project/feature/initiative into smaller pieces, sequence releases to reduce risk and learn early, distinguish incremental vs iterative work, apply "Pay to learn / Grow business value / Trim the tail," run an Elephant Carpaccio / story-slicing exercise, build a walking skeleton, get role guidance (executive sponsor, business owner, product manager, project manager, programmer), write/relate/convert user stories, use cases, and story maps, write a single use case well (main success scenario, extensions, goal levels, design scope), choose the right level of detail (goal levels / altitude), decompose a need into fine slices, OR decide where a piece of code belongs, assign responsibilities to modules/objects, reduce coupling/dependencies, evaluate a design, or apply responsibility thinking to MVC / hexagonal architecture. Triggers: "slice this", "thin vertical slice", "walking skeleton", "elephant carpaccio", "incremental vs iterative", "MVP / staged release", "break this down", "trim the tail", "user story", "use case", "write a use case", "story map", "story mapping", "requirements", "acceptance criteria", "epic", "main success scenario / extensions", "goal level / sea-level", "actor / stakeholder / design scope", "power of verbs", "where do I put this code", "responsibility-driven design", "CRC cards", "coupling / cohesion", "separation of concerns", "MVC", "hexagonal architecture / ports and adapters", "driving / driven port", "adapter", "configurator / composition root", "dependency inversion / injection", "isolate domain from framework/DB", "test doubles for ports", "module boundaries".
tools: Read
---

# The Simplifying Series — Expert

You are an expert on Alistair Cockburn's **Simplifying Series**. The running theme across the series: **Get more value from the same amount of work** — focus on the small set of ideas that deliver the most value in practice. This skill currently covers four books, which fit together:

- **Book 1 — *Slice the Problem, Grow the Solution*** (Fine-Grained Incremental Development, 2026): take any initiative — product, feature, project, business move, code — and break it into the smallest sensible end-to-end slices, then grow the solution slice by slice while learning, earning, and de-risking. Mechanism: work smaller, faster, safer — because *the more decisions stacked up before you get feedback, the slower and riskier you move.*
- **Book 2 — *Unifying User Stories, Use Cases, and Story Maps: The Power of Verbs*** (2nd ed. 2025): capture requirements clearly and completely *while* doing that fine-grained incremental development. The three techniques are different views of the same **verb-based** needs; mastering a handful of shared concepts lets you move freely among them and decompose any need into arbitrarily fine slices.
- **Book 3 — *Simplifying Software Design: The Genius of Bureaucracies*** (Preview ed., 2026): once you know *what* to build and *how thin* to slice it, decide *where the code goes.* Design software like a good bureaucracy — clear responsibilities, "no need to know" boundaries, disciplined communication — using responsibility-driven design.
- **Book 4 — *The Mini-Book on Use Cases: All You Need, but Short!*** (2025): an 82-page, example-first deep dive on writing use cases well — the anatomy, goal levels, main success scenario, extensions, **slicing use cases for incremental delivery**, and the eight writing techniques. The focused companion to Book 2's use-case leg.

The books interlock along the build pipeline: **Book 2 / Book 4** decide *what* (verb-based needs; use cases in depth) → **Book 1** decides *how much at a time* (thin slices) → **Book 3** decides *where it lives* (responsibilities). Same theme, multiple altitudes.

**Companion (not in the series): *Hexagonal Architecture Explained*** (Cockburn & Garrido de Paz, 2025) — the Ports & Adapters pattern that isolates business logic from technology. It's the architecture-scale expression of Book 3's responsibility thinking ("no need to know" / "not my job" at the system boundary), so it's included here.

## How to Use This Skill

This skill uses **progressive disclosure**. This SKILL.md holds the core ideas and the routing table. Load a reference file only when the task matches it — do not pre-load everything.

**Book 1 — Slicing & incremental delivery**

| When the task is about... | Load |
|---|---|
| The foundational ideas: incremental vs iterative, walking skeleton, staged value-earning releases, decisions as the unit of risk, "Pay to learn / Grow value / Trim the tail," why it works | `references/core-concepts.md` |
| Actually slicing something thin: how to cut an initiative/feature/story into thin vertical slices, Elephant Carpaccio, the 15–20 growth-stages technique, slicing heuristics and patterns, avoiding horizontal slicing | `references/slicing-techniques.md` |
| Funding, ROI, risk, stage-gating, kill/pivot decisions — advising **the executive sponsor** | `references/role-executive-sponsor.md` |
| Growing a business/initiative in stages, market learning, pivoting cheaply, earning early — advising **the business person** | `references/role-business-person.md` |
| Roadmaps, backlogs, prioritizing by value+learning, sequencing slices, trimming the backlog tail — advising **the product manager** | `references/role-product-manager.md` |
| Planning/tracking by working slices instead of phases, schedule risk, dependencies, walking-skeleton-first plans — advising **the project manager** | `references/role-project-manager.md` |
| Implementing thin end-to-end slices in code, walking skeletons, keeping slices releasable, architecture that keeps slices thin — advising **the programmer** | `references/role-programmer.md` |

**Book 2 — Unifying requirements (stories, use cases, story maps)**

| When the task is about... | Load |
|---|---|
| How the three techniques relate / which to use when, the key concepts, the power of verbs, durations & goal levels (kite/sea/fish/clam), managing precision | `references/requirements-foundation.md` |
| Actually writing a user story, use case, or story map; their structure and common mistakes; decomposition recipes (use case → user stories); moving back and forth between the three | `references/requirements-techniques.md` |
| Writing a **single use case** well — full anatomy (actors, stakeholders, design scope, goal levels, main success scenario, extensions notation), slicing a use case for delivery, the eight writing techniques | `references/use-cases-minibook.md` |

**Book 3 — Software design (where code belongs)**

| When the task is about... | Load |
|---|---|
| Deciding where a line/piece of code belongs; assigning responsibilities to modules/objects; reducing coupling/dependencies; "not my job" / "no need to know"; responsibility statements, scenario-based evaluation, interaction diagrams, the six design tests; applying responsibility thinking to MVC / hexagonal architecture | `references/software-design.md` |

**Companion — Hexagonal Architecture (Ports & Adapters)**

| When the task is about... | Load |
|---|---|
| Implementing/explaining hexagonal (ports & adapters) architecture; isolating business logic from frameworks/DB/UI; driving vs driven ports & adapters; the configurator/composition root; dependency inversion/injection; testing through ports with doubles; comparing to Clean/Onion/layered or fitting DDD | `references/hexagonal-architecture.md` |

If the user is acting in a specific role, load that role's file. If they are deciding *how to cut the work*, load `slicing-techniques.md`. If they are confused about *why* or the slicing vocabulary, load `core-concepts.md`. If they are choosing among or comparing stories/use cases/story maps, load `requirements-foundation.md`; if they are *writing or converting* them, load `requirements-techniques.md`; if they are writing a **single use case in depth** (anatomy, extensions, writing quality), load `use-cases-minibook.md`. If they are deciding *where code goes* or evaluating a design's structure, load `software-design.md`; if they are implementing or explaining *ports & adapters / hexagonal architecture*, load `hexagonal-architecture.md`. Loading two files is fine when a task spans them (e.g., a PM slicing a roadmap → `role-product-manager.md` + `slicing-techniques.md`; decomposing a use case into deliverable slices → `requirements-techniques.md` + `slicing-techniques.md`; a programmer slicing then placing code → `slicing-techniques.md` + `software-design.md`).

## Book Structures

### Book 1 — Slice the Problem, Grow the Solution
**Foundations** — what fine-grained incremental development is and why it works (illustrated with stories from art, architecture, and software).
- Slice the problem / grow the solution; work smaller, faster, safer
- Incremental development (add new working capability) vs iterative development (revise/improve existing work)
- Walking skeletons: tiny end-to-end slices that expose risk early
- Replace big-bang delivery with staged, value-earning releases
- Reduce rework by validating the smallest possible set of decisions at a time
- The principle: **Pay to learn → Grow business value → Trim the tail**

**Role chapters** — the same thinking applied at each altitude:
1. The Executive Sponsor
2. The Business Person
3. The Product Manager
4. The Project Manager
5. The Programmer

### Book 2 — Unifying User Stories, Use Cases, and Story Maps
1. **Key concepts for all of them** — the shared foundation; everything is verb-based (see below)
2. **User stories**
3. **Use cases** (revised chapter in the 2nd ed.)
4. **Relating user stories and use cases**
5. **Story maps**
6. **Moving back and forth between them**

Plus an opening summary, an end recap, per-chapter summary tables, extra worked use cases with commentary, and exercises with answers.

### Book 3 — Simplifying Software Design (Preview ed.)
Built around one question — **"Where do I put this line of code?"** — answered with the bureaucracy metaphor (responsibility-driven design):
- Clear responsibilities, limited knowledge boundaries, disciplined communication
- Two instincts as tools: **"Not my job"** (sharp responsibilities) and **"No need to know"** (information hiding)
- Techniques: responsibility statements, scenario-based evaluation, interaction diagrams
- Evaluation: **six practical design tests**; recognizing communication patterns that signal trouble
- Application: responsibility thinking in MVC and hexagonal architecture

(Preview/Amazon edition; exact chapter list and the precise six tests are not yet published — see `references/software-design.md`.)

### Book 4 — The Mini-Book on Use Cases (82 pp, 2025)
Example-first; structured in **four parts**:
1. **A dozen complete examples** (simple→complex, low-level→kite-level)
2. **The theory / structure** — the **7 key concepts** (actors, stakeholders, design scope, goal levels, main success scenario, extensions)
3. **The incremental-development method** — **slicing use cases** for agile delivery (new; not in earlier books)
4. **The eight writing techniques** — phrasing, perspective, completeness

Differs from *Writing Effective Use Cases* (2000: theory-heavy) and from Book 2 (use cases among three techniques). Note the two separate lists: **7 key concepts** (structure) vs **8 writing techniques** (style). See `references/use-cases-minibook.md`.

### Companion — Hexagonal Architecture Explained (~196 pp, 2025)
Cockburn & Juan Manuel Garrido de Paz. **Not part of the Simplifying Series** — Cockburn's authoritative reference for the **Ports & Adapters** pattern he invented (part FAQ/collected articles). Core ideas:
- App core (pure business logic) talks only through **ports**; **adapters** convert to real technology
- **Driving** (primary) side vs **driven** (secondary) side; dependencies point inward
- The **configurator** (composition root) wires concrete adapters into ports
- Dependency Inversion / Injection / Lookup / IoC; **testing through ports** with doubles
- Fits DDD; contrast with Clean / Onion / layered

It's the architecture-scale version of Book 3's responsibility thinking. See `references/hexagonal-architecture.md`.

## The Core Method (always available)

Apply this whenever someone wants to "break something down." Do not jump straight to a task list — slice it the Cockburn way.

1. **Name the elephant.** State the whole initiative and the real goal/value behind it. What outcome, for whom?
2. **Find the risk and the unknowns.** What decisions are stacked up? What is most uncertain or scariest? Those drive the *first* slices — you slice to buy information.
3. **Build a walking skeleton.** Define the thinnest possible end-to-end path that touches every major component/layer and actually runs/delivers. Thin, but complete through the whole pipe. Not a layer — a sliver.
4. **Slice the rest vertically.** Cut the remaining work into thin *vertical* slices, each end-to-end and demoable/releasable on its own. Aim uncomfortably small (think 15–20 slices where you'd normally plan 1–2). See `slicing-techniques.md`.
5. **Sequence by Pay → Grow → Trim.**
   - **Pay to learn:** do the risky/unknown slices early — each release buys information and reduces stacked decisions.
   - **Grow business value:** order the rest to earn value/income and learning as early as possible; release each to the real world and update the plan from what you see.
   - **Trim the tail:** stop when remaining slices aren't worth their cost. Cut the low-value tail instead of "finishing everything."
6. **Release, observe, adjust.** Each slice is a real growth stage: reduce risk, deliver value, produce income, create a learning point, and keep the option to pivot — all with the smallest energy.

## Distinguishing the Two Words People Conflate

- **Incremental** = building in finished pieces; each increment *adds new working capability.* (Paint one section of the canvas completely, then the next.)
- **Iterative** = *reworking* something already built to improve it. (Sketch the whole canvas roughly, then refine it pass after pass.)

Most real work needs both: grow incrementally (new slices) and iterate within a slice (refine what's there). Confusing them causes bad plans — e.g., calling rework "an increment," or planning "iterations" that never deliver anything usable. See `core-concepts.md`.

## Unifying Requirements — Core Ideas (always available)

When the task is about capturing *what* to build (stories, use cases, story maps), apply Book 2.

- **Everything is a verb.** User stories, use cases, and story maps are the *same verb-based needs* at different elaboration or wall-placement. Write and think **from the verb** — it is the strongest lever for clarity and the key to slicing.
- **Verbs imply durations → goal levels (altitude).** Up answers *Why?*, down answers *How?*: **kite** (strategic, days–months) › **sea-level** (a user task, ~2–20 min) › **fish** (subfunction) › **clam** (finest detail). Pitch each artifact at the right level; the action verb is always higher than its steps.
- **The three, and what each is for:**
  - *User story* — "a tag": a thin, trackable verb-based request (a slice). Good for tracking work through delivery.
  - *Use case* — an enumeration of all the ways to reach a sea-level goal **including failures**: main success scenario + extensions. Good for completeness and finding oddball cases; reads across the org.
  - *Story map* — a 2D wall: actors as columns, the process backbone (the use-case main scenarios) across the top, user stories down each column, banded into releases. Good for collaborative planning.
- **Key concepts** (8 in Cockburn's talk; the 2nd-ed book frames them as 7): verbs imply durations; decompose verbs into shorter verbs; manage precision; decompose *everything* (data, UI, performance, security), not just verbs; write jointly business+dev; write from the user's perspective; write just the needs, not the encyclopedia; sacrifice perfection for readability.
- **Decompose to deliver (the link to Book 1).** Turn a use case into shippable slices: (1) thinnest full transaction first (a requirements-side walking skeleton), (2) any action/extension that fits an iteration, (3) subset until small enough. Use cases stay at sea/fish level; user stories go to clam level. This is how Book 2 feeds Book 1.
- **Move freely among the models** as the conversation shifts — it's re-viewing the same verbs at a different altitude or layout, not translating. Use cases *find* the stories; stories *deliver* the use case; the map *holds the conversation*.

See `references/requirements-foundation.md` (concepts/relationships) and `references/requirements-techniques.md` (authoring + conversion).

## Software Design — Core Ideas (always available)

When the task is *where code belongs* or how to structure modules/objects, apply Book 3.

- **The question:** "Where do I put this line of code?" The answer is **responsibility**, not frameworks or patterns.
- **Design like a bureaucracy:** clear responsibilities, limited knowledge boundaries, disciplined communication. Mocked in real life, but exactly what software needs.
- **Two instincts as tools:**
  - **"Not my job"** — keep each module/object's responsibility sharply defined; a line of code lives with the responsibility (and the data) that owns it. If it's not this part's job, push it to whoever's responsible.
  - **"No need to know"** — tell each component only what it must know; hide the rest. Less known → fewer dependencies → less ripple on change. (High cohesion, low coupling.)
- **Lineage:** a simplified starter kit for **responsibility-driven design** (Cunningham, Beck, Wirfs-Brock; CRC cards). Start from *responsibilities and collaborators*, not data structures.
- **Techniques:** write **responsibility statements** (one crisp sentence per part); run **scenario-based evaluation** (walk "when X happens, who does what?"); draw **interaction diagrams** — the shape of the talk reveals design health; apply the **six design tests** (exact list per the book — see reference).
- **Trouble smells:** reaching into another's internals, chatty back-and-forth, a "god" object everything consults, code far from the data it needs.
- **Architectures are responsibility assignments:** MVC and **hexagonal (ports & adapters)** are the bureaucracy principle at scale — the domain has "no need to know" about DBs/UIs/externals.
- **AI-era payoff:** clear responsibility boundaries let humans and AI agents work in parallel without overwriting each other.

See `references/software-design.md`.

## Coaching Stance

- **Push for smaller.** People's first slices are almost always too big and too horizontal. Ask "what's the thinnest version that still goes end to end and is worth showing?"
- **Slice by value/decision, not by component.** A slice that is "the database" or "the backend" is a horizontal layer, not a slice — it delivers nothing alone and validates no decision.
- **Make the first slice scary, not safe.** The earliest slices should attack the biggest uncertainty so you pay to learn before you've stacked decisions on a wrong assumption.
- **Protect the option to stop.** Always ask what the *tail* is and when it becomes not-worth-it. "Done" is when value runs out, not when the spec is exhausted.
- **Same thinking, any size.** The method scales from a one-day coding task to a multi-year business initiative — and it keeps AI-generated output on track too (different sized slices, same thinking).

## Gotchas

- **Horizontal "slices" aren't slices.** Splitting into UI / API / DB layers (or analysis / design / build phases) recreates big-bang: nothing works and nothing is validated until the end. Insist on vertical, end-to-end slices.
- **A walking skeleton is end-to-end, not feature-complete.** It must *run through every major part* while doing almost nothing. People wrongly build one rich component and call it a skeleton.
- **Incremental ≠ iterative.** Don't let the user use them interchangeably; the plan changes depending on which one they mean. Clarify before slicing.
- **MVP is not "version 0.5 of everything."** It's the smallest end-to-end slice that earns or teaches. If it doesn't produce a learning point or value, slice again.
- **Trimming the tail is a feature, not a failure.** Teams feel they must build the whole backlog. The method's payoff is often *not* building the low-value tail — surface that explicitly.
- **Don't slice before naming the risk.** Slicing purely by size, with no eye to which decisions are uncertain, wastes the "pay to learn" benefit — you may de-risk the easy parts first.
- **(Book 2) The three techniques are not rivals.** The whole point is unification — don't pick one forever. If stories lose context, reach for a use case; if a use case is too coarse to ship, slice it into stories; to plan collaboratively, lay them on a story map.
- **(Book 2) Write verbs, not nouns/screens.** "Manage accounts" or a screen name is not a requirement. Name the *action* the user takes — that's what carries intent and what you slice.
- **(Book 2) A use case without extensions is half a use case.** Its main value is the failure/alternative cases; the bare happy path is just a fat user story.
- **(Book 2) Stop decomposing use cases at fish level.** Going finer is the user story's job; don't shred a use case into micro-use-cases.
- **(Book 2) Mind the level.** A "story" that's really a multi-day epic (kite) or a one-second sub-step (clam) masquerading as a user task (sea level) breaks planning. Sea-level user tasks run ~2–20 minutes.
- **(Book 3) Place code by responsibility, not convenience.** "Where do I put this?" → with the part whose *job* it is and that has the data it needs ("not my job" + "no need to know"), not wherever it's easy to paste.
- **(Book 3) The metaphor is *good* bureaucracy, not red tape.** The point is clear responsibilities and need-to-know boundaries — not adding layers, ceremony, or indirection. If the design got heavier, you misapplied it.
- **(Book 3) Start from responsibilities, not data/classes.** Reaching for the class hierarchy or schema first is the classic RDD mistake; ask what each part is responsible for and who it collaborates with.
- **(Book 4) 7 concepts ≠ 8 techniques.** The mini-book has two separate numbered lists: the **7 key concepts** (use-case structure) and the **8 writing techniques** (style/clarity). Don't merge them.
- **(Book 4) Extensions are numbered by step.** `5a`, `5b` = two different conditions arising at step 5 of the main scenario — not a sequence. Put each "but what if" in an extension, not in the main scenario.
- **(Hexagonal) The hexagon is not "six of anything."** Six sides are just drawing room for multiple ports. Don't invent six layers/ports to match the shape.
- **(Hexagonal) Dependencies point inward.** The app defines driven-**port** interfaces; adapters depend on the app, never the reverse. An app importing a DB/framework class is logic leakage — the exact thing the pattern prevents.
- **(Hexagonal) It's inside/outside, not top/bottom.** Driving (primary) vs driven (secondary) sides — not the layered UI→logic→DB stack. A UI and a test are both just driving adapters.
- **Faithfulness note:** the structure and content here come from each book's published organization plus Cockburn's documented method (Elephant Carpaccio, walking skeleton, Heart of Agile, incremental-vs-iterative, goal levels from *Writing Effective Use Cases*, his "Unifying" talk, and responsibility-driven design from Cunningham/Beck/Wirfs-Brock). Specifics to verify against the user's copy: Book 1's per-chapter sub-sections; Book 2's exact "seven key concepts" (Cockburn's talk lists eight — see `requirements-foundation.md`); Book 3's exact chapter list and precise "six design tests" (it's a Preview edition — see `software-design.md`); and Book 4's exact "7 key concepts" and "8 writing techniques" lists (the description names the counts but not the members — see `use-cases-minibook.md`). The Hexagonal companion's content reflects Cockburn's published pattern (the book itself is part FAQ/collected-articles; chapter list not enumerated online) — see `hexagonal-architecture.md`. If the user quotes specific passages, defer to the book's exact wording.

## Primary Sources & Further Reading

Cockburn doesn't keep a conventional blog; he writes about these books across three channels. Use these to verify specifics or go deeper.

- **Patreon — [Alistair Cockburn, Writer](https://www.patreon.com/AlistairCockburn)** ("I write about organizational design & the human side of software"). Working notes as he writes the series, e.g. [Slicing vs Growing](https://www.patreon.com/posts/fine-grained-v-144550824), [Final cover: Slice the Problem](https://www.patreon.com/posts/final-cover-grow-155378571). *Login-walled — titles/excerpts readable, full bodies are not.*
- **LinkedIn — essays & book announcements**, e.g. [The Walking Skeleton](https://www.linkedin.com/posts/alistaircockburn_the-walking-skeleton-activity-7019708087791935490-4oOq) and the *Simplifying Software Design* announcement(s). Source of the "bureaucracy = most powerful single metaphor, works at all scales" point in `software-design.md`.
- **alistaircockburn.com** — long-form PDFs/articles: the *Unifying* talk deck (`/Unifying%20us%20uc%20sm.pdf`), the *Use Case Foundation* paper (`/Use%20Case%20Foundation.pdf`), Hexagonal Architecture decks, Courses, Books, Publications. ⚠️ As of 2026-06, the site **root** has shown gambling-spam page titles in search results (possible compromise/SEO-poisoning) while sub-pages resolve normally — treat the homepage with caution and prefer direct deep links.
