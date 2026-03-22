# Azure Event Hubs — CLI Reference

## Prerequisites

```bash
az login
az account set --subscription "My Subscription"
```

---

## Namespace Management

```bash
# Create a Standard namespace
az eventhubs namespace create \
  --name mynamespace \
  --resource-group myRG \
  --location eastus \
  --sku Standard \
  --capacity 2 \
  --enable-kafka true \
  --enable-auto-inflate true \
  --maximum-throughput-units 20

# Create a Premium namespace
az eventhubs namespace create \
  --name mypremiumns \
  --resource-group myRG \
  --location eastus \
  --sku Premium \
  --capacity 1 \
  --minimum-tls-version 1.2

# Create a namespace with zone redundancy (Standard/Premium)
az eventhubs namespace create \
  --name mynamespace \
  --resource-group myRG \
  --location eastus \
  --sku Standard \
  --zone-redundant true \
  --capacity 4

# Show namespace details
az eventhubs namespace show \
  --name mynamespace \
  --resource-group myRG

# List namespaces in resource group
az eventhubs namespace list \
  --resource-group myRG \
  -o table

# Update namespace (increase TUs, change auto-inflate max)
az eventhubs namespace update \
  --name mynamespace \
  --resource-group myRG \
  --capacity 4 \
  --maximum-throughput-units 40

# Add tags
az eventhubs namespace update \
  --name mynamespace \
  --resource-group myRG \
  --tags environment=production team=streaming

# Delete namespace
az eventhubs namespace delete \
  --name mynamespace \
  --resource-group myRG \
  --yes
```

---

## Namespace Authorization Rules (SAS)

```bash
# Create namespace-level SAS policy (Send + Listen)
az eventhubs namespace authorization-rule create \
  --name AllAccessPolicy \
  --namespace-name mynamespace \
  --resource-group myRG \
  --rights Send Listen Manage

# List namespace-level SAS policies
az eventhubs namespace authorization-rule list \
  --namespace-name mynamespace \
  --resource-group myRG \
  -o table

# Get connection string for a policy
az eventhubs namespace authorization-rule keys list \
  --name RootManageSharedAccessKey \
  --namespace-name mynamespace \
  --resource-group myRG \
  --query primaryConnectionString -o tsv

# Regenerate primary key
az eventhubs namespace authorization-rule keys renew \
  --name RootManageSharedAccessKey \
  --namespace-name mynamespace \
  --resource-group myRG \
  --key PrimaryKey
```

---

## Event Hub (Topic) Management

```bash
# Create an Event Hub with 32 partitions and 7-day retention
az eventhubs eventhub create \
  --name myeventhub \
  --namespace-name mynamespace \
  --resource-group myRG \
  --partition-count 32 \
  --message-retention 7 \
  --cleanup-policy Delete

# Create with compaction (Premium/Dedicated only)
az eventhubs eventhub create \
  --name mycompactedhub \
  --namespace-name mynamespace \
  --resource-group myRG \
  --partition-count 16 \
  --cleanup-policy Compaction

# Show Event Hub details (partitions, retention, capture status)
az eventhubs eventhub show \
  --name myeventhub \
  --namespace-name mynamespace \
  --resource-group myRG

# List all Event Hubs in namespace
az eventhubs eventhub list \
  --namespace-name mynamespace \
  --resource-group myRG \
  -o table

# Update retention period
az eventhubs eventhub update \
  --name myeventhub \
  --namespace-name mynamespace \
  --resource-group myRG \
  --message-retention 3

# Delete Event Hub
az eventhubs eventhub delete \
  --name myeventhub \
  --namespace-name mynamespace \
  --resource-group myRG \
  --yes
```

---

## Event Hub Authorization Rules (per-hub SAS)

```bash
# Create Event Hub-level SAS policy (Send only — for producers)
az eventhubs eventhub authorization-rule create \
  --name SendOnlyPolicy \
  --eventhub-name myeventhub \
  --namespace-name mynamespace \
  --resource-group myRG \
  --rights Send

# Create Listen-only policy (for consumers)
az eventhubs eventhub authorization-rule create \
  --name ListenOnlyPolicy \
  --eventhub-name myeventhub \
  --namespace-name mynamespace \
  --resource-group myRG \
  --rights Listen

# Get connection string for a hub-level policy
az eventhubs eventhub authorization-rule keys list \
  --name SendOnlyPolicy \
  --eventhub-name myeventhub \
  --namespace-name mynamespace \
  --resource-group myRG \
  --query primaryConnectionString -o tsv

# List Event Hub authorization rules
az eventhubs eventhub authorization-rule list \
  --eventhub-name myeventhub \
  --namespace-name mynamespace \
  --resource-group myRG \
  -o table
```

---

## Consumer Groups

```bash
# Create a consumer group
az eventhubs eventhub consumer-group create \
  --name analytics-consumer-group \
  --eventhub-name myeventhub \
  --namespace-name mynamespace \
  --resource-group myRG

# Create with user metadata
az eventhubs eventhub consumer-group create \
  --name stream-analytics-cg \
  --eventhub-name myeventhub \
  --namespace-name mynamespace \
  --resource-group myRG \
  --user-metadata "Used by Stream Analytics job: myASAJob"

# List consumer groups
az eventhubs eventhub consumer-group list \
  --eventhub-name myeventhub \
  --namespace-name mynamespace \
  --resource-group myRG \
  -o table

# Show consumer group
az eventhubs eventhub consumer-group show \
  --name analytics-consumer-group \
  --eventhub-name myeventhub \
  --namespace-name mynamespace \
  --resource-group myRG

# Delete consumer group
az eventhubs eventhub consumer-group delete \
  --name analytics-consumer-group \
  --eventhub-name myeventhub \
  --namespace-name mynamespace \
  --resource-group myRG \
  --yes
```

---

## Capture Configuration

```bash
# Enable Capture to ADLS Gen2 (Avro format)
az eventhubs eventhub update \
  --name myeventhub \
  --namespace-name mynamespace \
  --resource-group myRG \
  --enable-capture true \
  --capture-interval 300 \
  --capture-size-limit 314572800 \
  --destination-name EventHubArchive.AzureBlockBlob \
  --storage-account /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{account} \
  --blob-container eventhub-capture \
  --archive-name-format "{Namespace}/{EventHub}/{PartitionId}/{Year}/{Month}/{Day}/{Hour}/{Minute}/{Second}" \
  --skip-empty-archives true

# Enable Capture to ADLS Gen2 with Parquet format (Premium/Dedicated)
az eventhubs eventhub update \
  --name myeventhub \
  --namespace-name mynamespace \
  --resource-group myRG \
  --enable-capture true \
  --capture-interval 60 \
  --capture-size-limit 10485760 \
  --destination-name EventHubArchive.AzureDataLake \
  --storage-account /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.DataLakeStore/accounts/{account} \
  --blob-container eventhub-capture

# Disable capture
az eventhubs eventhub update \
  --name myeventhub \
  --namespace-name mynamespace \
  --resource-group myRG \
  --enable-capture false
```

---

## Schema Registry

```bash
# Create schema group in namespace
az eventhubs namespace schema-registry create \
  --name my-schema-group \
  --namespace-name mynamespace \
  --resource-group myRG \
  --schema-compatibility Backward \
  --schema-type Avro

# List schema groups
az eventhubs namespace schema-registry list \
  --namespace-name mynamespace \
  --resource-group myRG \
  -o table

# Show schema group
az eventhubs namespace schema-registry show \
  --name my-schema-group \
  --namespace-name mynamespace \
  --resource-group myRG

# Delete schema group
az eventhubs namespace schema-registry delete \
  --name my-schema-group \
  --namespace-name mynamespace \
  --resource-group myRG \
  --yes
```

---

## Geo-Disaster Recovery

```bash
# Create alias (primary namespace as source)
az eventhubs georecovery-alias create \
  --alias mygeodralias \
  --namespace-name mynamespace-primary \
  --resource-group myRG \
  --partner-namespace /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.EventHub/namespaces/mynamespace-secondary

# Check replication state
az eventhubs georecovery-alias show \
  --alias mygeodralias \
  --namespace-name mynamespace-primary \
  --resource-group myRG \
  --query "provisioningState" -o tsv

# Get alias connection string (use this in apps — works for both primary/secondary)
az eventhubs georecovery-alias list-key \
  --alias mygeodralias \
  --namespace-name mynamespace-primary \
  --resource-group myRG \
  --authorization-rule-name RootManageSharedAccessKey

# Break pairing (before failover)
az eventhubs georecovery-alias break-pairing \
  --alias mygeodralias \
  --namespace-name mynamespace-primary \
  --resource-group myRG

# Initiate failover (on secondary namespace)
az eventhubs georecovery-alias fail-over \
  --alias mygeodralias \
  --namespace-name mynamespace-secondary \
  --resource-group myRG

# Delete alias
az eventhubs georecovery-alias delete \
  --alias mygeodralias \
  --namespace-name mynamespace-primary \
  --resource-group myRG
```

---

## Network Rules and Private Endpoints

```bash
# Add IP firewall rule
az eventhubs namespace network-rule add \
  --namespace-name mynamespace \
  --resource-group myRG \
  --ip-address 203.0.113.0/24

# Add VNet rule
az eventhubs namespace network-rule add \
  --namespace-name mynamespace \
  --resource-group myRG \
  --subnet /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Network/virtualNetworks/{vnet}/subnets/{subnet}

# Show network rules
az eventhubs namespace network-rule show \
  --namespace-name mynamespace \
  --resource-group myRG

# Set default action to Deny (enforce network rules)
az eventhubs namespace update \
  --name mynamespace \
  --resource-group myRG \
  --default-action Deny

# Create private endpoint
az network private-endpoint create \
  --name mynamespace-pe \
  --resource-group myRG \
  --vnet-name myVNet \
  --subnet mySubnet \
  --private-connection-resource-id $(az eventhubs namespace show --name mynamespace --resource-group myRG --query id -o tsv) \
  --group-id namespace \
  --connection-name mynamespace-connection
```

---

## RBAC Role Assignments

```bash
# Assign Event Hubs Data Sender role (for producers)
NAMESPACE_ID=$(az eventhubs namespace show --name mynamespace --resource-group myRG --query id -o tsv)

az role assignment create \
  --assignee <object-id-of-MI-or-user> \
  --role "Azure Event Hubs Data Sender" \
  --scope $NAMESPACE_ID

# Assign Event Hubs Data Receiver role (for consumers)
az role assignment create \
  --assignee <object-id> \
  --role "Azure Event Hubs Data Receiver" \
  --scope $NAMESPACE_ID

# Assign scope to specific Event Hub instead of namespace
az role assignment create \
  --assignee <object-id> \
  --role "Azure Event Hubs Data Sender" \
  --scope "$NAMESPACE_ID/eventhubs/myeventhub"
```
