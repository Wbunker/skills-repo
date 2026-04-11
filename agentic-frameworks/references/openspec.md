# OpenSpec Reference

**GitHub:** https://github.com/Fission-AI/OpenSpec  
**Stars:** ~39k | **License:** MIT | **Latest:** v1.3.0  
**Maintainer:** Fission-AI (community)

## Core Philosophy

"Fluid not rigid, iterative not waterfall, easy not complex, built for brownfield not just greenfield."

Where SpecKit enforces strict phase gates, OpenSpec lets you update any artifact at any time. The fundamental unit of work is a **change** (delta), not a feature spec.

## Delta Marker System

Instead of restating an entire specification when modifying existing functionality, OpenSpec uses semantic section headers:

```markdown
## ADDED Requirements
- New behavior X...

## MODIFIED Requirements  
- Changed behavior Y from A to B...

## REMOVED Requirements
- Removed behavior Z...
```

The archive parser operates at the requirement level (not brittle header matching) — changes are isolated and don't interfere with each other.

## Change-as-Folder Structure

Each change lives in its own folder, enabling parallel work without merge conflicts:

```
changes/[feature-name]/
├── proposal.md       ← intent, scope, approach
├── design.md         ← technical decisions
├── tasks.md          ← implementation checklist
├── .openspec.yaml    ← optional metadata
└── specs/
    └── [domain]/
        └── spec.md   ← delta spec with ADDED/MODIFIED/REMOVED sections

openspec/changes/archive/[date]-[name]/   ← completed changes
```

## Core Workflow

| Step | Command | Description |
|---|---|---|
| 1. Explore *(optional)* | `/opsx:explore` | Conceptualize before committing to a change |
| 2. New | `/opsx:new` | Initiate change, scaffold folder |
| 3. Continue | `/opsx:continue` | Build artifacts incrementally (proposal → design → specs → tasks) |
| 4. Fast-forward | `/opsx:ff` | Skip incremental steps, generate all planning artifacts at once |
| 5. Apply | `/opsx:apply` | Execute implementation tasks |
| 6. Verify | `/opsx:verify` | Validate implementation aligns with delta specs |
| 7. Sync | `/opsx:sync` | Merge delta specs back into main specs (semantic sync, not file overwrite) |
| 8. Archive | `/opsx:archive` | Complete change, move to archive |

## Installation & Key Commands

```bash
# Requirements: Node.js 20.19.0+
# Follow GitHub README for agent-specific installation

/opsx:explore         # conceptualize before committing
/opsx:new             # initiate a change, scaffold folder
/opsx:continue        # incrementally create artifacts
/opsx:ff              # fast-forward: generate all planning artifacts at once
/opsx:apply           # execute implementation tasks
/opsx:verify          # validate implementation vs. delta specs
/opsx:sync            # sync delta specs into main specs semantically
/opsx:archive         # complete a change, move to archive
/opsx:bulk-archive    # archive multiple changes with conflict detection
/opsx:onboard         # 15-minute guided walkthrough (start here)
```

## Supported AI Tools (21 as of v1.0)

Claude Code, Cursor, Windsurf, Continue, Gemini CLI, GitHub Copilot, Amazon Q, Cline, RooCode, Kilo Code, Augment, CodeBuddy, Qoder, Qwen, CoStrict, Crush, Factory, OpenCode, Antigravity, iFlow, Codex.

## SpecKit vs. OpenSpec Comparison

| Dimension | SpecKit | OpenSpec |
|---|---|---|
| Primary target | Greenfield | Brownfield |
| Phase enforcement | Hard gates | Fluid / iterative |
| Change granularity | Full spec per feature | Delta per change |
| Spec update mechanism | Rewrite spec files | `## ADDED/MODIFIED/REMOVED` + sync |
| Fast-path | None | `/opsx:ff` |
| AI tool support | ~11 | 21 |
| Maintainer | GitHub (official) | Fission-AI (community) |
| Avg output per change | ~800 lines | ~250 lines |

## When to Use OpenSpec

- **Brownfield projects** — modifying existing systems where restating the full spec is impractical
- **API/contract changes, migrations, security/privacy work** where ambiguity causes expensive rework
- **Cross-team or multi-repo changes** needing explicit behavioral contracts
- **Teams that want lightweight structure** with progressive rigor (can stay in "lite spec" mode for routine changes)
- **Multi-AI-tool shops** — broadest tool support, no vendor lock-in

**Skip for:** Large greenfield projects needing comprehensive architecture documentation — OpenSpec's lightweight approach may produce insufficient depth.

## Gotchas

### Workflow Enforcement (Agent Compliance)

- **Agents skip the workflow gates.** The most-reported real failure mode: agents (especially in GitHub Copilot, OpenCode, and Cursor) proceed directly from `/opsx:explore` or `/opsx:ff` into implementation, skipping spec creation entirely. OpenSpec's deontic instructions are advisory — the LLM can and does ignore them, particularly after context grows large. (Issues #405, #869, #875)
- **Rules in schema instructions are not deterministically enforced.** Any `rules` field that says "after X, do Y" depends on the LLM remembering to comply. In long sessions or when context is near the limit, post-create hooks and validation sub-agent invocations are silently skipped. There is no enforcement mechanism outside the PostToolUse hook pattern. (Issue #825)
- **Context degradation at ~40% window usage causes instruction drift.** After extended sessions (155k+ tokens observed in the wild), agents forget workflow constraints, miscount tasks, and claim success on incomplete changes. The framework doesn't detect or warn about this. (Issue #405)
- **`/opsx:archive` AI skill vs. CLI discrepancy.** The auto-generated AI commands for `/opsx:archive` perform manual file operations rather than calling `openspec archive` — the opposite of what docs and tutorials show. This means spec sync may silently not happen during the archive step. (Issue #863)
- **After `/opsx-archive` executes, sync is sometimes not triggered.** A confirmed bug in v1.2.0: the archive command completes but the spec sync step is skipped. (Issue #799)

### `/opsx:sync` and Delta Merge Failure Modes

- **`/opsx:sync` can produce unexpected spec.md mutations.** Real users report running sync and finding their main spec files changed in ways they didn't expect — sections restructured, content altered — with no easy rollback path. The semantic merge operates at the requirement level, not line level, so diffing the result against git history is non-trivial. (Issue #911)
- **MODIFIED/REMOVED delta ops silently fall through on name mismatches.** A `#### Scenario: Foo (MODIFIED)` that doesn't match any existing scenario in the main spec gets appended as a new scenario instead of erroring. Typos in delta marker names go undetected. This was identified as a known gap in the parser. (Issue #847)
- **MODIFIED requirement fails at sync if the requirement was renamed or removed in an earlier change.** Accumulated changes that touch the same spec domain can produce conflicts where a later delta references a requirement that no longer exists under that name. The sync aborts without merging, but leaves the delta in place — re-running sync will fail repeatedly until manually resolved.
- **Conflicting deltas from parallel changes require manual resolution.** `/opsx:bulk-archive` detects spec conflicts and stops — it does not auto-merge. Teams running parallel changes against the same domain spec must archive serially or manually diff-merge. (Deepwiki / official docs)

### Installation and Platform Issues

- **`npm install -g` silently corrupts the PowerShell profile on Windows.** The installer appends a completion block to `$PROFILE` without consent, and if the existing profile is UTF-16 LE (BOM), the UTF-8 append breaks PowerShell entirely — all aliases and dot-sourced scripts fail to load. Fixed as opt-in in v1.3+, but the default was destructive. (Issue #948)
- **Segfault on Node 22.22.0 / RHEL 9.6.** Confirmed at `openspec init`; no workaround documented. (Issue #811)
- **PostHog telemetry blocks `openspec init` on air-gapped / enterprise networks.** The CLI throws a network error and may fail to initialize. No opt-out mechanism was available until users filed the request; enterprise users must either whitelist the PostHog endpoint or wait for the opt-in flag. (Issue #754, Issue #895)
- **Shell completion is installed silently (pre-v1.3).** The installer modifies shell profile files without prompting. The fix (opt-in) landed in v1.3 but existing installs are not self-healing.

### Tool Integration Fragility

- **Tool API mismatches across AI agents.** Skills hardcode tool names that differ per agent: `AskUserQuestion` vs `question`, `TodoWrite` vs `todowrite`, `general-purpose` subagent vs `general`. OpenCode users hit these as silent failures where the skill runs but the wrong tool is invoked or ignored. (Issue #920)
- **Continue.dev + Ollama: tool invocation interpreted as a terminal command.** When using a local Ollama model, the agent treats `open_spec_propose` as a shell command rather than a registered tool, producing `Tool open_spec_propose not found`. Only affects non-Claude backends. (Issue #925)
- **`openspec-apply-change` blocked by hardcoded `tasks.md` check.** If you configure a custom schema with `tasks.yaml`, the apply skill checks for `tasks.md` specifically and returns a "blocked" state even when `tasks.yaml` is present. Schema-agnostic path handling wasn't implemented until after v1.2.0. (Issue #922)
- **`instructions apply` fails on glob-pattern artifact paths.** If spec files live at `specs/*/spec.md` (nested structure), the CLI cannot locate them; only flat paths are supported. (Issue #942)
- **Skills-only delivery mode emits `/opsx:*` command references** in output that don't exist in the skills-only install — agents try to invoke commands that aren't registered, silently doing nothing. (Issue #879)
- **Codex CLI: agent ignores "Request approval" instruction.** The Codex backend does not honor the confirmation-before-proceed deontic in skills, making unattended runs unsafe. (Issue from bug list)

### Spec Authoring and Workflow Limitations

- **Specs do not self-update during `/opsx:apply`.** If the agent takes a different implementation approach than planned, the proposal/design artifacts are not updated to reflect reality. You can end up with specs that describe something different from what was built — this is a documented design gap, not a bug. (Issue #684, intent-driven.dev)
- **Cannot iterate on artifacts once all are marked ready.** After proposal, design, specs, and tasks are all complete, the agent refuses to modify them, citing "use `/opsx:apply`." There is no `/opsx:clarify` or repair path without manually editing files. (Issue from bug list)
- **`/opsx:explore` eagerly transitions to implementation.** The explore phase is meant for conceptualization, not implementation, but on some models/tools it produces a plan and immediately starts coding. Especially observed in GitHub Copilot. (Issue #875)
- **Fast-forward (`/opsx:ff`) produces misaligned designs on complex brownfield changes.** Skipping the incremental proposal-review loop means the design step gets no human correction before specs are written. On existing codebases with non-obvious constraints, ff-generated specs regularly miss domain nuance.
- **AI-reverse-engineered specs for existing code are unreliable.** If you use OpenSpec to generate specs for existing brownfield code (instead of for upcoming changes), the AI-generated specs look convincing but diverge from actual behavior. Using them as the baseline for future changes amplifies misalignment over time. (intent-driven.dev)

### v1.0 Breaking Change Migration

- **Three workflow commands removed entirely.** `/openspec:proposal`, `/openspec:apply`, and `/openspec:archive` were deleted in v1.0. Any existing muscle memory, scripts, or team runbooks referencing them broke silently — the old commands produce no "deprecated" warning, just "unrecognized command." (CHANGELOG, v1.0 release)
- **Tool-specific instruction files deleted on upgrade.** `CLAUDE.md`, `.cursorrules`, `AGENTS.md`, and `project.md` are removed by `openspec init`. The `project.md` removal is not automatic (requires manual review), but the others are — teams storing custom instructions in those files lose them if they don't back up first.
- **`project.md` → `config.yaml` migration is manual.** Content must be manually reviewed and rewritten into `context:` + `rules:` YAML structure. The guide warns that context is injected into every planning request with a 50KB maximum — verbose project.md files need trimming or they bloat every prompt.
- **IDE restart required after upgrade.** Skills are detected at startup; existing sessions don't pick up new commands until the tool is restarted. This catches users who upgrade mid-session.

### Community and Longevity Concerns

- **Community-maintained, not vendor-backed.** Fission-AI is a community organization, not a company with enterprise support. Users have explicitly raised longevity questions (Issue #937: "hasn't been updated in over a month — has it stopped being updated?"). The maintainers responded that v1.3.0 was in progress, but the concern recurs with each quiet period.
- **MAINTAINERS.md exists** (added Issue #495) but the project has no SLA, no commercial support tier, and no LTS branch. Evaluate runway before adopting for production-critical workflows.
