# AWS ECS — Capabilities Reference
For CLI commands, see [ecs-cli.md](ecs-cli.md).

## Amazon ECS

**Purpose**: Fully managed container orchestration service; deploy, manage, and scale containerized applications without managing a control plane.

### Core Architecture

ECS operates on three layers:

| Layer | Description |
|---|---|
| **Capacity** | Where containers run: EC2 instances (managed or self), Fargate (serverless), or on-premises (ECS Anywhere) |
| **Controller** | The ECS scheduler; manages deployment and scaling |
| **Provisioning** | Access tools: AWS Console, CLI, SDK, CDK |

### Key Concepts

| Concept | Description |
|---|---|
| **Cluster** | Logical grouping of infrastructure (capacity providers + services); regional resource |
| **Task Definition** | JSON blueprint describing containers, resources, networking, logging, IAM for a workload |
| **Task** | A single running instantiation of a task definition; ephemeral (batch use case) |
| **Service** | Long-running task manager; maintains desired task count, handles restarts and load balancer registration |
| **Capacity Provider** | Associates a cluster with EC2 Auto Scaling groups or Fargate; controls task placement |
| **Container Instance** | EC2 instance registered to an ECS cluster running the ECS agent |

### Task Definitions

| Parameter | Details |
|---|---|
| **Container definition** | Image URI, port mappings, environment variables, secrets (from Secrets Manager / SSM), entry point, command, working directory, links |
| **Task role** | IAM role assumed by the running task's application code (e.g., read S3) |
| **Task execution role** | IAM role used by the ECS agent to pull images from ECR and push logs to CloudWatch |
| **Network mode** | `awsvpc` (each task gets its own ENI and VPC IP — required for Fargate), `bridge` (Docker NAT — EC2 only), `host` (no NAT, uses host's network namespace — EC2 only) |
| **CPU / memory** | Task-level limits (required for Fargate); container-level soft (`memoryReservation`) and hard (`memory`) limits |
| **Volumes** | Bind mounts, Docker managed volumes, EFS volumes (persistent, shared across tasks), FSx for Windows |
| **Logging — awslogs** | Native CloudWatch Logs driver; specify log group, region, stream prefix in `logConfiguration` |
| **Logging — FireLens** | Sidecar container (Fluent Bit or Fluentd) as a log router; route logs to S3, Kinesis, Splunk, etc. |
| **Health check** | Container-level health check command + interval + timeout + retries + start period |
| **ephemeralStorage** | Fargate only; override default 21 GB ephemeral storage up to 200 GB |

### Services

| Concept | Description |
|---|---|
| **Replica scheduling** | Maintain a desired count of tasks spread across the cluster (default; stateless workloads) |
| **Daemon scheduling** | Run exactly one task per container instance (e.g., log collectors, monitoring agents; EC2 only) |
| **Capacity provider strategy** | Distribute tasks across capacity providers with `base` (minimum tasks on a provider) and `weight` (proportional split); enables Fargate + Fargate Spot mixed fleets |
| **Rolling deployment** | Replace tasks gradually; controlled by `minimumHealthyPercent` (floor) and `maximumPercent` (ceiling) as % of desired count |
| **Blue/green deployment** | Via AWS CodeDeploy; two task sets (blue + green); traffic shifted by ALB/NLB listener rule; supports canary and linear shifting |
| **External deployment** | Third-party or custom deployment controller manages task sets |
| **Service Auto Scaling** | Application Auto Scaling adjusts desired task count; policies: Target Tracking (CPU/memory/ALB request count), Step Scaling, Scheduled Scaling |
| **Load balancer integration** | ALB (path/host routing, HTTP/HTTPS), NLB (TCP/UDP), Gateway Load Balancer; uses `ip` target type with `awsvpc` |

### Service Connect

| Concept | Description |
|---|---|
| **Purpose** | Combines service discovery + client-side load balancing + observability in ECS config; no separate infrastructure |
| **Namespace** | AWS Cloud Map namespace acting as the logical grouping; services in same namespace discover each other by short name |
| **Port alias / discovery name** | Name assigned to a port in task definition; becomes the DNS name clients use within the namespace |
| **Client alias** | Overrides the endpoint DNS name and port in the consuming service's config |
| **Proxy** | Service Connect agent sidecar runs in each task; intercepts traffic, round-robin load balances across healthy tasks with outlier detection |
| **Cross-cluster** | Services from multiple ECS clusters in the same region can share a namespace |
| **TLS** | Optional mTLS with AWS Private CA; certificates rotate every 5 days |
| **Metrics** | Per-connection and per-task metrics visible in ECS console and CloudWatch |

### ECS Exec

Allows interactive shell or command execution inside a running container via AWS Systems Manager (SSM). Requires:
- `enableExecuteCommand: true` on the service or task
- `ssmmessages:*` permissions on the task role
- SSM agent embedded in the container image (or use Amazon Linux 2 / Bottlerocket)

```bash
aws ecs execute-command --cluster my-cluster --task <task-id> \
  --container app --interactive --command "/bin/bash"
```

### Task Placement (EC2 launch type only)

| Strategy | Behavior |
|---|---|
| **spread** | Distribute evenly across values of a field (e.g., `attribute:ecs.availability-zone`) |
| **binpack** | Pack tasks onto fewest instances based on CPU or memory (cost optimization) |
| **random** | Place tasks randomly |

Placement constraints: `memberOf` (expression on instance attributes) and `distinctInstance` (each task on a unique instance).

### ECS Anywhere

Run ECS tasks on on-premises servers or VMs (any hardware). Register external instances using the ECS Anywhere installation script; instances appear as `EXTERNAL` container instances in the cluster. Requires SSM agent + ECS agent. Useful for hybrid workloads or edge computing scenarios.

---

## Comparison Tables

### ECS vs EKS vs App Runner

| Dimension | Amazon ECS | Amazon EKS | AWS App Runner |
|---|---|---|---|
| **Control plane** | AWS managed (no Kubernetes) | AWS managed Kubernetes | Fully managed |
| **Kubernetes required** | No | Yes | No |
| **Operational overhead** | Low | Medium–High | Minimal |
| **Scheduling granularity** | Task / Service | Pod / Deployment / StatefulSet | Instance (opaque) |
| **Networking model** | awsvpc (per-task ENI) | VPC CNI (per-pod ENI) or overlay | Abstracted |
| **Persistent storage** | EFS, FSx | EBS (CSI), EFS (CSI), S3 | Not supported |
| **DaemonSets / sidecar injection** | Daemon service scheduling | DaemonSets + admission webhooks | Not supported |
| **GPU workloads** | EC2 GPU instances | EC2 GPU instances | Not supported |
| **Auto scaling** | Service Auto Scaling + Cluster Auto Scaling | HPA + VPA + Karpenter / Cluster Autoscaler | Built-in (min/max/concurrency) |
| **Deployment strategies** | Rolling, Blue/Green (CodeDeploy), External | Rolling update, Argo Rollouts, Flux | Rolling (managed) |
| **Best for** | Simpler container orchestration, ECS-native teams, mixed Fargate/EC2 fleets | Complex microservices, stateful apps, K8s ecosystem (Helm, GitOps, service meshes) | Simple web apps and APIs from source or image with minimal ops |

### Service Connect vs Cloud Map vs App Mesh

| Feature | ECS Service Connect | AWS Cloud Map | AWS App Mesh |
|---|---|---|---|
| **Type** | ECS-native service mesh (built-in) | Service discovery registry | Full service mesh (Envoy-based) |
| **Load balancing** | Yes — built-in round-robin with outlier detection | No — DNS only | Yes — via Envoy proxy |
| **Traffic shifting** | No | No | Yes — weighted routes, canary |
| **Retry / timeout policies** | No | No | Yes |
| **mTLS** | Optional (via Private CA) | No | Optional (via Envoy) |
| **Platforms** | ECS only | ECS, EKS, EC2, Lambda | ECS, EKS, EC2 |
| **Metrics** | ECS + CloudWatch (built-in) | Basic | Envoy metrics → CloudWatch / Prometheus |
| **Distributed tracing** | No (use X-Ray SDK in app) | No | Yes — Envoy → X-Ray |
| **Operational overhead** | Low (config in ECS service definition) | Low | High (Envoy sidecars, mesh config) |
| **End of support** | Active | Active | September 30, 2026 |
| **Best for** | ECS service-to-service communication | Service discovery for any AWS workload | Advanced traffic management (migrating to alternatives recommended) |
