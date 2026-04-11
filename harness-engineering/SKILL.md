---
name: harness-engineering
description: Design and build reliable harnesses for AI agents — the environment of constraints, tools, feedback loops, and handoff artifacts that determines whether agents succeed or fail. Use when designing multi-session agent workflows, debugging why agents keep failing on long tasks, building multi-agent systems (planner/generator/evaluator), setting up context engineering and architectural constraints for a codebase, or evaluating harness quality. Core principle: Agent = Model + Harness. A more capable model inside a poorly designed harness will still fail in the same ways.
---

# Harness Engineering

A harness is not a prompt or a system message. It is the full environment built around a model: constraints, tools, feedback loops, handoff artifacts, and structure that determines whether an agent succeeds or fails.

**Agent = Model + Harness.** A more capable model inside a poorly designed harness fails in the same ways. Harness design becomes more important as models improve, not less — better models reveal new capability boundaries worth exploring with novel harness combinations.

**The code is a byproduct.** The generated files, the passing tests, the shipped PR — these are evidence of the coordination system, not the thing itself. When Sigrid Jin built a clean-room Python rewrite of Claude Code's architecture in two hours while asleep (claw-code, 2026), what impressed observers was the wrong layer. The Python files were the byproduct. The clawhip-based agent coordination system that produced them while the developer was asleep was the actual achievement. Build the system; the code follows.

**The model is a commodity; the harness is the durable investment.** The project configuration, tool permissions, workflow integrations, and AGENTS.md encoding team standards — that infrastructure persists across every model change. The LLM can be replaced. The harness cannot.

**The bottleneck shifts, not disappears.** As agents get faster, execution bandwidth approaches free. What becomes expensive: knowing what to build, why, and how the pieces should fit together. Architectural clarity and task decomposition get *more* valuable as agents improve, not less. A badly directed team of fast agents produces a lot of wrong code very quickly.

## The Seven-Layer Minimal Architecture

Source: "Everything I Learned About Harness Engineering and AI Factories in San Francisco" (April 2026)

Every production harness has seven layers. Any weak layer causes system regression:

| Layer | What it handles |
|---|---|
| **1. Intent capture** | Translating what the human actually wants into unambiguous direction |
| **2. Spec/issue framing** | Decomposing intent into discrete, verifiable work items |
| **3. Context and instruction layer** | CLAUDE.md, rules, architectural constraints — what the agent knows before starting |
| **4. Execution layer** | The agent doing the work |
| **5. Verification layer** | Tests, evaluators, coverage gates — confirming work is actually done |
| **6. Isolation and permission layer** | Worktrees, capability restrictions, tool allowlists — constraining blast radius |
| **7. Feedback loop** | What the harness learns from failures and improves |

The five harness elements described below map to this architecture: task decomposition = layers 1–2, session continuity = layer 3, external evaluation = layer 5, mechanical constraints = layer 6, incremental verification = layers 5+7.

## The Four Agent Failure Modes

Before designing a harness, understand why agents fail. See [failure-modes.md](references/failure-modes.md) for depth.

1. **Doing everything at once** — no decomposition, burns context, leaves half-built codebase
2. **Context anxiety** — as context window fills, agent wraps up prematurely (observed in Claude Sonnet 4.5)
3. **Declaring victory too early** — agent sees progress, concludes project is done even with features unbuilt
4. **Self-evaluation bias** — agents almost always approve their own output, even when broken
5. **Pattern replication** — agents amplify existing bad patterns in the codebase; entropy compounds across sessions without a recurring cleanup process (OpenAI measured this at 20% of the working week before systematizing)
6. **Over-delegation** — orchestrators split tasks that are not actually independent, paying for parallel context windows to produce an answer worse than a single session would have given. The fix is an explicit independence test before any fan-out. See [generator-evaluator-loop.md](references/generator-evaluator-loop.md) → "Decomposition and the Independence Test."

The failure cycle: high-level prompt → agent attempts everything → context fills → wraps up early → session ends with no docs/git commit → next session starts blind → cycle repeats.

## The Five Harness Elements

Every reliable harness addresses all five:

| Element | What it solves |
|---|---|
| **Task decomposition** | Prevents "do everything at once" — discrete, verifiable units vs. open-ended goals |
| **Session continuity** | Prevents blind starts — progress files + git history so each session picks up where the last ended |
| **External evaluation** | Prevents self-evaluation bias — a separate agent or process grades output |
| **Mechanical constraints** | Prevents drift — rules the model cannot override |
| **Incremental verification** | Prevents "declaring victory" — test each unit as a real user would before marking complete |

## Choosing an Architecture

**Minimal starting point — no framework required:**
Before adopting any architecture, two Claude Code tabs already eliminate most of the sequential waiting that dominates single-session development. Assign each tab a session type:

| Session Type | What it does |
|---|---|
| **Critique** | Argues against the plan before any building starts |
| **Implementation** | Builds the feature |
| **Simplification** | Reviews output for redundancy and unnecessary abstractions |
| **Review** | Checks correctness, security, spec compliance |
| **Testing/Docs** | Generates tests or documentation from the completed implementation |

The bottleneck in agentic development is rarely writing code — it's reviewing it. Running implementation in one tab and simplification/review in a second tab, in parallel, costs nothing and requires no installation. Start here; add framework machinery when this ceiling is hit.

**For single-agent, multi-session work** (most common starting point):
Use the initializer + coding agent pattern. Simple, effective for focused builds.
See [session-handoff-pattern.md](references/session-handoff-pattern.md).

**For complex builds requiring quality gates**:
Use the three-agent generator-evaluator loop (planner → generator → evaluator).
See [generator-evaluator-loop.md](references/generator-evaluator-loop.md).

**For team/org-level codebases**:
Apply context engineering: machine-readable rules, architectural constraints, entropy management, and structured knowledge base with mechanical CI enforcement.
See [context-engineering.md](references/context-engineering.md).

**Technology selection principle** (OpenAI): Before writing a line of code, prefer dependencies that are "boring" — composable, API-stable, well-represented in training data, and readable in-repo. An agent cannot fix bugs in opaque upstream libraries. In some cases, reimplementing a narrow subset of a library's behavior as in-repo code (fully tested, instrumented) outperforms using the library. See [context-engineering.md](references/context-engineering.md) → "Dependency Selection as a Harness Decision".

**Tool design (ACI)**: poka-yoke parameters, when to promote an action to a tool, structured output over format instructions, agent-driven context building over RAG injection.
See [aci-design.md](references/aci-design.md).

**Filesystem as navigation interface** (OpenAI): Agents navigate by listing directories and reading filenames before opening files. Treat directory structure and file naming as a first-class interface. `./billing/invoices/compute.ts` communicates domain and responsibility before the agent reads a single line; `./utils/helpers.ts` communicates nothing. Prefer many small well-scoped files — agents truncate large files when loading them; a file short enough to load in full stays entirely active in context. See [context-engineering.md](references/context-engineering.md) → "The Filesystem as Navigation Interface".

**End-to-end types** (OpenAI): Use a typed language and push type coverage across the full stack — application layer (TypeScript strict mode, semantic type names), API layer (OpenAPI + generated clients), database layer (typed ORM + constraints), third-party clients (wrap to give good types). Types eliminate illegal states the agent can construct, shrink the search space of possible actions, and provide guaranteed-current in-context documentation. Semantic names (`UserId`, `WorkspaceSlug`) are searchable; `string` is not. See [type-system-design.md](references/type-system-design.md).

## Quick-Start Harness Checklist

For any new agentic project, establish these before the first coding session:

- [ ] `CLAUDE.md` or `AGENTS.md` with project rules, stack, naming conventions — keep under 150-200 lines; use subdirectory files for domain-specific rules; see [claude-md-design.md](references/claude-md-design.md) and [hooks.md](references/hooks.md) for enforcement
- [ ] `feature_list.json` — all features listed, all marked `"passes": false`
- [ ] `claude-progress.txt` — session log the agent writes to at end of each session
- [ ] `init.sh` — starts dev server, runs baseline end-to-end test
- [ ] Initial git commit capturing the baseline
- [ ] Explicit constraint: "It is unacceptable to remove or edit tests"
- [ ] Agent instruction: work on ONE feature at a time

## Intent Before Planning

Before the planner sees the prompt, resolve two distinct things — in order:

1. **Intent clarification** — resolve *what to build*. An ambiguous prompt fed to a planner produces a spec built on inferred intent; those errors cascade through everything the generator builds. Sequence: **interview → plan approval → execute**. The planner gets a resolved spec; the generator gets an approved plan.

2. **Adversarial critique** — challenge *how to build it*. Before any planning begins, ask the agent to argue against your proposed approach. Effective prompts: "What are the three strongest reasons this architecture is wrong?" / "What would a senior engineer regret about this decision three years from now?" / "What am I assuming that might not be true?" This is upstream of intent clarification — it catches consequential architectural mistakes before they become specs. It takes five minutes and prevents the most expensive class of rework: building correctly what should not have been built that way.

These are different steps. Intent clarification resolves scope; adversarial critique challenges approach. Both belong before planning.

See [generator-evaluator-loop.md](references/generator-evaluator-loop.md) → "Intent-First Routing" (intent clarification) and "Adversarial verification" (post-generation adversarial evaluation).

## Controls: Guides and Sensors

All harness components are either guides (feedforward) or sensors (feedback).

- **Guides**: prevent problems before they occur — documentation, architectural rules, bootstrap scripts
- **Sensors**: catch problems after they occur — tests, linters, evaluator agents, CI checks

For the full framework including computational vs. inferential controls and "keep quality left":
See [guides-and-sensors.md](references/guides-and-sensors.md).

For Level 2–3 sensor infrastructure (typed lifecycle events, async notification, autonomy tiers, constitutional constraints):
See [sensor-infrastructure.md](references/sensor-infrastructure.md).

**Agent-readable lint rules**: custom lint rules where the error message is the remediation instruction — the agent reads it from tool output and applies the fix without human explanation. Covers ESLint, Semgrep, Ruff, golangci-lint, pre-commit integration, and the "promote rule into code" ratchet.
See [agent-readable-lints.md](references/agent-readable-lints.md).

**LSP and code intelligence**: full inventory of all LSP capabilities as agent harness tools (diagnostics, goToDefinition, findReferences, code actions, workspace symbols, call hierarchy, semantic rename, hover, inlay hints, type hierarchy), plus tool integrations (Claude Code v2.0.74+, OpenCode, oh-my-pi, oh-my-openagent, Kiro), limits and failure modes (startup latency, dynamic language gaps, context overhead), tree-sitter alternatives (Aider repo map, CodeRLM, AFT), and emerging protocols (ACP, LSAP).
See [lsp-code-intelligence.md](references/lsp-code-intelligence.md).

## Middleware Patterns

Four benchmarked patterns that improved agent performance from 52.8% → 66.5% on Terminal Bench 2.0 without changing the model (LangChain, 2026):

- **Build-Verify Loop** — enforce plan → build → verify → fix; block completion signals until verification runs
- **Context Injection** — inject working directory, available tools, recent test results before each model call
- **Loop Detection** — track repeated file edits or errors; interrupt and suggest strategy change at threshold
- **Reasoning Budgeting** — high reasoning for planning and verification; moderate for implementation ("reasoning sandwich")

Also covers Microsoft Magentic-One task/progress ledger validation and Meta-Harness automated optimization.

**Advisor Tool** (Anthropic API beta, April 2026): a dynamic guidance layer where a cheap executor model (Haiku or Sonnet) calls Opus for strategic advice at decision points — all within a single API call. Haiku + Opus advisor achieved 19.7% → 41.2% on BrowseComp at 85% less cost than Sonnet alone. 2–3 advisor calls per task is the validated sweet spot; the executor decides timing. Conceptual foundation: arXiv:2510.02453 (Asawa et al.).

See [middleware-patterns.md](references/middleware-patterns.md) → "Advisor Tool: Dynamic Guidance Layer."

## Spec-Driven Workflow Frameworks

Pre-built harness implementations you can adopt instead of building from scratch. Six main frameworks, each covering different portions of the five harness elements:

- **GSD** (32K stars) — most complete; discuss→plan→execute→verify; wave parallelization; 10-dim plan validation; goal-backward verification
- **GitHub Spec Kit** (80K stars) — most adopted; guides-strong; human fills sensor role; good starting point
- **Ralph Wiggum** — simplest autonomous loop; fresh context per iteration; DONE signal gates on passing criteria
- **BMAD** — 12+ agent personas; human-collaborative; agile-grounded; full SDLC
- **SPARC** — TDD-first 5-phase discipline; correctness-critical projects
- **Kiro** (Amazon) — IDE-native; EARS notation requirements; agent hooks as built-in sensors

All are harnesses. They differ in how much of the sensor layer they include alongside the guides layer.
See [spec-driven-workflows.md](references/spec-driven-workflows.md).

## Dev Environment Design

Running multiple agents concurrently requires a different environment model: fast guardrails (cheap enough to run after every change), ephemeral environments (one command, 1-2 seconds, no manual steps), and isolated concurrent workspaces (git worktrees + conflict-free port/db/cache allocation).

> "With agents, you do something closer to beekeeping — orchestrating across processes without knowing the specifics of what's happening within each."

Every minute added to the test loop adds hours to agent task completion time. Optimize aggressively.
See [dev-environment-design.md](references/dev-environment-design.md).

## Frameworks and Ecosystem

When to use LangGraph, Microsoft Agent Framework, OpenClaw, and findings from Chinese labs (DeepSeek context strategies, Moonshot Kimi K2 interleaved thinking, ACE evolving playbooks):
See [ecosystem.md](references/ecosystem.md).

## Implementation Levels

- **Level 1** (individual, 1-2 hrs): `CLAUDE.md`, pre-commit hooks, test suite
- **Level 2** (small team, 1-2 days): CI constraints, shared templates, review checklists
- **Level 3** (organization, 1-2 weeks): middleware, observability, entropy management

See [implementation-levels.md](references/implementation-levels.md) for checklists.

## The Durability Gap

Standard AI benchmarks measure single-turn or short-session performance. They miss the failure mode that matters most for production harnesses: reliability degradation over long sessions.

> "A model might excel in single-turn evaluations but drift off-track after fifty steps." — Phil Schmid, 2026

The harness's job is to detect and recover from this drift — through loop detection, context injection, session decomposition, and explicit continuity mechanisms. A harness that works for 10 tool calls but fails at 100 is not production-ready.

Evaluate harness quality against *duration*, not just success rate on individual tasks.

## When to Simplify

Each harness component encodes an assumption about a model limitation. As models improve, test those assumptions. Remove components that are no longer load-bearing. Re-examine the harness on every major model update. Opus 4.6 enabled eliminating sprint decomposition entirely for some tasks.

**The Bitter Lesson applied to harnesses**: simpler architectures consistently outperform complex ones over time. Manus refactored their harness five times in six months toward simplicity. Vercel removed 80% of their agent tools and got better results. GitHub Copilot's engineering team quantified this: pruning 40 built-in tools to a 13-tool core produced a 2–5 percentage point improvement in task success rate and 400ms latency reduction — the larger toolset caused agents to ignore instructions, use tools incorrectly, and make unnecessary calls (SWE-Lancer/SWEbench, 2025). When a harness component stops being load-bearing, removing it is not a regression — it's maintenance. Complex harnesses built for yesterday's model limitations become obstacles as models improve.

**Cost-quality reference data (Anthropic)**:
- Solo agent (game maker): 20 min, $9 — broken core functionality
- Full harness (game maker): 6 hrs, $200 — functional, minor issues
- Simplified harness (DAW): 3.8 hrs, $124

Quality differences are "immediately apparent."
