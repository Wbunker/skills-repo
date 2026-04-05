# Implementation Levels

Source: Community synthesis (NXCode, agent-engineering.dev)

## Table of Contents

- [Overview](#overview) — anti-overbuilding rule
- [Level 1 — Individual (1-2 hours)](#level-1--individual-1-2-hours) — CLAUDE.md, pre-commit hooks, test suite, feature list
- [Level 2 — Small Team (1-2 days)](#level-2--small-team-1-2-days) — CI constraints, token ceilings, shared templates, evaluator agent
- [Level 3 — Organization (1-2 weeks)](#level-3--organization-1-2-weeks) — middleware, observability, entropy management, rate limits, audit trail
- [Production Readiness Checklist](#production-readiness-checklist) — 12 gates (observability, budgeting, circuit breakers, human gate, microVM isolation, etc.)
- [Simplification Heuristics](#simplification-heuristics) — removing load-bearing assumptions as models improve
- [Cost Reference](#cost-reference) — benchmarks; cost reduction mechanisms

---

## Overview

Harness implementation scales with team size and project complexity. Start at Level 1 and add complexity only when it's load-bearing for quality.

**Anti-overbuilding rule**: Don't build harness components for hypothetical failures. Run real work for two weeks, log every failure, then build guardrails around the failures you actually observed. Overbuilding orchestration too early creates an internal product to maintain rather than a tool that serves development. Every component should have a specific observed failure it addresses.

---

## Level 1 — Individual (1-2 hours)

The minimum effective harness for a solo developer or single project.

### Checklist

- [ ] `CLAUDE.md` or `AGENTS.md` at repo root
  - Tech stack and key libraries
  - Naming conventions (files, variables, components)
  - What NOT to do (anti-patterns, prohibited patterns)
  - Testing requirements
  - Key architectural decisions
- [ ] Pre-commit hooks
  - Linter (ESLint, flake8, etc.)
  - Formatter (Prettier, Black, etc.)
  - Type checker if applicable
- [ ] Test suite with baseline passing
  - At minimum: smoke tests that verify the app starts and core flows work
  - Agents must not mark work complete if tests fail
  - **Target 100% coverage** — not for bug prevention, but to force the agent to demonstrate the behavior of every line it writes; the coverage report becomes a todo list of tests still needed (see [guides-and-sensors.md](guides-and-sensors.md) → "100% Code Coverage as a Harness Constraint")
- [ ] `feature_list.json` for multi-session projects
  - All features listed, all marked `"passes": false`
  - Explicit constraint: "It is unacceptable to remove or edit tests"
- [ ] `claude-progress.txt` for multi-session projects
- [ ] `init.sh` for multi-session projects
- [ ] Consistent naming (files, branches, commits)

### Spec-Driven Framework Options at Level 1

Instead of building handoff artifacts manually, use a pre-built framework that generates them:

| Framework | Setup time | What you get out of the box |
|---|---|---|
| **GitHub Spec Kit** | 15 min | `specify`/`plan`/`tasks` commands; spec + task artifacts |
| **Ralph Wiggum** | 30 min | Automated loop; specs folder + IMPLEMENTATION_PLAN.md |
| **GSD** | 1-2 hrs | Full pipeline; all artifacts; wave execution; plan validation |
| **BMAD** | 1-2 hrs | 12+ agent personas; full SDLC workflow |
| **SPARC** | 1 hr | TDD-first 5-phase discipline |
| **Kiro** | IDE install | EARS-notation requirements; auto-generated design + tasks |

These frameworks implement the guides layer. Add sensor layers (evaluator agent, build-verify middleware, CI constraints) on top as you move to Level 2.

See [spec-driven-workflows.md](spec-driven-workflows.md) for full comparison.

### When to Move to Level 2

- More than one person is using agents on the codebase
- Agents are repeatedly making the same class of mistake
- Manual review is consuming significant time catching agent drift

---

## Level 2 — Small Team (1-2 days)

Adds shared constraints and coordination artifacts for multi-developer agent use.

### Additions to Level 1

- [ ] CI-enforced constraints
  - All Level 1 checks run in CI (not just pre-commit)
  - Merge blocked if CI fails
  - Architecture fitness checks (dependency structure, bundle size, etc.)
  - **Token ceiling on headless runs**: set a workspace spend limit or session token cap for any automated Claude Code session; a PR review that burns 200K+ tokens is a bug signal — cut it off and investigate. Use `PreToolUse` hooks (not `PermissionRequest`, which doesn't fire in non-interactive mode) for access control in CI pipelines.
- [ ] Shared prompt templates
  - Standardized agent instructions for common tasks (PR description, code review, feature implementation)
  - Stored in the repo, version-controlled
- [ ] Linted documentation
  - Vale or similar for documentation consistency
  - API documentation coverage checks
- [ ] Agent-specific review checklists
  - What reviewers should specifically check in agent-generated PRs
  - Focus on areas where agents typically cut corners
- [ ] Expanded `AGENTS.md` / `CLAUDE.md`
  - Project architecture overview with key decisions documented
  - Data model documentation
  - External API and integration documentation
  - Common pitfalls the team has encountered with agents
- [ ] Sprint contracts for complex features
  - Before agents implement a feature, define what "done" looks like
  - Include testable acceptance criteria
- [ ] Evaluator agent for complex workflows
  - Separate agent (or separate session with fresh context) reviews generator output
  - Calibrate to be skeptical, not permissive

### When to Move to Level 3

- Agent quality issues are appearing in production
- Different teams/projects need consistent agent behavior
- Cost and efficiency tracking is needed to optimize harness ROI
- Entropy management is becoming a manual burden

---

## Level 3 — Organization (1-2 weeks)

Systematic harness infrastructure for multi-team or production-critical agent use.

### Additions to Level 2

- [ ] Custom middleware / orchestration layer
  - Centralized agent routing and model selection
  - Standardized tool registry shared across projects
  - Harness versioning (track which harness version was used for each agent run)
- [ ] Observability integration
  - Token usage tracking per agent run and per project
  - Success/failure rate by agent type and task type
  - Latency and cost dashboards
  - Trace logging for debugging agent failures
- [ ] Scheduled entropy management
  - Automated documentation drift detection
  - Constraint violation scans on a recurring schedule
  - Dependency audit agents
  - Pattern enforcement agents
- [ ] Performance dashboards
  - Throughput (PRs/day, features/session)
  - Quality metrics (test pass rate, evaluator scores over time)
  - Cost per feature
- [ ] Harness metrics (OmOCon SF, April 2026)
  - **Lead time**: issue opened → PR merged
  - **Agent autonomy rate**: % of tasks completed without human intervention
  - **Reopen/rollback rate**: % of agent PRs that were reverted or reopened
  - **Wasted work rate**: features reverted within 30 days of merge
  - **Issue clarity percentage**: % of issues that agents could start without clarification requests
  - **Monthly API cost per engineer**: tracks harness efficiency over time
- [ ] Governance and audit trail
  - "What did the AI actually do?" is unanswerable without explicit infrastructure. There is no native audit trail in Claude Code — build it through hooks and transcript logging, or accept the blind spot.
  - Minimum viable audit: a `PostToolUse` hook that appends tool name, file path, and timestamp to a session log; a `Stop` hook that archives the full session transcript. These provide a reviewable record of every file touched and every command run.
  - At org scale, route audit events to a centralized observability stack (see Observability integration above).
- [ ] Rate limit planning by team size (Anthropic recommendations):

  | Team size | TPM/user | RPM/user |
  |---|---|---|
  | 1–5 users | 200k–300k | 5–7 |
  | 5–20 users | 100k–150k | 2.5–3.5 |
  | 20–50 users | 50k–75k | 1.25–1.75 |
  | 50–100 users | 25k–35k | 0.62–0.87 |
  | 100–500 users | 15k–20k | 0.37–0.47 |
  | 500+ users | 10k–15k | 0.25–0.35 |

  TPM per user decreases at larger team sizes because fewer users are active concurrently. Limits apply at the org level, not per individual, so individuals can burst above their calculated share when others are idle.

- [ ] Escalation policies
  - When to route to human review
  - When to escalate to more capable model
  - When to halt and flag rather than attempt recovery
- [ ] Harness testing
  - Test harness components against known failure cases
  - Regression tests when harness is updated
  - A/B testing for harness improvements
- [ ] Cross-team harness sharing
  - Shared `AGENTS.md` components for org-wide conventions
  - Centralized golden principles repository
  - Harness component library for common patterns

---

---

## Production Readiness Checklist

Source: "Agentic Architectural Patterns" book

Before any agent touches production data or takes production actions, verify these gates. Items marked as already covered by Level 1-3 checklists above are noted.

- [ ] **Observability**: every reasoning step and tool call mapped to a Trace ID in an observability stack (Datadog, Honeycomb, etc.) — see FCoT + OpenTelemetry pattern in middleware-patterns.md
- [ ] **Budgeting**: hard token and dollar cap per session enforced at the middleware layer, not in the prompt
- [ ] **Circuit breakers**: maximum depth for recursive tool calls; watchdog process that forcefully halts on step limit breach
- [ ] **Fallback**: defined behavior when primary LLM returns 429/503 — adaptive retry + prompt mutation + secondary provider routing
- [ ] **Schema enforcement**: tool output validated against schema before being fed back to the LLM as context
- [ ] **Human gate**: high-stakes actions (write, delete, external API calls with side effects) protected by a human interrupt or confidence-score-triggered escalation. Implement at individual command granularity, not just action category — e.g., `"git push": "ask"`, `"rm": "deny"`, `"git status": "allow"`. The granularity matters: allowing all shell commands or blocking all shell commands are both wrong; the right boundary is per-command.
- [ ] **Execution isolation**: for production-critical or security-sensitive agent work, software-level permission controls (allow/ask/deny) are necessary but not sufficient — a model with strong reasoning can sometimes find secondary execution vectors that route around a blocked tool. A microVM or Docker sandbox removes this possibility entirely: the sandbox boundary is physical, not logical. The host machine, network, and filesystem are unreachable regardless of what the agent attempts. Use software-level controls during development; add VM-level isolation before agents touch production systems or run experimental models.
- [ ] **Data privacy**: PII filters active on both LLM input and output; no raw PII in trace logs
- [ ] **Instruction fidelity**: a critic or evaluator verifies that the agent followed its system prompt and sprint contract — not just that it produced output
- [ ] **Latency SLA**: timeout defined that triggers simplified reasoning mode or graceful halt rather than indefinite waiting
- [ ] **State persistence**: agent can recover exact working state after a crash or context reset (file-backed handoff artifacts, LangGraph checkpoints, or equivalent)
- [ ] **Tool discovery**: tools loaded via a protocol (MCP or equivalent) rather than hard-coded — enables hot-swap without agent restart
- [ ] **Explainability**: system can generate a reasoning summary on request — required for regulated industries (finance, healthcare); good practice everywhere

A demo that passes the first three gates is better than most. A production system should pass all twelve.

---

## Simplification Heuristics

Every harness component encodes an assumption about a model limitation. As models improve:

1. Identify which failure modes each component addresses
2. After a major model upgrade, test whether each component is still load-bearing
3. Remove components whose assumptions no longer hold
4. Add new components to explore newly unlocked capability boundaries

Documented examples:
- Claude Opus 4.6: sprint decomposition became unnecessary for some task types
- Context anxiety mitigation: needed for Claude Sonnet 4.5; Opus 4.5+ can use compaction instead
- Periodic task reminders (every-N-turns system injections): helped weaker models stay on track; became constraints for stronger models — Claude treated the reminder as "must not deviate from this list" rather than "helpful orientation." The reminder that helped one model generation constrained the next. (Source: Anthropic Claude Code team, 2025)

**Don't maintain complexity for its own sake.** A simpler harness that works is better than a complex one maintained out of habit.

## Cost Reference

Source: Anthropic official documentation (code.claude.com/docs/en/costs, 2026)

**Baseline benchmarks:**
- Average cost: ~$6/developer/day; 90% of users stay below $12/day
- Team average: ~$100–200/developer/month with Sonnet 4.6 (high variance depending on automation usage)
- Agent teams: ~7x more tokens than standard sessions when teammates run in plan mode — each teammate has its own context window

**Cost reduction mechanisms (Anthropic-documented):**
- **Model routing**: Haiku for monitoring/simple subagents, Sonnet for daily work, Opus for complex architecture — reduces cost 3–5x vs. running everything on Opus
- **Prompt caching**: applied automatically by Claude Code to repeated content (system prompts, CLAUDE.md, stable context). Reduces costs for long-running sessions.
- **Preprocessing hooks**: use `PreToolUse` hooks to filter verbose output before Claude sees it (e.g., 10,000-line test run filtered to ERROR lines only). Reduces tokens for the same work.
- **CLAUDE.md → Skills migration**: instructions for specific workflows in CLAUDE.md load every session regardless of relevance; moving them to skills loads them only when invoked. Keep CLAUDE.md under 200 lines.
- **Subagent delegation**: verbose operations (test runs, log fetches, large file reads) stay in the subagent's context; only a summary returns to the main session.

**Cost spike signals**: a headless session that enters a debugging loop without interrupt; agent teams left idle; large file reads that could be targeted grep. Set a token ceiling on automated sessions and investigate any session exceeding it.
