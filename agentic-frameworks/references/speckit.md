# SpecKit Reference

**GitHub:** https://github.com/github/spec-kit  
**Stars:** ~87k | **License:** MIT | **Latest:** v0.1.4 (Feb 2026)  
**Maintainer:** GitHub (official)

## Core Philosophy

"Specifications don't serve code; code serves specifications." The spec is the authoritative source of truth — code regenerates when specs change.

## Constitution (`memory/constitution.md`)

Immutable architectural DNA — nine articles governing the project:
- Article I: Simplicity (≤3 projects in scope)
- Article II: CLI-first interfaces
- Article III: Anti-abstraction (no premature abstraction)
- Article IV: Integration-first contract definitions
- Article V: Test-first requirements
- (+ four more governing constraints)

Amendments require documented rationale and maintainer approval. The constitution is a hard constraint — not a suggestion.

## Gated Phases

Each phase must pass quality gates before advancing. Gates check for simplicity, anti-abstraction violations, and integration-first contract definitions.

| Phase | Command | Artifacts Produced |
|---|---|---|
| 1. Constitution | `/speckit.constitution` | `memory/constitution.md` |
| 2. Specify | `/speckit.specify [description]` | `spec.md` |
| 3. Clarify *(optional)* | `/clarify` | Resolved `[NEEDS CLARIFICATION]` markers |
| 4. Plan | `/speckit.plan [technical guidance]` | `plan.md`, `data-model.md`, `contracts/`, `research.md`, `quickstart.md` |
| 5. Tasks | `/speckit.tasks` | `tasks.md` (with `[P]` marking parallel-safe tasks) |
| 6. Analyze *(optional)* | `/analyze` | Cross-document consistency validation report |
| 7. Implement | `/speckit.implement` | Code |

## Artifact Structure

```
specs/[feature-branch]/
├── spec.md
├── plan.md
├── data-model.md
├── contracts/
├── research.md
├── quickstart.md
└── tasks.md

memory/
└── constitution.md      ← project root, governs all features
```

`[NEEDS CLARIFICATION]` markers are auto-inserted into specs where requirements are ambiguous — must be resolved before planning proceeds.

## Installation & Key Commands

```bash
# Installation (varies by agent)
# Claude Code / Cursor / Windsurf / Gemini CLI:
# Follow GitHub README instructions — typically copy SKILL files or use the agent's plugin system

# Codex CLI uses $speckit-* prefix instead of slash commands
# All other agents use /speckit.* prefix

/speckit.constitution     # establish governing principles
/speckit.specify [desc]   # generate spec from feature description
/speckit.plan [guidance]  # produce implementation plan from spec
/speckit.tasks            # derive task breakdown from plan
/speckit.implement        # execute tasks
/analyze                  # cross-document consistency check
/clarify                  # resolve spec ambiguities
```

## Supported AI Tools

GitHub Copilot (primary), Claude Code, Gemini CLI, Cursor, Qwen, OpenCode, Codex CLI, Windsurf, Kilo Code, Augment, Roo. 60+ community extensions, 6+ community presets.

## When to Use SpecKit

- Greenfield projects where upfront spec rigor pays off
- Teams needing architectural consistency enforced across multiple AI tools
- Specification-as-source-of-truth workflows (regenerate code from specs)
- Projects with strict architectural constraints (anti-abstraction, CLI-first, TDD mandated)
- Multi-feature coordination where requirements interconnect

**Skip for:** Brownfield/incremental changes (openspec is better), GUI-heavy apps (CLI-first article conflicts), exploratory/research phases where requirements are still unknown.

## Gotchas

### Spec Drift — The Central Unsolved Problem
- **No first-class update command.** `/speckit.specify` always creates a new branch and new artifacts — it is optimized for net-new work, not amendments. Once you have specs across many branches, later specs contradict earlier ones. Discussion #152 (113 comments) is entirely about this. Issue #1191 tracks the missing `/speckit.update` command.
- **No upgrade path between SpecKit versions.** Running `specify init --here` on an existing project can overwrite a customized `constitution.md`. No diff/merge mechanism exists — teams reconcile manually after each SpecKit update.
- **Biggest unsolved problem practitioners report:** "The system has changed; update the spec to match." There is no first-class answer.

### Performance vs. Claims
- **The "15 minutes" claim does not survive contact with real projects.** Scott Logic measured 33m30s of agent time + 3.5 hours of human review for a feature that took 8 minutes + 15 minutes with iterative prompting — roughly 10x slower. The 1–3 hours/feature estimate assumes greenfield with no review/refinement cycles.
- **Spec output is often longer than the code it describes.** One practitioner generated 2,577 lines of markdown for a feature whose implementation was 444 lines — 4x the length of the code.
- **Token overhead is material and underreported.** Every slash command, constitution rule, and template burns context. A typical full run produces ~800 lines of artifacts before a single line of code is written.

### Brownfield Is Not a Supported Workflow
- **`specify init` ignores existing codebase architecture.** The generated constitution and spec templates treat the existing project structure as noise — agents generate duplicates of existing classes, ignore tech stack, and require manually injecting "architectural guidance." (Issues #806, #1436, Discussion #746)
- **Multi-repo brownfield projects have no guidance.** SpecKit assumes a single-repo model; typical enterprise features span web + microservice + shared-module repos. No documented workflow covers this.
- **No bug workflow.** Issue #103 ("How are bugs specified?") has no authoritative answer. No first-class bug spec concept exists. (Issue #1092)

### Agent Non-Compliance
- **Detailed specs don't prevent agents from ignoring them.** Even with specs loaded, agents routinely ignore existing file/class structure, miss specific library constraints, and create duplicate implementations. (Discussion #1784, Martin Fowler article)
- **Loading too many spec files creates context pressure** that causes agents to lose the thread mid-task — SpecKit helps manage context but does not enforce it.

### Constitutional Constraints in Practice
- **CLI-first (Article II)** is a poor fit for GUI-heavy applications — blocks patterns the spec would normally allow.
- **The boundary between constitution and feature spec is unclear** — users stuff architecture details into specs to make planning work, making specs messy. (Issue #1149)
- **Most brownfield teams add "justified exceptions"** to constitutional constraints within hours of first use — the exception mechanism is the real workflow.

### Maintenance and Lock-in
- **Single-maintainer bus-factor risk.** When a key maintainer departed, 22 PRs piled up with zero merges in one month. The project recovered, but the episode prompted a community exodus toward OpenSpec. (Discussion #1482)
- **Tool lock-in on init.** Switching AI tools (e.g., Claude → Copilot) requires manually reformatting agent files — no `specify migrate` command. The `--ai` flag is also being deprecated, introducing another migration cycle. (Issues #1228, #2169)
- **Community extensions are unaudited by GitHub** — vet before trusting in production.
- **Enterprise/air-gapped deployments** require manual wheel bundle setup.
- **Greenfield, single repo, team with discipline:** net positive. Below a ~5-point story, iterative prompting is faster and cheaper.
