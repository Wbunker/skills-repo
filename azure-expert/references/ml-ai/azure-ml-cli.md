# Azure Machine Learning — CLI & SDK Reference

## Prerequisites

```bash
# Install the Azure ML CLI extension (v2)
az extension add -n ml

# Upgrade to latest version
az extension update -n ml

# Set defaults to avoid repeating --resource-group and --workspace-name
az configure --defaults group=myRG workspace=myWorkspace

# Login
az login
az account set --subscription "My Subscription"
```

---

## Workspace Management

```bash
# Create a new Azure ML workspace
az ml workspace create \
  --name myWorkspace \
  --resource-group myRG \
  --location eastus \
  --display-name "My ML Workspace"

# Create workspace with existing associated resources
az ml workspace create \
  --name myWorkspace \
  --resource-group myRG \
  --location eastus \
  --storage-account /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{name} \
  --key-vault /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.KeyVault/vaults/{name} \
  --application-insights /subscriptions/{sub}/resourceGroups/{rg}/providers/microsoft.insights/components/{name} \
  --container-registry /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.ContainerRegistry/registries/{name}

# Show workspace details (includes storage, ACR, etc.)
az ml workspace show \
  --name myWorkspace \
  --resource-group myRG

# List workspaces in resource group
az ml workspace list \
  --resource-group myRG \
  -o table

# List connection details (endpoint, keys)
az ml workspace list-keys \
  --name myWorkspace \
  --resource-group myRG

# Diagnose workspace connectivity issues
az ml workspace diagnose \
  --name myWorkspace \
  --resource-group myRG

# Delete workspace (use --no-delete-dependent-resources to keep Storage/KV/ACR)
az ml workspace delete \
  --name myWorkspace \
  --resource-group myRG \
  --yes
```

---

## Compute Management

### Compute Clusters (AmlCompute)

```bash
# Create a CPU compute cluster
az ml compute create \
  --type AmlCompute \
  --name cpu-cluster \
  --resource-group myRG \
  --workspace-name myWorkspace \
  --size Standard_DS3_v2 \
  --min-instances 0 \
  --max-instances 4 \
  --idle-time-before-scale-down 120

# Create a GPU cluster (spot/low-priority for cost savings)
az ml compute create \
  --type AmlCompute \
  --name gpu-cluster \
  --resource-group myRG \
  --workspace-name myWorkspace \
  --size Standard_NC6s_v3 \
  --min-instances 0 \
  --max-instances 4 \
  --tier LowPriority

# From YAML definition
az ml compute create \
  --file compute-cluster.yaml \
  --resource-group myRG \
  --workspace-name myWorkspace

# List all compute targets
az ml compute list \
  --resource-group myRG \
  --workspace-name myWorkspace \
  -o table

# Show compute details
az ml compute show \
  --name cpu-cluster \
  --resource-group myRG \
  --workspace-name myWorkspace

# Update cluster max instances
az ml compute update \
  --name cpu-cluster \
  --resource-group myRG \
  --workspace-name myWorkspace \
  --max-instances 8

# Delete compute
az ml compute delete \
  --name cpu-cluster \
  --resource-group myRG \
  --workspace-name myWorkspace \
  --yes
```

### Compute Instances

```bash
# Create a compute instance for interactive development
az ml compute create \
  --type ComputeInstance \
  --name my-dev-instance \
  --resource-group myRG \
  --workspace-name myWorkspace \
  --size Standard_DS3_v2

# Start/stop a compute instance
az ml compute start \
  --name my-dev-instance \
  --resource-group myRG \
  --workspace-name myWorkspace

az ml compute stop \
  --name my-dev-instance \
  --resource-group myRG \
  --workspace-name myWorkspace

# Restart
az ml compute restart \
  --name my-dev-instance \
  --resource-group myRG \
  --workspace-name myWorkspace
```

---

## Jobs

```bash
# Submit a command job from YAML
az ml job create \
  --file job.yaml \
  --resource-group myRG \
  --workspace-name myWorkspace

# Submit and stream logs immediately
az ml job create \
  --file job.yaml \
  --resource-group myRG \
  --workspace-name myWorkspace \
  --stream

# Show job status and details
az ml job show \
  --name <job-name> \
  --resource-group myRG \
  --workspace-name myWorkspace

# List recent jobs (last 20)
az ml job list \
  --resource-group myRG \
  --workspace-name myWorkspace \
  --max-results 20 \
  -o table

# Stream logs from a running job
az ml job stream \
  --name <job-name> \
  --resource-group myRG \
  --workspace-name myWorkspace

# Download job outputs and artifacts
az ml job download \
  --name <job-name> \
  --resource-group myRG \
  --workspace-name myWorkspace \
  --output-name model_output \
  --download-path ./outputs

# Cancel a running job
az ml job cancel \
  --name <job-name> \
  --resource-group myRG \
  --workspace-name myWorkspace

# Submit a pipeline job
az ml job create \
  --file pipeline.yaml \
  --resource-group myRG \
  --workspace-name myWorkspace \
  --stream

# Submit an AutoML job
az ml job create \
  --file automl-job.yaml \
  --resource-group myRG \
  --workspace-name myWorkspace
```

---

## Online Endpoints

```bash
# Create a managed online endpoint
az ml online-endpoint create \
  --file endpoint.yaml \
  --resource-group myRG \
  --workspace-name myWorkspace

# Create a managed online endpoint inline
az ml online-endpoint create \
  --name my-endpoint \
  --resource-group myRG \
  --workspace-name myWorkspace \
  --auth-mode key

# Create a deployment (must specify endpoint)
az ml online-deployment create \
  --file deployment.yaml \
  --resource-group myRG \
  --workspace-name myWorkspace \
  --all-traffic  # route 100% traffic to this deployment

# List endpoints
az ml online-endpoint list \
  --resource-group myRG \
  --workspace-name myWorkspace \
  -o table

# Show endpoint details (scoring URI, auth mode)
az ml online-endpoint show \
  --name my-endpoint \
  --resource-group myRG \
  --workspace-name myWorkspace

# Get endpoint keys
az ml online-endpoint get-credentials \
  --name my-endpoint \
  --resource-group myRG \
  --workspace-name myWorkspace

# Invoke endpoint for testing
az ml online-endpoint invoke \
  --name my-endpoint \
  --resource-group myRG \
  --workspace-name myWorkspace \
  --request-file sample-request.json

# Update traffic split (blue-green: 90% v1, 10% v2)
az ml online-endpoint update \
  --name my-endpoint \
  --resource-group myRG \
  --workspace-name myWorkspace \
  --traffic "blue=90 green=10"

# Scale a deployment
az ml online-deployment update \
  --name blue \
  --endpoint-name my-endpoint \
  --resource-group myRG \
  --workspace-name myWorkspace \
  --instance-count 3

# Show deployment logs
az ml online-deployment get-logs \
  --name blue \
  --endpoint-name my-endpoint \
  --resource-group myRG \
  --workspace-name myWorkspace \
  --lines 100

# Delete deployment
az ml online-deployment delete \
  --name green \
  --endpoint-name my-endpoint \
  --resource-group myRG \
  --workspace-name myWorkspace \
  --yes

# Delete endpoint (and all deployments)
az ml online-endpoint delete \
  --name my-endpoint \
  --resource-group myRG \
  --workspace-name myWorkspace \
  --yes
```

---

## Batch Endpoints

```bash
# Create batch endpoint
az ml batch-endpoint create \
  --file batch-endpoint.yaml \
  --resource-group myRG \
  --workspace-name myWorkspace

# Create batch deployment
az ml batch-deployment create \
  --file batch-deployment.yaml \
  --resource-group myRG \
  --workspace-name myWorkspace

# Invoke batch endpoint (asynchronous)
az ml batch-endpoint invoke \
  --name my-batch-endpoint \
  --resource-group myRG \
  --workspace-name myWorkspace \
  --input azureml:batch-input@latest

# List batch endpoints
az ml batch-endpoint list \
  --resource-group myRG \
  --workspace-name myWorkspace \
  -o table

# Show batch endpoint
az ml batch-endpoint show \
  --name my-batch-endpoint \
  --resource-group myRG \
  --workspace-name myWorkspace

# Delete batch endpoint
az ml batch-endpoint delete \
  --name my-batch-endpoint \
  --resource-group myRG \
  --workspace-name myWorkspace \
  --yes
```

---

## Models

```bash
# Register a model from local path (MLflow format)
az ml model create \
  --name my-classifier \
  --version 1 \
  --path ./model \
  --type mlflow_model \
  --resource-group myRG \
  --workspace-name myWorkspace

# Register a model from a job output
az ml model create \
  --name my-classifier \
  --path azureml://jobs/<job-name>/outputs/artifacts/paths/model/ \
  --type mlflow_model \
  --resource-group myRG \
  --workspace-name myWorkspace

# List models
az ml model list \
  --resource-group myRG \
  --workspace-name myWorkspace \
  -o table

# Show a specific model version
az ml model show \
  --name my-classifier \
  --version 1 \
  --resource-group myRG \
  --workspace-name myWorkspace

# Download model artifacts
az ml model download \
  --name my-classifier \
  --version 1 \
  --download-path ./downloaded-model \
  --resource-group myRG \
  --workspace-name myWorkspace
```

---

## Environments

```bash
# Create a custom environment from YAML
az ml environment create \
  --file custom-env.yaml \
  --resource-group myRG \
  --workspace-name myWorkspace

# List environments (curated + custom)
az ml environment list \
  --resource-group myRG \
  --workspace-name myWorkspace \
  -o table

# Show environment details
az ml environment show \
  --name my-training-env \
  --version 1 \
  --resource-group myRG \
  --workspace-name myWorkspace
```

---

## Data Assets

```bash
# Create a data asset (URI folder pointing to ADLS)
az ml data create \
  --name customer-data \
  --version 1 \
  --type uri_folder \
  --path azureml://datastores/workspaceblobstore/paths/datasets/customers/ \
  --resource-group myRG \
  --workspace-name myWorkspace

# Create from local files (uploads to default datastore)
az ml data create \
  --name my-dataset \
  --version 1 \
  --type uri_folder \
  --path ./local-data/ \
  --resource-group myRG \
  --workspace-name myWorkspace

# List data assets
az ml data list \
  --resource-group myRG \
  --workspace-name myWorkspace \
  -o table

# Show data asset
az ml data show \
  --name customer-data \
  --version 1 \
  --resource-group myRG \
  --workspace-name myWorkspace
```

---

## Components

```bash
# Register a reusable component from YAML
az ml component create \
  --file component.yaml \
  --resource-group myRG \
  --workspace-name myWorkspace

# List registered components
az ml component list \
  --resource-group myRG \
  --workspace-name myWorkspace \
  -o table

# Show component
az ml component show \
  --name prep_data \
  --version 1 \
  --resource-group myRG \
  --workspace-name myWorkspace
```

---

## Datastores

```bash
# List datastores (includes default workspaceblobstore)
az ml datastore list \
  --resource-group myRG \
  --workspace-name myWorkspace \
  -o table

# Register an Azure Blob Storage datastore
az ml datastore create \
  --type AzureBlob \
  --name my-blob-store \
  --account-name mystorageaccount \
  --container-name mycontainer \
  --resource-group myRG \
  --workspace-name myWorkspace

# Register an ADLS Gen2 datastore
az ml datastore create \
  --type AzureDataLakeGen2 \
  --name my-adls-store \
  --account-name myadlsaccount \
  --filesystem myfilesystem \
  --resource-group myRG \
  --workspace-name myWorkspace
```
