# Analysis Workflow

Detailed procedures for each phase of codebase analysis. Execute phases in order
for full analysis, or jump to specific phases based on user need (see SKILL.md
Phase Selection tree).

## Table of Contents

- [Phase 1: Orient](#phase-1-orient)
- [Phase 2: Map Structure](#phase-2-map-structure)
- [Phase 3: Trace Runtime](#phase-3-trace-runtime)
- [Phase 4: Surface Contracts](#phase-4-surface-contracts)
- [Phase 5: Excavate Decisions](#phase-5-excavate-decisions)
- [Phase 6: Assess Risk](#phase-6-assess-risk)
- [Phase 7: Produce Artifacts](#phase-7-produce-artifacts)

---

## Phase 1: Orient

**Goal**: Rapidly identify what this system is, what technologies it uses, and
where the important parts live. Spend 5-10 minutes here before going deeper.

### 1.1 Project Shape Scan

Read these files/directories in order (skip if absent):

1. **Root directory listing** — `ls -la` to see project shape
2. **Package manifest** — `package.json`, `Cargo.toml`, `go.mod`, `pyproject.toml`,
   `pom.xml`, `Gemfile`, `build.gradle`, `*.csproj`, `requirements.txt`
   → Reveals: language, framework, dependencies, scripts/commands
3. **README.md** — Existing description, setup instructions
4. **Docker/container files** — `Dockerfile`, `docker-compose.yml`, `k8s/`
   → Reveals: runtime topology, services, databases
5. **CI/CD config** — `.github/workflows/`, `Jenkinsfile`, `.gitlab-ci.yml`, `cloudbuild.yaml`
   → Reveals: build process, test suites, deployment targets
6. **Config files** — `.env.example`, `config/`, `settings.py`, `application.yml`
   → Reveals: runtime configuration, feature flags, environment-specific behavior
7. **Existing architecture docs** — `ARCHITECTURE.md`, `docs/`, `ADR/`, `CLAUDE.md`

### 1.2 Tech Stack Identification

From the package manifest and imports, identify:

| Category | What to Find | Where to Look |
|----------|-------------|---------------|
| Language + version | Primary language, version constraints | Package manifest, CI config, Dockerfile |
| Framework | Web framework, ORM, test framework | Dependencies, import statements |
| Database | RDBMS, NoSQL, cache | Docker compose, config files, ORM config |
| Message broker | Queue, pub/sub, event bus | Dependencies, config, docker compose |
| External APIs | Third-party services | Config files, environment variables, SDK imports |
| Infrastructure | Cloud provider, IaC | Terraform, CloudFormation, deployment configs |

### 1.3 Entry Point Identification

Find the starting points for code execution:

- **Web apps**: Route definitions, controller files, API endpoint registrations
- **CLI tools**: Main function, command definitions, argument parsers
- **Libraries**: Public API surface, exported modules, index files
- **Workers/jobs**: Queue consumers, cron definitions, event handlers
- **Monorepos**: Workspace definitions, package interdependencies

### 1.4 Orient Output

Produce a brief summary:

```
System: [name]
Purpose: [one sentence]
Stack: [language/framework/database/infrastructure]
Shape: [monolith|microservices|monorepo|library|CLI]
Entry points: [list of 3-5 main entry points with file paths]
Key directories: [list of top-level dirs with purpose]
```

---

## Phase 2: Map Structure

**Goal**: Produce a static decomposition of the codebase — what modules exist,
how they relate, and how they are layered.

This corresponds to the **Module Viewtype** from Views and Beyond and the
**Container/Component levels** from C4.

### 2.1 Container Identification

A container is a separately-running process or data store. Identify all containers:

- Each service in docker-compose is typically a container
- Each deployable unit (backend, frontend, worker) is a container
- Each database, cache, or message broker is a container
- Each serverless function group may be a container

For each container, record:
- Name (as used in code/config)
- Technology (e.g., "Express.js app", "PostgreSQL 15", "Redis")
- Responsibility (one sentence)
- Communication protocols used (HTTP, gRPC, AMQP, SQL)

### 2.2 Module Decomposition (per container)

For each container, identify the major modules/packages/namespaces:

```
Scan Approach:
1. Read the top-level directory structure within the container
2. Identify organizational pattern:
   - By layer (controllers/, services/, models/, repositories/)
   - By feature/domain (users/, orders/, payments/, auth/)
   - Hybrid (src/api/, src/domain/, src/infrastructure/)
3. For each major module, identify:
   - Responsibility (what does it do?)
   - Public interface (what does it export/expose?)
   - Dependencies (what other modules does it import?)
```

### 2.3 Dependency Analysis

Map module-to-module dependencies by analyzing imports/requires:

- Scan import statements across all files in each module
- Build a dependency matrix: rows import from columns
- Identify dependency direction: Are there cycles? Layering violations?
- Flag bidirectional dependencies (these create coupling)

### 2.4 Layer Identification

Determine if the code follows a layering pattern:

```
Common layer patterns:
├── Clean Architecture: Entities → Use Cases → Interface Adapters → Frameworks
├── Traditional MVC: Controllers → Services → Models → Database
├── Hexagonal: Domain → Ports → Adapters
├── CQRS: Commands / Queries → Handlers → Repository → Storage
└── No clear layers (document what you observe)
```

For each layer, verify the dependency rule: dependencies should point inward/downward.
Flag violations.

### 2.5 Structure Output

Produce:
- C4 Level 2 Container diagram (Mermaid)
- C4 Level 3 Component diagram per major container (Mermaid)
- Module dependency matrix or diagram
- Layer diagram if layers are present

---

## Phase 3: Trace Runtime

**Goal**: Understand how the system behaves at runtime — what calls what, how
data flows, what happens when a request arrives.

This corresponds to the **Component-and-Connector Viewtype** from Views and Beyond
and **Dynamic Diagrams** from C4.

### 3.1 Request Flow Tracing

Pick 3-5 representative flows and trace them end-to-end:

1. **The "hello world" flow** — Simplest successful request (e.g., health check, login)
2. **The core business flow** — The primary thing the system does (e.g., create order, process payment)
3. **A read-heavy flow** — Data retrieval with joins/aggregation
4. **An async flow** — Background job, event-driven processing, webhook
5. **An error flow** — What happens when a downstream service fails

For each flow, trace:
```
Entry point → middleware/interceptors → handler/controller
→ service/use case → repository/data access → database/external API
→ response transformation → output
```

### 3.2 Data Flow Analysis

Map how data moves through the system:

- **Ingress**: Where does data enter? (API endpoints, file uploads, event consumers, CLI args)
- **Transformation**: Where is data validated, enriched, or transformed?
- **Storage**: Where is data persisted? What schemas exist?
- **Egress**: Where does data leave? (API responses, events published, files written, emails sent)
- **Caching**: Where is data cached? What invalidation strategy?

### 3.3 Communication Pattern Identification

Identify which runtime interaction patterns are used:

| Pattern | Evidence | What to Document |
|---------|----------|------------------|
| Synchronous request/response | HTTP calls, gRPC, function calls | Endpoint, payload, timeout |
| Publish/subscribe | Event bus, message queue, webhooks | Event types, topics, subscribers |
| Shared data | Database accessed by multiple services | Schema, ownership, consistency model |
| Pipe and filter | Stream processing, middleware chains | Stage order, data transformation |
| Client-server | Frontend-backend, mobile-API | Protocol, authentication, versioning |
| Peer-to-peer | Service mesh, distributed coordination | Discovery mechanism, consensus |

### 3.4 Concurrency Analysis

Identify concurrent execution:

- Thread pools and their configuration
- Async/await patterns and event loops
- Background workers and job queues
- Database connection pools
- Rate limiting and throttling mechanisms

### 3.5 Runtime Output

Produce:
- Sequence diagrams for each traced flow (Mermaid)
- Data flow diagram (Mermaid flowchart)
- Communication pattern summary table

---

## Phase 4: Surface Contracts

**Goal**: Document the key interfaces, boundaries, and invariants that a developer
must understand to work with the system safely.

Based on Ousterhout's interface documentation approach and SEI interface documentation.

### 4.1 External API Surface

For each external-facing API:

- **Endpoints/methods** with signatures
- **Authentication/authorization** requirements
- **Request/response schemas** (or pointer to OpenAPI spec if it exists)
- **Error responses** and their meanings
- **Rate limits** and quotas
- **Versioning** strategy

### 4.2 Internal Module Interfaces

For each major module boundary, document:

- **What it provides** — Public functions/classes/types exported
- **What it requires** — Dependencies it expects to be present
- **Preconditions** — What must be true before calling
- **Postconditions** — What is guaranteed after a successful call
- **Side effects** — State changes, events emitted, external calls made
- **Error conditions** — What can go wrong and how errors are signaled

### 4.3 Data Contracts

- **Database schemas** — Tables, columns, types, constraints, indexes
- **Event schemas** — Event types, payload shapes, versioning
- **Configuration contracts** — Required env vars, config keys, their types and defaults
- **File format contracts** — Input/output file formats the system handles

### 4.4 Invariants and Constraints

Identify rules that must hold true across the system:

- Business rules enforced in code (e.g., "an order cannot be negative")
- Consistency constraints (e.g., "user email must be unique")
- Ordering constraints (e.g., "payment must occur before shipment")
- Security boundaries (e.g., "tenant data must never leak across tenants")
- Performance constraints (e.g., "API response under 200ms at p99")

Sources for invariants:
- Validation logic in request handlers
- Database constraints (unique, foreign key, check)
- Assert/invariant statements in code
- Test assertions (especially integration tests)
- Comments containing "must", "never", "always", "invariant"

### 4.5 Contracts Output

Produce:
- API surface summary table
- Interface documentation for top 5-10 critical interfaces
- Data contract summary (schemas, events, config)
- Invariant catalog

---

## Phase 5: Excavate Decisions

**Goal**: Reverse-engineer the architectural decisions behind the code — the "why"
that is invisible in the code itself.

Based on ADR methodology (Nygard) and Views and Beyond rationale documentation.

### 5.1 Decision Signals in Code

Look for these indicators of deliberate architectural choices:

| Signal | Likely Decision |
|--------|----------------|
| Custom abstraction wrapping a library | "We may swap this dependency" |
| Feature flags | "We need gradual rollout / A-B testing" |
| Multiple implementations of an interface | "We need pluggability / strategy pattern" |
| Middleware/interceptor chain | "Cross-cutting concerns handled uniformly" |
| Event-driven communication between services | "We chose eventual consistency over strong consistency" |
| Separate read/write models | "We adopted CQRS for read/write scaling" |
| Extensive retry/circuit breaker logic | "Downstream services are unreliable" |
| Monorepo with workspace config | "We want shared tooling and atomic cross-package changes" |
| Denormalized data | "We optimized for read performance over write simplicity" |
| Custom error types hierarchy | "We need structured error handling across boundaries" |

### 5.2 Decision Archaeology via Git

Use git history to understand evolution:

```bash
# Most-changed files reveal complexity hotspots and iterative decisions
git log --format=format: --name-only | sort | uniq -c | sort -rn | head -20

# Large commits often represent architectural shifts
git log --oneline --shortstat | sort -t',' -k1 -rn | head -10

# Look for "refactor", "migrate", "replace", "rewrite" in commit messages
git log --oneline --grep="refactor\|migrate\|replace\|rewrite\|upgrade"

# Who has worked on what (ownership map)
git shortlog -sn --no-merges
```

### 5.3 Inferred ADR Format

For each identified decision, produce an inferred ADR:

```markdown
# ADR-N: [Decision Title]

**Status**: Inferred from code (not explicitly documented)
**Date**: [Approximate date from git history, or "unknown"]

## Context
[Forces and constraints that likely drove this decision,
based on code evidence and common engineering trade-offs]

## Decision
[What was decided, stated as "The system uses X because..."]

## Evidence
[Specific code locations, patterns, and git history that support this inference]

## Consequences
[Observable effects of this decision — both positive and negative]
```

### 5.4 Decisions Output

Produce:
- List of 5-10 key inferred ADRs
- Decision map linking decisions to the code areas they affect

---

## Phase 6: Assess Risk

**Goal**: Identify integration points, failure modes, and complexity hotspots
that present risk to maintainability and reliability.

Based on Release It! stability patterns/anti-patterns and Rozanski & Woods perspectives.

### 6.1 Integration Point Inventory

Every external dependency is a risk. Catalog each one:

| Integration Point | Type | Failure Mode | Protection | Monitoring |
|-------------------|------|-------------|------------|------------|
| [Service/API name] | HTTP/gRPC/DB/Queue | Timeout/Error/Unavailable | Circuit breaker/Retry/Fallback | Metrics/Alerts |

### 6.2 Stability Pattern Audit

For each integration point, check which patterns are present:

- **Timeout**: Is there an explicit timeout? What is its value? What happens on timeout?
- **Circuit Breaker**: Is there a circuit breaker? What are the thresholds? How is state exposed?
- **Retry**: Is there retry logic? How many retries? Is there backoff? Is it idempotent-safe?
- **Bulkhead**: Are thread/connection pools isolated per dependency?
- **Fallback**: Is there degraded-mode behavior when a dependency is unavailable?
- **Rate Limiting**: Are outbound calls rate-limited to protect the dependency?

### 6.3 Complexity Hotspot Analysis

Identify areas of highest cognitive load:

```
Indicators of complexity hotspots:
├── Files with high churn (from git log analysis)
├── Files with many dependencies (high fan-in or fan-out)
├── Long functions/methods (>100 lines)
├── Deep nesting (>4 levels)
├── Many conditionals in a single function
├── Global state or singletons with wide usage
├── Implicit dependencies (service locators, reflection, dynamic dispatch)
├── Shared mutable state between modules
└── Code with many TODO/FIXME/HACK comments
```

### 6.4 Security Boundary Analysis

Identify trust boundaries:

- Where is authentication checked?
- Where is authorization enforced?
- Where is user input validated/sanitized?
- Where is data encrypted (at rest, in transit)?
- Are there multi-tenancy isolation boundaries?

### 6.5 Risk Output

Produce:
- Integration point inventory table
- Stability pattern coverage matrix
- Complexity hotspot list with file paths and indicators
- Security boundary diagram

---

## Phase 7: Produce Artifacts

**Goal**: Assemble analysis results into polished documentation deliverables.

### Artifact Selection

Not every analysis needs every artifact. Select based on user need:

| Artifact | When to Produce | Template |
|----------|----------------|----------|
| System Overview | Always | [output-templates.md § System Overview](output-templates.md) |
| Container Diagram | Multi-service systems | [output-templates.md § Container Diagram](output-templates.md) |
| Component Analysis | Requested or complex containers | [output-templates.md § Component Analysis](output-templates.md) |
| Request Flow Traces | Bug fixing, onboarding | [output-templates.md § Request Flow](output-templates.md) |
| Interface Catalog | Extension/integration work | [output-templates.md § Interface Catalog](output-templates.md) |
| Inferred ADRs | Architecture understanding | [output-templates.md § Inferred ADR](output-templates.md) |
| Integration Point Inventory | Reliability concerns | [output-templates.md § Integration Points](output-templates.md) |
| ARCHITECTURE.md | Explicitly requested | [output-templates.md § ARCHITECTURE.md](output-templates.md) |
| "Where to Look" Guide | Onboarding | [output-templates.md § Where to Look](output-templates.md) |

### Quality Checklist

Before delivering any artifact:

- [ ] All names match actual code identifiers (no invented names)
- [ ] Diagrams use Mermaid and include titles
- [ ] Each artifact stays in one viewtype (no mixing structure and behavior)
- [ ] Cross-cutting concerns documented separately from structural views
- [ ] Rationale included wherever a non-obvious pattern exists
- [ ] File paths are accurate and verified
- [ ] No speculation presented as fact — mark inferences as "inferred"
