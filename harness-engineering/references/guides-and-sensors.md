# Guides and Sensors

Source: Martin Fowler, "Harness engineering for coding agent users" (martinfowler.com)

## Table of Contents

- [The Core Framework](#the-core-framework) — guides vs. sensors
- [Control Types](#control-types) — computational vs. inferential
- ["Keep Quality Left"](#keep-quality-left)
- [Three Regulation Dimensions](#three-regulation-dimensions) — autonomy, breadth, quality
- [Spec-Driven Frameworks as Pre-Built Guide Systems](#spec-driven-frameworks-as-pre-built-guide-systems)
- [Designing Guides](#designing-guides) — CLAUDE.md, bootstrap scripts, architectural constraints
- [LSP Integration as a Write-Time Sensor](#lsp-integration-as-a-write-time-sensor)
- [Designing Sensors](#designing-sensors) — tests, linters, evaluator agents
- [100% Code Coverage as a Harness Constraint](#100-code-coverage-as-a-harness-constraint-openai)
- [Entropy Agents: Scheduled Sensors](#entropy-agents-scheduled-sensors)
- [Parallel Guardrails](#parallel-guardrails) — screening agent in parallel with response agent
- [Human-in-the-Loop as a Sensor](#human-in-the-loop-as-a-sensor) — confidence scorer; HaaT pattern
- [Harnessability and Sensors](#harnessability-and-sensors) — legacy codebase onboarding
- **Advanced patterns** → [sensor-infrastructure.md](sensor-infrastructure.md): typed lifecycle events, async notification, autonomy tiers, constitutional constraints, preprocessing hooks, session scope threshold, emergent behavior signals

---

## The Core Framework

All harness components are either guides (feedforward) or sensors (feedback).

**Guides (feedforward controls)**:
- Anticipate and prevent unwanted behavior before it occurs
- Increase probability of quality first-time results
- Examples: documentation, architectural rules, bootstrap scripts, code mods, `CLAUDE.md`

**Sensors (feedback controls)**:
- Monitor outputs after execution
- Enable self-correction loops
- Most powerful when optimized for LLM consumption — custom linter messages written as positive prompt injection

The goal is not to pick one — effective harnesses use both. Guides reduce defect introduction; sensors catch what slips through.

## Control Types

Controls differ in cost, speed, and reliability:

| Type | Mechanism | Speed | Cost | Reliability |
|---|---|---|---|---|
| **Computational** | Tests, linters, type checkers, static analysis | Milliseconds–seconds | Low | Deterministic |
| **Inferential** | AI code review, LLM judges, evaluator agents | Seconds–minutes | Higher | Non-deterministic |

Use computational controls for everything they can cover. Reserve inferential controls for semantic judgment that deterministic tools can't handle.

Custom linter error messages are a particularly effective guide: they're read by the agent during execution and can be written as instructive guidance rather than just error codes.

## "Keep Quality Left"

Distribute checks across the development lifecycle based on cost and speed. Don't run expensive checks where fast ones will do.

```
Pre-commit     → Fast linters, basic format checks, unit tests
                 (run every time, milliseconds)

Post-integration → Expensive analyses, comprehensive test suites,
                   LLM-based auditors
                   (run on merge, minutes)

Continuous      → Drift detection, entropy management,
                  architectural compliance
                  (scheduled, hours)
```

Moving checks left (earlier in the lifecycle) reduces the cost of fixing issues. A constraint enforced at pre-commit catches problems before they compound.

## Three Regulation Dimensions

Harnesses regulate along three dimensions. They have different maturity levels and different tooling:

### 1. Maintainability Harness
Internal code quality: readability, testability, documentation, naming.

Most mature dimension — extensive tooling exists. Linters, formatters, complexity analyzers, documentation generators. Start here.

Examples: ESLint, Prettier, Black, flake8, SonarQube, code coverage thresholds.

### 2. Architecture Fitness Harness
Architectural characteristics: performance, observability, security, scalability, dependency structure.

Less mature than maintainability but improving. Requires intentional design.

Examples:
- ArchUnit (Java), Dependency Cruiser (JS) — enforce dependency rules
- Bundle size analyzers
- Performance regression tests
- Security scanners (Snyk, Dependabot)
- Observability requirements (all new endpoints must emit traces)

**Dependency inspectability as a fitness criterion** (OpenAI): In agent-maintained codebases, the Architecture Fitness Harness should include a dependency inspectability check — a gate that flags new dependencies that are opaque, magic-heavy, or poorly-represented in model training data. Prefer "boring" technology that agents can fully reason about. See [context-engineering.md](context-engineering.md) for the full dependency selection principle and heuristic table.

### 3. Behaviour Harness
Functional correctness: does the software do what users expect?

Least mature and hardest to harness. Most reliant on inferential (LLM-based) controls. Playwright/Puppeteer-based end-to-end testing is the current best practice for catching behavioral regressions.

The evaluator in the three-agent architecture is primarily a behaviour harness.

## Spec-Driven Frameworks as Pre-Built Guide Systems

Spec-driven workflow frameworks (GitHub Spec Kit, GSD, Ralph Wiggum, BMAD, SPARC, Kiro) are packaged implementations of the guides layer. Rather than building specification and planning artifacts from scratch, they provide:

- Structured templates for constitution → spec → plan → tasks
- Slash commands that drive agent behavior through each phase
- Pre-defined artifact schemas that persist state across sessions

They differ primarily in how much of the sensor layer they also include:

| Framework | Guides coverage | Sensors included |
|---|---|---|
| GitHub Spec Kit | Strong (spec→plan→tasks) | None — human review only |
| GSD | Strong + plan validation (10-dim) | gsd-verifier, goal-backward, UAT.md |
| Ralph Wiggum | Spec + acceptance criteria | Self-verify via DONE signal |
| BMAD | Full SDLC personas | Multi-persona review checkpoints |
| SPARC | TDD-phase discipline | Refinement phase as evaluator loop |
| Kiro | EARS notation + agent hooks | Hooks as automated sensors |

See [spec-driven-workflows.md](spec-driven-workflows.md) for full detail on each framework.

## Designing Guides

Effective guides share these properties:

**Specific over vague**: "Components must use named exports" is actionable. "Write clean code" is not.

**Subject to an instruction budget**: for Claude Code specifically, CLAUDE.md is advisory (not deterministic) with a practical ceiling of ~150–200 instructions before compliance drops. Every unnecessary line dilutes the ones that matter. Keep the root file lean; use subdirectory CLAUDE.md files and `.claude/rules/*.md` with path scoping for domain-specific rules. See [claude-md-design.md](claude-md-design.md) for the full 4-layer system and maintenance pattern.

**Machine-enforceable**: If a rule can't be checked automatically, it will be inconsistently applied. Prefer rules that can be encoded as linter rules, structural tests, or pre-commit hooks.

**Written for LLM consumption**: When guides are read by an agent (e.g., `CLAUDE.md` rules, linter messages), write them as positive instruction rather than prohibition. "Use `import type` for type-only imports" outperforms "Don't use regular imports for types."

**Repository-local**: All guides must live in the codebase. Guides in Slack or Google Docs don't exist from the agent's perspective.

**Mechanically enforced** (OpenAI): The knowledge base itself should be subject to CI validation — not just code. Dedicated linters and CI jobs validate that documentation is:
- Up to date (matched to actual code behavior)
- Cross-linked (references between docs resolve correctly)
- Structurally correct (required sections present, verification status populated)

This is the distinction between a knowledge base that is a convention and one that is a constraint. Conventions degrade over time; constraints are maintained by the CI pipeline. See [context-engineering.md](context-engineering.md) for the full structured knowledge base pattern.

**Taste invariants** (OpenAI): Beyond structural rules, encode human aesthetic judgment as lints. Examples: structured logging enforcement, naming conventions for schemas and types, file size limits, platform reliability requirements. The key advantage: because these lints are custom, their error messages can be written as remediation instructions — injecting actionable guidance into agent context at the moment of violation. An agent that reads "Error: log calls must use structured logging. Use `logger.info({ event, data })` instead of `logger.info(message)`" can self-correct without further investigation.

**The "promote rule into code" ratchet** (OpenAI): When documentation falls short of reliably enforcing a rule, promote the rule into tooling — a linter, structural test, or pre-commit hook. Review comments, refactoring PRs, and user-facing bugs are all inputs to this process.

> "In a human-first workflow, these rules might feel pedantic or constraining. With agents, they become multipliers: once encoded, they apply everywhere at once."

For concrete implementation — ESLint custom rules, Semgrep YAML rules, Ruff plugins, golangci-lint analyzers, pre-commit integration, and message design patterns:
See [agent-readable-lints.md](agent-readable-lints.md).

See [context-engineering.md](context-engineering.md) → "Architectural Constraints" for the full layered domain architecture pattern and taste invariants detail.

## LSP Integration as a Write-Time Sensor

Source: OpenCode documentation; Kristopher Dunham (2026); Maik Kingma, "Give Your AI Coding Agent Eyes" (Feb 2026); Claude Code v2.0.74 changelog (Dec 2025).

Standard agent sensors fire at pre-commit or CI time. Language Server Protocol (LSP) integration moves error detection to the moment a file is saved — before any build, before any test run.

When an agent writes code and saves a file, the LSP throws a diagnostic immediately: type errors, undefined references, unreachable code, call signature mismatches. That diagnostic is routed back into the model's context window. The agent sees its own mistakes and corrects them before the file is even staged.

This is a qualitatively different timing:

| Sensor timing | When errors are caught | Cost of fix |
|---|---|---|
| Pre-commit hooks | After the full change is drafted | Medium — agent must revise completed work |
| CI gates | After merge to branch | High — potentially many files to unwind |
| LSP diagnostics | At file save during writing | Lowest — caught in the same edit |

**What LSP sensors provide that linters don't**: semantic understanding. An LSP-connected agent doesn't match strings — it uses `goToDefinition`, `findReferences`, and call hierarchy analysis. When renaming a polymorphic method across 200 service files, the agent uses semantic references to know exactly what is a definition, a call, and a type annotation. String matching would miss aliased calls and incorrectly rename comments.

**How it works in practice**: configure the agent environment with LSP server access for your language stack (TypeScript, Python, Java, Rust, Go, PHP are commonly supported). The agent writes a file → LSP processes the save → diagnostics route back as context → agent corrects before moving to the next file. The build sees clean code because the agent already fixed everything the LSP caught.

**Harness implication**: if your codebase has strong type coverage (see [type-system-design.md](type-system-design.md)), an LSP sensor turns type errors into real-time agent feedback at near-zero additional cost. The sensor is only as good as the type coverage it can observe — another reason to invest in end-to-end types before adding agentic workflows.

**LSP goes beyond diagnostics**: diagnostics are the most common harness use, but LSP also provides goToDefinition, findReferences, workspaceSymbol, documentSymbol, call hierarchy, semantic rename, code actions, hover, inlay hints, type hierarchy, and goToImplementation. Each of these can be used as an agent tool — reducing context consumption for navigation, enabling reliable large-scale refactoring, and giving the agent IDE-quality understanding of the codebase.

For full capability inventory, tool integrations (Claude Code, OpenCode, oh-my-pi, oh-my-openagent, Kiro), limits and failure modes, and tree-sitter alternatives:
See [lsp-code-intelligence.md](lsp-code-intelligence.md).

## Designing Sensors

Effective sensors share these properties:

**Actionable output**: Sensor output is only valuable if the agent can act on it. Include enough context in error messages and evaluator feedback that the agent can fix the issue without additional investigation.

**Calibrated thresholds**: For inferential sensors (LLM evaluators), calibrate the threshold explicitly. Default LLM evaluation is too permissive — evaluators need to be tuned toward skepticism.

**Appropriate timing**: Fast sensors (linters, type checks) run pre-commit. Slow sensors (Playwright end-to-end, LLM evaluators) run on sprint completion or post-integration.

## 100% Code Coverage as a Harness Constraint (OpenAI)

> "Coverage, as we use it, isn't strictly about bug prevention; it's about guaranteeing the agent has double-checked the behavior of every line of code it wrote."

The usual objection to 100% coverage is that it's a metric being gamed. That's not the harness engineering rationale. The rationale is about **removing degrees of freedom from the agent** and **forcing behavioral demonstration**.

**The phase change argument:**

| Coverage level | What it means |
|---|---|
| 95% | Someone decided what was "important enough" to test — ambiguous, judgment-dependent |
| 99.9% | A specific uncovered line exists; unclear whether it was there before your changes |
| 100% | No ambiguity. If a line isn't covered, you actively just introduced it |

At 100%, there is no inference required. The coverage report is a simple todo list: every uncovered line is a test you still need to write. The agent can't stop at "this seems right" — it has to produce an executable example demonstrating how the line behaves.

**What this does to the agent's behavior:**
- Forces the agent to write a test for every code path it adds — including edge cases and error paths
- Unreachable code gets deleted (the coverage report surfaces it immediately)
- Edge cases are made explicit in tests rather than implicit in unverified code
- The agent cannot declare a feature complete if any line it wrote is uncovered

**Coverage as a sensor:**
The coverage report is a computational sensor — deterministic, fast, and zero-inference. It maps directly to the Build-Verify Loop pattern: the verify step isn't "does the agent think this is correct?" but "is every line covered by a passing test?" CI gates on 100% enforce this mechanically.

**Code reviews improve too:**
Every aspect of how the system is expected to behave or change is represented by a concrete, executable example. Reviewers don't need to infer intent from implementation — the tests show it.

**The step-function in leverage:**
At sub-100% coverage, tests provide incremental confidence. At 100%, the leverage experiences a step-function increase: the test suite becomes a complete behavioral specification of every line in the codebase, machine-verifiable on every run.

This belongs in the CI pipeline, not just as a guideline. Enforce it as a gate that fails the build — the same way a type error fails the build.

## Entropy Agents: Scheduled Sensors

Pre-commit hooks and CI gates catch violations as they're introduced. Entropy agents catch violations that already exist — accumulated drift that no single commit introduced.

**Doc-gardening agent** (OpenAI):
A scheduled agent that scans documentation against the actual code and opens fix-up pull requests where they diverge. This is the Continuous tier of the timing pyramid made concrete.

Why this is necessary in agent-maintained codebases: agents modify code without reliably updating the documentation that future agents will read. Without a gardening agent, the CLAUDE.md, architecture docs, and inline docs that guide future sessions quietly become wrong. Each wrong document degrades all future sessions that rely on it.

**Typical entropy agent responsibilities:**

| Agent | What it scans | Output |
|---|---|---|
| Doc-gardening | Docs vs. source code behavior | Fix-up PRs |
| Constraint scanner | Code vs. linter/style rules | Issue list or PRs |
| Convention checker | Patterns vs. established conventions | Violations report |
| Dependency auditor | Import graph vs. allowed layering | Refactor tasks |
| Harness optimizer | Execution traces vs. harness effectiveness | Harness improvement proposals (see Meta-Harness in middleware-patterns.md) |

**The garbage collection framing:**
Treat entropy management like a runtime garbage collector — running continuously in the background, reclaiming space before it becomes a problem. The alternative is the "Friday cleanup" model: manual intervention only when things are visibly broken, at which point patterns have already spread through the codebase for days or weeks.

OpenAI measured the cost of the Friday model: 20% of the working week consumed by manual "AI slop" cleanup before they replaced it with background agents. That cadence didn't scale.

> "Human taste is captured once, then enforced continuously on every line of code."

**Implementation guidance:**
- Trigger: cron (nightly or weekly) or on-merge to main — not at every commit (too slow)
- Scope: incremental scan of changed files first; full scan less frequently
- **Output as small, targeted PRs** — scoped to one pattern or one file type; reviewable in under a minute; most can be automerged after CI passes
- Avoid large refactor PRs: they sit unreviewed and undermine the continuous-small-payments model
- A surge of cleanup PRs is a signal that agents are drifting faster than entropy management can catch — check whether golden principles need strengthening or new violations need new rules

## Parallel Guardrails

Source: Anthropic, "Building effective agents" (December 2024)

Guardrail checks (safety screening, content filtering, policy validation) are commonly implemented in series: the request goes through the guardrail first, then reaches the response agent. This is correct but adds latency proportional to guardrail execution time.

For latency-sensitive workflows, run the guardrail agent in **parallel** with the response agent:

```
User request → [Response agent]    → synthesize → output
            ↘ [Guardrail agent] ↗
```

Both agents receive the same input simultaneously. The synthesizer waits for both to complete: if the guardrail passes, the response is returned; if it fails, the response is blocked regardless of quality.

**When this works:** when the guardrail's decision is independent of the response content — screening the *input* for policy violations, inappropriate content, or safety issues. The guardrail doesn't need to see what the response agent produced.

**When it doesn't:** when the guardrail needs to evaluate the *response* (e.g., checking that the answer doesn't reveal confidential data). That requires the response first and must remain sequential.

**Harness implication:** parallelization reduces wall-clock latency without reducing safety coverage. Each agent focuses on one concern — the response agent optimizes for quality; the guardrail agent optimizes for detection. Separation of concerns also makes each easier to improve independently.

## Human-in-the-Loop as a Sensor

Human review is a sensor — the highest-fidelity, highest-cost feedback control available. Design explicit interrupt points rather than relying on humans to notice problems in the output stream.

**LangGraph pattern**: built-in interrupt nodes pause execution at defined points for human review, then resume. Apply interrupts at:
- Before irreversible actions (deploys, database writes, external API calls)
- After each sprint completion, before marking features passing
- When loop detection middleware fires (agent is stuck)
- When evaluator scores fall below threshold

**Cost management**: human-in-the-loop is expensive in wall-clock time. Reserve interrupt points for decisions that require judgment, not mechanical checks. Mechanical checks belong in computational sensors (linters, tests). Judgment calls — "does this meet the design standard?" — belong at human interrupt points.

**Escalation policy**: define in advance what triggers a human interrupt vs. what the agent handles autonomously. Document this in `CLAUDE.md` so the agent knows when to pause and surface a decision rather than proceeding.

**Confidence Scorer → Human-as-a-Tool (HaaT)** (Agentic Architectural Patterns):
Rather than treating human intervention as an exception (the agent crashes; a human manually intervenes), model it as a first-class tool call triggered by a confidence threshold.

The pattern:
1. The agent maintains an internal confidence score for its current reasoning path
2. When the score drops below a threshold (e.g., < 0.7), the agent does not fail — it "calls" the human
3. It packages its current state, reasoning history, and the specific question into a structured payload
4. A human reviews the package via a standardized UI component and responds
5. The agent resumes from that decision point with the human input as context

The distinction from ad-hoc escalation: the human escalation becomes a **planned state in the agent's lifecycle**, not a crash handler. The agent remains autonomous where it has confidence; it escalates where it doesn't. This is preferable to both "never escalate" (agent makes bad decisions autonomously) and "always escalate" (defeats the purpose of the agent).

**Confidence signals to monitor**: consecutive tool call failures, LLM output that doesn't match expected schema, loop detection middleware firing, deviation from the sprint contract's stated success criteria.

## Advanced Sensor Infrastructure

For Level 2–3 patterns — typed lifecycle events, async human notification, autonomy tiers, constitutional constraints, preprocessing hooks, session scope thresholds, and emergent behavior as harness gap signals — see **[sensor-infrastructure.md](sensor-infrastructure.md)**.

## Harnessability and Sensors

Sensors are only as good as what they can observe. A codebase without tests gives sensors nothing to measure. A codebase without type annotations gives type checkers nothing to enforce.

When onboarding a legacy codebase to an agent workflow:
1. Identify what sensors are possible given current code state
2. Add missing instrumentation (tests, types, observability)
3. Establish baselines before adding agent workflows
4. Add sensors incrementally rather than attempting comprehensive coverage immediately
