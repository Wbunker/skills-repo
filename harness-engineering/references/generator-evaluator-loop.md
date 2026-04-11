# Generator-Evaluator Loop (Three-Agent Architecture)

Source: Anthropic engineering research (Mar 2026), inspired by GAN architecture

## Table of Contents

- [Why This Pattern Exists](#why-this-pattern-exists) — self-evaluation bias
- [Architecture](#architecture) — planner, generator, evaluator roles
- [The Three Agents](#the-three-agents) — planner / generator / evaluator prompts and responsibilities
- [The Self-Evaluation Bias Problem](#the-self-evaluation-bias-problem)
- [Sprint Contracts](#sprint-contracts)
- [Agent Isolation and Role Scoping](#agent-isolation-and-role-scoping)
- [Decomposition and the Independence Test](#decomposition-and-the-independence-test) — over-delegation failure mode; dependency types; encoding in CLAUDE.md
- [Research Agent Patterns](#research-agent-patterns) — structured findings format; citation drift + checker; cross-session lessons.md
- [Intent-First Routing: Interview Before Planning](#intent-first-routing-interview-before-planning)
- [Cross-Model Evaluation via the Codex Plugin](#cross-model-evaluation-via-the-codex-plugin) — adversarial-review, rescue, review-gate
- [Mixed-Provider Teams](#mixed-provider-teams)
- [Dynamic Evaluator Value](#dynamic-evaluator-value)
- [Cost-Quality Reference (Anthropic)](#cost-quality-reference-anthropic)
- [Iteration Loop Behavior](#iteration-loop-behavior)
- [Pre-Built Implementations of This Pattern](#pre-built-implementations-of-this-pattern)

---

## Why This Pattern Exists

The two-part initializer/coding pattern hits a ceiling on complex builds. Failure signatures:
- Features get stubbed instead of fully implemented
- UI looks complete but breaks on interaction
- Self-evaluation bias: agent approves its own broken work

The fix draws from GANs (Generative Adversarial Networks): separate the agent doing the work from the agent judging it. Applied to agent design — one agent generates, one evaluates.

## Architecture

```
User prompt (1-4 sentences)
        ↓
    PLANNER
    Expands prompt → full product spec + design language
    Avoids granular implementation (over-specification cascades errors)
        ↓
  Sprint contract (generator + evaluator agree on "done" before build)
        ↓
GENERATOR ←──────────── fail + feedback ────────────── EVALUATOR
Builds one sprint at a time        Navigates live app via Playwright MCP
Self-evaluates before handoff      Grades against sprint contract criteria
        ↓ sprint output             ↓ pass
                           Sprint marked complete
                           Feature list updated in git
                           [next sprint — loop continues]

Evaluator grading criteria:
  Design quality · Originality · Craft · Functionality
  (each with a hard pass/fail threshold)
```

## The Three Agents

### Planner

Takes a 1–4 sentence prompt and expands it into a full product spec and design language.

Responsibilities:
- Stay at high-level product scope — not granular implementation details
- Define visual language and design direction before any code is written
- Identify opportunities to weave AI features into the spec
- Avoid over-specifying implementation: upstream errors cascade into everything the generator builds

In Anthropic's test, the planner expanded a one-sentence prompt into a 16-feature spec across ten sprints — including features the solo agent never attempted.

### Generator

Builds the application one sprint at a time from the planner's spec.

Before each sprint:
- Negotiates a sprint contract with the evaluator — agreeing on what "done" looks like before writing a single line of code

During the sprint:
- Implements one sprint worth of features
- Self-evaluates at end of sprint before handing off to evaluator

The sprint contract prevents over-specification while ensuring alignment. It makes "done" concrete and testable.

### Evaluator

Uses Playwright MCP to navigate the live application as a real user would — not static screenshots, not code inspection.

Grades each sprint against four criteria, each with a hard pass/fail threshold:

| Criterion | What it measures |
|---|---|
| **Design quality** | Does it feel like a coherent whole vs. a collection of parts? |
| **Originality** | Evidence of custom decisions vs. template/AI patterns |
| **Craft** | Typography, spacing, color harmony, contrast ratios |
| **Functionality** | Usability and task completion |

If any criterion fails, the sprint fails. The evaluator returns specific, actionable feedback so the generator can fix issues without additional investigation.

**Evaluator calibration matters**: Use few-shot examples with detailed score breakdowns to align evaluator judgment with your preferences and reduce score drift. This is especially important for subjective domains.

**Trust scoring over binary pass/fail**: Rather than a binary pass/fail gate, an evaluator can maintain a numeric trust score that accumulates penalties for missing rigor. My-Jogyo's research harness (Yeachan Heo, 2026) implements this: missing statistical rigor (no confidence intervals) costs -30 trust points; missing effect sizes costs additional points. Below a threshold, the output is rejected; above it, it passes. The score also informs downstream routing — low-trust outputs get more careful human review; high-trust outputs can be automerged.

Apply this pattern when the evaluation domain has multiple quality dimensions that matter independently. A single pass/fail threshold hides which dimensions failed; a score breakdown shows where the deficit is and guides the generator's next revision.

**Adversarial verification**: The evaluator's default stance is skeptical; adversarial verification goes further — the evaluator's explicit role is to *try to disprove* the generator's claims, not just find weaknesses. My-Jogyo's Baksa agent is a "PhD Reviewer" who adversarially challenges findings with trust scoring penalties. Applied to code: the evaluator tries to break functionality, find security holes, and disprove test coverage claims rather than just confirming they look correct.

**Why interactive evaluation beats static review**: Running Playwright on a live app and clicking through it (vs. reading static screenshots) increases evaluation depth and catches interaction bugs that visual review misses. It also increases wall-clock runtime.

## The Self-Evaluation Bias Problem

Separating generator from evaluator doesn't fully solve self-evaluation bias — the evaluator is still an LLM, and LLMs are generous toward LLM-generated work.

What works: **tuning the standalone evaluator to be skeptical**. Tuning an external evaluator to be critical is far more tractable than making a generator self-critical. Once external feedback exists, the generator has something concrete to improve against.

Reading evaluator logs and iteratively updating prompts where judgment diverges is the practical calibration process. It takes multiple rounds.

**The taste gap — what the evaluator cannot do alone:**

> "$ralph will not develop taste on your behalf. No amount of agent coordination replaces the founder who knows what the thing should feel like when a real person uses it."
> — Sigrid Jin, "What you need to learn from claw-code repo" (April 2026)

The evaluator catches defects against stated criteria. It cannot catch the gap between a technically correct output and one that has *taste* — the moment where you look at what the agents produced and say "this is not good enough, and here is specifically why, and here is what it should feel like instead." That judgment is irreducibly human.

This is why evaluator calibration matters: it's not just bias correction — it's the mechanism by which human taste gets encoded into the evaluation criteria. Without ongoing calibration, the evaluator grades against what LLMs tend to produce rather than what the product should feel like. The calibration process is how human judgment enters the loop.

## Sprint Contracts

Before any code is written, generator and evaluator agree on:
- Specific implementation details for this sprint
- Testable success criteria
- What "done" looks like from a user perspective

This is the most important coordination mechanism in the system. Without it, the generator optimizes for code that exists and the evaluator grades against unstated expectations.

## Agent Isolation and Role Scoping

Each agent in the three-agent system should have strictly scoped context and tools — not shared access to everything.

**Per-agent tool restrictions** (validated by OpenClaw architecture):
- Planner: read-only access to specs and design references; no write or execution tools
- Generator: write and execute tools; no evaluation tools
- Evaluator: Playwright/browser tools and read access; no write tools that could bias its assessment

This enforces the role separation architecturally, not just through prompt instructions. An evaluator that can't write code is structurally prevented from "helpfully" fixing what it's supposed to be judging.

**Deterministic handoffs over LLM routing**: agent-to-agent handoffs should be deterministic where possible. The planner completes its spec and hands off to the generator — not an LLM router that decides whether the spec is ready. The generator completes a sprint and explicitly hands to the evaluator. LLM-based routing introduces a decision point that can fail; explicit handoff at defined completion states does not.

**Sprint contract as formal interface**: the sprint contract between generator and evaluator functions as the contract defined in arXiv 2603.25723 — explicit inputs, expected outputs, validation criteria, and permission boundaries agreed before execution begins. This makes the handoff inspectable and recoverable if either agent fails partway through.

## Decomposition and the Independence Test

Sources: Alireza Rezvani, production experience (April 2026); SEQCV (NeurIPS 2025); MAST failure taxonomy (arXiv:2503.13657); ACONIC (arXiv:2510.07772); TDAG (arXiv:2402.10178)

The planner's most consequential decision is not *how many* tasks to create — it is *which tasks are actually independent*. Over-delegation (splitting tasks that share hidden dependencies) pays for parallel context windows and produces output worse than a single session would have given. Under-delegation misses parallelism that's genuinely available.

The MAST failure taxonomy analyzed 1,600+ multi-agent execution traces and found **specification and design issues — primarily poor decomposition — account for ~42% of all failures**. Over-splitting and under-splitting are the dominant failure modes; the planner cannot fix these without modeling what the executor can actually do.

**The basic independence test:** A sub-task is independent if its answer (or output) would not change based on the answer (or output) of any other sub-task in the same batch. Apply this to every proposed split before spawning workers.

**What to check — four dependency types:**
- **Data flow dependency** — Task B requires an artifact, file, or state produced by Task A (the most visible type)
- **Shared conclusion dependency** — Task B's answer is partially determined by Task A's findings (e.g., "what are the honest limits of X" is not independent from "what is the current state of X" — limits are part of state)
- **Shared state dependency** — Both tasks read from or write to the same external resource, making parallel runs produce conflicts or redundant work
- **Hidden / latent dependency** — Tasks appear logically independent but LLM outputs carry correlations that propagate across the task graph; one worker's framing of a finding influences how another worker's finding is interpreted at synthesis time

**The hard problem:** The basic independence test is correct in theory but insufficient in practice. Ground-truth answers are not available at decomposition time — you cannot verify that Task B's answer is truly unaffected by Task A's until both have run. SEQCV (NeurIPS 2025) found that hidden latent correlations in LLM outputs create error cascades that pure logical independence checking cannot catch. Their finding: **sequential execution with consistency checking between steps outperforms pure parallel decomposition** despite appearing less efficient. Real independence is rare; most multi-step work has semi-dependencies that only manifest at execution time.

**Practical implication:** Use parallelism for tasks that are structurally independent — different files, different domains, no shared data flow — and treat synthesis as the error-recovery step where latent correlations surface. For tasks where the conclusions of one constrain the interpretation of another, run sequentially and condition later tasks on earlier results.

**What to do when tasks collapse:** If the independence test reveals that two proposed sub-tasks are not independent, merge them. Fewer workers running genuinely independent tasks outperforms more workers running entangled ones. In production use, enforcing this test reduced average worker count per query while increasing output quality.

**Granularity calibration:** The planner must model what the executor can actually do. Tasks split "too granularly" force sub-decisions into the executor that require orchestrator-level context; tasks split "too broadly" leave the executor stuck. Neither is detectable from the prompt alone — it requires knowing the executor's tool access, context budget, and typical capability boundary.

**Where decomposition quality lives:** The interesting engineering work in a multi-agent system is not in the orchestrator implementation, the subagent definitions, or the MCP wiring. It is in the decomposition rules. A well-architected orchestrator with bad decomposition rules produces worse output than a thoughtful single-session query.

**Encoding this in CLAUDE.md:**
```markdown
## Decomposition Rules
- Default to plan mode on any query that contains more than one question
- Decompose only when sub-questions are genuinely independent
- A sub-question is independent if its answer would not change based on the answer to another sub-question in the same query
- Check for: data flow dependencies, shared conclusion dependencies, shared state, and latent correlations at synthesis
- Fan out to workers via the Task tool, never inline
- Workers return structured findings, not transcripts
- When in doubt, merge and run sequentially rather than split and run in parallel
```

See [Research Agent Patterns](#research-agent-patterns) for the full research-specific pattern, and [Intent-First Routing](#intent-first-routing-interview-before-planning) for resolving intent ambiguity before decomposition begins.

## Research Agent Patterns

Source: Alireza Rezvani, production experience (April 2026)

Patterns that apply specifically to orchestrator-worker research systems (information gathering, synthesis, citation-backed output). Complement the general three-agent architecture.

### Structured Findings Format

Workers should return structured findings, not reasoning traces or full session transcripts. The orchestrator synthesizes findings; it does not re-read investigation logs.

```markdown
- Claim: [what was found]
- Source URL: [verified URL]
- Supporting quote or paraphrase: [exact text from source]
- Confidence: high / medium / low
```

"High" confidence means the claim is directly stated in the source. "Medium" means paraphrased from clear supporting content. "Low" means inferred or from a secondary source. The orchestrator uses confidence levels to weight synthesis and flag uncertain claims.

### Citation Drift and the Citation-Checker Subagent

**Citation drift** is a failure mode distinct from hallucination: the worker read something related on a page, paraphrased it, and the paraphrase became a claim the source does not actually support if you grep-match the wording. The worker was not fabricating — it was summarizing imprecisely. AutoResearch-style iterative loops do not re-verify their own quotes against source text.

The fix is a dedicated **citation-checker subagent** — a final-pass verifier that runs after all workers complete, before synthesis:

```markdown
---
name: citation-checker
description: Verifies that every cited claim appears in its cited source.
tools: Read, WebFetch
---

For each claim-source pair in the worker findings:
1. Fetch the source URL
2. Search the page text for the cited claim or supporting paraphrase
3. Flag any claim where the source does not contain what the worker reported

Return: list of verified claims, list of flagged claims with reason.
Flagged claims are returned to the orchestrator to re-verify or downgrade to "unverified."
```

The citation-checker is not clever — fetch, search, flag. But citation drift is common enough in research loops that the extra pass earns its cost.

**Important scope**: the citation-checker verifies that a claim *exists* on a page — it does not assess whether the page is a credible source. Source credibility remains a human judgment.

### Cross-Session Research Memory (lessons.md)

Subagents are fire-and-forget. Without a cross-session memory mechanism, a research orchestrator rediscovers the same sources from scratch on every query. On recurring research domains, this is expensive and wasteful.

A lightweight fix: a flat `lessons.md` file the orchestrator reads on startup, containing prior queries, their decompositions, and notes on sources that kept appearing.

```markdown
## Past Queries and Decompositions
- [2026-04-01] "State of MCP server tooling" → split into: (1) current state + limits [merged], (2) serious players, (3) changes last 6 months
  - Sources that kept surfacing: [list]

## Recurring Sources by Domain
- MCP tooling: [source A], [source B]
```

This is not memory in the auto-memory sense — it is a research log the orchestrator uses to avoid cold-starts. Update it at the end of each query session. Keep it flat and human-readable; it is also useful for reviewing what the agent has been investigating.

**Distinction from CLAUDE.md**: CLAUDE.md encodes rules and constraints (what the orchestrator *must* do). lessons.md encodes accumulated research context (what the orchestrator *knows*). They serve different purposes and should not be merged.

## Intent-First Routing: Interview Before Planning

Source: oh-my-codex (OMX) project

A common failure in multi-agent systems: the planner starts building a spec before the scope is actually clear. The planner infers intent from an ambiguous prompt, the generator implements the inferred spec, and the evaluator grades against criteria that were never agreed — because the human's actual intent was never surfaced.

The OMX `$deep-interview` → `$ralplan` → `$team/$ralph` workflow enforces a different sequence:

1. **$deep-interview**: An interviewer agent clarifies scope with the human. The interview does not end until the intent is unambiguous — who is the user, what is the goal, where are the boundaries?
2. **$ralplan**: Only after the interview concludes does the planner transform the clarified scope into an approved architecture and plan. The plan is reviewed before any execution begins.
3. **$team / $ralph**: Execution phase — either parallel team work or the persistence loop.

**Why this matters for the three-agent architecture**: the planner in the generator-evaluator loop receives the prompt directly and must infer intent. Intent-first routing moves intent clarification upstream of the planner — the planner gets a resolved spec rather than an ambiguous prompt. This prevents the "over-specification cascades errors" failure at the source rather than managing it downstream.

**When to apply**: for any task where the requirements contain ambiguity that would cause the planner to make consequential assumptions. For clearly-scoped tasks, the interview phase adds overhead without value. Use judgment based on prompt specificity.

**31 auto-detection triggers**: OMX maps natural language patterns to workflow intents automatically — reducing the cognitive load of choosing which mode to invoke. The principle generalizes: classify the task type before starting, route to the appropriate mode, and start the work knowing what kind of work it is.

## Cross-Model Evaluation via the Codex Plugin

Source: OpenAI codex-plugin-cc (March 2026); Alireza Rezvani, production experience

OpenAI's official Claude Code plugin (`openai/codex-plugin-cc`) implements the adversarial evaluator as an installable plugin rather than a custom build. It provides two evaluation patterns:

**1. On-demand adversarial review**

```
/codex:adversarial-review --base main challenge whether this retry and caching design handles partial failures
/codex:adversarial-review --background look for race conditions and question the chosen approach
```

The `--background` flag runs the review in parallel while Claude continues working — important for multi-file reviews that can take several minutes. Retrieve results with `/codex:status` and `/codex:result`.

**2. The Stop hook review gate** — automatic evaluation on every Claude response

```
/codex:setup --enable-review-gate
```

Installs a Stop hook that intercepts every Claude Code response and runs a Codex review before Claude can finish. This is the generator-evaluator loop implemented natively: every sprint output is automatically evaluated before completion is signaled.

**Review gate cost risk**: the feedback loop can drain usage limits in 30 minutes of active development. One Claude → Codex reject → Claude fix → Codex reject cycle can consume a full day's Codex allocation (ChatGPT subscription) or $15–30 in combined API calls (API billing). Only enable during actively monitored sessions on high-stakes work. Disable with `/codex:setup --disable-review-gate`.

**Empirical blind spot mapping** (production observation, 7-engineer team):

| Model | Tends to catch |
|---|---|
| Claude | Architectural coherence — "this abstraction doesn't fit the pattern established elsewhere" |
| Codex | Correctness and edge cases — "this edge case will fail silently under load" |

This is consistent with the self-evaluation bias problem: Claude approves its own architectural choices because it made them. Codex, with different training and reasoning patterns, surfaces correctness failures Claude's optimism misses. Running both is coverage, not distrust.

**When adversarial review adds value** (heuristic):
- Authentication, authorization, and security paths
- Caching and retry logic (failure modes are where optimistic generation bites hardest)
- Database migrations and schema changes
- Any change where a production incident costs more than the review time

**When to skip it**: cosmetic changes, README updates, dependency bumps, small bug fixes with obvious blast radius.

**Cost control**: specify model and effort for parallel investigation tasks:
```
/codex:rescue --model gpt-5.4-mini --effort medium investigate the flaky integration test
```

Not every investigation needs full reasoning power. Triage tasks suit smaller models at medium effort.

## Mixed-Provider Teams

Source: oh-my-codex (OMX) project

The three-agent architecture assumes agents run on the same model. Teams can instead assign different model providers to different roles:

```bash
OMX_TEAM_WORKER_CLI_MAP=codex,claude,gemini
```

Workers from different providers run in parallel worktrees. The orchestrator coordinates them via the shared task state, regardless of which provider each worker uses.

**Harness implications**:
- **Model diversity as a hedge**: different providers have different failure modes and reasoning styles. A task that one provider gets wrong may succeed on another, without explicit retry logic.
- **Cost optimization**: route expensive reasoning roles (architect, evaluator) to capable models; assign simpler execution roles to cheaper/faster models — even if "simpler" means a different provider's smaller model.
- **Competing hypotheses with model diversity**: for debugging (see Anthropic's competing hypotheses pattern), assigning each hypothesis to a different provider removes the anchoring bias that comes from one model's strong prior about a problem.

**Practical constraint**: mixed-provider teams require each worker's CLI to be available and configured in the environment. This is infrastructure complexity; only add it when single-provider teams have hit a capability or cost ceiling.

## Dynamic Evaluator Value

The evaluator is most valuable when tasks are at the edge of baseline model capability. Tasks well within capability are unnecessary overhead — the evaluator adds cost and time without proportional quality improvement.

As models improve, the capability boundary shifts. Re-evaluate which sprints need external evaluation on each model update.

## Cost-Quality Reference (Anthropic)

Same one-sentence prompt, different harness configurations:

| Setup | Time | Cost | Output quality |
|---|---|---|---|
| Solo agent | 20 min | $9 | Broken core functionality |
| Full three-agent harness | 6 hrs | $200 | Functional with minor issues |
| Simplified harness (DAW) | 3.8 hrs | $124 | — |

Quality differences are "immediately apparent."

## Iteration Loop Behavior

Running 5–15 iterations with active evaluator feedback produces "creative leaps" not visible in single-pass generation. The feedback loop forces the generator to improve rather than rationalize.

## Pre-Built Implementations of This Pattern

Several frameworks implement the generator-evaluator loop without requiring you to build it from scratch:

**GSD** is the most complete open-source implementation. Its `gsd-plan-checker` validates plans across 10 dimensions before any code is written (pre-execution evaluator). Its `gsd-verifier` performs goal-backward verification after execution (post-execution evaluator). The two together approximate the sprint contract + evaluator loop — the plan-checker is the sprint contract validation; the verifier is the evaluator grading the output. GSD also separates the `gsd-planner` (generator) from the `gsd-verifier` (evaluator), addressing self-evaluation bias structurally.

**BMAD** implements this via persona separation — a PM persona defines the spec, a Developer implements it, an Architect reviews the design. Different personas evaluating different phases approximates the planner → generator → evaluator chain with human involvement at each handoff.

**SPARC**'s Refinement phase is a structured evaluator loop — iterative passes over the implementation before the Completion phase. The Pseudocode phase is a pre-implementation sprint contract: logic agreed in abstract before code is committed.

**Kiro**'s agent hooks fire automatically on file events, creating a continuous sensor layer that approximates the evaluator running in parallel with the generator rather than only at sprint boundaries.

See [spec-driven-workflows.md](spec-driven-workflows.md) for full framework detail.
