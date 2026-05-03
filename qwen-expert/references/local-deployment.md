# Qwen Local Deployment

## Table of Contents
- [Ollama](#ollama)
- [vLLM](#vllm)
- [HuggingFace Transformers](#huggingface-transformers)
- [llama.cpp / GGUF](#llamacpp--gguf)
- [Hardware Requirements](#hardware-requirements)
- [Gotchas](#gotchas)

---

## Ollama

Simplest path to local Qwen. OpenAI-compatible server at `localhost:11434`.

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Pull and run a model
ollama pull qwen2.5-coder:32b
ollama run qwen2.5-coder:32b

# Available Qwen models on Ollama
ollama pull qwen2.5:72b          # General purpose
ollama pull qwen2.5:7b           # Smaller, faster
ollama pull qwen2.5-coder:32b    # Code-specialized (recommended)
ollama pull qwen2.5-coder:7b     # Fast code assistant
ollama pull qwq                  # Reasoning model
```

### Use with OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # required but ignored
)

response = client.chat.completions.create(
    model="qwen2.5-coder:32b",
    messages=[{"role": "user", "content": "Write a Python quicksort"}]
)
```

### Ollama API (native)

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "qwen2.5-coder:32b",
  "messages": [{"role": "user", "content": "Hello"}],
  "stream": false
}'
```

---

## SGLang (Recommended for Qwen3.6)

SGLang is the recommended inference backend for Qwen3.6 models — has native support for Qwen3's reasoning parser and tool-call parser.

```bash
pip install sglang[all]

# Serve Qwen3.6-35B-A3B with full features
python -m sglang.launch_server \
  --model-path Qwen/Qwen3.6-35B-A3B \
  --port 8000 \
  --tp-size 8 \
  --mem-fraction-static 0.8 \
  --context-length 262144 \
  --reasoning-parser qwen3 \
  --tool-call-parser qwen3_coder
```

---

## vLLM

High-throughput production inference. Best for serving Qwen to multiple users or in production pipelines.

```bash
pip install vllm

# Serve Qwen3.6-35B-A3B with tool calling support
vllm serve Qwen/Qwen3.6-35B-A3B \
  --port 8000 \
  --tensor-parallel-size 8 \
  --max-model-len 262144 \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder

# Serve Qwen2.5-Coder-32B (simpler, no reasoning parser needed)
vllm serve Qwen/Qwen2.5-Coder-32B-Instruct \
  --tensor-parallel-size 2
```

### Connect with OpenAI SDK

```python
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="token-vllm"  # any string
)
response = client.chat.completions.create(
    model="Qwen/Qwen2.5-72B-Instruct",
    messages=[{"role": "user", "content": "..."}]
)
```

### vLLM with Quantization (AWQ)

Reduces VRAM ~50%:

```bash
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-72B-Instruct-AWQ \
  --quantization awq \
  --dtype float16
```

---

## HuggingFace Transformers

Direct Python integration. Most flexible; useful for custom inference, fine-tuning, and research.

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "Qwen/Qwen2.5-Coder-7B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

messages = [
    {"role": "system", "content": "You are a helpful coding assistant."},
    {"role": "user", "content": "Write a Python binary search"}
]

text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)
inputs = tokenizer([text], return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=2048,
        temperature=0.1,
        do_sample=True
    )

response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
print(response)
```

### HuggingFace Inference API (serverless)

```python
client = OpenAI(
    base_url="https://api-inference.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"]
)
response = client.chat.completions.create(
    model="Qwen/Qwen2.5-Coder-32B-Instruct",
    messages=[{"role": "user", "content": "..."}]
)
```

---

## llama.cpp / GGUF

Runs on CPU or low-VRAM GPU. Recommended for Mac M-series and development machines.

```bash
# Install llama.cpp
brew install llama.cpp   # macOS
# or build from source: https://github.com/ggerganov/llama.cpp

# Download Qwen GGUF (from HuggingFace)
# Search: https://huggingface.co/models?search=qwen+gguf
# Popular quantizations: Q4_K_M (good balance), Q5_K_M (better quality), Q8_0 (best quality)

llama-server \
  --model qwen2.5-coder-7b-instruct-q4_k_m.gguf \
  --port 8080 \
  --ctx-size 32768
```

Exposes OpenAI-compatible endpoint at `http://localhost:8080/v1`.

---

## Hardware Requirements

| Model | Full Precision (BF16) | AWQ/GGUF Q4 | Recommended GPU |
|---|---|---|---|
| Qwen2.5-0.5B | ~1 GB VRAM | <1 GB | Any / CPU |
| Qwen2.5-3B | ~6 GB VRAM | ~2 GB | RTX 3060+ / Mac M1 |
| Qwen2.5-7B | ~14 GB VRAM | ~5 GB | RTX 3080 / Mac M2 |
| Qwen2.5-14B | ~28 GB VRAM | ~10 GB | RTX 4090 / A100 40GB |
| Qwen2.5-32B | ~64 GB VRAM | ~20 GB | A100 80GB / 2x4090 |
| Qwen2.5-72B | ~144 GB VRAM | ~45 GB | 4x A100 / H100 |

**Mac M-series:** Qwen2.5-7B and smaller run well via Ollama on 16GB unified memory. Qwen2.5-Coder-7B is the recommended local code model for Mac.

---

## Gotchas

- **Chat template is required**: Qwen models use a specific `<|im_start|>` / `<|im_end|>` chat format. Always use `tokenizer.apply_chat_template()` — raw string concatenation breaks generation.
- **`torch_dtype=torch.bfloat16` is required**: Loading in float32 doubles VRAM and is slower. Always set `torch_dtype=torch.bfloat16` (or `torch.float16` for older GPUs without BF16).
- **`device_map="auto"` doesn't always split optimally**: For multi-GPU, explicitly set `--tensor-parallel-size` in vLLM or use `device_map` with a custom allocation dict.
- **Ollama model tags matter**: `qwen2.5:latest` pulls the 7B model by default. Explicitly specify size (e.g., `qwen2.5:72b`) to get the model you want.
- **GGUF quantization quality**: Q4_K_M is a good default (good quality, 50% size reduction). Q2_K is too lossy for code tasks — use at minimum Q4_K_M for Qwen2.5-Coder.
- **vLLM max-model-len**: Default context length in vLLM may not match the model's advertised maximum. Set `--max-model-len` explicitly to match your use case, capped by available VRAM.
