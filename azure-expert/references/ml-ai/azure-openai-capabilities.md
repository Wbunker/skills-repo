# Azure OpenAI Service — Capabilities

## Service Overview

Azure OpenAI Service provides REST API access to OpenAI's powerful language models with the security, compliance, and regional availability of Azure. Key differentiators from OpenAI.com:

- **Data privacy**: Your prompts and completions are not used to train OpenAI or Microsoft models.
- **Compliance**: SOC 2, ISO 27001, HIPAA BAA, FedRAMP High (selected regions), GDPR.
- **Private networking**: Deploy behind a private endpoint within your VNet — no public internet exposure.
- **Azure RBAC**: Access controlled via Entra ID + Azure role assignments, not just API keys.
- **Content filtering**: Configurable built-in safety classifiers, adjustable per deployment.
- **SLA-backed**: Enterprise SLA with provisioned throughput options.

---

## Available Model Families

| Model Family | Models | Best For |
|---|---|---|
| **GPT-4o** | gpt-4o, gpt-4o-mini | Default recommendation — multimodal (text + vision), fast, cost-efficient |
| **o1 / o3** | o1, o1-mini, o3, o3-mini | Complex reasoning, math, code, chain-of-thought |
| **GPT-4 Turbo** | gpt-4-turbo | Legacy; prefer GPT-4o for new workloads |
| **GPT-3.5 Turbo** | gpt-3.5-turbo | Legacy; fine-tuning supported, low cost |
| **DALL-E** | dall-e-3 | Image generation from text prompts |
| **Whisper** | whisper | Speech-to-text, 100+ language transcription |
| **Text Embedding** | text-embedding-3-small, text-embedding-3-large, text-embedding-ada-002 | Vector embeddings for RAG, semantic search, similarity |

### Model Notes

- **GPT-4o** is the recommended default for new applications — lower cost and latency than GPT-4 Turbo with equivalent or better quality.
- **o1/o3 series** use extended thinking (chain-of-thought) internally; not suited for streaming or real-time applications. Best for complex analytical tasks.
- **text-embedding-3-large** (3072 dimensions) outperforms ada-002 on MTEB benchmarks; use `text-embedding-3-small` for cost-sensitive workloads.
- Model availability varies by region — check the [Azure OpenAI models documentation](https://learn.microsoft.com/azure/ai-services/openai/concepts/models) for region-to-model mapping.

---

## Deployments

A **deployment** is an instance of a model within an Azure OpenAI resource. Multiple deployments of different models (or the same model) can exist within one resource.

### Deployment Types

| Type | Description | Best For |
|---|---|---|
| **Standard** | Shared compute, pay-per-token, subject to TPM/RPM quotas | Dev, test, moderate traffic |
| **Global Standard** | Requests routed globally to available capacity, higher default quota | High-throughput production at lower cost |
| **Provisioned Throughput Unit (PTU)** | Reserved dedicated compute, monthly commitment, predictable latency | Mission-critical, SLA-sensitive production workloads |
| **Global Provisioned** | PTU with global routing | Highest throughput, predictable latency |

### Deployment Configuration

```json
{
  "model": "gpt-4o",
  "deploymentName": "gpt-4o-prod",
  "sku": {
    "name": "Standard",
    "capacity": 100
  }
}
```

- `capacity` = tokens-per-minute (TPM) quota in thousands (100 = 100K TPM for Standard).
- A single resource can host multiple deployments. Deployments are named independently from models.

---

## Quota and Throttling

Quotas are enforced per **subscription per region per model**.

| Limit Type | Description |
|---|---|
| **TPM (Tokens Per Minute)** | Total tokens (prompt + completion) processed per minute |
| **RPM (Requests Per Minute)** | Maximum API calls per minute |

- `429 TooManyRequests` is returned when limits are exceeded.
- Use exponential backoff with jitter for retry logic.
- Request quota increases via the Azure portal (Quotas blade in Azure OpenAI).
- **PTU** bypasses TPM/RPM limits with dedicated capacity.

---

## Key API Capabilities

### Chat Completions

The primary API for conversational and instruction-following tasks.

```python
response = client.chat.completions.create(
    model="gpt-4o-prod",  # deployment name
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain Azure OpenAI deployments."}
    ],
    max_tokens=1000,
    temperature=0.7,
    stream=True  # streaming response
)
```

### Completions (Legacy)

Text-in/text-out; only supported on older models (GPT-3.5-instruct, text-davinci-003). Avoid for new workloads.

### Embeddings

Convert text to high-dimensional vectors for semantic search, RAG, clustering.

```python
response = client.embeddings.create(
    model="text-embedding-3-small",  # deployment name
    input=["Azure OpenAI is enterprise-ready.", "ML models on Azure."]
)
vector = response.data[0].embedding  # list of floats
```

### DALL-E (Image Generation)

```python
response = client.images.generate(
    model="dall-e-3",
    prompt="A futuristic data center in the style of a watercolor painting",
    size="1024x1024",
    quality="standard",  # or "hd"
    n=1
)
image_url = response.data[0].url
```

### Whisper (Speech-to-Text)

```python
with open("audio.mp3", "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        model="whisper",
        file=audio_file,
        language="en"
    )
print(transcript.text)
```

### Realtime API (Audio)

WebSocket-based low-latency audio streaming for voice applications. Supports bidirectional audio, function calling, VAD (voice activity detection). Available for gpt-4o-realtime-preview.

### Assistants API

Stateful assistant with persistent threads, tool use, and file handling:

| Component | Description |
|---|---|
| **Assistant** | A configured AI agent with instructions, model, and tools |
| **Thread** | Conversation session (messages stored server-side) |
| **Message** | User or assistant turn within a thread |
| **Run** | Execution of an assistant on a thread |
| **File** | Uploaded document for analysis or retrieval |
| **Vector Store** | Index of files for file search (RAG) |

**Tools available**: `code_interpreter` (executes Python), `file_search` (RAG over uploaded files), `function` (custom tool calling).

```python
assistant = client.beta.assistants.create(
    name="Data Analyst",
    instructions="Analyze data and produce insights.",
    model="gpt-4o-prod",
    tools=[{"type": "code_interpreter"}, {"type": "file_search"}]
)
```

---

## Fine-Tuning

Fine-tuning adapts a base model to your specific data, format, or style.

| Supported Models | Notes |
|---|---|
| gpt-4o-mini | Recommended for fine-tuning — capable and cost-efficient |
| gpt-3.5-turbo | Widely fine-tuned, lower baseline capability |
| gpt-4o (preview) | Limited availability |

### Training Data Format (JSONL)

```jsonl
{"messages": [{"role": "system", "content": "You extract named entities."}, {"role": "user", "content": "John Smith visited Seattle."}, {"role": "assistant", "content": "Person: John Smith, Location: Seattle"}]}
{"messages": [{"role": "system", "content": "You extract named entities."}, {"role": "user", "content": "Acme Corp is based in New York."}, {"role": "assistant", "content": "Organization: Acme Corp, Location: New York"}]}
```

- Minimum ~10 examples; recommended 50-100+ for meaningful improvement.
- Training files uploaded via `client.files.create(purpose="fine-tune")`.
- Fine-tuned models appear as custom deployments in your resource.

---

## Content Filtering

All Azure OpenAI deployments include built-in content filtering by default.

### Default Filter Categories

| Category | Description |
|---|---|
| Hate | Derogatory content targeting protected groups |
| Violence | Descriptions of physical violence or threats |
| Sexual | Explicit sexual content |
| Self-harm | Content promoting self-harm or suicide |

### Severity Levels

`safe` → `low` → `medium` → `high` — configurable threshold per category (block at medium+, high+, etc.)

### Custom Policies

- **Custom blocklists**: Block specific terms, regex patterns, or phrases.
- **Prompt shield**: Detect and block prompt injection / jailbreak attempts.
- **Groundedness detection**: Verify completions are grounded in provided context.
- Policy configurations adjustable per deployment via Azure portal or REST API.
- Some filter relaxations require Microsoft approval (e.g., enabling adult content for approved use cases).

---

## RAG Pattern with Azure AI Search

The standard retrieval-augmented generation architecture on Azure:

```
User Query
    │
    ▼
text-embedding-3-small  ──► Query Vector
    │
    ▼
Azure AI Search  ──► Hybrid Search (BM25 + Vector + Semantic Ranking)
    │
    ▼
Retrieved Chunks (top-k)
    │
    ▼
GPT-4o  ──► Grounded Answer
```

**Key components**:
1. **Ingestion**: Chunk documents → embed with `text-embedding-3-*` → index in Azure AI Search with vector field.
2. **Retrieval**: Embed query → vector search (HNSW) + keyword (BM25) → semantic ranker reranks top-50.
3. **Generation**: Pass retrieved chunks as context in system prompt → GPT-4o generates grounded answer.

### On Your Data

Azure OpenAI "On Your Data" feature provides built-in RAG without custom code:
- Connect directly to Azure AI Search index via portal or API.
- Handles retrieval and prompt construction automatically.
- Supports intent detection, follow-up questions, citation generation.
- Available in Azure OpenAI Studio / AI Foundry portal.

```python
response = client.chat.completions.create(
    model="gpt-4o-prod",
    messages=[{"role": "user", "content": "What is our refund policy?"}],
    extra_body={
        "data_sources": [{
            "type": "azure_search",
            "parameters": {
                "endpoint": "https://mysearch.search.windows.net",
                "index_name": "policy-docs",
                "authentication": {"type": "system_assigned_managed_identity"}
            }
        }]
    }
)
```

---

## Azure OpenAI Studio → AI Foundry

Azure OpenAI Studio is being merged into **Azure AI Foundry** (ai.azure.com). Existing Studio URLs redirect to AI Foundry. Foundry provides the same model deployment, playground, and On Your Data experiences plus additional capabilities (model catalog, prompt flow, evaluation).

---

## Networking Options

| Option | Description |
|---|---|
| **Public** | Default — accessible from any IP (optionally restrict by IP/VNET rules) |
| **Selected Networks** | Firewall rules: restrict to specific IP ranges or VNet service endpoints |
| **Private Endpoint** | Resource injected into your VNet — no public internet exposure, DNS via Private DNS Zone |
| **Approved VNet** | Microsoft-managed VNet peering for specific scenarios |

Private endpoint recommended for production workloads. Pair with `az network private-dns zone` for DNS resolution.

---

## Provisioned Throughput Units (PTU)

PTU provides dedicated model compute capacity:

- **Predictable latency**: No noisy-neighbor effects from shared capacity.
- **Monthly commitment**: Reserve PTUs for 1 month or 1 year (discounted).
- **No TPM/RPM throttling**: Throughput limited only by provisioned PTUs.
- **Sizing**: PTU capacity measured per model — GPT-4o requires more PTUs than GPT-4o mini for equivalent throughput.
- **Overflow**: Configure standard deployment as fallback when PTU is saturated.

Use the [Azure OpenAI PTU Sizing Calculator](https://oai.azure.com/portal/calculator) to estimate PTU requirements from expected TPS (tokens per second).

---

## Authentication Patterns

| Method | Recommended | Notes |
|---|---|---|
| API Key | No (dev only) | Key stored in Key Vault; rotate regularly |
| Managed Identity | Yes (production) | `DefaultAzureCredential` picks up system/user-assigned MI automatically |
| Entra ID user token | Yes (interactive) | For developer testing via CLI |

```python
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)

client = AzureOpenAI(
    azure_endpoint="https://myresource.openai.azure.com/",
    azure_ad_token_provider=token_provider,
    api_version="2024-10-01-preview"
)
```
