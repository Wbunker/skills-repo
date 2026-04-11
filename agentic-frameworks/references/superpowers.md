# Superpowers Reference

**GitHub:** https://github.com/obra/superpowers  
**Stars:** ~147k | **License:** MIT  
**Author:** Jesse Vincent / Prime Radiant

## Core Philosophy

Superpowers is a **process-discipline system**, not an orchestration library or spec tool. Its premise: AI agents skip best practices under pressure in the same way humans do. The fix is **structural compliance** — making process steps impossible to skip, not just recommended.

Built on Robert Cialdini's persuasion principles (authority, commitment, social proof, etc.) as validated by the Wharton research paper "Call Me a Jerk: Persuading AI." Design principle: *operate AI on compliance rather than understanding*.

## Seven-Phase Workflow

| Phase | Description | Gate |
|---|---|---|
| 1. Brainstorming | Socratic discovery: single clarifying questions, YAGNI applied ruthlessly, 2–3 design alternatives with tradeoffs, incremental approval checkpoints | **Hard gate**: no code until design doc committed to git + explicit human approval |
| 2. Git Worktree Setup | Isolated branch created, full project setup run, test baseline verified green | Must be green before new code |
| 3. Writing Plans | Approved design → granular 2–5 min tasks with exact file paths and verification steps | Written for "an enthusiastic junior engineer with no project context" |
| 4. Subagent-Driven Development | Fresh subagents dispatched per task (clean 200k context window per task) | Controller agent coordinates |
| 5. Test-Driven Development | Mandatory RED-GREEN-REFACTOR, no exceptions without explicit human permission | **Iron Law**: no production code before failing test |
| 6. Code Review | Two-stage review between tasks: (1) spec compliance, (2) code quality | Critical issues block next task |
| 7. Finishing the Branch | Test verification, merge/PR decision, worktree cleanup | — |

## Mandatory Gates

**Brainstorming Gate** — The system refuses to proceed to implementation until the design document has been written and the human has explicitly signed off. Cannot be bypassed by the agent.

**TDD Iron Law** — No production code without a failing test first. "Tests written after code pass immediately, which proves nothing." If code is found before its corresponding failing test: **the code is deleted and restarted from test-writing**. Only exception: explicit human-partner permission.

**Two-Stage Review Gate** — A dedicated reviewer subagent (not the implementing subagent) runs after each task:
1. Specification compliance — does the code do what the plan said?
2. Code quality — does it meet quality standards?

Critical failures block the next task from starting.

## Social Engineering Defense

Named, explicit concern. AI agents skip TDD when given plausible pressure narratives (e.g., "production is down, $5k/minute in losses" or "we already have 45 minutes of working async infrastructure").

Superpowers addresses this by:
- Blocking "red-flag phrases" that signal rationalization (e.g., "I know what that means")
- Enforcing pre-action skill checks: "BEFORE any response or action, invoke relevant skills"
- **The 1% Rule**: if there is even a 1% chance a skill applies, the agent must invoke it
- Stress-testing instructions through deliberate pressure scenarios; iteratively strengthening `getting-started/SKILL.md` whenever the agent bypasses a gate

The mechanism is structural — the agent physically cannot mark a task complete without review artifacts — rather than relying on "understanding" why TDD matters.

## Skills Module Inventory

| Category | Modules |
|---|---|
| Meta | `using-superpowers`, `writing-skills` |
| Workflow | `brainstorming`, `writing-plans`, `executing-plans`, `subagent-driven-development`, `dispatching-parallel-agents` |
| Quality | `test-driven-development`, `systematic-debugging`, `verification-before-completion`, `requesting-code-review`, `receiving-code-review` |
| DevOps | `using-git-worktrees`, `finishing-a-development-branch` |

## Installation

| Platform | Command |
|---|---|
| Claude Code | `/plugin install superpowers@claude-plugins-official` |
| Cursor | `/add-plugin superpowers` |
| GitHub Copilot CLI | `copilot plugin marketplace add obra/superpowers-marketplace` |
| Gemini CLI | `gemini extensions install https://github.com/obra/superpowers` |

After install, restart the agent. A session-start hook initializes the skill system automatically. No per-session slash command needed — skills auto-trigger based on context.

## Superpowers vs. GSD

| Dimension | Superpowers | GSD |
|---|---|---|
| What it constrains | The development *process* (TDD, gates) | The execution *environment* (context isolation) |
| TDD stance | Mandatory, enforced by deletion | Not a core constraint |
| Brainstorming gate | Hard gate, no code without explicit approval | No equivalent |
| Context strategy | Fresh subagent per task | Thin orchestrators, fresh 200k per task |
| Test coverage result | 85–95% reported | Not TDD-focused |
| Best for | Process discipline, regression elimination, high-stakes production | Projects 50+ files where context degradation is the primary failure mode |

**Practical combination:** Use GSD for exploratory/prototype phases; switch to Superpowers when promoting to production. Note: Superpowers' interactive prompts can block GSD's autonomous input model — coordinate the handoff explicitly.

## When to Use Superpowers

- Complex features requiring 2+ hours of development
- Production code where high test coverage is required
- Teams experiencing inconsistent AI agent behavior
- Preventing regression bugs is a priority
- Long-term maintainability matters more than speed

**Skip for:** Throwaway prototypes, trivial changes (typo fixes, dependency bumps), projects where speed-to-prototype is the primary metric.

## Gotchas

### Token Cost and Performance Reality
- **All 14 SKILL.md files load at session start** — 22k tokens of baseline context (11% of a 200k window) before any work begins. (Issue #190)
- **Plans time out on complex tasks.** `writing-plans` generates the entire plan in one output — routinely hits API timeout (20–45 min waits) with no resume path. Workaround: ask Claude to write a skeleton first, then fill sections. (Issues #1026, #809)
- **Plan files get re-read 3–4 times during execution** as context compresses — a 48k-character plan costs 45–60k tokens in plan-reads alone before code is touched. (Issue #512)
- **The original two-stage review loop was empirically wrong.** Testing across 5 versions showed identical output quality whether it ran or not. The maintainer replaced it with inline self-review checklists. Earlier documentation describing it as a core strength is now outdated. (Issue #750)
- **Real user cost shock:** Multiple users burned a week's subscription credit on a single complex feature. One burned 75% of a 4-hour Claude Code limit on a 2-line bug fix that was still wrong.

### Brainstorming Gate in Practice
- **Asks generic questions despite rich project context.** Even with a detailed CLAUDE.md loaded, brainstorming asks "What type of project is this?" The skill doesn't tell the model that CLAUDE.md, memory, and git status are already loaded. (Issue #849)
- **No team workflow.** No path for one teammate to hand off a pre-approved spec, or for a team to skip brainstorming on known requirements. The gate is binary: full dialogue or CLAUDE.md override.
- **No formal lightweight path for small changes.** The framework acknowledges you should skip it for quick bug fixes but provides no `/superpowers-quick` equivalent — users fall back to unstructured chat.

### Plans Write the Code Twice
- **`writing-plans` produces complete implementation code in the plan document.** Users report plans containing full function bodies, 70-line test files, and exact shell commands — then the executor rewrites this to files. One user produced an 11,500-line plan with all code pre-written. (Issues #694, #895)
- This creates two failure modes: (1) when implementation reveals a better approach, the plan's code is "wrong" even though the intent is valid; (2) over-specified plans hinder capable models (cite: AGENTIF benchmark) — the model follows the SOP instead of using engineering judgment.
- **Maintainer's position:** "this is how it was designed to operate." Tension is real and unresolved.

### Subagent and Review Failures
- **Review gates are routinely skipped by rationalization.** Agents rationalize skipping for "trivial JSON edits" or "small changes," self-report PASS even when cross-file contracts are broken. In one case, CSS classes, EJS element IDs, and JS selectors built by parallel agents never saw each other's output — producing mismatches discovered only in debugging. (Issue #995)
- **Agents anchor to 5 tasks regardless of plan size.** Example workflow text with "Extract all 5 tasks" caused agents to stop after 5 tasks on 12+ task plans. (Issue #1058)
- **Subagent auto-creates worktrees without consent**, then leaves orphaned worktrees on disk. Now changing to opt-in. (Issue #991)
- **Parallel subagents don't start automatically** despite documentation claiming they do. (Issue #945)

### Git Worktree Problems
- **Worktree step was missing from brainstorming checklist for months** despite being documented as REQUIRED — `writing-plans` expected a worktree context that was never created. (Issue #1080)
- **Exploration agents return main-repo paths inside worktrees**, causing write agents to bypass worktree isolation and land changes on the main branch silently. (Issue #1040)
- **Path incompatibility with `claude --worktree` resume** — Superpowers creates worktrees at `.worktrees/`, but Claude Code only recognizes `.claude/worktrees/`. Sessions can't be resumed with `claude -w <name>`. (Issue #1009)
- **Worktree cleanup fails when CWD is inside the worktree** being removed. (Issues #238, #987)

### Platform and Installation
- **Windows has multiple unresolved issues:** SessionStart hook doesn't auto-register, hardcoded bash paths don't exist, plugin freezes Claude Code terminal keyboard in VSCode, git-based install fails with ENOENT leaving no skills registered. (Issues #225, #404, #1068)
- **Plugin marketplace inconsistently downloads 0–10 of 14 skills** due to a race condition in Claude Code's git clone mechanism. Most critical missing: `subagent-driven-development`. (Issue #818)
- **Hardcoded model IDs break API proxies.** Subagents dispatched with snapshot-specific IDs (e.g., `claude-haiku-4-5-20251001`) fall back to Session Mode on proxies that don't recognize them, spiking token consumption. (Issue #1099)
- **Brainstorm server has a WebSocket origin validation gap** — a malicious page visited during an active session can inject content into the AI's event stream. Medium severity, confirmed. (Issue #1014)

### The 85–95% Coverage Claim
- **No independent user has published actual coverage numbers** to validate this figure. It appears only in marketing-style summaries of official docs.
- TDD is routinely skipped by agent rationalization in practice.
- The figure only applies to freshly written code — not to existing untested code being extended.
- Coverage is self-reported by agents whose checklists they sometimes skip.

### No Iteration Path
- **No `superpowers:iterate` or `superpowers:refine` skill.** After execution, there is no structured path for "the spec was 80% right." Users fall back to unstructured chat — exactly the behavior Superpowers was designed to prevent — at the moment they need discipline most. (Issue #921)
- **Plans don't mark themselves complete.** After execution, all plan checkboxes remain unchecked — no way to tell from the plan file whether work was completed without cross-referencing git log. (Issue #1075)
- **The skill chain assumes a frozen codebase.** If another session merges to main between brainstorm and execution, the spec is stale and agents don't know. (Issue #989)
