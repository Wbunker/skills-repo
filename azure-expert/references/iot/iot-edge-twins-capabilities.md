# IoT Edge & Digital Twins — Capabilities Reference
For CLI commands, see [iot-edge-twins-cli.md](iot-edge-twins-cli.md).

## Azure IoT Edge

**Purpose**: Run cloud intelligence (AI inference, stream analytics, custom code) directly on edge devices using containerized modules. Enables local processing, offline operation, and reduced data egress costs.

### Architecture

| Component | Description |
|---|---|
| **IoT Edge device** | Any Linux or Windows device running the IoT Edge runtime |
| **IoT Edge runtime** | Two system modules: Edge Agent and Edge Hub; installed on the device |
| **Edge Agent** | Manages module lifecycle: pull images, start/stop/restart modules, report module status as device twin |
| **Edge Hub** | Local message broker; routes messages between modules and to IoT Hub when connected |
| **Modules** | Docker-compatible containers running business logic, AI models, or protocol translation |
| **Deployment manifest** | JSON document defining which modules to run, routing config, and desired module twin properties |
| **Routes** | Message routing rules between modules and to IoT Hub (`$upstream`) |

### Key Capabilities

| Capability | Details |
|---|---|
| **Offline operation** | Edge Hub stores messages locally and syncs to IoT Hub when connectivity restored |
| **Module-to-module messaging** | Routes: `FROM /messages/modules/tempSensor/* INTO BrokeredEndpoint("/modules/analytics/inputs/input1")` |
| **Store-and-forward** | Configurable message TTL and queue size for offline scenarios |
| **Transparent gateway** | Acts as gateway for downstream (leaf) devices that connect to Edge Hub instead of IoT Hub directly |
| **Protocol translation gateway** | Modules translate non-IP protocols (Modbus, OPC-UA, BACnet) to MQTT/AMQP for IoT Hub |
| **Container registry** | Modules pulled from any Docker-compatible registry (ACR, Docker Hub) |
| **Module twins** | Each module has a twin; desired properties pushed from cloud, reported properties from device |

### Module Sources

- **Azure Marketplace**: Pre-built modules (Azure Stream Analytics, Custom Vision, NVIDIA DeepStream, Modbus OPC Publisher, SQL Edge, Machine Learning)
- **Azure Container Registry**: Custom-built modules pushed by CI/CD pipeline
- **Docker Hub**: Open-source community modules
- **IoT Edge Dev Tool**: Scaffold, build, and debug modules locally before deploying

### Deployment Manifest Example

```json
{
  "modulesContent": {
    "$edgeAgent": {
      "properties.desired": {
        "schemaVersion": "1.1",
        "runtime": {"type": "docker", "settings": {"minDockerVersion": "v1.25"}},
        "systemModules": {
          "edgeAgent": {"type": "docker", "settings": {"image": "mcr.microsoft.com/azureiotedge-agent:1.5"}},
          "edgeHub": {"type": "docker", "settings": {"image": "mcr.microsoft.com/azureiotedge-hub:1.5"}, "env": {"OptimizeForPerformance": {"value": "false"}}}
        },
        "modules": {
          "tempSensor": {"type": "docker", "status": "running", "restartPolicy": "always",
            "settings": {"image": "mcr.microsoft.com/azureiotedge-simulated-temperature-sensor:1.0"}}
        }
      }
    },
    "$edgeHub": {
      "properties.desired": {
        "schemaVersion": "1.2",
        "routes": {
          "tempToCloud": "FROM /messages/modules/tempSensor/* INTO $upstream"
        }
      }
    }
  }
}
```

### At-Scale Deployments

- **Automatic deployments**: Target devices by twin tags (e.g., `tags.location = 'factory-A'`); applied to all matching devices
- **Layered deployments**: Stack partial deployment manifests; each layer merges with the base
- **Priority**: Higher priority number wins when multiple deployments target the same device
- **Metrics**: Track target/applied/reporting/success module counts per deployment

---

## Azure Digital Twins

**Purpose**: Build comprehensive graph-based models of physical environments (buildings, factories, cities, supply chains). Represents entities and their relationships, enabling simulation, analytics, and integration with live IoT data.

### Core Concepts

| Concept | Description |
|---|---|
| **DTDL** | Digital Twin Definition Language; JSON-LD schema for defining twin models (interfaces) |
| **Twin graph** | Live graph of twin instances and their relationships; queryable via SQL-like language |
| **Model** | DTDL interface definition: properties, telemetry, relationships, components |
| **Twin instance** | Instantiation of a model; stores current property values |
| **Relationship** | Directed, named edge between two twins (e.g., Building `contains` Floor) |
| **Component** | Reusable sub-model embedded within another model |
| **Event routes** | Route twin changes, telemetry, and lifecycle events to Event Grid, Event Hubs, or Service Bus |
| **Azure Maps integration** | Visualize twins geographically |

### DTDL Model Example

```json
{
  "@id": "dtmi:example:Room;1",
  "@type": "Interface",
  "displayName": "Room",
  "contents": [
    {"@type": "Property", "name": "roomName", "schema": "string"},
    {"@type": "Property", "name": "temperature", "schema": "double", "writable": true},
    {"@type": "Telemetry", "name": "humidity", "schema": "double"},
    {"@type": "Relationship", "name": "containsDevice", "target": "dtmi:example:Device;1"}
  ]
}
```

### Twin Graph Query Language

```sql
-- Get all twins of type Room
SELECT * FROM DIGITALTWINS WHERE IS_OF_MODEL('dtmi:example:Room;1')

-- Get rooms above 25°C
SELECT * FROM DIGITALTWINS WHERE IS_OF_MODEL('dtmi:example:Room;1') AND temperature > 25

-- Traverse relationships: find all devices in a building
SELECT Device FROM DIGITALTWINS Building
JOIN Floor RELATED Building.contains
JOIN Room RELATED Floor.contains
JOIN Device RELATED Room.containsDevice
WHERE Building.$dtId = 'Building-1'
```

### Integration Patterns

| Integration | Description |
|---|---|
| **IoT Hub → Digital Twins** | Azure Function triggered by IoT Hub messages; updates twin properties via REST API |
| **Event routing** | Twin changes → Event Grid → downstream consumers (Time Series Insights, custom APIs) |
| **Azure Data Explorer** | Export twin history to ADX for time-series analytics |
| **3D Scenes Studio** | Visual overlay of twin data on 3D models (buildings, factory floors) |
| **Power BI** | Connect to Digital Twins data for dashboards |

### 3D Scenes Studio

- Link Digital Twins instance to a 3D model (glTF/glb format stored in Azure Storage)
- Map twin properties to visual behaviors (color, scale, visibility) in 3D scene
- Create widgets that display live twin property values on 3D scene elements
- Share scenes via embeddable URL for operators and stakeholders
