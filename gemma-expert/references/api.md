# Gemma API Reference

## Google AI Studio (Gemini API)

Gemma models are accessible through the same API as Gemini. Free tier available.

```python
pip install google-genai
```

```python
from google import genai

client = genai.Client(api_key="YOUR_API_KEY")

response = client.models.generate_content(
    model="gemma-4-26b-a4b",
    contents="Explain MoE architecture."
)
print(response.text)
```

Get an API key at: aistudio.google.com

### Chat / Multi-Turn

```python
from google import genai
from google.genai import types

client = genai.Client(api_key="YOUR_API_KEY")

history = [
    types.Content(role="user", parts=[types.Part(text="Hi")]),
    types.Content(role="model", parts=[types.Part(text="Hello! How can I help?")]),
]

response = client.models.generate_content(
    model="gemma-4-26b-a4b",
    contents=history + [types.Content(role="user", parts=[types.Part(text="What is 2+2?")])],
)
```

### Streaming

```python
for chunk in client.models.generate_content_stream(
    model="gemma-4-26b-a4b",
    contents="Write a long essay on quantum computing."
):
    print(chunk.text, end="", flush=True)
```

### Generation Config

```python
config = types.GenerateContentConfig(
    temperature=1.0,
    top_k=40,
    top_p=0.95,
    max_output_tokens=8192,
    thinking_config=types.ThinkingConfig(thinking_budget=1024),  # enable CoT
)

response = client.models.generate_content(
    model="gemma-4-26b-a4b",
    contents="Solve this step by step: ...",
    config=config,
)
```

---

## Vertex AI

For production workloads with SLA, regional data residency, or enterprise billing.

```python
pip install google-cloud-aiplatform
```

```python
import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project="YOUR_PROJECT_ID", location="us-central1")

model = GenerativeModel("google/gemma-4-27b-it@001")
response = model.generate_content("Hello, Gemma!")
print(response.text)
```

### Available Models on Vertex

- `google/gemma-4-27b-it@001`
- `google/gemma-3-27b-it@001`
- `google/gemma-2-27b-it@001`
- Check Vertex AI Model Garden for current catalog

### Batch Prediction (Vertex)

```python
from google.cloud import aiplatform

job = aiplatform.BatchPredictionJob.create(
    model_name="google/gemma-3-27b-it",
    instances_format="jsonl",
    gcs_source=["gs://your-bucket/inputs.jsonl"],
    gcs_destination_prefix="gs://your-bucket/outputs/",
)
```

---

## HuggingFace Inference

### Via `transformers`

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_id = "google/gemma-3-27b-it"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    torch_dtype=torch.bfloat16,
)

messages = [{"role": "user", "content": "Hello!"}]
inputs = tokenizer.apply_chat_template(
    messages,
    return_tensors="pt",
    return_dict=True,
).to("cuda")

outputs = model.generate(**inputs, max_new_tokens=512)
print(tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True))
```

**Important**: Always use `apply_chat_template` — do not manually construct the prompt. Gemma's chat template wraps messages in `<start_of_turn>user\n...<end_of_turn>` tokens that the model requires.

### HuggingFace Inference API (Serverless)

```python
from huggingface_hub import InferenceClient

client = InferenceClient("google/gemma-3-27b-it", token="hf_...")
response = client.text_generation(
    "<start_of_turn>user\nHello!<end_of_turn>\n<start_of_turn>model\n",
    max_new_tokens=256,
    temperature=1.0,
)
```

---

## Rate Limits and Quotas

| Tier | RPM | TPM |
|------|-----|-----|
| Google AI Studio (Free) | 15 | 1,000,000 |
| Google AI Studio (Paid) | 1,000 | varies by model |
| Vertex AI | Quota-based, configurable | — |

For sustained production throughput, deploy a self-hosted instance (llama.cpp, vLLM) or use Vertex AI with quota increases.

---

## Thinking / Chain-of-Thought

Gemma 4 supports internal reasoning via a thinking budget:

```python
config = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_budget=2048)
)
```

The model generates hidden reasoning before the final answer. The response object contains both `thinking` and `text` fields when enabled.

**Gotcha**: In llama.cpp and Ollama, thinking tags (`<think>...</think>`) sometimes do not close properly during agentic tasks, causing the model to output its reasoning process. See [gotchas.md](gotchas.md).
