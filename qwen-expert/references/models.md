# Qwen Model Reference

## Table of Contents
- [Qwen3 Series (Current)](#qwen3-series-current)
- [Qwen2.5 Series](#qwen25-series)
- [Qwen2.5-Coder](#qwen25-coder)
- [Qwen2.5-VL (Vision-Language)](#qwen25-vl-vision-language)
- [QwQ (Reasoning)](#qwq-reasoning)
- [Benchmark Comparison vs Frontier Models](#benchmark-comparison-vs-frontier-models)
- [Pricing Comparison](#pricing-comparison)
- [Model Selection Guide](#model-selection-guide)

---

## Qwen3 Series (Current)

### Commercial Models (DashScope / OpenRouter)

| Model | Context | Max Output | Input | Output | Notes |
|---|---|---|---|---|---|
| **qwen3.6-plus** | 1M tokens | 65,536 | $0.325/M (≤256K) · $1.30/M (>256K) | $1.95/M (≤256K) · $3.90/M (>256K) | Agentic coding flagship; April 2026 |
| **qwen3-max** | 262K tokens | — | $1.20/M (intl) | $3.90/M | Most capable commercial model |
| **qwen3.5-plus** | 1M tokens | 65,536 | $0.73/M | $1.56/M | Balanced perf/speed/cost |
| **qwen3.5-flash** | 1M tokens | — | $0.065–$0.10/M | $0.26–$0.40/M | Fastest, cheapest |
| **qwen3-coder-next** | 262K tokens | — | $0.15/M | $0.80/M | Best balance for coding tasks; Feb 2026 |
| **qwen3-coder-plus** | 262K tokens | — | higher | higher | Max quality coding |

### Qwen3.6 Plus — Architecture

| Spec | Value |
|---|---|
| Architecture | Hybrid linear attention + sparse MoE |
| Open-source variant | Qwen3.6-35B-A3B (35B total / 3B activated) |
| Context window | 262K native; 1,010K with YaRN RoPE scaling |
| MoE experts | 256 total; 8 routed + 1 shared active per token |
| Thinking mode | Hybrid (enable/disable per request via `enable_thinking`) |
| API compatibility | OpenAI-compatible |
| License (OSS) | Apache 2.0 |

**OpenRouter model string:** `qwen/qwen3.6-plus` (paid) · `qwen/qwen3.6-plus-preview:free` (free tier, when available)

**DashScope model string:** `qwen3.6-plus`

**Design goal:** Agentic coding — built as both orchestrator and subagent, not a chat model that happens to support tools.

---

## Open Source Models (Qwen3 + Qwen2.5)

All Apache 2.0 licensed, available on HuggingFace and ModelScope.

### Qwen3.6 Open-Weight

| Model | Total Params | Active | Context | Notes |
|---|---|---|---|---|
| Qwen3.6-35B-A3B | 35B | 3B | 262K / 1M (YaRN) | MoE; multimodal (text+image+video) |
| Qwen3.6-27B | 27B | 27B | 262K | Dense; strong reasoning |

### Qwen3.5 Open-Weight

| Model | Active Params | Context |
|---|---|---|
| Qwen3.5-397B-A17B | 17B | 262K |
| Qwen3.5-27B | 27B | 262K |
| Qwen3.5-9B | 9B | 262K |
| Qwen3.5-4B / 2B / 0.8B | — | 262K |

### Qwen2.5 Series (Stable, Widely Deployed)

| Model | Params | Context | Best for |
|---|---|---|---|
| Qwen2.5-72B-Instruct | 72B | 128K | Near-frontier quality, self-hosted |
| Qwen2.5-32B-Instruct | 32B | 128K | Strong balance of quality and speed |
| Qwen2.5-14B-Instruct | 14B | 128K | Mid-range capability, fast inference |
| Qwen2.5-7B-Instruct | 7B | 128K | Edge / embedded / low VRAM |
| Qwen2.5-3B-Instruct | 3B | 32K | On-device, very fast |
| Qwen2.5-1.5B-Instruct | 1.5B | 32K | Micro-deployments |
| Qwen2.5-0.5B-Instruct | 0.5B | 32K | Tiny embedded |

**Qwen2.5-72B** remains the reference local model for production-stable, near-frontier quality on commodity hardware. Qwen3.6-35B-A3B supersedes it for new deployments with larger VRAM budgets.

---

## Qwen2.5-Coder

Code-specialized fine-tune of Qwen2.5. Available in 0.5B, 1.5B, 3B, 7B, 14B, 32B sizes.

| Model | Context | Notes |
|---|---|---|
| Qwen2.5-Coder-32B-Instruct | 128K | Matches GPT-4o on code benchmarks; recommended |
| Qwen2.5-Coder-7B-Instruct | 128K | Fast local code assistant |

**When to use Qwen2.5-Coder vs Qwen3.6 Plus:**
- Use Qwen2.5-Coder for dedicated local code generation (completion, repair, review)
- Use Qwen3.6 Plus for cloud agentic coding with long context and tool use

**Strengths:** Code completion, multi-language support (92+ programming languages), fill-in-the-middle (FIM), repo-level understanding.

**Fill-in-the-middle format:**
```
<|fim_prefix|>{prefix}<|fim_suffix|>{suffix}<|fim_middle|>
```

---

## Qwen2.5-VL (Vision-Language)

Multimodal: text + images + video frames + documents.

| Model | Params | Notes |
|---|---|---|
| Qwen2.5-VL-72B-Instruct | 72B | Flagship vision model; strong on OCR and documents |
| Qwen2.5-VL-7B-Instruct | 7B | Fast local vision model |

**Capabilities:** Image understanding, document parsing, chart/diagram analysis, video understanding (up to 20 min), GUI grounding (screen parsing), multi-image reasoning.

**OmniDocBench:** Qwen3.6 Plus scores 91.2 (best among all models tested, April 2026).

---

## QwQ — Reasoning Model

Qwen's chain-of-thought reasoning model, comparable to DeepSeek-R1 and OpenAI o-series.

| Model | Params | Context |
|---|---|---|
| QwQ-32B | 32B | 128K |
| QwQ-32B-Preview | 32B | 32K |

**When to use:** Hard math, theorem proving, complex multi-step reasoning, scientific problems requiring deliberation.

**Note:** QwQ generates explicit reasoning traces (visible `<think>` tags). Slower than standard models but significantly better on hard reasoning tasks.

---

## Benchmark Comparison vs Frontier Models

April 2026, Qwen3.6 Plus vs direct competitors:

| Benchmark | Qwen3.6 Plus | Claude Opus 4.6 | GPT-5.4 |
|---|---|---|---|
| SWE-bench Verified | 78.8% | **80.8%** | ~69% |
| Terminal-Bench 2.0 | **61.6%** | 59.3% | ~52% |
| OmniDocBench v1.5 | **91.2** | ~86 | ~84 |
| RealWorldQA | **85.4** | ~82 | ~80 |
| Inference speed | **158 tok/s** | ~53 tok/s | ~76 tok/s |

**Summary:** Claude Opus 4.6 leads by 2pp on SWE-bench. Qwen3.6 Plus leads on everything else including terminal tasks, document processing, and speed.

The 2pp SWE-bench gap is meaningful for the hardest autonomous coding tasks (ambiguous bugs, novel implementations). For volume workloads, document processing, and multi-agent pipelines, Qwen3.6 Plus is the better economic choice.

---

## Pricing Comparison

| Model | Input | Output | Notes |
|---|---|---|---|
| Qwen3.6 Plus (≤256K) | $0.325/M | $1.95/M | DashScope intl; OpenRouter may vary |
| Qwen3.6 Plus (>256K) | $1.30/M | $3.90/M | Long-context tier |
| Qwen3-coder-next | $0.15/M | $0.80/M | Best coding cost/quality |
| Qwen3.5-flash | $0.065–$0.10/M | $0.26–$0.40/M | Cheapest flagship |
| Qwen3.5-0.8B (via provider) | $0.01/M | $0.05/M | Smallest |
| Claude Opus 4.6 | $5.00/M | $25.00/M | Best SWE-bench score |
| GPT-5.4 | ~$3.00/M | ~$15.00/M | — |

**Context caching:** Create cache at 125% of input price; hit at 10% of input price. Minimum 1,024 tokens; 5-minute validity (resets on hit).

**Scale economics (500K-token agentic loop, 10 iterations/task, 1000 tasks/day):**
- Claude Opus 4.6: ~$25,000/day
- Qwen3.6 Plus (long-context tier): ~$5,500/day

---

## Model Selection Guide

| Need | Model |
|---|---|
| Best agentic coding (cloud, long context) | Qwen3.6 Plus |
| Best local code generation (quality) | Qwen2.5-Coder-32B |
| Best local all-purpose (quality) | Qwen2.5-72B |
| Reasoning / hard math | QwQ-32B |
| Vision + document analysis | Qwen2.5-VL-72B |
| Fast local code assistant | Qwen2.5-Coder-7B |
| Edge / low VRAM | Qwen2.5-7B or Qwen2.5-3B |
| Cheapest capable cloud | Qwen3.6 Plus (free tier on OpenRouter when available) |
| Hardest software engineering (quality over cost) | Claude Opus 4.6 (still leads SWE-bench) |
