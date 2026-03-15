# AWS Athena & EMR — Capabilities Reference
For CLI commands, see [athena-emr-cli.md](athena-emr-cli.md).

## Amazon Athena

**Purpose**: Serverless, interactive SQL query service that analyzes data directly in Amazon S3 and other sources without infrastructure management.

### Core Concepts

| Concept | Description |
|---|---|
| **Query engine** | Based on Presto/Trino for SQL queries; Apache Spark for notebook-based analytics |
| **Data Catalog** | Uses AWS Glue Data Catalog as the default metastore for databases and tables |
| **Workgroup** | Logical grouping of queries; enforces query limits, result locations, and encryption |
| **Named query** | Saved SQL query with a name and description; reusable across sessions |
| **Prepared statement** | Parameterized query with `?` placeholders; improves reuse and prevents SQL injection |
| **Result reuse** | Cache query results for up to 7 days; reuse when the same query runs on unchanged data |

### Supported File Formats

| Format | Notes |
|---|---|
| **Parquet** | Columnar; best performance and cost; recommended for analytics |
| **ORC** | Columnar; optimized row columnar; similar to Parquet |
| **JSON** | Row-based; flexible schema; higher scan cost |
| **CSV / TSV** | Row-based; simple; highest scan cost per query |
| **Avro** | Row-based; schema evolution support |
| **Ion** | Amazon's superset of JSON |

### Key Features

| Feature | Description |
|---|---|
| **CTAS (Create Table As Select)** | Create new table from query results; specify format, partitioning, and location |
| **INSERT INTO** | Append query results to existing table |
| **Federated Query** | Query data in RDS, DynamoDB, Redshift, CloudWatch, and on-premises via Lambda connectors |
| **Athena for Apache Spark** | Run PySpark analytics with managed notebooks; no cluster provisioning |
| **Partition projection** | Automatically project partition values without Glue Catalog partition metadata |
| **Query result reuse** | Reuse cached results up to 7 days; configurable per workgroup |
| **Capacity reservations** | Pre-purchase DPUs for dedicated query capacity; avoid shared queue waits |

### Pricing Model

- Charged per **TB of data scanned** (~$5/TB in us-east-1)
- Canceled queries charged for data scanned up to cancellation
- No charge for DDL statements, failed queries, or metadata operations
- Use columnar formats and partitioning to minimize scanned data

### Common Patterns

```sql
-- CTAS with partitioning and Parquet format
CREATE TABLE clean_data
WITH (
  format = 'PARQUET',
  partitioned_by = ARRAY['dt'],
  external_location = 's3://bucket/clean/'
) AS SELECT * FROM raw_data;

-- Federated query via Lambda connector
SELECT * FROM lambda_catalog.my_db.rds_table
WHERE created_at > current_date - interval '7' day;

-- Prepared statement
PREPARE get_user FROM
  SELECT * FROM users WHERE user_id = ? AND region = ?;
EXECUTE get_user USING '123', 'us-east-1';
```

---

## Amazon EMR

**Purpose**: Managed cluster platform for processing and analyzing vast amounts of data using open-source big data frameworks such as Apache Spark, Hive, Flink, and others.

### Deployment Types

| Type | Description |
|---|---|
| **EMR on EC2** | Traditional cluster on EC2 instances; full control over instance types, networking, and storage |
| **EMR on EKS** | Submit Spark/other jobs to an EKS cluster; share Kubernetes infrastructure across workloads |
| **EMR Serverless** | Run Spark and Hive jobs without cluster management; pay per vCPU-second and GB-second |

### Key Concepts (EMR on EC2)

| Concept | Description |
|---|---|
| **Cluster** | Collection of EC2 instances running a big data framework |
| **Master node** | Coordinates the cluster; runs YARN ResourceManager, HDFS NameNode; one per cluster |
| **Core node** | Runs YARN NodeManager and HDFS DataNode; stores data in HDFS |
| **Task node** | Runs YARN NodeManager only; no HDFS; used for spot-based scale-out |
| **Instance group** | Fixed configuration of instances for a node role; one instance group per role |
| **Instance fleet** | Mix of instance types and purchase options (on-demand + spot) per role; more flexible than instance groups |
| **Step** | Unit of work (Spark job, Hive script, custom JAR) submitted to the cluster |
| **Bootstrap action** | Script run on every node before applications start; used for custom configuration |

### Supported Applications

| Category | Applications |
|---|---|
| **Processing** | Apache Spark, Apache Flink, Apache Hadoop MapReduce |
| **SQL** | Apache Hive, Presto (PrestoSQL), Apache Pig |
| **Storage** | Apache HBase (NoSQL on HDFS/S3), Apache Hudi, Apache Iceberg, Delta Lake |
| **Coordination** | Apache ZooKeeper |
| **ML** | Apache MXNet, TensorFlow (via custom bootstrap) |

### EMR Serverless

| Concept | Description |
|---|---|
| **Application** | Long-lived resource defining the runtime (Spark or Hive) and default resource config |
| **Job run** | A single execution of a Spark or Hive job within an application |
| **Pre-initialized capacity** | Keep workers warm to reduce cold-start latency; optional, billed when idle |
| **Worker configuration** | Set default CPU/memory per worker; override per job run |

### EMR on EKS

| Concept | Description |
|---|---|
| **Virtual cluster** | Maps an EMR namespace to a Kubernetes namespace on an EKS cluster |
| **Job run** | Spark job submitted to the virtual cluster; runs as Kubernetes pods |
| **Job template** | Reusable job configuration with parameterization |
| **Managed endpoint** | Interactive endpoint for notebooks (EMR Studio integration) |

### Key Features

| Feature | Description |
|---|---|
| **Managed Scaling** | Automatically resize cluster (add/remove core and task nodes) based on YARN metrics |
| **Instance fleet + Spot** | Use Spot instances for task nodes to reduce costs; EMR handles interruptions |
| **EMR Studio** | Managed Jupyter notebooks with Git integration; connect to EMR clusters or serverless |
| **EMRFS** | EMR File System; allows Spark/Hive to use S3 as durable storage instead of HDFS |
| **Lake Formation integration** | Fine-grained column/row-level access control on S3 data accessed via EMR |
