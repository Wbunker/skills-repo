# Cloud Scheduler & Cloud Tasks — CLI Reference

---

## Cloud Scheduler

### Creating Jobs

```bash
# Create an HTTP job (POST to HTTPS endpoint, no auth)
gcloud scheduler jobs create http daily-report \
  --location=us-central1 \
  --schedule="0 8 * * *" \
  --uri=https://my-service.example.com/reports/generate \
  --http-method=POST \
  --time-zone=America/New_York \
  --description="Generate daily sales report at 8 AM ET" \
  --project=my-project

# Create HTTP job with OIDC auth for Cloud Run (recommended)
gcloud scheduler jobs create http invoke-cloud-run \
  --location=us-central1 \
  --schedule="0 2 * * *" \
  --uri=https://my-service-abc123-uc.a.run.app/nightly-job \
  --http-method=POST \
  --oidc-service-account-email=scheduler-sa@my-project.iam.gserviceaccount.com \
  --oidc-token-audience=https://my-service-abc123-uc.a.run.app \
  --time-zone=UTC \
  --project=my-project

# Create HTTP job with a JSON body and custom headers
gcloud scheduler jobs create http process-data \
  --location=us-central1 \
  --schedule="0 */4 * * *" \
  --uri=https://my-api.example.com/api/v1/process \
  --http-method=POST \
  --headers=Content-Type=application/json,X-Job-Source=scheduler \
  --message-body='{"date": "today", "environment": "production"}' \
  --oidc-service-account-email=scheduler-sa@my-project.iam.gserviceaccount.com \
  --oidc-token-audience=https://my-api.example.com \
  --time-zone=UTC \
  --project=my-project

# Create HTTP job with retry configuration
gcloud scheduler jobs create http retry-enabled-job \
  --location=us-central1 \
  --schedule="0 9 * * MON-FRI" \
  --uri=https://my-service-abc123-uc.a.run.app/weekly-task \
  --http-method=POST \
  --oidc-service-account-email=scheduler-sa@my-project.iam.gserviceaccount.com \
  --oidc-token-audience=https://my-service-abc123-uc.a.run.app \
  --max-retry-attempts=3 \
  --min-backoff=5s \
  --max-backoff=1h \
  --max-doublings=5 \
  --attempt-deadline=5m \
  --time-zone=America/Chicago \
  --project=my-project

# Create HTTP job with OAuth2 (for Google APIs)
gcloud scheduler jobs create http call-google-api \
  --location=us-central1 \
  --schedule="0 6 * * *" \
  --uri=https://bigquery.googleapis.com/bigquery/v2/projects/my-project/jobs \
  --http-method=POST \
  --oauth-service-account-email=scheduler-sa@my-project.iam.gserviceaccount.com \
  --oauth-token-scope=https://www.googleapis.com/auth/bigquery \
  --message-body='{"configuration": {"query": {"query": "SELECT 1", "useLegacySql": false}}}' \
  --headers=Content-Type=application/json \
  --project=my-project

# Create a Pub/Sub job (publish message to topic)
gcloud scheduler jobs create pubsub send-pubsub-message \
  --location=us-central1 \
  --schedule="*/15 * * * *" \
  --topic=projects/my-project/topics/scheduled-events \
  --message-body='{"type": "heartbeat"}' \
  --attributes=source=scheduler,env=production \
  --time-zone=UTC \
  --project=my-project

# Create an App Engine HTTP job (legacy)
gcloud scheduler jobs create app-engine run-cron-handler \
  --location=us-central1 \
  --schedule="0 0 * * *" \
  --relative-url=/cron/daily-cleanup \
  --service=worker \
  --version=v1 \
  --http-method=GET \
  --project=my-project
```

### Managing Jobs

```bash
# List scheduler jobs in a location
gcloud scheduler jobs list \
  --location=us-central1 \
  --project=my-project

# List jobs across all locations
gcloud scheduler jobs list \
  --location=- \
  --project=my-project

# Describe a job
gcloud scheduler jobs describe daily-report \
  --location=us-central1 \
  --project=my-project

# Update job schedule
gcloud scheduler jobs update http daily-report \
  --location=us-central1 \
  --schedule="0 9 * * *" \
  --project=my-project

# Update job URI
gcloud scheduler jobs update http daily-report \
  --location=us-central1 \
  --uri=https://new-service-abc123-uc.a.run.app/reports/generate \
  --project=my-project

# Update job message body
gcloud scheduler jobs update http process-data \
  --location=us-central1 \
  --message-body='{"date": "today", "environment": "staging"}' \
  --project=my-project

# Pause a job (stops firing without deleting)
gcloud scheduler jobs pause daily-report \
  --location=us-central1 \
  --project=my-project

# Resume a paused job
gcloud scheduler jobs resume daily-report \
  --location=us-central1 \
  --project=my-project

# Manually trigger a job (force run outside schedule)
gcloud scheduler jobs run daily-report \
  --location=us-central1 \
  --project=my-project

# Delete a job
gcloud scheduler jobs delete daily-report \
  --location=us-central1 \
  --project=my-project
```

---

## Cloud Tasks

### Creating Queues

```bash
# Create a basic task queue
gcloud tasks queues create my-queue \
  --location=us-central1 \
  --project=my-project

# Create a queue with rate limiting and retry config
gcloud tasks queues create rate-limited-queue \
  --location=us-central1 \
  --max-dispatches-per-second=10 \
  --max-concurrent-dispatches=5 \
  --max-attempts=5 \
  --min-backoff=2s \
  --max-backoff=300s \
  --max-doublings=5 \
  --project=my-project

# Create a queue for high-throughput fan-out
gcloud tasks queues create notification-queue \
  --location=us-central1 \
  --max-dispatches-per-second=500 \
  --max-concurrent-dispatches=100 \
  --max-attempts=10 \
  --min-backoff=1s \
  --max-backoff=3600s \
  --max-doublings=10 \
  --max-retry-duration=86400s \
  --project=my-project

# List queues
gcloud tasks queues list \
  --location=us-central1 \
  --project=my-project

# Describe a queue
gcloud tasks queues describe my-queue \
  --location=us-central1 \
  --project=my-project

# Update queue rate limits
gcloud tasks queues update my-queue \
  --location=us-central1 \
  --max-dispatches-per-second=50 \
  --max-concurrent-dispatches=20 \
  --project=my-project

# Update queue retry config
gcloud tasks queues update my-queue \
  --location=us-central1 \
  --max-attempts=3 \
  --max-retry-duration=3600s \
  --min-backoff=5s \
  --max-backoff=600s \
  --project=my-project

# Pause a queue (stop dispatching tasks; tasks remain in queue)
gcloud tasks queues pause my-queue \
  --location=us-central1 \
  --project=my-project

# Resume a paused queue
gcloud tasks queues resume my-queue \
  --location=us-central1 \
  --project=my-project

# Purge all tasks from a queue
gcloud tasks queues purge my-queue \
  --location=us-central1 \
  --project=my-project

# Delete a queue (must be paused or empty first)
gcloud tasks queues delete my-queue \
  --location=us-central1 \
  --project=my-project
```

### Creating Tasks

```bash
# Create a simple HTTP task
gcloud tasks create-http-task \
  --queue=my-queue \
  --location=us-central1 \
  --url=https://my-service-abc123-uc.a.run.app/process \
  --method=POST \
  --body-content='{"job_id": 12345, "action": "process"}' \
  --header=Content-Type:application/json \
  --project=my-project

# Create an HTTP task with OIDC authentication (for Cloud Run)
gcloud tasks create-http-task \
  --queue=my-queue \
  --location=us-central1 \
  --url=https://my-service-abc123-uc.a.run.app/process \
  --method=POST \
  --body-content='{"user_id": 456, "event": "send_welcome_email"}' \
  --header=Content-Type:application/json \
  --oidc-service-account-email=tasks-invoker@my-project.iam.gserviceaccount.com \
  --oidc-token-audience=https://my-service-abc123-uc.a.run.app \
  --project=my-project

# Create a task with a scheduled delivery time (delay by 5 minutes)
gcloud tasks create-http-task \
  --queue=my-queue \
  --location=us-central1 \
  --url=https://my-service-abc123-uc.a.run.app/follow-up \
  --method=POST \
  --body-content='{"user_id": 789}' \
  --oidc-service-account-email=tasks-invoker@my-project.iam.gserviceaccount.com \
  --oidc-token-audience=https://my-service-abc123-uc.a.run.app \
  --schedule-time=$(date -u -d '+5 minutes' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v+5M +%Y-%m-%dT%H:%M:%SZ) \
  --project=my-project

# Create a task with a specific schedule time (ISO 8601)
gcloud tasks create-http-task \
  --queue=my-queue \
  --location=us-central1 \
  --url=https://my-service-abc123-uc.a.run.app/reminder \
  --method=POST \
  --body-content='{"reminder_id": "rem-001"}' \
  --oidc-service-account-email=tasks-invoker@my-project.iam.gserviceaccount.com \
  --oidc-token-audience=https://my-service-abc123-uc.a.run.app \
  --schedule-time=2024-06-01T09:00:00Z \
  --project=my-project

# Create a named task (enables deduplication by name)
gcloud tasks create-http-task \
  --queue=my-queue \
  --location=us-central1 \
  --task-name=process-order-order-12345 \
  --url=https://my-service-abc123-uc.a.run.app/orders/process \
  --method=POST \
  --body-content='{"order_id": "order-12345"}' \
  --oidc-service-account-email=tasks-invoker@my-project.iam.gserviceaccount.com \
  --oidc-token-audience=https://my-service-abc123-uc.a.run.app \
  --project=my-project

# Create an App Engine task (legacy)
gcloud tasks create-app-engine-task \
  --queue=legacy-queue \
  --location=us-central1 \
  --routing=service:worker,version:v2 \
  --method=POST \
  --relative-uri=/tasks/process \
  --body-content='{"task_id": 99}' \
  --project=my-project
```

### Managing Tasks

```bash
# List tasks in a queue
gcloud tasks list \
  --queue=my-queue \
  --location=us-central1 \
  --project=my-project

# Describe a specific task
gcloud tasks describe TASK_ID \
  --queue=my-queue \
  --location=us-central1 \
  --project=my-project

# Manually run a task (force immediate dispatch)
gcloud tasks run TASK_ID \
  --queue=my-queue \
  --location=us-central1 \
  --project=my-project

# Delete a specific task
gcloud tasks delete TASK_ID \
  --queue=my-queue \
  --location=us-central1 \
  --project=my-project
```

---

## IAM Setup for Cloud Scheduler and Cloud Tasks

```bash
# Grant Cloud Run Invoker to Scheduler SA (allows Scheduler to call Cloud Run)
gcloud run services add-iam-policy-binding my-service \
  --region=us-central1 \
  --member="serviceAccount:scheduler-sa@my-project.iam.gserviceaccount.com" \
  --role="roles/run.invoker" \
  --project=my-project

# Grant Cloud Run Invoker to Tasks SA (allows Tasks to call Cloud Run)
gcloud run services add-iam-policy-binding my-service \
  --region=us-central1 \
  --member="serviceAccount:tasks-invoker@my-project.iam.gserviceaccount.com" \
  --role="roles/run.invoker" \
  --project=my-project

# Grant Cloud Functions Invoker (for Scheduler/Tasks calling Cloud Functions)
gcloud functions add-iam-policy-binding my-function \
  --region=us-central1 \
  --member="serviceAccount:scheduler-sa@my-project.iam.gserviceaccount.com" \
  --role="roles/cloudfunctions.invoker" \
  --project=my-project

# Create dedicated service accounts
gcloud iam service-accounts create scheduler-sa \
  --display-name="Cloud Scheduler Service Account" \
  --project=my-project

gcloud iam service-accounts create tasks-invoker \
  --display-name="Cloud Tasks HTTP Invoker" \
  --project=my-project

# Allow Cloud Tasks to create tasks (for application service account)
gcloud projects add-iam-policy-binding my-project \
  --member="serviceAccount:my-app-sa@my-project.iam.gserviceaccount.com" \
  --role="roles/cloudtasks.enqueuer"

# Key IAM roles:
# roles/cloudscheduler.admin     - manage Scheduler jobs
# roles/cloudscheduler.viewer    - view Scheduler jobs
# roles/cloudtasks.admin         - manage queues and tasks
# roles/cloudtasks.enqueuer      - create tasks in queues
# roles/cloudtasks.viewer        - view queues and tasks
# roles/run.invoker              - invoke Cloud Run services (for SA executing tasks)
```

---

## Cloud Tasks via Client Library (Code Reference)

Cloud Tasks is commonly used programmatically. This shows the Python pattern:

```python
# Python — Create an HTTP task with OIDC auth
from google.cloud import tasks_v2
from google.protobuf import duration_pb2, timestamp_pb2
import json
import datetime

client = tasks_v2.CloudTasksClient()

project = "my-project"
location = "us-central1"
queue_id = "my-queue"
queue_path = client.queue_path(project, location, queue_id)

service_url = "https://my-service-abc123-uc.a.run.app/process"
invoker_sa = "tasks-invoker@my-project.iam.gserviceaccount.com"

payload = {"user_id": 123, "action": "send_welcome_email"}

task = {
    "http_request": {
        "http_method": tasks_v2.HttpMethod.POST,
        "url": service_url,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(payload).encode(),
        "oidc_token": {
            "service_account_email": invoker_sa,
            "audience": service_url,
        },
    }
}

# Schedule for 5 minutes from now
schedule_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
timestamp = timestamp_pb2.Timestamp()
timestamp.FromDatetime(schedule_time)
task["schedule_time"] = timestamp

# Create with deduplication name
task["name"] = client.task_path(project, location, queue_id, f"process-user-{123}")

response = client.create_task(request={"parent": queue_path, "task": task})
print(f"Created task: {response.name}")
```
