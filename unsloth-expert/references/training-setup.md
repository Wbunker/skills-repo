# Training Setup: SFT, DPO, and GRPO

## Complete SFT Training Example (End-to-End)

```python
from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template, standardize_sharegpt, train_on_responses_only
from datasets import load_dataset
from trl import SFTTrainer, SFTConfig

# ── 1. Load Model ──────────────────────────────────────────────────────────────
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name     = "unsloth/Meta-Llama-3.1-8B-Instruct",
    max_seq_length = 2048,
    dtype          = None,
    load_in_4bit   = True,
)

# ── 2. Apply LoRA ──────────────────────────────────────────────────────────────
model = FastLanguageModel.get_peft_model(
    model,
    r                          = 16,
    target_modules             = ["q_proj", "k_proj", "v_proj", "o_proj",
                                  "gate_proj", "up_proj", "down_proj"],
    lora_alpha                 = 16,
    lora_dropout               = 0,
    bias                       = "none",
    use_gradient_checkpointing = "unsloth",
    random_state               = 3407,
    use_rslora                 = False,
)

# ── 3. Dataset Preparation ─────────────────────────────────────────────────────
tokenizer = get_chat_template(tokenizer, chat_template="llama-3")

dataset = load_dataset("mlabonne/guanaco-llama2-1k", split="train")
dataset = standardize_sharegpt(dataset)

def formatting_prompts_func(examples):
    convos = examples["conversations"]
    texts = [tokenizer.apply_chat_template(c, tokenize=False,
             add_generation_prompt=False) for c in convos]
    return {"text": texts}

dataset = dataset.map(formatting_prompts_func, batched=True)

# ── 4. Trainer Configuration ───────────────────────────────────────────────────
trainer = SFTTrainer(
    model      = model,
    tokenizer  = tokenizer,
    train_dataset = dataset,
    # eval_dataset = eval_dataset,  # Optional
    args = SFTConfig(
        dataset_text_field         = "text",
        max_seq_length             = 2048,
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,   # Effective batch = 2*4 = 8
        warmup_steps               = 5,
        # num_train_epochs          = 1,   # Use this OR max_steps
        max_steps                  = 60,   # For quick experiments
        learning_rate              = 2e-4,
        logging_steps              = 1,
        optim                      = "adamw_8bit",
        weight_decay               = 0.01,
        lr_scheduler_type          = "linear",
        seed                       = 3407,
        output_dir                 = "outputs",
        report_to                  = "none",  # or "wandb"
        # fp16                     = True,   # Set one of fp16/bf16
        # bf16                     = False,
    ),
)

# Mask prompt tokens — train only on assistant responses
trainer = train_on_responses_only(
    trainer,
    instruction_part = "<|start_header_id|>user<|end_header_id|>\n\n",
    response_part    = "<|start_header_id|>assistant<|end_header_id|>\n\n",
)

# ── 5. Train ────────────────────────────────────────────────────────────────────
trainer_stats = trainer.train()
```

---

## SFTConfig / SFTTrainer Key Hyperparameters

| Parameter | Recommended | Notes |
|-----------|------------|-------|
| `per_device_train_batch_size` | 2–4 | Higher = more stable gradients; needs more VRAM |
| `gradient_accumulation_steps` | 4–8 | Simulates larger batch without extra VRAM |
| `max_seq_length` | 2048 | Match model's `max_seq_length`; longer = more VRAM |
| `learning_rate` | 2e-4 | Range: 1e-5 to 5e-4; lower for less data |
| `num_train_epochs` | 1–3 | More epochs on small datasets risks overfitting |
| `max_steps` | 60–500 | Use for quick tests; overrides `num_train_epochs` |
| `warmup_steps` | 5–10% of total | Stabilizes early training |
| `optim` | `"adamw_8bit"` | 8-bit Adam; saves VRAM with no quality loss |
| `lr_scheduler_type` | `"linear"` or `"cosine"` | Linear is safer default |
| `weight_decay` | 0.01 | Light regularization |
| `logging_steps` | 1 | Log every step for loss monitoring |

### Effective Batch Size
`effective_batch_size = per_device_train_batch_size × gradient_accumulation_steps × num_gpus`

Standard target: 32–64 effective batch size.

### Loss Interpretation
| Training Loss | Interpretation |
|--------------|----------------|
| > 2.0 | Model not learning or very early training |
| 1.0–2.0 | Normal early range |
| 0.5–1.0 | Good; model learning task |
| 0.2–0.5 | Approaching convergence |
| < 0.2 | **Warning: likely overfitting** |
| ~0.0 | **Overfitting; dataset memorized** |

---

## DPO Training (Preference Optimization)

Direct Preference Optimization trains a model to prefer `chosen` responses over `rejected` ones.

```python
from unsloth import FastLanguageModel, PatchDPOTrainer
PatchDPOTrainer()  # Must call BEFORE importing DPOTrainer

from trl import DPOTrainer, DPOConfig
from datasets import load_dataset

# Load a model already fine-tuned with SFT (or use an instruct model)
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name     = "unsloth/zephyr-sft-bnb-4bit",
    max_seq_length = 2048,
    dtype          = None,
    load_in_4bit   = True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r              = 64,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj"],
    lora_alpha     = 64,
    lora_dropout   = 0,
    bias           = "none",
    use_gradient_checkpointing = "unsloth",
)

# Dataset must have: prompt, chosen, rejected columns
dataset = load_dataset("Intel/orca_dpo_pairs", split="train")

dpo_trainer = DPOTrainer(
    model        = model,
    ref_model    = None,   # Unsloth handles reference model internally
    tokenizer    = tokenizer,
    train_dataset = dataset,
    args = DPOConfig(
        per_device_train_batch_size  = 4,
        gradient_accumulation_steps  = 8,
        warmup_ratio                 = 0.1,
        num_train_epochs             = 3,
        learning_rate                = 5e-6,   # Much lower than SFT
        logging_steps                = 1,
        optim                        = "adamw_8bit",
        lr_scheduler_type            = "linear",
        seed                         = 42,
        output_dir                   = "dpo_outputs",
        beta                         = 0.1,     # KL penalty strength
        max_length                   = 1024,
        max_prompt_length            = 512,
    ),
)

dpo_trainer.train()
```

### DPO Key Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| `beta` | 0.1 | KL divergence penalty; higher = stay closer to reference |
| `learning_rate` | 5e-6 | Much lower than SFT; DPO is sensitive |
| `ref_model` | None | Unsloth manages reference internally when None |
| `max_length` | 1024 | Max total sequence length |
| `max_prompt_length` | 512 | Max prompt portion |

### ORPO (Odds Ratio Preference Optimization)

No reference model needed. Simpler than DPO.

```python
from trl import ORPOTrainer, ORPOConfig

orpo_trainer = ORPOTrainer(
    model        = model,
    tokenizer    = tokenizer,
    train_dataset = dataset,
    args = ORPOConfig(
        learning_rate = 8e-6,
        beta          = 0.1,   # ORPO-specific penalty
        max_length    = 1024,
        max_prompt_length = 512,
        num_train_epochs = 1,
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        output_dir = "orpo_outputs",
    ),
)
```

---

## GRPO Training (Reinforcement Learning)

Group Relative Policy Optimization — trains models using custom reward functions. Used for reasoning models like DeepSeek R1.

**Key insight:** GRPO removes the value model and reference model from PPO. Only a reward function is needed, making it very memory-efficient (80% less VRAM vs standard RL).

```python
from unsloth import FastLanguageModel, PatchFastRL
from trl import GRPOTrainer, GRPOConfig
import re

# Load base model (reasoning needs ≥1.5B params for thinking tokens)
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name     = "unsloth/Qwen2.5-3B-Instruct",
    max_seq_length = 2048,
    dtype          = None,
    load_in_4bit   = True,
)
PatchFastRL("GRPO", FastLanguageModel)

model = FastLanguageModel.get_peft_model(
    model,
    r              = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj"],
    lora_alpha     = 16,
    lora_dropout   = 0,
    bias           = "none",
    use_gradient_checkpointing = "unsloth",
)

# Dataset: only needs prompts (model generates completions)
from datasets import load_dataset
dataset = load_dataset("openai/gsm8k", "main", split="train")

def format_prompt(example):
    return {
        "prompt": [{"role": "user", "content": example["question"]}],
        "answer": example["answer"].split("####")[-1].strip()
    }
dataset = dataset.map(format_prompt)

# ── Reward Functions ───────────────────────────────────────────────────────────

def reward_correct_answer(completions, answer, **kwargs):
    """Score +1 if final numeric answer matches, -1 otherwise."""
    scores = []
    for completion in completions:
        numbers = re.findall(r'\d+\.?\d*', completion)
        last_number = numbers[-1] if numbers else None
        scores.append(1.0 if last_number == answer else -1.0)
    return scores

def reward_format(completions, **kwargs):
    """Score +0.5 if response contains reasoning structure."""
    scores = []
    for completion in completions:
        score = 0.0
        if "<think>" in completion and "</think>" in completion:
            score += 0.5  # Has thinking block
        if len(completion) > 50:
            score += 0.1  # Non-trivial response
        scores.append(score)
    return scores

# ── Trainer ────────────────────────────────────────────────────────────────────
grpo_trainer = GRPOTrainer(
    model            = model,
    tokenizer        = tokenizer,
    reward_funcs     = [reward_correct_answer, reward_format],
    train_dataset    = dataset,
    args = GRPOConfig(
        per_device_train_batch_size  = 1,
        gradient_accumulation_steps  = 4,
        num_generations              = 8,    # Responses per prompt (group size)
        max_new_tokens               = 512,  # Max completion length
        max_prompt_length            = 512,
        learning_rate                = 5e-6,
        num_train_epochs             = 1,
        beta                         = 0.001, # KL penalty (small = allow exploration)
        output_dir                   = "grpo_outputs",
        optim                        = "adamw_8bit",
        logging_steps                = 1,
        # epsilon                    = 0.2,  # PPO clip range
        # loss_type                  = "grpo",  # or "gspo", "dr_grpo"
    ),
)

grpo_trainer.train()
```

### GRPO Key Parameters

| Parameter | Recommended | Notes |
|-----------|------------|-------|
| `num_generations` | 4–8 | Completions per prompt; higher = better gradient estimate, more VRAM |
| `beta` | 0.001–0.01 | KL penalty; lower allows more exploration |
| `max_new_tokens` | 256–1024 | Longer for reasoning tasks |
| `learning_rate` | 5e-6 | Very low; RL training is sensitive |
| `epsilon` | 0.2 | PPO clip ratio |
| `loss_type` | `"grpo"` | Options: `"grpo"`, `"gspo"`, `"dr_grpo"` |
| `mask_truncated_completions` | True | Skip truncated responses in loss |

### Thinking Mode (R1-style)

Enable the model to generate `<think>...</think>` blocks:

```python
# Apply thinking mode to tokenizer/model
tokenizer = get_chat_template(tokenizer, chat_template="qwen-2.5")

# Reward function that encourages thinking format
def reward_thinking_format(completions, **kwargs):
    scores = []
    for c in completions:
        if re.match(r"<think>.*?</think>", c, re.DOTALL):
            scores.append(1.0)
        else:
            scores.append(-0.5)  # Penalize missing thinking block
    return scores
```

Minimum model size for thinking tokens: ~1.5B parameters.

### GRPO Training Timeline
- First 300 steps: Little visible reward improvement (normal)
- After 300–500 steps: Rewards should begin increasing
- Decent results typically require 12+ hours of training
- Reusing data across epochs is fine

---

## Continued Pretraining (CPT)

For domain adaptation on raw text corpora.

```python
from unsloth import FastLanguageModel
from trl import SFTTrainer, SFTConfig

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name     = "unsloth/Llama-3.2-1B",   # Use BASE model, not instruct
    max_seq_length = 2048,
    dtype          = None,
    load_in_4bit   = True,
)

# LoRA for CPT — typically larger rank, add embeddings
model = FastLanguageModel.get_peft_model(
    model,
    r              = 128,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj",
                      "embed_tokens", "lm_head"],  # Include embeddings for CPT
    lora_alpha     = 32,
    use_gradient_checkpointing = "unsloth",
)

# Dataset: just raw text
from datasets import load_dataset
dataset = load_dataset("my_domain_corpus", split="train")

trainer = SFTTrainer(
    model         = model,
    tokenizer     = tokenizer,
    train_dataset = dataset,
    args = SFTConfig(
        dataset_text_field = "text",
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 8,
        max_steps   = 1000,
        learning_rate = 5e-5,   # Lower than instruction tuning
        output_dir  = "cpt_output",
    ),
)
trainer.train()
```
