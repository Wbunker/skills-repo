# Kimi Models Reference

## Active Models

| Model ID | Context | Modalities | Thinking | Notes |
|---|---|---|---|---|
| `kimi-k2.6` | 256k | Text + Vision + Video | On by default; can disable | Flagship. Best coding + agents. |
| `kimi-k2.5` | 256k | Text + Vision | On by default; can disable | Stable predecessor to k2.6 |
| `kimi-k2-0905-preview` | 256k | Text + Vision | Supported | Enhanced front-end code |
| `kimi-k2-0711-preview` | 128k | Text | Supported | Older K2 variant |
| `kimi-k2-turbo-preview` | 256k | Text + Vision | Supported | High-speed; up to 100 tok/s |
| `kimi-k2-thinking` | 256k | Text + Vision | Always on | Dedicated thinking model |
| `kimi-k2-thinking-turbo` | 256k | Text + Vision | Always on | High-speed thinking |
| `moonshot-v1-8k` | 8k | Text | No | Legacy; short text |
| `moonshot-v1-32k` | 32k | Text | No | Legacy; medium text |
| `moonshot-v1-128k` | 128k | Text | No | Legacy; long text |
| `moonshot-v1-8k-vision-preview` | 8k | Text + Vision | No | Legacy + vision |
| `moonshot-v1-32k-vision-preview` | 32k | Text + Vision | No | Legacy + vision |
| `moonshot-v1-128k-vision-preview` | 128k | Text + Vision | No | Legacy + vision |

**Discontinued:** `kimi-latest` (Jan 28, 2026), `kimi-thinking-preview` (Nov 11, 2025), K2-series preview models (May 25, 2026).

---

## Pricing

### kimi-k2.6
| Billing item | Price |
|---|---|
| Input — cache hit | $0.16 / MTok |
| Input — cache miss | $0.95 / MTok |
| Output | $4.00 / MTok |

Context: 256k. Automatic context caching. Supports ToolCalls, JSON mode, thinking, multimodal.

### kimi-k2.5
| Billing item | Price |
|---|---|
| Input — cache hit | $0.10 / MTok |
| Input — cache miss | $0.60 / MTok |
| Output | $3.00 / MTok |

### kimi-k2 variants (preview — discontinuing May 25, 2026)
| Model | Input (cache miss) | Output | Context |
|---|---|---|---|
| kimi-k2-0905-preview | $0.60 / MTok | $2.50 / MTok | 256k |
| kimi-k2-0711-preview | $0.60 / MTok | $2.50 / MTok | 128k |
| kimi-k2-turbo-preview | $1.15 / MTok | $8.00 / MTok | 256k |
| kimi-k2-thinking | $0.60 / MTok | $2.50 / MTok | 256k |
| kimi-k2-thinking-turbo | $1.15 / MTok | $8.00 / MTok | 256k |

Cache hit rate for all K2 variants: $0.15 / MTok.

### moonshot-v1 series
| Model | Input | Output | Context |
|---|---|---|---|
| moonshot-v1-8k | $0.20 / MTok | $2.00 / MTok | 8k |
| moonshot-v1-32k | $1.00 / MTok | $3.00 / MTok | 32k |
| moonshot-v1-128k | $2.00 / MTok | $5.00 / MTok | 128k |
| moonshot-v1-{8k,32k,128k}-vision-preview | same as above | same | same |

### Batch API discount
40% off inference vs real-time API. Supported models: kimi-k2.6 and kimi-k2.5 only.

### Tool surcharges
- `$web_search`: $0.005 per successful tool call (when `finish_reason=tool_calls`). No charge on `finish_reason=stop`.
- All other official tools: free.

Prices exclude taxes. File upload/storage is temporarily free.

---

## Model Selection Guide

| Use Case | Recommended |
|---|---|
| Frontier coding / agents | `kimi-k2.6` |
| Cost-optimized coding / agents | `kimi-k2.5` |
| Deep reasoning, complex math | `kimi-k2.6` (thinking on) or `kimi-k2-thinking` |
| High throughput / speed | `kimi-k2-turbo-preview` |
| Legacy integrations needing 128k+ | `moonshot-v1-128k` |
| Vision + legacy context | `moonshot-v1-128k-vision-preview` |
| Async bulk jobs (cost savings) | `kimi-k2.6` via Batch API |

---

## Context Window in Characters (approximate)

| Model | Chinese chars |
|---|---|
| moonshot-v1-8k | ~15,000 |
| moonshot-v1-32k | ~60,000 |
| moonshot-v1-128k | ~200,000 |
| kimi-k2.6 / k2.5 | ~400,000 |

---

## K2.6 Benchmark Highlights (vs closed frontier, April 2026)

**Architecture:** 1 trillion parameter Mixture-of-Experts (MoE), 32B active parameters, 256K context window, native multimodal (text + images).

| Benchmark | K2.6 | GPT-5.4 | Opus 4.6 | Notes |
|---|---|---|---|---|
| HLE with Tools | **54.0** | 52.1 | 53.0 | Complex reasoning + tool use |
| SWE-Bench Pro | **58.6** | 57.7 | 53.4 | Real-world software engineering |
| SWE-Bench Multilingual | 76.7 | — | **77.8** | Python, JS, Go, etc. |
| Terminal-Bench 2.0 | **66.7** | 65.4 | 65.4 | Terminal-based coding (core Claude Code use) |
| Toolathlon | 50.0 | **54.6** | 47.2 | Tool calling reliability |
| DeepSearchQA (F1) | **+14 pts** over GPT-5.4 | baseline | — | Research/web search |
| MATH Olympiad | behind | — | — | Hard reasoning |
| BabyVision | −12 pts vs Gemini 3.1 Pro | — | — | Vision gap |

**Behind closed frontier:** MATH Olympiad, GPQA reasoning, BabyVision, APEX-Agents, Toolathlon vs GPT-5.4.

Agent Swarm scales to 300 concurrent sub-agents executing up to 4,000 coordinated steps simultaneously. Demonstrated 13-hour autonomous coding sessions.

**K2.5 Agent Swarm (for comparison):** Up to 100 sub-agents, 1,500 coordinated steps. Delivers ~4.5x speedup over single-agent execution on parallel-decomposable tasks.

**K2.6 improvements over K2.5:**
- **Reasoning depth:** Extends reasoning chain before committing — reduces shallow heuristic collapse on multi-step problems
- **Agent planning:** Orchestrator routing more reliably keeps swarm active instead of falling back to single-agent mode
- **Full-stack code quality:** Explicit frontend pattern training; React component structure notably improved
- **Complex debugging:** Dedicated debugging sub-agent routing isolates blast radius before attempting cross-file fixes
