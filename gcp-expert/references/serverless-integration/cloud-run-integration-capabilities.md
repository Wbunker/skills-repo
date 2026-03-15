# Cloud Run & Functions — Integration Capabilities

## Pub/Sub Push Integration

Cloud Run is a natural target for Pub/Sub push subscriptions. When a message is published to a Pub/Sub topic, the subscription forwards it as an HTTP POST to the Cloud Run service URL. Authentication is enforced via OIDC tokens: the Pub/Sub service account must hold `roles/run.invoker` on the target service, and the subscription must be configured with `--push-auth-service-account`. The Cloud Run handler must return HTTP 200–299 to acknowledge the message; any other status code (or a timeout) causes Pub/Sub to redeliver with exponential backoff. Dead-letter topics capture messages that exhaust the maximum delivery attempt count.

**Key design points:**
- Pub/Sub retries indefinitely until acknowledgement or dead-letter threshold; make handlers idempotent.
- Message payload arrives base64-encoded in `message.data`; decode in handler before processing.
- Set `--ack-deadline` on the subscription to match your handler's expected processing time (max 600 s).
- Use `--min-retry-delay` and `--max-retry-delay` on the subscription to tune backoff.

## Eventarc → Cloud Run

Eventarc routes events from 90+ GCP services to Cloud Run services in CloudEvents 1.0 format over HTTP. Two transport mechanisms exist:

- **Audit Log triggers**: any GCP API call that writes a Cloud Audit Log (data access or activity) can trigger a Cloud Run service. Covers BigQuery job completion, Cloud SQL instance creation, GCS object creation via the storage API, IAM policy changes, and hundreds more.
- **Direct event triggers**: Cloud Storage, Pub/Sub, Firebase, Cloud Build, and Artifact Registry publish events directly without requiring Audit Logs.

The Eventarc trigger binds a Cloud Run service, a service account with `roles/run.invoker`, and a set of event filters (service, method, resource). Events are delivered as CloudEvents HTTP requests; the handler acknowledges by returning 2xx.

**Key design points:**
- Each trigger creates an internal Pub/Sub topic; Eventarc manages delivery and retries.
- Filter by `resourceName` prefix to scope triggers to specific GCS buckets or projects.
- Eventarc triggers can also target GKE services and Workflows, not just Cloud Run.
- Region of the trigger must match the region of the destination Cloud Run service.

## Cloud Scheduler → Cloud Run

Cloud Scheduler sends HTTP requests on a cron schedule to Cloud Run. Configure the job with an OIDC token using the invoker service account — Scheduler injects the token in the `Authorization: Bearer` header, and Cloud Run's built-in IAM authentication validates it before forwarding to the container.

**Key design points:**
- Set `--attempt-deadline` to match the maximum expected handler duration (up to 30 min for Scheduler; Cloud Run request timeout must be >= this value).
- Use `--http-method=POST` with a JSON body to pass parameters to the handler.
- Retry configuration: `--max-retry-attempts`, `--max-backoff`, `--max-doublings`.
- Scheduler jobs are regional; Cloud Run services are regional — deploy both in the same region to avoid cross-region latency.

## Cloud Tasks → Cloud Run

Cloud Tasks provides a managed task queue for asynchronous, rate-limited HTTP invocations of Cloud Run. Use Cloud Tasks when you need fan-out with flow control (max dispatches per second, max concurrent dispatches), per-task retry configuration, deduplication, and task scheduling delay.

**Key design points:**
- Create an HTTP task with the target Cloud Run URL, OIDC token (service account with `roles/run.invoker`), payload, and optional scheduling time.
- Queue-level rate limits (`--max-dispatches-per-second`, `--max-concurrent-dispatches`) prevent overloading the downstream Cloud Run service.
- Task-level retry: `--max-attempts`, `--min-backoff`, `--max-backoff`, `--max-doublings`.
- Cloud Tasks is better than Pub/Sub when you need explicit task management (list, delete, pause a queue), deduplication by task name, or delivery scheduling.

## VPC Access for Cloud Run

Cloud Run containers run in Google-managed VPC infrastructure by default and cannot reach resources on your private VPC (Cloud SQL private IP, Memorystore, on-prem via VPN/Interconnect) without explicit VPC connectivity.

**Serverless VPC Access Connector** (older approach):
- Create a `/28` subnet in your VPC; the connector bridges Cloud Run egress into that subnet.
- Connect at deploy time with `--vpc-connector=CONNECTOR_NAME`.
- `--vpc-egress=private-ranges-only` (default): only RFC 1918 traffic goes through VPC; internet traffic goes direct. Use `all-traffic` to route all egress through VPC (e.g., for egress via a NAT gateway with a stable IP).

**Direct VPC Egress** (recommended for new services):
- No connector resource to manage; Cloud Run instances get an IP directly from your subnet.
- Specify `--network`, `--subnet`, and `--vpc-egress` at deploy time.
- Supports higher throughput and lower latency than connector-based approach.
- Firewall rules apply to the Cloud Run instances using network tags or the service's identity.

## Cloud Run Jobs

Cloud Run Jobs run containers to completion — unlike services, they are not request-driven. Use jobs for batch processing, database migrations, report generation, ML training data preparation, and any workload with a defined end state.

**Key features:**
- **Parallelism**: split work across up to 10,000 task instances; each task receives `CLOUD_RUN_TASK_INDEX` (0-based) and `CLOUD_RUN_TASK_COUNT` environment variables to partition work.
- **Task timeout**: each task has an independent timeout (`--task-timeout`); the job succeeds when all tasks exit 0.
- **Retries**: failed tasks are retried up to `--max-retries` times (default 3).
- **Triggering**: manually via `gcloud run jobs execute`, via Cloud Scheduler (HTTP trigger to the jobs execute API), or via Workflows using the Cloud Run connector.
- **Resource limits**: jobs can request more CPU and memory than services (up to 32 vCPU, 128 GiB RAM per task).

## Secret Manager Integration

Cloud Run supports two modes of Secret Manager integration at deploy time:

- **Environment variables**: `--set-secrets=ENV_VAR=secret-name:version` — secret value injected at container startup; value is fixed to the version resolved at startup (use `latest` to get the newest version, which is resolved once per container instance startup).
- **Mounted volumes**: `--set-secrets=/path/to/file=secret-name:version` — secret written to a file inside the container; the file is updated when the secret version is rotated and Cloud Run restarts the instance (with `latest` alias).

The Cloud Run service's runtime service account must have `roles/secretmanager.secretAccessor` on the secret. Volume mounts support automatic rotation (the file is updated when the secret is rotated and the container is not restarted mid-request).

## Cloud SQL Integration

Cloud Run can connect to Cloud SQL via two methods:

- **Cloud SQL Auth Proxy (sidecar)**: run the proxy as a sidecar container in the same Cloud Run service (multi-container deploy); the main container connects to `127.0.0.1:5432` (or MySQL/SQLServer port); the proxy handles IAM authentication and TLS.
- **Built-in Cloud SQL socket**: specify `--add-cloudsql-instances=PROJECT:REGION:INSTANCE` at deploy time; Cloud Run provisions a Unix socket at `/cloudsql/PROJECT:REGION:INSTANCE`; connect via that socket in the database driver; no proxy process needed.

Both methods require the service account to have `roles/cloudsql.client`. Prefer Unix socket (built-in) for simplicity; use sidecar proxy when you need connection pooling (PgBouncer in sidecar) or additional proxy features.

## AlloyDB Integration

Cloud Run connects to AlloyDB via:
- **AlloyDB Auth Proxy** as a sidecar container (analogous to Cloud SQL Auth Proxy).
- **Private IP** via Direct VPC Egress or Serverless VPC Access Connector pointing to the AlloyDB cluster's VPC.

The service account needs `roles/alloydb.client`.

## Minimum Instances (Cold Start Mitigation)

Cloud Run scales to zero by default; the first request to a cold instance incurs startup latency (container pull + process init). Set `--min-instances=N` to keep N instances warm at all times. Min instances are billed even when idle (at a reduced rate compared to active instances). For latency-sensitive APIs, set min-instances=1 or higher based on traffic patterns. Use **CPU boost** (`--cpu-boost`) to temporarily allocate extra CPU during container startup, reducing init time without permanently increasing CPU allocation.

## Cloud Functions Integration Patterns

Cloud Functions (2nd gen, built on Cloud Run) participate in the same integration patterns:
- **Pub/Sub trigger**: `--trigger-topic=TOPIC` — function is invoked for each Pub/Sub message.
- **Cloud Storage trigger**: `--trigger-event=google.storage.object.finalize --trigger-resource=BUCKET` — invoked on object creation.
- **HTTP trigger**: HTTPS endpoint; same IAM authentication as Cloud Run.
- **Eventarc trigger**: 2nd gen functions support Eventarc triggers (same as Cloud Run triggers).
- **Firebase triggers**: Firestore writes, Auth events, Realtime Database changes — managed via Firebase SDK deployment.

2nd gen Cloud Functions are deployed as Cloud Run services under the hood; they share the same runtime, scaling, and VPC networking capabilities.
