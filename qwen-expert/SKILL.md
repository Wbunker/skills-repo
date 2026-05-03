---
name: qwen-expert
description: >
  Expert guide covering all Qwen models, APIs, and deployment options. Use when: choosing a Qwen
  model for a project; building apps with the Qwen API (OpenAI-compatible, DashScope, or OpenRouter);
  tool use / function calling / structured outputs with Qwen models; deploying Qwen locally with
  Ollama, vLLM, or HuggingFace transformers; building agentic pipelines with Qwen3.6 Plus or
  QwQ; using Qwen2.5-Coder for code generation or repair; long-context processing with 1M-token
  context windows; questions about Qwen model families, benchmarks, pricing, and tradeoffs vs
  Claude or GPT-4.1; migrating an existing OpenAI codebase to Qwen (drop-in replacement).
---

# Qwen Expert

Reference hub for all Qwen models and APIs. Use the decision matrix to navigate, then load the relevant reference file.

## Decision Matrix

| Goal | Approach | Reference |
|---|---|---|
| Choose the right Qwen model | Model families + benchmarks | [models.md](references/models.md) |
| Build an app via API (cloud) | OpenAI-compatible API | [api.md](references/api.md) |
| Build an app via DashScope | Alibaba Cloud Model Studio | [api.md](references/api.md) |
| Use OpenRouter (free tier / routing) | OpenRouter endpoint | [api.md](references/api.md) |
| Function calling / tool use | Tool use API | [tool-use.md](references/tool-use.md) |
| Structured JSON outputs | `response_format` parameter | [tool-use.md](references/tool-use.md) |
| Run model locally | Ollama / vLLM / transformers | [local-deployment.md](references/local-deployment.md) |
| Agentic pipeline, long context | Qwen3.6 Plus, 1M context | [agentic.md](references/agentic.md) |
| Code generation / repair | Qwen2.5-Coder | [models.md](references/models.md) |
| Document analysis at scale | 1M context, OmniDocBench #1 | [agentic.md](references/agentic.md) |
| Migrate from OpenAI SDK | Drop-in base_url swap | [api.md](references/api.md) |
| Cost comparison vs Claude/GPT | Benchmark and pricing table | [models.md](references/models.md) |

---

## Qwen Overview

Qwen is Alibaba's open-weight model family. Models are available via:
- **DashScope** (Alibaba Cloud Model Studio) — official API, `dashscope.aliyuncs.com`
- **OpenRouter** — third-party routing, free tier available
- **HuggingFace** — weights for local deployment
- **Ollama / vLLM** — local inference

All cloud endpoints use **OpenAI-compatible API format** — drop-in for any OpenAI SDK/toolchain.

---

## Flagship: Qwen3.6 Plus (April 2026)

Alibaba's flagship agentic coding model. First model in history to exceed **1 trillion tokens in a single day** on OpenRouter (April 2026).

**Architecture:** Hybrid linear attention + sparse MoE. Linear attention for bulk context processing (avoids quadratic scaling), MoE activates only relevant experts per forward pass.

**Key specs:**
- Context: 1,000,000 tokens
- Max output: 65,536 tokens
- Inference speed: ~158 tokens/second (vs ~53 for Claude Opus 4.6)
- Always-on chain-of-thought (built-in, not toggled)
- OpenAI-compatible API

**Pricing:** $0.276/M input (<256K context) · $1.101/M (>256K, full 1M) · ~$1.10/M output

---

## Reference Index

| File | Contents |
|---|---|
| [models.md](references/models.md) | All Qwen model families, specs, pricing, benchmark table, selection guide |
| [api.md](references/api.md) | OpenAI-compatible API, DashScope, OpenRouter, SDK setup, streaming, auth |
| [tool-use.md](references/tool-use.md) | Function calling, parallel tools, structured JSON output, examples |
| [local-deployment.md](references/local-deployment.md) | Ollama, vLLM, HuggingFace transformers, GGUF/llama.cpp, quantization |
| [agentic.md](references/agentic.md) | Agentic architecture, 1M context patterns, CoT, orchestrator/subagent roles |
