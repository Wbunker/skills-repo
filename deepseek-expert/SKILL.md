---
name: deepseek-expert
description: DeepSeek AI expertise covering the DeepSeek API (V4-Pro, V4-Flash), thinking/reasoning mode, tool use and function calling, local inference (Ollama, LM Studio, llama.cpp, vLLM), model selection, pricing, and context caching. Use when integrating DeepSeek models via API, enabling chain-of-thought reasoning mode, configuring tool/function calling including strict mode, running DeepSeek models locally, comparing DeepSeek to other LLMs, or understanding the R1/V3/V4 model family differences.
---

# DeepSeek Expert

DeepSeek provides frontier-quality LLMs at aggressive price points. The API is OpenAI-compatible — any OpenAI SDK client works with a base URL swap. The model family splits into two lines: **V-series** (general intelligence, instruction following, coding) and **R-series** (reasoning/math/science with chain-of-thought).

```
DeepSeek Model Family
├── V-series (fast, cheap, great coding)
│   ├── deepseek-v4-pro   — 1.6T/49B active, 1M ctx, thinking optional
│   └── deepseek-v4-flash — 284B/13B active, 1M ctx, thinking optional
│       ↑ replaces deepseek-chat + deepseek-reasoner (deprecated 2026-07-24)
└── R-series (open-weights reasoning, local-friendly)
    ├── DeepSeek-R1        — full 671B MoE, matches o1
    └── R1-Distill variants — 1.5B/7B/8B/14B/32B/70B (Qwen/Llama base)
```

## Quick Setup (OpenAI SDK)

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-...",                    # from platform.deepseek.com
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.choices[0].message.content)
```

## Quick Reference

| Task | Reference |
|------|-----------|
| API endpoints, auth, parameters, streaming, errors, pricing, context caching | [api.md](references/api.md) |
| Thinking/reasoning mode, reasoning_content, effort levels, multi-turn rules | [thinking-mode.md](references/thinking-mode.md) |
| Tool use, function calling, strict mode, multi-turn tool loops | [tool-use.md](references/tool-use.md) |
| Local inference: Ollama, LM Studio, llama.cpp, vLLM, hardware requirements | [local-inference.md](references/local-inference.md) |
| Full model lineup, context windows, pricing table, R1 distill variants | [models.md](references/models.md) |

## Core Decision Trees

### Which model?

```
What's the task?
├── General coding / chat / instruction following
│   ├── Need cheapest → deepseek-v4-flash (non-thinking)
│   └── Need best quality → deepseek-v4-pro
├── Math / logic / science / complex reasoning
│   └── Enable thinking mode on v4-pro or v4-flash
│       → See thinking-mode.md
├── Local / offline / private
│   ├── Consumer GPU (≤24GB VRAM) → R1-Distill-Qwen-32B (Q4, ~20GB)
│   ├── 12GB VRAM → R1-Distill-14B
│   ├── 8GB VRAM → R1-Distill-7B
│   └── See local-inference.md for full hardware table
└── Via OpenRouter → use deepseek/deepseek-chat or deepseek/deepseek-r1
```

### API vs local?

```
Privacy required / no internet → Local (Ollama + R1-Distill)
Cost sensitive, high volume   → API (DeepSeek cloud is ~10× cheaper than Claude)
Best reasoning quality        → API (V4-Pro with thinking mode)
Offline / air-gapped          → Local
Prototyping quickly           → API
```

## Key Concepts

| Term | Meaning |
|------|---------|
| **Thinking mode** | Enables chain-of-thought reasoning; response includes `reasoning_content` + `content` |
| **Context caching** | Automatic prefix caching; cache-hit input tokens ~4× cheaper |
| **MoE** | Mixture of Experts — V4-Pro is 1.6T total but only 49B params are active per token |
| **R1-Distill** | Smaller models (7B–70B) trained by distilling R1's reasoning into Qwen/Llama bases |
| **Strict mode** | Beta tool-calling feature that enforces JSON schema compliance on function arguments |
| **deepseek-chat** | Legacy alias → now maps to deepseek-v4-flash (non-thinking). Deprecated 2026-07-24 |
| **deepseek-reasoner** | Legacy alias → now maps to deepseek-v4-flash (thinking). Deprecated 2026-07-24 |

## Gotchas

- `deepseek-chat` and `deepseek-reasoner` are **deprecated** as of 2026-07-24. Migrate to `deepseek-v4-flash` and `deepseek-v4-pro` now.
- Thinking mode **ignores** `temperature`, `top_p`, `presence_penalty`, `frequency_penalty` — setting them causes no error but has no effect.
- In multi-turn conversations with thinking mode + tool calls, **reasoning_content must be passed back** in subsequent requests. Without tool calls, omit it.
- Strict mode tool calling requires `base_url="https://api.deepseek.com/beta"` — the production endpoint does not support it.
- Context window is 1M tokens for V4, but **max output is 8K tokens** (not 1M). Don't confuse input context with output limits.
- R1-Distill models are reasoning-focused; they can be verbose on simple tasks. For instruction-following, V4-Flash is better.
