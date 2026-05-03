# DeepSeek Local Inference

Run DeepSeek models on your own hardware — private, offline, no API costs.

## Table of Contents
- [Model Selection for Local](#model-selection-for-local)
- [Hardware Requirements](#hardware-requirements)
- [Ollama](#ollama)
- [LM Studio](#lm-studio)
- [llama.cpp (direct)](#llamacpp-direct)
- [vLLM (production serving)](#vllm-production-serving)
- [Quantization Guide](#quantization-guide)
- [Gotchas](#gotchas)

---

## Model Selection for Local

The full DeepSeek-V4/R1 671B MoE model requires extreme hardware (multiple H100s). For local use, use the **R1-Distill** variants — smaller models trained by distilling R1's reasoning capability into Qwen and Llama base models.

| Model | Params | VRAM (Q4_K_M) | Quality |
|-------|--------|---------------|---------|
| R1-Distill-Qwen-1.5B | 1.5B | ~2GB | Basic reasoning, very fast |
| R1-Distill-Qwen-7B | 7B | ~5GB | Good reasoning for size |
| R1-Distill-Llama-8B | 8B | ~6GB | Good reasoning, Llama base |
| R1-Distill-Qwen-14B | 14B | ~10GB | Strong reasoning, recommended |
| R1-Distill-Qwen-32B | 32B | ~20GB | Near R1 quality, best local option |
| R1-Distill-Llama-70B | 70B | ~40GB | Excellent, needs multi-GPU |
| DeepSeek-R1 (full) | 671B | ~400GB | Full quality, datacenter only |

**Recommended for most developers:** R1-Distill-Qwen-32B at Q4_K_M — fits a single RTX 3090/4090 (24GB), near full R1 quality.

---

## Hardware Requirements

| Model | Min VRAM | Recommended GPU | Speed (tokens/s) |
|-------|---------|----------------|-----------------|
| 7B Q4_K_M | 6GB | RTX 3060 12GB | ~40–60 |
| 14B Q4_K_M | 10GB | RTX 3080 10GB | ~30–45 |
| 32B Q4_K_M | 20GB | RTX 3090 / 4090 | ~28–45 |
| 70B Q4_K_M | 40GB | 2× A100 40GB | ~15–25 |

**Apple Silicon:** Metal acceleration via llama.cpp/Ollama works well. M2 Max (32GB) handles 32B comfortably; M3 Ultra (96GB) runs 70B.

**CPU-only fallback:** Any model runs on CPU but at 2–5 tokens/s. Only practical for 7B or smaller.

---

## Ollama

Simplest option — handles download, quantization choice, and serving in one command.

**Install:**
```bash
curl -fsSL https://ollama.com/install.sh | sh   # Linux/Mac
# Windows: download from ollama.com
```

**Run a model:**
```bash
ollama run deepseek-r1:7b     # ~4.7GB download, Q4_K_M default
ollama run deepseek-r1:14b    # ~9GB
ollama run deepseek-r1:32b    # ~20GB
ollama run deepseek-r1:70b    # ~40GB
```

**List available tags:**
```bash
ollama list
# or visit: https://ollama.com/library/deepseek-r1
```

**Pull without running:**
```bash
ollama pull deepseek-r1:32b
```

**Use OpenAI-compatible API (Ollama serves on port 11434):**
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"   # required but ignored
)

response = client.chat.completions.create(
    model="deepseek-r1:32b",
    messages=[{"role": "user", "content": "Solve: x^2 + 5x + 6 = 0"}]
)
print(response.choices[0].message.content)
```

**Ollama environment variables:**
```bash
OLLAMA_HOST=0.0.0.0:11434      # Listen on all interfaces (for network access)
OLLAMA_NUM_PARALLEL=2           # Concurrent requests
OLLAMA_MAX_LOADED_MODELS=1      # Models kept in memory
```

**Modelfile for custom system prompt:**
```dockerfile
FROM deepseek-r1:32b
SYSTEM "You are a coding assistant. Think step by step."
PARAMETER temperature 0.6
```
```bash
ollama create my-deepseek -f Modelfile
ollama run my-deepseek
```

---

## LM Studio

Desktop GUI — best for non-developers or anyone who wants a ChatGPT-like interface locally.

1. Download from https://lmstudio.ai
2. Open LM Studio → Search "deepseek-r1" in the model hub
3. Download your preferred variant (shows file size and hardware compatibility)
4. Chat interface works immediately

**Local server (OpenAI-compatible):**
- Start server: LM Studio → Local Server tab → Start Server (port 1234)
```python
client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)
```

**Recommended quantization in LM Studio:** Q4_K_M for best quality/size tradeoff.

---

## llama.cpp (direct)

Lowest-level option — maximum control over compilation flags and hardware-specific optimizations.

**Build:**
```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build -DGGML_CUDA=ON    # for NVIDIA GPU
cmake --build build --config Release -j

# For Apple Silicon:
cmake -B build -DGGML_METAL=ON
cmake --build build --config Release -j
```

**Download GGUF model:**
```bash
# From Hugging Face (use huggingface-cli or wget)
huggingface-cli download \
  bartowski/DeepSeek-R1-Distill-Qwen-32B-GGUF \
  DeepSeek-R1-Distill-Qwen-32B-Q4_K_M.gguf \
  --local-dir ./models
```

**Run inference:**
```bash
./build/bin/llama-cli \
  -m ./models/DeepSeek-R1-Distill-Qwen-32B-Q4_K_M.gguf \
  -p "What is the derivative of x^3?" \
  -n 512 \
  --gpu-layers 99   # offload all layers to GPU
```

**Run as server:**
```bash
./build/bin/llama-server \
  -m ./models/DeepSeek-R1-Distill-Qwen-32B-Q4_K_M.gguf \
  --host 0.0.0.0 --port 8080 \
  --gpu-layers 99 \
  --ctx-size 8192
```
Server exposes OpenAI-compatible API at `http://localhost:8080`.

---

## vLLM (production serving)

Best for high-throughput serving, multiple concurrent users, or production deployments. Requires NVIDIA GPU with CUDA.

**Install:**
```bash
pip install vllm
```

**Serve a model:**
```bash
vllm serve deepseek-ai/DeepSeek-R1-Distill-Qwen-32B \
  --dtype bfloat16 \
  --tensor-parallel-size 1 \
  --max-model-len 8192 \
  --port 8000
```

**Docker:**
```bash
docker run --gpus all \
  -p 8000:8000 \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  vllm/vllm-openai:latest \
  --model deepseek-ai/DeepSeek-R1-Distill-Qwen-32B \
  --dtype bfloat16
```

**Client (same OpenAI SDK):**
```python
client = OpenAI(base_url="http://localhost:8000/v1", api_key="token")
```

---

## Quantization Guide

| Format | Size vs BF16 | Quality loss | Best for |
|--------|-------------|-------------|----------|
| BF16 / FP16 | 100% | None | GPU with enough VRAM |
| Q8_0 | 50% | ~0% | Highest quality quantized |
| Q4_K_M | 25% | <1% on STEM | **Recommended** — best size/quality |
| Q4_K_S | 23% | Slightly worse than K_M | Space-constrained |
| Q3_K_M | 18% | Noticeable on complex tasks | Very low VRAM only |
| Q2_K | 12% | Significant | Last resort |

**Rule of thumb:** Q4_K_M is the practical default. The quality difference between BF16 and Q4_K_M is under 1% on STEM benchmarks for the Qwen-32B distill.

---

## Gotchas

- R1-Distill models wrap their reasoning in `<think>...</think>` tags in the output — parse or strip these if you only want the final answer.
- Ollama's default context window is 2048 tokens. Override with `OLLAMA_NUM_CTX=8192` or set `num_ctx` in a Modelfile.
- vLLM requires at least 1 NVIDIA GPU with CUDA. It does not support Apple Silicon or AMD GPUs natively.
- The full DeepSeek-R1 671B requires ~400GB of GPU memory — only feasible on clusters of H100s/A100s. Don't attempt on consumer hardware.
- llama.cpp's `--gpu-layers 99` offloads all layers; reduce this number if you're getting CUDA out-of-memory errors.
- R1-Distill models are reasoning-optimized. They may be verbose on simple tasks. For pure instruction-following, V4-Flash via API is better.
- When using Ollama as an OpenAI-compatible server, the `model` parameter must match the Ollama model name exactly (e.g., `deepseek-r1:32b`, not `deepseek-r1`).
