# Responses API

Introduced March 2025. **Recommended for all new projects.** The Chat Completions API remains supported indefinitely but is the legacy approach for stateful/agentic work.

## Endpoint

`POST https://api.openai.com/v1/responses`

---

## Request Shape

```json
{
  "model": "gpt-4.1",
  "input": "What's the weather in Paris?",
  "previous_response_id": "resp_abc123",
  "instructions": "You are a helpful assistant.",
  "store": true,
  "tools": [
    {"type": "web_search_preview"},
    {"type": "file_search", "vector_store_ids": ["vs_..."]},
    {"type": "code_interpreter"},
    {
      "type": "mcp",
      "server_url": "https://mcp.example.com",
      "server_label": "mytools",
      "require_approval": "auto",
      "headers": {"Authorization": "Bearer token"}
    }
  ],
  "stream": false,
  "response_format": {...},
  "temperature": 1.0,
  "max_output_tokens": 4096
}
```

**Key parameters not in Chat Completions:**

| Parameter | Notes |
|-----------|-------|
| `input` | New user message (string or content array) — replaces `messages` |
| `instructions` | System-level instructions — replaces `messages[0].role=system` |
| `previous_response_id` | ID of prior response; server fetches history automatically |
| `store` | `true` = server stores this response for chaining |
| `tools` | Includes both client functions AND built-in server tools |

---

## Response Shape

```json
{
  "id": "resp_abc123",
  "object": "response",
  "created_at": 1234567890,
  "model": "gpt-4.1",
  "output": [
    {
      "type": "message",
      "role": "assistant",
      "content": [
        {"type": "output_text", "text": "The weather in Paris is 20°C."}
      ]
    }
  ],
  "usage": {
    "input_tokens": 28,
    "output_tokens": 12,
    "total_tokens": 40
  }
}
```

Key difference: `output` array instead of `choices` array.

---

## Multi-Turn State Management

With Chat Completions: caller must resend full message history every turn (manual state).

With Responses API:
1. First turn: no `previous_response_id` — server creates new response, returns `id`
2. Subsequent turns: pass `previous_response_id` — server fetches full history automatically
3. `store: true` persists responses on OpenAI servers for chaining

```python
# Turn 1
r1 = client.responses.create(model="gpt-4.1", input="My name is Alice.", store=True)

# Turn 2 — no need to resend "My name is Alice."
r2 = client.responses.create(
    model="gpt-4.1",
    input="What's my name?",
    previous_response_id=r1.id,
    store=True
)
```

---

## Streaming

```json
{"stream": true}
```

Uses a richer event model than Chat Completions SSE:

Event types: `response.created`, `response.in_progress`, `response.output_item.added`, `response.output_text.delta`, `response.output_text.done`, `response.completed`, `response.failed`

---

## Built-in Tools

All server-side. Not available in Chat Completions.

| Tool | Config |
|------|--------|
| `web_search_preview` | `{"type": "web_search_preview"}` |
| `file_search` | `{"type": "file_search", "vector_store_ids": [...]}` |
| `code_interpreter` | `{"type": "code_interpreter"}` |
| `computer_use_preview` | `{"type": "computer_use_preview"}` |
| `image_generation` | `{"type": "image_generation"}` |
| `mcp` | See MCP section below |

---

## Remote MCP Support

```json
{
  "type": "mcp",
  "server_url": "https://mcp.example.com/sse",
  "server_label": "mytools",
  "require_approval": "auto",
  "headers": {"Authorization": "Bearer <token>"}
}
```

- Supports Streamable HTTP and HTTP/SSE transports
- API fetches tool list from server automatically
- `require_approval`: `"always"` (default), `"never"`, or `"auto"` (per-tool override)
- Pricing: only pay for tokens in tool definitions and calls; no per-call fee
- Supported models: GPT-4o series, GPT-4.1 series, o1/o3/o3-mini/o4-mini

---

## vs. Chat Completions: Full Comparison

| Feature | Chat Completions | Responses API |
|---------|-----------------|---------------|
| State management | Developer-owned (resend history) | Server-maintained (`previous_response_id`) |
| Built-in web search | No (custom function only) | `web_search_preview` |
| Built-in file search | No | `file_search` |
| Built-in code interpreter | No | `code_interpreter` |
| Computer use | No | `computer_use_preview` |
| Image generation as tool | No | `image_generation` |
| Remote MCP servers | No | Yes |
| Prompt caching | 50% discount | 40–80% better utilization |
| Reasoning model support | Degrades after GPT-5.4 | Full support, continues improving |
| Response shape | `choices[].message` | `output[]` |
| System prompt field | `messages[0].role=system` | `instructions` field |
| API status | Supported indefinitely | **Recommended for new projects** |

---

## When to Use Each

**Chat Completions:**
- Stateless operations: classification, summarization, extraction
- Maximum model flexibility or third-party model compatibility
- Custom database persistence for conversation history
- Cost-critical applications (no context maintenance overhead)
- Existing integrations that already manage state

**Responses API:**
- Multi-turn conversations without managing state yourself
- Any use of built-in tools (web search, file search, code interpreter)
- Agentic workflows
- New projects — this is OpenAI's recommended path
- Reasoning models with tools (Chat Completions support degrading)
