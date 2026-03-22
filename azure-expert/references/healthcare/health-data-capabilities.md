# Azure Health Data Services — Capabilities Reference
For CLI commands, see [health-data-cli.md](health-data-cli.md).

## Azure Health Data Services (AHDS)

**Purpose**: Fully managed, enterprise-grade health data platform on Azure. Provides standards-based APIs for storing, processing, and analyzing Protected Health Information (PHI) in compliance with HIPAA, HITRUST, and other healthcare regulations.

### AHDS Workspace

- Top-level resource that serves as a logical container for all health data services
- A workspace groups FHIR, DICOM, and MedTech service instances
- Manages shared network settings, private endpoints, and identity access
- Workspace-level access control with Azure RBAC

### Services Within a Workspace

| Service | Standard | Purpose |
|---|---|---|
| **FHIR Service** | HL7 FHIR R4 / STU3 | Store, search, and retrieve clinical data |
| **DICOM Service** | DICOMweb (WADO-RS/STOW-RS/QIDO-RS) | Store and retrieve medical imaging data |
| **MedTech Service** | FHIR (output) | Ingest IoT device data → convert to FHIR Observations |
| **Health Data Manager** | FHIR-based | De-identification, data enrichment, pipeline management |

---

## FHIR Service

**Purpose**: Managed HL7 FHIR (Fast Healthcare Interoperability Resources) API for storing and exchanging clinical data. Enables health record exchange between systems using a modern REST API.

### FHIR Versions Supported

| Version | Status | Notes |
|---|---|---|
| **FHIR R4** (4.0.1) | Generally Available; preferred | Current standard; use for new projects |
| **FHIR STU3** (3.0.x) | Generally Available | Legacy; supported for existing systems |

### Key FHIR Capabilities

| Capability | Details |
|---|---|
| **REST API** | Standard FHIR RESTful API: `GET`, `POST`, `PUT`, `PATCH`, `DELETE` on resources |
| **Resource types** | 140+ FHIR resource types: Patient, Observation, Condition, MedicationRequest, Encounter, DiagnosticReport, etc. |
| **FHIR Search** | Comprehensive search parameters; chained search; includes; revIncludes |
| **SMART on FHIR** | Authorization framework for EHR-embedded apps (OAuth 2.0 + FHIR context scopes) |
| **Bulk export** | `$export` operation for large-scale data extraction (NDJSON format) |
| **Conditional operations** | Conditional create, update, delete (if-match, if-none-exist) |
| **Versioning** | Resource versioning with ETag; history endpoint (`_history`) |
| **Custom search parameters** | Define searchable extensions |
| **Consent management** | Store and enforce consent resources |
| **Transaction bundles** | Atomic multi-resource operations |
| **Cross-origin** | CORS configured for browser-based FHIR clients |

### FHIR Search Examples

```http
# Find all patients named Smith
GET /Patient?name=Smith

# Find observations for a specific patient above a threshold
GET /Observation?patient=Patient/123&code=8867-4&value-quantity=gt90

# Find encounters within a date range
GET /Encounter?date=ge2024-01-01&date=le2024-12-31

# Include referenced resources in result
GET /MedicationRequest?patient=Patient/123&_include=MedicationRequest:medication

# Chained search: find observations for patients in a specific city
GET /Observation?patient.address-city=Seattle
```

### Authentication

- **Entra ID only**: All FHIR API calls require a valid Entra ID bearer token
- **Service principal**: Assign `FHIR Data Reader`, `FHIR Data Writer`, or `FHIR Data Contributor` RBAC roles
- **Managed identity**: Recommended for Azure services (Azure Functions, ADF, Logic Apps) connecting to FHIR
- **SMART on FHIR**: For patient-facing or clinician-facing apps needing user context

### FHIR RBAC Roles

| Role | Permissions |
|---|---|
| `FHIR Data Reader` | Read FHIR resources only |
| `FHIR Data Writer` | Write FHIR resources (no delete) |
| `FHIR Data Contributor` | Full read/write/delete; manage capabilities |
| `FHIR Data Exporter` | Trigger and retrieve bulk export ($export) |
| `FHIR Data Importer` | Trigger bulk import ($import) |

### Bulk Export

```http
# Initiate system-level export (all resources)
GET /$export

# Patient-level export
GET /Patient/$export

# Export specific resource types
GET /$export?_type=Patient,Observation,Condition

# Export to Azure Storage
GET /$export?_container=https://mystorageacct.blob.core.windows.net/fhirexport

# Poll export status
GET /_operations/export/{job-id}

# Retrieve exported files (NDJSON format)
GET /results/{file-name}.ndjson
```

### HIPAA Compliance

- Azure Health Data Services is HIPAA-eligible (part of Microsoft's Business Associate Agreement)
- Data encrypted at rest (AES-256) and in transit (TLS 1.2+)
- Audit logging: all API calls logged to Azure Monitor / Azure Storage / Log Analytics
- Network isolation: private endpoints, service firewall
- Role-based access control: granular FHIR resource-level permissions

---

## DICOM Service

**Purpose**: Store, retrieve, and query medical images using the DICOMweb standard. Enables cloud-based medical imaging workflows integrated with FHIR clinical data.

### DICOMweb API Standards

| Standard | Operation | Description |
|---|---|---|
| **WADO-RS** | Retrieve | Download DICOM instances, series, studies |
| **STOW-RS** | Store | Upload DICOM files to cloud |
| **QIDO-RS** | Query | Search for studies, series, instances |

### Key Capabilities

| Capability | Details |
|---|---|
| **DICOM Standard** | DICOM PS3.18 (DICOMweb); supports DICOM Part 10 files |
| **Entra ID auth** | Bearer token authentication (same as FHIR Service) |
| **Bulk operations** | Batch upload/download for large imaging datasets |
| **Change feed** | Event stream of DICOM operations (create, delete, update) for downstream processing |
| **FHIR integration** | DICOM metadata can be converted to FHIR ImagingStudy resources |
| **Azure Data Lake export** | Export DICOM metadata and pixel data to ADLS Gen2 for analytics |
| **Anonymization** | Built-in de-identification tools for research use |

### DICOM Hierarchy

```
Study (patient encounter producing images)
  └── Series (acquisition sequence, e.g., CT chest series)
        └── Instance (individual DICOM file/image)
```

### QIDO-RS Search Examples

```http
# Search for all studies for a patient
GET /studies?PatientID=PAT001

# Find CT studies from 2024
GET /studies?StudyDate=20240101-20241231&Modality=CT

# Find all series in a study
GET /studies/{StudyInstanceUID}/series

# Find instances in a series
GET /studies/{StudyInstanceUID}/series/{SeriesInstanceUID}/instances
```

---

## MedTech Service

**Purpose**: Ingest device telemetry data from IoT devices (via Azure Event Hubs), normalize it, and convert it to FHIR Observation resources stored in the FHIR Service.

### Data Flow

```
Medical IoT Devices (wearables, monitors, point-of-care)
  → Azure IoT Hub OR Azure Event Hubs
  → MedTech Service
     → Device Mapping (normalize to intermediary format)
     → FHIR Mapping (convert to FHIR Observation resource)
  → FHIR Service (stored as Observation linked to Patient)
```

### Mapping Templates

#### Device Mapping (normalizes raw device data)

```json
{
  "templateType": "CollectionContent",
  "template": [{
    "templateType": "JsonPathContent",
    "template": {
      "typeName": "heartrate",
      "typeMatchExpression": "$..[?(@heartRate)]",
      "deviceIdExpression": "$.deviceId",
      "timestampExpression": "$.endDate",
      "values": [{
        "required": true,
        "valueExpression": "$.heartRate",
        "valueName": "hr"
      }]
    }
  }]
}
```

#### FHIR Mapping (converts to FHIR Observation)

```json
{
  "templateType": "CollectionFhir",
  "template": [{
    "templateType": "CodeValueFhir",
    "template": {
      "codes": [{"code": "8867-4", "system": "http://loinc.org", "display": "Heart rate"}],
      "typeName": "heartrate",
      "value": {"valueName": "hr", "valueType": "Quantity", "unit": "/min"}
    }
  }]
}
```

### Resolution Modes

| Mode | Description |
|---|---|
| **Create** | Create new Patient and Device FHIR resources if not found (for testing) |
| **Lookup** | Look up existing Patient and Device resources; fail if not found (for production) |
| **Lookup with Identity Resolution** | Use device-to-patient mapping from DeviceRegistration |

---

## Compliance and Security

| Compliance | Status |
|---|---|
| **HIPAA BAA** | Eligible; Microsoft signs BAA |
| **HITRUST CSF** | Certified |
| **SOC 2 Type II** | Certified |
| **ISO 27001** | Certified |
| **FedRAMP** | High (Azure Government) |
| **PCI DSS** | Compliant |

### Data Protection Features

- **Encryption at rest**: AES-256; customer-managed keys (CMK) via Key Vault supported
- **Encryption in transit**: TLS 1.2+ enforced; TLS 1.0/1.1 disabled
- **Private endpoints**: Deploy FHIR/DICOM services with no public internet access
- **Service firewall**: Restrict to specific IP ranges
- **Audit logs**: All data plane operations logged to Diagnostic Settings (Log Analytics, Storage, Event Hubs)
- **De-identification**: Built-in FHIR de-identification tools for research and analytics
