# IoT Hub & DPS — CLI Reference
For service concepts, see [iot-hub-capabilities.md](iot-hub-capabilities.md).

## Azure IoT Hub

```bash
# Install IoT extension if needed
az extension add --name azure-iot

# --- IoT Hub Management ---
az iot hub create \
  --resource-group myRG \
  --name myIoTHub \
  --sku S1 \
  --units 1 \
  --location eastus                              # Create IoT Hub (Standard tier, 1 unit)

az iot hub list --resource-group myRG           # List IoT Hubs
az iot hub show --name myIoTHub --resource-group myRG  # Get hub details
az iot hub show-stats --name myIoTHub --resource-group myRG  # Message quota usage

az iot hub update \
  --name myIoTHub \
  --resource-group myRG \
  --set properties.routing.fallbackRoute.isEnabled=true  # Update hub property

az iot hub delete \
  --name myIoTHub \
  --resource-group myRG                         # Delete IoT Hub

# Show connection strings
az iot hub connection-string show \
  --hub-name myIoTHub \
  --policy-name iothubowner                     # Get owner connection string

az iot hub connection-string show \
  --hub-name myIoTHub \
  --policy-name service                         # Get service connection string
```

## Device Identity Management

```bash
# --- Device Identity ---
az iot hub device-identity create \
  --hub-name myIoTHub \
  --device-id myDevice01                        # Create device with symmetric key auth

az iot hub device-identity create \
  --hub-name myIoTHub \
  --device-id myDevice02 \
  --auth-method x509_thumbprint \
  --primary-thumbprint <SHA1-thumbprint> \
  --secondary-thumbprint <SHA1-thumbprint>      # Create device with X.509 thumbprint auth

az iot hub device-identity list \
  --hub-name myIoTHub                           # List all device identities

az iot hub device-identity list \
  --hub-name myIoTHub --output table            # Tabular view

az iot hub device-identity show \
  --hub-name myIoTHub \
  --device-id myDevice01                        # Get device details

az iot hub device-identity delete \
  --hub-name myIoTHub \
  --device-id myDevice01                        # Delete device identity

az iot hub device-identity connection-string show \
  --hub-name myIoTHub \
  --device-id myDevice01                        # Get device connection string

az iot hub device-identity export \
  --hub-name myIoTHub \
  --include-keys \
  --blob-container-uri "https://mystorageacct.blob.core.windows.net/iot-export?sas"  # Bulk export

# --- Device Twins ---
az iot hub device-twin show \
  --hub-name myIoTHub \
  --device-id myDevice01                        # View full device twin JSON

az iot hub device-twin update \
  --hub-name myIoTHub \
  --device-id myDevice01 \
  --desired '{"telemetryInterval": 60}'         # Update desired properties

az iot hub device-twin update \
  --hub-name myIoTHub \
  --device-id myDevice01 \
  --tags '{"location": "building-A", "floor": 3}'  # Update tags
```

## Messaging & Commands

```bash
# --- Device-to-Cloud Messages ---
az iot device send-d2c-message \
  --hub-name myIoTHub \
  --device-id myDevice01 \
  --data '{"temperature": 22.5, "humidity": 65}'  # Simulate D2C message from device

az iot device send-d2c-message \
  --hub-name myIoTHub \
  --device-id myDevice01 \
  --data '{"alert": "overheat"}' \
  --properties "contentType=application/json;charset=utf-8"  # With system properties

# --- Cloud-to-Device Messages ---
az iot device c2d-message send \
  --hub-name myIoTHub \
  --device-id myDevice01 \
  --data '{"command": "restart"}' \
  --ack full                                    # Send C2D message with ACK

az iot device c2d-message receive \
  --hub-name myIoTHub \
  --device-id myDevice01                        # Receive pending C2D message (as device)

# --- Direct Methods ---
az iot hub invoke-device-method \
  --hub-name myIoTHub \
  --device-id myDevice01 \
  --method-name reboot \
  --method-payload '{"delay": 5}'              # Invoke direct method on device

# --- Monitor Events ---
az iot hub monitor-events \
  --hub-name myIoTHub                           # Monitor all D2C messages real-time

az iot hub monitor-events \
  --hub-name myIoTHub \
  --device-id myDevice01                        # Filter to one device

az iot hub monitor-events \
  --hub-name myIoTHub \
  --timeout 30                                  # Monitor for 30 seconds then exit
```

## Message Routing

```bash
# --- Custom Endpoints ---
az iot hub message-endpoint create \
  --hub-name myIoTHub \
  --endpoint-name myEventHub \
  --endpoint-type eventhub \
  --resource-group myRG \
  --connection-string "Endpoint=sb://myns.servicebus.windows.net/..."  # Add Event Hub endpoint

az iot hub message-endpoint create \
  --hub-name myIoTHub \
  --endpoint-name myStorage \
  --endpoint-type azurestoragecontainer \
  --resource-group myRG \
  --connection-string "DefaultEndpointsProtocol=https;AccountName=..." \
  --container mycontainer \
  --file-name-format '{iothub}/{partition}/{YYYY}/{MM}/{DD}/{HH}/{mm}'  # Storage endpoint

# --- Message Routes ---
az iot hub message-route create \
  --hub-name myIoTHub \
  --resource-group myRG \
  --route-name alerts-route \
  --endpoint-name myEventHub \
  --source DeviceMessages \
  --condition "temperatureAlert = true"         # Route filtered messages to endpoint

az iot hub message-route show \
  --hub-name myIoTHub \
  --resource-group myRG \
  --route-name alerts-route                     # View route

az iot hub message-route list \
  --hub-name myIoTHub \
  --resource-group myRG                         # List all routes

az iot hub message-route test \
  --hub-name myIoTHub \
  --resource-group myRG \
  --route-name alerts-route \
  --body '{"temperatureAlert": true}' \
  --properties "contentType=application/json"   # Test a route condition
```

## Device Provisioning Service (DPS)

```bash
# --- DPS Management ---
az iot dps create \
  --resource-group myRG \
  --name myDPS \
  --location eastus                             # Create DPS instance

az iot dps list --resource-group myRG          # List DPS instances
az iot dps show --name myDPS --resource-group myRG  # Get DPS details

# Link IoT Hub to DPS
az iot dps linked-hub create \
  --dps-name myDPS \
  --resource-group myRG \
  --connection-string "HostName=myIoTHub.azure-devices.net;..." \
  --location eastus

# --- Individual Enrollment ---
az iot dps enrollment create \
  --dps-name myDPS \
  --resource-group myRG \
  --enrollment-id myDevice01 \
  --attestation-type symmetrickey \
  --device-id myDevice01 \
  --hub-host-name myIoTHub.azure-devices.net   # Individual enrollment with symmetric key

az iot dps enrollment create \
  --dps-name myDPS \
  --resource-group myRG \
  --enrollment-id mySecureDevice \
  --attestation-type x509 \
  --certificate-path ./device-cert.pem          # Individual enrollment with X.509 cert

az iot dps enrollment list \
  --dps-name myDPS --resource-group myRG        # List individual enrollments

az iot dps enrollment show \
  --dps-name myDPS --resource-group myRG \
  --enrollment-id myDevice01                    # Show enrollment details

# --- Enrollment Groups ---
az iot dps enrollment-group create \
  --dps-name myDPS \
  --resource-group myRG \
  --enrollment-id factory-line-A \
  --attestation-type x509 \
  --certificate-path ./ca-cert.pem \
  --provisioning-status enabled                 # Group enrollment with CA cert

az iot dps enrollment-group create \
  --dps-name myDPS \
  --resource-group myRG \
  --enrollment-id dev-devices \
  --attestation-type symmetrickey               # Group enrollment with symmetric key

az iot dps enrollment-group list \
  --dps-name myDPS --resource-group myRG        # List enrollment groups
```
