# Azure Synapse Analytics — Capabilities

## Service Overview

Azure Synapse Analytics is a unified analytics platform that combines enterprise data warehousing, big data, and data integration in a single workspace. It eliminates silos between SQL data warehousing, Spark analytics, and ETL/ELT pipelines.

**Primary interface**: Synapse Studio (web-based IDE at `web.azuresynapse.net`)

---

## Synapse Workspace Architecture

A Synapse workspace is the top-level resource containing all analytics engines and supporting resources:

```
Synapse Workspace
├── SQL Pools
│   ├── Dedicated SQL Pool (MPP data warehouse)
│   └── Built-in Serverless SQL Pool (always available)
├── Apache Spark Pools (custom auto-scaling clusters)
├── Data Explorer Pools (Kusto for log/telemetry)
├── Synapse Pipelines (ADF-based ETL)
├── Linked Services (connections to external data sources)
├── Integration Datasets
└── Triggers (schedule, event, tumbling window)
```

**Associated resources** (auto-created or specified):
- Azure Data Lake Storage Gen2 (primary storage — filesystem on ADLS)
- Azure Active Directory (Entra ID) for authentication
- Managed Virtual Network (optional but recommended for security)

---

## Dedicated SQL Pool

**Formerly SQL Data Warehouse** — MPP (Massively Parallel Processing) cloud data warehouse.

### Architecture

- **Control node**: Receives queries, builds execution plans, coordinates DMS.
- **Compute nodes**: Execute query fragments in parallel (60 nodes for DW100c–DW30000c).
- **Data Movement Service (DMS)**: Shuffles data between nodes for joins and aggregations.
- **Storage**: Columnar format (clustered columnstore index) on Azure Storage — decoupled from compute.

### DWU (Data Warehouse Units)

Scaling unit representing combined CPU, memory, and I/O:

| DWU | Compute Nodes | Use Case |
|---|---|---|
| DW100c | 1 | Dev/test |
| DW500c | 5 | Small production |
| DW1000c | 10 | Medium workloads |
| DW5000c | 30 | Large enterprise DW |
| DW30000c | 60 | Highest scale |

- **Pause/Resume**: Compute stops when paused — storage charges only. Resume takes ~5 minutes.
- **Scaling**: Adjust DWU in 60-second operations without data movement.

### Distribution Types

How data is physically distributed across the 60 distributions:

| Type | Description | Best For |
|---|---|---|
| **Hash** | Rows assigned to distribution by hash of specified column | Large fact tables; choose high-cardinality join column |
| **Round-Robin** | Rows distributed evenly in rotation | Staging tables; tables without clear distribution column |
| **Replicated** | Full copy on every compute node (max 2 GB) | Small dimension tables for fast joins |

```sql
-- Hash-distributed fact table
CREATE TABLE dbo.FactSales
(
    SaleKey         INT         NOT NULL,
    CustomerKey     INT         NOT NULL,
    ProductKey      INT         NOT NULL,
    SaleAmount      DECIMAL(18,2),
    SaleDate        DATE
)
WITH
(
    DISTRIBUTION = HASH(CustomerKey),
    CLUSTERED COLUMNSTORE INDEX
);

-- Replicated small dimension
CREATE TABLE dbo.DimProduct
(
    ProductKey      INT         NOT NULL,
    ProductName     NVARCHAR(255),
    Category        NVARCHAR(100)
)
WITH
(
    DISTRIBUTION = REPLICATE,
    CLUSTERED COLUMNSTORE INDEX
);
```

### Data Loading

| Method | Description |
|---|---|
| **COPY statement** | Recommended for loading from ADLS Gen2/Blob — parallel, fast, no external table |
| **PolyBase** | External tables over ADLS/Blob — query directly or INSERT INTO for loading |
| **Azure Data Factory** | Orchestrated copy activities — best for complex transformations |
| **BCP** | For small loads only |

```sql
-- COPY statement (recommended)
COPY INTO dbo.FactSales
FROM 'https://mystorageaccount.dfs.core.windows.net/mycontainer/sales/*.parquet'
WITH (
    FILE_TYPE = 'PARQUET',
    IDENTITY_INSERT = 'OFF'
);
```

### Workload Management

- **Workload groups**: Allocate minimum/maximum resources to query groups.
- **Resource classes**: static (staticrc10–staticrc80) and dynamic (smallrc–xlargerc) memory allocation per query.
- **Workload classifiers**: Route queries to workload groups based on user, label, or time.

```sql
-- Create a workload group
CREATE WORKLOAD GROUP DataLoads
WITH (
    MIN_PERCENTAGE_RESOURCE = 50,
    CAP_PERCENTAGE_RESOURCE = 100,
    REQUEST_MIN_RESOURCE_GRANT_PERCENT = 25
);
```

---

## Serverless SQL Pool

Pay-per-query SQL engine over your data lake — no cluster to provision or manage.

### Key Characteristics

- Always available in every Synapse workspace (no provisioning).
- Query files directly in ADLS Gen2: Parquet, Delta Lake, CSV, JSON.
- **Cost model**: $5 per TB of data scanned.
- No DML (INSERT/UPDATE/DELETE) — read-only analytics engine.
- Support for external tables, views, and stored procedures.

### Supported Formats

| Format | Notes |
|---|---|
| Parquet | Recommended — columnar, predicate/column pushdown for cost efficiency |
| Delta Lake | Read Delta tables natively including time travel |
| CSV | Specify delimiter, header, encoding |
| JSON | Single-line and multi-line JSON |
| ORC | Read ORC files |

```sql
-- Query Parquet files in ADLS Gen2
SELECT TOP 100
    year,
    month,
    SUM(amount) AS total_amount
FROM OPENROWSET(
    BULK 'https://mystorageaccount.dfs.core.windows.net/data/sales/**',
    FORMAT = 'PARQUET'
) AS [sales]
GROUP BY year, month
ORDER BY year, month;

-- Query Delta Lake table with time travel
SELECT *
FROM OPENROWSET(
    BULK 'https://mystorageaccount.dfs.core.windows.net/delta/customers/',
    FORMAT = 'DELTA'
)
AS [customers]
FOR SYSTEM_TIME AS OF '2024-01-01T00:00:00';

-- Create external table for reusable access
CREATE EXTERNAL TABLE dbo.SalesExternal
WITH (
    LOCATION = 'sales/',
    DATA_SOURCE = MyDataLake,
    FILE_FORMAT = ParquetFormat
)
AS SELECT * FROM OPENROWSET(...);
```

---

## Apache Spark Pools

Auto-scaling Spark clusters for data engineering, data science, and ML.

### Pool Configuration

```yaml
# Spark pool settings
Pool Size: Small (4 vCores, 28 GB), Medium (8 vCores, 56 GB), Large (16 vCores, 112 GB)
Auto-scale: min 3 nodes to max 200 nodes
Auto-pause: after N minutes of inactivity (reduces cost)
Spark version: 3.x (latest LTS recommended)
```

### Key Features

- **Notebooks**: Jupyter-compatible notebooks in Synapse Studio; share between SQL and Spark.
- **Delta Lake**: Native Delta support for ACID transactions on ADLS Gen2.
- **MLflow**: Built-in experiment tracking for ML workloads.
- **Horovod**: Distributed deep learning training.
- **PySpark, Scala, R, .NET Spark**: Multiple language support.
- **Synapse Analytics library**: Pre-installed ML/data libraries (scikit-learn, pandas, PyTorch, TensorFlow).

```python
# PySpark in Synapse notebook — read from ADLS Gen2 (linked directly)
df = spark.read.parquet("abfss://mycontainer@mystorageaccount.dfs.core.windows.net/data/")
df.createOrReplaceTempView("sales")

result = spark.sql("""
    SELECT year, SUM(amount) as total
    FROM sales
    GROUP BY year
    ORDER BY year
""")
result.show()

# Write Delta table
result.write.format("delta").mode("overwrite").save(
    "abfss://mycontainer@mystorageaccount.dfs.core.windows.net/delta/sales-summary/"
)
```

---

## Synapse Link

**Zero-ETL operational analytics** — replicate operational data to Synapse analytical store without impacting transactional performance.

### Supported Sources

| Source | Sync Type | Notes |
|---|---|---|
| **Azure Cosmos DB** | Change feed → analytical store (columnar) | Sub-minute latency; query analytical store with Spark or Serverless SQL |
| **Microsoft Dataverse** | Delta format to Synapse workspace ADLS | Power Platform / Dynamics 365 data |
| **SQL Server 2022** | Change feed → ADLS Gen2 | On-premises SQL Server integration |
| **Azure SQL Database** | Change data capture → ADLS Gen2 | Near-real-time replication |

### Benefits

- No ETL pipelines required.
- No impact on transactional workload (OLTP).
- Columnar analytical store optimized for aggregations.
- Historical data retention configurable (90 days default for Cosmos DB).

---

## Synapse Pipelines

Integrated ADF-based ETL/ELT capability within the Synapse workspace:

- **Functionally identical to Azure Data Factory** (same runtime, same connectors, same activity types).
- Preferred over standalone ADF if already using Synapse workspace.
- 100+ connectors: Azure services, SaaS, databases, file formats.
- Key activities: Copy Activity, Data Flow (code-free Spark), ForEach, IfCondition, Web, Stored Procedure.
- Triggers: Schedule, Tumbling Window, Storage Event, Custom Event.
- Git integration: Azure DevOps or GitHub for CI/CD.

---

## Data Explorer Pool

Kusto-based time-series and log analytics within Synapse:

- Optimized for: telemetry, log analytics, time-series data.
- **KQL (Kusto Query Language)**: Pipe-based query language for sub-second results.
- Auto-ingestion from Event Hubs, IoT Hub, Blob Storage.
- Hot/warm/cold cache tiers for cost optimization.
- Cross-cluster queries with Synapse SQL and Spark.

---

## Security

### Authentication

| Method | Description |
|---|---|
| SQL Authentication | Username/password for dedicated SQL pools (dev/test only) |
| Entra ID (AAD) | Preferred for all access — supports MFA, Conditional Access |
| Managed Identity | For pipeline activities and service-to-service |

### Access Control

- **Synapse RBAC**: Synapse-specific roles (Synapse Administrator, SQL Administrator, Apache Spark Administrator, Synapse Contributor, Synapse Artifact Publisher/User/Operator).
- **Azure RBAC**: Owner/Contributor for resource management.
- **SQL permissions**: Database-level GRANT/DENY for Dedicated SQL Pool.

### Network Security

- **Managed VNet**: All compute resources deployed in Microsoft-managed VNet — outbound only through Managed Private Endpoints.
- **Managed Private Endpoints**: Connect to ADLS Gen2, Key Vault, Event Hubs privately (no public internet).
- **Data exfiltration protection**: Prevent data from leaving approved targets.
- **Column-level security**: Restrict access to specific columns in SQL pools.
- **Row-level security**: Filter rows based on user context.
- **Dynamic data masking**: Mask sensitive data (PII) for non-privileged users.

---

## Synapse vs. Databricks

| Dimension | Azure Synapse | Azure Databricks |
|---|---|---|
| **SQL Warehouse** | Dedicated SQL Pool (MPP) | Databricks SQL Warehouses |
| **Spark** | Synapse Spark Pools | All-Purpose / Job Clusters |
| **Delta Lake** | Supported | Native (inventor) |
| **Unity Catalog** | Purview integration | Native Unity Catalog |
| **ETL/ELT** | Synapse Pipelines (ADF-based) | Workflows + DLT |
| **Best For** | SQL-centric teams + tight Azure integration | Spark-heavy ML + advanced data engineering |
| **Pricing** | DWU-based + per-node for Spark | DBU-based |
| **CI/CD** | ADF-style Git integration | Databricks Asset Bundles |
