# Claude Code Primitives as Harness Mechanisms

Source: Anthropic official documentation (code.claude.com/docs, 2026)

The harness patterns in this skill — guides, sensors, agent isolation, reasoning budgeting, entropy management — are abstract concepts. Claude Code implements them as concrete primitives. This file maps each primitive to the harness engineering patterns it enables.

## Table of Contents

- [The Six Primitives](#the-six-primitives) — overview table
- [CLAUDE.md and Rules → Guides Layer](#claudemd-and-rules--guides-layer)
- [Hooks → Sensors Layer](#hooks--sensors-layer) — PreToolUse, PostToolUse, Stop hooks; full detail in [hooks.md](hooks.md)
- [Skills → Role Scoping, Reasoning Budgeting, Task Decomposition](#skills--role-scoping-reasoning-budgeting-task-decomposition)
- [Subagents → Agent Isolation, Per-Role Configuration](#subagents--agent-isolation-per-role-configuration)
- [Scheduled Tasks → Entropy Management](#scheduled-tasks--entropy-management)
- [Channels → Event-Driven External Triggering](#channels--event-driven-external-triggering)
- [Agent Teams → Parallel Evaluation and Investigation](#agent-teams--parallel-evaluation-and-investigation)
- [Composing Primitives: Full Harness Example](#composing-primitives-full-harness-example)
- [Quick Reference: Which Primitive for What](#quick-reference-which-primitive-for-what)

---

## The Six Primitives

| Primitive | Harness role | Reliability |
|---|---|---|
| **CLAUDE.md / Rules** | Guides (feedforward context) | Advisory |
| **Hooks** | Sensors (deterministic enforcement) | Deterministic |
| **Skills** | Task decomposition, role scoping, reasoning budgeting | Advisory or deterministic (user-controlled) |
| **Subagents** | Agent isolation, tool allowlists, per-agent context | Controlled |
| **Scheduled Tasks** | Entropy management, recurring background agents | Deterministic (when machine on) |
| **Channels** | Event-driven external triggering (CI, monitoring, messaging) | Research preview |
| **Agent Teams** | Multi-agent parallel work, competing hypotheses | Experimental |

---

## CLAUDE.md and Rules → Guides Layer

Already documented in [claude-md-design.md](claude-md-design.md). The guides layer of the harness: advisory, context-based, session-bridging.

**Key constraint**: advisory, not deterministic. For enforcement, use hooks.

---

## Hooks → Sensors Layer

Already documented in [claude-md-design.md](claude-md-design.md) and [guides-and-sensors.md](guides-and-sensors.md). The deterministic enforcement layer.

**Key hook events for harness engineering:**

| Event | Harness use |
|---|---|
| `PreToolUse` | Block constraint violations before they happen |
| `PostToolUse` | Auto-format, schema validation, coverage checks |
| `Stop` | Build-verify gate — block completion if tests haven't passed |
| `SessionStart` (matcher: `compact`) | Re-inject context after compaction |
| `InstructionsLoaded` | Debug which CLAUDE.md files are loading |
| `TeammateIdle` | Quality gate when an agent team teammate finishes |
| `TaskCreated` / `TaskCompleted` | Gate on task quality in agent teams |
| `ConfigChange` | Audit trail for settings changes |

See [guides-and-sensors.md](guides-and-sensors.md) and [claude-md-design.md](claude-md-design.md) for detail.

---

## Skills → Role Scoping, Reasoning Budgeting, Task Decomposition

Skills are the primitive that most directly implements multiple harness patterns simultaneously.

### Per-skill tool restrictions = agent role scoping

The `allowed-tools` frontmatter field limits which tools Claude can use when a skill is active. This is the OpenClaw SOUL.md principle implemented natively:

```yaml
---
name: safe-reader
description: Read and analyze files without making changes
allowed-tools: Read Grep Glob
---
```

A skill with `allowed-tools: Read Grep Glob` is structurally prevented from writing files — not by instruction, but by capability restriction. See [generator-evaluator-loop.md](generator-evaluator-loop.md) → "Per-Agent Tool Restrictions."

This is also the principle behind `omx explore` in oh-my-codex — a dedicated read-only exploration entry point with "repository-safe allowlists." Rather than letting a research phase happen in the same context as an execution phase (where the agent might accidentally write), exploration is a distinct capability-restricted invocation. The pattern names the entry point explicitly so there's no ambiguity about which mode is active.

### Per-skill model + effort = reasoning budgeting

The `model` and `effort` fields implement the reasoning sandwich pattern natively:

```yaml
# Planning skill — high effort, capable model
---
name: plan-feature
description: Plan implementation of a new feature
model: claude-opus-4-6
effort: high
disable-model-invocation: true
---
```

```yaml
# Implementation skill — moderate effort, faster model
---
name: implement
description: Implement a planned feature
effort: medium
---
```

```yaml
# Verification skill — high effort, skeptical evaluation
---
name: verify-implementation
description: Verify implemented feature against spec
effort: high
allowed-tools: Read Grep Bash(npm test)
---
```

Route each phase to the appropriate model and effort level rather than using uniform high-reasoning for everything. See [middleware-patterns.md](middleware-patterns.md) → "Reasoning Budgeting."

### `disable-model-invocation: true` = side-effect safety

Claude should not autonomously decide to run skills with side effects (deploy, commit, send notifications). Use `disable-model-invocation: true` for any skill that takes irreversible action:

```yaml
---
name: deploy
description: Deploy to production
disable-model-invocation: true  # You must type /deploy — Claude won't trigger this
---
```

Without this flag, Claude might deploy because "the code looks ready." The flag enforces human-in-the-loop for consequential actions structurally, not by instruction.

### `context: fork` = isolated agent execution

```yaml
---
name: deep-research
description: Research a topic without consuming main context
context: fork
agent: Explore
allowed-tools: Read Grep Glob Bash(rg *)
---

Research $ARGUMENTS thoroughly. Report findings with specific file references.
```

Running a skill with `context: fork` creates an isolated context window. The main session doesn't get polluted with the research process — only the synthesized result returns. This implements the "per-agent context scoping" principle from [context-engineering.md](context-engineering.md).

### Shell injection `!` = dynamic context at invocation time

```yaml
---
name: pr-review
description: Review the current pull request
context: fork
agent: Explore
---

## PR Context
- Diff: !`gh pr diff`
- Comments: !`gh pr view --comments`
- CI status: !`gh pr checks`

Review this PR for correctness, test coverage, and potential issues.
```

The `!` commands run before Claude sees anything — Claude receives the fully-rendered prompt with live data. This is the context injection middleware pattern (see [middleware-patterns.md](middleware-patterns.md)) applied at skill invocation time.

### `user-invocable: false` = background knowledge

Skills with `user-invocable: false` are loaded by Claude automatically when relevant but don't appear in the `/` menu:

```yaml
---
name: legacy-payment-context
description: Context about the legacy payment system. Load when working with src/payments/legacy/ or when the user mentions the old billing system.
user-invocable: false
paths:
  - "src/payments/legacy/**"
---

# Legacy Payment System Context
This system was built in 2019 and uses...
```

This is how you encode architectural notes that are too long for CLAUDE.md but need to load automatically in relevant contexts. The `paths` frontmatter triggers loading only when Claude is working in the relevant directory.

### Bundled skills = pre-built harness patterns

Claude Code ships bundled skills that implement harness patterns without configuration:

| Bundled skill | Harness pattern |
|---|---|
| `/batch` | Parallel agent execution in isolated git worktrees; spawns one agent per independent unit; each runs tests and opens a PR |
| `/simplify` | Three parallel review agents (generator-evaluator loop, lightweight variant) |
| `/loop [interval] <prompt>` | Session-scoped polling — monitor deploys, babysit CI, re-run skills on a timer while session is open |

`/batch` is the most powerful: it implements the full concurrent environment pattern (see [dev-environment-design.md](dev-environment-design.md)) as a single command. For large-scale codebase changes, this is the native mechanism.

### Codex plugin — cross-model evaluation and parallel delegation

The official `openai/codex-plugin-cc` plugin (March 2026) adds Codex as an external evaluator and parallel agent from within Claude Code:

| Command | Harness pattern |
|---|---|
| `/codex:adversarial-review --base main <focus>` | Cross-model adversarial evaluator — see [generator-evaluator-loop.md](generator-evaluator-loop.md) |
| `/codex:adversarial-review --background <focus>` | Async evaluation — runs while Claude continues working; retrieve with `/codex:result` |
| `/codex:rescue --background <task>` | Delegate to Codex without breaking Claude's context — parallel bug investigation, fire-drill triage |
| `/codex:setup --enable-review-gate` | Stop hook that auto-runs Codex review before each Claude completion — generator-evaluator loop as middleware |
| `/codex:rescue --model <model> --effort <level>` | Cost-routed parallel task — smaller model for triage, larger for critical investigation |

**The key harness use of `/codex:rescue`**: when Claude is deep in a complex session (full context, multi-step refactor), a CI failure on a different branch would normally force a context break. `/codex:rescue --background` delegates the investigation to Codex in a parallel process — Claude's context stays intact, Codex handles the fire drill, results come back via `/codex:result`.

Installation: `/plugin marketplace add openai/codex-plugin-cc` → `/plugin install codex@openai-codex` → `/reload-plugins` → `/codex:setup`. Requires ChatGPT subscription or OpenAI API key.

---

## Subagents → Agent Isolation, Per-Role Configuration

Subagents are defined in `.claude/agents/<name>.md` (or `~/.claude/agents/`). Each has a custom system prompt, tool allowlist, and model. When Claude encounters a task matching the subagent's description, it delegates.

```markdown
---
name: security-reviewer
description: Review code for security vulnerabilities. Use when asked to audit code, check for OWASP issues, or verify authentication logic.
tools: Read Grep Glob
model: claude-opus-4-6
---

You are a security-focused code reviewer. Your job is to find vulnerabilities...
```

**Key subagent harness properties:**

- **Own context window**: subagent's work doesn't pollute the main session's context
- **Tool allowlist**: the `tools` field is a hard capability restriction, not advisory
- **Custom system prompt**: the body implements the "per-agent SOUL.md" pattern (see [context-engineering.md](context-engineering.md))
- **Model selection**: route expensive reasoning to capable models; fast tasks to smaller models
- **`memory: true`**: subagent can maintain its own auto memory across sessions
- **`preload-skills`**: inject skills into the subagent's context at startup

**Subagents can be reused as agent team teammates**: define a `security-reviewer` subagent once; use it both for inline delegation and as a named teammate in an agent team.

---

## Scheduled Tasks → Entropy Management

**This is the native implementation of entropy agents.**

The patterns described in [context-engineering.md](context-engineering.md) and [guides-and-sensors.md](guides-and-sensors.md) (doc-gardening agents, constraint scanners, quality graders) run as scheduled tasks.

### Three scheduling options

| Option | Where | Requires machine on | Local files | Use for |
|---|---|---|---|---|
| **Desktop scheduled tasks** | Your machine | Yes | Yes | Full access to local checkout |
| **Cloud scheduled tasks** | Anthropic cloud | No | No (fresh clone) | Reliability without machine |
| **`/loop` in session** | Your machine | Yes | Yes | Polling during active session |

### Creating entropy management tasks

Each scheduled task is stored as a SKILL.md file at `~/.claude/scheduled-tasks/<task-name>/SKILL.md`. You can edit it directly.

**Doc-gardening task** (daily):
```markdown
---
name: doc-gardening
description: Scan documentation for drift from source code
---

Scan all markdown files in docs/ and compare them against their corresponding
source files. For each discrepancy (function signature changed, endpoint
removed, parameter renamed):
1. Note the file, line, and specific mismatch
2. Open a fix-up PR with the correction
Keep PRs small — one per file or per topic area.
```

**Constraint violation scanner** (nightly):
```markdown
---
name: constraint-scanner
description: Scan for golden principle violations
---

Scan the codebase for violations of our golden principles:
1. Hand-rolled helpers that duplicate src/shared/utils — open refactor PR
2. YOLO data access without Zod validation — open PR with validation added
3. Files over 300 lines — note in quality.md with refactor suggestions
Update quality.md with today's grade for each domain.
```

**Quality grader** (weekly):
```markdown
---
name: weekly-quality-grade
description: Update the quality document with domain grades
---

For each domain in src/ (billing, auth, reporting, etc.):
1. Count constraint violations from this week's constraint-scanner runs
2. Check test coverage
3. Review documentation freshness
4. Assign a grade (A/B/C/D) to each domain
Update docs/quality.md with the updated grades and a trend note.
```

### `/loop` — session-scoped polling

The `/loop` built-in skill runs a prompt repeatedly at an interval while the session stays open:

```
/loop 5m check if the deploy finished
/loop 10m run tests and report any new failures
/loop 2m summarize what the PR checks are showing
```

**Harness use cases:**
- Polling a deployment until it completes or fails
- Babysitting CI — surfacing failures as they appear rather than waiting until the end
- Monitoring a long-running build and alerting when it finishes
- Periodically re-running another skill during an active work session

**Tradeoffs vs. scheduled tasks:**

| | `/loop` | Scheduled task |
|---|---|---|
| Session required | Yes — closes when session ends | No (cloud) or only while machine is on (desktop) |
| Interval minimum | 1 minute | Configurable |
| Context window | Runs in main session context | Own isolated context per run |
| Access to session state | Yes — can reference current conversation | No |
| Persists across restarts | No | Yes |

Use `/loop` for monitoring tasks you are actively watching during a session. Use scheduled tasks for entropy management, background maintenance, and anything that needs to run reliably outside active sessions.

### Worktree isolation for scheduled tasks

Enable the worktree toggle when creating a scheduled task to give each run its own isolated git worktree. This prevents scheduled tasks from interfering with active development work — the same isolation principle as concurrent agent environments (see [dev-environment-design.md](dev-environment-design.md)).

### Cloud tasks for reliability

For entropy agents that need to run even when your machine is off (nightly scans, weekly quality reports), use cloud scheduled tasks. They run against a fresh clone of your repository, so they don't have access to local `.env` files — design prompts to work from source code alone.

---

## Channels → Event-Driven External Triggering

**Status: research preview.** Requires Claude Code 2.1.80+, Bun runtime.

Source: Anthropic Channels documentation (March 2026).

Channels turns Claude Code into a background agent that external systems can push events into — Telegram messages, Discord messages, CI webhooks, monitoring alerts. Claude maintains session context across those events. You don't need to be at the terminal.

This is the event-driven complement to Scheduled Tasks. Scheduled tasks fire on a timer; channels fire when external events happen.

### Setup (Telegram example)

```
1. Create bot via BotFather, get token
2. /plugin install telegram@claude-plugins-official
3. Configure with token, restart with --channels
4. Send pairing code to your bot in Telegram
```

Discord follows the same pattern via the Discord Developer Portal. A `fakechat` demo mode lets you test the push/response loop locally before connecting external services.

### Harness use cases

**CI failure → immediate investigation:**
```
Wire a GitHub Actions webhook so Claude receives a push event when a build fails.
Claude inspects the logs and reports findings to Telegram before you've checked your phone.
```

**Monitoring alert → triage:**
```
Datadog fires an alert → Channels event → Claude investigates → summary delivered to Telegram.
No polling required. Claude is idle until the event arrives.
```

**Long-running task → async notification:**
```
Kick off a migration from your terminal, close your laptop.
Claude messages you in Discord when it completes or when it needs a decision.
```

### Security model

The plugin runs locally and polls the Bot API **outbound**. No inbound ports are opened. No public webhook endpoint. No reverse proxy. Authentication is pairing-code based — the bot is locked to your specific user ID. Anthropic has published prompt injection threat modeling in the docs; review before connecting sensitive repositories.

Teams and Enterprise orgs must explicitly enable Channels — it is off by default.

### Critical permission tradeoff

Claude Code's permission system does not work remotely. Any operation requiring approval (file writes, shell commands) pauses the session and waits for physical terminal presence. The workaround is `--dangerously-skip-permissions`, which bypasses the approval gate entirely.

| Mode | Remote autonomy | Oversight |
|---|---|---|
| Default | Blocks on every approval | Full human-in-the-loop |
| `--dangerously-skip-permissions` | Fully autonomous | No per-operation approval |

For unattended entropy agents (CI triage, nightly scans) where you've scoped the task tightly, `--dangerously-skip-permissions` is the practical choice. For anything touching production state, the default pause-and-wait model is safer even if inconvenient.

### Channels vs. scheduled tasks vs. clawhip

| | Channels | Scheduled tasks | clawhip |
|---|---|---|---|
| Trigger | External event push | Timer (cron) | Agent lifecycle events |
| Direction | Bidirectional (you can reply) | Outbound notification only | Outbound notification only |
| First-party | Yes | Yes | No (third-party) |
| Requires machine | Yes (local plugin) | No (cloud option) | Yes (daemon) |
| Best for | Interactive remote control, event-driven triage | Recurring maintenance, entropy agents | Multi-source lifecycle routing |

Channels and clawhip are complementary: use Channels for bidirectional interaction and event-triggered tasks; use clawhip if you need to normalize events from multiple sources (Git, GitHub, tmux, OMC) into a typed routing layer.

---

## Agent Teams → Parallel Evaluation and Investigation

**Status: experimental.** Current limitations include no session resumption for in-process teammates, task status lag, and no nested teams. Evaluate before using in production harnesses.

### Quality gates with hooks

The `TeammateIdle`, `TaskCreated`, and `TaskCompleted` hooks implement the build-verify loop for agent teams:

```json
{
  "hooks": {
    "TaskCompleted": [
      {
        "hooks": [{
          "type": "agent",
          "prompt": "Verify the task output. Run tests for the changed files. If tests don't pass, respond with {\"ok\": false, \"reason\": \"which tests failed\"}."
        }]
      }
    ]
  }
}
```

This gates task completion on passing tests — the build-verify loop applied to team-level work.

### Competing hypotheses pattern

For debugging, agent teams outperform single agents by preventing anchoring bias:

```
Spawn 3 teammates to investigate why payments are failing.
Each teammate should test a different hypothesis:
- Teammate 1: race condition in payment processor
- Teammate 2: invalid state transition in billing FSM
- Teammate 3: external API timeout with silent failure
Have them report findings and attempt to disprove each other.
```

See [generator-evaluator-loop.md](generator-evaluator-loop.md) for the three-agent planner/generator/evaluator pattern.

### Plan approval for teammates

```
Spawn an architect teammate to refactor the authentication module.
Require plan approval before they make any changes.
```

This implements human-in-the-loop at the planning stage — the teammate stays in read-only plan mode until the lead approves. Apply the same criteria you'd apply in a sprint contract review.

---

## Composing Primitives: Full Harness Example

A production harness using all five primitives:

```
CLAUDE.md (root)            → Golden principles, build commands, never list
.claude/rules/api.md        → API conventions, paths: src/api/**
.claude/rules/testing.md    → Coverage requirements, paths: **/*.test.ts

.claude/skills/plan/        → High-effort planning skill, Opus, fork context
.claude/skills/verify/      → Verification skill, read-only tools, high effort
.claude/skills/deploy/      → Deploy skill, disable-model-invocation: true

.claude/agents/evaluator.md → Skeptical evaluator subagent, read-only tools

.claude/settings.json hooks:
  PostToolUse(Edit|Write)   → Auto-format, typecheck, coverage check
  Stop                      → Agent-based: verify tests pass before completing
  TaskCompleted             → Verify task output in agent teams

~/.claude/scheduled-tasks/
  doc-gardening/            → Daily: scan docs vs source, open PRs
  constraint-scanner/       → Nightly: scan for golden principle violations
  quality-grader/           → Weekly: update quality.md with domain grades
```

Each primitive has one job. CLAUDE.md is advisory context; hooks are deterministic enforcement; skills scope capability per task; subagents isolate evaluation; scheduled tasks maintain quality over time; channels handle event-driven triggering when external systems need to reach Claude.

---

## Quick Reference: Which Primitive for What

| Goal | Primitive | Why |
|---|---|---|
| Tell Claude project conventions | CLAUDE.md | Advisory context, session-bridging |
| Enforce conventions mechanically | Hook (PostToolUse) | Deterministic, always runs |
| Restrict tools for a specific task | Skill `allowed-tools` | Per-invocation capability restriction |
| Route expensive tasks to capable model | Skill `model` + `effort` | Per-skill model selection |
| Prevent Claude from auto-triggering a workflow | Skill `disable-model-invocation: true` | Human controls timing |
| Keep research out of main context | Skill `context: fork` | Isolated context window |
| Recurring background maintenance | Scheduled task | Entropy agent mechanism |
| React to CI failures, monitoring alerts, or messages | Channels | Event-driven trigger, no polling required |
| Interactive remote control from phone | Channels | Bidirectional — you can reply via Telegram/Discord |
| Isolated agent with custom role | Subagent | Own context, tool allowlist, custom prompt |
| Parallel work requiring inter-agent communication | Agent team | Shared task list, direct messaging |
| Parallel work without communication | `/batch` skill | Worktree isolation, built-in |
