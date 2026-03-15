# Health Data & Imaging — CLI Reference

For service concepts, see [health-data-capabilities.md](health-data-capabilities.md).

## Amazon HealthLake

```bash
# --- Data Store Management ---

# Create a FHIR R4 data store with an AWS-owned key
aws healthlake create-fhir-datastore \
  --datastore-type-version R4 \
  --datastore-name "prod-clinical-data" \
  --region us-east-1

# Create a data store with a customer-managed KMS key
aws healthlake create-fhir-datastore \
  --datastore-type-version R4 \
  --datastore-name "prod-clinical-data" \
  --sse-configuration '{"KmsEncryptionConfig":{"CmkType":"CUSTOMER_MANAGED_KMS_KEY","KmsKeyId":"arn:aws:kms:us-east-1:123456789012:key/mrk-abc123"}}' \
  --region us-east-1

# Create a data store pre-populated with synthetic Synthea patient data (for dev/test)
aws healthlake create-fhir-datastore \
  --datastore-type-version R4 \
  --datastore-name "dev-synthea" \
  --preload-data-config '{"PreloadDataType":"SYNTHEA"}' \
  --region us-east-1

# List all data stores
aws healthlake list-fhir-datastores \
  --region us-east-1

# Describe a specific data store (get endpoint URL and status)
aws healthlake describe-fhir-datastore \
  --datastore-id "0af9f7d8b1c2e3f4a5b6c7d8e9f0a1b2" \
  --region us-east-1

# Delete a data store
aws healthlake delete-fhir-datastore \
  --datastore-id "0af9f7d8b1c2e3f4a5b6c7d8e9f0a1b2" \
  --region us-east-1

# --- Bulk Import ---

# Start a FHIR bulk import job (imports NDJSON files from S3)
aws healthlake start-fhir-import-job \
  --input-data-config '{"S3Uri":"s3://my-fhir-bucket/import/"}' \
  --datastore-id "0af9f7d8b1c2e3f4a5b6c7d8e9f0a1b2" \
  --data-access-role-arn "arn:aws:iam::123456789012:role/HealthLakeImportRole" \
  --job-output-data-config '{"S3Configuration":{"S3Uri":"s3://my-fhir-bucket/import-output/","KmsKeyId":"arn:aws:kms:us-east-1:123456789012:key/mrk-abc123"}}' \
  --region us-east-1

# Check import job status
aws healthlake describe-fhir-import-job \
  --datastore-id "0af9f7d8b1c2e3f4a5b6c7d8e9f0a1b2" \
  --job-id "j1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6" \
  --region us-east-1

# List all import jobs for a data store
aws healthlake list-fhir-import-jobs \
  --datastore-id "0af9f7d8b1c2e3f4a5b6c7d8e9f0a1b2" \
  --region us-east-1

# --- Bulk Export ---

# Start a FHIR bulk export job
aws healthlake start-fhir-export-job \
  --output-data-config '{"S3Configuration":{"S3Uri":"s3://my-fhir-bucket/export/","KmsKeyId":"arn:aws:kms:us-east-1:123456789012:key/mrk-abc123"}}' \
  --datastore-id "0af9f7d8b1c2e3f4a5b6c7d8e9f0a1b2" \
  --data-access-role-arn "arn:aws:iam::123456789012:role/HealthLakeExportRole" \
  --region us-east-1

# Check export job status
aws healthlake describe-fhir-export-job \
  --datastore-id "0af9f7d8b1c2e3f4a5b6c7d8e9f0a1b2" \
  --job-id "j9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4" \
  --region us-east-1
```

---

## Amazon HealthImaging

```bash
# --- Datastore Management ---

# Create an imaging datastore with an AWS-owned key
aws medical-imaging create-datastore \
  --datastore-name "radiology-prod" \
  --region us-east-1

# Create a datastore with a customer-managed KMS key
aws medical-imaging create-datastore \
  --datastore-name "radiology-prod" \
  --kms-key-arn "arn:aws:kms:us-east-1:123456789012:key/mrk-abc123" \
  --region us-east-1

# List all datastores
aws medical-imaging list-datastores \
  --region us-east-1

# Describe a specific datastore (status, endpoint, ARN)
aws medical-imaging get-datastore \
  --datastore-id "datastoreId123abc456def" \
  --region us-east-1

# Delete a datastore (must be empty of image sets)
aws medical-imaging delete-datastore \
  --datastore-id "datastoreId123abc456def" \
  --region us-east-1

# --- DICOM Import Jobs ---

# Start a DICOM import job (import P10 DICOM files from S3)
aws medical-imaging start-dicom-import-job \
  --job-name "ct-scan-batch-2026-03-14" \
  --datastore-id "datastoreId123abc456def" \
  --data-access-role-arn "arn:aws:iam::123456789012:role/HealthImagingImportRole" \
  --input-s3-uri "s3://dicom-inbox/studies/2026-03-14/" \
  --output-s3-uri "s3://dicom-output/import-results/" \
  --region us-east-1

# Get import job status
aws medical-imaging get-dicom-import-job \
  --datastore-id "datastoreId123abc456def" \
  --job-id "jobId789xyz" \
  --region us-east-1

# List all import jobs for a datastore
aws medical-imaging list-dicom-import-jobs \
  --datastore-id "datastoreId123abc456def" \
  --region us-east-1

# --- Image Set Operations ---

# Search image sets by DICOM attributes (PatientID)
aws medical-imaging search-image-sets \
  --datastore-id "datastoreId123abc456def" \
  --search-criteria '{"filters":[{"values":[{"DICOMPatientId":"PID-12345"}],"operator":"EQUAL"}]}' \
  --region us-east-1

# Search image sets by StudyDate range
aws medical-imaging search-image-sets \
  --datastore-id "datastoreId123abc456def" \
  --search-criteria '{"filters":[{"values":[{"DICOMStudyDateAndTime":{"DICOMStudyDate":"20260101","DICOMStudyTime":"000000"}},{"DICOMStudyDateAndTime":{"DICOMStudyDate":"20260314","DICOMStudyTime":"235959"}}],"operator":"BETWEEN"}]}' \
  --region us-east-1

# Get image set properties (status, version, created/updated timestamps)
aws medical-imaging get-image-set \
  --datastore-id "datastoreId123abc456def" \
  --image-set-id "imageSetId111aaa222bbb" \
  --region us-east-1

# Get image set metadata (DICOM attributes as JSON)
aws medical-imaging get-image-set-metadata \
  --datastore-id "datastoreId123abc456def" \
  --image-set-id "imageSetId111aaa222bbb" \
  --region us-east-1 \
  --output text --query 'imageSetMetadataBlob' > metadata.json.gz
# Decompress: gunzip metadata.json.gz

# Get a specific image frame (HTJ2K-encoded pixel data)
aws medical-imaging get-image-frame \
  --datastore-id "datastoreId123abc456def" \
  --image-set-id "imageSetId111aaa222bbb" \
  --image-frame-information '{"imageFrameId":"frameId000aaa111bbb"}' \
  --region us-east-1 \
  frame.htj2k
# Decode HTJ2K: use openjph or AWS HealthImaging SDK

# List image set versions (history)
aws medical-imaging list-image-set-versions \
  --datastore-id "datastoreId123abc456def" \
  --image-set-id "imageSetId111aaa222bbb" \
  --region us-east-1

# Update image set metadata (add/remove DICOM attributes)
aws medical-imaging update-image-set-metadata \
  --datastore-id "datastoreId123abc456def" \
  --image-set-id "imageSetId111aaa222bbb" \
  --latest-version-id "1" \
  --update-image-set-metadata-updates '{"DICOMUpdates":{"updatableAttributes":"{\"SchemaVersion\":1.1,\"Study\":{\"DICOM\":{\"StudyDescription\":\"Chest CT with contrast\"}}}"}}'  \
  --region us-east-1

# Copy an image set to another datastore
aws medical-imaging copy-image-set \
  --datastore-id "datastoreId123abc456def" \
  --source-image-set-id "imageSetId111aaa222bbb" \
  --copy-image-set-information '{"sourceImageSet":{"latestVersionId":"1"},"destinationImageSet":{"datastoreId":"datastoreIdDest999"}}' \
  --region us-east-1

# Delete an image set
aws medical-imaging delete-image-set \
  --datastore-id "datastoreId123abc456def" \
  --image-set-id "imageSetId111aaa222bbb" \
  --region us-east-1

# List image sets in a datastore
aws medical-imaging list-image-sets \
  --datastore-id "datastoreId123abc456def" \
  --region us-east-1

# Tag a datastore
aws medical-imaging tag-resource \
  --resource-arn "arn:aws:medical-imaging:us-east-1:123456789012:datastore/datastoreId123abc456def" \
  --tags '{"Project":"Radiology-AI","CostCenter":"12345"}' \
  --region us-east-1
```

---

## AWS HealthOmics

```bash
# --- Reference Store & References ---

# Get the reference store for the current account/region
aws omics get-reference-store \
  --id "refStoreId123" \
  --region us-east-1

# List reference stores
aws omics list-reference-stores \
  --region us-east-1

# Import a reference genome from S3
aws omics start-reference-import-job \
  --reference-store-id "refStoreId123" \
  --role-arn "arn:aws:iam::123456789012:role/OmicsImportRole" \
  --sources '[{"sourceFile":"s3://genomics-refs/hg38/GRCh38.fasta","name":"GRCh38","description":"Human Genome GRCh38","tags":{"Build":"hg38"}}]' \
  --region us-east-1

# List available references
aws omics list-references \
  --reference-store-id "refStoreId123" \
  --region us-east-1

# Get a reference (download FASTA from S3 presigned URL)
aws omics get-reference \
  --reference-store-id "refStoreId123" \
  --id "referenceId456" \
  --part-number 1 \
  --region us-east-1

# --- Sequence Stores & Read Sets ---

# Create a sequence store
aws omics create-sequence-store \
  --name "wgs-samples-prod" \
  --description "Whole genome sequencing samples" \
  --sse-config '{"type":"KMS","keyArn":"arn:aws:kms:us-east-1:123456789012:key/mrk-abc123"}' \
  --region us-east-1

# List sequence stores
aws omics list-sequence-stores \
  --region us-east-1

# Import read sets from S3 (e.g., paired-end FASTQs)
aws omics start-read-set-import-job \
  --sequence-store-id "seqStoreId789" \
  --role-arn "arn:aws:iam::123456789012:role/OmicsImportRole" \
  --sources '[{"sourceFiles":{"source1":"s3://genomics-data/sample001_R1.fastq.gz","source2":"s3://genomics-data/sample001_R2.fastq.gz"},"sourceFileType":"FASTQ","subjectId":"SUBJECT-001","sampleId":"SAMPLE-001","referenceArn":"arn:aws:omics:us-east-1:123456789012:referenceStore/refStoreId123/reference/referenceId456","name":"sample001"}]' \
  --region us-east-1

# Get read set import job status
aws omics get-read-set-import-job \
  --sequence-store-id "seqStoreId789" \
  --id "importJobId111" \
  --region us-east-1

# List read sets in a sequence store
aws omics list-read-sets \
  --sequence-store-id "seqStoreId789" \
  --region us-east-1

# Get read set metadata
aws omics get-read-set-metadata \
  --sequence-store-id "seqStoreId789" \
  --id "readSetId222" \
  --region us-east-1

# Export read sets back to S3
aws omics start-read-set-export-job \
  --sequence-store-id "seqStoreId789" \
  --destination "s3://genomics-export/sample001/" \
  --role-arn "arn:aws:iam::123456789012:role/OmicsExportRole" \
  --sources '[{"readSetId":"readSetId222"}]' \
  --region us-east-1

# Activate archived read sets (make them retrievable)
aws omics start-read-set-activation-job \
  --sequence-store-id "seqStoreId789" \
  --sources '[{"readSetId":"readSetId222"}]' \
  --region us-east-1

# Delete a read set
aws omics delete-read-set \
  --sequence-store-id "seqStoreId789" \
  --ids "readSetId222" \
  --region us-east-1

# --- Variant Stores ---

# Create a variant store linked to a reference genome
aws omics create-variant-store \
  --name "cohort-a-variants" \
  --reference '{"referenceArn":"arn:aws:omics:us-east-1:123456789012:referenceStore/refStoreId123/reference/referenceId456"}' \
  --sse-config '{"type":"KMS","keyArn":"arn:aws:kms:us-east-1:123456789012:key/mrk-abc123"}' \
  --region us-east-1

# Get variant store status
aws omics get-variant-store \
  --name "cohort-a-variants" \
  --region us-east-1

# Import variants from S3 (VCF or gVCF)
aws omics start-variant-import-job \
  --destination-name "cohort-a-variants" \
  --role-arn "arn:aws:iam::123456789012:role/OmicsImportRole" \
  --items '[{"source":"s3://genomics-data/sample001.g.vcf.gz"}]' \
  --region us-east-1

# Get variant import job status
aws omics get-variant-import-job \
  --job-id "variantJobId333" \
  --region us-east-1

# List variant stores
aws omics list-variant-stores \
  --region us-east-1

# --- Annotation Stores ---

# Create an annotation store (GFF3 format)
aws omics create-annotation-store \
  --name "refseq-annotations" \
  --reference '{"referenceArn":"arn:aws:omics:us-east-1:123456789012:referenceStore/refStoreId123/reference/referenceId456"}' \
  --store-format "GFF" \
  --region us-east-1

# Import annotations from S3
aws omics start-annotation-import-job \
  --destination-name "refseq-annotations" \
  --role-arn "arn:aws:iam::123456789012:role/OmicsImportRole" \
  --items '[{"source":"s3://genomics-data/refseq_hg38.gff3.gz"}]' \
  --region us-east-1

# List annotation stores
aws omics list-annotation-stores \
  --region us-east-1

# --- Workflows & Runs ---

# Create a workflow from a WDL definition in S3
aws omics create-workflow \
  --name "gatk-germline-snp-indel" \
  --description "GATK Best Practices germline SNP/Indel pipeline" \
  --engine "WDL" \
  --definition-uri "s3://genomics-workflows/gatk-germline/main.wdl" \
  --main "main.wdl" \
  --region us-east-1

# Create a workflow from a Nextflow definition
aws omics create-workflow \
  --name "nf-core-rnaseq" \
  --engine "NEXTFLOW" \
  --definition-zip fileb://nf-core-rnaseq.zip \
  --region us-east-1

# List available workflows (including Ready2Run)
aws omics list-workflows \
  --region us-east-1

# List Ready2Run workflows specifically
aws omics list-workflows \
  --type "READY2RUN" \
  --region us-east-1

# Get workflow details (parameters, engine, status)
aws omics get-workflow \
  --id "workflowId444" \
  --region us-east-1

# Start a workflow run
aws omics start-run \
  --workflow-id "workflowId444" \
  --name "patient-001-germline-call" \
  --role-arn "arn:aws:iam::123456789012:role/OmicsWorkflowRole" \
  --parameters '{"sample_bam":"s3://genomics-data/patient001.bam","ref_fasta":"s3://genomics-refs/hg38.fasta","output_dir":"s3://genomics-results/patient001/"}' \
  --output-uri "s3://genomics-results/patient001/run-outputs/" \
  --storage-capacity 1200 \
  --region us-east-1

# Start a Ready2Run workflow run (GATK Best Practices germline)
aws omics start-run \
  --workflow-id "1234567" \
  --workflow-type "READY2RUN" \
  --name "ready2run-gatk-germline" \
  --role-arn "arn:aws:iam::123456789012:role/OmicsWorkflowRole" \
  --parameters '{"input_bam":"s3://genomics-data/patient002.cram","output_s3_path":"s3://genomics-results/patient002/"}' \
  --output-uri "s3://genomics-results/patient002/run-outputs/" \
  --region us-east-1

# Get run status and details
aws omics get-run \
  --id "runId555" \
  --region us-east-1

# List all runs
aws omics list-runs \
  --region us-east-1

# List tasks within a run
aws omics list-run-tasks \
  --id "runId555" \
  --region us-east-1

# Get a specific task (CPU, memory, status, log stream)
aws omics get-run-task \
  --id "runId555" \
  --task-id "taskId666" \
  --region us-east-1

# Cancel a run
aws omics cancel-run \
  --id "runId555" \
  --region us-east-1

# Delete a run
aws omics delete-run \
  --id "runId555" \
  --region us-east-1

# --- Run Groups ---

# Create a run group (limit concurrent runs and total CPUs)
aws omics create-run-group \
  --name "batch-cohort-processing" \
  --max-cpus 512 \
  --max-runs 10 \
  --max-duration 4320 \
  --region us-east-1

# List run groups
aws omics list-run-groups \
  --region us-east-1

# Get a run group
aws omics get-run-group \
  --id "runGroupId777" \
  --region us-east-1
```

---

## AWS HealthScribe

```bash
# --- Batch Transcription Jobs ---

# Start a medical scribe job (transcribe and generate clinical notes from audio file)
aws transcribe start-medical-scribe-job \
  --medical-scribe-job-name "encounter-20260314-patient001" \
  --media '{"MediaFileUri":"s3://clinical-audio/encounters/20260314/patient001.mp3"}' \
  --output-bucket-name "clinical-notes-output" \
  --output-encryption-kms-key-id "arn:aws:kms:us-east-1:123456789012:key/mrk-abc123" \
  --data-access-role-arn "arn:aws:iam::123456789012:role/HealthScribeRole" \
  --settings '{"ShowSpeakerLabels":true,"MaxSpeakerLabels":2,"ChannelIdentification":false,"VocabularyName":"medical-vocabulary"}' \
  --region us-east-1

# Start a job with channel identification (stereo audio: ch0=clinician, ch1=patient)
aws transcribe start-medical-scribe-job \
  --medical-scribe-job-name "encounter-20260314-patient002-stereo" \
  --media '{"MediaFileUri":"s3://clinical-audio/encounters/20260314/patient002-stereo.wav"}' \
  --output-bucket-name "clinical-notes-output" \
  --data-access-role-arn "arn:aws:iam::123456789012:role/HealthScribeRole" \
  --settings '{"ChannelIdentification":true}' \
  --channel-definitions '[{"ChannelId":0,"ParticipantRole":"CLINICIAN"},{"ChannelId":1,"ParticipantRole":"PATIENT"}]' \
  --region us-east-1

# Get job status and output URIs
aws transcribe get-medical-scribe-job \
  --medical-scribe-job-name "encounter-20260314-patient001" \
  --region us-east-1

# List all medical scribe jobs
aws transcribe list-medical-scribe-jobs \
  --region us-east-1

# List jobs filtered by status
aws transcribe list-medical-scribe-jobs \
  --status "COMPLETED" \
  --region us-east-1

# List jobs with a name prefix
aws transcribe list-medical-scribe-jobs \
  --job-name-contains "encounter-20260314" \
  --region us-east-1

# Delete a medical scribe job
aws transcribe delete-medical-scribe-job \
  --medical-scribe-job-name "encounter-20260314-patient001" \
  --region us-east-1

# --- Custom Vocabulary (used by HealthScribe jobs) ---

# Create a custom medical vocabulary for better recognition of specific terms
aws transcribe create-medical-vocabulary \
  --vocabulary-name "cardiology-terms" \
  --language-code "en-US" \
  --vocabulary-file-uri "s3://clinical-audio/vocabularies/cardiology-vocab.txt" \
  --region us-east-1

# Get vocabulary status
aws transcribe get-medical-vocabulary \
  --vocabulary-name "cardiology-terms" \
  --region us-east-1

# List medical vocabularies
aws transcribe list-medical-vocabularies \
  --region us-east-1

# --- Common Workflow: Poll until complete, then download output ---

# Poll job status (run repeatedly or use EventBridge/Lambda for event-driven)
aws transcribe get-medical-scribe-job \
  --medical-scribe-job-name "encounter-20260314-patient001" \
  --query 'MedicalScribeJob.MedicalScribeJobStatus' \
  --output text \
  --region us-east-1

# Once COMPLETED, get output URIs
aws transcribe get-medical-scribe-job \
  --medical-scribe-job-name "encounter-20260314-patient001" \
  --query 'MedicalScribeJob.MedicalScribeOutput' \
  --output json \
  --region us-east-1

# Download transcript JSON
aws s3 cp \
  "s3://clinical-notes-output/encounter-20260314-patient001/transcript.json" \
  ./transcript.json

# Download clinical note JSON
aws s3 cp \
  "s3://clinical-notes-output/encounter-20260314-patient001/clinicalnote.json" \
  ./clinicalnote.json
```
