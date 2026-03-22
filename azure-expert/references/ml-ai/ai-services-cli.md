# Azure AI Services — CLI & SDK Reference

## Prerequisites

```bash
# No additional extensions needed for cognitiveservices commands
az login
az account set --subscription "My Subscription"

# Install Python SDKs
pip install azure-ai-textanalytics \
            azure-ai-vision-imageanalysis \
            azure-ai-formrecognizer \
            azure-cognitiveservices-speech \
            azure-ai-contentsafety \
            azure-ai-translation-text \
            azure-identity
```

---

## Resource Management

### Create Resources

```bash
# Multi-service Cognitive Services resource (single key/endpoint for all services)
az cognitiveservices account create \
  --name my-ai-services \
  --resource-group myRG \
  --kind CognitiveServices \
  --sku S0 \
  --location eastus \
  --yes

# Azure AI Vision (Computer Vision)
az cognitiveservices account create \
  --name my-vision \
  --resource-group myRG \
  --kind ComputerVision \
  --sku S1 \
  --location eastus \
  --yes

# Azure AI Speech
az cognitiveservices account create \
  --name my-speech \
  --resource-group myRG \
  --kind SpeechServices \
  --sku S0 \
  --location eastus \
  --yes

# Azure AI Language (Text Analytics)
az cognitiveservices account create \
  --name my-language \
  --resource-group myRG \
  --kind TextAnalytics \
  --sku S \
  --location eastus \
  --yes

# Azure Document Intelligence (Form Recognizer)
az cognitiveservices account create \
  --name my-docint \
  --resource-group myRG \
  --kind FormRecognizer \
  --sku S0 \
  --location eastus \
  --yes

# Azure AI Translator
az cognitiveservices account create \
  --name my-translator \
  --resource-group myRG \
  --kind TextTranslation \
  --sku S1 \
  --location global \
  --yes

# Azure AI Content Safety
az cognitiveservices account create \
  --name my-content-safety \
  --resource-group myRG \
  --kind ContentSafety \
  --sku S0 \
  --location eastus \
  --yes

# Azure AI Face
az cognitiveservices account create \
  --name my-face \
  --resource-group myRG \
  --kind Face \
  --sku S0 \
  --location eastus \
  --yes
```

---

## Resource Discovery

```bash
# List all Cognitive Services accounts in a subscription
az cognitiveservices account list \
  -o table

# List by resource group
az cognitiveservices account list \
  --resource-group myRG \
  -o table

# List only specific service type (e.g., all OpenAI resources)
az cognitiveservices account list \
  --query "[?kind=='OpenAI']" \
  -o table

# Show resource details including endpoint URL
az cognitiveservices account show \
  --name my-language \
  --resource-group myRG

# Get endpoint URL
az cognitiveservices account show \
  --name my-language \
  --resource-group myRG \
  --query "properties.endpoint" -o tsv

# List available SKUs for a service kind in a region
az cognitiveservices account list-skus \
  --kind TextAnalytics \
  --location eastus \
  -o table

# List all supported kinds/APIs in a region
az cognitiveservices account list-kinds \
  --location eastus \
  -o table

# Update tags on a resource
az cognitiveservices account update \
  --name my-language \
  --resource-group myRG \
  --tags environment=production team=nlp-team

# Delete a resource
az cognitiveservices account delete \
  --name my-language \
  --resource-group myRG
```

---

## Keys and Authentication

```bash
# List API keys (Key1, Key2)
az cognitiveservices account keys list \
  --name my-language \
  --resource-group myRG

# Get just Key1
az cognitiveservices account keys list \
  --name my-language \
  --resource-group myRG \
  --query key1 -o tsv

# Regenerate Key1 (rotate keys without downtime — update apps to Key2 first)
az cognitiveservices account keys regenerate \
  --name my-language \
  --resource-group myRG \
  --key-name Key1

# Store key in Key Vault (recommended pattern)
KEY=$(az cognitiveservices account keys list \
  --name my-language \
  --resource-group myRG \
  --query key1 -o tsv)

az keyvault secret set \
  --vault-name myKeyVault \
  --name language-api-key \
  --value "$KEY"

# Assign Cognitive Services User role for managed identity access
az role assignment create \
  --assignee <object-id-of-MI> \
  --role "Cognitive Services User" \
  --scope $(az cognitiveservices account show \
    --name my-language \
    --resource-group myRG \
    --query id -o tsv)
```

---

## Network Configuration

```bash
# Add VNet rule (restrict access to specific subnet)
az cognitiveservices account network-rule add \
  --name my-language \
  --resource-group myRG \
  --subnet /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Network/virtualNetworks/{vnet}/subnets/{subnet}

# Add IP rule
az cognitiveservices account network-rule add \
  --name my-language \
  --resource-group myRG \
  --ip-address "203.0.113.0/24"

# Set default network action to Deny (enforce network rules)
az cognitiveservices account update \
  --name my-language \
  --resource-group myRG \
  --default-action Deny

# Create private endpoint for secure access
az network private-endpoint create \
  --name my-language-pe \
  --resource-group myRG \
  --vnet-name myVNet \
  --subnet mySubnet \
  --private-connection-resource-id $(az cognitiveservices account show \
    --name my-language --resource-group myRG --query id -o tsv) \
  --group-id account \
  --connection-name my-language-connection
```

---

## Python SDK: Text Analytics (Azure AI Language)

```python
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

# Key-based auth
client = TextAnalyticsClient(
    endpoint="https://my-language.cognitiveservices.azure.com/",
    credential=AzureKeyCredential("<key>")
)

# Managed identity auth (production)
client = TextAnalyticsClient(
    endpoint="https://my-language.cognitiveservices.azure.com/",
    credential=DefaultAzureCredential()
)

documents = [
    "Azure AI Language is a powerful NLP service.",
    "I had a terrible experience with the customer support team.",
    "The food was amazing but the service was slow."
]

# --- Batch operations ---

# Sentiment analysis with opinion mining
results = client.analyze_sentiment(documents, show_opinion_mining=True)
for doc in results:
    print(f"Sentiment: {doc.sentiment}")
    for sentence in doc.sentences:
        for opinion in sentence.mined_opinions:
            print(f"  Aspect: {opinion.target.text} → {opinion.target.sentiment}")

# Named entity recognition
results = client.recognize_entities(documents)
for doc in results:
    for entity in doc.entities:
        print(f"Entity: {entity.text} | {entity.category} | {entity.confidence_score:.2f}")

# PII detection and redaction
results = client.recognize_pii_entities(documents, language="en")
for doc in results:
    print(f"Redacted: {doc.redacted_text}")

# Key phrase extraction
results = client.extract_key_phrases(documents)
for doc in results:
    print(f"Key phrases: {', '.join(doc.key_phrases)}")

# Language detection
results = client.detect_language(documents)
for doc in results:
    print(f"Language: {doc.primary_language.name} ({doc.primary_language.iso6391_name})")

# Text summarization (abstractive)
from azure.ai.textanalytics import AbstractiveSummaryAction
poller = client.begin_analyze_actions(
    documents,
    actions=[AbstractiveSummaryAction(sentence_count=3)]
)
for doc_results in poller.result():
    for result in doc_results:
        if not result.is_error:
            for summary in result.summaries:
                print(f"Summary: {summary.text}")
```

---

## Python SDK: Vision (Azure AI Vision)

```python
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

client = ImageAnalysisClient(
    endpoint="https://my-vision.cognitiveservices.azure.com/",
    credential=AzureKeyCredential("<key>")
)

# Analyze from URL
result = client.analyze_from_url(
    image_url="https://example.com/image.jpg",
    visual_features=[
        VisualFeatures.CAPTION,
        VisualFeatures.TAGS,
        VisualFeatures.OBJECTS,
        VisualFeatures.READ,
        VisualFeatures.PEOPLE
    ]
)

# Analyze from file
with open("image.jpg", "rb") as f:
    result = client.analyze(
        image_data=f.read(),
        visual_features=[VisualFeatures.CAPTION, VisualFeatures.TAGS],
        language="en"
    )

print(f"Caption: {result.caption.text}")
for tag in result.tags.list[:5]:
    print(f"  Tag: {tag.name} ({tag.confidence:.2f})")
```

---

## Python SDK: Speech Services

```python
import azure.cognitiveservices.speech as speechsdk

# Configuration
speech_config = speechsdk.SpeechConfig(
    subscription="<key>",
    region="eastus"
)
speech_config.speech_recognition_language = "en-US"
speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"

# Speech-to-text from file
audio_config = speechsdk.AudioConfig(filename="audio.wav")
recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

result = recognizer.recognize_once_async().get()
print(f"Recognized: {result.text}")

# Text-to-speech to file
audio_output = speechsdk.AudioOutputConfig(filename="output.wav")
synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output)
result = synthesizer.speak_text_async("Hello from Azure AI Speech.").get()

# Continuous recognition (for long audio)
done = False
def stop_cb(evt): global done; done = True
recognizer.session_stopped.connect(stop_cb)
recognizer.recognized.connect(lambda evt: print(f"RECOGNIZED: {evt.result.text}"))
recognizer.start_continuous_recognition()
while not done:
    import time; time.sleep(0.5)
recognizer.stop_continuous_recognition()
```

---

## Python SDK: Document Intelligence

```python
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

client = DocumentAnalysisClient(
    endpoint="https://my-docint.cognitiveservices.azure.com/",
    credential=AzureKeyCredential("<key>")
)

# Analyze invoice (prebuilt model)
with open("invoice.pdf", "rb") as f:
    poller = client.begin_analyze_document("prebuilt-invoice", f)
result = poller.result()

for doc in result.documents:
    fields = doc.fields
    print(f"Vendor: {fields.get('VendorName', {}).value}")
    print(f"Invoice #: {fields.get('InvoiceId', {}).value}")
    print(f"Total: {fields.get('InvoiceTotal', {}).value}")

# General document layout analysis
with open("document.pdf", "rb") as f:
    poller = client.begin_analyze_document("prebuilt-layout", f)
result = poller.result()

for table in result.tables:
    print(f"Table with {table.row_count} rows, {table.column_count} columns")
    for cell in table.cells:
        print(f"  [{cell.row_index},{cell.column_index}]: {cell.content}")
```

---

## Commitment Plan (High-Volume Pricing)

```bash
# Create a commitment plan for a service (reduces per-transaction cost)
az cognitiveservices commitment-plan create \
  --name my-language-plan \
  --resource-group myRG \
  --location eastus \
  --kind TextAnalytics \
  --sku S \
  --hosting-model DisconnectedContainer \
  --plan-type TA-TextAnalytics-Commitment-Tier

# List commitment plans
az cognitiveservices commitment-plan list \
  --resource-group myRG \
  -o table
```
