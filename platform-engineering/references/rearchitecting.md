# Rearchitecting Platforms

Rearchitecting a platform is one of the highest-risk, highest-reward undertakings a platform engineering team can pursue. It demands clear reasoning about why the current system is insufficient, disciplined execution to avoid the many pitfalls that derail large technical efforts, and constant communication with the stakeholders who depend on the platform. This reference covers the principles, patterns, and practices for rearchitecting platform systems effectively, drawing on the themes from Chapter 8 of Camille Fournier's *Platform Engineering*.

## When Rearchitecting Is Necessary

Not every frustration with the current system justifies a rearchitecture. Genuine triggers tend to fall into a few categories:

**Scaling limits.** The system has hit a ceiling that cannot be overcome with incremental optimization. This might be throughput limits in a message bus, storage bottlenecks in a database, or deployment pipeline latency that grows superlinearly with team size. The key indicator is that you have already tried tuning the existing system and the returns are diminishing or nonexistent.

**Accumulated technical debt.** Over time, workarounds and quick fixes accumulate until the system becomes brittle and difficult to change. When the cost of every new feature or bug fix is dominated by navigating around old decisions, the debt has become structural. At this point, paying it down incrementally may be more expensive than replacing the foundation.

**Changing requirements.** The platform was designed for a set of assumptions that no longer hold. Perhaps the organization shifted from a monolithic deployment model to microservices, or from on-premises infrastructure to cloud-native. When the gap between what the system was designed for and what it needs to do becomes too wide, adaptation within the existing architecture ceases to be viable.

**Vendor lock-in.** Dependencies on a specific vendor's proprietary APIs, data formats, or runtime environments can become liabilities when pricing changes, the vendor's roadmap diverges from your needs, or organizational policy mandates portability. Rearchitecting to introduce abstraction layers or migrate to open standards may be the only path to regaining control.

## When NOT to Rearchitect

The urge to rebuild is strong in engineering culture, and many rearchitecture efforts are launched for the wrong reasons.

**Shiny object syndrome.** A new technology appears and the team wants to adopt it, not because it solves a concrete problem, but because it is interesting. Kubernetes, serverless, the latest database engine -- these are tools, not goals. The question is always whether the new technology addresses a specific, measurable deficiency in the current system.

**Resume-driven development.** Engineers sometimes push for rearchitecture because working on a greenfield system is more personally rewarding than maintaining an existing one. This motivation produces systems that are optimized for the builder's learning rather than the organization's needs.

**Underestimating migration cost.** Teams routinely underestimate the cost of migration by a factor of two to ten. Building the new system is often the easier half. Migrating data, retraining users, updating documentation, achieving feature parity, and decommissioning the old system consume enormous effort. If the analysis does not account for migration cost, the business case for rearchitecture is incomplete.

**The system works but is aesthetically displeasing.** Code that is ugly, poorly structured, or written in an unfashionable language is not, by itself, a reason to rearchitect. If the system meets its performance, reliability, and extensibility requirements, the right response is targeted refactoring, not a ground-up rewrite.

A useful heuristic: if you cannot articulate the specific, measurable problem the rearchitecture solves, and the specific, measurable outcome it produces, you are not ready to start.

## Incremental vs. Big-Bang Rearchitecture

Almost always prefer incremental rearchitecture. The big-bang approach -- stop the world, build the new system, switch over on a target date -- fails for predictable reasons:

- The new system must achieve full feature parity before it can replace the old one, which means the old system's quirks and edge cases must be understood completely. This understanding rarely exists at the start.
- The organization continues to evolve its requirements while the new system is being built, creating a moving target.
- A single cutover event concentrates risk into a narrow window, with limited opportunity for learning and correction.
- Teams lose motivation during long build phases with no production validation.

Incremental rearchitecture, by contrast, delivers value continuously, surfaces problems early, and allows the team to adjust course based on real production experience.

The exception to this rule is when the old and new systems are so fundamentally different that no incremental path exists. Even then, the migration itself should be incremental -- move users, workloads, or data in stages rather than all at once.

## The Strangler Fig Pattern

The strangler fig pattern, named after the tropical plant that grows around a host tree and eventually replaces it, is the most important architectural pattern for incremental rearchitecture of platform systems.

The approach works as follows:

1. **Identify a boundary.** Find a seam in the existing system where traffic or data can be intercepted. This might be an API gateway, a load balancer, a message queue, or a database access layer.
2. **Build the new implementation for a subset of functionality.** Rather than replacing everything at once, pick one capability or one category of requests.
3. **Route selectively.** Direct some traffic to the new implementation while the rest continues to flow through the old system. The routing layer becomes the control point for the migration.
4. **Validate and expand.** Once the new implementation proves itself for the initial subset, expand its scope. Repeat until the old system handles no traffic.
5. **Decommission.** Remove the old system only after the new one has fully replaced it and a soak period has passed.

For platform systems, the strangler fig pattern often manifests as a facade or proxy layer that presents a unified interface to consumers while internally delegating to either the old or new backend. This facade is not merely a routing layer -- it is an explicit architectural component that must be designed, tested, and maintained.

## Building the New System Alongside the Old

Running two systems simultaneously is operationally expensive but strategically necessary. Several practices make this manageable:

**Compatibility layers.** Build adapters that translate between the old system's interfaces and the new system's interfaces. This allows consumers to migrate at their own pace rather than requiring a coordinated cutover.

**Shared data stores with care.** If both systems need access to the same data, decide whether the old system or the new system is the source of truth at any given time. Dual-write strategies (writing to both systems) introduce consistency risks and should be treated as temporary scaffolding, not permanent architecture.

**Feature flags for routing.** Use feature flags or configuration to control which system handles which workloads. This gives operators fine-grained control over the migration pace and the ability to revert quickly.

**Operational parity.** The new system must be observable from day one. It needs logging, metrics, alerting, and dashboards that are at least as good as what the old system provides. Teams that defer observability until after migration find themselves operating a production system blind.

## Abstraction Boundaries

Well-designed abstraction boundaries are what make rearchitecture possible without disrupting consumers. The principle is straightforward: if consumers depend on a stable interface rather than a specific implementation, you can swap the implementation behind that interface.

**Design interfaces around capabilities, not implementations.** An interface that exposes "store this object and retrieve it by key" is more durable than one that exposes "execute this SQL query." The former lets you migrate from one storage engine to another; the latter binds consumers to a specific technology.

**Use the rearchitecture as an opportunity to improve interfaces.** If the old system's interfaces are poorly designed, the rearchitecture is a chance to fix them. But be cautious about changing interfaces and implementations simultaneously -- it doubles the risk. Prefer introducing the new interface first (backed by the old implementation), then swapping the implementation.

**Document the contract explicitly.** The interface between the platform and its consumers should be defined in a machine-readable format (OpenAPI specs, protobuf definitions, JSON schemas) and validated automatically. This makes it possible to verify that the new implementation honors the contract.

**Beware of Hyrum's Law.** Regardless of what the documented interface says, consumers will depend on observable behavior. If the old system happened to return results in a particular order, some consumer has come to rely on that order. Comprehensive integration testing and shadow traffic analysis help surface these implicit contracts.

## Managing Risk During Rearchitecture

Rearchitecture is inherently risky. The following practices contain that risk:

**Rollback plans.** Every stage of the migration should have a defined rollback procedure. If the new system begins to fail, it must be possible to revert to the old system quickly. This means the old system must remain operational and its data must remain current until the migration is complete.

**Feature parity tracking.** Maintain an explicit, shared list of every capability the old system provides. Track which capabilities have been implemented in the new system, which have been validated in production, and which are intentionally being dropped. Gaps in feature parity are the most common source of migration surprises.

**Performance benchmarking.** Establish performance baselines for the old system before beginning the rearchitecture. Measure the new system against those baselines continuously. Performance regressions are easy to introduce and hard to detect without explicit benchmarking.

**Canary deployments.** Migrate a small percentage of traffic or a small number of users first. Monitor aggressively. Expand only when the canary population has been stable for a defined period.

**Blast radius limitation.** Structure the migration so that failures affect the smallest possible scope. If you are migrating a database, migrate one table or one service's data at a time rather than everything simultaneously.

## The Role of Testing in Rearchitecture

Testing during rearchitecture goes beyond standard software testing practices:

**Dual-write verification.** When both systems are running simultaneously, write to both and compare results. Discrepancies indicate bugs in the new implementation or undocumented behavior in the old one. Dual-write verification should be automated and run continuously.

**Shadow traffic.** Replay production traffic against the new system without serving its responses to users. Compare the new system's responses to the old system's responses. This is particularly valuable for read-heavy systems where correctness can be verified by comparison.

**Integration testing across the boundary.** The compatibility layer between old and new systems is a critical failure point. Integration tests should exercise this layer specifically, covering both the happy path and edge cases.

**Load testing.** The new system must be load-tested under realistic conditions before it takes production traffic. "Realistic" means using production-like data volumes, traffic patterns, and concurrency levels -- not synthetic benchmarks.

**Data migration validation.** When data is migrated from the old system to the new one, validate completeness and correctness systematically. Row counts, checksums, and sampling-based comparison are minimum requirements. For critical data, consider full comparison.

## Technical Decision-Making

Rearchitecture involves many consequential technical decisions. Structured decision-making processes reduce the risk of poor choices:

**Requests for Comments (RFCs).** Before committing to an approach, write a document that describes the problem, proposes a solution, considers alternatives, and identifies risks. Circulate it broadly. The act of writing forces clarity, and review by others surfaces blind spots.

**Architecture Decision Records (ADRs).** Record significant decisions in a lightweight, structured format: context, decision, consequences. ADRs serve as institutional memory -- when someone asks "why did we choose this approach?" six months later, the answer is documented. ADRs should be stored alongside the code they describe, versioned in the same repository.

**Design reviews.** For critical components, conduct design reviews with engineers outside the immediate team. External reviewers bring fresh perspectives and are less likely to share the team's assumptions. Design reviews are most valuable early, when the cost of changing direction is low.

**Proof of concept before commitment.** For high-uncertainty decisions, build a time-boxed proof of concept. Define success criteria before starting. A two-week prototype that validates (or invalidates) a key assumption is far cheaper than discovering the problem six months into implementation.

## Communicating Rearchitecture Plans to Stakeholders

Platform rearchitecture affects everyone who depends on the platform. Stakeholder communication must address three questions:

**Why it matters.** Translate technical problems into business impact. "The build system takes 45 minutes" is a technical fact. "Engineers spend 20% of their time waiting for builds, which costs the organization $X per quarter in lost productivity" is a business argument. Stakeholders need to understand the cost of inaction.

**What it costs.** Be honest about the investment required, including engineering time, operational overhead during the transition, and potential disruption to consumers. Underestimating costs to get approval erodes trust when the true costs emerge later.

**What is the timeline.** Provide a phased timeline with milestones that stakeholders can track. Each milestone should deliver measurable value. Avoid timelines that show no visible progress for months -- if the first visible outcome is nine months away, stakeholders will lose confidence. Structure the work so that early milestones demonstrate momentum.

**What consumers need to do.** If the rearchitecture requires consumer teams to make changes (adopt a new API, migrate to a new deployment process), communicate this early and provide support. Migration guides, office hours, and dedicated support channels reduce friction and resentment.

## Common Pitfalls

**The second system effect.** Fred Brooks identified this decades ago: the second system a team builds tends to be over-engineered because the team tries to address every shortcoming of the first system simultaneously. The result is a system that is more complex than necessary and takes longer to build than planned. Resist the temptation to solve every problem at once.

**Scope creep.** Rearchitecture projects attract requirements like magnets. Every stakeholder sees the rearchitecture as an opportunity to get their pet feature included. Without disciplined scope management, the project grows until it collapses under its own weight. Define the scope explicitly at the outset and require a formal process for additions.

**Losing momentum.** Long-running rearchitecture projects are vulnerable to attrition -- key engineers leave, organizational priorities shift, or the team simply gets tired. Counteract this by delivering value incrementally, celebrating milestones, and keeping the team small and focused.

**Forgetting about the old system.** Once the team is excited about the new system, maintenance of the old system suffers. But the old system is still running in production and serving users. Bugs still need to be fixed. Security patches still need to be applied. Allocate explicit capacity for old-system maintenance throughout the migration.

**Premature decommissioning.** The urge to turn off the old system is strong, but doing so before the migration is truly complete leads to outages and data loss. Define clear criteria for decommissioning and verify them rigorously.

**Insufficient testing of the migration path.** Teams test the new system thoroughly but neglect to test the migration itself -- the data conversion scripts, the traffic routing changes, the rollback procedures. The migration path is code and deserves the same testing rigor as any other code.

## Case Study Patterns

### Database Migrations

Database migrations are among the most challenging rearchitecture efforts because data is stateful, consistency matters, and downtime is usually unacceptable.

A typical pattern involves introducing a data access layer that abstracts the underlying storage engine. Consumers interact with this layer rather than with the database directly. The layer initially delegates to the old database. A dual-write phase follows, where writes go to both databases and reads are compared. Once the new database is verified, reads shift to it. Finally, writes to the old database stop and it is decommissioned.

Critical considerations include schema translation (the new database may have a different data model), consistency during the dual-write phase (what happens if a write to one database succeeds and the other fails), and backfill (migrating historical data that predates the dual-write phase).

### Build System Replacements

Build systems are deeply integrated into developer workflows, making migration particularly disruptive. The strangler fig approach works well here: migrate one project or one team at a time. Maintain the ability to build with either system during the transition.

Key challenges include reproducing hermetic builds (the new system must produce identical artifacts), handling custom build rules that accumulated over years, and maintaining acceptable build times throughout the migration. Developer experience matters enormously -- if the new build system is slower or harder to use during the transition, adoption will stall.

### Compute Platform Upgrades

Migrating from one compute platform to another (for example, from VMs to containers, or from one orchestration system to another) requires careful attention to the full lifecycle: deployment, scaling, networking, service discovery, logging, and monitoring.

The pattern typically involves running both platforms simultaneously and migrating services one at a time. A service mesh or load balancer provides the routing layer. Each migrated service goes through a validation phase where it runs on the new platform but can be rolled back to the old one.

The most common failure mode is underestimating the "long tail" of services that depend on platform-specific behavior -- hardcoded IP addresses, filesystem assumptions, kernel version dependencies, or timing-sensitive operations that behave differently on the new platform.

## Summary

Rearchitecting a platform is a project management challenge as much as a technical one. The technical work -- designing the new system, building the migration path, validating correctness -- is necessary but not sufficient. Success requires honest assessment of whether rearchitecture is truly warranted, disciplined scope management, structured decision-making, continuous communication with stakeholders, and relentless attention to the operational reality of running two systems simultaneously. The strangler fig pattern, incremental migration, and strong abstraction boundaries are the foundational techniques. The greatest risks are not technical but organizational: losing momentum, underestimating cost, and forgetting that the old system still matters until the day it is finally turned off.
