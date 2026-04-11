# Middleware Patterns and Validated Harness Techniques

Sources: LangChain "Improving Deep Agents with Harness Engineering" (2026), Microsoft Magentic-One research

## Table of Contents

- [What Middleware Is](#what-middleware-is)
- [Four Middleware Patterns (LangChain)](#four-middleware-patterns-langchain-terminal-bench-20) — Build-Verify Loop, Context Injection, Loop Detection, Reasoning Budgeting
- [Pre-Action Verification](#pre-action-verification-certainty-protocol-and-intentgate) — Certainty Protocol; IntentGate; model-specific variants
- [Microsoft Magentic-One: Task and Progress Ledgers](#microsoft-magentic-one-task-and-progress-ledgers)
- [Meta-Harness: Automated Harness Optimization](#meta-harness-automated-harness-optimization)
- [Framework Implementations of Middleware Patterns](#framework-implementations-of-middleware-patterns)
- [LangChain Observability Finding](#langchain-state-of-agent-engineering-observability-finding) — 89% of production users have observability; FCoT + OpenTelemetry
- [Tool Count Management](#tool-count-management) — 40→13 tools; virtual tools; embedding-guided routing; tool use coverage metric
- [Programmatic Tool Calling (PTC) and the Composition Tax](#programmatic-tool-calling-ptc-and-the-composition-tax)
- [Adaptive Retry and Prompt Mutation](#adaptive-retry-and-prompt-mutation)
- [Rate Limit Management](#rate-limit-management)
- [Hash-Anchored Edits (Hashline)](#hash-anchored-edits-hashline) — 6.7% → 68.3% success rate
- [Skill-Embedded MCPs](#skill-embedded-mcps)
- [Schema Enforcement at Tool Boundaries](#schema-enforcement-at-tool-boundaries) — agentjson repair pipeline
- [Advisor Tool: Dynamic Guidance Layer](#advisor-tool-dynamic-guidance-layer) — Anthropic API beta; Opus-as-advisor; cost-quality trade-offs; when to call

---

## What Middleware Is

Middleware sits between the model and tool execution — hooks that fire around model calls and tool calls to enforce behavior, inject context, and detect failure states. Unlike system prompt instructions (which the model can ignore), middleware is deterministic and always runs.

"The goal of a harness is to mold the inherently spiky intelligence of a model for tasks we care about."

## Four Middleware Patterns (LangChain, Terminal Bench 2.0)

LangChain improved agent performance from **52.8% → 66.5%** on Terminal Bench 2.0 without changing the underlying model by applying these four patterns.

### The Persistence Loop: When It Works and When It Doesn't

Source: Sigrid Jin, "ralph is a form of porn" (January 2026); claw-code project

The ralph loop — running an agent repeatedly until acceptance criteria pass — is powerful but has a specific precondition: **success must be mechanically verifiable**. When it is, the loop converges. When it isn't, the loop exploits its way to false completion.

> "Without a human in the loop to provide sanity checks, an AI might find 'hacky' ways to pass tests while producing code that is unmaintainable, insecure, or structurally flawed."
> — Sigrid Jin

The other failure mode: the loop has no mechanism to recognize when an architectural approach is a dead end. A human would abandon the approach; the loop continues indefinitely, wasting compute on a direction that will never converge.

**When to use the persistence loop:**
- Success criteria are deterministic and machine-verifiable (test suite, type checker, coverage gate)
- The task is scoped tightly enough that the agent can succeed without architectural pivots
- Human oversight is available at interrupt points (loop detection middleware fires, confidence drops)

**When not to use it:**
- Success criteria require aesthetic judgment ("does this look good?", "is this architecture correct?")
- The task scope is ambiguous — the loop will converge on the wrong thing
- There's no evaluator: the generator and the verifier are the same agent

The persistence loop is not a replacement for the generator-evaluator architecture; it's a component within it. `$ralph` mode in oh-my-codex uses architect-level verification — a separate evaluator runs after each iteration. Without external evaluation, the loop degrades into a self-approval machine.

See [generator-evaluator-loop.md](generator-evaluator-loop.md) for the external evaluator pattern. See below for the Build-Verify Loop middleware implementation.

### 1. Build-Verify Loop

**Problem**: Models naturally stop after drafting a solution without testing it. Code gets written; verification never happens.

**Pattern**: Implement explicit guidance for plan → build → verify → fix, backed by middleware that enforces verification checkpoints. The checkpoint fires after each tool call sequence and checks whether verification was actually performed before allowing the agent to mark work complete.

**Implementation notes**:
- Middleware intercepts completion signals and checks whether a test run occurred in the recent tool call history
- If no test run detected, inject a reminder before allowing the model to continue
- Combine with the session-handoff pattern: mark features as passing only after the build-verify loop completes
- **100% coverage as the verify gate** (OpenAI): the verification step isn't "does the agent think this is correct?" — it's "is every line covered by a passing test?" A CI gate enforcing 100% coverage makes the build-verify loop mechanical rather than relying on agent judgment. The coverage report becomes a todo list: uncovered lines are tests the agent still needs to write. See [guides-and-sensors.md](guides-and-sensors.md) → "100% Code Coverage as a Harness Constraint" for the full rationale.
- **Boulder mechanism (todoContinuationEnforcer)**: when an agent generates a TODO list as part of its planning, enforce that all items are marked complete before the session can end. The agent cannot declare done while TODOs remain open. This is the build-verify loop applied to task lists rather than test results — useful when the verification gate is a structured checklist rather than an automated test suite.

- **Test suite speed is a prerequisite**: the Build-Verify Loop only works if tests run fast enough to run constantly. At 20-30 minutes per test run, agents avoid running tests — the loop breaks down. OpenAI achieved 10,000+ assertions in ~1 minute via high concurrency, strong isolation, and a caching layer for third-party calls. See [dev-environment-design.md](dev-environment-design.md) → "Fast" for the optimization techniques.

### 2. Context Injection Middleware

**Problem**: Agents struggle in unfamiliar environments. They waste tool calls rediscovering directory structure, available commands, and project conventions — and make planning errors because they don't have this context at the right moment.

**Pattern**: Pre-completion context injection. Before each model call, middleware injects current state:
- Working directory and project structure summary
- Available tools and their current status
- Recent test results
- Known constraints and timeouts

**Implementation notes**:
- Inject at the start of each turn, not just in the system prompt (which fades in long sessions)
- Keep injections concise — this is dynamic context, not documentation
- This pattern directly addresses "instruction fade-out" in long sessions: initial instructions degrade, event-driven reminders at decision points maintain consistency

### 3. Loop Detection Middleware

**Problem**: Agents enter "doom loops" — repeating the same failed approach because they're committed to a strategy and don't recognize they're stuck. Symptoms: the same file being edited repeatedly, the same error appearing in consecutive tool results.

**Pattern**: Track file edits and error patterns. When the same file has been edited N times (typically 3) without a passing test, or the same error has appeared M consecutive times, inject a strategy reconsideration prompt before the next model call.

**Implementation notes**:
- Track at the middleware level, not in the prompt
- Trigger message example: "You've edited [file] 4 times without resolving the test failure. Consider an alternative approach: [list options]"
- Set thresholds conservatively — too sensitive causes unnecessary interruptions
- Reset counters when a new feature is started

### Pre-Action Verification: Certainty Protocol and IntentGate

Source: oh-my-openagent ultrawork mode (code-yeongyu, 2026)

Two complementary patterns that prevent the most common form of speculative execution — the agent writes code based on an assumption it hasn't verified.

**Mandatory Certainty Protocol** (Claude-targeted):
Before writing any code, the agent must explicitly confirm it is 100% certain about:
- What the current state of the file/system is
- What the change should accomplish
- That the change won't break adjacent behavior

If uncertain, the agent reads/investigates first. Code generation is blocked until certainty is explicit. This prevents the common failure where an agent writes code based on what it *thinks* is true rather than what it has verified.

**IntentGate Verbalization** (per-tool-call):
Before each tool execution, the agent writes an `<intent_verbalization>` block explaining what it understands the current state to be and what the tool call will accomplish. This anchors reasoning at the tool level — not just at task start — and provides an inspection point for harness validators.

```
<intent_verbalization>
Current state: the test suite is failing on auth.test.ts line 42 because 
the mock is returning null instead of the user object.
This Edit call: replaces the mock return value with a valid user fixture.
Expected outcome: auth.test.ts passes; no other tests affected.
</intent_verbalization>
[Edit call follows]
```

These two patterns address the same root cause from different angles: Certainty Protocol gates *session-level* code generation; IntentGate gates *per-call* execution. Applied together, they reduce speculative modifications — code written based on assumptions rather than verified state.

**Model-specific variants**: different models have different failure tendencies, and the harness should adapt accordingly:

| Model family | Failure tendency | Harness adaptation |
|---|---|---|
| Claude | — | Mandatory Certainty Protocol before code generation |
| Gemini | Premature coding (jumps to implementation before understanding) | INTENT_GATE: classify intent before any action (Step 0) |
| GPT | — | Decision Framework: self vs. delegate, two-track parallel context gathering |

The harness carries different system prompt sections per model family. This is the reasoning budgeting principle extended: not just effort levels, but model-specific behavioral guardrails calibrated to each model's observed failure modes.

### 4. Reasoning Budgeting ("Reasoning Sandwich")

**Problem**: Extended thinking on every step is expensive, slow, and often unnecessary. Uniform high reasoning burns tokens on routine implementation steps. Uniform low reasoning misses the planning and verification steps that actually benefit from deeper thinking.

**Pattern**: Apply high reasoning budget for planning and verification phases; moderate reasoning for implementation.

```
Planning phase    → High reasoning (understand scope, identify risks)
Implementation    → Moderate reasoning (routine execution)
Verification      → High reasoning (catch edge cases, assess completeness)
```

**Implementation notes**:
- Detect phase from recent context (what tools were called, what the model just said)
- Or make phase explicit in the harness state machine
- Balances cost against timeout constraints better than uniform reasoning settings
- Combine with the generator-evaluator loop: the evaluator always gets high reasoning; the generator uses moderate for sprint work

## Microsoft Magentic-One: Task and Progress Ledgers

Microsoft's Magentic-One system (part of AutoGen / Microsoft Agent Framework) independently validated the same handoff artifact pattern that Anthropic documented:

| Anthropic term | Magentic-One term | Purpose |
|---|---|---|
| `feature_list.json` | **Task ledger** | Blueprint of all steps/features; tracks what's pending |
| `claude-progress.txt` | **Progress ledger** | Monitors completion, adapted dynamically |

The Magentic-One orchestrator updates both ledgers in real time and uses them to adapt the workflow — re-planning when progress stalls or unexpected results emerge.

**Key difference from the Anthropic pattern**: Magentic-One's orchestrator is itself an LLM that reads the ledgers and dynamically selects which specialized agent acts next, rather than a single coding agent that reads the ledgers and self-directs. Both patterns are valid; the dynamic orchestrator adds flexibility at the cost of complexity.

**Magentic-One architecture:**
- Orchestrator (plans, tracks, re-plans)
- WebSurfer (browser)
- FileSurfer (local files)
- Coder (writes and executes code)
- ComputerTerminal (shell)

The task and progress ledger pattern is now validated by three independent labs (Anthropic, OpenAI via structured feature lists, Microsoft). It is load-bearing.

## Meta-Harness: Automated Harness Optimization

Source: "Meta-Harness: End-to-End Optimization of Model Harnesses" (Yoon Ho Lee et al.)

Treats harness engineering as a **search problem**: an LLM agent proposes harness improvements iteratively, guided by execution traces.

**Key insight**: Access to full execution traces (filesystem with source code, scores, and traces of every prior candidate — ~10M tokens) produces better harness improvements than compressed summaries (26K tokens max for competing methods). The agent reads logs with grep/cat to trace specific failures back to harness decisions, enabling targeted fixes grounded in concrete evidence rather than aggregate scores.

**Results:**
- Text classification: 40.9% → 48.6% accuracy (Label-Primed Query harness)
- Math reasoning: 34.1% → 38.8% on IMO-level problems
- Agentic coding: 76.4% pass rate on TerminalBench-2 with Claude Opus 4.6 (#2 ranking)

**Practical implication**: Harness engineering is not a one-time activity. It benefits from systematic iteration against execution traces. Logging every agent run with enough detail to trace failures is a prerequisite for this kind of improvement.

**Workflow this implies:**
1. Run agents; log execution traces to files (not just metrics)
2. Periodically run a "harness optimizer" agent that reads the traces
3. Agent proposes specific harness changes (system prompt edits, new middleware rules, constraint additions)
4. Evaluate proposed changes against benchmarks
5. Merge improvements into the harness

This is the automated version of the manual process of reading evaluator logs and updating prompts iteratively.

**Manual equivalent — the "promote rule into code" ratchet** (OpenAI):
Before automating harness optimization, teams do this manually:
1. A review comment surfaces a recurring pattern
2. The pattern is documented in `CLAUDE.md` or the architecture doc
3. If documentation proves insufficient (the pattern recurs anyway), the rule is promoted into a linter, structural test, or pre-commit hook

Each promotion reduces the future cost of enforcement to zero — the constraint applies everywhere at once with no human attention required. Review comments → documentation → tooling is the progression. The Meta-Harness automates step 3; the manual ratchet is how most teams get there before automation is justified.

## Framework Implementations of Middleware Patterns

Rather than building middleware from scratch, several frameworks implement these patterns natively:

**GSD** implements all four patterns at the workflow level:
- Build-Verify Loop → `gsd-verifier` runs goal-backward verification after every execute phase; DONE is never automatic
- Context Injection → each agent receives a bounded context with `STATE.md` + phase artifacts at spawn time
- Loop Detection → `gsd-plan-checker` catches dependency cycles and complexity imbalance before execution
- Reasoning Budgeting → configurable model profiles: Opus for planning/verification, Sonnet for execution, Haiku for budget verification

**Kiro**'s agent hooks are an IDE-native implementation of context injection middleware — hooks fire on file save, file creation, and file deletion, automatically injecting updated context before the next agent action. This is the "event-driven reminders" pattern applied continuously rather than at explicit checkpoints.

**Ralph Wiggum** implements the Build-Verify Loop at the process level: the bash wrapper checks for the `<promise>DONE</promise>` signal, which the agent can only emit after its acceptance criteria pass. No DONE without verified completion — the loop itself enforces the build-verify constraint.

**SPARC**'s Pseudocode phase prevents the "commit to implementation before verifying the plan" failure that the Build-Verify Loop addresses. By externalizing logic into pseudocode first, the Refinement phase has something concrete to evaluate before any production code is written.

See [spec-driven-workflows.md](spec-driven-workflows.md) for full framework detail.

## LangChain State of Agent Engineering: Observability Finding

From LangChain's survey of 1,300+ professionals (2026): **89% of production agent users have implemented observability**. Among production deployments, this rises to 94%.

"Without visibility into how an agent reasons and acts, teams can't reliably debug failures."

Full tracing adoption enables transparent reasoning inspection — which is the prerequisite for both loop detection middleware and Meta-Harness-style optimization.

**Practical minimum for observability:**
- Log every tool call with inputs and outputs
- Log model responses (not just final output)
- Track token usage per session and per feature
- Record pass/fail status for each feature attempt
- Store traces as files (path-addressable, compaction-stable)

This is not optional for production agent workflows. It's the foundation that makes all other harness improvement possible.

**Fractal Chain-of-Thought (FCoT) + OpenTelemetry mapping** (Agentic Architectural Patterns):
Rather than a single "thought" block, structure the agent to emit nested metadata for every sub-task — each tool call and reasoning step mapped to a standardized Trace Span. Plug these spans into an existing enterprise observability stack (Datadog, Honeycomb, etc.).

The result: every tool call has a Span ID. You can trace exactly which retrieved document caused a specific tool invocation. When an agent makes a costly error, you can reconstruct the exact reasoning chain that led to it.

Practical implementation:
- Wrap each tool call with a span: `tracer.startSpan('tool.call', { attributes: { tool: name, input: JSON.stringify(args) } })`
- Nest sub-task spans under their parent task span
- Record the model response (not just the final output) as a span event
- Tag spans with session ID, feature ID, and agent role — enables filtering by session or feature in the observability dashboard

## Tool Count Management

Source: GitHub Copilot engineering blog, Anisha Agarwal & Connor Peet (November 2025)

Too many tools don't just add latency — they degrade agent obedience. In benchmarks on SWE-Lancer and SWEbench-Verified (GPT-5 and Sonnet 4.5), the full 40-tool built-in set produced a **2–5 percentage point decrease in resolution rate** vs. a pruned 13-tool core. The behavioral signature of tool bloat: agents ignore explicit instructions, use tools incorrectly, and call tools that are unnecessary to the task. The cause is reasoning overhead — the model spends more of its reasoning budget navigating tool options than solving the problem.

Pruning 40 → 13 tools produced: **400ms reduction in time to final response**, **190ms reduction in time to first token**.

**The virtual tools pattern** — a middle ground between "give all tools" and "hard restrict":

Rather than exposing 40+ individual tools or hiding capabilities entirely, group semantically similar tools under one expandable "virtual tool" entry. The agent sees the cluster name, can expand it if needed, but doesn't have to reason across all tools simultaneously. Example groupings: Jupyter Notebook Tools, Web Interaction Tools, VS Code Workspace Tools, Testing Tools.

Implementation: use embedding similarity (cosine similarity on tool description embeddings) to form stable, reproducible clusters. Use a model call to summarize each cluster (cheap — one call per cluster, not one call across all tools). Cache embeddings and summaries locally.

**Embedding-guided tool routing** — pre-select relevant tools before the agent starts:

Before any tool group is expanded, compare the query embedding against vector representations of all tools. Surface the most semantically relevant candidates directly into the agent's initial context. Results: **94.5% tool use coverage** (how often the agent already has the right tool visible when it needs it) vs. 87.5% for LLM-based selection and 69% for the default static list.

This eliminates the "wrong group lookup" failure mode: the agent opens search tools, then documentation tools, then finally finds the right tool — each unnecessary lookup adding latency and failure risk.

**Tool use coverage** as a harness metric: measures how often the model already has the right tool visible when it needs it. Track this when evaluating harness tool configurations. A drop in coverage signals your tool set or routing logic needs adjustment.

**Practical guidance:**
- Audit tool usage statistics before pruning — remove tools with low usage first
- Identify a core set covering: file read/edit, codebase search, terminal, repository structure. This is the 13-tool pattern.
- Group remaining tools into virtual categories by semantic similarity
- Re-evaluate after model upgrades — newer models may navigate more tools effectively, changing the optimal set size

## Programmatic Tool Calling (PTC) and the Composition Tax

Source: Anthropic engineering blog (2026)

Standard tool use has a **composition tax**: each tool call round-trips to Claude's context window. The result is serialized into context (potentially thousands of rows when only a few are needed), requires a reasoning step, and adds latency. For a workflow making N sequential tool calls, the tax grows linearly.

**Programmatic Tool Calling (PTC)** addresses this: instead of calling tools individually, Claude writes code that orchestrates tool calls inside a container. Intermediate results return to the running code, not to Claude's context window. Only the final output reaches Claude. The code can filter, cross-reference, and process results programmatically — keeping only what's relevant before returning anything to the model.

The key harness property: **tool handlers remain in the middle**. Every tool call still crosses the sandbox boundary as a typed tool-use event. The harness can still inspect, reject, log, or queue for human approval. PTC gives Claude the composability of code without removing the harness's control surface.

Empirical results (Anthropic, BrowseComp + DeepsearchQA with Opus 4.6): **11% average accuracy improvement, 24% reduction in input tokens** vs. standard tool calling. PTC is now built into the `web_search_20260209` API tool by default.

**Harness implication**: for multi-step workflows with many sequential tool calls (search → filter → cross-reference → summarize), PTC reduces both token cost and context noise. The same tool handlers that provide guardrails in standard use still apply. This is also why the composition tax frames the tool count problem: every unnecessary tool the agent calls has a context cost, whether the call is useful or not.

## Adaptive Retry and Prompt Mutation

Source: "Agentic Architectural Patterns" book

**Problem**: When a primary LLM provider returns a reasoning failure (non-JSON response, malformed output, provider timeout or 503), naive retry repeats the same prompt against the same provider. Production systems cannot tolerate a single provider as a single point of failure.

**Pattern**: Detect reasoning failures and execute an adaptive mutation rather than a simple retry:
1. **Detect failure**: non-JSON response, schema validation failure on tool output, provider timeout
2. **Simplify**: strip non-essential tools from the context; reduce prompt complexity
3. **Re-route**: send the simplified request to a secondary, geographically distinct provider
4. **Degrade gracefully**: if secondary also fails, trigger a graceful halt with state preserved for resumption

**Implementation notes**:
- Define "reasoning failure" explicitly — not just HTTP errors, but semantic failures (response doesn't match expected schema)
- Schema-validate all tool outputs before feeding them back to the LLM (see Schema Enforcement below)
- Maintain a provider fallback chain: primary → secondary → tertiary, each with independent rate limits
- Log every fallback event with the failure reason — a high fallback rate indicates a prompt that needs hardening

## Rate Limit Management

Source: oh-my-claudecode (OMC, Yeachan Heo, 2026)

Production agent workflows hit rate limits. The naive response is to fail the session and require manual restart — losing context, state, and progress. A harness handles this as a recoverable state.

The pattern:
1. Detect rate limit response (HTTP 429 or provider-specific error)
2. Preserve current session state (write claim-safe state file, update progress log)
3. Wait for the reset window (OMC's `omc wait` auto-resumes when the limit clears)
4. Resume from preserved state — not from scratch

**The harness implication**: rate limits are a lifecycle event, not a failure. Design the harness to treat them like any other `session.blocked` event: write durable state, notify the human if needed, and auto-resume when the resource becomes available.

**For long-running overnight tasks specifically**: rate limits are the most common reason unattended sessions fail midway. Without explicit handling, the session dies, no handoff artifacts are written, and the next session starts blind. With explicit handling, the session pauses cleanly and continues.

This connects to the claim-safe lifecycle pattern: write task state before starting work so that any interruption — crash, rate limit, network failure — leaves a resumable checkpoint rather than a lost session.

## Hash-Anchored Edits (Hashline)

Source: oh-my-openagent project

**Problem**: When a file changes mid-session — another agent edits it, a process regenerates it, or a rebase lands — the model's internal representation of that file is stale. Subsequent edits reference line numbers or content that no longer exists. This causes silent failures or produces corrupted output. Standard tools (which reference by line number or substring match) fail when content shifts.

**Pattern**: Instead of referencing file content by position, anchor each edit to a content hash of the target line. The edit operation validates the hash before applying — if the content has changed, the hash doesn't match and the edit is rejected cleanly rather than silently applied to the wrong location.

```
EDIT target: file.ts
ANCHOR: sha256("  const result = await fetchUser(id)") → 7f3a...
REPLACE WITH: "  const result = await fetchUser(id, { timeout: 5000 })"
```

If the target line changed since the hash was computed, the middleware rejects the edit and surfaces a conflict notice rather than proceeding.

**Empirical results (oh-my-openagent)**: 6.7% → 68.3% task success rate on multi-agent workflows with concurrent file modification. The improvement is dramatic because the failure mode it prevents — silently applying an edit to the wrong context — produces compounding errors that invalidate downstream work.

**When to apply**: critical for any concurrent agent workflow where multiple agents may touch the same files. For single-agent sequential work, line-position edits are usually sufficient. The risk escalates with team size and file overlap.

## Skill-Embedded MCPs

Source: oh-my-openagent project

**Problem**: Loading all MCP servers globally (in the main session context) consumes context budget for every session, even when most servers are irrelevant to the current task. A database schema server loaded for a UI task wastes tokens and adds noise.

**Pattern**: Instead of global MCP server registration, skills bring their own scoped MCP servers that:
- Activate when the skill is invoked
- Provide only the context relevant to that skill's domain
- Shut down after the skill completes

```yaml
---
name: query-billing
description: Query billing database for revenue metrics
---
# MCP: billing-db-mcp (activates on invocation, shuts down on completion)

Run billing queries using the billing-db context provided...
```

The result: each skill invocation gets precisely the MCP context it needs, and no other skill's context leaks in. This is the progressive disclosure principle (see skill-creator guidance) applied to MCP servers — load only what's needed, when it's needed.

**Connection to reasoning budgeting**: skill-embedded MCPs are the context-management complement to per-skill model selection. Just as you route different tasks to different model tiers, you activate different context sources per task rather than loading everything globally.

## Schema Enforcement at Tool Boundaries

Source: "Agentic Architectural Patterns" book

**Problem**: Tool calls return unstructured or unexpected output. When fed back to the LLM as context, malformed tool output causes reasoning failures, hallucinations about data that doesn't exist, or silent logic errors.

**Pattern**: Validate tool output against a defined schema before it re-enters the LLM's context.

```python
# Middleware that validates tool output before returning to LLM
def tool_call_middleware(tool_name: str, result: Any) -> Any:
    schema = TOOL_OUTPUT_SCHEMAS[tool_name]
    try:
        validated = schema.parse(result)
        return validated
    except ValidationError as e:
        # Tool returned malformed output — trigger adaptive retry
        raise ToolOutputValidationError(
            tool=tool_name,
            error=str(e),
            raw_output=result
        )
```

**Repair before reject** — before failing on malformed tool output, attempt deterministic repair. LLMs routinely produce near-valid JSON: trailing commas, single quotes, Python boolean literals (`True`/`None`), markdown fences wrapping the output. A repair pass (strip fences → heuristic fixes → probabilistic beam search) resolves the majority of cases in microseconds. Only escalate to LLM fallback or reject when local repair confidence is low.

agentjson (sigridjineth/agentjson) benchmarks: strict JSON parsers 0/10 on a "LLM messy JSON" suite; repair pipeline 10/10 in ~19-23 microseconds per case. The repair traces show exactly what changed — visibility is preserved for debugging. This eliminates the most common class of schema enforcement failures without triggering retries.

**What to enforce**:
- Required fields present (no silent nulls)
- Type correctness (IDs are strings, amounts are numbers, not the reverse)
- Value constraints (status is one of the expected enum values)
- Reasonable size bounds (a tool result that's 500KB is probably wrong)

This is the output-side equivalent of typed API clients: just as you validate inputs at the boundary (typed SDKs, OpenAPI), validate tool outputs at the boundary before they become LLM context. See [type-system-design.md](type-system-design.md) for the full boundary validation strategy.

## Advisor Tool: Dynamic Guidance Layer

Sources: Anthropic API documentation (April 2026, beta); arXiv:2510.02453 "How to Train Your Advisor" (Asawa et al., Feb 2026)

**The conceptual shift:** All other middleware patterns in this file operate on static rules — hand-authored instructions injected at specific points. The Advisor Tool introduces a different layer: a stronger model generating dynamic, per-instance natural language guidance that steers a cheaper executor model. Instead of encoding what the agent should do in CLAUDE.md, you let Opus reason about the specific situation and tell the executor what to do next.

This was formalized in the arXiv paper: train a lightweight open-weight model via RL to generate per-instance advice injected in-context before the target model's generation. Anthropic's production implementation replaces the trained advisor with Opus directly — same architectural pattern, no training infrastructure required.

**How it works (Anthropic API beta):**

```python
tools = [{
    "type": "advisor_20260301",
    "name": "advisor",
    "model": "claude-opus-4-6",
    "max_uses": 3,                              # cap advisor calls per request
    "caching": {"type": "ephemeral", "ttl": "1h"}  # for multi-turn conversations
}]
```

Requires beta header: `anthropic-beta: advisor-tool-2026-03-01`

The executor model (Haiku or Sonnet) runs the task end-to-end and calls the advisor like any other tool — the executor decides when advice is needed. On each advisor call:
1. Executor emits a `server_tool_use` block with `name: "advisor"`
2. Anthropic runs a separate Opus inference pass server-side
3. Opus receives the full system prompt, tool definitions, conversation history, and all prior tool results
4. Opus generates 400–700 tokens of advice (1,400–1,800 with extended thinking)
5. Opus's thinking blocks are dropped; only the text advice returns as `advisor_tool_result`
6. Executor resumes with that advice in context

All of this happens within a single `/v1/messages` API call — no extra round trips from the client.

**Supported model pairs (executor → advisor):**

| Executor | Advisor | Primary use case |
|---|---|---|
| Claude Haiku 4.5 | Claude Opus 4.6 | Maximum cost reduction, longer tasks |
| Claude Sonnet 4.6 | Claude Opus 4.6 | Quality improvement, cost-neutral to positive |
| Claude Opus 4.6 | Claude Opus 4.6 | Extended thinking on decision points |

**Pricing:** Executor tokens billed at executor model rates; advisor tokens billed at Opus rates. Top-level `usage` reports executor tokens; advisor tokens appear in `usage.iterations[].type == "advisor_message"`. No separate access fee for the tool itself.

**Validated cost-quality results (Anthropic benchmarks):**
- **Haiku + Opus advisor**: 19.7% → 41.2% on BrowseComp — 85% cheaper than Sonnet alone for comparable quality
- **Sonnet + Opus advisor**: 2.7 point improvement on SWE-bench Multilingual, 11.9% cost reduction vs. Sonnet alone

**When the executor should call the advisor:**
- After initial exploratory reads, before substantive implementation begins
- At a decision fork where multiple approaches are viable and the choice has downstream consequences
- When the executor is stuck (same error repeated, approach not converging)
- Before declaring the task complete — one advisor call to verify nothing was missed

2–3 advisor calls per task is the validated sweet spot. The executor should not call the advisor on every turn; the value is in strategic decision points, not continuous supervision.

**When not to use it:**
- Single-turn Q&A where no multi-step reasoning is required
- Tasks where every step needs top-tier reasoning (just use Opus directly)
- Cost-sensitive bulk processing where the overhead isn't justified by quality requirements

**The untrained advisor finding (from the arXiv paper):** Adding a naive, untrained advisor to a pipeline actively hurts performance — RuleArena accuracy dropped from 64.8% → 52.0% when an untrained advisor was introduced. The same principle applies to the production tool: calling the advisor at the wrong moments (too frequently, or on trivial decisions) will degrade output. The executor must be prompted to use the advisor judiciously, not by default.

**Connection to the harness skill:** The Advisor Tool is a dynamic alternative to context injection middleware. Where context injection injects static pre-authored information, the advisor generates situation-specific guidance. For tasks with high variability in what "the right next step" looks like, the advisor will outperform static injection. For tasks with consistent, predictable decision points, static CLAUDE.md rules remain more efficient.

**Docs:** `platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool`
