# Database Migration Service — CLI Reference
For service concepts, see [dms-capabilities.md](dms-capabilities.md).

## DMS Instance Management

```bash
# --- Create DMS Instance ---
az dms create \
  --resource-group myRG \
  --name myDMS \
  --location eastus \
  --sku-name Premium_4vCores \
  --subnet /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.Network/virtualNetworks/myVNet/subnets/dms-subnet  # Create Premium DMS instance (online migrations)

az dms create \
  --resource-group myRG \
  --name myDMSStandard \
  --location eastus \
  --sku-name Standard_4vCores \
  --subnet /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.Network/virtualNetworks/myVNet/subnets/dms-subnet  # Create Standard DMS (offline only)

az dms list --resource-group myRG              # List DMS instances
az dms show --resource-group myRG --name myDMS  # Show DMS instance details

az dms check-status \
  --resource-group myRG \
  --name myDMS                                 # Check DMS service health/status

az dms delete \
  --resource-group myRG \
  --name myDMS --yes                           # Delete DMS instance

# --- List Supported SKUs ---
az dms list-skus                               # Show available SKU options by region
```

## Migration Projects

```bash
# --- Project Creation ---
# Create project for SQL Server → SQL Managed Instance migration
az dms project create \
  --resource-group myRG \
  --service-name myDMS \
  --name sql-to-sqlmi-project \
  --source-platform SQL \
  --target-platform SQLMI \
  --location eastus

# Create project for MySQL → Azure DB for MySQL
az dms project create \
  --resource-group myRG \
  --service-name myDMS \
  --name mysql-migration-project \
  --source-platform MySQL \
  --target-platform AzureDbForMySQL \
  --location eastus

# Create project for PostgreSQL → Azure DB for PostgreSQL
az dms project create \
  --resource-group myRG \
  --service-name myDMS \
  --name pg-migration-project \
  --source-platform PostgreSQL \
  --target-platform AzureDbForPostgreSQL \
  --location eastus

# Create project for MongoDB → Cosmos DB
az dms project create \
  --resource-group myRG \
  --service-name myDMS \
  --name mongo-to-cosmos-project \
  --source-platform MongoDb \
  --target-platform MongoDb \
  --location eastus

az dms project list \
  --resource-group myRG \
  --service-name myDMS                         # List projects in a DMS instance

az dms project show \
  --resource-group myRG \
  --service-name myDMS \
  --name sql-to-sqlmi-project                  # Show project details

az dms project delete \
  --resource-group myRG \
  --service-name myDMS \
  --name sql-to-sqlmi-project --yes            # Delete project and its tasks
```

## Migration Tasks

```bash
# --- SQL to SQL MI Offline Migration Task ---
az dms project task create \
  --resource-group myRG \
  --service-name myDMS \
  --project-name sql-to-sqlmi-project \
  --name migrate-adventureworks \
  --task-type MigrateSqlServerSqlMI \
  --source-connection-json @source-connection.json \
  --target-connection-json @target-connection.json \
  --selected-databases @databases.json \
  --backup-blob-sas-uri "https://mystorageacct.blob.core.windows.net/backups?sv=...&sp=rwl..."

# --- SQL to SQL MI Online Migration Task ---
az dms project task create \
  --resource-group myRG \
  --service-name myDMS \
  --project-name sql-to-sqlmi-project \
  --name migrate-online \
  --task-type MigrateSqlServerSqlMISync \
  --source-connection-json @source-connection.json \
  --target-connection-json @target-connection.json \
  --selected-databases @databases.json \
  --backup-blob-sas-uri "https://mystorageacct.blob.core.windows.net/backups?sv=...&sp=rwl..."

# --- MySQL Online Migration Task ---
az dms project task create \
  --resource-group myRG \
  --service-name myDMS \
  --project-name mysql-migration-project \
  --name migrate-mysql-db \
  --task-type MigrateMySqlAzureDbForMySqlSync \
  --source-connection-json '{"serverName": "source-mysql.company.com", "port": 3306, "userName": "migration_user", "password": "...", "authentication": "SqlAuthentication"}' \
  --target-connection-json '{"serverName": "target.mysql.database.azure.com", "port": 3306, "userName": "migration_user@target", "password": "...", "authentication": "SqlAuthentication"}' \
  --selected-databases @mysql-databases.json

# --- Task Management ---
az dms project task list \
  --resource-group myRG \
  --service-name myDMS \
  --project-name sql-to-sqlmi-project          # List all tasks in a project

az dms project task show \
  --resource-group myRG \
  --service-name myDMS \
  --project-name sql-to-sqlmi-project \
  --name migrate-adventureworks                # Show task status and progress

az dms project task show \
  --resource-group myRG \
  --service-name myDMS \
  --project-name sql-to-sqlmi-project \
  --name migrate-adventureworks \
  --expand output                              # Show detailed migration output including errors

az dms project task cancel \
  --resource-group myRG \
  --service-name myDMS \
  --project-name sql-to-sqlmi-project \
  --name migrate-adventureworks               # Cancel a running migration task

az dms project task delete \
  --resource-group myRG \
  --service-name myDMS \
  --project-name sql-to-sqlmi-project \
  --name migrate-adventureworks --yes          # Delete a task
```

## Connection JSON File Formats

```bash
# --- Source Connection (SQL Server) ---
cat source-connection.json
# {
#   "userName": "migration_user",
#   "password": "StrongPassword123!",
#   "dataSource": "source-sqlserver.company.com",
#   "authentication": "SqlAuthentication",
#   "encryptConnection": true,
#   "trustServerCertificate": true
# }

# --- Target Connection (SQL Managed Instance) ---
cat target-connection.json
# {
#   "userName": "migration_user",
#   "password": "StrongPassword123!",
#   "dataSource": "my-sqlmi.public.database.windows.net,3342",
#   "authentication": "SqlAuthentication",
#   "encryptConnection": true,
#   "trustServerCertificate": false
# }

# --- Selected Databases ---
cat databases.json
# [
#   {
#     "name": "AdventureWorks",
#     "restoreDatabaseName": "AdventureWorks",
#     "backupFileShare": {"path": "\\\\source-server\\backup", "userName": "...", "password": "..."},
#     "selectedTables": []
#   }
# ]
```

## Database Assessment (Azure CLI + PowerShell)

```bash
# Run database assessment via Az.DataMigration PowerShell module
Install-Module Az.DataMigration -Force

# Collect performance data from source SQL Server (run on source server)
Get-AzDataMigrationPerformanceDataCollection `
  -SqlConnectionString "Server=source;Database=master;User Id=sa;Password=..." `
  -OutputFolder "C:\PerfData" `
  -PerfQueryInterval 30 `
  -NumberOfIterations 20

# Get SKU recommendations from collected data
Get-AzDataMigrationSkuRecommendation `
  -PerfQueryResultsDirectory "C:\PerfData" `
  -OutputFolder "C:\SkuRecommendations" `
  -Overwrite

# Run assessment
Invoke-AzDataMigrationGetAssessment `
  -SqlConnectionString "Server=source;Database=master;User Id=sa;Password=..." \
  -OutputFolder "C:\Assessment" \
  -Overwrite
```
