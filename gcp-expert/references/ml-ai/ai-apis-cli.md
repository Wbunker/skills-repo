# AI APIs — CLI Reference

Most AI APIs are primarily accessed via REST. `gcloud ml` commands are available for Vision, Natural Language, Translation, and Speech. Video Intelligence uses REST only (shown with curl).

```bash
export TOKEN=$(gcloud auth print-access-token)
export PROJECT_ID=$(gcloud config get-value project)
```

---

## Vision AI (Cloud Vision API)

### gcloud ml vision commands

```bash
# Detect labels (general objects and concepts) in an image
gcloud ml vision detect-labels gs://my-bucket/image.jpg

# Detect labels in a local file
gcloud ml vision detect-labels /path/to/image.jpg

# Detect text (OCR) in an image
gcloud ml vision detect-text gs://my-bucket/scanned-doc.jpg

# Detect text in a document (PDF, multi-page; layout-aware)
gcloud ml vision detect-document gs://my-bucket/document.pdf

# Detect objects with bounding boxes
gcloud ml vision detect-objects gs://my-bucket/street-photo.jpg

# Detect faces
gcloud ml vision detect-faces gs://my-bucket/photo.jpg

# Detect landmarks (famous locations)
gcloud ml vision detect-landmarks gs://my-bucket/photo.jpg

# Detect logos
gcloud ml vision detect-logos gs://my-bucket/product-photo.jpg

# Safe search (classify image content)
gcloud ml vision detect-safe-search gs://my-bucket/image.jpg

# Detect image properties (dominant colors)
gcloud ml vision detect-image-properties gs://my-bucket/image.jpg

# Web detection (find similar images on the web)
gcloud ml vision detect-web gs://my-bucket/image.jpg

# Run multiple detection types in one request
gcloud ml vision detect-text gs://my-bucket/image.jpg \
  --format="json(responses[0].fullTextAnnotation)"
```

### REST API — Multiple features in one request

```bash
# Request multiple detection types simultaneously
IMAGE_B64=$(base64 -i image.jpg)
curl -s -X POST \
  "https://vision.googleapis.com/v1/images:annotate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"requests\": [{
      \"image\": {
        \"content\": \"$IMAGE_B64\"
      },
      \"features\": [
        {\"type\": \"LABEL_DETECTION\", \"maxResults\": 10},
        {\"type\": \"TEXT_DETECTION\"},
        {\"type\": \"OBJECT_LOCALIZATION\", \"maxResults\": 10},
        {\"type\": \"SAFE_SEARCH_DETECTION\"}
      ]
    }]
  }" | python3 -m json.tool

# Annotate an image from Cloud Storage
curl -s -X POST \
  "https://vision.googleapis.com/v1/images:annotate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [{
      "image": {"source": {"gcsImageUri": "gs://my-bucket/photo.jpg"}},
      "features": [
        {"type": "LABEL_DETECTION", "maxResults": 5},
        {"type": "SAFE_SEARCH_DETECTION"}
      ]
    }]
  }'

# Async batch annotation (multiple images in Cloud Storage)
curl -s -X POST \
  "https://vision.googleapis.com/v1/files:asyncBatchAnnotate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [{
      "inputConfig": {
        "gcsSource": {"uri": "gs://my-bucket/input/"},
        "mimeType": "application/pdf"
      },
      "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
      "outputConfig": {
        "gcsDestination": {"uri": "gs://my-bucket/output/"},
        "batchSize": 10
      }
    }]
  }'
```

---

## Natural Language AI

### gcloud ml language commands

```bash
# Analyze entities (named entity recognition)
gcloud ml language analyze-entities \
  --content="Google Cloud was founded in 2008 and is headquartered in Mountain View, California."

# Analyze entities from a file
gcloud ml language analyze-entities \
  --content-file=document.txt

# Analyze entities from Cloud Storage
gcloud ml language analyze-entities \
  --content-file=gs://my-bucket/article.txt

# Analyze sentiment
gcloud ml language analyze-sentiment \
  --content="I absolutely love the new Vertex AI features! The documentation is excellent."

# Analyze sentiment with detailed output
gcloud ml language analyze-sentiment \
  --content="The product quality is great but shipping was very slow." \
  --format="json(documentSentiment,sentences)"

# Analyze syntax (POS tagging, dependency parse)
gcloud ml language analyze-syntax \
  --content="The quick brown fox jumps over the lazy dog."

# Classify text (content classification)
gcloud ml language classify-text \
  --content="Google Cloud has launched new AI features including improved Vertex AI pipelines and enhanced BigQuery ML capabilities."

# Analyze entity sentiment (sentiment per entity)
gcloud ml language analyze-entity-sentiment \
  --content="The service from Alice was fantastic but the food was disappointing."

# Annotate text (all features combined)
gcloud ml language annotate-text \
  --content="Apple acquired Beats Electronics for $3 billion in 2014." \
  --features=entities,sentiment,syntax,classifyText

# Analyze with language specification
gcloud ml language analyze-sentiment \
  --content="Excelente producto, muy recomendado." \
  --language=es
```

### REST API example

```bash
curl -s -X POST \
  "https://language.googleapis.com/v1/documents:analyzeEntities" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "document": {
      "type": "PLAIN_TEXT",
      "content": "Sundar Pichai is the CEO of Alphabet Inc., the parent company of Google Cloud."
    },
    "encodingType": "UTF8"
  }' | python3 -c "
import sys, json
data = json.load(sys.stdin)
for entity in data.get('entities', []):
    print(f\"{entity['name']:30s} {entity['type']:15s} salience={entity.get('salience', 0):.3f}\")
"
```

---

## Translation AI

### gcloud ml translate commands

```bash
# List supported languages
gcloud ml translate get-supported-languages

# List with target language names in English
gcloud ml translate get-supported-languages \
  --target=en \
  --format="table(language,displayName,supportSource,supportTarget)"

# Translate text to a target language
gcloud ml translate translate-text \
  --content="Hello, how are you?" \
  --target-language=es

# Translate text, specifying source language
gcloud ml translate translate-text \
  --content="Bonjour le monde" \
  --source-language=fr \
  --target-language=en

# Translate multiple strings
gcloud ml translate translate-text \
  --content="Hello" \
  --content="Goodbye" \
  --content="Thank you" \
  --target-language=ja

# Detect the language of a text
gcloud ml translate detect-language \
  --content="Guten Morgen, wie geht es Ihnen?"

# Translate a file (v3 Advanced API via REST)
# First create a glossary (optional):
curl -s -X POST \
  "https://translation.googleapis.com/v3/projects/$PROJECT_ID/locations/us-central1/glossaries" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "projects/'$PROJECT_ID'/locations/us-central1/glossaries/my-glossary",
    "languagePair": {
      "sourceLanguageCode": "en",
      "targetLanguageCode": "es"
    },
    "inputConfig": {
      "gcsSource": {
        "inputUri": "gs://my-bucket/glossary.csv"
      }
    }
  }'
# glossary.csv format: source_term,target_term (one pair per line)

# Batch translate documents
curl -s -X POST \
  "https://translation.googleapis.com/v3/projects/$PROJECT_ID/locations/us-central1:batchTranslateDocument" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sourceLanguageCode": "en",
    "targetLanguageCodes": ["es", "fr", "de"],
    "inputConfigs": [{
      "gcsSource": {"inputUri": "gs://my-bucket/docs-to-translate/"},
      "mimeType": "application/pdf"
    }],
    "outputConfig": {
      "gcsDestination": {"outputUriPrefix": "gs://my-bucket/translated/"}
    }
  }'

# Batch translate text files
curl -s -X POST \
  "https://translation.googleapis.com/v3/projects/$PROJECT_ID/locations/us-central1:batchTranslateText" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sourceLanguageCode": "en",
    "targetLanguageCodes": ["ja", "ko", "zh-CN"],
    "inputConfigs": [{
      "gcsSource": {"inputUri": "gs://my-bucket/text-files/*.txt"},
      "mimeType": "text/plain"
    }],
    "outputConfig": {
      "gcsDestination": {"outputUriPrefix": "gs://my-bucket/translated-text/"}
    }
  }'
```

---

## Speech-to-Text (STT)

### gcloud ml speech commands

```bash
# Synchronous transcription (short audio, ≤60 seconds)
gcloud ml speech recognize audio.wav \
  --language-code=en-US

# Synchronous transcription with options
gcloud ml speech recognize audio.flac \
  --language-code=en-US \
  --encoding=FLAC \
  --sample-rate=16000 \
  --model=latest_long

# Async transcription from Cloud Storage (long audio)
gcloud ml speech recognize-long-running \
  gs://my-bucket/audio/long-recording.mp3 \
  --language-code=en-US \
  --encoding=MP3 \
  --sample-rate=16000 \
  --async

# Wait for async operation to complete
gcloud ml speech operations wait OPERATION_ID

# List active speech operations
gcloud ml speech operations list

# Describe a specific operation
gcloud ml speech operations describe OPERATION_ID

# Transcription with speaker diarization
gcloud ml speech recognize-long-running \
  gs://my-bucket/meeting-audio.wav \
  --language-code=en-US \
  --encoding=LINEAR16 \
  --sample-rate=16000 \
  --min-speaker-count=2 \
  --max-speaker-count=4 \
  --enable-speaker-diarization \
  --async

# Transcription with automatic punctuation and word timestamps
gcloud ml speech recognize-long-running \
  gs://my-bucket/audio.mp3 \
  --language-code=en-US \
  --encoding=MP3 \
  --enable-automatic-punctuation \
  --include-word-time-offsets \
  --async
```

### REST API — Streaming and advanced config

```bash
# Async recognition with full config via REST
curl -s -X POST \
  "https://speech.googleapis.com/v1/speech:longrunningrecognize" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "encoding": "MP3",
      "sampleRateHertz": 16000,
      "languageCode": "en-US",
      "model": "latest_long",
      "enableAutomaticPunctuation": true,
      "enableWordTimeOffsets": true,
      "enableWordConfidence": true,
      "diarizationConfig": {
        "enableSpeakerDiarization": true,
        "minSpeakerCount": 2,
        "maxSpeakerCount": 4
      },
      "speechContexts": [{
        "phrases": ["Vertex AI", "BigQuery", "Cloud Run", "GKE"],
        "boost": 15.0
      }]
    },
    "audio": {
      "uri": "gs://my-bucket/audio/conference-call.mp3"
    }
  }'
```

---

## Text-to-Speech (TTS)

```bash
# Synthesize speech from text
gcloud ml tts synthesize \
  --text="Welcome to Google Cloud. How can I help you today?" \
  --voice-name=en-US-Neural2-C \
  --audio-encoding=MP3 \
  --output-file=output.mp3

# Synthesize using SSML for more control
gcloud ml tts synthesize \
  --ssml='<speak>Your order <emphasis>12345</emphasis> has been <break time="300ms"/> shipped.</speak>' \
  --voice-name=en-US-Studio-O \
  --audio-encoding=LINEAR16 \
  --output-file=notification.wav

# List available voices
gcloud ml tts list-voices

# List voices for a specific language
gcloud ml tts list-voices \
  --language-code=ja-JP

# List Neural2 voices
gcloud ml tts list-voices \
  --language-code=en-US \
  --format="table(name,languageCodes,ssmlGender)" | grep Neural2

# Synthesize with custom speaking rate and pitch
gcloud ml tts synthesize \
  --text="This message is slightly faster and higher pitched." \
  --voice-name=en-US-Neural2-A \
  --speaking-rate=1.2 \
  --pitch=2.0 \
  --audio-encoding=OGG_OPUS \
  --output-file=output.ogg

# REST API for TTS (useful for Studio voices and advanced options)
curl -s -X POST \
  "https://texttospeech.googleapis.com/v1/text:synthesize" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "ssml": "<speak>Welcome back, <emphasis>valued customer</emphasis>. <break time=\"500ms\"/>Your account balance is <say-as interpret-as=\"currency\" language=\"en-US\">$1234.56</say-as>.</speak>"
    },
    "voice": {
      "languageCode": "en-US",
      "name": "en-US-Studio-O"
    },
    "audioConfig": {
      "audioEncoding": "MP3",
      "speakingRate": 0.95,
      "pitch": -1.0,
      "volumeGainDb": 0.0,
      "effectsProfileId": ["telephony-class-application"]
    }
  }' | python3 -c "
import sys, json, base64
data = json.load(sys.stdin)
audio = base64.b64decode(data['audioContent'])
with open('output.mp3', 'wb') as f:
    f.write(audio)
print('Saved output.mp3')
"
```

---

## Video Intelligence API

The Video Intelligence API has no `gcloud ml` subcommand; use REST with `curl`.

```bash
# Analyze a video with multiple detection features
curl -s -X POST \
  "https://videointelligence.googleapis.com/v1/videos:annotate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputUri": "gs://my-bucket/videos/product-demo.mp4",
    "outputUri": "gs://my-bucket/video-results/",
    "features": [
      "LABEL_DETECTION",
      "SHOT_CHANGE_DETECTION",
      "SPEECH_TRANSCRIPTION",
      "TEXT_DETECTION",
      "OBJECT_TRACKING"
    ],
    "videoContext": {
      "labelDetectionConfig": {
        "labelDetectionMode": "SHOT_AND_FRAME_MODE",
        "model": "latest"
      },
      "speechTranscriptionConfig": {
        "languageCode": "en-US",
        "enableAutomaticPunctuation": true
      }
    }
  }'
# Returns: {"name": "projects/.../operations/OPERATION_ID"}

# Check the status of the video annotation operation
OPERATION_ID="projects/$PROJECT_ID/locations/us-east1/operations/YOUR_OP_ID"
curl -s \
  "https://videointelligence.googleapis.com/v1/$OPERATION_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('Done:', data.get('done', False))
if data.get('done'):
    results = data.get('response', {}).get('annotationResults', [{}])[0]
    labels = results.get('segmentLabelAnnotations', [])
    for l in labels[:5]:
        desc = l.get('entity', {}).get('description', '')
        conf = max([s.get('confidence', 0) for s in l.get('segments', [])], default=0)
        print(f'  Label: {desc} ({conf:.2f})')
"

# Shot detection only (faster, cheaper)
curl -s -X POST \
  "https://videointelligence.googleapis.com/v1/videos:annotate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputUri": "gs://my-bucket/videos/clip.mp4",
    "features": ["SHOT_CHANGE_DETECTION"]
  }'

# Explicit content detection
curl -s -X POST \
  "https://videointelligence.googleapis.com/v1/videos:annotate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputUri": "gs://my-bucket/videos/user-upload.mp4",
    "features": ["EXPLICIT_CONTENT_DETECTION"]
  }'

# Logo recognition
curl -s -X POST \
  "https://videointelligence.googleapis.com/v1/videos:annotate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputUri": "gs://my-bucket/videos/broadcast.mp4",
    "features": ["LOGO_RECOGNITION"]
  }'
```
