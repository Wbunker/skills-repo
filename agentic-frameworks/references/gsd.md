# GSD (Get Shit Done) Reference

**GitHub (v1):** https://github.com/gsd-build/get-shit-done  
**GitHub (v2/CLI):** https://github.com/gsd-build/gsd-2  
**Stars:** ~51k (v1), ~5k (v2) | **License:** MIT  
**Creator:** Lex Christopherson / TÂCHES

## Core Concept: Context Rot

GSD's entire architecture targets context rot — the quality degradation as context windows fill:

| Context Utilization | Effect |
|---|---|
| 0–30% | Peak quality |
| 50–70% | Corner-cutting begins |
| 70%+ | Hallucinations increase |
| 80%+ | Requirements forgotten |

**Solution:** Fresh 200k-token context window per task via subagent isolation. Task 50 gets the same quality as Task 1.

## Planning Files (`.planning/` directory)

| File | Purpose |
|---|---|
| `PROJECT.md` | Vision anchor — always loaded |
| `REQUIREMENTS.md` | Scoped v1/v2 with phase traceability |
| `STATE.md` | Decisions, blockers, cross-session memory |
| `PLAN.md` | XML-structured atomic tasks with `<verify>` sections |
| `CONTEXT.md` | Phase-specific design decisions |
| `research/` | Ecosystem knowledge from researcher agents |

## Subagent Types

| Agent | Role |
|---|---|
| **Researcher** (×4 parallel) | Investigates domain patterns, libraries, architecture |
| **Planner** | Creates XML atomic tasks with verify criteria; detects scope reduction |
| **Executor** | Implements tasks in fresh 200k context; atomic git commit per task |
| **Verifier** | Validates against requirements; flags silent scope drops |
| **Debugger** | Scientific-method hypothesis testing; auto-spawned on failures |
| **Orchestrator** (v2) | State machine reading disk files for autonomous execution |

## Wave-Based Parallelism

Tasks organized into dependency-ordered waves. Independent tasks run in parallel; dependent tasks sequence after.

```
Wave 1: [Researcher A] [Researcher B] [Researcher C] [Researcher D]  ← parallel
Wave 2: [Synthesizer]                                                  ← waits for Wave 1
Wave 3: [Roadmapper]                                                   ← waits for Wave 2
```

Favor **vertical feature slices** (end-to-end) over horizontal layers (all models first, then all APIs) — vertical minimizes inter-task dependencies and maximizes parallelism.

## Core Workflow

| Phase | Command | Description |
|---|---|---|
| 1. Init | `/gsd-new-project` | Interview → domain research → requirements → roadmap |
| 2. Discuss | `/gsd-discuss-phase N` | Capture preferences, edge cases before planning |
| 3. Plan | `/gsd-plan-phase N` | Research approaches → XML atomic task plan with verify criteria |
| 4. Execute | `/gsd-execute-phase N` | Spawn subagents in parallel waves; fresh context per task; atomic commits |
| 5. Verify | `/gsd-verify-work N` | Human UAT + auto-spawns debugger agents on failures |
| 6. Ship | `/gsd-ship N` | Create PR from verified work |

## Installation & Key Commands

```bash
# Install
npx get-shit-done-cc@latest              # interactive
npx get-shit-done-cc --claude --global   # non-interactive, Claude Code global

# Workflow
/gsd-new-project              # initialize project
/gsd-discuss-phase N          # discuss before planning
/gsd-plan-phase N             # research + plan
/gsd-execute-phase N          # execute in waves
/gsd-verify-work N            # verify + debug
/gsd-ship N                   # create PR

# Utilities
/gsd-quick                    # fast path (supports --discuss --research --validate --full)
/gsd-next                     # auto-detect next step
/gsd-map-codebase             # brownfield analysis
/gsd-new-milestone            # add milestone
/gsd-complete-milestone       # archive/tag release
/gsd-settings                 # configure mode

# GSD-2 (standalone CLI — separate install)
npm install -g gsd-pi@latest
/gsd                          # step mode (pauses between units)
/gsd auto                     # autonomous execution
gsd headless                  # CI/script mode (JSON output, exit codes)
```

**Supported runtimes (v1):** Claude Code, OpenCode, Gemini CLI, Kilo, Codex, Copilot, Cursor, Windsurf, Augment, Cline, and ~10 others.

## Token Cost Model

| Profile | Models Used |
|---|---|
| Quality | Opus throughout |
| Balanced (default) | Opus planning + Sonnet execution |
| Budget | Sonnet + Haiku verification |

- **4:1 token overhead** vs. single-session coding
- **Large projects:** 1–2M tokens per phase realistic
- **Pro plan ($20/mo) exhausts quickly** — Max plan ($100–200/mo) strongly recommended
- Skip `--research` flag when implementation approach is already known

## When to Use GSD

- Multi-phase projects spanning multiple sessions
- Complex features requiring quality consistency across many tasks
- Large codebase refactoring with coordinated changes
- Projects with 20+ tasks requiring parallel execution

**Skip for:** Quick bug fixes (use `/gsd-quick`), exploratory prototyping, tight token budgets.

## Gotchas

### Token Consumption — The #1 User Complaint
- **4:1 overhead is a floor, not a ceiling.** After a version bump (v1.5.27) users reported 4–10x increases in token burn with no quality improvement. A trivial UI change (moving a table into a collapsible card) consumed 200k tokens in planning alone and ran 20+ minutes. (Issue #120)
- **Pro plan ($20/mo) exhausts in 1–2 hours of GSD use.** Several Max plan ($100–200/mo) users burned through their weekly budget in 2 days. Users explicitly removed GSD because of token burn.
- **Defaulting to Opus multiplies costs 5x** because GSD spawns many subagents per phase — verify model profile settings before starting a project.
- **GSD-2 draws from "extra usage"** (API charges on top of subscription), not from the Max/Pro subscription allocation — effectively double-billed for Max subscribers.

### Worktree Mode: Silent File Deletion
- **`workflow.use_worktrees: true` can silently delete committed files.** One user documented 8 deletion incidents across 6 phases: worktrees branching from `main` instead of the feature branch HEAD, executor running `git clean`, `SUMMARY.md` destroyed by `git worktree remove --force`. (Issue #2075)
- **Disable worktrees on brownfield projects:** set `workflow.use_worktrees: false` unless on a clean greenfield project.

### Project CLAUDE.md Invisible to Subagents (pre-v1.31)
- **Until v1.31.x, GSD subagents never received the project-level CLAUDE.md.** All project-specific instructions, coding conventions, and security rules were invisible to every executor run. A documented post-production audit found IDOR vulnerabilities, hardcoded session secret fallbacks, and user enumeration bugs — all caused by security rules that executors never saw across 41 executor runs. (Issue #671)
- **Verify you are on v1.31.x+ before relying on CLAUDE.md instructions in GSD workflows.**

### Bash Permissions Not Documented
- **Fresh installs fail mid-phase with "Permission denied."** GSD executors need broad Bash permissions (`bin/rails:*`, `bundle:*`, `git commit:*`, `git merge:*`, `git worktree:*`, etc.) not included in Claude Code's default `settings.json`. Not documented as a prerequisite — users hit this on first real execution. (Issue #2071)

### GSD-2 Specific Failures
- **Auto-mode compaction deadlock:** when auto-mode is executing, GSD's `session_before_compact` hook cancels ALL compaction including overflow recovery. If the context window fills, the session goes permanently idle with no error — silently consuming tokens until the 30-minute hard timeout. One user tracked 39 instances, with cost spikes up to 8.7x average ($33 for a single unit). (Issue #3971)
- **SQLite corruption on macOS after ~1h22m** of continuous auto-mode due to mmap + WAL mode on APFS. Auto-mode terminates with no recovery. (Issue #3900)
- **Auto-mode runs silently with no summary** — users came back from a break to find $17 in tokens spent in circles with nothing to show. Phases marked "complete" with deliverables missing or wrong.
- **No rollback path from GSD-2 to GSD-1.** The maintainer later posted recommending v1 as the default again, which users interpreted as a signal of v2 abandonment. No official clarification was provided. (Discussion #2468, Issue #3993)
- **GSD-2 originally implemented an unauthorized Anthropic OAuth flow** (violating ToS) to use subscription accounts. It was removed — users who used it against third-party providers reported account bans. (Issue #3952)

### Brownfield and Monorepo Limitations
- **`--auto` flag during init always assumes greenfield** — skips brownfield detection entirely.
- **Codebase analyzer skips `.ps1`, `.cs`, `.razor`, `.sql` files** — polyglot and Windows-stack projects get incomplete maps.
- **Single `.planning/` directory for the entire repo** — in monorepos, running execute-phase for one app overwrites another app's state. No multi-project isolation. (Issue #108)
- **Map-codebase on medium-complexity Java backend** was reported stuck for 4+ hours consuming tokens with no output.

### MCP Tools Broken for Subagents (pre-CC 2.1.30)
- **Custom subagents in `.claude/agents/` could not access MCP servers** due to a Claude Code upstream bug. GSD's subagents are defined this way — Context7, Serena, and other MCP tools were unavailable in research and executor agents for an extended period. (Issues #859, #2074; fixed in CC 2.1.30+)

### Acceptance Criteria Enforcement Was Advisory (pre-Issue #1959 fix)
- **Until the fix landed, "MANDATORY" verification was advisory text** — executors could and did skip it. Phases that "passed" before this fix may have shipped without actual acceptance criteria verification.

### Other
- **Skipping discuss phase leads to rework** — 5–10 minutes of preferences captured upfront prevents most of it.
- **Plan atomicity** — each task must fit in ~200k tokens; large features need manual subdivision before planning.
- **GSD-2 is a separate install** (`gsd-pi@latest`) — architecturally incompatible with v1.
- **iOS/mobile scaffolding generates incorrect output** — scaffold templates are written for web/JS and produce a macOS CLI binary instead of an Xcode project. (Issue #2023)
- An ETH Zurich study (Feb 2026) found LLM-generated context files like PROJECT.md reduce task success rates ~3% while increasing costs 20%+. GSD inlines these into nearly every session.
