# Migrations and Sunsetting of Platforms

Migrations are the unglamorous, often painful work that separates mature platform organizations from those that accumulate unbounded technical debt. Chapter 9 of Camille Fournier's *Platform Engineering* confronts this reality directly: building a new platform is the easy part. Getting everyone off the old one is where the real work begins.

## Why Migrations Are the Hardest Part of Platform Engineering

Building a new system is a creative act with clear momentum. Migrating users off an old system is a grinding, cross-organizational coordination problem that touches every team that depends on you. Migrations are hard for several reinforcing reasons:

- **Distributed ownership.** The platform team owns the old and new systems, but the migration work is distributed across consuming teams who have their own priorities and deadlines. You are asking other people to do work that benefits you more than it benefits them, at least in the short term.
- **Invisible value.** Migrations rarely produce visible new features. Leadership often struggles to prioritize work that maintains the status quo from an end-user perspective, even when the internal benefits are substantial.
- **Combinatorial complexity.** Every consumer uses the old platform slightly differently. Edge cases, undocumented behaviors, and implicit contracts all surface during migration and must be handled individually.
- **Emotional attachment.** Teams that built workflows around the old system have legitimate comfort with it. The old system works for them. Asking them to change is asking them to accept short-term risk and disruption for long-term organizational benefit.

The fundamental tension is that the platform team bears the cost of maintaining the old system, while the consuming teams bear the cost of migrating. Resolving this tension requires organizational strategy, not just technical execution.

## Migration Planning

Successful migrations begin long before any code is written. The planning phase determines whether a migration will finish cleanly or stall at 80% completion indefinitely.

### Inventory of Users and Consumers

Before you can plan a migration, you need a complete picture of who uses the old system and how. This means:

- **Direct API consumers.** Services that call the old platform's APIs, import its libraries, or depend on its data formats. Static analysis, dependency graphs, and API gateway logs all contribute to this picture.
- **Indirect consumers.** Teams that depend on behaviors of the old system without being direct clients. A downstream service that relies on a specific error format or timing behavior is an indirect consumer that will break if the new system behaves differently.
- **Operational dependencies.** Runbooks, alerting rules, dashboards, and on-call procedures that reference the old system. These are easy to overlook and painful to discover mid-migration.
- **Data dependencies.** Anything that reads from or writes to the old system's data stores, including batch jobs, analytics pipelines, and data warehouse extracts.

### Dependency Mapping

With the inventory in hand, map the dependencies to understand ordering constraints. Some teams must migrate before others because of data flow direction or API compatibility requirements. Dependency mapping reveals the critical path through the migration and identifies which teams are blocking others.

### Risk Assessment

For each consumer, assess the migration risk along several dimensions: complexity of their integration, criticality of their service, team capacity and expertise, and the blast radius if something goes wrong. This assessment drives the sequencing of the migration. Start with lower-risk consumers to build confidence and discover problems early, then work toward the higher-risk ones with the benefit of accumulated experience.

## Migration Strategies

There is no single correct migration strategy. The right approach depends on the nature of the platform, the number of consumers, the degree of behavioral difference between old and new systems, and the organization's risk tolerance.

### Big-Bang Migration

In a big-bang migration, all consumers switch from the old system to the new system at once, typically during a maintenance window. This approach is appropriate when the number of consumers is small, the switchover can be done at an infrastructure level without requiring consumer code changes, or when the old and new systems cannot meaningfully coexist. The advantage is that you do not have to maintain two systems in parallel. The risk is that if the new system has problems, everyone is affected simultaneously. Big-bang migrations require extensive pre-migration testing and a well-rehearsed rollback plan.

### Incremental and Phased Migration

Phased migration moves consumers over in groups, typically starting with less critical or more willing teams and progressing toward the most complex or resistant consumers. Each phase provides learning that informs the next. This is the most common strategy for large platform migrations because it limits blast radius and allows the platform team to iterate on migration tooling and documentation between phases. The downside is that you must support both old and new systems for the duration of the migration, which can be months or even years.

### Parallel Run

In a parallel run, both the old and new systems receive the same traffic, and the results are compared. This is particularly valuable when correctness is critical, such as in billing systems, data pipelines, or security infrastructure. The parallel run builds confidence that the new system behaves correctly under real-world conditions before any consumer is actually switched. The cost is the engineering effort to set up traffic mirroring and result comparison, and the infrastructure cost of running both systems under full load.

### Automated Migration Tooling

For migrations that require code changes in consuming services, automated tooling can dramatically reduce the effort required from each team. This is discussed in more detail below, but the strategic point is that investing in automation changes the migration from an O(n) coordination problem to something closer to O(1) from the consumer's perspective.

## The Long Tail Problem

The single most predictable pattern in platform migrations is that the last 10% of consumers will require 90% of the effort to migrate. This happens because:

- **Easy movers go first.** Teams with simple integrations, high technical capability, and good relationships with the platform team migrate early. What remains are the complex cases, the under-resourced teams, and the reluctant adopters.
- **Edge cases accumulate.** Each remaining consumer is more likely to depend on obscure behaviors of the old system. The migration path that worked for the first 90% does not work for these consumers without additional adaptation.
- **Organizational attention fades.** Leadership declared the migration a priority when it launched. Six months later, with most teams migrated, the urgency has dissipated even though the old system is still running and still incurring maintenance cost.
- **The old system still works.** For the remaining consumers, the old system continues to function. There is no forcing function compelling them to move. The pain of staying on the old system is diffuse and long-term, while the pain of migrating is acute and immediate.

Addressing the long tail requires deliberate strategy. You must plan for it from the beginning, not treat it as a surprise when it arrives.

## Incentive Structures

People respond to incentives. If migrating is hard and staying is easy, teams will stay. Effective migration programs work both sides of this equation.

### Making It Easy to Migrate

Reduce the cost of migration for consuming teams as much as possible. This means comprehensive migration guides with specific instructions for common integration patterns, not generic documentation. It means dedicated support from the platform team during the migration window, including pairing sessions and office hours. It means automated tooling that handles the mechanical parts of the migration. Every hour you invest in making migration easier pays off across every consuming team.

### Creating Pressure to Migrate

At the same time, there must be consequences for not migrating. Effective pressure mechanisms include:

- **Deprecation timelines with firm deadlines.** Announce that the old system will lose support on a specific date. Make the deadline real by actually reducing support after it passes.
- **Feature freezes on the old system.** New capabilities are only available on the new platform. Teams that want access to new features must migrate.
- **Security and compliance requirements.** If the old system cannot meet updated security standards, compliance requirements become a natural forcing function.
- **Escalation to leadership.** When teams refuse to migrate despite reasonable timelines and support, escalate. This is not a failure; it is a necessary organizational mechanism.

### Deadlines

Deadlines deserve special attention. A migration without a deadline is a migration that never finishes. But deadlines must be credible. If you announce a deadline and then extend it without consequence, you have taught every team that deadlines are negotiable. Set deadlines you intend to keep, communicate them early, provide adequate support to meet them, and enforce them when they arrive.

## Communication During Migrations

Migrations are as much a communication challenge as a technical one. Poor communication is the most common reason migrations stall.

Establish a regular communication cadence before the migration begins. This should include an initial announcement that explains the why, not just the what. Teams are more willing to do migration work when they understand the rationale: reduced operational cost, better reliability, security improvements, new capabilities they will gain access to.

Provide clear timelines with specific milestones. "We need you to migrate by Q3" is less useful than "Complete integration testing by July 15, begin canary traffic by August 1, full cutover by August 31." Specific dates create specific plans.

Maintain dedicated communication channels for migration support: a Slack channel, regular office hours, a FAQ document that grows as questions come in. Make it easy for teams to ask questions and get fast answers. Slow support during migration erodes trust and creates resistance.

Provide training when the new system requires new skills or workflows. Do not assume that documentation alone is sufficient. Hands-on workshops, recorded walkthroughs, and worked examples all reduce the barrier to adoption.

## Automated Migration Tools

The highest-leverage investment a platform team can make in a migration is building automated tooling.

**Codemods** are programs that automatically transform source code from the old API or pattern to the new one. For well-structured migrations where the old and new APIs have a clear mapping, codemods can handle the majority of the mechanical changes. Tools like jscodeshift for JavaScript, lib2to3 for Python, or custom AST-based transformers can rewrite import statements, update function signatures, rename configuration keys, and restructure data access patterns.

**Automated pull requests** take codemods a step further by not just generating the changes but opening pull requests in consuming teams' repositories. This shifts the burden from "figure out what to change and change it" to "review and merge this PR." The difference in effort for the consuming team is enormous.

**Migration scripts** handle runtime and infrastructure changes: updating configuration in deployment manifests, migrating data between storage systems, updating DNS records, switching feature flags. These scripts should be idempotent and reversible, allowing teams to test the migration and roll back if needed.

**Validation tooling** confirms that the migration was successful. This might include integration test suites that run against the new system, traffic comparison tools that verify behavioral equivalence, or health check scripts that confirm all expected functionality works post-migration.

The key principle is that every hour the platform team spends on automation saves that hour multiplied by the number of consuming teams. For a platform with 50 consumers, a day spent building a codemod can save 50 days of manual work across the organization.

## Tracking Migration Progress

What gets measured gets managed. Migration progress must be tracked visibly and continuously.

**Dashboards** that show migration status across all consumers are essential. At a minimum, track how many consumers have completed migration, how many are in progress, and how many have not started. Color-code by risk or deadline proximity. Make the dashboard accessible to leadership, not just the platform team.

**Metrics** should capture both progress and health. Track the percentage of traffic flowing to the new system, error rates during and after migration, and latency comparisons between old and new. These metrics serve double duty: they demonstrate progress to stakeholders and they catch problems early.

**Burndown charts** show the trajectory of the migration. Are you on track to meet the deadline? Is the rate of migration accelerating as tooling improves, or decelerating as you hit the long tail? Burndown charts make stalls visible before they become crises.

Publish migration status regularly in the same channels where you communicate about the migration. When a team completes their migration, acknowledge it publicly. Visibility creates social pressure and momentum.

## Sunsetting Old Platforms

The migration is not complete until the old system is turned off. Sunsetting is the final phase, and it requires its own planning and execution.

### When to Turn Off the Old System

The old system can be decommissioned when all consumers have migrated and verified their new integrations, no traffic is flowing to the old system (verify with monitoring, not just consumer reports), data has been migrated or archived according to retention requirements, and operational dependencies like runbooks and alerts have been updated. Do not rush this. A premature shutdown that breaks a forgotten consumer is worse than running the old system for an extra week while you verify.

### Handling Holdouts

Despite deadlines and support, some teams may not migrate on time. You have several options, roughly in order of escalation: extend dedicated support with a hard final deadline, have the platform team perform the migration on the holdout team's behalf, escalate to engineering leadership for prioritization decisions, or proceed with shutdown and accept that the holdout team's integration will break. The last option sounds extreme, but it is sometimes necessary. If a team has had months of notice, dedicated support, and automated tooling, and has still not migrated, continued delay penalizes every team that did the work on time.

### Forced Migrations

In some cases, the platform team can perform the migration without the consuming team's active participation. This is feasible when the migration is primarily a configuration or infrastructure change, when the platform team has the ability to submit and merge changes in consuming repositories, or when the behavioral differences between old and new systems are minimal. Forced migrations should be communicated clearly and should include a verification period where the consuming team can report issues.

## Managing the Emotional Aspects

Migrations are not purely technical events. They are organizational changes that affect how people work, and they provoke emotional responses.

Teams that built their workflows around the old system may feel that the migration invalidates their past decisions. Engineers who were experts in the old system may feel their expertise is being devalued. Teams under deadline pressure may resent being asked to take on migration work that was not in their plans.

Acknowledge these feelings directly. Explain that the migration is not a judgment on the old system. The old system served its purpose, and the organization's needs have evolved. Where possible, involve teams in the design of the new system so they feel ownership rather than imposition. Recognize that migration is real work that deserves credit, not an afterthought to be squeezed in between feature development.

Resistance to change is normal and human. Responding to it with empathy and clear communication is more effective than responding with authority and mandates, though mandates are sometimes necessary as a last resort.

## The Cost of Not Migrating

When organizations fail to complete migrations, they accumulate compounding costs.

**Operational burden.** The platform team must maintain two systems: two sets of deployments, two on-call rotations, two sets of runbooks, two upgrade paths. This is not twice the work since the old system is presumably stable, but it is significantly more than maintaining one system.

**Security risk.** Unmaintained systems accumulate vulnerabilities. If the old platform is no longer receiving active development, security patches may be delayed or skipped entirely. A security incident in a deprecated-but-still-running system is an organizational failure with real consequences.

**Cognitive overhead.** New engineers joining the organization must understand both systems. Documentation becomes stale. Knowledge about the old system concentrates in a shrinking number of people, creating bus-factor risk.

**Opportunity cost.** Every hour spent maintaining the old system is an hour not spent improving the new one. Over time, this drag compounds. The new platform evolves slower than it should because the team cannot fully focus on it.

These costs are often invisible in the short term, which is precisely why they are so dangerous. They accumulate quietly until a security incident, a production outage caused by the unmaintained system, or an engineering capacity crisis makes them undeniable.

## Getting Leadership Support for Migration Work

Migrations compete for prioritization with feature development, and they usually lose unless the platform team makes an explicit case for leadership support.

Frame the migration in terms leadership cares about: risk reduction, engineering efficiency, cost savings, and velocity. Quantify where you can. "We spend 20% of our on-call time on incidents related to the old system" is more compelling than "the old system is technical debt." "Completing this migration will reduce our infrastructure spend by $X per month" creates a clear business case.

Be honest about the timeline and the effort required. Under-promising and over-delivering is better than the reverse, especially for migrations where optimistic estimates are almost always wrong. Present a phased plan with clear milestones so leadership can see progress incrementally rather than waiting months for a binary done/not-done outcome.

Ask for specific support: headcount allocation, leadership communication to consuming teams about prioritization, authority to set and enforce deadlines. Vague support is not useful. You need leadership to actively communicate that migration work is a priority, not just to nod when you present a plan.

## Post-Migration Cleanup

The migration is not truly complete when the last consumer has switched over. Post-migration cleanup is essential to capture the full value of the work.

**Remove old code paths.** Feature flags, compatibility shims, and dual-write logic that supported the migration period should be removed. Dead code is a source of confusion and bugs. If you do not clean it up immediately after migration, it will linger for years.

**Decommission infrastructure.** Shut down old servers, delete old databases (after confirming backups and archival), remove old DNS entries, and clean up monitoring and alerting configurations. Infrastructure that is running but unused costs money and creates security surface area.

**Update documentation.** Remove references to the old system from wikis, runbooks, onboarding materials, and architectural diagrams. New engineers should not have to learn about a system that no longer exists.

**Archive institutional knowledge.** While you are removing references to the old system, capture what you learned from the migration. What worked, what did not, what would you do differently? This knowledge is valuable for the next migration, and there will always be a next migration.

**Celebrate completion.** Migrations are long, difficult, and thankless work. When one finishes, recognize the effort publicly. Thank the consuming teams that did the migration work. Thank the platform engineers who built the tooling and provided support. Acknowledge that the organization accomplished something hard. Celebration is not just morale-building; it signals to the organization that migration work is valued, which makes the next migration easier to staff and prioritize.
