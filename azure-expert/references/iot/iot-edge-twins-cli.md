# IoT Edge & Digital Twins — CLI Reference
For service concepts, see [iot-edge-twins-capabilities.md](iot-edge-twins-capabilities.md).

## Azure IoT Edge

```bash
# Install IoT extension
az extension add --name azure-iot

# --- Module Deployment ---
az iot edge set-modules \
  --hub-name myIoTHub \
  --device-id myEdgeDevice \
  --content deployment-manifest.json            # Deploy modules to a single edge device

az iot edge set-modules \
  --hub-name myIoTHub \
  --device-id myEdgeDevice \
  --content @./deployment.manifest.json         # Deploy from local file

# --- At-Scale Automatic Deployments ---
az iot edge deployment create \
  --hub-name myIoTHub \
  --deployment-id prod-factory-a-v2 \
  --content deployment-manifest.json \
  --target-condition "tags.location='factory-A' AND tags.tier='prod'" \
  --priority 10 \
  --labels '{"version":"v2","team":"iot"}'      # Create automatic deployment with target condition

az iot edge deployment list \
  --hub-name myIoTHub                           # List all automatic deployments

az iot edge deployment show \
  --hub-name myIoTHub \
  --deployment-id prod-factory-a-v2             # Show deployment details

az iot edge deployment show-metric \
  --hub-name myIoTHub \
  --deployment-id prod-factory-a-v2 \
  --metric-id appliedCount                      # Check how many devices applied deployment

az iot edge deployment update \
  --hub-name myIoTHub \
  --deployment-id prod-factory-a-v2 \
  --set priority=20                             # Update deployment priority

az iot edge deployment delete \
  --hub-name myIoTHub \
  --deployment-id prod-factory-a-v2             # Delete deployment

# --- Layered Deployments ---
az iot edge deployment create \
  --hub-name myIoTHub \
  --deployment-id monitoring-layer \
  --content monitoring-partial-manifest.json \
  --target-condition "tags.environment='prod'" \
  --priority 5 \
  --layered                                     # Create layered deployment

# --- Edge Device Management ---
az iot hub device-identity create \
  --hub-name myIoTHub \
  --device-id myEdgeGateway \
  --edge-enabled                                # Create edge-enabled device identity

az iot hub device-identity show \
  --hub-name myIoTHub \
  --device-id myEdgeGateway                     # Show edge device identity

# List modules running on an edge device
az iot hub module-identity list \
  --hub-name myIoTHub \
  --device-id myEdgeDevice                      # List modules (including $edgeAgent, $edgeHub)

az iot hub module-twin show \
  --hub-name myIoTHub \
  --device-id myEdgeDevice \
  --module-id tempSensor                        # Show module twin

az iot hub module-twin update \
  --hub-name myIoTHub \
  --device-id myEdgeDevice \
  --module-id tempSensor \
  --desired '{"sendInterval": 10}'              # Update module desired properties

# --- Invoke Direct Method on Module ---
az iot hub invoke-module-method \
  --hub-name myIoTHub \
  --device-id myEdgeDevice \
  --module-id tempSensor \
  --method-name reset                           # Invoke direct method on IoT Edge module

# --- Monitor Edge Messages ---
az iot hub monitor-events \
  --hub-name myIoTHub \
  --device-id myEdgeDevice                      # Monitor messages from edge device
```

## Azure Digital Twins

```bash
# Install Digital Twins extension
az extension add --name azure-iot

# --- Digital Twins Instance ---
az dt create \
  --resource-group myRG \
  --dt-name myDigitalTwins \
  --location eastus \
  --assign-identity                             # Create Digital Twins instance with managed identity

az dt list --resource-group myRG               # List Digital Twins instances
az dt show --dt-name myDigitalTwins --resource-group myRG  # Show instance details

az dt role-assignment create \
  --dt-name myDigitalTwins \
  --role "Azure Digital Twins Data Owner" \
  --assignee user@example.com                  # Grant access to Digital Twins

az dt role-assignment create \
  --dt-name myDigitalTwins \
  --role "Azure Digital Twins Data Reader" \
  --assignee <service-principal-id>            # Grant read-only access

# --- Model Management ---
az dt model create \
  --dt-name myDigitalTwins \
  --models @room-model.json                    # Upload a DTDL model

az dt model create \
  --dt-name myDigitalTwins \
  --models '[{"@id": "dtmi:example:Room;1", "@type": "Interface", "contents": [...]}]'

az dt model list \
  --dt-name myDigitalTwins                     # List all models

az dt model show \
  --dt-name myDigitalTwins \
  --dtmi "dtmi:example:Room;1"                 # Show model definition

az dt model delete \
  --dt-name myDigitalTwins \
  --dtmi "dtmi:example:Room;1"                 # Delete model (no twins can use it)

# --- Twin Instance Management ---
az dt twin create \
  --dt-name myDigitalTwins \
  --dtmi "dtmi:example:Room;1" \
  --twin-id "Room-101" \
  --properties '{"roomName": "Conference Room A", "temperature": 22.0}'  # Create twin instance

az dt twin show \
  --dt-name myDigitalTwins \
  --twin-id "Room-101"                         # Show twin

az dt twin update \
  --dt-name myDigitalTwins \
  --twin-id "Room-101" \
  --json-patch '[{"op": "replace", "path": "/temperature", "value": 24.5}]'  # Update twin property

az dt twin query \
  --dt-name myDigitalTwins \
  --query-command "SELECT * FROM DIGITALTWINS WHERE IS_OF_MODEL('dtmi:example:Room;1')"  # Query twin graph

az dt twin delete \
  --dt-name myDigitalTwins \
  --twin-id "Room-101"                         # Delete twin

# --- Relationship Management ---
az dt twin relationship create \
  --dt-name myDigitalTwins \
  --twin-id "Building-1" \
  --relationship-id "Building-1-contains-Floor-1" \
  --relationship "contains" \
  --target "Floor-1"                           # Create relationship between twins

az dt twin relationship list \
  --dt-name myDigitalTwins \
  --twin-id "Building-1"                       # List all relationships for a twin

az dt twin relationship delete \
  --dt-name myDigitalTwins \
  --twin-id "Building-1" \
  --relationship-id "Building-1-contains-Floor-1"  # Delete relationship

# --- Event Routes ---
az dt route create \
  --dt-name myDigitalTwins \
  --rn twin-change-route \
  --endpoint-name myEventHubEndpoint \
  --filter "type = 'Microsoft.DigitalTwins.Twin.Update'"  # Route twin updates to Event Hub

az dt route list \
  --dt-name myDigitalTwins                     # List event routes

az dt route delete \
  --dt-name myDigitalTwins \
  --rn twin-change-route                       # Delete event route

# --- Endpoints ---
az dt endpoint create eventhub \
  --dt-name myDigitalTwins \
  --en myEventHubEndpoint \
  --eventhub-resource-group myRG \
  --eventhub-namespace myEventHubNS \
  --eventhub myEventHub                        # Add Event Hub endpoint

az dt endpoint list --dt-name myDigitalTwins  # List endpoints
```
