# Evolutionary Architecture: Redesigning Applications to API-Driven Architectures

This reference covers principles, patterns, and decision frameworks for evolving existing systems toward API-driven architectures using incremental transformation rather than risky rewrites.

## Why Use APIs to Evolve a System

APIs create explicit, enforceable boundaries between parts of a system, enabling incremental change while the existing system continues to operate.

### Creating Useful Abstractions: Increasing Cohesion

A well-designed API groups related operations together so modifications remain localized. An Order API encapsulates all order-related operations; the internal implementation can be restructured freely as long as the contract holds. The key principle: **APIs should reflect domain concepts, not implementation structure.** `/api/orders` reflects the business domain; `/api/database/query` leaks implementation details.

### Clarifying Domain Boundaries: Promoting Loose Coupling

APIs make dependencies explicit and contractual. When service A calls service B through a versioned API, the coupling is visible and manageable. When service A directly queries service B's database, the coupling is hidden and dangerous. Signs of poor boundaries: multiple teams modifying the same codebase for unrelated features, shared database tables across domains, changes to one feature breaking unrelated features, and coupled deployments.

### Case Study Approach: Establishing Domain Boundaries

1. **List business capabilities** from a business perspective (manage accounts, process orders, handle payments)
2. **Map capabilities to code** -- which packages/modules implement each capability?
3. **Identify shared dependencies** -- where do capabilities overlap in data or infrastructure?
4. **Draw candidate boundaries** -- group highly cohesive capabilities with minimal shared dependencies
5. **Validate with team structure** -- do boundaries align with how teams are or could be organized?
6. **Define API contracts at boundaries** between each bounded area

## End State Architecture Options

### Monolith (Modular Monolith)

A single deployable unit with well-defined internal module boundaries enforced through APIs or interfaces. Right when: small-medium teams (<15 developers), simple deployment needs, domain boundaries not yet understood, latency-sensitive in-process communication needed. **Key discipline:** enforce module boundaries rigorously with internal APIs, access modifiers, and build-time checks. A modular monolith with leaky boundaries is just a monolith.

### Service-Oriented Architecture (SOA)

SOA (early 2000s) organized systems around business services with ESBs, SOAP, and WS-*. Its core insight -- explicit service contracts -- was sound, but centralized governance, heavy middleware, verbose WSDL, "smart pipes/dumb endpoints" (the inverse of what works), and reuse-as-primary-goal all failed. Modern API architectures carry the insight forward while discarding the middleware-heavy approach.

### Microservices

Independently deployable services organized around business capabilities, each owning its data, communicating through lightweight protocols. **Characteristics:** single responsibility, independent deployment/scaling, decentralized data, designed for failure, automated infrastructure. **Benefits:** independent scaling, technology heterogeneity, team autonomy, fault isolation. **Costs:** network complexity, distributed transactions, operational overhead, data consistency challenges. **When appropriate:** large organizations, multiple teams, well-understood boundaries, mature DevOps practices.

### Functions (Serverless / FaaS)

Event-triggered functions on managed runtimes (Lambda, Azure Functions, Cloud Functions). Pay-per-invocation, auto-scaling including scale-to-zero, cold start latency (50ms-seconds), execution duration limits (5-15 min). **Use for:** event processing, webhooks, scheduled tasks, bursty/unpredictable workloads. **Avoid for:** long-running processes, latency-intolerant workloads, stateful operations, steady-state high-throughput.

### Architecture Style Comparison

| Attribute | Modular Monolith | Microservices | Functions (FaaS) |
|-----------|------------------|---------------|-------------------|
| Deployment unit | Single artifact | Per-service | Per-function |
| Scaling granularity | Entire app | Per-service | Per-function |
| Data ownership | Shared database | Database per service | Typically external |
| Communication | In-process | Network (sync/async) | Event-driven |
| Operational complexity | Low | High | Medium (managed) |
| Team autonomy | Low-medium | High | High |
| Latency overhead | None | Network hops | Cold start + network |
| Technology diversity | Single stack | Polyglot possible | Runtime-constrained |
| Best for | Small-medium systems | Large complex domains | Event-driven, bursty |

## Managing the Evolutionary Process

### Determine Your Goals

Articulate the problem before decomposing. **Valid reasons:** independent deployment (teams blocked by coordinated releases), independent scaling (divergent load profiles), technology migration, team autonomy (Conway's Law friction), fault isolation. **Invalid reasons:** "microservices are modern," "our competitors did it," "we want to use Kubernetes." These are solutions, not problems.

### Using Fitness Functions

Fitness functions are automated checks that validate architectural goals, making intent executable and measurable. Run them in CI/CD pipelines.

- **Modularity:** Static analysis fails the build if a module imports another's internals (ArchUnit, NetArchTest, dependency-cruiser)
- **Coupling:** Measure synchronous runtime dependencies between services; alert if threshold exceeded
- **Deployment independence:** Track whether services deploy independently; fail if co-deployment required
- **Performance:** Automated load tests verify p99 latency stays below threshold after each change
- **Data ownership:** Schema analysis flags tables accessed by more than one service's credentials

### Decomposing a System into Modules

1. **Identify module candidates** via domain analysis (business capabilities, bounded contexts)
2. **Analyze dependencies** -- high-dependency clusters may need to remain together
3. **Extract the easiest module first** -- few inbound dependencies, clear data ownership
4. **Define the API contract before extracting** -- consumers program against the API while implementation stays in the monolith
5. **Extract incrementally** -- move code behind the API boundary, verify with tests at each step
6. **Separate data last** -- keep shared database access until the API boundary is proven stable

### Creating APIs as Seams for Extension

A "seam" is where you can alter behavior without editing existing code. Introduce an API interface within the monolith that wraps a subsystem, route all access through it, then the implementation behind it can be replaced, extracted, or rewritten without affecting consumers. This means you do not need to choose the final architecture up front -- create the seam, prove it works, then decide if the implementation stays in-process, becomes a service, or moves to serverless.

### Identifying Change Leverage Points

Focus where small changes produce disproportionate benefit:
- **Hotspots:** Components that change most frequently (use `git log --format=format: --name-only | sort | uniq -c | sort -rn`)
- **Bottlenecks:** Components limiting overall system throughput
- **Pain points:** Areas with lowest developer productivity (long builds, complex testing, merge conflicts)
- **Risk concentrators:** Components where bugs have the highest blast radius

### Continuous Delivery and Verification

Every evolutionary step must be independently deployable and reversible: comprehensive automated tests at API boundaries (contract tests, integration tests), feature flags for rollout control, canary deployments for subset verification, parallel running/dark launching (route to both implementations, compare results), and instant rollback capability. The rule: **never take a step that cannot be reversed.**

## Architectural Patterns for Evolving Systems

### Strangler Fig Pattern

A routing layer (API gateway, reverse proxy) sits in front of the legacy system. All traffic initially routes to legacy. New capabilities are implemented separately, and routing rules incrementally redirect traffic to the new system. If a migration fails, revert the route. Repeat until the legacy system handles no traffic and can be decommissioned. **Key advantage:** the legacy system is never modified; risk is contained to routing and new implementation.

```
  Clients ──> Router/Proxy ──┬──> Legacy System (shrinking)
                             └──> New Implementation (growing)
```

### Facade and Adapter Patterns

**Facade:** simplified, modern API over a complex legacy interface. **Adapter:** translates between incompatible interfaces (different data formats, protocols, conventions). Both stabilize the external contract so the internal implementation can be replaced later. Often the first step in evolutionary migration.

### API Layer Cake

New API layers on top of existing systems provide progressive enhancement without modifying the underlying system. Useful for vendor software, regulated systems, or shared infrastructure. Risk: layers accumulate over time creating latency and debugging complexity. Plan to collapse layers as legacy systems retire.

### Anti-Corruption Layer (ACL)

A translation layer preventing a legacy system's domain model from leaking into a new system. The ACL translates between bounded contexts so each maintains its own clean model. Essential when integrating with systems whose naming conventions, data structures, and business rules would distort your domain model if consumed directly.

## Identifying Pain Points and Opportunities

**Upgrade and maintenance:** Dependency hell (incompatible library versions in a monolith), framework upgrades requiring full retesting, security patches forcing full redeployment. Recurring dependency conflicts signal that extraction along API boundaries will reduce maintenance cost.

**Performance:** Problems are often concentrated in specific components. Identify bottlenecks through profiling and tracing (not intuition), extract behind an API, then scale or optimize independently. But measure first -- many problems can be solved within a monolith through caching or query optimization.

**Breaking dependencies:** Circular dependencies (break with shared API interface), hub dependencies (split along consumer lines), temporal coupling (introduce orchestration or events), data coupling (establish per-module data ownership, expose through APIs instead of shared database access).

## Domain-Driven Design and APIs

**Bounded Contexts** define scope within which a domain model is valid. Each context gets its own API. Order and Shipping contexts may both have "address" but with different models -- each API expresses its own.

**Aggregates** define consistency boundaries. The API should expose operations at the aggregate level (`POST /orders`), not sub-entity level (`POST /order-lines`), because the aggregate is the unit of consistency.

**Context Mapping** identifies relationships: Shared Kernel (small common model, use sparingly), Customer-Supplier (upstream/downstream API), Conformist (downstream adopts upstream model), Anti-Corruption Layer (downstream translates), Published Language (shared API specification).

## Conway's Law

> "Any organization that designs a system will produce a design whose structure is a copy of the organization's communication structure." -- Melvin Conway, 1967

This actively shapes architecture. Architecture and team structure must evolve together -- extracting a service without assigning team ownership creates an orphan. The **Inverse Conway Maneuver** deliberately restructures teams to match the desired architecture: want independent services, create independent teams first. Communication overhead maps to API boundaries.

## Decision Framework: When to Decompose vs. Keep Together

**Decompose when:** different scaling requirements, teams blocked by coordination/deployment coupling, component needs different tech stack, failure isolation required, components change at very different rates, regulatory isolation needed.

**Keep together when:** team is small and effective, boundaries not yet understood (premature decomposition creates distributed monoliths), insufficient operational maturity (no CI/CD, monitoring, orchestration), tightly coupled data/transactions, communication overhead would negate benefits.

**The default should be to keep things together.** Decomposition solves specific problems. If you cannot articulate the problem, you are not ready to decompose. Start with a modular monolith, define internal APIs, enforce boundaries, and extract only when concrete need emerges.
