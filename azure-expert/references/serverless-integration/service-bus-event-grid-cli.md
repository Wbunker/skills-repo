# Azure Service Bus & Event Grid — CLI Reference
For service concepts, see [service-bus-event-grid-capabilities.md](service-bus-event-grid-capabilities.md).

---

## Azure Service Bus

```bash
# --- Namespace Management ---
# Create a Service Bus namespace (Standard tier)
az servicebus namespace create \
  --resource-group myRG \
  --name myServiceBusNS \
  --location eastus \
  --sku Standard

# Create a Premium namespace (dedicated, VNet-capable)
az servicebus namespace create \
  --resource-group myRG \
  --name myPremiumServiceBusNS \
  --location eastus \
  --sku Premium \
  --premium-messaging-partitions 1 \
  --zone-redundant true

# List namespaces in a resource group
az servicebus namespace list \
  --resource-group myRG \
  --query "[].{Name:name, Sku:sku.name, State:status, Location:location}" \
  --output table

# Show namespace details
az servicebus namespace show \
  --resource-group myRG \
  --name myServiceBusNS

# Delete a namespace
az servicebus namespace delete \
  --resource-group myRG \
  --name myServiceBusNS \
  --yes

# --- Queue Management ---
# Create a basic queue
az servicebus queue create \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --name myQueue

# Create a queue with sessions, DLQ, and duplicate detection
az servicebus queue create \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --name myOrderQueue \
  --enable-session true \
  --dead-lettering-on-message-expiration true \
  --duplicate-detection-history-time-window PT10M \
  --max-delivery-count 5 \
  --lock-duration PT1M \
  --default-message-time-to-live P7D

# Create a queue with auto-forward to another queue
az servicebus queue create \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --name myForwardingQueue \
  --forward-to myTargetQueue

# Show queue details (including current message count)
az servicebus queue show \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --name myQueue

# List all queues in a namespace
az servicebus queue list \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --query "[].{Name:name, MessageCount:messageCount, ActiveMessages:countDetails.activeMessageCount, DLQ:countDetails.deadLetterMessageCount}" \
  --output table

# Update queue properties
az servicebus queue update \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --name myQueue \
  --max-delivery-count 10 \
  --lock-duration PT2M

# Delete a queue
az servicebus queue delete \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --name myQueue \
  --yes

# --- Topic Management ---
# Create a topic
az servicebus topic create \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --name myTopic \
  --default-message-time-to-live P1D \
  --enable-duplicate-detection true \
  --duplicate-detection-history-time-window PT10M

# List topics in a namespace
az servicebus topic list \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --output table

# Show topic details
az servicebus topic show \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --name myTopic

# Delete a topic
az servicebus topic delete \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --name myTopic \
  --yes

# --- Subscription Management ---
# Create a subscription on a topic (default: receives all messages)
az servicebus topic subscription create \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --topic-name myTopic \
  --name mySubscription \
  --max-delivery-count 5 \
  --dead-lettering-on-message-expiration true

# Create a subscription with session support
az servicebus topic subscription create \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --topic-name myTopic \
  --name mySessionSubscription \
  --enable-session true

# List subscriptions on a topic
az servicebus topic subscription list \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --topic-name myTopic \
  --output table

# Show subscription details (including message counts)
az servicebus topic subscription show \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --topic-name myTopic \
  --name mySubscription

# --- Subscription Rules / Filters ---
# Create a SQL filter rule (replace default True rule)
az servicebus topic subscription rule create \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --topic-name myTopic \
  --subscription-name mySubscription \
  --name emea-filter \
  --filter-sql-expression "Region = 'EMEA' AND OrderType = 'B2B'"

# Create a correlation filter rule
az servicebus topic subscription rule create \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --topic-name myTopic \
  --subscription-name mySubscription \
  --name priority-filter \
  --action-sql-expression "SET Priority = 'High'" \
  --filter-correlation-id "high-priority"

# List rules on a subscription
az servicebus topic subscription rule list \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --topic-name myTopic \
  --subscription-name mySubscription \
  --output table

# Delete a rule
az servicebus topic subscription rule delete \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --topic-name myTopic \
  --subscription-name mySubscription \
  --name emea-filter

# --- Authorization Rules ---
# Create a namespace-level authorization rule (Send only)
az servicebus namespace authorization-rule create \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --name sendOnlyRule \
  --rights Send

# Create a rule with Listen and Send
az servicebus namespace authorization-rule create \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --name appRule \
  --rights Listen Send

# List authorization rules
az servicebus namespace authorization-rule list \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --output table

# Get connection string for an authorization rule
az servicebus namespace authorization-rule keys list \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --name RootManageSharedAccessKey \
  --query primaryConnectionString \
  --output tsv

# Create a queue-level authorization rule (Listen only)
az servicebus queue authorization-rule create \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --queue-name myQueue \
  --name listenerRule \
  --rights Listen

# Get queue-level connection string
az servicebus queue authorization-rule keys list \
  --resource-group myRG \
  --namespace-name myServiceBusNS \
  --queue-name myQueue \
  --name listenerRule \
  --query primaryConnectionString \
  --output tsv

# --- Geo-Disaster Recovery (Premium) ---
# Create a Geo-DR alias (pair two Premium namespaces)
az servicebus georecovery-alias create \
  --resource-group myRG \
  --namespace-name myPrimaryNS \
  --alias myGeoAlias \
  --partner-namespace /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.ServiceBus/namespaces/mySecondaryNS

# Initiate failover (breaks pairing, promotes secondary)
az servicebus georecovery-alias fail-over \
  --resource-group myRG \
  --namespace-name mySecondaryNS \
  --alias myGeoAlias
```

---

## Azure Event Grid

```bash
# --- System Topics (Azure service events) ---
# Create a system topic for Azure Blob Storage events
az eventgrid system-topic create \
  --resource-group myRG \
  --name myBlobSystemTopic \
  --topic-type Microsoft.Storage.StorageAccounts \
  --source /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.Storage/storageAccounts/myStorageAcct \
  --location eastus

# List system topics
az eventgrid system-topic list \
  --resource-group myRG \
  --output table

# Create an event subscription on a system topic (deliver to Azure Function)
az eventgrid system-topic event-subscription create \
  --resource-group myRG \
  --system-topic-name myBlobSystemTopic \
  --name blob-to-function \
  --endpoint /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.Web/sites/myFunctionApp/functions/ProcessBlob \
  --endpoint-type azurefunction \
  --included-event-types Microsoft.Storage.BlobCreated \
  --subject-begins-with /blobServices/default/containers/uploads/

# Create subscription delivering to Service Bus queue
az eventgrid system-topic event-subscription create \
  --resource-group myRG \
  --system-topic-name myBlobSystemTopic \
  --name blob-to-servicebus \
  --endpoint /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.ServiceBus/namespaces/myNS/queues/myQueue \
  --endpoint-type servicebusqueue \
  --included-event-types Microsoft.Storage.BlobDeleted

# --- Custom Topics ---
# Create a custom event topic
az eventgrid topic create \
  --resource-group myRG \
  --name myCustomTopic \
  --location eastus \
  --input-schema cloudeventschemav1_0

# List custom topics
az eventgrid topic list \
  --resource-group myRG \
  --output table

# Show topic details (including endpoint URL)
az eventgrid topic show \
  --resource-group myRG \
  --name myCustomTopic \
  --query "{Endpoint:endpoint, State:provisioningState}" \
  --output json

# Get topic keys (for publishing events)
az eventgrid topic key list \
  --resource-group myRG \
  --name myCustomTopic \
  --query "key1" \
  --output tsv

# Create an event subscription on a custom topic (webhook)
az eventgrid event-subscription create \
  --source-resource-id /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.EventGrid/topics/myCustomTopic \
  --name my-webhook-sub \
  --endpoint https://myapp.contoso.com/api/events \
  --endpoint-type webhook

# Create event subscription with dead-lettering (to Storage Blob)
az eventgrid event-subscription create \
  --source-resource-id /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.EventGrid/topics/myCustomTopic \
  --name my-sub-with-dlq \
  --endpoint /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.Web/sites/myFunctionApp/functions/HandleEvent \
  --endpoint-type azurefunction \
  --deadletter-endpoint /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.Storage/storageAccounts/myStorage/blobServices/default/containers/deadletter

# --- Event Domains ---
# Create an Event Grid domain (for multi-tenant topic management)
az eventgrid domain create \
  --resource-group myRG \
  --name myEventDomain \
  --location eastus \
  --input-schema cloudeventschemav1_0

# Create a domain topic
az eventgrid domain topic create \
  --resource-group myRG \
  --domain-name myEventDomain \
  --name tenant-abc-topic

# Create an event subscription on a domain topic
az eventgrid event-subscription create \
  --source-resource-id /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.EventGrid/domains/myEventDomain/topics/tenant-abc-topic \
  --name tenant-abc-sub \
  --endpoint https://tenant-abc.contoso.com/api/events \
  --endpoint-type webhook

# List domain topics
az eventgrid domain topic list \
  --resource-group myRG \
  --domain-name myEventDomain \
  --output table

# --- List Event Subscriptions ---
# List all event subscriptions for a custom topic
az eventgrid event-subscription list \
  --source-resource-id /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.EventGrid/topics/myCustomTopic \
  --output table

# List all event subscriptions in a resource group
az eventgrid event-subscription list \
  --resource-group myRG \
  --output table

# Show details of a specific event subscription
az eventgrid event-subscription show \
  --source-resource-id /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.EventGrid/topics/myCustomTopic \
  --name my-webhook-sub

# Delete an event subscription
az eventgrid event-subscription delete \
  --source-resource-id /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.EventGrid/topics/myCustomTopic \
  --name my-webhook-sub

# Delete a custom topic
az eventgrid topic delete \
  --resource-group myRG \
  --name myCustomTopic \
  --yes
```
