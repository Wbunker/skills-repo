# Cloud Logging — CLI Reference

---

## Reading Logs

```bash
# Read recent logs for a project
gcloud logging read "resource.type=gce_instance" \
  --project=my-project \
  --limit=50

# Read ERROR and above logs from the last hour
gcloud logging read "severity>=ERROR" \
  --project=my-project \
  --freshness=1h \
  --limit=100

# Read logs from a specific GKE container
gcloud logging read \
  'resource.type="k8s_container"
   resource.labels.cluster_name="my-cluster"
   resource.labels.namespace_name="production"
   resource.labels.container_name="my-app"
   severity>=ERROR' \
  --project=my-project \
  --freshness=24h \
  --limit=200

# Read logs with JSON payload field filter
gcloud logging read \
  'resource.type="cloud_run_revision"
   jsonPayload.message:"database connection"
   severity>=WARNING' \
  --project=my-project \
  --freshness=6h

# Read audit logs for a specific user
gcloud logging read \
  'logName:"cloudaudit.googleapis.com%2Factivity"
   protoPayload.authenticationInfo.principalEmail="admin@example.com"' \
  --project=my-project \
  --freshness=7d \
  --limit=50

# Read HTTP request logs with 5xx errors
gcloud logging read \
  'resource.type="cloud_run_revision"
   httpRequest.status>=500' \
  --project=my-project \
  --freshness=1h

# Read logs and format as JSON
gcloud logging read "severity>=ERROR" \
  --project=my-project \
  --freshness=1h \
  --format=json \
  | jq '.[] | {timestamp: .timestamp, message: .textPayload, severity: .severity}'

# Tail logs in real-time (streaming)
gcloud logging tail "resource.type=k8s_container" \
  --project=my-project

# Tail logs with filter
gcloud logging tail \
  'resource.type="cloud_run_revision" severity>=WARNING' \
  --project=my-project

# Write a single log entry (for testing)
gcloud logging write my-test-log \
  "This is a test log entry" \
  --severity=INFO \
  --project=my-project

# Write a structured (JSON) log entry
gcloud logging write my-test-log \
  '{"message": "User login", "user_id": 123, "action": "login"}' \
  --payload-type=json \
  --severity=INFO \
  --project=my-project

# Delete log entries matching a filter (use carefully!)
gcloud logging logs delete my-custom-log-name \
  --project=my-project
```

---

## Log Sinks

```bash
# Create a sink to export logs to BigQuery
gcloud logging sinks create errors-to-bigquery \
  bigquery.googleapis.com/projects/my-project/datasets/log_analysis \
  --log-filter='severity>=ERROR' \
  --project=my-project

# Create a sink to export all logs to Cloud Storage
gcloud logging sinks create all-logs-to-gcs \
  storage.googleapis.com/my-log-archive-bucket \
  --log-filter='' \
  --project=my-project

# Create a sink to stream logs to Pub/Sub (for SIEM/Splunk)
gcloud logging sinks create security-logs-to-pubsub \
  pubsub.googleapis.com/projects/my-project/topics/security-logs \
  --log-filter='logName:"cloudaudit.googleapis.com"' \
  --project=my-project

# Create a sink to route to another project's log bucket
gcloud logging sinks create to-central-logging \
  logging.googleapis.com/projects/central-logging-project/locations/global/buckets/all-org-logs \
  --log-filter='severity>=WARNING' \
  --project=my-project

# Create an aggregated sink at the organization level (all projects)
gcloud logging sinks create org-audit-sink \
  bigquery.googleapis.com/projects/security-project/datasets/org_audit_logs \
  --log-filter='logName:"cloudaudit.googleapis.com"' \
  --include-children \
  --organization=123456789

# Create an aggregated sink at the folder level
gcloud logging sinks create folder-error-sink \
  storage.googleapis.com/org-error-logs-bucket \
  --log-filter='severity>=ERROR' \
  --include-children \
  --folder=987654321

# List sinks in a project
gcloud logging sinks list --project=my-project

# Describe a sink (shows writer identity)
gcloud logging sinks describe errors-to-bigquery --project=my-project

# Grant permissions to the sink's writer identity
# (After creating a sink, gcloud shows the writer identity; grant it the necessary role)
SINK_SA=$(gcloud logging sinks describe errors-to-bigquery \
  --project=my-project \
  --format="value(writerIdentity)")

gcloud projects add-iam-policy-binding my-project \
  --member="${SINK_SA}" \
  --role="roles/bigquery.dataEditor"

# For GCS sink:
gcloud storage buckets add-iam-policy-binding gs://my-log-archive-bucket \
  --member="${SINK_SA}" \
  --role="roles/storage.objectCreator"

# For Pub/Sub sink:
gcloud pubsub topics add-iam-policy-binding security-logs \
  --member="${SINK_SA}" \
  --role="roles/pubsub.publisher" \
  --project=my-project

# Update a sink filter
gcloud logging sinks update errors-to-bigquery \
  --log-filter='severity>=WARNING' \
  --project=my-project

# Update sink destination
gcloud logging sinks update errors-to-bigquery \
  bigquery.googleapis.com/projects/my-project/datasets/new_log_dataset \
  --project=my-project

# Delete a sink
gcloud logging sinks delete errors-to-bigquery --project=my-project
```

---

## Log Buckets

```bash
# Create a custom log bucket in a specific region
gcloud logging buckets create my-custom-logs \
  --location=us-central1 \
  --retention-days=365 \
  --description="Custom log bucket with 1-year retention" \
  --project=my-project

# Create a log bucket with CMEK
gcloud logging buckets create encrypted-logs \
  --location=us-central1 \
  --retention-days=90 \
  --cmek-kms-key-name=projects/my-project/locations/us-central1/keyRings/my-ring/cryptoKeys/my-key \
  --project=my-project

# Enable Log Analytics on a bucket (creates linked BigQuery dataset)
gcloud logging buckets update my-custom-logs \
  --location=us-central1 \
  --enable-analytics \
  --project=my-project

# List log buckets
gcloud logging buckets list \
  --location=us-central1 \
  --project=my-project

# List buckets across all locations
gcloud logging buckets list \
  --location=global \
  --project=my-project

# Describe a log bucket
gcloud logging buckets describe my-custom-logs \
  --location=us-central1 \
  --project=my-project

# Update bucket retention
gcloud logging buckets update my-custom-logs \
  --location=us-central1 \
  --retention-days=180 \
  --project=my-project

# Delete a custom log bucket
gcloud logging buckets delete my-custom-logs \
  --location=us-central1 \
  --project=my-project
```

---

## Log Views

```bash
# Create a log view (filtered access to a bucket)
gcloud logging views create my-service-view \
  --bucket=my-custom-logs \
  --location=us-central1 \
  --log-filter='resource.labels.service_name="my-service"' \
  --description="Access for my-service team" \
  --project=my-project

# List views in a bucket
gcloud logging views list \
  --bucket=my-custom-logs \
  --location=us-central1 \
  --project=my-project

# Describe a view
gcloud logging views describe my-service-view \
  --bucket=my-custom-logs \
  --location=us-central1 \
  --project=my-project

# Grant IAM access to a log view
gcloud logging views add-iam-policy-binding my-service-view \
  --bucket=my-custom-logs \
  --location=us-central1 \
  --member="group:my-service-team@example.com" \
  --role="roles/logging.viewAccessor" \
  --project=my-project

# Delete a view
gcloud logging views delete my-service-view \
  --bucket=my-custom-logs \
  --location=us-central1 \
  --project=my-project
```

---

## Log-Based Metrics

```bash
# Create a counter metric (count error log entries)
gcloud logging metrics create error-count \
  --description="Count of ERROR log entries per service" \
  --log-filter='severity=ERROR AND resource.type="cloud_run_revision"' \
  --project=my-project

# Create a counter metric with labels (useful for slicing by service)
gcloud logging metrics create errors-by-service \
  --description="ERROR count by service name" \
  --log-filter='severity>=ERROR' \
  --label-name=service \
  --label-description="Service name from resource label" \
  --label-value-type=STRING \
  --label-extractor='EXTRACT(resource.labels.service_name)' \
  --project=my-project

# Create a distribution metric (extract response latency)
cat > latency-metric.yaml << 'EOF'
name: "request-latency"
description: "Distribution of request latency in ms"
filter: 'resource.type="cloud_run_revision" httpRequest.latency!=""'
labelExtractors:
  service: "EXTRACT(resource.labels.service_name)"
valueExtractor: "EXTRACT(httpRequest.latency)"
bucketOptions:
  exponentialBuckets:
    numFiniteBuckets: 10
    growthFactor: 2.0
    scale: 1.0
EOF

gcloud logging metrics create request-latency \
  --config-from-file=latency-metric.yaml \
  --project=my-project

# List log-based metrics
gcloud logging metrics list --project=my-project

# Describe a metric
gcloud logging metrics describe error-count --project=my-project

# Update a metric filter
gcloud logging metrics update error-count \
  --log-filter='severity=ERROR AND resource.type="k8s_container"' \
  --project=my-project

# Delete a metric
gcloud logging metrics delete error-count --project=my-project
```

---

## Log Exclusions

```bash
# Create an exclusion to drop health check logs
gcloud logging exclusions create drop-healthchecks \
  --description="Drop GKE health check requests" \
  --log-filter='resource.type="k8s_container" httpRequest.requestUrl=~"/(health|readyz|livez)"' \
  --project=my-project

# Create an exclusion for a specific verbose service
gcloud logging exclusions create drop-verbose-service \
  --description="Drop DEBUG logs from noisy-service" \
  --log-filter='resource.labels.service_name="noisy-service" severity=DEBUG' \
  --project=my-project

# Create a partial exclusion (exclude 99% of matching logs — keep 1% as sample)
gcloud logging exclusions create sample-gcs-data-access \
  --description="Sample 1% of GCS Data Access logs" \
  --log-filter='logName:"logs/cloudaudit.googleapis.com%2Fdata_access" protoPayload.serviceName="storage.googleapis.com"' \
  --disabled=false \
  --project=my-project

# List exclusions
gcloud logging exclusions list --project=my-project

# Describe an exclusion
gcloud logging exclusions describe drop-healthchecks --project=my-project

# Disable an exclusion (temporarily)
gcloud logging exclusions update drop-healthchecks \
  --disabled \
  --project=my-project

# Re-enable an exclusion
gcloud logging exclusions update drop-healthchecks \
  --no-disabled \
  --project=my-project

# Delete an exclusion
gcloud logging exclusions delete drop-healthchecks --project=my-project
```

---

## Audit Log Configuration

```bash
# View current audit log configuration
gcloud projects get-iam-policy my-project \
  --format=json \
  | jq '.auditConfigs'

# Enable Data Access logs for BigQuery (all types)
cat > audit-config.yaml << 'EOF'
bindings:
- members:
  - allUsers
  role: roles/viewer
auditConfigs:
- auditLogConfigs:
  - logType: ADMIN_READ
  - logType: DATA_READ
  - logType: DATA_WRITE
  service: bigquery.googleapis.com
- auditLogConfigs:
  - logType: DATA_READ
  - logType: DATA_WRITE
  service: storage.googleapis.com
EOF

gcloud projects set-iam-policy my-project audit-config.yaml

# Check which services have Data Access logging enabled
gcloud projects get-iam-policy my-project \
  --format="value(auditConfigs[].service)"
```

---

## Useful Filter Examples for Log Explorer

```bash
# All 5xx errors from Cloud Run in last hour
gcloud logging read \
  'resource.type="cloud_run_revision"
   httpRequest.status>=500
   timestamp >= timestamp_sub(now(), duration("1h"))' \
  --project=my-project

# OOMKilled containers in GKE
gcloud logging read \
  'resource.type="k8s_node"
   jsonPayload.reason="OOMKilling"' \
  --project=my-project \
  --freshness=24h

# Cloud SQL connection errors
gcloud logging read \
  'resource.type="cloudsql_database"
   textPayload:"too many connections"' \
  --project=my-project \
  --freshness=6h

# IAM permission denied events
gcloud logging read \
  'protoPayload.status.code=7
   logName:"cloudaudit.googleapis.com%2Factivity"' \
  --project=my-project \
  --freshness=24h

# BigQuery job failures
gcloud logging read \
  'resource.type="bigquery_resource"
   protoPayload.status.code!=0
   logName:"cloudaudit.googleapis.com%2Factivity"' \
  --project=my-project \
  --freshness=24h

# Cloud Run cold starts (useful for scaling analysis)
gcloud logging read \
  'resource.type="cloud_run_revision"
   textPayload:"Starting container"' \
  --project=my-project \
  --freshness=1h
```
