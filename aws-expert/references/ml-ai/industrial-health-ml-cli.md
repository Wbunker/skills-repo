# Industrial, Health & Physical ML — CLI Reference
For capabilities, see [industrial-health-ml-capabilities.md](industrial-health-ml-capabilities.md).

## Amazon Lookout for Equipment

```bash
# --- Datasets ---
aws lookout-for-equipment create-dataset \
  --dataset-name pump-sensor-data \
  --dataset-schema file://schema.json
  # schema.json defines component names and sensor tag names

aws lookout-for-equipment describe-dataset --dataset-name pump-sensor-data
aws lookout-for-equipment list-datasets
aws lookout-for-equipment delete-dataset --dataset-name pump-sensor-data

# --- Data Ingestion Jobs ---
aws lookout-for-equipment start-data-ingestion-job \
  --dataset-name pump-sensor-data \
  --ingestion-input-configuration '{
    "S3InputConfiguration": {
      "Bucket": "my-sensor-bucket",
      "Prefix": "pump-data/historical/"
    }
  }' \
  --role-arn arn:aws:iam::123456789012:role/LookoutEquipmentRole \
  --client-token $(uuidgen)

aws lookout-for-equipment describe-data-ingestion-job --job-id JOB_ID

# --- Label Groups and Labels ---
aws lookout-for-equipment create-label-group \
  --label-group-name pump-failures \
  --fault-codes '["Bearing_Failure","Seal_Leak","Cavitation"]'

aws lookout-for-equipment create-label \
  --label-group-name pump-failures \
  --start-time 1640000000 \
  --end-time 1640086400 \
  --rating ANOMALY \
  --fault-code "Bearing_Failure" \
  --equipment "Pump-A1"

aws lookout-for-equipment list-labels --label-group-name pump-failures

# --- Model Training ---
aws lookout-for-equipment create-model \
  --model-name pump-anomaly-detector \
  --dataset-name pump-sensor-data \
  --dataset-schema file://schema.json \
  --labels-input-configuration '{
    "LabelGroupName": "pump-failures"
  }' \
  --training-data-start-time 1609459200 \
  --training-data-end-time 1640995200 \
  --evaluation-data-start-time 1640995200 \
  --evaluation-data-end-time 1643673600 \
  --role-arn arn:aws:iam::123456789012:role/LookoutEquipmentRole

aws lookout-for-equipment describe-model --model-name pump-anomaly-detector
aws lookout-for-equipment list-models --dataset-name pump-sensor-data
aws lookout-for-equipment delete-model --model-name pump-anomaly-detector

# --- Inference Schedulers ---
aws lookout-for-equipment create-inference-scheduler \
  --model-name pump-anomaly-detector \
  --inference-scheduler-name pump-live-monitor \
  --data-upload-frequency PT5M \
  --data-input-configuration '{
    "S3InputConfiguration": {
      "Bucket": "my-sensor-bucket",
      "Prefix": "pump-data/live/"
    },
    "InputTimeZoneOffset": "+00:00",
    "InferenceInputNameConfiguration": {
      "TimestampFormat": "yyyyMMddHHmmss",
      "ComponentTimestampDelimiter": "_"
    }
  }' \
  --data-output-configuration '{
    "S3OutputConfiguration": {
      "Bucket": "my-output-bucket",
      "Prefix": "pump-predictions/"
    },
    "KmsKeyId": "alias/my-key"
  }' \
  --role-arn arn:aws:iam::123456789012:role/LookoutEquipmentRole

aws lookout-for-equipment describe-inference-scheduler \
  --inference-scheduler-name pump-live-monitor

aws lookout-for-equipment start-inference-scheduler \
  --inference-scheduler-name pump-live-monitor

aws lookout-for-equipment stop-inference-scheduler \
  --inference-scheduler-name pump-live-monitor

aws lookout-for-equipment list-inference-schedulers --model-name pump-anomaly-detector
aws lookout-for-equipment delete-inference-scheduler --inference-scheduler-name pump-live-monitor

# --- Inference Executions (results) ---
aws lookout-for-equipment list-inference-executions \
  --inference-scheduler-name pump-live-monitor \
  --status SUCCESS \
  --data-start-time-after 2024-01-01T00:00:00Z \
  --data-end-time-before 2024-01-31T00:00:00Z

aws lookout-for-equipment describe-model-version \
  --model-name pump-anomaly-detector \
  --model-version 1
```

---

## Amazon Lookout for Vision

```bash
# --- Projects ---
aws lookoutvision create-project --project-name circuit-board-inspection
aws lookoutvision describe-project --project-name circuit-board-inspection
aws lookoutvision list-projects
aws lookoutvision delete-project --project-name circuit-board-inspection

# --- Datasets ---
# Create training dataset
aws lookoutvision create-dataset \
  --project-name circuit-board-inspection \
  --dataset-type train \
  --dataset-source '{
    "GroundTruthManifest": {
      "S3Object": {
        "Bucket": "my-vision-bucket",
        "Key": "manifests/train.manifest"
      }
    }
  }'

# Create test dataset
aws lookoutvision create-dataset \
  --project-name circuit-board-inspection \
  --dataset-type test \
  --dataset-source '{
    "GroundTruthManifest": {
      "S3Object": {
        "Bucket": "my-vision-bucket",
        "Key": "manifests/test.manifest"
      }
    }
  }'

aws lookoutvision describe-dataset \
  --project-name circuit-board-inspection \
  --dataset-type train

aws lookoutvision list-dataset-entries \
  --project-name circuit-board-inspection \
  --dataset-type train \
  --anomaly-class Anomaly

# Update (add/relabel) entries
aws lookoutvision update-dataset-entries \
  --project-name circuit-board-inspection \
  --dataset-type train \
  --changes file://new-entries.jsonl

# --- Model Training ---
aws lookoutvision create-model \
  --project-name circuit-board-inspection \
  --output-config '{
    "S3Location": {
      "Bucket": "my-vision-bucket",
      "Prefix": "model-output/"
    }
  }'

aws lookoutvision describe-model \
  --project-name circuit-board-inspection \
  --model-version 1

aws lookoutvision list-models --project-name circuit-board-inspection
aws lookoutvision delete-model \
  --project-name circuit-board-inspection \
  --model-version 1

# --- Starting / Stopping Model (inference units) ---
# Billed per hour per model unit; start before calling DetectAnomalies
aws lookoutvision start-model \
  --project-name circuit-board-inspection \
  --model-version 1 \
  --min-inference-units 1

aws lookoutvision stop-model \
  --project-name circuit-board-inspection \
  --model-version 1

# --- Anomaly Detection (inference) ---
aws lookoutvision detect-anomalies \
  --project-name circuit-board-inspection \
  --model-version 1 \
  --content-type image/jpeg \
  --body file://product-image.jpg

# --- Trial Detection (bulk inference without running model unit) ---
aws lookoutvision start-model-packaging-job \
  --project-name circuit-board-inspection \
  --model-version 1 \
  --job-name edge-deployment-package \
  --configuration '{
    "Greengrass": {
      "S3OutputLocation": {
        "Bucket": "my-vision-bucket",
        "Prefix": "edge-packages/"
      },
      "ComponentName": "circuit-board-inspector",
      "ComponentVersion": "1.0.0"
    }
  }'

aws lookoutvision describe-model-packaging-job \
  --project-name circuit-board-inspection \
  --job-name edge-deployment-package

aws lookoutvision list-model-packaging-jobs \
  --project-name circuit-board-inspection
```

---

## AWS HealthLake

```bash
# --- FHIR Datastore Management ---
aws healthlake create-fhir-datastore \
  --datastore-type-version R4 \
  --datastore-name my-clinical-datastore \
  --sse-configuration '{
    "KmsEncryptionConfig": {
      "CmkType": "CUSTOMER_MANAGED_KMS_KEY",
      "KmsKeyId": "arn:aws:kms:us-east-1:123456789012:key/my-key"
    }
  }' \
  --preload-data-config '{"PreloadDataType": "SYNTHEA"}'
  # Remove preload-data-config for empty production datastores

aws healthlake describe-fhir-datastore --datastore-id DATASTORE_ID
aws healthlake list-fhir-datastores
aws healthlake list-fhir-datastores \
  --filter '{"DatastoreStatus": "ACTIVE"}'

aws healthlake delete-fhir-datastore --datastore-id DATASTORE_ID

# --- Import FHIR Data from S3 ---
aws healthlake start-fhir-import-job \
  --input-data-config '{
    "S3Uri": "s3://my-fhir-bucket/input-data/"
  }' \
  --job-output-data-config '{
    "S3Configuration": {
      "S3Uri": "s3://my-fhir-bucket/import-output/",
      "KmsKeyId": "arn:aws:kms:us-east-1:123456789012:key/my-key"
    }
  }' \
  --datastore-id DATASTORE_ID \
  --data-access-role-arn arn:aws:iam::123456789012:role/HealthLakeRole \
  --job-name initial-patient-import

aws healthlake describe-fhir-import-job \
  --datastore-id DATASTORE_ID \
  --job-id IMPORT_JOB_ID

aws healthlake list-fhir-import-jobs \
  --datastore-id DATASTORE_ID \
  --job-status COMPLETED

# --- Export FHIR Data to S3 ---
aws healthlake start-fhir-export-job \
  --output-data-config '{
    "S3Configuration": {
      "S3Uri": "s3://my-fhir-bucket/export-output/",
      "KmsKeyId": "arn:aws:kms:us-east-1:123456789012:key/my-key"
    }
  }' \
  --datastore-id DATASTORE_ID \
  --data-access-role-arn arn:aws:iam::123456789012:role/HealthLakeRole \
  --job-name quarterly-export

aws healthlake describe-fhir-export-job \
  --datastore-id DATASTORE_ID \
  --job-id EXPORT_JOB_ID

aws healthlake list-fhir-export-jobs \
  --datastore-id DATASTORE_ID

# Tagging
aws healthlake tag-resource \
  --resource-arn arn:aws:healthlake:us-east-1:123456789012:datastore/fhir/DATASTORE_ID \
  --tags '[{"Key":"env","Value":"production"},{"Key":"compliance","Value":"hipaa"}]'

aws healthlake list-tags-for-resource \
  --resource-arn arn:aws:healthlake:us-east-1:123456789012:datastore/fhir/DATASTORE_ID

# Note: FHIR CRUD operations (read/write individual resources) are performed
# via the FHIR REST API endpoint, not the AWS CLI:
# POST https://DATASTORE_ENDPOINT/r4/Patient
# GET  https://DATASTORE_ENDPOINT/r4/Patient/PATIENT_ID
# GET  https://DATASTORE_ENDPOINT/r4/Observation?patient=PATIENT_ID
```

---

## AWS HealthScribe

HealthScribe is accessed through the Amazon Transcribe CLI using `medical-scribe-job` commands.

```bash
# --- Start a Medical Scribe Job ---
aws transcribe start-medical-scribe-job \
  --medical-scribe-job-name patient-visit-2024-001 \
  --media '{"MediaFileUri": "s3://my-audio-bucket/visits/visit-001.mp3"}' \
  --output-bucket-name my-transcribe-output \
  --output-encryption-kms-key-id alias/my-key \
  --data-access-role-arn arn:aws:iam::123456789012:role/HealthScribeRole \
  --settings '{
    "ShowSpeakerLabels": true,
    "MaxSpeakerLabels": 2,
    "ChannelIdentification": false
  }'
  # MaxSpeakerLabels: 2 for typical patient-clinician encounter
  # ChannelIdentification: true if audio has separate channels per speaker

# --- Check Job Status ---
aws transcribe get-medical-scribe-job \
  --medical-scribe-job-name patient-visit-2024-001

# Poll until status is COMPLETED or FAILED
aws transcribe get-medical-scribe-job \
  --medical-scribe-job-name patient-visit-2024-001 \
  --query 'MedicalScribeJob.MedicalScribeJobStatus'

# --- List Jobs ---
aws transcribe list-medical-scribe-jobs
aws transcribe list-medical-scribe-jobs \
  --status COMPLETED \
  --job-name-contains "2024"
aws transcribe list-medical-scribe-jobs \
  --status FAILED

# --- Delete a Job ---
aws transcribe delete-medical-scribe-job \
  --medical-scribe-job-name patient-visit-2024-001
```

Output is written to `s3://my-transcribe-output/patient-visit-2024-001/`:
- `transcript.json` — turn-by-turn transcript with speaker labels, timestamps, and segmentation
- `summary.json` — structured clinical note sections (Chief Complaint, HPI, Assessment, Treatment Plan) with evidence mapping

---

## AWS Trainium & Inferentia (EC2 + Neuron)

Trainium and Inferentia are accessed via standard EC2 and SageMaker APIs; the Neuron SDK provides chip-specific tooling installed on the instances.

```bash
# --- Launch a Trainium Instance ---
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type trn1.2xlarge \
  --key-name my-key-pair \
  --subnet-id subnet-12345678 \
  --security-group-ids sg-12345678 \
  --iam-instance-profile Name=NeuronInstanceProfile \
  --count 1 \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=trainium-training}]'
  # Instance types: trn1.2xlarge (2 chips), trn1.32xlarge (16 chips)
  # trn2.48xlarge (16 Trainium2 chips), trn2u.48xlarge (UltraServer 64 chips)

# --- Launch an Inferentia Instance ---
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type inf2.xlarge \
  --key-name my-key-pair \
  --subnet-id subnet-12345678 \
  --security-group-ids sg-12345678 \
  --count 1
  # Instance types: inf2.xlarge (1 chip), inf2.8xlarge (1 chip, more vCPU/RAM),
  # inf2.24xlarge (6 chips), inf2.48xlarge (12 chips)
  # inf1.xlarge, inf1.2xlarge, inf1.6xlarge, inf1.24xlarge (Inferentia1)

# --- Deploy Inf2 via SageMaker Endpoint ---
aws sagemaker create-model \
  --model-name llama3-neuron-model \
  --primary-container '{
    "Image": "763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-inference-neuronx:2.1.2-neuronx-py310-sdk2.18.0-ubuntu20.04",
    "ModelDataUrl": "s3://my-model-bucket/llama3-neuron.tar.gz",
    "Environment": {
      "NEURON_RT_NUM_CORES": "2",
      "TENSOR_PARALLEL_DEGREE": "2"
    }
  }' \
  --execution-role-arn arn:aws:iam::123456789012:role/SageMakerRole

aws sagemaker create-endpoint-config \
  --endpoint-config-name llama3-neuron-config \
  --production-variants '[{
    "VariantName": "primary",
    "ModelName": "llama3-neuron-model",
    "InstanceType": "ml.inf2.8xlarge",
    "InitialInstanceCount": 1
  }]'

aws sagemaker create-endpoint \
  --endpoint-name llama3-neuron-endpoint \
  --endpoint-config-name llama3-neuron-config

aws sagemaker describe-endpoint --endpoint-name llama3-neuron-endpoint

# --- Neuron Tools (run on instance via SSH) ---
# List Neuron devices and status
neuron-ls

# Real-time Neuron utilization monitor (like nvidia-smi for Neuron)
neuron-top

# Detailed monitoring daemon output
neuron-monitor

# Check installed Neuron SDK version
pip show torch-neuronx
pip show neuronx-cc
```
