# Using Claude Code with MiniMax

Claude Code can be pointed at the MiniMax API via the Anthropic-compatible endpoint.

## Setup

```bash
export ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic
export ANTHROPIC_API_KEY=your_minimax_api_key
export CLAUDE_MODEL=MiniMax-M2.7   # optional; sets default model
```

Then launch Claude Code normally:
```bash
claude
```

## Model IDs for Claude Code

Use the direct MiniMax model IDs (not OpenRouter slugs):

| Model | ID |
|---|---|
| Flagship | `MiniMax-M2.7` |
| Best coding/agent | `MiniMax-M2.5` |
| Fast/cheap | `MiniMax-M2.7-highspeed` |
| Roleplay | `MiniMax-M2-her` |

## docker-compose Integration (OpenClaw Setup)

From the article pattern — running an always-on agent with MiniMax via OpenClaw:

```yaml
# docker-compose.yml
services:
  openclaw:
    environment:
      - OPENCLAW_MODEL=minimax/MiniMax-M2.7
      - MINIMAX_API_KEY=${MINIMAX_API_KEY}
```

OpenClaw config equivalent:
```json
{
  "agents": {
    "defaults": {
      "model": "minimax/MiniMax-M2.7"
    }
  }
}
```

Or via env:
```bash
OPENCLAW_MODEL=minimax/MiniMax-M2.7
MINIMAX_API_KEY=your_key_here
```

## What Works with MiniMax via Claude Code

| Feature | Status |
|---|---|
| Text generation / chat | ✅ Works |
| Streaming responses | ✅ Works |
| Tool use / function calling | ✅ Works |
| Reasoning / extended thinking | ✅ Works (via `thinking` param) |
| System prompts | ✅ Works |
| Image inputs | ❌ Not yet supported |
| Document inputs | ❌ Not yet supported |
| `top_k` parameter | ❌ Not supported by MiniMax |
| `stop_sequences` | ❌ Not supported by MiniMax |

## Gotchas

- MiniMax's Anthropic-compatible endpoint does **not** support `top_k` or `stop_sequences`. If Claude Code sends these, MiniMax will silently ignore or error.
- Image and document inputs in messages are not supported — tasks requiring vision will fail.
- The Anthropic SDK appends its own path suffix. Use `https://api.minimax.io/anthropic` (not `/v1`) as the base URL.
- Token Plan Starter ($10/mo) is suitable for personal Claude Code usage — 1,500 requests per 5 hours is generous for interactive coding sessions.

## Cost Comparison for Claude Code Usage

| LLM | Cost model | ~Monthly for moderate usage |
|---|---|---|
| Claude Sonnet (Anthropic direct) | Pay-as-you-go | Variable, often $20–$100+ |
| MiniMax M2.7 (pay-as-you-go) | $0.30/$1.20 per M tokens | Varies |
| MiniMax Token Plan Starter | $10/month flat | $10/month |

For an always-on coding assistant making frequent requests, the Token Plan Starter offers the most predictable cost.
