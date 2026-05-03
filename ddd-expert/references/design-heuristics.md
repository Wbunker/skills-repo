# Design Heuristics — Chapters 10–11

Heuristics are not rules — they are decision aids for situations where no single correct answer exists. Apply them, weigh their guidance, then exercise judgment. These heuristics cover bounded context boundaries, aggregate design, tactical pattern selection, and evolution strategies.

---

## Heuristics for Finding Bounded Context Boundaries

### Linguistic Heuristics
1. **The vocabulary test**: gather domain experts from different parts of the organization and ask them to define the same term. When definitions diverge, you've found a boundary.
2. **The conversation test**: when two groups of domain experts talk past each other about the "same" concept, they're working in different bounded contexts.
3. **The overloading test**: if a single term means different things depending on context ("account" in CRM vs. billing vs. auth), each context deserves its own model with its own term.

### Organizational Heuristics
4. **Team ownership**: if two different teams maintain a piece of the system independently, it's likely two bounded contexts. Conway's Law is prescriptive as well as descriptive — design your teams to match your desired architecture.
5. **Business capability alignment**: one bounded context per distinct business capability is a good starting heuristic. Business capabilities rarely need to be split further at the BC level.
6. **Domain expert ownership**: if one domain expert is the authoritative source for a piece of domain knowledge, that knowledge likely belongs in one bounded context.

### Lifecycle Heuristics
7. **Change frequency**: entities that change together, for the same reasons, tend to belong in the same bounded context. Entities that change independently, for different reasons, are likely in different contexts.
8. **Transaction boundary**: operations that must be atomic belong together. Operations that can tolerate eventual consistency can be separated.
9. **Deployment independence**: if two parts of the system are always deployed together, splitting them into separate bounded contexts is premature. If they need to be deployed independently, they should be separate contexts.

### Warning Signs That a BC Is Too Large
- The "ubiquitous language" inside it is actually ambiguous — the same word means different things in different parts of the codebase.
- The team maintaining it is too large to be effective (pizza rule: > 8–10 people).
- Changes in one area frequently break another area with no business relationship.
- The bounded context contains multiple unrelated aggregate clusters.

### Warning Signs That a BC Is Too Small
- Every use case requires orchestrating calls to 5+ bounded contexts.
- Data that naturally belongs together (same lifecycle, same business rules) is split across multiple contexts, requiring constant synchronization.
- Teams spend more time managing integration contracts than delivering features.

---

## Heuristics for Aggregate Design

### The Consistency Question (Most Important)
**"What must be true together, always?"** — State that must always be consistent within a single transaction defines the aggregate boundary. If two objects never need to be consistent at the same instant, they don't need to be in the same aggregate.

### The Small Aggregate Heuristic
Start with the smallest possible aggregate that can still protect its invariants. If you're unsure, err toward smaller. You can always merge aggregates later when you discover they share invariants; it's harder to split a large aggregate.

### The Reference-by-ID Heuristic
If you find yourself traversing from one aggregate to another via an object reference (not an ID), ask: "Do these two things share an invariant?" If yes, they might belong in the same aggregate. If no, the reference should be an ID.

### The Single Responsibility Heuristic
Each aggregate should have one primary reason to change — one aspect of the domain it's responsible for protecting. If an aggregate changes for many different business reasons, it's probably too large.

### The Contention Heuristic
Aggregates with many concurrent writers will experience contention (optimistic locking conflicts). If an aggregate is frequently contended, either it's too large (split it) or the business process needs redesigning. Common cause: a shared counter or list that all users modify.

### Aggregate Design Red Flags
- An aggregate holds references to many other aggregates via object references (not IDs).
- An aggregate has dozens of properties, many of which are unrelated.
- Loading an aggregate requires joining many tables or loading many child collections.
- Business methods on the aggregate take many parameters from outside the aggregate.
- Two aggregates always need to be updated together (indicates they may actually be one aggregate, or they need a saga).

---

## Heuristics for Choosing Tactical Patterns

The primary driver is **subdomain type and complexity**, but also consider team skill, time pressure, and codebase maturity.

### By Subdomain Type (Primary Heuristic)

| Subdomain Type | Default Pattern | Upgrade When |
|----------------|-----------------|--------------|
| Generic | Transaction Script | It never upgrades — buy or use OSS |
| Supporting (simple) | Transaction Script or Active Record | Logic grows beyond simple CRUD |
| Supporting (moderate) | Active Record | Complex invariants emerge |
| Core (moderate) | Domain Model | Always for core |
| Core (complex, audit) | Event Sourcing + Domain Model | Audit, temporal, replay needed |

### By Business Logic Complexity

**Symptoms that you need to upgrade to Domain Model:**
- You have multiple if/else chains enforcing the same business rule in different services.
- The same business concept appears with slightly different validation rules in different places.
- Developers need to read the database to understand what state an entity is in.
- Business logic is scattered across services, controllers, and database stored procedures.

**Symptoms that you're over-engineering with Domain Model:**
- Your aggregates have one method: `update_fields()`.
- There are no invariants to protect — any combination of field values is valid.
- Domain experts can't name the "things" the domain model represents.
- The model is isomorphic to the database schema (you have an ORM, not a domain model).

### The Core Subdomain Litmus Test
If you're uncertain whether to use Domain Model for a subdomain, ask: "Would this subdomain qualify as intellectual property worth protecting?" If yes, it's core — invest in Domain Model. If no, use simpler patterns and save the investment.

---

## Evolving Design: Migration Strategies

### Strangler Fig Pattern (Incremental Replacement)
The strangler fig grows around a host tree, gradually replacing it. The original system continues to run while the new system grows around it.

**Steps:**
1. **Identify a seam** — find a capability in the legacy system that can be extracted without breaking others.
2. **Build the new implementation** — implement the same capability in the new bounded context with proper DDD patterns.
3. **Route new traffic** — use a facade/proxy to route new requests to the new implementation. Existing legacy traffic still goes to the old system.
4. **Migrate data** — synchronize data between old and new systems (bidirectional sync or event-based).
5. **Cut over** — once the new system handles all traffic, retire the old code path.
6. **Repeat** — identify the next seam and repeat.

**Gotcha**: the strangler fig only works if you can route at the seam. If the legacy system is a monolith with no clear entry points, you may need to create a facade first.

### Big Ball of Mud → DDD Migration Path

A **Big Ball of Mud** (BBOM) is a system with no clear architecture, where everything is coupled to everything else. Migrating a BBOM to DDD is a multi-year effort that cannot be done all at once.

**Phase 1: Understand the problem space**
- Run Big Picture EventStorming to discover subdomains and bounded contexts.
- Identify the core subdomain — this is where you'll focus first.
- Map the current system to subdomains (which parts of the monolith correspond to which subdomain?).

**Phase 2: Protect the core with an ACL**
- Add an Anti-Corruption Layer around the module you want to modernize.
- The ACL translates the BBOM's implicit model into your new bounded context's ubiquitous language.
- This isolates the new model from the mess.

**Phase 3: Extract incrementally (strangler fig)**
- Extract one capability at a time into a new bounded context.
- Establish proper bounded context contracts at the seams.
- Use the outbox pattern when event-driven integration is needed.

**Phase 4: Invest in the core**
- Once extracted, apply full tactical patterns (Domain Model, repositories, etc.) to the core subdomain.
- Supporting subdomains can remain simpler.

**Phase 5: Let supporting subdomains be**
- Not everything in a legacy system needs DDD treatment.
- Supporting and generic subdomains may be fine as-is or as transaction scripts behind an ACL.

### Incremental Refactoring: Practical Rules
- **Never do a big rewrite** — always incremental.
- **Keep the old code running** while the new code is built alongside it.
- **Use feature flags** to route traffic between old and new implementations during transition.
- **Don't refactor and feature-add simultaneously** — refactoring is a dedicated effort.
- **Tests before refactoring** — characterization tests on the legacy code document current behavior before you touch it.

---

## When NOT to Use DDD

DDD carries real costs: learning curve, implementation overhead, increased codebase complexity. These costs are only worth bearing when the business logic justifies them.

### Avoid DDD When:
1. **The problem is CRUD** — if the application is primarily creating, reading, updating, and deleting records with minimal business rules, DDD adds ceremony without value.
2. **The domain is well-understood and stable** — if the business logic never changes and is simple, a transaction script with a good database is fine.
3. **Time-to-market is paramount for an MVP** — get the MVP out with simple patterns; refactor to DDD if the product succeeds and complexity grows.
4. **The team has no domain expert access** — DDD requires ongoing collaboration with domain experts. If you can't get their time, you'll invent a model that doesn't match reality.
5. **The subdomain is generic** — buying a SaaS solution or using an open-source library is better than modeling a generic subdomain with DDD.
6. **The team is not familiar with DDD** — introducing DDD to a team without training or coaching leads to cargo-cult DDD: the vocabulary without the substance.

### The Complexity Threshold
DDD earns its cost when:
- The business logic is genuinely complex (complex invariants, many edge cases, frequent change).
- The domain model is expected to evolve significantly over time.
- Multiple developers need to collaborate on the same domain, requiring a shared language.
- The cost of bugs in this area is high (financial, safety, regulatory).

Below this threshold, YAGNI applies: simpler patterns are not technical debt — they're the right choice.

### The Pragmatic Test
Ask: "If we used a transaction script for this, would the code become unmaintainable within 6–12 months?" If yes, use Domain Model. If no, use the simpler pattern. Revisit when conditions change.
