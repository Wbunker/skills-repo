# Cloud Healthcare API — Capabilities

## Overview

The **Cloud Healthcare API** is a HIPAA-compliant managed service for storing, processing, and sharing healthcare data in Google Cloud. It provides standards-based APIs for the three primary healthcare data standards: FHIR, DICOM, and HL7 v2.

**Key compliance properties:**
- HIPAA Business Associate Agreement (BAA) available
- HITECH Act compliant
- SOC 2 Type II certified
- Data encrypted at rest (AES-256) and in transit (TLS 1.2+)
- Cloud Audit Logs capture all data access and admin operations
- VPC Service Controls support for data perimeter enforcement

---

## Architecture: Datasets and Stores

**Dataset**: the top-level container resource; scoped to a region; holds one or more data stores; inherits project-level IAM.

**Data stores**: created within a dataset; each store is specific to one standard:
- FHIR stores for FHIR resources
- DICOM stores for medical images
- HL7 v2 stores for HL7 v2 messages

```
projects/my-project/
└── locations/us-central1/
    └── datasets/hospital-ehr/
        ├── fhirStores/r4-patient-data/
        ├── dicomStores/radiology-images/
        └── hl7V2Stores/adt-messages/
```

---

## FHIR Store

### Supported FHIR Versions

| Version | Status | Notes |
|---|---|---|
| FHIR R4 (4.0.1) | GA | Recommended for new implementations |
| FHIR STU3 (3.0.1) | GA | Legacy; R4 preferred |
| FHIR DSTU2 (1.0.2) | Limited | Only for legacy integrations |

### FHIR RESTful API

The FHIR store implements the standard FHIR RESTful API:

**CRUD operations:**
- `GET /fhir/{resourceType}/{id}` — read a resource
- `POST /fhir/{resourceType}` — create a resource
- `PUT /fhir/{resourceType}/{id}` — update (full replacement)
- `PATCH /fhir/{resourceType}/{id}` — partial update (JSON Patch)
- `DELETE /fhir/{resourceType}/{id}` — delete a resource
- `GET /fhir/{resourceType}/{id}/_history` — version history
- `GET /fhir/{resourceType}/{id}/_history/{vid}` — specific version

**Search:**
- `GET /fhir/{resourceType}?param=value` — search by parameters
- `POST /fhir/{resourceType}/_search` — search with POST body
- Supported parameters: `_id`, `_lastUpdated`, patient-specific parameters (subject, patient), date ranges, coded values
- Chained searches, reverse chaining (`_has`)

**Batch and Transaction:**
- `POST /fhir` with Bundle resource (type=batch or type=transaction)
- Transactions are atomic (all-or-nothing); batches are independent

**FHIR Operations (Special):**
- `$everything`: get all resources for a patient (Patient/{id}/$everything)
- `$validate`: validate a resource against a profile
- `$convert`: convert between FHIR versions (R4 ↔ STU3)
- `$patient-everything`: full patient clinical summary export
- `$export`: bulk data export (async; NDJSON output to GCS)

### SMART on FHIR Authorization

Identity Platform or any OIDC provider can issue tokens with SMART scopes:
- `patient/Patient.read` — read specific patient's data
- `system/Observation.write` — system-level write to Observation resources
- `user/MedicationRequest.*` — user-level access to MedicationRequest resources
- Integrate with Identity Platform for consumer-facing SMART apps

### FHIR Notifications

Configure Pub/Sub notifications on FHIR store for:
- New resource created
- Resource updated
- Resource deleted
- Bulk export complete

Enables event-driven architectures: trigger Cloud Functions on new clinical observations, alert on critical lab values, sync to downstream systems.

### FHIR Bulk Export

Export all FHIR resources to Cloud Storage:
- Output format: NDJSON (one JSON object per line; one file per resource type)
- Supports `_type` filter (export only specific resource types)
- `_since` filter (export resources modified after a timestamp)
- Export initiated via `POST /fhir/$export`; returns operation name; poll for completion
- Use for: analytics export to BigQuery, backup, migration to another FHIR server

### BigQuery Streaming Integration

Configure FHIR store to stream resources to BigQuery automatically:
- Each FHIR resource type becomes a BigQuery table (`Patient`, `Observation`, `Condition`, etc.)
- Resources are denormalized to BigQuery-friendly schema
- Supports both R4 and STU3 schemas
- Use BigQuery to run population-level analytics, cohort identification, clinical quality measures

---

## DICOM Store

**DICOM** (Digital Imaging and Communications in Medicine) is the standard for medical imaging data (X-rays, CT scans, MRI, pathology whole-slide images, ultrasounds).

### DICOMweb API

The DICOM store implements the DICOMweb standard:

| Service | Description |
|---|---|
| **STOW-RS** (Store) | Upload DICOM instances (studies/series/instances) |
| **WADO-RS** (Retrieve) | Retrieve DICOM instances, frames, metadata |
| **QIDO-RS** (Query) | Search for studies, series, instances by DICOM attributes |

### DICOM Hierarchy

```
Study (one exam/encounter)
└── Series (one acquisition/sequence)
    └── Instance (one image)
```

Each level has a UID (Study Instance UID, Series Instance UID, SOP Instance UID).

### De-identification for DICOM

The DICOM store includes built-in de-identification:
- Removes or replaces PHI burned into DICOM metadata tags (patient name, date of birth, MRN, etc.)
- Options: keep study UIDs or remap to new UIDs; keep dates or shift by random offset
- PHI redaction from pixel data (burned-in annotations): requires separate image processing
- Output to a new DICOM store (original is preserved)

### OHIF Viewer Integration

The **Open Health Imaging Foundation (OHIF) Viewer** can be configured to read directly from Cloud Healthcare API DICOM stores via DICOMweb, enabling browser-based medical image viewing without a separate PACS server.

### Large-Scale Imaging

- No individual file size limits (supports multi-GB whole-slide pathology images)
- Parallel upload via STOW-RS multipart
- Thumbnail and frame-level retrieval for efficient loading
- Integration with Vertex AI for ML-based image analysis (anomaly detection, segmentation)

---

## HL7 v2 Store

**HL7 v2** is the most widely deployed healthcare messaging standard, used for point-to-point exchange between hospital systems (EHR, lab, pharmacy, ADT).

### Supported Message Types

- **ADT (Admit/Discharge/Transfer)**: patient movement events; A01 (admit), A02 (transfer), A03 (discharge), A04 (register)
- **ORM (Order Message)**: clinical orders (labs, radiology)
- **ORU (Observation Result)**: lab results, radiology reports
- **DFT (Detailed Financial Transaction)**: billing/charges
- **MDM (Medical Document Management)**: clinical documents
- **MFN (Master File Notification)**: reference data updates

### HL7 v2 Operations

- `projects.locations.datasets.hl7V2Stores.messages.create`: ingest a single message
- `projects.locations.datasets.hl7V2Stores.messages.list`: list messages with filters
- `projects.locations.datasets.hl7V2Stores.messages.get`: retrieve a message by ID
- `projects.locations.datasets.hl7V2Stores.messages.delete`: delete a message

### Pub/Sub Notifications

Configure a Pub/Sub topic on the HL7 v2 store to receive notifications when messages are ingested:
- One notification per message received
- Notification includes message ID and store path
- Consumer Cloud Function or Dataflow job processes the HL7 v2 data
- Use for real-time integration: parse ADT messages → update patient state in Firestore

### MLLP to Cloud Healthcare Routing

MLLP (Minimum Lower Layer Protocol) is the traditional transport for HL7 v2. Route MLLP traffic to Cloud Healthcare API:
- Deploy MLLP adapter (GCP provided Docker image) on GCE or GKE
- MLLP adapter receives HL7 v2 over TCP (MLLP) from hospital systems
- Converts and forwards messages to Cloud Healthcare API via HTTPS
- Sends HL7 ACK/NACK back to the source system

---

## De-identification

Cloud Healthcare API provides built-in PHI de-identification for all three data types:

### FHIR De-identification

- Transforms FHIR resources to remove PHI
- Supported transforms: `REPLACE_WITH_INFO_TYPE`, `DATE_SHIFT`, `CRYPTO_REPLACE_FFX_FPE`, `REMOVE`, `TRANSFORM`
- PHI element types detected: names, addresses, dates, phone numbers, email, SSN, medical record numbers
- Integration with Cloud DLP for configurable redaction

### DICOM De-identification

- Removes PHI from DICOM metadata tags (Patient Name, Patient ID, dates, institution name)
- Options to keep or reassign Study/Series/SOP Instance UIDs
- Date shifting for preserving temporal relationships
- Pixel data redaction (for burned-in annotations) requires pixel validation config

### HL7 v2 De-identification

- Parses HL7 v2 segments and removes/replaces PHI fields
- Segment-level de-identification: PID, NK1, PV1 segments

---

## Healthcare NLP API

The **Healthcare Natural Language API** extracts medical entities and relationships from clinical text (doctor notes, discharge summaries, pathology reports, clinical trial protocols).

### Entity Types Extracted

| Entity Type | Examples |
|---|---|
| Medical conditions | "hypertension", "type 2 diabetes", "acute MI" |
| Medications | "metformin 500mg", "lisinopril", "aspirin daily" |
| Procedures | "coronary artery bypass graft", "CBC panel" |
| Anatomy | "left ventricle", "right knee", "T2 vertebra" |
| Lab values | "HbA1c 7.2%", "creatinine 1.4 mg/dL" |

### Medical Coding

Normalize extracted entities to standard code systems:
- **ICD-10-CM**: International Classification of Diseases (diagnosis codes)
- **CPT**: Current Procedural Terminology (procedure codes)
- **RxNorm**: Drug names and formulations
- **SNOMED CT**: Clinical terminology
- **LOINC**: Lab observation identifiers

### Relationship Detection

Extract semantic relationships between entities:
- "patient takes metformin for type 2 diabetes" → MEDICATION_INDICATION relationship
- "positive for S. aureus in blood culture" → FINDING_SUBJECT relationship
- Negation detection ("no chest pain") → negation modifier on condition entity

### API Access

The Healthcare NLP API is accessed via REST (not via Cloud Healthcare API console):
```
POST https://healthcare.googleapis.com/v1/projects/{project}/locations/{location}/services/nlp:analyzeEntities
```

Not available via `gcloud` CLI; use REST or client libraries.
