# Dataset Formatting & Chat Templates

## Dataset Format Types

| Format | Use Case | Turns | Key Fields |
|--------|----------|-------|------------|
| Raw Corpus | Continued pretraining | N/A | `text` |
| Alpaca/Instruct | Single-turn instruction following | 1 | `instruction`, `input`, `output` |
| ShareGPT | Multi-turn conversation | Multiple | `conversations[{from, value}]` |
| ChatML | Multi-turn (OpenAI standard) | Multiple | `messages[{role, content}]` |
| RLHF/DPO | Preference optimization | Multiple | `prompt`, `chosen`, `rejected` |

---

## Raw Corpus Format (Continued Pretraining)

```json
{"text": "Pasta carbonara is a traditional Roman pasta dish made with eggs, Pecorino Romano..."}
{"text": "The French Revolution began in 1789 when..."}
```

Load with:
```python
from datasets import load_dataset
dataset = load_dataset("text", data_files="my_corpus.txt", split="train")
```

---

## Alpaca Format (Instruction-Tuning)

Single-turn format. Very common for instruction datasets.

```json
{
  "instruction": "Translate the following English text to French.",
  "input": "Hello, how are you?",
  "output": "Bonjour, comment allez-vous?"
}
```

Note: `input` field is optional. When empty, only `instruction` and `output` are used.

**Loading Alpaca-style from HuggingFace:**
```python
from datasets import load_dataset
dataset = load_dataset("yahma/alpaca-cleaned", split="train")
```

**Convert Alpaca to multi-turn using `to_sharegpt`:**
```python
from unsloth.chat_templates import to_sharegpt

dataset = to_sharegpt(
    dataset,
    merged_prompt = "{instruction} {input}",  # Combine columns into prompt
    output_column_name = "output",
    conversation_extension = 3,  # Merge 3 random rows into one multi-turn conversation
)
```

---

## ShareGPT Format (Multi-Turn)

Uses `from`/`value` keys. Very common for conversational datasets.

```json
{
  "conversations": [
    {"from": "human", "value": "What is machine learning?"},
    {"from": "gpt", "value": "Machine learning is a subset of AI..."},
    {"from": "human", "value": "Can you give an example?"},
    {"from": "gpt", "value": "Sure! A spam filter is a classic example..."}
  ]
}
```

**Standardize to ChatML format:**
```python
from unsloth.chat_templates import standardize_sharegpt
dataset = standardize_sharegpt(dataset)
# Converts from/value -> role/content automatically
```

---

## ChatML Format (OpenAI Standard)

Uses `role`/`content` keys. HuggingFace default.

```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is 2+2?"},
    {"role": "assistant", "content": "2+2 equals 4."},
    {"role": "user", "content": "What about 3+3?"},
    {"role": "assistant", "content": "3+3 equals 6."}
  ]
}
```

---

## Applying Chat Templates

### Step 1: Check available templates
```python
from unsloth.chat_templates import CHAT_TEMPLATES
print(list(CHAT_TEMPLATES.keys()))
# ['unsloth', 'zephyr', 'chatml', 'mistral', 'llama', 'llama-3',
#  'vicuna', 'alpaca', 'gemma', 'gemma-3', 'phi-4', 'qwen-2.5', ...]
```

### Step 2: Apply template to tokenizer
```python
from unsloth.chat_templates import get_chat_template

tokenizer = get_chat_template(
    tokenizer,
    chat_template = "llama-3",   # Match the model you loaded
    mapping       = {"role": "from", "content": "value",
                     "user": "human", "assistant": "gpt"},  # For ShareGPT keys
    map_eos_token = True,        # Map EOS token for compatibility
)
```

### Step 3: Define formatting function
```python
def formatting_prompts_func(examples):
    convos = examples["conversations"]  # or "messages" depending on your dataset
    texts = [
        tokenizer.apply_chat_template(
            convo,
            tokenize            = False,
            add_generation_prompt = False,  # False during training
        )
        for convo in convos
    ]
    return {"text": texts}
```

### Step 4: Apply to dataset
```python
dataset = dataset.map(formatting_prompts_func, batched=True)
```

---

## Custom Chat Templates

Pass a tuple of `(template_string, eos_token)`:

```python
tokenizer = get_chat_template(
    tokenizer,
    chat_template = (
        "{% for message in messages %}"
        "{{ message['role'] + ': ' + message['content'] + '\n' }}"
        "{% endfor %}",
        "</s>"  # EOS token string
    ),
)
```

The EOS token must appear somewhere in the template for proper generation termination.

---

## Multimodal (Vision) Dataset Format

For vision fine-tuning (e.g., Llama 3.2 Vision, Gemma 3):

```python
from PIL import Image

# Format: each message can have mixed content types
conversation = [
    {
        "role": "user",
        "content": [
            {"type": "text",  "text": "Describe what you see in this image."},
            {"type": "image", "image": Image.open("photo.jpg")}  # PIL Image object
        ]
    },
    {
        "role": "assistant",
        "content": [
            {"type": "text", "text": "The image shows a golden retriever sitting..."}
        ]
    }
]
```

For audio models, replace `"image"` type with `"audio"` and provide audio tensors.

**Dataset loading for vision:**
```python
from datasets import load_dataset
dataset = load_dataset("HuggingFaceM4/the_cauldron", "ai2d", split="train")
# Datasets with 'image' column are automatically handled
```

---

## DPO Dataset Format

Requires prompt, chosen response, and rejected response:

```json
{
  "prompt": "What is the capital of France?",
  "chosen": "The capital of France is Paris.",
  "rejected": "I think it might be Lyon or Marseille."
}
```

Or with conversation history:
```json
{
  "prompt": [
    {"role": "user", "content": "What is the capital of France?"}
  ],
  "chosen": [
    {"role": "assistant", "content": "The capital of France is Paris."}
  ],
  "rejected": [
    {"role": "assistant", "content": "I think it might be Lyon."}
  ]
}
```

---

## GRPO Dataset Format

GRPO only needs prompts (model generates its own completions):

```json
{
  "prompt": "Solve: What is 15% of 240?",
  "answer": "36"
}
```

Or as conversations:
```python
dataset = dataset.map(lambda x: {
    "prompt": [{"role": "user", "content": x["question"]}],
    "answer": x["answer"]
})
```

---

## Dataset Size Guidelines

| Dataset Size | Recommendation |
|-------------|----------------|
| < 100 rows | Not recommended; synthetic data augmentation needed |
| 100–300 rows | Use instruct model; expect limited generalization |
| 300–1000 rows | Either base or instruct works; quality critical |
| 1000–10000 rows | Base model viable; strong improvements |
| 10000+ rows | Full fine-tuning territory; consider CPT |

Quality matters far more than quantity. 500 carefully crafted examples outperform 50,000 noisy ones.

---

## Loading Datasets from HuggingFace

```python
from datasets import load_dataset

# Standard HF dataset
dataset = load_dataset("mlabonne/guanaco-llama2-1k", split="train")

# Specific subset
dataset = load_dataset("Open-Orca/OpenOrca", split="train[:5000]")

# From local CSV/JSON
dataset = load_dataset("json", data_files="my_data.jsonl", split="train")
dataset = load_dataset("csv",  data_files="my_data.csv",   split="train")

# Train/test split
split = dataset.train_test_split(test_size=0.1, shuffle=True, seed=42)
train_dataset = split["train"]
eval_dataset  = split["test"]
```
