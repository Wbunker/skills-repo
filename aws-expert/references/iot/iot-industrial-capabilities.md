# AWS IoT Industrial — Capabilities Reference

For CLI commands, see [iot-industrial-cli.md](iot-industrial-cli.md).

---

## AWS IoT SiteWise

**Purpose**: Managed service for collecting, organizing, and analyzing industrial equipment data at scale. Reduces the time to build industrial data infrastructure by modeling physical assets and automating data ingestion from OPC-UA sources, MQTT, and direct API calls.

### Core Concepts

| Concept | Description |
|---|---|
| **Asset model** | Reusable schema defining the properties, metrics, transforms, and hierarchies for a class of industrial assets |
| **Asset** | An instance of an asset model; represents a specific piece of equipment or process |
| **Property** | A data stream on an asset: attribute (static), measurement (raw time-series), transform (formula applied to measurements), metric (windowed aggregation) |
| **Hierarchy** | Parent-child relationship between asset models; enables querying data up and down the physical hierarchy |
| **Gateway** | Edge software (runs on a server at the facility) that connects to OPC-UA servers and ingests data into SiteWise |
| **Portal** | Web application for operators built on top of SiteWise data; no custom coding required |
| **Project** | Logical grouping of assets and dashboards within a portal |
| **Dashboard** | Visualization of asset property data within a portal project |

---

## Asset Models

Asset models are the schema layer. You define:

### Property Types

| Type | Description |
|---|---|
| **Attribute** | Static metadata value (e.g., manufacturer, serial number, installation date); can have a default value |
| **Measurement** | Raw time-series data ingested from a device (e.g., raw temperature readings) |
| **Transform** | Formula computed from other properties using SiteWise expression language (e.g., `temperature * 9/5 + 32` to convert C→F) |
| **Metric** | Windowed aggregation over measurements or transforms: `avg()`, `sum()`, `min()`, `max()`, `count()`, `stdev()`, `latest()` over tumbling windows (1 min, 5 min, 15 min, 1 hr, 1 day) |

**Expression functions available in transforms and metrics**: `abs`, `floor`, `ceil`, `sqrt`, `ln`, `log`, `pow`, `sin`, `cos`, `tan`, `contains`, `if`, `ite`, `jp` (JSONPath), `prettyprint`

### Model Hierarchy Definitions

Asset models can define hierarchies that reference other asset models. For example, a "Factory" model has a hierarchy "ProductionLines" that references the "ProductionLine" model, which in turn references "Machines."

### Composite Models (Components)

Composite models allow embedding reusable sub-models within a parent model (e.g., an alarm composite model embedded in any asset model).

---

## Assets

Assets are instantiated from models. Each asset has:
- A **name** (human-readable)
- Property values (attribute values set per instance)
- Associated hierarchical children assets

**Property value ingestion**:
- Timestamps must be within ±7 days of current time
- Batch ingestion: up to 10 entries per `batch-put-asset-property-value` call
- Data types: `DOUBLE`, `INTEGER`, `BOOLEAN`, `STRING`
- Maximum ingestion rate: 10 data points per second per property per asset

---

## Data Ingestion Paths

| Path | Description |
|---|---|
| **SiteWise Gateway (OPC-UA)** | Gateway software on an industrial server reads OPC-UA tags; maps tags to SiteWise asset properties |
| **MQTT (via IoT Core rule)** | Devices publish MQTT; a rule action routes to SiteWise via `iotsitewise` rule action |
| **Direct API** | `BatchPutAssetPropertyValue` API call from any application |
| **SiteWise Edge** | Process and store data locally before syncing to cloud (see below) |

---

## SiteWise Edge

SiteWise Edge extends SiteWise to edge infrastructure (on-premises servers or Greengrass core devices). Two deployment options:

| Option | Description |
|---|---|
| **SiteWise Edge — AWS Managed** | Run via Greengrass components; store and process data locally; sync property values to cloud |
| **SiteWise Edge — Siemens Industrial Edge** | Native integration with Siemens Industrial Edge platform |

**Local capabilities**: Compute transforms and metrics locally, store historical data in local time-series store, serve SiteWise Monitor portals from the edge (for air-gapped facilities).

---

## SiteWise Monitor

**Purpose**: Web-based application for industrial operators and process engineers to visualize asset data without building custom web applications.

| Component | Description |
|---|---|
| **Portal** | Multi-user web application; backed by AWS SSO / IAM Identity Center for authentication |
| **Project** | Groups of assets + dashboards managed by a project administrator |
| **Dashboard** | Line charts, bar charts, scatter plots, status grids, KPI widgets showing real-time and historical property data |
| **Alarms** | Threshold-based alarms on asset properties; states: NORMAL, ACTIVE, ACKNOWLEDGED, SNOOZED, DISABLED |

---

## Important Limits

| Limit | Default |
|---|---|
| Max asset models per account | 100 (soft) |
| Max assets per account | 100,000 (soft) |
| Max properties per asset model | 200 |
| Max hierarchy levels | 10 |
| Metric computation window minimum | 1 minute |
| Data retention in SiteWise | Unlimited (pay per data point stored) |
| Batch put asset property value max entries | 10 per request |

---

## Pricing

| Resource | Basis |
|---|---|
| **Data ingestion** | Per data point ingested |
| **Data storage** | Per month per data point stored (hot tier) + cold tier archival |
| **Data queries** | Per data point retrieved |
| **Monitor portals** | Per portal per month |
| **SiteWise Edge** | Per Greengrass deployment |

---

## AWS IoT TwinMaker

**Purpose**: Build operational digital twins of physical environments — factories, buildings, industrial plants — by connecting to multiple data sources and creating 3D visualizations with real-time property overlays.

### Core Concepts

| Concept | Description |
|---|---|
| **Workspace** | Top-level container for a digital twin; backed by an S3 bucket and IAM role |
| **Entity** | Represents a physical or logical object in the twin (e.g., a pump, a room, a cooling system) |
| **Component** | Attached to an entity; links the entity to a data source via a component type connector |
| **Component type** | Schema defining the properties and data source connector for a class of component |
| **Scene** | 3D environment (GLTF/GLB model) uploaded to the workspace S3 bucket with tags binding visual nodes to entities |
| **Knowledge graph** | Graph of entity relationships queryable with PartiQL |
| **Connector** | Lambda function or built-in connector that retrieves property data from an external data source at query time |

---

## TwinMaker Data Sources (Connectors)

TwinMaker does not store telemetry; it queries data sources at read time via connectors.

| Built-in connector | Description |
|---|---|
| **IoT SiteWise** | Query SiteWise asset property values (latest and historical) |
| **Amazon Timestream** | Query time-series data from Timestream tables |
| **Amazon Kinesis Video Streams** | Stream video feeds for cameras embedded in scenes |

**Custom connectors**: Lambda functions implementing the TwinMaker connector schema (DataValue schema for reading property values and time-series data).

---

## TwinMaker Scenes

A scene is a 3D visualization layer:
1. Upload a GLTF/GLB file or Matterport scan to the workspace S3 bucket
2. Add **scene nodes** (tags) in the TwinMaker scene editor (Grafana plugin or AWS console)
3. Each tag references an **entity + component + property** to overlay live data on the 3D model
4. Widget types: data overlay, color rule (green/yellow/red), motion indicator

---

## TwinMaker Grafana Integration

AWS provides a Grafana plugin (`grafana-iot-twinmaker-app`) that enables:
- Querying TwinMaker entity properties from Grafana panels
- Embedding 3D scenes in Grafana dashboards
- Scene hierarchy browser panel

---

## AWS IoT FleetWise

**Purpose**: Collect, transform, and transfer vehicle data from connected vehicles to the cloud at scale. Define data collection campaigns based on vehicle network signals and conditions.

### Core Concepts

| Concept | Description |
|---|---|
| **Signal catalog** | Library of all possible signals (sensor readings, ECU data) in a standardized format; created from DBC files (CAN) or custom definitions |
| **Vehicle model (model manifest)** | A subset of signal catalog entries that apply to a particular vehicle model; validated against signal catalog |
| **Decoder manifest** | Specifies how raw network frames (CAN, OBD-II) map to signals; includes network interfaces, CAN/OBD decoders |
| **Vehicle** | Instance of a vehicle model; has a unique vehicle name (maps to an IoT thing) |
| **Fleet** | Named group of vehicles for targeting campaigns |
| **Campaign** | Data collection definition: target (vehicle/fleet), signals to collect, collection scheme, compression, destination |
| **Edge agent** | C++ software library embedded in the vehicle gateway/telematics control unit (TCU) |

---

## FleetWise Data Collection Schemes

| Scheme | Description |
|---|---|
| **Time-based** | Collect signals at a fixed period (e.g., every 30 seconds) |
| **Condition-based** | Collect data when an expression evaluates to true (e.g., `$variable.engineRPM > 5000`) |

---

## FleetWise Vehicle Networks

| Network type | Description |
|---|---|
| **CAN (Controller Area Network)** | Industry-standard vehicle bus; decode via DBC files |
| **OBD-II** | On-board diagnostics standard; standardized PIDs for engine data |
| **Custom (Structured)** | Arbitrary signal definitions not tied to a specific protocol |

---

## FleetWise Data Destinations

Collected data is delivered to:
- **Amazon S3**: Parquet or JSON format; organized by `vehicleName/campaignName/partitionDate`
- **Amazon Timestream**: Real-time time-series storage for immediate querying

---

## FleetWise Pricing

| Resource | Basis |
|---|---|
| **Vehicles** | Per vehicle registered per month |
| **Data collection** | Per GB of vehicle data transferred |
| **Signal catalog** | Per signal catalog entry per month (small) |
