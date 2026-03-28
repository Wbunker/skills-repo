# Codebase Analysis Orchestration

## Parallelized Workflow for Building Complete Codebase Context

This workflow systematically applies all 13 analysis types from the diagram selection
guide to an unfamiliar codebase, producing a `site-context` skill that lives in
`.claude/skills/site-context/` in the target repository. Background agents are launched
in waves — parallel when independent, sequential when one analysis depends on another's output.

---

## Table of Contents

- [Output Structure: site-context Skill](#output-structure-site-context-skill)
- [Dependency Graph](#dependency-graph)
- [Wave Execution Plan](#wave-execution-plan)
- [Wave 0: Bootstrap](#wave-0-bootstrap)
- [Wave 1: Orient](#wave-1-orient)
- [Wave 2: Structure (parallel)](#wave-2-structure-parallel)
- [Wave 3: Behavior (parallel)](#wave-3-behavior-parallel)
- [Wave 4: Deep Dive (parallel)](#wave-4-deep-dive-parallel)
- [Wave 5: Synthesis](#wave-5-synthesis)
- [Agent Prompt Templates](#agent-prompt-templates)
- [Incremental Updates](#incremental-updates)

---

## Output Structure: site-context Skill

Every repository gets the same structure. Each analysis agent writes to one file.

```
.claude/skills/site-context/
├── SKILL.md                          ← Index: system overview + links to all references
└── references/
    ├── system-overview.md            ← Wave 1: tech stack, entry points, project shape
    ├── context-diagram.md            ← Wave 2: system boundary, external deps, actors
    ├── component-map.md              ← Wave 2: containers, components, layers, module structure
    ├── data-model.md                 ← Wave 2: ERD, schemas, constraints, relationships
    ├── dependency-analysis.md        ← Wave 2: module dependencies, fan-in/out, cycles, layers
    ├── use-cases.md                  ← Wave 2: actor-goal table, system capabilities
    ├── decisions.md                  ← Wave 2: inferred ADRs from code + git archaeology
    ├── key-flows.md                  ← Wave 3: sequence diagrams for primary request flows
    ├── event-catalog.md              ← Wave 3: events, producers, consumers, schemas, sagas
    ├── data-ownership.md             ← Wave 3: CRUD matrix, ownership conflicts, shared writes
    ├── state-lifecycles.md           ← Wave 3: state diagrams for key domain entities
    ├── business-rules.md             ← Wave 4: decision tables, validation rules, auth matrix
    ├── control-flow.md               ← Wave 4: flowcharts for complex functions/processes
    ├── deployment.md                 ← Wave 4: infrastructure, environments, network boundaries
    └── risk-assessment.md            ← Wave 5: integration points, stability patterns, hotspots
```

---

## Dependency Graph

```
Wave 0: Bootstrap
  └── Create site-context skill directory structure

Wave 1: Orient (SEQUENTIAL — everything depends on this)
  └── Agent: system-overview
        Reads: project root, package manifest, README, docker-compose, CI config
        Writes: system-overview.md

Wave 2: Structure (PARALLEL — all depend on Wave 1 only)
  ├── Agent: context-diagram
  │     Reads: system-overview.md + env vars, SDK imports, config files
  │     Writes: context-diagram.md
  │
  ├── Agent: component-map
  │     Reads: system-overview.md + directory tree, imports, docker-compose
  │     Writes: component-map.md
  │
  ├── Agent: data-model
  │     Reads: system-overview.md + migrations, ORM models, schema files
  │     Writes: data-model.md
  │
  ├── Agent: dependency-analysis
  │     Reads: system-overview.md + all import statements
  │     Writes: dependency-analysis.md
  │
  ├── Agent: use-cases
  │     Reads: system-overview.md + route definitions, auth config, cron jobs
  │     Writes: use-cases.md
  │
  └── Agent: decisions
        Reads: system-overview.md + git log, code patterns
        Writes: decisions.md

Wave 3: Behavior (PARALLEL — depend on Wave 2)
  ├── Agent: key-flows
  │     Reads: system-overview.md, component-map.md, use-cases.md
  │     Writes: key-flows.md
  │
  ├── Agent: event-catalog
  │     Reads: system-overview.md, component-map.md
  │     Writes: event-catalog.md
  │
  ├── Agent: data-ownership
  │     Reads: component-map.md, data-model.md
  │     Writes: data-ownership.md
  │
  └── Agent: state-lifecycles
        Reads: data-model.md, key-flows.md (if ready), use-cases.md
        Writes: state-lifecycles.md
        Note: can start with data-model.md alone; refine if key-flows.md
              becomes available before completion

Wave 4: Deep Dive (PARALLEL — depend on Wave 3)
  ├── Agent: business-rules
  │     Reads: key-flows.md, use-cases.md, data-model.md
  │     Writes: business-rules.md
  │
  ├── Agent: control-flow
  │     Reads: key-flows.md, component-map.md
  │     Writes: control-flow.md
  │
  └── Agent: deployment
        Reads: system-overview.md, component-map.md, context-diagram.md
        Writes: deployment.md

Wave 5: Synthesis (SEQUENTIAL — depends on everything)
  ├── Agent: risk-assessment
  │     Reads: ALL previous outputs
  │     Writes: risk-assessment.md
  │
  └── Agent: site-context-index
        Reads: ALL previous outputs
        Writes: SKILL.md (the index/overview)
```

---

## Wave Execution Plan

### Wave 0: Bootstrap

**Mode**: Synchronous (run before launching any agents)

Create the output directory structure:

```bash
mkdir -p .claude/skills/site-context/references
```

---

### Wave 1: Orient

**Mode**: Single agent, synchronous — all subsequent waves depend on this output.

**Agent**: `system-overview`

**Goal**: Rapidly identify what this system is, what technologies it uses, and where
the important parts live. This is the foundation every other agent reads first.

**Reads**:
- Root directory listing
- Package manifest (`package.json`, `Cargo.toml`, `go.mod`, `pyproject.toml`, `pom.xml`, etc.)
- `README.md`
- `Dockerfile`, `docker-compose.yml`, `k8s/` manifests
- `.github/workflows/`, `Jenkinsfile`, `.gitlab-ci.yml`
- `.env.example`, `config/`, `settings.py`, `application.yml`
- Existing `ARCHITECTURE.md`, `CLAUDE.md`, `docs/`

**Writes**: `references/system-overview.md`

**Output format** (from templates.md § System Overview):
```
System: [name]
Purpose: [1-2 sentences]
Stack: [language/version, framework, database, cache, message broker, infrastructure]
Shape: [monolith|microservices|monorepo|library|CLI|data-pipeline]
Entry points: [list with file paths]
Key directories: [tree with one-line purpose per dir]
Build/run commands: [exact commands]
Test commands: [exact commands]
```

**Diagrams to produce**: None — this is a text inventory. Diagrams start in Wave 2.

**Completion gate**: system-overview.md exists and contains all fields above.

---

### Wave 2: Structure (parallel)

**Mode**: 6 agents launched in parallel. All read `system-overview.md` as input.

#### Agent: `context-diagram`

**Goal**: Map system boundary — what is inside vs outside, all external dependencies,
all actors.

**Reads**: `system-overview.md` + scan codebase for:
- Environment variables containing `URL`, `HOST`, `ENDPOINT`, `KEY`, `SECRET`
- SDK/client package imports (e.g., `stripe`, `twilio`, `@aws-sdk/*`, `redis`)
- HTTP client instantiations and their base URLs
- Webhook/callback route handlers
- Auth middleware config (identity provider)
- CORS configuration (which frontends are allowed)
- Docker compose external service definitions

**Writes**: `references/context-diagram.md`

**Diagrams to produce**:

| # | Diagram | Mermaid Type | Description |
|---|---------|-------------|-------------|
| 1 | C4 Level 1 Context diagram | `C4Context` | System in center, all actors and external systems around it |
| 2 | Context flowchart (non-C4) | `flowchart` | Same content as simpler boxes-and-arrows with subgraphs |
| 3 | System Landscape diagram | `C4Context` | Only if this system is one of several in the org |

**Tables to produce**:
- External dependency inventory (dependency, category, protocol, auth, direction, SLA, failure impact)
- Categorized actor list (users, upstream, downstream, vendors, identity, platform)

---

#### Agent: `component-map`

**Goal**: Produce the static decomposition — containers, components, modules, layers,
and their relationships.

**Reads**: `system-overview.md` + scan codebase for:
- Docker compose services (container identification)
- Top-level directory structure per container
- Organizational pattern (by layer, by feature/domain, hybrid)
- Public interfaces (exported modules, index files)
- Layer patterns (Clean Architecture, MVC, Hexagonal, CQRS)

**Writes**: `references/component-map.md`

**Diagrams to produce**:

| # | Diagram | Mermaid Type | When | Description |
|---|---------|-------------|------|-------------|
| 4 | C4 Level 2 Container diagram | `C4Container` | Multi-service systems | All containers (apps, DBs, queues) with protocols |
| 5 | C4 Level 3 Component diagram | `C4Component` | Per major container | Internals of each complex container |
| 6 | Monolith component map | `flowchart TD` with subgraphs | Monoliths | Layers and modules with dependency direction |
| 7 | Module boundary + ownership diagram | `flowchart TD` with team subgraphs | If multiple teams | Components grouped by owning team |

**Tables to produce**:
- Module/container inventory (name, responsibility, technology, location, public interface)
- Layer violation inventory (if layers detected)

---

#### Agent: `data-model`

**Goal**: Document all data entities, their schemas, relationships, constraints,
and storage locations.

**Reads**: `system-overview.md` + scan codebase for:
- Database migration files
- ORM model definitions (SQLAlchemy, ActiveRecord, Prisma, TypeORM, etc.)
- Schema files (`.prisma`, `.graphql`, OpenAPI, JSON Schema, Avro, Protobuf)
- Database seed files and fixtures
- Raw SQL files

**Writes**: `references/data-model.md`

**Diagrams to produce**:

| # | Diagram | Mermaid Type | Description |
|---|---------|-------------|-------------|
| 8 | Primary ERD | `erDiagram` | All core entities with relationships and cardinality |
| 9 | ERD per bounded context | `erDiagram` | If >15 entities, split by domain (orders, users, payments) |

**Tables to produce**:
- Entity inventory (entity, table name, key fields, relationships, storage)
- Many-to-many junction tables identified
- Self-referential relationships identified
- Polymorphic/inheritance patterns (STI vs TPT) identified
- Constraints and indexes summary (per entity)

---

#### Agent: `dependency-analysis`

**Goal**: Map module-to-module dependencies, identify coupling hotspots, cycles,
and layer violations.

**Reads**: `system-overview.md` + scan codebase for:
- All import/require statements across all source files
- Package internal cross-references
- Shared utility/common module usage

**Writes**: `references/dependency-analysis.md`

**Diagrams to produce**:

| # | Diagram | Mermaid Type | Description |
|---|---------|-------------|-------------|
| 10 | Module dependency graph | `flowchart TD` | Directed graph: A → B means "A depends on B", color-coded by risk |
| 11 | Service dependency graph | `flowchart LR` | Microservices only: solid (sync) vs dashed (async) arrows |
| 12 | Layer dependency diagram | `flowchart TD` with subgraphs | Layers with red dashed arrows for violations |

**Tables to produce**:
- Dependency matrix (modules × modules, ✓ = depends on)
- Fan-in / fan-out analysis (module, fan-in, fan-out, risk assessment)
- Circular dependencies (cycle, modules, manifestation, suggested fix)
- Layer violations (from → to, file, impact, fix)
- Shared dependency stability (module, used by, stability, risk)

---

#### Agent: `use-cases`

**Goal**: Map all actors to goals — what can each type of user or system do?

**Reads**: `system-overview.md` + scan codebase for:
- Route definitions / controller files
- Auth middleware role checks (actor types)
- API key / service auth (system actors)
- Cron jobs and scheduled tasks (automated actors)
- Webhook endpoints (external system actors)
- CLI command definitions
- Queue consumers

**Writes**: `references/use-cases.md`

**Diagrams to produce**:

| # | Diagram | Mermaid Type | Description |
|---|---------|-------------|-------------|
| 13 | Use case diagram | `flowchart LR` | Actor nodes `(( ))` connected to use case boxes, grouped by domain subgraph |

**Tables to produce**:
- Actor-goal table (actor, goal, trigger, primary flow, entry point file path)
- Automated processes inventory (cron jobs, webhooks, queue consumers)
- Permission/authorization matrix (role × resource × action) — if discoverable from auth middleware

---

#### Agent: `decisions`

**Goal**: Reverse-engineer architectural decisions from code patterns and git history.

**Reads**: `system-overview.md` + scan codebase for:
- Code pattern signals (see analysis-workflow.md § 5.1 Decision Signals)
- Git history:
  - `git log --format=format: --name-only | sort | uniq -c | sort -rn | head -20` (churn)
  - `git log --oneline --grep="refactor\|migrate\|replace\|rewrite\|upgrade"` (architectural shifts)
  - `git shortlog -sn --no-merges` (ownership)
- Existing ADRs in `docs/decisions/`, `docs/adr/`, `architecture/decisions/`
- Comments containing "TODO", "HACK", "FIXME", "workaround"

**Writes**: `references/decisions.md`

**Diagrams to produce**: None — this is a text analysis. ADRs are documents, not diagrams.

**Documents to produce**:
- 5-10 inferred ADRs (using Inferred ADR template from templates.md)
- Decision map linking decisions to affected code areas
- Existing ADR index (if any found)
- Technical debt inventory (from TODO/HACK/FIXME comments)

---

### Wave 3: Behavior (parallel)

**Mode**: 4 agents launched in parallel. Depend on Wave 2 outputs.

#### Agent: `key-flows`

**Goal**: Trace 3-5 representative request flows end-to-end through the system.

**Reads**: `system-overview.md`, `component-map.md`, `use-cases.md`

**Process**:
1. From use-cases.md, select the 3-5 most important flows:
   - The simplest successful flow (health check, login)
   - The core business flow (create order, process payment, etc.)
   - A read-heavy flow (search, dashboard, report)
   - An async flow (background job, webhook processing)
   - An error/failure flow
2. For each flow, trace through the codebase:
   Entry point → middleware → handler → service → repository → DB/external
3. Document each hop with the actual file:line reference

**Writes**: `references/key-flows.md`

**Diagrams to produce**:

| # | Diagram | Mermaid Type | Description |
|---|---------|-------------|-------------|
| 14 | Sequence diagram: simplest flow | `sequenceDiagram` | Health check or login — the "hello world" |
| 15 | Sequence diagram: core business flow | `sequenceDiagram` | The primary thing the system does (create order, etc.) |
| 16 | Sequence diagram: read-heavy flow | `sequenceDiagram` | Search, dashboard, report — with joins/aggregation |
| 17 | Sequence diagram: async flow | `sequenceDiagram` | Background job, webhook, event processing |
| 18 | Sequence diagram: error flow | `sequenceDiagram` | What happens when a downstream service fails |
| 19 | Data flow diagram | `flowchart LR` | How data moves: ingress → transform → store → egress |

**Tables to produce**:
- Step-by-step table per flow (step, component, action, file:line)
- Error path table per flow (error condition, where caught, response)
- Side effects per flow (events emitted, logs written, metrics recorded)

---

#### Agent: `event-catalog`

**Goal**: Catalog all domain events — producers, consumers, schemas, and flow chains.

**Reads**: `system-overview.md`, `component-map.md`

**Process**:
1. Grep for event class/type definitions: `class.*Event`, `type.*Event`, `interface.*Event`
2. Find all publish/emit/send calls — trace to triggering action
3. Find all subscribe/on/handler registrations — trace to reaction logic
4. List all message queue topics from config (Kafka, SQS, SNS, RabbitMQ, Redis pub/sub)
5. Check for saga/orchestration patterns (state machines, step tracking tables)

**Skip if**: system-overview.md indicates no message broker, event bus, or pub/sub.
Write a stub noting "No event-driven patterns detected" instead.

**Writes**: `references/event-catalog.md`

**Diagrams to produce**:

| # | Diagram | Mermaid Type | When | Description |
|---|---------|-------------|------|-------------|
| 20 | Producer-consumer map | `flowchart LR` | Always (if events exist) | Services → topics → consumers |
| 21 | Event flow timeline | `flowchart LR` | Always (if events exist) | Chronological event chain with command/event color coding |
| 22 | Saga flow diagram | `flowchart TD` | If saga/orchestration detected | Steps with success/failure/compensation paths |

**Tables to produce**:
- Event catalog (event name, producer, topic/queue, consumers, key payload fields)
- Command-Event-Policy chain (step, type, name, triggered by, produces, handler file)
- Event schema for top 3-5 events (field, type, required, description)
- Saga compensation table (step, service, action, success event, failure event, compensation)
- Delivery guarantee notes (at-least-once, idempotency requirements)

---

#### Agent: `data-ownership`

**Goal**: Map which modules/services create, read, update, and delete which data entities.

**Reads**: `component-map.md`, `data-model.md`

**Process**:
1. From data-model.md, get the list of all data entities
2. From component-map.md, get the list of all modules/services
3. For each module × entity combination, grep for:
   - ORM create/insert operations → C
   - ORM find/select/query operations → R
   - ORM update/save operations → U
   - ORM delete/destroy operations → D
   - Raw SQL equivalents
4. Identify ownership conflicts (multiple writers to same entity)
5. Check database permissions if accessible (migration grants)

**Writes**: `references/data-ownership.md`

**Diagrams to produce**:

| # | Diagram | Mermaid Type | Description |
|---|---------|-------------|-------------|
| 23 | Data ownership diagram | `flowchart TD` | Services → owned data stores (solid = owner, dashed = reader) |

**Tables to produce**:
- CRUD matrix (module × entity, bold = owner)
- Ownership analysis (clean ownership vs shared writes vs violations)
- Column-level breakdown for shared tables (which service writes which columns)
- API-to-data mapping (endpoint × entity × CRUD operation)
- Ownership violation inventory with recommended fixes

---

#### Agent: `state-lifecycles`

**Goal**: Document state machines for key domain entities — valid states, transitions,
and terminal states.

**Reads**: `data-model.md`, `use-cases.md`, and `key-flows.md` (if available — can
start without it and refine later)

**Process**:
1. From data-model.md, find entities with `status`, `state`, or enum-typed columns
2. From the codebase, find:
   - Enum/const definitions for status values
   - Transition functions or state machine implementations
   - Validation logic that checks status before allowing operations
   - Test cases that exercise state transitions
3. For each stateful entity, build the state diagram
4. Identify terminal states, guard conditions, and invalid transitions

**Skip if**: No entities with status/state fields found.
Write a stub noting "No stateful entities detected" instead.

**Writes**: `references/state-lifecycles.md`

**Diagrams to produce**:

| # | Diagram | Mermaid Type | Description |
|---|---------|-------------|-------------|
| 24 | State diagram per stateful entity | `stateDiagram-v2` | One per entity with status/state field (e.g., Order, Job, Payment) |

Typically 2-5 state diagrams. Common candidates: orders, payments, jobs/tasks,
user accounts, subscriptions, shipments.

**Tables to produce**:
- Transition table per entity (current state × event → next state + guard condition)
- Invalid transitions documented explicitly
- Terminal states identified
- Enum/const linkage (the code type that maps to each diagram)

---

### Wave 4: Deep Dive (parallel)

**Mode**: 3 agents launched in parallel. Depend on Wave 3 outputs.

#### Agent: `business-rules`

**Goal**: Extract decision tables, validation rules, authorization matrices, and
feature flags from the codebase.

**Reads**: `key-flows.md`, `use-cases.md`, `data-model.md`

**Process**:
1. From key-flows.md, identify functions with complex branching (>3 paths)
2. Find validation middleware/functions and extract rule tables
3. Find authorization checks and build permission matrix
4. Find pricing/discount/eligibility calculations
5. Find feature flag configuration
6. For each discovered rule set, build a decision table

**Writes**: `references/business-rules.md`

**Diagrams to produce**: None — decision tables are tabular, not diagrammatic.

**Tables to produce**:

| # | Table Type | Description |
|---|-----------|-------------|
| T1 | Decision tables | Condition-action format for each complex business rule set |
| T2 | Validation rules matrix | Per entity: field, rule, error code, error message, cross-field rules |
| T3 | Permission/authorization matrix | Role × resource × action (✓/✗ with guard conditions) |
| T4 | Feature flag inventory | Flag name, state per environment, rollout %, behavior when on |

Include source file:line linkage for each rule set.

---

#### Agent: `control-flow`

**Goal**: Document complex functions with flowcharts and decision trees.

**Reads**: `key-flows.md`, `component-map.md`

**Process**:
1. From key-flows.md, identify functions flagged as complex during flow tracing
2. From the codebase, find functions with:
   - Deep nesting (>4 levels)
   - Many conditionals (>5 branches)
   - Retry/loop logic
   - Error handling with multiple catch paths
3. For each complex function, produce a flowchart showing:
   - Happy path
   - All error paths
   - Retry loops
   - Decision points with conditions

**Limit**: Document the 5-10 most complex functions. Not every function needs this.

**Writes**: `references/control-flow.md`

**Diagrams to produce**:

| # | Diagram | Mermaid Type | Description |
|---|---------|-------------|-------------|
| 25 | Flowchart per complex function | `flowchart TD` | Happy path + all error paths + retry loops |
| 26 | Decision tree per multi-condition logic | `flowchart TD` or ASCII | Series of conditions with distinct leaf outcomes |
| 27 | Activity diagram per loop/retry process | `flowchart TD` with back-edges | Batch processing, retry with backoff, polling |

Produce 5-10 of these total — only for the most complex functions discovered
during flow tracing. Include source file:line for each.

---

#### Agent: `deployment`

**Goal**: Document where the software runs, infrastructure layout, and environment
differences.

**Reads**: `system-overview.md`, `component-map.md`, `context-diagram.md`

**Process**:
1. Read infrastructure-as-code files:
   - Terraform (`.tf`), CloudFormation, Pulumi, CDK
   - Kubernetes manifests (`k8s/`, `manifests/`, `helm/`)
   - Docker compose (production variant if separate from dev)
2. Read CI/CD deployment config:
   - GitHub Actions deploy jobs
   - Deployment scripts
3. Read cloud-specific config:
   - `serverless.yml`, `sam template.yaml`
   - Cloud Run, ECS task definitions, Lambda config
4. Build deployment diagram
5. Identify environment differences (prod vs staging vs dev)

**Writes**: `references/deployment.md`

**Diagrams to produce**:

| # | Diagram | Mermaid Type | When | Description |
|---|---------|-------------|------|-------------|
| 28 | Production deployment diagram | `C4Deployment` or `flowchart TD` | Always | Infrastructure topology with network boundaries |
| 29 | Kubernetes deployment diagram | `flowchart TD` with namespace subgraphs | If K8s | Namespaces, deployments, services, ingress |
| 30 | Serverless deployment diagram | `flowchart LR` | If serverless | Functions, API gateways, managed services with config |

**Tables to produce**:
- Infrastructure inventory (component, technology, scaling config, notes)
- Network boundary map notes (VPCs, subnets, public vs private)
- Environment comparison table (prod vs staging vs dev: DB, replicas, secrets, monitoring, domain)
- Critical config values (timeouts, pool sizes, replica counts, memory limits)

---

### Wave 5: Synthesis

**Mode**: 2 agents, sequential. Depend on all previous outputs.

#### Agent: `risk-assessment`

**Goal**: Synthesize all previous analyses into an integrated risk and quality assessment.

**Reads**: ALL files in `references/`

**Writes**: `references/risk-assessment.md`

**Output includes**:

**Integration point inventory** (from context-diagram.md + key-flows.md):
- Every external dependency with failure mode, protection pattern, and monitoring

**Stability pattern audit** (from context-diagram.md + key-flows.md):
- For each integration point: timeout? circuit breaker? retry? bulkhead? fallback?

**Complexity hotspot report** (from dependency-analysis.md + git history):
- Files with highest churn × complexity
- Modules with highest fan-in AND fan-out
- Functions flagged in control-flow.md

**Data integrity risks** (from data-ownership.md + data-model.md):
- Shared writes without coordination mechanism
- Missing constraints or validation
- Inconsistency windows in async flows

**Architecture health summary**:
- Layer violations count (from dependency-analysis.md)
- Circular dependencies count
- Ownership violations count (from data-ownership.md)
- Missing stability patterns count

**Top 5 risks** (synthesized, ordered by severity):
- Each with: description, evidence, impact, recommended action

---

#### Agent: `site-context-index`

**Goal**: Generate the SKILL.md index that ties all references together.

**Reads**: ALL files in `references/`

**Writes**: `SKILL.md`

**Output format**:

```markdown
---
name: site-context
description: >
  Comprehensive analysis of the [System Name] codebase. Provides system overview,
  architecture diagrams, data model, key request flows, event catalog, dependency
  analysis, business rules, deployment topology, and risk assessment. Use when
  working on this codebase to understand how things are structured, how they
  interact, where the risks are, and where to make changes.
---

# [System Name] — Site Context

## System at a Glance

[2-3 sentence summary from system-overview.md]

**Stack**: [from system-overview.md]
**Shape**: [monolith|microservices|etc.]
**Entry points**: [top 3-5 from system-overview.md]

## Reference Index

| What You Need to Understand | Reference |
|-----------------------------|-----------|
| System boundary, external deps, actors | [context-diagram.md](references/context-diagram.md) |
| Major components, modules, layers | [component-map.md](references/component-map.md) |
| Data model, schemas, relationships | [data-model.md](references/data-model.md) |
| Module dependencies, coupling, cycles | [dependency-analysis.md](references/dependency-analysis.md) |
| User/system capabilities, permissions | [use-cases.md](references/use-cases.md) |
| Architectural decisions (inferred) | [decisions.md](references/decisions.md) |
| Primary request flows (sequence diagrams) | [key-flows.md](references/key-flows.md) |
| Domain events, producers, consumers | [event-catalog.md](references/event-catalog.md) |
| Data ownership, CRUD matrix | [data-ownership.md](references/data-ownership.md) |
| Entity lifecycles, state machines | [state-lifecycles.md](references/state-lifecycles.md) |
| Business rules, validation, auth | [business-rules.md](references/business-rules.md) |
| Complex function logic | [control-flow.md](references/control-flow.md) |
| Infrastructure, deployment, environments | [deployment.md](references/deployment.md) |
| Risk assessment, integration points, hotspots | [risk-assessment.md](references/risk-assessment.md) |

## Quick Navigation

### "I need to fix a bug in X"
→ Read: key-flows.md (trace the flow), state-lifecycles.md (check lifecycle),
  control-flow.md (check logic), business-rules.md (check rules)

### "I need to add a feature"
→ Read: component-map.md (where does it go?), key-flows.md (existing pattern),
  data-model.md (data changes), dependency-analysis.md (what else to update)

### "I need to understand the architecture"
→ Read: context-diagram.md → component-map.md → key-flows.md → decisions.md

### "I need to understand the data"
→ Read: data-model.md → data-ownership.md → state-lifecycles.md

### "Where are the risks?"
→ Read: risk-assessment.md → dependency-analysis.md → data-ownership.md
```

---

## Complete Diagram and Artifact Inventory

### All Diagrams by Wave

| # | Diagram | Agent | Wave | Type | Conditional |
|---|---------|-------|------|------|-------------|
| 1 | C4 L1 Context diagram | context-diagram | 2 | `C4Context` | Always |
| 2 | Context flowchart (non-C4) | context-diagram | 2 | `flowchart` | Always |
| 3 | System Landscape diagram | context-diagram | 2 | `C4Context` | If multi-system org |
| 4 | C4 L2 Container diagram | component-map | 2 | `C4Container` | If multi-service |
| 5 | C4 L3 Component diagram(s) | component-map | 2 | `C4Component` | Per complex container |
| 6 | Monolith component map | component-map | 2 | `flowchart TD` | If monolith |
| 7 | Module boundary + ownership | component-map | 2 | `flowchart TD` | If multiple teams |
| 8 | Primary ERD | data-model | 2 | `erDiagram` | Always |
| 9 | ERD per bounded context | data-model | 2 | `erDiagram` | If >15 entities |
| 10 | Module dependency graph | dependency-analysis | 2 | `flowchart TD` | Always |
| 11 | Service dependency graph | dependency-analysis | 2 | `flowchart LR` | If microservices |
| 12 | Layer dependency diagram | dependency-analysis | 2 | `flowchart TD` | If layers detected |
| 13 | Use case diagram | use-cases | 2 | `flowchart LR` | Always |
| 14 | Sequence: simplest flow | key-flows | 3 | `sequenceDiagram` | Always |
| 15 | Sequence: core business flow | key-flows | 3 | `sequenceDiagram` | Always |
| 16 | Sequence: read-heavy flow | key-flows | 3 | `sequenceDiagram` | Always |
| 17 | Sequence: async flow | key-flows | 3 | `sequenceDiagram` | If async patterns exist |
| 18 | Sequence: error flow | key-flows | 3 | `sequenceDiagram` | Always |
| 19 | Data flow diagram | key-flows | 3 | `flowchart LR` | Always |
| 20 | Producer-consumer map | event-catalog | 3 | `flowchart LR` | If events exist |
| 21 | Event flow timeline | event-catalog | 3 | `flowchart LR` | If events exist |
| 22 | Saga flow diagram | event-catalog | 3 | `flowchart TD` | If saga detected |
| 23 | Data ownership diagram | data-ownership | 3 | `flowchart TD` | Always |
| 24 | State diagram(s) | state-lifecycles | 3 | `stateDiagram-v2` | Per stateful entity (2-5 typical) |
| 25 | Flowchart(s) for complex functions | control-flow | 4 | `flowchart TD` | 5-10 most complex |
| 26 | Decision tree(s) | control-flow | 4 | `flowchart TD` / ASCII | Per multi-condition logic |
| 27 | Activity diagram(s) for loops/retries | control-flow | 4 | `flowchart TD` | Per retry/batch process |
| 28 | Production deployment diagram | deployment | 4 | `C4Deployment` / `flowchart` | Always |
| 29 | Kubernetes deployment diagram | deployment | 4 | `flowchart TD` | If K8s |
| 30 | Serverless deployment diagram | deployment | 4 | `flowchart LR` | If serverless |

**Guaranteed minimum**: Diagrams 1, 2, 8, 10, 13, 14, 15, 16, 18, 19, 23, 28 = **12 diagrams always produced**.

**Typical total**: 20-30 diagrams depending on system complexity.

### All Tables by Wave

| Table | Agent | Wave | Conditional |
|-------|-------|------|-------------|
| External dependency inventory | context-diagram | 2 | Always |
| Module/container inventory | component-map | 2 | Always |
| Entity inventory | data-model | 2 | Always |
| Constraints and indexes summary | data-model | 2 | Always |
| Dependency matrix | dependency-analysis | 2 | Always |
| Fan-in / fan-out analysis | dependency-analysis | 2 | Always |
| Circular dependency inventory | dependency-analysis | 2 | If cycles found |
| Actor-goal table | use-cases | 2 | Always |
| Automated processes inventory | use-cases | 2 | Always |
| Inferred ADRs (5-10) | decisions | 2 | Always |
| Technical debt inventory | decisions | 2 | If TODOs found |
| Step-by-step table per flow | key-flows | 3 | Always |
| Error path table per flow | key-flows | 3 | Always |
| Event catalog | event-catalog | 3 | If events exist |
| Command-Event-Policy chain | event-catalog | 3 | If events exist |
| Event schemas (top 3-5) | event-catalog | 3 | If events exist |
| CRUD matrix | data-ownership | 3 | Always |
| Ownership conflict analysis | data-ownership | 3 | Always |
| Transition table per stateful entity | state-lifecycles | 3 | Per stateful entity |
| Decision tables | business-rules | 4 | Per complex rule set |
| Validation rules matrix | business-rules | 4 | If validators found |
| Permission matrix | business-rules | 4 | If auth middleware found |
| Feature flag inventory | business-rules | 4 | If feature flags found |
| Infrastructure inventory | deployment | 4 | Always |
| Environment comparison table | deployment | 4 | If multiple envs |
| Integration point inventory | risk-assessment | 5 | Always |
| Stability pattern audit | risk-assessment | 5 | Always |
| Complexity hotspot report | risk-assessment | 5 | Always |
| Top 5 risks | risk-assessment | 5 | Always |

---

## Agent Prompt Templates

### Prompt Structure for Each Agent

Every agent prompt follows this pattern:

```
You are analyzing the codebase at [repo root] to produce documentation for a
site-context skill.

TASK: [specific analysis goal]

INPUT: Read these files first for context:
- .claude/skills/site-context/references/system-overview.md
- [any other Wave N-1 outputs this agent depends on]

PROCESS: [numbered steps from the wave description above]

OUTPUT: Write your analysis to:
  .claude/skills/site-context/references/[target-file].md

FORMAT RULES:
- Use Mermaid for all diagrams (```mermaid code blocks)
- Label diagram nodes with actual names from code (class names, service names, table names)
- Label arrows with operations (method calls, HTTP verbs, event names)
- Include file:line references for every code element mentioned
- Mark inferences as "inferred" — do not present speculation as fact
- If an analysis type is not applicable (e.g., no events in a non-event-driven system),
  write a stub file noting "Not applicable: [reason]" rather than omitting the file

Do NOT:
- Invent names that don't exist in the code
- Document standard framework conventions (only document deviations)
- Include code snippets longer than 10 lines (reference file:line instead)
- Speculate about future plans
```

### Launching Agents in Code

```
# Wave 0
mkdir -p .claude/skills/site-context/references

# Wave 1 (synchronous — must complete before Wave 2)
Launch agent: system-overview (foreground, wait for completion)

# Wave 2 (all 6 in parallel)
Launch agents in parallel, all in background:
  - context-diagram
  - component-map
  - data-model
  - dependency-analysis
  - use-cases
  - decisions
Wait for all 6 to complete before proceeding.

# Wave 3 (all 4 in parallel)
Launch agents in parallel, all in background:
  - key-flows
  - event-catalog
  - data-ownership
  - state-lifecycles
Wait for all 4 to complete before proceeding.

# Wave 4 (all 3 in parallel)
Launch agents in parallel, all in background:
  - business-rules
  - control-flow
  - deployment
Wait for all 3 to complete before proceeding.

# Wave 5 (sequential)
Launch agent: risk-assessment (foreground, wait for completion)
Launch agent: site-context-index (foreground, wait for completion)
```

### Total Agent Count

| Wave | Agents | Mode | Depends On |
|------|--------|------|-----------|
| 0 | 0 | mkdir | — |
| 1 | 1 | Foreground | Wave 0 |
| 2 | 6 | Background, parallel | Wave 1 |
| 3 | 4 | Background, parallel | Wave 2 |
| 4 | 3 | Background, parallel | Wave 3 |
| 5 | 2 | Foreground, sequential | Wave 4 |
| **Total** | **16 agents** | | |

---

## Incremental Updates

The site-context skill is not a one-time artifact. When the codebase changes
significantly, re-run specific agents rather than the entire workflow.

### When to Re-Run

| Change | Re-Run These Agents |
|--------|-------------------|
| New service/container added | component-map, context-diagram, dependency-analysis, deployment |
| New database table/entity | data-model, data-ownership, state-lifecycles (if stateful) |
| New external integration | context-diagram, risk-assessment |
| Major refactor | dependency-analysis, component-map, key-flows |
| New event type added | event-catalog |
| Auth model changed | use-cases (permission matrix), business-rules |
| Infrastructure change | deployment |
| Any significant change | risk-assessment (always re-run last) |
| Full refresh | Re-run all waves in order |

### Staleness Detection

Before using site-context, check staleness:

```bash
# Compare last analysis date to most recent meaningful commit
LAST_ANALYSIS=$(stat -f "%Sm" -t "%Y-%m-%d" .claude/skills/site-context/SKILL.md 2>/dev/null || echo "never")
LAST_COMMIT=$(git log -1 --format="%ai" -- ':!*.md' ':!*.txt' | cut -d' ' -f1)
echo "Last analysis: $LAST_ANALYSIS"
echo "Last code change: $LAST_COMMIT"
```

If the gap is significant (>2 weeks of active development), consider a full refresh.
