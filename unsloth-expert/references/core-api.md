# Unsloth Core API Reference

## FastLanguageModel

The central class for all model loading, LoRA patching, and inference preparation.

```python
from unsloth import FastLanguageModel
```

---

## FastLanguageModel.from_pretrained()

Loads a model with optional quantization. Returns `(model, tokenizer)`.

```python
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name    = "unsloth/Meta-Llama-3.1-8B",  # HF repo or local path
    max_seq_length = 2048,        # Context length; supports RoPE scaling internally
    dtype          = None,        # None = auto (Float16 for T4/V100, BFloat16 for Ampere+)
    load_in_4bit   = True,        # True = QLoRA; False = LoRA (16-bit)
    token          = "hf_...",    # HuggingFace token for gated models (optional)
    trust_remote_code = False,    # Set True for custom architectures
)
```

### Key Parameters

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `model_name` | str | required | HF model ID or local path; prefer `unsloth/` variants for pre-quantized |
| `max_seq_length` | int | 2048 | Max tokens; Unsloth auto-scales RoPE if model supports it |
| `dtype` | torch.dtype or None | None | `None` = auto-detect; `torch.float16`; `torch.bfloat16` |
| `load_in_4bit` | bool | True | 4-bit NF4 quantization (QLoRA mode) |
| `token` | str | None | HF token; or set `HF_TOKEN` env var |
| `trust_remote_code` | bool | False | For non-standard architectures |

### Unsloth-Optimized Model IDs

Unsloth publishes pre-quantized versions of popular models on HuggingFace under the `unsloth/` namespace:

```
unsloth/Meta-Llama-3.1-8B
unsloth/Meta-Llama-3.1-8B-Instruct
unsloth/Meta-Llama-3.1-70B-bnb-4bit
unsloth/Mistral-7B-v0.3
unsloth/mistral-7b-v0.3-bnb-4bit
unsloth/gemma-2-9b
unsloth/gemma-2-27b-bnb-4bit
unsloth/Qwen2.5-7B
unsloth/Qwen2.5-72B-Instruct-bnb-4bit
unsloth/Phi-4
unsloth/DeepSeek-R1
unsloth/DeepSeek-R1-GGUF
```

Using `unsloth/` variants is faster to download (pre-quantized) and validated to work.

---

## FastLanguageModel.get_peft_model()

Applies LoRA adapters to a loaded model. Must be called after `from_pretrained()`.

```python
model = FastLanguageModel.get_peft_model(
    model,
    r                   = 16,          # LoRA rank
    target_modules      = ["q_proj", "k_proj", "v_proj", "o_proj",
                           "gate_proj", "up_proj", "down_proj"],
    lora_alpha          = 16,          # Scaling: effect = (alpha/r) * adapter
    lora_dropout        = 0,           # 0 is optimized by Unsloth; 0-0.1 range
    bias                = "none",      # "none" | "all" | "lora_only"
    use_gradient_checkpointing = "unsloth",  # "unsloth" | True | False
    random_state        = 3407,        # Reproducibility seed
    use_rslora          = False,       # Rank-Stabilized LoRA (alpha/sqrt(r))
    loftq_config        = None,        # LoftQ config for quantization-aware init
)
```

### Parameter Explanations

**`r` (LoRA Rank)**
- Controls the number of trainable parameters in each adapter matrix
- Common values: 8, 16, 32, 64, 128
- Recommended starting point: 16 or 32
- Higher rank = more capacity but more VRAM and overfitting risk
- Very small datasets: use r=8 or r=16

**`lora_alpha`**
- Scaling factor: `effective_update = (lora_alpha / r) * (A @ B)`
- Two common strategies:
  - `lora_alpha = r` — conservative, stable (ratio = 1.0)
  - `lora_alpha = r * 2` — more aggressive learning (ratio = 2.0)
- Rule: keep `lora_alpha / r >= 1`

**`target_modules`**
- Which weight matrices receive LoRA adapters
- Full recommended set covers both attention and MLP layers:
  ```python
  ["q_proj", "k_proj", "v_proj", "o_proj",   # attention
   "gate_proj", "up_proj", "down_proj"]        # MLP/FFN
  ```
- Research shows targeting all major linear layers matches full fine-tuning performance
- Embedding and LM head can optionally be added: `"embed_tokens"`, `"lm_head"`

**`lora_dropout`**
- Randomly zeros adapter activations during training (regularization)
- Set to 0 for Unsloth's optimized fast path
- Values 0.05–0.1 add regularization at a small speed cost

**`bias`**
- `"none"` — fastest, no bias training (recommended)
- `"all"` — train all biases
- `"lora_only"` — train only LoRA biases

**`use_gradient_checkpointing`**
- `"unsloth"` — Unsloth's smart checkpointing, saves extra 30% VRAM vs standard
- `True` — standard HuggingFace gradient checkpointing
- `False` — disable (fastest, most VRAM)
- Use `"unsloth"` for long-context or memory-constrained setups

**`use_rslora`**
- Rank-Stabilized LoRA: scales by `alpha / sqrt(r)` instead of `alpha / r`
- More stable at higher ranks; set to True when r >= 64

---

## FastLanguageModel.for_inference()

Switches model to optimized inference mode (2x faster). Must call before generating.

```python
FastLanguageModel.for_inference(model)
```

Then generate:

```python
from transformers import TextStreamer

inputs = tokenizer.apply_chat_template(
    [{"role": "user", "content": "What is LoRA?"}],
    tokenize=True,
    add_generation_prompt=True,
    return_tensors="pt"
).to("cuda")

text_streamer = TextStreamer(tokenizer, skip_prompt=True)
_ = model.generate(
    input_ids    = inputs,
    streamer     = text_streamer,
    max_new_tokens = 256,
    temperature  = 0.7,
    do_sample    = True,
)
```

---

## train_on_responses_only()

Masks prompt tokens so loss is computed only on assistant responses.

```python
from unsloth.chat_templates import train_on_responses_only

trainer = train_on_responses_only(
    trainer,
    instruction_part = "<|start_header_id|>user<|end_header_id|>\n\n",
    response_part    = "<|start_header_id|>assistant<|end_header_id|>\n\n",
)
```

The exact token strings depend on the chat template used. For Llama-3:
- `instruction_part`: `"<|start_header_id|>user<|end_header_id|>\n\n"`
- `response_part`: `"<|start_header_id|>assistant<|end_header_id|>\n\n"`

For ChatML:
- `instruction_part`: `"<|im_start|>user\n"`
- `response_part`: `"<|im_start|>assistant\n"`

**Common error:** `"All labels in your dataset are -100"` means these strings don't match what's in your formatted data — verify with `print(tokenizer.decode(dataset[0]["input_ids"]))`.

---

## PatchDPOTrainer / PatchFastRL

For DPO training, patch the trainer before importing:

```python
from unsloth import PatchDPOTrainer
PatchDPOTrainer()

from trl import DPOTrainer, DPOConfig
```

For GRPO:

```python
from unsloth import PatchFastRL
PatchFastRL("GRPO", FastLanguageModel)
```
