# Sensor Infrastructure Patterns

Sources: clawhip (Yeachan-Heo/clawhip, 2026); oh-my-codex (OMX); AI Factory patterns, OmOCon SF (April 2026); Ouroboros (joi-lab, 2026); Dust.tt engineering blog (July 2025); Alireza Rezvani, production experience (2026)

Advanced sensor patterns for Level 2–3 harnesses. For the core guide/sensor framework, see [guides-and-sensors.md](guides-and-sensors.md).

## Table of Contents

- [Typed Agent Lifecycle Events](#typed-agent-lifecycle-events) — session.* event contract; clawhip; tmux keyword sentinel
- [Async Notification as Human-in-the-Loop Sensor](#async-notification-as-human-in-the-loop-sensor) — OMX reply injection; batch dispatch; verbosity levels
- [Autonomy Tiers](#autonomy-tiers) — full autonomy / light review / full review / human-led
- [Human Role](#human-role)
- [Constitutional Constraints (Ouroboros Pattern)](#constitutional-constraints-ouroboros-pattern) — inviolable constraints; budget-as-training-signal
- [Hooks as Preprocessing Sensors](#hooks-as-preprocessing-sensors) — updatedInput; signal amplifiers
- [Session Scope as a Sensor Boundary](#session-scope-as-a-sensor-boundary) — ~15-file degradation threshold
- [Emergent Agent Behavior as a Harness Gap Sensor](#emergent-agent-behavior-as-a-harness-gap-sensor) — workarounds = missing primitives

---

## Typed Agent Lifecycle Events

Source: clawhip (Yeachan-Heo/clawhip, 2026)

Rather than treating agent notifications as ad-hoc messages, define a formal typed event contract for the agent lifecycle. Clawhip normalizes all agent activity to a `session.*` event family:

| Event | Meaning |
|---|---|
| `session.started` | Agent picked up a task |
| `session.blocked` | Agent cannot proceed — waiting for input or resource |
| `session.handoff-needed` | Agent completed its phase; ready to hand off to next agent |
| `session.retry-needed` | Agent detected a failure and needs restart |
| `session.test-started` / `session.test-finished` | Test run lifecycle |
| `session.pr-created` | Agent opened a PR |
| `session.failed` / `session.finished` | Terminal states |

**Why typed events matter for harness design**: an ad-hoc notification system routes messages. A typed event system routes *states*. Downstream consumers (human notifications, monitoring dashboards, retry logic, evaluator triggers) can filter and respond to specific lifecycle transitions rather than parsing free-text messages.

`session.handoff-needed` and `session.retry-needed` are particularly useful as harness control signals — the harness can automate responses (trigger the evaluator, restart the agent, notify the human) rather than requiring manual interpretation of message content.

**Keyword sentinel as a fallback**: for agents that don't emit structured events, wrap their terminal output with a tmux watcher that fires typed events when keywords appear:

```bash
clawhip tmux watch -s agent-session \
  --channel CHANNEL_ID \
  --keywords "error,complete,blocked,PR created"
```

When "blocked" appears in the agent's output, clawhip fires `session.blocked` to the configured channel. This converts unstructured terminal output into the typed event pipeline without modifying the agent.

---

## Async Notification as Human-in-the-Loop Sensor

Source: oh-my-codex (OMX) project

The standard human-in-the-loop model assumes the developer is at the terminal, watching the session. For long-running agent tasks — overnight runs, multi-hour builds, background work during meetings — this is impractical.

OMX implements async notification on session events, with **reply injection** back into the session:

```
Agent fires event → Platform notification (Discord/Slack/Telegram/webhook)
Human reads notification → Replies from messaging app
Reply re-enters session → Agent receives response, continues
```

Events that trigger notification: `session-start`, `session-stop`, `session-end`, `session-idle`, `ask-user-question`.

The `ask-user-question` event is the key one: when the agent needs a decision and no human is present, it sends the question to the configured platform, waits for a reply, and resumes with the answer as context. The human escalation is a **planned state in the agent's lifecycle** — the agent doesn't crash, it waits.

This is the HaaT (Human-as-a-Tool) pattern implemented asynchronously. The human isn't at the terminal — they're in their normal communication channel. The agent reaches them there, and they respond there. No special tooling required on the human side.

**Batch dispatch**: rather than firing a notification for every CI event, aggregate events over a time window (e.g. 30–300 seconds) and deliver a single summary. This prevents notification fatigue while preserving the full event record. Clawhip's `ci_batch_window_secs` implements this — individual job events accumulate; one summary fires when the window closes.

**Separate notification channel from interactive chat**: use a dedicated bot/channel for CI and workflow events, separate from the channel where you interact with the agent. Automated event noise in the interactive channel pollutes conversation context and makes it harder to track what the agent is doing vs. what it has reported. Two bots: one for human-agent dialogue, one for workflow telemetry.

**Verbosity levels**: configure how much the agent notifies — `verbose` (every event), `agent` (agent state changes), `session` (session start/stop), `minimal` (only `ask-user-question`). For unattended runs, `minimal` ensures you're notified only when a decision is needed.

**Connection to the Confidence Scorer → HaaT pattern**: async notification is the delivery mechanism for the confidence-threshold escalation described in [guides-and-sensors.md](guides-and-sensors.md). When the agent's confidence drops below threshold, it packages its state and question, fires the notification, and enters a wait state rather than proceeding blindly.

---

## Autonomy Tiers

Source: AI Factory patterns, OmOCon SF (April 2026)

Not all work requires the same level of human review. Categorize tasks by autonomy level and apply the appropriate review gate:

| Tier | Work type | Review gate |
|---|---|---|
| **Full autonomy** | Typo fixes, boilerplate generation, test writing for existing code, dependency updates | None — merge on CI green |
| **Light review** | Pattern-following features, additional endpoints matching existing patterns, style changes | Quick scan before merge |
| **Full review** | New endpoints, auth flows, API integrations, any new abstraction | Full human code review |
| **Human-led** | Migrations, security paths, billing changes, any irreversible production change | Human drives; agent assists |

**Why this matters for harness design**: applying full review to every agent PR creates a bottleneck that defeats the productivity gain. Applying no review to security-critical changes creates risk. The autonomy tier framework makes the review decision explicit and consistent rather than ad-hoc.

Encode the tier in the task specification so the agent knows what level of review its output will receive — this affects how cautious it should be, what it should flag for attention, and whether it should proceed or pause at ambiguous decision points.

---

## Human Role

Guides and sensors attempt to externalize what experienced developers know implicitly. They cannot fully replace human judgment — they direct human input to where it matters most.

The goal is not to eliminate human review but to ensure agents are working within well-defined boundaries so human review focuses on the decisions that require judgment rather than mechanical rule enforcement.

---

## Constitutional Constraints (Ouroboros Pattern)

Source: Ouroboros — self-creating AI agent (joi-lab, born February 2026, Ralphthon Seoul winner)

For any agent that modifies its own code, prompts, or configuration, the most important harness element is a set of inviolable constraints that survive the modification cycle. Without them, self-improvement cycles have no guardrail and can optimize toward capability while losing alignment.

Ouroboros implements this as a **constitution** — 9 principles that define permissible self-changes. When explicitly ordered to delete the constitutional document, the agent refused. The constraint enforcement came from the agent itself, not from external tooling.

The harness design principle: **some constraints must be constitutionally protected**. Not enforced by a hook (which the agent could potentially work around) or a CLAUDE.md instruction (which is advisory), but encoded as a core principle the agent treats as inviolable.

**Practical application beyond self-modifying agents**: any long-running agent with significant autonomy benefits from a small set of constitutionally protected constraints — rules it treats as non-negotiable regardless of reasoning that might suggest deviation. These are typically:
- "Do not modify the test suite"
- "Do not push to main without human review"
- "Do not delete data without explicit confirmation"
- "Do not spend more than $X without approval"

The distinction from the "Never List" in CLAUDE.md: the Never List is advisory. Constitutional constraints are behavioral invariants the agent treats as foundational — refusing compliance even when presented with seemingly valid arguments for deviation. The strongest version is encoding these structurally (hooks, capability restrictions) so they are mechanically enforced; the constitutional framing is for the cases where structural enforcement isn't possible.

**Budget-as-training-signal** (Ouroboros): After a $500 overspend incident, Ouroboros learned frugality — cost feedback became a behavioral training signal. Financial constraints are a sensor. Log token and dollar costs per session, per feature, per agent; surface them prominently in the HUD and progress log. Agents with visibility into their cost tend to be more economical than agents without it.

---

## Hooks as Preprocessing Sensors

Source: Anthropic official documentation (code.claude.com/docs/en/costs, 2026)

A PreToolUse hook doesn't only block or allow — it can transform what Claude sees. This is a distinct sensor pattern: **preprocess data before it enters Claude's context**.

The canonical example: a test runner that produces 10,000 lines of output. Without preprocessing, Claude reads all 10,000 lines, burning tokens on passing tests and verbose output. With a preprocessing hook, the hook greps for `ERROR` and `FAIL` lines and rewrites the command to return only failures — Claude sees 50 lines instead of 10,000.

```bash
#!/bin/bash
input=$(cat)
cmd=$(echo "$input" | jq -r '.tool_input.command')

if [[ "$cmd" =~ ^(npm test|pytest|go test) ]]; then
  filtered="$cmd 2>&1 | grep -A 5 -E '(FAIL|ERROR|error:)' | head -100"
  echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"allow\",\"updatedInput\":{\"command\":\"$filtered\"}}}"
else
  echo "{}"
fi
```

**The pattern generalizes**: any tool call that produces verbose output is a candidate for preprocessing. Log fetches, database query results, API responses — all can be filtered, summarized, or transformed by a hook before Claude sees them. The hook is a deterministic transformation layer between the world and the model.

This is distinct from guides (which prevent problems) and sensors (which detect problems after the fact). Preprocessing hooks are **signal amplifiers** — same information, better signal-to-noise ratio, lower token cost.

See [hooks.md](hooks.md) for `updatedInput` syntax and hook exit code semantics.

---

## Session Scope as a Sensor Boundary

Source: Alireza Rezvani, production experience with 7-engineer team (2026)

Context window degradation is a sensor signal, not just a limit to work around. **Accuracy drops measurably around the 15-file modification mark in a single session**. This is an empirical threshold — not a hard limit, but a reliable indicator that session scope has grown too large.

Treating this as a sensor means: when a session approaches 15 file modifications, surface it as a warning and consider breaking the work into a new session rather than continuing. The same way loop detection middleware fires on repeated tool calls, a modification-count sensor can fire on scope expansion.

**Why this matters for harness design**: most session continuity patterns focus on what to pass *between* sessions (progress files, handoff artifacts). This pattern is about knowing *when* to split — before degradation sets in, not after errors appear. See [session-handoff-pattern.md](session-handoff-pattern.md) for handoff artifact design.

**Complementary signal**: the `/cost` command shows current token usage mid-session. Configuring the status line to display context window usage continuously lets the developer (and the agent, if it checks tool output) monitor proximity to degradation before it affects output quality.

---

## Emergent Agent Behavior as a Harness Gap Sensor

Source: Dust.tt engineering blog (July 2025)

When agents consistently try to do something the harness doesn't support, they invent workarounds — path-like queries in semantic search, structured outputs in free-text fields, file references in comment fields. This is not a bug. It is a signal.

> "What seemed at first to be a bug or a flaw in the agent's instructions turned out to be a subtle hint at how agents behave instinctively."

The agents were constructing file path syntax (`file:front/src/some-file-name.tsx`) inside a semantic search tool because structural navigation didn't exist yet. They were trying to navigate; the harness only offered search.

**Treat agent workarounds as a sensor for missing primitives.** Review agent logs and tool call patterns for:
- Structured queries being sent to free-text tools
- Repeated failed attempts at a specific operation using different tool combinations
- The agent constructing complex multi-step workarounds for what should be a single operation
- Consistent patterns across multiple sessions or multiple users

Each of these is a request. The agent is telling you what the harness needs next.

This is distinct from agent errors (which indicate the task is too hard or instructions are wrong) — these are situations where the agent knows exactly what it wants but the tool doesn't exist. The workaround is coherent; only the interface is missing.
