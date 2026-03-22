# Azure Data Factory — Capabilities

## Service Overview

Azure Data Factory (ADF) is Azure's fully managed, serverless data integration service for building ETL and ELT pipelines. It orchestrates data movement and transformation across 100+ data sources without managing any infrastructure.

**Key principle**: ADF separates concerns into Linked Services (connections), Datasets (data structures), Activities (operations), and Pipelines (workflows).

> **Synapse Pipelines vs ADF**: Functionally identical — same engine, same connectors, same concepts. Use Synapse Pipelines if your team already works within a Synapse workspace. Use standalone ADF for organizations without Synapse.

---

## Core Concepts

### Linked Services

Connection definitions to external data sources — analogous to connection strings:

| Category | Examples |
|---|---|
| Azure Storage | Blob Storage, ADLS Gen2, Azure Files |
| Azure Data Services | Synapse, SQL Database, Cosmos DB, Event Hubs |
| Azure AI | Azure Machine Learning, Cognitive Services |
| Databases | SQL Server, Oracle, MySQL, PostgreSQL, Snowflake |
| SaaS Applications | Salesforce, ServiceNow, SAP ECC/S4HANA, Dynamics |
| File Systems | SFTP, FTP, HTTP, Amazon S3, Google Cloud Storage |
| NoSQL | MongoDB, Cassandra |
| Big Data | HDFS, Azure Databricks, HDInsight |

Authentication options per connector: account key, SAS, service principal, managed identity, username/password.

### Datasets

Schema-aware references to data within a linked service — define format and location:

```json
{
  "name": "SalesParquetDataset",
  "type": "Parquet",
  "linkedServiceName": {"referenceName": "MyADLSLinkedService"},
  "typeProperties": {
    "location": {
      "type": "AzureBlobFSLocation",
      "fileSystem": "data",
      "folderPath": "sales/@{formatDateTime(pipeline().parameters.runDate, 'yyyy/MM')}",
      "fileName": "*.parquet"
    }
  }
}
```

### Pipelines

Logical grouping of activities that perform a unit of work. Pipelines support:
- **Parameters**: Dynamic values passed at runtime or trigger time.
- **Variables**: Pipeline-scoped mutable values for state tracking.
- **Global Parameters**: Factory-wide constants (e.g., environment name, key vault URL).

---

## Integration Runtimes

The compute infrastructure for data movement and activity execution:

| Type | Description | Use Case |
|---|---|---|
| **Azure IR** | Managed Microsoft-hosted compute in Azure region | Cloud-to-cloud data movement, Mapping Data Flows |
| **Self-hosted IR** | Customer-managed VM/server running IR software | On-premises data sources, secure VNet access |
| **Azure-SSIS IR** | Lift-and-shift SSIS package execution | Migrating existing SSIS ETL to cloud |

### Azure IR

- Microsoft manages infrastructure — no VMs to manage.
- Supports **Data Flow cluster** for Mapping Data Flows (auto-provisionged Spark cluster).
- **Auto-resolve IR**: Automatically picks optimal region; can pin to specific region for data residency.
- **Managed VNet IR**: Azure IR deployed in ADF-managed VNet — access private data sources via managed private endpoints (no self-hosted IR needed for Azure private resources).

### Self-hosted IR

- Install IR software on on-premises Windows VM or EC2 instance.
- Supports HA with multiple nodes.
- Communication: outbound HTTPS to ADF — no inbound firewall rules needed.
- Used for: SQL Server on-premises, Oracle, SAP, file shares, databases in private networks.

### Azure-SSIS IR

- Dedicated VM cluster for running SSIS packages unchanged in Azure.
- Packages stored in SSISDB (SQL Managed Instance/Azure SQL), file system, or Azure Files.
- License Mobility: bring existing SQL Server licenses (BYOL) to reduce cost.

---

## Key Activities

### Copy Activity

Primary data movement activity — parallel, fault-tolerant data copy:

| Feature | Description |
|---|---|
| **Parallel copies** | Number of parallel threads for reading/writing |
| **Staging** | Use Blob/ADLS as staging for PolyBase/COPY command loading |
| **Fault tolerance** | Skip incompatible rows, log skipped rows |
| **Schema mapping** | Map source columns to sink columns (different names/types) |
| **Data type mapping** | Automatic type conversion between source and sink |

```json
{
  "name": "CopySalesData",
  "type": "Copy",
  "inputs": [{"referenceName": "SourceSQLDataset", "type": "DatasetReference"}],
  "outputs": [{"referenceName": "SinkParquetDataset", "type": "DatasetReference"}],
  "typeProperties": {
    "source": {"type": "SqlSource", "queryTimeout": "02:00:00"},
    "sink": {
      "type": "ParquetSink",
      "storeSettings": {"type": "AzureBlobFSWriteSettings"}
    },
    "parallelCopies": 8,
    "enableStaging": false
  }
}
```

### Mapping Data Flows

Code-free visual Spark transformations — runs on auto-provisioned Spark cluster:

**Transformation types**:
- **Source**: Read from any supported source
- **Sink**: Write to any supported sink
- **Select**: Column selection and renaming
- **Filter**: Row filtering with expressions
- **Derived Column**: Add/transform columns with expression builder
- **Aggregate**: Group by + aggregations (sum, count, avg, etc.)
- **Join**: Inner, left outer, right outer, full outer, cross, exists
- **Union**: Combine multiple streams
- **Pivot/Unpivot**: Reshape data
- **Lookup**: Non-joining reference enrichment
- **Sort**: Order rows
- **Flatten**: Explode arrays/complex types
- **Parse/Stringify**: JSON/XML handling within columns
- **Window**: Analytical window functions (rank, lag, lead, row_number)

```
[SQL Source] → [Filter: date > '2024-01-01'] → [Derived: fullName = firstName + ' ' + lastName]
→ [Aggregate: totalSales by customerId] → [Sink: ADLS Parquet]
```

**Debug mode**: Interactive cluster (warm-up ~2 min) for row-by-row data preview while developing.

### Control Flow Activities

| Activity | Description |
|---|---|
| **ForEach** | Iterate over array of items (sequential or parallel) |
| **IfCondition** | Branch based on boolean expression |
| **Switch** | Multi-branch routing based on value |
| **Until** | Loop until condition is true (polling pattern) |
| **Wait** | Pause pipeline for N seconds |
| **Execute Pipeline** | Call another pipeline (sync or async) |
| **Web** | HTTP REST call to any API |
| **Webhook** | Pause pipeline and resume when callback received |
| **Azure Function** | Invoke Azure Function App |
| **Stored Procedure** | Execute SQL stored procedure |
| **Lookup** | Read single dataset row for use in pipeline |
| **Get Metadata** | Retrieve file/folder metadata from storage |
| **Delete** | Delete files or folders |
| **Validation** | Wait until dataset exists or has minimum size |
| **Script** | Execute SQL script (DDL, stored procedures) |
| **Notebook** | Run Databricks or Synapse Spark notebook |
| **Set Variable** | Set pipeline variable value |
| **Append Variable** | Append to array variable |
| **Fail** | Explicitly fail pipeline with custom error message |

---

## Triggers

| Type | Description |
|---|---|
| **Schedule** | Time-based (cron expression or interval) |
| **Tumbling Window** | Fixed-interval time windows with dependency management, concurrency, retry |
| **Storage Event** | Fires on blob creation or deletion in Storage/ADLS |
| **Custom Event** | Fires on Azure Event Grid custom events |
| **Pipeline Trigger (dependency)** | Trigger pipeline B when pipeline A completes |

```json
{
  "name": "DailyScheduleTrigger",
  "type": "ScheduleTrigger",
  "typeProperties": {
    "recurrence": {
      "frequency": "Day",
      "interval": 1,
      "startTime": "2024-01-01T02:00:00Z",
      "timeZone": "UTC",
      "schedule": {"hours": [2], "minutes": [0]}
    }
  },
  "pipelines": [{"pipelineReference": {"referenceName": "MyPipeline"}, "parameters": {}}]
}
```

---

## Wrangling Data Flows

Power Query-based simple transformations for business users:
- No-code transformations using Power Query M language.
- Simpler than Mapping Data Flows — for straightforward reshaping.
- Runs on ADF cluster (not full Spark like Mapping Data Flows).

---

## Git Integration (CI/CD)

ADF supports collaboration via Git-backed development:

- **Collaboration branch**: Active development (`main` or `develop`).
- **Feature branches**: Individual developers work on branches, create PR to collaboration branch.
- **Publish branch**: `adf_publish` — ARM templates for deployment to other environments.
- Supports: **Azure DevOps Git** and **GitHub**.
- **Export ARM templates**: Published to `adf_publish` branch → deploy to test/prod with ADF deployment task.

```bash
# CI/CD pattern:
# 1. Developers work in feature branches in ADF Studio
# 2. PR to collaboration branch (dev environment)
# 3. After testing, ADF publishes to adf_publish branch
# 4. Azure Pipelines picks up adf_publish and deploys to test/prod
# using az datafactory pipeline create or ADF ARM template deployment
```

---

## Managed Private Endpoint

ADF Managed VNet IR can access private data sources without self-hosted IR:

- Create managed private endpoint in ADF → connects to Azure storage, SQL, Event Hubs, etc.
- Private endpoint provisioned in Microsoft-managed VNet — no customer VNet needed.
- Source owner must approve the private endpoint connection.

---

## Monitoring

| Feature | Description |
|---|---|
| **Monitor tab in ADF Studio** | Pipeline runs, trigger runs, data flow debug — 45-day history |
| **Azure Monitor integration** | Route diagnostics to Log Analytics workspace |
| **Log Analytics** | Query pipeline runs, activity runs with KQL |
| **Alerts** | Alert on pipeline failures, trigger failures via Action Groups |
| **Metrics** | Pipeline succeeded/failed/cancelled, integration runtime availability |

```kusto
// KQL: Failed pipeline runs in last 7 days
ADFPipelineRun
| where TimeGenerated > ago(7d)
| where Status == "Failed"
| project TimeGenerated, PipelineName, FailureType, ErrorMessage
| order by TimeGenerated desc
```

---

## Parameterization Patterns

### Dynamic Content Expressions

ADF uses `@{}` expressions for dynamic values:

```
@{pipeline().parameters.sourceTable}           // pipeline parameter
@{pipeline().RunId}                            // system variable
@{formatDateTime(utcNow(), 'yyyy-MM-dd')}      // date formatting
@{concat('data/', pipeline().parameters.env)}  // string concat
@{activity('LookupActivity').output.firstRow.value}  // activity output
@{variables('myVariable')}                     // pipeline variable
```

### Parameterized Linked Services

Single linked service for multiple databases:

```json
{
  "typeProperties": {
    "connectionString": "Server=@{linkedService().serverName};Database=@{linkedService().databaseName};..."
  },
  "parameters": {
    "serverName": {"type": "string"},
    "databaseName": {"type": "string"}
  }
}
```

---

## Common Patterns

### Incremental Load with High Watermark

```json
// 1. Lookup activity: Get last max timestamp from control table
// 2. Copy activity: WHERE UpdatedAt > @{activity('GetWatermark').output.firstRow.lastWatermark}
// 3. Stored Procedure activity: Update watermark table with new max timestamp
```

### Metadata-Driven Pipeline

Single pipeline processes multiple tables configured in a control table:
1. Lookup: Query control table for list of tables to process.
2. ForEach: Iterate over table list.
3. Inside ForEach: Copy activity with parameterized source/sink.

### File Existence Check

```json
// Validation activity: Wait for file to arrive in ADLS before processing
{
  "type": "Validation",
  "typeProperties": {
    "dataset": {"referenceName": "InputFileDataset"},
    "timeout": "7.00:00:00",
    "sleep": 60,
    "minimumSize": 1024
  }
}
```
