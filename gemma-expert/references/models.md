# Gemma Models Reference

## Gemma 4 (2026) — Current Generation

Gemma 4 uses Mixture-of-Experts (MoE) for the larger variants. MoE activates only a fraction of parameters per token, enabling large-model capability at small-model inference cost.

### Gemma 4 Variants

| Model | Params | Active | Context | VRAM (fp16) | Notes |
|-------|--------|--------|---------|-------------|-------|
| gemma-4-e2b | 2B | 2B | 32K | ~4 GB | Edge; audio + video-with-audio |
| gemma-4-e4b | 4B | 4B | 32K | ~8 GB | Edge; best multimodal for size |
| gemma-4-12b | 12B | 12B | 128K | ~24 GB | Dense; text + vision |
| gemma-4-26b-a3b | 26B | ~3B | 260K | ~18 GB | MoE; consumer GPU friendly |
| gemma-4-26b-a4b | 26B | ~4B | 260K | ~18 GB | MoE; best text/code quality |
| gemma-4-31b | 31B | 31B | 128K | ~62 GB | Dense; top benchmark scores |

**MoE note**: Despite 26B total parameters, only ~3.8B activate per token. The full 26B must still be loaded into VRAM — it is not streamed lazily.

### Gemma 4 Benchmark Highlights (26B A4B)

| Benchmark | Score | Notes |
|-----------|-------|-------|
| MMLU Pro | ~72% | Strong general knowledge |
| HumanEval | ~85% | Code generation |
| MATH | ~70% | Mathematical reasoning |
| MMMU Pro (Vision) | 73.8% | Multimodal understanding |
| Codeforces ELO | 1718 | Competitive programming |
| LMArena | ~1441 | Human preference |
| MRCR v2 8-needle 128K | 44.1% | Long-context retrieval |

---

## Gemma 3 (2025)

Dense architecture, text-only (1B/4B/12B) and multimodal (27B). Widely supported by all inference frameworks.

| Model | Params | Context | VRAM (fp16) |
|-------|--------|---------|-------------|
| gemma-3-1b | 1B | 32K | ~2 GB |
| gemma-3-4b | 4B | 128K | ~8 GB |
| gemma-3-12b | 12B | 128K | ~24 GB |
| gemma-3-27b | 27B | 128K | ~54 GB |

Gemma 3 27B supports image input and performs well on long-context tasks. Recommended for teams that need maximum framework compatibility.

---

## Gemma 2 (2024)

| Model | Params | Context |
|-------|--------|---------|
| gemma-2-2b | 2B | 8K |
| gemma-2-9b | 9B | 8K |
| gemma-2-27b | 27B | 8K |

Shorter context than Gemma 3/4. Useful for embedded or legacy deployments.

---

## Model Selection Guide

**For local consumer GPU (RTX 3090, 24 GB VRAM):**
- Best quality: `gemma-4-26b-a4b` (Q3_K_M quant, ~18 GB)
- Faster iteration: `gemma-4-12b` or `gemma-3-12b`

**For 16 GB VRAM (RTX 4080, etc.):**
- `gemma-4-12b` fits cleanly
- `gemma-4-26b-a3b` with partial CPU offload (MoE layers)

**For on-device / mobile / edge:**
- `gemma-4-e2b` or `gemma-4-e4b` — designed for LiteRT-LM and on-device inference
- E4B is the better quality choice if size allows

**For API use (no local GPU):**
- `gemma-4-26b-a4b` via Google AI Studio (free tier available)
- `gemma-4-31b` via Vertex AI for highest benchmark performance

**For multimodal tasks:**
- Images + video: `gemma-4-26b-a4b` or `gemma-4-12b`
- Audio + video-with-audio: `gemma-4-e2b` or `gemma-4-e4b`
- Vision tasks: E4B underperforms relative to 26B for complex visual reasoning

**For code generation:**
- `gemma-4-26b-a4b` (Codeforces ELO 1718)
- `gemma-4-31b` for highest ceiling (ELO 2150)

---

## Accessing Models

- **HuggingFace**: `google/gemma-4-27b-it`, `google/gemma-3-27b-it`, etc.
- **Ollama**: `gemma4`, `gemma3` (tag names vary by version)
- **Google AI Studio**: `gemma-4-26b-a4b` — free API access
- **Vertex AI**: Full model catalog via `google/gemma-4-*`
- **Kaggle Models**: Direct download with Kaggle credentials
