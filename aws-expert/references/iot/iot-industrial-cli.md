# AWS IoT Industrial — CLI Reference

For service concepts, see [iot-industrial-capabilities.md](iot-industrial-capabilities.md).

---

## AWS IoT SiteWise — `aws iotsitewise`

### Asset Models

```bash
# --- Create an asset model ---
aws iotsitewise create-asset-model \
  --asset-model-name "CNC Machine" \
  --asset-model-description "Model for CNC machining centers" \
  --asset-model-properties '[
    {
      "name": "SerialNumber",
      "dataType": "STRING",
      "type": {"attribute": {"defaultValue": "UNKNOWN"}}
    },
    {
      "name": "SpindleSpeed",
      "dataType": "DOUBLE",
      "unit": "RPM",
      "type": {"measurement": {}}
    },
    {
      "name": "MotorTemperature",
      "dataType": "DOUBLE",
      "unit": "Celsius",
      "type": {"measurement": {}}
    },
    {
      "name": "MotorTemperatureF",
      "dataType": "DOUBLE",
      "unit": "Fahrenheit",
      "type": {
        "transform": {
          "expression": "temp_c * 9 / 5 + 32",
          "variables": [{"name": "temp_c", "value": {"propertyId": "<MotorTemperature-property-id>"}}]
        }
      }
    },
    {
      "name": "AvgSpindleSpeed1Hr",
      "dataType": "DOUBLE",
      "unit": "RPM",
      "type": {
        "metric": {
          "expression": "avg(speed)",
          "variables": [{"name": "speed", "value": {"propertyId": "<SpindleSpeed-property-id>"}}],
          "window": {"tumbling": {"interval": "1h"}}
        }
      }
    }
  ]' \
  --asset-model-composite-models '[
    {
      "name": "SpindleAlarm",
      "type": "AWS/ALARM",
      "properties": [
        {"name": "AWS/ALARM_TYPE", "dataType": "STRING", "type": {"attribute": {"defaultValue": "IOT_EVENTS"}}},
        {"name": "AWS/ALARM_STATE", "dataType": "STRUCT", "dataTypeSpec": "AWS/ALARM_STATE", "type": {"measurement": {}}}
      ]
    }
  ]'

aws iotsitewise describe-asset-model --asset-model-id <model-id>
aws iotsitewise list-asset-models
aws iotsitewise list-asset-models --asset-model-types ASSET_MODEL  # ASSET_MODEL | COMPONENT_MODEL

aws iotsitewise update-asset-model \
  --asset-model-id <model-id> \
  --asset-model-name "CNC Machine v2" \
  --asset-model-properties file://updated-properties.json

aws iotsitewise delete-asset-model --asset-model-id <model-id>

# --- Asset model hierarchies ---
aws iotsitewise update-asset-model \
  --asset-model-id <factory-model-id> \
  --asset-model-name "Factory" \
  --asset-model-hierarchies '[
    {
      "name": "ProductionLines",
      "childAssetModelId": "<production-line-model-id>"
    }
  ]'
```

---

### Assets

```bash
# --- Create an asset ---
aws iotsitewise create-asset \
  --asset-name "CNC-001" \
  --asset-model-id <model-id> \
  --asset-description "CNC machine on line 1"

aws iotsitewise describe-asset --asset-id <asset-id>
aws iotsitewise list-assets --asset-model-id <model-id>
aws iotsitewise list-assets --filter TOP_LEVEL  # top-level assets only

aws iotsitewise update-asset \
  --asset-id <asset-id> \
  --asset-name "CNC-001-Updated"

aws iotsitewise delete-asset --asset-id <asset-id>

# --- Manage asset hierarchy associations ---
aws iotsitewise associate-assets \
  --asset-id <factory-asset-id> \
  --hierarchy-id <ProductionLines-hierarchy-id> \
  --child-asset-id <line1-asset-id>

aws iotsitewise disassociate-assets \
  --asset-id <factory-asset-id> \
  --hierarchy-id <ProductionLines-hierarchy-id> \
  --child-asset-id <line1-asset-id>

aws iotsitewise list-associated-assets \
  --asset-id <factory-asset-id> \
  --hierarchy-id <ProductionLines-hierarchy-id>

# --- Update attribute value ---
aws iotsitewise update-asset-property \
  --asset-id <asset-id> \
  --property-id <SerialNumber-property-id> \
  --property-alias "/factory/cnc001/serialnumber" \
  --property-notification-state ENABLED

# --- Ingest property values ---
aws iotsitewise batch-put-asset-property-value \
  --entries '[
    {
      "entryId": "entry-001",
      "assetId": "<asset-id>",
      "propertyId": "<SpindleSpeed-property-id>",
      "propertyValues": [
        {
          "value": {"doubleValue": 3200.5},
          "timestamp": {"timeInSeconds": 1700000000, "offsetInNanos": 0},
          "quality": "GOOD"
        }
      ]
    },
    {
      "entryId": "entry-002",
      "assetId": "<asset-id>",
      "propertyId": "<MotorTemperature-property-id>",
      "propertyValues": [
        {
          "value": {"doubleValue": 72.3},
          "timestamp": {"timeInSeconds": 1700000000, "offsetInNanos": 0},
          "quality": "GOOD"
        }
      ]
    }
  ]'

# Ingest via property alias (no asset/property IDs needed)
aws iotsitewise batch-put-asset-property-value \
  --entries '[
    {
      "entryId": "alias-entry-001",
      "propertyAlias": "/factory/cnc001/spindle_speed",
      "propertyValues": [
        {"value": {"doubleValue": 3250.0}, "timestamp": {"timeInSeconds": 1700000001}}
      ]
    }
  ]'
```

---

### Querying Asset Data

```bash
# --- Get latest property value ---
aws iotsitewise get-asset-property-value \
  --asset-id <asset-id> \
  --property-id <SpindleSpeed-property-id>

# By alias
aws iotsitewise get-asset-property-value \
  --property-alias "/factory/cnc001/spindle_speed"

# --- Get historical values ---
aws iotsitewise get-asset-property-value-history \
  --asset-id <asset-id> \
  --property-id <SpindleSpeed-property-id> \
  --start-date 2024-01-01T00:00:00Z \
  --end-date 2024-01-02T00:00:00Z \
  --max-results 100 \
  --qualities GOOD

# --- Get aggregated values (metrics) ---
aws iotsitewise get-asset-property-aggregates \
  --asset-id <asset-id> \
  --property-id <SpindleSpeed-property-id> \
  --aggregate-types AVERAGE MAXIMUM MINIMUM \
  --resolution 1h \
  --start-date 2024-01-01T00:00:00Z \
  --end-date 2024-01-02T00:00:00Z

# --- Batch get latest values ---
aws iotsitewise batch-get-asset-property-value \
  --entries '[
    {"entryId": "e1", "assetId": "<asset-id-1>", "propertyId": "<prop-id-1>"},
    {"entryId": "e2", "propertyAlias": "/factory/cnc002/motor_temp"}
  ]'

# --- Execute SQL-like queries ---
aws iotsitewise execute-query \
  --query-statement "SELECT a.name, p.propertyValue.value
    FROM asset a
    JOIN assetProperty p ON a.assetId = p.assetId
    WHERE a.assetModelId = '<model-id>'
    AND p.propertyName = 'SpindleSpeed'"
```

---

### Gateways and Portals

```bash
# --- Gateways ---
aws iotsitewise create-gateway \
  --gateway-name "Factory1-Gateway" \
  --gateway-platform '{"greengrass": {"groupArn": "arn:aws:greengrass:us-east-1:123456789012:/greengrass/groups/<group-id>"}}'
  # Or for Greengrass v2:
  # "greengrassV2": {"coreDeviceThingName": "FactoryGatewayDevice"}

aws iotsitewise describe-gateway --gateway-id <gateway-id>
aws iotsitewise list-gateways

aws iotsitewise update-gateway-capability-configuration \
  --gateway-id <gateway-id> \
  --capability-namespace "iotsitewise:opcuacollector:2" \
  --capability-configuration file://opc-ua-config.json

aws iotsitewise describe-gateway-capability-configuration \
  --gateway-id <gateway-id> \
  --capability-namespace "iotsitewise:opcuacollector:2"

aws iotsitewise delete-gateway --gateway-id <gateway-id>

# --- Portals ---
aws iotsitewise create-portal \
  --portal-name "Factory Operations" \
  --portal-contact-email "ops-admin@example.com" \
  --role-arn arn:aws:iam::123456789012:role/SiteWiseMonitorRole \
  --portal-auth-mode IAM  # IAM | SSO

aws iotsitewise describe-portal --portal-id <portal-id>
aws iotsitewise list-portals

aws iotsitewise delete-portal --portal-id <portal-id> --client-token <token>

# --- Projects within a portal ---
aws iotsitewise create-project \
  --portal-id <portal-id> \
  --project-name "Line 1 Operations"

aws iotsitewise list-projects --portal-id <portal-id>
aws iotsitewise delete-project --project-id <project-id> --client-token <token>
```

---

## AWS IoT TwinMaker — `aws iottwinmaker`

### Workspaces

```bash
# --- Create a workspace ---
aws iottwinmaker create-workspace \
  --workspace-id FactoryTwin \
  --s3-location arn:aws:s3:::my-twinmaker-workspace-bucket \
  --role arn:aws:iam::123456789012:role/TwinMakerRole \
  --description "Digital twin for Atlanta factory"

aws iottwinmaker get-workspace --workspace-id FactoryTwin
aws iottwinmaker list-workspaces

aws iottwinmaker update-workspace \
  --workspace-id FactoryTwin \
  --description "Updated factory digital twin"

aws iottwinmaker delete-workspace --workspace-id FactoryTwin
```

---

### Component Types

```bash
# --- Create a component type (SiteWise connector) ---
aws iottwinmaker create-component-type \
  --workspace-id FactoryTwin \
  --component-type-id "com.example.SiteWiseConnector" \
  --description "Links entities to SiteWise asset properties" \
  --functions '{
    "dataReader": {
      "implementedBy": {
        "isNative": true,
        "lambda": {"arn": "arn:aws:lambda:us-east-1:123456789012:function:TwinMakerSiteWiseConnector"}
      }
    }
  }' \
  --property-definitions '{
    "siteWiseAssetId": {
      "dataType": {"type": "STRING"},
      "isRequiredInEntity": true,
      "isStoredExternally": false
    },
    "temperature": {
      "dataType": {"type": "DOUBLE"},
      "isStoredExternally": true,
      "isTimeSeries": true
    }
  }'

aws iottwinmaker get-component-type \
  --workspace-id FactoryTwin \
  --component-type-id "com.example.SiteWiseConnector"

aws iottwinmaker list-component-types --workspace-id FactoryTwin

aws iottwinmaker delete-component-type \
  --workspace-id FactoryTwin \
  --component-type-id "com.example.SiteWiseConnector"
```

---

### Entities

```bash
# --- Create an entity ---
aws iottwinmaker create-entity \
  --workspace-id FactoryTwin \
  --entity-name "CNC-Machine-001" \
  --entity-id "cnc-001" \
  --description "CNC machine on production line 1" \
  --parent-entity-id "production-line-1" \
  --components '{
    "SiteWiseData": {
      "componentTypeId": "com.amazon.iotsitewise.connector",
      "properties": {
        "sitewiseAssetId": {"value": {"stringValue": "<sitewise-asset-id>"}}
      }
    }
  }'

aws iottwinmaker get-entity \
  --workspace-id FactoryTwin \
  --entity-id "cnc-001"

aws iottwinmaker list-entities --workspace-id FactoryTwin

aws iottwinmaker update-entity \
  --workspace-id FactoryTwin \
  --entity-id "cnc-001" \
  --entity-name "CNC-Machine-001-Updated"

aws iottwinmaker delete-entity \
  --workspace-id FactoryTwin \
  --entity-id "cnc-001"

# --- Query entity properties (time-series data) ---
aws iottwinmaker get-property-value \
  --workspace-id FactoryTwin \
  --entity-id "cnc-001" \
  --component-name "SiteWiseData" \
  --selected-properties '["temperature", "spindleSpeed"]'

aws iottwinmaker get-property-value-history \
  --workspace-id FactoryTwin \
  --entity-id "cnc-001" \
  --component-name "SiteWiseData" \
  --selected-properties '["temperature"]' \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z \
  --interpolation '{"interpolationType": "LINEAR", "intervalInSeconds": 60}'
```

---

### Scenes

```bash
# --- Create a scene ---
aws iottwinmaker create-scene \
  --workspace-id FactoryTwin \
  --scene-id "FactoryFloorScene" \
  --content-location "s3://my-twinmaker-workspace-bucket/scenes/factory-floor.json" \
  --description "3D scene of factory floor"

aws iottwinmaker get-scene \
  --workspace-id FactoryTwin \
  --scene-id "FactoryFloorScene"

aws iottwinmaker list-scenes --workspace-id FactoryTwin

aws iottwinmaker update-scene \
  --workspace-id FactoryTwin \
  --scene-id "FactoryFloorScene" \
  --content-location "s3://my-twinmaker-workspace-bucket/scenes/factory-floor-v2.json"

aws iottwinmaker delete-scene \
  --workspace-id FactoryTwin \
  --scene-id "FactoryFloorScene"
```

---

### Knowledge Graph Queries

```bash
# --- Execute a PartiQL query against the entity graph ---
aws iottwinmaker execute-query \
  --workspace-id FactoryTwin \
  --query-statement "SELECT e.entityName, e.entityId
    FROM EntityGraph
    MATCH (e)-[:isChildOf]->(p)
    WHERE p.entityId = 'production-line-1'"

aws iottwinmaker list-sync-jobs --workspace-id FactoryTwin
```

---

## AWS IoT FleetWise — `aws iotfleetwise`

### Signal Catalog

```bash
# --- Create signal catalog ---
aws iotfleetwise create-signal-catalog \
  --name VehicleSignalCatalog \
  --description "Catalog of all vehicle signals" \
  --nodes '[
    {
      "branch": {
        "fullyQualifiedName": "Vehicle",
        "description": "Root vehicle branch"
      }
    },
    {
      "branch": {
        "fullyQualifiedName": "Vehicle.Engine",
        "description": "Engine signals"
      }
    },
    {
      "sensor": {
        "fullyQualifiedName": "Vehicle.Engine.RPM",
        "description": "Engine revolutions per minute",
        "dataType": "FLOAT",
        "unit": "rpm",
        "min": 0.0,
        "max": 10000.0
      }
    },
    {
      "sensor": {
        "fullyQualifiedName": "Vehicle.Engine.CoolantTemperature",
        "description": "Engine coolant temperature",
        "dataType": "FLOAT",
        "unit": "celsius"
      }
    },
    {
      "sensor": {
        "fullyQualifiedName": "Vehicle.Speed",
        "description": "Vehicle speed",
        "dataType": "FLOAT",
        "unit": "km/h"
      }
    }
  ]'

aws iotfleetwise get-signal-catalog --name VehicleSignalCatalog
aws iotfleetwise list-signal-catalogs

aws iotfleetwise update-signal-catalog \
  --name VehicleSignalCatalog \
  --nodes-to-add '[{"sensor": {"fullyQualifiedName": "Vehicle.FuelLevel", "dataType": "FLOAT", "unit": "percent"}}]'

aws iotfleetwise list-signal-catalog-nodes --name VehicleSignalCatalog
aws iotfleetwise delete-signal-catalog --name VehicleSignalCatalog
```

---

### Vehicle Model (Model Manifest) and Decoder Manifest

```bash
# --- Create model manifest ---
aws iotfleetwise create-model-manifest \
  --name "SedanModelV1" \
  --signal-catalog-arn arn:aws:iotfleetwise:us-east-1:123456789012:signal-catalog/VehicleSignalCatalog \
  --nodes '["Vehicle.Engine.RPM", "Vehicle.Engine.CoolantTemperature", "Vehicle.Speed", "Vehicle.FuelLevel"]'

aws iotfleetwise update-model-manifest \
  --name "SedanModelV1" \
  --status ACTIVE   # DRAFT → ACTIVE (cannot edit after ACTIVE)

aws iotfleetwise get-model-manifest --name "SedanModelV1"
aws iotfleetwise list-model-manifests
aws iotfleetwise delete-model-manifest --name "SedanModelV1"

# --- Create decoder manifest (CAN decoder) ---
aws iotfleetwise create-decoder-manifest \
  --name "SedanDecoderV1" \
  --model-manifest-arn arn:aws:iotfleetwise:us-east-1:123456789012:model-manifest/SedanModelV1 \
  --network-interfaces '[
    {
      "interfaceId": "CAN0",
      "type": "CAN_INTERFACE",
      "canInterface": {
        "name": "can0",
        "protocolName": "CAN",
        "protocolVersion": "2.0B"
      }
    }
  ]' \
  --signal-decoders '[
    {
      "fullyQualifiedName": "Vehicle.Engine.RPM",
      "type": "CAN_SIGNAL",
      "interfaceId": "CAN0",
      "canSignal": {
        "messageId": 288,
        "isBigEndian": false,
        "isSigned": false,
        "startBit": 0,
        "length": 16,
        "factor": 0.25,
        "offset": 0
      }
    },
    {
      "fullyQualifiedName": "Vehicle.Speed",
      "type": "OBD_SIGNAL",
      "interfaceId": "CAN0",
      "obdSignal": {
        "pidResponseLength": 2,
        "serviceMode": 1,
        "pid": 13,
        "scaling": 1.0,
        "offset": 0.0,
        "startByte": 0,
        "byteLength": 1,
        "bitMaskLength": 8,
        "bitRightShift": 0
      }
    }
  ]'

aws iotfleetwise update-decoder-manifest \
  --name "SedanDecoderV1" \
  --status ACTIVE

aws iotfleetwise get-decoder-manifest --name "SedanDecoderV1"
aws iotfleetwise list-decoder-manifests
aws iotfleetwise delete-decoder-manifest --name "SedanDecoderV1"
```

---

### Vehicles and Fleets

```bash
# --- Create vehicles ---
aws iotfleetwise create-vehicle \
  --vehicle-name "VIN1HGBH41JXMN109186" \
  --model-manifest-arn arn:aws:iotfleetwise:us-east-1:123456789012:model-manifest/SedanModelV1 \
  --decoder-manifest-arn arn:aws:iotfleetwise:us-east-1:123456789012:decoder-manifest/SedanDecoderV1 \
  --association-behavior CreateIotThing \
  --attributes '{"make": "Honda", "model": "Accord", "year": "2022"}'

aws iotfleetwise get-vehicle --vehicle-name "VIN1HGBH41JXMN109186"
aws iotfleetwise list-vehicles
aws iotfleetwise list-vehicles --model-manifest-arn arn:aws:iotfleetwise:us-east-1:123456789012:model-manifest/SedanModelV1

aws iotfleetwise update-vehicle \
  --vehicle-name "VIN1HGBH41JXMN109186" \
  --attributes '{"region": "northeast"}'

aws iotfleetwise delete-vehicle --vehicle-name "VIN1HGBH41JXMN109186"

# --- Batch create vehicles ---
aws iotfleetwise batch-create-vehicle \
  --vehicles file://vehicles-batch.json

# --- Fleets ---
aws iotfleetwise create-fleet \
  --fleet-id "NortheastFleet" \
  --description "All vehicles in the northeast region" \
  --signal-catalog-arn arn:aws:iotfleetwise:us-east-1:123456789012:signal-catalog/VehicleSignalCatalog

aws iotfleetwise associate-vehicle-fleet \
  --vehicle-name "VIN1HGBH41JXMN109186" \
  --fleet-id "NortheastFleet"

aws iotfleetwise disassociate-vehicle-fleet \
  --vehicle-name "VIN1HGBH41JXMN109186" \
  --fleet-id "NortheastFleet"

aws iotfleetwise list-vehicles-in-fleet --fleet-id "NortheastFleet"
aws iotfleetwise list-fleets-for-vehicle --vehicle-name "VIN1HGBH41JXMN109186"
aws iotfleetwise get-fleet --fleet-id "NortheastFleet"
aws iotfleetwise list-fleets
aws iotfleetwise delete-fleet --fleet-id "NortheastFleet"
```

---

### Campaigns

```bash
# --- Create a time-based campaign ---
aws iotfleetwise create-campaign \
  --name "BaselineTelemetry" \
  --description "Collect baseline vehicle telemetry every 30 seconds" \
  --signal-catalog-arn arn:aws:iotfleetwise:us-east-1:123456789012:signal-catalog/VehicleSignalCatalog \
  --target-arn arn:aws:iotfleetwise:us-east-1:123456789012:fleet/NortheastFleet \
  --collection-scheme '{"timeBased": {"periodMs": 30000}}' \
  --signals-to-collect '[
    {"name": "Vehicle.Speed", "maxSampleCount": 10},
    {"name": "Vehicle.Engine.RPM", "maxSampleCount": 10},
    {"name": "Vehicle.FuelLevel"}
  ]' \
  --data-destination-configs '[
    {
      "s3Config": {
        "bucketArn": "arn:aws:s3:::my-vehicle-data-bucket",
        "dataFormat": "PARQUET",
        "storageCompressionFormat": "SNAPPY",
        "prefix": "fleetwise/baseline/"
      }
    }
  ]' \
  --compression SNAPPY \
  --priority 0 \
  --start-time 2024-01-01T00:00:00Z \
  --expiry-time 2025-01-01T00:00:00Z

# --- Create a condition-based campaign ---
aws iotfleetwise create-campaign \
  --name "HighRPMCapture" \
  --signal-catalog-arn arn:aws:iotfleetwise:us-east-1:123456789012:signal-catalog/VehicleSignalCatalog \
  --target-arn arn:aws:iotfleetwise:us-east-1:123456789012:fleet/NortheastFleet \
  --collection-scheme '{
    "conditionBased": {
      "expression": "$variable.`Vehicle.Engine.RPM` > 5000",
      "minimumTriggerIntervalMs": 5000,
      "triggerMode": "RISING_EDGE",
      "conditionLanguageVersion": 1
    }
  }' \
  --signals-to-collect '[
    {"name": "Vehicle.Engine.RPM"},
    {"name": "Vehicle.Speed"},
    {"name": "Vehicle.Engine.CoolantTemperature"}
  ]' \
  --data-destination-configs '[
    {
      "timestreamConfig": {
        "timestreamTableArn": "arn:aws:timestream:us-east-1:123456789012:database/VehicleDB/table/TelemetryTable",
        "executionRoleArn": "arn:aws:iam::123456789012:role/FleetWiseTimestreamRole"
      }
    }
  ]'

# --- Manage campaign lifecycle ---
aws iotfleetwise get-campaign --name "BaselineTelemetry"
aws iotfleetwise list-campaigns
aws iotfleetwise list-campaigns --status WAITING_FOR_APPROVAL  # CREATING | WAITING_FOR_APPROVAL | RUNNING | SUSPENDED

# Approve campaign (move from WAITING_FOR_APPROVAL → RUNNING)
aws iotfleetwise update-campaign \
  --name "BaselineTelemetry" \
  --action APPROVE

# Suspend a running campaign
aws iotfleetwise update-campaign \
  --name "BaselineTelemetry" \
  --action SUSPEND

# Resume a suspended campaign
aws iotfleetwise update-campaign \
  --name "BaselineTelemetry" \
  --action RESUME

aws iotfleetwise delete-campaign --name "BaselineTelemetry"
```
