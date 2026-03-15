# Analytics Pipeline — Capabilities

## Services Covered

- Cloud Composer (managed Apache Airflow)
- Cloud Data Fusion (visual ETL/ELT)
- Dataplex (data governance and catalog)
- Datastream (CDC / replication)
- Analytics Hub (data sharing)
- Looker Studio (visualization)
- Dataprep / Trifacta (data wrangling)

---

## Cloud Composer (Apache Airflow)

### Purpose
Fully managed Apache Airflow orchestration environment running on GKE. Used to author, schedule, and monitor data pipeline workflows (DAGs).

### Architecture
- Composer 1: dedicated GKE cluster per environment; Airflow on VMs
- Composer 2: improved autoscaling; smaller footprint; workloads on GKE Autopilot
- Composer 3 (latest): serverless-style; no GKE cluster to manage; faster provisioning; DAG-triggered worker scaling

### Core Concepts
- **DAG (Directed Acyclic Graph)**: Python file defining workflow tasks and dependencies
- **Task**: single unit of work; instances of Operators
- **Operator**: template for a task (BashOperator, PythonOperator, BigQueryOperator, DataflowOperator, etc.)
- **Sensor**: waits for a condition (GCSObjectExistenceSensor, BigQueryTableExistenceSensor, TimeSensor)
- **Hook**: interface to external systems; reused by Operators
- **Connection**: stored credentials for external systems (BigQuery, Cloud Storage, databases)
- **Variable**: key-value store for configuration values shared across DAGs
- **XCom**: cross-communication between tasks; pass small data between task instances
- **Pool**: limit concurrency for resource-intensive tasks
- **SLA**: define expected task completion times; miss triggers alerts

### GCP Operators (commonly used)
- `BigQueryExecuteQueryOperator` / `BigQueryInsertJobOperator`
- `DataflowTemplatedJobStartOperator` / `DataflowStartFlexTemplateOperator`
- `DataprocSubmitJobOperator` / `DataprocCreateClusterOperator`
- `GCSToGCSOperator`, `GCSToLocalOperator`, `LocalToGCSOperator`
- `GCSObjectExistenceSensor`
- `PubSubPublishMessageOperator`
- `CloudRunExecuteJobOperator`

### Environments
- Created in a region; multiple environments can coexist in a project
- DAGs stored in a GCS bucket (`<env-name>/dags/`); auto-synced to Airflow
- Logs written to Cloud Logging and GCS
- Airflow web UI accessible via HTTPS (IAP-protected)
- PyPI packages installable via environment config

### Versions
- Composer 3 supports Airflow 2.x (2.7+)
- Specify at creation: `--airflow-version=2.7.3`

---

## Cloud Data Fusion

### Purpose
Managed, cloud-native data integration platform based on the open-source CDAP framework. Provides a visual drag-and-drop pipeline builder for ETL/ELT workloads. Targets data engineers and business analysts who prefer a no-code/low-code interface over writing pipeline code.

### Core Concepts
- **Instance**: Data Fusion environment; runs in a managed GCP project
- **Pipeline**: visual data flow from source → transformations → sink
- **Plugin**: connector or transformation (150+ built-in plugins)
- **Studio**: drag-and-drop visual pipeline canvas
- **Namespace**: isolated tenant within a Data Fusion instance
- **Replication job**: CDC-based replication from relational databases (MySQL, PostgreSQL, Oracle, SQL Server) to BigQuery or Cloud Storage
- **Wrangler**: interactive data preparation UI within Data Fusion
- **Profiles**: compute execution profiles (Dataproc cluster config) assigned to pipelines

### Editions
| Edition | Description |
|---|---|
| Developer | Single-node; non-production; low cost |
| Basic | Multi-node Dataproc backend; batch pipelines |
| Enterprise | Full feature set; real-time pipelines, replication, advanced governance |

### Execution
- Batch pipelines execute on ephemeral Dataproc clusters (provisioned per run) or existing clusters
- Real-time pipelines use Spark Streaming
- Direct pipelines run in the Data Fusion engine without external compute

### Key Connectors
Sources: Cloud Storage (CSV, JSON, Avro, Parquet, ORC), BigQuery, Cloud Spanner, Cloud SQL, MySQL, PostgreSQL, Oracle, SQL Server, Salesforce, Amazon S3, ADLS Gen2, SAP
Sinks: BigQuery, Cloud Storage, Cloud Spanner, Cloud SQL, Kafka, Elasticsearch, Teradata
Transforms: Joiner, Aggregator, Deduplicate, Normalizer, Value Mapper, Python Evaluator, JavaScript Evaluator, Wrangler

---

## Dataplex

### Purpose
Intelligent data fabric for managing, monitoring, and governing distributed data across Cloud Storage and BigQuery. Provides automated data discovery, metadata management, data quality, and data lineage.

### Core Concepts
- **Lake**: top-level organizational unit representing a data domain (e.g., "marketing", "finance")
- **Zone**: division within a lake by data lifecycle stage (Raw zone, Curated zone); enforces schema and format policies
- **Asset**: specific data source attached to a zone (Cloud Storage bucket or path, BigQuery dataset)
- **Data Quality**: define rules (SQL-based assertions, non-null checks, range checks, regex) that run as scheduled Dataproc/Spark jobs
- **Data Catalog (now Dataplex Catalog)**: unified metadata catalog for all GCP data; tags, tag templates, business glossary; search across all assets
- **Data Lineage**: track how data flows through pipelines; integration with BigQuery, Dataflow, Composer
- **Data Profile**: automated statistical profiling of columns (null %, distinct %, min/max/mean)
- **Auto-discovery**: Dataplex scans Cloud Storage and BigQuery to discover tables, infer schemas, and register in catalog

### Zones
| Zone Type | Purpose | Format Policy |
|---|---|---|
| Raw zone | Ingested, unprocessed data | Any format accepted |
| Curated zone | Processed, analytics-ready data | Enforces columnar format (Parquet, Avro, ORC) |

### Data Governance Flow
```
Data Ingestion → Dataplex Raw Zone → Transform → Curated Zone
                      ↓
               Auto-discovery → Data Catalog → Policy Tags (column security)
                      ↓
               Data Quality Rules → Quality Scores → Alerting
```

### Integration
- Policy tags from Dataplex Catalog apply to BigQuery columns for column-level security
- Data lineage visible in Cloud Console for BigQuery, Dataflow, Composer pipelines
- Works with Sensitive Data Protection for PII scanning

---

## Datastream

### Purpose
Serverless CDC (Change Data Capture) and replication service. Continuously replicates changes from operational databases to BigQuery, Cloud Storage, or Pub/Sub without batch windows or manual ETL code.

### Supported Sources
| Source | Protocols |
|---|---|
| MySQL | Binary log replication (binlog) |
| PostgreSQL | Logical replication (pglogical / wal2json) |
| Oracle | LogMiner-based CDC |
| SQL Server | Change Tracking / CDC feature |
| AlloyDB | PostgreSQL-compatible |
| Salesforce | Salesforce CDC |

### Supported Destinations
- BigQuery (direct streaming; merge semantics for CDC)
- Cloud Storage (Avro or JSON files; consumed by Dataflow or other tools)

### Core Concepts
- **Connection profile**: stores credentials and network config for source/destination
- **Stream**: defines source → destination replication with config (tables, schema, CDC vs backfill)
- **Backfill**: initial full historical data load before starting CDC
- **Private connectivity**: use private peering connection for secure source access (no public internet)
- **Schema evolution**: Datastream detects source schema changes and propagates to BigQuery automatically

### BigQuery Destination Behavior
- Creates tables in BigQuery matching source schema
- Applies CDC changes as `UPSERT` operations using BigQuery's DML merge
- Optional: BigQuery CDC feature (append-only or merge-based)
- Low latency: typically sub-minute end-to-end

---

## Analytics Hub

### Purpose
Exchange and share BigQuery datasets (live data, not copies) across organizations and projects. Publishers list datasets; subscribers get access to linked datasets that always reflect current data.

### Core Concepts
- **Data exchange**: named marketplace where publishers list datasets
- **Listing**: a specific dataset offered for sharing; includes documentation, pricing model
- **Linked dataset**: subscriber's read-only reference to the publisher's BigQuery dataset; no data duplication
- **Publisher**: creates exchange and listings; controls who can subscribe
- **Subscriber**: discovers and subscribes to listings; gets linked dataset in their project

### Use Cases
- Share data across GCP organizations without copying
- Monetize proprietary datasets
- Internal data sharing across business units
- Public data marketplace (Google-hosted public datasets)

### Commercial Data Exchange
- Analytics Hub integrates with Google Cloud Marketplace for commercial dataset monetization
- Free, paid subscription, and pay-per-query models

---

## Looker Studio (formerly Data Studio)

### Purpose
Free, web-based data visualization and reporting tool. Connect to dozens of data sources, create interactive dashboards, and share with Google accounts.

### Key Features
- 1000+ connector types (BigQuery, Cloud SQL, Google Sheets, Google Analytics, Ads, YouTube, and partner connectors)
- Interactive dashboards with filters, date range controls, and drill-through
- Calculated fields using formulas (similar to spreadsheet functions)
- Embed dashboards in web pages (iframe embed)
- Schedule email delivery of reports
- Real-time data from BigQuery via direct connection or BigQuery BI Engine

### Looker Studio vs Looker
| Feature | Looker Studio | Looker |
|---|---|---|
| Cost | Free | Paid (license required) |
| Data modeling | No semantic layer | LookML semantic layer |
| Governance | Limited | Strong (governed metrics) |
| Complexity | Simple drag-drop | Enterprise; LookML code |
| Best for | Ad-hoc self-service | Governed enterprise BI |

---

## Dataprep (Trifacta / Alteryx)

### Purpose
Visual data preparation and wrangling service for cleaning, structuring, and enriching data before loading to BigQuery or Cloud Storage. Partnership product (originally Trifacta, now Alteryx).

### Key Features
- Visual profile of data: distribution charts, outlier detection, missing value highlighting
- ML-suggested transforms: Trifacta automatically suggests cleaning steps
- Wrangle transformations: split, merge, extract, replace, filter, aggregate, pivot
- Output to BigQuery or Cloud Storage
- Runs Dataflow jobs for scalable execution

### Use Cases
- Business analysts preparing data without code
- One-time data cleaning before BigQuery load
- Interactive exploration of messy CSVs or JSON files
