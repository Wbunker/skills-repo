# Context Engineering

Sources: OpenAI harness engineering (Feb 2026), arXiv 2603.25723 (Natural-Language Agent Harnesses), arXiv 2603.05344 (Building AI Coding Agents for the Terminal)

## Table of Contents

- [The Core Constraint](#the-core-constraint)
- [The Filesystem as Navigation Interface](#the-filesystem-as-navigation-interface-openai) — path as context signal; many small files; pagination primitive
- [Structural Navigation + Semantic Search](#structural-navigation--semantic-search-complementary-primitives) — two-mode workflow; synthetic filesystem
- [OpenAI's Three Pillars](#openais-three-pillars) — tests, types, documentation
- [Structured Knowledge Base](#structured-knowledge-base-openai) — architecture doc, decision log, entity catalog, canonical examples
- [File-Backed State](#file-backed-state-in-practice-framework-artifact-architectures) — framework artifact architectures; arXiv research
- [Harness Contracts](#harness-contracts-arxiv-research) — pre/post-conditions, invariants, action contracts
- [Context Overflow Intervention](#context-overflow-intervention-deepseek-v32) — 80% threshold; summary/discard strategies
- [Adaptive Context Management](#adaptive-context-management) — progressive compaction
- [Centralized vs. Distributed State Management](#centralized-vs-distributed-state-management)
- [Per-Agent Context Scoping](#per-agent-context-scoping-openclaw-pattern) — SOUL.md pattern
- [Model-Agnostic Harness Design](#model-agnostic-harness-design)
- [Multi-Model Routing](#multi-model-routing) — task complexity routing; cost tiers
- [Harnessability Assessment](#harnessability-assessment)
- [Dependency Selection as a Harness Decision](#dependency-selection-as-a-harness-decision-openai) — "boring" tech; deliberate reimplementation
- [Agent-Computer Interface (ACI) Design](#agent-computer-interface-aci-design) → [aci-design.md](aci-design.md)

---

## The Core Constraint

From an agent's perspective, anything it can't access in-context doesn't exist. Knowledge in Slack threads, Google Docs, or people's heads is inaccessible. Repository-local, versioned artifacts are what the agent can see.

Context engineering is the discipline of deciding what instructions, evidence, and state should be available at each step of a long run.

## The Filesystem as Navigation Interface (OpenAI)

> "The main mechanism agentic tools use to navigate your codebase is the filesystem. They list directories, read filenames, search for strings, and pull files into context. You should treat your directory structure and file naming with the same thoughtfulness you'd treat any other interface."

Agents don't read codebases top-to-bottom. They navigate by path. A file's location and name are context signals the agent reads before it opens the file — and they influence which files get pulled into context at all.

**Namespaced paths communicate intent:**

```
./billing/invoices/compute.ts    ← unambiguous domain + responsibility
./utils/helpers.ts               ← no information
```

Even if the code inside is identical, the first path tells the agent what domain it's in, what kind of file this is, and what it's responsible for. The second requires the agent to read the file to discover that. Multiply this across a large codebase: poor naming forces the agent to open many more files to orient itself, burning context on discovery rather than work.

**Implications for directory structure:**
- Organize by domain, not by type — `billing/`, `auth/`, `reporting/` over `utils/`, `helpers/`, `shared/`
- Flat is often better than deep: too many nesting levels make paths harder to reason about
- Every directory name should constrain what can be in it — a reader (or agent) should be able to predict the contents from the path

**Prefer many small, well-scoped files:**
Agents summarize or truncate large files when loading them into their working set. A file short enough to be loaded in full stays entirely active in context — the agent never has to guess what was truncated.

In practice, this eliminates a class of degraded performance: the agent working on a partially-loaded file, missing the section it needs, and making decisions based on incomplete information.

**Practical rule**: if a file is doing more than one well-scoped thing, split it. A file should be nameable in one noun phrase (`invoice-calculator.ts`, `user-auth-middleware.ts`). If it requires "and" to describe, it should be two files.

**Connection to file size limits**: this is the underlying rationale for the file size taste invariant (see [agent-readable-lints.md](agent-readable-lints.md)). Enforcing a line limit mechanically catches drift; the principle explains why the limit exists.

**Pagination primitive for unavoidably large files:**

When files cannot be split (generated code, logs, large data files), design the read tool to accept `limit`, `offset`, and `grep` parameters rather than loading the full content. The agent reads in chunks, jumps to relevant sections, and filters content — handling arbitrarily large files without context overflow.

```json
{ "nodeId": "file-id", "offset": 200, "limit": 100, "grep": "ERROR" }
```

This mirrors how a program with limited RAM must sample a file rather than load it entirely. The agent acts similarly: it peeks, orients, then reads what it needs. Without pagination, large-file reads either fail (context overflow) or silently truncate — the worst outcome, because the agent proceeds on incomplete information without knowing it.

## Structural Navigation + Semantic Search: Complementary Primitives

Source: Dust.tt engineering blog, "How We Taught AI Agents to Navigate Company Data Like a Filesystem" (July 2025)

Semantic search and structural navigation are not competing approaches — they compose. Each covers what the other cannot:

- **Semantic search** finds information by meaning across a broad corpus, but cannot navigate to a known location ("the TeamOS section of last week's meeting notes")
- **Structural navigation** (list, find, locate) traverses hierarchies to known locations, but cannot find meaning-based content scattered across a knowledge base

The failure mode of semantic-search-only systems: agents start inventing path-like syntax to hack around the missing navigation primitive — `file:front/src/some-file-name.tsx`, `path:/notion/engineering/weekly-updates`. **Agents reaching for a tool that doesn't exist is a harness design signal.** Build what the agent is trying to do.

**The two-mode workflow:**

```
Broad semantic search across the entire corpus
    → locate_in_tree on results to understand structural placement
    → list adjacent directories to discover related modules
    → focused semantic search within that specific subtree
    → cat/read specific files for implementation detail
```

Or in reverse — when the location is known but the content isn't:

```
list the relevant directory
    → find the target document
    → cat with grep to surface the specific section
```

Neither mode alone handles complex knowledge tasks. Together, they let agents develop contextual understanding — not just finding information, but understanding where it lives relative to everything else.

**Synthetic filesystem as an abstraction pattern:**

For external data sources (Notion, Slack, Google Drive, databases), the structural hierarchy may not exist natively. Imposing a synthetic filesystem — mapping disparate sources to a consistent ls/find/cat interface — gives agents one navigation vocabulary for everything. Slack channels become directories; threads become files. The abstraction isn't constrained by how the source organizes data internally; it's designed for how agents navigate.

**Files that are also folders:** some nodes are simultaneously readable (cat their content) and traversable (list their children). Notion pages are the canonical example — a page has content and sub-pages. Tool schemas should represent this dual nature explicitly so the agent knows which operations are valid.

## OpenAI's Three Pillars

### 1. Context Engineering

Make all critical knowledge repository-local and machine-readable:

**Static context (always available)**:
- `AGENTS.md` or `CLAUDE.md` — architectural decisions, naming conventions, stack choices, deployment processes. For Claude Code specifically, this file is advisory (not deterministic) and subject to an instruction budget of ~150–200 items before compliance drops. See [claude-md-design.md](claude-md-design.md) for the 4-layer system, the three sections that matter, and the compounding maintenance pattern.
- Architecture specs, API contracts, style guides
- "Golden principles" — opinionated, mechanical rules encoded directly in the repository to keep the codebase legible and consistent for future agent runs

**Dynamic context (injected at runtime)**:
- Observability data and CI/CD status
- Directory mappings and project structure
- Feature list status

Everything that should guide agent behavior must live in the codebase — never in external systems. This includes architectural decisions and deployment processes.

## Structured Knowledge Base (OpenAI)

OpenAI describes a richer structure for the repository knowledge base, treating it as a catalogued, indexed, and mechanically enforced system:

**Design documentation layer:**
- **Core beliefs** — agent-first operating principles that define how the team thinks about AI development; the philosophical layer above individual rules
- **Architecture document** — top-level map of domains and package layering; the entry point for any agent orienting to the codebase
- **Quality document** — grades each product domain and architectural layer; tracks gaps over time; a lagging indicator of codebase health

**Plans as first-class artifacts:**

| Plan type | When to use | Contents |
|---|---|---|
| Lightweight plan | Small, bounded changes | Ephemeral; may be a comment or scratch file |
| Execution plan | Complex work | Progress log, decision log, checked into repo |

Active plans, completed plans, and known technical debt are all versioned and co-located. An agent starting a new session reads active plans the same way it reads the feature list — not from memory, but from the repository.

**Verification status**: design docs include a verification status field. Unverified designs are treated differently from designs that have been validated against the running system. This prevents agents from building on assumptions that haven't been confirmed.

**Progressive disclosure architecture:**
> "Agents start with a small, stable entry point and are taught where to look next, rather than being overwhelmed up front."

Design your knowledge base with this progression:
1. Entry point (`AGENTS.md` / `CLAUDE.md`) — stable, short, points to everything else
2. Architecture doc — top-level map, one level deeper
3. Domain-specific docs — loaded only when working in that domain
4. Execution plans — loaded only when resuming a specific task

Each level loaded only when the agent needs it. This mirrors the progressive disclosure principle in harness design.

**Mechanical enforcement of the knowledge base:**
Linters and CI jobs validate that the knowledge base is:
- Up to date (docs match current code — see doc-gardening agent)
- Cross-linked (references between docs are valid, no broken pointers)
- Structurally correct (required sections present, verification status fields populated)

This is the key move: the knowledge base is not just written convention — it is enforced. The same CI pipeline that enforces code quality enforces documentation quality.

### 2. Architectural Constraints

Constraints make agents more productive by narrowing the solution space. This is counterintuitive but empirically validated.

> "This is the kind of architecture you usually postpone until you have hundreds of engineers. With coding agents, it's an early prerequisite: the constraints are what allows speed without decay or architectural drift."

**Invariants over implementations:**
The key distinction is what to enforce vs. what to leave free. Enforce what matters structurally; don't prescribe how it's implemented. OpenAI's example: require that data shapes be parsed at the boundary — but don't specify the library. The model chose Zod on its own. Prescribing the implementation would have added rules without improving correctness.

This mirrors "enforce boundaries centrally, allow autonomy locally" — the operating model of a platform engineering organization applied to an agent codebase.

**Rigid layered domain architecture:**
OpenAI built their application around a fixed architectural model: each business domain is divided into a set of layers with strictly validated dependency directions.

Example layer order (within a domain):
```
Types → Config → Repo → Service → Runtime → UI
```

Cross-cutting concerns (auth, connectors, telemetry, feature flags) enter through a single explicit interface: Providers. All other cross-domain dependencies are disallowed and enforced mechanically.

This structure is enforced via:
- Custom linters (themselves generated by Codex)
- Structural tests validating dependency direction

**"Taste invariants" — encoding human judgment into tooling:**
Beyond structural layering, OpenAI statically enforces a small set of what they call "taste invariants":
- Structured logging (not ad-hoc string log messages)
- Naming conventions for schemas and types
- File size limits
- Platform-specific reliability requirements

These are enforced via custom lints. Because lints are custom, the error messages can be written as remediation instructions — injecting actionable guidance directly into agent context at the moment of violation.

**Deterministic enforcement tooling:**
- Linters with machine-readable rules
- Structural tests enforcing dependency layering
- Pre-commit hooks preventing constraint violations
- Type checkers and static analysis
- **100% code coverage gate** — CI fails if any line is uncovered; the coverage report becomes the agent's todo list of tests still needed (see [guides-and-sensors.md](guides-and-sensors.md) → "100% Code Coverage as a Harness Constraint")

**Semantic enforcement:**
- LLM-based auditors reviewing agent-generated code
- Custom linter messages written as positive prompt injection (for LLM consumption)

For the concrete implementation of agent-readable lint rules — ESLint, Semgrep, Ruff, golangci-lint, pre-commit integration, and example message patterns:
See [agent-readable-lints.md](agent-readable-lints.md).

**Repo-level rules — golden principles:**
- Explicit prohibitions: "It is unacceptable to remove or edit tests"
- "Golden principles" — opinionated, mechanical rules that keep the codebase legible for future agent runs. Concrete OpenAI examples:
  - **Prefer shared utility packages over hand-rolled helpers** — prevents agents from writing N slightly-different versions of the same function, keeps invariants centralized
  - **Validate data at boundaries; don't probe YOLO-style** — use typed SDKs or explicit validation so agents can't accidentally build on guessed data shapes

**The bar for agent output:**
> "The resulting code does not always match human stylistic preferences, and that's okay. As long as the output is correct, maintainable, and legible to future agent runs, it meets the bar."

This reframes the evaluation criterion: optimize for machine-readability and future-agent-legibility, not for human aesthetic preference.

**Human taste as a continuous input loop:**
Review comments, refactoring PRs, and user-facing bugs are captured as documentation updates or encoded directly into tooling. When documentation falls short of reliably enforcing a rule, the rule is promoted into code — a linter, a structural test, or a pre-commit hook.

This creates a ratchet: every discovered violation that matters becomes a constraint that prevents future violations.

> "In a human-first workflow, these rules might feel pedantic or constraining. With agents, they become multipliers: once encoded, they apply everywhere at once."

OpenAI's result with this approach: a 3-person team shipped 1M+ lines of production code in 5 months with zero manually written lines. Average 3.5 PRs/engineer/day. Throughput increased as the team grew.

### 3. Entropy Management

Codebases drift. Documentation becomes stale. Constraints get bypassed. OpenAI treats entropy management as a first-class harness responsibility — scheduled or event-triggered agents that maintain the integrity of the codebase over time.

> "Technical debt is like a high-interest loan: it's almost always better to pay it down continuously in small increments than to let it compound and tackle it in painful bursts."

Without systematic entropy management, OpenAI's team spent every Friday — 20% of the working week — manually cleaning up "AI slop." The cleanup process didn't scale. They replaced it with a recurring background agent process.

**The operational model:**
A set of background tasks run on a regular cadence (daily or weekly). Each task:
1. Scans the codebase for a specific class of deviation from golden principles
2. Updates quality grades in the quality document
3. Opens targeted refactoring PRs — scoped, small, reviewable in under a minute
4. Most can be automerged after passing CI

The PRs are small by design. A cleanup agent that opens a 2,000-line refactor PR will sit unreviewed. One that opens a 20-line PR fixing a specific pattern violation gets merged in minutes.

**Entropy sources and their cleanup agents:**

| Source | Cleanup agent | Trigger |
|---|---|---|
| Documentation drift | Doc-gardening agent | Scheduled (daily/weekly) |
| Golden principle violations | Pattern scanner | Scheduled (daily) |
| Constraint violations | Violation scanner | Post-merge or nightly |
| Convention deviations | Convention checker | On PR or scheduled |
| Circular dependencies | Dependency auditor | On new import or scheduled |
| Quality grade drift | Quality grader | Scheduled (weekly) |

**Doc-gardening agent pattern** (OpenAI):
A recurring agent that scans documentation for content that no longer matches real code behavior. It:
1. Reads every doc file and its corresponding source code
2. Detects discrepancies (e.g., a function's signature changed but the docstring wasn't updated; a deleted API endpoint still documented as available)
3. Opens fix-up pull requests for each discrepancy it finds

The doc-gardening agent is most valuable in codebases where agents are writing the code — because agents don't reliably update docs when they change implementation. Without a gardening agent, the documentation that future agents rely on becomes increasingly inaccurate.

**The garbage collection framing:**
Treat entropy management like a runtime garbage collector — it runs continuously in the background, reclaiming space before it becomes a problem. The alternative (the "Friday cleanup" model) is manual memory management: you only clean up when things are visibly broken, by which point the cost is high.

> "Human taste is captured once, then enforced continuously on every line of code."

Don't treat the harness as static. Schedule entropy management as a recurring process — it is one of the most durable advantages of agent-maintained codebases over human-maintained ones.

## File-Backed State in Practice: Framework Artifact Architectures

Before reading the arXiv theory, note how production frameworks implement file-backed state:

**GSD** (`.planning/` directory):
`PROJECT.md` → `REQUIREMENTS.md` → `ROADMAP.md` → `STATE.md` (current position) → `N-CONTEXT.md` (per-phase decisions) → `N-M-PLAN.md` (atomic tasks) → `N-M-SUMMARY.md` (execution results) → `N-VERIFICATION.md` (gaps) → `UAT.md` (acceptance tests)

Every artifact is path-addressable, compaction-stable, and written by one agent to be read by the next. `STATE.md` is the harness equivalent of `claude-progress.txt` — but updated by `gsd-tools.cjs` (deterministic code, not the agent) to prevent formatting drift.

**Ralph Wiggum**: `specs/` (feature requirements) + `IMPLEMENTATION_PLAN.md` (task progress) + `logs/` (full session traces) + `completion_log/` (finished work records). The DONE signal is only emitted after criteria pass — the bash wrapper, not the agent, controls when the loop advances.

**Kiro**: `requirements.md` + `design.md` + task list — all generated per-feature from a natural language prompt. EARS notation makes requirements machine-verifiable: "When [condition], the system shall [action]."

**GitHub Spec Kit**: spec artifact + technical plan + task list — persisted in the project, consumed by every subsequent agent session.

The pattern is consistent across all frameworks: externalized, path-addressable, compaction-stable state. The arXiv research names the properties; the frameworks demonstrate what they look like at production scale.

## File-Backed State (arXiv Research)

From arXiv 2603.25723, file-backed state modules are a foundational pattern for multi-session and multi-agent work.

State must be:
- **Externalized**: written to artifacts (files), not held in memory
- **Path-addressable**: later sessions and agents can reopen state by path
- **Compaction-stable**: state survives context truncation and session restart

Examples: `feature_list.json`, `claude-progress.txt`, `git history`. These aren't just convenience — they are the mechanism by which agent state persists across context boundaries.

## Harness Contracts (arXiv Research)

From arXiv 2603.25723, every agent call in a well-designed harness should have an explicit contract:

- Required inputs and expected outputs
- Format constraints and validation gates
- Permission boundaries (what the agent can and cannot do)
- Artifact paths (where outputs are written)
- Budget constraints (token limits, iteration limits)

This makes delegation inspectable and enables recovery when agents fail partway through.

## Context Overflow Intervention (DeepSeek-V3.2)

DeepSeek-V3.2 documented specific strategies triggered when token usage exceeds **80% of the context window** — the point where context anxiety sets in before a hard limit is reached.

| Strategy | Mechanism | When to use |
|---|---|---|
| **Summary** | Compress the overflowed trajectory into a structured narrative | Preserve semantics; acceptable latency |
| **Discard-75%** | Drop oldest 75% of tool call history; retain recent context | Fast; when recent work is most relevant |
| **Discard-all** | Full context reset with handoff artifacts | Maximum headroom; use with session-handoff pattern |

The 80% threshold is the actionable harness trigger point. Build monitoring that detects this threshold and applies the appropriate strategy rather than waiting for the model to exhibit context anxiety behavior.

## Adaptive Context Management

From arXiv 2603.05344 (OpenDev coding agent):

**Tiered compression**: as token budget nears exhaustion, implement progressive compression — summarize aged observations aggressively while preserving recent interactions.

**Dual-memory architecture**:
- Episodic memory: full conversation history for recent context
- Working memory: extracted facts, decisions, and patterns for quick reference

**Event-driven reminders**: inject targeted behavioral guidance at decision points rather than relying solely on initial instructions. Initial instructions fade out in extended sessions. Reminders at key decision points (tool failures, iteration counts, approval changes) maintain consistency.

**Dynamic system prompt composition**: assemble instructions from conditional, priority-ordered sections that load based on context. Reduces overhead while maintaining comprehensive guidance.

## Centralized vs. Distributed State Management

Two valid architectural patterns for who owns the state ledgers in a multi-agent harness:

**Distributed (Anthropic pattern)**: The coding agent manages its own state. It reads and writes `feature_list.json` and `claude-progress.txt` directly. Agents are self-directing — they orient themselves from the artifacts on each session start.

**Centralized (Microsoft Magentic-One pattern)**: A dedicated orchestrator agent maintains the task ledger and progress ledger. Individual agents are stateless — they receive context from the orchestrator and return results. The orchestrator selects which agent acts next and re-plans when progress stalls.

| | Distributed | Centralized |
|---|---|---|
| Agent role | Self-directing | Stateless specialist |
| State ownership | Each agent | Orchestrator |
| Best fit | Single-agent, multi-session | Multi-agent, specialized roles |
| Framework dependency | None (file-based) | Orchestrator framework required |

Centralized state is more suitable when agents have narrow, specialized roles (browser, file, code, shell) and the orchestrator needs to dynamically route between them. Distributed state is more suitable when a single agent needs to self-direct across sessions without framework infrastructure.

## Per-Agent Context Scoping (OpenClaw pattern)

In multi-agent harnesses, each agent should have its own scoped context — not just a shared project-level `CLAUDE.md`. OpenClaw's `SOUL.md` pattern applies this:

- Each agent has a dedicated `SOUL.md` defining its role, capabilities, constraints, and persona
- **Agent isolation**: separate workspace, state directory, and session storage per agent — no automatic credential or state sharing
- **Skill allowlists**: per-agent tool filtering — a research agent gets web search; a coding agent gets file and shell tools; an evaluator gets Playwright but not write access

This maps directly to the "non-overlapping responsibilities" and "contracts" principles from arXiv 2603.25723. In a three-agent planner/generator/evaluator setup, each agent's scoped context prevents it from taking actions outside its role.

**Deterministic routing**: rather than using an LLM to decide which agent handles a request, bind routing rules deterministically — by task type, input format, or explicit handoff from the previous agent. "Most-specific wins" routing eliminates a class of orchestration failures where the routing LLM makes wrong decisions.

**Security**: per-agent skill allowlists also enforce a security boundary. An agent that only has read tools cannot accidentally (or via prompt injection) take write actions. Audit any third-party skills before granting them to any agent in your harness.

## Model-Agnostic Harness Design

Design harnesses to function across multiple AI providers. Build context engineering, constraints, and state management in a way that doesn't assume a specific model's behavior.

As models improve, assumptions encoded in the harness may no longer hold. Test components individually. Remove anything that is no longer load-bearing. Re-examine on every major model update.

## Multi-Model Routing

For complex harnesses, different models can handle different cognitive tasks:
- Thinking phase: deeper reasoning model (higher cost, slower)
- Execution phase: faster model
- Critique/evaluation phase: verification model

This compounds capabilities more efficiently than using a single model for all tasks. Configure per-workflow rather than globally.

## Harnessability Assessment

Not all codebases are equally amenable to harnessing. Before designing a harness for an existing codebase:

Higher harnessability:
- Typed languages with explicit interfaces and semantic type names
- End-to-end type coverage (application + API + database + third-party clients)
- Clear module boundaries and separation of concerns
- Established frameworks with conventions
- Comprehensive test coverage

Lower harnessability:
- Loosely typed or dynamically typed code with implicit contracts
- Untyped API boundaries (no OpenAPI spec, hand-written HTTP clients)
- Database without constraints or typed client generation
- Legacy systems with entangled concerns
- Inconsistent naming and structure
- Missing or broken tests

Legacy systems need harnesses most but face implementation challenges. Address harnessability gaps (adding types, breaking apart entangled modules, adding tests) before expecting high agent reliability.

**Types as the highest-leverage harnessability investment**: typed languages with semantic names eliminate illegal states, shrink the agent's search space, and provide guaranteed-current in-context documentation. The investment in end-to-end type coverage pays back on every agent session. See [type-system-design.md](type-system-design.md) for the full stack treatment (TypeScript, OpenAPI, Postgres + Kysely, third-party wrapping).

## Dependency Selection as a Harness Decision (OpenAI)

The context constraint — "anything the agent can't access in-context doesn't exist" — applies to dependencies as well as to documentation and state.

> "We favored dependencies and abstractions that could be fully internalized and reasoned about in-repo. Pulling more of the system into a form the agent can inspect, validate, and modify directly increases leverage."

**Prefer "boring" technology:**
Technologies described as boring tend to be higher harnessability choices:
- **Composable**: behavior can be understood from its parts, not just from end-to-end tests
- **API-stable**: fewer surprise breakages for the agent to work around
- **Well-represented in training data**: the model has strong priors for standard patterns; exotic abstractions require more correction

Bleeding-edge, opaque, or heavily-magic frameworks reduce agent leverage even when they improve developer ergonomics.

**Deliberate reimplementation:**
OpenAI found that for small, well-scoped behaviors, reimplementing a subset of a library's functionality is sometimes cheaper than working around opaque upstream behavior. Their example: rather than using a generic `p-limit`-style concurrency package, they implemented a custom `map-with-concurrency` helper:
- Tightly integrated with their OpenTelemetry instrumentation
- 100% test coverage
- Behavior exactly matched to their runtime expectations

The agent can read, validate, and modify the in-repo implementation directly. It cannot do the same for an opaque upstream library.

**The leverage principle:**
> "Pulling more of the system into a form the agent can inspect, validate, and modify directly increases leverage — not just for Codex, but for other agents."

This is the dependency corollary to the context engineering rule: just as all guiding knowledge must live in the repo, the code the agent needs to understand and modify benefits from living in the repo too. Each opaque dependency is a partial context hole.

**Practical heuristic — apply to new dependency decisions:**

| Factor | Prefer | Avoid |
|---|---|---|
| Transparency | In-repo helpers, well-known stdlib | Magic frameworks, complex DSLs |
| Stability | APIs with long stability guarantees | Rapidly-evolving packages |
| Training representation | Widely-used standard patterns | Niche or internal-only abstractions |
| Scope | Narrow, single-purpose | Sprawling, many-behavior packages |
| Auditability | Open, readable source | Minified, generated, or compiled-only |

This doesn't mean always rolling your own — it means weighing inspectability as a first-class dependency criterion alongside capability and maintenance cost.

## Agent-Computer Interface (ACI) Design

Tool design is a first-class engineering discipline. For the full ACI guide — tool format principles, poka-yoke parameters, when to promote an action to a tool, structured tool output, agent-driven context building, and context rot — see **[aci-design.md](aci-design.md)**.
