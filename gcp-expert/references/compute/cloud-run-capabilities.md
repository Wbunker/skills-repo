# Cloud Run — Capabilities Reference

CLI reference: [cloud-run-cli.md](cloud-run-cli.md)

## Purpose

Fully managed serverless container platform that runs stateless containers on demand. Cloud Run abstracts all infrastructure management—you provide a container image and Cloud Run handles provisioning, scaling (including scale to zero), and HTTPS endpoint management. Billed only for actual request processing time (or continuously if CPU is always allocated).

---

## Core Concepts

| Concept | Description |
|---|---|
| Service | A long-running HTTP endpoint backed by one or more revisions. Automatically scales based on incoming requests. Provides a stable HTTPS URL. |
| Revision | An immutable snapshot of a Cloud Run service configuration (container image + environment + scaling settings). Each deploy creates a new revision. |
| Container image | The OCI/Docker container image hosted in Artifact Registry or Container Registry that Cloud Run executes. Must listen on a configurable port (default: 8080). |
| Concurrency | Number of simultaneous requests a single container instance can handle (default: 80, max: 1000). Higher concurrency = fewer instances needed. |
| Min instances | Minimum number of container instances kept warm (never scaled to zero). Reduces cold start latency; incurs idle cost. |
| Max instances | Maximum number of container instances Cloud Run will scale to. Prevents runaway costs and protects downstream dependencies. |
| Cloud Run Jobs | Run containers to completion (batch-style) rather than serving HTTP requests. Used for scheduled or triggered batch processing. |
| Traffic splitting | Route a percentage of traffic to different revisions. Used for canary deployments, A/B testing, and gradual rollouts. |
| HTTPS endpoint | Automatically provisioned, Google-managed HTTPS URL: `https://SERVICE_NAME-HASH-REGION.a.run.app`. TLS certificate managed automatically. |
| VPC connector | Enables Cloud Run to access resources in a VPC network (private Cloud SQL, internal services). Uses Serverless VPC Access. |
| Service account | IAM identity the container runs as. Used to authenticate calls to other GCP services. Defaults to the default Compute service account if unset. |
| Execution environment | First generation (default, faster cold starts) or second generation (full Linux compatibility, more CPU/memory, can run side-car-style binaries). |

---

## Cloud Run Services vs Cloud Run Jobs

| Attribute | Cloud Run Services | Cloud Run Jobs |
|---|---|---|
| Trigger | HTTP request or Pub/Sub push | Manual, Cloud Scheduler, Eventarc, Workflows |
| Execution model | Long-running, request-driven | Run-to-completion; terminates when done |
| Scaling | Scales with request load, including to zero | One task per index; parallel tasks per execution |
| Timeout | Max 60 minutes per request | Max 24 hours per task |
| Retry behavior | Client-side (no built-in retry) | Built-in task retry count |
| Billing | Per request + CPU/memory time | CPU/memory time during execution |
| Use case | APIs, webhooks, web apps, microservices | ETL, data processing, ML training jobs, DB migrations |

---

## Key Features

### Automatic HTTPS
Every Cloud Run service gets a `*.run.app` URL with a Google-managed TLS certificate. No certificate provisioning, renewal, or load balancer configuration required.

### Traffic Splitting
Route traffic across multiple revisions:
- 100% to latest revision (default)
- Percentage split (e.g., 90/10 for canary)
- Tag-based routing: named revisions accessible via `https://TAG---SERVICE.run.app` (no traffic allocation needed)

### Scale to Zero
When no requests are incoming, Cloud Run scales to zero instances. The next request triggers a cold start (typically 0.5-5 seconds depending on image size and startup). Use `--min-instances=1` to prevent cold starts for latency-sensitive workloads.

### CPU Allocation Modes
- **CPU allocated during request processing only** (default): CPU is throttled between requests. Most cost-efficient.
- **CPU always allocated**: CPU available throughout container lifetime (even between requests). Required for background threads, Pub/Sub processing, cron jobs. Billed per second continuously.

### VPC Egress
Options for outbound network access:
- **All traffic via VPC connector**: all egress routes through VPC (access private IPs and public IPs through Cloud NAT)
- **Private ranges via VPC connector**: only RFC 1918 addresses go through VPC; public traffic goes direct
- **Direct VPC egress** (newer feature): connect directly to VPC without a Serverless VPC Access connector for lower latency

### Custom Domains
Map a custom domain to a Cloud Run service via domain mappings or by pointing to a load balancer. Global HTTP(S) Load Balancer with Cloud Run backend is preferred for production (enables Cloud Armor, CDN, custom SSL cert).

### IAM-based Authentication
By default, Cloud Run services are private (require authentication). Grant `roles/run.invoker` to:
- `allUsers` for public access
- A service account for service-to-service calls
- A specific Google identity for developer access

### HTTP/2 and gRPC
Cloud Run supports HTTP/1.1, HTTP/2 (h2c and TLS), and gRPC. gRPC streaming is supported. Must configure the container port protocol.

### Startup and Liveness Probes (2nd gen execution environment)
Configure health probes to delay traffic until the container is ready (`startupProbe`) and restart unhealthy containers (`livenessProbe`). Uses the same probe definitions as Kubernetes.

---

## Concurrency Model

| Concurrency Value | Behavior |
|---|---|
| 1 | One request per instance (like Cloud Functions 1st gen). Simple, but highest instance count. |
| Default (80) | Up to 80 simultaneous requests per instance. Good for I/O-bound workloads. |
| 1000 (max) | Up to 1000 simultaneous requests per instance. Best for fast async handlers. |

**Request-based billing** (CPU allocated during request only): billed for CPU/memory while actively processing requests, rounded to the nearest 100ms.

**CPU always allocated billing**: billed continuously while at least one instance exists (min instances > 0 or during request processing).

**Recommendation**: for stateless web APIs, use high concurrency (80-1000). For CPU-intensive workloads (image processing, ML inference), use low concurrency (1-10) to avoid resource contention.

---

## Integration Patterns

### Pub/Sub Push Subscriptions
Cloud Run can receive Pub/Sub messages via push subscriptions:
1. Create a Pub/Sub push subscription pointing to the Cloud Run service URL.
2. Grant the Pub/Sub service account `roles/run.invoker` on the service.
3. Cloud Run receives POST requests with base64-encoded message data.

### Eventarc
Trigger Cloud Run services from 90+ GCP event sources (Cloud Storage, BigQuery, Firestore, Audit Logs, etc.) using CloudEvents format. Eventarc handles retry and delivery.

### Cloud Scheduler
Trigger Cloud Run services or Jobs on a cron schedule. For services: use OIDC authentication with the Cloud Run invoker role. For Jobs: use the `gcloud scheduler jobs create http` pointing to the Jobs API.

### Cloud Tasks
Queue async tasks that invoke Cloud Run services. Provides rate limiting, retry with backoff, deduplication, and task scheduling. Useful for background work, fan-out processing.

### Workflows
Orchestrate multi-step processes that call Cloud Run services as steps. Handles retries, parallel branches, and conditional logic.

### Cloud Run as Event Consumer
Use Cloud Run with `--cpu-always-allocated` and `--min-instances=1` to run a long-lived consumer process (e.g., Kafka consumer, Redis Streams reader) that processes events continuously.

---

## When to Use Cloud Run vs Cloud Functions vs GKE vs App Engine

| Scenario | Recommendation |
|---|---|
| Containerized stateless HTTP API or microservice | **Cloud Run** |
| Event-driven function with minimal boilerplate, HTTP or Pub/Sub trigger | **Cloud Functions** (2nd gen is also Cloud Run under the hood) |
| Need full Kubernetes: custom schedulers, operators, daemonsets, persistent workloads | **GKE** |
| Legacy App Engine Standard app (Python 2.7, Java 8) needing minimal migration | **App Engine** (maintain existing) |
| New general-purpose web application | **Cloud Run** (preferred over App Engine for new apps) |
| Batch processing that runs to completion | **Cloud Run Jobs** or **Cloud Batch** |
| Real-time stream processing | **Dataflow** (not Cloud Run) |
| Applications needing VM-level access or custom OS | **Compute Engine** |

---

## Important Patterns & Constraints

- **Stateless containers**: do not store state on local disk (ephemeral filesystem, up to 32 GB in-memory tmpfs). Use Cloud Storage, Firestore, Cloud SQL, or Redis for persistence.
- **Request timeout**: max 60 minutes per request (set via `--timeout` flag). Default is 5 minutes. For long-running work, use Cloud Run Jobs.
- **Container startup time**: Cloud Run waits for the container to start listening on the configured port. Long startup times increase cold start latency. Optimize image size and startup code.
- **One container per instance**: Cloud Run runs a single container per instance (unlike Kubernetes pods). Multi-container sidecars are available as a preview feature.
- **512 MiB to 32 GiB memory**: configure based on workload needs. Memory limit applies to the container instance.
- **1 to 8 vCPUs per instance**: more vCPUs do not help unless concurrency is high enough to use them.
- **Graceful shutdown**: Cloud Run sends SIGTERM 10 seconds before force-killing. Handle SIGTERM to drain in-flight requests cleanly.
- **Concurrency and thread safety**: when concurrency > 1, multiple goroutines/threads handle requests simultaneously—code must be thread-safe.
- **No inbound VPC access**: Cloud Run is not VPC-native (inbound requests come from the internet or through load balancers). Use Private Service Connect or Internal Load Balancer (ILB) for private ingress.
- **Max 1000 instances per service**: hard limit per service. For higher throughput, consider multiple services or GKE.
- **Region selection**: Cloud Run is regional; choose the same region as Cloud SQL, Firestore, and Pub/Sub for lowest latency and no egress charges.
- **Environment variables and secrets**: pass configuration via env vars; use Secret Manager integration to inject secrets as env vars or mounted files.
