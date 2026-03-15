# Cloud Functions — CLI Reference

Capabilities reference: [cloud-functions-capabilities.md](cloud-functions-capabilities.md)

Commands use `gcloud functions` (works for both 1st and 2nd gen). 2nd gen functions can also be managed via `gcloud run` for advanced configuration.

```bash
gcloud config set project my-project-id
```

---

## Deploy Functions

### HTTP Functions

```bash
# Deploy a 1st gen HTTP function (Node.js, public)
gcloud functions deploy my-http-function \
  --gen2=false \
  --runtime=nodejs20 \
  --entry-point=myHttpHandler \
  --trigger-http \
  --allow-unauthenticated \
  --region=us-central1 \
  --memory=256MB \
  --timeout=60s \
  --source=./my-function-dir

# Deploy a 2nd gen HTTP function (Python, authenticated)
gcloud functions deploy my-api-function \
  --gen2 \
  --runtime=python312 \
  --entry-point=handle_request \
  --trigger-http \
  --no-allow-unauthenticated \
  --region=us-central1 \
  --memory=512MB \
  --cpu=1 \
  --timeout=120s \
  --min-instances=0 \
  --max-instances=100 \
  --concurrency=10 \
  --service-account=my-function-sa@my-project.iam.gserviceaccount.com \
  --source=./my-function-dir

# Deploy with environment variables
gcloud functions deploy my-function \
  --gen2 \
  --runtime=nodejs20 \
  --entry-point=processRequest \
  --trigger-http \
  --allow-unauthenticated \
  --region=us-central1 \
  --set-env-vars=NODE_ENV=production,API_BASE_URL=https://api.example.com,LOG_LEVEL=info

# Deploy a Go HTTP function
gcloud functions deploy my-go-function \
  --gen2 \
  --runtime=go122 \
  --entry-point=HandleRequest \
  --trigger-http \
  --allow-unauthenticated \
  --region=us-central1 \
  --memory=256MB \
  --source=.
```

### Pub/Sub Triggered Functions

```bash
# Deploy a 1st gen Pub/Sub function (Python)
gcloud functions deploy my-pubsub-processor \
  --gen2=false \
  --runtime=python312 \
  --entry-point=process_message \
  --trigger-topic=my-topic \
  --region=us-central1 \
  --memory=256MB \
  --timeout=120s

# Deploy a 2nd gen Pub/Sub function via Eventarc
gcloud functions deploy my-pubsub-function \
  --gen2 \
  --runtime=python312 \
  --entry-point=process_message \
  --trigger-topic=my-input-topic \
  --region=us-central1 \
  --memory=512MB \
  --timeout=300s \
  --service-account=my-function-sa@my-project.iam.gserviceaccount.com
```

### Cloud Storage Triggered Functions

```bash
# Trigger on object finalize (new object created or overwritten)
gcloud functions deploy my-gcs-processor \
  --gen2 \
  --runtime=python312 \
  --entry-point=process_file \
  --trigger-bucket=my-input-bucket \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --region=us-central1 \
  --memory=1GB \
  --timeout=540s \
  --service-account=my-function-sa@my-project.iam.gserviceaccount.com

# 1st gen GCS trigger (simpler syntax)
gcloud functions deploy my-gcs-function \
  --runtime=nodejs20 \
  --entry-point=processFile \
  --trigger-bucket=my-input-bucket \
  --trigger-event=google.storage.object.finalize \
  --region=us-central1
```

### Eventarc Triggers (2nd Gen)

```bash
# Trigger on BigQuery job completion (via Audit Logs)
gcloud functions deploy my-bq-notifier \
  --gen2 \
  --runtime=python312 \
  --entry-point=handle_bq_event \
  --trigger-event-filters="type=google.cloud.audit.log.v1.written" \
  --trigger-event-filters="serviceName=bigquery.googleapis.com" \
  --trigger-event-filters="methodName=jobservice.jobcompleted" \
  --trigger-location=us-central1 \
  --region=us-central1 \
  --service-account=my-function-sa@my-project.iam.gserviceaccount.com

# Trigger on Firestore document write (2nd gen)
gcloud functions deploy my-firestore-function \
  --gen2 \
  --runtime=nodejs20 \
  --entry-point=onDocumentWrite \
  --trigger-event-filters="type=google.cloud.firestore.document.v1.written" \
  --trigger-event-filters="database=(default)" \
  --trigger-event-filters-path-pattern="document=users/{userId}" \
  --trigger-location=us-central1 \
  --region=us-central1
```

### Deploy with Secrets from Secret Manager

```bash
# Inject secret as environment variable
gcloud functions deploy my-function \
  --gen2 \
  --runtime=python312 \
  --entry-point=main \
  --trigger-http \
  --allow-unauthenticated \
  --region=us-central1 \
  --set-secrets=DB_PASSWORD=projects/my-project/secrets/db-password:latest,API_KEY=projects/my-project/secrets/api-key:v2

# Shorthand form (uses current project)
gcloud functions deploy my-function \
  --gen2 \
  --runtime=python312 \
  --entry-point=main \
  --trigger-http \
  --region=us-central1 \
  --set-secrets=DB_PASSWORD=db-password:latest

# Mount secrets as files
gcloud functions deploy my-function \
  --gen2 \
  --runtime=python312 \
  --entry-point=main \
  --trigger-http \
  --region=us-central1 \
  --set-secrets=/secrets/sa-key=my-sa-key:latest
```

### Deploy with VPC Connector

```bash
gcloud functions deploy my-private-function \
  --gen2 \
  --runtime=nodejs20 \
  --entry-point=handler \
  --trigger-http \
  --no-allow-unauthenticated \
  --region=us-central1 \
  --vpc-connector=my-vpc-connector \
  --vpc-connector-egress-settings=all-traffic
```

---

## Describe and List Functions

```bash
# List all functions in a region
gcloud functions list --region=us-central1

# List all functions across all regions
gcloud functions list

# List 2nd gen only
gcloud functions list --filter="environment=GEN_2"

# Describe a function (full config)
gcloud functions describe my-function --region=us-central1

# Get the HTTP trigger URL
gcloud functions describe my-function \
  --region=us-central1 \
  --format="get(serviceConfig.uri)"

# Get function status
gcloud functions describe my-function \
  --region=us-central1 \
  --format="get(state,stateMessages)"
```

---

## Invoke (Call) Functions

```bash
# Invoke an HTTP function directly (uses gcloud credentials for auth)
gcloud functions call my-http-function \
  --region=us-central1 \
  --data='{"name": "World"}'

# Invoke with JSON data from a file
gcloud functions call my-function \
  --region=us-central1 \
  --data="$(cat test-payload.json)"

# For 2nd gen HTTP functions (calls via the Cloud Run URL)
TOKEN=$(gcloud auth print-identity-token)
FUNCTION_URL=$(gcloud functions describe my-function --region=us-central1 --format="get(serviceConfig.uri)")
curl -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}' \
  "${FUNCTION_URL}"

# Invoke a Pub/Sub triggered function by publishing a test message
gcloud pubsub topics publish my-topic \
  --message='{"event_type": "test", "data": "hello"}'
```

---

## Read Logs

```bash
# Read recent logs for a function
gcloud functions logs read my-function \
  --region=us-central1 \
  --limit=50

# Read logs with a start time filter
gcloud functions logs read my-function \
  --region=us-central1 \
  --start-time="2024-01-15T10:00:00Z" \
  --end-time="2024-01-15T11:00:00Z"

# Tail logs (stream live logs - uses Cloud Logging)
gcloud logging tail \
  'resource.type="cloud_function" AND resource.labels.function_name="my-function"' \
  --format="value(textPayload)"

# For 2nd gen (Cloud Run backed), use Cloud Logging
gcloud logging read \
  'resource.type="cloud_run_revision" AND labels."goog-managed-by"="cloudfunctions" AND resource.labels.service_name="my-function"' \
  --limit=100 \
  --format="table(timestamp,textPayload,severity)"
```

---

## IAM — Invoker Permissions

```bash
# Allow unauthenticated invocation (public HTTP function)
gcloud functions add-invoker-policy-binding my-function \
  --region=us-central1 \
  --member=allUsers

# Grant a service account permission to invoke
gcloud functions add-invoker-policy-binding my-function \
  --region=us-central1 \
  --member=serviceAccount:caller-sa@my-project.iam.gserviceaccount.com

# Grant a user permission to invoke
gcloud functions add-invoker-policy-binding my-function \
  --region=us-central1 \
  --member=user:developer@example.com

# For 2nd gen (also works via Cloud Run IAM)
gcloud run services add-iam-policy-binding my-function \
  --region=us-central1 \
  --member=serviceAccount:pubsub-sa@my-project.iam.gserviceaccount.com \
  --role=roles/run.invoker

# View current IAM policy
gcloud functions get-iam-policy my-function --region=us-central1

# Remove invoker access
gcloud functions remove-invoker-policy-binding my-function \
  --region=us-central1 \
  --member=user:former-dev@example.com
```

---

## Update Functions

```bash
# Update environment variables
gcloud functions deploy my-function \
  --gen2 \
  --region=us-central1 \
  --update-env-vars=LOG_LEVEL=debug

# Update source code (redeploy)
gcloud functions deploy my-function \
  --gen2 \
  --runtime=python312 \
  --entry-point=main \
  --trigger-http \
  --region=us-central1 \
  --source=./updated-src

# Update memory and CPU (2nd gen)
gcloud functions deploy my-function \
  --gen2 \
  --runtime=python312 \
  --entry-point=main \
  --trigger-http \
  --region=us-central1 \
  --memory=1GB \
  --cpu=2 \
  --concurrency=50
```

---

## Delete Functions

```bash
# Delete a function
gcloud functions delete my-function --region=us-central1 --quiet

# Delete multiple functions
gcloud functions delete my-function-1 my-function-2 --region=us-central1 --quiet
```

---

## 2nd Gen Specific — Managing via Cloud Run

Since 2nd gen functions are Cloud Run services, you can use `gcloud run` commands for advanced configuration:

```bash
# View 2nd gen function as a Cloud Run service
gcloud run services describe my-function --region=us-central1

# Update traffic splitting for 2nd gen function
gcloud run services update-traffic my-function \
  --region=us-central1 \
  --to-revisions=my-function-00002-abc=90,my-function-00003-xyz=10

# View revisions of a 2nd gen function
gcloud run revisions list --service=my-function --region=us-central1
```
