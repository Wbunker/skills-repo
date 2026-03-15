# Cloud Functions — Capabilities Reference

CLI reference: [cloud-functions-cli.md](cloud-functions-cli.md)

## Purpose

Event-driven serverless compute for lightweight functions. Write and deploy individual functions without managing servers or containers. Cloud Functions handles scaling, patching, and availability. Ideal for glue code, webhooks, event processing, and lightweight APIs that don't warrant a full containerized service.

---

## 1st Gen vs 2nd Gen

| Attribute | 1st Generation | 2nd Generation |
|---|---|---|
| Underlying infrastructure | Proprietary GCP runtime | Cloud Run (fully Knative-based) |
| Max timeout | 9 minutes | 60 minutes |
| Max memory | 8 GB | 32 GB |
| Max vCPUs | 4 vCPUs | 8 vCPUs |
| Concurrency | 1 request per instance | Up to 1000 concurrent requests |
| Trigger types | HTTP, Pub/Sub, Cloud Storage, Firestore, Firebase | All 1st gen triggers + 90+ via Eventarc |
| Minimum instances | Not supported | Supported (warm instances) |
| VPC connector | Supported | Supported + direct VPC egress |
| Execution environment | Sandboxed | Full gen2 Cloud Run execution environment |
| Traffic splitting | Not supported | Supported (via Cloud Run revisions) |
| Health probes | Not supported | Startup + liveness probes |
| CMEK | Supported | Supported |
| Recommendation | Existing workloads | New workloads |

**Note**: Cloud Functions 2nd gen is built on Cloud Run. You can also view, manage, and configure 2nd gen functions through the Cloud Run console. The `gcloud functions` CLI is the primary interface but `gcloud run` also works for 2nd gen.

---

## Trigger Types

| Trigger | Gen | Description |
|---|---|---|
| HTTP | Both | Function invoked via HTTPS request. Returns HTTP response. Can be public or require auth. |
| Pub/Sub | Both | Triggered when a message is published to a specified topic. Message delivered as base64-encoded data in the event payload. |
| Cloud Storage | Both | Triggered on object finalize (create/overwrite), delete, archive, or metadata update events in a bucket. |
| Firestore | 1st gen | Triggered on Firestore document create, update, delete, or write events. |
| Firebase Realtime DB | 1st gen | Triggered on Firebase RTDB events. |
| Firebase Auth | 1st gen | Triggered on user create or delete. |
| Firebase Remote Config | 1st gen | Triggered on config update. |
| Eventarc (Cloud Audit Logs) | 2nd gen | Triggered by Cloud Audit Log events from any GCP service (e.g., BigQuery job complete, GCS object change). |
| Eventarc (direct) | 2nd gen | Direct Eventarc triggers for supported event types (Pub/Sub, Cloud Storage, etc.) in CloudEvents format. |

---

## Core Concepts

| Concept | Description |
|---|---|
| Function | A single-purpose piece of code with a named entry point. Stateless. |
| Entry point | The exported function name in source code that Cloud Functions calls (e.g., `helloWorld` in Node.js, `hello_world` in Python). |
| Runtime | Execution environment for the function code. Determines language, version, and available libraries. |
| Trigger | Event source that causes the function to execute. |
| Environment variables | Key-value pairs accessible in the function at runtime. Set at deploy time. |
| Service account | IAM identity the function uses to authenticate GCP API calls. Defaults to the App Engine default service account for 1st gen, Compute default SA for 2nd gen. |
| VPC connector | Allows functions to access private VPC resources (Cloud SQL private IP, internal services). |
| Secrets | Inject Secret Manager secrets as environment variables or mounted files using `--set-secrets`. |
| Source code | Deployed as a ZIP in Cloud Storage, from a source directory, or from a Cloud Source Repository. |

---

## Supported Runtimes

| Language | Versions Available |
|---|---|
| Node.js | 14, 16, 18, 20, 22 |
| Python | 3.8, 3.9, 3.10, 3.11, 3.12 |
| Go | 1.19, 1.20, 1.21, 1.22 |
| Java | 11, 17, 21 |
| .NET | .NET 6, .NET 8 |
| Ruby | 3.0, 3.2 |
| PHP | 8.1, 8.2 |

Each runtime supports a `requirements.txt` / `package.json` / `go.mod` / `pom.xml` / etc. for dependency management.

---

## Concurrency

### 1st Gen
- **Strictly 1 request per instance**: each concurrent request requires a separate instance.
- Simple concurrency model but requires more instances for high-traffic scenarios.
- Instance startup (cold start) on every new concurrent request.

### 2nd Gen
- **Up to 1000 concurrent requests per instance**.
- Concurrency is configurable; default is 1 (can be changed to match workload).
- Reduces instance count and cold starts for I/O-bound functions.
- Must ensure function code is thread-safe when concurrency > 1.

---

## Pricing

Billing components (both generations):

| Component | 1st Gen | 2nd Gen |
|---|---|---|
| Invocations | $0.40 per million (first 2M/month free) | $0.40 per million (first 2M/month free) |
| Compute time (memory) | GB-seconds ($0.0000025/GB-s; 400,000 GB-s/month free) | GB-seconds (same rates as Cloud Run) |
| Compute time (CPU) | GHz-seconds ($0.00001/GHz-s; 200,000 GHz-s/month free) | vCPU-seconds (same rates as Cloud Run) |
| Networking | Standard Cloud egress rates | Standard Cloud egress rates |

**Key pricing insight**: a function that runs for 100ms using 256 MB of memory costs roughly $0.000000648 per invocation. At 1 million invocations: ~$0.65 for compute + $0.40 for invocations.

Minimum invocation billing: 100ms (1st gen), 10ms (2nd gen).

---

## When to Use Cloud Functions vs Cloud Run

| Signal | Use Cloud Functions | Use Cloud Run |
|---|---|---|
| Code complexity | Simple, single-purpose function (<500 lines) | Complex application, multiple endpoints, dependencies |
| Container control | No container needed; just upload source code | Need specific base image, custom runtime, or Dockerfile |
| Cold start tolerance | Acceptable (or use 2nd gen with min instances) | Use min instances for latency-sensitive |
| Concurrency | Handled automatically (1st gen = 1, 2nd gen = configurable) | Full control over concurrency settings |
| Multiple HTTP routes | Single endpoint per function; multiple functions needed | Single service with full router |
| Build system | Google-managed build | Custom Dockerfile or Buildpack |
| Event processing | First-class support with simple SDK | Manual HTTP endpoint handling |
| Team familiarity | Developers want to write just functions | Team comfortable with containers |

---

## Important Patterns & Constraints

- **Stateless**: functions do not maintain in-memory state between invocations on different instances. Use Cloud Storage, Firestore, Memorystore (Redis), or Cloud SQL for persistent state.
- **Cold starts**: when a new instance is created, the runtime initializes (imports, global setup). Keep global initialization minimal. 2nd gen with `--min-instances` avoids cold starts.
- **Max execution time**: 1st gen = 540 seconds (9 minutes); 2nd gen = 3600 seconds (60 minutes). Long-running work should use Cloud Run Jobs or Cloud Batch.
- **Instance reuse**: Google may reuse instances for subsequent invocations. Initialize expensive resources (DB connections, HTTP clients) in global scope, not inside the function handler, to benefit from instance reuse.
- **Pub/Sub at-least-once delivery**: Pub/Sub triggered functions may be called more than once for the same message. Design functions to be idempotent.
- **Cloud Storage trigger timing**: Cloud Storage triggers have at-least-once delivery guarantee. Functions processing GCS objects should be idempotent.
- **Dependency size**: maximum deployment size is 100 MB compressed, 500 MB uncompressed. For large ML models or dependencies, use Cloud Run instead.
- **Timeout for HTTP functions**: HTTP functions must return a response before the timeout. Long processing should be offloaded asynchronously (Pub/Sub, Cloud Tasks).
- **IAM invoker for HTTP**: HTTP functions require the `roles/cloudfunctions.invoker` (1st gen) or `roles/run.invoker` (2nd gen) role for authentication. Grant `allUsers` for public functions.
- **Function names are immutable per region**: you cannot change a function's trigger type after creation; must delete and recreate.
- **Secrets access**: grant the function's service account `roles/secretmanager.secretAccessor` on the secret resource before using `--set-secrets`.
- **VPC connector required for private resources**: functions cannot access private VPC IPs without a Serverless VPC Access connector.
- **Pub/Sub trigger subscription**: Cloud Functions automatically creates a Pub/Sub push subscription; do not manually manage this subscription.
