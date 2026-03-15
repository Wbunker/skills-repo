# Cloud Logging — Capabilities

## Purpose

Centralized managed logging service for all GCP services, Compute Engine VMs, GKE workloads, and custom applications. Cloud Logging automatically ingests logs from all GCP services without configuration, provides a powerful query language for searching logs, and enables log export to Cloud Storage, BigQuery, or Pub/Sub for long-term retention and analysis.

---

## Core Concepts

| Concept | Description |
|---|---|
| Log entry | Single log record: resource, timestamp, severity, payload (text/JSON/proto), labels, trace |
| Log name | Identifier within a resource (e.g., `projects/my-project/logs/cloudaudit.googleapis.com%2Factivity`) |
| Monitored resource | The resource that generated the log (gce_instance, k8s_container, cloud_run_revision, etc.) |
| Log bucket | Storage container for log entries; defines retention period and region |
| Log view | Filtered view over a log bucket; controls what IAM principals can see |
| Log sink | Route that exports matching log entries to a destination (GCS, BigQuery, Pub/Sub, Log Bucket) |
| Log router | Intercepts all log entries; applies sinks and exclusions before storage |
| Log exclusion | Rule that drops matching log entries before storage (reduce cost, noise) |
| Log-based metric | Counter or distribution metric derived from log entries matching a filter |
| Log Analytics | Query log buckets using BigQuery SQL (without exporting) |
| Audit log | Special logs recording API calls and admin actions on GCP resources |
| _Required bucket | System-managed bucket; stores Admin Activity and System Event audit logs; 400-day retention; immutable |
| _Default bucket | System-managed bucket; stores all other logs; 30-day default retention; configurable |

---

## Log Storage Architecture

```
Application/GCP Service
        ↓
   Log Router
   ├── Sinks (export matching logs to GCS, BigQuery, Pub/Sub, Log Bucket)
   ├── Exclusions (drop matching logs; save cost)
   └── Default: all logs → _Default log bucket
        ↓
   Log Buckets (storage + retention)
   ├── _Required (Admin Activity, System Event) — 400 days, immutable
   ├── _Default (everything else) — 30 days default, configurable
   └── Custom buckets (user-defined retention, region, CMEK)
```

---

## Log Buckets

### _Required Bucket
- Stores: Admin Activity audit logs, System Event audit logs
- Retention: 400 days, **cannot be reduced or overridden**
- Immutable: cannot be deleted, cannot be modified
- Region: global (logs stored where project is)

### _Default Bucket
- Stores: Data Access audit logs, VPC Flow logs, and all other logs not matched by other sinks
- Default retention: 30 days
- Configurable: 1 day to 3650 days
- Can add log exclusions at the sink level

### Custom Log Buckets
- User-defined name, region, retention period (1–3650 days)
- Support Log Analytics (enable BigQuery-linked dataset)
- Support CMEK (Customer-Managed Encryption Keys)
- Support Log Views for fine-grained IAM access

### Log Views
- Filter subset of logs within a bucket accessible to specific users
- IAM binding on the log view grants access to only matching entries
- Use for multi-tenant scenarios (team A sees only their service's logs)

---

## Log Sinks

Route logs to external destinations for archival, analysis, or streaming:

| Destination | Use Case |
|---|---|
| **Cloud Storage** | Long-term archival; compliance; audit log backup |
| **BigQuery** | SQL analysis of logs; join with business data |
| **Pub/Sub** | Stream to SIEM tools (Splunk, Datadog); custom processing via Dataflow |
| **Log Bucket** | Route to another project's log bucket; centralized logging |

**Sink filter**: logs matching the filter are exported; use Logging query language
**Sink writer identity**: service account that writes to destination; must have appropriate IAM role on destination
**Aggregated sinks**: export logs from all projects in an organization/folder to a single destination

---

## Cloud Audit Logs

Four types of audit logs:

| Type | Description | Default State |
|---|---|---|
| **Admin Activity** | API calls that modify resource configuration (create, update, delete) | Always enabled, cannot disable |
| **Data Access** | API calls that read/access data or resource metadata | Disabled by default (enable per service) |
| **System Event** | GCP system-generated admin actions (auto-scale, maintenance) | Always enabled, cannot disable |
| **Policy Denied** | Authorization denied by VPC Service Controls | Always enabled for VPC-SC violations |

**Enabling Data Access logs:**
```bash
gcloud projects get-iam-policy my-project | grep auditConfigs
# Enable via gcloud or Terraform
```

**Important**: Data Access logs can generate very high volumes (especially BigQuery, Cloud Storage). Enable selectively and filter aggressively to manage costs.

---

## Log Analytics

- Query log buckets using BigQuery SQL without exporting
- Enable on a log bucket to create a linked BigQuery dataset
- Use Cloud Console Log Analytics tab or direct BigQuery queries
- Useful for ad-hoc log analysis, security investigations, compliance queries

```sql
-- Example: find top 10 most frequent error messages
SELECT
  jsonPayload.message,
  COUNT(*) as error_count
FROM `my-project.global._Default._AllLogs`
WHERE severity = 'ERROR'
  AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
GROUP BY 1
ORDER BY 2 DESC
LIMIT 10;

-- Find all authentication failures
SELECT
  timestamp,
  resource.labels.instance_id,
  jsonPayload.message
FROM `my-project.global._Default._AllLogs`
WHERE logName LIKE '%/logs/auth'
  AND textPayload LIKE '%authentication failure%'
ORDER BY timestamp DESC;
```

---

## Error Reporting

- Automatically groups and aggregates errors from Cloud Logging
- Parses stack traces from multiple languages: Go, Java, Python, Ruby, PHP, Node.js, .NET
- Alerts when new error groups appear or error count spikes
- Error groups can be linked to Cloud Trace spans
- Resolution workflow: mark errors as resolved/acknowledged; reopen if they recur
- API: query error groups and events programmatically

**Error formats recognized automatically:**
- Exception stack traces in Cloud Run, App Engine, Cloud Functions logs
- Custom errors using Error Reporting API
- GKE pod crash logs

---

## Logging Query Language

Used for filtering in Log Explorer, sinks, exclusions, metrics, and alerts:

```
# Basic field comparisons
severity=ERROR
severity>=WARNING

# Resource type filter
resource.type="gce_instance"
resource.type="k8s_container"
resource.type="cloud_run_revision"

# Label filters
resource.labels.project_id="my-project"
resource.labels.cluster_name="my-cluster"
resource.labels.namespace_name="production"

# Log name filter
logName="projects/my-project/logs/run.googleapis.com%2Frequests"
logName=~"cloudaudit.googleapis.com"

# Text search in any field
textPayload:"NullPointerException"
textPayload:"OOM"

# JSON payload field filter
jsonPayload.httpRequest.status>=500
jsonPayload.message:"connection refused"
jsonPayload.userId="user-123"

# Timestamp filter
timestamp >= "2024-01-01T00:00:00Z"
timestamp >= timestamp_sub(now(), duration("1h"))

# HTTP request filters (for load balancer / web server logs)
httpRequest.status=500
httpRequest.requestUrl:"/api/v1/orders"
httpRequest.latency>1s

# Trace filter
trace="projects/my-project/traces/TRACE_ID"

# Combining filters (AND, OR, NOT)
resource.type="k8s_container" AND severity>=ERROR
(severity=ERROR OR severity=CRITICAL) AND resource.labels.cluster_name="prod-cluster"
NOT logName:"cloudaudit.googleapis.com"

# Prefix/substring matching
jsonPayload.message=~"timeout"  # regex match

# Exclude healthcheck noise
resource.type="k8s_container"
-httpRequest.requestUrl="/health"
-httpRequest.requestUrl="/readyz"
```

---

## Monitoring Integration

- **Log-based metrics**: count log entries matching a filter; create alerting policies on these metrics
- **Alerting on log patterns**: e.g., alert when error log count > 10 in 5 minutes
- **Uptime check failure logging**: uptime check failures logged automatically
- **Cloud Trace correlation**: log entries with `trace` field linked to trace spans in Cloud Trace

---

## Retention and Cost Management

- **Log exclusions**: drop high-volume, low-value logs before ingestion to reduce cost
  - Common exclusions: health check logs, GCS access logs for cold storage buckets, verbose debug logs
- **Bucket retention**: set to minimum required for compliance; long-term archival use GCS sinks
- **Log-based metric with exclusion**: export to BigQuery for analysis while excluding from Cloud Logging to reduce ingestion cost
- **Aggregated sinks**: reduce duplication when logs are already captured at org level

| Log Type | Approximate Cost Driver |
|---|---|
| System logs (small VMs) | Low volume |
| Cloud SQL Data Access | Can be very high; enable selectively |
| BigQuery Data Access | Can be very high; enable selectively |
| GCS Data Access | High for bucket with millions of objects |
| VPC Flow Logs | High volume; filter by sampled flows |
