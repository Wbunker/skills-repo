# Eventarc & Workflows — CLI

## Eventarc Triggers

### Create Triggers

```bash
# Create Eventarc trigger for Cloud Storage object creation → Cloud Run
gcloud eventarc triggers create process-new-file \
  --location=us-central1 \
  --destination-run-service=my-processor \
  --destination-run-region=us-central1 \
  --event-filters="type=google.cloud.storage.object.v1.finalized" \
  --event-filters="bucket=my-uploads-bucket" \
  --service-account=eventarc-trigger-sa@PROJECT_ID.iam.gserviceaccount.com

# Create Eventarc trigger for Cloud Audit Log event (BigQuery job completion)
gcloud eventarc triggers create bq-job-complete \
  --location=us-central1 \
  --destination-run-service=bq-job-handler \
  --destination-run-region=us-central1 \
  --event-filters="type=google.cloud.audit.log.v1.written" \
  --event-filters="serviceName=bigquery.googleapis.com" \
  --event-filters="methodName=google.cloud.bigquery.v2.JobService.InsertJob" \
  --service-account=eventarc-trigger-sa@PROJECT_ID.iam.gserviceaccount.com

# Create Eventarc trigger for Cloud Storage → Workflows
gcloud eventarc triggers create file-upload-workflow \
  --location=us-central1 \
  --destination-workflow=my-etl-workflow \
  --destination-workflow-location=us-central1 \
  --event-filters="type=google.cloud.storage.object.v1.finalized" \
  --event-filters="bucket=my-data-bucket" \
  --service-account=eventarc-trigger-sa@PROJECT_ID.iam.gserviceaccount.com

# Create Eventarc trigger for Pub/Sub topic → Cloud Run
gcloud eventarc triggers create pubsub-to-run \
  --location=us-central1 \
  --destination-run-service=message-processor \
  --destination-run-region=us-central1 \
  --event-filters="type=google.cloud.pubsub.topic.v1.messagePublished" \
  --transport-topic=my-events-topic \
  --service-account=eventarc-trigger-sa@PROJECT_ID.iam.gserviceaccount.com

# Create Eventarc trigger for Artifact Registry image push → Cloud Run
gcloud eventarc triggers create new-image-trigger \
  --location=us-central1 \
  --destination-run-service=image-scanner \
  --destination-run-region=us-central1 \
  --event-filters="type=google.cloud.artifactregistry.v1.docker.image.v1.finalized" \
  --service-account=eventarc-trigger-sa@PROJECT_ID.iam.gserviceaccount.com
```

### Manage Triggers

```bash
# List all triggers in a region
gcloud eventarc triggers list --location=us-central1

# List triggers across all locations
gcloud eventarc triggers list --location=-

# Describe a trigger
gcloud eventarc triggers describe process-new-file --location=us-central1

# Update trigger destination
gcloud eventarc triggers update process-new-file \
  --location=us-central1 \
  --destination-run-service=my-new-processor

# Update trigger event filters
gcloud eventarc triggers update bq-job-complete \
  --location=us-central1 \
  --event-filters="methodName=google.cloud.bigquery.v2.JobService.InsertJob"

# Delete a trigger
gcloud eventarc triggers delete process-new-file --location=us-central1

# Grant Eventarc Event Receiver role (required for the trigger SA)
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:eventarc-trigger-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/eventarc.eventReceiver"
```

### Eventarc Channels (Custom Events)

```bash
# Create a custom event channel
gcloud eventarc channels create my-app-channel \
  --location=us-central1 \
  --provider=projects/PROJECT_ID/locations/us-central1/channelConnections/my-connection

# List channels
gcloud eventarc channels list --location=us-central1

# Describe channel (get publish URL)
gcloud eventarc channels describe my-app-channel --location=us-central1

# Create a channel connection (from a third-party provider)
gcloud eventarc channel-connections create my-connection \
  --location=us-central1 \
  --channel=my-app-channel

# Create trigger from custom channel
gcloud eventarc triggers create custom-event-trigger \
  --location=us-central1 \
  --destination-run-service=my-custom-handler \
  --destination-run-region=us-central1 \
  --channel=my-app-channel \
  --event-filters="type=com.myapp.order.v1.created" \
  --service-account=eventarc-trigger-sa@PROJECT_ID.iam.gserviceaccount.com
```

---

## Workflows

### Create and Deploy Workflows

```bash
# Create a workflow from a YAML file
gcloud workflows deploy my-etl-workflow \
  --location=us-central1 \
  --source=workflow.yaml \
  --service-account=workflows-sa@PROJECT_ID.iam.gserviceaccount.com \
  --description="ETL orchestration workflow"

# Update a workflow (redeploy with new source)
gcloud workflows deploy my-etl-workflow \
  --location=us-central1 \
  --source=workflow-v2.yaml

# List workflows
gcloud workflows list --location=us-central1

# Describe a workflow
gcloud workflows describe my-etl-workflow --location=us-central1

# Delete a workflow
gcloud workflows delete my-etl-workflow --location=us-central1
```

### Execute Workflows

```bash
# Execute a workflow (no input arguments)
gcloud workflows run my-etl-workflow --location=us-central1

# Execute a workflow with JSON input arguments
gcloud workflows run my-etl-workflow \
  --location=us-central1 \
  --data='{"input_bucket": "gs://my-data", "output_table": "my-project.dataset.table", "date": "2024-11-15"}'

# Execute and wait for result (synchronous)
gcloud workflows run my-etl-workflow \
  --location=us-central1 \
  --data='{"date": "2024-11-15"}' \
  --call-log-level=LOG_ALL_CALLS

# Execute and capture the execution ID
EXECUTION_ID=$(gcloud workflows run my-etl-workflow \
  --location=us-central1 \
  --format="value(name)" | awk -F/ '{print $NF}')
```

### Manage Executions

```bash
# List recent executions of a workflow
gcloud workflows executions list my-etl-workflow \
  --location=us-central1 \
  --limit=20

# List only failed executions
gcloud workflows executions list my-etl-workflow \
  --location=us-central1 \
  --filter="state=FAILED"

# Describe an execution (see status, result, error)
gcloud workflows executions describe EXECUTION_ID \
  --workflow=my-etl-workflow \
  --location=us-central1

# Wait for an execution to complete
gcloud workflows executions wait EXECUTION_ID \
  --workflow=my-etl-workflow \
  --location=us-central1

# Cancel a running execution
gcloud workflows executions cancel EXECUTION_ID \
  --workflow=my-etl-workflow \
  --location=us-central1

# Get the result of a completed execution
gcloud workflows executions describe EXECUTION_ID \
  --workflow=my-etl-workflow \
  --location=us-central1 \
  --format="value(result)"

# List executions across all workflows
gcloud workflows executions list --location=us-central1 \
  --filter="workflowRevisionId:*"
```

### IAM for Workflows

```bash
# Grant Workflows Invoker role (to trigger workflows via HTTP/Scheduler/Eventarc)
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:scheduler-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/workflows.invoker"

# Grant Workflows runtime SA permissions to call GCP APIs it needs
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:workflows-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:workflows-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:workflows-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

### Example Workflow YAML Files

**Simple GCS → BigQuery ETL workflow (workflow.yaml)**:

```yaml
# workflow.yaml
main:
  params: [args]
  steps:
    - init:
        assign:
          - project_id: ${sys.get_env("GOOGLE_CLOUD_PROJECT_ID")}
          - input_bucket: ${args.input_bucket}
          - output_table: ${args.output_table}

    - run_bq_load:
        call: googleapis.bigquery.v2.jobs.insert
        args:
          projectId: ${project_id}
          body:
            configuration:
              load:
                sourceUris:
                  - ${"gs://" + input_bucket + "/*.csv"}
                destinationTable:
                  projectId: ${project_id}
                  datasetId: ${text.split(output_table, ".")[1]}
                  tableId: ${text.split(output_table, ".")[2]}
                sourceFormat: CSV
                writeDisposition: WRITE_TRUNCATE
                autodetect: true
        result: load_job

    - wait_for_job:
        call: googleapis.bigquery.v2.jobs.get
        args:
          projectId: ${project_id}
          jobId: ${load_job.jobReference.jobId}
        result: job_status

    - check_status:
        switch:
          - condition: ${job_status.status.state == "DONE"}
            next: check_error
          - condition: true
            steps:
              - sleep:
                  call: sys.sleep
                  args:
                    seconds: 5
              - retry_check:
                  next: wait_for_job

    - check_error:
        switch:
          - condition: ${"errorResult" in job_status.status}
            raise: ${job_status.status.errorResult.message}

    - return_result:
        return: ${job_status.jobReference.jobId}
```

**Workflow with callback (approval gate)**:

```yaml
# approval-workflow.yaml
main:
  params: [args]
  steps:
    - create_callback:
        call: events.create_callback_endpoint
        args:
          http_callback_method: POST
        result: callback_details

    - notify_approver:
        call: http.post
        args:
          url: https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
          body:
            text: ${"Approve deployment? Click: " + callback_details.http_callback_uri}

    - wait_for_approval:
        call: events.await_callback
        args:
          callback: ${callback_details}
          http_callback_method: POST
        result: approval_response

    - check_approval:
        switch:
          - condition: ${approval_response.http_request.body.approved == true}
            next: deploy
          - condition: true
            next: reject

    - deploy:
        call: http.post
        args:
          url: https://us-central1-run.googleapis.com/v2/projects/PROJECT/locations/us-central1/services/my-service:setIamPolicy
          auth:
            type: OAuth2
          body:
            policy:
              bindings:
                - role: roles/run.invoker
                  members:
                    - allUsers
        result: deploy_result

    - reject:
        return: "Deployment rejected by approver"

    - return_result:
        return: "Deployment approved and completed"
```

### Cloud Scheduler → Workflows

```bash
# Create service account for Scheduler to invoke Workflows
gcloud iam service-accounts create scheduler-workflows-sa \
  --display-name="Scheduler Workflows Invoker"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:scheduler-workflows-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/workflows.invoker"

WORKFLOW_URL="https://workflowexecutions.googleapis.com/v1/projects/PROJECT_ID/locations/us-central1/workflows/my-etl-workflow/executions"

# Schedule a workflow to run daily at midnight
gcloud scheduler jobs create http run-etl-daily \
  --location=us-central1 \
  --schedule="0 0 * * *" \
  --uri="${WORKFLOW_URL}" \
  --message-body='{"argument": "{\"date\": \"today\"}"}' \
  --oauth-service-account-email="scheduler-workflows-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --oauth-token-audience="${WORKFLOW_URL}"
```
