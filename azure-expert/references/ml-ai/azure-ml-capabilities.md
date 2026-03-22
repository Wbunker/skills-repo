# Azure Machine Learning — Capabilities

## Service Overview

Azure Machine Learning (Azure ML) is Microsoft's enterprise MLOps platform covering the full lifecycle of machine learning: data preparation, experiment tracking, model training, evaluation, deployment, monitoring, and governance. It is the platform for building and operationalizing custom ML models on Azure.

**Primary SDK**: `azure-ai-ml` (v2, Python) — YAML-based job definitions with SDK orchestration.

---

## Azure ML Workspace

The workspace is the top-level resource that acts as the central hub for all ML activities within a project or team.

### Associated Resources (auto-created)

| Resource | Purpose |
|---|---|
| Azure Storage Account | Default datastore for job inputs/outputs, artifacts |
| Azure Key Vault | Store secrets, credentials, connection strings |
| Application Insights | Log metrics, traces, and custom telemetry |
| Azure Container Registry | Store Docker images for training environments |

### Workspace Variants

| Type | Description |
|---|---|
| **Standalone ML Workspace** | Standard Azure Machine Learning workspace |
| **Hub Workspace (AI Foundry Hub)** | Extended workspace for GenAI workloads via Azure AI Foundry; acts as shared resource hub for AI Foundry projects |

### Access Control

- **Owner**: Full control, manage access
- **Contributor**: Create and manage resources, run experiments
- **AzureML Data Scientist**: Submit experiments, register models, create endpoints
- **AzureML Compute Operator**: Start/stop/manage compute without data access

---

## Compute

### Compute Instances

Managed cloud VMs for interactive ML development:

- Single-node VM (CPU or GPU) assigned to a specific user.
- Pre-installed: JupyterLab, Jupyter, VS Code Server, R Studio, conda, ML frameworks.
- Supports **VS Code Remote** attachment for local IDE experience against cloud compute.
- Idle shutdown configurable to reduce cost.
- Managed identity support for secure access to data stores.

```yaml
# compute-instance.yaml
$schema: https://azuremlschemas.azureedge.net/latest/computeInstance.schema.json
name: dev-instance
type: computeinstance
size: Standard_DS3_v2
idle_time_before_shutdown_minutes: 60
```

### Compute Clusters

Auto-scaling multi-node clusters for training and batch jobs:

- Scale from 0 to N nodes (scale to zero when idle to eliminate costs).
- Supports **Spot VMs** (interruptible, up to 90% cost reduction) for fault-tolerant jobs.
- CPU and GPU clusters; GPU options: NC-series (T4), NCA100, NDv4 (A100).
- Per-job cluster allocation — multiple jobs share cluster.

```yaml
# compute-cluster.yaml
$schema: https://azuremlschemas.azureedge.net/latest/amlCompute.schema.json
name: gpu-cluster
type: amlcompute
size: Standard_NC6s_v3
min_instances: 0
max_instances: 4
idle_time_before_scale_down: 120
tier: Dedicated  # or LowPriority (Spot)
```

### Serverless Compute

- On-demand compute without pre-provisioning a cluster.
- Recommended for most training jobs — Microsoft manages capacity.
- Specify `compute: serverless` in job YAML.
- No idle cost; billed per job execution second.

### Inference Clusters (AKS)

- Azure Kubernetes Service clusters attached for high-scale online inference.
- Useful for existing AKS infrastructure or advanced Kubernetes-native requirements.
- Managed Online Endpoints preferred for most new deployments.

### Attached Compute

External compute attached to Azure ML workspace for job submission:

| Type | Use Case |
|---|---|
| Databricks | Spark-based training on existing Databricks cluster |
| HDInsight | Hadoop-based processing |
| Remote VM | On-premises or other cloud VMs |
| Azure Arc-enabled Kubernetes | Edge or multi-cloud Kubernetes |

---

## MLflow Integration

Azure ML natively integrates with MLflow for experiment tracking and model packaging.

### Experiment Tracking

```python
import mlflow
import mlflow.sklearn
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

ml_client = MLClient(DefaultAzureCredential(), subscription_id, resource_group, workspace_name)

# MLflow tracking URI automatically set when running as Azure ML job
mlflow.set_experiment("my-experiment")

with mlflow.start_run():
    mlflow.log_param("learning_rate", 0.01)
    mlflow.log_param("max_depth", 5)
    mlflow.log_metric("accuracy", 0.92)
    mlflow.log_metric("f1_score", 0.89)
    mlflow.sklearn.log_model(model, "model")
```

### Model Flavors

MLflow supports logging models in many flavors: `mlflow.sklearn`, `mlflow.pytorch`, `mlflow.tensorflow`, `mlflow.xgboost`, `mlflow.transformers` (Hugging Face), `mlflow.pyfunc` (custom).

---

## Model Training Approaches

### 1. Script-Based Jobs (Recommended)

Submit Python training scripts as Azure ML jobs via YAML definitions.

```yaml
# job.yaml
$schema: https://azuremlschemas.azureedge.net/latest/commandJob.schema.json
type: command
display_name: train-classifier
code: ./src
command: python train.py --lr ${{inputs.lr}} --epochs ${{inputs.epochs}} --data ${{inputs.training_data}}
inputs:
  lr: 0.01
  epochs: 50
  training_data:
    type: uri_folder
    path: azureml:my-dataset@latest
outputs:
  model_output:
    type: mlflow_model
environment: azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest
compute: serverless
resources:
  instance_type: Standard_DS3_v2
```

### 2. AutoML

Automated machine learning — Azure ML searches for the best model and hyperparameters.

**Supported task types**:
- Classification, Regression, Time-series Forecasting
- Computer Vision: Image Classification, Object Detection, Instance Segmentation
- NLP: Text Classification, Named Entity Recognition, Question Answering

```yaml
# automl-job.yaml
$schema: https://azuremlschemas.azureedge.net/latest/autoMLJob.schema.json
type: automl
task: classification
primary_metric: accuracy
training_data:
  path: azureml:my-training-data@latest
  type: mltable
target_column_name: label
limits:
  timeout_minutes: 60
  max_trials: 20
  max_concurrent_trials: 4
compute: cpu-cluster
```

### 3. Designer (Drag-and-Drop)

Low-code ML pipeline builder in the Azure ML Studio UI. Pre-built modules for data transformation, feature engineering, model training, evaluation. Export to YAML pipelines for production.

---

## Pipelines

Component-based ML pipelines for reproducible, parameterized workflows.

### Components

Reusable building blocks defined in YAML:

```yaml
# component.yaml
$schema: https://azuremlschemas.azureedge.net/latest/commandComponent.schema.json
name: prep_data
version: 1
display_name: Prepare Data
type: command
inputs:
  raw_data:
    type: uri_folder
outputs:
  processed_data:
    type: uri_folder
code: ./prep_src
command: python prep.py --raw-data ${{inputs.raw_data}} --processed-data ${{outputs.processed_data}}
environment: azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest
```

### Pipeline Job

```yaml
# pipeline.yaml
$schema: https://azuremlschemas.azureedge.net/latest/pipelineJob.schema.json
type: pipeline
display_name: ml-pipeline
compute: serverless
jobs:
  prep_step:
    type: command
    component: azureml:prep_data@1
    inputs:
      raw_data:
        type: uri_folder
        path: azureml:raw-dataset@latest
  train_step:
    type: command
    component: azureml:train_model@1
    inputs:
      training_data: ${{parent.jobs.prep_step.outputs.processed_data}}
```

---

## Environments

Docker-based reproducible compute environments.

### Curated Environments

Microsoft-maintained environments with common frameworks pre-installed:

```bash
# List curated environments
az ml environment list --query "[?startsWith(name, 'AzureML')]" -o table
# Examples: AzureML-sklearn-1.0-ubuntu20.04-py38-cpu, AzureML-pytorch-1.13-ubuntu20.04-py38-cuda11-gpu
```

### Custom Environments

```yaml
# custom-env.yaml
$schema: https://azuremlschemas.azureedge.net/latest/environment.schema.json
name: my-training-env
version: 1
image: mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest
conda_file: conda.yaml
```

```yaml
# conda.yaml
name: my-env
channels: [conda-forge, defaults]
dependencies:
  - python=3.10
  - pip:
    - scikit-learn>=1.3
    - pandas>=2.0
    - mlflow
    - azure-ai-ml
```

---

## Managed Online Endpoints

Real-time inference with managed infrastructure:

- **Blue-green deployment**: Route traffic percentages between deployment versions (e.g., 90% blue / 10% green) for safe rollouts.
- **Managed scaling**: Auto-scale based on CPU/memory/request queue depth.
- **Instance-based**: Choose VM SKU and instance count.
- **Key-based or token-based auth**: RBAC with `AzureML Online Endpoint` role.
- **Monitoring**: Prometheus metrics, Azure Monitor integration.

```yaml
# endpoint.yaml
$schema: https://azuremlschemas.azureedge.net/latest/managedOnlineEndpoint.schema.json
name: my-classifier-endpoint
auth_mode: key

# deployment.yaml
$schema: https://azuremlschemas.azureedge.net/latest/managedOnlineDeployment.schema.json
name: blue
endpoint_name: my-classifier-endpoint
model: azureml:my-model@latest
instance_type: Standard_DS3_v2
instance_count: 2
```

---

## Managed Batch Endpoints

Large-scale asynchronous batch inference:

- Invoke with a pointer to input data (ADLS path, registered dataset).
- Returns output data to a configured output path.
- Auto-scales compute, parallelizes inference across many files.
- Supports MLflow models and custom scoring scripts.
- No persistent compute when not running — cost-efficient for scheduled inference.

```bash
# Invoke batch endpoint
az ml batch-endpoint invoke \
  --name my-batch-endpoint \
  --input azureml:batch-input-data@latest \
  --output-path azureml://datastores/workspaceblobstore/paths/batch-outputs/
```

---

## Model Registry

Centralized versioned model store within the workspace.

| Concept | Description |
|---|---|
| **Model name** | Logical identifier for a model family |
| **Version** | Immutable numbered artifact (auto-incremented or specified) |
| **Model format** | mlflow_model, custom_model, triton_model |
| **Tags/Properties** | Key-value metadata for filtering and promotion |
| **Lineage** | Link to training job, dataset, environment |

```python
from azure.ai.ml.entities import Model
from azure.ai.ml.constants import AssetTypes

model = ml_client.models.create_or_update(
    Model(
        name="my-classifier",
        path="runs:/<run-id>/model",
        type=AssetTypes.MLFLOW_MODEL,
        description="Random forest classifier for customer churn",
        tags={"stage": "production", "accuracy": "0.92"}
    )
)
```

---

## Data Assets

| Type | Description | Use Case |
|---|---|---|
| `uri_file` | Reference to a single file | Input file for a job |
| `uri_folder` | Reference to a directory | Folder of training files |
| `mltable` | Schema-defined tabular data | AutoML, structured data jobs |

```yaml
# data-asset.yaml
$schema: https://azuremlschemas.azureedge.net/latest/data.schema.json
name: customer-churn-data
version: 1
type: uri_folder
path: azureml://datastores/workspaceblobstore/paths/datasets/churn/
```

---

## Responsible AI Dashboard

Integrated tooling for model explanation and fairness analysis:

| Component | Tool / Library | Description |
|---|---|---|
| Model Explanations | SHAP (SHapley Additive exPlanations) | Feature importance at global and local (per-prediction) level |
| Error Analysis | Microsoft ErrorAnalysis library | Identify cohorts where model underperforms |
| Fairness Assessment | Fairlearn | Measure and mitigate disparate impact across demographic groups |
| Causal Analysis | EconML | Estimate causal effects of features on outcomes |
| Data Insights | Built-in | Dataset statistics, feature distributions, target balance |
| Counterfactual Analysis | DiCE | Minimal changes to flip model prediction |

Enable via `ResponsibleAIInsights` pipeline component after model training. Outputs viewable in Azure ML Studio.

---

## Azure ML SDK v2 Quick Reference

```python
from azure.ai.ml import MLClient, command, Input, Output
from azure.ai.ml.entities import (
    AmlCompute, ComputeInstance, Environment, Model,
    ManagedOnlineEndpoint, ManagedOnlineDeployment
)
from azure.identity import DefaultAzureCredential

# Connect to workspace
ml_client = MLClient(
    DefaultAzureCredential(),
    subscription_id="<sub-id>",
    resource_group_name="<rg>",
    workspace_name="<ws>"
)

# Submit a job
job = command(
    code="./src",
    command="python train.py --data ${{inputs.data}}",
    inputs={"data": Input(type="uri_folder", path="azureml:my-data@latest")},
    environment="azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",
    compute="serverless",
    display_name="my-training-job"
)
returned_job = ml_client.jobs.create_or_update(job)
ml_client.jobs.stream(returned_job.name)  # stream logs

# Register a model
ml_client.models.create_or_update(
    Model(name="my-model", path=f"azureml://jobs/{returned_job.name}/outputs/artifacts/paths/model/")
)
```
