# Chat Completions API

## Endpoint

`POST https://api.openai.com/v1/chat/completions`

Stateless. Caller manages all conversation history by resending the full `messages` array each turn.

---

## Full Request Shape

```json
{
  "model": "gpt-4.1",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi there!"},
    {"role": "user", "content": "What's the capital of France?"}
  ],
  "temperature": 1.0,
  "max_tokens": 4096,
  "top_p": 1.0,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0,
  "stream": false,
  "tools": [...],
  "tool_choice": "auto",
  "response_format": {"type": "text"},
  "n": 1,
  "stop": null,
  "logprobs": false,
  "top_logprobs": null,
  "seed": null,
  "user": "user-123"
}
```

**Key parameters:**

| Parameter | Type | Notes |
|-----------|------|-------|
| `model` | string | Required. Model ID |
| `messages` | array | Required. Full conversation history |
| `temperature` | float 0–2 | Sampling randomness. Default 1.0 |
| `max_tokens` | int | Max output tokens |
| `stream` | bool | Enable SSE streaming |
| `tools` | array | Function/tool definitions |
| `tool_choice` | string/object | `"auto"`, `"none"`, `"required"`, or `{"type":"function","function":{"name":"..."}}` |
| `response_format` | object | `{"type": "text"}`, `{"type": "json_object"}`, or `{"type": "json_schema", "json_schema": {...}}` |
| `n` | int | Number of choices to generate |
| `seed` | int | For deterministic outputs (best-effort) |

---

## Message Roles

- `system` — instructions, persona
- `user` — human turn
- `assistant` — model turn (for history)
- `tool` — tool result (role when returning function call output)
- `developer` — new alias for system in some newer docs

---

## Response Format

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1694268190,
  "model": "gpt-4.1",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Paris is the capital of France."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 28,
    "completion_tokens": 9,
    "total_tokens": 37
  }
}
```

`finish_reason` values: `"stop"`, `"length"`, `"tool_calls"`, `"content_filter"`, `"function_call"` (legacy)

---

## Streaming (SSE)

Set `"stream": true`. Responses arrive as `data: {...}` lines terminated by `data: [DONE]`.

**Chunk shape:**
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion.chunk",
  "created": 1694268190,
  "model": "gpt-4o-mini",
  "choices": [{
    "index": 0,
    "delta": {
      "role": "assistant",
      "content": "Hello"
    },
    "finish_reason": null
  }]
}
```

First chunk: `delta` contains `{"role": "assistant", "content": ""}`.
Final chunk: `finish_reason` is set, `content` is `""` or null.
Last line: `data: [DONE]`

**Python SDK streaming:**
```python
with client.chat.completions.stream(model="gpt-4.1", messages=[...]) as stream:
    for chunk in stream:
        print(chunk.choices[0].delta.content or "", end="", flush=True)
```

**TypeScript SDK streaming:**
```typescript
const stream = await client.chat.completions.stream({model: 'gpt-4.1', messages: [...]});
for await (const chunk of stream) {
  process.stdout.write(chunk.choices[0]?.delta?.content || '');
}
```

---

## Vision / Multimodal Inputs

Pass images via the `content` array in user messages:

```json
{
  "role": "user",
  "content": [
    {"type": "text", "text": "What's in this image?"},
    {
      "type": "image_url",
      "image_url": {
        "url": "https://example.com/photo.jpg",
        "detail": "auto"
      }
    }
  ]
}
```

**`detail` values:**
- `"auto"` — model decides
- `"low"` — faster, fewer tokens (always uses 85 tokens)
- `"high"` — full resolution analysis, more tokens
- `"original"` — no resize

**Base64 images:**
```json
"url": "data:image/jpeg;base64,<base64_encoded_data>"
```

Supported formats: JPEG, PNG, GIF, WebP.
Multiple images: include multiple `image_url` objects in same content array.
Images count as tokens and are billed accordingly.

**Vision-capable models:** All o-series, GPT-5 series, GPT-4.1 series, GPT-4.5, GPT-4o series.

---

## Tool Use / Function Calling

```json
{
  "tools": [{
    "type": "function",
    "function": {
      "name": "get_weather",
      "description": "Get current weather for a location",
      "parameters": {
        "type": "object",
        "properties": {
          "city": {"type": "string", "description": "City name"},
          "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
        },
        "required": ["city"],
        "additionalProperties": false
      },
      "strict": true
    }
  }]
}
```

**Flow:**
1. Send request with tools defined
2. Model returns response with `finish_reason: "tool_calls"` and `tool_calls` array
3. Caller executes the function locally
4. Caller sends new message with `role: "tool"`, `tool_call_id`, and result
5. Model generates final response

**Model response when calling a tool:**
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "call_abc123",
        "type": "function",
        "function": {
          "name": "get_weather",
          "arguments": "{\"city\": \"Paris\", \"unit\": \"celsius\"}"
        }
      }]
    },
    "finish_reason": "tool_calls"
  }]
}
```

**Tool result message:**
```json
{
  "role": "tool",
  "tool_call_id": "call_abc123",
  "content": "{\"temperature\": 20, \"condition\": \"sunny\"}"
}
```

Note: `strict: true` on function definition enables Structured Outputs enforcement for arguments.

---

## Structured Outputs

### Mode 1: `response_format` with JSON Schema

```python
response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[...],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "CalendarEvent",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "date": {"type": "string"},
                    "attendees": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["name", "date", "attendees"],
                "additionalProperties": False
            }
        }
    }
)
```

### Mode 2: Via Python SDK with Pydantic (parse method)

```python
from pydantic import BaseModel

class CalendarEvent(BaseModel):
    name: str
    date: str
    attendees: list[str]

response = client.beta.chat.completions.parse(
    model="gpt-4.1",
    messages=[...],
    response_format=CalendarEvent,
)
event = response.choices[0].message.parsed  # CalendarEvent instance
```

### JSON mode (weaker, no schema enforcement)

```json
"response_format": {"type": "json_object"}
```
Guarantees valid JSON output but does not enforce any schema.

---

## Prompt Caching

- **Automatic** — zero code changes required
- Activates when two requests share the same prefix AND land on the same machine
- Minimum 1024 tokens to qualify
- Cache TTL: 5–10 minutes of inactivity; up to 1 hour off-peak
- **50–90% discount on cached input tokens** (varies by model)
- No additional fees

| Model | Full Input | Cached Input | Savings |
|-------|-----------|--------------|---------|
| GPT-4.1 | $2.00/M | $0.50/M | 75% |
| GPT-4o | $2.50/M | $0.25/M | 90% |
| GPT-4o mini | $0.15/M | $0.075/M | 50% |
| o3 | $2.00/M | $0.50/M | 75% |
| o4-mini | $1.10/M | $0.275/M | 75% |

**Design for caching:** Put static content (system prompt, few-shot examples, long context) at the start of messages. Put dynamic content (user query) at the end.

---

## SDKs

### Python

```bash
pip install openai
```

```python
from openai import OpenAI

client = OpenAI(api_key="sk-...")  # or reads OPENAI_API_KEY env var

# Sync
response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.choices[0].message.content)

# Async
from openai import AsyncOpenAI
client = AsyncOpenAI()
response = await client.chat.completions.create(...)
```

### TypeScript / JavaScript

```bash
npm install openai
```

```typescript
import OpenAI from 'openai';

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const response = await client.chat.completions.create({
    model: 'gpt-4.1',
    messages: [{ role: 'user', content: 'Hello' }],
});
console.log(response.choices[0].message.content);
```

Requirements: Node.js 20 LTS+, TypeScript 4.9+.

Both SDKs support Pydantic/Zod for structured outputs, auto-retry with exponential backoff, streaming helpers, and work with 100+ non-OpenAI LLMs via OpenAI-compatible APIs.
