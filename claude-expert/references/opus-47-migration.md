# Claude Opus 4.7 — Migration Guide

> Official docs: [Migration guide](https://platform.claude.com/docs/en/docs/about-claude/models/migrating-to-claude-4) · [What's new](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7) · [Prompting best practices](https://platform.claude.com/docs/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices)

## Contents

1. [The One Line That Undoes the Panic](#the-one-line-that-undoes-the-panic)
2. [Breaking API Changes](#breaking-api-changes-messages-api-only)
3. [New Features](#new-features)
4. [Behavioral Changes and the Two Prompt Patterns That Break](#behavioral-changes-non-breaking-may-need-prompt-updates)
5. [Prompting Strategy for 4.7](#prompting-strategy-for-47)
6. [Gotchas](#gotchas)

---

## The One Line That Undoes the Panic

> "Claude Opus 4.7 should have strong out-of-the-box performance on existing Claude Opus 4.6 prompts and evals."

The default assumption is: **your old prompts work**. There are two narrowly-scoped prompt patterns that need fixing. Everything else is noise.

---

## Breaking API Changes (Messages API only)

Claude Managed Agents users: no API changes required — just update the model name.

### 1. Extended Thinking Budgets Removed

```python
# BEFORE (Opus 4.6) — returns 400 on 4.7
thinking = {"type": "enabled", "budget_tokens": 32000}

# AFTER (Opus 4.7)
thinking = {"type": "adaptive"}
output_config = {"effort": "high"}
```

- `thinking: {type: "enabled", budget_tokens: N}` → **400 error** on Opus 4.7
- Only supported mode: `thinking: {type: "adaptive"}`
- Adaptive thinking is **off by default** — must explicitly set `thinking: {type: "adaptive"}` to enable
- Adaptive thinking outperforms extended thinking in Anthropic's internal evals

### 2. Sampling Parameters Removed

- Setting `temperature`, `top_p`, or `top_k` to any non-default value → **400 error**
- Migration: **omit these parameters entirely**
- Use prompting to guide behavior instead
- Note: `temperature=0` never guaranteed identical outputs anyway

### 3. Prefill Assistant Messages Removed

- Prefilling the last assistant turn → **400 error**
- Migration patterns:

| Old prefill use case | New approach |
|---|---|
| Control output formatting | Structured outputs or `output_config.format` |
| Eliminate preambles | System prompt: "Do not add preambles" |
| Avoid bad refusals | Clear prompting in user message |
| Continuation | Move continuation to user message with context |
| Context hydration | Inject reminders into user turn |

### 4. Thinking Content Omitted by Default (Silent)

- Thinking blocks appear in stream but `thinking` field is **empty** by default — no error raised
- If streaming reasoning to users: appears as a long pause before output
- To restore: `thinking = {"type": "adaptive", "display": "summarized"}`
- Default is `"display": "omitted"`

### 5. New Tokenizer — ~35% More Tokens

- New tokenizer on Opus 4.7; `/v1/messages/count_tokens` returns different numbers than 4.6
- Text: 1x–1.35x as many tokens vs 4.6 (varies by content)
- Images: full-resolution now up to 4,784 tokens vs ~1,600 cap previously (up to 3x increase)
- Action items: update `max_tokens` with additional headroom; audit compaction triggers; re-evaluate client-side token-count estimations

### 6. New Stop Reason

- `model_context_window_exceeded` — returned when generation stops due to hitting context window limit (distinct from hitting requested `max_tokens`)

---

## New Features

### xhigh Effort Level

New effort level added to the existing scale:

| Level | Best for |
|---|---|
| `max` | Intelligence-demanding tasks; may overthink |
| `xhigh` **(NEW)** | **Coding and agentic use cases — recommended start** |
| `high` | Balanced; recommended minimum for intelligence-sensitive tasks |
| `medium` | Cost-sensitive workloads |
| `low` | Short scoped tasks, latency-sensitive, non-intelligence-sensitive |

Effort is strictly obeyed at `low`/`medium` — model scopes work to exactly what was asked. Raise effort rather than prompting around shallow reasoning.

### Task Budgets (Beta)

Advisory token budget across a full agentic loop (thinking + tool calls + results + output). Model sees a running countdown and self-moderates.

```python
response = client.beta.messages.create(
    model="claude-opus-4-7",
    max_tokens=128000,
    output_config={
        "effort": "high",
        "task_budget": {"type": "tokens", "total": 128000},
    },
    betas=["task-budgets-2026-03-13"],
    messages=[{"role": "user", "content": "..."}],
)
```

- Minimum: 20k tokens
- Not a hard cap — use `max_tokens` for the hard per-request ceiling
- Reserve for workloads needing scoped token allowance; skip for open-ended quality-focused tasks

### High-Resolution Image Support

- Max resolution: 2,576px / 3.75MP (was 1,568px / 1.15MP)
- Coordinates now 1:1 with actual pixels — no scale-factor math needed
- Full-res images use up to 3x more tokens; downsample if fidelity is unnecessary
- Improvements: low-level perception, bounding-box localization, dense screenshot reading

### Capability Improvements

- **.docx redlining / .pptx editing**: improved self-checking; remove "double-check the slide layout" scaffolding
- **Charts and figure analysis**: improved programmatic tool-calling with image-processing libraries
- **File-based memory**: improved scratchpad note-taking and retrieval across turns

---

## Behavioral Changes (Non-Breaking, May Need Prompt Updates)

### The Two Prompt Patterns That Actually Break

#### Pattern 1: Implicit Tool Calls

Opus 4.7 reads instructions literally. `"check"` = "think about it", not "invoke a tool".

```
# BREAKS on 4.7 — "check" is treated as "think about", not "call Glob"
Before suggesting changes, check the current project structure.

# FIXED
Before any code suggestion, you MUST call Glob to list the current project structure.
Do not rely on prior session context for file structure.
```

Fix formula:
- Replace soft verbs (`check`, `consider`, `look at`, `review`) with `MUST` + named tool
- Add explicit negation of the fallback: "Do not rely on prior context"
- Only apply this to **load-bearing** tool calls where the next step depends on fresh output

#### Pattern 2: Implicit Scope and Exceptions

Rules with implicit exceptions no longer have those exceptions inferred.

```
# BREAKS on 4.7 — quoted reviews lose their exclamation marks
Never use exclamation marks.

# FIXED
Never use exclamation marks anywhere in the generated prose.
This rule does not apply inside quoted customer reviews pulled verbatim from external sources.
```

```
# BREAKS on 4.7 — policy never reconfirmed even for new orders
Confirm the shipping policy once per conversation.

# FIXED
Confirm the shipping policy once per conversation under normal flow.
Reconfirm whenever: (a) a new order is introduced, (b) the destination changes,
(c) the customer explicitly asks about shipping terms again.
```

**The counter-intuitive takeaway:** Don't soften NEVER rules — they got *sharper* on 4.7. Fix your "once", "always", "usually" rules by writing out their scope and exceptions explicitly.

### Full Behavioral Change List

| Behavior | 4.6 | 4.7 |
|---|---|---|
| Instruction following | Infers intent, fills gaps silently | Literal; no silent inference |
| Response length | Fixed verbosity | Calibrates to task complexity |
| Tool calls | More frequent | Fewer; uses reasoning more (generally better results) |
| Tone | Warmer, more emoji | Direct, opinionated |
| Agentic progress updates | Required scaffolding to force | Built-in; remove forcing scaffolding |
| Subagent spawning | More frequent | Fewer by default; steerable via prompting |
| .docx/.pptx editing | Good | Improved; remove self-check scaffolding |
| Memory (file-based) | Good | Improved scratchpad usage |

---

## Prompting Strategy for 4.7

### Audit Checklist (Two Questions)

1. **Where does my prompt depend on a tool call I didn't explicitly demand?**
   → Find those. Make the call mandatory. Name the tool. Close the fallback.

2. **Where does my prompt depend on the model guessing scope or exceptions?**
   → Find those. Write the scope. List the exceptions.

That's the full rewrite surface. Not seventeen checkpoints.

### Useful XML Blocks

```xml
<!-- Force implementation over suggestion -->
<default_to_action>
Implement changes directly rather than suggesting them.
</default_to_action>

<!-- Require investigation before acting -->
<investigate_before_answering>
Read the relevant files before proposing changes.
</investigate_before_answering>

<!-- Maximize parallel tool execution -->
<use_parallel_tool_calls>
Run multiple tool calls in parallel when operations are independent.
</use_parallel_tool_calls>
```

### System Prompt Responsiveness

4.5/4.6+ models are more responsive to system prompts. If you wrote aggressive triggering language to prevent under-use, you may now get over-triggering:

```
# May overtrigger on 4.7
CRITICAL: You MUST use this tool when the user asks about X.

# Better
Use this tool when the user asks about X.
```

### Long Context Prompting

- Place long documents at the top of your prompt, above query/instructions/examples
- Query at the end can improve response quality up to 30% on complex multi-document inputs
- Structure documents with XML: `<documents>`, `<document>`, `<document_content>`, `<source>`

### What Stays the Same

- Hard bans (no em dashes, no tables, banned openers) run *tighter* on 4.7 — no changes needed
- Long system prompts hold across context
- Markdown rendering identical
- Tool definitions, personas, output format specs, content rules
- Prompt caching, batch API, Files API, streaming — all identical

---

## Gotchas

- `temperature`, `top_p`, `top_k` silently worked on 4.6; on 4.7 they **error with 400**. Remove them proactively even on models where they still work to future-proof.
- Thinking content omission is **silent** — no error, no warning. If your product surfaces reasoning to users, test before upgrading.
- The tokenizer change hits **image tokens hardest** (up to 3x more). Vision-heavy workloads need `max_tokens` headroom updated before flipping the model name.
- Task budgets are advisory, not hard. A too-small budget causes graceful under-completion or refusal — not a clean hard stop.
- Adaptive thinking is **off by default** on 4.7 — omitting the `thinking` field means no thinking at all, not adaptive thinking.
- Fewer tool calls at `low`/`medium` effort is intentional, not a regression. Raise effort to `high`/`xhigh` to increase tool usage; don't prompt around it.
