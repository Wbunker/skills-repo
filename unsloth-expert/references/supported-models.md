# Unsloth Supported Models & VRAM Requirements

## Overview

Unsloth supports 500+ model architectures. The team works directly with model creators at Meta (Llama), Google DeepMind (Gemma), Qwen (Alibaba), Mistral AI, OpenAI (gpt-oss), and others to ensure optimized support.

All models from the `unsloth/` HuggingFace namespace are pre-validated and often pre-quantized.

---

## Major Model Families

### Llama (Meta)
| Model | VRAM (4-bit QLoRA) | VRAM (16-bit LoRA) | Notes |
|-------|-------------------|-------------------|-------|
| Llama 3.2 1B | ~4GB | ~8GB | Fastest; good for mobile/edge experiments |
| Llama 3.2 3B | ~6GB | ~12GB | Best small model balance |
| Llama 3.1 8B | ~8GB | ~20GB | Recommended starting point |
| Llama 3.3 70B | ~40GB | ~160GB | Best 70B as of Jan 2025 |
| Llama 4 Scout / Maverick | varies | varies | MoE architecture; new 2025 |

HF IDs: `unsloth/Meta-Llama-3.1-8B-Instruct`, `unsloth/Meta-Llama-3.1-70B-Instruct-bnb-4bit`

### Gemma (Google DeepMind)
| Model | VRAM (4-bit) | VRAM (8-bit) | Notes |
|-------|-------------|-------------|-------|
| Gemma-4-E2B | ~5GB | ~15GB | MoE 2B active params |
| Gemma-4-E4B | ~8GB | ~18GB | MoE 4B active params |
| Gemma-4-26B-A4B | ~18GB | ~28GB | Excellent quality |
| Gemma-4-31B | ~20GB | ~34GB | Largest Gemma |
| Gemma 3 2B | ~4GB | ~8GB | |
| Gemma 3 12B | ~12GB | ~24GB | |
| Gemma 3 27B | ~24GB | ~48GB | |

HF IDs: `unsloth/gemma-4-E2B-it`, `unsloth/gemma-3-12b-it-bnb-4bit`

### Qwen (Alibaba)
| Model | VRAM (4-bit) | Notes |
|-------|-------------|-------|
| Qwen3.5-0.8B | ~3GB | Ultra-small |
| Qwen3.5-2B | ~4GB | |
| Qwen3.5-4B | ~6GB | |
| Qwen3.5-9B | ~12GB | 12GB RAM minimum |
| Qwen3.5-27B | ~22GB | 22GB RAM/VRAM |
| Qwen3.5-35B-A3B | ~22GB | MoE, 3B active |
| Qwen3.5-72B | ~40GB | |
| Qwen3.5-122B-A10B | ~60GB | MoE, 10B active |
| Qwen2.5-Coder-7B | ~8GB | Code-specialized |
| Qwen2.5-Coder-32B | ~24GB | Strong coder |

HF IDs: `unsloth/Qwen3.5-9B`, `unsloth/Qwen2.5-Coder-32B-Instruct-bnb-4bit`

### Mistral / Mixtral
| Model | VRAM (4-bit) | Notes |
|-------|-------------|-------|
| Mistral 7B v0.3 | ~8GB | Classic dense model |
| Mistral Nemo 12B | ~12GB | Long context |
| Mistral 22B | ~18GB | |
| Mixtral 8x7B | ~28GB | MoE, 12B+ active |

HF IDs: `unsloth/mistral-7b-v0.3-bnb-4bit`, `unsloth/Mistral-Nemo-Base-2407`

### Phi (Microsoft)
| Model | VRAM (4-bit) | Notes |
|-------|-------------|-------|
| Phi-4 14B | ~14GB | Very strong reasoning |
| Phi-3.5 Mini 3.8B | ~6GB | |
| Phi-3 Medium 14B | ~14GB | |

HF IDs: `unsloth/Phi-4`, `unsloth/phi-4-bnb-4bit`

### DeepSeek
| Model | VRAM (4-bit) | Notes |
|-------|-------------|-------|
| DeepSeek-R1-Distill-Qwen-1.5B | ~4GB | Reasoning distilled |
| DeepSeek-R1-Distill-Qwen-7B | ~8GB | |
| DeepSeek-R1-Distill-Llama-8B | ~8GB | |
| DeepSeek-R1-Distill-Qwen-14B | ~14GB | |
| DeepSeek-R1 (full) | ~400GB | Multi-node |

HF IDs: `unsloth/DeepSeek-R1-Distill-Qwen-7B`, `unsloth/DeepSeek-R1-GGUF`

### Other Notable Models
| Model | Family | VRAM (4-bit) |
|-------|--------|-------------|
| GLM-5.1 | ZhipuAI | ~8GB+ |
| GPT-OSS (OpenAI open) | OpenAI | ~20GB |
| Kimi K2.5 | Moonshot | varies |
| NVIDIA Nemotron 3 | NVIDIA | ~8GB |
| Gemma 4 (2026 release) | Google | ~5GB+ |

---

## Quantization Format Comparison

| Format | Description | Speed | VRAM | Quality |
|--------|-------------|-------|------|---------|
| `load_in_4bit=True` | BitsAndBytes NF4 (QLoRA) | Fast | Minimal | ~= 16-bit |
| `load_in_4bit=False` | Full 16-bit LoRA | Faster | 4x more | Slightly better |
| Unsloth Dynamic 4-bit | Higher-accuracy 4-bit | Fast | Minimal | Better than BnB 4-bit |

---

## Model Selection Guidelines

**Under 300 rows dataset** → Use an instruct model  
**300–1000 rows** → Either instruct or base  
**1000+ rows** → Base model gives more customization

**Task-specific recommendations:**
- Code generation: Qwen2.5-Coder, DeepSeek-Coder
- Reasoning/math: DeepSeek-R1 distills, Phi-4, Qwen3.5
- Vision/multimodal: Llama 3.2 Vision, Gemma 3 (vision variants)
- Long context: Mistral Nemo, Llama 3.1 (supports 128K)
- Multilingual: Qwen2.5, Mistral

---

## Browsing Available Models

```python
# All unsloth-optimized models on HuggingFace:
# https://huggingface.co/unsloth

# Check what's loaded in Python:
from unsloth import FastLanguageModel
# Refer to: https://docs.unsloth.ai for current model list
```
