# Azure AI Services — Capabilities

## Service Overview

Azure AI Services (formerly Azure Cognitive Services) provides pre-built AI capabilities as REST APIs and SDKs — enabling developers to add AI features to applications without deep ML expertise. Services can be deployed as a single **multi-service resource** (one endpoint + key for all services) or as **individual resources** per service type.

**Pricing model**: Pay-per-transaction (per image, per 1K characters, per minute of audio, etc.) or commitment-tier plans for high volume.

---

## Azure AI Vision

Image and video understanding capabilities.

### Image Analysis (v4.0)

| Capability | Description |
|---|---|
| **Captions** | Natural language description of an image |
| **Dense Captions** | Captions for specific regions within an image |
| **Tags** | Keywords describing image content |
| **Objects** | Detected objects with bounding boxes |
| **People** | Person detection with bounding boxes |
| **Smart Crop** | Suggest crop ratios based on visual content |
| **Background Removal** | Remove or separate image background |

```python
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

client = ImageAnalysisClient(
    endpoint="https://myvision.cognitiveservices.azure.com/",
    credential=AzureKeyCredential("<key>")
)

result = client.analyze_from_url(
    image_url="https://example.com/image.jpg",
    visual_features=[VisualFeatures.CAPTION, VisualFeatures.TAGS, VisualFeatures.OBJECTS],
    language="en"
)

print(f"Caption: {result.caption.text} (confidence: {result.caption.confidence:.2f})")
for tag in result.tags.list:
    print(f"Tag: {tag.name} ({tag.confidence:.2f})")
```

### OCR — Read API

High-accuracy text extraction from images and documents:

- Supports printed and handwritten text, 164+ languages.
- Returns word-level bounding boxes, line structure, page layout.
- Handles: photos, scanned documents, PDFs, whiteboards.
- Async operation for large documents.

```python
from azure.ai.vision.imageanalysis.models import VisualFeatures

result = client.analyze_from_url(
    image_url="https://example.com/receipt.jpg",
    visual_features=[VisualFeatures.READ]
)

for block in result.read.blocks:
    for line in block.lines:
        print(f"Line: {line.text}")
        for word in line.words:
            print(f"  Word: {word.text} (confidence: {word.confidence:.2f})")
```

### Spatial Analysis (Video)

Count people, detect movements, enforce social distancing — processes live video streams (requires container deployment on edge or VM).

### Product Recognition

Detect retail products on shelves, planogram compliance analysis.

---

## Azure AI Speech

Full speech processing pipeline for audio I/O.

### Speech-to-Text (STT)

| Mode | Description | Use Case |
|---|---|---|
| **Real-time transcription** | Low-latency streaming recognition | Live captions, voice assistants |
| **Batch transcription** | Asynchronous processing of audio files | Call center recordings, media |
| **Fast transcription** | Faster-than-real-time for uploaded files | Quick turnaround transcription |
| **Custom speech** | Fine-tuned acoustic/language model | Domain-specific vocabulary |

```python
import azure.cognitiveservices.speech as speechsdk

config = speechsdk.SpeechConfig(
    subscription="<key>",
    region="eastus"
)
config.speech_recognition_language = "en-US"

audio_config = speechsdk.AudioConfig(use_default_microphone=True)
recognizer = speechsdk.SpeechRecognizer(speech_config=config, audio_config=audio_config)

result = recognizer.recognize_once()
if result.reason == speechsdk.ResultReason.RecognizedSpeech:
    print(f"Recognized: {result.text}")
```

### Text-to-Speech (TTS)

- 400+ neural voices across 140+ languages.
- **Custom Neural Voice**: train a voice model on ~1 hour of audio (requires Microsoft approval for deployment).
- SSML (Speech Synthesis Markup Language) for fine-grained control: rate, pitch, emphasis, pronunciation.

```python
synthesizer = speechsdk.SpeechSynthesizer(speech_config=config)
result = synthesizer.speak_text_async("Hello, welcome to Azure AI Speech.").get()

# SSML for custom control
ssml = """<speak version='1.0' xml:lang='en-US'>
  <voice name='en-US-AriaNeural'>
    <prosody rate='slow' pitch='+5%'>Welcome to Azure!</prosody>
  </voice>
</speak>"""
result = synthesizer.speak_ssml_async(ssml).get()
```

### Speaker Recognition

- **Speaker verification**: Does this audio match a known speaker? (1:1 comparison)
- **Speaker identification**: Which of N known speakers is speaking? (1:N comparison)

### Speech Translation

Real-time translation from speech input to text/audio output. 90+ source languages, 70+ target languages.

### Pronunciation Assessment

Score pronunciation accuracy, fluency, completeness — used in language learning applications.

---

## Azure AI Language

NLP capabilities for text understanding and generation.

### Pre-built Capabilities (No training required)

| Feature | Description |
|---|---|
| **Named Entity Recognition (NER)** | Extract entities: Person, Location, Organization, Date, URL, Phone, etc. |
| **Key Phrase Extraction** | Identify the main topics in text |
| **Sentiment Analysis** | Document-level sentiment (positive/negative/neutral) with confidence |
| **Opinion Mining** | Aspect-based sentiment — sentiment toward specific aspects (food: negative, service: positive) |
| **Language Detection** | Identify language of text input (100+ languages) |
| **PII Detection** | Identify and redact personal information (SSN, credit card, email, phone) |
| **Text Summarization** | Extractive (key sentences) and abstractive (generated summary) |
| **Entity Linking** | Link entities to Wikipedia knowledge base |

```python
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

client = TextAnalyticsClient(
    endpoint="https://mylanguage.cognitiveservices.azure.com/",
    credential=AzureKeyCredential("<key>")
)

documents = ["Azure AI Language provides NLP capabilities for text analysis."]

# Sentiment analysis
response = client.analyze_sentiment(documents)
for doc in response:
    print(f"Sentiment: {doc.sentiment}, Scores: {doc.confidence_scores}")

# NER
response = client.recognize_entities(documents)
for doc in response:
    for entity in doc.entities:
        print(f"Entity: {entity.text} | Category: {entity.category} | Score: {entity.confidence_score:.2f}")

# Key phrase extraction
response = client.extract_key_phrases(documents)
for doc in response:
    print(f"Key phrases: {doc.key_phrases}")
```

### Custom Language Features (Training required)

| Feature | Description |
|---|---|
| **Custom NER** | Train entity extractor for domain-specific entity types |
| **Custom Text Classification** | Multi-class or multi-label document classification |
| **Conversational Language Understanding (CLU)** | Intent classification + entity extraction for conversational AI |
| **Orchestration Workflow** | Route queries across multiple CLU/QA/LUIS projects |
| **Custom Question Answering** | Build FAQ-style QA from documents |

---

## Azure Document Intelligence

(Formerly Form Recognizer) — Extracts structured data from documents.

### Prebuilt Models

| Model | Documents Supported |
|---|---|
| `prebuilt-invoice` | Invoices — vendor, line items, totals, dates |
| `prebuilt-receipt` | Receipts — merchant, items, totals, payment |
| `prebuilt-idDocument` | Passports, driver licenses — name, DOB, ID number |
| `prebuilt-businessCard` | Business cards — name, phone, email, company |
| `prebuilt-tax.us.w2` | US W-2 tax forms |
| `prebuilt-tax.us.1098` | US 1098 tax forms |
| `prebuilt-healthInsuranceCard.us` | US health insurance cards |
| `prebuilt-layout` | General document layout — tables, paragraphs, key-value pairs |
| `prebuilt-read` | Text extraction only (OCR) |
| `prebuilt-document` | General document + key-value pair extraction |
| `prebuilt-contract` | Contract documents — parties, terms |

### Custom Models

| Type | Description | Training |
|---|---|---|
| **Template** | Fixed-layout documents (forms with consistent structure) | 5+ labeled samples |
| **Neural** | Variable-layout documents | 50+ labeled samples recommended |
| **Composed** | Multiple custom models combined for multi-document-type routing | - |

```python
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

client = DocumentAnalysisClient(
    endpoint="https://myformrecognizer.cognitiveservices.azure.com/",
    credential=AzureKeyCredential("<key>")
)

# Analyze an invoice
with open("invoice.pdf", "rb") as f:
    poller = client.begin_analyze_document("prebuilt-invoice", f)

result = poller.result()
for doc in result.documents:
    print(f"Vendor: {doc.fields.get('VendorName', {}).value}")
    print(f"Total: {doc.fields.get('InvoiceTotal', {}).value}")
    for item in doc.fields.get("Items", {}).value or []:
        print(f"  Item: {item.value.get('Description', {}).value}")
```

---

## Azure AI Translator

Text and document translation service.

| Capability | Description |
|---|---|
| **Text Translation** | Translate text in 100+ languages, auto-detect source language |
| **Transliteration** | Convert text between scripts (e.g., Arabic to Latin) |
| **Language Detection** | Detect language of input text |
| **Dictionary Lookup** | Bilingual dictionary with alternate translations |
| **Document Translation** | Async translation of full documents (PDF, DOCX, PPTX, XLSX) |
| **Custom Translator** | Train domain-specific translation model with parallel corpus |

```python
import requests, json

endpoint = "https://api.cognitive.microsofttranslator.com"
key = "<key>"
location = "eastus"

response = requests.post(
    f"{endpoint}/translate?api-version=3.0&to=es&to=fr",
    headers={"Ocp-Apim-Subscription-Key": key, "Ocp-Apim-Subscription-Region": location},
    json=[{"text": "Azure AI Translator supports 100+ languages."}]
)
translations = response.json()
print(translations[0]["translations"])  # [{text: "...", to: "es"}, {text: "...", to: "fr"}]
```

---

## Azure AI Content Safety

Content moderation for applications handling user-generated content.

### Text Moderation

- Detect: Violence, Hate, Sexual, Self-harm content in text.
- Severity levels: Safe (0), Low (2), Medium (4), High (6).
- Configurable block thresholds per category.

### Image Moderation

- Detect: Violence, Hate, Sexual content in images.
- Returns severity score per category.

### Prompt Shield

- **Jailbreak Detection**: Detect attempts to bypass safety guardrails in user prompts.
- **Indirect Prompt Injection**: Detect attack instructions embedded in documents fed to LLMs.

### Groundedness Detection

- Verify LLM responses are factually grounded in provided context.
- Returns ungrounded claim detection with specific spans.

```python
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions, TextCategory
from azure.core.credentials import AzureKeyCredential

client = ContentSafetyClient(
    endpoint="https://mycontentsafety.cognitiveservices.azure.com/",
    credential=AzureKeyCredential("<key>")
)

request = AnalyzeTextOptions(
    text="User-generated text to analyze",
    categories=[TextCategory.HATE, TextCategory.VIOLENCE, TextCategory.SEXUAL, TextCategory.SELF_HARM]
)
response = client.analyze_text(request)

for item in response.categories_analysis:
    print(f"{item.category}: severity={item.severity}")
```

---

## Azure AI Face

**Access Restricted** — requires Microsoft approval for production use beyond basic detection.

| Capability | Access Level |
|---|---|
| Face Detection (bounding box) | Open |
| Face Attribute Analysis (age, emotion, glasses, blur) | Open |
| Face Verification (1:1 matching) | Restricted |
| Face Identification (1:N) | Restricted |
| Similar Face Finding | Restricted |
| Face Grouping | Restricted |

---

## Azure AI Health Insights

Domain-specific AI for healthcare scenarios:

| Capability | Description |
|---|---|
| **Radiology Insights** | Analyze radiology reports — findings, critical findings, laterality |
| **Clinical Matching** | Match patients to clinical trials based on clinical notes |
| **Patient Timeline** | Extract chronological clinical events from unstructured notes |
| **Oncology Phenotyping** | Extract cancer staging, tumor characteristics from pathology reports |

Requires HIPAA BAA and appropriate data handling — process de-identified data in compliance with healthcare regulations.

---

## Multi-Service Resource vs. Individual Resources

| Aspect | Multi-Service (CognitiveServices) | Individual Resources |
|---|---|---|
| Endpoint | Single endpoint for all services | Separate endpoint per service |
| Key | One key for all services | Separate keys |
| Pricing | Pay-per-transaction per service | Same |
| Commitment Plans | Not available | Available per service |
| Best For | Development, small projects | Production, separate billing/quotas per service |

```bash
# Multi-service resource (kind = CognitiveServices)
az cognitiveservices account create --kind CognitiveServices --name myaiservices --sku S0 ...

# Individual service resources
az cognitiveservices account create --kind ComputerVision ...
az cognitiveservices account create --kind SpeechServices ...
az cognitiveservices account create --kind TextAnalytics ...
az cognitiveservices account create --kind FormRecognizer ...
az cognitiveservices account create --kind TextTranslation ...
```
