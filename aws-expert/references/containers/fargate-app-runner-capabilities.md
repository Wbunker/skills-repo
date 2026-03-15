# AWS Fargate & App Runner — Capabilities Reference
For CLI commands, see [fargate-app-runner-cli.md](fargate-app-runner-cli.md).

## AWS Fargate

**Purpose**: Serverless compute engine for containers; run ECS tasks and EKS pods without provisioning or managing EC2 instances.

### Task / Pod Sizing

For ECS, each task must declare CPU and memory. Valid combinations:

| vCPU | Memory options |
|---|---|
| 0.25 vCPU | 512 MB, 1 GB, 2 GB |
| 0.5 vCPU | 1 GB – 4 GB (in 1 GB increments) |
| 1 vCPU | 2 GB – 8 GB (in 1 GB increments) |
| 2 vCPU | 4 GB – 16 GB (in 1 GB increments) |
| 4 vCPU | 8 GB – 30 GB (in 1 GB increments) |
| 8 vCPU | 16 GB – 60 GB (in 4 GB increments) |
| 16 vCPU | 32 GB – 120 GB (in 8 GB increments) |

### Key Features

| Feature | Description |
|---|---|
| **Network mode** | `awsvpc` only — each task/pod gets a dedicated ENI and VPC IP; no port conflicts between tasks |
| **Isolation** | Each task/pod runs in its own dedicated kernel (VM boundary); no shared CPU, memory, or kernel with other workloads |
| **Ephemeral storage** | Default 21 GB; configurable up to 200 GB via `ephemeralStorage` in task definition; storage is lost when task stops |
| **Platform versions (ECS)** | Versioned combination of kernel + container runtime; tasks automatically use latest patched revision; older insecure revisions are retired |
| **Supported OS** | Amazon Linux 2, Bottlerocket; Windows Server 2019 Full and Core (ECS only) |
| **Fargate Spot** | Run tasks on spare AWS capacity at up to 70% discount; tasks receive 2-minute interruption notice before termination; suitable for fault-tolerant batch workloads |

### Fargate for EKS — Limitations

| Not Supported | Notes |
|---|---|
| DaemonSets | Must be converted to sidecar containers |
| Privileged containers | Security boundary prevents elevated privileges |
| HostPort / HostNetwork | No host networking |
| GPUs | Use EC2 GPU nodes instead |
| Windows containers | Linux only on EKS Fargate |
| Amazon EBS volumes | Use EFS for persistent storage |
| Public subnets | Fargate pods must run in private subnets |
| EKS Pod Identity | Use IRSA for pod IAM on Fargate |
| SSM / ECS Exec equivalent | Not supported; use CloudWatch Logs for debugging |

### Pricing Model

- Charged per vCPU-second and per GB-memory-second consumed by running tasks/pods
- Fargate Spot pricing is variable (based on available capacity); On-Demand pricing is fixed
- No charge for stopped tasks; ephemeral storage above 20 GB charged per GB-hour

---

## AWS App Runner

**Purpose**: Fully managed service to build and run containerized web applications and APIs from source code or container images, with zero infrastructure management.

### Key Concepts

| Concept | Description |
|---|---|
| **Service** | The core resource; runs your container or builds from source; has a URL, scaling config, and IAM roles |
| **Source type — ECR** | Pull a container image from Amazon ECR (private or public); optionally deploy automatically on new image push |
| **Source type — Source code** | Connect a GitHub (or Bitbucket) repository; App Runner builds the image using a managed runtime (Node.js, Python, Java, .NET, Go, Ruby, PHP) |
| **Configuration file** | `apprunner.yaml` in the repo root; defines build and run commands, port, environment variables, and runtime |
| **Auto-deployments** | Trigger a new deployment automatically on every commit (source code) or every new image tag (ECR) |
| **Instance role** | IAM role assumed by running application code (e.g., to call DynamoDB) |
| **Access role** | IAM role that App Runner uses to pull images from private ECR |

### Auto Scaling

| Setting | Description |
|---|---|
| **Min instances** | Always-on instances; set to 1+ for zero cold-start latency |
| **Max instances** | Upper bound on concurrent instances |
| **Concurrency** | Max concurrent requests per instance before a new instance is added (default: 100) |
| **Scale-to-zero** | Setting min instances to 0 allows full scale-down; incurs cold start on next request |

### Networking

| Feature | Description |
|---|---|
| **Inbound (public)** | Default: public HTTPS endpoint provided by App Runner |
| **Inbound (private)** | VPC Ingress Connection: restrict traffic to come from within a specific VPC (via PrivateLink) |
| **Outbound (VPC Connector)** | Connect App Runner service to resources inside a VPC (RDS, ElastiCache, internal services); attach a VPC connector with subnets and security groups |
| **Custom domain** | Associate your own domain via `associate-custom-domain`; App Runner provides certificate validation records; auto-renews TLS certificate |

### Observability

| Feature | Description |
|---|---|
| **Metrics** | Application and service metrics to CloudWatch (request count, latency, HTTP 2xx/4xx/5xx, active instances) |
| **Logs** | Application logs and system event logs streamed to CloudWatch Logs |
| **X-Ray tracing** | Enable AWS X-Ray in service configuration for distributed tracing; no code changes required |

### Configuration File (`apprunner.yaml`)

```yaml
version: 1.0
runtime: python311
build:
  commands:
    build:
      - pip install -r requirements.txt
run:
  command: python app.py
  network:
    port: 8080
  env:
    - name: ENV
      value: production
```
