# Eventarc & Workflows — Capabilities

## Eventarc

Eventarc is GCP's managed event routing service. It decouples event producers from consumers using the CloudEvents 1.0 standard, a CNCF specification for describing event data in a common way.

### Event Sources and Transport

Eventarc uses two transport mechanisms depending on the event source:

**Pub/Sub-backed direct event sources** (lower latency, ~1 second delivery):
- Cloud Storage (object created, deleted, archived, metadata updated)
- Firebase Realtime Database
- Firebase Remote Config
- Pub/Sub (topic message)
- Cloud Build (build state changes)
- Artifact Registry (image pushed, deleted)

**Cloud Audit Log events** (any GCP service with Audit Logs, ~1-10 second delivery):
- BigQuery (job completion, table creation, dataset creation)
- Cloud SQL (instance creation, deletion, backup)
- Compute Engine (instance creation, deletion, disk operations)
- Cloud Storage (via Data Access Audit Logs — separate from direct events)
- IAM (policy changes)
- Cloud Run (service deployment)
- GKE (cluster creation, node pool changes)
- Any service that emits Cloud Audit Logs (DATA_READ, DATA_WRITE, ADMIN_ACTIVITY)

### Destinations

- **Cloud Run services**: HTTP POST with CloudEvents payload; IAM-authenticated via trigger's service account (needs `roles/run.invoker`).
- **GKE services** (Autopilot and Standard): targets a GKE service via Kubernetes service name and namespace.
- **Workflows**: triggers a Workflow execution; passes the CloudEvent as the workflow input argument.
- **Cloud Functions (2nd gen)**: functions deployed with Eventarc trigger are Cloud Run services; same delivery mechanism.

### Event Filters

Triggers can specify multiple `--event-filters` to narrow which events fire the trigger:
- `type=google.cloud.storage.object.v1.finalized` — specific event type
- `serviceName=storage.googleapis.com` — all events from a service (Audit Log triggers)
- `methodName=storage.buckets.create` — specific API method
- `resourceName=projects/_/buckets/my-bucket/objects/*` — resource path prefix/suffix matching with wildcards

### Dead Letter Topics

Configure a Pub/Sub dead letter topic on the Eventarc trigger's underlying subscription to capture events that cannot be delivered after maximum retries. Monitor the dead letter topic with a Cloud Monitoring alert to detect delivery failures.

### Custom Channels

Eventarc supports custom channels for publishing your own application events (not limited to GCP services). A channel is a Pub/Sub topic wrapper with CloudEvents schema enforcement. Third-party providers (e.g., Datadog, PagerDuty) can publish to channels. This enables event-driven integration between GCP services and external systems.

### Eventarc Advanced

Eventarc Advanced (GA) adds:
- **Buses**: central event routing hubs; decouple producers from consumers; multiple pipelines can subscribe to one bus.
- **Pipelines**: consume events from a bus, apply transformations (CEL-based filtering and enrichment), and deliver to destinations.
- **Enrollments**: subscribe a bus to an event source (Pub/Sub topic, Google source).

---

## Workflows

Workflows is a fully managed serverless orchestration engine for sequencing calls to GCP APIs, HTTP endpoints, and other services. It does not require Kubernetes, Airflow, or any infrastructure management.

### Workflow Language

Workflows are defined in YAML or JSON. A workflow consists of named steps executed in sequence by default. The language supports:

- **Variables**: `assign` step to bind values to variables.
- **Conditionals**: `switch` step with condition expressions; `if/elif/else` construct.
- **Loops**: `for` step iterating over a list or range; `while` loop with condition.
- **Parallel branches**: `parallel` step executes multiple branches or iterations concurrently; `shared` variables collect results.
- **Error handling**: `try/except` with `retry` policy (fixed or exponential backoff); catch specific HTTP error codes or exception types.
- **HTTP calls**: `http.get`, `http.post`, `http.request` built-in calls to any HTTP endpoint with auth support (OAuth2 for GCP APIs, OIDC for Cloud Run).
- **Expressions**: CEL-like expressions for string manipulation, arithmetic, type casting, list/map operations.
- **Sub-workflows**: define reusable workflow fragments called with `call: my_subworkflow`; parameters passed as arguments.
- **Callbacks**: `events.create_callback_endpoint` pauses the workflow and returns a URL; an external system posts to the URL to resume execution with a result. Use for human approval gates, webhook-based async operations.
- **System variables**: `sys.get_env`, `sys.log`, `sys.sleep`, `sys.now` for utilities.

### Built-in Connectors

Workflows provides generated connectors for most GCP APIs — pre-built steps that call GCP APIs with proper auth and retry:

- `googleapis.bigquery.v2`: create dataset, run query job, wait for job completion, insert rows.
- `googleapis.storage.v1`: create bucket, insert object, list objects.
- `googleapis.cloudsql.v1`: list instances, patch instance, restart.
- `googleapis.firestore.v1`: list/get/create/patch/delete documents.
- `googleapis.pubsub.v1`: publish messages.
- `googleapis.secretmanager.v1`: access secret versions.
- `googleapis.run.v2`: run jobs, get execution status.
- `googleapis.cloudtasks.v2`: create tasks.
- `googleapis.compute.v1`: operate on VMs, disks, snapshots.

Connectors handle pagination, polling for long-running operations (LROs), and error mapping.

### Workflow Execution

- Executions can be started via: gcloud CLI, Eventarc trigger, Cloud Scheduler (HTTP call to Workflows REST API), another Workflow (via HTTP call to the Workflows API), or the GCP Console.
- Execution arguments: JSON object passed as the workflow input; accessible via `${args}` in the workflow.
- Execution results: the final step's return value is the execution result.
- Execution history: retained for 90 days; query via API or gcloud.
- Concurrent executions: unlimited (subject to quota); each is independent.

### vs Cloud Composer (Airflow)

| Criterion | Workflows | Cloud Composer |
|---|---|---|
| Use case | Event-driven, API orchestration, simpler DAGs | Complex data pipeline DAGs, existing Airflow investment |
| Setup | Serverless, deploy YAML; seconds | Composer environment: ~20 min provisioning, GKE-backed |
| Cost | Per-step billing; very low for infrequent workflows | Compute costs for Composer environment (always-on GKE) |
| Language | YAML/JSON (Workflows syntax) | Python (Airflow DAGs) |
| Operators | Built-in GCP connectors; HTTP calls | 600+ Airflow operators (GCP, AWS, Spark, Kubernetes, etc.) |
| Long-running | Callbacks, sleep; max 1 year execution | Native; Airflow tasks can run indefinitely |
| Trigger | Eventarc, Scheduler, HTTP, another Workflow | Scheduler (cron), external trigger, Airflow REST API |

**Decision**: Use Workflows for orchestrating GCP API sequences, event-driven patterns, and integrations requiring conditional logic without Airflow's complexity. Use Composer when you need Airflow operators, Spark integration, complex dependency graphs, or migrating existing Airflow DAGs.

---

## Event-Driven Architecture Patterns

### Pattern 1: Object Upload → Processing → Storage

```
Cloud Storage (upload)
  → Eventarc (storage.object.finalize trigger)
    → Cloud Run service (process file)
      → BigQuery (stream results)
```

Implementation: Eventarc trigger on GCS bucket, Cloud Run service reads object, transforms data, streams to BigQuery via the BigQuery Storage Write API.

### Pattern 2: Multi-Step Orchestration with Workflows

```
Cloud Scheduler (cron)
  → Workflows execution
    → BigQuery (run export query)
    → [wait for LRO completion]
    → Cloud Run Job (transform data)
    → [wait for job completion]
    → Pub/Sub (publish completion event)
```

Implementation: Workflows uses the BigQuery and Cloud Run connectors (which handle LRO polling automatically), then publishes a Pub/Sub message upon success.

### Pattern 3: Audit Log → Eventarc → Workflows → Approval

```
BigQuery job completion (Audit Log)
  → Eventarc (Audit Log trigger, methodName=bigquery.jobs.insert)
    → Workflows execution (receives CloudEvent)
      → HTTP call (notify Slack with callback URL)
      → [pause, wait for callback]
      → conditional: approved → BigQuery (publish results to downstream table)
                     rejected → Pub/Sub (alert ops team)
```

Implementation: Workflows `events.create_callback_endpoint` returns a URL embedded in the Slack message; operator clicks Approve/Reject which calls the URL; Workflow resumes with the result.

### Pattern 4: Fan-Out with Cloud Tasks

```
Eventarc trigger (new file in GCS)
  → Cloud Run (dispatcher service)
    → Cloud Tasks (enqueue N tasks, one per record)
      → Cloud Run (worker service, rate-limited processing)
```

Implementation: dispatcher reads the file, splits into chunks, enqueues a Cloud Task per chunk pointing to the worker Cloud Run service; Cloud Tasks enforces rate limiting and handles retries.

### Pattern 5: Cross-Service Saga (Distributed Transaction)

```
Pub/Sub (order created)
  → Workflows (saga orchestrator)
    → Cloud Run (inventory service — reserve items)
    → Cloud Run (payment service — charge card)
    → on error: Cloud Run (inventory service — release items)
              Cloud Run (payment service — refund)
```

Implementation: Workflows `try/except` with compensating actions in the `except` block; each Cloud Run service is idempotent (use order ID as idempotency key).
