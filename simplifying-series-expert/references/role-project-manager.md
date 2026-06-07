# Role: The Project Manager

Load when advising the person responsible for **planning, tracking, and delivering** an initiative on time with acceptable risk. Their lever is *the plan and the flow of work*. Pair with `slicing-techniques.md` for building the plan from slices; `core-concepts.md` for the reasoning.

## What the Project Manager Cares About
Predictability, schedule and integration risk, dependencies, and visible progress. Their classic big-bang trap is the **phase-gated plan** (analysis → design → build → integrate → test), where integration risk is deferred to the end and "90% done" hides the painful 90% still to come.

## The Reframe
Plan and track by **working, end-to-end slices**, not by phases or components. A plan is a sequence of growth stages, each one a runnable slice. Progress is measured in *slices released*, because a released slice is the only honest signal that risk has actually been retired.

## Core Moves
- **Walking skeleton first.** Make the very first deliverable a thin end-to-end path through every major component. This forces integration on day one and surfaces the seam risks that phase-gated plans hide until the end.
- **Plan in vertical slices.** Convert the work breakdown from layers/phases into a sequence of demoable slices. Each slice = a small set of decisions validated.
- **Sequence by Pay → Grow → Trim.** Front-load the slices that retire the biggest schedule/technical risks; order the rest for steady value; keep an eye on the trimmable tail so the deadline can be met by *scope shaping*, not heroics.
- **Manage decisions and dependencies, not just tasks.** Track which open decisions each slice closes; pull forward slices that unblock the most downstream work and dependencies.
- **Report progress as working slices.** Replace "design phase 80% complete" with "8 of ~20 growth stages released." Burn down *risk and slices*, not hours.
- **Re-plan after each release.** Treat the plan as living; update estimates and sequence from what each released slice taught you.

## Questions a PM Should Ask
- "What's our walking skeleton, and when does it walk?"
- "Is this plan item end-to-end, or is it a layer/phase?"
- "Which risk or dependency does the next slice retire?"
- "If we're squeezed on time, which tail slices do we cut — and is that decided in advance?"
- "What did the last release change about our plan?"

## Anti-Patterns
- **Phase/layer Gantt charts** that integrate only at the end (integration risk parked until it's most expensive).
- **Tracking % complete of unfinished work** instead of released slices ("the last 10% takes 90% of the time").
- **Scope as fixed, schedule as the casualty** — instead of shaping scope by trimming the tail.
- **Big-bang integration:** building components in parallel and hoping they fit at the end.
- **Plan-as-contract:** refusing to re-sequence as learning arrives.

## What Good Looks Like
A plan whose first deliverable is a walking skeleton; work tracked as a burn-down of end-to-end slices and retired risks; the riskiest integration done first; dependencies cleared by sequencing; a pre-agreed trimmable tail that absorbs schedule pressure; and a plan that is updated after every release rather than defended.
