# AI APIs — Capabilities

## Overview

Google Cloud's pre-trained AI APIs provide ready-to-use ML models for common perception and language tasks without any training data or ML expertise. These are fully managed REST APIs that accept raw content (images, text, audio, video) and return structured ML predictions.

---

## Vision AI (Cloud Vision API)

### Purpose
Analyze images to detect and classify objects, text, faces, landmarks, logos, and explicit content using Google's computer vision models.

### Detection features

| Feature | Description | Output |
|---|---|---|
| **Label Detection** | Identify general objects and concepts in an image | Labels with confidence scores (e.g., "dog: 0.98", "outdoor: 0.91") |
| **Object Localization** | Detect objects and return bounding boxes | Object name, bounding polygon, confidence |
| **Text Detection (OCR)** | Extract all text visible in an image | Raw text string; individual word bounding boxes |
| **Document Text Detection** | Full-page OCR optimized for documents | Text with layout structure (paragraphs, blocks, words) |
| **Face Detection** | Detect human faces | Bounding box, facial landmarks, emotions (JOY, SORROW, ANGER, SURPRISE), headwear, blurriness, exposure likelihood |
| **Landmark Detection** | Identify well-known natural and human-made structures | Landmark name, confidence, geographic coordinates (lat/lon) |
| **Logo Detection** | Detect corporate brand logos | Logo description, bounding polygon, confidence |
| **Safe Search Detection** | Classify image content by category | `adult`, `spoof`, `medical`, `violence`, `racy` — each rated VERY_UNLIKELY to VERY_LIKELY |
| **Image Properties** | Extract dominant colors from an image | RGB values, pixel fraction, score |
| **Crop Hints** | Suggest crop coordinates to focus on the most important content | Bounding polygons with confidence and aspect ratios |
| **Web Detection** | Find similar images and web pages using the image as a query | Matching URLs, visually similar images, best-guess labels |

### Product Search (Vision Product Search)
Match a query image against a catalog of product images for visual product lookup (e-commerce "shop the look"):
- Create a product catalog in Vision Product Search
- Add reference images per product
- Query with a user-provided image to find similar products

### Async batch processing
Process many images stored in Cloud Storage asynchronously:
- JSON request file lists GCS URIs
- Results written to GCS as JSON files
- Operation tracked via long-running operations API

### Input
- Images: JPEG, PNG, GIF, BMP, WebP, RAW, ICO, PDF (first page), TIFF
- Source: inline base64 (max 10 MB) or `gs://` URI (max 20 MB)

---

## Natural Language AI (Cloud Natural Language API)

### Purpose
Analyze text to extract entities, understand sentiment, analyze syntax, and classify content. Multilingual; 700+ languages for some features.

### Analysis features

| Feature | Description | Output |
|---|---|---|
| **Entity Analysis** | Identify named entities (people, places, organizations, events, works of art, consumer goods, etc.) | Entity name, type, salience, Wikipedia URLs, mentions with character offsets |
| **Sentiment Analysis** | Determine overall emotional tone of the text | `documentSentiment.score` (-1.0 to +1.0), `documentSentiment.magnitude` (0 to ∞), per-sentence sentiment |
| **Syntax Analysis** | Parse sentence structure and parts of speech | Tokens with lemma, POS tags, morphological features, dependency tree |
| **Entity Sentiment Analysis** | Sentiment associated with each specific entity | Entity mentions with sentiment score and magnitude |
| **Content Classification** | Classify the text into one or more of 700+ categories | Category path and confidence (e.g., `/Health/Fitness/Weight Loss: 0.89`) |
| **Classify Text (v2)** | Updated classification taxonomy (more categories, more accurate) | Category path and confidence |

### Languages
- All features: English, Spanish, Japanese, Chinese (Simplified/Traditional), French, German, Portuguese
- Entity analysis only: many additional languages
- Auto-detect: pass `language: ""` to auto-detect the language

### Custom AutoML models
For domain-specific entity extraction or classification beyond the pre-built model capabilities, use AutoML Natural Language (see automl-capabilities.md).

---

## Translation AI (Cloud Translation API)

### Basic Translation API (v2)
Simple, low-latency translation for individual strings or batches:
- Detect the source language automatically
- 100+ supported languages
- Glossaries: custom terminology (e.g., product names, brand names should not be translated)
- Model selection: `nmt` (Neural Machine Translation; default) or `base` (phrase-based; faster, lower quality)

### Advanced Translation API (v3)
More features for enterprise translation workflows:
- **Batch translation**: translate large numbers of files stored in Cloud Storage
- **Document translation**: preserve formatting of HTML, DOCX, PDF documents while translating
- **Adaptive MT (beta)**: fine-tune translation quality using example translations (sentence pairs) to adapt to your style
- **AutoML Translation**: train completely custom translation models on your data (for significant quality improvement on domain-specific content)
- **Glossary support**: apply custom glossaries to batch and document translation
- **Translation memory**: reuse previous translations for identical segments

### Supported document formats (v3 document translation)
- HTML
- Plain text
- DOCX, PPTX, XLSX (Office Open XML)
- PDF (text-based; not scanned)

---

## Speech-to-Text (STT)

### Purpose
Convert spoken audio to text transcription with support for diverse accents, technical vocabulary, multiple speakers, and noisy environments.

### API modes

| Mode | Latency | Max Audio Duration | Use case |
|---|---|---|---|
| **Synchronous** (`recognize`) | Seconds | 60 seconds | Short clips, synchronous responses |
| **Asynchronous** (`longRunningRecognize`) | Minutes | 480 minutes (8 hours) | Long files from Cloud Storage |
| **Streaming** (`streamingRecognize`) | Real-time | None (continuous) | Live transcription, real-time captioning |

### Key features

| Feature | Description |
|---|---|
| **Model selection** | `latest_long`, `latest_short`, `phone_call`, `video`, `telephony`, `medical_dictation`, `medical_conversation` |
| **Chirp model** | Universal speech model; significantly more accurate for diverse accents and languages; higher cost |
| **Language support** | 125+ languages and dialects |
| **Speaker diarization** | Identify and label different speakers (`diarizationConfig`); up to 6 speakers |
| **Word-level timestamps** | Exact start/end time for each word |
| **Automatic punctuation** | Add periods, commas, question marks automatically |
| **Spoken punctuation** | Convert spoken "period", "comma" to punctuation marks |
| **Profanity filtering** | Replace profane words with `***` |
| **Word confidence** | Per-word confidence score |
| **Boost phrases** | Increase recognition probability for domain-specific terms (`speechContext`) |
| **Multi-channel recognition** | Transcribe each audio channel separately |
| **Multi-language** | Recognize multiple languages simultaneously (beta) |

### Audio encoding support
LINEAR16, FLAC, MULAW, AMR, AMR_WB, OGG_OPUS, SPEEX_WITH_HEADER_BYTE, MP3, WEBM_OPUS

### Batch transcription
For large volumes of audio files, use Cloud Speech-to-Text API batch processing or Vertex AI Chirp batch.

---

## Text-to-Speech (TTS)

### Purpose
Convert text to natural-sounding speech for voice applications, accessibility features, IVR systems, and content creation.

### Voice types

| Voice Type | Quality | Cost | Best for |
|---|---|---|---|
| **Standard** | Good | Lowest | High-volume, cost-sensitive |
| **WaveNet** | Very good | Medium | General production use |
| **Neural2** | Excellent | High | High-quality, natural-sounding apps |
| **Studio** | Studio-quality | Highest | Audiobooks, professional content |
| **Polyglot** | Good | Medium | Multilingual apps |
| **News** | Good | Medium | News reading, journalism |

### Key features
- **220+ voices** across 40+ languages and dialects
- **SSML support** (Speech Synthesis Markup Language): control prosody, pronunciation, pauses, emphasis, audio insertions
- **Audio formats**: MP3, OGG_OPUS, LINEAR16, MULAW, ALAW
- **Speaking rate**: 0.25x to 4.0x speed
- **Pitch**: -20 to +20 semitones
- **Volume gain**: -96dB to +16dB
- **Custom voice** (Journey): create a custom voice model from 30+ hours of voice recording data

### SSML example
```xml
<speak>
  Hello, <emphasis level="strong">welcome</emphasis> to our service.
  <break time="500ms"/>
  Your order number is
  <say-as interpret-as="digits">12345</say-as>.
  <break time="1s"/>
  The current time is
  <say-as interpret-as="time" format="hms12">2:30pm</say-as>.
</speak>
```

---

## Video Intelligence API

### Purpose
Analyze video content to detect scenes, objects, activities, text, and faces. Processes entire video files asynchronously (Cloud Storage input).

### Detection features

| Feature | Description | Output |
|---|---|---|
| **Label Detection** | Detect objects, activities, and concepts in video | Labels with temporal segments and confidence |
| **Shot Change Detection** | Detect cut/transitions between video shots | Timestamp ranges per shot |
| **Object Tracking** | Track objects across frames with bounding boxes | Object labels + bounding boxes + timestamps |
| **Speech Transcription** | Transcribe speech from the video's audio track | Word-level transcriptions with timestamps |
| **Text Detection (OCR in video)** | Detect and read text visible in video frames | Text content with temporal segments and bounding boxes |
| **Face Detection** | Detect faces in video frames | Bounding boxes, temporal segments |
| **Person Detection** | Detect and track people in video | Person tracks with bounding boxes |
| **Logo Recognition** | Detect corporate logos in video | Logo name, temporal segments, bounding boxes |
| **Explicit Content Detection** | Detect adult/violent content | Likelihood per frame |

### Label detection granularity
- `LABEL_DETECTION_MODE_VIDEO_LEVEL`: one label per video
- `LABEL_DETECTION_MODE_SHOT_MODE`: labels per shot
- `LABEL_DETECTION_MODE_FRAME_MODE`: labels per frame (most detailed; highest cost)

### Input and output
- Input: MP4, AVI, MOV, FLV, MKV, WebM stored in Cloud Storage
- Output: written to Cloud Storage (for long videos) or returned inline (for short)
- Always asynchronous (operation API)

---

## Recommendations AI (Retail API)

### Purpose
Provide personalized product recommendations for e-commerce applications. Trains on your catalog and user behavior data to generate individually personalized recommendation results.

### Workflow
1. **Import catalog**: ingest your product catalog (ID, title, description, category, price, availability) via BigQuery or GCS
2. **Ingest user events**: record user behavior in real-time or batch (`detail-page-view`, `add-to-cart`, `purchase-complete`, `category-page-view`, `search`, `home-page-view`, `shopping-cart-page-view`)
3. **Create a model**: choose a recommendation objective
4. **Create a serving config**: associate a model with serving configuration (number of results, diversification, etc.)
5. **Query predictions**: call `predict` API at serving time with a user ID and optional context

### Recommendation models

| Model Type | What it recommends |
|---|---|
| Others You May Like | Similar items to what the user viewed |
| Frequently Bought Together | Items often purchased with the current item |
| Recommended for You | Personalized homepage/section recommendations |
| Recently Viewed | User's own browsing history |
| Buy It Again | Repurchase recommendations for consumable products |
| On Sale | Sale items likely to interest the user |

### A/B testing
Recommendations AI supports serving configs with traffic splitting for A/B testing between different models or configurations.

---

## Best Practices

1. **Use Label Detection caching**: Vision API responses for the same image URI are cached; don't re-request labels for unchanged images.
2. **Batch Vision API requests**: send multiple images in a single `annotateImages` request (up to 16 per request) to reduce per-request overhead.
3. **Use `DOCUMENT_TEXT_DETECTION` instead of `TEXT_DETECTION` for multi-page documents**: it returns a richer layout-aware structure.
4. **Pre-filter audio before STT**: remove long silences and noise before sending to Speech-to-Text to reduce cost and improve accuracy.
5. **Use `speechContext` to boost domain vocabulary**: technical terms, product names, and proper nouns are frequently misrecognized without boosting.
6. **Use Neural2 or Studio voices for customer-facing TTS**: cheaper Standard/WaveNet voices are noticeably robotic; Neural2 is the minimum quality bar for production apps.
7. **Use async Video Intelligence for all but very short clips**: even clips under 60 seconds should use the async API in production to avoid connection timeouts.
8. **Warm up Recommendations AI models**: models need at least 30 days of user event data for meaningful personalization; seed with existing historical event data before going live.
9. **Monitor Natural Language API confidence scores**: entity detection and sentiment scores below 0.6 are often unreliable; implement confidence thresholds in your application.
10. **Use Translation v3 for production translation workflows**: v2 is simpler but v3 supports glossaries, batch, and document translation needed for enterprise use.
