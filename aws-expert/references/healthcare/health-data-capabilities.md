# Health Data & Imaging — Capabilities Reference

For CLI commands, see [health-data-cli.md](health-data-cli.md).

## Amazon HealthLake

**Purpose**: HIPAA-eligible, FHIR R4-compliant managed data store that ingests, normalizes, and analyzes health data at scale; provides integrated NLP-based enrichment, search, and analytics over structured clinical data without managing infrastructure.

### Core Concepts

| Concept | Description |
|---|---|
| **Data store** | An isolated FHIR R4 repository identified by a data store ID; all resources are stored in a single AWS-managed account partition with server-side encryption (AWS-owned or CMK) |
| **FHIR R4** | Health Level 7 (HL7) Fast Healthcare Interoperability Resources Release 4; the standard data model for clinical resources (Patient, Observation, Condition, MedicationRequest, etc.) |
| **FHIR REST API** | HealthLake exposes a standards-compliant FHIR REST endpoint for `create`, `read`, `update`, `delete`, `search`, and `history` operations on FHIR resources |
| **Bulk import** | Asynchronous ingestion of large FHIR NDJSON files from S3; suitable for initial data loads and batch transfers |
| **Bulk export** | Asynchronous FHIR `$export` operation that writes all or filtered resources to S3 in NDJSON format |
| **SMART on FHIR** | OAuth 2.0-based authorization profile for FHIR; HealthLake data stores can be configured with SMART on FHIR identity providers for patient/provider-scoped access |
| **Integrated medical NLP** | Optional enrichment pipeline powered by Comprehend Medical that auto-annotates `DocumentReference` resources with ICD-10-CM, RxNorm, and SNOMED CT codes |
| **Analytics** | Bulk export to S3 feeds downstream analytics in Athena, Redshift, or SageMaker; HealthLake also integrates with QuickSight via Athena |

### FHIR Resource Operations

| Operation | HTTP Method | Description |
|---|---|---|
| **Create** | `POST /datastore/{id}/r4/{ResourceType}` | Create a new FHIR resource; server assigns an ID |
| **Read** | `GET /datastore/{id}/r4/{ResourceType}/{id}` | Retrieve a resource by logical ID |
| **Update** | `PUT /datastore/{id}/r4/{ResourceType}/{id}` | Full replacement of a resource |
| **Delete** | `DELETE /datastore/{id}/r4/{ResourceType}/{id}` | Logical delete (resource remains with a `deleted` history entry) |
| **Search** | `GET /datastore/{id}/r4/{ResourceType}?{params}` | Search by FHIR search parameters (patient, date, code, identifier, etc.) |
| **History** | `GET /datastore/{id}/r4/{ResourceType}/{id}/_history` | Version history of a resource |
| **Transaction** | `POST /datastore/{id}/r4` with Bundle type `transaction` | Atomic multi-resource operation |
| **Bulk import** | `StartFHIRImportJob` API | Import NDJSON files from S3 asynchronously |
| **Bulk export** | `StartFHIRExportJob` API | Export resources to S3 as NDJSON asynchronously |

### Data Store Configuration

| Setting | Options |
|---|---|
| **Encryption** | AWS-owned key (default) or customer-managed KMS CMK |
| **Preloaded data** | Optionally pre-populate with Synthea-generated synthetic patient data for development/testing |
| **Identity provider** | Cognito User Pool or external IdP for SMART on FHIR authorization |
| **Tagging** | Key-value tags on the data store for cost allocation and access control |

---

## Amazon HealthImaging

**Purpose**: Purpose-built, HIPAA-eligible medical imaging store for petabyte-scale DICOM data; stores images in a high-performance, cloud-native format (HTJ2K) with sub-second frame retrieval, enabling AI/ML inference directly on pixel data without separate DICOM servers.

### Core Concepts

| Concept | Description |
|---|---|
| **Datastore** | Top-level container for medical imaging data; analogous to a PACS; encrypted with an AWS-owned key or CMK |
| **Import job** | Asynchronous operation that ingests a DICOM P10 dataset from an S3 source bucket into a datastore; assigns a `jobId` for status tracking |
| **Image set** | Logical grouping of DICOM instances sharing a common study; the primary addressable unit in HealthImaging; contains DICOM metadata and one or more image frames |
| **Image set metadata** | Study/series/instance-level DICOM attributes stored as a structured JSON document; searchable and updatable independently of pixel data |
| **Image frame** | A single 2D pixel plane within an image set; stored and retrieved individually; encoded in HTJ2K (High-Throughput JPEG 2000) |
| **HTJ2K** | High-Throughput JPEG 2000; a modern, lossless (or lossy) wavelet codec optimized for fast random access, progressive decoding, and ML inference pipelines |
| **Pixel data** | Raw decoded frame bytes; retrieved via `GetImageFrame` and decoded client-side using HTJ2K decoders (openjph, OpenJPEG, or AWS-provided SDKs) |
| **Copy image set** | Creates an independent copy of an image set within the same or different datastore |
| **Delete image set** | Marks an image set for deletion; deletion occurs asynchronously |

### Datastore Lifecycle

| State | Description |
|---|---|
| `CREATING` | Provisioning in progress |
`ACTIVE` | Ready to accept import jobs and serve image data |
| `DELETING` | Deletion in progress |

### Image Set Lifecycle States

| State | Description |
|---|---|
| `ACTIVE` | Fully ingested and retrievable |
| `LOCKED` | Being modified (copy, update) — read-only during lock |
| `DELETED` | Soft-deleted; not retrievable |

### Key Operations

| Operation | API Call | Description |
|---|---|---|
| **Create datastore** | `CreateDatastore` | Provision a new imaging datastore with optional CMK |
| **Start import** | `StartDICOMImportJob` | Import DICOM files from S3; specify source S3 URI and IAM role |
| **Get import job** | `GetDICOMImportJob` | Poll import job status (`IN_PROGRESS`, `COMPLETED`, `FAILED`) |
| **List image sets** | `SearchImageSets` | Search image sets by DICOM attributes (PatientID, StudyDate, Modality, etc.) |
| **Get metadata** | `GetImageSetMetadata` | Retrieve DICOM metadata JSON for a specific image set version |
| **Get image frame** | `GetImageFrame` | Stream the raw HTJ2K-encoded bytes of a single frame |
| **Update metadata** | `UpdateImageSetMetadata` | Add, remove, or copy DICOM attributes without re-importing pixel data |
| **Copy image set** | `CopyImageSet` | Duplicate image set within or across datastores |
| **Delete image set** | `DeleteImageSet` | Soft-delete an image set |

---

## AWS HealthOmics

**Purpose**: Managed service for storing, querying, and analyzing genomic and multiomics data at scale; provides purpose-built omics data stores, managed workflow execution (WDL/Nextflow/CWL), and ready2run curated bioinformatics pipelines — replacing the need to manage HPC clusters for genomics workloads.

### Storage — Omics Store Types

| Store Type | Description |
|---|---|
| **Sequence store** | Stores raw genomics read data as FASTQ, BAM, CRAM, or UBAM files; optimized for large binary genomics data; objects called **read sets** |
| **Reference store** | Stores genome reference assemblies (FASTA); read sets link to a reference; each account has one reference store per region |
| **Variant store** | Stores small variant call data in VCF, gVCF, or BCF format at scale; queryable via Athena |
| **Annotation store** | Stores genome annotation data (GFF3, GTF, VCF, TSV); queryable via Athena alongside variant data |

### Sequence Store — Read Set Lifecycle

| Concept | Description |
|---|---|
| **Read set** | A file (or paired-end pair) uploaded to a sequence store; has metadata (subject ID, sample ID, reference ARN, file type) |
| **Import read set job** | Asynchronous job to import read set files from S3 (`StartReadSetImportJob`) |
| **Export read set job** | Asynchronous job to export read sets back to S3 for external processing (`StartReadSetExportJob`) |
| **Activation job** | Re-activates read sets from archived state for retrieval (`StartReadSetActivationJob`) |

### Variant & Annotation Stores

| Concept | Description |
|---|---|
| **Variant store** | Created with a reference genome; ingests VCF/gVCF/BCF via `CreateVariantStore` + `StartVariantImportJob` |
| **Annotation store** | Ingests GFF3/GTF/VCF/TSV annotation files; queryable alongside variant data in Athena |
| **Athena integration** | Both variant and annotation stores surface data as Athena-queryable tables in the AWS Glue Data Catalog |

### Workflows — Run Execution

| Concept | Description |
|---|---|
| **Workflow** | A bioinformatics pipeline definition in WDL (Workflow Description Language), Nextflow, or CWL; uploaded and versioned in HealthOmics |
| **Run** | A single execution of a workflow with specific inputs; HealthOmics provisions managed compute (no cluster management) |
| **Run group** | A named container that limits concurrent runs and total CPU/GPU for cost and quota control |
| **Task** | An individual step within a workflow run; each task runs in an isolated container with specified `cpu`, `memory`, `gpus` |
| **Log group** | Each run streams logs to CloudWatch Logs for observability |

### Ready2Run Workflows

**Ready2Run** workflows are AWS-curated, pre-validated bioinformatics pipelines available without uploading a workflow definition:

| Pipeline | Description |
|---|---|
| **GATK Best Practices — Germline SNP/Indel** | BWA-MEM alignment + GATK HaplotypeCaller; produces gVCF |
| **GATK Best Practices — Somatic SNV/Indel** | Mutect2-based somatic variant calling from tumor/normal pairs |
| **GATK Best Practices — Joint Genotyping** | Combines multiple gVCFs via GenomicsDBImport + GenotypeGVCFs |
| **GATK Best Practices — RNA-seq** | STAR alignment + GATK RNA variant calling |
| **DeepVariant** | Google DeepVariant germline variant calling |
| **CWL Tool Workflows** | CWL-based alignment and QC pipelines |

### Analytics

| Feature | Description |
|---|---|
| **Athena queries** | Variant and annotation stores are automatically catalogued in Glue; query with standard SQL in Athena |
| **SageMaker integration** | Run groups can output to S3 for downstream ML model training in SageMaker |
| **Cross-account sharing** | Share sequence stores and variant stores across accounts via AWS RAM |

---

## AWS HealthScribe

**Purpose**: HIPAA-eligible, generative AI-powered service that automatically transcribes medical conversations (patient-clinician encounters) and generates structured clinical notes with sections (subjective, objective, assessment, plan) — reducing documentation burden for clinicians.

### Core Concepts

| Concept | Description |
|---|---|
| **Medical conversation** | A recorded or streamed audio interaction between a clinician and patient; the primary input to HealthScribe |
| **Streaming transcription** | Real-time transcription of a live conversation using the HealthScribe streaming API; requires an audio stream over WebSocket |
| **Batch transcription job** | Asynchronous job (`StartMedicalScribeJob`) that processes a pre-recorded audio file from S3 |
| **Transcript** | Word-level timestamped transcription of the conversation with speaker labels (CLINICIAN or PATIENT) |
| **Clinical note** | A structured SOAP-like document generated from the transcript; divided into named sections |
| **Summarization model** | The LLM layer that reads the transcript and generates clinical note sections; outputs include evidence from transcript |
| **Evidence** | Each clinical note statement links back to the specific transcript segment(s) that support it — enabling clinician review and audit |

### Clinical Note Sections

| Section | Description |
|---|---|
| **SUBJECTIVE** | Patient-reported symptoms, history of present illness, review of systems — drawn from patient's own statements |
| **OBJECTIVE** | Clinical observations, vital signs, physical exam findings — drawn from clinician statements |
| **ASSESSMENT** | Differential diagnoses and working assessments stated during the encounter |
| **PLAN** | Treatment plan, prescriptions, follow-up instructions, referrals — drawn from clinician decision statements |
| **HISTORY** | Past medical, surgical, family, and social history mentioned during the encounter |
| **CHIEF_COMPLAINT** | The primary reason for the visit as expressed by the patient |

### Batch Job Configuration

| Setting | Options |
|---|---|
| **Input** | S3 URI to audio file (MP3, MP4, WAV, FLAC, AMR, OGG, WebM) |
| **Output** | S3 prefix where transcript JSON and clinical note JSON are written |
| **Channel identification** | Identify speaker channels when audio is recorded in stereo (channel 0 = clinician, channel 1 = patient, or vice versa) |
| **Vocabulary filter** | Custom vocabulary filter to mask or replace specific terms |
| **Custom vocabulary** | Domain-specific pronunciation hints for medications, procedures, and clinical terms |
| **Data access role** | IAM role HealthScribe assumes to read input S3 and write output S3 |
| **KMS encryption** | Optional CMK for encrypting output files |
| **Tags** | Key-value tags for cost allocation |

### Streaming API

| Concept | Description |
|---|---|
| **WebSocket stream** | HealthScribe streaming uses a bidirectional WebSocket connection to send audio chunks and receive real-time transcript events |
| **Session** | A single streaming session for one encounter; has a `SessionId` for correlation |
| **Audio encoding** | PCM (16-bit linear), FLAC, or Opus; sample rate 8000 or 16000 Hz |
| **Speaker role** | Streaming events include `CLINICIAN` or `PATIENT` role for each utterance segment |
| **Partial/final results** | Streaming returns `PARTIAL` transcripts updated in real time and `FINAL` stable results per utterance |

### Output Structure

```
{
  "JobName": "encounter-2026-03-14",
  "Transcript": {
    "TranscriptFileUri": "s3://bucket/prefix/transcript.json"
  },
  "ClinicalDocumentation": {
    "Sections": [
      {
        "SectionName": "CHIEF_COMPLAINT",
        "Summary": [{ "SummarizedSegment": "...", "EvidenceLinks": [...] }]
      },
      ...
    ]
  }
}
```

### Key Patterns

- **EHR integration**: Run a batch job post-encounter → parse clinical note JSON → pre-populate EHR fields for clinician review and sign-off
- **Real-time ambient documentation**: Use streaming API during the encounter → display live transcript and draft note on a secondary screen
- **Audit trail**: `EvidenceLinks` in each note segment link to exact transcript timestamps — satisfying documentation review requirements
- **Cost model**: Charged per second of audio processed; batch and streaming priced identically per audio-second
