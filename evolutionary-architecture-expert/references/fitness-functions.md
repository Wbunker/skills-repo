# Fitness Functions (Ch 2)

The central technique of the book. Load when defining, classifying, or writing fitness functions. For
running them in a pipeline see `incremental-change.md`; for governance-as-code see `governance.md`.

## Contents
- Definition & origin
- The taxonomy (the categories)
- Worked examples by dimension
- Tools
- The system-wide fitness function
- How to write good ones

## Definition & Origin
An **architectural fitness function provides an objective integrity assessment of some architectural
characteristic(s).** Borrowed from evolutionary computing (genetic algorithms use a "fitness function"
to judge how close a candidate solution is to the goal). In architecture, fitness functions judge
whether the system still meets its required characteristics as it changes. **If you can't measure a
characteristic, you can't protect it** — so making the `-ilities` testable is the whole game.

## The Taxonomy (the categories)
Fitness functions are classified along several independent axes — a single fitness function has a value
on each:

- **Scope**
  - **Atomic** — checks a single dimension in isolation (e.g., a unit test asserting cyclomatic
    complexity, or a layering rule).
  - **Holistic** — checks a *combination* of characteristics together, catching emergent interactions
    (e.g., security + scalability under load — the two can conflict).
- **Cadence (how often it runs)**
  - **Triggered** — runs on an event: a commit, a build, a deploy (most unit/integration-style checks).
  - **Continual** — runs constantly in production (monitoring, synthetic transactions; "monitoring-driven
    development").
  - **Temporal** — runs on a time schedule (e.g., monthly check for outdated/CVE'd dependencies, a
    breaking-change deadline).
- **Result**
  - **Static** — fixed pass/fail against a set threshold (e.g., test coverage ≥ X, latency < Y ms).
  - **Dynamic** — acceptable values shift with context (e.g., allowable latency rises as scale rises).
- **Invocation**
  - **Automated** — runs in CI/CD or monitoring (the default goal).
  - **Manual** — for things not yet automatable (legal/compliance sign-off, exploratory QA, manual
    security review). Still a fitness function — just human-executed.
- **Proactivity**
  - **Intentional** — defined up front when you know the characteristic matters.
  - **Emergent** — discovered during the project as you learn what needs protecting; add them as you go.
- **Domain-specific** — fitness functions for business/regulatory rules unique to the system (e.g.,
  "a trade must be auditable end-to-end").

## Worked Examples by Dimension
- **Code structure** — ArchUnit/NetArchTest rules: "controllers may not depend on persistence,"
  no package cycles, naming conventions, layering. (Atomic, triggered, static, automated.)
- **Performance/scalability** — assert p99 latency under load; elasticity test that the system scales
  with traffic. (Often holistic + dynamic.)
- **Resilience** — **Chaos engineering (Netflix Simian Army / Chaos Monkey) is a fitness function**:
  it continually verifies the system tolerates failure. (Holistic, continual.)
- **Security** — dependency vulnerability scans, zero-day checks. (Temporal or triggered.)
- **Operability** — health checks, error-budget/SLO monitors in prod. (Continual.)
- **Data** — schema-migration validity, referential integrity, data-quality/age checks (see
  `structure-and-data.md`).

## Tools
- **ArchUnit** (Java), **NetArchTest** / ArchUnitNET (.NET) — code-structure rules as unit tests.
- **JDepend / dependency-cruiser / import-linter** — dependency & cycle checks.
- **PACT / Spring Cloud Contract** — consumer-driven contract tests (integration evolvability).
- **Cucumber/Gherkin** — executable domain fitness functions.
- **Chaos Monkey / Gremlin** — resilience fitness functions.
- **Prometheus/Grafana, k6/Gatling, JMeter** — continual & performance fitness functions.

## The System-Wide Fitness Function
No single test captures "good architecture." The **system-wide (or system) fitness function** is the
*collection* of all individual fitness functions taken together — the conceptual whole that guides the
architecture. Maintain it like a portfolio: review, add (emergent), retire, and watch for fitness
functions that conflict (that's a real architectural trade-off to decide explicitly).

## How to Write Good Ones
- Start from a **characteristic that matters** (don't test what doesn't). Tie each to a dimension.
- Make it **objective and runnable** — a clear pass/fail or measured value, not a vibe.
- Prefer **automated + triggered** in a deployment pipeline; fall back to manual only where automation
  isn't feasible yet, and revisit.
- Keep them **lightweight** — heavy, slow, or flaky fitness functions get ignored or disabled (see the
  over-governance antipattern in `practice.md`).
- **Document & socialize** them as living architecture: the fitness functions *are* the architecture's
  enforceable definition. (Automating them: `governance.md`.)
