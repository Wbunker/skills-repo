# Prioritization Guide

How to decide what to analyze first, how deep to go, and where documentation
effort yields the highest return. Synthesized from Ousterhout's cognitive load
theory, Rozanski & Woods' stakeholder analysis, and practical heuristics.

## Table of Contents

- [The Cognitive Load Principle](#the-cognitive-load-principle)
- [Documentation ROI Matrix](#documentation-roi-matrix)
- [Depth Heuristics](#depth-heuristics)
- [What NOT to Document](#what-not-to-document)
- [Prioritization by System Type](#prioritization-by-system-type)

---

## The Cognitive Load Principle

From Ousterhout: complexity manifests as **change amplification** (one change
requires many edits), **cognitive load** (developer must hold too much context),
and **unknown unknowns** (developer doesn't know what they don't know).

**Documentation priority = cognitive load created x frequency of encounter.**

### Module Depth Analysis

Prioritize documentation based on the depth/shallowness of modules:

```
Deep module (simple interface, complex internals)
├── Document the INTERFACE thoroughly
├── Skip internals (complexity is properly hidden)
├── Focus on: contract, preconditions, postconditions, error cases
└── Example: a database connection pool — document how to use it, not how it works

Shallow module (complex interface, limited functionality)
├── These LEAK complexity — document EVERYTHING
├── Focus on: why the interface is shaped this way, common usage patterns
├── Consider recommending refactoring
└── Example: a config class with 30 constructor parameters

Cross-module dependency
├── Document EVERY non-obvious coupling
├── Focus on: what changes in A require changes in B
├── Include: ordering constraints, shared state, implicit contracts
└── Example: module A publishes events that module B must consume in order
```

### Unknown Unknowns Priority

These are the highest-priority documentation targets because they cause the
most damage. Indicators of unknown unknowns:

| Indicator | Example | Documentation Action |
|-----------|---------|---------------------|
| Implicit ordering | Must call init() before process() | Document as precondition |
| Hidden side effects | Writing to cache also invalidates another service | Document as side effect |
| Non-obvious failure modes | Timeout causes data duplication | Document in integration inventory |
| Environment-specific behavior | Works in dev, fails in prod due to config | Document in gotchas |
| Convention violations | This module breaks the pattern used everywhere else | Document as inferred ADR |
| Shared mutable state | Global variable modified by multiple modules | Document as coupling risk |
| Temporal coupling | Events must arrive within 5s or transaction times out | Document as constraint |

---

## Documentation ROI Matrix

Where to invest analysis time for maximum impact:

### High ROI (Always Document)

| Target | Why | How Deep |
|--------|-----|----------|
| System boundary (C4 L1) | Orients everyone; changes slowly | Complete |
| Container topology (C4 L2) | Developers need the big picture | Complete |
| Primary request flow | Most common debugging starting point | Full sequence diagram |
| External integration points | Highest failure risk | Full inventory with failure modes |
| Inferred ADRs (top 5) | Prevents re-making old decisions | Full ADR format |
| Non-obvious conventions | Prevents bugs from pattern violations | "Where to Look" entry |

### Medium ROI (Document When Requested)

| Target | Why | How Deep |
|--------|-----|----------|
| Component analysis (C4 L3) | Useful for specific container work | Per container as needed |
| Secondary request flows | Important but less common paths | Sequence diagram |
| Layer structure | Helps enforce architecture | Diagram + violation list |
| Data model (ERD) | Important for data work | Tables, relationships, key constraints |
| Security boundaries | Critical but specialized audience | Boundary diagram + auth flow |

### Low ROI (Document Only on Request)

| Target | Why | How Deep |
|--------|-----|----------|
| Code-level detail (C4 L4) | Changes too fast; IDE does this | Only for specific complex areas |
| Utility modules | Self-explanatory, low coupling | Skip unless non-obvious |
| Test implementation | Tests are their own documentation | Skip — read the tests directly |
| Build/CI internals | Standard tooling, well-documented elsewhere | Only if custom/non-obvious |
| Third-party library usage | Library docs exist | Only if wrapper pattern is non-obvious |

---

## Depth Heuristics

### How Deep Should I Go?

```
For each area of the codebase, ask:

1. Does a new developer need to understand this to be productive?
   ├── Yes → Document at least to Component level (C4 L3)
   └── No → Skip unless specifically requested

2. Has this area caused bugs or confusion in the past?
   ├── Yes → Document thoroughly including failure modes
   └── No → Standard depth

3. Does this area cross module/service boundaries?
   ├── Yes → Document the interface contract and data flow
   └── No → Interface summary is sufficient

4. Is this area likely to change soon?
   ├── Yes → Document the extension points and constraints
   └── No → Static description is sufficient

5. Is the code self-explanatory?
   ├── Yes → Document only the "why" (inferred ADR)
   └── No → Document both "what" and "why"
```

### Time-Boxing Analysis

For a full codebase analysis, allocate time proportionally:

| Phase | % of Time | Rationale |
|-------|-----------|-----------|
| Phase 1: Orient | 10% | Quick scan, sets direction for everything |
| Phase 2: Map Structure | 25% | Foundation for all other analysis |
| Phase 3: Trace Runtime | 25% | Highest value for debugging/extending |
| Phase 4: Surface Contracts | 15% | Critical for interface documentation |
| Phase 5: Excavate Decisions | 10% | High value but can be done selectively |
| Phase 6: Assess Risk | 10% | Important but focused on integration points |
| Phase 7: Produce Artifacts | 5% | Formatting/polishing — analysis is already done |

---

## What NOT to Document

Save time and context window by skipping these:

### Never Document

- **What the code literally does** — The code says this already. Document *why*.
- **Standard library usage** — `Array.map()` doesn't need explanation.
- **Framework conventions** — If Rails says put models in `app/models/`, don't restate it.
- **Obvious structure** — A file called `UserService.ts` containing a `UserService` class.
- **Generated code** — Migrations, compiled output, lock files.
- **Deprecated code** — Unless it's still running in production.

### Document Only the Delta

- **Wrapper patterns** — Only document *why* the wrapper exists, not how the wrapped library works.
- **Config files** — Only document non-default or non-obvious values.
- **Test files** — Only document the testing strategy, not individual tests.
- **CI/CD** — Only document steps that aren't standard for the framework.

### The "Would They Google It?" Test

Before documenting something, ask: "Would a competent developer in this stack
Google this, and find the answer in <2 minutes?"
- Yes → Don't document it.
- No → Document it.

---

## Prioritization by System Type

### Monolith

```
Priority order:
1. Module decomposition (how is this big thing organized?)
2. Layer structure (what depends on what?)
3. Primary request flows (how does a request traverse the layers?)
4. Database schema (single database is often the integration point)
5. Extension patterns (how do I add a new feature following the pattern?)
```

### Microservices

```
Priority order:
1. Container topology (what services exist and how they communicate)
2. Integration point inventory (every service boundary is a risk)
3. Event/message contracts (async communication is hardest to trace)
4. Data ownership (which service owns which data?)
5. Deployment topology (how does this run in production?)
```

### Library / SDK

```
Priority order:
1. Public API surface (the whole point of the library)
2. Extension points (how do users customize behavior?)
3. Design decisions / trade-offs (why is the API shaped this way?)
4. Usage examples for common scenarios
5. Version compatibility and migration paths
```

### Data Pipeline

```
Priority order:
1. Pipeline stages (what transforms data, in what order?)
2. Data contracts (input/output schemas at each stage)
3. Failure and retry behavior (what happens when a stage fails?)
4. Data lineage (where does data come from, where does it go?)
5. Performance characteristics (throughput, latency, batch sizes)
```

### Event-Driven System

```
Priority order:
1. Event catalog (what events exist, their schemas)
2. Producer-consumer map (who publishes, who subscribes)
3. Ordering and consistency guarantees
4. Failure and dead-letter handling
5. Saga/orchestration patterns (for multi-step workflows)
```
