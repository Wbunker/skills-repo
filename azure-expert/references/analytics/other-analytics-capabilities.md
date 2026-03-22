# Other Analytics Services — Capabilities

## Azure Data Explorer (ADX / Kusto)

### Service Overview

Azure Data Explorer (ADX) is a fully managed, purpose-built analytics service for real-time analysis of large volumes of log, telemetry, and time-series data. It delivers sub-second query latency over petabytes of data using the **Kusto Query Language (KQL)**.

**Best for**: Log analytics, IoT telemetry, application metrics, security events, time-series analysis, operational analytics requiring near-real-time results.

**Not for**: Transactional workloads, ad-hoc schema exploration (use Synapse Serverless SQL instead).

---

### ADX Architecture

```
ADX Cluster
└── Database
    └── Tables (immutable append-only columnar storage)
        ├── Hot cache (SSD — fastest queries)
        ├── Warm cache (HDD — intermediate)
        └── Cold cache (Azure Blob Storage — cheapest)
```

### Cluster Tiers

| Tier | Description |
|---|---|
| **Dev/Test** | Single-node, low cost, no SLA — for development only |
| **Standard** | Production, HA, multiple SKUs (L8s_v3, D14_v2, etc.) |

- **Scale out**: Add/remove nodes dynamically (2–1000 nodes).
- **Auto-scale**: Based on CPU and data ingestion rate.
- **Optimized autoscale**: Enable in Azure portal for hands-off scaling.

---

### Data Ingestion

| Method | Latency | Use Case |
|---|---|---|
| **Event Hubs / IoT Hub (streaming)** | Seconds | Continuous IoT/telemetry streaming |
| **Event Grid + Blob** | Minutes | File-based auto-ingestion on upload |
| **Kafka connector** | Seconds | Kafka-native streaming |
| **Azure Data Factory** | Minutes | Batch ETL from other sources |
| **LightIngest** | Minutes | Large historical data loads |
| **One-click ingestion** | Manual | Ad-hoc data uploads for exploration |
| **SDKs (Python, .NET, Java)** | Seconds | Application-level ingestion |

**Batching policy**: ADX batches ingested data (default: 1000 rows or 1 GB or 5 minutes) before compressing and indexing — optimize for your ingestion pattern.

---

### Kusto Query Language (KQL)

KQL is a read-only, pipe-based query language optimized for data exploration.

```kql
// Basic query structure: table | operator | operator...
StormEvents
| where StartTime > ago(7d)
| where EventType == "Tornado"
| summarize Count=count(), MaxDamage=max(DamageProperty) by State
| order by Count desc
| take 10

// Time-series aggregation with bin()
DeviceTelemetry
| where Timestamp between (datetime(2024-01-01) .. datetime(2024-02-01))
| where DeviceId in ("sensor-001", "sensor-002")
| summarize AvgTemp=avg(Temperature), MaxTemp=max(Temperature)
    by DeviceId, bin(Timestamp, 1h)
| render timechart

// Join (lookup pattern)
let DeviceInfo = DeviceReference | project DeviceId, Location, AlertThreshold;
DeviceTelemetry
| where Timestamp > ago(1h)
| join kind=leftouter DeviceInfo on DeviceId
| where Temperature > AlertThreshold
| project Timestamp, DeviceId, Location, Temperature, AlertThreshold

// Anomaly detection with time series
let series = DeviceTelemetry
| make-series AvgTemp=avg(Temperature) on Timestamp from ago(30d) to now() step 1h by DeviceId;
series
| extend anomalies=series_decompose_anomalies(AvgTemp)
| mv-expand Timestamp, AvgTemp, anomalies
| where anomalies != 0

// Parse structured text with parse
AppLogs
| where Level == "Error"
| parse Message with "RequestId=" RequestId " User=" User " Error=" *
| summarize ErrorCount=count() by User, bin(TimeGenerated, 1h)

// KQL functions
.create function MyFunction(startTime: datetime, endTime: datetime) {
    DeviceTelemetry
    | where Timestamp between (startTime .. endTime)
    | summarize count() by DeviceId
}
```

### Common KQL Operators

| Operator | Description |
|---|---|
| `where` | Filter rows by condition |
| `project` | Select and rename columns |
| `extend` | Add computed columns |
| `summarize` | Aggregate with group by |
| `order by` / `sort by` | Sort results |
| `top N by column` | Return top N rows |
| `take N` / `limit N` | Return N rows (arbitrary) |
| `join` | Inner, left outer, full outer, anti joins |
| `union` | Combine tables |
| `distinct` | Deduplicate |
| `parse` | Extract values from strings |
| `mv-expand` | Expand arrays to rows |
| `make-series` | Create time series for ML functions |
| `bin()` | Round time to bucket (for aggregation) |
| `ago()` | Relative time expression |
| `between` | Range filter |
| `render` | Visualization hint (timechart, barchart, piechart) |

---

### Hot/Warm/Cold Cache Tiers

```
         Query Latency    Cost
Hot      Milliseconds     Highest (SSD on VMs)
Warm     Seconds          Medium (managed HDD)
Cold     Seconds–minutes  Lowest (Azure Storage)
```

- **Hot cache period**: Configure per table — data within period kept on SSD.
- **Warm cache**: Recent data on managed disks.
- **Cold storage**: Azure Blob Storage — data available but slower retrieval.
- Tune based on query patterns: operational queries → hot, historical analytics → cold.

---

### ADX Dashboards and Visualization

- **Azure Data Explorer Dashboards**: Native dashboard tool with auto-refresh, KQL queries, multiple chart types.
- **Grafana**: ADX data source plugin for Grafana dashboards.
- **Power BI**: ADX connector (native query mode for KQL, DirectQuery or Import).
- **Azure Monitor Workbooks**: Visualize ADX data alongside Azure Monitor data.

---

### Cross-Cluster Queries

```kql
// Query data across multiple ADX clusters in one query
cluster('mycluster2.eastus').database('MyDB').MyTable
| where Timestamp > ago(1d)
| union (MyTable | where Timestamp > ago(1d))
| summarize count() by Region
```

---

## Azure HDInsight

### Service Overview

Azure HDInsight is a managed cloud service for open-source analytics frameworks. Microsoft manages cluster provisioning, patching, and monitoring — you bring your workloads.

> **Recommendation**: For new Spark workloads, prefer **Azure Databricks** (better performance, Unity Catalog, better notebook experience). HDInsight is best for existing Hadoop workloads or frameworks not available in Databricks.

### Supported Cluster Types

| Type | Framework | Use Case |
|---|---|---|
| **Spark** | Apache Spark 3.x | General analytics, ML (prefer Databricks) |
| **Interactive Query** | Apache Hive LLAP | Low-latency interactive SQL on ADLS |
| **Kafka** | Apache Kafka | Managed Kafka broker (prefer Event Hubs for most scenarios) |
| **HBase** | Apache HBase | Real-time NoSQL on Hadoop (consider Cosmos DB) |
| **Hadoop** | MapReduce, YARN, HDFS | Legacy MapReduce batch jobs |

### Storage Integration

- **Primary storage**: ADLS Gen2 or Blob Storage (HDFS abstraction via `wasbs://` or `abfss://`).
- **Metastore**: External Hive metastore (Azure SQL Database recommended) for persistence across cluster restarts.

### Cluster Lifecycle

- Clusters are provisioned per-workload — common pattern is to create, use, delete (not long-running).
- Head nodes: 2 (HA).
- Worker nodes: Variable (auto-scale supported).
- **Bootstrap actions**: Run scripts at cluster creation for custom software.

---

## Azure Data Share

### Service Overview

Azure Data Share enables organizations to share data with external organizations securely and easily, without custom ETL, APIs, or storage management.

### Sharing Models

| Model | Description | Supported Sources |
|---|---|---|
| **Snapshot-based** | Copy of data sent to recipient on share; scheduled refresh | ADLS Gen2, Blob Storage, SQL Database, Synapse, Data Explorer |
| **In-place** | Recipient queries source directly — no data copy | Azure Data Explorer (cross-cluster), Azure Storage (read access) |

### Key Concepts

- **Data Share Account**: Top-level resource in your Azure subscription.
- **Sent Share**: Data you're sharing with others — define datasets and recipients.
- **Received Share**: Data shared with you by another org — map to your storage.
- **Invitation**: Sent to recipient email — they accept in their own Azure subscription.
- **Snapshot schedule**: How frequently shared data is refreshed for snapshot-based shares.

### Use Cases

- Share operational data between business units in different Azure subscriptions.
- Share analytics data with partners or customers without API development.
- Replace manual file transfers or FTP for data exchange.
- Public sector data sharing between agencies.

---

## Azure Open Datasets

### Overview

A curated catalog of publicly available datasets optimized for use in Azure ML and Azure Databricks:

| Dataset Category | Examples |
|---|---|
| **Weather** | NOAA ISD, NOAA GFS, ERA5 climate reanalysis |
| **Health & Genomics** | US COVID-19 public data, ENCODE genomics |
| **Labor & Economics** | US Bureau of Labor Statistics, US Census |
| **Safety** | NYC taxi/limousine, Chicago safety data |
| **Transportation** | NYC Yellow/Green taxi, TLC FHV |
| **Geospatial** | OpenStreetMap, US Natural Resources |
| **Finance** | MSCI Open Source datasets |

### Access Patterns

```python
# Access via Azure ML SDK
from azureml.opendatasets import NycTlcYellow
from datetime import datetime

taxi_data = NycTlcYellow(start_date=datetime(2024, 1, 1), end_date=datetime(2024, 1, 31))
df = taxi_data.to_pandas_dataframe()

# Access via Databricks
from azureml.opendatasets import NycTlcYellow
taxi_spark = NycTlcYellow(...).to_spark_dataframe()

# Direct Azure Blob access (many datasets available as Parquet/CSV)
# e.g. wasbs://nyctlc@azureopendatastorage.blob.core.windows.net/yellow/
```

- Datasets are **read-only** — copy to your own storage for transformation.
- Reduce data download costs — datasets are in Azure Storage, so access from Azure compute is free (same-region).
