# Export & Deployment

## Saving Options Overview

| Method | File Size | Use Case | Command |
|--------|-----------|----------|---------|
| LoRA adapters only | ~100MB | HF Hub sharing; reload with base model | `save_method="lora"` |
| Merged 16-bit | Large (full model) | vLLM, further training, maximum quality | `save_method="merged_16bit"` |
| Merged 4-bit | Medium | Space-efficient full model | `save_method="merged_4bit"` |
| GGUF quantized | Small–Medium | llama.cpp, Ollama, local inference | `save_pretrained_gguf()` |

---

## Save as LoRA Adapters

Smallest footprint (~100MB). Requires base model at inference time.

```python
# Save locally
model.save_pretrained("lora_model")
tokenizer.save_pretrained("lora_model")

# Or using Unsloth's method
model.save_pretrained_merged("lora_model", tokenizer, save_method="lora")

# Push to HuggingFace Hub
model.push_to_hub_merged(
    "your-username/my-lora-model",
    tokenizer,
    save_method = "lora",
    token       = "hf_your_token_here",
)
```

**Reloading LoRA adapters later:**
```python
from peft import PeftModel

base_model, tokenizer = FastLanguageModel.from_pretrained(
    "unsloth/Meta-Llama-3.1-8B", max_seq_length=2048, load_in_4bit=True
)
model = PeftModel.from_pretrained(base_model, "lora_model")
```

---

## Merge to 16-bit (Full Model)

Bakes LoRA weights into the base model. Needed for vLLM deployment.

```python
# Save merged model locally
model.save_pretrained_merged("merged_model", tokenizer, save_method="merged_16bit")
tokenizer.save_pretrained("merged_model")

# Push merged 16-bit to HuggingFace Hub
model.push_to_hub_merged(
    "your-username/my-merged-model",
    tokenizer,
    save_method = "merged_16bit",
    token       = "hf_your_token_here",
)
```

**For vLLM deployment:**
```bash
python -m vllm.entrypoints.openai.api_server \
  --model merged_model \
  --dtype bfloat16 \
  --port 8000
```

---

## GGUF Export (for llama.cpp / Ollama)

### Quick One-Step Export

```python
# Save GGUF locally
model.save_pretrained_gguf(
    "gguf_model",
    tokenizer,
    quantization_method = "q4_k_m"   # Recommended default
)

# Push GGUF to HuggingFace Hub
model.push_to_hub_gguf(
    "your-username/my-gguf-model",
    tokenizer,
    quantization_method = "q4_k_m",
    token = "hf_your_token_here",
)
```

### Multiple Quantizations at Once

```python
model.push_to_hub_gguf(
    "your-username/my-model",
    tokenizer,
    quantization_method = ["q4_k_m", "q8_0", "q5_k_m"],  # List of formats
    token = "hf_your_token_here",
)
```

### GGUF Quantization Options

| Method | Bits per Weight | Quality | Speed | Notes |
|--------|----------------|---------|-------|-------|
| `not_quantized` | 16 bpw | Best | Slowest | F16 baseline |
| `f16` | 16 bpw | Best | Slow | Full precision |
| `q8_0` | 8 bpw | Excellent | Good | Fast export; recommended for testing |
| `q6_k` | ~6 bpw | Very Good | Good | |
| `q5_k_m` | ~5 bpw | Good | Faster | Hybrid Q5/Q6 |
| `q4_k_m` | ~4 bpw | Good | Fast | **Recommended default** |
| `q4_k_s` | ~4 bpw | Good | Fast | Smaller than q4_k_m |
| `q3_k_m` | ~3 bpw | Acceptable | Faster | |
| `q2_k` | ~2 bpw | Degraded | Fastest | Minimum useful quality |
| `iq2_xxs` | 2.06 bpw | Degraded | Fastest | Maximum compression |

**Unsloth Dynamic Quantization (2.0):** Higher accuracy alternative to standard GGUF. Uses mixed precision (important layers keep higher precision). Available as `"unsloth_dynamic"` method.

### Manual GGUF Conversion (Advanced)

If one-step method fails, do it in two steps:

```python
# Step 1: Save merged 16-bit
model.save_pretrained_merged("merged_model", tokenizer, save_method="merged_16bit")
```

```bash
# Step 2: Compile llama.cpp and convert
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp && make

python convert_hf_to_gguf.py ../merged_model \
    --outfile model-F16.gguf \
    --outtype f16

# Then quantize
./quantize model-F16.gguf model-Q4_K_M.gguf Q4_K_M
```

### Memory During GGUF Export

If GGUF conversion crashes (OOM):
```python
# Reduce GPU usage during export
model.save_pretrained_gguf(
    "gguf_model",
    tokenizer,
    quantization_method  = "q4_k_m",
    maximum_memory_usage = 0.5,    # Default is 0.75; reduce if crashing
)
```

---

## Ollama Integration

### Save for Ollama (Local)

```python
# Step 1: Save as GGUF
model.save_pretrained_gguf("ollama_model", tokenizer, quantization_method="q8_0")

# Step 2: Unsloth auto-generates the Modelfile
# Check/print it:
modelfile_path = "ollama_model/Modelfile"
with open(modelfile_path) as f:
    print(f.read())
```

The Modelfile includes the correct chat template for the model family. This is critical — Ollama needs this to format prompts correctly.

### Register with Ollama

```bash
# Start Ollama server (must be running)
ollama serve &

# Create model from Modelfile
ollama create my_finetuned_model -f ollama_model/Modelfile

# Test it
ollama run my_finetuned_model
```

### Push to Ollama.com Hub

```python
# From Colab / Python
from unsloth.save import push_to_ollama_hub

push_to_ollama_hub(
    model,
    tokenizer,
    quantization_method = "q4_k_m",
    ollama_username     = "your-ollama-username",
    ollama_token        = "your_ollama_token",
    repo_name           = "my-finetuned-model",
)
```

### Common Ollama Gotcha

The Modelfile's `TEMPLATE` section must exactly match the chat template used during training. Unsloth generates this automatically for 40+ model families. If inference gives garbled output, verify with:

```bash
ollama show my_finetuned_model --modelfile
```

---

## vLLM Deployment

For production multi-user serving:

```python
# First, save merged 16-bit
model.save_pretrained_merged("vllm_model", tokenizer, save_method="merged_16bit")
```

```bash
pip install vllm

python -m vllm.entrypoints.openai.api_server \
    --model vllm_model \
    --dtype bfloat16 \
    --max-model-len 4096 \
    --port 8000

# Query via OpenAI-compatible API
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "vllm_model", "messages": [{"role": "user", "content": "Hello"}]}'
```

---

## Push to HuggingFace Hub — All Methods

```python
# LoRA only (smallest)
model.push_to_hub_merged("username/model-lora",   tokenizer, save_method="lora",        token="hf_...")

# Merged 16-bit (full quality)
model.push_to_hub_merged("username/model-16bit",  tokenizer, save_method="merged_16bit", token="hf_...")

# Merged 4-bit
model.push_to_hub_merged("username/model-4bit",   tokenizer, save_method="merged_4bit",  token="hf_...")

# GGUF (q4_k_m)
model.push_to_hub_gguf(  "username/model-gguf",   tokenizer, quantization_method="q4_k_m", token="hf_...")

# Multiple GGUF formats at once
model.push_to_hub_gguf(  "username/model-gguf",   tokenizer,
    quantization_method=["q4_k_m", "q8_0"], token="hf_...")
```
