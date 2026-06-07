# Engineering Incremental Change (Ch 3)

The "incremental" half of the definition — making change safe and small in development and operations.
Load when setting up deployment pipelines, fitness-function gates, or release mechanics. For the
governance angle (architecture rules as code) see `governance.md`.

## Contents
- Two facets of incremental change
- The deployment pipeline
- Fitness functions as pipeline stages
- Release mechanics (toggles, canary, blue-green)
- Hypothesis- and data-driven development
- Case study pattern

## Two Facets of Incremental Change
- **Developmental** — how engineers build: modular, testable, decoupled code so a change touches a
  small area and integrates continuously.
- **Operational** — how the system runs and is released: the ability to deploy small increments safely
  and roll back fast. Both are prerequisites; you can't evolve what you can't deploy in small steps.

## The Deployment Pipeline
The engine of incremental change (Humble & Farley, *Continuous Delivery*). A deployment pipeline
automatically takes a commit through stages to a release decision. A typical multistage pipeline:
1. **CI / build & unit tests** — fast feedback.
2. **Atomic fitness functions** — code-structure, contract, security-scan gates.
3. **Holistic fitness functions** — integration, performance/scalability, resilience in a
   prod-like environment.
4. **Manual gates** (only where needed) — exploratory QA, compliance sign-off.
5. **Deploy** — to staging/prod with a safe release strategy.
**Fixtures/environments** let each stage run the right fitness functions. The pipeline turns the
"system-wide fitness function" into something that runs on every change.

## Fitness Functions as Pipeline Stages
- Map each fitness function (from `fitness-functions.md`) to a **stage** by its cadence: *triggered*
  ones become build/deploy gates; *continual* ones run as production monitors feeding back; *temporal*
  ones run on schedule (cron job, scheduled pipeline).
- A failing fitness function **breaks the build** — architectural regressions are caught like any other
  test failure, the moment they're introduced (this is the heart of automated governance).
- Keep stages ordered fast→slow (fail cheap first) so feedback stays quick.

## Release Mechanics (decoupling deploy from release)
- **Feature toggles / flags** — merge and deploy incomplete work dark; turn on independently. Enables
  trunk-based development and fine-grained rollback. (Remove stale toggles — they're debt.)
- **Canary releases** — route a small % of traffic to the new version; promote if its fitness functions
  (latency, errors) stay green; otherwise roll back.
- **Blue-green deployment** — two environments, switch traffic atomically, instant rollback.
These make change *operationally* incremental and reversible — supporting "prefer evolvable."

## Hypothesis- and Data-Driven Development
- Treat features as **hypotheses**: "we believe change X improves metric Y." Ship a small increment,
  measure with production fitness functions, keep or revert based on data.
- Data/telemetry from continual fitness functions feeds the next increment — evolution guided by
  evidence, not opinion. (Expanded in `practice.md` under culture of experimentation.)

## Case Study Pattern
The book's running example (PenultimateWidgets) adds fitness functions to an existing **invoicing
service**: introduce a deployment pipeline, add an atomic fitness function (e.g., detect new package
cycles / enforce a layering rule), then a holistic one (e.g., scaling/latency under load), so future
changes can't reintroduce the problems. The pattern to copy: *pick a real degradation you want to
prevent → write a fitness function for it → wire it into the pipeline → iterate.*
