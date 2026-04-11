---
name: agentic-frameworks
description: Expert on agentic coding frameworks for AI-assisted development. Use when the user asks about BMAD, SpecKit, OpenSpec, GSD, Superpowers, or agentic coding workflows. Covers: choosing the right framework, how to use each one, comparing frameworks, combining frameworks, and understanding their trade-offs. Triggers on questions like "which agentic framework should I use", "how does GSD work", "BMAD vs SpecKit", "should I use Superpowers", "what is context rot", or any discussion of structured AI development methodologies.
---

# Agentic Frameworks Expert

Five frameworks dominate structured AI-assisted development as of 2026. This skill covers how to choose, use, and combine them.

## The Five Frameworks at a Glance

| Framework | Stars | Core Problem Solved | Best For |
|---|---|---|---|
| **SpecKit** | ~87k | Spec-first discipline | Greenfield, strict architecture |
| **BMAD** | ~44k | Role-based team simulation | Enterprise, full lifecycle |
| **GSD** | ~51k | Context rot / parallel execution | Complex multi-phase features |
| **OpenSpec** | ~39k | Brownfield delta changes | Existing codebases, daily iteration |
| **Superpowers** | ~147k | Process discipline + TDD enforcement | Production quality, regression prevention |

All share a common triad: **Agents** (roles/personas), **Workflows** (phase sequences), **Skills** (atomic capabilities). The differences are in what they constrain and how hard.

## Quick Decision Guide

**Choose SpecKit** — greenfield project, want strict spec-as-source-of-truth, architectural constraints (CLI-first, anti-abstraction, TDD mandated), and multi-tool support across 20+ agents.

**Choose BMAD** — need the full enterprise lifecycle (idea → PRD → architecture → stories → code → QA), multiple stakeholders, audit trails, compliance documentation, or role-based artifact handoffs.

**Choose GSD** — complex feature with many independent tasks, long sessions where context quality degrades, parallel execution needed, or budget for higher token spend.

**Choose OpenSpec** — working on an existing codebase, need lightweight delta specs for ongoing changes, want fast iteration without per-feature ceremony.

**Choose Superpowers** — production code quality is paramount, need TDD enforced (not just recommended), teams experiencing inconsistent AI behavior, or complex features requiring 2+ hours of development.

**When in doubt: start with GSD.** It has the second-best capability in most categories, and its context isolation architecture addresses the most universal failure mode.

## Hybrid Combinations

- **SpecKit + GSD** — strongest spec layer + strongest execution engine. Best for greenfield projects where requirements must be locked before parallel implementation begins.
- **BMAD + Superpowers** — enterprise artifact trail + TDD enforcement. BMAD handles architecture/planning personas; Superpowers gates each implementation task.
- **OpenSpec + Superpowers** — minimal ceremony for brownfield change management + quality gates during execution. Practical for daily production work on legacy systems.

## The Shared Triad

All five frameworks implement three primitives:
- **Agents** — bounded roles with defined responsibilities (BMAD personas, GSD subagents, Superpowers skills)
- **Workflows** — phase sequences with quality gates between steps
- **Skills** — reusable units of work (write PRD, run tests, generate diagram, review code)

## Framework Reference Files

Load these when the user asks about a specific framework:

- **[BMAD](references/bmad.md)** — persona system, four-phase workflow, Party Mode, Agent-as-Code
- **[GSD](references/gsd.md)** — wave parallelism, context isolation, subagent types, token costs
- **[SpecKit](references/speckit.md)** — constitution, gated phases, artifact structure, CLI commands
- **[OpenSpec](references/openspec.md)** — delta markers, change folders, fast-forward, brownfield workflow
- **[Superpowers](references/superpowers.md)** — brainstorming gate, TDD iron law, social engineering defense, skill modules

## Cross-Framework Techniques

These patterns apply regardless of which framework you use — or with no framework at all.

### Adversarial Prompting Before Implementation

Before asking AI to build anything, ask it to argue against your plan first. Effective prompts:
- "What are the three strongest reasons this architecture is wrong?"
- "What would a senior engineer regret about this decision three years from now?"
- "What am I assuming that might not be true?"

The failure mode this prevents: AI produces exactly what you asked for, and you asked for the wrong thing. This is **distinct from Superpowers' brainstorming gate** — that gate elicits clarifying questions and design alternatives; adversarial prompting specifically solicits *critique of your stated approach*.

One adversarial pass takes ~5 minutes. It surfaces the assumptions most likely to cause rework. Use it before any non-trivial implementation, and before any `/gsd-plan-phase`, `/speckit.specify`, or BMAD planning invocation.

### Session Topology: AI as Workforce

Parallel sessions work best when each session has a defined *type* — not just "different tasks," but different kinds of thinking:

| Session Type | What it does |
|---|---|
| **Critique** | Adversarial pass before implementation |
| **Implementation** | Builds the feature |
| **Simplification** | Reviews output for redundancy and unnecessary abstractions |
| **Review** | Checks correctness, security, spec compliance |
| **Testing/Docs** | Generates tests or documentation from the completed implementation |

Two sessions (implementation + simplification/review) already eliminates most of the sequential waiting that dominates single-session development. The bottleneck is rarely writing code — it's reviewing it. Running review and simplification in parallel with the next implementation task reclaims that wait time.

**Connection to frameworks:** GSD's wave-based parallelism and Superpowers' subagent-driven development mechanize this. But the session-type mental model applies even without a framework — two Claude Code tabs configured with different roles costs nothing and no installation.

### Living Context Files as Compounding Assets

A CLAUDE.md that captures *why* decisions were made — not just *what* the conventions are — compounds in value over time. The high-value content is the **failure log**:

```markdown
## What We've Tried and Won't Try Again
- [2024-Q3] Redis for session state → race conditions, migrated to Postgres
- [2024-Q4] GraphQL subscriptions → latency on mobile, reverted to REST polling

## Architecture Decisions
- Chose Y over Z because [reason]. Trade-off accepted: [what we gave up].
```

Every mistake encoded becomes a permanent instruction that prevents repetition. Update after any session where something was learned the hard way.

**Connection to frameworks:** GSD's `STATE.md` serves this purpose within a project. The CLAUDE.md pattern extends it across sessions and projects — and unlike framework-specific files, it's readable by every tool.

## Gotchas

- **Every framework's token cost is higher in practice than documented.** GSD's 4:1 overhead is a floor; BMAD can hit 80–100x vs. unassisted Claude; Superpowers loads 22k tokens of skill context at startup. Pro plan users get burned — Max plan is the realistic minimum for sustained use of any of these.
- **Agent compliance is advisory, not enforced**, across all five frameworks. Quality gates, workflow phases, and TDD mandates are deontic instructions — LLMs can and do rationalize past them, especially as context fills. None of these frameworks have hard programmatic enforcement.
- **Spec drift is unsolved** in all spec-focused frameworks (SpecKit, OpenSpec, BMAD). Specs written at the start of a project diverge from the code within days with no automatic reconciliation.
- **All frameworks degrade on brownfield projects** — SpecKit ignores existing architecture, BMAD exhausts context ingesting it, GSD's `--auto` assumes greenfield, OpenSpec is the least bad option.
- GSD worktree mode (`use_worktrees: true`) silently deletes committed files in some versions — disable on brownfield projects.
- BMAD's TEA agent alone can consume 86% of a 200k context window before any task work begins.
- Superpowers has no structured iteration path — after execution, users fall back to unstructured chat for refinement.
- SpecKit's biggest unsolved problem: no `/speckit.update` command — once specs exist, there's no first-class way to evolve them.
- All five frameworks assume high-reasoning models; output quality degrades noticeably with weaker models.
- This landscape moves fast — check GitHub issue trackers and release dates before recommending; known bugs are often fixed within weeks.
