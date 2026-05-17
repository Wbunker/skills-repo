# MiniMax API Reference

## Base URLs

| Compatibility | Base URL |
|---|---|
| OpenAI-compatible | `https://api.minimax.io/v1` |
| Anthropic-compatible | `https://api.minimax.io/anthropic` |

## Authentication

Set the API key in the SDK constructor or as an environment variable:

```bash
# For OpenAI SDK
export OPENAI_API_KEY="your_minimax_key"

# For Anthropic SDK
export ANTHROPIC_API_KEY="your_minimax_key"
```

Or pass it explicitly in code — the key is the same regardless of which SDK surface you use.

## OpenAI-Compatible Endpoint

**Endpoint:** `POST https://api.minimax.io/v1/chat/completions`

### Supported Parameters

| Parameter | Notes |
|---|---|
| `model` | Required. e.g. `MiniMax-M2.7` |
| `messages` | Required. Text content only — image inputs not yet supported |
| `max_tokens` | Max output tokens |
| `stream` | `true`/`false` |
| `temperature` | Range: `(0.0, 1.0]` |
| `top_p` | Nucleus sampling |
| `tools` | Tool definitions array |
| `tool_choice` | `"auto"`, `"none"`, or specific tool |
| `n` | Must be `1` — multiple completions not supported |
| `extra_body` | MiniMax extensions (see below) |

### Unsupported Parameters

`presence_penalty`, `frequency_penalty`, `logit_bias`, `function_call` (deprecated), image/audio message inputs.

### Reasoning / Chain-of-Thought (OpenAI surface)

Enable extended thinking via `extra_body`:

```python
response = client.chat.completions.create(
    model="MiniMax-M2.7",
    messages=[{"role": "user", "content": "Solve: ..."}],
    extra_body={"reasoning_split": True}
)
# Access thinking: response.choices[0].message.reasoning_details
# Access answer:   response.choices[0].message.content
```

Max CoT output: 128K tokens.

### Streaming

```python
stream = client.chat.completions.create(
    model="MiniMax-M2.5",
    messages=[{"role": "user", "content": "Hello"}],
    stream=True
)
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="")
```

### Tool Use (OpenAI surface)

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather",
        "parameters": {
            "type": "object",
            "properties": {"location": {"type": "string"}},
            "required": ["location"]
        }
    }
}]

response = client.chat.completions.create(
    model="MiniMax-M2.7",
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    tools=tools,
    tool_choice="auto"
)
```

**Multi-turn tool calls:** Preserve the complete assistant message (including tool call fields) in the messages array on subsequent requests — required for reasoning continuity.

### Prompt Caching (OpenAI surface)

Available on M2.7 and M2.5. Automatic prefix caching — no special parameters needed. Cache pricing:
- Cache read: ~$0.059/M tokens
- Cache write: ~$0.375/M tokens
- Effective blended cost with caching on M2.5: ~$0.06/M tokens

## Anthropic-Compatible Endpoint

**Endpoint:** `POST https://api.minimax.io/anthropic/v1/messages`

```python
import anthropic

client = anthropic.Anthropic(
    base_url="https://api.minimax.io/anthropic",
    api_key="your_minimax_key"
)

message = client.messages.create(
    model="MiniMax-M2.7",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Supported Parameters

`model`, `messages` (text + tool calls only), `max_tokens`, `stream`, `system`, `temperature`, `tool_choice`, `tools`, `top_p`, `metadata`, `thinking`

### Unsupported Parameters

`top_k`, `stop_sequences`, `service_tier`, `mcp_servers`, `context_management`, `container`. Image and document inputs in messages are **not yet supported**.

### Reasoning (Anthropic surface)

```python
response = client.messages.create(
    model="MiniMax-M2.7",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    messages=[{"role": "user", "content": "Solve: ..."}]
)
```

## Error Codes

Standard HTTP status codes apply. Common causes:
- `401` — invalid or missing API key
- `429` — rate limit exceeded (Token Plan: per-5-hour window; Pay-as-you-go: see rate-limits in pricing.md)
- `400` — unsupported parameter or malformed request

Contact `api@minimax.io` to raise rate limits.

## Platform URLs

| Resource | URL |
|---|---|
| Console / API Keys | `https://platform.minimax.io` |
| API Documentation | `https://platform.minimax.io/docs` |
| Models overview | `https://platform.minimax.io/docs/guides/models-intro` |
