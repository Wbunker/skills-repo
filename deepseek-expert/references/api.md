# DeepSeek API Reference

## Table of Contents
- [Endpoints](#endpoints)
- [Authentication](#authentication)
- [Chat Completions](#chat-completions)
- [Streaming](#streaming)
- [Context Caching](#context-caching)
- [Key Parameters](#key-parameters)
- [Error Codes](#error-codes)
- [Pricing](#pricing)
- [Check Balance & Key Info](#check-balance--key-info)

---

## Endpoints

| Format | Base URL |
|--------|----------|
| OpenAI-compatible | `https://api.deepseek.com` |
| Anthropic-compatible | `https://api.deepseek.com/anthropic` |
| Strict mode (beta) | `https://api.deepseek.com/beta` |

**Primary endpoint:** `POST https://api.deepseek.com/chat/completions`

The API is a drop-in replacement for OpenAI's chat completions API. Any library that supports a custom `base_url` (openai Python/JS SDK, LiteLLM, etc.) works without code changes beyond setting the base URL and API key.

---

## Authentication

```http
Authorization: Bearer sk-YOUR_DEEPSEEK_KEY
Content-Type: application/json
```

Get your key at: https://platform.deepseek.com/api_keys

---

## Chat Completions

**Minimal request:**
```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-...",
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is 2+2?"}
    ]
)
print(response.choices[0].message.content)
```

**Raw HTTP:**
```bash
curl https://api.deepseek.com/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

**Response structure:**
```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "model": "deepseek-v4-flash",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Hello! How can I help you?"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 8,
    "total_tokens": 18,
    "prompt_cache_hit_tokens": 0,
    "prompt_cache_miss_tokens": 10
  }
}
```

Note the `prompt_cache_hit_tokens` and `prompt_cache_miss_tokens` in usage — these determine which pricing tier applies.

---

## Streaming

```python
stream = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[{"role": "user", "content": "Count to 10"}],
    stream=True
)

for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="", flush=True)
```

When thinking mode is enabled and streaming, `reasoning_content` chunks arrive first, then `content` chunks. They arrive in separate delta fields — do not concatenate them.

---

## Context Caching

DeepSeek automatically caches prompt prefixes. No configuration needed — it happens transparently.

**How it works:**
- Repeated prefixes (system prompts, long contexts, few-shot examples) are cached on disk
- Cache hits are billed at ~4× cheaper rate than cache misses
- The `usage` field shows `prompt_cache_hit_tokens` vs `prompt_cache_miss_tokens`

**Optimize for caching:**
- Put static content (system prompt, reference material) at the **beginning** of the context
- Put dynamic/variable content (user message) at the **end**
- Longer shared prefixes = more cache hits = lower cost

---

## Key Parameters

| Parameter | Type | Notes |
|-----------|------|-------|
| `model` | string | Required. `deepseek-v4-flash` or `deepseek-v4-pro` |
| `messages` | array | Required. `[{role, content}]` |
| `max_tokens` | integer | Max output tokens (default varies; cap is 8K) |
| `temperature` | float | 0.0–2.0. **Ignored in thinking mode** |
| `top_p` | float | Nucleus sampling. **Ignored in thinking mode** |
| `stream` | boolean | Enable SSE streaming |
| `tools` | array | Function/tool definitions — see tool-use.md |
| `tool_choice` | string/object | `"auto"`, `"none"`, `"required"`, or specific function |
| `response_format` | object | `{"type": "json_object"}` for JSON mode |
| `thinking` | object | `{"type": "enabled"}` to enable reasoning — see thinking-mode.md |

---

## Error Codes

| HTTP | Meaning | Fix |
|------|---------|-----|
| 400 | Bad request / invalid params | Check JSON structure, model name |
| 401 | Invalid API key | Verify key at platform.deepseek.com |
| 402 | Insufficient balance | Top up at platform.deepseek.com |
| 422 | Invalid parameter values | Check parameter types and ranges |
| 429 | Rate limit exceeded | Back off and retry |
| 500 | Server error | Retry with exponential backoff |
| 503 | Server overloaded | Common during peak hours — retry |

---

## Pricing

Pricing as of May 2026 (USD per 1M tokens). DeepSeek uses **context caching** — cache-hit tokens are cheaper.

| Model | Context | Max Output | Input (cache miss) | Input (cache hit) | Output |
|-------|---------|------------|-------------------|------------------|--------|
| deepseek-v4-flash | 1M | 8K | ~$0.27 | ~$0.07 | ~$1.10 |
| deepseek-v4-pro | 1M | 8K | ~$0.55* | ~$0.14* | ~$2.19* |
| deepseek-chat (legacy) | 64K | 8K | $0.27 | $0.07 | $1.10 |
| deepseek-reasoner (legacy) | 64K | 8K (+ 32K CoT) | $0.55 | $0.14 | $2.19 |

*V4-Pro at 75% launch discount until 2026-05-31. Check https://api-docs.deepseek.com/quick_start/pricing for current rates.

**Cost comparison context:** DeepSeek is roughly 10–20× cheaper than Claude Sonnet for equivalent tasks.

---

## Check Balance & Key Info

```bash
curl https://api.deepseek.com/user/balance \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY"
```

Response includes `balance_infos` with currency, total balance, and topped-up balance.
