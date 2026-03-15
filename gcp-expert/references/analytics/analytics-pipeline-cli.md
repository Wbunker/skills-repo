# Analytics Pipeline — CLI Reference

---

## Cloud Composer

```bash
# Create a Composer 3 environment (latest)
gcloud composer environments create my-composer-env \
  --location=us-central1 \
  --environment-size=ENVIRONMENT_SIZE_SMALL \
  --airflow-version=2.7.3 \
  --project=my-project

# Create Composer 2 environment with custom configuration
gcloud composer environments create prod-composer-env \
  --location=us-central1 \
  --environment-size=ENVIRONMENT_SIZE_MEDIUM \
  --airflow-version=2.6.3 \
  --scheduler-count=2 \
  --scheduler-cpu=2 \
  --scheduler-memory=7.5GB \
  --scheduler-storage=5GB \
  --web-server-cpu=2 \
  --web-server-memory=7.5GB \
  --worker-cpu=2 \
  --worker-memory=7.5GB \
  --worker-storage=10GB \
  --min-workers=2 \
  --max-workers=10 \
  --network=my-vpc \
  --subnetwork=my-subnet \
  --service-account=composer-sa@my-project.iam.gserviceaccount.com \
  --image-version=composer-2.6.3-airflow-2.6.3 \
  --project=my-project

# Create Composer environment with PyPI packages
gcloud composer environments create my-composer-env \
  --location=us-central1 \
  --airflow-version=2.7.3 \
  --pypi-packages=pandas==2.0.3,numpy==1.25.0,requests==2.31.0 \
  --project=my-project

# List environments
gcloud composer environments list \
  --locations=us-central1 \
  --project=my-project

# List environments across all locations
gcloud composer environments list \
  --locations=- \
  --project=my-project

# Describe an environment
gcloud composer environments describe my-composer-env \
  --location=us-central1 \
  --project=my-project

# Update environment: add PyPI packages
gcloud composer environments update my-composer-env \
  --location=us-central1 \
  --update-pypi-packages=great-expectations==0.18.0,dbt-bigquery==1.6.0 \
  --project=my-project

# Update environment: set Airflow config overrides
gcloud composer environments update my-composer-env \
  --location=us-central1 \
  --update-airflow-configs=core-max_active_runs_per_dag=5,scheduler-min_file_process_interval=30 \
  --project=my-project

# Update environment: scale workers
gcloud composer environments update my-composer-env \
  --location=us-central1 \
  --min-workers=3 \
  --max-workers=20 \
  --project=my-project

# Delete an environment
gcloud composer environments delete my-composer-env \
  --location=us-central1 \
  --project=my-project

# Import (upload) a DAG to the environment's GCS bucket
gcloud composer environments storage dags import \
  --environment=my-composer-env \
  --location=us-central1 \
  --source=my_dag.py \
  --project=my-project

# Import an entire directory of DAGs
gcloud composer environments storage dags import \
  --environment=my-composer-env \
  --location=us-central1 \
  --source=dags/ \
  --project=my-project

# List DAGs in the environment bucket
gcloud composer environments storage dags list \
  --environment=my-composer-env \
  --location=us-central1 \
  --project=my-project

# Delete a DAG from the environment bucket
gcloud composer environments storage dags delete my_dag.py \
  --environment=my-composer-env \
  --location=us-central1 \
  --project=my-project

# Import plugins
gcloud composer environments storage plugins import \
  --environment=my-composer-env \
  --location=us-central1 \
  --source=my_plugin.py \
  --project=my-project

# Run (trigger) a DAG
gcloud composer environments run my-composer-env \
  --location=us-central1 \
  dags trigger -- my_dag_id

# Trigger DAG with config JSON
gcloud composer environments run my-composer-env \
  --location=us-central1 \
  dags trigger -- my_dag_id --conf '{"date": "2024-01-01"}'

# List DAG runs
gcloud composer environments run my-composer-env \
  --location=us-central1 \
  dags list-runs -- --dag-id=my_dag_id

# Pause a DAG
gcloud composer environments run my-composer-env \
  --location=us-central1 \
  dags pause -- my_dag_id

# Unpause a DAG
gcloud composer environments run my-composer-env \
  --location=us-central1 \
  dags unpause -- my_dag_id

# Get the GCS bucket for a Composer environment
gcloud composer environments describe my-composer-env \
  --location=us-central1 \
  --format="value(config.dagGcsPrefix)" \
  --project=my-project
```

---

## Cloud Data Fusion

```bash
# Create a Data Fusion instance (Developer edition)
gcloud datafusion instances create my-data-fusion \
  --location=us-central1 \
  --edition=DEVELOPER \
  --project=my-project

# Create a Data Fusion instance (Enterprise edition with private VPC)
gcloud datafusion instances create prod-data-fusion \
  --location=us-central1 \
  --edition=ENTERPRISE \
  --enable-private-ip \
  --no-enable-public-ip \
  --network=my-vpc \
  --project=my-project

# List Data Fusion instances
gcloud datafusion instances list \
  --location=us-central1 \
  --project=my-project

# Describe a Data Fusion instance
gcloud datafusion instances describe my-data-fusion \
  --location=us-central1 \
  --project=my-project

# Get the service endpoint URL
gcloud datafusion instances describe my-data-fusion \
  --location=us-central1 \
  --format="value(apiEndpoint)" \
  --project=my-project

# Update a Data Fusion instance (e.g., enable Data Lineage)
gcloud datafusion instances update my-data-fusion \
  --location=us-central1 \
  --enable-lineage-event-publish \
  --project=my-project

# Restart a Data Fusion instance
gcloud datafusion instances restart my-data-fusion \
  --location=us-central1 \
  --project=my-project

# Delete a Data Fusion instance
gcloud datafusion instances delete my-data-fusion \
  --location=us-central1 \
  --project=my-project
```

---

## Dataplex

```bash
# Create a Dataplex Lake
gcloud dataplex lakes create marketing-lake \
  --location=us-central1 \
  --display-name="Marketing Data Lake" \
  --description="Data lake for marketing analytics" \
  --project=my-project

# List lakes
gcloud dataplex lakes list \
  --location=us-central1 \
  --project=my-project

# Create a Raw zone in the lake
gcloud dataplex zones create raw-zone \
  --lake=marketing-lake \
  --location=us-central1 \
  --type=RAW \
  --resource-spec-type=MULTI_PROJECT \
  --display-name="Raw Zone" \
  --project=my-project

# Create a Curated zone
gcloud dataplex zones create curated-zone \
  --lake=marketing-lake \
  --location=us-central1 \
  --type=CURATED \
  --resource-spec-type=SINGLE_PROJECT \
  --display-name="Curated Zone" \
  --project=my-project

# List zones in a lake
gcloud dataplex zones list \
  --lake=marketing-lake \
  --location=us-central1 \
  --project=my-project

# Attach a Cloud Storage bucket as an asset to a zone
gcloud dataplex assets create raw-gcs-asset \
  --lake=marketing-lake \
  --zone=raw-zone \
  --location=us-central1 \
  --resource-type=STORAGE_BUCKET \
  --resource-name=projects/my-project/buckets/my-raw-data-bucket \
  --display-name="Raw GCS Data" \
  --project=my-project

# Attach a BigQuery dataset as an asset
gcloud dataplex assets create curated-bq-asset \
  --lake=marketing-lake \
  --zone=curated-zone \
  --location=us-central1 \
  --resource-type=BIGQUERY_DATASET \
  --resource-name=projects/my-project/datasets/marketing_curated \
  --display-name="Curated BQ Dataset" \
  --project=my-project

# List assets in a zone
gcloud dataplex assets list \
  --lake=marketing-lake \
  --zone=raw-zone \
  --location=us-central1 \
  --project=my-project

# Create a Dataplex task (Spark job for data processing)
gcloud dataplex tasks create my-processing-task \
  --lake=marketing-lake \
  --location=us-central1 \
  --trigger-type=ON_DEMAND \
  --execution-service-account=dataplex-sa@my-project.iam.gserviceaccount.com \
  --spark-file-uris=gs://my-bucket/scripts/process.py \
  --spark-python-script-file=gs://my-bucket/scripts/process.py \
  --project=my-project

# List tasks in a lake
gcloud dataplex tasks list \
  --lake=marketing-lake \
  --location=us-central1 \
  --project=my-project

# Delete a lake
gcloud dataplex lakes delete marketing-lake \
  --location=us-central1 \
  --project=my-project
```

---

## Datastream

```bash
# Create a connection profile for a MySQL source
gcloud datastream connection-profiles create mysql-source \
  --location=us-central1 \
  --display-name="MySQL Production Source" \
  --type=mysql \
  --mysql-hostname=10.1.2.3 \
  --mysql-port=3306 \
  --mysql-username=datastream_user \
  --mysql-password=my-secret-password \
  --project=my-project

# Create a connection profile for PostgreSQL
gcloud datastream connection-profiles create pg-source \
  --location=us-central1 \
  --type=postgresql \
  --postgresql-hostname=10.1.2.4 \
  --postgresql-port=5432 \
  --postgresql-username=replication_user \
  --postgresql-password=my-pg-password \
  --postgresql-database=mydb \
  --project=my-project

# Create a BigQuery destination connection profile
gcloud datastream connection-profiles create bq-destination \
  --location=us-central1 \
  --display-name="BigQuery Destination" \
  --type=bigquery \
  --project=my-project

# Create a Cloud Storage destination connection profile
gcloud datastream connection-profiles create gcs-destination \
  --location=us-central1 \
  --type=google-cloud-storage \
  --bucket=my-datastream-bucket \
  --root-path=/datastream \
  --project=my-project

# List connection profiles
gcloud datastream connection-profiles list \
  --location=us-central1 \
  --project=my-project

# Create a Datastream stream (MySQL → BigQuery)
gcloud datastream streams create mysql-to-bq-stream \
  --location=us-central1 \
  --display-name="MySQL to BigQuery CDC" \
  --source=mysql-source \
  --mysql-source-config='{"allowlist": {"mysql_databases": [{"database": "mydb", "mysql_tables": [{"table": "orders"}, {"table": "customers"}]}]}}' \
  --destination=bq-destination \
  --bigquery-destination-config='{"data_freshness": "900s", "single_target_dataset": {"dataset_id": "my-project:datastream_dataset"}}' \
  --backfill-all \
  --project=my-project

# Create a stream (PostgreSQL → Cloud Storage → Dataflow → BigQuery pattern)
gcloud datastream streams create pg-to-gcs-stream \
  --location=us-central1 \
  --source=pg-source \
  --postgresql-source-config='{"allowlist": {"postgresql_schemas": [{"schema": "public", "postgresql_tables": [{"table": "events"}]}]}, "replication_slot": "datastream_slot", "publication": "datastream_pub"}' \
  --destination=gcs-destination \
  --gcs-destination-config='{"path": "/events", "avro_file_format": {}, "file_rotation_mb": 100, "file_rotation_interval": "60s"}' \
  --backfill-all \
  --project=my-project

# List streams
gcloud datastream streams list \
  --location=us-central1 \
  --project=my-project

# Describe a stream
gcloud datastream streams describe mysql-to-bq-stream \
  --location=us-central1 \
  --project=my-project

# Start a stream
gcloud datastream streams start mysql-to-bq-stream \
  --location=us-central1 \
  --project=my-project

# Pause a stream
gcloud datastream streams pause mysql-to-bq-stream \
  --location=us-central1 \
  --project=my-project

# Resume a stream
gcloud datastream streams resume mysql-to-bq-stream \
  --location=us-central1 \
  --project=my-project

# Run validation on a stream config (before creating)
gcloud datastream streams run mysql-to-bq-stream \
  --location=us-central1 \
  --project=my-project

# Delete a stream
gcloud datastream streams delete mysql-to-bq-stream \
  --location=us-central1 \
  --project=my-project

# Create private connectivity (VPC peering for private source access)
gcloud datastream private-connections create my-private-conn \
  --location=us-central1 \
  --display-name="VPC Peering for Datastream" \
  --vpc-name=projects/my-project/global/networks/my-vpc \
  --subnet=10.10.0.0/29 \
  --project=my-project
```

---

## Analytics Hub

```bash
# Create a data exchange (organization-level operation)
gcloud bigquery analytics-hub data-exchanges create my-exchange \
  --location=us-central1 \
  --display-name="Marketing Analytics Exchange" \
  --description="Internal data exchange for marketing datasets" \
  --project=my-project

# List data exchanges
gcloud bigquery analytics-hub data-exchanges list \
  --location=us-central1 \
  --project=my-project

# Create a listing (publish a BigQuery dataset)
gcloud bigquery analytics-hub listings create my-listing \
  --location=us-central1 \
  --data-exchange=my-exchange \
  --display-name="Clickstream Events Dataset" \
  --description="Anonymized web clickstream data" \
  --source-dataset=projects/my-project/datasets/clickstream_public \
  --project=my-project

# List listings in an exchange
gcloud bigquery analytics-hub listings list \
  --location=us-central1 \
  --data-exchange=my-exchange \
  --project=my-project

# Describe a listing
gcloud bigquery analytics-hub listings describe my-listing \
  --location=us-central1 \
  --data-exchange=my-exchange \
  --project=my-project

# Subscribe to a listing (creates linked dataset in subscriber project)
gcloud bigquery analytics-hub listings subscribe my-listing \
  --location=us-central1 \
  --data-exchange=my-exchange \
  --destination-dataset=subscriber-project:linked_dataset \
  --project=publisher-project

# Delete a listing
gcloud bigquery analytics-hub listings delete my-listing \
  --location=us-central1 \
  --data-exchange=my-exchange \
  --project=my-project
```
