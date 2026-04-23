# Claude API Reference

## Table of Contents
- [Messages API](#messages-api)
- [Tool Use / Function Calling](#tool-use--function-calling)
- [Streaming](#streaming)
- [Extended Thinking](#extended-thinking)
- [Prompt Caching](#prompt-caching)
- [Message Batches API](#message-batches-api)
- [Files API](#files-api)
- [Task Budgets](#task-budgets)
- [Third-party Platforms](#third-party-platforms)
- [SDKs](#sdks)
- [Gotchas](#gotchas)

---

## Messages API

`POST /v1/messages`

```json
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 4096,
  "system": "...",
  "messages": [{"role": "user", "content": "..."}]
}
```

**Content block types** (in `messages[].content`):
- `text` — plain text
- `image` — URL or base64 (JPEG, PNG, GIF, WebP)
- `document` — PDF or plain text (URL, base64, or `file_id`)
- `tool_use` / `tool_result` — function calling blocks
- `thinking` — extended thinking blocks (cacheable)

**Key parameters:**
| Parameter | Notes |
|---|---|
| `temperature` | 0–1.0; 0 = deterministic, 1 = creative |
| `stop_sequences` | Custom stop tokens |
| `stream` | `true` for SSE streaming |
| `tool_choice` | `auto`, `any`, `tool` (force specific), `none` |
| `thinking` | `{"type": "enabled", "budget_tokens": N}` |
| `output_config` | JSON schema for structured outputs |
| `service_tier` | `"auto"` or `"standard_only"` |
| `metadata.user_id` | Attribution |

Response `usage` includes: `input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`.

---

## Tool Use / Function Calling

### Client tools (you execute them)
Define with name, description, JSON Schema input. Claude returns `stop_reason: "tool_use"` with a `tool_use` block. You execute and send back `tool_result`.

Add `strict: true` to guarantee schema conformance.

### Server tools (Anthropic executes them)
| Tool | Type string |
|---|---|
| Web search | `web_search_20260209` |
| Fetch URL | `web_fetch` |
| Execute Python | `code_execution` |
| Execute bash | `bash_code_execution` |
| Edit text files | `str_replace_based_edit_tool` |
| Cross-conversation memory | `memory` |

Token overhead for built-in system prompt: ~313–530 tokens depending on model and `tool_choice`.

---

## Streaming

Enable with `stream: true`. Server-sent events:
- `content_block_start`
- `content_block_delta`
- `message_delta`
- `message_stop`

---

## Extended Thinking

Available on Sonnet 4.6, Haiku 4.5, Opus 4.7 (adaptive), and legacy 4.x models.

```json
"thinking": {"type": "enabled", "budget_tokens": 20000}
```

Minimum budget: 1024 tokens. Display: `"summarized"` (visible) or `"omitted"` (redacted but keeps signature for caching). Priced as output tokens at a discount.

---

## Prompt Caching

Reduces cost ~90% on cache hits (cache read = 0.1× base input price).

| TTL | Write cost multiplier |
|---|---|
| 5 minutes (default) | 1.25× |
| 1 hour | 2× |

Mark cacheable blocks with `"cache_control": {"type": "ephemeral", "ttl": "1h"}` (omit `ttl` for 5-min default).

Up to 4 explicit breakpoints. Minimum cacheable size: 1024–4096 tokens (model-dependent).

Cache invalidated by: changing tools, toggling server tools, modifying system + messages above the breakpoint, changing thinking parameters.

---

## Message Batches API

Async bulk processing. **50% cost reduction.** Most batches complete in under 1 hour.

- `POST /v1/messages/batches` — submit array of requests
- Poll status until `processing_status: "ended"`
- Max 300k output tokens per request (with `output-300k-2026-03-24` beta header on Opus 4.7/4.6, Sonnet 4.6)
- Not eligible for Zero Data Retention
- Not available on Bedrock/Vertex

---

## Files API

Upload files once, reference by `file_id` across many requests. Beta header required: `anthropic-beta: files-api-2025-04-14`.

| Operation | Endpoint |
|---|---|
| Upload | `POST /v1/files` |
| List | `GET /v1/files` |
| Delete | `DELETE /v1/files/{id}` |

Supported types: PDF → `document` block, plain text → `document`, images → `image`, datasets → `container_upload` (code execution).

Limits: 500 MB per file, 500 GB org storage. Upload/list/delete operations are free; content billed as input tokens when used in messages.

Not available on Bedrock/Vertex.

---

## Task Budgets

**Public beta.** Guide how Claude allocates tokens across a long agentic run so the model can prioritize work rather than exhausting context on exploration.

Useful when agents consistently run out of context before finishing — task budgets let you declare priorities so the model knows what to cut or defer if space gets tight. Beta header required (check API changelog for current header name).

---

## Third-party Platforms

**Amazon Bedrock**: Model IDs prefixed `anthropic.` (e.g., `anthropic.claude-sonnet-4-6`). AWS SigV4 auth. Supports: prompt caching, extended thinking, tool use, structured outputs. Does not support: Anthropic server tools, Files API, Batches API, computer use.

**Google Vertex AI**: GCP-style model IDs, global/multi-region/regional endpoints. Similar feature parity to Bedrock.

**Microsoft Azure Foundry**: Azure-native deployment.

---

## SDKs

```bash
pip install anthropic                    # Python
npm install @anthropic-ai/sdk            # TypeScript/Node
```

Also available: C#, Go, Java, PHP, Ruby.

```python
from anthropic import Anthropic
client = Anthropic()
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
print(message.content[0].text)
```

---

## Gotchas

- **`stop_reason: "tool_use"`** means you must call the tool — Claude is paused waiting. Failure to respond breaks the loop.
- **Cache breakpoints must be stable** — adding a message before a breakpoint invalidates all caches below it.
- **Batch API is async-only** — no streaming; poll until complete.
- **Files API beta header is required** — requests without it get a 400 error.
- **Server tools add ~400–530 tokens of system prompt overhead** — account for this in context budget.
- **`tool_choice: "tool"` forces a specific tool** — useful to guarantee Claude calls your function rather than answering directly.
