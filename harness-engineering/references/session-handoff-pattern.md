# Session Handoff Pattern

Source: Anthropic engineering research (Nov 2025)

## Table of Contents

- [Two-Part Structure](#two-part-structure) — initializer + coding agent
- [Initializer Agent (Session 1 Only)](#initializer-agent-session-1-only) — feature_list.json, progress.txt, init.sh
- [Coding Agent (Every Session After the First)](#coding-agent-every-session-after-the-first)
- [Handoff Artifacts](#handoff-artifacts) — what to include; update discipline
- [Priority-Injected Notepad (OMX)](#priority-injected-notepad-omx)
- [Claim-Safe Lifecycle](#claim-safe-lifecycle) — write state before starting work
- [Plans as First-Class Artifacts (OpenAI)](#plans-as-first-class-artifacts-openai)
- [Upgrading claude-progress.txt: ACE Evolving Playbooks](#upgrading-claude-progresstxt-ace-evolving-playbooks)
- [LangGraph as an Alternative to File-Based Handoffs](#langgraph-as-an-alternative-to-file-based-handoffs)
- [Pre-Built Implementations of This Pattern](#pre-built-implementations-of-this-pattern)
- [Running Multiple Sessions Concurrently](#running-multiple-sessions-concurrently) — git worktrees; parallel agents
- [Skill Learning: Harness-Extracted Reusable Patterns](#skill-learning-harness-extracted-reusable-patterns)
- [Parity Audit Artifact](#parity-audit-artifact)
- [When This Pattern Hits Its Limits](#when-this-pattern-hits-its-limits)

---

The key insight: agents need to quickly understand the state of work when starting with a fresh context window. The initializer + coding agent structure mirrors how effective software engineers work — a developer joining a project mid-sprint doesn't read every file in the repository. They check recent commits, read the task board, run the app, and pick up the next ticket.

## Two-Part Structure

```
SESSION 1: Initializer Agent
├── feature_list.json       ← 200+ features, all marked failing
├── claude-progress.txt     ← Running log of session activity
└── init.sh + git commit    ← Starts dev server, runs baseline test

                     ↓ HANDOFF ARTIFACTS (shared across every session)
                     
SESSION 2→N: Coding Agent
1. Read progress file + git log
2. Run init.sh — start dev server
3. Run baseline end-to-end test
4. Pick one failing feature
5. Build + test like a human user
6. Commit to git + update progress
7. Mark feature passing only if verified
```

## Initializer Agent (Session 1 Only)

The very first session is different from every session that follows. Its job is to set up the environment — the groundwork that every future session depends on.

It creates three things:

### feature_list.json

Structured JSON file that expands the user's prompt into individual features, each marked as failing by default.

```json
{
  "features": [
    {
      "id": "auth-001",
      "category": "authentication",
      "description": "User can register with email and password",
      "steps": [
        "Navigate to /register",
        "Fill in email and password fields",
        "Submit form",
        "Verify redirect to dashboard"
      ],
      "passes": false
    }
  ]
}
```

In Anthropic's claude.ai clone test, this produced 200+ granular features with specific pass/fail steps for each one.

**Why JSON, not Markdown**: Models are less likely to accidentally overwrite or reformat JSON. Structure is preserved across sessions.

**Why all marked `false`**: Prevents the agent from declaring victory early. A feature is only marked `true` after verified end-to-end testing — not after writing the code.

**Explicit constraint to include**: "It is unacceptable to remove or edit tests" — prevents agents from deleting features they can't implement.

### claude-progress.txt

A running log each session writes to at the end of its work, so the next agent knows where things stand without guessing.

Each entry should include:
- What was worked on
- What was completed (and confirmed passing)
- What was attempted but not completed
- Known issues or blockers
- What to tackle next

### init.sh + Initial Git Commit

A shell script that starts the dev server and runs a baseline end-to-end test before any new work begins. The initial git commit records the baseline files and structure.

This gives every subsequent session a known-good starting point.

## Coding Agent (Every Session After the First)

Every session after the first follows the same orientation sequence before writing a single line of code:

1. **Run `pwd`** — confirm working directory
2. **Read `claude-progress.txt` and git log** — understand what was last done
3. **Read `feature_list.json`** — pick the highest-priority incomplete feature
4. **Run `init.sh`** — start the dev server
5. **Run a baseline end-to-end test** — catch any existing bugs before adding new work
6. **Work on one feature at a time**

That last rule — work on one feature at a time — turned out to be the most important rule in the system. Without it, agents attempt multiple features simultaneously and lose track mid-session.

At the end of every session, the coding agent must:
- Commit all changes to git with a descriptive message
- Update the progress file with a clear summary of what was done
- Mark features as passing **only after proper end-to-end testing** — not after writing the code

Without explicit prompting, agents mark features complete after writing the code without verifying the feature worked from a user's perspective. Giving the agent access to Playwright MCP (or Puppeteer) and requiring it to test like a human user significantly improves feature accuracy.

## Handoff Artifacts

Three artifacts are shared across every session:

| Artifact | Purpose |
|---|---|
| `feature_list.json` | What's done vs. still failing |
| `claude-progress.txt` | Log of session activity |
| `git history` | Revert point + change log |

## Priority-Injected Notepad (OMX)

Source: oh-my-codex (OMX) project

The `.omx/notepad.md` pattern addresses a gap in the basic progress log: `claude-progress.txt` is a static append-only log that grows indefinitely and gets read at session start. The notepad is a different artifact:

- **Priority-injected**: inserted into the model's context at high priority, not appended at the end where it competes with session history
- **Mutable scratchpad**: the agent actively overwrites and condenses it during a session rather than appending to it
- **Survives compaction**: because it's injected at high priority, it persists through context window pruning rather than being summarized away
- **Auto-prunes**: working notes older than 7 days are removed automatically, preventing unbounded growth

The distinction from `claude-progress.txt`:

| Artifact | Written | Read | Priority | Lifecycle |
|---|---|---|---|---|
| `claude-progress.txt` | Appended at session end | Once at session start | Normal | Grows indefinitely |
| `notepad.md` | Overwritten during session | Re-injected each turn | High | Auto-prunes at 7 days |

The notepad is best used for active working state — current task, recent decisions, blockers — while the progress log preserves the historical record.

## Claim-Safe Lifecycle

Source: oh-my-codex (OMX) project

The `claude-progress.txt` pattern relies on the agent writing its handoff log at session end. If the session crashes or is interrupted, the handoff may be incomplete.

A more robust approach: write task state before work begins, not after. The claim-safe pattern:
1. When the agent picks up a task, it writes a "claimed" state to `.state/team/<task-id>.json` before starting
2. The task record captures: task ID, agent ID, timestamp, current phase
3. On interrupt or crash, the state file persists — the next session reads it and resumes from the exact phase where work was interrupted, not from scratch
4. On completion, the state transitions to "complete" and the record is retained for audit

This is the file-based equivalent of LangGraph checkpoints: rather than relying on the session completing cleanly, durable state is written at defined lifecycle points so recovery is always possible. See [spec-driven-workflows.md](spec-driven-workflows.md) for LangGraph's equivalent mechanism.

## Plans as First-Class Artifacts (OpenAI)

OpenAI's approach formalizes the distinction between different types of plan artifacts:

| Plan type | When | Contents | Lifetime |
|---|---|---|---|
| Lightweight plan | Small, bounded changes | Ephemeral scratch; may be inline comment | Discarded on completion |
| Execution plan | Complex work | Progress log + decision log | Checked into repo; versioned |

**Decision logs matter**: an execution plan isn't just a task list — it includes the decisions made during execution and why. The next agent (or the next session) can read the decision log and understand not just what was done but what alternatives were considered and rejected.

**Active, completed, and debt are all versioned**: active plans (work in progress), completed plans (finished work), and known technical debt are co-located and version-controlled. An agent starting a new session reads the active plan directory the same way it reads `feature_list.json` — the state of planned work is always in the repository.

This is an upgrade to the `claude-progress.txt` pattern: instead of a single running log, maintain a `plans/` directory with structured execution plan files that persist across sessions. GSD's `.planning/` directory implements this same idea — see [spec-driven-workflows.md](spec-driven-workflows.md) for detail.

## Upgrading claude-progress.txt: ACE Evolving Playbooks

The basic `claude-progress.txt` pattern logs what happened each session. The Agentic Context Engineering (ACE) framework (arXiv 2510.04618) upgrades this to an evolving playbook that accumulates learned strategies rather than just recording events.

ACE uses three roles to manage this:
- **Generator**: produces reasoning trajectories that surface effective strategies and recurring problems
- **Reflector**: extracts concrete insights from successes and errors across sessions
- **Curator**: integrates insights into compact delta entries using deterministic (non-LLM) deduplication logic

**Practical upgrade to the handoff pattern**: instead of (or alongside) a raw log, maintain a `playbook.md` that the Reflector updates at session end with extracted lessons. The Curator deduplicates to prevent bloat. Over weeks, the agent's starting context improves rather than growing indefinitely.

Results from ACE: 10.6% average improvement on agent tasks; 86.9% reduction in adaptation latency vs. baseline compression methods.

Apply this for long-running projects (weeks+) where patterns repeat across sessions. For short projects, the basic progress log is sufficient.

## LangGraph as an Alternative to File-Based Handoffs

LangGraph provides checkpoint-based state persistence as a framework-managed alternative to the file-based handoff artifacts.

| Approach | State managed by | Recovery on failure | Best fit |
|---|---|---|---|
| File-based (progress.txt + git) | The agent itself | Agent reads files on next session start | Arbitrary environments, no framework dependency |
| LangGraph checkpoints | The framework | Auto-resume from last checkpoint node | Python teams, infrastructure you control |

LangGraph checkpoints persist state at every graph node — if a session fails mid-task, execution resumes from the last checkpoint rather than restarting from scratch. This is automatic rather than requiring the agent to write handoff artifacts explicitly.

**Human-in-the-loop**: LangGraph has built-in interrupt support — pause execution at defined points for human review, then resume. Use this at the same decision points where you'd otherwise inject context reminders: before destructive operations, after each sprint, or when loop detection middleware fires.

Both approaches solve the same problem. The file-based pattern is more portable (works with any model in any environment); LangGraph checkpoints are more robust for infrastructure you own and operate.

## Pre-Built Implementations of This Pattern

Rather than building the initializer + coding agent pattern from scratch, several frameworks implement it for you:

**Ralph Wiggum** (`fstandhartinger/ralph-wiggum`) is the closest direct implementation — a bash loop that runs the agent repeatedly with fresh contexts, reading specs from disk each iteration. Its `specs/` folder maps to `feature_list.json`; its `IMPLEMENTATION_PLAN.md` maps to `claude-progress.txt`; its DONE signal gated on passing acceptance criteria maps to "mark features passing only after end-to-end testing." The difference: Ralph automates the loop; this pattern relies on the developer to re-invoke the agent.

**GSD** (`gsd-build/get-shit-done`) is an enhanced version — its `STATE.md` artifact is the progress file, its `.planning/` directory is the full artifact suite, and its wave execution system parallelizes across independent tasks rather than running them sequentially. GSD also adds a discuss phase before planning, which reduces ambiguity in the feature list before any coding begins.

**GitHub Spec Kit** produces the planning artifacts (spec → plan → tasks) that serve as the initializer output — the feature list and architecture decisions that every subsequent session reads. Spec Kit covers the initializer role; you still need the coding agent pattern for subsequent sessions.

See [spec-driven-workflows.md](spec-driven-workflows.md) for full comparison.

## Running Multiple Sessions Concurrently

The session handoff pattern is designed for sequential sessions: one agent finishes, writes handoff artifacts, and a new session picks up from where it left off. For concurrent work — multiple agents running simultaneously on different features — the environment model needs to extend beyond sequential handoffs.

**Git worktrees** are the natural primitive: each worktree is a full checkout of the repository at a branch, sharing git history but with an independent working directory. Multiple worktrees can be active simultaneously with no interference. Each agent session gets its own worktree; handoff artifacts live per-worktree.

**Ephemerality requirement**: creating a new worktree-based environment must be a single command taking 1-2 seconds, not a multi-step manual process. If setup takes minutes, you will avoid spinning up concurrent environments — and that directly limits throughput.

**Isolation requirement**: ports, database names, caches, and background job queues must be configurable per-environment (via env vars) so multiple environments can run on the same machine without cross-talk.

See [dev-environment-design.md](dev-environment-design.md) for the full fast/ephemeral/concurrent environment design pattern.

## Skill Learning: Harness-Extracted Reusable Patterns

Source: oh-my-claudecode (OMC, Yeachan Heo, 2026)

Rather than relying purely on the agent's built-in knowledge, the harness can extract reusable debugging and problem-solving patterns from sessions and store them as first-class artifacts.

OMC's `.omc/skills/` directory:
- When an agent successfully resolves a class of problem (e.g., a specific test failure pattern, a recurring build error), the harness extracts the resolution strategy as a skill file
- On future sessions, relevant skill files are auto-injected into context when the same problem signature is detected

This is the ACE evolving playbook concept (see above) specialized for problem-solving patterns rather than session history. The distinction:

| Artifact | Contains | Updated by |
|---|---|---|
| `claude-progress.txt` | What happened in each session | Agent at session end |
| `playbook.md` (ACE) | Learned strategies across sessions | Reflector + Curator |
| `.omc/skills/*.md` | Reusable resolution patterns by problem type | Harness on successful resolution |

The skill learning approach is particularly effective for codebases with recurring failure patterns — the same error class keeps appearing; the harness learns the fix and applies it automatically in future sessions rather than the agent re-deriving it each time.

**Implementation without a framework**: maintain a `handoffs/skills/` directory. When an agent resolves a non-obvious problem, prompt it to write a brief skill file: `symptom`, `diagnosis`, `resolution steps`. On future sessions, have the agent scan this directory before starting work. Low overhead; compounds over time.

## Parity Audit Artifact

Source: claw-code project (Sigrid Jin, April 2026)

A variant on the feature list: a dedicated file that tracks what the implementation has not yet matched against its specification. Rather than marking tasks as passing/failing, it explicitly lists known gaps with a "haven't caught up yet" framing.

The distinction:
- `feature_list.json` tracks what was built and whether it passes
- A parity audit tracks what exists in the reference/spec that the implementation doesn't yet cover — surfacing gaps that the agent never attempted rather than attempts that failed

```python
# parity_audit.py — run to generate a current gap report
def audit_parity():
    spec_features = load_spec()
    implemented = scan_implementation()
    gaps = [f for f in spec_features if f not in implemented]
    report_gaps(gaps, "docs/parity-gaps.md")
```

**Why this matters**: agents tend to mark tasks done after implementing the obvious path. The parity audit runs separately and surfaces what was never attempted — features that silently don't exist rather than features that failed tests. It's honest accounting for the agent and for reviewers.

The parity audit is particularly valuable when porting or rewriting an existing system: the spec is the original, the implementation is the rewrite, and the gap is what still needs work. But it generalizes to any project where the reference spec is larger than what one session can complete.

## When This Pattern Hits Its Limits

The two-part pattern works well for focused builds, but for more complex projects shows failure signatures:
- Features get stubbed instead of fully implemented
- UI looks complete but breaks the moment you use it
- When asked to assess its own work, the agent approves things a human reviewer would immediately reject

When this happens, move to the three-agent generator-evaluator loop. See [generator-evaluator-loop.md](generator-evaluator-loop.md).
