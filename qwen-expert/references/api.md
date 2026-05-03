# Qwen API Reference

## Table of Contents
- [Access Points](#access-points)
- [OpenAI-Compatible API](#openai-compatible-api)
- [DashScope (Alibaba Cloud)](#dashscope-alibaba-cloud)
- [OpenRouter](#openrouter)
- [Key Parameters](#key-parameters)
- [Streaming](#streaming)
- [Authentication](#authentication)
- [Gotchas](#gotchas)

---

## Access Points

### DashScope (Official)

| Region | Base URL |
|---|---|
| Singapore (International) | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| US (Virginia) | `https://dashscope-us.aliyuncs.com/compatible-mode/v1` |
| China (Beijing) | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| Hong Kong | `https://cn-hongkong.dashscope.aliyuncs.com/compatible-mode/v1` |

### Third-Party

| Provider | Base URL | Notes |
|---|---|---|
| OpenRouter | `https://openrouter.ai/api/v1` | No waitlist; free tier available |
| ofox.ai | `https://api.ofox.ai/v1` | All major Qwen3 variants |
| DeepInfra | standard OpenAI compat | Various Qwen models |
| HuggingFace Inference | `https://api-inference.huggingface.co/v1` | HF token required |

All use the **OpenAI Chat Completions format** — same SDK, same request shape, only `base_url` and `api_key` change.

---

## OpenAI-Compatible API

### Quick Setup (OpenRouter — recommended for getting started)

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-openrouter-key",
    base_url="https://openrouter.ai/api/v1"
)

response = client.chat.completions.create(
    model="qwen/qwen3.6-plus",
    messages=[
        {"role": "system", "content": "You are an expert software engineer."},
        {"role": "user", "content": "Refactor this function to be more memory-efficient: ..."}
    ],
    temperature=0.2
)
print(response.choices[0].message.content)
```

### TypeScript / Node

```typescript
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.OPENROUTER_API_KEY,
  baseURL: "https://openrouter.ai/api/v1",
});

const response = await client.chat.completions.create({
  model: "qwen/qwen3.6-plus",
  messages: [{ role: "user", content: "..." }],
});
```

### Raw HTTP

```bash
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen/qwen3.6-plus",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

---

## DashScope (Alibaba Cloud)

Official provider. Requires Alibaba Cloud account + DashScope API key.

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DASHSCOPE_API_KEY"],
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

response = client.chat.completions.create(
    model="qwen3.6-plus",   # no "qwen/" prefix on DashScope
    messages=[{"role": "user", "content": "..."}]
)
```

**DashScope model strings** (no `qwen/` prefix):
- `qwen3.6-plus`
- `qwen2.5-72b-instruct`
- `qwen2.5-coder-32b-instruct`
- `qwen2.5-vl-72b-instruct`
- `qwq-32b`

Also supports the native DashScope SDK: `pip install dashscope` — but OpenAI-compatible endpoint is simpler for new projects.

---

## OpenRouter

Third-party routing. No waitlist. Recommended for:
- Getting started fast
- Accessing the free tier (`qwen/qwen3.6-plus-preview:free` when available)
- Comparing models across providers without changing code

**Model strings on OpenRouter:**
- `qwen/qwen3.6-plus`
- `qwen/qwen2.5-72b-instruct`
- `qwen/qwen2.5-coder-32b-instruct`
- `qwen/qwq-32b`

**OpenRouter-specific headers** (optional, for rate limit and attribution):
```python
client = OpenAI(
    api_key="your-openrouter-key",
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "https://yourapp.com",  # optional attribution
        "X-Title": "Your App Name",              # optional
    }
)
```

---

## Key Parameters

| Parameter | Type | Notes |
|---|---|---|
| `model` | string | Required. See model strings above |
| `messages` | array | Required. `system` / `user` / `assistant` / `tool` roles |
| `temperature` | float 0–2 | Randomness. Default 1.0. Use 0.1–0.3 for coding tasks |
| `max_tokens` | int | Max output tokens. Qwen3.6 Plus max: 65,536 |
| `stream` | bool | Enable SSE streaming |
| `tools` | array | Function/tool definitions (see tool-use.md) |
| `tool_choice` | string/object | `"auto"`, `"none"`, `"required"`, or `{"type":"function","function":{"name":"..."}}` |
| `response_format` | object | `{"type":"text"}`, `{"type":"json_object"}`, or `{"type":"json_schema","json_schema":{...}}` |
| `top_p` | float | Nucleus sampling; use with temperature, not both |
| `top_k` | int | Via `extra_body={"top_k": 20}` — useful for coding tasks |
| `seed` | int | Reproducible outputs (best-effort) |
| `stop` | string/array | Custom stop sequences |
| `enable_thinking` | bool | Via `extra_body={"enable_thinking": True}` — enables reasoning tokens |
| `preserve_thinking` | bool | Via `extra_body={"chat_template_kwargs": {"preserve_thinking": True}}` — keeps CoT in history for agents |

**Recommended sampling for coding tasks:** `temperature=0.6, top_p=0.95, top_k=20, presence_penalty=0.0`

---

## Streaming

```python
stream = client.chat.completions.create(
    model="qwen/qwen3.6-plus",
    messages=[{"role": "user", "content": "Write a sorting algorithm"}],
    stream=True
)

for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="", flush=True)
```

---

## Authentication

| Provider | Env var | Where to get |
|---|---|---|
| OpenRouter | `OPENROUTER_API_KEY` | openrouter.ai/keys |
| DashScope | `DASHSCOPE_API_KEY` | dashscope.aliyuncs.com |
| HuggingFace | `HF_TOKEN` | huggingface.co/settings/tokens |

---

## Responses API (Newer — Recommended for Agents)

Alibaba also offers a Responses API compatible with OpenAI's Responses API format. Advantages over Chat Completions:
- Built-in tools: `web_search`, `code_interpreter`, `web_extractor`
- `previous_response_id` for automatic multi-turn context (no manual history management)
- Better cache utilization

**Endpoint (Singapore):** `https://dashscope-intl.aliyuncs.com/api/v2/apps/protocols/compatible-mode/v1/responses`

```python
# Multi-turn with Responses API
response1 = client.responses.create(model="qwen3.5-plus", input="My name is John.")
response2 = client.responses.create(
    model="qwen3.5-plus",
    input="Do you remember my name?",
    previous_response_id=response1.id
)

# Built-in tools
response = client.responses.create(
    model="qwen3.5-plus",
    input="Search for Alibaba Cloud AI news and summarize key points",
    tools=[{"type": "web_search"}, {"type": "code_interpreter"}]
)
print(response.output_text)
```

**Supported models for Responses API:** `qwen3-max`, `qwen3.5-plus`, `qwen3.5-flash`, `qwen3-coder-plus`, `qwen3-coder-flash`.

---

## Gotchas

- **DashScope vs OpenRouter model strings differ**: DashScope uses `qwen3.6-plus`; OpenRouter uses `qwen/qwen3.6-plus`. Mixing them up returns a 404 model-not-found error.
- **Long-context pricing jump**: Qwen3.6 Plus input pricing jumps 4x (from $0.276 to $1.101/M) for requests exceeding 256K tokens. Chunk requests under 256K when possible to stay on the cheaper tier.
- **Free tier availability**: `qwen/qwen3.6-plus-preview:free` on OpenRouter has rate limits and may go offline. Always have the paid model string as fallback.
- **Max output is 65,536 tokens**: Much higher than most models but not unlimited. Set `max_tokens` explicitly for long-form generation to avoid hitting it unexpectedly.
- **Always-on CoT uses output tokens**: Qwen3.6 Plus's chain-of-thought is always active and counts toward output token billing — factor this into cost estimates for short tasks.
- **LangChain/LlamaIndex compatibility**: Works via OpenAI provider — just swap `openai_api_base` and `model`. No code changes beyond those two params.
