# Other Analytics Services — CLI Reference

## Azure Data Explorer (ADX / Kusto)

### Prerequisites

```bash
az login
az account set --subscription "My Subscription"

# Install Kusto extension
az extension add -n kusto

# ADX Python SDK
pip install azure-kusto-data azure-kusto-ingest azure-mgmt-kusto
```

---

### Cluster Management

```bash
# Create an ADX cluster (Standard tier)
az kusto cluster create \
  --name myadxcluster \
  --resource-group myRG \
  --location eastus \
  --sku name="Standard_D14_v2" tier="Standard" capacity=2 \
  --enable-streaming-ingest true \
  --enable-auto-stop false

# Create a Dev tier cluster (lower cost, no SLA)
az kusto cluster create \
  --name myadxdev \
  --resource-group myRG \
  --location eastus \
  --sku name="Dev(No SLA)_Standard_D11_v2" tier="Basic" capacity=1

# Create with optimized autoscale
az kusto cluster create \
  --name myadxcluster \
  --resource-group myRG \
  --location eastus \
  --sku name="Standard_L8s_v3" tier="Standard" capacity=2 \
  --optimized-autoscale is-enabled=true minimum=2 maximum=20 version=1

# Show cluster details (URI, state, data ingestion URI)
az kusto cluster show \
  --name myadxcluster \
  --resource-group myRG

# Get cluster data ingestion URI (for ingestion client configuration)
az kusto cluster show \
  --name myadxcluster \
  --resource-group myRG \
  --query "dataIngestionUri" -o tsv

# Get cluster URI (for query connections)
az kusto cluster show \
  --name myadxcluster \
  --resource-group myRG \
  --query "uri" -o tsv

# List clusters
az kusto cluster list \
  --resource-group myRG \
  -o table

# Start cluster (after stopping)
az kusto cluster start \
  --name myadxcluster \
  --resource-group myRG

# Stop cluster (eliminate compute cost)
az kusto cluster stop \
  --name myadxcluster \
  --resource-group myRG

# Scale cluster (update node count)
az kusto cluster update \
  --name myadxcluster \
  --resource-group myRG \
  --sku name="Standard_D14_v2" tier="Standard" capacity=4

# Add language extensions (Python/R for inline scripts in KQL)
az kusto cluster add-language-extension \
  --name myadxcluster \
  --resource-group myRG \
  --value "[{\"languageExtensionName\": \"PYTHON\"}]"

# Delete cluster
az kusto cluster delete \
  --name myadxcluster \
  --resource-group myRG \
  --yes
```

---

### Database Management

```bash
# Create a database (ReadWrite type)
az kusto database create \
  --cluster-name myadxcluster \
  --database-name MyDatabase \
  --resource-group myRG \
  --read-write-database soft-delete-period=P365D hot-cache-period=P31D location=eastus

# Periods use ISO 8601 duration format:
# P365D = 365 days (soft delete / retention)
# P31D = 31 days (hot cache period)

# Create a ReadOnly database (follower database)
az kusto database create \
  --cluster-name myadxcluster \
  --database-name FollowerDB \
  --resource-group myRG \
  --read-only-following-database \
    attached-database-configuration-name=myconfig \
    cluster-resource-id=/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Kusto/clusters/{leader-cluster} \
    location=eastus

# Show database details
az kusto database show \
  --cluster-name myadxcluster \
  --database-name MyDatabase \
  --resource-group myRG

# List databases in cluster
az kusto database list \
  --cluster-name myadxcluster \
  --resource-group myRG \
  -o table

# Update database hot cache period
az kusto database update \
  --cluster-name myadxcluster \
  --database-name MyDatabase \
  --resource-group myRG \
  --read-write-database hot-cache-period=P7D soft-delete-period=P730D location=eastus

# Delete database
az kusto database delete \
  --cluster-name myadxcluster \
  --database-name MyDatabase \
  --resource-group myRG \
  --yes
```

---

### Data Connections (Streaming Ingestion)

```bash
# Create Event Hubs data connection (continuous ingestion)
az kusto data-connection event-hub create \
  --cluster-name myadxcluster \
  --database-name MyDatabase \
  --data-connection-name eventhub-connection \
  --resource-group myRG \
  --location eastus \
  --event-hub-resource-id /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.EventHub/namespaces/{ns}/eventhubs/{hub} \
  --consumer-group adx-cg \
  --table-name DeviceTelemetry \
  --data-format JSON \
  --mapping-rule-name DeviceTelemetryMapping \
  --managed-identity-resource-id $(az kusto cluster show --name myadxcluster --resource-group myRG --query id -o tsv)

# Create IoT Hub data connection
az kusto data-connection iot-hub create \
  --cluster-name myadxcluster \
  --database-name MyDatabase \
  --data-connection-name iothub-connection \
  --resource-group myRG \
  --location eastus \
  --iot-hub-resource-id /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Devices/IotHubs/{hub} \
  --consumer-group adx-cg \
  --shared-access-policy-name iothubowner \
  --table-name IoTDeviceData \
  --data-format JSON \
  --mapping-rule-name IoTMapping

# Create Event Grid data connection (auto-ingest new blobs)
az kusto data-connection event-grid create \
  --cluster-name myadxcluster \
  --database-name MyDatabase \
  --data-connection-name eventgrid-connection \
  --resource-group myRG \
  --location eastus \
  --storage-account-resource-id /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{account} \
  --event-hub-resource-id /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.EventHub/namespaces/{ns}/eventhubs/{hub} \
  --consumer-group adx-cg \
  --table-name FileData \
  --data-format PARQUET \
  --blob-storage-event-type Microsoft.Storage.BlobCreated \
  --ignore-first-record false

# List data connections
az kusto data-connection list \
  --cluster-name myadxcluster \
  --database-name MyDatabase \
  --resource-group myRG \
  -o table

# Delete data connection
az kusto data-connection delete \
  --cluster-name myadxcluster \
  --database-name MyDatabase \
  --data-connection-name eventhub-connection \
  --resource-group myRG \
  --yes
```

---

### KQL Queries via Python SDK

```python
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.identity import DefaultAzureCredential

# Authenticate with managed identity / DefaultAzureCredential
cluster_uri = "https://myadxcluster.eastus.kusto.windows.net"
kcsb = KustoConnectionStringBuilder.with_azure_token_credential(
    cluster_uri, DefaultAzureCredential()
)

client = KustoClient(kcsb)

# Execute KQL query
response = client.execute("MyDatabase", """
    DeviceTelemetry
    | where Timestamp > ago(1h)
    | where Temperature > 80
    | summarize MaxTemp=max(Temperature) by DeviceId
    | order by MaxTemp desc
    | take 20
""")

for row in response.primary_results[0]:
    print(f"DeviceId: {row['DeviceId']}, MaxTemp: {row['MaxTemp']}")
```

---

## Azure HDInsight

### Prerequisites

```bash
# HDInsight CLI is part of base Azure CLI
az login
az account set --subscription "My Subscription"
```

### Cluster Management

```bash
# Create an Interactive Query (Hive LLAP) cluster
az hdinsight create \
  --name myHDICluster \
  --resource-group myRG \
  --location eastus \
  --type InteractiveQuery \
  --component-version InteractiveHive=3.1 \
  --headnode-size Standard_D13_v2 \
  --workernode-size Standard_D13_v2 \
  --workernode-count 4 \
  --http-user admin \
  --http-password "P@ssw0rd123!" \
  --ssh-user sshuser \
  --ssh-password "P@ssw0rd123!" \
  --storage-account mystorageaccount \
  --storage-account-key $(az storage account keys list --account-name mystorageaccount --resource-group myRG --query "[0].value" -o tsv) \
  --storage-default-container hdinsight-default

# Create a Spark cluster with ADLS Gen2
az hdinsight create \
  --name mySparkCluster \
  --resource-group myRG \
  --location eastus \
  --type Spark \
  --component-version Spark=3.1 \
  --headnode-size Standard_D13_v2 \
  --workernode-size Standard_D14_v2 \
  --workernode-count 4 \
  --http-user admin \
  --http-password "P@ssw0rd123!" \
  --ssh-user sshuser \
  --ssh-password "P@ssw0rd123!" \
  --storage-account mystorageaccount \
  --storage-account-key <key> \
  --storage-default-container spark-container \
  --assign-identity <managed-identity-resource-id>

# Show cluster details
az hdinsight show \
  --name myHDICluster \
  --resource-group myRG

# List clusters
az hdinsight list \
  --resource-group myRG \
  -o table

# Get cluster sizes (resize worker nodes)
az hdinsight resize \
  --name myHDICluster \
  --resource-group myRG \
  --workernode-count 8

# Enable auto-scale
az hdinsight autoscale create \
  --cluster-name myHDICluster \
  --resource-group myRG \
  --type Load \
  --min-workernode-count 4 \
  --max-workernode-count 20

# Delete cluster
az hdinsight delete \
  --name myHDICluster \
  --resource-group myRG \
  --yes
```

---

## Azure Data Share

### Prerequisites

```bash
# Install Data Share extension
az extension add -n datashare
```

### Account Management

```bash
# Create a Data Share account
az datashare account create \
  --name myDataShareAccount \
  --resource-group myRG \
  --location eastus

# Show account
az datashare account show \
  --name myDataShareAccount \
  --resource-group myRG

# List accounts
az datashare account list \
  --resource-group myRG \
  -o table

# Delete account
az datashare account delete \
  --name myDataShareAccount \
  --resource-group myRG \
  --yes
```

### Creating and Managing Shares

```bash
# Create a share (sent share — data you're sharing)
az datashare share create \
  --account-name myDataShareAccount \
  --resource-group myRG \
  --name MySalesDataShare \
  --share-kind CopyBased \
  --description "Monthly sales data for partner access"

# Add a dataset to the share (ADLS Gen2 file system)
az datashare dataset create \
  --account-name myDataShareAccount \
  --resource-group myRG \
  --share-name MySalesDataShare \
  --dataset-name SalesData \
  --dataset '{
    "kind": "AdlsGen2Folder",
    "dataSetName": "SalesData",
    "properties": {
      "resourceGroup": "myRG",
      "storageAccountName": "mystorageaccount",
      "fileSystem": "data",
      "folderPath": "sales/2024",
      "subscriptionId": "<sub-id>"
    }
  }'

# Add a snapshot schedule (refresh schedule for recipients)
az datashare synchronization-setting create \
  --account-name myDataShareAccount \
  --resource-group myRG \
  --share-name MySalesDataShare \
  --synchronization-setting-name DailyRefresh \
  --synchronization-setting '{
    "kind": "ScheduleBased",
    "recurrenceInterval": "Day",
    "synchronizationTime": "2024-01-01T02:00:00Z"
  }'

# Invite a recipient
az datashare invitation create \
  --account-name myDataShareAccount \
  --resource-group myRG \
  --share-name MySalesDataShare \
  --invitation-name PartnerInvitation \
  --target-email "partner@partner.com"

# List invitations
az datashare invitation list \
  --account-name myDataShareAccount \
  --resource-group myRG \
  --share-name MySalesDataShare \
  -o table

# List sent shares
az datashare share list \
  --account-name myDataShareAccount \
  --resource-group myRG \
  -o table

# Revoke an invitation
az datashare invitation delete \
  --account-name myDataShareAccount \
  --resource-group myRG \
  --share-name MySalesDataShare \
  --invitation-name PartnerInvitation

# Delete a share
az datashare share delete \
  --account-name myDataShareAccount \
  --resource-group myRG \
  --name MySalesDataShare \
  --yes
```

### Receiving Shares

```bash
# List received share invitations in your account
az datashare consumer invitation list \
  -o table

# Accept invitation and create received share
az datashare share-subscription create \
  --account-name myDataShareAccount \
  --resource-group myRG \
  --share-subscription-name PartnerSalesData \
  --invitation-id <invitation-guid> \
  --source-share-location eastus

# List received shares (subscriptions)
az datashare share-subscription list \
  --account-name myDataShareAccount \
  --resource-group myRG \
  -o table

# Trigger synchronization (pull latest snapshot)
az datashare share-subscription synchronize \
  --account-name myDataShareAccount \
  --resource-group myRG \
  --share-subscription-name PartnerSalesData \
  --synchronization-mode FullSync

# Map received dataset to your storage (where data will land)
az datashare consumer source-data-set-mapping create \
  --account-name myDataShareAccount \
  --resource-group myRG \
  --share-subscription-name PartnerSalesData \
  --data-set-mapping-name SalesMapping \
  --mapping '{
    "kind": "AdlsGen2Folder",
    "dataSetId": "<source-dataset-id>",
    "properties": {
      "resourceGroup": "myRG",
      "storageAccountName": "myreceiverstore",
      "fileSystem": "received-data",
      "folderPath": "partner-sales/",
      "subscriptionId": "<sub-id>"
    }
  }'
```
