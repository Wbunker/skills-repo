# Dev Environment Design for Agent Workflows

Source: OpenAI harness engineering (Feb 2026)

## Table of Contents

- [The Mental Model Shift: Beekeeping](#the-mental-model-shift-beekeeping)
- [Fast: Guardrails Must Be Cheap to Run](#fast-guardrails-must-be-cheap-to-run) — test speed; concurrency; caching
- [Ephemeral: One Command, One Environment](#ephemeral-one-command-one-environment) — Docker; env var namespacing; port/db/cache isolation
- [Concurrent: Isolation Story](#concurrent-isolation-story) — git worktrees; per-worktree env
- [Incremental Merge Tracking for Concurrent Worktrees](#incremental-merge-tracking-for-concurrent-worktrees)
- [HUD: The Beekeeper's Dashboard](#hud-the-beekeepers-dashboard) — omx hud; JSON output; clawhip integration
- [Session-Scoped Monitoring with /loop](#session-scoped-monitoring-with-loop)
- [Monitoring as a Daemon, Not a Tool](#monitoring-as-a-daemon-not-a-tool) — clawhip architecture
- [Connecting to the Harness](#connecting-to-the-harness)

---

## The Mental Model Shift: Beekeeping

In a human-first workflow, you live in one dev environment. You craft a solution, tweak things, restart servers, and converge gradually.

With agents, the mental model is closer to **beekeeping**: orchestrating across processes without knowing the specifics of what's happening inside each one. Your job is to cultivate a good and healthy hive — environments that spin up reliably, run without cross-talk, and can be torn down without ceremony.

This requires a different approach to environment design: fast guardrails, ephemeral environments, and solid isolation.

## Fast: Guardrails Must Be Cheap to Run

> "The goal is to keep the agent on a short leash: make a small change, check it, fix it, repeat."

Agent hooks, git hooks, and CI checks all require the same property: they need to be cheap enough that running them constantly doesn't slow things down. If a quality check takes 20 minutes, agents will only run it occasionally. If it takes 1 minute, agents can run it after every meaningful change.

**OpenAI's benchmark:**
- 10,000+ assertions finishing in approximately 1 minute
- Without optimization: 20-30 minutes
- At 20-30 minutes, expecting an agent to run tests several times per task adds hours to completion time

**How they achieve this:**

| Technique | What it does |
|---|---|
| High test concurrency | Run tests in parallel rather than sequentially |
| Strong test isolation | Each test runs against its own state; no shared database rows or caches between tests |
| Caching layer for third-party calls | Record and replay external API calls; eliminates network latency from the test loop |
| Fresh database per run | `npm test` creates a new database, runs migrations, executes full suite — fast enough to do every time |

**The caching layer is load-bearing:** without it, 10,000 tests that make external calls would be 20-30 minutes. With it, 1 minute. This is the difference between a guardrail the agent runs constantly and one it avoids.

**Design principle**: every minute added to the test loop adds hours to agent task completion time. Optimize aggressively. The investment pays back on every agent run.

## Ephemeral: One Command, One Environment

Once comfortable with agents, you naturally run many of them. Environments spin up and tear down multiple times a day. If setup involves manual steps, you will avoid doing it — and that avoidance directly limits how many parallel agents you can run.

**The latency requirement:**
> "If it takes minutes and involves a bunch of tinkering and manual configuration, you won't do it. If it is one command and takes 1-2 seconds, you'll do it constantly."

**OpenAI's `new-feature` command:**
```bash
new-feature <name>
```
One command that:
1. Creates a new git worktree for the feature
2. Copies in local config not tracked in git (`.env` files, credentials)
3. Installs dependencies
4. Starts the agent with a prompt to interview you and write a PRD together

If the feature name is descriptive enough, the agent may skip the interview and start work immediately.

The implementation details are less important than the latency. One command, 1-2 seconds, working environment with agent ready to start.

**Ephemeral tmux workers** (OMC pattern): spawn real worker processes (Codex, Gemini, Claude) in tmux split panes on demand — they execute their task and die on completion, eliminating idle resource usage. Unlike persistent agent processes that stay running between tasks, ephemeral workers have zero idle cost. The trade-off: startup latency per task vs. zero background resource consumption. For bursty workloads with clear task boundaries, ephemeral workers are preferable.

**Git worktrees** are the natural primitive for this pattern: each worktree is a full checkout of the repository at a branch, sharing the git history but with an independent working directory. Multiple worktrees can be active simultaneously with no interference between them.

**What must be automated for true ephemerality:**
- Dependency installation (no manual `npm install` step)
- Environment variable setup (`.env` copying or secrets injection)
- Dev server startup
- Agent invocation with appropriate context (feature name, relevant files, handoff artifacts)

If any of these steps requires human intervention, the environment is not truly ephemeral and you will not spin up environments freely.

## Concurrent: Isolation Story

Multiple worktrees running simultaneously only works if they don't step on each other. Any shared resource — ports, database names, caches, background job queues — is a potential conflict point.

**What needs conflict-free allocation:**

| Resource | Conflict risk | Solution |
|---|---|---|
| HTTP ports | Two agents binding the same port | Random port or port range allocation via env var |
| Database names/schemas | Shared state, test interference | Per-environment database name (`db_feature_<name>`) |
| File caches | Cache poisoning across environments | Per-environment cache directory |
| Background job queues | Jobs from one environment processed by another | Per-environment queue prefix or namespace |
| Lock files | Build system conflicts | Per-worktree node_modules, not shared |

**Env var configuration is the standard mechanism:**
All conflict-prone resources should be configurable via environment variables that the bootstrap script sets per-environment. Docker provides some of this automatically; without Docker, explicit env var namespacing achieves the same isolation.

**The isolation test**: can two instances of the application run simultaneously on the same machine without any interaction? If running `npm test` in worktree A causes test failures in worktree B, the isolation story is incomplete.

## Incremental Merge Tracking for Concurrent Worktrees

Source: oh-my-codex (OMX) project

When multiple agents work in parallel worktrees and a leader integrates their output, "use git" is not a complete strategy. Naive merge causes conflicts when worktrees have diverged significantly. OMX's team runtime tracks merges incrementally and selects the integration strategy based on divergence:

| Divergence level | Integration strategy |
|---|---|
| Low (few commits, non-overlapping files) | Standard merge |
| Medium (overlapping files, linear history) | Cherry-pick specific commits |
| High (significant history divergence) | Cross-worker rebase |

The leader runs conflict detection across worktrees before attempting integration — catching conflicts early rather than discovering them at merge time. This is a meaningful operational upgrade over "each agent commits to its branch, you deal with it later."

**Practical implication**: for concurrent agent teams, assign ownership of file domains at task assignment time. The conflict detection then confirms the assignment held — agents that drifted into each other's domains are flagged before integration. Domain assignment upfront + incremental conflict tracking avoids the worst merge scenarios.

## HUD: The Beekeeper's Dashboard

Source: oh-my-codex (OMX) project

The beekeeping metaphor — orchestrating across processes without knowing what's happening inside each one — implies a monitoring interface. OMX provides this as a HUD (Heads-Up Display):

```bash
omx hud --watch      # Live render of all running agents and their states
omx hud --json       # Machine-readable output for programmatic consumption
```

The HUD surfaces:
- Active agents and their current phase
- Quota usage and token consumption per agent
- Session duration metrics
- Event log across team coordination

**Why machine-readable matters**: `--json` output enables downstream tooling — pipe into Slack notifications, log to your observability stack, or trigger alerts when quota thresholds are hit. The HUD bridges the gap between agent execution (which the FCoT/OpenTelemetry tracing captures at code level) and operator awareness (what's happening right now in human terms).

This is the harness operator's interface. FCoT traces are for debugging after the fact; the HUD is for awareness during execution.

## Session-Scoped Monitoring with `/loop`

During active development sessions, use `/loop [interval] <prompt>` to poll background processes without leaving the session:

```
/loop 5m check if the deploy finished and report status
/loop 2m run pnpm test:unit and surface any new failures
```

This keeps the agent in the beekeeping role — watching across processes — without requiring a separate terminal or manual checking. Unlike scheduled tasks, `/loop` runs inside the active session context and closes when the session ends. It's the lightweight choice when you're already present; use scheduled tasks for anything that needs to run while you're away.

See [claude-code-primitives.md](claude-code-primitives.md) → "Scheduled Tasks" for the full comparison of `/loop` vs. Desktop vs. Cloud scheduled tasks.

## Monitoring as a Daemon, Not a Tool

Source: claw-code project (Sigrid Jin / Yeachan Heo, April 2026)

Any observability, event routing, or notification logic that runs around agents should not be loaded into the agents' context windows. Monitoring as a tool call consumes tokens for every operation; monitoring as a sidecar daemon has zero token cost.

The `clawhip` pattern: a separate process that observes agent lifecycle events (git commits, GitHub activity, session start/stop, ask-user-question) and handles notifications, routing, and audit logging entirely outside the agents' contexts. The agents themselves never see or invoke the monitoring layer — clawhip watches them from outside.

This is the architectural complement to the HUD: the HUD is the human-facing view; clawhip is the infrastructure that feeds it. Both run outside agent contexts.

**Design principle**: separate every recurring background operation (monitoring, notifications, cleanup, audit logging) from agent execution context. Agents should not spend tokens managing infrastructure that can be handled by a sidecar. This also prevents monitoring failures from cascading into agent failures — the sidecar crashing doesn't affect the agents.

Related: see [claude-code-primitives.md](claude-code-primitives.md) → "Scheduled Tasks" for the Claude Code-native implementation of this principle (entropy agents running outside the main session context).

## Connecting to the Harness

Environment design is infrastructure for everything else in the harness:

- **Build-Verify Loop** only works if tests run fast enough to run constantly
- **Multiple concurrent agents** (generator + evaluator; parallel feature work) require concurrent environments
- **Session handoff** is simpler when each session starts from a clean, known environment rather than a shared one that may have accumulated state

The dev environment is the harness's substrate. A slow or fragile environment degrades every other harness pattern built on top of it.
