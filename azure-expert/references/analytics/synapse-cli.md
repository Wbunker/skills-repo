# Azure Synapse Analytics — CLI Reference

## Prerequisites

```bash
# Install Synapse extension (included in base Azure CLI 2.x+)
az extension add -n synapse  # if not already available
az extension update -n synapse

az login
az account set --subscription "My Subscription"
```

---

## Workspace Management

```bash
# Create a Synapse workspace (requires ADLS Gen2 with hierarchical namespace)
# First create the storage account
az storage account create \
  --name mysynapsestorage \
  --resource-group myRG \
  --location eastus \
  --sku Standard_LRS \
  --kind StorageV2 \
  --enable-hierarchical-namespace true

# Create filesystem on ADLS Gen2
az storage fs create \
  --account-name mysynapsestorage \
  --name synapsefs

# Create the Synapse workspace
az synapse workspace create \
  --name mysynapsews \
  --resource-group myRG \
  --location eastus \
  --storage-account mysynapsestorage \
  --file-system synapsefs \
  --sql-admin-login-user sqladmin \
  --sql-admin-login-password "P@ssw0rd123!"

# Enable managed VNet (must be done at creation time)
az synapse workspace create \
  --name mysynapsews \
  --resource-group myRG \
  --location eastus \
  --storage-account mysynapsestorage \
  --file-system synapsefs \
  --sql-admin-login-user sqladmin \
  --sql-admin-login-password "P@ssw0rd123!" \
  --enable-managed-virtual-network true \
  --prevent-data-exfiltration true

# Show workspace details (Synapse Studio URL, SQL endpoint)
az synapse workspace show \
  --name mysynapsews \
  --resource-group myRG

# Get Synapse Studio URL
az synapse workspace show \
  --name mysynapsews \
  --resource-group myRG \
  --query "connectivityEndpoints.web" -o tsv

# List workspaces in resource group
az synapse workspace list \
  --resource-group myRG \
  -o table

# Update workspace (add tags, change SQL admin password)
az synapse workspace update \
  --name mysynapsews \
  --resource-group myRG \
  --tags environment=production

# Delete workspace
az synapse workspace delete \
  --name mysynapsews \
  --resource-group myRG \
  --yes
```

---

## Firewall Rules

```bash
# Allow all Azure services (for development)
az synapse workspace firewall-rule create \
  --workspace-name mysynapsews \
  --resource-group myRG \
  --name AllowAllAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Allow specific IP range (corporate office)
az synapse workspace firewall-rule create \
  --workspace-name mysynapsews \
  --resource-group myRG \
  --name CorporateOffice \
  --start-ip-address 203.0.113.0 \
  --end-ip-address 203.0.113.255

# List firewall rules
az synapse workspace firewall-rule list \
  --workspace-name mysynapsews \
  --resource-group myRG \
  -o table

# Delete rule
az synapse workspace firewall-rule delete \
  --workspace-name mysynapsews \
  --resource-group myRG \
  --name AllowAllAzureServices
```

---

## Dedicated SQL Pools

```bash
# Create a dedicated SQL pool
az synapse sql pool create \
  --name MySQLPool \
  --workspace-name mysynapsews \
  --resource-group myRG \
  --performance-level DW500c

# Show SQL pool details
az synapse sql pool show \
  --name MySQLPool \
  --workspace-name mysynapsews \
  --resource-group myRG

# List SQL pools in workspace
az synapse sql pool list \
  --workspace-name mysynapsews \
  --resource-group myRG \
  -o table

# Pause a SQL pool (stop compute charges)
az synapse sql pool pause \
  --name MySQLPool \
  --workspace-name mysynapsews \
  --resource-group myRG

# Resume a SQL pool
az synapse sql pool resume \
  --name MySQLPool \
  --workspace-name mysynapsews \
  --resource-group myRG

# Scale SQL pool (change DWU)
az synapse sql pool update \
  --name MySQLPool \
  --workspace-name mysynapsews \
  --resource-group myRG \
  --performance-level DW1000c

# Delete SQL pool
az synapse sql pool delete \
  --name MySQLPool \
  --workspace-name mysynapsews \
  --resource-group myRG \
  --yes
```

### SQL Pool Restore Points

```bash
# Create manual restore point
az synapse sql pool restore-point create \
  --restore-point-label "BeforeMigration" \
  --sql-pool-name MySQLPool \
  --workspace-name mysynapsews \
  --resource-group myRG

# List restore points
az synapse sql pool restore-point list \
  --sql-pool-name MySQLPool \
  --workspace-name mysynapsews \
  --resource-group myRG \
  -o table
```

---

## Serverless SQL Pool

The serverless SQL pool is always available — no provisioning needed. Query via SSMS, Azure Data Studio, or Synapse Studio using the serverless endpoint.

```bash
# Get serverless SQL endpoint
az synapse workspace show \
  --name mysynapsews \
  --resource-group myRG \
  --query "connectivityEndpoints.sqlOnDemand" -o tsv
# Returns: mysynapsews-ondemand.sql.azuresynapse.net
```

---

## Spark Pools

```bash
# Create a Spark pool
az synapse spark pool create \
  --name mySparkPool \
  --workspace-name mysynapsews \
  --resource-group myRG \
  --spark-version 3.3 \
  --node-count 5 \
  --node-size Medium

# Create with auto-scale and auto-pause
az synapse spark pool create \
  --name mySparkPool \
  --workspace-name mysynapsews \
  --resource-group myRG \
  --spark-version 3.3 \
  --node-size Medium \
  --enable-auto-scale true \
  --min-node-count 3 \
  --max-node-count 20 \
  --enable-auto-pause true \
  --delay 15

# Show Spark pool
az synapse spark pool show \
  --name mySparkPool \
  --workspace-name mysynapsews \
  --resource-group myRG

# List Spark pools
az synapse spark pool list \
  --workspace-name mysynapsews \
  --resource-group myRG \
  -o table

# Update Spark pool (change node count or size)
az synapse spark pool update \
  --name mySparkPool \
  --workspace-name mysynapsews \
  --resource-group myRG \
  --node-count 10

# Delete Spark pool
az synapse spark pool delete \
  --name mySparkPool \
  --workspace-name mysynapsews \
  --resource-group myRG \
  --yes
```

### Spark Sessions and Jobs

```bash
# Create interactive Spark session
az synapse spark session create \
  --name mysession \
  --workspace-name mysynapsews \
  --spark-pool-name mySparkPool \
  --executor-count 2 \
  --executor-size Small

# List active Spark sessions
az synapse spark session list \
  --workspace-name mysynapsews \
  --spark-pool-name mySparkPool

# Cancel session
az synapse spark session cancel \
  --session-id <session-id> \
  --workspace-name mysynapsews \
  --spark-pool-name mySparkPool

# Submit a Spark batch job
az synapse spark job submit \
  --name my-batch-job \
  --workspace-name mysynapsews \
  --spark-pool-name mySparkPool \
  --main-definition-file abfss://myfs@mystorageaccount.dfs.core.windows.net/scripts/job.py \
  --executor-count 4 \
  --executor-size Medium \
  --arguments "--input abfss://..." "--output abfss://..."

# List batch jobs
az synapse spark job list \
  --workspace-name mysynapsews \
  --spark-pool-name mySparkPool

# Show job details
az synapse spark job show \
  --livy-id <job-id> \
  --workspace-name mysynapsews \
  --spark-pool-name mySparkPool
```

---

## Pipelines and Integration

```bash
# Create pipeline from JSON definition
az synapse pipeline create \
  --name my-etl-pipeline \
  --workspace-name mysynapsews \
  --file @pipeline-definition.json

# Run pipeline
az synapse pipeline create-run \
  --name my-etl-pipeline \
  --workspace-name mysynapsews

# Run with parameters
az synapse pipeline create-run \
  --name my-etl-pipeline \
  --workspace-name mysynapsews \
  --parameters '{"sourcePath": "raw/2024/", "targetPath": "processed/2024/"}'

# Show pipeline run status
az synapse pipeline-run show \
  --run-id <run-id> \
  --workspace-name mysynapsews

# Cancel pipeline run
az synapse pipeline-run cancel \
  --run-id <run-id> \
  --workspace-name mysynapsews

# List recent pipeline runs
az synapse pipeline-run query-by-workspace \
  --workspace-name mysynapsews \
  --last-updated-after "2024-01-01T00:00:00Z" \
  --last-updated-before "2024-12-31T23:59:59Z"

# Create trigger
az synapse trigger create \
  --name my-schedule-trigger \
  --workspace-name mysynapsews \
  --file @trigger-definition.json

# Start/stop trigger
az synapse trigger start \
  --name my-schedule-trigger \
  --workspace-name mysynapsews

az synapse trigger stop \
  --name my-schedule-trigger \
  --workspace-name mysynapsews

# Create linked service (connection to data source)
az synapse linked-service create \
  --name MyADLSLinkedService \
  --workspace-name mysynapsews \
  --file @linked-service.json

# Create dataset
az synapse dataset create \
  --name MySalesDataset \
  --workspace-name mysynapsews \
  --file @dataset.json
```

---

## Role Assignment

```bash
# Assign Synapse Administrator role
az synapse role assignment create \
  --workspace-name mysynapsews \
  --role "Synapse Administrator" \
  --assignee user@example.com

# Assign Synapse Contributor (can create artifacts but not manage compute)
az synapse role assignment create \
  --workspace-name mysynapsews \
  --role "Synapse Contributor" \
  --assignee <object-id>

# List role assignments
az synapse role assignment list \
  --workspace-name mysynapsews \
  -o table

# Delete role assignment
az synapse role assignment delete \
  --workspace-name mysynapsews \
  --ids <assignment-id>
```

---

## Managed Private Endpoints

```bash
# Create managed private endpoint to ADLS Gen2
az synapse managed-private-endpoint create \
  --workspace-name mysynapsews \
  --pe-name my-adls-pe \
  --resource-id /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{account} \
  --group-id dfs

# List managed private endpoints
az synapse managed-private-endpoint list \
  --workspace-name mysynapsews \
  -o table

# Show approval status (storage account owner must approve)
az synapse managed-private-endpoint show \
  --workspace-name mysynapsews \
  --pe-name my-adls-pe
```
