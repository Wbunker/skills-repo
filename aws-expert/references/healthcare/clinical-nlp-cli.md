# Clinical NLP — CLI Reference

For service concepts, see [clinical-nlp-capabilities.md](clinical-nlp-capabilities.md).

## Amazon Comprehend Medical

```bash
# --- Real-Time Entity Detection ---

# Detect all medical entities in a text snippet (DetectEntitiesV2 — recommended)
aws comprehendmedical detect-entities-v2 \
  --text "Patient takes metformin 500 mg twice daily for type 2 diabetes. No chest pain reported." \
  --region us-east-1

# Detect HIPAA PHI entities only
aws comprehendmedical detect-phi \
  --text "John Smith, DOB 1975-04-12, called from 555-867-5309 to schedule follow-up." \
  --region us-east-1

# Infer RxNorm codes from medication mentions
aws comprehendmedical infer-rx-norm \
  --text "Patient prescribed atorvastatin 40 mg at bedtime and aspirin 81 mg daily." \
  --region us-east-1

# Infer ICD-10-CM codes from condition mentions
aws comprehendmedical infer-icd10-cm \
  --text "Patient presents with essential hypertension and mild chronic kidney disease stage 3." \
  --region us-east-1

# Infer SNOMED CT codes for conditions, anatomy, and procedures
aws comprehendmedical infer-snomedct \
  --text "MRI of lumbar spine shows L4-L5 disc herniation with moderate foraminal stenosis." \
  --region us-east-1

# --- Batch Jobs — DetectEntitiesV2 ---

# Start a batch entity detection job over S3 documents
aws comprehendmedical start-entities-detection-v2-job \
  --job-name "discharge-summaries-batch-2026-03" \
  --input-data-config '{"S3Bucket":"clinical-docs-bucket","S3Key":"discharge-summaries/2026-03/"}' \
  --output-data-config '{"S3Bucket":"clinical-nlp-output","S3Key":"entities/discharge-summaries/2026-03/"}' \
  --data-access-role-arn "arn:aws:iam::123456789012:role/ComprehendMedicalBatchRole" \
  --language-code "en" \
  --region us-east-1

# Get batch entity detection job status
aws comprehendmedical describe-entities-detection-v2-job \
  --job-id "jobId111aaa222bbb" \
  --region us-east-1

# List entity detection jobs (filter by status)
aws comprehendmedical list-entities-detection-v2-jobs \
  --filter '{"JobStatus":"COMPLETED"}' \
  --region us-east-1

# Stop a running entity detection job
aws comprehendmedical stop-entities-detection-v2-job \
  --job-id "jobId111aaa222bbb" \
  --region us-east-1

# --- Batch Jobs — PHI Detection ---

# Start a batch PHI detection job
aws comprehendmedical start-phi-detection-job \
  --job-name "phi-redaction-batch-2026-03" \
  --input-data-config '{"S3Bucket":"clinical-docs-bucket","S3Key":"notes/2026-03/"}' \
  --output-data-config '{"S3Bucket":"clinical-nlp-output","S3Key":"phi/notes/2026-03/"}' \
  --data-access-role-arn "arn:aws:iam::123456789012:role/ComprehendMedicalBatchRole" \
  --language-code "en" \
  --region us-east-1

# Get PHI detection job status
aws comprehendmedical describe-phi-detection-job \
  --job-id "jobId333ccc444ddd" \
  --region us-east-1

# List PHI detection jobs
aws comprehendmedical list-phi-detection-jobs \
  --filter '{"JobStatus":"IN_PROGRESS"}' \
  --region us-east-1

# Stop a PHI detection job
aws comprehendmedical stop-phi-detection-job \
  --job-id "jobId333ccc444ddd" \
  --region us-east-1

# --- Batch Jobs — Ontology Linking (RxNorm) ---

# Start a batch RxNorm inference job
aws comprehendmedical start-rx-norm-inference-job \
  --job-name "medication-coding-batch-2026-03" \
  --input-data-config '{"S3Bucket":"clinical-docs-bucket","S3Key":"medication-lists/2026-03/"}' \
  --output-data-config '{"S3Bucket":"clinical-nlp-output","S3Key":"rxnorm/2026-03/"}' \
  --data-access-role-arn "arn:aws:iam::123456789012:role/ComprehendMedicalBatchRole" \
  --language-code "en" \
  --region us-east-1

# Get RxNorm job status
aws comprehendmedical describe-rx-norm-inference-job \
  --job-id "jobId555eee666fff" \
  --region us-east-1

# List RxNorm inference jobs
aws comprehendmedical list-rx-norm-inference-jobs \
  --region us-east-1

# Stop a RxNorm inference job
aws comprehendmedical stop-rx-norm-inference-job \
  --job-id "jobId555eee666fff" \
  --region us-east-1

# --- Batch Jobs — Ontology Linking (ICD-10-CM) ---

# Start a batch ICD-10-CM inference job
aws comprehendmedical start-icd10-cm-inference-job \
  --job-name "icd-coding-batch-2026-03" \
  --input-data-config '{"S3Bucket":"clinical-docs-bucket","S3Key":"diagnoses/2026-03/"}' \
  --output-data-config '{"S3Bucket":"clinical-nlp-output","S3Key":"icd10cm/2026-03/"}' \
  --data-access-role-arn "arn:aws:iam::123456789012:role/ComprehendMedicalBatchRole" \
  --language-code "en" \
  --region us-east-1

# Get ICD-10-CM job status
aws comprehendmedical describe-icd10-cm-inference-job \
  --job-id "jobId777ggg888hhh" \
  --region us-east-1

# List ICD-10-CM inference jobs
aws comprehendmedical list-icd10-cm-inference-jobs \
  --region us-east-1

# Stop an ICD-10-CM inference job
aws comprehendmedical stop-icd10-cm-inference-job \
  --job-id "jobId777ggg888hhh" \
  --region us-east-1

# --- Batch Jobs — Ontology Linking (SNOMED CT) ---

# Start a batch SNOMED CT inference job
aws comprehendmedical start-snomedct-inference-job \
  --job-name "snomed-coding-batch-2026-03" \
  --input-data-config '{"S3Bucket":"clinical-docs-bucket","S3Key":"clinical-notes/2026-03/"}' \
  --output-data-config '{"S3Bucket":"clinical-nlp-output","S3Key":"snomedct/2026-03/"}' \
  --data-access-role-arn "arn:aws:iam::123456789012:role/ComprehendMedicalBatchRole" \
  --language-code "en" \
  --region us-east-1

# Get SNOMED CT job status
aws comprehendmedical describe-snomedct-inference-job \
  --job-id "jobId999iii000jjj" \
  --region us-east-1

# List SNOMED CT inference jobs
aws comprehendmedical list-snomedct-inference-jobs \
  --region us-east-1

# Stop a SNOMED CT inference job
aws comprehendmedical stop-snomedct-inference-job \
  --job-id "jobId999iii000jjj" \
  --region us-east-1
```

---

## Amazon Transcribe Medical

```bash
# --- Custom Vocabularies ---

# Create a custom medical vocabulary from a file in S3
# Vocabulary file format: TSV with columns Phrase, SoundsLike, IPA, DisplayAs
aws transcribe create-medical-vocabulary \
  --vocabulary-name "oncology-medications" \
  --language-code "en-US" \
  --vocabulary-file-uri "s3://clinical-resources/vocabularies/oncology-meds.txt" \
  --region us-east-1

# Get vocabulary status (READY, PENDING, FAILED)
aws transcribe get-medical-vocabulary \
  --vocabulary-name "oncology-medications" \
  --region us-east-1

# List all medical vocabularies
aws transcribe list-medical-vocabularies \
  --region us-east-1

# Update an existing custom vocabulary
aws transcribe update-medical-vocabulary \
  --vocabulary-name "oncology-medications" \
  --language-code "en-US" \
  --vocabulary-file-uri "s3://clinical-resources/vocabularies/oncology-meds-v2.txt" \
  --region us-east-1

# Delete a custom vocabulary
aws transcribe delete-medical-vocabulary \
  --vocabulary-name "oncology-medications" \
  --region us-east-1

# --- Batch Transcription Jobs ---

# Transcribe a radiology dictation (DICTATION type, RADIOLOGY specialty)
aws transcribe start-medical-transcription-job \
  --medical-transcription-job-name "radiology-report-ct-chest-20260314" \
  --language-code "en-US" \
  --media-sample-rate-hertz 16000 \
  --media-format "mp3" \
  --media '{"MediaFileUri":"s3://clinical-audio/radiology/ct-chest-20260314.mp3"}' \
  --output-bucket-name "clinical-transcripts" \
  --output-key "radiology/ct-chest-20260314-transcript.json" \
  --specialty "RADIOLOGY" \
  --type "DICTATION" \
  --region us-east-1

# Transcribe a primary care clinical encounter (CONVERSATION, speaker labels)
aws transcribe start-medical-transcription-job \
  --medical-transcription-job-name "encounter-pcp-20260314-patient003" \
  --language-code "en-US" \
  --media-sample-rate-hertz 16000 \
  --media-format "wav" \
  --media '{"MediaFileUri":"s3://clinical-audio/encounters/pcp-20260314-patient003.wav"}' \
  --output-bucket-name "clinical-transcripts" \
  --output-key "encounters/pcp-20260314-patient003-transcript.json" \
  --specialty "PRIMARYCARE" \
  --type "CONVERSATION" \
  --settings '{"ShowSpeakerLabels":true,"MaxSpeakerLabels":2,"VocabularyName":"primarycare-terms"}' \
  --region us-east-1

# Transcribe with channel identification (stereo recording: ch0=clinician, ch1=patient)
aws transcribe start-medical-transcription-job \
  --medical-transcription-job-name "cardiology-consult-stereo-20260314" \
  --language-code "en-US" \
  --media-sample-rate-hertz 16000 \
  --media-format "wav" \
  --media '{"MediaFileUri":"s3://clinical-audio/cardiology/consult-20260314-stereo.wav"}' \
  --output-bucket-name "clinical-transcripts" \
  --specialty "CARDIOLOGY" \
  --type "CONVERSATION" \
  --settings '{"ChannelIdentification":true}' \
  --region us-east-1

# Transcribe with PHI identification (tags PHI in output)
aws transcribe start-medical-transcription-job \
  --medical-transcription-job-name "neurology-consult-phi-tagged-20260314" \
  --language-code "en-US" \
  --media-sample-rate-hertz 16000 \
  --media-format "mp4" \
  --media '{"MediaFileUri":"s3://clinical-audio/neurology/consult-20260314.mp4"}' \
  --output-bucket-name "clinical-transcripts" \
  --specialty "NEUROLOGY" \
  --type "CONVERSATION" \
  --content-identification-type "PHI" \
  --region us-east-1

# Transcribe with PHI redaction (replaces PHI with [PHI] in output)
aws transcribe start-medical-transcription-job \
  --medical-transcription-job-name "research-deidentified-20260314" \
  --language-code "en-US" \
  --media-sample-rate-hertz 16000 \
  --media-format "flac" \
  --media '{"MediaFileUri":"s3://clinical-audio/research/patient004.flac"}' \
  --output-bucket-name "research-transcripts-deidentified" \
  --specialty "PRIMARYCARE" \
  --type "CONVERSATION" \
  --content-redaction-type "PHI" \
  --region us-east-1

# Transcribe with encrypted output using a KMS CMK
aws transcribe start-medical-transcription-job \
  --medical-transcription-job-name "oncology-consult-encrypted-20260314" \
  --language-code "en-US" \
  --media-sample-rate-hertz 16000 \
  --media-format "mp3" \
  --media '{"MediaFileUri":"s3://clinical-audio/oncology/consult-20260314.mp3"}' \
  --output-bucket-name "clinical-transcripts-encrypted" \
  --output-encryption-kms-key-id "arn:aws:kms:us-east-1:123456789012:key/mrk-abc123" \
  --specialty "ONCOLOGY" \
  --type "CONVERSATION" \
  --settings '{"ShowSpeakerLabels":true,"MaxSpeakerLabels":2}' \
  --region us-east-1

# --- Job Management ---

# Get job status and output location
aws transcribe get-medical-transcription-job \
  --medical-transcription-job-name "radiology-report-ct-chest-20260314" \
  --region us-east-1

# Get job status only (useful for polling)
aws transcribe get-medical-transcription-job \
  --medical-transcription-job-name "radiology-report-ct-chest-20260314" \
  --query 'MedicalTranscriptionJob.TranscriptionJobStatus' \
  --output text \
  --region us-east-1

# Get output transcript URI once completed
aws transcribe get-medical-transcription-job \
  --medical-transcription-job-name "radiology-report-ct-chest-20260314" \
  --query 'MedicalTranscriptionJob.Transcript.TranscriptFileUri' \
  --output text \
  --region us-east-1

# List all medical transcription jobs
aws transcribe list-medical-transcription-jobs \
  --region us-east-1

# List jobs filtered by status
aws transcribe list-medical-transcription-jobs \
  --status "COMPLETED" \
  --region us-east-1

# List jobs filtered by name prefix
aws transcribe list-medical-transcription-jobs \
  --job-name-contains "radiology" \
  --region us-east-1

# Delete a medical transcription job
aws transcribe delete-medical-transcription-job \
  --medical-transcription-job-name "radiology-report-ct-chest-20260314" \
  --region us-east-1

# --- Common Workflow: Transcribe then NLP pipeline ---

# Step 1: Start transcription
aws transcribe start-medical-transcription-job \
  --medical-transcription-job-name "pcp-encounter-pipeline-$(date +%Y%m%d%H%M%S)" \
  --language-code "en-US" \
  --media-sample-rate-hertz 16000 \
  --media-format "mp3" \
  --media '{"MediaFileUri":"s3://clinical-audio/pcp/encounter-today.mp3"}' \
  --output-bucket-name "clinical-transcripts" \
  --specialty "PRIMARYCARE" \
  --type "CONVERSATION" \
  --settings '{"ShowSpeakerLabels":true,"MaxSpeakerLabels":2}' \
  --region us-east-1

# Step 2: Poll for completion (or use EventBridge rule on TranscriptionJobStatus change)
aws transcribe get-medical-transcription-job \
  --medical-transcription-job-name "pcp-encounter-pipeline-20260314120000" \
  --query 'MedicalTranscriptionJob.TranscriptionJobStatus' \
  --output text \
  --region us-east-1

# Step 3: Download the transcript
aws s3 cp \
  "s3://clinical-transcripts/pcp-encounter-pipeline-20260314120000.json" \
  ./transcript.json

# Step 4: Extract transcript text and send to Comprehend Medical
TRANSCRIPT=$(cat transcript.json | python3 -c "import json,sys; data=json.load(sys.stdin); print(data['results']['transcripts'][0]['transcript'])")
aws comprehendmedical detect-entities-v2 \
  --text "$TRANSCRIPT" \
  --region us-east-1

# Step 5: Infer ICD-10-CM codes from the same transcript
aws comprehendmedical infer-icd10-cm \
  --text "$TRANSCRIPT" \
  --region us-east-1
```
