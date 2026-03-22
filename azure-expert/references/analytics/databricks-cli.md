# Azure Databricks — CLI Reference

## Prerequisites

```bash
# Azure CLI for workspace provisioning
az login
az account set --subscription "My Subscription"

# Databricks CLI v2 (install)
pip install databricks-cli  # legacy v1, avoid
# OR
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
# Installs databricks CLI v2 (Go-based, recommended)

# Configure Databricks CLI for a workspace
databricks configure --host https://adb-<workspace-id>.<region>.azuredatabricks.net

# Configure with service principal (for CI/CD)
export DATABRICKS_HOST=https://adb-<workspace-id>.<region>.azuredatabricks.net
export DATABRICKS_TOKEN=<personal-access-token-or-sp-token>

# Or use Azure CLI auth (recommended for developers)
databricks auth login --host https://adb-<workspace-id>.<region>.azuredatabricks.net \
  --configure-cluster  # stores in ~/.databrickscfg

# Verify authentication
databricks auth env
databricks current-user me
```

---

## Workspace Provisioning (Azure CLI)

```bash
# Create Azure Databricks workspace (Standard tier)
az databricks workspace create \
  --name myDatabricks \
  --resource-group myRG \
  --location eastus \
  --sku standard

# Create Premium tier workspace (required for Unity Catalog, ACLs)
az databricks workspace create \
  --name myDatabricks \
  --resource-group myRG \
  --location eastus \
  --sku premium

# Create with managed VNet (no-public-IP / private workspace)
az databricks workspace create \
  --name myDatabricks \
  --resource-group myRG \
  --location eastus \
  --sku premium \
  --enable-no-public-ip true \
  --custom-virtual-network-id /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Network/virtualNetworks/{vnet} \
  --public-subnet-name databricks-public \
  --private-subnet-name databricks-private

# Show workspace (get workspace URL)
az databricks workspace show \
  --name myDatabricks \
  --resource-group myRG \
  --query "workspaceUrl" -o tsv

# List workspaces
az databricks workspace list \
  --resource-group myRG \
  -o table

# Update workspace (add tags)
az databricks workspace update \
  --name myDatabricks \
  --resource-group myRG \
  --tags environment=production team=data-engineering

# Delete workspace
az databricks workspace delete \
  --name myDatabricks \
  --resource-group myRG \
  --yes
```

---

## Clusters

```bash
# List clusters
databricks clusters list
databricks clusters list --output json

# Get cluster details
databricks clusters get --cluster-id <cluster-id>

# Create a cluster from JSON spec
databricks clusters create --json '{
  "cluster_name": "dev-cluster",
  "spark_version": "14.3.x-scala2.12",
  "node_type_id": "Standard_DS3_v2",
  "autoscale": {"min_workers": 2, "max_workers": 8},
  "autotermination_minutes": 60,
  "azure_attributes": {
    "availability": "ON_DEMAND_AZURE"
  }
}'

# Create from JSON file
databricks clusters create --json @cluster-spec.json

# Start a stopped cluster
databricks clusters start --cluster-id <cluster-id>

# Restart a running cluster
databricks clusters restart --cluster-id <cluster-id>

# Terminate (stop) a cluster
databricks clusters delete --cluster-id <cluster-id>

# Pin cluster (prevent auto-deletion after 30 days of inactivity)
databricks clusters pin --cluster-id <cluster-id>

# Unpin cluster
databricks clusters unpin --cluster-id <cluster-id>

# List Spark versions available
databricks clusters spark-versions

# List available node types (VM sizes)
databricks clusters list-node-types

# Get cluster events (errors, resizes, etc.)
databricks clusters events --cluster-id <cluster-id>
```

---

## Jobs and Workflows

```bash
# List jobs
databricks jobs list
databricks jobs list --output json

# Create a job from JSON spec
databricks jobs create --json @job-spec.json

# Create a simple notebook job inline
databricks jobs create --json '{
  "name": "Daily ETL",
  "tasks": [{
    "task_key": "etl_notebook",
    "notebook_task": {
      "notebook_path": "/Repos/main/notebooks/etl"
    },
    "new_cluster": {
      "spark_version": "14.3.x-scala2.12",
      "node_type_id": "Standard_DS3_v2",
      "num_workers": 4
    }
  }],
  "schedule": {
    "quartz_cron_expression": "0 0 2 * * ?",
    "timezone_id": "UTC",
    "pause_status": "UNPAUSED"
  }
}'

# Get job details
databricks jobs get --job-id <job-id>

# Update a job (replace entire spec)
databricks jobs update --job-id <job-id> --json @updated-job-spec.json

# Run a job now (one-time manual trigger)
databricks jobs run-now --job-id <job-id>

# Run with parameter overrides
databricks jobs run-now --job-id <job-id> \
  --job-parameters '{"date": "2024-01-15", "env": "prod"}'

# List job runs
databricks jobs list-runs --job-id <job-id>
databricks jobs list-runs --job-id <job-id> --limit 10

# Get run details (status, task results)
databricks runs get --run-id <run-id>

# Get run output (for Python/notebook tasks)
databricks runs get-output --run-id <run-id>

# Cancel a running job
databricks runs cancel --run-id <run-id>

# Delete a job
databricks jobs delete --job-id <job-id>
```

---

## Databricks Asset Bundles (CI/CD)

```bash
# Initialize a new bundle from a template
databricks bundle init

# Initialize with a specific template
databricks bundle init --template default-python

# Validate bundle configuration
databricks bundle validate

# Deploy bundle to a target environment
databricks bundle deploy --target dev

# Deploy to production
databricks bundle deploy --target prod

# Run a resource defined in the bundle
databricks bundle run --target dev my_job

# Run with parameter overrides
databricks bundle run --target dev my_job \
  --python-params '["--date", "2024-01-15"]'

# Show bundle status (deployed resources)
databricks bundle summary --target prod

# Destroy all resources deployed by bundle
databricks bundle destroy --target dev --auto-approve

# Generate bundle configuration from existing workspace resources
databricks bundle generate job --existing-job-id <job-id>
```

---

## DBFS and Files

```bash
# List files in DBFS
databricks fs ls dbfs:/

# List Unity Catalog volume
databricks fs ls dbfs:/mnt/myvolume/

# Copy local file to DBFS
databricks fs cp ./local-file.csv dbfs:/tmp/local-file.csv

# Copy from DBFS to local
databricks fs cp dbfs:/tmp/output.csv ./output.csv

# Recursive copy (directory)
databricks fs cp --recursive ./local-dir/ dbfs:/tmp/my-dir/

# Make directory
databricks fs mkdir dbfs:/tmp/my-dir

# Remove file
databricks fs rm dbfs:/tmp/old-file.csv

# Remove directory recursively
databricks fs rm --recursive dbfs:/tmp/old-dir/
```

---

## Unity Catalog

```bash
# List catalogs
databricks unity-catalog catalogs list

# Create catalog
databricks unity-catalog catalogs create --name my_catalog

# List schemas in catalog
databricks unity-catalog schemas list --catalog-name my_catalog

# Create schema
databricks unity-catalog schemas create --catalog-name my_catalog --name sales

# List tables in schema
databricks unity-catalog tables list --catalog-name my_catalog --schema-name sales

# Get table details
databricks unity-catalog tables get --full-name my_catalog.sales.transactions

# List external locations
databricks unity-catalog external-locations list

# Create external location (link to ADLS Gen2 path)
databricks unity-catalog external-locations create \
  --name my-adls-location \
  --url abfss://mycontainer@mystorageaccount.dfs.core.windows.net/data \
  --credential-name my-azure-credential

# List storage credentials
databricks unity-catalog storage-credentials list
```

---

## Secrets

```bash
# Create a secret scope (Databricks-backed)
databricks secrets create-scope --scope my-scope

# Create a Key Vault-backed secret scope (recommended for Azure)
databricks secrets create-scope \
  --scope my-kv-scope \
  --scope-backend-type AZURE_KEYVAULT \
  --resource-id /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.KeyVault/vaults/{vault} \
  --dns-name https://myvault.vault.azure.net/

# List secret scopes
databricks secrets list-scopes

# Put a secret in a Databricks-backed scope
databricks secrets put-secret --scope my-scope --key db-password --string-value "mypassword"

# List secrets in scope (shows keys only, not values)
databricks secrets list-secrets --scope my-scope

# Delete a secret
databricks secrets delete-secret --scope my-scope --key db-password

# Delete a scope
databricks secrets delete-scope --scope my-scope

# Use secrets in notebooks:
# dbutils.secrets.get(scope="my-scope", key="db-password")
```

---

## SQL Warehouses

```bash
# List SQL warehouses
databricks sql warehouses list

# Create a serverless SQL warehouse
databricks sql warehouses create --json '{
  "name": "prod-sql-warehouse",
  "cluster_size": "Medium",
  "warehouse_type": "PRO",
  "enable_serverless_compute": true,
  "auto_stop_mins": 10,
  "min_num_clusters": 1,
  "max_num_clusters": 3
}'

# Get warehouse details
databricks sql warehouses get --id <warehouse-id>

# Start warehouse
databricks sql warehouses start --id <warehouse-id>

# Stop warehouse
databricks sql warehouses stop --id <warehouse-id>

# Delete warehouse
databricks sql warehouses delete --id <warehouse-id>
```

---

## Notebooks

```bash
# Export a notebook to local file (all formats: SOURCE, HTML, JUPYTER, DBC)
databricks workspace export-dir \
  --source-path /Repos/main/notebooks \
  --target-path ./exported-notebooks \
  --format SOURCE

# Export single notebook
databricks workspace export \
  /Repos/main/notebooks/etl.py \
  --format SOURCE > etl.py

# Import notebook from local file
databricks workspace import \
  ./etl.py \
  --path /Repos/main/notebooks/etl.py \
  --format SOURCE \
  --overwrite

# List workspace directory contents
databricks workspace list /Repos

# Create directory
databricks workspace mkdirs /my-notebooks/project-a

# Delete notebook or directory
databricks workspace delete /old-notebooks --recursive
```

---

## Repos (Git Integration)

```bash
# List repos in workspace
databricks repos list

# Create a repo (link to remote Git repo)
databricks repos create \
  --url https://github.com/myorg/my-databricks-repo.git \
  --provider gitHub \
  --path /Repos/myuser/my-databricks-repo

# Update repo (pull from remote branch)
databricks repos update \
  --repo-id <repo-id> \
  --branch main

# Delete repo
databricks repos delete --repo-id <repo-id>
```
