# Gemini & Generative AI — CLI Reference

Gemini on Vertex AI is primarily accessed via REST API or the Vertex AI SDK (Python, Node.js, Java, Go). The gcloud CLI has limited direct Gemini support, but REST examples with `curl` are provided throughout. Set your access token:

```bash
export TOKEN=$(gcloud auth print-access-token)
export PROJECT_ID=$(gcloud config get-value project)
export LOCATION=us-central1
```

---

## List Available Models

```bash
# List all models available in your project/region (includes Gemini, OSS, fine-tuned)
gcloud ai models list \
  --region=us-central1 \
  --project=$PROJECT_ID

# List publisher models (includes Gemini family)
curl -s \
  "https://$LOCATION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/publishers/google/models" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Describe a specific Gemini model
curl -s \
  "https://$LOCATION-aiplatform.googleapis.com/v1/publishers/google/models/gemini-2.0-flash" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

---

## Text Generation (generateContent)

```bash
# Simple text generation with Gemini 2.0 Flash
curl -s -X POST \
  "https://$LOCATION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/publishers/google/models/gemini-2.0-flash:generateContent" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "role": "user",
      "parts": [{"text": "Explain the CAP theorem in simple terms."}]
    }],
    "generationConfig": {
      "temperature": 0.2,
      "maxOutputTokens": 1024
    }
  }' | python3 -m json.tool

# Generation with a system instruction
curl -s -X POST \
  "https://$LOCATION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/publishers/google/models/gemini-2.0-flash:generateContent" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "systemInstruction": {
      "parts": [{"text": "You are a senior GCP architect. Give concise, actionable advice."}]
    },
    "contents": [{
      "role": "user",
      "parts": [{"text": "Should I use Cloud Run or GKE for a stateless API?"}]
    }],
    "generationConfig": {
      "temperature": 0.0,
      "maxOutputTokens": 512
    }
  }'

# Structured JSON output with a schema
curl -s -X POST \
  "https://$LOCATION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/publishers/google/models/gemini-2.0-flash:generateContent" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "role": "user",
      "parts": [{"text": "Extract the invoice details: Invoice #12345, Date: Jan 15 2025, Amount: $1,234.56, Vendor: Acme Corp"}]
    }],
    "generationConfig": {
      "responseMimeType": "application/json",
      "responseSchema": {
        "type": "object",
        "properties": {
          "invoice_number": {"type": "string"},
          "date": {"type": "string"},
          "amount": {"type": "number"},
          "vendor": {"type": "string"}
        },
        "required": ["invoice_number", "date", "amount", "vendor"]
      }
    }
  }'

# Count tokens before sending (to estimate cost)
curl -s -X POST \
  "https://$LOCATION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/publishers/google/models/gemini-2.0-flash:countTokens" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "role": "user",
      "parts": [{"text": "Hello, how many tokens am I using?"}]
    }]
  }'
```

---

## Streaming Generation (streamGenerateContent)

```bash
# Streaming response (Server-Sent Events; each chunk is a JSON object)
curl -s -X POST \
  "https://$LOCATION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/publishers/google/models/gemini-2.0-flash:streamGenerateContent?alt=sse" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "role": "user",
      "parts": [{"text": "Write a short poem about cloud computing."}]
    }]
  }'
# Each SSE event: data: {"candidates": [{"content": {"parts": [{"text": "chunk..."}]}}]}
```

---

## Multimodal: Image + Text

```bash
# Analyze an image from Cloud Storage
curl -s -X POST \
  "https://$LOCATION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/publishers/google/models/gemini-2.0-flash:generateContent" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "role": "user",
      "parts": [
        {
          "fileData": {
            "mimeType": "image/jpeg",
            "fileUri": "gs://my-bucket/images/diagram.jpg"
          }
        },
        {"text": "Describe the architecture shown in this diagram and identify any potential issues."}
      ]
    }]
  }'

# Analyze a base64-encoded image inline
IMAGE_B64=$(base64 -i image.jpg)
curl -s -X POST \
  "https://$LOCATION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/publishers/google/models/gemini-2.0-flash:generateContent" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"contents\": [{
      \"role\": \"user\",
      \"parts\": [
        {
          \"inlineData\": {
            \"mimeType\": \"image/jpeg\",
            \"data\": \"$IMAGE_B64\"
          }
        },
        {\"text\": \"What is shown in this image?\"}
      ]
    }]
  }"

# Analyze a PDF document
curl -s -X POST \
  "https://$LOCATION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/publishers/google/models/gemini-1.5-pro:generateContent" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "role": "user",
      "parts": [
        {
          "fileData": {
            "mimeType": "application/pdf",
            "fileUri": "gs://my-bucket/docs/contract.pdf"
          }
        },
        {"text": "Summarize the key obligations of each party in this contract."}
      ]
    }]
  }'
```

---

## Multimodal: Video + Text

```bash
# Analyze a video from Cloud Storage
curl -s -X POST \
  "https://$LOCATION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/publishers/google/models/gemini-1.5-pro:generateContent" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "role": "user",
      "parts": [
        {
          "fileData": {
            "mimeType": "video/mp4",
            "fileUri": "gs://my-bucket/videos/product-demo.mp4"
          }
        },
        {"text": "Create a timestamped outline of the key topics covered in this video."}
      ]
    }]
  }'
```

---

## Grounding: Google Search

```bash
# Enable Google Search grounding
curl -s -X POST \
  "https://$LOCATION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/publishers/google/models/gemini-2.0-flash:generateContent" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "role": "user",
      "parts": [{"text": "What are the latest features announced at Google Cloud Next 2025?"}]
    }],
    "tools": [{
      "googleSearchRetrieval": {
        "dynamicRetrievalConfig": {
          "mode": "MODE_DYNAMIC",
          "dynamicThreshold": 0.8
        }
      }
    }]
  }'

# Always use search (not dynamic)
curl -s -X POST \
  "https://$LOCATION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/publishers/google/models/gemini-2.0-flash:generateContent" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"role": "user", "parts": [{"text": "What is the current price of Alphabet stock?"}]}],
    "tools": [{"googleSearchRetrieval": {}}]
  }'
```

---

## Grounding: Vertex AI Search (Private Data)

```bash
# Ground responses in a Vertex AI Agent Builder data store
curl -s -X POST \
  "https://$LOCATION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/publishers/google/models/gemini-2.0-flash:generateContent" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"contents\": [{
      \"role\": \"user\",
      \"parts\": [{\"text\": \"What is our company's refund policy for enterprise customers?\"}]
    }],
    \"tools\": [{
      \"retrieval\": {
        \"vertexAiSearch\": {
          \"datastore\": \"projects/$PROJECT_ID/locations/global/collections/default_collection/dataStores/DATA_STORE_ID\"
        }
      }
    }]
  }"
```

---

## Function Calling

```bash
# Define tools and call a model that may invoke them
curl -s -X POST \
  "https://$LOCATION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/publishers/google/models/gemini-2.0-flash:generateContent" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "systemInstruction": {
      "parts": [{"text": "You are a helpful assistant with access to tools."}]
    },
    "contents": [{
      "role": "user",
      "parts": [{"text": "What is the weather like in Paris right now?"}]
    }],
    "tools": [{
      "functionDeclarations": [{
        "name": "get_current_weather",
        "description": "Get the current weather for a location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "City and country, e.g. Paris, France"
            },
            "unit": {
              "type": "string",
              "enum": ["celsius", "fahrenheit"]
            }
          },
          "required": ["location"]
        }
      }]
    }]
  }'
# If the model wants to call the function, the response includes:
# {"functionCall": {"name": "get_current_weather", "args": {"location": "Paris, France"}}}

# Send back the function result
curl -s -X POST \
  "https://$LOCATION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/publishers/google/models/gemini-2.0-flash:generateContent" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [
      {"role": "user", "parts": [{"text": "What is the weather like in Paris right now?"}]},
      {"role": "model", "parts": [{"functionCall": {"name": "get_current_weather", "args": {"location": "Paris, France"}}}]},
      {"role": "user", "parts": [{"functionResponse": {"name": "get_current_weather", "response": {"temperature": 18, "condition": "Partly cloudy", "humidity": 65}}}]}
    ],
    "tools": [{"functionDeclarations": [{"name": "get_current_weather", "description": "Get current weather", "parameters": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]}}]}]
  }'
```

---

## Python SDK Examples

```python
import vertexai
from vertexai.generative_models import (
    GenerativeModel, GenerationConfig, Part, Tool,
    FunctionDeclaration, grounding
)
import datetime

vertexai.init(project="my-project", location="us-central1")

# --- Basic text generation ---
model = GenerativeModel("gemini-2.0-flash")
response = model.generate_content(
    "What is the difference between Vertex AI Pipelines and Cloud Composer?",
    generation_config=GenerationConfig(temperature=0.2, max_output_tokens=1024)
)
print(response.text)

# --- Streaming ---
for chunk in model.generate_content("Write a haiku about Kubernetes.", stream=True):
    print(chunk.text, end="", flush=True)

# --- Multi-turn chat ---
chat = model.start_chat()
r1 = chat.send_message("I'm building a real-time analytics pipeline on GCP.")
r2 = chat.send_message("What streaming service should I use for ingestion?")
r3 = chat.send_message("How does that compare to Kafka on GKE?")
print(r3.text)

# --- Multimodal: image from GCS ---
model15 = GenerativeModel("gemini-1.5-pro")
image_part = Part.from_uri("gs://my-bucket/screenshot.png", mime_type="image/png")
response = model15.generate_content([image_part, "Identify all UI components visible."])
print(response.text)

# --- Grounding with Google Search ---
search_tool = Tool.from_google_search_retrieval(grounding.GoogleSearchRetrieval())
grounded_model = GenerativeModel("gemini-2.0-flash", tools=[search_tool])
response = grounded_model.generate_content("What GCP services were announced at Next '25?")
print(response.text)
# Print sources
if response.candidates[0].grounding_metadata:
    for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
        print(f"  Source: {chunk.web.title} — {chunk.web.uri}")

# --- Function calling ---
weather_func = FunctionDeclaration(
    name="get_weather",
    description="Get current weather for a city",
    parameters={
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"]
    }
)
tool = Tool(function_declarations=[weather_func])
model_with_tools = GenerativeModel("gemini-2.0-flash", tools=[tool])
response = model_with_tools.generate_content("Is it raining in London?")
if response.candidates[0].content.parts[0].function_call.name:
    fc = response.candidates[0].content.parts[0].function_call
    print(f"Model wants to call: {fc.name}({dict(fc.args)})")

# --- Structured output (JSON mode) ---
import json
response = model.generate_content(
    "List 3 GCP storage services with their use cases",
    generation_config=GenerationConfig(
        response_mime_type="application/json",
        response_schema={
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "service": {"type": "string"},
                    "use_case": {"type": "string"},
                    "pricing_model": {"type": "string"}
                }
            }
        }
    )
)
services = json.loads(response.text)
for s in services:
    print(f"{s['service']}: {s['use_case']}")

# --- Context caching ---
from vertexai.preview.caching import CachedContent
import datetime

cache = CachedContent.create(
    model_name="gemini-1.5-pro",
    system_instruction="You are an expert analyst. Answer questions based only on the provided document.",
    contents=[Part.from_uri("gs://my-bucket/annual-report-2024.pdf", mime_type="application/pdf")],
    ttl=datetime.timedelta(hours=4)
)
cached_model = GenerativeModel.from_cached_content(cached_content=cache)
r1 = cached_model.generate_content("What was total revenue in 2024?")
r2 = cached_model.generate_content("Which product line grew fastest?")
r3 = cached_model.generate_content("What are the top 3 risk factors mentioned?")

# --- Batch prediction (Python SDK) ---
from vertexai.preview.batch_prediction import BatchPredictionJob

# Input JSONL format (one request per line):
# {"request": {"contents": [{"role": "user", "parts": [{"text": "Summarize: ..."}]}]}}
job = BatchPredictionJob.submit(
    source_model="gemini-1.5-flash",
    input_dataset="gs://my-bucket/batch-input.jsonl",
    output_uri_prefix="gs://my-bucket/batch-output/"
)
print(f"Batch job: {job.resource_name}")
job.wait()
print(f"Output at: gs://my-bucket/batch-output/")
```

---

## Generation Config Reference

```bash
# Full generationConfig with all common parameters
curl -s -X POST \
  "https://$LOCATION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/publishers/google/models/gemini-2.0-flash:generateContent" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"role": "user", "parts": [{"text": "Write a creative product description."}]}],
    "generationConfig": {
      "temperature": 1.0,
      "topP": 0.95,
      "topK": 40,
      "maxOutputTokens": 512,
      "stopSequences": ["END", "###"],
      "candidateCount": 1
    },
    "safetySettings": [
      {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
      {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
      {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
      {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
    ]
  }'
```
