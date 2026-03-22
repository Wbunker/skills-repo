# NoSQL & Specialized Databases — CLI Reference
For service concepts, see [nosql-specialized-capabilities.md](nosql-specialized-capabilities.md).

## Azure Table Storage

```bash
# Note: Table Storage is part of Azure Storage accounts.
# Set storage account credentials first:
export AZURE_STORAGE_ACCOUNT=mystorageaccount
export AZURE_STORAGE_KEY=$(az storage account keys list \
  --account-name mystorageaccount --resource-group myRG \
  --query '[0].value' --output tsv)

# --- Create Table ---
az storage table create \
  --name mytable \
  --account-name mystorageaccount \
  --auth-mode login                 # login (Entra ID) | key

az storage table create \
  --name mytable \
  --account-name mystorageaccount

# --- List Tables ---
az storage table list \
  --account-name mystorageaccount \
  --output table

# --- Show Table Stats ---
az storage table stats \
  --account-name mystorageaccount

# --- Delete Table ---
az storage table delete \
  --name mytable \
  --account-name mystorageaccount --yes

# ============================================================
# ENTITY OPERATIONS
# ============================================================

# --- Insert Entity ---
az storage entity insert \
  --account-name mystorageaccount \
  --table-name mytable \
  --entity \
    PartitionKey=devices \
    RowKey=device-001 \
    DeviceType=sensor \
    Location=Building-A \
    Temperature@odata.type=Edm.Double \
    Temperature=23.5 \
    Timestamp@odata.type=Edm.DateTime \
    Timestamp=2024-01-15T10:30:00Z

# --- Insert or Merge (upsert) ---
az storage entity merge \
  --account-name mystorageaccount \
  --table-name mytable \
  --entity \
    PartitionKey=devices \
    RowKey=device-001 \
    Temperature@odata.type=Edm.Double \
    Temperature=24.1

# --- Insert or Replace ---
az storage entity replace \
  --account-name mystorageaccount \
  --table-name mytable \
  --entity \
    PartitionKey=devices \
    RowKey=device-001 \
    DeviceType=sensor \
    Location=Building-B \
    Temperature@odata.type=Edm.Double \
    Temperature=22.0

# --- Show Entity (point lookup) ---
az storage entity show \
  --account-name mystorageaccount \
  --table-name mytable \
  --partition-key devices \
  --row-key device-001

# --- Query Entities ---
# Query all entities in partition
az storage entity query \
  --account-name mystorageaccount \
  --table-name mytable \
  --filter "PartitionKey eq 'devices'" \
  --output table

# Query with multiple conditions
az storage entity query \
  --account-name mystorageaccount \
  --table-name mytable \
  --filter "PartitionKey eq 'devices' and DeviceType eq 'sensor'" \
  --select "RowKey,Location,Temperature" \
  --output table

# Query with row key range (efficient; within partition)
az storage entity query \
  --account-name mystorageaccount \
  --table-name mytable \
  --filter "PartitionKey eq 'logs' and RowKey ge '2024-01-01' and RowKey lt '2024-02-01'" \
  --output json

# --- Delete Entity ---
az storage entity delete \
  --account-name mystorageaccount \
  --table-name mytable \
  --partition-key devices \
  --row-key device-001

# ============================================================
# TABLE STORAGE SAS
# ============================================================

# Generate SAS for table (read + query; expires in 24 hours)
az storage table generate-sas \
  --account-name mystorageaccount \
  --name mytable \
  --permissions rq \                # r=read, q=query, a=add, u=update, d=delete
  --expiry 2025-01-16T00:00:00Z \
  --https-only \
  --output tsv
```

---

## Azure Database Migration Service (DMS)

```bash
# --- Register DMS Provider ---
az provider register --namespace Microsoft.DataMigration

# --- Create DMS Instance ---
az dms create \
  --name myDMSService \
  --resource-group myRG \
  --location eastus \
  --sku-name Premium_4vCores \      # GeneralPurpose_4vCores | Premium_4vCores (Premium required for online)
  --subnet /subscriptions/<sub>/resourceGroups/myRG/providers/Microsoft.Network/virtualNetworks/myVNet/subnets/dmsSubnet

# --- List DMS Instances ---
az dms list \
  --resource-group myRG \
  --output table

# --- Show DMS Instance ---
az dms show \
  --name myDMSService \
  --resource-group myRG

# --- Check DMS Instance Status ---
az dms check-status \
  --name myDMSService \
  --resource-group myRG

# ============================================================
# DMS PROJECT (SQL Server → Azure SQL MI example)
# ============================================================

# --- Create Migration Project ---
az dms project create \
  --name mySQLMigration \
  --service-name myDMSService \
  --resource-group myRG \
  --location eastus \
  --source-platform SQL \           # SQL | MySQL | PostgreSQL | MongoDb | Oracle
  --target-platform SQLMI           # SqlDb | SQLMI | MySQL | AzureDbForPostgreSql | MongoDb

# --- List Projects ---
az dms project list \
  --service-name myDMSService \
  --resource-group myRG \
  --output table

# --- Show Project ---
az dms project show \
  --name mySQLMigration \
  --service-name myDMSService \
  --resource-group myRG

# --- Create Migration Task (Online - SQL Server to SQL MI) ---
# Task configuration JSON defines source/target connection and database list
az dms project task create \
  --task-name myMigrationTask \
  --project-name mySQLMigration \
  --service-name myDMSService \
  --resource-group myRG \
  --task-type MigrateSqlServerSqlMiOnline \  # Task type determines migration mode
  --task-parameters @migration-task.json

# --- List Tasks ---
az dms project task list \
  --project-name mySQLMigration \
  --service-name myDMSService \
  --resource-group myRG \
  --output table

# --- Show Task Status and Progress ---
az dms project task show \
  --task-name myMigrationTask \
  --project-name mySQLMigration \
  --service-name myDMSService \
  --resource-group myRG \
  --expand output                   # Show detailed output including errors

# --- Cancel Task ---
az dms project task cancel \
  --task-name myMigrationTask \
  --project-name mySQLMigration \
  --service-name myDMSService \
  --resource-group myRG

# --- Delete Task ---
az dms project task delete \
  --task-name myMigrationTask \
  --project-name mySQLMigration \
  --service-name myDMSService \
  --resource-group myRG --yes

# --- Delete Project ---
az dms project delete \
  --name mySQLMigration \
  --service-name myDMSService \
  --resource-group myRG \
  --delete-running-tasks true --yes

# --- Delete DMS Instance ---
az dms delete \
  --name myDMSService \
  --resource-group myRG --yes
```

---

## Azure SQL Edge (IoT/Edge Deployment)

```bash
# Note: Azure SQL Edge is deployed as a container (Docker / IoT Edge)
# CLI operations are typically via IoT Hub or Docker; minimal Azure CLI surface

# --- Deploy via IoT Edge (assuming IoT Hub exists) ---
# Create IoT Edge device
az iot hub device-identity create \
  --hub-name myIoTHub \
  --device-id myEdgeDevice \
  --edge-enabled

# Get connection string for device
az iot hub device-identity connection-string show \
  --hub-name myIoTHub \
  --device-id myEdgeDevice \
  --output tsv

# Apply IoT Edge deployment manifest (includes SQL Edge module)
az iot edge set-modules \
  --hub-name myIoTHub \
  --device-id myEdgeDevice \
  --content @deployment.manifest.json

# Sample SQL Edge module spec in deployment.manifest.json:
# {
#   "AzureSQLEdge": {
#     "type": "docker",
#     "settings": {
#       "image": "mcr.microsoft.com/azure-sql-edge",
#       "createOptions": "{\"HostConfig\":{\"CapAdd\":[\"SYS_PTRACE\"],\"Binds\":[\"sqlvolume:/var/opt/mssql\"],\"PortBindings\":{\"1433/tcp\":[{\"HostPort\":\"1433\"}]}}}"
#     },
#     "env": {
#       "ACCEPT_EULA": {"value": "Y"},
#       "MSSQL_SA_PASSWORD": {"value": "<your-password>"},
#       "MSSQL_AGENT_ENABLED": {"value": "TRUE"},
#       "MSSQL_PID": {"value": "Premium"}
#     }
#   }
# }

# --- Monitor IoT Edge Module Status ---
az iot hub module-identity list \
  --hub-name myIoTHub \
  --device-id myEdgeDevice \
  --output table

az iot hub module-twin show \
  --hub-name myIoTHub \
  --device-id myEdgeDevice \
  --module-id AzureSQLEdge

# Connect to SQL Edge from local machine (after port forward or direct IP)
# sqlcmd -S <edge-device-ip>,1433 -U SA -P '<password>'
```

---

## MariaDB Migration Helper Commands

```bash
# --- Check MariaDB Retirement Status ---
az mariadb server list \
  --resource-group myRG \
  --output table                    # List servers to identify for migration

az mariadb server show \
  --name mymariadbserver \
  --resource-group myRG

# --- Export Data for Migration (using mysqldump on client machine) ---
# mysqldump -h mymariadbserver.mariadb.database.azure.com \
#   -u myadmin@mymariadbserver \
#   -p \
#   --databases mydb \
#   --single-transaction \
#   --routines \
#   --events \
#   > mydb-export.sql

# --- Create Target MySQL Flexible Server ---
az mysql flexible-server create \
  --name mymysqlserver-migrated \
  --resource-group myRG \
  --location eastus \
  --admin-user mysqladmin \
  --admin-password 'P@ssw0rd123!' \
  --sku-name Standard_D4ds_v4 \
  --tier GeneralPurpose \
  --version 8.0 \
  --storage-size 128 \
  --public-access 0.0.0.0           # Temporarily open for migration; restrict after

# --- Use DMS for Online Migration (MariaDB → MySQL) ---
az dms project create \
  --name myMariaDBMigration \
  --service-name myDMSService \
  --resource-group myRG \
  --location eastus \
  --source-platform MySQL \
  --target-platform MySQL

az dms project task create \
  --task-name myMariaDBTask \
  --project-name myMariaDBMigration \
  --service-name myDMSService \
  --resource-group myRG \
  --task-type MigrateMySqlAzureDbForMySqlOffline \
  --task-parameters @mariadb-migration-task.json
```
