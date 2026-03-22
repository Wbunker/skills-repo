# Analytics Domain Index

This domain covers Azure's data analytics, streaming, ETL, and data platform portfolio. Load the relevant namespace files based on the user's specific workload.

## Namespace Index

| Namespace | Capabilities | CLI | Load when... |
|-----------|-------------|-----|--------------|
| Azure Synapse Analytics | analytics/synapse-capabilities.md | analytics/synapse-cli.md | Unified analytics platform: dedicated SQL pools (data warehouse), serverless SQL pool, Spark pools, Data Explorer pools, pipelines (ADF integrated), Synapse Link |
| Azure Data Factory | analytics/data-factory-capabilities.md | analytics/data-factory-cli.md | Cloud ETL/ELT, 100+ connectors, pipelines, data flows (code-free Spark), integration runtimes, triggers, copy activity, mapping data flows |
| Event Hubs | analytics/event-hubs-capabilities.md | analytics/event-hubs-cli.md | Kafka-compatible streaming ingestion, partitions, consumer groups, Capture to ADLS/Blob, Schema Registry, Event Hubs Premium/Dedicated |
| Stream Analytics | analytics/stream-analytics-capabilities.md | analytics/stream-analytics-cli.md | Real-time SQL-based stream processing, IoT Hub/Event Hubs input, Power BI/Azure output, windowing functions, ASA on Edge |
| Azure Databricks | analytics/databricks-capabilities.md | analytics/databricks-cli.md | Managed Apache Spark, Delta Lake, Unity Catalog, ML Runtime, Photon engine, Workflows (orchestration), Model Serving |
| Purview & Power BI | analytics/purview-powerbi-capabilities.md | analytics/purview-powerbi-cli.md | Microsoft Purview (data governance, catalog, lineage, policy), Power BI Embedded, Azure Analysis Services |
| Other Analytics | analytics/other-analytics-capabilities.md | analytics/other-analytics-cli.md | Azure Data Explorer (Kusto), Azure HDInsight (Hadoop/Spark managed), Azure Data Share, Azure Open Datasets |

## Domain Overview

The Azure analytics portfolio covers the full modern data platform stack:

- **Batch ETL/ELT**: Azure Data Factory, Synapse Pipelines
- **Data Warehouse**: Synapse Dedicated SQL Pool (MPP), Serverless SQL Pool
- **Big Data / Spark**: Azure Databricks, Synapse Spark Pools
- **Streaming**: Event Hubs (ingestion), Stream Analytics (processing), Databricks Structured Streaming
- **Data Governance**: Microsoft Purview (catalog, lineage, data policy)
- **BI / Semantic Layer**: Power BI Embedded, Azure Analysis Services
- **Log / Telemetry Analytics**: Azure Data Explorer (ADX/Kusto)

## Key Decision Points

| Scenario | Recommended Service |
|----------|-------------------|
| Cloud data warehouse (SQL-centric team) | Synapse Dedicated SQL Pool |
| Ad-hoc queries over data lake (no cluster) | Synapse Serverless SQL Pool |
| Spark-heavy analytics + ML + Delta Lake | Azure Databricks |
| Cloud ETL/ELT with 100+ connectors | Azure Data Factory / Synapse Pipelines |
| Kafka-compatible event streaming ingestion | Event Hubs |
| Real-time SQL stream processing | Stream Analytics |
| Log/telemetry sub-second queries | Azure Data Explorer (ADX) |
| Enterprise data governance and catalog | Microsoft Purview |
| Embed BI reports in applications | Power BI Embedded |
