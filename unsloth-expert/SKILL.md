---
name: unsloth-expert
description: Expert knowledge for Unsloth LLM fine-tuning — FastLanguageModel API, LoRA/QLoRA config, SFT/DPO/GRPO training, GGUF export, Ollama deployment, and Unsloth Studio GUI. Use when helping users fine-tune, export, or deploy LLMs with Unsloth.
---

# Unsloth Expert

You are an expert on Unsloth, the library for fast and memory-efficient LLM fine-tuning. You have deep knowledge of the Python API, training workflows, export pipelines, and the Studio GUI.

## Core Knowledge Areas

- `FastLanguageModel.from_pretrained()` and `get_peft_model()` parameters
- LoRA vs QLoRA trade-offs and hyperparameter selection
- SFTTrainer, DPO, ORPO, and GRPO training setup
- Dataset formatting: Alpaca, ShareGPT, ChatML, vision/multimodal
- Chat template application and the `train_on_responses_only` pattern
- GGUF export with quantization options (q4_k_m, q8_0, etc.)
- Ollama Modelfile generation and deployment
- Unsloth Studio GUI installation, launch, and workflow
- Troubleshooting: OOM, wrong chat template, loss issues, label -100 errors

## Reference Files (load on demand)

- `references/overview-and-installation.md` — performance claims, hardware support, all install methods
- `references/core-api.md` — FastLanguageModel API, LoRA parameters, inference setup
- `references/supported-models.md` — model families, VRAM requirements, selection guide
- `references/dataset-formatting.md` — all dataset formats with code examples, chat templates
- `references/training-setup.md` — complete SFT, DPO, GRPO training code
- `references/export-and-deployment.md` — LoRA save, merge 16-bit, GGUF, Ollama, HF Hub
- `references/unsloth-studio-gui.md` — Studio install, launch, workflow, platform support
- `references/gotchas-and-troubleshooting.md` — common errors and fixes

## Quick-Start Pattern

When a user asks how to fine-tune a model, use this decision flow:

1. **Hardware check** — what GPU/VRAM do they have? → recommend model size
2. **Data check** — how many rows, what format? → recommend base vs instruct, format guidance
3. **Method check** — SFT (imitation), DPO (preference), or GRPO (RL/reasoning)?
4. **Load core-api.md** — provide FastLanguageModel code
5. **Load training-setup.md** — provide complete training code
6. **Load export-and-deployment.md** — show save/export for their target (Ollama, HF, vLLM)

## Key Facts to Always Know

- `use_gradient_checkpointing="unsloth"` saves an extra 30% VRAM vs `True`
- `lora_alpha = r` (conservative) or `lora_alpha = r * 2` (aggressive); always keep `alpha/r >= 1`
- `train_on_responses_only()` is almost always the right call for chat/instruct fine-tuning
- Chat template at inference **must** match training template — most common failure mode
- Training loss 0.5–1.0 is healthy; below 0.2 is overfitting territory
- `q4_k_m` is the recommended default GGUF quantization for Ollama
- GRPO needs at least 1.5B parameter model for thinking tokens; expect 300+ steps before reward improves
- `PatchDPOTrainer()` must be called **before** `from trl import DPOTrainer`
