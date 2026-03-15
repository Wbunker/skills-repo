# Clinical NLP — Capabilities Reference

For CLI commands, see [clinical-nlp-cli.md](clinical-nlp-cli.md).

## Amazon Comprehend Medical

**Purpose**: HIPAA-eligible, pre-trained NLP service that extracts medical entities (conditions, medications, anatomy, procedures, protected health information) from unstructured clinical text, maps them to standard ontologies (RxNorm, ICD-10-CM, SNOMED CT), and identifies relationships between entities — without requiring ML expertise.

### Core Concepts

| Concept | Description |
|---|---|
| **Entity** | A discrete clinical concept extracted from text; has a `Type`, `Category`, `Score` (confidence 0–1), `BeginOffset`, and `EndOffset` |
| **Category** | Broad classification of an entity (e.g., `MEDICAL_CONDITION`, `MEDICATION`, `ANATOMY`, `PROTECTED_HEALTH_INFORMATION`, `TEST_TREATMENT_PROCEDURE`) |
| **Trait** | A modifier on an entity that changes its clinical meaning (e.g., `NEGATION` — "no fever"; `SIGN` vs. `SYMPTOM`; `DIAGNOSIS`; `PERTAINS_TO_FAMILY`) |
| **Attribute** | A related piece of information that describes or qualifies an entity (e.g., a dosage attribute linked to a medication entity, or a direction attribute linked to an anatomy entity) |
| **Ontology linking** | Maps extracted entities to standard medical codes (RxNorm concept IDs, ICD-10-CM codes, SNOMED CT codes) with confidence scores |
| **Relationship** | A typed connection between two entities in the same text (e.g., `DOSAGE` → `MEDICATION`, `SYSTEM_ORGAN_SITE` → `MEDICAL_CONDITION`) |
| **Batch job** | Asynchronous processing of large volumes of clinical documents stored in S3; results written as JSON to an output S3 prefix |

### Entity Categories

| Category | Description | Example Entities |
|---|---|---|
| **MEDICAL_CONDITION** | Diseases, disorders, symptoms, diagnoses, signs | "hypertension", "shortness of breath", "type 2 diabetes" |
| **MEDICATION** | Drug names, brand names, generic names, dosages, frequencies, routes, strengths | "metformin 500 mg twice daily", "lisinopril 10 mg PO" |
| **ANATOMY** | Body parts, locations, systems | "left ventricle", "lumbar spine", "hepatic artery" |
| **TEST_TREATMENT_PROCEDURE** | Lab tests, imaging, surgical procedures, therapies | "CBC", "MRI brain", "laparoscopic cholecystectomy" |
| **PROTECTED_HEALTH_INFORMATION** | HIPAA PHI elements | "John Smith", "555-867-5309", "DOB: 1975-04-12", "123 Main St" |
| **TIME_EXPRESSION** | Dates, times, durations, frequencies referenced in clinical context | "3 weeks ago", "since childhood", "every 8 hours" |

### Traits

| Trait | Meaning |
|---|---|
| `NEGATION` | Entity is explicitly negated ("denies chest pain", "no fever") |
| `SIGN` | Entity is an objective clinical finding observed by a clinician |
| `SYMPTOM` | Entity is a subjective complaint reported by the patient |
| `DIAGNOSIS` | Entity is explicitly identified as a diagnosis |
| `PERTAINS_TO_FAMILY` | Entity refers to a family member's history, not the patient |
| `HYPOTHETICAL` | Entity is speculative or conditional ("rule out pneumonia") |

### PHI Entity Types (DetectPHI)

| PHI Type | Description |
|---|---|
| `NAME` | Patient, provider, or third-party names |
| `DATE` | Dates (birth date, appointment date, procedure date) |
| `AGE` | Patient age or age of family members |
| `PHONE` | Phone and fax numbers |
| `EMAIL` | Email addresses |
| `ADDRESS` | Street addresses, city, state, ZIP |
| `ID` | Medical record numbers, account numbers, SSN, device IDs |
| `URL` | Web URLs |
| `PROFESSION` | Occupation that could identify the patient |

### Ontology Linking

| Ontology | API | Use Case |
|---|---|---|
| **RxNorm** | `InferRxNorm` | Maps medication mentions to standard RxNorm concept IDs (RxCUI) for drug interoperability and e-prescribing |
| **ICD-10-CM** | `InferICD10CM` | Maps medical conditions and diagnoses to ICD-10-CM billing and coding classification codes |
| **SNOMED CT** | `InferSNOMEDCT` | Maps medical conditions, anatomy, and procedures to SNOMED CT clinical terminology concepts |

Each ontology response includes a ranked list of candidate codes with `Score` (confidence), `Code`, `Description`, and `Trait` information.

### Relationship Extraction

| Relationship Type | Example |
|---|---|
| `DOSAGE` → `MEDICATION` | "500 mg" modifies "metformin" |
| `ROUTE_OR_MODE` → `MEDICATION` | "orally" modifies "lisinopril" |
| `FREQUENCY` → `MEDICATION` | "twice daily" modifies "metformin" |
| `STRENGTH` → `MEDICATION` | "10 mg" modifies "atorvastatin" |
| `DURATION` → `MEDICATION` | "for 10 days" modifies "amoxicillin" |
| `SYSTEM_ORGAN_SITE` → `MEDICAL_CONDITION` | "pulmonary" modifies "embolism" |
| `DIRECTION` → `ANATOMY` | "left" modifies "femur" |
| `ACUITY` → `MEDICAL_CONDITION` | "severe" modifies "pain" |
| `TEST_VALUE` → `TEST_TREATMENT_PROCEDURE` | "140/90" modifies "blood pressure" |

### API Operations (Real-Time)

| Operation | Description | Input Limit |
|---|---|---|
| `DetectEntitiesV2` | Extract all medical entities with categories, traits, and attributes; V2 recommended over V1 | ~20 KB |
| `DetectPHI` | Extract only HIPAA PHI entities (NAME, DATE, AGE, ADDRESS, etc.) | ~20 KB |
| `InferRxNorm` | Extract medications and link to RxNorm concept IDs | ~20 KB |
| `InferICD10CM` | Extract conditions and link to ICD-10-CM codes | ~20 KB |
| `InferSNOMEDCT` | Extract conditions, anatomy, procedures and link to SNOMED CT | ~20 KB |

### Batch Operations (Async, S3-based)

| Operation | Description |
|---|---|
| `StartEntitiesDetectionV2Job` | Batch DetectEntitiesV2 over many documents in S3 |
| `StartPHIDetectionJob` | Batch PHI detection over documents in S3 |
| `StartRxNormInferenceJob` | Batch RxNorm ontology linking |
| `StartICD10CMInferenceJob` | Batch ICD-10-CM ontology linking |
| `StartSNOMEDCTInferenceJob` | Batch SNOMED CT ontology linking |

### Key Patterns

- **Clinical coding assistance**: Run `InferICD10CM` on discharge summaries → suggest ICD codes for medical coders to review, reducing manual lookup time
- **Medication reconciliation**: Run `InferRxNorm` on medication lists in free text → normalize to RxCUI → feed into pharmacy systems for interaction checking
- **De-identification pipeline**: Run `DetectPHI` → redact or replace all PHI offsets in the text → produce de-identified documents for research datasets
- **Cohort identification**: Batch process EHR notes with `StartEntitiesDetectionV2Job` → index extracted conditions in OpenSearch for patient cohort queries
- **Adverse event detection**: Extract MEDICATION entities + NEGATION/SIGN traits → identify mentions of adverse drug reactions in clinical notes

---

## Amazon Transcribe Medical

**Purpose**: HIPAA-eligible automatic speech recognition (ASR) service optimized for medical terminology and clinical conversations; supports multiple medical specialties, batch transcription of recordings, and real-time streaming — producing accurate medical transcripts with speaker identification and channel separation.

### Core Concepts

| Concept | Description |
|---|---|
| **Medical ASR model** | Specialized speech recognition model trained on medical vocabulary; higher accuracy for drug names, anatomical terms, and clinical jargon than general Transcribe |
| **Specialty** | A clinical domain that further specializes recognition accuracy within that field |
| **Transcription job** | Asynchronous batch job that processes a pre-recorded audio file from S3 |
| **Streaming transcription** | Real-time ASR over a WebSocket or HTTP/2 stream; returns partial and final transcript events |
| **Speaker identification** | Identifies and labels distinct speakers in a recording (up to 10 speakers in batch jobs) |
| **Channel identification** | For multi-channel audio, transcribes each channel independently and merges results with channel labels |
| **Custom vocabulary** | A list of custom medical terms (drug names, procedures, proper names) with optional display forms and pronunciation hints |
| **Vocabulary filter** | A list of words to mask or remove from the transcript (e.g., filler words, profanity) |
| **Output transcript** | JSON document with word-level timestamps, confidence scores, speaker labels, and the full transcript text |

### Supported Medical Specialties

| Specialty | `Specialty` Value | Use Case |
|---|---|---|
| Primary Care | `PRIMARYCARE` | General practice, family medicine encounters |
| Cardiology | `CARDIOLOGY` | Cardiac procedures, ECG interpretation, cardiology notes |
| Neurology | `NEUROLOGY` | Neurological exams, stroke assessments, neurology notes |
| Oncology | `ONCOLOGY` | Cancer diagnosis and treatment notes, chemotherapy regimens |
| Radiology | `RADIOLOGY` | Radiology report dictation (CT, MRI, X-ray findings) |
| Urology | `UROLOGY` | Urological procedure notes and consultations |

### Transcription Job Configuration

| Setting | Options | Description |
|---|---|---|
| **Media format** | mp3, mp4, wav, flac, amr, ogg, webm | Audio format of the source file |
| **Sample rate** | 16000 Hz recommended | Audio sample rate (8000 or 16000 Hz) |
| **Language code** | `en-US` | Medical transcription supports US English |
| **Type** | `CONVERSATION`, `DICTATION` | `CONVERSATION` for patient-clinician dialogue; `DICTATION` for single-speaker dictation (radiology reports) |
| **Specialty** | See table above | Clinical domain for specialized vocabulary |
| **Speaker labels** | `ShowSpeakerLabels: true`, `MaxSpeakerLabels: 2–10` | Identify and label distinct speakers |
| **Channel identification** | `ChannelIdentification: true` | Transcribe each audio channel separately |
| **Custom vocabulary** | Vocabulary name | Reference a pre-created custom medical vocabulary |
| **Content identification** | `PHIIdentification` | Identify and tag PHI in the transcript |
| **Content redaction** | `PHIRedaction` | Redact PHI from the transcript output |
| **Output encryption** | KMS key ARN | Encrypt the output transcript file |

### Streaming Transcription

| Concept | Description |
|---|---|
| **Protocol** | HTTP/2 or WebSocket event streams |
| **Audio encoding** | PCM (signed 16-bit little-endian), FLAC, or OGG-Opus |
| **Sample rate** | 8000 or 16000 Hz |
| **Result stability** | `STABLE` results are unlikely to change; `UNSTABLE` results are in-progress partial transcripts |
| **Partial results stabilization** | Enable `EnablePartialResultsStabilization` + `PartialResultsStability` (`LOW`, `MEDIUM`, `HIGH`) to control how quickly partial results are committed |
| **Speaker labels** | Available in streaming for real-time speaker diarization |
| **Vocabulary filters** | Can be applied in real time during streaming |
| **Endpoint** | Regional HTTPS streaming endpoint (e.g., `transcribestreaming.us-east-1.amazonaws.com`) |

### PHI Identification and Redaction

| Feature | Description |
|---|---|
| **PHI identification** | Tags PHI entities (names, dates, ages, phone numbers, addresses) in the transcript with entity type labels |
| **PHI redaction** | Replaces PHI in the output transcript with `[PHI]` placeholder — produces a de-identified transcript |
| **Availability** | Supported in both batch transcription jobs and streaming |

### Custom Vocabulary

| Field | Description |
|---|---|
| **Phrase** | The word or phrase as it should appear in the transcript (display form) |
| **SoundsLike** | Phonetic hint for unusual pronunciations (e.g., drug names) |
| **IPA** | International Phonetic Alphabet pronunciation |
| **DisplayAs** | Override the display representation (e.g., lowercase, abbreviation) |

Example vocabulary table row: `Xarelto\t\t\tXarelto` (phrase with display form)

### Output Transcript Structure

```json
{
  "jobName": "radiology-report-001",
  "accountId": "123456789012",
  "results": {
    "transcripts": [{ "transcript": "The chest CT demonstrates a 1.2 cm pulmonary nodule in the right upper lobe..." }],
    "items": [
      {
        "start_time": "0.0",
        "end_time": "0.31",
        "alternatives": [{ "confidence": "0.999", "content": "The" }],
        "type": "pronunciation"
      }
    ],
    "speaker_labels": {
      "speakers": 2,
      "segments": [
        { "speaker_label": "spk_0", "start_time": "0.0", "end_time": "12.5", "items": [...] }
      ]
    }
  },
  "status": "COMPLETED"
}
```

### Key Patterns

- **Radiology report dictation**: Use `DICTATION` type + `RADIOLOGY` specialty → stream or batch process radiologist dictation → structured report for PACS/RIS integration
- **Clinical encounter documentation**: Use `CONVERSATION` type + `PRIMARYCARE` or relevant specialty → transcript feeds into HealthScribe for clinical note generation
- **Real-time captioning**: Streaming API with `STABLE` partial results → display live captions of clinical conversation on ambient display
- **De-identified research dataset**: Batch transcription with `PHIRedaction` → de-identified transcripts for NLP model training without HIPAA PHI exposure
- **Post-visit summary**: Transcribe patient-clinician call → pipe transcript text through Comprehend Medical for entity extraction → generate structured visit summary
