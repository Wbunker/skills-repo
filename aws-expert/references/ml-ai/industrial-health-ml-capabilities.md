# Industrial, Health & Physical ML — Capabilities Reference
For CLI commands, see [industrial-health-ml-cli.md](industrial-health-ml-cli.md).

## Amazon Lookout for Equipment

**Purpose**: Anomaly detection service for industrial equipment that trains ML models on historical sensor data (vibration, temperature, pressure, flow rates) to detect abnormal machine behavior and enable predictive maintenance — no ML expertise required.

> **Note**: AWS will discontinue Lookout for Equipment on October 7, 2026. Explore Amazon SageMaker or third-party predictive maintenance solutions as alternatives.

### Core Concepts

| Concept | Description |
|---|---|
| **Dataset** | Container for historical sensor data uploaded from SCADA, process historians, or condition monitoring systems |
| **Data ingestion job** | Job that imports data from S3 into a dataset for model training |
| **Model** | ML model trained on a specific dataset; learns normal operating patterns for one piece of equipment |
| **Label group** | Collection of time-range labels marking historical anomaly/failure periods used to improve model accuracy |
| **Inference scheduler** | Scheduled job that continuously feeds new sensor readings to a deployed model and generates predictions |
| **Inference execution** | Individual run of the inference scheduler; outputs anomaly scores and flagged sensors to S3 |

### How It Works

```
Sensor data (S3) → Dataset → Train Model → Deploy Model
→ Inference Scheduler → Anomaly Score + Flagged Sensors → S3 output → SNS/EventBridge alert
```

### Key Features

- **Up to 300 sensors per model**: Learns multi-dimensional relationships across all sensor channels
- **Pinpoints failing sensors**: Rather than a generic alert, identifies which specific sensor signals are anomalous
- **Confidence scoring**: Each inference execution returns an anomaly score and flagged sensors with timestamps
- **Label-guided training**: Optionally mark known failure periods in historical data to sharpen the model
- **Scheduled inference**: Run on 5-minute, 10-minute, 15-minute, 30-minute, or 1-hour intervals
- **S3 output + EventBridge**: Results written to S3; trigger downstream actions via EventBridge rules

### Supported Equipment Types

| Category | Examples |
|---|---|
| Rotating | Pumps, compressors, motors, turbines, CNC machines |
| Process | Heat exchangers, boilers, inverters |
| Constraint | Fixed, stationary equipment with relatively stable operating conditions |

### Use Case Pattern: Predictive Maintenance

1. Export 30–90 days of multi-sensor historical data to S3 in CSV format
2. Create dataset and run data ingestion job
3. Optionally add label group with known failure windows
4. Train model (takes ~30 minutes to several hours)
5. Create inference scheduler pointing at a live sensor data S3 prefix
6. Route inference output to SNS or a maintenance ticketing system via EventBridge

---

## Amazon Lookout for Vision

**Purpose**: Computer vision anomaly detection service that trains models to identify visual defects (dents, scratches, missing components, incorrect assemblies) in product images from manufacturing inspection stations — no CV/ML expertise required.

> **Note**: Check current AWS service status, as Lookout for Vision has been superseded in some use cases by Amazon Rekognition Custom Labels.

### Core Concepts

| Concept | Description |
|---|---|
| **Project** | Top-level container for datasets and trained models for a single inspection use case |
| **Dataset** | Labeled image collection: `train` (required) and `test` datasets |
| **Anomaly** | Detected defect in an image; can be image-level (classification) or pixel-level (segmentation) |
| **Model** | Trained CV model associated with a project; versioned |
| **Model version** | Specific training run; evaluate metrics (F1, precision, recall) before deploying |
| **Trial detection** | Run bulk inference against a set of images without a running model unit (pay-per-image) |
| **Model packaging job** | Package a trained model to deploy on AWS Panorama appliance or edge device |

### Detection Types

| Type | Description | When to Use |
|---|---|---|
| **Image classification** | Labels entire image as `normal` or `anomaly` | Pass/fail inspection without needing defect location |
| **Image segmentation** | Identifies which pixels are anomalous; returns anomaly mask | When defect type and location matter |

### Training Workflow

```
Labeled images (normal + anomaly) → S3 → Dataset → Train Model
→ Evaluate metrics → Start model unit → DetectAnomalies API → Stop model unit
```

### Key Features

- **Small labeled dataset support**: Can train effective models with as few as 20–30 labeled anomaly images
- **Automatic augmentation**: Service augments training data for improved generalization
- **Pixel-level segmentation**: Anomaly masks identify exact defect location and type
- **Edge deployment**: Package models for AWS Panorama for on-premises camera inference
- **Pay-per-use inference**: Trial detection mode bills per image; running model units bill per hour

---

## Amazon Monitron

**Purpose**: End-to-end industrial condition monitoring system combining wireless vibration/temperature sensors, a gateway, and ML-powered cloud analysis to detect early signs of abnormal equipment behavior — no data science or infrastructure setup required.

> **Note**: Amazon Monitron is no longer available to new customers as of October 31, 2024.

### System Components

| Component | Description |
|---|---|
| **Monitron sensor** | Wireless device attached to equipment; measures vibration (ISO 10816) and temperature; transmits via Bluetooth LE |
| **Monitron gateway** | WiFi/LTE device that receives sensor readings and securely relays data to AWS |
| **Monitron project** | AWS resource grouping assets, gateways, and sensors for a monitoring deployment |
| **Asset** | Represents a physical machine (e.g., pump, motor, fan); groups measurement positions |
| **Position** | Specific attachment point on an asset (e.g., drive end bearing, non-drive end bearing) |
| **Monitron mobile/web app** | Interface for setup, alert management, and technician feedback |

### Detection Model

Monitron uses ISO 10816-3 vibration standards combined with ML anomaly detection:

| State | Meaning |
|---|---|
| **Healthy** | Vibration and temperature within normal operating bounds |
| **Warning** | Early anomaly signal detected; schedule preventive action |
| **Alarm** | Significant anomaly; immediate attention recommended |
| **Unknown** | Insufficient data for classification (new equipment or sensor) |

### Key Features

- **Zero-configuration ML**: Models automatically establish baselines per sensor position; no training data required
- **Sub-5-minute setup**: Sensor stickers + gateway pairing via mobile app; monitoring begins within minutes
- **Feedback loop**: Technicians confirm or dismiss alerts via app, improving future detection accuracy
- **ISO 10816 compliance**: Vibration severity categorized per international standards for rotating machinery
- **Equipment coverage**: Fans, bearings, compressors, motors, gearboxes, pumps

---

## AWS Panorama

**Purpose**: ML appliance service that enables on-premises computer vision inference on existing IP cameras without sending video to the cloud; runs CV models at the edge on the AWS Panorama Appliance.

> **Note**: AWS will end support for AWS Panorama on May 31, 2026.

### Core Concepts

| Concept | Description |
|---|---|
| **Panorama appliance** | Edge hardware device (IP-62 rated) running multiple CV models on multiple video streams simultaneously |
| **Panorama application** | Containerized Python code + ML model(s) packaged and deployed to the appliance |
| **Application node** | Modular component within a Panorama application: camera node, model node, or code node |
| **Application package** | Versioned container image + model assets uploaded to S3 and registered with Panorama |
| **Device** | Registered Panorama appliance provisioned in an AWS account |
| **Deployment job** | Operation that pushes an application to a device; includes camera stream assignments |

### Architecture

```
IP cameras (RTSP) → Panorama Appliance → [CV Model + Application Code]
→ Results (metadata, alerts) → S3 / DynamoDB / SNS / SageMaker
```

### Key Features

- **No cloud video egress**: Video frames processed locally; only inference results sent to AWS
- **Multi-stream, multi-model**: Run several models on multiple camera feeds in parallel
- **SageMaker Neo integration**: Compile and optimize models for the Panorama hardware before deployment
- **IoT-managed updates**: Device software updates and application deployments via AWS IoT
- **Edge SDK**: Python SDK for writing application business logic that processes inference results

### Common Use Cases

| Use Case | Pattern |
|---|---|
| Retail traffic analytics | Count people per zone; write counts to DynamoDB or QuickSight |
| Safety monitoring | Detect PPE compliance or unauthorized area access; send SNS alert |
| Quality control | Identify manufacturing defects on assembly line in real time |
| Model improvement | Capture borderline images locally; upload to S3 for SageMaker retraining |

---

## AWS HealthLake

**Purpose**: HIPAA-eligible, fully managed cloud service for storing, indexing, querying, and analyzing health data using the FHIR R4 standard; includes integrated medical NLP to extract insights from unstructured clinical text.

### Core Concepts

| Concept | Description |
|---|---|
| **FHIR datastore** | Managed, indexed repository of FHIR R4 resources; provides a transactional FHIR server with REST APIs |
| **FHIR R4 resource** | Standard health data object: Patient, Encounter, Observation, Condition, MedicationRequest, Procedure, etc. |
| **Import job** | Bulk load FHIR-format data from S3 into a datastore |
| **Export job** | Export all FHIR resources from a datastore to S3 for downstream analytics |
| **Integrated NLP** | Automated extraction of medical entities, relationships, and traits from unstructured text fields; results stored as FHIR extensions |
| **SMART on FHIR** | OAuth 2.0-based authorization standard for controlling access to FHIR resources |

### FHIR Server Capabilities

| Capability | Description |
|---|---|
| **CRUD operations** | Create, read, update, delete individual FHIR resources via REST API |
| **Search** | FHIR-standard search parameters (by patient, date, code, etc.) |
| **Bulk export** | Export all resources or filtered subsets via FHIR Bulk Data API |
| **Validate** | Resource validation against FHIR R4 schema |
| **Patient timeline** | Chronological view of all resources for a patient |

### Integrated NLP

Automatically processes unstructured text in FHIR resources (e.g., clinical notes in `DocumentReference`):
- Extracts medical entities: conditions, medications, dosages, anatomy, test/treatment/procedure
- Identifies PHI for compliance auditing
- Maps entities to ICD-10-CM, RxNorm, and SNOMED CT
- Stores extracted insights as FHIR R4 extensions queryable via Athena

### Analytics Integration Pattern

```
EHR system → S3 → HealthLake Import Job → FHIR Datastore
→ Export to S3 → Athena / QuickSight / SageMaker
```

### Security & Compliance

- HIPAA eligible; suitable for PHI
- Encryption at rest and in transit by default
- IAM + SMART on FHIR for access control
- CloudTrail audit logging; PrivateLink for VPC-only access

---

## AWS HealthScribe

**Purpose**: HIPAA-eligible service that automatically generates structured clinical documentation (SOAP notes, GIRPP notes) from patient-clinician conversation audio using speech recognition combined with generative AI; purpose-built for healthcare software vendors (ISVs).

### Core Concepts

| Concept | Description |
|---|---|
| **Medical scribe job** | Async job that processes an audio file and returns transcript + clinical note sections |
| **Transcript** | Turn-by-turn conversation with speaker labels (CLINICIAN / PATIENT), word timestamps, and dialogue segmentation |
| **Clinical note sections** | Structured output: Chief Complaint, History of Present Illness (HPI), Review of Systems, Physical Exam, Assessment, Treatment Plan |
| **GIRPP note** | Behavioral health note format: Goals, Interventions, Response, Progress, Plan |
| **Evidence mapping** | Each generated note sentence links back to the transcript segment that supports it |
| **Medical entities** | Extracted structured data: conditions, medications, procedures, dosages, anatomy |

### How It Works

```
Audio recording (S3) → start-medical-scribe-job
→ [Speaker diarization + ASR → NLP entity extraction → Generative note synthesis]
→ Output JSON (transcript + clinical sections + evidence links) in S3
```

### Key Features

- **Speaker role identification**: Automatically labels CLINICIAN vs PATIENT speech turns
- **Dialogue segmentation**: Classifies transcript by clinical relevance (small talk, subjective, objective, assessment/plan)
- **Evidence-linked notes**: Every AI-generated sentence cites the exact transcript lines it was drawn from
- **Medical vocabulary**: Optimized for clinical terminology, drug names, procedures, anatomy
- **Data privacy**: Audio and outputs are not retained by AWS; data not used for model training
- **HIPAA eligible**: Suitable for Protected Health Information (PHI)

### Supported Note Templates

| Template | Use Case |
|---|---|
| **SOAP** | General outpatient consultations (Subjective, Objective, Assessment, Plan) |
| **GIRPP** | Behavioral health / mental health sessions |

### Integration Pattern

```python
# Typical integration: record audio, submit job, poll, retrieve output
import boto3
transcribe = boto3.client('transcribe')
transcribe.start_medical_scribe_job(
    MedicalScribeJobName='visit-2024-001',
    Media={'MediaFileUri': 's3://my-bucket/audio/visit.mp3'},
    OutputBucketName='my-output-bucket',
    OutputEncryptionKMSKeyId='alias/my-key',
    DataAccessRoleArn='arn:aws:iam::123456789012:role/HealthScribeRole',
    Settings={
        'ShowSpeakerLabels': True,
        'MaxSpeakerLabels': 2,
        'ChannelIdentification': False
    }
)
```

---

## AWS Trainium

**Purpose**: AWS-designed ML training accelerator chip (available as EC2 Trn1/Trn2/Trn3 instances) that delivers high performance and cost efficiency for training large-scale deep learning models — up to 50% lower training cost than comparable GPU instances.

### Instance Families

| Instance | Chip | Key Specs | Best For |
|---|---|---|---|
| **Trn1** | Trainium1 | Up to 16 chips per instance, 512 GB HBM | Cost-efficient large model training |
| **Trn2** | Trainium2 | Up to 16 chips (single), 64 chips (UltraServer), 4x perf vs Trn1 | Frontier model training, large-scale distributed |
| **Trn3** | Trainium3 (3nm) | 2.52 PFLOPs, 144 GB HBM3e, 4.4x vs Trn2 UltraServer | Cutting-edge GenAI model training |

### AWS Neuron SDK

The Neuron SDK is the software stack for programming Trainium (and Inferentia) chips:

| Component | Description |
|---|---|
| **Neuron Compiler** | Compiles PyTorch/JAX graphs to Neuron Executable File Format (NEFF) for hardware execution |
| **Neuron Runtime** | Manages model execution, memory allocation, and NeuronCore scheduling |
| **Neuron Tools** | CLI tools for profiling, debugging, and monitoring (`neuron-top`, `neuron-ls`) |
| **NeuronCore** | Individual compute unit on each chip; multiple NeuronCores per chip |

### Supported Frameworks

- **PyTorch** (`torch-neuronx`): Native `torch.compile()` integration; minimal code changes
- **JAX** (`jax-neuronx`): XLA-based compilation path
- **Hugging Face Transformers**: `optimum-neuron` library for seamless model training

### Key Features

- **BF16, FP8, MXFP8, MXFP4**: Mixed precision for memory and compute efficiency
- **Stochastic rounding**: Improves convergence with reduced-precision training
- **4x sparsity**: Hardware-accelerated sparse matrix operations
- **NeuronLink interconnect**: High-bandwidth chip-to-chip communication for multi-chip distributed training
- **EFA networking**: Elastic Fabric Adapter for low-latency multi-node training

### Use Case Pattern: Distributed LLM Training

```python
# torch-neuronx distributed training (minimal changes from standard PyTorch)
import torch_neuronx
import torch.distributed as dist

# Standard DDP or FSDP training loop works with neuronx backend
# Compile step: first run traces and compiles the graph
model = MyTransformerModel()
optimizer = torch.optim.AdamW(model.parameters())
# model.to('xla')  # Trainium uses XLA device
```

---

## AWS Inferentia

**Purpose**: AWS-designed ML inference accelerator chip (available as EC2 Inf1/Inf2 instances) that delivers high throughput and low latency for serving trained deep learning models at reduced cost versus GPU-based inference.

### Instance Families

| Instance | Chip | Key Specs | Best For |
|---|---|---|---|
| **Inf1** | Inferentia1 | Up to 16 chips, 128 GB total HBM | Cost-efficient inference for production workloads |
| **Inf2** | Inferentia2 | Up to 12 chips, 384 GB HBM, 4x higher throughput vs Inf1 | Large model inference, sub-10ms latency |

### Inferentia2 Performance

- 190 TFLOPS FP16 per chip (2 NeuronCores per chip)
- Up to 10x lower latency vs Inferentia1
- 50% better performance-per-watt vs comparable GPU instances
- Supports: FP32, FP16, BF16, INT8, configurable FP8

### AWS Neuron SDK (Inference Path)

| Step | Tool/Library | Description |
|---|---|---|
| **Compile** | `torch_neuronx.trace()` | Trace and compile a PyTorch model to NEFF format |
| **Optimize** | Neuron Compiler flags | Choose precision, data parallelism, pipeline parallelism |
| **Serve** | TorchServe, Triton, SageMaker | Deploy compiled `.neff` model for inference |
| **Monitor** | `neuron-monitor`, CloudWatch | Track NeuronCore utilization, memory, throughput |

### Supported Frameworks

- **PyTorch** (`torch-neuronx`): `trace()` and `compile()` compilation paths
- **TensorFlow** (`tensorflow-neuron`): Graph compilation via `tfn.trace()`
- **Hugging Face** (`optimum-neuron`): One-line export for popular Transformers models

### Key Features

- **Automatic precision casting**: Neuron SDK handles FP32 → BF16 without retraining
- **Model sharding**: Pipeline parallelism splits large models across multiple NeuronCores/chips
- **Continuous batching**: Maximizes throughput for LLM token generation
- **SageMaker integration**: Deploy Inf2 instances via SageMaker endpoints with `inf2` instance type selection

### Use Case Pattern: Compile and Deploy a Transformers Model

```python
import torch
import torch_neuronx
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3-8b")
# Trace (compile) for Inferentia2
example_inputs = (input_ids, attention_mask)
traced_model = torch_neuronx.trace(model, example_inputs)
traced_model.save("llama3-8b-neuron.pt")

# Load and serve compiled model
loaded_model = torch.jit.load("llama3-8b-neuron.pt")
```
