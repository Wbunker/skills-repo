# Fine-Tuning Gemma

## Overview

Gemma supports supervised fine-tuning (SFT) via LoRA and full fine-tuning. Unsloth provides the fastest path with significant memory savings. For Gemma 4 MoE variants, use 16-bit LoRA — QLoRA interacts poorly with MoE expert routing.

---

## Unsloth (Recommended)

Unsloth provides 2x faster training and ~60% less VRAM than vanilla HuggingFace for Gemma.

```bash
pip install unsloth
```

```python
from unsloth import FastLanguageModel
import torch

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/gemma-3-27b-it",
    max_seq_length=8192,
    dtype=torch.bfloat16,
    load_in_4bit=True,   # QLoRA (use False for 16-bit LoRA on MoE)
)

model = FastLanguageModel.get_peft_model(
    model,
    r=16,                    # LoRA rank
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0.0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=42,
)
```

### Training with TRL

```python
from trl import SFTTrainer
from transformers import TrainingArguments

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=8192,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=10,
        num_train_epochs=3,
        learning_rate=2e-4,
        fp16=False,
        bf16=True,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="cosine",
        output_dir="./gemma-finetuned",
        save_strategy="epoch",
    ),
)
trainer.train()
```

### Save and Export

```python
# Save LoRA adapter only
model.save_pretrained("gemma-lora-adapter")
tokenizer.save_pretrained("gemma-lora-adapter")

# Merge and export to GGUF (for llama.cpp)
model.save_pretrained_gguf(
    "gemma-finetuned-gguf",
    tokenizer,
    quantization_method="q4_k_m"
)
```

---

## HuggingFace PEFT (Standard LoRA)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, TaskType
import torch

# QLoRA config (4-bit base, fp16 adapters)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)

model = AutoModelForCausalLM.from_pretrained(
    "google/gemma-3-27b-it",
    quantization_config=bnb_config,
    device_map="auto",
)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# Prints: trainable params: ~40M || all params: 27B || trainable%: ~0.15%
```

---

## MoE Fine-Tuning (Gemma 4 26B A4B)

**Critical**: For Gemma 4 MoE variants, use **16-bit LoRA**, not QLoRA.

```python
# For MoE models — do NOT use load_in_4bit=True
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/gemma-4-26b-a4b",
    max_seq_length=8192,
    dtype=torch.bfloat16,
    load_in_4bit=False,   # Must be False for MoE
)
```

Why: QLoRA's 4-bit quantization conflicts with MoE expert routing, causing training instability and degraded convergence. MoE models need full-precision expert weights during forward passes.

**Memory implication**: 16-bit LoRA on 26B A4B requires ~52 GB VRAM (2 bytes × 26B params). Use 2x A100 80GB or an H100 80GB.

---

## Dataset Preparation

Format data using Gemma's chat template:

```python
def format_example(example):
    messages = [
        {"role": "user", "content": example["instruction"]},
        {"role": "assistant", "content": example["output"]}
    ]
    return tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False
    )

dataset = dataset.map(lambda x: {"text": format_example(x)})
```

Always use `apply_chat_template` — never construct `<start_of_turn>` tokens manually.

---

## Google Vertex AI Fine-Tuning

For managed fine-tuning without local GPU infrastructure:

```python
import vertexai
from vertexai.tuning import sft

vertexai.init(project="YOUR_PROJECT_ID", location="us-central1")

sft_tuning_job = sft.train(
    source_model="google/gemma-3-12b-it",
    train_dataset="gs://your-bucket/train.jsonl",
    validation_dataset="gs://your-bucket/val.jsonl",
    epochs=3,
    learning_rate_multiplier=1.0,
    tuned_model_display_name="gemma-finetuned-v1",
)

sft_tuning_job.result()
print(sft_tuning_job.tuned_model_endpoint_name)
```

Training data format (JSONL):
```json
{"messages": [{"role": "user", "content": "..."}, {"role": "model", "content": "..."}]}
```

---

## VRAM Requirements for Fine-Tuning

| Model | Method | Min VRAM |
|-------|--------|----------|
| gemma-3-4b | QLoRA | ~8 GB |
| gemma-3-12b | QLoRA | ~16 GB |
| gemma-3-27b | QLoRA | ~24 GB |
| gemma-4-26b-a4b | 16-bit LoRA | ~52 GB |
| gemma-4-31b | QLoRA | ~48 GB |

---

## Gotchas

- **MoE + QLoRA = unstable**: Use 16-bit LoRA for Gemma 4 26B A4B
- **Chat template is mandatory**: Fine-tuning on raw text without the chat template produces a model that ignores turn structure
- **Learning rate**: Start at 2e-4 for LoRA; too high causes catastrophic forgetting, too low causes no adaptation
- **Gradient checkpointing**: Required for larger models to fit in VRAM — Unsloth's version is faster than HuggingFace's
- **Merging adapters**: If deploying to llama.cpp, merge and export to GGUF before deployment — adapters alone are not compatible
