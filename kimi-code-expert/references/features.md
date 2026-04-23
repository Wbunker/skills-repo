# Kimi API Features

## Thinking Mode (Extended Reasoning)

### Models
- **`kimi-k2.6`**: Thinking on by default. Disable with `{"type": "disabled"}`. Supports `"keep": "all"`.
- **`kimi-k2.5`**: Thinking on by default. Disable with `{"type": "disabled"}`.
- **`kimi-k2-thinking`**: Always on — no control needed, just switch model.
- **`kimi-k2-thinking-turbo`**: Always on, high speed.

### Enabling / Disabling (kimi-k2.6)

```python
# Thinking enabled (default)
response = client.chat.completions.create(
    model="kimi-k2.6",
    messages=[{"role": "user", "content": "Solve this step by step..."}],
    temperature=1.0,
    max_completion_tokens=32000,
    stream=True,
)

# Disable thinking
response = client.chat.completions.create(
    model="kimi-k2.6",
    messages=[...],
    extra_body={"thinking": {"type": "disabled"}},
    temperature=0.6,
)
```

### Thinking Response

The `reasoning_content` field appears before `content`. In streaming, it always streams first.

```python
# Access reasoning_content (not in OpenAI SDK types — use getattr)
for chunk in stream:
    delta = chunk.choices[0].delta
    rc = getattr(delta, "reasoning_content", None)
    if rc:
        print(rc, end="")  # Thinking
    elif delta.content:
        print(delta.content, end="")  # Answer
```

### Configuration Requirements
| Setting | Value | Reason |
|---|---|---|
| `temperature` | 1.0 (thinking) / 0.6 (non-thinking) | Required; mismatching degrades output |
| `max_completion_tokens` | ≥ 16,000 | Prevents truncation of reasoning |
| `stream` | `True` | Recommended to avoid gateway timeouts |

### Preserved Thinking (`keep: "all"`) — kimi-k2.6 only
Maintains full `reasoning_content` across multi-turn conversations for continuous chain-of-thought. Incurs additional token cost. Include complete `reasoning_content` from prior context when using multi-turn thinking.

---

## Vision (Image and Video Input)

Supported by: `kimi-k2.6`, `kimi-k2.5`, all `moonshot-v1-*-vision-preview` models.

### Image Input

```python
messages = [{
    "role": "user",
    "content": [
        {"type": "text", "text": "What is in this image?"},
        {
            "type": "image_url",
            "image_url": {
                "url": "data:image/jpeg;base64,{base64_string}"
                # or file ID: "ms://files/{file_id}"
            }
        }
    ]
}]
```

**Supported formats:** PNG, JPEG, WebP, GIF  
**Recommended max resolution:** 4K (4096×2160)

### Video Input

```python
{"type": "video_url", "video_url": {"url": "ms://files/{file_id}"}}
```

**Supported formats:** MP4, MPEG, MOV, AVI, X-FLV, MPG, WebM, WMV, 3GPP  
**Recommended max resolution:** 2K (2048×1080)  
Videos are processed as key frames — higher resolution = more tokens.

### Token Cost
Dynamic, based on resolution and content. Use `POST /v1/tokenizers/estimate-token-count` before processing to estimate cost. Avoid base64 for large images — dramatically increases token consumption vs file upload.

---

## File Upload and Document QA

### Upload Flow

```python
# 1. Upload
with open("document.pdf", "rb") as f:
    file = client.files.create(file=f, purpose="file-extract")

# 2. Extract content
content = client.files.content(file.id)
file_text = content.text

# 3. Use in chat (pass content, NOT file_id)
messages = [
    {"role": "system", "content": file_text},
    {"role": "user", "content": "Summarize this document."},
]
```

**Supported:** Text files, PDFs, images (OCR), Office formats  
**Limit:** 1,000 files per user  
**File storage:** Temporarily free  
**Critical:** Pass extracted **content** as system message — not the `file_id`.  
For multiple files: use separate system messages, one per file.

Store extracted content locally to avoid re-uploading. Delete files with `client.files.delete(file_id)` when done.

---

## JSON Mode

Enable structured JSON output:

```python
response = client.chat.completions.create(
    model="kimi-k2.6",
    messages=[
        {"role": "system", "content": "Output JSON with keys: title, summary, author"},
        {"role": "user", "content": "Summarize this article: ..."},
    ],
    response_format={"type": "json_object"},
)
result = json.loads(response.choices[0].message.content)
```

- Model outputs only JSON **objects** (not arrays)
- Always parse with `json.loads()`
- If `finish_reason="length"`, increase `max_completion_tokens`
- **Do not mix** with partial mode

---

## Partial Mode (Prefill)

Control model output by prefilling the response start:

```python
messages = [
    {"role": "user", "content": "Extract product info as JSON"},
    {"role": "assistant", "content": "{", "partial": True},  # Prefill
]
response = client.chat.completions.create(model="kimi-k2.6", messages=messages)
# Concatenate prefill + response:
full_output = "{" + response.choices[0].message.content
```

**Use cases:**
- JSON output without needing `json_object` mode (prefill `{`)
- Role-play consistency (prefill character name)

**API response does not include the leading_text** — concatenate manually.  
**Do not mix** with `response_format=json_object`.

---

## Streaming

```python
stream = client.chat.completions.create(
    model="kimi-k2.6",
    messages=[...],
    stream=True,
)
full_content = ""
for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.content:
        full_content += delta.content
        print(delta.content, end="", flush=True)
# usage is in the last chunk
```

**SSE format:** `data: {...}\n\n` ... `data: [DONE]`  
**Usage stats** only in final chunk.  
**`role`** only in first chunk.  
For `n>1`: track `chunk.choices[0].index` to organize multiple responses.

---

## Auto-Reconnect for Long Streams

For very long streaming responses, connections may drop. Use `Last-Event-ID` header with the last received event ID to resume. Documented at: `platform.kimi.ai/docs/guide/auto-reconnect.md`
