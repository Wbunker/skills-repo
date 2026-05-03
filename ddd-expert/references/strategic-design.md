# Strategic Design — Chapters 1–4

Strategic design answers: **What are we building, and how should we carve it up?** It operates in two spaces: the problem space (subdomains) and the solution space (bounded contexts). Confusing the two is one of the most common DDD mistakes.

---

## Business Domain and Subdomains (Chapter 1)

### Business Domain
A **business domain** is the main area of activity of the company — what the company does to earn money (e.g., "online retail," "insurance underwriting," "logistics"). A company can operate in multiple business domains.

### Subdomain Types

| Type | Description | Characteristics | Tactical Implication |
|------|-------------|-----------------|---------------------|
| **Core** | The company's competitive differentiator; unique to the business | Complex, volatile, high value; cannot be bought off-the-shelf | Invest most in design quality; use Domain Model or Event Sourcing |
| **Supporting** | Required to support core capabilities; not a differentiator | Simpler logic; competitors likely solve the same problem, but differently | Active Record or Transaction Script; consider outsourcing |
| **Generic** | Commodity functionality that all companies need | Well-understood, stable; solved problems (auth, email, payments) | Buy or use OSS; avoid inventing here |

### How to Identify Subdomain Type
1. **Ask: "Could I buy this?"** — If yes, it's generic or supporting.
2. **Ask: "Would competitors have this exact logic?"** — If yes, it's generic.
3. **Ask: "Would losing this put us out of business?"** — If yes, it's core.
4. **Ask: "Does this directly generate revenue or differentiate our product?"** — Core.
5. **Watch for volatility** — Core subdomains change frequently as the business evolves; generic ones are stable.

### Subdomain Boundaries
Subdomains are discovered, not designed. They reflect how the business operates, not how the software is built. Multiple subdomains can exist within one legacy system. One microservice can span subdomains (though this is usually a smell).

**Gotcha**: The same concept (e.g., "User") can appear in multiple subdomains with different meanings. In CRM it might be a "Lead" or "Customer"; in billing it's an "Account." This is expected and fine — it's a signal you need separate bounded contexts.

---

## Ubiquitous Language (Chapter 2)

### Definition
The **ubiquitous language** is a shared, precise, unambiguous vocabulary used by both domain experts and engineers. It is not a translation layer — developers must internalize the domain language, and it must appear in the code (class names, method names, variable names, database columns).

### Why It Matters
Ambiguous language hides conceptual confusion. If developers use different words than domain experts, or if the same word means different things in different contexts, the model becomes inconsistent. Many bugs are really vocabulary bugs.

### How to Discover Ubiquitous Language
1. **Interview domain experts** — ask them to walk through scenarios using their words, not IT words.
2. **Collect domain terms** — maintain a living glossary; definitions come from domain experts, not developers.
3. **Watch for ambiguity** — if a term means different things to different people, you likely have a boundary.
4. **Look for implicit concepts** — domain experts often describe processes without naming the concept. Name it.
5. **Challenge with examples** — "What happens when an order is placed but inventory is low?" forces precision.

### How to Maintain It
- **Code enforces language**: rename classes/methods when the business renames concepts.
- **Glossary as a living document**: version it alongside the code.
- **Ubiquitous language per bounded context**: the same word CAN mean different things in different bounded contexts. "Account" in billing vs. "Account" in CRM are different concepts.

### How to Test for It
- Can a domain expert read the code (at a high level) and confirm it matches how the business works?
- Does a new developer learn the domain by reading the code?
- Are there any terms in the code that domain experts don't recognize?

**Gotcha**: "Ubiquitous" does not mean global. It means universal within a bounded context. Trying to create one universal language across the whole company is a trap — it leads to bloated, ambiguous models.

---

## Bounded Contexts (Chapter 3)

### Definition
A **bounded context** is an explicit boundary (logical or physical) within which a particular domain model is defined, consistent, and applicable. Inside the boundary, all terms have precise, unambiguous meanings. Outside the boundary, the same term may mean something different.

### Bounded Context vs. Subdomain

| | Subdomain | Bounded Context |
|--|-----------|----------------|
| Space | Problem | Solution |
| Discovered or designed? | Discovered | Designed |
| Represents | Business capability | Software model/system |
| Changes when? | Business changes | Team decides |
| Size | Usually natural grouping | Team's design decision |

**Key insight**: Subdomains exist in the problem space — they reflect how the business works. Bounded contexts exist in the solution space — they reflect how we choose to model it. Ideally, one bounded context maps to one subdomain, but this is not required and is often not true in legacy systems.

### How to Identify Bounded Context Boundaries

1. **Linguistic boundaries**: When the same word means different things to different groups of people, you have a bounded context boundary.
2. **Organizational boundaries**: Different teams with different domain experts often indicate different bounded contexts.
3. **Lifecycle boundaries**: Objects that change together often belong together.
4. **Invariant boundaries**: Business rules that must be consistent form the core of a bounded context.
5. **Integration boundaries**: Where data formats change or translation is needed is a boundary.

### Bounded Context Size
- Khononov's heuristic: a bounded context should be **as small as possible** while still containing a consistent, meaningful model.
- Too large: the model becomes inconsistent, language becomes ambiguous.
- Too small: excessive integration overhead; anemic models; forced coupling through APIs.
- **Conway's Law** applies: system boundaries tend to mirror team/organizational boundaries. Design your teams and your bounded contexts together.

### What Lives Inside a Bounded Context
- The ubiquitous language (its vocabulary and grammar)
- The domain model (aggregates, entities, value objects, domain events)
- The application and infrastructure layers
- Potentially: a database schema, a service, a module

---

## Context Mapping (Chapter 4)

A **context map** is a document (often a diagram) that captures all bounded contexts and the integration relationships between them. It is both a technical artifact and an organizational one — it reveals power relationships between teams.

### The 8 Context Mapping Patterns

#### 1. Partnership
- **Forces**: Two teams have a mutual dependency; neither can deliver value without the other's cooperation.
- **Structure**: Both teams commit to coordination. They synchronize release schedules and API changes.
- **When to use**: Early-stage products; tightly-coupled teams that trust each other.
- **Consequences**: High coordination cost. Fails if one team stops cooperating.
- **Gotcha**: Partnership requires ongoing active collaboration, not just a shared API contract.

#### 2. Shared Kernel
- **Forces**: Two bounded contexts share a subset of the model (code, database, or schema).
- **Structure**: A shared, explicitly-defined portion of the domain model is co-owned by both teams. Changes require both teams' agreement.
- **When to use**: When duplication is genuinely worse than coupling; rarely justified.
- **Consequences**: Any change can break both contexts. High coordination cost.
- **Gotcha**: The shared kernel tends to grow over time unless actively governed. Start small.

#### 3. Customer-Supplier (Upstream/Downstream)
- **Forces**: Downstream team depends on upstream team's output. Upstream has power.
- **Structure**: Downstream acts as "customer" — can raise requirements, but upstream chooses what to build and when. Formalized through planning meetings.
- **When to use**: When the upstream team is cooperative but has its own roadmap.
- **Consequences**: Downstream must plan around upstream's schedule.

#### 4. Conformist
- **Forces**: Upstream team has no incentive to support downstream. Downstream has no leverage.
- **Structure**: Downstream simply accepts and uses the upstream model as-is — no translation layer.
- **When to use**: When the upstream model is good enough and the cost of translation exceeds the benefit.
- **Consequences**: Downstream team's model becomes coupled to upstream's design decisions. Can pollute the domain model with foreign concepts.
- **Gotcha**: Often chosen out of laziness when an ACL would be better. Evaluate explicitly.

#### 5. Anticorruption Layer (ACL)
- **Forces**: Downstream needs to protect its model from an upstream model that is legacy, poorly designed, or conceptually misaligned.
- **Structure**: A translation layer at the downstream boundary converts upstream concepts into the downstream's ubiquitous language.
- **When to use**: Integrating with legacy systems; integrating with third-party APIs; any time upstream's model would corrupt your domain.
- **Consequences**: Additional code to write and maintain; decouples your model from upstream changes.
- **Implementation**: Typically an interface + adapter; the adapter calls the upstream, maps the response to your domain objects.

#### 6. Open-Host Service (OHS)
- **Forces**: Multiple downstream contexts need to integrate with your bounded context.
- **Structure**: Upstream publishes a well-defined, versioned integration API (REST, gRPC, events) rather than exposing its internal model.
- **When to use**: High-traffic upstream systems; public APIs; platform teams.
- **Consequences**: Upstream team owns API versioning and deprecation. Reduces coupling.
- **Often paired with Published Language**.

#### 7. Published Language
- **Forces**: Multiple systems need to exchange data in a shared, well-understood format.
- **Structure**: An explicit, documented data exchange format (JSON schema, Avro, Protobuf, XML Schema) used as the integration medium.
- **When to use**: Event-driven integration; public APIs; industry standards (HL7, EDIFACT).
- **Often paired with OHS**.

#### 8. Separate Ways
- **Forces**: Integration between two contexts provides little value relative to the cost.
- **Structure**: No integration. Each context solves its needs independently, possibly duplicating functionality.
- **When to use**: When the communication overhead, organizational friction, or technical complexity of integration outweighs the benefits.
- **Consequences**: Duplication but also complete autonomy.
- **Gotcha**: Consider this option explicitly — teams often assume integration is required when it isn't.

### Context Map as Organizational Tool
The context map reveals:
- **Power dynamics**: Who is upstream? Who must conform?
- **Team coupling**: Shared kernel and partnership patterns imply tight team coordination.
- **Risk areas**: Conformist and shared kernel relationships are fragile.
- **Migration targets**: ACLs can be temporary — added to protect during migration, removed when the upstream is replaced.

### Team Topology Implications
- **Partnership** → requires joint planning; stream-aligned teams that coordinate.
- **Shared Kernel** → requires a joint team ownership model or a dedicated platform team.
- **Customer-Supplier** → upstream team owns a platform; downstream teams are consumers.
- **Conformist / ACL** → downstream team is autonomous; upstream is an external dependency.
- **OHS + Published Language** → upstream acts as a platform; enables self-service integration.

**Practical advice**: Draw the context map before designing microservice boundaries. The context map is the strategic view; microservice decomposition follows from it.
