---
name: zhipuai-glm-capabilities
description: GLM API capabilities beyond basic chat — Structured Output (JSON mode), Context Caching, Thinking Mode (5 modes), and Streaming. Use when implementing pipelines, optimizing costs, controlling reasoning depth, or building tool-calling agents on Z.ai.
type: reference
---

# Z.ai GLM — API Capabilities

## Structured Output (JSON Mode)

Force deterministic JSON output by setting `response_format`:

```python
from zai import ZaiClient
import json

client = ZaiClient(api_key="your-api-key")
response = client.chat.completions.create(
    model="GLM-4.7",
    messages=[
        {"role": "system", "content": 'Return: {"sentiment": "positive|negative|neutral", "confidence": 0.0-1.0}'},
        {"role": "user",   "content": "Analyze: 'This code is a mess but it works.'"}
    ],
    response_format={"type": "json_object"}
)
result = json.loads(response.choices[0].message.content)
```

**Supported models:** GLM-5, GLM-4.7, GLM-4.6, GLM-4.5

**Best practices:**
- Define the exact schema in the system message with field names and types
- Keep schemas simple initially — add complexity once baseline works
- Validate output against a schema (pydantic, jsonschema) — model may deviate on complex structures
- Prepare a simplified fallback schema for error handling
- JSON mode can reduce response naturalness in edge cases; don't use it for conversational turns

---

## Context Caching

Caching is **automatic** — no configuration required. The API detects repeated content (system prompts, shared documents, conversation history) across requests and bills cached tokens at ~50% of standard price.

**How to maximize cache hits:**
- Keep system prompts identical across requests (even minor formatting changes break the cache)
- Load large reference documents (codebases, API specs) in the system message once, then reuse
- For multi-turn conversations, preserve the full message array rather than summarizing
- In batch processing, share a common prefix across all items in the batch

**Pricing:**
- Cached input tokens: ~50% of standard rate
- New input tokens: standard rate
- Output tokens: standard rate always

**Example savings:** 1,000-token system prompt reused across 100 requests = 99,000 cached tokens at half price.

**Gotcha:** Cache TTL is not documented exactly. Build retries that treat cache misses gracefully rather than assuming persistent caching.

**Supported models:** GLM-5, GLM-4.7, GLM-4.6, GLM-4.5 series

---

## Thinking Modes

Five distinct thinking configurations. Pass via `thinking` or `extra_body={"thinking": ...}` depending on SDK.

| Mode | Parameter | Use Case |
|------|-----------|---------|
| **Enabled (default)** | `{"type": "enabled"}` | General reasoning for most tasks |
| **Disabled** | `{"type": "disabled"}` | Simple/fast queries — cuts latency and tokens |
| **Interleaved** | `{"type": "enabled", "clear_thinking": true}` | Tool-calling agents that need reasoning between each tool call |
| **Preserved** | `{"type": "enabled", "clear_thinking": false}` | Default on Coding Plan endpoint; retains reasoning across turns for better cache + coherence |
| **Turn-level** | Toggle per request (GLM-4.7+) | Mixed sessions with both simple and complex turns |

### Critical rule for Preserved / Interleaved thinking

When using preserved thinking in a multi-turn loop, **you must return the unmodified `reasoning_content` back to the API** in subsequent messages:

```python
response = client.chat.completions.create(
    model="GLM-4.7",
    messages=messages,
    tools=tools,
    extra_body={"thinking": {"type": "enabled", "clear_thinking": False}}
)

msg = response.choices[0].message
# Append with reasoning_content preserved — do NOT strip it
messages.append({
    "role": "assistant",
    "content": msg.content,
    "reasoning_content": msg.reasoning_content,  # return unmodified
    "tool_calls": msg.tool_calls
})
```

Stripping `reasoning_content` breaks the preserved thinking chain and degrades multi-step coherence. It also loses the cache hit on the reasoning tokens.

**Interleaved thinking** is specifically designed for tool-call scenarios — the model thinks between invocations and after receiving tool results. This produces more accurate tool argument generation on complex calls.

---

## Streaming

### Text streaming
```python
stream = client.chat.completions.create(
    model="GLM-4.7",
    messages=[{"role": "user", "content": "Implement a rate limiter in Python."}],
    stream=True,
    temperature=1.0
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Tool call streaming
Add `tool_stream=True` to stream tool argument JSON as it's generated rather than buffering:

```python
response = client.chat.completions.create(
    model="GLM-4.7",
    messages=messages,
    tools=tools,
    stream=True,
    tool_stream=True  # stream tool call parameters incrementally
)
for chunk in response:
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="", flush=True)
    if delta.tool_calls:
        for tc in delta.tool_calls:
            # accumulate streamed JSON args by index
            pass
```

`tool_stream=True` reduces perceived latency for tool-heavy agents. Supported on `GLM-4.6`, `GLM-4.7`, `GLM-5`.

### Streaming reasoning content
When thinking is enabled, reasoning tokens appear in `delta.reasoning_content`:

```python
for chunk in response:
    delta = chunk.choices[0].delta
    if hasattr(delta, "reasoning_content") and delta.reasoning_content:
        print(delta.reasoning_content, end="", flush=True)  # thinking
    if delta.content:
        print(delta.content, end="", flush=True)            # answer
```

### curl streaming
```bash
curl -sN https://api.z.ai/v1/chat/completions \
  -H "Authorization: Bearer $ZAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"GLM-4.7","messages":[{"role":"user","content":"..."}],"stream":true}'
# -N disables buffering; parse lines starting with "data:"; stop at "data: [DONE]"
```
