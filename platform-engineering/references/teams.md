# Building Great Platform Teams

## Platform Team Roles

A mature platform organization draws on several distinct roles:

**Infrastructure engineers** design, build, and maintain foundational systems: compute clusters, networking, storage, databases, and surrounding automation. They combine low-level technical depth with systems thinking about failure modes, capacity planning, and blast radius.

**Site Reliability Engineers (SREs)** apply software engineering to operations. Platform SREs own SLOs, build toil-reducing automation, lead incident response, and drive postmortem culture. Unlike product-embedded SREs, they reason about cascading failures affecting the entire organization simultaneously.

**Developer experience engineers** focus on the interface between platform and users: CLIs, SDKs, templates, developer portals, onboarding flows. The role requires infrastructure knowledge, frontend sensibility, and empathy for those who did not build the platform.

**Platform product managers** conduct user research, prioritize roadmaps, define success metrics, and communicate strategy. They navigate internal customers who cannot easily switch providers but will build shadow infrastructure if unserved.

**Technical writers** are a chronically underinvested force multiplier. Good documentation reduces support burden, accelerates onboarding, and decreases misconfigurations. Effective platform docs use progressive disclosure: tutorials, conceptual guides, and API references.

## Team Structure Patterns

### By Platform Domain

Organize around major domains: compute, CI/CD, data, observability, networking. Each team owns the full lifecycle of their domain. Builds deep expertise with clear ownership, but cross-domain user journeys fall through the cracks. Combine with explicit ownership of end-to-end developer workflows.

### By Pillar

Separate product-focused teams (roadmap features, developer experience) from operations-focused teams (reliability, on-call, incident response). Protects feature development from interrupts but risks a two-tier system where ops is less prestigious and builders lose operational feedback loops. Rotation between pillars mitigates this.

### By Customer Segment

Align teams with customer groups: mobile, backend, data science. Builds deep customer understanding but creates duplication and divergence. Best for very large organizations where platform needs genuinely differ across segments.

## Team Topologies Applied to Platforms

The Team Topologies framework (Skelton and Pais) provides vocabulary for platform interaction patterns:

**Platform team** provides self-service capabilities to stream-aligned teams. Target state: developers provision services, set up pipelines, and configure monitoring without filing tickets. Interaction mode is "X-as-a-Service."

**Enabling team** helps other teams adopt new capabilities through pairing, workshops, and temporary support. Key distinction: enabling teams work themselves out of a job with each engagement, building capability rather than dependency.

**Complicated subsystem team** owns domains requiring deep specialist knowledge: custom database engines, low-level networking, compiler toolchains. Justified by cognitive load; small, highly specialized, interacting through well-defined APIs.

## Hiring for Platform Teams

### What to Look For

- **Systems thinking**: reasoning about second-order effects, failure modes, scaling characteristics
- **Comfort with ambiguity**: defining problems, not just solving well-specified ones
- **User empathy**: understanding that product engineers want infrastructure to just work
- **Operational maturity**: natural instinct for monitoring, alerting, runbooks, graceful degradation
- **Long-term thinking**: designing for backward compatibility, maintainability, migration paths

### Differences from Product Engineering

Platform interviews should weight backward-compatible interface design, distributed systems debugging, writing software others will operate, and infrastructure fundamentals. Avoid hiring only for deep infrastructure expertise; a team of pure systems specialists will build a technically impressive platform that product engineers find impenetrable. Balance depth with developer empathy.

## Onboarding Platform Engineers

Platform onboarding is harder than product onboarding: systems are more complex, context is wider, and mistakes affect the entire organization.

- **Structured ramp-up**: low-risk to complex work over 60-90 days; no on-call in the first month
- **Architecture deep dives**: pair with seniors to walk through major systems, covering how, why, known limitations, and historical landmines
- **Shadow on-call**: observe incident response for at least one full rotation before joining the schedule
- **Milestones**: bug fix in week one, medium project in month one, feature ownership by end of quarter one
- **Documentation duty**: new engineers document what they learn, capturing fresh-eyes insights for future hires

## Career Ladders and Growth

Platform IC ladders progress along: **scope** (component to system to org-wide), **technical depth** (implementing to designing to setting direction), **operational ownership** (following runbooks to designing systems that need fewer), **customer impact** (building what is asked for to identifying unmet needs), and **mentorship** (learning to raising the team's bar).

Recognize invisible work: outages prevented through good design, complexity reduced by sunsetting systems, velocity improved through abstractions, migrations completed across dozens of teams.

Platform managers must communicate platform value to non-technical stakeholders, maintain morale when successes are things that did not happen, and prioritize when every request feels urgent.

## Scaling from Small Team to Platform Organization

### Single-Team Phase (3-8 engineers)
Everyone does everything. Generalists thrive. The main challenge is prioritization: choosing what not to do matters more than choosing what to do.

### Split Phase (2-4 teams, 8-20 engineers)
First structural decisions. The most common initial split is by domain: compute/infrastructure and developer tools/CI-CD. Split where cognitive load and on-call burden are highest. Risks: losing generalist culture too quickly, creating teams too small for healthy on-call, failing to establish clear ownership boundaries.

### Organization Phase (5+ teams, 20+ engineers)
Requires dedicated leadership (director or VP), formal planning, platform product management, and cross-team coordination. Resist creating a team for every problem; six engineers on a well-scoped domain beats two teams of three with an ambiguous boundary.

## Specialization vs. Generalization

**Favor specialization** when domains are deeply complex, teams large enough to avoid single points of failure, and errors have severe consequences. **Favor generalization** when teams are small, needs shift rapidly, or on-call must cover multiple systems.

Most organizations benefit from a **T-shaped model**: broad stack familiarity plus deep expertise in one or two areas. Periodic domain rotation builds resilience, cross-team empathy, and helps engineers discover their strengths.

## Embedding vs. Centralized Models

**Centralized**: all platform engineers in the platform org, serving via self-service and defined support channels. Consistent standards, efficient expertise use, clear career paths. Risk: distance from product reality.

**Embedded**: platform engineers sit within product teams with a dotted-line to platform org. Deep customer understanding and short feedback loops. Risk: engineers get pulled into product work, standards diverge, knowledge silos.

**When to embed**: genuinely unique platform needs, or during migrations and transitions. Keep it temporary and goal-oriented (one to three months). The best hybrid uses centralized teams as home base with short-term embedding rotations, keeping embedded engineers in platform planning, on-call, and communication channels.

## On-Call and Operational Burden

Platform systems are tier-zero: when they fail, everything fails. A healthy rotation needs five to six engineers minimum, on-call no more than every five to six weeks. If the team is too small, solve through hiring, scope reduction, or consolidating on-call across related systems.

Operational burden concentrates on senior engineers, creating a vicious cycle: constant firefighting leaves no capacity for proactive improvement. Break this with runbooks and automation so junior engineers handle more incidents, rotating toil reduction ownership, visible burden tracking, and explicit proactive-to-reactive work targets.

## Burnout and Toil

Platform teams are especially susceptible to burnout: high operational stakes, interrupt-driven work, invisible successes, perpetual feeling of being behind. Warning signs: cynicism about product teams, declining postmortem quality, resistance to new projects, growing unaddressed backlogs, senior engineers exploring external roles.

**Address toil systematically**: measure it explicitly, allocate 20-30% of capacity to reduction, celebrate automation wins visibly, refuse to accept year-old manual processes as inevitable, and build self-service solutions that eliminate entire request classes.

Leaders must actively protect teams: say no, push back on timelines, advocate for headcount, acknowledge on-call burden. Create space for creative, forward-looking work.

## Building Customer Empathy

The most common platform failure mode is building technology for its own sake. Infrastructure engineers are drawn to elegant architectures and cutting-edge technology. These instincts must be channeled toward real customer problems.

**Practices that build empathy:**
- **Regular conversations**: talk directly to product engineers monthly about workflows, frustrations, and needs
- **Dogfooding**: use your own platform to build and deploy services; maintain a sample app that exercises the full stack
- **Support rotations**: a week answering "how do I do X?" is the fastest way to find documentation gaps and UX problems
- **Satisfaction measurement**: run periodic developer experience surveys and treat results as seriously as product NPS
- **Shadowing**: watch product engineers set up services, debug issues, and deploy changes to observe real friction

Platform teams that lose customer touch build systems that are architecturally pure but practically hostile. The antidote is making empathy a core value: include user impact in design docs, require usability reviews for developer-facing interfaces, and celebrate simplification as much as optimization. A platform team's success is measured by the productivity of the engineers it serves.
