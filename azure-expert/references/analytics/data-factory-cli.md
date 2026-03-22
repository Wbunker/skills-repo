# Azure Data Factory — CLI Reference

## Prerequisites

```bash
# ADF commands are built into Azure CLI
az login
az account set --subscription "My Subscription"

# Install ADF extension if commands not available
az extension add -n datafactory
```

---

## Factory Management

```bash
# Create a data factory
az datafactory create \
  --name myDataFactory \
  --resource-group myRG \
  --location eastus

# Create with git configuration (Azure DevOps)
az datafactory create \
  --name myDataFactory \
  --resource-group myRG \
  --location eastus \
  --factory-git-hub-configuration \
    '{"type": "FactoryGitHubConfiguration", "accountName": "myorg", "repositoryName": "my-adf-repo", "collaborationBranch": "main", "rootFolder": "/"}'

# Show factory details
az datafactory show \
  --name myDataFactory \
  --resource-group myRG

# List factories in resource group
az datafactory list \
  --resource-group myRG \
  -o table

# Update factory (e.g., add tags)
az datafactory update \
  --name myDataFactory \
  --resource-group myRG \
  --tags environment=production team=data-engineering

# Configure managed VNet (enable for managed private endpoints)
az datafactory managed-virtual-network create \
  --factory-name myDataFactory \
  --resource-group myRG \
  --managed-virtual-network-name default

# Delete factory
az datafactory delete \
  --name myDataFactory \
  --resource-group myRG \
  --yes
```

---

## Integration Runtimes

```bash
# Create managed Azure IR (auto-resolve region)
az datafactory integration-runtime managed create \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name AutoResolveIR

# Create managed Azure IR pinned to a region
az datafactory integration-runtime managed create \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name EastUSIR \
  --location eastus

# Create managed VNet IR (for private endpoint access)
az datafactory integration-runtime managed create \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name ManagedVNetIR \
  --location eastus \
  --compute-properties '{"dataFlowProperties": {"computeType": "General", "coreCount": 8}}'

# Create self-hosted IR
az datafactory integration-runtime self-hosted create \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name SelfHostedIR

# Get authentication keys for self-hosted IR (to register on VM)
az datafactory integration-runtime list-auth-key \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name SelfHostedIR

# Show IR status
az datafactory integration-runtime get-status \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name SelfHostedIR

# List all IRs
az datafactory integration-runtime list \
  --factory-name myDataFactory \
  --resource-group myRG \
  -o table

# Delete IR
az datafactory integration-runtime delete \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name SelfHostedIR \
  --yes
```

---

## Linked Services

```bash
# Create linked service from JSON file
az datafactory linked-service create \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name MyADLSLinkedService \
  --properties @adls-linked-service.json

# Example ADLS Gen2 linked service JSON (adls-linked-service.json):
cat <<EOF > adls-linked-service.json
{
  "type": "AzureBlobFS",
  "typeProperties": {
    "url": "https://mystorageaccount.dfs.core.windows.net",
    "accountKey": {
      "type": "SecureString",
      "value": "<storage-account-key>"
    }
  },
  "connectVia": {
    "referenceName": "AutoResolveIR",
    "type": "IntegrationRuntimeReference"
  }
}
EOF

# Azure SQL Database linked service with managed identity
cat <<EOF > sql-linked-service.json
{
  "type": "AzureSqlDatabase",
  "typeProperties": {
    "connectionString": "Server=myserver.database.windows.net;Database=mydb;",
    "authenticationType": "ManagedServiceIdentity"
  }
}
EOF

az datafactory linked-service create \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name MySQLLinkedService \
  --properties @sql-linked-service.json

# List linked services
az datafactory linked-service list \
  --factory-name myDataFactory \
  --resource-group myRG \
  -o table

# Show linked service
az datafactory linked-service show \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name MyADLSLinkedService

# Delete linked service
az datafactory linked-service delete \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name MyADLSLinkedService \
  --yes
```

---

## Datasets

```bash
# Create dataset from JSON file
az datafactory dataset create \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name SalesParquetDataset \
  --properties @sales-dataset.json

# Example Parquet dataset JSON:
cat <<EOF > sales-dataset.json
{
  "type": "Parquet",
  "linkedServiceName": {
    "referenceName": "MyADLSLinkedService",
    "type": "LinkedServiceReference"
  },
  "typeProperties": {
    "location": {
      "type": "AzureBlobFSLocation",
      "fileSystem": "data",
      "folderPath": "sales"
    }
  }
}
EOF

# List datasets
az datafactory dataset list \
  --factory-name myDataFactory \
  --resource-group myRG \
  -o table

# Show dataset
az datafactory dataset show \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name SalesParquetDataset

# Delete dataset
az datafactory dataset delete \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name SalesParquetDataset \
  --yes
```

---

## Pipelines

```bash
# Create pipeline from JSON file
az datafactory pipeline create \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name MyETLPipeline \
  --pipeline @pipeline.json

# List pipelines
az datafactory pipeline list \
  --factory-name myDataFactory \
  --resource-group myRG \
  -o table

# Show pipeline
az datafactory pipeline show \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name MyETLPipeline

# Delete pipeline
az datafactory pipeline delete \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name MyETLPipeline \
  --yes
```

---

## Pipeline Runs

```bash
# Trigger a pipeline run (with parameters)
az datafactory pipeline create-run \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name MyETLPipeline \
  --parameters '{"sourceTable": "dbo.Sales", "targetPath": "processed/sales/"}'

# Capture run ID from output
RUN_ID=$(az datafactory pipeline create-run \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name MyETLPipeline \
  --query runId -o tsv)

echo "Pipeline run ID: $RUN_ID"

# Show pipeline run status and details
az datafactory pipeline-run show \
  --factory-name myDataFactory \
  --resource-group myRG \
  --run-id $RUN_ID

# Poll until completed
az datafactory pipeline-run show \
  --factory-name myDataFactory \
  --resource-group myRG \
  --run-id $RUN_ID \
  --query "status" -o tsv
# Returns: Queued | InProgress | Succeeded | Failed | Canceling | Cancelled

# Cancel a running pipeline
az datafactory pipeline-run cancel \
  --factory-name myDataFactory \
  --resource-group myRG \
  --run-id $RUN_ID

# Query pipeline runs (filter by time and status)
az datafactory pipeline-run query-by-factory \
  --factory-name myDataFactory \
  --resource-group myRG \
  --last-updated-after "2024-01-01T00:00:00Z" \
  --last-updated-before "2024-12-31T23:59:59Z" \
  --filters operand=PipelineName operator=Equals values=MyETLPipeline \
  --filters operand=Status operator=Equals values=Failed

# Show activity runs within a pipeline run
az datafactory activity-run query-by-pipeline-run \
  --factory-name myDataFactory \
  --resource-group myRG \
  --run-id $RUN_ID \
  --last-updated-after "2024-01-01T00:00:00Z" \
  --last-updated-before "2024-12-31T23:59:59Z"
```

---

## Triggers

```bash
# Create schedule trigger from JSON file
az datafactory trigger create \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name DailyScheduleTrigger \
  --properties @schedule-trigger.json

# Start trigger (activate scheduling)
az datafactory trigger start \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name DailyScheduleTrigger

# Stop trigger (deactivate without deleting)
az datafactory trigger stop \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name DailyScheduleTrigger

# List triggers
az datafactory trigger list \
  --factory-name myDataFactory \
  --resource-group myRG \
  -o table

# Show trigger details
az datafactory trigger show \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name DailyScheduleTrigger

# Query trigger runs
az datafactory trigger-run query-by-factory \
  --factory-name myDataFactory \
  --resource-group myRG \
  --last-updated-after "2024-01-01T00:00:00Z" \
  --last-updated-before "2024-12-31T23:59:59Z"

# Rerun a tumbling window trigger (for backfill)
az datafactory trigger-run rerun \
  --factory-name myDataFactory \
  --resource-group myRG \
  --trigger-name TumblingWindowTrigger \
  --run-id <trigger-run-id>

# Delete trigger (must stop first)
az datafactory trigger delete \
  --factory-name myDataFactory \
  --resource-group myRG \
  --name DailyScheduleTrigger \
  --yes
```

---

## Managed Private Endpoints

```bash
# Create managed private endpoint to ADLS Gen2 (within managed VNet IR)
az datafactory managed-private-endpoint create \
  --factory-name myDataFactory \
  --managed-virtual-network-name default \
  --resource-group myRG \
  --name my-adls-mpe \
  --group-id dfs \
  --private-link-resource-id /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{account}

# Create managed private endpoint to Azure SQL
az datafactory managed-private-endpoint create \
  --factory-name myDataFactory \
  --managed-virtual-network-name default \
  --resource-group myRG \
  --name my-sql-mpe \
  --group-id sqlServer \
  --private-link-resource-id /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Sql/servers/{server}

# List managed private endpoints
az datafactory managed-private-endpoint list \
  --factory-name myDataFactory \
  --managed-virtual-network-name default \
  --resource-group myRG \
  -o table

# Show status (check if approved by resource owner)
az datafactory managed-private-endpoint show \
  --factory-name myDataFactory \
  --managed-virtual-network-name default \
  --resource-group myRG \
  --name my-adls-mpe
```

---

## Diagnostic Settings (Monitoring)

```bash
# Enable diagnostic logs to Log Analytics
FACTORY_ID=$(az datafactory show --name myDataFactory --resource-group myRG --query id -o tsv)
WORKSPACE_ID=$(az monitor log-analytics workspace show --name myLogWorkspace --resource-group myRG --query id -o tsv)

az monitor diagnostic-settings create \
  --name adf-diagnostics \
  --resource $FACTORY_ID \
  --workspace $WORKSPACE_ID \
  --logs '[
    {"category": "PipelineRuns", "enabled": true},
    {"category": "ActivityRuns", "enabled": true},
    {"category": "TriggerRuns", "enabled": true}
  ]' \
  --metrics '[{"category": "AllMetrics", "enabled": true}]'
```
