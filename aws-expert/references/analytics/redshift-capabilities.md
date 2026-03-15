# AWS Redshift — Capabilities Reference
For CLI commands, see [redshift-cli.md](redshift-cli.md).

## Amazon Redshift

**Purpose**: Fully managed, petabyte-scale columnar data warehouse optimized for online analytic processing (OLAP) and complex SQL queries across large datasets.

### Core Concepts

| Concept | Description |
|---|---|
| **Cluster** | One or more compute nodes with a leader node that manages query execution and client connections |
| **Leader node** | Parses queries, builds execution plans, coordinates parallel execution across compute nodes |
| **Compute node** | Executes query fragments; stores data in columnar format across slices |
| **Slice** | Partition of a compute node's memory and disk; data is distributed across slices |
| **Node type** | DC2 (compute-intensive, local SSD), RA3 (managed storage, separates compute/storage) |
| **RA3 node** | Compute and storage scale independently; data stored in Redshift Managed Storage (RMS) backed by S3 |

### Distribution Styles

| Style | How data is distributed | When to use |
|---|---|---|
| **KEY** | Rows with the same key value placed on the same slice | Large fact tables joined to dimension tables on the same key |
| **ALL** | Full copy of the table on every node | Small, slowly changing dimension tables |
  | **EVEN** | Rows distributed round-robin across slices | No clear join key; tables not frequently joined |
| **AUTO** | Redshift chooses KEY or ALL based on table size | Default; let Redshift optimize |

### Sort Keys

| Type | Description |
|---|---|
| **Compound sort key** | Columns defined in order; most effective when queries filter on leading columns; default |
| **Interleaved sort key** | Equal weight to each column; effective for queries filtering on any subset of sort key columns; higher vacuum cost |

### Key Features

| Feature | Description |
|---|---|
| **AQUA (Advanced Query Accelerator)** | Hardware-accelerated cache layer that pushes computation to the storage layer; for RA3 nodes |
| **Concurrency Scaling** | Automatically adds transient clusters to handle query bursts; first 1 hour/day free |
| **Redshift Spectrum** | Query data directly in S3 using external tables; scales to thousands of nodes; requires RA3 or DC2 |
| **Data Sharing** | Share live data across Redshift clusters without copying; producer shares a datashare, consumers read it |
| **Materialized Views** | Pre-computed result sets; can be auto-refreshed; used by query optimizer transparently |
| **Federated Query** | Query live data in RDS/Aurora PostgreSQL and MySQL from Redshift; requires Secrets Manager |
| **Redshift ML** | `CREATE MODEL` trains SageMaker models using SQL; `PREDICT` function scores data in queries |
| **Query Editor v2** | Browser-based SQL editor; supports notebooks, collaboration, and schema browsing |

### Serverless

| Concept | Description |
|---|---|
| **Namespace** | Logical container for database objects, users, and schemas; holds the data |
| **Workgroup** | Compute resources (RPUs) associated with a namespace; handles query execution |
| **RPU (Redshift Processing Unit)** | Unit of compute capacity; minimum 8 RPUs; automatically scales up and down |
| **Base capacity** | Minimum RPUs allocated; you pay for actual usage, not idle time |
| **Snapshot** | Point-in-time backup of a namespace; can restore to new serverless or provisioned cluster |

### Common Patterns

```sql
-- Distribution key on join column
CREATE TABLE orders DISTKEY(customer_id) SORTKEY(order_date) AS ...;

-- External table via Spectrum
CREATE EXTERNAL TABLE spectrum.clicks (...)
STORED AS PARQUET
LOCATION 's3://my-bucket/clicks/';

-- Train an ML model
CREATE MODEL churn_model FROM (SELECT * FROM training_data)
TARGET churned IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftML';

-- Materialized view with auto-refresh
CREATE MATERIALIZED VIEW daily_sales AUTO REFRESH YES AS
SELECT date_trunc('day', sale_ts), sum(amount) FROM sales GROUP BY 1;
```
