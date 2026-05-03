---
name: ddd-expert
description: Domain-Driven Design expertise covering strategic design (bounded contexts, subdomains, ubiquitous language, context mapping), tactical design (aggregates, value objects, domain events, repositories, domain services, event sourcing), architectural patterns (layered, ports & adapters, CQRS, event-driven), integration patterns (outbox, saga, process manager), EventStorming facilitation, and DDD + microservices. Based on Vlad Khononov's "Learning Domain-Driven Design." Use when designing software systems around business domains, choosing between tactical patterns (transaction script vs active record vs domain model), modeling aggregates and bounded contexts, mapping context relationships, running EventStorming workshops, integrating DDD with microservices, or applying design heuristics and evolution strategies.
---

# DDD Expert

Domain-Driven Design has two schools: **strategic design** (how to carve the problem space into subdomains and map the solution space into bounded contexts) and **tactical design** (the building blocks used inside a bounded context). Strategic design is the higher-leverage investment — getting the boundaries right matters more than which tactical patterns you use. Tactical patterns then give you the implementation vocabulary to express the domain model in code.

## DDD Landscape

```
PROBLEM SPACE                    SOLUTION SPACE
─────────────────────────────────────────────────────────────────
Business Domain
  ├── Core Subdomain          →   Bounded Context (own model)
  │     (competitive edge)         ↕ Context Map
  ├── Supporting Subdomain    →   Bounded Context (or outsourced)
  │     (necessary, not core)      ↕ Context Map
  └── Generic Subdomain       →   Off-the-shelf / shared BC
        (commodity)
                                   Inside a Bounded Context:
                                   ├── Ubiquitous Language
                                   ├── Tactical Patterns
                                   │     Transaction Script
                                   │     Active Record
                                   │     Domain Model
                                   │       Aggregate
                                   │       Entity / Value Object
                                   │       Domain Event
                                   │       Repository
                                   │       Domain Service
                                   │     Event Sourcing
                                   └── Architectural Pattern
                                         Layered
                                         Ports & Adapters
                                         CQRS
                                         Event-Driven
```

## Quick Reference

| Task | Reference File |
|------|---------------|
| Classify subdomains; define bounded contexts; ubiquitous language; context mapping patterns | [strategic-design.md](references/strategic-design.md) |
| Choose tactical pattern; design aggregates, value objects, domain events, repositories | [tactical-design.md](references/tactical-design.md) |
| Select architectural pattern: layered, hexagonal, CQRS, event-driven | [architectural-patterns.md](references/architectural-patterns.md) |
| Outbox, saga, process manager, cross-BC integration | [integration-patterns.md](references/integration-patterns.md) |
| Heuristics for BC/aggregate boundaries; when to use DDD; legacy migration | [design-heuristics.md](references/design-heuristics.md) |
| Run EventStorming workshops; notation; facilitation steps | [eventstorming.md](references/eventstorming.md) |
| DDD + microservices; service granularity; distributed design | [ddd-microservices.md](references/ddd-microservices.md) |

## Reference Files

| File | Chapters | Topics |
|------|----------|--------|
| strategic-design.md | 1–4 | Domains, subdomains, ubiquitous language, bounded contexts, context mapping (8 patterns) |
| tactical-design.md | 5–7 | Transaction script, active record, domain model, aggregates, value objects, domain events, repositories, event sourcing |
| architectural-patterns.md | 8 | Layered, ports & adapters, CQRS, event-driven architecture |
| integration-patterns.md | 9 | Outbox pattern, choreography/orchestration sagas, process manager |
| design-heuristics.md | 10–11 | BC/aggregate heuristics, pattern selection, legacy migration, when NOT to use DDD |
| eventstorming.md | 12 | Big Picture / Process Modeling / Design-Level workshops, notation, facilitation |
| ddd-microservices.md | 13 | BC-to-service mapping, service granularity, distributed ACL, shared kernel |

---

## Core Decision Trees

### Which Business Logic Pattern?

```
How complex is the business logic?
│
├── Simple ETL / CRUD, no real invariants
│     └── Transaction Script
│
├── Simple business logic, needs object graph + persistence
│   (data and logic together, no complex rules)
│     └── Active Record
│
├── Complex business logic, non-trivial invariants, rich behavior
│   │
│   ├── State-based (current state is what matters)
│   │     └── Domain Model (aggregates, value objects, domain events)
│   │
│   └── Audit log / temporal queries / event replay needed
│         └── Event Sourcing (domain model + event store)
│
└── Hint: match pattern to SUBDOMAIN TYPE
      Core subdomain       → Domain Model (or Event Sourcing)
      Supporting subdomain → Active Record (sometimes Domain Model)
      Generic subdomain    → Transaction Script or off-the-shelf
```

### What Aggregate Boundaries?

```
Start with candidate: one aggregate per noun in ubiquitous language
│
Apply Vernon's 4 rules:
  1. Protect invariants within a single transaction
  2. Design small aggregates
  3. Reference other aggregates by ID only
  4. Use eventual consistency between aggregates
│
Ask:
  ├── Must these objects change together atomically?
  │     YES → same aggregate
  │     NO  → separate aggregates (reference by ID)
  │
  ├── Would this aggregate become a "god object"?
  │     YES → split it
  │
  ├── Is this a value (defined by attributes, no identity)?
  │     YES → value object, not entity
  │
  └── Does this aggregate reference another aggregate?
        If by object reference → refactor to ID reference
```

### Which Context Mapping Pattern?

```
What is the team/organizational relationship?
│
├── Equal collaboration, shared codebase section → Shared Kernel
│
├── Teams cooperate, upstream/downstream agreed  → Partnership
│
├── Upstream controls API, downstream conforms   → Customer-Supplier
│
├── Upstream does not care about downstream       → Conformist
│   (downstream accepts upstream model as-is)
│
├── Downstream needs to isolate from upstream     → Anticorruption Layer (ACL)
│   (translate upstream model at the boundary)
│
├── Upstream publishes stable, versioned API      → Open-Host Service (OHS)
│   with well-defined protocol                      + Published Language
│
└── No integration needed / too costly            → Separate Ways
```

---

## Key Concepts

| Term | Definition |
|------|-----------|
| **Domain** | The sphere of knowledge and activity of the business |
| **Core subdomain** | What differentiates the business; competitive advantage; invest here |
| **Supporting subdomain** | Necessary but not differentiating; simpler patterns OK |
| **Generic subdomain** | Commodity capability; buy or use open-source |
| **Bounded context** | Explicit boundary within which a model is defined and applicable |
| **Ubiquitous language** | Shared, precise vocabulary between developers and domain experts, enforced in code |
| **Aggregate** | Cluster of domain objects treated as a unit for data changes; has a root entity |
| **Entity** | Object with continuous identity; defined by ID, not attributes |
| **Value object** | Immutable object defined entirely by its attributes; no identity |
| **Domain event** | Record of something that happened in the domain; past tense; immutable |
| **Repository** | Abstraction for retrieving and persisting aggregates; hides storage details |
| **Domain service** | Stateless logic that doesn't belong on any single aggregate or value object |
| **Application service** | Orchestrates use cases; no business logic; calls domain objects and infra |
| **Context map** | Visual/documented overview of all bounded contexts and their relationships |
