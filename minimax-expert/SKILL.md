---
name: minimax-expert
description: MiniMax AI expertise covering their API (OpenAI-compatible and Anthropic-compatible endpoints), model lineup (M2.7, M2.5, M2.1, M2-her), flat-rate Token Plan subscriptions ($10–$150/mo), pay-as-you-go pricing, tool use/function calling, streaming, reasoning/chain-of-thought, prompt caching, and multimodal APIs (speech, video, music, image). Use when integrating MiniMax models via API, configuring Claude Code or other CLI tools to use MiniMax, understanding the Token Plan vs pay-as-you-go billing, selecting the right MiniMax model, enabling thinking/reasoning mode, or working with MiniMax's speech/video/music generation APIs.
---

# MiniMax Expert

MiniMax is an independent Chinese AI lab offering frontier models at aggressive prices. Their API is available in both **OpenAI-compatible** and **Anthropic-compatible** flavors — no MiniMax SDK needed.

```
MiniMax Model Family
├── M2.7         — flagship, ~60 tps, 204,800 ctx, agent harness, #1 Artificial Analysis Index
├── M2.7-highspeed — same capability, ~100 tps
├── M2.5         — SOTA coding/agent (SWE-bench 80.2%), 204,800 ctx
├── M2.5-highspeed
├── M2.1         — 230B params / 10B active, 204,800 ctx
├── M2.1-highspeed
├── M2           — 200K ctx, 128K max output, agentic
└── M2-her       — 204,800 ctx, roleplay/dialogue specialist
```

## Quick Setup

**OpenAI SDK:**
```python
from openai import OpenAI
client = OpenAI(
    base_url="https://api.minimax.io/v1",
    api_key="YOUR_MINIMAX_API_KEY"
)
response = client.chat.completions.create(
    model="MiniMax-M2.7",
    messages=[{"role": "user", "content": "Hello"}]
)
```

**Anthropic SDK:**
```python
import anthropic
client = anthropic.Anthropic(
    base_url="https://api.minimax.io/anthropic",
    api_key="YOUR_MINIMAX_API_KEY"
)
```

**Environment variables:**
```bash
export MINIMAX_API_KEY="your_key_here"
```

API keys are created at: `platform.minimax.io` → Account Management → API Keys

## Quick Reference

| Task | Reference |
|------|-----------|
| Endpoints, auth, parameters, streaming, tool use, caching, errors | [api.md](references/api.md) |
| Full model lineup, context windows, benchmarks, OpenRouter IDs | [models.md](references/models.md) |
| Token Plan subscriptions, pay-as-you-go rates, rate limits | [pricing.md](references/pricing.md) |
| Speech, video (Hailuo), music, image generation APIs | [multimodal.md](references/multimodal.md) |
| Claude Code CLI, env vars, model mapping | [claude-code.md](references/claude-code.md) |

## Core Decision Trees

### Which model?

```
Task type?
├── General coding / chat / instruction following
│   ├── Best quality → MiniMax-M2.7
│   └── Fastest → MiniMax-M2.7-highspeed or MiniMax-M2.5-highspeed
├── Complex reasoning / math / code review
│   └── MiniMax-M2.5 (SWE-bench 80.2%) or M2.7 with thinking enabled
├── Roleplay / dialogue / character
│   └── MiniMax-M2-her
├── Need 1M context (legacy)
│   └── Use via OpenRouter: minimax/minimax-m1 or minimax/minimax-01
└── Agentic workflows
    └── MiniMax-M2.7 (has built-in agent harness)
```

### Token Plan vs pay-as-you-go?

```
Usage pattern?
├── Always-on agent / high daily volume → Token Plan ($10/mo flat rate)
├── Bursty / unpredictable usage → Pay-as-you-go
├── Just prototyping → Pay-as-you-go (no subscription needed)
└── Need speech/image/video features → Token Plan Plus+ tier minimum
    (speech and image unlock at Plus tier, $20/mo)
```

## Key Concepts

| Term | Meaning |
|------|---------|
| **Token Plan** | Flat monthly subscription — requests included, no per-token billing |
| **Pay-as-you-go** | Per-token billing: M2.7 at $0.30/M input, $1.20/M output |
| **Highspeed variants** | Same model, ~100 tps vs ~60 tps; 2× more expensive |
| **reasoning_split** | OpenAI extra_body param to separate CoT into `reasoning_details` |
| **Prompt caching** | Available on M2.7 and M2.5; cache read ~$0.059/M, write ~$0.375/M |
| **Agent harness** | M2.7 built-in agentic framework capability |

## Gotchas

- The Anthropic-compatible endpoint does NOT support image/document inputs in messages (not yet implemented). Use the OpenAI endpoint for multimodal.
- `top_k` and `stop_sequences` are not supported by the Anthropic-compatible endpoint — omit them.
- The Token Plan `Starter` ($10/mo) does **not** include speech or image features — those require `Plus` ($20/mo) or higher.
- Rate limits on the Token Plan are per **5-hour window** (e.g., 1,500 M2.7 requests per 5 hours on Starter), not per month.
- On OpenRouter, MiniMax model IDs use versioned slugs like `minimax/minimax-m2.7-20260318` — not the same as the direct API IDs (`MiniMax-M2.7`).
- The `n` parameter only supports `n=1` — requesting multiple completions per call is not supported.
- `presence_penalty` and `frequency_penalty` are not supported by the OpenAI-compatible endpoint.
