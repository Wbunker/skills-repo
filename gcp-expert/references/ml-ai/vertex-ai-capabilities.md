# Vertex AI Platform — Capabilities

## Purpose

Vertex AI is Google Cloud's unified MLOps platform for building, training, deploying, and managing machine learning models at scale. It consolidates all GCP ML services under one API surface and provides end-to-end ML pipeline automation, experiment tracking, model governance, and production serving infrastructure. Vertex AI supports all major ML frameworks and provides both managed services and infrastructure for custom workloads.

---

## Core Concepts

| Concept | Description |
|---|---|
| **Training Job** | A managed compute job that runs ML training code; Custom or AutoML |
| **Experiment** | A named container for tracking multiple training runs with different parameters |
| **Run** | A single execution within an Experiment; tracks metrics, parameters, and artifacts |
| **Model** | A versioned artifact stored in the Model Registry with metadata and evaluation metrics |
| **Model Version** | Immutable snapshot of a trained model; supports A/B testing between versions |
| **Endpoint** | An HTTPS endpoint that serves one or more deployed model versions with traffic splitting |
| **Deployed Model** | A model version deployed to an endpoint with specific machine type and autoscaling config |
| **Pipeline** | A DAG of ML steps (data prep, training, evaluation, deployment) using Kubeflow Pipelines v2 |
| **Dataset** | A managed dataset resource linking to data in Cloud Storage, BigQuery, or inline |
| **Feature Store** | Centralized feature repository for training and serving; online and offline |
| **Workbench** | Managed JupyterLab notebook instances with GPU/TPU, pre-installed ML frameworks |
| **Colab Enterprise** | Collaborative notebook environment connected to GCP resources |
| **TensorBoard** | Managed TensorBoard instances for visualizing training metrics |
| **Model Garden** | Catalog of pre-trained models (Google and OSS) available for one-click deployment |

---

## Custom Training

### Supported frameworks
- TensorFlow 2.x (tf.keras, tf.estimator)
- PyTorch (any version via custom container)
- scikit-learn and XGBoost (pre-built containers)
- JAX (with XLA; particularly for TPU training)
- Hugging Face Transformers and Diffusers (custom containers)
- Any Python-based framework via a custom Docker container

### Training job types

| Type | Description |
|---|---|
| **Custom Job** | Single training run; specify container, args, machine type, replica count |
| **Hyperparameter Tuning Job** | Run multiple trials with different hyperparameter values; uses Google Vizier |
| **Training Pipeline** | AutoML training managed as a Pipeline |
| **Custom Training Pipeline** | Custom training step within a Vertex AI Pipeline |

### Pre-built training containers
Google provides pre-built containers for common frameworks:
- `us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.2-2:latest`
- `us-docker.pkg.dev/vertex-ai/training/tf2-gpu.2-13:latest`
- `us-docker.pkg.dev/vertex-ai/training/sklearn.1-3:latest`
- `us-docker.pkg.dev/vertex-ai/training/xgboost-cpu.1-7:latest`

### Worker pool configuration
Custom training jobs can have multiple worker pools for distributed training:
- **Pool 0** (chief/master): typically 1 replica
- **Pool 1** (workers): N replicas for data-parallel training
- **Pool 2** (parameter servers): for async parameter server training
- **Pool 3** (evaluators): optional evaluation workers

### Machine types for training
- Standard: `n1-standard-4`, `n2-standard-8`, etc.
- GPU: `n1-standard-8` + `NVIDIA_TESLA_T4` accelerator
- A100: `a2-highgpu-1g` (1x A100 80GB), `a2-highgpu-8g` (8x A100)
- H100: `a3-highgpu-8g` (8x H100 80GB SXM)
- TPU: specify `tpu_type` in the worker pool spec

---

## Hyperparameter Tuning (Vizier)

Vertex AI Hyperparameter Tuning uses Google Vizier, a black-box optimization service, to find the best hyperparameter combination:
- Define **parameter specs**: continuous, discrete, categorical, integer ranges
- Define a **metric** to optimize (maximize or minimize)
- Vertex AI runs parallel trials, uses Bayesian optimization to select next values based on previous results
- Supports early stopping (pruning) to cancel underperforming trials
- Maximum 8 parallel trials per job (soft limit; configurable)

---

## Experiments and Tracking

Vertex AI Experiments integrates with ML Metadata (MLMD) and TensorBoard:
- **Experiments**: create an experiment context to group related runs
- **Runs**: log parameters (hyperparameters), metrics (loss, accuracy, AUC), and artifact lineage
- **Artifact tracking**: log input datasets, output models, feature schemas as MLMD artifacts with lineage edges
- **TensorBoard integration**: stream training metrics to a managed TensorBoard instance in real-time

### Key metrics tracked per run:
- Time-series metrics (logged at each step): `loss`, `accuracy`, `val_loss`, etc.
- Summary metrics (scalar per run): final epoch accuracy, training duration
- Parameters: learning rate, batch size, model architecture choices

---

## Model Registry

The Vertex AI Model Registry stores model artifacts with full governance:
- **Model upload**: register any model artifact (SavedModel, ONNX, scikit-learn pickle, XGBoost booster, PyTorch state dict) with a serving container
- **Model versions**: maintain multiple versions; compare evaluation metrics across versions
- **Lineage**: link models to the training job and dataset that produced them
- **Evaluation**: store evaluation metrics per version (precision, recall, AUC, RMSE, etc.)
- **Labels and descriptions**: metadata for governance
- **Model export**: download model artifacts from the registry

### Serving containers
Each model version specifies a serving container:
- Pre-built: `us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-13:latest`
- Custom: any container that implements the Vertex AI prediction contract (HTTP endpoint at `0.0.0.0:8080`, `/predict` endpoint, health check at `/`)

---

## Online Prediction (Endpoints)

An **Endpoint** is a stable HTTPS URL that routes requests to deployed model versions:
- **Deploy model to endpoint**: specify machine type, min/max replicas for autoscaling, traffic split
- **Traffic splitting**: route X% of requests to model version A and Y% to version B (for A/B testing / canary deployments)
- **Autoscaling**: scale from 0 replicas (cold start ~30s) to N based on request rate and CPU/GPU utilization
- **Dedicated endpoints**: for high-throughput, low-latency use cases; dedicated compute not shared
- **Explanation**: enable feature attributions (SHAP/Integrated Gradients) per prediction
- **Request/response logging**: log prediction inputs and outputs to BigQuery for monitoring

### Prediction request format
```json
{
  "instances": [
    {"feature_1": 1.0, "feature_2": "value"},
    {"feature_1": 2.0, "feature_2": "other"}
  ],
  "parameters": {"temperature": 0.0}
}
```

### Response format
```json
{
  "predictions": [
    {"score": 0.95, "label": "class_A"},
    {"score": 0.72, "label": "class_B"}
  ],
  "deployedModelId": "1234567890",
  "model": "projects/.../models/my-model",
  "modelDisplayName": "my-model"
}
```

---

## Batch Prediction

For non-latency-sensitive workloads where you need predictions for a large dataset:
- **Input**: BigQuery table, Cloud Storage files (JSON Lines, CSV, TFRecord, Parquet)
- **Output**: BigQuery table or Cloud Storage bucket
- Supports the same model artifacts as online prediction
- Spins up temporary compute (no persistent endpoint needed)
- Significantly cheaper than online prediction for bulk workloads
- Supports accelerators (GPUs) for batch jobs

---

## Vertex AI Pipelines

Vertex AI Pipelines runs orchestrated ML workflows as directed acyclic graphs (DAGs) using the Kubeflow Pipelines v2 (KFP v2) SDK:

### Core concepts
- **Component**: a containerized function with typed inputs and outputs; defined with `@component` decorator or from a YAML spec
- **Pipeline**: a Python function decorated with `@pipeline` that connects components; compiled to a YAML/JSON artifact
- **Pipeline Run**: an execution of a compiled pipeline; tracked in Vertex AI with full artifact lineage
- **Importer component**: import an existing artifact (model, dataset) into a pipeline without retraining
- **Artifact types**: Dataset, Model, Metrics, ClassificationMetrics, HTML, Markdown

### Pre-built components
- Google Cloud Pipeline Components (`google-cloud-pipeline-components` library): ready-to-use components for AutoML, BigQuery, Dataflow, Vertex AI training/deployment
- Example: `AutoMLTabularTrainingJobRunOp`, `ModelDeployOp`, `BigqueryQueryJobOp`

### Scheduling
- Trigger pipeline runs on a cron schedule via Vertex AI Pipeline Schedules
- Trigger from Cloud Scheduler, Pub/Sub, or Cloud Functions for event-driven pipelines

---

## Feature Store

Vertex AI Feature Store is a centralized repository for ML features that enables:
- **Online serving**: low-latency (single-digit milliseconds) feature lookup by entity key
- **Offline serving**: batch export of feature values joined with entity labels for training
- **Feature monitoring**: detect data distribution drift between baseline and serving distributions
- **Backfills**: ingest historical feature values with timestamps (point-in-time correct joins)

### Architecture
- **Feature Store** (resource) → **Feature View** → **Feature Registry** (defines feature schemas)
- Feature data is stored in Bigtable (online) and BigQuery (offline)
- **Feature Sync**: periodically sync from BigQuery source to online store
- Supports `FeatureOnlineStore` (legacy: BigTable) and newer embedding-based index for vector search

---

## Vector Search (Matching Engine)

Vertex AI Vector Search (formerly Matching Engine) provides billion-scale approximate nearest neighbor (ANN) search:
- Index types: `tree-ah` (memory-efficient), `brute-force` (exact, smaller datasets)
- Supports cosine, dot product, and L2 distance metrics
- Update modes: batch updates (rebuild index) or streaming updates (incremental)
- Deploy index to an `IndexEndpoint` for online querying
- Common use: semantic search, recommendation engines, RAG retrieval

---

## Model Garden

Model Garden is a catalog of pre-trained models available on Vertex AI:

| Category | Models |
|---|---|
| Google Foundation | Gemini 2.0 Pro/Flash, Gemma 2, Gemma 3, PaLM 2, Imagen 3, MusicLM |
| OSS LLMs | Llama 3.1/3.2/3.3 (Meta), Mistral, Mixtral, Falcon, Phi-3/3.5 |
| Vision | Stable Diffusion XL, FLUX, SAM (Meta Segment Anything) |
| Multimodal | LLaVA, InternVL |
| Specialized | Med-PaLM 2 (medical), SecLM (security) |

Deploy models from Model Garden with one click to a Vertex AI Endpoint. Some models require a model license acceptance before deployment.

---

## Vertex AI Agent Builder

Build production-grade search and conversational AI applications:

### Data Stores (knowledge bases)
| Type | Data Source |
|---|---|
| Website | URLs crawled by Googlebot |
| Cloud Storage | PDF, HTML, DOCX, TXT files |
| BigQuery | Structured data tables |
| Firestore / Spanner | Application database documents |
| Third-party (Healthcare, etc.) | FHIR data stores |

### Applications
- **Search**: unstructured document retrieval with LLM-enhanced summaries and citations
- **Conversational agent**: multi-turn chat with grounding in data stores; built on Dialogflow CX infrastructure
- **Recommendations**: personalized recommendations using structured data stores
- **RAG** (Retrieval Augmented Generation): retrieve relevant chunks → generate grounded answers

### Grounding in Agent Builder
The `groundingConfig` in Vertex AI generative model calls can reference Agent Builder data store IDs to ground model responses in your private enterprise data.

---

## MLOps Best Practices

1. **Version everything**: use the Model Registry with semantic versioning; tag each model with the training dataset version and pipeline run ID.
2. **Track all experiments**: use Vertex AI Experiments for every training run; never run training without logging parameters and metrics.
3. **Automate with Pipelines**: production training must use a pipeline; manual notebook re-runs are not reproducible.
4. **Monitor models in production**: enable prediction logging on endpoints; set up Model Monitoring for feature skew and prediction drift alerts.
5. **Use Feature Store for shared features**: prevent feature computation duplication across teams; ensure point-in-time correct feature values for training.
6. **Implement evaluation gates**: pipelines should include an evaluation step that compares the new model against the current production model; only deploy if the new model meets a quality threshold.
7. **Use dedicated endpoints for latency-critical services**: shared endpoints have variable latency; dedicated endpoints have reserved compute.
8. **Artifact lineage is auditable by default**: use it; query MLMD to trace which data produced which model.
9. **Use Workbench for development, Pipelines for production**: exploratory work in notebooks; scheduled, reproducible runs in pipelines.
10. **Implement CI/CD for pipelines**: store pipeline definitions in version control; trigger pipeline compilation and re-runs via Cloud Build on changes.
