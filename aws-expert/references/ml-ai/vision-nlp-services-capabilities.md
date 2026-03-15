# AWS Vision & NLP Services — Capabilities Reference
For CLI commands, see [vision-nlp-services-cli.md](vision-nlp-services-cli.md).

## Amazon Rekognition

**Purpose**: Deep learning-powered image and video analysis service requiring no ML expertise; provides pre-built models for common computer vision tasks.

### Image Analysis

| Feature | Description |
|---|---|
| **Detect labels** | Objects, scenes, concepts, and activities with confidence scores and bounding boxes |
| **Detect faces** | Face detection with attributes: age range, gender, emotions, facial hair, glasses, pose, quality |
| **Compare faces** | Compare a source face against a target image; returns similarity score |
| **Recognize celebrities** | Identify tens of thousands of celebrities across entertainment, sports, media, and politics |
| **Detect text** | OCR for printed and handwritten text in images; returns word-level bounding boxes |
| **Detect moderation labels** | Hierarchical taxonomy of unsafe content: explicit nudity, violence, drugs, hate symbols, etc. |
| **Detect custom labels** | Train custom classifiers using your own labeled images via Rekognition Custom Labels |
| **Analyze image properties** | Image quality, dominant colors, sharpness, brightness, contrast |

### Face Collections

| Concept | Description |
|---|---|
| **Collection** | Persistent store of indexed face vectors for search operations |
| **IndexFaces** | Add face vectors from an image to a collection |
| **SearchFacesByImage** | Find matching faces in a collection given an input image |
| **SearchFaces** | Search by an already-indexed face ID |
| **Face Liveness** | Verify a live user is present; detects spoofing, deepfakes, and 3D masks |

### Video Analysis

| Feature | Mode | Description |
|---|---|---|
| **Label detection** | Async (stored) | Detect objects, scenes, activities across video frames |
| **Face detection** | Async (stored) | Detect and track faces with attributes over time |
| **People pathing** | Async (stored) | Track identified people across frames with path coordinates |
| **Text detection** | Async (stored) | Detect text in video content |
| **Unsafe content** | Async (stored) | Moderate video content frame-by-frame |
| **Video segmentation** | Async (stored) | Identify black frames, end credits, slates, color bars |
| **Streaming video** | Real-time | Live video face analysis via Kinesis Video Streams |

---

## Amazon Textract

**Purpose**: Deep learning document analysis service that extracts text, data, and structure from scanned documents, PDFs, and images — going beyond simple OCR.

### Core APIs

| API | What It Extracts | Sync/Async |
|---|---|---|
| **DetectDocumentText** | Raw text (lines and words) with bounding boxes | Sync + Async |
| **AnalyzeDocument** | Text + forms (key-value pairs) + tables + signatures | Sync + Async |
| **AnalyzeExpense** | Invoice/receipt fields: vendor, total, line items, dates, amounts | Sync + Async |
| **AnalyzeID** | U.S. government-issued IDs: driver's license, passport fields | Sync only |
| **StartDocumentAnalysis** | Async version of AnalyzeDocument for multi-page documents | Async |
| **StartDocumentTextDetection** | Async text detection for multi-page documents | Async |

### Queries Feature

Natural language queries against a document:
- Example: "What is the patient's date of birth?" → Textract returns the value with a confidence score
- Custom queries allow fine-tuning the pre-trained Queries model with your document types

### Document Types and Use Cases

| Document Type | Recommended API |
|---|---|
| Scanned forms, PDFs with key-value pairs | `AnalyzeDocument` with `FORMS` feature type |
| Spreadsheets, tables in documents | `AnalyzeDocument` with `TABLES` feature type |
| Invoices, receipts | `AnalyzeExpense` |
| Driver's licenses, passports | `AnalyzeID` |
| Mortgage loan packages | Analyze Lending workflow (auto-routes pages to correct API) |
| Large multi-page documents | Async APIs (`StartDocumentAnalysis`) |

### Processing Modes

- **Synchronous**: Single-page documents; immediate response; up to 10 MB
- **Asynchronous**: Multi-page documents; start job → poll with `GetDocumentAnalysis` using job ID

---

## Amazon Comprehend

**Purpose**: Natural language processing (NLP) service using ML to extract insights and relationships from unstructured text.

### Pre-trained Insights

| Capability | Description |
|---|---|
| **Entity recognition** | Identifies named entities: PERSON, LOCATION, ORGANIZATION, DATE, QUANTITY, TITLE, EVENT, and more |
| **Key phrase extraction** | Extracts significant phrases (nouns and noun phrases) from text |
| **Sentiment analysis** | Document-level sentiment: POSITIVE, NEGATIVE, NEUTRAL, MIXED |
| **Targeted sentiment** | Sentiment toward specific named entities within a document |
| **Language detection** | Identifies the dominant language; supports 100+ languages |
| **Syntax analysis** | Part-of-speech tagging (noun, verb, adjective, etc.) for each word |
| **PII detection** | Identifies PII: name, address, SSN, credit card, phone, email, bank account, etc.; block or redact |

### Custom Models

| Feature | Description |
|---|---|
| **Custom classification** | Train a classifier to categorize documents into your own defined categories (multi-class or multi-label) |
| **Custom entity recognition (NER)** | Train a model to recognize domain-specific entities (product names, part numbers, medical codes) |
| **Flywheel** | Continuously retrain and manage custom model versions as new labeled data arrives |

### Batch Operations

All detection APIs support synchronous (single document), batch synchronous (up to 25 docs), and async batch jobs (large document sets from S3).

### Amazon Comprehend Medical

Separate service optimized for clinical text:
- Extracts medical entities: Medication, Dosage, Frequency, Anatomy, Medical Condition, Test/Treatment/Procedure
- Detects Protected Health Information (PHI)
- Maps entities to ICD-10-CM, RxNorm, and SNOMED CT ontologies

---

## Amazon Transcribe

**Purpose**: Automatic speech recognition (ASR) service that converts audio to text using deep learning; supports streaming and batch processing.

### Core Features

| Feature | Description |
|---|---|
| **Batch transcription** | Transcribe audio/video files stored in S3; supports MP3, MP4, WAV, FLAC, OGG, and more |
| **Streaming transcription** | Real-time speech-to-text via WebSocket or HTTP/2 streaming |
| **Speaker diarization** | Identify and label individual speakers in multi-speaker audio |
| **Multi-channel audio** | Transcribe each audio channel separately (e.g., agent and customer on separate channels) |
| **Custom vocabulary** | Improve recognition of domain-specific terms, product names, and acronyms |
| **Custom language model** | Train a custom acoustic model on your domain text data for improved accuracy |
| **PII redaction** | Automatically identify and redact PHI/PII from transcripts |
| **Content filtering** | Remove profanity and unwanted terms from transcripts |
| **Vocabulary filtering** | Filter out or mask specific words |

### Specialized Services

| Service | Description |
|---|---|
| **Transcribe Medical** | Optimized for clinical/medical conversations; recognizes medical terminology; HIPAA eligible |
| **Transcribe Call Analytics** | Call center focused: speaker sentiment, issue detection, call summarization, agent/customer labeling, interruption detection |

### Key Concepts

| Concept | Description |
|---|---|
| **Transcription job** | Async batch job; poll with `GetTranscriptionJob` for status |
| **Language code** | Required parameter; auto-identification available for batch |
| **Output location** | Transcript delivered to specified S3 bucket as JSON |
| **Confidence score** | Per-word confidence returned in detailed transcript |

---

## Amazon Translate

**Purpose**: Neural machine translation service providing high-quality, on-demand translation between 75+ language pairs for text and documents.

### Translation Modes

| Mode | Description |
|---|---|
| **Real-time translation** | `TranslateText` API; synchronous; up to 10,000 bytes per request |
| **Batch translation** | Async jobs processing documents in S3; supports TXT, HTML, DOCX, PPTX, XLIFF, etc. |
| **Document translation** | Translate a single document synchronously preserving formatting (console/SDK) |

### Customization Features

| Feature | Description |
|---|---|
| **Custom terminology** | Upload a CSV/TMX glossary mapping source terms to approved target translations; ensures consistent brand/product names |
| **Parallel data** | Upload example translation pairs to adapt translation style and domain (active customization); improves translations for your specific domain |
| **Formality setting** | Control formal vs. informal register for supported language pairs |
| **Profanity masking** | Replace profane words in translations with a grawlix (****) |

### Integration Patterns

Translate integrates with Amazon Comprehend (multilingual NLP), Amazon Transcribe (speech-to-translated-text pipelines), Amazon Polly (translated speech synthesis), and Amazon S3 (batch document workflows).

---

## Amazon Polly

**Purpose**: Text-to-speech (TTS) service that converts text into lifelike speech using deep learning; supports multiple voice types, languages, and speech control features.

### Voice Engine Types

| Engine | Description |
|---|---|
| **Generative** | Highest quality; most expressive and natural-sounding; powered by generative AI |
| **Long-form** | Optimized for long-form content (articles, books, broadcasts); natural prosody |
| **Neural (NTTS)** | High-quality neural TTS; supports Newscaster and Conversational speaking styles |
| **Standard** | Classic concatenative TTS; broadest language coverage; lower cost |

### Key Features

| Feature | Description |
|---|---|
| **SSML support** | Speech Synthesis Markup Language; control prosody, emphasis, breaks, pronunciation, speaking rate, volume, pitch |
| **Lexicons** | Custom pronunciation rules for domain-specific words (acronyms, product names, proper nouns) in PLS format |
| **Speech marks** | Metadata (word, sentence, viseme, SSML mark) returned with timing info; enables lip sync and karaoke effects |
| **Speaking styles** | Newscaster (news reading), Conversational (casual speech) — Neural engine only |
| **Output formats** | MP3, OGG Vorbis, PCM; configurable sample rate |

### Async Synthesis

For long texts or batch jobs, use `StartSpeechSynthesisTask` (async); output delivered to S3. `SynthesizeSpeech` is synchronous and suitable for short to medium texts.
