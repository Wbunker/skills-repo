# Azure AI Foundry — Capabilities

## Service Overview

Azure AI Foundry (ai.azure.com) is Microsoft's unified platform for building, evaluating, deploying, and monitoring generative AI applications and agents. It consolidates Azure OpenAI Studio, Azure ML Studio (for GenAI), and Azure AI Services management into a single portal and SDK experience.

**Key principle**: AI Foundry is the "application layer" for GenAI — while Azure Machine Learning remains the platform for classical ML/MLOps.

---

## Hub and Project Architecture

AI Foundry uses a two-tier organizational model:

### Hub (Top-Level Resource)

The hub is the organizational container for shared resources, security, and governance:

- Backed by an **Azure ML Hub Workspace** resource type.
- Provides shared: connections (API keys/endpoints), compute, network configuration.
- Managed by platform/ops teams — one hub per organization or team is common.
- Associates with: Azure Storage, Key Vault, Application Insights, Container Registry.
- Controls network isolation (public, managed VNet, private endpoint).
- All projects within a hub inherit the hub's network and identity configuration.

### Project (Application Workspace)

Projects are isolated workspaces for a specific AI application or development team:

- Backed by an **Azure ML Project Workspace** resource type within the hub.
- Each project gets its own: storage, deployments, experiment history, evaluation runs.
- Multiple projects can share the hub's connections and compute.
- IAM applied at project level for developer access control.
- Billing tracked at project level for cost attribution.

```
Azure Subscription
└── Resource Group
    └── AI Foundry Hub (hub-myorg)
        ├── Connections (Azure OpenAI, AI Search, storage...)
        ├── Compute pools
        └── Projects
            ├── Project: customer-support-bot
            ├── Project: document-intelligence-app
            └── Project: internal-copilot
```

---

## AI Foundry Portal

The portal at **ai.azure.com** provides a unified UX replacing multiple previous studios:

| Previous Tool | Now In AI Foundry |
|---|---|
| Azure OpenAI Studio | AI Foundry → your project → Playgrounds |
| Azure ML Studio (GenAI) | AI Foundry → Prompt Flow, Evaluation |
| Azure AI Services management | AI Foundry → Connections |

### Portal Sections

- **Home**: Hub/project overview, quickstarts
- **Model Catalog**: Browse and deploy 1,600+ models
- **Playgrounds**: Chat, Assistants, Images, Audio, Real-time Audio
- **Prompt Flow**: Build and test LLM workflows
- **Evaluation**: Run and view model/app evaluations
- **Fine-tuning**: Fine-tune supported models
- **Deployments**: Manage model deployments
- **Connections**: Manage external resource connections
- **Settings**: Hub-level configuration, network, access control

---

## Model Catalog

AI Foundry's model catalog provides access to 1,600+ AI models from Microsoft and partners:

### Model Providers

| Provider | Notable Models |
|---|---|
| Azure OpenAI | GPT-4o, o1, o3, DALL-E 3, Whisper, text-embedding-3 |
| Meta | LLaMA 3.1 (8B, 70B, 405B), LLaMA 3.2 (vision) |
| Mistral AI | Mistral Large, Mixtral 8x7B, Mistral Small |
| Cohere | Command R+, Embed v3, Rerank |
| AI21 Labs | Jamba Instruct |
| NVIDIA | Nemotron, NIM endpoints |
| Hugging Face | Thousands of open-source models |
| Microsoft | Phi-4, Phi-3.5-mini, Florence-2 |

### Deployment Options

| Option | Description | Billing |
|---|---|---|
| **Serverless API (MaaS)** | Deploy without managing infrastructure; Microsoft hosts | Pay-per-token |
| **Managed Compute** | Deploy on dedicated VMs in your subscription | Per-hour VM cost |
| **Azure OpenAI Service** | For Azure OpenAI models specifically | Standard/PTU pricing |

**Serverless API** (Model as a Service) is ideal for: LLaMA 3, Phi-4, Mistral, Cohere — no cluster management, instant deployment, pay-per-token pricing.

```python
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

# Serverless API endpoint (MaaS)
client = ChatCompletionsClient(
    endpoint="https://myproject.eastus.models.ai.azure.com",
    credential=AzureKeyCredential("<key>")
)

response = client.complete(
    messages=[{"role": "user", "content": "Explain transformer architecture."}],
    model="llama-3-1-70b-instruct",
    max_tokens=500
)
```

---

## Prompt Flow

Prompt Flow is AI Foundry's LLM application orchestration framework for building, testing, and deploying LLM workflows.

### Flow Types

| Type | Description |
|---|---|
| **Standard Flow** | DAG-based workflow with Python nodes, LLM nodes, tool nodes |
| **Chat Flow** | Conversational multi-turn flow with history management |
| **Evaluation Flow** | Scoring flow for assessing another flow's outputs |

### Flow Nodes

- **LLM Node**: Calls a model deployment with a Jinja2 prompt template.
- **Python Node**: Custom Python function for data transformation, API calls, business logic.
- **Tool Node**: Pre-built integrations (Azure AI Search, Bing grounding, Content Safety).
- **Prompt Node**: Renders a Jinja2 template into a string.

### Connections

Connections store credentials for external resources used within flows:

```python
# Connection types managed in AI Foundry
# AzureOpenAI, AzureAISearch, AzureContentSafety, Custom (generic key-value)
```

### Evaluation Flow Example

```yaml
# eval_flow/flow.dag.yaml
inputs:
  question:
    type: string
  answer:
    type: string
  ground_truth:
    type: string
outputs:
  groundedness_score:
    type: double
    reference: ${check_groundedness.output}
nodes:
- name: check_groundedness
  type: llm
  source:
    type: code
    path: check_groundedness.jinja2
  inputs:
    answer: ${inputs.answer}
    ground_truth: ${inputs.ground_truth}
  connection: azure-openai-connection
  api: chat
  model: gpt-4o-prod
```

---

## Evaluation

Built-in AI application evaluation with standard and custom metrics:

### Built-in Metrics

| Metric | Measures | Method |
|---|---|---|
| **Groundedness** | Whether answer is supported by context | LLM-as-judge |
| **Relevance** | Whether answer addresses the question | LLM-as-judge |
| **Coherence** | Logical flow and readability of answer | LLM-as-judge |
| **Fluency** | Grammatical quality of answer | LLM-as-judge |
| **Similarity** | Semantic similarity to ground truth | Embedding cosine |
| **F1 Score** | Token-level overlap with ground truth | Statistical |
| **Violence/Hate/Sexual/Self-harm** | Safety content detection | Classifier model |

### Custom Evaluators

Define custom Python evaluators for domain-specific metrics:

```python
from promptflow.core import tool

@tool
def my_evaluator(answer: str, expected: str) -> dict:
    """Custom evaluator: checks if answer contains required keywords."""
    required_keywords = extract_keywords(expected)
    found = [kw for kw in required_keywords if kw.lower() in answer.lower()]
    score = len(found) / len(required_keywords) if required_keywords else 1.0
    return {"keyword_match_score": score}
```

### Running Evaluations

```bash
# Run evaluation via prompt flow CLI
pf run create \
  --flow ./eval_flow \
  --data ./test_data.jsonl \
  --column-mapping question='${data.question}' answer='${data.answer}' ground_truth='${data.ground_truth}' \
  --stream
```

---

## AI Safety

### Content Safety Integration

- Automatic content safety evaluation during model evaluation runs.
- Detect: violence, hate, sexual content, self-harm, jailbreak attempts, prompt injection.
- **Prompt Shields**: Detect jailbreak attempts in user prompts and indirect attacks in documents.
- **Groundedness Detection**: Verify model responses are factually grounded in provided context.

### Red Teaming

AI Foundry provides built-in red teaming capabilities to identify safety vulnerabilities:
- Automated adversarial prompt generation.
- Systematic evaluation across harm categories.
- Produces safety evaluation report with risk scores.

---

## Azure AI Search Integration

AI Foundry has deep integration with Azure AI Search for RAG workflows:

- **Vector Search**: HNSW index, inner product / cosine similarity.
- **Hybrid Search**: BM25 keyword + vector search combined.
- **Semantic Ranking**: ML re-ranking of top results for improved relevance.
- **Integrated Vectorization**: Auto-embed documents at indexing time using Azure OpenAI embeddings.

### Index Creation from AI Foundry

Via portal: AI Foundry → your project → Indexes → Create → upload files or connect to source → auto-chunks and embeds → creates AI Search index.

---

## Agent Frameworks

### Azure AI Agent Service

Enterprise-grade agent platform built on the Assistants API with extensions:

- **Built-in tools**: File search, Code Interpreter, Bing grounding, Azure AI Search, Azure Functions.
- **Managed threads/state**: Server-side conversation history, no client-side storage.
- **Enterprise security**: Private networking, managed identity, customer-managed keys.
- Accessed via `azure-ai-projects` SDK.

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient.from_connection_string(
    conn_str="<project-connection-string>",
    credential=DefaultAzureCredential()
)

agent = project_client.agents.create_agent(
    model="gpt-4o-prod",
    name="Support Agent",
    instructions="You are a helpful customer support agent.",
    tools=[{"type": "file_search"}, {"type": "bing_grounding"}]
)
```

### AutoGen Integration

Microsoft's multi-agent orchestration framework for complex agent workflows:
- Multiple collaborating agents (AssistantAgent, UserProxyAgent, GroupChat).
- Built-in code execution, tool use, human-in-the-loop.
- Available via `pyautogen` package; integrates with AI Foundry model endpoints.

### Semantic Kernel

Open-source SDK for building AI-powered applications:
- Plugin architecture: connect AI to existing code and APIs.
- Memory: vector store integration for context retrieval.
- Planner: automatic task decomposition and execution.
- Supports Python, C#, Java.

---

## Connections Management

Connections store credentials and endpoint information for resources used within hub/projects:

| Connection Type | Resources |
|---|---|
| Azure OpenAI | OpenAI resource endpoint + key or MI |
| Azure AI Search | Search service endpoint + admin key or MI |
| Azure Blob Storage | Storage account + connection string |
| Azure Content Safety | Content Safety resource |
| Custom | Generic key-value pairs for any API |
| Serverless Model | MaaS endpoint key |

Connections defined at hub level are shared across all projects. Project-level connections are isolated.

---

## Grounding with Bing

Real-time web data retrieval for RAG applications:
- Provides Bing Search API integration as a tool within AI Agent Service and Prompt Flow.
- Agent can search Bing for current events, product information, and facts.
- Responses grounded in web content with citations.
- Requires Bing Search resource in Azure subscription.

```python
# Bing grounding tool definition for AI Agent Service
bing_tool = BingGroundingTool(connection_id=bing_connection.id)
agent = project_client.agents.create_agent(
    model="gpt-4o-prod",
    tools=bing_tool.definitions,
    tool_resources=bing_tool.resources
)
```
