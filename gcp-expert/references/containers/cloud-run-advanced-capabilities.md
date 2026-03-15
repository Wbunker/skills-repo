# Cloud Run Advanced — Capabilities

## Multi-Region Architecture

Cloud Run is a regional service — each Cloud Run service is deployed to a single GCP region. There is no built-in multi-region failover or global routing at the Cloud Run level. To serve traffic globally and handle regional failover, front multiple regional Cloud Run services with a **Global External Application Load Balancer** using Cloud Run NEG (Network Endpoint Group) backends.

**Architecture**:
1. Deploy the same Cloud Run service image to multiple regions (e.g., `us-central1`, `europe-west1`, `asia-east1`).
2. Create a Serverless NEG for each regional Cloud Run service.
3. Create a backend service in the Global Load Balancer with all three NEGs as backends.
4. Configure a URL map and HTTPS target proxy.
5. Create a global static external IP and forwarding rule.

**Traffic routing behavior**:
- Google's anycast routing sends users to the nearest region's Point of Presence.
- The load balancer directs requests to the closest healthy backend.
- If a regional backend becomes unhealthy (all Cloud Run instances down or returning errors), the LB routes to the next-closest healthy backend.
- Custom health checks on the backend service define what "healthy" means.

**Cost consideration**: you pay for the global load balancer forwarding rules and traffic processing in addition to Cloud Run invocations.

---

## Traffic Splitting and Revision Management

Cloud Run maintains a revision history. Each deployment creates a new immutable revision. Traffic is distributed across revisions by percentage.

### Canary Deployments
Deploy a new revision but send only a small percentage of traffic to it. Monitor error rates and latency. Gradually shift traffic to the new revision.

### Blue-Green Deployments
Deploy a new revision (green) with 0% traffic. Test via the revision-specific URL (tag-based routing). Switch 100% of traffic from old revision (blue) to new. Keep the old revision for quick rollback.

### Tag-Based Routing
Assign a named tag to a revision at deploy time. Each tagged revision gets a unique URL:
`https://TAG---SERVICE-HASH-REGION.a.run.app`

This URL is always accessible regardless of traffic allocation, enabling:
- Testing a new revision in production environment without affecting live traffic.
- Sharing a preview URL with QA or stakeholders.
- Running integration tests against a specific revision.

### Rollback
Shift 100% traffic back to a previous revision via `gcloud run services update-traffic`. No redeployment needed.

---

## Custom Domains

Two approaches to custom domains on Cloud Run:

### Domain Mappings (Simple, for single-region)
`gcloud run domain-mappings create` maps a verified domain to a Cloud Run service. Limitations:
- One domain mapping per service per region.
- Cannot map apex domains (example.com) — only subdomains (api.example.com) or `www`.
- TLS certificate is automatically provisioned via Google-managed certificates.
- Does not support custom SSL certificates.

### Cloud Load Balancing (Recommended for production)
Use the Global External Application Load Balancer (or Regional External) with a Cloud Run NEG backend. Benefits:
- Global anycast IP.
- Custom SSL certificate (managed or self-provided).
- Cloud CDN integration.
- Cloud Armor (WAF) integration.
- Multiple backends (multi-region, or mix of Cloud Run + other backends).
- Apex domain support.

This approach requires more setup (NEG, backend service, URL map, forwarding rule) but provides enterprise-grade features.

---

## GPU Support

Cloud Run supports NVIDIA L4 GPUs for AI inference workloads. This enables running ML model serving (TensorFlow Serving, TorchServe, Ollama, vLLM) as serverless Cloud Run services.

**Key characteristics**:
- Requires **Second Generation execution environment** (`--execution-environment=gen2`).
- Requires `--no-cpu-throttling` (CPU must be always allocated when GPU is present).
- Container must include CUDA libraries compatible with the L4 GPU.
- Startup time for GPU containers is longer — use `--min-instances=1` to keep a warm GPU instance for low-latency inference.
- Scale to zero works but incurs GPU initialization time (~30-60 seconds).
- Available GPU types: `nvidia-l4` (1 or 4 GPUs per instance).
- GPU-enabled instances have high per-second billing — set `--max-instances` carefully.

**Use cases**: LLM inference (Ollama, llama.cpp), image generation (Stable Diffusion), embedding generation, speech-to-text, real-time ML inference APIs.

---

## Sidecar Containers (Multi-Container)

Cloud Run supports deploying multiple containers per service instance. One container is the "ingress" container (receives external traffic); additional containers are "sidecar" containers (accessible only to the ingress container via localhost).

**Common sidecar patterns**:

**Cloud SQL Auth Proxy sidecar**:
- Main container connects to `127.0.0.1:5432`.
- Sidecar runs `cloud-sql-proxy PROJECT:REGION:INSTANCE --port=5432`.
- The proxy handles IAM auth and TLS to Cloud SQL.
- Service account needs `roles/cloudsql.client`.

**Envoy/GRPC proxy sidecar**:
- Run a protocol transcoding proxy (Envoy with gRPC-JSON transcoding) alongside a gRPC server.
- External HTTP/JSON requests hit the Envoy sidecar; translated to gRPC for the main container.

**Log shipping sidecar**:
- Main container writes structured logs to a shared volume.
- Sidecar runs a log forwarder (Fluentd, Fluent Bit, OpenTelemetry Collector) that ships logs to external systems (Datadog, Splunk, New Relic).

**Nginx caching proxy**:
- Sidecar runs Nginx as a reverse proxy with local caching.
- Reduces calls to downstream services for frequently requested data.

**Configuration**:
Multi-container deployments require a YAML service spec (not fully supported via gcloud flags alone). Use `gcloud run services replace service.yaml`.

---

## Health Checks

Cloud Run supports two probe types:

### Startup Probe
Determines when the container is ready to serve traffic after startup. Cloud Run waits for the startup probe to succeed before sending requests. If the probe fails beyond the configured threshold, Cloud Run terminates the container and tries again (restarts).

**Configuration**:
- `httpGet`: make an HTTP GET request to a path.
- `tcpSocket`: attempt to open a TCP connection to a port.
- `exec`: run a command inside the container.
- `initialDelaySeconds`, `periodSeconds`, `failureThreshold`, `timeoutSeconds`.

**Use case**: slow-starting applications (JVM startup, model loading, database connection pool initialization). Without a startup probe, Cloud Run may send traffic before the app is ready, causing errors.

### Liveness Probe
Periodically checks if the container is still healthy while running. If the probe fails, Cloud Run restarts the container.

**Use case**: detect and recover from deadlocks, corrupted state, or memory leaks that don't crash the process but make it unresponsive.

**Important**: Cloud Run does not support readiness probes (used in Kubernetes to temporarily remove an instance from the load balancer without restarting it). If your app needs temporary not-ready state, you must handle it in the application (return 503 during startup; Cloud Run retries or routes to other instances).

---

## Execution Environments

### First Generation
- Sandbox-based; shares kernel with other tenants.
- Slower cold starts (sandbox setup overhead).
- Background processing after response is returned may be throttled.
- No GPU support.
- Some syscalls restricted.

### Second Generation (Recommended)
- Linux VM-based; hardware virtualization isolation.
- Faster cold starts and lower overhead.
- Full syscall compatibility (runs any Linux binary).
- Background thread/process support (CPU not throttled after response).
- **Required for**: GPU workloads, gRPC streaming, WebSockets, long-running background goroutines/threads.
- Higher security isolation (VM boundary rather than sandbox).

---

## Session Affinity

Cloud Run supports session affinity (sticky sessions) to route requests from the same client to the same container instance. Enable with `--session-affinity` flag. Uses a cookie-based mechanism. Useful for stateful protocols or applications that cache user-specific data in memory. Note: Cloud Run can still create new instances for scale-out; session affinity is best-effort.

---

## CPU Allocation Modes

### CPU Throttling (Default)
- CPU allocated only when a request is being processed.
- CPU is throttled (near zero) when the instance is idle between requests.
- Background threads or goroutines cannot do work between requests.
- Lower cost for infrequent traffic.

### CPU Always Allocated
- CPU allocated continuously, even between requests.
- Background jobs, scheduled tasks, async processing can run.
- Required for: message queue polling loops, background cache warming, streaming pipelines.
- Billed by wall-clock time (more expensive for idle services).
- Must use `--no-cpu-throttling` flag.
- Always-allocated services should use `--min-instances=1` (otherwise, with scale to zero, there is no running instance to do background work).

---

## Cloud Run Integrations (Direct Integrations)

Cloud Run provides managed integrations that automate connection setup for common services:

- **Cloud SQL**: automatically configures Cloud SQL Auth Proxy or Unix socket connection; grants IAM permissions; injects connection string as env var.
- **Cloud Storage**: creates a GCS bucket; grants appropriate IAM role to the service account; injects bucket name as env var.
- **Redis (Memorystore)**: provisions a Memorystore for Redis instance; configures VPC connector; injects Redis URL as env var.
- **Firebase Hosting**: serves static frontend from Firebase Hosting with Cloud Run as the dynamic backend; configures Hosting rewrites.

Access via `gcloud run integrations create/list/describe/delete`.

---

## Request and Response Limits

- **Request timeout**: up to 3600 seconds (60 minutes) for Cloud Run services; set with `--timeout`.
- **Request body size**: up to 32 MB for incoming requests.
- **Response body size**: up to 32 MB.
- **Concurrent requests per instance**: up to 1000 (`--concurrency`); default 80. Set to 1 for CPU-bound, single-threaded apps.
- **Max instances**: up to 1000 per service (soft limit; request increase via quota).
- **Memory**: up to 32 GiB per container (with matching CPU: 8 vCPU minimum for 32 GiB).
- **CPU**: up to 8 vCPU per container (gen2).
