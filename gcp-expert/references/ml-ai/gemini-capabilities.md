# Gemini & Generative AI — Capabilities

## Gemini Models on Vertex AI

All Gemini models are available via Vertex AI with enterprise features including SLAs, CMEK, VPC Service Controls, audit logging, and no-data-training guarantees.

### Current model lineup

| Model | Context Window | Strengths | Best for |
|---|---|---|---|
| `gemini-2.0-flash` | 1M tokens | Fast, cost-efficient, multimodal, low latency | High-volume applications, real-time chat, simple tasks |
| `gemini-2.0-flash-thinking` | 1M tokens | Extended thinking before answering | Math, logic, coding with reasoning transparency |
| `gemini-2.0-pro-exp` | 2M tokens | Strongest reasoning, most capable | Complex analysis, long-document QA, advanced coding |
| `gemini-1.5-pro` | 2M tokens | Mature, stable, very large context | Long-document analysis, video understanding, production workloads |
| `gemini-1.5-flash` | 1M tokens | Fast, efficient, 1.5-generation | Cost-conscious production; familiar 1.5 behavior |
| `gemini-1.0-pro` | 32K tokens | Stable, well-tested | Legacy integrations, simple text tasks |

### Multi-modal inputs
Gemini models accept mixed-modality inputs in a single API call:
- **Text**: any language; code; structured formats (JSON, XML, CSV)
- **Images**: JPEG, PNG, GIF, WebP, BMP, TIFF (up to 3,000 images per request for 1.5 Pro)
- **Video**: MP4, AVI, MOV, MKV, WebM; up to ~2 hours at 1 FPS for 1.5 Pro; audio track included
- **Audio**: WAV, MP3, AAC, OGG, FLAC; up to ~9 hours for 1.5 Pro
- **PDF**: inline document understanding (not just OCR; semantic understanding of layout)
- **Code**: understand and generate code in 20+ languages

### Output formats
- **Text**: natural language responses
- **Code**: code blocks with syntax, explanation, and test generation
- **Structured JSON**: use `response_mime_type: "application/json"` with a `response_schema` to force valid JSON output matching a schema
- **Streaming**: token-by-token streaming for real-time UX

---

## Core API Concepts

### GenerativeModel
The entry point for calling Gemini. Instantiate with a model ID:
```python
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Content

vertexai.init(project="my-project", location="us-central1")
model = GenerativeModel("gemini-2.0-flash")
```

### GenerationConfig
Controls the generation behavior:

| Parameter | Type | Effect |
|---|---|---|
| `temperature` | 0.0–2.0 | Higher = more creative/random; 0.0 = deterministic |
| `top_p` | 0.0–1.0 | Nucleus sampling; higher = broader vocabulary |
| `top_k` | 1–40 | Top-k sampling; restricts next token choices |
| `max_output_tokens` | int | Maximum tokens in the response |
| `stop_sequences` | list[str] | Stop generation when any of these strings is produced |
| `response_mime_type` | str | `"text/plain"` or `"application/json"` |
| `response_schema` | Schema | JSON schema for structured output |
| `candidate_count` | 1–8 | Number of independent completions to return |

### System Instructions
A special "system prompt" passed once to configure the model's behavior for the entire conversation. Set at model instantiation:
```python
model = GenerativeModel(
    "gemini-2.0-flash",
    system_instruction="You are a helpful customer support agent for Acme Corp. Always respond in the customer's language."
)
```

### Context Window Management
- Gemini 1.5 Pro and 2.0 Pro: up to 2 million tokens in a single context
- Input tokens are all tokens in the request (system instruction + history + new message + all files)
- Use `model.count_tokens(contents)` to count tokens before sending
- Very long contexts cost more; use Context Caching for repeated large prefixes

### Safety Filters
Gemini applies safety filters for:
- Harassment, hate speech, sexually explicit content, dangerous content
- Each category has a threshold: `BLOCK_NONE`, `BLOCK_LOW_AND_ABOVE`, `BLOCK_MEDIUM_AND_ABOVE`, `BLOCK_ONLY_HIGH`
- Blocked responses include a `finish_reason=SAFETY` and `safety_ratings` in the response
- Safety thresholds can be configured per model call (within API limits)

---

## Grounding

Grounding connects model responses to factual, up-to-date, or private data sources, reducing hallucinations.

### Google Search Grounding
Connect Gemini to live Google Search results:
```python
from vertexai.generative_models import grounding, Tool

google_search_tool = Tool.from_google_search_retrieval(
    grounding.GoogleSearchRetrieval(
        dynamic_retrieval_config=grounding.DynamicRetrievalConfig(
            mode=grounding.DynamicRetrievalConfig.Mode.MODE_DYNAMIC,
            dynamic_threshold=0.8  # use search only if needed above this threshold
        )
    )
)
model = GenerativeModel("gemini-2.0-flash", tools=[google_search_tool])
response = model.generate_content("What is the current stock price of Google?")
```
- Grounded responses include `groundingMetadata` with search queries used and web source citations
- Grounding supports attributions: the model cites which search results support each claim

### Vertex AI Search Grounding (Private Data)
Ground responses in your own enterprise documents indexed in Vertex AI Agent Builder:
```python
from vertexai.generative_models import grounding, Tool

retrieval = grounding.Retrieval(
    source=grounding.VertexAISearch(
        datastore="projects/PROJECT_ID/locations/global/collections/default_collection/dataStores/DATA_STORE_ID"
    )
)
tool = Tool.from_retrieval(retrieval)
model = GenerativeModel("gemini-2.0-flash", tools=[tool])
response = model.generate_content("What is our refund policy?")
```

---

## Function Calling (Tool Use)

Function calling lets you define tools (functions) that the model can decide to call, enabling agentic workflows where the model orchestrates external API calls.

### How it works
1. Define `FunctionDeclaration` objects with name, description, and JSON schema for parameters.
2. Pass them as a `Tool` to the model.
3. The model either returns a `FunctionCall` part (requesting a tool call) or a text response.
4. Your code executes the function and passes the result back as a `FunctionResponse`.
5. The model generates a final response based on the function result.

### Example: weather function
```python
from vertexai.generative_models import FunctionDeclaration, Tool

get_weather = FunctionDeclaration(
    name="get_current_weather",
    description="Get the current weather conditions for a location",
    parameters={
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name, e.g. San Francisco, CA"
            },
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "Temperature unit"
            }
        },
        "required": ["location"]
    }
)

weather_tool = Tool(function_declarations=[get_weather])
model = GenerativeModel("gemini-2.0-flash", tools=[weather_tool])

response = model.generate_content("What's the weather like in Tokyo?")
# If model wants to call the function:
# response.candidates[0].content.parts[0].function_call.name == "get_current_weather"
# response.candidates[0].content.parts[0].function_call.args == {"location": "Tokyo"}
```

### Tool config (force / prevent function calling)
```python
from vertexai.generative_models import ToolConfig

# Force the model to always call a specific function
tool_config = ToolConfig(
    function_calling_config=ToolConfig.FunctionCallingConfig(
        mode=ToolConfig.FunctionCallingConfig.Mode.ANY,
        allowed_function_names=["get_current_weather"]
    )
)

# Prevent all function calling (text only)
tool_config = ToolConfig(
    function_calling_config=ToolConfig.FunctionCallingConfig(
        mode=ToolConfig.FunctionCallingConfig.Mode.NONE
    )
)
```

### Parallel function calls
Gemini 2.0 supports requesting multiple function calls in a single model turn, enabling parallel execution of independent tool calls (e.g., fetch weather AND stock price in parallel).

---

## Multi-turn Conversations (Chat)

```python
chat = model.start_chat(
    history=[
        Content(role="user", parts=[Part.from_text("Hello!")]),
        Content(role="model", parts=[Part.from_text("Hi there! How can I help?")])
    ]
)
response = chat.send_message("Tell me about Vertex AI")
print(response.text)

# Continue the conversation
response2 = chat.send_message("How does it compare to AWS SageMaker?")
```

The `chat` object maintains the conversation history automatically. Access it via `chat.history`.

---

## Structured Output (JSON Mode)

Force the model to produce valid JSON matching a schema:
```python
from vertexai.generative_models import GenerationConfig
import json

response = model.generate_content(
    "Extract the person's name, age, and email from this text: Alice Smith, 34, alice@example.com",
    generation_config=GenerationConfig(
        response_mime_type="application/json",
        response_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "email": {"type": "string"}
            },
            "required": ["name", "age", "email"]
        }
    )
)
data = json.loads(response.text)  # guaranteed valid JSON matching schema
```

---

## Context Caching

For workloads that repeatedly send the same large prefix (long system prompts, reference documents, codebases), Context Caching stores the processed prefix server-side to reduce latency and cost.

- Cache is tied to a specific model + content combination
- Cache has a TTL (default 60 minutes; configurable up to hours)
- Cost: cached tokens billed at a reduced rate (~4x cheaper than fresh tokens)
- Use cases: RAG with a fixed large knowledge base, multi-turn Q&A over a long document, coding assistant with a large codebase loaded

```python
from vertexai.preview.caching import CachedContent

# Create a cache
cache = CachedContent.create(
    model_name="gemini-1.5-pro",
    contents=[
        Part.from_uri("gs://my-bucket/large-report.pdf", mime_type="application/pdf")
    ],
    system_instruction="You are an expert analyst of this report. Answer questions accurately.",
    ttl=datetime.timedelta(hours=2)
)

# Use the cache in subsequent calls
model_with_cache = GenerativeModel.from_cached_content(cache)
response = model_with_cache.generate_content("What was the Q3 revenue?")
```

---

## Batch API (Async Generation)

For non-real-time bulk generation tasks (offline evaluation, batch document processing, dataset annotation):
- Submit a batch of prompts as a JSONL file to Cloud Storage
- Vertex AI processes them asynchronously
- Results written to Cloud Storage or BigQuery
- Significantly cheaper than online API (up to 50% discount)
- Latency: typically 1-24 hours depending on batch size and queuing

```python
from vertexai.batch_prediction import BatchPredictionJob

job = BatchPredictionJob.submit(
    source_model="gemini-1.5-flash",
    input_dataset="gs://my-bucket/batch-prompts.jsonl",
    output_uri_prefix="gs://my-bucket/batch-results/"
)
job.wait()
```

---

## Vertex AI Agent Builder

A managed platform for building RAG and search applications without writing infrastructure code:

### Data store creation flow
1. Create a data store with a content source (Cloud Storage, BigQuery, website URLs, Firestore).
2. Agent Builder indexes the documents (chunking, embedding, vector indexing via Vertex AI Vector Search).
3. Use the data store ID in grounding calls or build a search/chat app on top.

### Search App
Provides document search with:
- Semantic search (embedding-based similarity)
- Sparse retrieval (keyword-based BM25)
- Hybrid retrieval (combination)
- Extractive answers and segments
- LLM-generated summaries with source citations

### Conversational Agent
Multi-turn conversational AI backed by Dialogflow CX infrastructure with:
- Intent and entity recognition
- Flows and pages (conversation state machine)
- Generative fallback (Gemini for out-of-scope questions)
- Integration with data stores for grounded answers
- Webhook integrations for dynamic responses

---

## Gemini Code Assist

Enterprise-grade AI coding assistant:
- **IDE plugins**: VS Code, JetBrains, Cloud Shell Editor, Cloud Workstations
- **Features**: inline code completion, natural language to code, code explanation, code review, test generation, documentation generation, bug fixing
- **Standard tier**: access to Gemini models for coding tasks; no private codebase indexing
- **Enterprise tier**: custom code customization (index your private GitHub/GitLab repos for context-aware suggestions specific to your codebase)
- **Cloud Shell integration**: natural language commands in Cloud Shell; explain gcloud outputs
- **BigQuery integration**: generate SQL from natural language; explain queries

---

## Best Practices

1. **Use `gemini-2.0-flash` for high-volume or latency-sensitive workloads**: it is significantly cheaper and faster than Pro models with only marginal quality differences for most tasks.
2. **Use structured output (JSON mode) for data extraction**: do not parse free-form text; use `response_schema` to guarantee valid structured output.
3. **Ground production responses**: for factual questions, always use Google Search grounding or private data store grounding to reduce hallucinations.
4. **Implement retry with exponential backoff**: Gemini API returns 429 (quota exceeded) and 503 (overload) errors; implement retry logic in all production clients.
5. **Use Context Caching for fixed large prefixes**: if you send the same document or system prompt repeatedly, context caching reduces both cost and latency.
6. **Validate safety ratings on all responses**: check `candidate.finish_reason` and `candidate.safety_ratings` before using the response, especially in user-facing applications.
7. **Use the Batch API for offline workloads**: evaluation, annotation, bulk content generation; dramatically cheaper than online API.
8. **Use `count_tokens` before sending large requests**: avoid sending requests that exceed the context window or cost more than expected.
9. **Store system instructions separately from code**: system prompts are part of your application's logic; version them alongside code.
10. **Use VPC Service Controls with Vertex AI** for sensitive enterprise workloads to prevent data exfiltration from the Gemini API endpoint.
