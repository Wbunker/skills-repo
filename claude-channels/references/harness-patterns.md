# Harness Patterns for Channels

Channels is an event-driven primitive. These are the three core harness patterns it enables, with concrete prompts and architectural notes.

## Table of Contents
- [Pattern 1: CI failure triage](#pattern-1-ci-failure-triage)
- [Pattern 2: Monitoring alert triage](#pattern-2-monitoring-alert-triage)
- [Pattern 3: Async task notification](#pattern-3-async-task-notification)
- [Channels vs scheduled tasks vs /loop](#channels-vs-scheduled-tasks-vs-loop)
- [Composing Channels with other harness primitives](#composing-channels-with-other-harness-primitives)

---

## Pattern 1: CI failure triage

**Trigger**: CI build or test suite fails
**Action**: Claude investigates, reports root cause
**Response**: Summary delivered to Telegram/Discord before you've checked your phone

### When to use

Use when you want immediate signal on CI failures without polling dashboards. Especially valuable for long-running pipelines (10+ minutes) where you've moved on to other work by the time they fail.

### Prompt template

```
When you receive a ci_failure event:
1. Fetch the failing run logs: gh run view ${{ run_id }} --log --repo ${{ repo }}
2. Identify the specific failure: compilation error, test failure, lint error, or infrastructure issue
3. Check if this test failed in any of the last 5 runs (flaky test signal):
   gh run list --repo ${{ repo }} --branch main --limit 10
4. Report in Telegram:
   - What failed (test name or error message, one line)
   - Likely cause (2-3 sentences)
   - Flaky? (yes/no with run count)
   - Suggested fix (1-2 sentences) or "needs investigation"
Keep the total report under 150 words.
```

### Autonomy level

Read-only investigation: use **default mode** (no `--dangerously-skip-permissions`). If you also want Claude to push a fix for lint/formatting failures automatically, use `--dangerously-skip-permissions` with an explicit bounds statement:

```
If and only if the failure is a lint or formatting error (eslint, prettier, ruff, gofmt),
fix it and push to the PR branch. For all other failure types, report only.
```

### Architecture notes

- CI payload should include the run ID and repository so Claude can fetch logs via `gh`
- Authenticate `gh` before starting the Channels session so Claude has access
- For private repositories, ensure the GitHub CLI has a token with `repo` scope

---

## Pattern 2: Monitoring alert triage

**Trigger**: Monitoring platform fires an alert (error rate spike, latency increase, host down)
**Action**: Claude investigates logs and recent deployments
**Response**: Triage summary — what it is, whether it's a regression, severity assessment

### When to use

Use when you're on-call or responsible for a service and want Claude to do first-pass triage so you receive a summary rather than raw alert noise. Claude can cut the time from "alert fired" to "I understand what's happening" significantly.

### Prompt template

```
When you receive a monitoring_alert event:
1. Note the alert name, severity, and affected service from the payload
2. Check recent logs for the affected service (last 15 minutes):
   journalctl -u ${{ service }} --since "15 minutes ago" | tail -200
   or: kubectl logs -n production -l app=${{ service }} --since=15m | tail -200
3. Check for recent deployments:
   git log --oneline -10 -- src/${{ service }}/
4. Assess:
   - Is this correlated with a recent deployment? (compare alert start time vs last deploy)
   - Is the error rate still climbing, stable, or recovering?
   - Is there a clear error message in logs?
5. Send to Telegram:
   - Alert: ${{ alert_name }} (${{ severity }})
   - Status: [recovering / stable / worsening]
   - Deployment correlation: [yes (deploy at HH:MM) / no recent deploys]
   - Key error: [one-line summary or "no clear error in logs"]
   - Recommended action: [rollback / investigate further / likely transient]
```

### Autonomy level

Triage and report: **default mode** is appropriate — Claude reads logs and git history, no writes.

If you want Claude to auto-rollback on clear deployment regressions, that's `--dangerously-skip-permissions` territory with explicit bounds:

```
If and only if: the alert is a 5xx error spike AND it started within 10 minutes of a deployment,
initiate a rollback: kubectl rollout undo deployment/${{ service }} -n production.
In all other cases, report only.
```

### Architecture notes

- Monitoring webhook payload should include service name in a consistent field Claude can reference
- Ensure Claude has log access in the session environment (authenticated kubectl, SSH, or log aggregator CLI)
- For PagerDuty/OpsGenie, configure the webhook to fire on alert creation (not just acknowledgment)

---

## Pattern 3: Async task notification

**Trigger**: You initiate a long-running task from your terminal, then leave
**Action**: Claude completes the task autonomously
**Response**: Claude messages you when done, or when it needs a decision

### When to use

Use when tasks take long enough that you'll naturally context-switch away: migrations, large refactors, test suite runs, data pipeline jobs, overnight batch work. Instead of checking back manually, you get a message when done.

### Prompt template (task-start message to send via Telegram)

```
Run the following migration: npm run migrate:prod
Report progress every 5 minutes.
If you encounter any error that requires a decision, stop and ask me.
When complete, report: how many records were migrated, any warnings, total duration.
```

### Prompt template (CLAUDE.md for all Channels sessions)

```markdown
# Channels session defaults

When working on async tasks, follow these reporting conventions:

- Progress updates: send a brief status every 5-10 minutes for tasks over 15 minutes
- Blocking decisions: stop and ask rather than guessing — describe the decision and your recommendation
- Completion report: what was done, any warnings, whether human review is needed
- Failures: describe what failed, what you tried, what you recommend, then stop

Keep all messages under 200 words. Use bullet points.
```

### Autonomy level

Long-running write tasks require `--dangerously-skip-permissions`. Structure your task description to include stopping conditions:

```
Refactor all API handlers in src/api/ to use the new middleware pattern from src/middleware/auth.ts.
Stop and ask before modifying any file outside src/api/.
Stop and ask if any test fails after your changes.
When all tests pass, open a PR with title "refactor: migrate API handlers to new auth middleware".
```

### Architecture notes

- Pair this with a CLAUDE.md that defines notification conventions so Claude doesn't have to figure out reporting format each session
- For interactive decisions, the pairing ensures only you can respond — others in a shared Telegram group cannot steer the agent
- Consider using `--dangerously-skip-permissions` with a CLAUDE.md that restores some constraints via the guides layer

---

## Channels vs scheduled tasks vs /loop

| | Channels | Scheduled tasks | `/loop` |
|---|---|---|---|
| Trigger | External event push | Timer (cron) | Timer (session-scoped) |
| Direction | Bidirectional — you can reply | Outbound notification only | In-session only |
| Machine required | Yes (local plugin) | No (cloud option) | Yes (session open) |
| Best for | Event-driven triage, remote control | Recurring maintenance, entropy agents | Monitoring during active session |

Use Channels when you need **event-driven reaction** (something happened, now investigate). Use scheduled tasks when you need **recurring maintenance** (check for drift every night regardless of events). Use `/loop` when you're actively watching a session and want periodic polling.

These compose: a scheduled task can post to a Telegram channel that's also used for Channels interaction; `/loop` can supplement a Channels session with periodic status checks while the session is open.

---

## Composing Channels with other harness primitives

**Channels + hooks**: Hooks still fire in a Channels session. A `PostToolUse` hook that auto-formats code runs when Claude makes edits remotely, just as it would in an interactive session. A `Stop` hook that gates completion on passing tests applies equally.

**Channels + CLAUDE.md**: CLAUDE.md governs Claude's behavior for all sessions including remote Channels sessions. Use it to define notification conventions, stopping conditions, and constraint lists that apply when Claude operates autonomously.

**Channels + subagents**: Claude can delegate sub-tasks to subagents during a Channels session. A subagent with read-only tool restrictions can safely investigate without inheriting the broader `--dangerously-skip-permissions` scope — though the subagent's tool restrictions are what matters, not the parent session's permission mode.

**Channels + `/batch`**: For large-scale changes initiated remotely, Claude can spawn `/batch` workers in isolated worktrees. Each worker opens its own PR. You receive a summary message when all workers complete.
