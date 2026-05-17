# MiniMax Models Reference

## Current-Generation Text Models (direct API)

| Model ID | Speed | Context | Max Output | Notes |
|---|---|---|---|---|
| `MiniMax-M2.7` | ~60 tps | 204,800 | — | Flagship; #1 Artificial Analysis Intelligence Index; agent harness |
| `MiniMax-M2.7-highspeed` | ~100 tps | 204,800 | — | Same capability, faster, 2× cost |
| `MiniMax-M2.5` | ~60 tps | 204,800 | — | SWE-bench 80.2%; SOTA coding/agent |
| `MiniMax-M2.5-highspeed` | ~100 tps | 204,800 | — | Faster variant |
| `MiniMax-M2.1` | ~60 tps | 204,800 | — | 230B params / 10B active (MoE) |
| `MiniMax-M2.1-highspeed` | ~100 tps | 204,800 | — | Faster variant |
| `MiniMax-M2` | — | 200,000 | 128,000 | Agentic, function calling |
| `MiniMax-M2-her` | — | 204,800 | — | Roleplay/dialogue specialist |

## On OpenRouter

OpenRouter uses versioned model IDs in `provider/model` format:

| OpenRouter ID | Maps to | Context | Input $/M | Output $/M |
|---|---|---|---|---|
| `minimax/minimax-m2.7-20260318` | M2.7 | 204,800 | $0.30 | $1.20 |
| `minimax/minimax-m2.5-20260211` | M2.5 | 204,800 | $0.30 | $1.20 |

## Legacy / Extended-Context Models (via OpenRouter)

These older models support 1M token context but are not on the current direct API:

| OpenRouter ID | Context | Input $/M | Output $/M | Notes |
|---|---|---|---|---|
| `minimax/minimax-m1` | 1,000,000 | $0.40 | $2.20 | 456B/45.9B active, lightning attention |
| `minimax/minimax-01` | 1,000,192 | $0.20 | $1.10 | MoE + hybrid attention, image understanding |

## Benchmarks (M2.5 and M2.7)

| Benchmark | M2.5 | M2.7 |
|---|---|---|
| SWE-bench Verified | 80.2% (also 78%) | — |
| SWE-bench Pro | 85% | 56.2% |
| Multi-SWE-Bench | 51.3% | — |
| BrowseComp | 76.3% | — |
| Terminal Bench 2 | — | 57.0% |
| GDPval-AA ELO | — | 1495 |
| Artificial Analysis Index | — | #1 (136 models) |

Marketing claim: M2.5 output at "1/10 to 1/20" the cost of comparable Western models.

## Model Selection Guide

| Use case | Recommended |
|---|---|
| General assistant / coding | `MiniMax-M2.7` |
| Complex code review / agentic tasks | `MiniMax-M2.5` |
| Low-latency applications | `MiniMax-M2.7-highspeed` or `MiniMax-M2.5-highspeed` |
| Character AI / roleplay | `MiniMax-M2-her` |
| Need 1M context window | `minimax/minimax-m1` via OpenRouter |
| Budget-conscious, good quality | `minimax/minimax-01` via OpenRouter |

## Architecture Notes

- M2.1 is explicitly MoE: 230B total parameters, 10B activated per token
- M2.7 includes an "agent harness" capability for autonomous task execution
- All current-gen models support: streaming, tool use, function calling, reasoning/CoT
- Max CoT (chain-of-thought) budget: 128K tokens
- Token counting: ~1,600 Chinese characters per 1,000 tokens
