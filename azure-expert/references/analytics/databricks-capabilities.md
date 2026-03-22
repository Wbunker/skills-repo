# Azure Databricks — Capabilities

## Service Overview

Azure Databricks is a managed Apache Spark-based analytics platform deeply integrated with Azure services. It provides a collaborative notebook environment, scalable job orchestration, data engineering pipelines, ML/AI workflows, and SQL analytics — all on a unified platform built by the original creators of Apache Spark.

**Pricing tiers**: Standard, Premium (Unity Catalog, jobs ACLs, audit logs), Enterprise.

---

## Workspace Organization

```
Databricks Workspace
├── Notebooks (Python, Scala, SQL, R)
├── Repos (Git integration — GitHub, GitLab, Azure DevOps)
├── Experiments (MLflow experiment tracking)
├── Models (MLflow Model Registry)
├── Jobs (Workflow orchestration)
├── SQL Warehouses (SQL analytics compute)
├── Clusters (All-purpose and Job clusters)
├── Delta Live Tables (DLT) pipelines
├── Dashboards (Lakeview dashboards)
└── Volumes, Catalogs, Schemas (Unity Catalog)
```

---

## Cluster Types

### All-Purpose Clusters

Interactive clusters for collaborative development in notebooks:

- Start on-demand; manually started/terminated or with auto-termination.
- Shared by multiple users and notebooks simultaneously.
- **Multi-user mode**: Shared access (default for interactive work).
- **Single-user mode**: Isolated environment for user-specific workloads.
- Billed per DBU-hour while running — auto-terminate to save cost.

### Job Clusters

Ephemeral clusters created per job run and terminated on completion:

- Fully isolated per run — no shared state between runs.
- Lower DBU rate than all-purpose clusters.
- **Best practice**: Always use job clusters for production jobs.

### SQL Warehouses

Optimized compute for SQL analytics (BI, ad-hoc SQL, Databricks SQL):

| Type | Description |
|---|---|
| **Classic** | Spark-based SQL warehouse, auto-scaling |
| **Serverless** | Databricks-managed compute (faster startup, higher cost) |

- Powers Databricks SQL (formerly SQL Analytics).
- Auto-starts on query; auto-stops after inactivity.
- Sizing: X-Small (2 DBUs/hour) to 4X-Large (128 DBUs/hour).
- **Serverless** recommended for most organizations (no cluster startup wait).

### Cluster Configuration

```json
{
  "cluster_name": "prod-etl-cluster",
  "spark_version": "14.3.x-scala2.12",
  "node_type_id": "Standard_DS3_v2",
  "num_workers": 4,
  "autoscale": {
    "min_workers": 2,
    "max_workers": 10
  },
  "spark_conf": {
    "spark.databricks.delta.optimizeWrite.enabled": "true",
    "spark.databricks.delta.autoCompact.enabled": "true"
  },
  "azure_attributes": {
    "availability": "SPOT_WITH_FALLBACK_AZURE",
    "spot_bid_max_price": -1
  },
  "auto_termination_minutes": 60
}
```

---

## Delta Lake

Delta Lake is the open-source storage layer that brings ACID transactions to data lakes. Databricks is the inventor and primary contributor.

### Core Features

| Feature | Description |
|---|---|
| **ACID Transactions** | Serializable isolation — concurrent reads/writes are safe |
| **Schema Enforcement** | Reject writes that don't match table schema |
| **Schema Evolution** | `mergeSchema` option adds new columns on write |
| **Time Travel** | Query historical versions by version number or timestamp |
| **DML Support** | `UPDATE`, `DELETE`, `MERGE INTO` on data lake files |
| **Scalable Metadata** | Delta log stores metadata locally (not in Hive Metastore) |
| **Audit History** | `DESCRIBE HISTORY` for complete change log |

### Delta Operations

```python
from delta.tables import DeltaTable
from pyspark.sql.functions import col

# Create Delta table
df.write.format("delta").saveAsTable("catalog.schema.customers")

# Time travel — query a previous version
df_v1 = spark.read.format("delta") \
    .option("versionAsOf", 5) \
    .table("catalog.schema.customers")

# Time travel by timestamp
df_yesterday = spark.read.format("delta") \
    .option("timestampAsOf", "2024-01-01T00:00:00Z") \
    .table("catalog.schema.customers")

# MERGE INTO (upsert)
delta_table = DeltaTable.forName(spark, "catalog.schema.customers")
delta_table.alias("target").merge(
    source_df.alias("source"),
    "target.CustomerId = source.CustomerId"
).whenMatchedUpdateAll() \
 .whenNotMatchedInsertAll() \
 .execute()

# OPTIMIZE — compact small files and Z-order for query pruning
spark.sql("OPTIMIZE catalog.schema.events ZORDER BY (CustomerId, EventDate)")

# Liquid clustering (recommended over Z-order for large tables)
spark.sql("""
    CREATE TABLE catalog.schema.events
    CLUSTER BY (CustomerId, EventDate)
""")
spark.sql("OPTIMIZE catalog.schema.events")

# VACUUM — remove old files (respect retention period)
spark.sql("VACUUM catalog.schema.customers RETAIN 168 HOURS")  # 7 days

# Show table history
spark.sql("DESCRIBE HISTORY catalog.schema.customers").show(truncate=False)
```

---

## Unity Catalog

Unity Catalog is Databricks' unified governance solution for data and AI — providing a single governance layer across all workspaces in an account.

### Three-Level Namespace

```
catalog.schema.table
────────────────────
my_catalog.sales.transactions         -- Delta table
my_catalog.ml.models                  -- MLflow models
my_catalog.files.documents            -- Volumes (files)
```

### Object Hierarchy

```
Metastore (one per Databricks account region)
└── Catalog
    └── Schema (database)
        ├── Tables (Delta, external, views)
        ├── Volumes (file storage abstraction)
        ├── Functions (SQL/Python UDFs)
        └── Models (MLflow registered models)
```

### Key Capabilities

| Capability | Description |
|---|---|
| **Fine-grained access control** | `GRANT SELECT ON TABLE`, `GRANT USAGE ON SCHEMA` |
| **Column masking** | Mask PII columns based on user identity |
| **Row filters** | Row-level security via SQL predicates |
| **Data lineage** | Automatic column-level lineage tracking |
| **Audit logs** | All data access events logged to system tables |
| **External locations** | Mount ADLS Gen2 paths with managed credentials |
| **Delta Sharing** | Open-protocol data sharing across organizations/platforms |

```sql
-- Unity Catalog access control
GRANT CREATE, USAGE ON SCHEMA my_catalog.sales TO `data-engineers@mycompany.com`;
GRANT SELECT ON TABLE my_catalog.sales.transactions TO `analysts@mycompany.com`;
GRANT ALL PRIVILEGES ON CATALOG my_catalog TO `data-platform@mycompany.com`;

-- Create volume (file storage in Unity Catalog)
CREATE VOLUME my_catalog.raw.landing_zone
COMMENT 'Landing zone for raw files';
```

---

## Databricks Workflows

DAG-based job orchestration for multi-task pipelines.

### Key Features

- **Task dependencies**: Define upstream/downstream task relationships.
- **Cluster per task**: Each task can use different cluster type/size.
- **Retry policies**: Configurable retry with backoff per task.
- **Repair and rerun**: Re-run only failed tasks without starting over.
- **Job scheduling**: Cron schedule, manual trigger, or API trigger.
- **Webhooks/notifications**: Email, Slack, PagerDuty on job success/failure.
- **Condition tasks**: Branch on upstream task result (success/failure/skip).
- **For-each tasks**: Iterate over an array and run a task for each element.

```json
{
  "name": "Daily ETL Pipeline",
  "tasks": [
    {
      "task_key": "ingest",
      "notebook_task": {"notebook_path": "/Repos/main/notebooks/01_ingest"},
      "job_cluster_key": "etl-cluster",
      "retry_on_timeout": false,
      "max_retries": 2
    },
    {
      "task_key": "transform",
      "depends_on": [{"task_key": "ingest"}],
      "notebook_task": {"notebook_path": "/Repos/main/notebooks/02_transform"},
      "job_cluster_key": "etl-cluster"
    },
    {
      "task_key": "validate",
      "depends_on": [{"task_key": "transform"}],
      "python_wheel_task": {"package_name": "mypackage", "entry_point": "validate"},
      "job_cluster_key": "etl-cluster"
    }
  ],
  "job_clusters": [{
    "job_cluster_key": "etl-cluster",
    "new_cluster": {
      "spark_version": "14.3.x-scala2.12",
      "node_type_id": "Standard_DS4_v2",
      "num_workers": 4
    }
  }],
  "schedule": {
    "quartz_cron_expression": "0 0 2 * * ?",
    "timezone_id": "UTC"
  }
}
```

---

## Delta Live Tables (DLT)

Declarative framework for building reliable, maintainable, and testable data pipelines:

```python
import dlt
from pyspark.sql.functions import col, current_timestamp

# Streaming ingest layer (Bronze)
@dlt.table(comment="Raw events from Event Hubs")
def raw_events():
    return (spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .load("abfss://landing@storage.dfs.core.windows.net/events/"))

# Cleaned layer (Silver)
@dlt.table(comment="Validated and cleaned events")
@dlt.expect_or_drop("valid_device", "DeviceId IS NOT NULL")
@dlt.expect("valid_temperature", "Temperature BETWEEN -50 AND 150")
def cleaned_events():
    return (dlt.read_stream("raw_events")
        .select("DeviceId", "Temperature", "EventTime")
        .withColumn("ingested_at", current_timestamp()))

# Aggregated layer (Gold)
@dlt.table(comment="Hourly device statistics")
def device_stats():
    return (dlt.read("cleaned_events")
        .groupBy("DeviceId", window("EventTime", "1 hour"))
        .agg(avg("Temperature").alias("avg_temp"), count("*").alias("event_count")))
```

---

## Databricks Asset Bundles (DAB)

CI/CD framework for Databricks resources (replaces `dbx`):

```yaml
# databricks.yml
bundle:
  name: my-etl-bundle

targets:
  dev:
    mode: development
    default: true
    workspace:
      host: https://adb-xxx.azuredatabricks.net

  prod:
    mode: production
    workspace:
      host: https://adb-yyy.azuredatabricks.net
    run_as:
      service_principal_name: my-sp@mycompany.com

resources:
  jobs:
    daily_etl:
      name: "Daily ETL - ${bundle.target}"
      tasks:
        - task_key: ingest
          notebook_task:
            notebook_path: ./notebooks/01_ingest.py
```

---

## MLflow Integration

Databricks provides a managed MLflow instance with every workspace.

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import GradientBoostingClassifier

# Experiment tracking (autolog works for many frameworks)
mlflow.sklearn.autolog()

with mlflow.start_run(run_name="GBM-v3") as run:
    model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1)
    model.fit(X_train, y_train)

    # Manual logging
    mlflow.log_metric("test_accuracy", model.score(X_test, y_test))
    mlflow.log_param("features", X_train.columns.tolist())
    mlflow.log_artifact("feature_importance.png")

    print(f"Run ID: {run.info.run_id}")
```

### Model Registry (Unity Catalog)

```python
# Register model to Unity Catalog
mlflow.set_registry_uri("databricks-uc")
mlflow.register_model(
    model_uri=f"runs:/{run.info.run_id}/model",
    name="my_catalog.ml.churn_model"
)

# Load registered model for inference
model = mlflow.sklearn.load_model("models:/my_catalog.ml.churn_model/Production")
```

---

## Model Serving

Real-time inference endpoints managed by Databricks:

- **Model endpoints**: Serve MLflow models with auto-scaling.
- **Foundation model endpoints**: Pay-per-token serving for Llama 3, DBRX, and other open models.
- **External model endpoints**: Proxy to Azure OpenAI, Anthropic, etc. with unified API.
- **A/B testing**: Route traffic between model versions.

```python
# Create serving endpoint via SDK
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ServedModelInput, EndpointCoreConfigInput

w = WorkspaceClient()
w.serving_endpoints.create(
    name="churn-model-endpoint",
    config=EndpointCoreConfigInput(
        served_models=[ServedModelInput(
            name="churn-v1",
            model_name="my_catalog.ml.churn_model",
            model_version="1",
            scale_to_zero_enabled=True,
            workload_size="Small"
        )]
    )
)
```

---

## Photon

Databricks-native vectorized query engine written in C++:

- Drop-in replacement for Spark SQL and DataFrame API — no code changes.
- 2–8x faster for SQL workloads, 4x faster sort operations.
- Enabled per cluster — select "Photon Acceleration" checkbox.
- Available on DBR 9.1+ and all SQL Warehouses.
- Best for: Delta Lake queries, aggregations, joins, I/O-bound workloads.
- Not all operations Photon-accelerated (complex Python UDFs, streaming not fully covered).

---

## Azure Integration

| Integration | Description |
|---|---|
| **ADLS Gen2** | Default storage via Unity Catalog External Locations; credential passthrough via managed identity |
| **Azure Key Vault** | Key Vault-backed secret scopes — `dbutils.secrets.get(scope, key)` retrieves secrets without exposure in notebooks |
| **Entra ID passthrough** | Pass end-user AAD token to ADLS — file-level access control per user |
| **Azure Monitor** | Forward Spark metrics and logs to Log Analytics via cluster init scripts |
| **Event Hubs** | Structured Streaming connector (`com.microsoft.azure:azure-eventhubs-spark_2.12`) |
| **Azure ML** | MLflow tracking server integration; deploy Databricks models to Azure ML endpoints |
| **Azure DevOps / GitHub** | Repos integration for notebook versioning and CI/CD |
| **Entra ID SSO** | Single sign-on for Databricks workspace access |
