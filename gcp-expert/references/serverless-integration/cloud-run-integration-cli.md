# Cloud Run & Functions — Integration CLI

## Deploy Cloud Run Service with Pub/Sub Authentication

```bash
# Create a service account for Pub/Sub to invoke Cloud Run
gcloud iam service-accounts create pubsub-invoker \
  --display-name="Pub/Sub Cloud Run Invoker"

# Grant the invoker role on the Cloud Run service
gcloud run services add-iam-policy-binding my-service \
  --region=us-central1 \
  --member="serviceAccount:pubsub-invoker@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

# Get the Cloud Run service URL
SERVICE_URL=$(gcloud run services describe my-service \
  --region=us-central1 \
  --format="value(status.url)")

# Create a Pub/Sub push subscription pointing to Cloud Run with OIDC auth
gcloud pubsub subscriptions create my-push-sub \
  --topic=my-topic \
  --push-endpoint="${SERVICE_URL}/pubsub" \
  --push-auth-service-account="pubsub-invoker@PROJECT_ID.iam.gserviceaccount.com" \
  --ack-deadline=60 \
  --min-retry-delay=10s \
  --max-retry-delay=600s \
  --dead-letter-topic=my-dead-letter-topic \
  --max-delivery-attempts=5

# Grant Pub/Sub the ability to create tokens for the invoker SA
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:service-PROJECT_NUMBER@gcp-sa-pubsub.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountTokenCreator"
```

## Deploy Cloud Run with Cloud SQL (Built-in Socket)

```bash
# Deploy Cloud Run service with Cloud SQL connection
gcloud run deploy my-api \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-api:latest \
  --region=us-central1 \
  --service-account=my-runtime-sa@PROJECT_ID.iam.gserviceaccount.com \
  --add-cloudsql-instances=PROJECT_ID:us-central1:my-postgres-instance \
  --set-env-vars="DB_HOST=/cloudsql/PROJECT_ID:us-central1:my-postgres-instance,DB_NAME=mydb,DB_USER=myuser" \
  --set-secrets="DB_PASS=db-password:latest" \
  --no-allow-unauthenticated

# Grant Cloud SQL Client role to runtime SA
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:my-runtime-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"
```

## Deploy Cloud Run with Secret Manager

```bash
# Grant Secret Manager accessor to the runtime service account
gcloud secrets add-iam-policy-binding my-api-key \
  --member="serviceAccount:my-runtime-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Mount a secret as an environment variable (resolved at startup)
gcloud run deploy my-service \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-service:latest \
  --region=us-central1 \
  --set-secrets="API_KEY=my-api-key:latest,DB_PASS=db-password:2"

# Mount a secret as a volume file (auto-refreshed on rotation)
gcloud run deploy my-service \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-service:latest \
  --region=us-central1 \
  --set-secrets="/secrets/api-key=my-api-key:latest"
```

## Direct VPC Egress

```bash
# Deploy with Direct VPC Egress (no connector needed)
gcloud run deploy my-service \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-service:latest \
  --region=us-central1 \
  --network=my-vpc \
  --subnet=my-subnet \
  --vpc-egress=all-traffic

# Deploy with private-ranges-only egress (default; only RFC 1918 via VPC)
gcloud run deploy my-service \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-service:latest \
  --region=us-central1 \
  --network=my-vpc \
  --subnet=my-subnet \
  --vpc-egress=private-ranges-only
```

## Serverless VPC Access Connector

```bash
# Create a Serverless VPC Access connector
gcloud compute networks vpc-access connectors create my-connector \
  --region=us-central1 \
  --network=my-vpc \
  --range=10.8.0.0/28 \
  --min-instances=2 \
  --max-instances=10 \
  --machine-type=e2-micro

# Deploy Cloud Run using the connector
gcloud run deploy my-service \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-service:latest \
  --region=us-central1 \
  --vpc-connector=my-connector \
  --vpc-egress=private-ranges-only

# List connectors
gcloud compute networks vpc-access connectors list --region=us-central1

# Delete connector
gcloud compute networks vpc-access connectors delete my-connector --region=us-central1
```

## Cloud Run Jobs

```bash
# Create a Cloud Run Job
gcloud run jobs create my-batch-job \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/batch-worker:latest \
  --region=us-central1 \
  --service-account=batch-sa@PROJECT_ID.iam.gserviceaccount.com \
  --task-timeout=3600s \
  --parallelism=10 \
  --tasks=100 \
  --max-retries=3 \
  --cpu=2 \
  --memory=4Gi \
  --set-env-vars="OUTPUT_BUCKET=my-results-bucket"

# Execute the job (run all tasks)
gcloud run jobs execute my-batch-job \
  --region=us-central1 \
  --wait

# Execute job and tail logs
gcloud run jobs execute my-batch-job \
  --region=us-central1 \
  --wait \
  --async
# Then stream logs:
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=my-batch-job" \
  --freshness=1h \
  --format="value(textPayload)"

# Describe job status
gcloud run jobs describe my-batch-job --region=us-central1

# List recent executions
gcloud run jobs executions list --job=my-batch-job --region=us-central1

# Describe a specific execution
gcloud run jobs executions describe EXECUTION_NAME --region=us-central1

# Update job configuration
gcloud run jobs update my-batch-job \
  --region=us-central1 \
  --parallelism=20 \
  --tasks=200

# Delete job
gcloud run jobs delete my-batch-job --region=us-central1
```

## Cloud Scheduler → Cloud Run

```bash
# Create service account for Scheduler to invoke Cloud Run
gcloud iam service-accounts create scheduler-invoker \
  --display-name="Cloud Scheduler Cloud Run Invoker"

gcloud run services add-iam-policy-binding my-service \
  --region=us-central1 \
  --member="serviceAccount:scheduler-invoker@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

SERVICE_URL=$(gcloud run services describe my-service \
  --region=us-central1 \
  --format="value(status.url)")

# Create Cloud Scheduler job with OIDC auth
gcloud scheduler jobs create http my-cron-job \
  --location=us-central1 \
  --schedule="0 2 * * *" \
  --uri="${SERVICE_URL}/run-report" \
  --http-method=POST \
  --message-body='{"report_date": "today"}' \
  --headers="Content-Type=application/json" \
  --oidc-service-account-email="scheduler-invoker@PROJECT_ID.iam.gserviceaccount.com" \
  --oidc-token-audience="${SERVICE_URL}" \
  --attempt-deadline=30m \
  --max-retry-attempts=3 \
  --min-backoff=30s \
  --max-backoff=600s

# Trigger a scheduler job manually
gcloud scheduler jobs run my-cron-job --location=us-central1

# List scheduler jobs
gcloud scheduler jobs list --location=us-central1

# Pause/resume a scheduler job
gcloud scheduler jobs pause my-cron-job --location=us-central1
gcloud scheduler jobs resume my-cron-job --location=us-central1

# Delete scheduler job
gcloud scheduler jobs delete my-cron-job --location=us-central1
```

## Cloud Tasks → Cloud Run

```bash
# Create a Cloud Tasks queue targeting Cloud Run
gcloud tasks queues create my-work-queue \
  --location=us-central1 \
  --max-dispatches-per-second=100 \
  --max-concurrent-dispatches=50 \
  --max-attempts=5 \
  --min-backoff=1s \
  --max-backoff=300s \
  --max-doublings=5

# Create a service account for Cloud Tasks to invoke Cloud Run
gcloud iam service-accounts create tasks-invoker \
  --display-name="Cloud Tasks Cloud Run Invoker"

gcloud run services add-iam-policy-binding my-worker \
  --region=us-central1 \
  --member="serviceAccount:tasks-invoker@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

SERVICE_URL=$(gcloud run services describe my-worker \
  --region=us-central1 \
  --format="value(status.url)")

# Enqueue a task (typically done programmatically; gcloud for testing)
gcloud tasks create-http-task \
  --queue=my-work-queue \
  --location=us-central1 \
  --url="${SERVICE_URL}/process" \
  --method=POST \
  --body='{"item_id": "abc123"}' \
  --header="Content-Type:application/json" \
  --oidc-service-account-email="tasks-invoker@PROJECT_ID.iam.gserviceaccount.com" \
  --oidc-token-audience="${SERVICE_URL}" \
  --schedule-time="2024-12-01T10:00:00Z"

# List tasks in a queue
gcloud tasks list --queue=my-work-queue --location=us-central1

# Pause/resume queue
gcloud tasks queues pause my-work-queue --location=us-central1
gcloud tasks queues resume my-work-queue --location=us-central1

# Purge all tasks from a queue
gcloud tasks queues purge my-work-queue --location=us-central1

# Describe queue
gcloud tasks queues describe my-work-queue --location=us-central1
```

## Cloud Functions (2nd Gen) Integration

```bash
# Deploy Cloud Function with Pub/Sub trigger (2nd gen)
gcloud functions deploy process-message \
  --gen2 \
  --region=us-central1 \
  --runtime=python311 \
  --source=. \
  --entry-point=process_message \
  --trigger-topic=my-input-topic \
  --service-account=functions-sa@PROJECT_ID.iam.gserviceaccount.com \
  --memory=512Mi \
  --timeout=60s

# Deploy Cloud Function with Cloud Storage trigger (object finalize)
gcloud functions deploy process-upload \
  --gen2 \
  --region=us-central1 \
  --runtime=nodejs20 \
  --source=. \
  --entry-point=processUpload \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --trigger-event-filters="bucket=my-uploads-bucket" \
  --service-account=functions-sa@PROJECT_ID.iam.gserviceaccount.com

# Deploy HTTP Cloud Function (no unauthenticated access)
gcloud functions deploy my-api \
  --gen2 \
  --region=us-central1 \
  --runtime=go121 \
  --source=. \
  --entry-point=HandleRequest \
  --trigger-http \
  --no-allow-unauthenticated \
  --service-account=functions-sa@PROJECT_ID.iam.gserviceaccount.com \
  --vpc-connector=my-connector

# List functions
gcloud functions list --region=us-central1

# Describe function
gcloud functions describe process-message --gen2 --region=us-central1

# View function logs
gcloud functions logs read process-message --gen2 --region=us-central1 --limit=50

# Delete function
gcloud functions delete process-message --gen2 --region=us-central1
```

## Minimum Instances and CPU Boost

```bash
# Deploy with minimum instances to prevent cold starts
gcloud run deploy latency-sensitive-api \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/api:latest \
  --region=us-central1 \
  --min-instances=2 \
  --max-instances=100 \
  --cpu-boost \
  --cpu=2 \
  --memory=1Gi \
  --concurrency=80 \
  --timeout=30s
```
