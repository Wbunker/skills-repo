# AWS Redshift — Capabilities Reference
For CLI commands, see [redshift-cli.md](redshift-cli.md).

## Amazon Redshift

**Purpose**: Fully managed, petabyte-scale cloud data warehouse using columnar storage and MPP (massively parallel processing); designed for complex analytical queries across large datasets.

### Key Concepts

| Concept | Description |
|---|---|
| **Columnar storage** | Data stored by column, not row; dramatically reduces I/O for analytical queries that select few columns |
| **Distribution style** | Controls how rows are distributed across compute nodes; affects query performance and data movement |
| **Sort key** | Defines physical order of data on disk; allows zone maps to skip irrelevant blocks |
| **Concurrency Scaling** | Automatically adds transient clusters to handle bursts in query concurrency; first 1 hour/day free |
| **Redshift Spectrum** | Query data in S3 directly from Redshift without loading it; uses external tables |
| **Data Sharing** | Share live data across Redshift clusters and accounts without ETL; producer shares a datashare, consumer queries it |
| **Materialized Views** | Pre-computed result sets; can be auto-refreshed; accelerate repeated complex queries |
| **Redshift ML** | `CREATE MODEL` statement trains SageMaker models directly from SQL; inference via SQL function |
| **Redshift Serverless** | Auto-provisioned and scaled Redshift without managing clusters; charged per RPU-second |

### Distribution Styles

| Style | Description | Use Case |
|---|---|---|
| **KEY** | Distribute rows by hashing a column value; matching rows on same node | Join-heavy tables; distribute on join key |
| **ALL** | Copy entire table to every compute node | Small dimension tables; eliminates data movement on joins |
| **EVEN** | Round-robin distribution; no distribution key | Intermediate result tables; no dominant join pattern |
| **AUTO** | Redshift chooses EVEN (small tables) or KEY (larger tables) automatically | Default; let Redshift optimize |

### Sort Key Types

| Type | Description |
|---|---|
| **Compound** | Multi-column sort key; most useful for range queries on leading columns |
| **Interleaved** | Equal weight to all sort key columns; useful when queries filter on any of the columns |

### Key Features

| Feature | Description |
|---|---|
| **Columnar storage + compression** | Column encodings reduce storage; zone maps skip irrelevant blocks; vectorized query execution |
| **Concurrency Scaling** | Seamlessly handles bursts; additional clusters added in < 60 s; per-cluster billing |
| **Redshift Spectrum** | Query exabytes of S3 data via external tables; supports Parquet, ORC, JSON, CSV; integrates with Glue Data Catalog |
| **Data Sharing** | Live cross-cluster and cross-account data access; no data copies or ETL pipelines |
| **Materialized Views** | Incremental refresh for Redshift tables; full refresh for external tables; accelerate dashboards |
| **Redshift ML** | `CREATE MODEL` trains AutoPilot models; inference via SQL `ml_function_name(args)` |
| **AQUA (Advanced Query Accelerator)** | Hardware-accelerated cache in the storage layer; available on ra3 nodes |
| **Federated query** | Query live data in RDS/Aurora PostgreSQL/MySQL without ETL |
| **Serverless** | Pay per RPU-second; auto-scales; no VPC or cluster configuration needed |

### When to Use Redshift

- Complex analytical queries over large (GB to PB) datasets
- Business intelligence and reporting workloads
- Aggregating data from multiple operational databases into a central warehouse
- When querying S3 data lake alongside warehouse data (Spectrum)
- ML model training directly on warehouse data without moving it to SageMaker
