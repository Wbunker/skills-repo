# Cloud Healthcare API — CLI Reference

## Enable Healthcare API

```bash
# Enable Cloud Healthcare API
gcloud services enable healthcare.googleapis.com --project=my-project

# Verify
gcloud services list --enabled --filter="name:healthcare" --project=my-project
```

---

## Datasets

```bash
# Create a dataset
gcloud healthcare datasets create hospital-ehr \
  --location=us-central1 \
  --project=my-project

# Create a dataset with specific time zone (for date-based operations)
gcloud healthcare datasets create hospital-ehr-west \
  --location=us-west2 \
  --time-zone=America/Los_Angeles \
  --project=my-project

# List datasets in a location
gcloud healthcare datasets list \
  --location=us-central1 \
  --project=my-project \
  --format="table(name,timeZone)"

# Describe a dataset
gcloud healthcare datasets describe hospital-ehr \
  --location=us-central1 \
  --project=my-project

# Delete a dataset (also deletes all contained stores and data — irreversible)
gcloud healthcare datasets delete hospital-ehr \
  --location=us-central1 \
  --project=my-project

# De-identify an entire dataset (creates a new de-identified dataset)
gcloud healthcare datasets deidentify hospital-ehr \
  --location=us-central1 \
  --destination-dataset=projects/my-project/locations/us-central1/datasets/hospital-ehr-deid \
  --default-fhir-config-text-redaction-config-scheme=REDACT_ALL_TEXT \
  --project=my-project
```

---

## FHIR Stores

```bash
# Create a FHIR R4 store
gcloud healthcare fhir-stores create r4-patient-data \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --version=R4 \
  --project=my-project

# Create FHIR store with BigQuery streaming export enabled
gcloud healthcare fhir-stores create r4-with-bq \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --version=R4 \
  --bq-dataset=bq://my-project.healthcare_analytics \
  --project=my-project

# Create FHIR store with Pub/Sub notifications
gcloud healthcare fhir-stores create r4-with-pubsub \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --version=R4 \
  --pubsub-topic=projects/my-project/topics/fhir-notifications \
  --project=my-project

# List FHIR stores
gcloud healthcare fhir-stores list \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --project=my-project

# Describe a FHIR store
gcloud healthcare fhir-stores describe r4-patient-data \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --project=my-project

# Update FHIR store (add Pub/Sub notification)
gcloud healthcare fhir-stores update r4-patient-data \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --pubsub-topic=projects/my-project/topics/fhir-notifications \
  --project=my-project

# Delete a FHIR store
gcloud healthcare fhir-stores delete r4-patient-data \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --project=my-project
```

---

## FHIR Resource Operations

```bash
# Create a FHIR resource (Patient)
cat > patient.json << 'EOF'
{
  "resourceType": "Patient",
  "id": "patient-001",
  "active": true,
  "name": [{"family": "Doe", "given": ["Jane"]}],
  "gender": "female",
  "birthDate": "1980-06-15",
  "telecom": [{"system": "phone", "value": "555-867-5309"}]
}
EOF

gcloud healthcare fhir resources create \
  --fhir-store=r4-patient-data \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --resource-type=Patient \
  --gcs-uri=gs://my-bucket/patient.json \
  --project=my-project

# Read a FHIR resource
gcloud healthcare fhir resources read \
  --fhir-store=r4-patient-data \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --resource-type=Patient \
  --resource-id=patient-001 \
  --project=my-project

# Search FHIR resources
gcloud healthcare fhir resources search \
  --fhir-store=r4-patient-data \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --resource-type=Patient \
  --params="family=Doe&birthdate=1980-06-15" \
  --project=my-project

# Execute FHIR operation ($everything for a patient)
gcloud healthcare fhir resources execute-bundle \
  --fhir-store=r4-patient-data \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --input-file=transaction-bundle.json \
  --project=my-project

# Export FHIR resources to Cloud Storage (bulk export)
gcloud healthcare fhir-stores export gcs r4-patient-data \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --gcs-uri=gs://my-bucket/fhir-export/ \
  --project=my-project

# Export FHIR resources to BigQuery
gcloud healthcare fhir-stores export bq r4-patient-data \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --bq-dataset=bq://my-project.healthcare_analytics \
  --recursive-depth=5 \
  --project=my-project

# Import FHIR resources from GCS (NDJSON format)
gcloud healthcare fhir-stores import gcs r4-patient-data \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --gcs-uri=gs://my-bucket/fhir-import/*.ndjson \
  --content-structure=BUNDLE \
  --project=my-project
```

---

## DICOM Stores

```bash
# Create a DICOM store
gcloud healthcare dicom-stores create radiology-images \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --project=my-project

# Create DICOM store with Pub/Sub notifications
gcloud healthcare dicom-stores create radiology-with-pubsub \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --pubsub-topic=projects/my-project/topics/dicom-notifications \
  --project=my-project

# List DICOM stores
gcloud healthcare dicom-stores list \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --project=my-project

# Describe a DICOM store
gcloud healthcare dicom-stores describe radiology-images \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --project=my-project

# Export DICOM instances to Cloud Storage
gcloud healthcare dicom-stores export gcs radiology-images \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --gcs-uri=gs://my-dicom-archive/ \
  --project=my-project

# Export DICOM instances to BigQuery (metadata only, not pixel data)
gcloud healthcare dicom-stores export bq radiology-images \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --bq-dataset=bq://my-project.dicom_metadata \
  --overwrite-table \
  --project=my-project

# De-identify a DICOM store (create de-identified copy)
gcloud healthcare dicom-stores deidentify radiology-images \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --destination-store=projects/my-project/locations/us-central1/datasets/hospital-ehr/dicomStores/radiology-deid \
  --remove-list=PatientName,PatientID,PatientBirthDate,PatientAddress \
  --project=my-project

# Import DICOM instances from Cloud Storage
gcloud healthcare dicom-stores import gcs radiology-images \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --gcs-uri=gs://my-dicom-source/**/*.dcm \
  --project=my-project

# Delete a DICOM store
gcloud healthcare dicom-stores delete radiology-images \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --project=my-project
```

---

## HL7 v2 Stores

```bash
# Create an HL7 v2 store
gcloud healthcare hl7v2-stores create adt-messages \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --project=my-project

# Create HL7 v2 store with Pub/Sub notification
gcloud healthcare hl7v2-stores create adt-with-pubsub \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --pubsub-topic=projects/my-project/topics/hl7v2-adt-events \
  --project=my-project

# List HL7 v2 stores
gcloud healthcare hl7v2-stores list \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --project=my-project

# Describe an HL7 v2 store
gcloud healthcare hl7v2-stores describe adt-messages \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --project=my-project

# Create (ingest) an HL7 v2 message
# (base64-encoded HL7 v2 message)
HL7_MSG=$(echo "MSH|^~\&|ADT|HOSPITAL|APP|DEST|20250115120000||ADT^A01|MSG001|P|2.3|||AL|NE|
PID|1||MRN001^^^HOSPITAL^MR||DOE^JANE^A||19800615|F" | base64)

gcloud healthcare hl7v2-stores messages create \
  --hl7v2-store=adt-messages \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --message-data="${HL7_MSG}" \
  --project=my-project

# List messages in an HL7 v2 store
gcloud healthcare hl7v2-stores messages list \
  --hl7v2-store=adt-messages \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --project=my-project \
  --format="table(name,messageType,createTime)"

# Get a specific message
gcloud healthcare hl7v2-stores messages get MESSAGE_ID \
  --hl7v2-store=adt-messages \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --project=my-project

# Delete a message
gcloud healthcare hl7v2-stores messages delete MESSAGE_ID \
  --hl7v2-store=adt-messages \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --project=my-project

# Delete an HL7 v2 store
gcloud healthcare hl7v2-stores delete adt-messages \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --project=my-project
```

---

## Healthcare NLP API (REST)

The Healthcare NLP API is not available via gcloud CLI; use the REST API:

```bash
TOKEN=$(gcloud auth print-access-token)

# Analyze entities in clinical text
curl -s -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "documentContent": "Patient presents with hypertension and type 2 diabetes mellitus. Currently taking metformin 500mg twice daily and lisinopril 10mg daily. No chest pain or shortness of breath.",
    "licensedVocabularies": ["ICD10CM", "RXNORM", "SNOMEDCT_US"]
  }' \
  "https://healthcare.googleapis.com/v1/projects/my-project/locations/us-central1/services/nlp:analyzeEntities" \
  | python3 -m json.tool
```

---

## IAM for Healthcare API

```bash
# Grant a service account access to read FHIR resources
gcloud healthcare fhir-stores set-iam-policy r4-patient-data \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --policy-file=fhir-policy.json \
  --project=my-project

# Add a principal to a FHIR store role
gcloud healthcare fhir-stores add-iam-policy-binding r4-patient-data \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --member=serviceAccount:fhir-reader@my-project.iam.gserviceaccount.com \
  --role=roles/healthcare.fhirResourceReader \
  --project=my-project

# Common Healthcare IAM roles:
# roles/healthcare.fhirResourceReader - Read FHIR resources
# roles/healthcare.fhirResourceEditor - Create/update/delete FHIR resources
# roles/healthcare.dicomEditor - Full DICOM store access
# roles/healthcare.hl7V2Consumer - Ingest and read HL7 v2 messages
# roles/healthcare.datasetAdmin - Full dataset admin

# View IAM policy on a FHIR store
gcloud healthcare fhir-stores get-iam-policy r4-patient-data \
  --dataset=hospital-ehr \
  --location=us-central1 \
  --project=my-project
```
