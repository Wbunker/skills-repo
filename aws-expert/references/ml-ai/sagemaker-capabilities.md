# AWS Amazon SageMaker — Capabilities Reference
For CLI commands, see [sagemaker-cli.md](sagemaker-cli.md).

## Amazon SageMaker

**Purpose**: Fully managed ML platform for building, training, and deploying machine learning models at scale. Renamed to **Amazon SageMaker AI** in December 2024 (APIs and CLI namespaces unchanged).

### Key Concepts

| Concept | Description |
|---|---|
| **Domain** | Isolated SageMaker environment for a team; contains Studio users, apps, and data configurations |
| **User profile** | Per-user settings within a domain; maps to a single IAM role |
| **Studio** | Browser-based IDE for the full ML lifecycle (notebooks, experiments, pipelines, models) |
| **JupyterLab** | Notebook environment inside Studio |
| **Execution role** | IAM role assigned to training jobs, endpoints, and pipelines for AWS resource access |

### Training Jobs

| Concept | Description |
|---|---|
| **Training job** | Managed container run on EC2 instances; pulls data from S3, outputs model artifacts to S3 |
| **Built-in algorithms** | XGBoost, Linear Learner, DeepAR, etc.; no custom code required |
| **Script mode** | Bring your own Python script with a supported framework (PyTorch, TensorFlow, Hugging Face) |
| **Custom container** | Bring your own Docker image for maximum flexibility |
| **Distributed training** | SageMaker Data Parallelism (SDP) and Model Parallelism (SMP) libraries; supports expert parallelism, sharded data parallelism |
| **Managed Spot Training** | Use EC2 Spot Instances for up to 90% cost savings; requires checkpointing |
| **Warm pools** | Keep compute instances warm between training jobs to reduce startup time |
| **Hyperparameter tuning** | Automated HPO using Bayesian, random, or grid search across defined parameter ranges |

**Common training instance families**: `ml.p3.*` (V100 GPU), `ml.p4d.*` (A100 GPU), `ml.g5.*` (A10G GPU), `ml.trn1.*` (AWS Trainium), `ml.c5.*`/`ml.m5.*` (CPU).

### Model Deployment

| Deployment Type | Description | Best For |
|---|---|---|
| **Real-time endpoint** | Always-on HTTPS endpoint; auto-scales; supports A/B traffic splitting across variants | Low-latency, synchronous inference |
| **Serverless inference** | No instance management; scales to zero; cold starts possible | Intermittent/unpredictable traffic |
| **Async inference** | Queues requests; processes up to 1 GB payloads; up to 1 hour processing; output to S3 | Large inputs, long processing times |
| **Batch transform** | One-time batch job against S3 input dataset; no persistent endpoint | Offline scoring of large datasets |
| **Multi-model endpoint (MME)** | Host thousands of models on a single endpoint; dynamically loaded | Many small models with infrequent access |
| **Multi-container endpoint (MCE)** | Multiple containers on one endpoint in series or independently | Ensembles, preprocessing+inference pipelines |

### SageMaker Pipelines

**Purpose**: Serverless workflow orchestration for ML workflows; DAG-based directed acyclic graph of steps.

| Step Type | Description |
|---|---|
| **Processing** | Run a data processing script (sklearn, Spark, custom) |
| **Training** | Train a model |
| **Tuning** | Hyperparameter optimization |
| **Model** | Register a model artifact |
| **RegisterModel** | Register model to Model Registry |
| **Condition** | Branch pipeline based on metric threshold |
| **Transform** | Batch transform job |
| **Fail** | Explicitly fail the pipeline with a message |
| **Callback** | Pause and wait for external system via SQS/Lambda |
| **Lambda** | Invoke a Lambda function |

Key features: built-in lineage tracking, versioning, visual editor in Studio, SDK + JSON definition, integration with Model Registry.

### Feature Store

| Concept | Description |
|---|---|
| **Feature group** | Named collection of features with an associated schema |
| **Online store** | Low-latency (single-digit ms) storage for real-time inference lookups |
| **Offline store** | S3-backed columnar store for training data and batch retrieval; backed by Glue Data Catalog |
| **Record identifier** | Unique key per entity (e.g., customer_id) |
| **Event time** | Timestamp for point-in-time correct feature retrieval |

### Model Monitor

| Monitor Type | What It Detects |
|---|---|
| **Data quality** | Distribution drift in input features vs. baseline statistics |
| **Model quality** | Prediction accuracy/metric drift vs. ground-truth labels |
| **Bias drift** | Changes in model fairness metrics using SageMaker Clarify |
| **Feature attribution drift** | Changes in SHAP-based feature importance vs. baseline |

### HyperPod

**Purpose**: Persistent clusters for large-scale foundation model pre-training and fine-tuning; survives training interruptions via automatic node recovery and checkpointing.

- Supports Slurm and Amazon EKS as orchestrators
- Optimized networking (EFA, NVLink) for distributed training
- Resilient training: automatically replaces failed nodes

### JumpStart

**Purpose**: Hub for 400+ pre-trained open-source and proprietary models; one-click fine-tuning and deployment.

- Access models from Hugging Face, Meta, Mistral, and more
- Managed inference containers with optimized configurations
- Private model hubs for organizations with governance controls

### Other SageMaker Capabilities

| Capability | Description |
|---|---|
| **Canvas** | No-code AutoML UI; build models by uploading data and selecting a target column |
| **Autopilot** | Automated ML (AutoML); automatically explores algorithms and hyperparameters; produces explainable models |
| **Data Wrangler** | Visual data preparation and feature engineering; exports to Pipelines or Feature Store |
| **Clarify** | Bias detection and explainability (SHAP values) during training and inference |
| **Experiments** | Track, compare, and organize training runs, parameters, and metrics |
| **Model Registry** | Versioned catalog of approved models with metadata, lineage, and deployment history |
| **Ground Truth** | Data labeling service with human workforce (Mechanical Turk, private, or vendor) |
