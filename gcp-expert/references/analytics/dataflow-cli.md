# Dataflow — CLI Reference

Dataflow uses `gcloud dataflow` for job and template management. Pipeline submission is done via the Beam SDK (Python/Java) with `--runner=DataflowRunner`, or via template commands for pre-built pipelines.

---

## Jobs

```bash
# List jobs in a project/region
gcloud dataflow jobs list \
  --region=us-central1 \
  --project=my-project

# List jobs with filters (active jobs only)
gcloud dataflow jobs list \
  --region=us-central1 \
  --filter="currentState=JOB_STATE_RUNNING"

# List all jobs including historical
gcloud dataflow jobs list \
  --region=us-central1 \
  --status=all

# Describe a job (state, parameters, metrics)
gcloud dataflow jobs describe JOB_ID \
  --region=us-central1

# Show job options (parameters used at launch)
gcloud dataflow jobs show-options JOB_ID \
  --region=us-central1

# Cancel a streaming or batch job (immediate stop)
gcloud dataflow jobs cancel JOB_ID \
  --region=us-central1

# Drain a streaming job (stop accepting new input; process buffered data)
# Preferred over cancel for streaming jobs — avoids data loss
gcloud dataflow jobs drain JOB_ID \
  --region=us-central1
```

---

## Running Flex Templates

Flex Templates package pipelines as Docker containers. This is the recommended approach for new pipelines.

```bash
# Run a Flex Template job
gcloud dataflow flex-template run "my-job-$(date +%Y%m%d-%H%M%S)" \
  --template-file-gcs-location=gs://my-bucket/templates/my-template.json \
  --region=us-central1 \
  --project=my-project \
  --parameters inputTopic=projects/my-project/topics/my-topic \
  --parameters outputTable=my-project:my_dataset.my_table \
  --parameters tempLocation=gs://my-bucket/temp/ \
  --parameters maxNumWorkers=10

# Run Google-provided Flex Template: Pub/Sub to BigQuery
gcloud dataflow flex-template run "pubsub-to-bq-$(date +%Y%m%d)" \
  --template-file-gcs-location=gs://dataflow-templates-us-central1/latest/flex/PubSub_to_BigQuery_Flex \
  --region=us-central1 \
  --parameters inputTopic=projects/my-project/topics/events \
  --parameters outputTableSpec=my-project:my_dataset.events_raw \
  --parameters outputDeadletterTable=my-project:my_dataset.events_deadletter

# Run Datastream to BigQuery Flex Template (CDC replication)
gcloud dataflow flex-template run "datastream-to-bq-$(date +%Y%m%d)" \
  --template-file-gcs-location=gs://dataflow-templates-us-central1/latest/flex/Cloud_Datastream_to_BigQuery \
  --region=us-central1 \
  --parameters inputFilePattern=gs://my-bucket/datastream/**/*.avro \
  --parameters gcsPubSubSubscription=projects/my-project/subscriptions/datastream-sub \
  --parameters outputProjectId=my-project \
  --parameters outputStagingDatasetTemplate={_metadata_dataset} \
  --parameters outputStagingTableNameTemplate={_metadata_table}_log \
  --parameters outputDatasetTemplate={_metadata_dataset} \
  --parameters outputTableNameTemplate={_metadata_table} \
  --parameters deadLetterQueueDirectory=gs://my-bucket/dlq/
```

---

## Building Flex Templates

```bash
# Build a Flex Template (packages pipeline as Docker image + template spec)
gcloud dataflow flex-template build gs://my-bucket/templates/my-template.json \
  --image-gcr-path=us-central1-docker.pkg.dev/my-project/dataflow-templates/my-pipeline:latest \
  --sdk-language=PYTHON \
  --flex-template-base-image=PYTHON3 \
  --metadata-file=metadata.json \
  --py-path=pipeline.py \
  --env=FLEX_TEMPLATE_PYTHON_PY_FILE=pipeline.py \
  --env=FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE=requirements.txt

# Build a Java Flex Template
gcloud dataflow flex-template build gs://my-bucket/templates/java-pipeline.json \
  --image-gcr-path=us-central1-docker.pkg.dev/my-project/dataflow-templates/java-pipeline:latest \
  --sdk-language=JAVA \
  --image=us-central1-docker.pkg.dev/my-project/dataflow-templates/java-pipeline:latest
```

---

## Running Classic Templates

Classic Templates are pre-compiled pipeline JARs stored in GCS.

```bash
# Run a Classic Template job
gcloud dataflow jobs run my-classic-job \
  --gcs-location=gs://dataflow-templates-us-central1/latest/GCS_Text_to_BigQuery \
  --region=us-central1 \
  --staging-location=gs://my-bucket/temp \
  --parameters javascriptTextTransformGcsPath=gs://my-bucket/udf/transform.js \
  --parameters JSONPath=gs://my-bucket/schema/schema.json \
  --parameters javascriptTextTransformFunctionName=transform \
  --parameters inputFilePattern=gs://my-bucket/input/*.csv \
  --parameters outputTable=my-project:my_dataset.output \
  --parameters bigQueryLoadingTemporaryDirectory=gs://my-bucket/bq-temp/

# Run Pub/Sub to Cloud Storage Classic Template
gcloud dataflow jobs run pubsub-to-gcs \
  --gcs-location=gs://dataflow-templates-us-central1/latest/Cloud_PubSub_to_GCS_Text \
  --region=us-central1 \
  --staging-location=gs://my-bucket/temp \
  --parameters inputTopic=projects/my-project/topics/my-topic \
  --parameters outputDirectory=gs://my-bucket/output/ \
  --parameters outputFilenamePrefix=output- \
  --parameters outputFilenameSuffix=.txt \
  --parameters windowDuration=5m
```

---

## Metrics

```bash
# List metrics for a job
gcloud dataflow metrics list JOB_ID \
  --region=us-central1

# List metrics with filter (e.g., system metrics only)
gcloud dataflow metrics list JOB_ID \
  --region=us-central1 \
  --filter="name.origin=dataflow/v1b3"

# Get specific metric value
gcloud dataflow metrics list JOB_ID \
  --region=us-central1 \
  --filter="name.name=ElementCount" \
  --format="value(scalar)"
```

---

## Snapshots (Streaming Jobs)

Snapshots capture the in-flight state of a streaming pipeline for safe restarts.

```bash
# Create a snapshot of a running streaming job
gcloud dataflow snapshots create \
  --job-id=JOB_ID \
  --region=us-central1 \
  --snapshot-sources \
  --ttl=7d

# List snapshots for a region
gcloud dataflow snapshots list \
  --region=us-central1 \
  --project=my-project

# Describe a snapshot
gcloud dataflow snapshots describe SNAPSHOT_ID \
  --region=us-central1

# Delete a snapshot
gcloud dataflow snapshots delete SNAPSHOT_ID \
  --region=us-central1
```

---

## Dataflow SQL

```bash
# Launch a Dataflow SQL query against Pub/Sub
gcloud dataflow sql query \
  --job-name=my-sql-job \
  --region=us-central1 \
  --bigquery-write-disposition=WRITE_APPEND \
  --bigquery-project=my-project \
  --bigquery-dataset=my_dataset \
  --bigquery-table=sql_output \
  'SELECT
     user_id,
     COUNT(*) AS event_count,
     TUMBLE_START("INTERVAL 1 MINUTE") AS window_start
   FROM pubsub.topic.`my-project`.`my-topic`
   GROUP BY
     user_id,
     TUMBLE(event_timestamp, "INTERVAL 1 MINUTE")'
```

---

## Submitting Pipelines via Beam SDK

While not a `gcloud` command, this is the primary way to launch custom pipelines:

```bash
# Python pipeline submission to Dataflow
python my_pipeline.py \
  --runner=DataflowRunner \
  --project=my-project \
  --region=us-central1 \
  --staging_location=gs://my-bucket/staging \
  --temp_location=gs://my-bucket/temp \
  --job_name=my-pipeline-job \
  --setup_file=./setup.py \
  --service_account_email=dataflow-sa@my-project.iam.gserviceaccount.com \
  --network=my-vpc \
  --subnetwork=regions/us-central1/subnetworks/my-subnet \
  --no_use_public_ips \
  --enable_streaming_engine \
  --max_num_workers=50 \
  --worker_machine_type=n2-standard-4 \
  --streaming

# Java pipeline submission
mvn compile exec:java \
  -Dexec.mainClass=com.example.MyPipeline \
  -Dexec.args=" \
    --runner=DataflowRunner \
    --project=my-project \
    --region=us-central1 \
    --stagingLocation=gs://my-bucket/staging \
    --tempLocation=gs://my-bucket/temp \
    --jobName=my-java-pipeline \
    --serviceAccount=dataflow-sa@my-project.iam.gserviceaccount.com \
    --enableStreamingEngine"
```

---

## IAM for Dataflow

```bash
# Grant Dataflow Worker role to service account (minimum for running jobs)
gcloud projects add-iam-policy-binding my-project \
  --member="serviceAccount:dataflow-sa@my-project.iam.gserviceaccount.com" \
  --role="roles/dataflow.worker"

# Grant Dataflow Admin role (submit and manage jobs)
gcloud projects add-iam-policy-binding my-project \
  --member="serviceAccount:ci-sa@my-project.iam.gserviceaccount.com" \
  --role="roles/dataflow.admin"

# Dataflow SA also needs these on resources it accesses:
# roles/storage.objectAdmin on GCS buckets
# roles/bigquery.dataEditor on BigQuery datasets
# roles/pubsub.subscriber on Pub/Sub subscriptions
# roles/pubsub.publisher on Pub/Sub topics (if writing)

# Key IAM roles:
# roles/dataflow.admin     - submit, cancel, modify jobs
# roles/dataflow.developer - submit and view jobs
# roles/dataflow.viewer    - view jobs and metrics only
# roles/dataflow.worker    - SA role for worker VMs
```
