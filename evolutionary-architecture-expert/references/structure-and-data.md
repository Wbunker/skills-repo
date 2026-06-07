# Structure & Data — Topologies (Ch 5) and Evolutionary Data (Ch 6)

How design choices determine evolvability. Load when reasoning about coupling, quanta, topology choice,
or database evolution. Coupling is the dominant factor in how evolvable an architecture is.

## Contents
- Connascence (the coupling vocabulary)
- Architectural quantum
- Other structural properties
- Comparing topologies by evolvability
- Contracts for evolvable integration
- Reuse: the coupling trap
- Evolutionary data: schema as code
- Data coupling antipatterns

## Connascence (the coupling vocabulary)
Connascence measures how two pieces of code are coupled: two components are connascent if a change in
one requires a change in the other to stay correct. Judge it on **strength** (how hard to change),
**locality** (how close together), and **degree** (how many things affected).
- **Static connascence** (visible in source): of **Name**, **Type**, **Meaning** (magic values),
  **Position** (argument order), **Algorithm** (both sides must share an algorithm, e.g., a checksum).
- **Dynamic connascence** (only at runtime, generally stronger/worse): of **Execution** (order),
  **Timing** (race conditions), **Value** (related values must change together), **Identity** (must
  reference the same instance).
**Rules of thumb:** prefer weaker forms; keep strong connascence **local** (within a module/quantum);
minimize connascence that **crosses** boundaries. Strong, remote coupling is what kills evolvability.

## Architectural Quantum
The book's key structural unit: **an architectural quantum is an independently deployable artifact with
high functional cohesion and synchronous connascence** — everything that must be deployed together to
function. The quantum is the **unit of evolution**: you evolve quanta, not files.
- **More, smaller quanta → more evolvable** (each changes/deploys independently).
- A monolith is a **single large quantum** (low evolvability); well-formed microservices are **many
  small quanta** (high evolvability) — *if* coupling is appropriate.
- **Granularity** matters: too fine and you get distributed coupling/chatty calls; too coarse and you
  lose independence. Aim for quanta aligned to business capabilities.

## Other Structural Properties
- **High functional cohesion** — a quantum should do one business thing; cohesion bounds good quantum size.
- **Independently deployable** — no lockstep releases with other quanta.
- **Appropriate coupling** — not zero coupling (impossible/useless), but the *right* amount in the
  *right* places (weak across boundaries, stronger within).

## Comparing Topologies by Evolvability
Architectural styles rank by how well they support guided incremental change — driven by their quanta
and coupling, not their names:
- **Big ball of mud / unstructured** — worst; everything coupled.
- **Layered / monolith** — single quantum; low evolvability but simple.
- **Service-based / modular monolith** — coarse quanta; moderate.
- **Microservices / event-driven** — many small quanta, low coupling; **highest evolvability** (at the
  cost of operational complexity). Choose based on how much evolvability the system actually needs.

## Contracts for Evolvable Integration
Integration points couple quanta. Use **contracts** to evolve them safely:
- **Consumer-driven contracts** (PACT, Spring Cloud Contract) — consumers publish expectations;
  providers run them as **fitness functions** so a provider change that breaks a consumer fails the build.
- Prefer loose, versioned, tolerant-reader contracts over shared types. This lets quanta evolve
  independently without big-bang coordinated releases.

## Reuse: the Coupling Trap
**Excessive reuse creates coupling**, which fights evolvability. A shared library/service everyone
depends on becomes a change bottleneck and a single point of failure.
- Favor **appropriate duplication** over coupling-creating reuse when the shared thing changes for
  different reasons per consumer.
- For orthogonal/operational concerns, use the **sidecar pattern / service mesh** to share capability
  (logging, security, telemetry) *without* code coupling.
- "Pull, don't reuse" when reuse would bind unrelated quanta together.

## Evolutionary Data: Schema as Code
Data is a first-class evolutionary dimension (Sadalage & Fowler, *Refactoring Databases*):
- **Database refactoring / migrations as code** — Flyway, Liquibase; every schema change is a versioned,
  tested migration that runs in the **deployment pipeline** (a data fitness function).
- **Expand/contract (parallel change)** — to change a schema with zero downtime: **expand** (add the
  new structure, write to both), **migrate** (backfill, switch reads), **contract** (remove the old).
  This makes data changes incremental and reversible.
- **Data as a fitness function** — referential integrity, data **quality**, and data **age** can be
  asserted and monitored.

## Data Coupling Antipatterns
- **Shared database integration** — multiple services on one schema is *inappropriate coupling*; a
  schema change ripples across services and blocks independent evolution. Give each quantum its own data.
- **Inappropriate data entanglement** — foreign keys, triggers, and stored procedures spanning quanta
  bind them together.
- **Two-phase commit (distributed transactions)** — strong dynamic coupling (connascence of timing/
  execution) across quanta; avoid by designing for eventual consistency / sagas where possible.
- Migrating data with the architecture (e.g., relational → NoSQL, or splitting a shared DB) is part of
  evolving the system, not an afterthought.
