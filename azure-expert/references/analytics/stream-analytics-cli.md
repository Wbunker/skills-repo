# Azure Stream Analytics — CLI Reference

## Prerequisites

```bash
az login
az account set --subscription "My Subscription"

# Verify Stream Analytics commands are available
az stream-analytics --help
```

---

## Job Management

```bash
# Create a Stream Analytics job
az stream-analytics job create \
  --name myASAJob \
  --resource-group myRG \
  --location eastus \
  --output-error-policy Drop \
  --events-out-of-order-policy Adjust \
  --events-out-of-order-max-delay-in-seconds 10 \
  --events-late-arrival-max-delay-in-seconds 5 \
  --data-locale "en-US" \
  --compatibility-level "1.2" \
  --sku-name Standard

# Show job details (status, streaming units, query)
az stream-analytics job show \
  --name myASAJob \
  --resource-group myRG

# List jobs in resource group
az stream-analytics job list \
  --resource-group myRG \
  -o table

# List all jobs in subscription
az stream-analytics job list \
  -o table

# Update job (change streaming units, output error policy)
az stream-analytics job update \
  --name myASAJob \
  --resource-group myRG \
  --output-error-policy Retry

# Start job (begin processing from event source)
az stream-analytics job start \
  --name myASAJob \
  --resource-group myRG \
  --output-start-mode JobStartTime
  # OutputStartMode options: JobStartTime | CustomTime | LastOutputEventTime

# Start from a specific time (for reprocessing)
az stream-analytics job start \
  --name myASAJob \
  --resource-group myRG \
  --output-start-mode CustomTime \
  --output-start-time "2024-01-01T00:00:00Z"

# Stop job (pause processing, retain state)
az stream-analytics job stop \
  --name myASAJob \
  --resource-group myRG

# Delete job
az stream-analytics job delete \
  --name myASAJob \
  --resource-group myRG \
  --yes
```

---

## Inputs

### Streaming Input from Event Hubs

```bash
# Create Event Hubs streaming input
az stream-analytics input create \
  --input-name EventHubInput \
  --job-name myASAJob \
  --resource-group myRG \
  --properties '{
    "type": "Stream",
    "datasource": {
      "type": "Microsoft.ServiceBus/EventHub",
      "properties": {
        "serviceBusNamespace": "mynamespace",
        "eventHubName": "myeventhub",
        "consumerGroupName": "stream-analytics-cg",
        "authenticationMode": "Msi"
      }
    },
    "serialization": {
      "type": "Json",
      "properties": {
        "encoding": "UTF8"
      }
    }
  }'
```

### Streaming Input from IoT Hub

```bash
az stream-analytics input create \
  --input-name IoTInput \
  --job-name myASAJob \
  --resource-group myRG \
  --properties '{
    "type": "Stream",
    "datasource": {
      "type": "Microsoft.Devices/IotHubs",
      "properties": {
        "iotHubNamespace": "myiothub",
        "sharedAccessPolicyName": "iothubowner",
        "sharedAccessPolicyKey": "<key>",
        "consumerGroupName": "asa-cg",
        "endpoint": "messages/events"
      }
    },
    "serialization": {
      "type": "Json",
      "properties": {"encoding": "UTF8"}
    }
  }'
```

### Reference Data Input from Blob Storage

```bash
az stream-analytics input create \
  --input-name ReferenceData \
  --job-name myASAJob \
  --resource-group myRG \
  --properties '{
    "type": "Reference",
    "datasource": {
      "type": "Microsoft.Storage/Blob",
      "properties": {
        "storageAccounts": [{"accountName": "mystorageaccount", "accountKey": "<key>"}],
        "container": "reference-data",
        "pathPattern": "devices/{date}/{time}",
        "dateFormat": "yyyy/MM/dd",
        "timeFormat": "HH"
      }
    },
    "serialization": {
      "type": "Json",
      "properties": {"encoding": "UTF8"}
    }
  }'
```

### Manage Inputs

```bash
# List inputs
az stream-analytics input list \
  --job-name myASAJob \
  --resource-group myRG \
  -o table

# Show input details
az stream-analytics input show \
  --input-name EventHubInput \
  --job-name myASAJob \
  --resource-group myRG

# Test input connectivity
az stream-analytics input test \
  --input-name EventHubInput \
  --job-name myASAJob \
  --resource-group myRG

# Delete input
az stream-analytics input delete \
  --input-name EventHubInput \
  --job-name myASAJob \
  --resource-group myRG \
  --yes
```

---

## Outputs

### Output to Power BI

```bash
az stream-analytics output create \
  --output-name PowerBIOutput \
  --job-name myASAJob \
  --resource-group myRG \
  --datasource '{
    "type": "PowerBI",
    "properties": {
      "dataset": "RealTimeSensors",
      "table": "SensorReadings",
      "groupId": "<power-bi-workspace-id>",
      "groupName": "My Workspace",
      "authenticationMode": "UserToken"
    }
  }'
```

### Output to Azure SQL Database

```bash
az stream-analytics output create \
  --output-name SQLOutput \
  --job-name myASAJob \
  --resource-group myRG \
  --datasource '{
    "type": "Microsoft.Sql/Server/Database",
    "properties": {
      "server": "myserver.database.windows.net",
      "database": "mydb",
      "table": "StreamingResults",
      "user": "sqladmin",
      "password": "<password>",
      "authenticationMode": "Msi"
    }
  }'
```

### Output to Azure Blob Storage / ADLS Gen2

```bash
az stream-analytics output create \
  --output-name ADLSOutput \
  --job-name myASAJob \
  --resource-group myRG \
  --datasource '{
    "type": "Microsoft.Storage/Blob",
    "properties": {
      "storageAccounts": [{"accountName": "mystorageaccount", "accountKey": "<key>"}],
      "container": "streaming-output",
      "pathPattern": "data/{date}/{time}",
      "dateFormat": "yyyy/MM/dd",
      "timeFormat": "HH",
      "authenticationMode": "Msi"
    }
  }' \
  --serialization '{
    "type": "Parquet"
  }'
```

### Output to Event Hubs

```bash
az stream-analytics output create \
  --output-name EventHubOutput \
  --job-name myASAJob \
  --resource-group myRG \
  --datasource '{
    "type": "Microsoft.ServiceBus/EventHub",
    "properties": {
      "serviceBusNamespace": "mynamespace",
      "eventHubName": "enriched-events",
      "authenticationMode": "Msi"
    }
  }' \
  --serialization '{
    "type": "Json",
    "properties": {"encoding": "UTF8", "format": "LineSeparated"}
  }'
```

### Manage Outputs

```bash
# List outputs
az stream-analytics output list \
  --job-name myASAJob \
  --resource-group myRG \
  -o table

# Show output
az stream-analytics output show \
  --output-name SQLOutput \
  --job-name myASAJob \
  --resource-group myRG

# Test output connectivity
az stream-analytics output test \
  --output-name SQLOutput \
  --job-name myASAJob \
  --resource-group myRG

# Delete output
az stream-analytics output delete \
  --output-name SQLOutput \
  --job-name myASAJob \
  --resource-group myRG \
  --yes
```

---

## Transformation (Query)

```bash
# Create/update the SAQL query (transformation)
az stream-analytics transformation create \
  --transformation-name Transformation \
  --job-name myASAJob \
  --resource-group myRG \
  --streaming-units 6 \
  --saql "SELECT DeviceId, AVG(Temperature) AS AvgTemp, System.Timestamp() AS WindowEnd INTO SQLOutput FROM IoTInput TIMESTAMP BY EventEnqueuedUtcTime GROUP BY DeviceId, TumblingWindow(minute, 5)"

# Update the query (replace with contents from file)
QUERY=$(cat query.sql)
az stream-analytics transformation update \
  --transformation-name Transformation \
  --job-name myASAJob \
  --resource-group myRG \
  --saql "$QUERY"

# Update streaming units
az stream-analytics transformation update \
  --transformation-name Transformation \
  --job-name myASAJob \
  --resource-group myRG \
  --streaming-units 12

# Show current transformation
az stream-analytics transformation show \
  --transformation-name Transformation \
  --job-name myASAJob \
  --resource-group myRG
```

---

## Cluster Management (Dedicated)

```bash
# Create a dedicated ASA cluster
az stream-analytics cluster create \
  --name myASACluster \
  --resource-group myRG \
  --location eastus \
  --sku-capacity 36  # minimum 36 SUs

# Show cluster details
az stream-analytics cluster show \
  --name myASACluster \
  --resource-group myRG

# List clusters
az stream-analytics cluster list \
  --resource-group myRG \
  -o table

# Scale cluster
az stream-analytics cluster update \
  --name myASACluster \
  --resource-group myRG \
  --sku-capacity 72

# List jobs running on cluster
az stream-analytics cluster list-streaming-jobs \
  --name myASACluster \
  --resource-group myRG

# Create private endpoint on cluster
az stream-analytics private-endpoint create \
  --cluster-name myASACluster \
  --resource-group myRG \
  --name myEventHubPE \
  --group-ids namespace \
  --manual-private-link-service-connections '[{"name": "myEventHubPE", "privateLinkServiceId": "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.EventHub/namespaces/{ns}", "groupIds": ["namespace"]}]'

# Delete cluster
az stream-analytics cluster delete \
  --name myASACluster \
  --resource-group myRG \
  --yes
```

---

## Monitoring

```bash
# Enable diagnostic settings for ASA job
JOB_ID=$(az stream-analytics job show --name myASAJob --resource-group myRG --query id -o tsv)
WORKSPACE_ID=$(az monitor log-analytics workspace show --name myLogWorkspace --resource-group myRG --query id -o tsv)

az monitor diagnostic-settings create \
  --name asa-diagnostics \
  --resource $JOB_ID \
  --workspace $WORKSPACE_ID \
  --logs '[{"category": "Execution", "enabled": true}]' \
  --metrics '[{"category": "AllMetrics", "enabled": true}]'

# Key metrics to monitor:
# - ResourceUtilization: SU % utilization
# - InputEventBytes: Input throughput
# - OutputEvents: Events written to outputs
# - DroppedOrAdjustedEvents: Late/out-of-order events
# - Errors: Processing errors
# - WatermarkDelaySeconds: Processing lag
```
