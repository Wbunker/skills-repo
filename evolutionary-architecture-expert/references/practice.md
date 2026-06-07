# Practice & Impact — Building (Ch 7), Pitfalls (Ch 8), Putting Into Practice (Ch 9)

How to apply evolutionary architecture: build/retrofit it, avoid the traps, and roll it out in a real
organization. Load when planning adoption, migrating a system, or reviewing for antipatterns.

## Contents
- Building evolvable architectures (the steps)
- Retrofitting & migrating existing systems
- Guidelines for evolvable design
- Pitfalls and antipatterns
- Organizational factors (Conway's Law)
- Culture of experimentation
- Where to start

## Building Evolvable Architectures (the steps)
The book's three-step method (the same one in SKILL.md):
1. **Identify the dimensions** affected by evolution (which architectural characteristics matter).
2. **Define fitness function(s)** for each dimension (make them objective/testable).
3. **Use deployment pipelines** to automate the fitness functions so evolution stays guided.
Greenfield: design quanta with appropriate coupling and add fitness functions from day one.

## Retrofitting & Migrating Existing Systems
- **Understand coupling first** — map the existing connascence/quanta before changing anything;
  appropriate coupling is the precondition for evolvability.
- **Migrate monolith → service-based incrementally**: decompose along **business capabilities**,
  identify quantum boundaries, break hard dependencies, extract components, then services — one slice at
  a time behind the deployment pipeline. Avoid big-bang rewrites.
- **COTS / packaged software** constrains evolvability (you don't control its fitness) — isolate it
  behind an **anticorruption layer**.
- Add fitness functions to **lock in** characteristics as you migrate so you don't regress.

## Guidelines for Evolvable Design
- **Remove needless variability** — eliminate "snowflake" servers; use immutable infrastructure and
  reproducible builds so the only variability left is intentional.
- **Make decisions reversible** (last responsible moment); enable fast rollback (canary, blue-green,
  toggles) so wrong evolutions are cheap.
- **Prefer evolvable over predictable** — don't over-engineer for predicted futures.
- **Build anticorruption layers** *just in time* (DDD) to keep external/legacy coupling from leaking in.
- **Keep appropriate coupling** and independently deployable quanta (see `structure-and-data.md`).

## Pitfalls and Antipatterns
The book distinguishes **antipatterns** (look good, go bad over time) from **pitfalls** (bad from the
start). Key ones:
- **Technical:**
  - *Last 10% trap / low-code-high-control* — tools/frameworks get you 90% fast, the last 10% is
    impossible; you're stuck.
  - *Vendor King* — building the whole architecture around an ERP/vendor product; the vendor dictates
    (and limits) your evolution. Treat vendor products as one component behind an anticorruption layer.
  - *Leaky abstractions* — deep tool/abstraction stacks where low-level failures surface unpredictably.
  - *Resume-Driven Development* — choosing tech for novelty/CV, not fit.
- **Incremental-change pitfalls:**
  - *Inappropriate (excessive) governance* — heavy standards/gates that crush productivity; right-size
    via Goldilocks governance.
  - *Lack of speed to release* — without genuine CD you can't evolve incrementally.
- **Business pitfalls:**
  - *Excessive product customization* — per-customer forks that explode evolution cost.
  - *Reporting / shared-data coupling* — reporting needs driving inappropriate data entanglement.
  - *Planning horizons / sunk cost* — over-long upfront plans and "irrational artifact attachment"
    (defending a design because of effort spent). Prefer evidence over sunk cost.

## Organizational Factors (Conway's Law)
- **Conway's Law** — systems mirror the communication structure of the org that builds them. Team
  boundaries become architecture boundaries.
- **Inverse Conway Maneuver** — deliberately structure teams to match the architecture you *want*
  (small, cross-functional, domain-aligned teams → well-bounded quanta).
- Organize **product/domain-centric, cross-functional teams** (not siloed by tech layer) so a team can
  own and evolve a quantum end to end. Team coupling shows up as software coupling.

## Culture of Experimentation
- Evolution thrives on a **culture of experimentation**: **hypothesis-driven development** (ship small,
  measure with production fitness functions, keep or revert on data), A/B tests, spikes, and bringing
  ideas from outside.
- Fitness functions are the **experimental instrument** — they tell you objectively whether an
  experiment preserved the architecture's qualities.
- Budgeting/funding should allow experiments, not just predetermined features.

## Where to Start
- **First, get testability + a deployment pipeline** — they're the prerequisites for any fitness
  function. Often the highest-value first step in a legacy system.
- Add a few **high-value, low-effort fitness functions** for the characteristics most at risk
  (emergent additions come later).
- Use the **inverse Conway maneuver** to align teams as you go.
- Sell it to the business as **risk reduction + speed**, not a rewrite: cheaper, safer change and
  protection against architectural decay.
