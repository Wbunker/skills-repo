# DeepSeek Models Reference

## Table of Contents
- [Current API Models](#current-api-models)
- [Legacy Models (Deprecated)](#legacy-models-deprecated)
- [R1 Distill Variants (Local / Open Weights)](#r1-distill-variants-local--open-weights)
- [Model Capabilities Matrix](#model-capabilities-matrix)
- [Changelog Highlights](#changelog-highlights)
- [Via OpenRouter](#via-openrouter)
- [Via AWS Bedrock](#via-aws-bedrock)

---

## Current API Models

As of May 2026, DeepSeek's production API models:

### deepseek-v4-pro
- **Architecture:** MoE, 1.6T total params / 49B active per token
- **Context window:** 1,000,000 tokens (1M)
- **Max output:** 8,192 tokens
- **Thinking mode:** Enabled by default; can be disabled
- **Tool use:** Yes (including in thinking mode)
- **Pricing:** ~$0.55/M input (cache miss), ~$0.14/M (cache hit), ~$2.19/M output
  - 75% launch discount active until 2026-05-31
- **Best for:** Most complex reasoning, coding, analysis; when quality > cost

### deepseek-v4-flash
- **Architecture:** MoE, 284B total params / 13B active per token
- **Context window:** 1,000,000 tokens (1M)
- **Max output:** 8,192 tokens
- **Thinking mode:** Available but disabled by default
- **Tool use:** Yes
- **Pricing:** ~$0.27/M input (cache miss), ~$0.07/M (cache hit), ~$1.10/M output
- **Best for:** High-volume tasks, cost-sensitive applications, everyday coding/chat

---

## Legacy Models (Deprecated)

**Deprecation date: 2026-07-24**

These model names now map to V4 equivalents and will be removed on 2026-07-24. Migrate now.

| Legacy name | Maps to | Mode |
|-------------|---------|------|
| `deepseek-chat` | `deepseek-v4-flash` | Non-thinking |
| `deepseek-reasoner` | `deepseek-v4-flash` | Thinking |

Legacy specs (while still active):
- Context: 64K (significantly less than V4's 1M)
- Max output: 8K (chat) / 8K output + 32K CoT (reasoner)
- Pricing: same as V4-Flash above

---

## R1 Distill Variants (Local / Open Weights)

These are open-weight models released by DeepSeek for local deployment. They are **not available on the DeepSeek API** — use them via Ollama, LM Studio, llama.cpp, or vLLM.

### Qwen-base distills (recommended)
| Model | Params | Ollama tag | VRAM (Q4_K_M) |
|-------|--------|------------|---------------|
| DeepSeek-R1-Distill-Qwen-1.5B | 1.5B | `deepseek-r1:1.5b` | ~2GB |
| DeepSeek-R1-Distill-Qwen-7B | 7B | `deepseek-r1:7b` | ~5GB |
| DeepSeek-R1-Distill-Qwen-14B | 14B | `deepseek-r1:14b` | ~10GB |
| DeepSeek-R1-Distill-Qwen-32B | 32B | `deepseek-r1:32b` | ~20GB |

### Llama-base distills
| Model | Params | Ollama tag | VRAM (Q4_K_M) |
|-------|--------|------------|---------------|
| DeepSeek-R1-Distill-Llama-8B | 8B | `deepseek-r1:8b` | ~6GB |
| DeepSeek-R1-Distill-Llama-70B | 70B | `deepseek-r1:70b` | ~40GB |

### Full model (datacenter only)
| Model | Params | Notes |
|-------|--------|-------|
| DeepSeek-R1 | 671B MoE | ~400GB GPU memory; cluster deployment only |
| DeepSeek-V4-Pro | 1.6T/49B active | API only (cloud) |

**Hugging Face:** All open-weight models at `huggingface.co/deepseek-ai`

---

## Model Capabilities Matrix

| Model | Tool Use | Thinking | JSON Mode | Context | API / Local |
|-------|----------|----------|-----------|---------|-------------|
| deepseek-v4-pro | ✓ | ✓ (default on) | ✓ | 1M | API |
| deepseek-v4-flash | ✓ | ✓ (opt-in) | ✓ | 1M | API |
| deepseek-chat (legacy) | ✓ | ✗ | ✓ | 64K | API |
| deepseek-reasoner (legacy) | ✓* | ✓ | ✓ | 64K | API |
| R1-Distill-Qwen-32B | ✗† | Built-in | ✗ | ~128K | Local |
| R1-Distill-Llama-8B | ✗† | Built-in | ✗ | ~128K | Local |

*`deepseek-reasoner` got tool use in the R1-0528 upgrade (2025-05-28)  
†R1-Distill models output `<think>` tags natively but don't have structured API tool use

---

## Changelog Highlights

| Date | Event |
|------|-------|
| 2026-04-24 | **V4-Pro + V4-Flash released.** 1M context, MoE architecture. Legacy names deprecated. |
| 2025-12-01 | deepseek-chat + deepseek-reasoner upgraded to V3.2 |
| 2025-08-21 | V3.1 released — hybrid thinking/non-thinking, SWE-bench 66.0 |
| 2025-05-28 | deepseek-reasoner upgraded to R1-0528: AIME 70→87.5, added tool use + JSON |
| 2025-03-24 | deepseek-chat upgraded to V3-0324: MMLU-Pro 75.9→81.2 |
| 2025-01-20 | deepseek-reasoner (R1) introduced — first thinking-mode API model |
| 2024-12-26 | deepseek-chat upgraded to V3 |
| 2024-08-02 | Context caching on disk launched — major pricing reduction |
| 2024-07-25 | JSON mode, function calling, FIM completion introduced |

---

## Via OpenRouter

Access DeepSeek via OpenRouter for a single unified API key:

| OpenRouter model ID | Maps to |
|---------------------|---------|
| `deepseek/deepseek-chat` | deepseek-v4-flash |
| `deepseek/deepseek-r1` | Full R1 671B |
| `deepseek/deepseek-r1-distill-qwen-32b` | R1-Distill-Qwen-32B |
| `deepseek/deepseek-r1-distill-llama-70b` | R1-Distill-Llama-70B |
| `deepseek/deepseek-coder-v2` | Coder V2 |

```python
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="sk-or-v1-..."
)
response = client.chat.completions.create(
    model="deepseek/deepseek-chat",
    messages=[...]
)
```

---

## Via AWS Bedrock

DeepSeek models are available on Amazon Bedrock in select regions:

```python
import boto3, json

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

response = bedrock.invoke_model(
    modelId="deepseek.r1-v1:0",
    body=json.dumps({
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 512
    })
)
result = json.loads(response["body"].read())
```

Check `aws bedrock list-foundation-models --region us-east-1 | grep -i deepseek` for available model IDs in your region.
