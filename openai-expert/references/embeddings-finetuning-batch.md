# Embeddings, Fine-tuning, and Batch API

---

## Embeddings

### Endpoint

`POST https://api.openai.com/v1/embeddings`

```python
from openai import OpenAI
client = OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-small",
    input="The quick brown fox jumps over the lazy dog",
    encoding_format="float"  # or "base64"
)

embedding = response.data[0].embedding  # list of floats
```

### Models

| Model | Dimensions | Price | Use Case |
|-------|-----------|-------|---------|
| `text-embedding-3-small` | 1536 | $0.02/M tokens | Fast retrieval, semantic search, clustering |
| `text-embedding-3-large` | 3072 | $0.13/M tokens | Higher accuracy, domain-specific retrieval |

`text-embedding-3-small` is sufficient for most RAG applications. Use `text-embedding-3-large` when retrieval quality is critical.

### Truncation

Both models support `dimensions` parameter to reduce output size:
```python
response = client.embeddings.create(
    model="text-embedding-3-large",
    input="...",
    dimensions=512  # reduce from 3072 to save storage/compute
)
```

### Fine-tuning Embeddings

Custom-tuned embedding models for domain-specific retrieval:
- Input: 100–500 labeled similar-text pairs
- Training time: 1–2 hours
- Cost: 10% more per million tokens than base model
- Accuracy improvement: 15–30% on domain-specific retrieval tasks

---

## Fine-tuning

### What It Is

Supervised fine-tuning (SFT): upload a dataset of examples → OpenAI trains a custom model → you get a custom model ID to deploy.

Use cases: specific tone/style, domain jargon, consistent output format, reducing prompt length by teaching behavior rather than describing it.

### Endpoint

```
POST /v1/fine_tuning/jobs
```

### Workflow

```python
from openai import OpenAI
client = OpenAI()

# 1. Upload training file
with open("training_data.jsonl", "rb") as f:
    file = client.files.create(file=f, purpose="fine-tune")

# 2. Create fine-tuning job
job = client.fine_tuning.jobs.create(
    training_file=file.id,
    model="gpt-4o-mini-2024-07-18",
    hyperparameters={
        "n_epochs": "auto",
        "batch_size": "auto",
        "learning_rate_multiplier": "auto"
    }
)

# 3. Monitor status
job_status = client.fine_tuning.jobs.retrieve(job.id)
print(job_status.status)  # queued, running, succeeded, failed, cancelled

# 4. Use the fine-tuned model
response = client.chat.completions.create(
    model=job_status.fine_tuned_model,  # e.g., "ft:gpt-4o-mini:org:custom:abc123"
    messages=[...]
)
```

### Training Data Format

JSONL file, each line is a complete conversation:
```jsonl
{"messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is 2+2?"}, {"role": "assistant", "content": "4"}]}
{"messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "Capital of France?"}, {"role": "assistant", "content": "Paris"}]}
```

### Hyperparameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| `n_epochs` | `"auto"` | Passes through training data. Auto = 3–5 typically |
| `batch_size` | `"auto"` | Training batch size |
| `learning_rate_multiplier` | `"auto"` | Scales the learning rate |

All default to `"auto"` for automatic optimization. Manual tuning rarely needed.

### Data Requirements

| Examples | Expected Result |
|----------|----------------|
| 10 (minimum) | Possible to train, minimal improvement |
| 50–100 | Recommended starting point; clear improvements visible |
| 100–500 | Good results for most use cases |
| 1000+ | Significant behavioral change |

### Supported Models for Fine-tuning

- `gpt-4o-mini-2024-07-18`
- `gpt-4.1`, `gpt-4.1-mini`
- `gpt-3.5-turbo` variants (legacy)

---

## Batch API

### What It Is

Asynchronous bulk processing. Submit up to 50,000 requests at once. Results returned within 24 hours at **50% of standard API pricing**.

Best for: large-scale classification, summarization, embedding generation, evaluation, data enrichment — any task where you don't need real-time results.

### Supported Endpoints

- `/v1/chat/completions`
- `/v1/embeddings`
- `/v1/completions` (legacy)

### Limits

| Limit | Value |
|-------|-------|
| Max requests per batch | 50,000 |
| Max input file size | 200 MB |
| Max embedding inputs per batch | 50,000 |
| Result turnaround | Within 24 hours |

### Workflow

```python
from openai import OpenAI
import json

client = OpenAI()

# 1. Prepare JSONL input file
requests = [
    {
        "custom_id": f"request-{i}",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4.1",
            "messages": [{"role": "user", "content": f"Summarize: {text}"}],
            "max_tokens": 100
        }
    }
    for i, text in enumerate(texts)
]

with open("batch_input.jsonl", "w") as f:
    for req in requests:
        f.write(json.dumps(req) + "\n")

# 2. Upload input file
with open("batch_input.jsonl", "rb") as f:
    input_file = client.files.create(file=f, purpose="batch")

# 3. Create batch job
batch = client.batches.create(
    input_file_id=input_file.id,
    endpoint="/v1/chat/completions",
    completion_window="24h"
)

# 4. Poll for completion
import time
while True:
    batch_status = client.batches.retrieve(batch.id)
    if batch_status.status in ("completed", "failed", "expired", "cancelled"):
        break
    time.sleep(60)

# 5. Download results
output_file = client.files.content(batch_status.output_file_id)
results = [json.loads(line) for line in output_file.text.strip().split("\n")]

# Each result contains:
# {"id": "...", "custom_id": "request-0", "response": {"body": {...}}, "error": null}
for result in results:
    if result["error"] is None:
        content = result["response"]["body"]["choices"][0]["message"]["content"]
```

### Pricing Comparison

| Model | Standard Input | Batch Input | Savings |
|-------|---------------|-------------|---------|
| GPT-4.1 | $2.00/M | $1.00/M | 50% |
| GPT-4.1 mini | $0.40/M | $0.20/M | 50% |
| GPT-4o | $2.50/M | $0.25/M (listed) | varies |
| GPT-4o-mini | $0.15/M | $0.075/M | 50% |
| o3 | $2.00/M | $1.00/M | 50% |
| o4-mini | $1.10/M | $0.55/M | 50% |
| text-embedding-3-small | $0.02/M | $0.01/M | 50% |
