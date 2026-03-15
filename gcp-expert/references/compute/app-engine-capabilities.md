# App Engine — Capabilities Reference

CLI reference: [app-engine-cli.md](app-engine-cli.md)

## Purpose

Google's fully managed application platform for running web applications and APIs. App Engine abstracts all infrastructure management—no VMs or containers to configure. Each GCP project can have one App Engine application, deployed to a region. **For new applications, Cloud Run is generally preferred**; App Engine is best maintained for existing applications.

---

## Standard vs Flexible Environments

| Attribute | Standard Environment | Flexible Environment |
|---|---|---|
| Runtime | Specific language versions (sandbox) | Any language via Docker container |
| Supported languages | Python, Java, Go, PHP, Ruby, Node.js | Any (custom Dockerfile) + managed runtimes |
| Instances | Ephemeral; start in seconds; scale to zero | Docker containers on Compute Engine VMs; min 1 instance |
| Scaling | Automatic (to zero), basic, manual | Automatic, manual (min 1 instance, no scale-to-zero) |
| Startup time | ~500ms–2s (fast cold starts) | 1-3 minutes (VM startup) |
| Request timeout | 10 minutes (HTTP), 24 hours (background tasks) | 60 minutes |
| VM access | No SSH access; sandboxed | Full SSH access to underlying VMs |
| Local disk | 5 MB local, read-only app files | Ephemeral writeable disk (size configurable) |
| Background threads | Limited (no sustained background work) | Full support for background threads |
| Network access | Limited (HTTPS outbound only) | Full VPC networking support |
| Custom OS packages | Not allowed | Supported via Dockerfile |
| Pricing | Per instance-hour (based on instance class) | Per vCPU/memory-hour (similar to GCE) |
| Best for | Low-latency web APIs, high-variable traffic, legacy App Engine apps | Long-running processes, dependencies requiring native binaries, existing Dockerfiles |

---

## Supported Runtimes

### Standard Environment
| Runtime | Available Versions |
|---|---|
| Python | 3.8, 3.9, 3.10, 3.11, 3.12 (also legacy 2.7) |
| Java | 11, 17, 21 (also legacy 8) |
| Go | 1.19, 1.20, 1.21, 1.22 |
| PHP | 8.1, 8.2 (also legacy 5.5, 7.4) |
| Ruby | 3.0, 3.2 |
| Node.js | 18, 20, 22 |

### Flexible Environment
Any language supported via a Dockerfile. Google-managed runtimes also available for Python, Java, Go, PHP, Ruby, Node.js, .NET without a full Dockerfile.

---

## Core Concepts

| Concept | Description |
|---|---|
| Application | The App Engine application in a GCP project. One per project, one region. Created once, cannot be changed. |
| Service | A logical component of an application (formerly called modules). Each service has its own code, config, and scaling. Default service is named `default`. |
| Version | A specific deployment of a service. Multiple versions can exist simultaneously. Traffic can be split across versions. |
| Instance class | Determines CPU and memory of Standard environment instances. F1 (default, shared), F2, F4, F4_1G for frontend; B1, B2, B4 for backend (manual scaling). |
| Traffic splitting | Divide incoming requests across multiple versions by IP, cookie (session stickiness), or random (uniform). |
| app.yaml | Configuration file for App Engine deployments. Specifies runtime, scaling, environment variables, handlers, and entrypoint. |
| Cron jobs | Scheduled tasks defined in `cron.yaml`. App Engine automatically sends HTTP requests to your app on the defined schedule. |
| Task queues | Legacy App Engine feature for background task processing. **Migrated to Cloud Tasks for new applications.** |
| Dispatch rules | `dispatch.yaml` routes URLs to specific services (useful for microservice-style multi-service apps). |
| Static file handlers | `app.yaml` can serve static files directly from App Engine's CDN without invoking application code. |

---

## app.yaml Structure

### Standard Environment (Python example)
```yaml
runtime: python312
service: default

instance_class: F2

automatic_scaling:
  min_idle_instances: 1
  max_idle_instances: 5
  min_pending_latency: automatic
  max_pending_latency: 30ms
  max_concurrent_requests: 80

env_variables:
  DATABASE_URL: "postgresql://user:pass@/dbname"
  ENV: "production"

handlers:
  - url: /static
    static_dir: static
    secure: always

  - url: /.*
    script: auto
    secure: always
```

### Flexible Environment (Python example)
```yaml
runtime: python
env: flex

service: backend-worker

resources:
  cpu: 2
  memory_gb: 4
  disk_size_gb: 20

manual_scaling:
  instances: 2

env_variables:
  WORKERS: "4"

beta_settings:
  cloud_sql_instances: my-project:us-central1:my-db

network:
  name: my-vpc
  subnetwork_name: my-subnet
```

---

## Scaling Options

| Type | Description | Ideal For |
|---|---|---|
| Automatic | GCP manages instance count based on request rate and latency. Scales to zero (Standard only). Default. | Variable traffic web apps, APIs |
| Basic | Creates instances as needed; shuts down after idle period. Cannot serve traffic while idle. | Scheduled background work |
| Manual | Fixed number of instances; never scales automatically. | Steady state with predictable load |

---

## Storage Integration

App Engine Standard has no persistent local disk. Use:
- **Cloud Storage**: for files, user uploads, static assets
- **Cloud Firestore / Cloud Datastore**: native GCP NoSQL, best integrated with App Engine
- **Cloud SQL**: managed PostgreSQL/MySQL via Unix socket (Standard/Flexible) or TCP (Flexible)
- **Memorystore (Redis)**: for caching (requires Serverless VPC Access for Standard)

---

## Traffic Splitting

Three splitting methods:
- **IP-based**: consistent routing per source IP. No warm-up requests needed. Not sticky across IP changes.
- **Cookie-based (GOOGAPPUID)**: consistent routing per browser session. Requires cookie support.
- **Random**: uniform distribution. Use for equal A/B testing with stateless services.

```bash
# Split 80/20 between two versions
gcloud app services set-traffic default \
  --splits=v2=0.8,v1=0.2 \
  --split-by=random
```

---

## When to Use vs Cloud Run

| Signal | App Engine | Cloud Run |
|---|---|---|
| Existing App Engine Standard app (Python 2.7, Java 8) | Maintain (migration cost not worth it) | New greenfield |
| New web application or API | Consider Cloud Run first | Preferred for new apps |
| Need exactly one service per project constraint is fine | OK | OK (no such constraint) |
| Need 5-second cold starts with no config | App Engine Standard is fast | Cloud Run also fast with min-instances |
| Task queues (Cloud Tasks replacement) | Legacy only | Cloud Tasks + Cloud Run |
| Multi-service app with dispatch routing | App Engine services + dispatch.yaml | Cloud Run multiple services + load balancer |

---

## Important Patterns & Constraints

- **One App Engine app per project**: the application region is permanent and cannot be changed. Regions are set at application creation.
- **Service names are permanent**: once a service is named, you cannot rename it. The `default` service must exist before other services.
- **Versions accumulate**: old versions remain deployed until explicitly deleted. Set up a cleanup policy or CI/CD pipeline to delete old versions.
- **Warm-up requests**: for automatic scaling, enable warmup requests (`/_ah/warmup`) to pre-initialize application state before instances serve traffic. Add the URL handler in `app.yaml`.
- **`app.yaml` is required**: deploy will fail without a valid `app.yaml` in the deployment source directory.
- **Cloud SQL connectivity**: Standard environment uses Unix socket (`/cloudsql/PROJECT:REGION:INSTANCE`); Flexible uses public IP or Unix socket.
- **Billable minimum for Flexible**: Flexible environment always runs at least 1 instance. No scale-to-zero. Standard can scale to zero.
- **Instance hours billing**: Standard billed in instance-hours by instance class. F1 is cheapest. Shared F-class instances are not guaranteed CPU.
- **Cannot run as root**: App Engine sandbox restricts system access. Standard environment has limited filesystem access.
