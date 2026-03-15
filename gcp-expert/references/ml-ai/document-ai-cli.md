# Document AI — CLI Reference

Document AI uses `gcloud documentai` commands. Most operations require specifying a location (e.g., `us` or `eu`).

```bash
export PROJECT_ID=$(gcloud config get-value project)
export LOCATION=us  # Document AI uses multi-region: "us" or "eu"
```

---

## Processor Types (Discovery)

```bash
# List all available processor types in a location
gcloud documentai processor-types list \
  --location=$LOCATION \
  --project=$PROJECT_ID

# List processor types formatted as a table
gcloud documentai processor-types list \
  --location=$LOCATION \
  --project=$PROJECT_ID \
  --format="table(name,type,category)"

# Describe a specific processor type
gcloud documentai processor-types describe INVOICE_PROCESSOR \
  --location=$LOCATION \
  --project=$PROJECT_ID
```

**Common processor type IDs:**
- `OCR_PROCESSOR` — Enterprise Document OCR
- `FORM_PARSER_PROCESSOR` — Form Parser
- `INVOICE_PROCESSOR` — Invoice Parser
- `EXPENSE_PROCESSOR` — Expense Parser
- `ID_PROOFING_PROCESSOR` — Identity Document Parser
- `US_DRIVER_LICENSE_PROCESSOR` — US Driver's License
- `US_PASSPORT_PROCESSOR` — US Passport
- `W2_PROCESSOR` — W-2 Tax Form
- `FORM_1099_PROCESSOR` — 1099 Tax Form
- `CUSTOM_EXTRACTION_PROCESSOR` — Custom Document Extractor
- `CUSTOM_CLASSIFICATION_PROCESSOR` — Document Classifier

---

## Processors

### Create Processors

```bash
# Create an Invoice Parser processor
gcloud documentai processors create \
  --display-name="Invoice Parser - Prod" \
  --type=INVOICE_PROCESSOR \
  --location=$LOCATION \
  --project=$PROJECT_ID

# Create a Form Parser processor
gcloud documentai processors create \
  --display-name="Form Parser" \
  --type=FORM_PARSER_PROCESSOR \
  --location=$LOCATION \
  --project=$PROJECT_ID

# Create an OCR processor
gcloud documentai processors create \
  --display-name="Enterprise OCR" \
  --type=OCR_PROCESSOR \
  --location=$LOCATION \
  --project=$PROJECT_ID

# Create a Custom Document Extractor processor
gcloud documentai processors create \
  --display-name="My Custom Parser" \
  --type=CUSTOM_EXTRACTION_PROCESSOR \
  --location=$LOCATION \
  --project=$PROJECT_ID

# Create an Identity Document Parser
gcloud documentai processors create \
  --display-name="ID Document Parser" \
  --type=ID_PROOFING_PROCESSOR \
  --location=$LOCATION \
  --project=$PROJECT_ID
```

### List and Describe Processors

```bash
# List all processors in a location
gcloud documentai processors list \
  --location=$LOCATION \
  --project=$PROJECT_ID

# List formatted as a table
gcloud documentai processors list \
  --location=$LOCATION \
  --project=$PROJECT_ID \
  --format="table(name,displayName,type,state,defaultProcessorVersion)"

# Describe a specific processor
gcloud documentai processors describe PROCESSOR_ID \
  --location=$LOCATION \
  --project=$PROJECT_ID
```

### Enable and Disable Processors

```bash
# Enable a processor (make it active for processing)
gcloud documentai processors enable PROCESSOR_ID \
  --location=$LOCATION \
  --project=$PROJECT_ID

# Disable a processor (cannot process documents while disabled)
gcloud documentai processors disable PROCESSOR_ID \
  --location=$LOCATION \
  --project=$PROJECT_ID
```

### Delete Processors

```bash
# Delete a processor
gcloud documentai processors delete PROCESSOR_ID \
  --location=$LOCATION \
  --project=$PROJECT_ID
```

---

## Processor Versions

```bash
# List versions of a processor
gcloud documentai processors versions list PROCESSOR_ID \
  --location=$LOCATION \
  --project=$PROJECT_ID

# List versions formatted
gcloud documentai processors versions list PROCESSOR_ID \
  --location=$LOCATION \
  --project=$PROJECT_ID \
  --format="table(name,displayName,state,createTime)"

# Describe a specific version
gcloud documentai processors versions describe VERSION_ID \
  --processor=PROCESSOR_ID \
  --location=$LOCATION \
  --project=$PROJECT_ID

# Deploy a processor version (make it available for use)
gcloud documentai processors versions deploy VERSION_ID \
  --processor=PROCESSOR_ID \
  --location=$LOCATION \
  --project=$PROJECT_ID

# Undeploy a processor version (stop serving it)
gcloud documentai processors versions undeploy VERSION_ID \
  --processor=PROCESSOR_ID \
  --location=$LOCATION \
  --project=$PROJECT_ID

# Set a version as the default version for the processor
gcloud documentai processors set-default-processor-version PROCESSOR_ID \
  --processor-version=VERSION_ID \
  --location=$LOCATION \
  --project=$PROJECT_ID

# Delete a processor version
gcloud documentai processors versions delete VERSION_ID \
  --processor=PROCESSOR_ID \
  --location=$LOCATION \
  --project=$PROJECT_ID
```

---

## Processing Documents

### Synchronous Processing (Single Document)

```bash
# Process a local file (inline; base64 encoded automatically by gcloud)
gcloud documentai processors process PROCESSOR_ID \
  --location=$LOCATION \
  --raw-document=invoice.pdf \
  --mime-type=application/pdf \
  --project=$PROJECT_ID

# Process a document from Cloud Storage
gcloud documentai processors process PROCESSOR_ID \
  --location=$LOCATION \
  --gcs-uri=gs://my-bucket/documents/invoice.pdf \
  --mime-type=application/pdf \
  --project=$PROJECT_ID

# Process and save the output to a file
gcloud documentai processors process PROCESSOR_ID \
  --location=$LOCATION \
  --raw-document=receipt.pdf \
  --mime-type=application/pdf \
  --project=$PROJECT_ID \
  --format=json > receipt-result.json

# Extract just the text field from the response
gcloud documentai processors process PROCESSOR_ID \
  --location=$LOCATION \
  --raw-document=document.pdf \
  --mime-type=application/pdf \
  --project=$PROJECT_ID \
  --format="value(document.text)"

# Extract entities (key-value pairs)
gcloud documentai processors process PROCESSOR_ID \
  --location=$LOCATION \
  --raw-document=invoice.pdf \
  --mime-type=application/pdf \
  --project=$PROJECT_ID \
  --format="json(document.entities)"

# Process a JPEG image
gcloud documentai processors process PROCESSOR_ID \
  --location=$LOCATION \
  --raw-document=form.jpg \
  --mime-type=image/jpeg \
  --project=$PROJECT_ID

# Process a PNG image
gcloud documentai processors process PROCESSOR_ID \
  --location=$LOCATION \
  --raw-document=scan.png \
  --mime-type=image/png \
  --project=$PROJECT_ID

# Process with a specific processor version
gcloud documentai processors process PROCESSOR_ID \
  --location=$LOCATION \
  --processor-version=VERSION_ID \
  --raw-document=invoice.pdf \
  --mime-type=application/pdf \
  --project=$PROJECT_ID
```

### Batch Processing (Multiple Documents)

```bash
# Create a batch processing job from Cloud Storage input
gcloud documentai processors batch-process PROCESSOR_ID \
  --location=$LOCATION \
  --gcs-uri=gs://my-bucket/input-documents/ \
  --output-gcs-uri-prefix=gs://my-bucket/output-documents/ \
  --project=$PROJECT_ID

# Batch process specific files (via JSON config file)
# batch-request.json:
# {
#   "inputDocuments": {
#     "gcsDocuments": {
#       "documents": [
#         {"gcsUri": "gs://my-bucket/inv-001.pdf", "mimeType": "application/pdf"},
#         {"gcsUri": "gs://my-bucket/inv-002.pdf", "mimeType": "application/pdf"}
#       ]
#     }
#   },
#   "documentOutputConfig": {
#     "gcsOutputConfig": {
#       "gcsUri": "gs://my-bucket/output/"
#     }
#   }
# }
TOKEN=$(gcloud auth print-access-token)
curl -s -X POST \
  "https://$LOCATION-documentai.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/processors/PROCESSOR_ID:batchProcess" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @batch-request.json

# Check batch operation status (returns a long-running operation name from batch-process)
gcloud documentai operations describe OPERATION_ID \
  --location=$LOCATION \
  --project=$PROJECT_ID

# Wait for batch operation to complete
gcloud documentai operations wait OPERATION_ID \
  --location=$LOCATION \
  --project=$PROJECT_ID
```

---

## Human Review (HITL)

```bash
# Review a specific document (send it to the human review queue)
gcloud documentai processors human-review-config review PROCESSOR_ID \
  --location=$LOCATION \
  --inline-document=document.json \
  --project=$PROJECT_ID

# Review from a GCS URI
gcloud documentai processors human-review-config review PROCESSOR_ID \
  --location=$LOCATION \
  --gcs-uri=gs://my-bucket/documents/flagged-invoice.pdf \
  --mime-type=application/pdf \
  --project=$PROJECT_ID

# Fetch the human review config for a processor
gcloud documentai processors describe PROCESSOR_ID \
  --location=$LOCATION \
  --format="value(humanReviewConfig)" \
  --project=$PROJECT_ID
```

---

## Evaluation (for Custom Processors)

```bash
# Evaluate a processor version against labeled test data
# (Test data must be in Document AI labeled format in Cloud Storage)
gcloud documentai processors versions evaluate VERSION_ID \
  --processor=PROCESSOR_ID \
  --location=$LOCATION \
  --gcs-uri=gs://my-bucket/test-data/ \
  --project=$PROJECT_ID

# List evaluations for a processor version
gcloud documentai processors versions evaluations list \
  --processor-version=VERSION_ID \
  --processor=PROCESSOR_ID \
  --location=$LOCATION \
  --project=$PROJECT_ID

# Describe an evaluation (precision, recall, F1 per entity type)
gcloud documentai processors versions evaluations describe EVALUATION_ID \
  --processor-version=VERSION_ID \
  --processor=PROCESSOR_ID \
  --location=$LOCATION \
  --project=$PROJECT_ID

# Get evaluation metrics as JSON
gcloud documentai processors versions evaluations describe EVALUATION_ID \
  --processor-version=VERSION_ID \
  --processor=PROCESSOR_ID \
  --location=$LOCATION \
  --project=$PROJECT_ID \
  --format="json(allEntitiesMetrics,entityMetrics)"
```

---

## REST API Examples

```bash
TOKEN=$(gcloud auth print-access-token)

# Process a document via REST API (inline base64)
IMAGE_B64=$(base64 -i invoice.pdf)
curl -s -X POST \
  "https://us-documentai.googleapis.com/v1/projects/$PROJECT_ID/locations/us/processors/PROCESSOR_ID:process" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"rawDocument\": {
      \"content\": \"$IMAGE_B64\",
      \"mimeType\": \"application/pdf\"
    }
  }" | python3 -m json.tool

# Process a document from Cloud Storage via REST
curl -s -X POST \
  "https://us-documentai.googleapis.com/v1/projects/$PROJECT_ID/locations/us/processors/PROCESSOR_ID:process" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "gcsDocument": {
      "gcsUri": "gs://my-bucket/invoice.pdf",
      "mimeType": "application/pdf"
    }
  }' | python3 -c "
import sys, json
data = json.load(sys.stdin)
entities = data.get('document', {}).get('entities', [])
for e in entities:
    print(f\"{e.get('type_', 'UNKNOWN')}: {e.get('mentionText', '')} (confidence: {e.get('confidence', 0):.2f})\")
"
```
