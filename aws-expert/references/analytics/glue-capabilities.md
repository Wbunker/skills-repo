# AWS Glue — Capabilities Reference
For CLI commands, see [glue-cli.md](glue-cli.md).

## AWS Glue

**Purpose**: Serverless data integration service for discovering, preparing, moving, and integrating data from multiple sources for analytics, ML, and application development.

### Core Concepts

| Concept | Description |
|---|---|
| **Data Catalog** | Centralized metadata repository; stores database/table definitions, schemas, and connection info |
| **Crawler** | Automatically discovers data stores, infers schemas, and populates/updates the Data Catalog |
| **ETL job** | Spark, Python Shell, Ray, or streaming job that extracts, transforms, and loads data |
| **Connection** | Stores connection details (JDBC URL, credentials) for data sources and targets |
| **Trigger** | Starts jobs or crawlers on a schedule, on-demand, or based on job completion events |
| **Workflow** | Orchestrates multiple crawlers, jobs, and triggers into a pipeline with dependencies |
| **Classifier** | Custom schema detection logic for files not recognized by built-in classifiers |

### ETL Job Types

| Type | Runtime | Use case |
|---|---|---|
| **Spark (glueetl)** | Apache Spark | Large-scale data transformation; supports DynamicFrame and DataFrame |
| **Python Shell** | Python 3 | Lightweight ETL, metadata operations, small datasets |
| **Streaming** | Spark Structured Streaming | Continuous ETL from Kinesis Data Streams or Kafka |
| **Ray** | Ray framework | Python-based distributed ML and data processing |

### Glue Studio

Visual drag-and-drop interface for building ETL jobs. Generates PySpark code automatically. Supports source/transform/target nodes, job monitoring, and Git integration.

### AWS Glue DataBrew

No-code visual data preparation tool. 250+ built-in transformations. Profiling to understand data quality. Recipes (transformation sequences) applied to datasets. Outputs to S3 or Glue Data Catalog.

### Glue Data Quality (DQDL)

| Concept | Description |
|---|---|
| **DQDL (Data Quality Definition Language)** | Rule language for defining data quality checks |
| **Ruleset** | Collection of DQDL rules applied to a table or job |
| **Evaluation run** | Executes a ruleset against data; returns PASS/FAIL per rule and overall score |
| **Recommendations** | Glue can suggest rules based on data profiling |

### Key Features

| Feature | Description |
|---|---|
| **Job bookmarks** | Track processed data to avoid reprocessing; state stored between runs |
| **DynamicFrame** | Glue's extension of Spark DataFrame; handles schema inconsistencies and nested data |
| **FindMatches transform** | ML-based deduplication; identify matching records without exact key matches |
| **Sensitive data detection** | Detect and optionally redact PII in ETL jobs using built-in entity detectors |
| **Interactive sessions** | Jupyter-compatible sessions for interactive Spark development in Glue |
| **Lake Formation integration** | Glue crawlers and jobs respect Lake Formation permissions on Data Catalog tables |

---

## AWS Glue Data Catalog

**Purpose**: Central metastore for all analytics services — a unified view of databases, tables, schemas, and partitions across your data lake.

### Core Concepts

| Concept | Description |
|---|---|
| **Database** | Logical grouping of tables; analogous to a Hive database |
| **Table** | Metadata definition: schema, format, location (S3 path), partition keys, SerDe |
| **Partition** | Subdivision of a table by key values (e.g., `dt=2024-01-01`); maps to S3 prefixes |
| **Connection** | Reusable JDBC/Kafka/network connection credentials for Glue jobs and crawlers |
| **Schema Registry** | Manage and enforce schemas for streaming data (Avro, JSON Schema, Protobuf) |

### Service Integration

| Service | How it uses the Data Catalog |
|---|---|
| **Amazon Athena** | Default metastore; queries reference catalog databases and tables directly |
| **Amazon Redshift Spectrum** | Uses catalog tables as external tables for querying S3 |
| **Amazon EMR** | Hive Metastore compatible; Spark and Hive read catalog metadata |
| **AWS Glue ETL** | Source and target tables defined in catalog; crawlers populate it |
| **AWS Lake Formation** | Permissions enforced on top of catalog resources (column/row/cell-level) |

### Resource Policies

Attach resource-based policies to the Data Catalog to control cross-account access. Combined with Lake Formation permissions for fine-grained data governance.

---

## AWS Data Pipeline (Legacy)

> **Note**: AWS Data Pipeline is in maintenance mode and no longer available to new customers. AWS recommends migrating existing workloads to AWS Glue or AWS Step Functions. No new features or region expansions are planned.

**Purpose**: Scheduled data movement and transformation between AWS services and on-premises data sources. Orchestrates EC2 and EMR resources to run activities on a defined schedule.

### Core Concepts

| Concept | Description |
|---|---|
| **Pipeline** | The operational unit; defines the schedule, data nodes, activities, and preconditions |
| **Pipeline definition** | JSON document specifying all pipeline objects, their types, and field values |
| **Data node** | Represents a data location and schema; supported types: S3DataNode, SqlDataQuery (RDS/Redshift), DynamoDBDataNode, MySqlDataNode |
| **Activity** | Work to be performed; runs on a compute resource (EC2 instance or EMR cluster) |
| **Precondition** | Condition that must be true before an activity runs (e.g., `S3KeyExists`, `DynamoDBDataExists`) |
| **Schedule** | Defines when and how often a pipeline runs; supports cron-style expressions |
| **Task Runner** | Agent process (managed by AWS or self-installed) that polls for tasks and executes them |

### Activity Types

| Activity | Description |
|---|---|
| **CopyActivity** | Copy data between data nodes (e.g., S3 to S3, RDS to S3) |
| **EmrActivity** | Run a MapReduce, Hive, Pig, or Spark job on an EMR cluster |
| **HiveActivity** | Run a Hive query on an EMR cluster |
| **HiveCopyActivity** | Copy data using Hive between nodes with optional filtering |
| **PigActivity** | Run a Pig script on an EMR cluster |
| **ShellCommandActivity** | Run a shell script on an EC2 instance |
| **SqlActivity** | Run a SQL query on an RDS or Redshift database |

### Migration Path

| Use case | Recommended replacement |
|---|---|
| ETL and data transformation | AWS Glue (serverless Spark; Data Catalog integration) |
| Complex multi-step workflows | AWS Step Functions (with Glue, Lambda, ECS tasks) |
| Scheduled SQL or shell jobs | Amazon EventBridge Scheduler + Lambda or Glue |
