# Gotchas, Common Mistakes & Troubleshooting

## The #1 Mistake: Wrong Chat Template at Inference

**Problem:** Model generates garbled output, repeats tokens, or ignores instructions after export.

**Cause:** The chat template used during inference (in Ollama, llama.cpp, vLLM) doesn't match the one used during training.

**Fix:**
```python
# During training — always note which template you used
tokenizer = get_chat_template(tokenizer, chat_template="llama-3")

# During inference — use EXACT same template
# For Ollama: verify Modelfile TEMPLATE section matches
# For llama.cpp: check --chat-template flag
# For vLLM: pass chat_template explicitly
```

Unsloth auto-generates correct Modelfiles for Ollama for 40+ model families. If using manual inference, print your tokenizer's chat template:

```python
print(tokenizer.chat_template)
```

---

## Loss Issues

### Loss Too Low / Overfitting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Loss < 0.2 | Overfitting | Reduce epochs, increase dropout |
| Loss → 0.0 | Dataset memorized | Stop training; add regularization |
| Loss stays flat | LR too low or dataset too small | Increase learning rate |
| Loss diverges (NaN) | LR too high | Reduce learning rate 10x |

**Overfitting fixes:**
```python
# Option 1: Reduce lora_alpha (scale down adapter)
lora_alpha = r * 0.5   # Instead of r * 1 or r * 2

# Option 2: Lower learning rate
learning_rate = 1e-5    # Instead of 2e-4

# Option 3: Reduce epochs
num_train_epochs = 1    # Instead of 3+

# Option 4: Enable evaluation with early stopping
from transformers import EarlyStoppingCallback

trainer = SFTTrainer(
    ...,
    eval_dataset = eval_dataset,
    callbacks    = [EarlyStoppingCallback(early_stopping_patience=3)],
    args = SFTConfig(
        ...,
        evaluation_strategy = "steps",
        eval_steps          = 50,
        load_best_model_at_end = True,
    ),
)
```

### "All labels in your dataset are -100"

**Cause:** `train_on_responses_only()` instruction/response markers don't match tokenized data.

**Diagnosis:**
```python
# Decode a sample to see what's actually in the data
print(tokenizer.decode(dataset[0]["input_ids"]))
# Find the exact string before assistant responses
```

**Fix:** Update `instruction_part` and `response_part` to match exactly what appears in the tokenized output. For Llama-3.1:
```python
trainer = train_on_responses_only(
    trainer,
    instruction_part = "<|start_header_id|>user<|end_header_id|>\n\n",
    response_part    = "<|start_header_id|>assistant<|end_header_id|>\n\n",
)
```

For ChatML:
```python
trainer = train_on_responses_only(
    trainer,
    instruction_part = "<|im_start|>user\n",
    response_part    = "<|im_start|>assistant\n",
)
```

---

## Memory Errors

### CUDA Out of Memory During Training

```python
# Reduce in this order:
# 1. Lower batch size
per_device_train_batch_size = 1

# 2. Increase gradient accumulation to compensate
gradient_accumulation_steps = 8

# 3. Use Unsloth's gradient checkpointing
use_gradient_checkpointing = "unsloth"  # Saves extra 30% vs True

# 4. Switch to QLoRA if using LoRA
load_in_4bit = True  # QLoRA instead of 16-bit LoRA

# 5. Reduce sequence length
max_seq_length = 1024  # Down from 2048

# 6. Lower LoRA rank
r = 8  # Down from 16 or 32
```

### OOM During GGUF Export

```python
model.save_pretrained_gguf(
    "model",
    tokenizer,
    quantization_method  = "q4_k_m",
    maximum_memory_usage = 0.5,    # Default 0.75 — reduce this
)
```

### Evaluation OOM

```python
args = SFTConfig(
    per_device_eval_batch_size = 1,   # Low eval batch
    fp16_full_eval             = True,  # FP16 for eval
)
```

---

## Slow Training / Torch.compile

```bash
# torch.compile has ~5 minute warmup — wait before measuring throughput
# Disable if causing issues:
export UNSLOTH_COMPILE_DISABLE=1
```

Or in Python before any imports:
```python
import os
os.environ["UNSLOTH_COMPILE_DISABLE"] = "1"
```

---

## Downloads Stuck at 90–95%

```python
import os
os.environ["UNSLOTH_STABLE_DOWNLOADS"] = "1"
```

Or in bash: `export UNSLOTH_STABLE_DOWNLOADS=1`

---

## UTF-8 Locale Error (Google Colab)

```python
import locale
locale.getpreferredencoding = lambda: "UTF-8"
```

---

## "CUDA error: device-side assert triggered"

```python
import os
os.environ["UNSLOTH_COMPILE_DISABLE"] = "1"
# Must be set BEFORE importing unsloth or torch
```

---

## Infinite EOS Tokens at Inference

**Symptom:** Model generates `<|eot_id|>` or similar tokens infinitely.

**Cause:** EOS token not properly set in tokenizer or mismatch in `apply_chat_template`.

**Fix:**
```python
tokenizer = get_chat_template(tokenizer, chat_template="llama-3", map_eos_token=True)

# Always use add_generation_prompt=True at inference
inputs = tokenizer.apply_chat_template(
    messages,
    tokenize              = True,
    add_generation_prompt = True,  # Critical for inference
    return_tensors        = "pt"
)

# Set eos_token_id explicitly in generate()
_ = model.generate(
    **inputs,
    max_new_tokens  = 256,
    eos_token_id    = tokenizer.eos_token_id,
    pad_token_id    = tokenizer.pad_token_id,
)
```

---

## Gradient Accumulation Notes

Gradient accumulation simulates a larger batch without more VRAM:
```
effective_batch = per_device_batch × gradient_accumulation_steps × num_gpus
```

Common misconception: gradient accumulation does NOT reduce VRAM — it uses the same VRAM as without it. It only enables training with effectively larger batches.

**Target effective batch:** 32–64 for most fine-tuning tasks.

---

## QLoRA vs LoRA Trade-offs

| | QLoRA (4-bit) | LoRA (16-bit) |
|-|--------------|---------------|
| VRAM | ~75% less | Baseline |
| Speed | Slightly slower | Slightly faster |
| Quality | Nearly identical | Marginally better |
| Recommended | Most cases (limited VRAM) | When you have VRAM budget |

Set `load_in_4bit=True` for QLoRA, `load_in_4bit=False` for LoRA.

---

## Using Unsupported Models

For models not in Unsloth's optimized list:

```python
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name        = "some-new-model/not-in-unsloth",
    max_seq_length    = 2048,
    load_in_4bit      = True,
    trust_remote_code = True,   # Required for non-standard architectures
)
```

Unsloth falls back to standard HuggingFace transformers for unsupported architectures — slower but functional.

---

## Version Conflicts

```bash
# Always update all Unsloth packages together
pip install --upgrade --force-reinstall --no-cache-dir --no-deps \
    unsloth unsloth_zoo

# If still broken, also update transformers and TRL
pip install --upgrade transformers trl peft accelerate
```

---

## Common Errors Reference

| Error Message | Cause | Fix |
|---------------|-------|-----|
| `All labels are -100` | `train_on_responses_only` markers wrong | Check tokenized text, fix marker strings |
| `CUDA device-side assert` | Compile issue | Set `UNSLOTH_COMPILE_DISABLE=1` before imports |
| Downloads stuck 90-95% | Network/download issue | Set `UNSLOTH_STABLE_DOWNLOADS=1` |
| `UTF-8 locale required` | Colab locale | `locale.getpreferredencoding = lambda: "UTF-8"` |
| Garbled inference output | Wrong chat template | Match template to training exactly |
| OOM during export | Memory pressure | Set `maximum_memory_usage=0.5` |
| Infinite token generation | EOS not configured | Set `eos_token_id`, use `map_eos_token=True` |
| `Weight initialization warnings` | Old packages | Update transformers, timm, unsloth |
