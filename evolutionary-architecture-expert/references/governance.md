# Automating Architectural Governance (Ch 4)

Turning architecture rules into executable, automated checks — governance that runs instead of
governance by document and review board. Load when enforcing architecture as code or scaling
governance across teams. For the fitness-function taxonomy see `fitness-functions.md`; for pipelines
see `incremental-change.md`.

## Contents
- The shift: governance as code
- Architecture-as-code tools & rules
- Enterprise / holistic governance
- Goldilocks governance (scale to the org)
- Security & dependency governance
- Communicating fitness functions
- Case study pattern

## The Shift: Governance as Code
Traditional architecture governance = guidelines, wikis, and a review board catching violations late
(or never). Evolutionary architecture replaces this with **fitness functions running in the build**:
the architecture's rules become executable tests that fail the pipeline on violation. Governance moves
from *advisory and periodic* to *automated and continuous* — the same rigor as automated testing,
applied to architectural characteristics.

## Architecture-as-Code Tools & Rules
Express structural rules as code that runs every build:
- **ArchUnit** (Java/JVM), **ArchUnitNET / NetArchTest** (.NET), **dependency-cruiser** /
  **import-linter** / **ts-arch** (JS/TS/Python) — assert things like:
  - Layering: "domain must not depend on infrastructure," "controllers only call services."
  - No package/module **cycles**.
  - Naming & location conventions (e.g., "`*Controller` lives in `..web..`").
  - Allowed dependency directions between modules/quanta.
- Each rule is an **atomic, triggered, static, automated** fitness function (per the taxonomy) wired
  into the pipeline as a gate.

## Enterprise / Holistic Governance
- Beyond one codebase: **enterprise-wide fitness functions** enforce cross-team standards (security
  baselines, observability, allowed platforms) consistently.
- **Holistic** governance checks combinations (e.g., scalability *and* security together) in
  prod-like environments, catching emergent problems no atomic check sees.
- Shared, reusable fitness-function libraries let many teams inherit the same guardrails.

## Goldilocks Governance (scale to the org)
Match governance weight to context — not too little, not too much ("just right"). The book frames
three company sizes/risk profiles:
- **Small / low-ceremony** — a handful of high-value fitness functions; speed over control.
- **Medium** — a broader suite, shared across teams.
- **Large / regulated** — comprehensive, including compliance and security fitness functions.
Over-governing a small team kills velocity; under-governing a regulated enterprise invites risk.
*Inappropriate governance* is an explicit antipattern (see `practice.md`).

## Security & Dependency Governance
- **Dependency/CVE scanning** as a fitness function (triggered on build + temporal monthly sweep).
- Zero-day response: a temporal fitness function that flags newly-vulnerable libraries already in use.
- License-compliance checks; secret-scanning. Security becomes a continuously-guarded dimension, not a
  pre-release audit.

## Communicating Fitness Functions
Fitness functions double as **living documentation**: they state, executably, what the architecture
guarantees. Keep them discoverable (a known location/suite), named for the characteristic they protect,
and reviewed as the architecture evolves. New team members learn the architecture's real constraints by
reading the fitness functions.

## Case Study Pattern
The book shows **validating API consistency in the automated build** — a fitness function that fails CI
if a service's API drifts from its agreed contract/standard (naming, versioning, breaking changes).
Copy the pattern: encode the governance rule as a test, add it to the pipeline, and let every build
enforce it — no review meeting required.
