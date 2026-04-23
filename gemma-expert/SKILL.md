---
name: gemma-expert
description: >
  Expert guidance for working with Google's Gemma open-weight model family (Gemma 1, 2, 3, 4).
  Covers model selection, local inference, Google AI Studio API, Vertex AI, fine-tuning, multimodal
  capabilities, tool/function calling, and agentic deployment. Use when the user asks about:
  running Gemma locally (Ollama, llama.cpp, LM Studio), using Gemma via API, choosing between
  Gemma variants, fine-tuning Gemma with LoRA/Unsloth, Gemma vision/audio tasks, configuring
  quantization, debugging tool-calling issues, or building on-device/edge AI applications with Gemma.
---

# Gemma Expert

Gemma is Google's family of open-weight models ranging from 1B edge models to 27B/31B frontier models. Gemma 4 introduced a Mixture-of-Experts (MoE) architecture — the 26B-A4B variant activates only ~3.8B parameters per token, making it run on consumer GPUs while delivering large-model reasoning depth.

## Decision Matrix

| Goal | Approach | Reference |
|------|----------|-----------|
| Choose the right Gemma model | Compare variants by task, VRAM, context | [models.md](references/models.md) |
| Run Gemma locally (Ollama) | `ollama run gemma4:…` with config flags | [local-inference.md](references/local-inference.md) |
| Run Gemma locally (llama.cpp) | GGUF quants, --jinja flag for tools | [local-inference.md](references/local-inference.md) |
| Call Gemma via API | Google AI Studio or Vertex AI | [api.md](references/api.md) |
| Add tool/function calling | Chat template + --jinja flag | [tool-calling.md](references/tool-calling.md) |
| Use vision / image input | Gemma 4 multimodal variants | [multimodal.md](references/multimodal.md) |
| Fine-tune Gemma | LoRA/QLoRA, Unsloth, HuggingFace | [fine-tuning.md](references/fine-tuning.md) |
| Deploy on-device / Android | LiteRT-LM, E2B, MediaPipe | [local-inference.md](references/local-inference.md) |
| Debug inference issues | CUDA bugs, looping, thinking tags | [gotchas.md](references/gotchas.md) |
| Build RAG with Gemma | Context override, prompt strategy | [gotchas.md](references/gotchas.md) |

## Model Families

Gemma 4 (2026) is the current generation with MoE architecture and multimodal support. Gemma 3 (2025) remains widely used for text-only tasks. See [models.md](references/models.md) for full variant comparison including context lengths, VRAM requirements, and benchmark scores.

## Local Inference

The recommended local setup for Gemma 4 26B on an RTX 3090:

```bash
ollama run gemma4:26b-a3b-q3_K_M
```

Key parameters: `temperature: 1.0`, `top_k: 40`, `flash_attention: enabled`, `kv_cache_quant: q8_0`. See [local-inference.md](references/local-inference.md) for full setup including llama.cpp, LM Studio, and on-device deployment.

## Tool Calling

Gemma 4 supports function calling but requires correct configuration. In llama.cpp, the `--jinja` flag is **required** for tool-calling behavior. Without it, tool calls loop or malform. See [tool-calling.md](references/tool-calling.md) for prompt format and agentic patterns.

## Multimodal

Gemma 4 supports image, audio, and video inputs — with variant-specific limits. The 26B A4B handles images and video; E2B/E4B handle audio and video-with-audio. See [multimodal.md](references/multimodal.md).

## Fine-Tuning

LoRA fine-tuning works well for text-only Gemma variants. For MoE (26B A4B), use 16-bit LoRA — QLoRA + MoE interact poorly. Unsloth provides optimized fine-tuning with significant memory savings. See [fine-tuning.md](references/fine-tuning.md).

## Gotchas

Critical issues to check before building: [gotchas.md](references/gotchas.md) covers CUDA 13.2 bugs, tool-calling loops, thinking tag leakage, RAG context override, and vLLM performance penalties.

## Reference Index

| File | Contents |
|------|----------|
| [models.md](references/models.md) | All Gemma variants, VRAM requirements, context lengths, benchmarks |
| [local-inference.md](references/local-inference.md) | Ollama, llama.cpp, LM Studio, quantization, on-device/Android |
| [api.md](references/api.md) | Google AI Studio API, Vertex AI, Python SDK, streaming |
| [tool-calling.md](references/tool-calling.md) | Function calling format, --jinja flag, agentic patterns |
| [multimodal.md](references/multimodal.md) | Vision, audio, video — capabilities and limits per variant |
| [fine-tuning.md](references/fine-tuning.md) | LoRA, QLoRA, Unsloth, HuggingFace Trainer, MoE caveats |
| [gotchas.md](references/gotchas.md) | Known bugs, CUDA issues, RAG caveats, workarounds |
