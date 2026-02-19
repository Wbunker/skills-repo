---
name: platform-engineering
description: >
  Expert-level platform engineering guidance covering strategy, team building,
  operations, product management, and organizational leadership for internal
  developer platforms. Use when the user is working on platform engineering
  strategy, internal developer platforms (IDPs), developer experience (DevEx),
  platform-as-a-product, self-service infrastructure, golden paths, platform
  team organization, infrastructure abstraction layers, migrations, sunsetting
  legacy systems, stakeholder management, or any topic related to building and
  operating shared engineering platforms. Also triggers on discussions of
  platform reliability, SLOs for internal platforms, build systems, CI/CD
  platforms, compute platforms, data platforms, developer tooling, platform
  adoption, paved roads, internal customers, tech debt reduction, or
  organizational scaling challenges for engineering infrastructure.
---

# Platform Engineering Expert

## Core Concept

Platform engineering is the discipline of **designing, building, and operating shared technical platforms** that enable product engineering teams to deliver software faster, more reliably, and more efficiently. It treats infrastructure and developer tooling as an internal product with real customers.

## The Four Pillars

Every mature platform organization excels across four dimensions:

```
┌─────────────────────────────────────────────────────────┐
│                  Platform Engineering                     │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │   PRODUCT    │  │ DEVELOPMENT │  │     BREADTH     │ │
│  │             │  │             │  │                 │ │
│  │ Customer    │  │ Building &  │  │ Scaling across  │ │
│  │ focus,      │  │ evolving    │  │ the org,        │ │
│  │ roadmaps,   │  │ platform    │  │ migrations,     │ │
│  │ metrics     │  │ systems     │  │ adoption        │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
│                                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                  OPERATIONS                          │ │
│  │  Reliability, on-call, incident response, trust     │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Product** — Understand customers, measure value, prioritize ruthlessly
**Development** — Build, iterate, and evolve the platform's technical systems
**Breadth** — Drive adoption, manage migrations, support the whole organization
**Operations** — Ensure reliability, build trust through operational excellence

## Platform vs. Product Engineering

| Dimension | Product Engineering | Platform Engineering |
|-----------|-------------------|---------------------|
| Customer | External end users | Internal developers/teams |
| Feedback loop | Usage metrics, revenue | Adoption rates, developer surveys |
| Release cadence | Feature-driven | Stability + capability driven |
| Success metric | User growth, revenue | Developer velocity, reliability |
| Migration burden | Users adopt voluntarily | Must actively migrate internal users |
| Switching cost | Users can leave | Teams are often captive audiences |

## Key Principles

1. **Platform as a product** — Your platform has customers (developers). Understand their needs, measure satisfaction, build roadmaps.
2. **Golden paths, not golden cages** — Provide well-paved default paths but don't unnecessarily constrain teams. Make the right thing the easy thing.
3. **Self-service first** — Reduce the need for tickets and human intervention. Automate provisioning, configuration, and common operations.
4. **Manage complexity** — Curate and limit technology choices. Every additional option is a maintenance burden. Fewer, better-supported paths beat unlimited choice.
5. **Earn trust through operations** — Reliability is the foundation. Teams won't adopt a platform they can't trust.
6. **Migrations are first-class work** — Building a new system is only half the job. Migrating users off the old system is equally important and often harder.
7. **Measure what matters** — Track adoption, developer satisfaction, time-to-productivity, incident rates, and migration progress.

## Common Platform Domains

| Domain | Examples | Typical Responsibilities |
|--------|----------|------------------------|
| **Compute** | Kubernetes, serverless, VMs | Container orchestration, autoscaling, resource management |
| **CI/CD** | Build systems, deployment pipelines | Build infrastructure, deployment automation, release tooling |
| **Data** | Data pipelines, warehouses, streaming | ETL infrastructure, query engines, data governance |
| **Observability** | Monitoring, logging, tracing | Metrics collection, alerting, dashboards, log aggregation |
| **Developer tools** | IDEs, CLIs, SDKs, templates | Developer productivity, code generation, local dev environments |
| **Networking** | Service mesh, DNS, load balancers | Service discovery, traffic management, API gateways |
| **Security** | Auth, secrets, compliance | Identity management, certificate management, policy enforcement |
| **Storage** | Databases, object stores, caches | Database-as-a-service, storage provisioning, backup/restore |

## Platform Maturity Model

```
Level 1: Ad Hoc         → Shared scripts, tribal knowledge, manual processes
Level 2: Standardized   → Documented standards, some self-service, basic tooling
Level 3: Self-Service   → APIs and portals for provisioning, golden paths defined
Level 4: Optimized      → Data-driven decisions, automated migrations, proactive capacity
Level 5: Product-Led    → Full product management, developer NPS, platform marketplace
```

## Reference Documents

Load these as needed based on the specific topic:

| Topic | File | When to read |
|-------|------|-------------|
| **Why Platform Engineering** | [references/introduction.md](references/introduction.md) | History, motivation, what platform engineering is and isn't, organizational context, when it becomes essential (Ch 1) |
| **The Four Pillars** | [references/pillars.md](references/pillars.md) | Product, development, breadth, and operations pillars in depth; balancing across pillars; maturity assessment (Ch 2) |
| **Getting Started** | [references/getting-started.md](references/getting-started.md) | How and when to start a platform org, bootstrapping from scratch, common starting patterns, early wins (Ch 3) |
| **Building Teams** | [references/teams.md](references/teams.md) | Team structure, hiring, roles (SRE, infra, DevEx), team topologies, scaling teams, career ladders (Ch 4) |
| **Platform as Product** | [references/platform-as-product.md](references/platform-as-product.md) | Product management for platforms, roadmaps, customer research, metrics, prioritization, internal product culture (Ch 5) |
| **Operating Platforms** | [references/operations.md](references/operations.md) | On-call, incident response, SLOs, reliability practices, operational maturity, toil reduction, runbooks (Ch 6) |
| **Planning & Delivery** | [references/planning-delivery.md](references/planning-delivery.md) | Planning processes, delivery cadence, estimation, project management for platform teams, technical debt management (Ch 7) |
| **Rearchitecting** | [references/rearchitecting.md](references/rearchitecting.md) | When and how to rearchitect platform systems, incremental vs big-bang, managing risk, strangler fig pattern (Ch 8) |
| **Migrations & Sunsetting** | [references/migrations.md](references/migrations.md) | Migration planning, execution strategies, user communication, sunsetting old systems, handling the long tail (Ch 9) |
| **Stakeholder Relationships** | [references/stakeholders.md](references/stakeholders.md) | Managing up, cross-team relationships, executive communication, navigating organizational politics, building influence (Ch 10) |
| **Platforms Are Aligned** | [references/alignment.md](references/alignment.md) | Strategic alignment with business goals, connecting platform work to company objectives, OKRs, prioritization frameworks (Ch 11) |
| **Platforms Are Trusted** | [references/trust.md](references/trust.md) | Building operational trust, reliability culture, transparency, incident communication, SLA/SLO commitments (Ch 12) |
| **Managing Complexity** | [references/complexity.md](references/complexity.md) | Technology curation, reducing optionality, abstraction design, managing sprawl, technical governance (Ch 13) |
| **Platforms Are Loved** | [references/developer-experience.md](references/developer-experience.md) | Developer experience, documentation, onboarding, feedback loops, measuring satisfaction, building platform advocates (Ch 14) |
