# DeepSeek Thinking Mode

Chain-of-thought reasoning that surfaces the model's internal reasoning process before giving a final answer. Best for math, logic, science, and complex multi-step problems.

## Table of Contents
- [Enabling Thinking Mode](#enabling-thinking-mode)
- [Effort Levels](#effort-levels)
- [Response Structure](#response-structure)
- [Streaming with Thinking](#streaming-with-thinking)
- [Multi-turn Rules](#multi-turn-rules)
- [When to Use Thinking Mode](#when-to-use-thinking-mode)
- [Gotchas](#gotchas)

---

## Enabling Thinking Mode

**OpenAI SDK (extra_body):**
```python
from openai import OpenAI

client = OpenAI(api_key="sk-...", base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[{"role": "user", "content": "Prove that √2 is irrational."}],
    extra_body={"thinking": {"type": "enabled"}}
)

reasoning = response.choices[0].message.reasoning_content
answer = response.choices[0].message.content

print("REASONING:\n", reasoning)
print("\nANSWER:\n", answer)
```

**Anthropic SDK:**
```python
import anthropic

client = anthropic.Anthropic(
    api_key="sk-...",
    base_url="https://api.deepseek.com/anthropic"
)

response = client.messages.create(
    model="deepseek-v4-pro",
    max_tokens=4096,
    thinking={"type": "enabled", "budget_tokens": 8000},
    messages=[{"role": "user", "content": "Solve this step by step..."}]
)
```

**Disable thinking (explicit):**
```python
extra_body={"thinking": {"type": "disabled"}}
```

---

## Effort Levels

Control how much computation the model spends on reasoning:

| Level | `output_config.effort` | Use case |
|-------|----------------------|----------|
| `high` | `"high"` | Default — standard complex reasoning |
| `max` | `"max"` | Hardest problems; used automatically by Claude Code / OpenCode |

Note: Values `"low"` and `"medium"` map to `"high"`; `"xhigh"` maps to `"max"` (backward-compat aliases).

Setting effort via `extra_body` (OpenAI format):
```python
extra_body={
    "thinking": {"type": "enabled"},
    "output_config": {"effort": "max"}
}
```

---

## Response Structure

When thinking is enabled, the assistant message has two fields:

```python
message = response.choices[0].message

message.reasoning_content   # str — the chain-of-thought (can be very long)
message.content             # str — the final answer shown to users
```

**Example response JSON:**
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "reasoning_content": "Let me think step by step...\n\nFirst, assume √2 = p/q...",
      "content": "√2 is irrational. Proof by contradiction: assume √2 = p/q in lowest terms..."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 450,
    "completion_tokens_details": {
      "reasoning_tokens": 380
    }
  }
}
```

`reasoning_tokens` in usage shows how many tokens were used for the chain-of-thought — these are billed at output token price.

---

## Streaming with Thinking

During streaming, `reasoning_content` and `content` arrive in separate delta fields. They stream sequentially — reasoning first, then the final answer.

```python
stream = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[{"role": "user", "content": "What is 17 × 23?"}],
    stream=True,
    extra_body={"thinking": {"type": "enabled"}}
)

reasoning_buffer = ""
content_buffer = ""

for chunk in stream:
    delta = chunk.choices[0].delta
    if hasattr(delta, "reasoning_content") and delta.reasoning_content:
        reasoning_buffer += delta.reasoning_content
    if delta.content:
        content_buffer += delta.content
```

---

## Multi-turn Rules

The handling of `reasoning_content` in multi-turn conversations depends on whether tool calls are involved:

**Without tool calls — omit reasoning_content:**
```python
# After getting a response with reasoning, the next turn just uses content:
messages = [
    {"role": "user", "content": "What is the capital of France?"},
    {"role": "assistant", "content": response.choices[0].message.content},
    # Do NOT include reasoning_content here
    {"role": "user", "content": "And what language do they speak?"}
]
```

**With tool calls — reasoning_content MUST be included:**
```python
# When the response includes tool_calls, pass reasoning_content back
assistant_msg = {
    "role": "assistant",
    "content": response.choices[0].message.content,
    "reasoning_content": response.choices[0].message.reasoning_content,  # required
    "tool_calls": response.choices[0].message.tool_calls
}
messages.append(assistant_msg)
messages.append({"role": "tool", "tool_call_id": "...", "content": tool_result})
```

---

## When to Use Thinking Mode

**Enable for:**
- Mathematical proofs, competition math (AIME/AMC level)
- Complex algorithm design
- Multi-step logical reasoning
- Scientific analysis with multiple constraints
- Debugging hard problems where reasoning trace is valuable

**Disable for:**
- Simple Q&A, summarization, translation
- Creative writing
- High-volume / latency-sensitive applications (thinking adds significant tokens/cost)
- Tasks where `temperature`/`top_p` control matters (they're ignored in thinking mode)

---

## Gotchas

- `temperature`, `top_p`, `presence_penalty`, `frequency_penalty` are **silently ignored** in thinking mode — no error, no effect.
- `reasoning_content` is only present in thinking mode. Accessing it in non-thinking mode returns `None`.
- Reasoning tokens are billed at **output token price**, which can make thinking mode 2–5× more expensive per call.
- Supported models: **deepseek-v4-pro** and **deepseek-v4-flash** (and legacy `deepseek-reasoner`). Does not work on R1-Distill variants via API.
- Thinking mode defaults to **enabled** on `deepseek-v4-pro`. Explicitly disable it if you want non-thinking behavior.
- When streaming, do not assume `reasoning_content` completes before `content` begins — process both deltas independently.
