# Local Inference with Gemma

## Ollama (Recommended for Most Users)

Ollama is the easiest path to running Gemma locally.

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Run Gemma 4 26B (MoE, recommended for RTX 3090)
ollama run gemma4:26b-a3b-q3_K_M

# Smaller options
ollama run gemma4:12b
ollama run gemma3:27b
```

### Recommended Parameters (Gemma 4 26B)

```json
{
  "temperature": 1.0,
  "top_k": 40,
  "num_ctx": 131072,
  "flash_attention": true,
  "kv_cache_type": "q8_0"
}
```

Set via Modelfile or API parameter. Temperature 1.0 is **not optional** — default temperature degrades output quality noticeably for Gemma 4.

### Ollama API

```python
import ollama

response = ollama.chat(
    model="gemma4:26b-a3b-q3_K_M",
    messages=[{"role": "user", "content": "Hello"}],
    options={"temperature": 1.0, "top_k": 40}
)
print(response["message"]["content"])
```

### Inference Speed Reference (RTX 4090, 24 GB VRAM)

| Model | Task Type | Response Time |
|-------|-----------|---------------|
| gemma-4-31b | Typical coding prompts | 8–15 seconds |
| gemma-4-26b-a4b (Q3_K_M) | Typical coding prompts | ~5–10 seconds |

Fast enough for development flow. API models (Claude, GPT-5.4) are faster due to server-side batching, but local latency is acceptable for interactive coding work.

### Known Ollama Bug

`think=false` combined with structured output (`format`) is an open bug in Ollama — they conflict. Use one or the other, not both.

---

## llama.cpp

### Setup

```bash
git clone https://github.com/ggerganov/llama.cpp && cd llama.cpp
cmake -B build -DGGML_CUDA=ON && cmake --build build --config Release -j$(nproc)
```

### Download GGUF

```bash
# From HuggingFace (Unsloth provides best quantizations)
huggingface-cli download unsloth/gemma-4-26b-a4b-GGUF \
  --include "gemma-4-26b-a4b-Q3_K_M.gguf"
```

### Run

```bash
./build/bin/llama-server \
  -m gemma-4-26b-a4b-Q3_K_M.gguf \
  --n-gpu-layers 99 \
  --flash-attn \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --ctx-size 131072 \
  --jinja                    # REQUIRED for tool calling
```

**Critical**: Always use `--jinja` if doing any tool calling or agentic work. Without it, tool calls loop or produce malformed output. See [tool-calling.md](tool-calling.md).

**CUDA version**: Use CUDA 13.0, not 13.2. CUDA 13.2 has a bug causing corrupted GGUF outputs (random mid-generation typos, garbled tokens).

### Quantization Guide

| Quant | Size (26B) | Quality | VRAM Needed |
|-------|-----------|---------|-------------|
| Q2_K | ~10 GB | Degraded | ~12 GB |
| Q3_K_M | ~13 GB | Good | ~16 GB |
| Q4_K_M | ~17 GB | Very good | ~20 GB |
| Q5_K_M | ~21 GB | Excellent | ~24 GB |
| Q8_0 | ~28 GB | Near lossless | ~32 GB |

**RTX 3090 sweet spot**: Q3_K_M (fits in 24 GB VRAM with room for KV cache).

The Unsloth Q3_K_M quant is the community-validated choice for quality-at-size. Unsloth applies additional optimizations not present in generic GGUF exports.

---

## LM Studio

1. Download from lmstudio.ai
2. Search for `gemma-4` in the model browser
3. Select an Unsloth GGUF variant (Q3_K_M for 24 GB VRAM)
4. Configure in Advanced: temperature 1.0, top-k 40, Flash Attention on
5. For tool calling: enable "Structured Output / Tool Use" and set jinja template mode

---

## vLLM

```bash
pip install vllm
vllm serve google/gemma-4-27b-it --dtype bfloat16
```

**Note**: vLLM falls back from FlashAttention for Gemma 4 due to heterogeneous attention head dimensions in the MoE architecture. This causes a throughput penalty vs. llama.cpp. Monitor GPU utilization; if below 80%, check the vLLM log for attention fallback warnings.

---

## On-Device / Android Deployment

Google provides **LiteRT-LM** for on-device inference using Gemma 4 E2B/E4B.

### Memory Targets

| Variant | Min RAM | Quantization |
|---------|---------|-------------|
| E2B | ~1.5 GB | 4-bit (INT4) |
| E4B | ~3 GB | 4-bit (INT4) |

### Performance (Gemma 4 E2B)

| Platform | Prefill (tok/s) | Decode (tok/s) |
|----------|-----------------|----------------|
| Raspberry Pi 5 (CPU) | 133 | 7.6 |
| Qualcomm Dragonwing IQ8 (NPU) | 3,700 | 31 |
| Android (AICore) | varies | 15-30 |

### Android Integration

```kotlin
// MediaPipe Tasks (LLM Inference API)
val options = LlmInferenceOptions.builder()
    .setModelPath("/data/local/tmp/gemma-e2b.bin")
    .setMaxTokens(1024)
    .build()
val llm = LlmInference.createFromOptions(context, options)
val result = llm.generateResponse("Your prompt here")
```

Google AI Edge Gallery provides an "Agent Skills" framework for building on-device agentic workflows (knowledge augmentation, content transformation, multi-step pipelines).

---

## CPU-Only Inference

Gemma 3 4B and smaller run acceptably on modern CPUs with llama.cpp:

```bash
./build/bin/llama-server \
  -m gemma-3-4b-Q4_K_M.gguf \
  --n-gpu-layers 0 \
  --threads $(nproc)
```

Expect 3-8 tokens/sec on a modern 8-core CPU. Not recommended for production, but viable for experimentation.
