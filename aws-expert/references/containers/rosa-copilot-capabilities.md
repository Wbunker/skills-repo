# ROSA & AWS Copilot — Capabilities Reference
For CLI commands, see [rosa-copilot-cli.md](rosa-copilot-cli.md).

## Red Hat OpenShift Service on AWS (ROSA)

**Purpose**: Fully managed OpenShift (OCP) clusters on AWS; jointly operated by Red Hat SRE and AWS; integrates natively with AWS IAM, networking, and storage.

### Deployment Modes

| Mode | Description |
|---|---|
| **Classic** | Control plane runs as EC2 instances in your AWS account; you see the control plane nodes in your VPC; SRE manages them jointly |
| **HCP (Hosted Control Plane)** | Control plane hosted in a Red Hat-managed AWS account; your account only contains worker nodes (machine pools); faster cluster creation, lower blast radius, recommended for new deployments |

### Cluster Architecture

| Component | Description |
|---|---|
| **Machine pools** | Groups of EC2 worker nodes; each pool has an instance type, min/max size, labels, taints, and availability zone configuration; HCP supports multiple machine pools with independent scaling |
| **Cluster autoscaling** | Per-machine-pool autoscaling based on pending workloads; configure min/max replicas per pool; ROSA manages the Cluster Autoscaler |
| **PrivateLink clusters** | Control plane communication over AWS PrivateLink; no public endpoints; traffic stays within AWS network; requires PrivateLink endpoint in your VPC |
| **Multi-AZ** | Machine pools can span multiple availability zones for HA |

### Authentication and IAM

| Concept | Description |
|---|---|
| **STS authentication** | ROSA uses AWS STS (Secure Token Service) for short-lived credentials; no long-lived IAM user keys stored in the cluster |
| **OIDC provider** | Each ROSA cluster has an OIDC identity provider registered in IAM; OpenShift components assume IAM roles via OIDC federation |
| **Operator roles** | IAM roles for in-cluster operators (Ingress Operator, Image Registry Operator, etc.); created during cluster installation via `rosa create operator-roles` |
| **Account roles** | IAM roles for ROSA control plane and worker nodes (Installer, ControlPlane, Worker, Support roles); created once per AWS account via `rosa create account-roles` |
| **SRE joint management** | Red Hat SRE has access via a break-glass IAM role to perform operational tasks; all access is logged and auditable |

### Networking

| Component | Description |
|---|---|
| **OpenShift Routes** | OCP-native HTTP/HTTPS ingress; `Route` objects expose services externally via the HAProxy-based OpenShift Router (Ingress Operator); supports TLS passthrough, edge, and re-encrypt termination |
| **Ingress Operator** | Manages the default router; deploys as an AWS NLB + HAProxy pods; supports custom domain certificates |
| **Custom domains** | Configure additional `IngressController` objects for custom domain routing |
| **VPC prerequisites** | You provision the VPC, subnets, and NAT gateways; ROSA uses your existing networking; subnets must be tagged for ROSA discovery |

### OCP Operators (OLM)

| Concept | Description |
|---|---|
| **OLM (Operator Lifecycle Manager)** | Built into OpenShift; manages installation, upgrading, and RBAC for cluster operators and user-installed operators |
| **OperatorHub** | Catalog of certified and community operators available in the OpenShift console; backed by Red Hat, certified ISV, and community catalogs |
| **Operator installation** | Install via console OperatorHub or `oc` CLI; OLM creates `Subscription`, `InstallPlan`, and `ClusterServiceVersion` resources |
| **Managed operators** | Certain operators (Ingress, Image Registry, Monitoring) are managed by SRE and cannot be disabled |

### Cluster Upgrades

| Concept | Description |
|---|---|
| **Upgrade channels** | `stable`, `fast`, `candidate`; control which OCP patch/minor versions are available for upgrade; set at cluster creation or updated later |
| **Scheduled upgrades** | Configure automatic upgrades during a maintenance window; SRE coordinates control-plane and node upgrades |
| **Manual upgrades** | Trigger via `rosa upgrade cluster` or the console; ROSA validates compatibility before proceeding |
| **Node drain** | Worker nodes are drained gracefully before replacement during upgrades |

### Monitoring Stack

| Component | Description |
|---|---|
| **Default stack** | Prometheus + Alertmanager + Grafana deployed by the Cluster Monitoring Operator; cannot be disabled on ROSA |
| **User workload monitoring** | Optional second Prometheus stack for application metrics; enabled via `cluster-monitoring-config` ConfigMap |
| **Alertmanager** | Route alerts to PagerDuty, Slack, email, etc.; user-workload Alertmanager is configurable |
| **Metrics forwarding** | Forward metrics to an external system (e.g., Amazon Managed Prometheus) using remote-write configuration |

### Image Registry

| Concept | Description |
|---|---|
| **Integrated registry** | OpenShift Image Registry operator provides an in-cluster registry backed by S3; used for build artifacts and internal image promotion |
| **S3 backend** | ROSA Image Registry stores images in an S3 bucket in your account; managed by the Image Registry Operator IAM role |
| **Registry route** | Optionally expose the registry externally via a Route for external pushes |
| **ECR integration** | Use ECR as an external registry; configure pull secrets or use IRSA-equivalent OIDC role for the kubelet to pull images |

---

## AWS Copilot

**Purpose**: CLI tool for deploying and operating containerized applications on Amazon ECS and AWS App Runner; abstracts infrastructure into application and environment concepts using CloudFormation under the hood.

### Core Concepts

| Concept | Description |
|---|---|
| **Application** | Top-level grouping for all services, jobs, and environments belonging to a project; stored in SSM Parameter Store |
| **Environment** | An isolated deployment target (e.g., `test`, `staging`, `production`); each environment gets its own VPC, ECS cluster, and shared ALB (for ECS workloads) |
| **Service / Workload** | A deployable unit within an application; maps to an ECS service or App Runner service |
| **Job** | A short-lived task; runs on a schedule or as a one-off; maps to ECS Scheduled Tasks or on-demand task runs |
| **Manifest file** | YAML file (`copilot/<name>/manifest.yml`) describing the workload type, image, CPU/memory, environment variables, scaling, and addons |
| **Addons** | CloudFormation templates in `copilot/<name>/addons/` or `copilot/environments/<env>/addons/` that provision supplementary AWS resources (S3, DynamoDB, RDS, etc.) and inject their outputs as environment variables |

### Workload Types

| Type | Description |
|---|---|
| **Load Balanced Web Service** | Internet-facing ECS service behind an ALB; suitable for HTTP/HTTPS APIs and web apps; supports path/host-based routing |
| **Backend Service** | ECS service not exposed to the internet; reachable only from other services in the same environment via Service Connect or service discovery |
| **Worker Service** | ECS service that polls an SQS queue (auto-created by Copilot); processes background jobs asynchronously |
| **Scheduled Job** | ECS task triggered by a cron schedule or rate expression via EventBridge Scheduler |
| **Request-Driven Web Service** | AWS App Runner service; fully managed; auto-scales to zero; no VPC required by default (can opt into VPC Connector) |

### Environments

| Concept | Description |
|---|---|
| **Environment provisioning** | `copilot env init` creates a VPC (or imports existing), subnets, ECS cluster, and shared ALB; all via CloudFormation |
| **Environment overrides** | Manifest supports `environments:` block to override CPU, memory, scaling, variables, or secrets per environment |
| **Shared ALB** | All Load Balanced Web Services in an environment share an ALB; Copilot manages listener rules per service |
| **Service Connect** | Default service-to-service communication within an environment; replaces Cloud Map-based service discovery |

### Pipelines

| Concept | Description |
|---|---|
| **Pipeline** | CI/CD pipeline using AWS CodePipeline; `copilot pipeline init` generates the pipeline manifest |
| **Pipeline manifest** | Defines source (GitHub, CodeCommit, Bitbucket, S3), stages, and deployment order across environments |
| **Build** | CodeBuild project builds and pushes the Docker image to ECR on each pipeline run |
| **Automated deployments** | Each stage calls `copilot svc deploy` internally; supports manual approval gates between stages |

### Storage Addons

| Resource | How to add |
|---|---|
| **S3 bucket** | `copilot storage init --storage-type S3` — generates an addon template; bucket ARN and name injected as env vars |
| **DynamoDB table** | `copilot storage init --storage-type DynamoDB` — generates table with configurable partition/sort keys and LSI/GSI |
| **RDS Aurora Serverless** | `copilot storage init --storage-type Aurora` — provisions Aurora Serverless v2 cluster; connection secret injected via Secrets Manager |

### Manifest File Key Fields

| Field | Description |
|---|---|
| `image.build` | Path to Dockerfile or build context |
| `image.location` | Pre-built ECR/Docker image URI (skip build) |
| `cpu` / `memory` | ECS task CPU units and memory (MiB) |
| `count` | Fixed replica count or autoscaling config with `min`, `max`, and CPU/memory targets |
| `http.path` | ALB routing path prefix for Load Balanced Web Service |
| `variables` | Key-value environment variables |
| `secrets` | SSM Parameter Store or Secrets Manager references injected as env vars |
| `network.vpc.placement` | `public` or `private` subnet placement for tasks |
| `publish.topics` | SNS topics the service publishes to (auto-created) |
| `subscribe.topics` | SQS subscriptions to SNS topics from other services (Worker Service) |
