# Event-driven IoT Integration — CLI Reference
For service concepts, see [iot-integration-capabilities.md](iot-integration-capabilities.md).

## IoT Hub Message Routing

```bash
# --- Custom Routing Endpoints ---
# Add Event Hub endpoint
az iot hub routing-endpoint create \
  --hub-name myIoTHub \
  --resource-group myRG \
  --endpoint-name alertsEventHub \
  --endpoint-type eventhub \
  --connection-string "Endpoint=sb://myns.servicebus.windows.net/;EntityPath=alerts;SharedAccessKeyName=..."

# Add Storage Container endpoint
az iot hub routing-endpoint create \
  --hub-name myIoTHub \
  --resource-group myRG \
  --endpoint-name coldStorage \
  --endpoint-type azurestoragecontainer \
  --connection-string "DefaultEndpointsProtocol=https;AccountName=mystore;AccountKey=..." \
  --container iot-archive \
  --file-name-format '{iothub}/{partition}/{YYYY}/{MM}/{DD}/{HH}/{mm}'

# Add Service Bus Queue endpoint
az iot hub routing-endpoint create \
  --hub-name myIoTHub \
  --resource-group myRG \
  --endpoint-name commandQueue \
  --endpoint-type servicebusqueue \
  --connection-string "Endpoint=sb://myns.servicebus.windows.net/;EntityPath=commands;..."

# List all routing endpoints
az iot hub routing-endpoint list \
  --hub-name myIoTHub \
  --resource-group myRG

# Show a specific endpoint
az iot hub routing-endpoint show \
  --hub-name myIoTHub \
  --resource-group myRG \
  --endpoint-name alertsEventHub

# Delete an endpoint
az iot hub routing-endpoint delete \
  --hub-name myIoTHub \
  --resource-group myRG \
  --endpoint-name alertsEventHub

# --- Message Routes ---
# Create route for temperature alerts to Event Hub
az iot hub route create \
  --hub-name myIoTHub \
  --resource-group myRG \
  --route-name high-temp-alerts \
  --endpoint-name alertsEventHub \
  --source DeviceMessages \
  --condition "temperatureAlert = true AND temperature > 80" \
  --enabled true

# Create route for all messages to cold storage (no filter)
az iot hub route create \
  --hub-name myIoTHub \
  --resource-group myRG \
  --route-name archive-all \
  --endpoint-name coldStorage \
  --source DeviceMessages \
  --enabled true

# Create route for device twin change events
az iot hub route create \
  --hub-name myIoTHub \
  --resource-group myRG \
  --route-name twin-changes \
  --endpoint-name alertsEventHub \
  --source TwinChangeEvents \
  --enabled true

# List all routes
az iot hub route list \
  --hub-name myIoTHub \
  --resource-group myRG

# Show a route
az iot hub route show \
  --hub-name myIoTHub \
  --resource-group myRG \
  --route-name high-temp-alerts

# Test a route condition against a simulated message
az iot hub route test \
  --hub-name myIoTHub \
  --resource-group myRG \
  --route-name high-temp-alerts \
  --body '{"temperature": 95, "temperatureAlert": true}' \
  --properties "contentType=application/json"

# Update a route (disable)
az iot hub route update \
  --hub-name myIoTHub \
  --resource-group myRG \
  --route-name archive-all \
  --enabled false

# Delete a route
az iot hub route delete \
  --hub-name myIoTHub \
  --resource-group myRG \
  --route-name high-temp-alerts
```

## Azure Stream Analytics (IoT Jobs)

```bash
# --- Stream Analytics Job Management ---
az stream-analytics job create \
  --resource-group myRG \
  --job-name myIoTStreamJob \
  --location eastus \
  --output-error-policy Drop \
  --events-out-of-order-policy Adjust \
  --events-out-of-order-max-delay-in-seconds 5 \
  --compatibility-level 1.2               # Create ASA job

az stream-analytics job list --resource-group myRG  # List jobs

az stream-analytics job start \
  --resource-group myRG \
  --job-name myIoTStreamJob \
  --output-start-mode JobStartTime        # Start job (process from now)

az stream-analytics job stop \
  --resource-group myRG \
  --job-name myIoTStreamJob               # Stop job

# --- Inputs (IoT Hub) ---
az stream-analytics input create \
  --resource-group myRG \
  --job-name myIoTStreamJob \
  --name IoTHubInput \
  --type Stream \
  --datasource '{
    "type": "Microsoft.Devices/IotHubs",
    "properties": {
      "iotHubNamespace": "myIoTHub",
      "sharedAccessPolicyName": "service",
      "sharedAccessPolicyKey": "...",
      "consumerGroupName": "streamanalytics",
      "endpoint": "messages/events"
    }
  }' \
  --serialization '{"type": "Json", "properties": {"encoding": "UTF8"}}'

# --- Outputs (Cosmos DB) ---
az stream-analytics output create \
  --resource-group myRG \
  --job-name myIoTStreamJob \
  --name CosmosOutput \
  --datasource '{
    "type": "Microsoft.Storage/DocumentDB",
    "properties": {
      "accountId": "myCosmosAccount",
      "accountKey": "...",
      "database": "iotdb",
      "collectionNamePattern": "telemetry"
    }
  }'
```

## Azure Notification Hubs

```bash
# --- Namespace Management ---
az notification-hub namespace create \
  --resource-group myRG \
  --name myNotifNamespace \
  --location eastus \
  --sku Free                              # Create Notification Hub namespace

az notification-hub namespace list \
  --resource-group myRG                  # List namespaces

az notification-hub namespace show \
  --resource-group myRG \
  --namespace-name myNotifNamespace      # Show namespace details

az notification-hub namespace delete \
  --resource-group myRG \
  --name myNotifNamespace --yes          # Delete namespace

# --- Hub Management ---
az notification-hub create \
  --resource-group myRG \
  --namespace-name myNotifNamespace \
  --name myNotifHub \
  --location eastus                      # Create notification hub

az notification-hub list \
  --resource-group myRG \
  --namespace-name myNotifNamespace      # List hubs in namespace

az notification-hub show \
  --resource-group myRG \
  --namespace-name myNotifNamespace \
  --name myNotifHub                      # Show hub details

# --- Platform Credentials ---
# Configure FCM (Android) credentials
az notification-hub credential gcm update \
  --resource-group myRG \
  --namespace-name myNotifNamespace \
  --notification-hub-name myNotifHub \
  --google-api-key "your-fcm-server-key"

# Configure APNs (iOS) credentials
az notification-hub credential apns update \
  --resource-group myRG \
  --namespace-name myNotifNamespace \
  --notification-hub-name myNotifHub \
  --apns-certificate ./cert.p12 \
  --certificate-key "cert-password" \
  --endpoint "gateway.sandbox.push.apple.com"  # sandbox; use push.apple.com for prod

# List configured credentials
az notification-hub credential list \
  --resource-group myRG \
  --namespace-name myNotifNamespace \
  --notification-hub-name myNotifHub

# --- Authorization Rules ---
az notification-hub authorization-rule create \
  --resource-group myRG \
  --namespace-name myNotifNamespace \
  --notification-hub-name myNotifHub \
  --name myapp-send-rule \
  --rights Send                          # Create rule with Send-only rights

az notification-hub authorization-rule list \
  --resource-group myRG \
  --namespace-name myNotifNamespace \
  --notification-hub-name myNotifHub    # List authorization rules

az notification-hub authorization-rule list-keys \
  --resource-group myRG \
  --namespace-name myNotifNamespace \
  --notification-hub-name myNotifHub \
  --name myapp-send-rule                 # Get connection strings for a rule
```
