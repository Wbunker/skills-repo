# Kimi Chat Completions API

## Endpoint

```
POST https://api.moonshot.ai/v1/chat/completions
Authorization: Bearer $MOONSHOT_API_KEY
Content-Type: application/json
```

OpenAI-compatible. Use the OpenAI SDK with `base_url="https://api.moonshot.ai/v1"`.

---

## Request Parameters

### Required
| Parameter | Type | Description |
|---|---|---|
| `model` | string | Model ID (e.g., `kimi-k2.6`) |
| `messages` | array | Conversation history — role: `system`, `user`, `assistant`, `tool` |

### Optional — Core
| Parameter | Type | Default | Notes |
|---|---|---|---|
| `max_completion_tokens` | int | ~1024 | Max output tokens. Set ≥16,000 when using thinking mode. |
| `temperature` | float | 0.6 (k2, non-think) / 1.0 (thinking) | Range [0, 1]. k2.6 non-thinking: 0.6; thinking: 1.0. |
| `top_p` | float | 1.0 (non-think) / 0.95 (thinking) | Nucleus sampling |
| `stream` | bool | false | Enable SSE streaming |
| `stop` | string\|array | — | Up to 5 stop sequences, max 32 bytes each |
| `n` | int | 1 | Number of completions (1–5). With `temperature=0`, always 1. |
| `presence_penalty` | float | 0 | Range [−2.0, 2.0] |
| `frequency_penalty` | float | 0 | Range [−2.0, 2.0] |

### Optional — Output Format
| Parameter | Type | Notes |
|---|---|---|
| `response_format` | object | `{"type": "text"}` (default), `{"type": "json_object"}`, or `{"type": "json_schema", ...}` |
| `partial` | bool | Enable partial/prefill mode (on last assistant message) |

### Optional — Tools
| Parameter | Type | Notes |
|---|---|---|
| `tools` | array | Function definitions. Max 128 tools. |
| `tool_choice` | string | `"none"`, `"auto"`, `null`. `"required"` NOT supported. |

### Optional — Thinking (kimi-k2.6 / kimi-k2.5)
| Parameter | Type | Notes |
|---|---|---|
| `thinking` | object | `{"type": "enabled"}`, `{"type": "disabled"}`, or `{"type": "enabled", "keep": "all"}` |

### Content Types (multimodal)
Content field accepts a string or array of typed objects:
```json
[
  {"type": "text", "text": "Describe this image:"},
  {"type": "image_url", "image_url": "data:image/jpeg;base64,..."},
  {"type": "video_url", "video_url": "ms://files/{file_id}"}
]
```

---

## Response Format

```json
{
  "id": "cmpl-...",
  "object": "chat.completion",
  "created": 1698999496,
  "model": "kimi-k2.6",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "response text",
      "reasoning_content": "chain-of-thought (if thinking enabled)",
      "tool_calls": [...]
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 21,
    "total_tokens": 40,
    "cached_tokens": 10
  }
}
```

**`finish_reason` values:** `stop`, `tool_calls`, `length` (truncated — increase `max_completion_tokens`), `content_filter`.

---

## Streaming Response

```python
stream = client.chat.completions.create(
    model="kimi-k2.6",
    messages=[...],
    stream=True,
)
for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="")
```

- Each SSE chunk: `data: {...}\n\n`
- Stream ends with `data: [DONE]`
- `usage` appears only in the **final** chunk
- `reasoning_content` always streams before `content`
- Access `reasoning_content` via `getattr(delta, "reasoning_content", None)` — OpenAI SDK types don't declare it

---

## Other Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /v1/models` | List available models (id, context_length, capabilities flags) |
| `POST /v1/tokenizers/estimate-token-count` | Estimate token count before sending |
| `GET /v1/users/me/balance` | Check account balance |
| `POST /v1/files` | Upload file (`purpose`: `file-extract` or `batch`) |
| `GET /v1/files` | List files |
| `GET /v1/files/{id}` | Get file metadata |
| `GET /v1/files/{id}/content` | Get extracted file content |
| `DELETE /v1/files/{id}` | Delete file |
| `POST /v1/batches` | Create batch job |
| `GET /v1/batches` | List batches |
| `GET /v1/batches/{id}` | Retrieve batch status |
| `POST /v1/batches/{id}/cancel` | Cancel batch |

---

## Error Codes

| HTTP | Code | Meaning | Fix |
|---|---|---|---|
| 400 | `content_filter` | Request flagged as high risk | Remove unsafe content |
| 400 | `invalid_request_error` | Bad format, missing params, token limit exceeded | Check request structure |
| 401 | `incorrect_api_key_error` | Bad API key | Verify key; check platform (.ai vs .com) |
| 403 | `permission_denied_error` | API disabled or unauthorized | Check account access |
| 404 | `resource_not_found_error` | Model ID wrong or no access | Verify model ID |
| 429 | `rate_limit_reached_error` | RPM/TPM/concurrency exceeded | Back off and retry |
| 429 | `exceeded_current_quota_error` | No balance or suspended account | Top up account |
| 429 | `engine_overloaded_error` | Server overload | Retry later |
| 500 | `server_error` | Internal error | Retry; contact support if persistent |

---

## Differences from OpenAI API

| Feature | OpenAI | Kimi |
|---|---|---|
| `temperature` range | [0, 2] | [0, 1] |
| `temperature=0` + `n>1` | Allowed | Returns 1 completion |
| `tool_choice="required"` | Supported | Not supported |
| `functions` param | Deprecated but accepted | Not supported — use `tools` |
| Usage in stream | Last data block only | In each choice's end data block |
| Thinking output | N/A | `reasoning_content` field (use `getattr`) |
