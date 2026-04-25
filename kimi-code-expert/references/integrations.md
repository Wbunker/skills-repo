# Kimi Integrations, Batch API, and Rate Limits

## Migrating from OpenAI

Kimi is OpenAI-compatible. Change two things:

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["MOONSHOT_API_KEY"],   # was OPENAI_API_KEY
    base_url="https://api.moonshot.ai/v1",    # was https://api.openai.com/v1
)
```

### Model ID Mapping (approximate)

| OpenAI | Kimi equivalent |
|---|---|
| gpt-4o / gpt-4.1 | kimi-k2.6 |
| gpt-4o-mini | kimi-k2.5 |
| o1 / o3 | kimi-k2.6 (thinking) or kimi-k2-thinking |
| text-embedding-* | No direct equivalent currently |

### API Differences to Watch

| Item | Difference |
|---|---|
| `temperature` range | Kimi: [0, 1]. Set max to 1.0 (not 2.0) |
| Thinking mode temperature | Non-thinking: 0.6. Thinking: 1.0 — must match exactly |
| `tool_choice="required"` | Not supported — use prompt engineering |
| `functions` param | Not supported — use `tools` only |
| Usage in stream | Kimi puts it in each choice's end block, not just the last block |
| `reasoning_content` | Use `getattr(msg, "reasoning_content", None)` — not in OpenAI SDK types |
| `temperature=0` + `n>1` | Kimi always returns n=1 when temperature=0 |

### Compatible Endpoints
`/v1/chat/completions`, `/v1/files`, `/v1/files/{id}`, `/v1/files/{id}/content`

---

## Claude Code / Cline / RooCode Integration

### Option A: Direct API (no Ollama)

Use Kimi as a drop-in replacement backend in OpenAI-compatible IDE tools.

**Configuration pattern:**
```json
{
  "apiProvider": "openai-compatible",
  "baseUrl": "https://api.moonshot.ai/v1",
  "apiKey": "$MOONSHOT_API_KEY",
  "model": "kimi-k2.6"
}
```

Refer to `platform.kimi.ai/docs/guide/agent-support.md` for tool-specific setup instructions for Claude Code, Cline, RooCode, and OpenCode.

### Option B: Ollama Cloud proxy (recommended if you already use Ollama)

Ollama Cloud ($20/month Pro) provides cloud-hosted inference for Kimi K2.6 via an Anthropic-compatible API. `ollama launch claude` wires up `ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_BASE_URL` automatically — no manual env var setup.

**Setup:**
```bash
# 1. Requires Ollama v0.15+
ollama --version

# 2. Sign in / create account (links to ollama.com/pricing for Pro)
ollama login

# 3. Pull the cloud model (lightweight — inference runs remotely)
ollama pull kimi-k2.6:cloud

# 4. Launch Claude Code pointed at Kimi K2.6
ollama launch claude --model kimi-k2.6:cloud
```

**Verify inside Claude Code:**
```
/status
# Should show:
# Model: kimi-k2.6:cloud
# Auth token: ANTHROPIC_AUTH_TOKEN
# Anthropic base URL: http://localhost:11434
```

**Cost comparison:** Ollama Cloud Pro $20/month vs Claude Max $100/month vs Claude Max Ultimate $200/month. Suitable for prototyping and experimental projects where per-token API cost and data privacy constraints don't apply.

---

## Batch API

Async job processing at 40% off real-time inference pricing.  
**Supported models:** `kimi-k2.6` and `kimi-k2.5` only. One model per batch.

### Workflow

```python
# 1. Build JSONL input file
import jsonlines

with jsonlines.open("requests.jsonl", "w") as writer:
    writer.write({
        "custom_id": "req-001",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "kimi-k2.6",
            "messages": [{"role": "user", "content": "Summarize..."}],
        }
    })

# 2. Upload
with open("requests.jsonl", "rb") as f:
    upload = client.files.create(file=f, purpose="batch")

# 3. Create batch
batch = client.batches.create(
    input_file_id=upload.id,
    endpoint="/v1/chat/completions",
    completion_window="24h",  # or "3d" / "7d" for large datasets
)

# 4. Poll (every 10–60 seconds)
while True:
    status = client.batches.retrieve(batch.id)
    if status.status == "completed":
        break
    time.sleep(30)

# 5. Download results
output = client.files.content(status.output_file_id)
for line in output.text.splitlines():
    result = json.loads(line)
    print(result["custom_id"], result["response"]["body"]["choices"][0]["message"]["content"])
```

### Batch Constraints
- Max file size: 100MB
- Status lifecycle: `validating → in_progress → finalizing → completed` (also: `failed`, `expired`, `cancelling`, `cancelled`)
- Parameters that cannot be changed per request in a batch: `temperature`, `top_p`, `n`, `presence_penalty`, `frequency_penalty`
- Use `completion_window="3d"` or `"7d"` for large datasets

---

## Rate Limits

Tiers are based on account level (determined by spend/age):

| Tier | RPM | TPM | TPD | Concurrency |
|---|---|---|---|---|
| 0 | 3 | 500K | 1.5M | 1 |
| 1 | 200 | 2M | Unlimited | — |
| 2 | 500 | 3M | Unlimited | — |
| 3 | 5,000 | 3M | Unlimited | — |
| 4 | 5,000 | 4M | Unlimited | — |
| 5 | 10,000 | 5M | Unlimited | 1,000 |

**Rate limit FAQ:** `platform.kimi.ai/docs/pricing/faq.md`

### Handling Rate Limits
- OpenAI SDK retries twice by default — a rate-limited call = 3 API hits. Disable with `max_retries=0` if managing retries yourself.
- Back off exponentially on 429 errors.
- Check `engine_overloaded_error` (server busy) vs `rate_limit_reached_error` (your quota) — different retry strategies.

---

## OpenClaw Integration

Kimi can be used within the OpenClaw agent platform.  
Documentation: `platform.kimi.ai/docs/guide/use-kimi-in-openclaw.md`

---

## Organization Setup

For team/enterprise usage: `platform.kimi.ai/docs/guide/org-best-practice.md`

Enterprise plan: custom rate limits, SLA-backed reliability, dedicated support. Contact via `platform.kimi.ai`.
