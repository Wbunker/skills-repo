# Platform as a Product

## Table of Contents
- [Why Product Thinking Matters](#why-product-thinking-matters)
- [The Platform Product Manager](#the-platform-product-manager)
- [Customer Research for Platforms](#customer-research-for-platforms)
- [Building Platform Roadmaps](#building-platform-roadmaps)
- [Prioritization Frameworks](#prioritization-frameworks)
- [Platform Metrics That Matter](#platform-metrics-that-matter)
- [Self-Service as a Product Principle](#self-service-as-a-product-principle)
- [Golden Paths and Paved Roads](#golden-paths-and-paved-roads)
- [Versioning and Backward Compatibility](#versioning-and-backward-compatibility)
- [Communication and Internal Marketing](#communication-and-internal-marketing)
- [Avoiding Build It and They Will Come](#avoiding-build-it-and-they-will-come)
- [Balancing Power Users and the Majority](#balancing-power-users-and-the-majority)
- [Feature Flags and Gradual Rollouts](#feature-flags-and-gradual-rollouts)

## Why Product Thinking Matters

Internal customers are still customers. Developers who cannot easily switch to an external alternative still resist, work around, or refuse to adopt platforms that ignore their needs. Product thinking means:

- **Empathy over assumption.** Understand how developers actually work, not how you imagine they work.
- **Outcomes over outputs.** Shipping a Kubernetes abstraction is an output. Reducing time-to-first-deploy from two days to fifteen minutes is an outcome.
- **Deliberate trade-offs.** Every feature added is a feature to maintain. Product discipline forces saying no to requests that do not serve the broader population.
- **Trust through reliability.** Developers tolerate a less feature-rich platform that works reliably over a feature-rich one that breaks.

The captive-audience dynamic makes this more important, not less. When developers cannot leave, frustration manifests as shadow IT, workarounds, complaints to leadership, and low morale. A platform team behaving like a monopoly utility eventually gets treated like one.

## The Platform Product Manager

| Dimension | Traditional PM | Platform PM |
|-----------|---------------|-------------|
| Customers | External users or buyers | Internal engineering teams |
| Revenue signal | Direct (purchases, subscriptions) | Indirect (developer velocity, fewer incidents) |
| Adoption | Voluntary | Semi-captive; mandates possible but adoption quality varies |
| Domain knowledge | Market and user behavior | Infrastructure systems and developer workflows |
| Success metric | Revenue, MAU, retention | Adoption rate, developer satisfaction, time-to-productivity |

The platform PM must be technically credible -- able to distinguish a Kubernetes namespace from a cluster, able to participate meaningfully in design discussions. Key responsibilities:

1. **Own the roadmap** -- synthesize customer research, leadership priorities, tech debt, and reliability needs.
2. **Represent the customer** -- ensure developer experience has a voice in technical design.
3. **Define success criteria** -- measurable outcomes, not just delivery milestones.
4. **Manage stakeholder expectations** -- communicate what the team will and will not do.
5. **Drive adoption** -- ensure capabilities are used, not just shipped.

Not every team has a dedicated PM. The engineering manager or a senior engineer often fills the role. The function matters more than the title, but the lack of dedicated product management becomes a bottleneck as the platform grows.

## Customer Research for Platforms

Platform teams have a major advantage: their customers are in the same Slack workspace. Use this proximity aggressively.

**Developer surveys.** Run quarterly. Keep them focused: satisfaction ratings per capability, top three pain points (open-ended), hours lost per week to platform friction, NPS ("How likely are you to recommend this to a colleague joining the company?"). Short, consistent surveys you visibly act on beat comprehensive questionnaires that vanish.

**Interviews.** Regular one-on-ones with a rotating sample across teams. Ask what they are working on, their most recent frustrating platform interaction, what they wish existed, what they would remove. Interview both enthusiastic adopters and vocal critics.

**Shadowing.** Sit with developers performing common tasks: setting up a service, debugging production, configuring a pipeline. Watch for copy-pasting from old projects, pauses to look up documentation, workarounds, and "I always forget this part" moments. Shadowing reveals friction developers have normalized.

**Support ticket analysis.** Categorize support channel interactions by volume, repeat questions (documentation or usability failures), time to resolution (missing self-service), and escalation patterns (automation opportunities). Monthly review of support data should be a standard roadmap input.

## Building Platform Roadmaps

Platform roadmaps balance four competing categories:

| Category | Description | Risk of neglect |
|----------|-------------|-----------------|
| **New capabilities** | Features unlocking new workflows | Developers route around the platform |
| **Reliability** | SLO work, performance, incident follow-ups | Eroded trust, shadow IT |
| **Migrations** | Moving users to new systems, sunsetting old | Ever-growing operational surface area |
| **Tech debt** | Internal code quality, refactoring, dependencies | Declining team velocity |

A common starting heuristic: 40% new capabilities, 20% reliability, 20% migrations, 20% tech debt. Adjust based on current state -- a platform drowning in incidents tilts toward reliability; one running three generations of systems prioritizes migrations.

**Time horizons:**
- **Now (current quarter):** Committed, scoped, owned. High delivery confidence.
- **Next (next quarter):** Planned with preliminary scope. May shift.
- **Later (2-4 quarters):** Directional themes, not commitments. Resist pressure to promise dates here.

## Prioritization Frameworks

**Impact vs. effort.** The simplest approach. High impact / low effort items go first. The challenge: platform engineers tend to underestimate effort and overestimate impact for technically interesting work.

**RICE scoring.** More structured: Reach (teams/services affected) x Impact (magnitude per developer) x Confidence (certainty) / Effort (person-weeks). For platform work, define Reach as teams or services, not individual developers -- a deployment pipeline change touching every service has enormous reach.

**Reliability vs. features.** Tilt toward reliability when SLOs are at risk, incident frequency trends upward, on-call burden is unsustainable, or trust scores decline. Tilt toward features when the platform is operationally stable with SLO margin, developer feedback names missing capabilities as the top pain point, or business initiatives are blocked. Reliability is not shipped once; roadmaps should always include some allocation even during heavy feature periods.

## Platform Metrics That Matter

### Adoption
- **Adoption rate** -- percentage of eligible services/teams using the capability
- **Active usage** -- services deploying through the platform in the last 30 days
- **Migration progress** -- percentage migrated from legacy to current

### Developer Experience
- **Time-to-first-deploy** -- time from "I want a new service" to first production deployment
- **Developer satisfaction** -- quarterly survey scores, NPS
- **Time lost to friction** -- self-reported hours per week

### Operational
- **Support ticket volume** -- demand for human-assisted support, tracked by category
- **Mean time to provision** -- how long to get a new resource (database, namespace, etc.)
- **Self-service completion rate** -- requests completed without human intervention
- **Platform-caused incidents** -- incidents where the platform was root cause

Track trends over time rather than absolute numbers. Support tickets dropping from 100 to 50 after a self-service initiative tells a clear story; 50 in isolation does not.

## Self-Service as a Product Principle

Every interaction requiring a ticket, a human, or a meeting is friction. The self-service stack:

**APIs** -- the foundation. Every capability should be available programmatically. If provisioning a database requires a platform engineer running a script, you have a service desk, not a platform.

**CLIs** -- developer-friendly API access. Good help text, tab completion, sensible defaults.

**Portals** -- serve discovery, status visibility, infrequent configuration, and onboarding workflows.

**Documentation as product** -- version-controlled, reviewed alongside code, tested (can a new developer follow the quickstart?), measured (bounce rates, failed searches), maintained (stale docs erode trust worse than no docs).

Self-service maturity progression:
```
Level 0: File a ticket, wait for a human               (days)
Level 1: Run a script a platform engineer provides      (hours)
Level 2: Use a CLI/API with documentation               (minutes)
Level 3: Click through a portal wizard                  (minutes)
Level 4: Declare intent in code, auto-provisioned       (seconds)
```

## Golden Paths and Paved Roads

A golden path is the default, well-supported way to accomplish a common task -- where tooling is integrated, docs are thorough, monitoring is pre-configured, and support is available.

**Characteristics:** Opinionated but not mandatory. End-to-end (not "use Docker" but "create from template, build with this pipeline, deploy here, monitor with these dashboards"). Continuously tested -- if the golden path breaks, it is a high-priority incident. Kept current -- golden paths that fall behind become legacy paths.

**Boundaries:** Define explicitly what is on-path (standard web services, common patterns -- 80%+ of use cases), supported off-path (specialized workloads with documented approaches), and unsupported off-path (exotic requirements teams handle themselves). Communicate what support teams will and will not receive when stepping off-path.

## Versioning and Backward Compatibility

Treat platform APIs with the same discipline as external APIs. Breaking changes impose real costs on internal customers.

**Strategies:** Semantic versioning for libraries and CLIs. API path versioning (`/v1/`, `/v2/`) with simultaneous support during migration windows. Schema versioning for configuration formats.

**Principles:**
1. Additive changes (new optional fields, endpoints, flags) are safe.
2. Removal requires deprecation with a timeline and migration guide.
3. Behavioral changes (default values, error codes, result ordering) are breaking even if signatures are unchanged.
4. Measure usage before deprecating -- "rarely used" features may be critical to teams you are unaware of.
5. Provide migration tooling (codemods, scripts, automated upgrades), not just documentation.

**Deprecation process:** Announce with timeline (minimum 1 quarter minor, 2+ major) -> add runtime warnings -> provide migration path and tooling -> track progress and follow up -> set hard removal date -> remove.

## Communication and Internal Marketing

Platforms fail not from lack of technical quality but because developers do not know about them, understand them, or trust them.

**Changelog.** Weekly or biweekly. New features, fixes, deprecation announcements, upcoming changes. Concise and scannable.

**Migration guides.** Step-by-step with estimated effort, common pitfalls, and rollback plans.

**Office hours.** Regular sessions for questions and feedback. Double as customer research. Rotate attending engineers to build team-wide empathy.

**Demos.** A 20-minute demo beats a page of documentation for initial awareness.

**Support channels.** Well-monitored, fast response times. Response time is a direct signal of how much the team cares.

Adopt a marketing mindset: name things well, celebrate adoption wins with real stories, acknowledge failures transparently (builds more trust than silence), and gather testimonials from satisfied teams.

## Avoiding Build It and They Will Come

The most common platform product failure: technically excellent systems nobody uses. This happens when the team builds what is technically interesting rather than what is needed, ships without an adoption plan, provides poor onboarding, offers no migration support, or skips communication.

Every significant initiative needs an explicit adoption plan:
1. **Target audience** -- which teams? Have you talked to them?
2. **Onboarding path** -- zero to working in under an hour?
3. **Migration plan** -- how do existing users transition?
4. **Success criteria** -- what adoption numbers, by when?
5. **Feedback loop** -- how will you collect early feedback and iterate?

Launch to early adopters first. Fix rough edges. Then expand. Slower than a big-bang launch but far more likely to succeed.

## Balancing Power Users and the Majority

**The majority (80%)** want simplicity: golden paths, minimal configuration, opinionated defaults, templates.

**Power users (20%)** want control: escape hatches, extension points, ability to override defaults.

Strategies for serving both:
- **Layered interfaces.** `platform deploy` (all defaults) and `platform deploy --config custom.yaml` (full control).
- **Progressive disclosure.** Simple options first; advanced configuration behind explicit opt-in.
- **Extension points, not forks.** Hooks and customization without forking the system.
- **Escape hatches with guardrails.** Off-path is a conscious, explicit choice with clear trade-offs.
- **Advisory boards.** Include both power users and mainstream developers to prevent power-user voice from dominating.

The critical mistake is over-indexing on power user feedback. They are louder, more articulate, and more likely to file requests. But building primarily for them creates a platform hostile to the majority. Weight feedback by population size.

## Feature Flags and Gradual Rollouts

Platform changes affect every team simultaneously. A bad deployment can break hundreds of services. Feature flags and gradual rollouts reduce blast radius.

**Flag types:** Per-team flags (specific teams opt into beta), percentage-based rollouts (gradual traffic/service exposure), kill switches (revert in seconds rather than minutes for a rollback deploy).

**Rollout stages:**
```
1. Dogfooding        -> Platform team uses it on their own services
2. Friendly beta     -> 2-3 close partner teams opt in
3. Expanded beta     -> 10-20% of teams, diverse use cases
4. General availability -> All teams, with docs and support
5. Migration enforcement -> Begin sunsetting old behavior
```

At each stage, define monitoring criteria and pause triggers: error rate thresholds, latency regressions, support ticket spikes, negative beta feedback.

For configuration-driven changes: ship behind a config option defaulting to off, enable per-team, monitor, flip the default, then deprecate and remove the old behavior. This gives teams agency in the timeline while driving toward a consistent end state.
