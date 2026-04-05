# Agent Failure Modes

Source: Anthropic engineering research (Nov 2025, Mar 2026)

## Table of Contents

- [The Agent Failure Cycle](#the-agent-failure-cycle)
- [The Four Failure Modes in Depth](#the-four-failure-modes-in-depth) — doing everything at once, context anxiety, declaring victory, self-evaluation bias
- [Which Frameworks Address Which Failure Modes](#which-frameworks-address-which-failure-modes)
- [Failure Mode 5: Pattern Replication and Entropy Accumulation](#failure-mode-5-pattern-replication-and-entropy-accumulation)
- [The Organizational Failure Mode: PoC Purgatory](#the-organizational-failure-mode-poc-purgatory)
- [Why a Better Model Doesn't Fix This](#why-a-better-model-doesnt-fix-this)

---

## The Agent Failure Cycle

```
High-level prompt given
        ↓
Agent attempts everything at once (no plan, no feature breakdown)
        ↓
Context window fills up → Context anxiety kicks in → Wraps up early even if incomplete
        ↓
Session ends mid-task → No progress file, no git commit
        ↓
Next session starts blind → Guesses what happened
        ↓
[cycle repeats]
```

Side effect running continuously: **Self-evaluation bias** — when asked to review its own output, the agent almost always says it looks good, even when features are broken or incomplete.

## The Four Failure Modes in Depth

### 1. Doing Everything at Once

Give an agent a high-level prompt like "build me a full-stack web app" and it will attempt to one-shot the entire thing.

It starts implementing features without a plan, burns through its context window halfway through, and leaves the next session to pick up a half-built codebase with no documentation of what was done or what comes next.

**Root cause**: No task decomposition guidance.
**Fix**: Feature list with "failing" status markers; one-feature-at-a-time instruction.

### 2. Context Anxiety

As an agent's context window fills up, some models begin wrapping up work prematurely because the model senses it's approaching its limit and starts closing things off.

Anthropic observed this in Claude Sonnet 4.5. The model would slow down, start summarizing instead of building, and signal completion on work that was unfinished.

This is one of the harder failure modes to catch because the agent sounds confident when it's doing it.

**Root cause**: Model behavior under token pressure without explicit guidance.
**Fix**: Context resets (preferred) — clear the context entirely, start fresh with structured handoff artifacts. Compaction (summarizing earlier conversation in place) preserves continuity but fails to eliminate context anxiety.

**Harness intervention point**: DeepSeek-V3.2 documented that context overflow behavior triggers around 80% token usage — don't wait for 100%. At 80%, apply one of three strategies:
- **Summary**: compress the overflowed trajectory into a structured handoff
- **Discard-75%**: drop the oldest 75% of tool call history, retain recent context
- **Discard-all**: full reset with structured handoff artifacts (the session-handoff pattern)

**Extending session length before reset is needed**: Moonshot Kimi K2's "interleaved thinking" (reasoning steps generated between tool calls, not just at the start) enables 200–300 sequential tool calls without human intervention. For long tool chain tasks, choosing a model with this capability can defer the need for a session reset.

Model notes:
- Claude Sonnet 4.5: requires periodic resets
- Claude Opus 4.5+: can operate continuously with automatic compaction
- Claude Opus 4.6: enabled eliminating sprint decomposition entirely for some tasks
- DeepSeek-V3.2 / Kimi K2: built-in context management and interleaved thinking reduce per-session degradation

### 3. Declaring Victory Too Early

After a few sessions of progress, a later agent instance will look around, see that meaningful work has been done, and conclude the project is complete — even when some features remain unbuilt.

Without a structured record of what's done and what isn't, nothing is anchoring the agent to the actual scope of the work.

**Root cause**: No comprehensive requirements inventory with explicit completion tracking.
**Fix**: `feature_list.json` with all features marked `"passes": false` by default; only mark passing after verified end-to-end testing.

Using JSON (not Markdown): models are less likely to accidentally overwrite or reformat JSON.

### 4. Self-Evaluation Bias

When you ask an agent to review its own output, it almost always says it looks good.

Anthropic tested this on both subjective tasks (UI design) and objective tasks (functional software). In both cases, agents evaluated their own work, often approving outputs that a human reviewer would immediately flag as mediocre or broken.

The same reasoning that produced the output is doing the evaluation. It's biased toward its own decisions.

Separating the generator from the evaluator doesn't fully fix this — the evaluator is still an LLM, and LLMs are generous toward LLM-generated work.

**Fix**: A standalone evaluator tuned to be skeptical. Tuning an external evaluator to be critical is far more tractable than making a generator self-critical. Once external feedback exists, the generator has something concrete to improve against.

Google DeepMind's Aletheia agent uses the same insight: a Generator proposes solutions, a Verifier checks for flaws, and a Reviser corrects until approved. Explicitly separating verification helps the model recognize flaws it initially overlooks during generation.

## Which Frameworks Address Which Failure Modes

Pre-built spec-driven frameworks package fixes for these failure modes. Use this to evaluate any framework you adopt:

| Failure mode | Addressed by |
|---|---|
| **Doing everything at once** | All — GSD wave execution + atomicity; Spec Kit tasks; Ralph spec-per-iteration; BMAD phased personas; SPARC 5-phase; Kiro task list |
| **Context anxiety** | GSD (fresh 200k+ context per agent); Ralph (fresh context every loop iteration); DeepSeek 80% threshold strategies |
| **Declaring victory too early** | GSD (DONE requires UAT.md pass + goal-backward trace); Ralph (DONE signal gated on acceptance criteria); BMAD (multi-persona sign-off); Kiro (EARS acceptance criteria) |
| **Self-evaluation bias** | GSD (gsd-verifier is a separate external evaluator); BMAD (different persona evaluates what another built); SPARC (refinement phase is a separate evaluation pass) |

Spec Kit and Kiro rely on human developers for evaluation — they address the first three failure modes structurally but leave self-evaluation bias to human review.

See [spec-driven-workflows.md](spec-driven-workflows.md) for full framework detail.

## Failure Mode 5: Pattern Replication and Entropy Accumulation

Source: OpenAI harness engineering (Feb 2026)

The four failure modes above occur within a single session or handoff boundary. This fifth mode operates across time, at the codebase level.

**Agents replicate patterns that already exist in the repository — including uneven or suboptimal ones.**

An agent that encounters an ad-hoc hand-rolled helper will write another one. An agent that finds a YOLO-style data probe will probe the same way. The existing codebase becomes the implicit training signal for what the agent does next. Bad patterns compound faster than good ones, because there are more of them and they're easier to imitate.

Left unaddressed, this creates progressive entropy: the codebase becomes harder for future agents to reason about, which causes more errors, which introduces more bad patterns.

**Cost without intervention**: OpenAI's team spent every Friday — 20% of the working week — manually cleaning up "AI slop" before they systematized entropy management. That cleanup cadence did not scale.

**Fix**: Two complementary mechanisms:
1. **Golden principles** — opinionated, mechanical rules encoded directly in the repository that define what good looks like. Not aspirational ("write clean code") but specific and enforceable:
   - Prefer shared utility packages over hand-rolled helpers — keeps invariants centralized and prevents the agent from writing N slightly-different versions of the same thing
   - Validate data at boundaries or use typed SDKs — don't probe data "YOLO-style" (guessing shapes and hoping); the agent can't accidentally build on unvalidated assumptions
2. **Recurring background cleanup tasks** — agents that scan for deviations from golden principles, update quality grades, and open targeted refactoring PRs. Most are reviewable in under a minute and can be automerged.

**Root cause**: No encoding of what "good" looks like; no recurring process to surface and correct accumulated drift.

See [context-engineering.md](context-engineering.md) → "Entropy Management" for the operational model of background cleanup tasks.
See [guides-and-sensors.md](guides-and-sensors.md) → "Entropy Agents" for the scheduling and review workflow.

## The Organizational Failure Mode: PoC Purgatory

Source: "Agentic Architectural Patterns" book

Beyond the session-level and codebase-level failure modes above, there is an organizational failure mode: thousands of enterprise teams build impressive AI agent demos that disintegrate when exposed to production environments.

> "The failure isn't typically in the 'brain' (the LLM) or the high-level intent. It's in the invisible scaffolding that makes a system survivable, observable, and cost-effective."

Teams in "PoC Purgatory" have working demos but not working systems. The gap is almost always operational: the demo has no observability, no cost guardrails, no resilience to provider failures, no audit trail, no escalation path. These aren't edge cases — they're first-class architectural concerns that demos defer and production demands.

The harness is the solution to PoC Purgatory. The patterns in this skill are the "invisible scaffolding."

## Why a Better Model Doesn't Fix This

The obvious solution when agents fail is to upgrade the model. But a more capable model running inside a poorly designed environment will still fail in the same ways.

The failure modes are structural, not capability gaps. They emerge from the interaction between model behavior and the environment — which is exactly what harness engineering addresses. Pattern replication (failure mode 5) is particularly immune to model improvements: a more capable agent replicates existing patterns more faithfully, not less.
