# Foundations — Evolving Software Architecture (Ch 1)

The "what and why." Load when the user is new to evolutionary architecture, doubts the approach, or
needs the vocabulary (dimensions, guided/incremental change, evolvability). For the central technique
see `fitness-functions.md`.

## Contents
- The definition, unpacked
- Why evolutionary (the problem)
- Guided change
- Incremental change
- Multiple dimensions
- Bit rot & dynamic equilibrium
- Evolvable vs predictable

## The Definition, Unpacked
**An evolutionary architecture supports guided, incremental change across multiple dimensions.**
Each word is load-bearing — guided (fitness functions), incremental (deployment pipelines), multiple
dimensions (all the architectural characteristics, not just code). Evolutionary architecture isn't a
style you adopt; it's a *property* you build in so the architecture can change safely as the world does.

## Why Evolutionary (the Problem)
- **You can't predict the future.** Requirements, business priorities, and technology (and now AI
  tooling) change in ways no upfront design anticipates — the "unknown unknowns." Big-design-up-front
  bets on predictions that don't hold.
- **Architecture decays.** Software suffers entropy/"bit rot": every change risks eroding the
  characteristics the architecture was built to provide. Without protection, structure degrades.
- **The shift:** stop trying to *predict* change and build the perfect future-proof system; instead
  make the system **cheap and safe to change** and guard what matters with automated checks. Enable
  evolution rather than forecast it.

## Guided Change
Change is **steered**, not random. **Fitness functions** are the steering mechanism: objective tests
of architectural characteristics that tell you, continuously, whether a change has degraded the
qualities you care about. (Full treatment: `fitness-functions.md`.) "Evolutionary" without guidance is
just drift.

## Incremental Change
The architecture must support **small changes deployed easily**:
- In **development** — modular, testable, decoupled enough to change one part without a big-bang.
- In **operations** — a **deployment pipeline** that builds, runs fitness functions, and releases in
  small increments (CD, feature toggles, canary/blue-green). (See `incremental-change.md`.)
Small batches + automated guardrails = safe evolution.

## Multiple Dimensions
Architecture is more than code structure. The book's dimensions (architectural characteristics, the
`-ilities`) all evolve and all need protection, e.g.:
- **Technical** — frameworks, languages, libraries, code structure.
- **Data** — schemas, database design, data quality (a first-class dimension; see `structure-and-data.md`).
- **Security** — vulnerabilities, dependency CVEs, auth.
- **Operational / system** — scalability, performance, elasticity, availability.
- **Domain** — the business capabilities the system serves.
Evolving one dimension safely means having fitness functions across *all* the relevant ones — change
in one (e.g., a new library) must not silently break another (e.g., security or latency).

## Bit Rot & Dynamic Equilibrium
- **Bit rot / architectural decay** — unguarded characteristics erode over time as code is changed.
- **Dynamic equilibrium** — the software ecosystem (tools, platforms, expectations) is in constant
  motion, so a "finished" architecture goes stale; evolvability keeps the system in step with its
  environment instead of frozen against it.

## Evolvable vs Predictable
A recurring principle: **prefer evolvable over predictable.** Where you'd otherwise make an
irreversible, prediction-based decision, prefer the option that keeps change cheap and decisions
reversible (the *last responsible moment*). You trade the illusion of a perfect plan for the real
ability to adapt.
