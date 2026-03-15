# AWS Amazon Bedrock — Capabilities Reference
For CLI commands, see [bedrock-cli.md](bedrock-cli.md).

## Amazon Bedrock

**Purpose**: Fully managed service providing secure, enterprise-grade access to 100+ high-performing foundation models (FMs) from leading AI providers, enabling generative AI applications without managing infrastructure.

### Supported Foundation Model Providers

| Provider | Models |
|---|---|
| **Amazon** | Nova Micro, Nova Lite, Nova Pro, Nova Canvas, Nova Reel, Titan Text, Titan Embeddings |
| **Anthropic** | Claude Opus, Claude Sonnet, Claude Haiku (multiple versions) |
| **Meta** | Llama 3.x (8B, 70B, 405B variants) |
| **Mistral** | Mistral 7B, Mixtral 8x7B, Mistral Large |
| **Cohere** | Command R, Command R+, Embed |
| **AI21 Labs** | Jamba Instruct |
| **Stability AI** | Stable Diffusion (image generation) |
| **DeepSeek** | DeepSeek V3 |

### Model ID Format

```
anthropic.claude-3-5-sonnet-20241022-v2:0
amazon.nova-pro-v1:0
meta.llama3-70b-instruct-v1:0
mistral.mistral-large-2402-v1:0
```

### API Modes

| Mode | API Call | Use Case |
|---|---|---|
| **InvokeModel** | `bedrock-runtime:InvokeModel` | Single request; model-specific request/response bodies |
| **InvokeModelWithResponseStream** | `bedrock-runtime:InvokeModelWithResponseStream` | Streaming tokens as they are generated |
| **Converse** | `bedrock-runtime:Converse` | Unified multi-turn API; normalizes request/response across all models |
| **ConverseStream** | `bedrock-runtime:ConverseStream` | Streaming version of Converse |
| **StartAsyncInvoke** | `bedrock-runtime:StartAsyncInvoke` | Long-running batch inference; results to S3 |

### Bedrock Agents

**Purpose**: Autonomous AI agents that orchestrate multi-step tasks by combining foundation models with action execution and knowledge retrieval.

| Concept | Description |
|---|---|
| **Agent** | Configured FM + instructions + action groups + optional knowledge bases |
| **Action group** | Set of API operations the agent can call; defined via OpenAPI schema or Lambda function |
| **Knowledge base** | Connected data source the agent queries for context (RAG) |
| **Memory** | Short-term (session) and long-term memory retention across conversations |
| **Code interpreter** | Built-in capability for the agent to write and execute code |
| **Agent alias** | Immutable pointer to a specific agent version; use in production integrations |
| **TSTALIASID** | Reserved alias for testing in-progress (draft) agent |

**Agent lifecycle**: Create → Add action groups and/or knowledge bases → Prepare → Create alias → Invoke via `bedrock-agent-runtime:InvokeAgent`.

### Knowledge Bases

**Purpose**: Managed RAG pipeline connecting data sources to vector stores, enabling foundation models to answer questions using your proprietary data.

| Concept | Description |
|---|---|
| **Data source** | Origin of content: Amazon S3, Confluence, SharePoint, Salesforce, web crawl |
| **Vector store** | Stores embeddings for semantic search; options below |
| **Chunking strategy** | How documents are split: fixed-size, semantic, hierarchical, or custom Lambda |
| **Embedding model** | Converts text to vectors; Amazon Titan Embeddings or Cohere Embed |
| **Ingestion job** | Process that reads data source, chunks, embeds, and stores in vector store |
| **Retrieve API** | Returns relevant chunks without generating a response |
| **RetrieveAndGenerate API** | Retrieves context then generates a grounded response |
| **Citations** | Source document references included in generated responses |

**Supported vector stores**:

| Store | Notes |
|---|---|
| **Amazon OpenSearch Serverless** | Default; auto-created by console; managed |
| **Amazon Aurora (pgvector)** | PostgreSQL-compatible; customer-managed |
| **Amazon RDS (pgvector)** | PostgreSQL with pgvector extension |
| **Pinecone** | Third-party; customer-managed |
| **Redis Enterprise** | Third-party; customer-managed |
| **MongoDB Atlas** | Third-party; customer-managed |

**Multimodal support**: Image extraction from documents, image-based queries, multimodal embedding models for combined text + image retrieval.

### Guardrails

**Purpose**: Configurable safety layer applied to both inputs and outputs across any foundation model to enforce application policies.

| Filter Type | What It Does |
|---|---|
| **Content filters** | Block/flag harmful content: Hate, Insults, Sexual, Violence, Misconduct, Prompt Attack; configurable strength per category |
| **Denied topics** | Define topic names + descriptions; Bedrock denies inputs/outputs matching those topics |
| **Word filters** | Block exact words or phrases; built-in profanity list available |
| **Sensitive information (PII)** | Detect and block or redact PII: SSN, DOB, address, phone, email, and more; supports custom regex |
| **Contextual grounding** | Detect hallucinations in RAG responses; checks factual grounding against retrieved context |
| **Automated reasoning** | Validate accuracy against logical rules; detect hallucinations and flag unstated assumptions |

**Key concepts**:
- Guardrails are versioned; create a working draft, publish a version when satisfied
- Apply via guardrail ID + version number on any `InvokeModel`, `Converse`, or `RetrieveAndGenerate` call
- `ApplyGuardrail` API allows standalone guardrail evaluation without invoking a model
- **Selective evaluation**: Tag content blocks to exclude system prompts or conversation history from evaluation in RAG/chat apps

### Model Customization

| Feature | Description |
|---|---|
| **Fine-tuning** | Adapt a model to a specific task using labeled examples (instruction/response pairs) |
| **Continued pre-training** | Extend training on unlabeled domain-specific data to improve domain knowledge |
| **Model distillation** | Train a smaller (student) model to replicate the behavior of a larger (teacher) model |
| **Provisioned throughput** | Reserve dedicated model capacity for consistent latency; required for custom models in production |

### Model Evaluation

Managed service to compare and evaluate foundation model performance:
- **Automatic evaluation**: Benchmark on built-in datasets (accuracy, toxicity, robustness, etc.)
- **Human evaluation**: Route model outputs to human reviewers via your own workforce or AWS Managed
- **Evaluation jobs**: Compare multiple models or prompts; results stored in S3

### Additional Capabilities

| Feature | Description |
|---|---|
| **Cross-region inference** | Route requests across regions for higher throughput and availability via inference profiles |
| **Bedrock Studio** | Web-based IDE for building, testing, and sharing generative AI applications |
| **Prompt management** | Save, version, and share prompts; use in applications via prompt ARN |
| **Prompt routing** | Intelligently route prompts to models based on cost/performance tradeoffs |
| **Batch inference** | Process large datasets of prompts asynchronously; output to S3 |
| **Model invocation logging** | Log all inference requests/responses to S3 or CloudWatch Logs for compliance |

---

## Amazon Nova Models

**Purpose**: Amazon's own family of foundation models available exclusively through Amazon Bedrock, optimized for performance and cost across different modalities.

### Text Models

| Model | Tier | Context Window | Key Strengths |
|---|---|---|---|
| **Nova Micro** | Lowest cost | 128K tokens | Fast, text-only; ideal for simple Q&A, classification, summarization |
| **Nova Lite** | Low cost | 300K tokens | Multimodal (text + image + video); fast and cost-effective |
| **Nova Pro** | Balanced | 300K tokens | Highest accuracy; complex reasoning, agentic tasks, multimodal |

### Media Generation Models

| Model | Output | Key Capabilities |
|---|---|---|
| **Nova Canvas** | Images | Text-to-image, image editing, inpainting/outpainting, background removal; adjustable quality tiers |
| **Nova Reel** | Video | Text-to-video and image-to-video generation; up to 2 minutes; configurable resolution |

### Nova Key Patterns

- All Nova text models support tool use (function calling) and structured output
- Nova Lite and Pro accept images and video as input alongside text
- Nova Canvas supports negative prompts, style presets, and reference images
- Nova models are priced per 1,000 input/output tokens (text) or per image/second of video (media)
