# Spec-Driven Workflow Frameworks

Sources: GitHub Spec Kit, GSD (gsd-build/get-shit-done), BMAD Method, Ralph Wiggum, SPARC/Claude-Flow, Kiro (Amazon)

## Table of Contents

- [What These Are](#what-these-are) — harnesses vs. orchestration infrastructure
- [Framework Comparison](#framework-comparison) — stars, harness completeness, primary strength
- [GSD](#gsd--get-shit-done) — wave parallelization; 10-dim plan validation; goal-backward verification
- [GitHub Spec Kit](#github-spec-kit) — specify/plan/tasks commands; widest agent support
- [Ralph Wiggum Loop](#ralph-wiggum-loop) — autonomous loop; DONE signal; fresh context per iteration
- [BMAD Method](#bmad-method) — 12+ agent personas; Party Mode; agile-grounded
- [SPARC](#sparc-specification-pseudocode-architecture-refinement-completion) — TDD-first 5-phase; pseudocode before implementation
- [Kiro (Amazon)](#kiro-amazon) — EARS notation; agent hooks as built-in sensors
- [Choosing a Framework](#choosing-a-framework)
- [These Are Not Mutually Exclusive](#these-are-not-mutually-exclusive)

---

## What These Are

Spec-driven workflow frameworks are pre-built harness implementations — packaged systems that enforce a planning-first, decomposition-forward process around AI coding agents. Rather than designing your harness from scratch, you adopt a framework that already encodes the key harness elements.

They are harnesses. Each one addresses some or all of the five harness elements (task decomposition, session continuity, external evaluation, mechanical constraints, incremental verification) with varying depth.

## Framework Comparison

| Framework | Stars | Task decomp | Session continuity | External eval | Mech. constraints | Incremental verify |
|---|---|---|---|---|---|---|
| **GSD** | 32K | ✓ atomic + waves | ✓ STATE.md + git | ✓ gsd-verifier | ✓ 10-dim validation | ✓ UAT.md + goal-backward |
| **GitHub Spec Kit** | 80K | ✓ spec→plan→tasks | ✓ artifact persistence | ✗ human only | ✓ partial (tasks anchor spec) | ✗ human review |
| **Ralph Wiggum** | — | ✓ specs folder | ✓ IMPLEMENTATION_PLAN.md | ✓ self-verify via criteria | ✓ testable acceptance required | ✓ DONE signal gates |
| **BMAD** | — | ✓ agile phases | ✓ file-based passing | ✓ multi-persona review | ✓ role boundaries | ✓ partial |
| **SPARC** | — | ✓ 5-phase TDD | ✓ TDD artifacts | ✓ refinement phase | ✓ tests-first required | ✓ TDD |
| **Kiro** | — | ✓ req→design→tasks | ✓ 3 docs + hooks | ✗ human review | ✓ EARS notation + criteria | ✓ agent hooks |

---

## GSD — Get Shit Done

**GitHub**: `gsd-build/get-shit-done` | 32K stars | Works with: Claude Code, Codex, Copilot, Windsurf, OpenCode, Augment

The most complete spec-driven harness available. Addresses all five harness elements and adds wave-based parallel execution.

### Phases
**Discuss → Plan → Execute → Verify → Ship**

1. `/gsd:discuss-phase N` — surfaces ambiguities; produces `N-CONTEXT.md`
2. `/gsd:plan-phase N` — gsd-planner decomposes to atomic tasks with dependency graphs; gsd-plan-checker validates across 10 dimensions; produces `N-0X-PLAN.md`
3. `/gsd:execute-phase N` — runs tasks in dependency-ordered waves, each with a fresh 200k+ context; atomic git commit per task; produces `N-M-SUMMARY.md`
4. `/gsd:verify-work N` — gsd-verifier performs goal-backward verification; produces `N-VERIFICATION.md` + `UAT.md`
5. `/gsd:ship` — generates rich PR with full requirement traceability

### Key Architectural Concepts

**Wave execution**: tasks group into dependency graphs; independent tasks run in parallel waves with fresh contexts, mimicking a multi-threaded engineering team. Tasks declare `depends_on: [task_ids]`; Wave 2 waits for Wave 1.

**Context rot prevention**: thin orchestrator spawns specialized agents with fresh contexts. No single agent accumulates implementation details. All state persists in `.planning/`.

**10-dimension plan validation**: atomicity, dependency correctness, completeness, resource feasibility, risk, complexity balance, testing coverage, documentation, rollback feasibility, acceptance criteria clarity.

**Goal-backward verification**: verifier traces requirement → plan → execution → test for each feature — not just "did it run" but "does it satisfy what was specified."

**Multi-model routing**: Quality profile = Opus for planning/verification, Sonnet for execution; Budget profile = Sonnet for planning, Haiku for verification.

### Artifacts (in `.planning/`)
`PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`, `N-CONTEXT.md`, `N-RESEARCH.md`, `N-M-PLAN.md`, `N-M-SUMMARY.md`, `N-VERIFICATION.md`, `UAT.md`, `config.json`

### What It Adds Beyond Anthropic's Pattern
- Wave parallelization (vs. sequential single-feature execution)
- 10-dimension plan checker (vs. no plan validation)
- Goal-backward verification agent (vs. human review or playwright)
- Brownfield codebase mapping before new phases
- Three-way merge patch preservation across framework updates

---

## GitHub Spec Kit

**GitHub**: `github/spec-kit` | 80K stars | Works with: Claude Code, Copilot, Gemini CLI, 24+ agents

The most widely adopted, simplest to adopt. Strong on planning and decomposition; relies on human for evaluation.

### Phases
**Constitution → Specify → Plan → Tasks → Implement**

- `/specify` — expands goals into detailed spec (user journeys, not implementation)
- `/plan` — establishes technical direction, stack, constraints, architecture
- `/tasks` — breaks spec + plan into small, reviewable, testable units

### Harness Engineering Mapping
- **Guides-first**: spec + plan + tasks are all guides (feedforward). The spec is the source of truth; tasks anchor the agent to it.
- **Separation of intent from implementation**: explicitly separates "what" from "how" — reducing specification-cascade errors (over-specifying causes the same cascading errors the Planner in the three-agent architecture is designed to avoid).
- **No sensors**: no external evaluator, no verification loop, no loop detection. Human developer fills this role.

### `spec-kit-plus` Fork
`panaversity/spec-kit-plus` extends Spec Kit by treating "specifications, architecture history, prompt history, tests, and automated evaluations as first-class artifacts" and adds multi-agent orchestration. Closer to a full harness.

**When to use Spec Kit**: teams that want a lightweight planning structure without committing to a full harness. Strong starting point; add sensor layers (evaluator agent, build-verify middleware) as needed.

---

## Ralph Wiggum Loop

**GitHub**: `fstandhartinger/ralph-wiggum`, `snarktank/ralph` | Works with: Claude Code, Amp

The simplest autonomous loop. Minimal framework, maximum automation. Named after the Simpsons character.

### How It Works
A bash wrapper runs the agent in a loop until all specs complete:

1. Agent reads spec from disk (fresh context window each iteration)
2. Selects highest-priority incomplete task
3. Implements and tests
4. Verifies acceptance criteria
5. Outputs `<promise>DONE</promise>` only if criteria pass
6. Bash wrapper detects DONE, loops to next task or exits

If DONE is absent, the wrapper retries with fresh context. The agent never accumulates context rot — each iteration rebuilds understanding from written artifacts.

### Artifacts
`specs/` — feature requirements with testable acceptance criteria | `IMPLEMENTATION_PLAN.md` — task breakdown + progress | `logs/` — full session traces | `completion_log/` — finished work records (markdown + mermaid)

### Harness Engineering Mapping
- Directly implements the session-handoff pattern in automated form: fresh context per iteration, disk-based state
- Verification-driven: DONE signal is gated on passing criteria, not code completion
- "Backpressure enforcement": tests and builds actively reject incomplete work
- Simpler than GSD but shares the same core loop: decompose → execute one task → verify → commit → repeat

**`smart-ralph`** (`tzachbon/smart-ralph`): adds spec-driven development workflow and smart compaction to Ralph — closer to a full harness.

**When to use**: fully autonomous execution on well-specified projects; preference for minimal framework overhead.

---

## BMAD Method

**GitHub**: `bmad-code-org/BMAD-METHOD` | Works with: Claude Code, Cursor, Windsurf, Copilot, Gemini CLI

"Breakthrough Method for Agile AI-Driven Development." The most human-collaborative of the frameworks — positions agents as expert collaborators, not autonomous executors.

### Architecture
12+ specialized agent personas covering the full SDLC: PM, Architect, Developer, UX Designer, and 8+ more domain specialists.

**Party Mode**: multiple agent personas collaborate in a single session — e.g., PM and Architect discuss requirements before the Developer implements. Approximates a real team standup within a single context.

**Scale-adaptive workflows**: automatically adjusts planning depth based on project complexity — a bug fix gets a different workflow depth than an enterprise feature.

**Composable**: 5 official extension modules for domain-specific workflows.

### Harness Engineering Mapping
- Strong on the human-in-the-loop dimension — each persona hand-off is a human review checkpoint
- Role boundaries as mechanical constraints: PM doesn't implement, Developer doesn't define requirements
- The `bmad-help` command provides contextual guidance for what to do next — a workflow sensor that tells humans when to escalate
- File-based context passing between personas

**When to use**: teams that want AI amplification of their own thinking rather than AI autonomy; complex projects where domain expertise matters at each phase; existing agile teams adding AI to their process.

---

## SPARC (Specification, Pseudocode, Architecture, Refinement, Completion)

**Part of**: Claude-Flow (now Ruflo: `ruvnet/ruflo`) | TDD-focused

Five systematic phases designed to enforce test-driven development discipline on AI-assisted projects.

### Phases
1. **Specification** — define requirements, acceptance criteria, constraints
2. **Pseudocode** — outline logic without implementation commitment
3. **Architecture** — structure, modules, interfaces, data flows
4. **Refinement** — iterative improvement, edge cases, optimization
5. **Completion** — final validation, documentation, delivery

### Harness Engineering Mapping
- Strong on the **behaviour harness** dimension (Martin Fowler's taxonomy) — the most mature TDD-first approach among these frameworks
- Pseudocode phase prevents implementation lock-in before architecture is settled (addresses the over-specification cascade problem)
- Refinement phase is a structured evaluator loop — multiple passes before completion
- Tests-first requirement makes the incremental verification element structural, not optional

**When to use**: projects where correctness and test coverage are primary concerns; teams already practicing TDD who want to extend that discipline to AI-assisted development.

---

## Kiro (Amazon)

**URL**: kiro.dev | AWS-integrated | IDE built on Code OSS

Amazon's agentic IDE built around spec-driven development from the ground up. Unlike the other frameworks (which are workflow layers over existing tools), Kiro is the IDE itself.

### Per-Feature Artifact Set
For every feature from a natural language prompt, Kiro automatically generates:
- `requirements.md` — EARS notation (Easy Approach to Requirements Syntax): structured, unambiguous acceptance criteria
- `design.md` — technical architecture, implementation approach, integration points
- Task list — coding tasks implementing the requirements

**EARS notation** converts vague requirements into structured, machine-verifiable form: "When [condition], the system shall [action]" — making acceptance criteria unambiguous for both humans and agents.

### Agent Hooks
Automated triggers that execute predefined agent actions on file system events (save, create, delete) — a built-in sensor layer that fires continuously rather than requiring explicit invocation.

### Harness Engineering Mapping
- Requirements → design → tasks is the same three-phase Planner output as the three-agent architecture, but built into the IDE
- EARS notation is a stronger form of the testable acceptance criteria that Ralph and GSD require
- Agent hooks are an automated implementation of context injection middleware — fire on events, not just on explicit agent calls
- Relies on human review for evaluation; no external evaluator agent

**When to use**: AWS-native teams; projects where IDE-integrated spec generation matters; situations where EARS notation quality of requirements is worth the AWS lock-in.

---

## Choosing a Framework

| Situation | Recommended framework |
|---|---|
| Maximum automation, full harness coverage | GSD |
| Quick adoption, large community, add sensors later | GitHub Spec Kit |
| Fully autonomous loop, minimal overhead | Ralph Wiggum |
| Human-collaborative, agile team process | BMAD |
| TDD-first, correctness-critical | SPARC |
| AWS-native, IDE-integrated | Kiro |
| Build your own from primitives | See session-handoff-pattern.md + middleware-patterns.md |

## These Are Not Mutually Exclusive

The frameworks implement different parts of the harness. Patterns can be mixed:
- Use GSD's 10-dimension plan checker on top of GitHub Spec Kit's spec output
- Use Ralph's automated loop for execution after BMAD's planning phase
- Apply SPARC's TDD discipline within GSD's wave execution framework
