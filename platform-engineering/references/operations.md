# Operating Platforms

Platform teams carry a distinctive operational burden: the infrastructure they run is the foundation for every other engineering team in the organization. When a product team's service goes down, that team feels the pain. When a platform goes down, everyone feels it. This asymmetry shapes every aspect of how platform teams approach operations, from on-call structures to change management to capacity planning.

## Operational Responsibilities Unique to Platform Teams

Platform operations differ from product operations in several fundamental ways. First, the blast radius of any failure is multiplied across every team that depends on the platform. A bug in your deployment pipeline does not break one service; it blocks every team from shipping. Second, platform teams must operate with a dual focus: they maintain the infrastructure itself while simultaneously supporting the teams that consume it. This means operational work includes both traditional infrastructure concerns (uptime, performance, capacity) and developer experience concerns (documentation, onboarding, debugging support).

Platform teams are also responsible for the contract between themselves and their consumers. Product teams can often make tradeoffs that affect only their own users. Platform teams must negotiate those tradeoffs across many stakeholders with competing priorities. A database team cannot simply take downtime during business hours because one team says it is fine; they must account for every consumer.

The operational surface area tends to be broad. A platform team running a compute layer might be responsible for the scheduler, networking, storage integration, secrets management, logging pipelines, and the CLI tools that developers use to interact with all of it. Each of these components has its own failure modes, its own monitoring requirements, and its own set of consumers with different expectations.

## On-Call for Platform Teams

On-call for platform teams requires careful structural thinking. The most common model is a primary/secondary rotation where the primary handles incoming pages and the secondary serves as backup and escalation. Rotation length of one week is standard, though some teams use shorter rotations for high-volume services.

Several principles guide effective platform on-call:

**Scope the rotation to what one person can reasonably handle.** If a single on-call engineer is responsible for dozens of unrelated systems, they will burn out and response quality will degrade. As the platform grows, split rotations by domain: one for the compute layer, another for the data platform, another for developer tooling.

**Establish clear escalation paths.** Not every incident can be resolved by the on-call engineer alone. Define when and how to escalate to subject-matter experts, to management, and to dependent teams. Make these paths explicit in runbooks rather than relying on tribal knowledge.

**Manage alert fatigue aggressively.** Every alert that pages someone at 3 AM must be actionable and represent a real problem that requires human intervention. Review alert volume weekly. If an alert fires frequently and the response is always the same mechanical action, that is a candidate for automation, not a reason to keep waking people up. A good target is fewer than two pages per on-call shift outside business hours.

**Compensate on-call fairly.** Platform on-call tends to be high-stress because of the blast radius problem. If your organization offers on-call compensation, ensure platform teams are not shortchanged relative to product teams. If it does not, advocate for establishing compensation.

## Incident Response

Platform incidents demand a structured response process because they typically affect multiple teams simultaneously and require coordinated communication.

### Severity Levels

Define severity levels that reflect the breadth of impact:

- **SEV1 / Critical**: Widespread outage affecting most or all consumers. Customer-facing impact is likely. All-hands response, executive notification.
- **SEV2 / Major**: Significant degradation or partial outage. Multiple teams affected but some workarounds exist. Dedicated incident commander, regular status updates.
- **SEV3 / Minor**: Limited impact, single component degraded, most consumers unaffected. Handled by on-call within normal workflow.
- **SEV4 / Low**: Cosmetic issues, minor bugs, no meaningful consumer impact. Tracked as normal work items.

### Communication During Incidents

Platform teams must communicate more broadly during incidents than product teams do. When the deployment pipeline is broken, every engineering team needs to know. Establish dedicated channels for incident communication: a status page, a Slack channel, or both. Assign a communications role during major incidents so that the people debugging the problem are not also fielding questions from thirty different teams.

Post regular updates even when there is nothing new to report. Silence during an incident breeds anxiety and shadow investigation by consuming teams, which creates noise and slows resolution.

### Postmortems and Blameless Culture

Every SEV1 and SEV2 incident should produce a written postmortem. The postmortem format should include a timeline of events, root cause analysis, impact assessment, and concrete action items with owners and due dates.

Blameless culture is not about pretending that humans do not make mistakes. It is about recognizing that if a single human error can cause a major outage, the system lacks adequate safeguards. The question is never "who made the mistake" but "why did the system allow this mistake to cause this outcome, and what can we change so it cannot happen again." Action items should focus on systemic improvements: better guardrails, improved automation, additional monitoring, clearer documentation.

Follow through on postmortem action items. A binder full of postmortems with unresolved action items is organizational debt that compounds over time.

## SLOs and SLAs for Internal Platforms

Service Level Objectives (SLOs) define the reliability targets for your platform. Service Level Agreements (SLAs) formalize those targets into commitments with consequences. Internal platforms typically operate with SLOs rather than formal SLAs, though high-maturity organizations may establish internal SLAs with defined remediation commitments.

### Defining SLOs

Choose SLO metrics that reflect what consumers actually care about. For a deployment platform, that might be deployment success rate and time-to-deploy. For a database platform, it might be query latency at the 99th percentile and availability. Avoid vanity metrics that look good on dashboards but do not capture the consumer experience.

Set targets that are ambitious but achievable. A 99.9% availability SLO means roughly 8.7 hours of allowed downtime per year. A 99.99% target means 52 minutes. Be honest about what your team can sustain given its current size and investment level. An SLO that you routinely miss is worse than no SLO at all because it trains consumers to distrust your commitments.

### Error Budgets

Error budgets are the operational consequence of SLOs. If your SLO is 99.9% availability, your error budget is 0.1% unavailability. When the error budget is healthy, the team has room to take risks: ship new features, run migrations, experiment with architectural changes. When the error budget is depleted, the team shifts focus to reliability work.

Error budgets create a shared language for discussing risk. Instead of arguing abstractly about whether to prioritize features or reliability, the team can point to concrete data. They also protect the team from unreasonable demands: if a stakeholder wants a risky change shipped immediately but the error budget is exhausted, the SLO framework provides objective grounds for pushback.

### Communicating to Stakeholders

Publish SLO dashboards where consumers can see current performance. Send regular reports (monthly or quarterly) summarizing SLO compliance, notable incidents, and planned investments. When you miss an SLO, communicate proactively about what happened and what you are doing about it.

## Toil

Toil is operational work that is manual, repetitive, automatable, and scales linearly with the size of the system or the number of consumers. It is distinct from overhead (meetings, planning) and from creative problem-solving. Toil is the work that a machine should be doing but is not yet.

### Identifying and Measuring Toil

Track where on-call engineers and the broader team spend their time. Common sources of platform toil include: manually provisioning resources for new consumers, running database migrations on behalf of other teams, manually rotating certificates, responding to access requests, and debugging consumer issues that could be self-served with better tooling.

Measure toil as a percentage of total engineering time. Google's SRE model suggests keeping toil below 50% of any individual's time, with a target of driving it much lower. If a platform engineer is spending more than half their time on repetitive operational tasks, they have no capacity for the engineering work that would reduce that toil.

### Reducing Toil

Prioritize automation for the highest-volume and most error-prone toil. Self-service is the ultimate toil reducer for platform teams: if consumers can provision their own resources, manage their own access, and debug their own issues through well-designed tools and documentation, the platform team's operational load becomes decoupled from the number of consuming teams.

Not all toil needs to be eliminated immediately. Some toil is low-frequency and low-pain; automating it may not be worth the investment. Focus on toil that is growing, that wakes people up at night, or that creates a bottleneck for consumers.

## Runbooks and Operational Documentation

Every alert should link to a runbook that describes what the alert means, how to diagnose the underlying problem, and what steps to take to resolve it. Runbooks are not optional documentation; they are operational tooling.

Effective runbooks share several characteristics. They are specific and actionable, containing exact commands to run and exact things to check rather than vague guidance. They are maintained alongside the systems they describe, updated whenever the system changes. They assume the reader is an on-call engineer who may not be an expert in this particular subsystem and may be operating under stress at an unusual hour.

Beyond alert-specific runbooks, maintain operational documentation covering: architecture overviews for each major subsystem, dependency maps showing what depends on what, common failure modes and their resolutions, and escalation contacts for external dependencies.

## Capacity Planning for Shared Infrastructure

Platform capacity planning is complicated by the fact that growth is driven by consumer behavior that the platform team does not directly control. A product team launching a new feature might suddenly triple the load on the message queue. A machine learning team training a new model might consume all available GPU capacity.

Effective capacity planning requires both demand forecasting and demand management. On the forecasting side, track consumption trends per consumer, maintain relationships with teams planning large-scale launches, and build headroom into capacity plans. On the demand management side, implement quotas and rate limits so that no single consumer can exhaust shared resources, provide visibility into consumption so teams understand their own usage, and establish processes for requesting capacity increases.

Plan for both organic growth and step-function changes. Organic growth is relatively predictable from historical trends. Step-function changes (new teams onboarding, major product launches, acquisitions) require active communication channels with the rest of the organization.

## Change Management

Platform changes carry outsize risk because of the multiplied blast radius. A change management discipline that might be excessive for a product team is often appropriate for a platform team.

**Progressive rollouts** are essential. Never deploy a platform change to all consumers simultaneously. Use canary deployments to expose the change to a small subset of traffic first, then gradually increase. For changes that affect developer workflows (CLI updates, API changes), consider opt-in beta periods where willing consumers can test before the change becomes the default.

**Feature flags** allow decoupling deployment from activation. Deploy the new code path behind a flag, activate it for a subset of consumers, monitor for problems, and roll back instantly if issues arise. This is particularly valuable for platform changes where rollback of the deployment itself might be difficult.

**Communication is part of change management.** Consumers need to know what is changing, when, and what they need to do (if anything). Maintain a changelog. Send advance notice for breaking changes. Provide migration guides and tooling when APIs change.

**Establish change freeze policies** for high-risk periods: end of quarter, major product launches, holiday seasons. Define what constitutes an emergency change that can bypass the freeze and who can approve it.

## Operational Reviews

Conduct regular operational reviews (weekly or biweekly) where the team examines platform health holistically. These reviews should cover:

- SLO compliance trends: are you meeting your targets, and is the trend improving or degrading?
- Incident review: what happened since the last review, are there patterns, are postmortem action items being completed?
- Alert volume and quality: is alert noise increasing, are there new sources of toil?
- Capacity trends: are any resources approaching limits, are there upcoming demand changes?
- Consumer feedback: what are the most common support requests, what are teams struggling with?
- Recurring issues: problems that keep appearing suggest systemic weaknesses that need engineering investment rather than repeated manual fixes.

Operational reviews serve a dual purpose. They keep the team informed about the state of the platform, and they generate data that informs planning. If operational reviews consistently surface the same three issues, those issues belong on the roadmap.

## Balancing Operational Work and Project Work

The tension between keeping the lights on and building new things is the central operational challenge for platform teams. Too much time on operations and the platform stagnates, consumers grow frustrated with the lack of improvement, and engineers burn out on toil. Too little time on operations and reliability degrades, incidents multiply, and trust erodes.

Several strategies help manage this balance. **Dedicated operational time** reserves a fixed percentage of each sprint for operational work, typically 20-30%. **Rotation models** assign one or two engineers to an "ops rotation" each sprint, handling tickets and operational tasks while the rest of the team focuses on project work. **Toil budgets** set explicit limits on acceptable toil levels and trigger investment in automation when those limits are exceeded.

The most effective long-term strategy is to treat operational improvement as project work. Building better self-service tooling, improving automation, investing in observability: these are engineering projects that reduce the operational burden over time. Teams that treat operations and engineering as separate concerns end up with neither done well.

## Monitoring and Observability for Platforms

Platform monitoring must cover two dimensions: the health of the platform itself and the experience of the platform's consumers.

**Infrastructure metrics** capture the internal state of the platform: CPU utilization, memory pressure, disk I/O, network throughput, queue depths, replication lag. These are necessary for diagnosing problems but insufficient for understanding the consumer experience.

**Consumer-facing metrics** capture what consumers actually experience: API latency and error rates, deployment success rates and durations, provisioning time, query performance. These should be the basis for SLOs and the primary indicators on operational dashboards.

**Alerting philosophy** for platforms should be symptom-based rather than cause-based. Alert when consumers are experiencing degraded service, not when an internal metric crosses an arbitrary threshold. A CPU spike that does not affect consumer experience should not page anyone. A subtle increase in error rates that indicates a real problem should.

Invest in distributed tracing and structured logging that allows you to trace a consumer's request through the platform stack. When a team reports that "deploys are slow," you need the observability to quickly determine whether the bottleneck is in the build system, the artifact registry, the scheduler, or the rollout controller.

## Disaster Recovery and Business Continuity

Platform disaster recovery planning must account for the cascading effects of platform failure. If the platform is unavailable, what can consuming teams still do? Can they serve existing traffic even if they cannot deploy? Can they access their data even if they cannot run new queries?

**Define recovery objectives.** Recovery Time Objective (RTO) is how quickly the platform must be restored. Recovery Point Objective (RPO) is how much data loss is acceptable. These objectives should be set in consultation with consumers and aligned with business requirements.

**Test recovery procedures regularly.** Disaster recovery plans that have never been tested are fiction. Run game days or chaos engineering exercises that simulate platform failures and validate that recovery procedures work. Document what breaks and feed findings back into the recovery plan.

**Maintain operational independence for critical paths.** If your CI/CD platform depends on your configuration management platform which depends on your secrets management platform, a single failure can create a cascade that prevents you from deploying the fix. Identify these dependency chains and ensure that critical recovery paths have minimal dependencies.

## Graduating Operational Maturity

Platform teams typically progress through stages of operational maturity:

**Reactive**: The team responds to incidents as they occur. Monitoring is basic, runbooks are sparse, and operational knowledge lives primarily in people's heads. The team spends most of its time firefighting.

**Standardized**: The team has established incident response processes, on-call rotations, and basic monitoring. Runbooks exist for common scenarios. SLOs are defined though not always met. Toil is recognized as a problem even if not yet systematically addressed.

**Proactive**: The team anticipates problems before they become incidents. Capacity planning is forward-looking. Automation handles most routine operations. SLOs are consistently met and error budgets are actively managed. The team spends more time on engineering than on operations.

**Optimized**: Operational excellence is embedded in the team's culture and processes. Self-service handles the majority of consumer interactions. Operational reviews drive continuous improvement. The team's operational burden scales sublinearly with the number of consumers. New systems are designed with operability as a first-class concern.

Moving between these stages requires deliberate investment. It does not happen organically. Leadership must create space for the engineering work that improves operational maturity, even when there is pressure to ship new features. The payoff is compounding: every investment in operational maturity frees up future capacity that can be directed toward building the next thing.
