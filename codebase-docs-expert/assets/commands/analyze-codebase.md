---
name: analyze-codebase
description: >
  Run a comprehensive codebase analysis producing a site-context skill with 14
  reference files covering all 13 analysis types: context diagram, component map,
  ERD, dependency analysis, use cases, decisions, sequence diagrams, event catalog,
  CRUD matrix, state diagrams, business rules, control flow, deployment, and risk
  assessment. Launches 16 background agents across 8 steps. Use when the user says
  "analyze this codebase", "build site context", "document this repo", or
  "create site-context".
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, TaskCreate, TaskUpdate
---

# Codebase Analysis Orchestrator

Run a full codebase analysis in 8 steps, producing a `.claude/skills/site-context/`
skill and a top-level `CLAUDE.md`. Steps launch background agents in parallel where
possible, waiting for completion before the next step begins.

## Output

The final output is a **complete skill** at `.claude/skills/site-context/` with:
- `SKILL.md` — valid skill frontmatter (name, description) + reference index
- `references/` — 14 analysis files with diagrams and tables

Plus a top-level `CLAUDE.md` with essentials and `@path` imports pointing to
the site-context skill for detailed analysis.

This skill must conform to the skill-creator conventions:
- SKILL.md has YAML frontmatter with `name` and `description` fields
- The body provides a quick reference table linking to all reference files
- Reference files are standalone and can be loaded on demand

For detailed analysis procedures per agent, reference the codebase-docs-expert skill at:
`${CLAUDE_SKILL_DIR}/../references/codebase-analysis-orchestration.md`

## Model Selection Per Step

When dispatching agents via the Agent tool, set the `model` parameter:

| Step | Agents | Model | Rationale |
|------|--------|-------|-----------|
| 2 | system-overview | `sonnet` | Fast scan, low complexity |
| 3 | context, component, data-model, deps, use-cases, decisions | `sonnet` | Parallel structural analysis, cost-efficient |
| 4 | key-flows, events, data-ownership, state | `sonnet` | Behavioral tracing, moderate complexity |
| 5 | business-rules, control-flow, deployment | `sonnet` | Deep analysis of specific areas |
| 6 | risk-assessment | `opus` | Synthesis across all outputs, needs highest reasoning |
| 6 | site-context-index | `sonnet` | Assembly/formatting, low complexity |

Use `model: "sonnet"` or `model: "opus"` when calling the Agent tool.

## Agent Dispatch Rules

When dispatching each agent via the Agent tool, always set these parameters:

```
Agent(
  prompt: "<the prompt text shown in each agent section below>",
  model: "<model from the table above — sonnet for steps 2-5, opus for risk-assessment>",
  run_in_background: <true for steps 3-5, false for steps 2 and 6>,
  description: "<short 3-5 word label>"
)
```

Every agent prompt below includes the full instructions inline. The
`.claude/agents/codebase-analyzer.md` agent file provides general rules
(Mermaid format, file:line references, quality checklist) that apply to
all agents — but since custom agents cannot be invoked via `subagent_type`,
the prompts below are self-contained.

---

## Step 1: Bootstrap

Create the output directory structure and a skeleton SKILL.md so the skill is
immediately discoverable by all subsequent agents. They can read previous step
outputs via the site-context skill references.

```bash
mkdir -p .claude/skills/site-context/references
```

Then write this skeleton SKILL.md:

```markdown
---
name: site-context
description: >
  Codebase analysis in progress. This skill will contain system overview,
  architecture diagrams, data model, request flows, event catalog, dependency
  analysis, business rules, deployment topology, and risk assessment once
  analysis completes. References are populated incrementally by /analyze-codebase.
---

# Site Context (building...)

Analysis in progress. Reference files will appear in `references/` as each
analysis step completes.
```

This skeleton will be overwritten by the site-context-index agent in Step 6
with the complete index.

---

## Step 2: Orient (1 foreground agent)

Launch a single foreground agent. Everything else depends on this output.

### Agent 1: system-overview

Dispatch with the Agent tool (model: sonnet, foreground, NOT background):

```
Produce a comprehensive system overview and code layout map for this codebase.
This is the foundation document that every subsequent analysis agent reads first.

SCAN these files in order (skip if absent):
- Root directory listing (ls -la the project root, then ls each top-level dir)
- Package manifests (package.json, Cargo.toml, go.mod, pyproject.toml, pom.xml,
  Gemfile, build.gradle, *.csproj, requirements.txt, composer.json)
- Lock files (for version pinning: package-lock.json, yarn.lock, Cargo.lock, etc.)
- README.md, ARCHITECTURE.md, CLAUDE.md, AGENTS.md
- Dockerfile, docker-compose.yml, k8s/ manifests
- CI/CD config (.github/workflows/, Jenkinsfile, .gitlab-ci.yml, cloudbuild.yaml)
- Config files (.env.example, config/, settings.py, application.yml, .eslintrc, .prettierrc, tsconfig.json)
- Monorepo workspace config (lerna.json, pnpm-workspace.yaml, nx.json, turbo.json, Cargo workspace)
- Test config (jest.config, pytest.ini, vitest.config, .mocharc, phpunit.xml)
- Existing docs/ directory (list all files)

ALSO RUN these commands for scale indicators:
- Count source files by language: find . -name '*.ts' -o -name '*.py' -o -name '*.java' etc. | wc -l
- Count test files: find . -path '*/test*' -o -path '*__tests__*' -o -path '*_test.*' | wc -l
- git log --oneline | wc -l (total commits — indicates project maturity)
- git shortlog -sn --no-merges | head -10 (top contributors)

Write output to: .claude/skills/site-context/references/system-overview.md

Output format — include ALL of these sections:

# System Overview

## Identity
- System: [name]
- Purpose: [1-2 sentences — what problem does this solve and for whom]
- Repository: [repo URL if discoverable from git remote]

## Tech Stack
| Layer | Technology | Version | Notes |
|-------|-----------|---------|-------|
| Language | ... | ... | [runtime version constraints] |
| Framework | ... | ... | [web, API, CLI framework] |
| Database | ... | ... | [RDBMS, NoSQL, type] |
| Cache | ... | ... | [if present] |
| Message Broker | ... | ... | [if present] |
| Search | ... | ... | [if present — Elasticsearch, etc.] |
| Infrastructure | ... | ... | [cloud provider, IaC tool] |
| Auth | ... | ... | [auth provider, strategy] |

## Key Dependencies
| Package | Purpose | Category |
|---------|---------|----------|
| [top 10-15 non-trivial dependencies from package manifest] | [what it does] | [web, ORM, auth, queue, testing, etc.] |

## Shape
[monolith|microservices|monorepo|library|CLI|data-pipeline]

If monorepo, include workspace map:
| Package/Service | Location | Purpose | Dependencies |
|----------------|----------|---------|-------------|
| [name] | [path] | [what it does] | [which other workspace packages it depends on] |

## Scale
| Metric | Count |
|--------|-------|
| Source files | [n] |
| Test files | [n] |
| Total commits | [n] |
| Top contributors | [list top 5] |
| Languages detected | [list with approx file counts] |

## Entry Points
| Entry Point | Location | Purpose |
|-------------|----------|---------|
| [main, routes, CLI, workers, etc.] | [file path] | [what it handles] |

## Directory Structure
[Full top-level tree with one-line purpose per directory, 2 levels deep]

```
project-root/
├── src/              — [purpose]
│   ├── api/          — [purpose]
│   ├── services/     — [purpose]
│   └── ...
├── tests/            — [purpose]
├── docs/             — [purpose]
├── scripts/          — [purpose]
├── infra/            — [purpose]
└── ...
```

## Code Organization Pattern
[by-layer | by-feature | by-domain | hybrid] — describe the observed pattern:
- How are source files organized? (controllers/services/models vs users/orders/payments)
- Is there a clear separation of concerns?
- Where do shared utilities live?

## Commands
| Action | Command | Notes |
|--------|---------|-------|
| Install dependencies | [exact command] | |
| Build | [exact command] | |
| Run tests | [exact command] | |
| Run single test | [exact command] | |
| Lint / type check | [exact command] | |
| Run locally | [exact command] | |
| Run with Docker | [exact command] | [if applicable] |

## Dev Tooling
| Tool | Config File | Purpose |
|------|------------|---------|
| [linter] | [.eslintrc, ruff.toml, etc.] | [code quality] |
| [formatter] | [.prettierrc, black config, etc.] | [code formatting] |
| [type checker] | [tsconfig.json, mypy.ini, etc.] | [type safety] |
| [pre-commit] | [.pre-commit-config.yaml, husky, etc.] | [git hooks] |
| [code generator] | [if any — OpenAPI codegen, Prisma, etc.] | [generated code] |

## Test Infrastructure
- Test runner: [jest, pytest, JUnit, etc.]
- Test directory pattern: [mirrors src, flat, nested]
- Fixture/factory pattern: [if discoverable]
- Coverage tool: [if configured]
- CI test command: [from CI config]

## Existing Documentation Inventory
| Document | Location | Last Updated | Status |
|----------|----------|-------------|--------|
| [README, ARCHITECTURE, ADRs, etc.] | [path] | [from git log] | [current|stale|empty] |
```

**Wait for this agent to complete before proceeding to Step 3.**

---

## Step 3: Structure (6 parallel background agents)

All 6 agents read `system-overview.md` as input. Launch all in parallel using
`run_in_background: true`, `model: "sonnet"`.

### Agent 2: context-diagram

```
Analyze this codebase to produce a context diagram showing system boundaries and
external dependencies.

INPUT: Read the system-overview.md reference from the site-context skill
(.claude/skills/site-context/references/system-overview.md).

SCAN the codebase for:
- Environment variables containing URL, HOST, ENDPOINT, KEY, SECRET
- SDK/client package imports (stripe, twilio, @aws-sdk/*, redis, etc.)
- HTTP client instantiations and their base URLs
- Webhook/callback route handlers
- Auth middleware config (identity provider)
- CORS configuration
- Docker compose external service definitions

WRITE output to: .claude/skills/site-context/references/context-diagram.md

PRODUCE these diagrams:
1. C4 Level 1 Context diagram (Mermaid C4Context) — system in center, all actors and external systems
2. Context flowchart (Mermaid flowchart) — same content, simpler boxes-and-arrows with subgraphs

PRODUCE these tables:
- External dependency inventory (dependency, category, protocol, auth, direction, SLA estimate, failure impact)
- Categorized actor list (users, upstream systems, downstream consumers, vendor services, identity providers, platform services)
```

### Agent 3: component-map

```
Analyze this codebase to produce a component map showing containers, components,
modules, and layers.

INPUT: Read the system-overview.md reference from the site-context skill
(.claude/skills/site-context/references/system-overview.md).

SCAN the codebase for:
- Docker compose services (container identification)
- Top-level directory structure per container/service
- Organizational pattern (by layer, by feature/domain, hybrid)
- Public interfaces (exported modules, index files)
- Layer patterns (Clean Architecture, MVC, Hexagonal, CQRS)

WRITE output to: .claude/skills/site-context/references/component-map.md

PRODUCE these diagrams (as applicable):
- C4 Level 2 Container diagram (Mermaid C4Container) — if multi-service
- C4 Level 3 Component diagram per major container (Mermaid C4Component)
- Monolith component map (Mermaid flowchart TD with layer subgraphs) — if monolith
- Module boundary + ownership diagram (flowchart with team subgraphs) — if ownership discoverable

PRODUCE these tables:
- Module/container inventory (name, responsibility, technology, location, public interface)
- Layer violation inventory (if layering pattern detected)
```

### Agent 4: data-model

```
Analyze this codebase to produce an entity-relationship model of all data entities.

INPUT: Read the system-overview.md reference from the site-context skill
(.claude/skills/site-context/references/system-overview.md).

SCAN the codebase for:
- Database migration files
- ORM model definitions (SQLAlchemy, ActiveRecord, Prisma, TypeORM, Sequelize, etc.)
- Schema files (.prisma, .graphql, OpenAPI, JSON Schema, Avro, Protobuf)
- Database seed files and fixtures
- Raw SQL files

WRITE output to: .claude/skills/site-context/references/data-model.md

PRODUCE these diagrams:
- Primary ERD (Mermaid erDiagram) covering all core entities with PK/FK, types, and cardinality
- Additional ERD per bounded context if >15 entities (split by domain)

PRODUCE these tables:
- Entity inventory (entity, table name, key fields, relationships, storage location)
- Many-to-many junction tables
- Self-referential relationships
- Polymorphic/inheritance patterns (STI vs TPT)
- Constraints and indexes summary per entity
```

### Agent 5: dependency-analysis

```
Analyze this codebase to map module-to-module dependencies, coupling hotspots,
circular dependencies, and layer violations.

INPUT: Read the system-overview.md reference from the site-context skill
(.claude/skills/site-context/references/system-overview.md).

SCAN the codebase for:
- All import/require/use statements across all source files
- Package internal cross-references
- Shared utility/common module usage

WRITE output to: .claude/skills/site-context/references/dependency-analysis.md

PRODUCE these diagrams:
- Module dependency graph (Mermaid flowchart TD) — directed, color-coded by risk
- Service dependency graph (Mermaid flowchart LR) — if microservices, solid=sync, dashed=async
- Layer dependency diagram (Mermaid flowchart TD with subgraphs) — if layers detected, red dashed for violations

PRODUCE these tables:
- Dependency matrix (modules x modules, check = depends on)
- Fan-in / fan-out analysis (module, fan-in, fan-out, risk assessment)
- Circular dependency inventory (cycle, modules, manifestation, suggested fix)
- Layer violations (from, to, file, impact, fix)
- Shared dependency stability (module, used by count, change frequency, risk)
```

### Agent 6: use-cases

```
Analyze this codebase to map all actors to goals — what each type of user or
system can do.

INPUT: Read the system-overview.md reference from the site-context skill
(.claude/skills/site-context/references/system-overview.md).

SCAN the codebase for:
- Route definitions / controller files
- Auth middleware role checks (actor types)
- API key / service auth (system actors)
- Cron jobs and scheduled tasks (automated actors)
- Webhook endpoints (external system actors)
- CLI command definitions
- Queue consumers

WRITE output to: .claude/skills/site-context/references/use-cases.md

PRODUCE these diagrams:
- Use case diagram (Mermaid flowchart LR) — actor nodes (( )) connected to use case boxes, grouped by domain subgraph

PRODUCE these tables:
- Actor-goal table (actor, goal, trigger, primary flow, entry point file path)
- Automated processes inventory (cron jobs, webhooks, queue consumers with schedule/trigger)
- Permission/authorization matrix (role x resource x action) — if discoverable from auth middleware
```

### Agent 7: decisions

```
Reverse-engineer architectural decisions from code patterns and git history.

INPUT: Read the system-overview.md reference from the site-context skill
(.claude/skills/site-context/references/system-overview.md).

SCAN the codebase for:
- Decision signals: custom abstractions wrapping libraries, feature flags, multiple
  interface implementations, middleware chains, event-driven communication, separate
  read/write models, retry/circuit breaker logic, monorepo workspace config,
  denormalized data, custom error type hierarchies
- Git history:
  * git log --format=format: --name-only | sort | uniq -c | sort -rn | head -20 (churn hotspots)
  * git log --oneline --grep="refactor\|migrate\|replace\|rewrite\|upgrade" (architectural shifts)
  * git shortlog -sn --no-merges (ownership)
- Existing ADRs in docs/decisions/, docs/adr/, architecture/decisions/
- Comments containing TODO, HACK, FIXME, workaround

WRITE output to: .claude/skills/site-context/references/decisions.md

PRODUCE:
- 5-10 inferred ADRs using this format per ADR:
  # ADR-N: [Title]
  Status: Inferred from code
  Date: [from git history or "unknown"]
  Confidence: [High|Medium|Low]
  ## Context — [forces/constraints observed in code]
  ## Decision — [what was decided]
  ## Evidence — [code locations, git history]
  ## Consequences — [positive, negative, neutral]
- Decision map linking decisions to affected code areas
- Existing ADR index (if any found)
- Technical debt inventory (from TODO/HACK/FIXME comments with file:line)
```

**Wait for ALL 6 Step 3 agents to complete before proceeding to Step 4.**

---

## Step 4: Behavior (4 parallel background agents)

All depend on Step 3 outputs. Launch all 4 in parallel with
`run_in_background: true`, `model: "sonnet"`.

### Agent 8: key-flows

```
Trace 3-5 representative request flows end-to-end through this codebase.

INPUT: Read these references from the site-context skill
(.claude/skills/site-context/references/):
- system-overview.md
- component-map.md
- use-cases.md

SELECT 3-5 flows to trace:
1. The simplest successful flow (health check, login, basic GET)
2. The core business flow (the primary thing the system does)
3. A read-heavy flow (search, dashboard, report with joins/aggregation)
4. An async flow (background job, webhook, event processing) — if applicable
5. An error/failure flow (what happens when a downstream service fails)

For each flow, trace through the codebase:
  Entry point → middleware/interceptors → handler/controller
  → service/use case → repository/data access → database/external API
  → response transformation → output

WRITE output to: .claude/skills/site-context/references/key-flows.md

PRODUCE these diagrams:
- Sequence diagram per flow (Mermaid sequenceDiagram) — with actual component names, method calls, protocols
- Data flow diagram (Mermaid flowchart LR) — ingress → transform → store → egress

PRODUCE these tables:
- Step-by-step table per flow (step, component, action, file:line)
- Error path table per flow (error condition, where caught, response)
- Side effects per flow (events emitted, logs written, metrics recorded)
```

### Agent 9: event-catalog

```
Catalog all domain events — producers, consumers, schemas, and flow chains.

INPUT: Read these references from the site-context skill
(.claude/skills/site-context/references/):
- system-overview.md
- component-map.md

SCAN the codebase for:
- Event class/type definitions (class.*Event, type.*Event, interface.*Event)
- All publish/emit/send calls — trace to triggering action
- All subscribe/on/handler registrations — trace to reaction logic
- Message queue topics from config (Kafka, SQS, SNS, RabbitMQ, Redis pub/sub)
- Saga/orchestration patterns (state machines, step tracking tables)

If NO event-driven patterns are detected (no message broker, event bus, or pub/sub),
write a stub: "# Event Catalog\n\nNot applicable: this system does not use event-driven patterns."

WRITE output to: .claude/skills/site-context/references/event-catalog.md

PRODUCE these diagrams (if events exist):
- Producer-consumer map (Mermaid flowchart LR) — services → topics → consumers
- Event flow timeline (Mermaid flowchart LR) — chronological chain with command/event distinction
- Saga flow diagram (Mermaid flowchart TD) — if saga/orchestration detected

PRODUCE these tables (if events exist):
- Event catalog (event name, producer, topic/queue, consumers, key payload fields)
- Command-Event-Policy chain (step, type, name, triggered by, produces, handler file)
- Event schema for top 3-5 events (field, type, required, description)
- Saga compensation table (step, service, action, success event, failure event, compensation)
- Delivery guarantee notes
```

### Agent 10: data-ownership

```
Map which modules/services create, read, update, and delete which data entities.

INPUT: Read these references from the site-context skill
(.claude/skills/site-context/references/):
- component-map.md
- data-model.md

PROCESS:
1. From data-model.md, get the list of all data entities
2. From component-map.md, get the list of all modules/services
3. For each module x entity, grep for: ORM create/insert (C), find/select (R), update/save (U), delete/destroy (D)
4. Also check raw SQL operations
5. Identify ownership conflicts (multiple writers to same entity)

WRITE output to: .claude/skills/site-context/references/data-ownership.md

PRODUCE these diagrams:
- Data ownership diagram (Mermaid flowchart TD) — services → data stores, solid=owner, dashed=reader

PRODUCE these tables:
- CRUD matrix (module x entity, bold = owner)
- Ownership analysis (clean ownership, shared writes, violations — with coordination mechanism for each)
- Column-level breakdown for shared tables (which service writes which columns)
- API-to-data mapping (endpoint x entity x CRUD operation)
- Ownership violation inventory with recommended fixes
```

### Agent 11: state-lifecycles

```
Document state machines for key domain entities — valid states, transitions,
terminal states.

INPUT: Read these references from the site-context skill
(.claude/skills/site-context/references/):
- data-model.md
- use-cases.md

SCAN the codebase for:
- Entities with status, state, or enum-typed columns (from data-model.md)
- Enum/const definitions for status values
- Transition functions or state machine implementations
- Validation logic that checks status before allowing operations
- Test cases that exercise state transitions

If NO entities with status/state fields are found, write a stub:
"# State Lifecycles\n\nNo stateful entities detected in this codebase."

WRITE output to: .claude/skills/site-context/references/state-lifecycles.md

PRODUCE these diagrams:
- State diagram per stateful entity (Mermaid stateDiagram-v2) — typically 2-5 diagrams
  Common candidates: orders, payments, jobs/tasks, user accounts, subscriptions, shipments

PRODUCE these tables:
- Transition table per entity (current state x event → next state + guard condition)
- Invalid transitions documented explicitly
- Terminal states identified
- Enum/const code linkage (the type definition that maps to each diagram, with file:line)
```

**Wait for ALL 4 Step 4 agents to complete before proceeding to Step 5.**

---

## Step 5: Deep Dive (3 parallel background agents)

Depend on Step 4 outputs. Launch all 3 in parallel with
`run_in_background: true`, `model: "sonnet"`.

### Agent 12: business-rules

```
Extract decision tables, validation rules, authorization matrices, and feature
flags from this codebase.

INPUT: Read these references from the site-context skill
(.claude/skills/site-context/references/):
- key-flows.md
- use-cases.md
- data-model.md

SCAN the codebase for:
- Functions with complex branching (>3 paths) identified during flow tracing
- Validation middleware/functions — extract rule tables
- Authorization checks — build permission matrix
- Pricing/discount/eligibility calculations
- Feature flag configuration (LaunchDarkly, env-based, config files)
- Risk scoring or classification functions

WRITE output to: .claude/skills/site-context/references/business-rules.md

PRODUCE these tables:
- Decision tables for complex business logic (condition-action format, one per rule set)
- Validation rules matrix per entity (field, rule, error code, error message, cross-field rules)
- Permission/authorization matrix (role x resource x action, with guard conditions)
- Feature flag inventory (flag name, state per environment, rollout %, behavior when on)
- Include source file:line linkage for each rule set
```

### Agent 13: control-flow

```
Document complex functions with flowcharts, decision trees, and activity diagrams.

INPUT: Read these references from the site-context skill
(.claude/skills/site-context/references/):
- key-flows.md
- component-map.md

SCAN the codebase for functions with:
- Deep nesting (>4 levels)
- Many conditionals (>5 branches)
- Retry/loop logic with backoff
- Error handling with multiple catch paths
- Complex business logic identified in key-flows.md

LIMIT: Document the 5-10 most complex functions only.

WRITE output to: .claude/skills/site-context/references/control-flow.md

PRODUCE these diagrams:
- Flowchart per complex function (Mermaid flowchart TD) — happy path + all error paths + retry loops
- Decision tree per multi-condition logic (Mermaid flowchart TD or ASCII)
- Activity diagram per loop/retry process (Mermaid flowchart TD with back-edges)

Include source file:line for each function documented.
```

### Agent 14: deployment

```
Document where the software runs — infrastructure layout, environments, network
boundaries.

INPUT: Read these references from the site-context skill
(.claude/skills/site-context/references/):
- system-overview.md
- component-map.md
- context-diagram.md

SCAN the codebase for:
- Infrastructure-as-code (Terraform .tf, CloudFormation, Pulumi, CDK)
- Kubernetes manifests (k8s/, manifests/, helm/)
- Docker compose (production variant if separate from dev)
- CI/CD deployment config (GitHub Actions deploy jobs, deployment scripts)
- Cloud-specific config (serverless.yml, SAM template.yaml, ECS task defs, Lambda config)
- Environment-specific config files

WRITE output to: .claude/skills/site-context/references/deployment.md

PRODUCE these diagrams (as applicable):
- Production deployment diagram (Mermaid C4Deployment or flowchart TD)
- Kubernetes deployment diagram (flowchart TD with namespace subgraphs) — if K8s
- Serverless deployment diagram (flowchart LR) — if serverless

PRODUCE these tables:
- Infrastructure inventory (component, technology, scaling config, notes)
- Network boundary notes (VPCs, subnets, public vs private)
- Environment comparison table (prod vs staging vs dev: DB, replicas, secrets, monitoring, domain)
- Critical config values (timeouts, pool sizes, replica counts, memory limits)
```

**Wait for ALL 3 Step 5 agents to complete before proceeding to Step 6.**

---

## Step 6: Synthesis (2 foreground agents, sequential)

### Agent 15: risk-assessment

Dispatch as foreground (model: opus, NOT background) — this agent synthesizes
everything and needs the highest reasoning capability.

```
Synthesize all previous codebase analyses into an integrated risk and quality
assessment.

INPUT: Read ALL reference files from the site-context skill
(.claude/skills/site-context/references/) — read every .md file in that directory.

WRITE output to: .claude/skills/site-context/references/risk-assessment.md

PRODUCE:

## Integration Point Inventory
For every external dependency (from context-diagram.md + key-flows.md):
| Integration Point | Type | Failure Mode | Protection Pattern | Monitoring |

## Stability Pattern Audit
For each integration point, check: timeout? circuit breaker? retry? bulkhead? fallback?
| Integration Point | Timeout | Circuit Breaker | Retry | Bulkhead | Fallback |

## Complexity Hotspot Report
From dependency-analysis.md + git history + control-flow.md:
| File/Module | Indicators | Cognitive Load | Risk | Recommendation |

## Data Integrity Risks
From data-ownership.md + data-model.md:
- Shared writes without coordination mechanism
- Missing constraints or validation
- Inconsistency windows in async flows

## Architecture Health Summary
- Layer violations count (from dependency-analysis.md)
- Circular dependencies count
- Ownership violations count (from data-ownership.md)
- Missing stability patterns count

## Top 5 Risks (ordered by severity)
For each: description, evidence (file:line), impact, recommended action
```

### Agent 16: site-context-index

Dispatch as foreground (model: sonnet), AFTER risk-assessment completes.

This agent produces a valid Claude Code skill. The output MUST conform to
skill-creator conventions: YAML frontmatter with `name` and `description`,
and a body that serves as a quick reference index to all analysis files.

```
Generate the SKILL.md index for the site-context skill.

You are building a valid Claude Code skill file. The SKILL.md you produce will
be installed at .claude/skills/site-context/SKILL.md and must work as a
functional skill that Claude can discover and use.

SKILL REQUIREMENTS:
- YAML frontmatter between --- markers with exactly two fields: name and description
- The description must explain what the skill provides AND when to use it
- The body is a markdown reference index linking to all analysis files in references/
- Keep the SKILL.md under 150 lines (it's an index, not the analysis itself)

INPUT: Read ALL reference files from the site-context skill
(.claude/skills/site-context/references/) — read every .md file in that directory.
- Extract the system name and purpose from system-overview.md
- Scan each file to verify it exists and is non-empty
- Note any files that contain "Not applicable" stubs

WRITE output to: .claude/skills/site-context/SKILL.md

STRUCTURE:

1. Frontmatter:
   - name: site-context
   - description: must mention the actual system name, what analysis is included,
     and trigger phrases like "how does this work", "where do I change X",
     "what are the risks", "explain the architecture"

2. Heading: # [Actual System Name] — Site Context

3. System at a Glance section:
   - 2-3 sentence summary (from system-overview.md)
   - Stack, Shape, key entry points (brief)

4. Reference Index table:
   | What You Need | Reference |
   Each of the 14 reference files with a one-line description of what it contains.
   Skip any files that are "Not applicable" stubs — note them at the bottom instead.

5. Quick Navigation section with these exact scenarios:
   - "I need to fix a bug in X" → which files to read in order
   - "I need to add a feature" → which files to read in order
   - "I need to understand the architecture" → which files to read in order
   - "I need to understand the data" → which files to read in order
   - "Where are the risks?" → which files to read in order
```

---

## Step 7: Validation (synchronous, no agents)

After Step 6 completes, validate the site-context skill directly (no agent needed):

1. **Verify SKILL.md frontmatter** — read `.claude/skills/site-context/SKILL.md` and
   confirm it has valid YAML frontmatter with `name` and `description` fields.

2. **Verify progressive disclosure** — SKILL.md should be under 150 lines (it's an
   index). All detailed content should be in `references/` files. If SKILL.md is too
   long, move content to a reference file and replace with a link.

3. **Verify reference files** — read each file in `references/` and confirm:
   - File is non-empty
   - Files >100 lines have a table of contents
   - All Mermaid diagrams have titles
   - No broken internal links between reference files

4. **Fix any issues found** — edit files directly to resolve problems.

Use the `/skill-creator` conventions as the quality standard:
- Frontmatter: only `name` and `description` fields
- Description: includes what the skill does AND when to use it (trigger phrases)
- Body: quick reference index, not detailed content
- References: standalone, loaded on demand

---

## Step 8: Generate CLAUDE.md (synchronous, no agents)

As the final step, generate (or update) a top-level `CLAUDE.md` at the project root.
This is the file Claude reads at the start of every session. It should contain only
the essentials and point to the site-context skill for everything else.

Read `.claude/skills/site-context/references/system-overview.md` to extract:
- System name and purpose
- Tech stack (abbreviated — language, framework, database only)
- Build/test/lint/run commands
- Directory structure (abbreviated — top-level only)
- Key conventions (only non-obvious ones)

**If a CLAUDE.md already exists**: read it first. Preserve any existing content the
user has written (conventions, constraints, git workflow). Add or update only the
sections below. Do NOT overwrite user-authored rules.

**If no CLAUDE.md exists**: create one from scratch using this template.

Write to: `CLAUDE.md` (project root)

Target: **under 100 lines**. This is a pointer, not the analysis.

```markdown
# [System Name]

## Stack
- [Language/version], [Framework], [Database]
- [Other key technologies — 1 line]

## Commands
- Install: `[exact command]`
- Build: `[exact command]`
- Test: `[exact command]`
- Test single: `[exact command for single file/test]`
- Lint: `[exact command]`
- Run locally: `[exact command]`

## Structure
```
[top-level directory tree, 1 level deep, one-line purpose per dir]
```

## Key Conventions
- [Only non-obvious conventions that deviate from standard practice]
- [e.g., "All DB writes require conditional expressions — see ADR in site-context"]
- [e.g., "Integration tests require TEST_DB_URL env var"]

## Architecture & Documentation
Comprehensive codebase analysis is available in the site-context skill:
- System boundary and external deps: @.claude/skills/site-context/references/context-diagram.md
- Component architecture: @.claude/skills/site-context/references/component-map.md
- Data model: @.claude/skills/site-context/references/data-model.md
- Key request flows: @.claude/skills/site-context/references/key-flows.md
- Business rules: @.claude/skills/site-context/references/business-rules.md
- Risk assessment: @.claude/skills/site-context/references/risk-assessment.md

For the full analysis index, see @.claude/skills/site-context/SKILL.md
```

**Important rules for CLAUDE.md generation**:
- Keep it under 100 lines — every line costs context window space
- Use exact commands (copy-pasteable), not descriptions
- Do NOT include anything Claude already knows from standard conventions
- Do NOT duplicate content from site-context — point to it with @path imports
- The @path syntax tells Claude to load those files on demand when relevant
- Only include the 5-6 most important site-context references in CLAUDE.md — the
  full list is in the site-context SKILL.md

---

## Completion

After generating CLAUDE.md, report to the user:
1. Total agents run and completion status
2. List of all files created:
   - `CLAUDE.md` (project root)
   - `.claude/skills/site-context/SKILL.md`
   - `.claude/skills/site-context/references/*.md` (list each)
3. Top 3 findings from risk-assessment.md
4. Any analysis types that were marked "not applicable"
5. Validation result (pass/fail + any fixes applied)
6. Whether CLAUDE.md was created new or merged with existing
