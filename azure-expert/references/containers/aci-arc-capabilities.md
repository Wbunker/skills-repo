# Azure Container Instances & Azure Arc — Capabilities Reference
For CLI commands, see [aci-arc-cli.md](aci-arc-cli.md).

---

## Azure Container Instances (ACI)

**Purpose**: Run containers on-demand without managing virtual machines or orchestrators. Fastest way to run a container in Azure — provision in seconds, billed per second.

---

### Container Groups

The top-level resource in ACI is the **container group** — analogous to a Kubernetes pod.

| Feature | Description |
|---|---|
| **Shared lifecycle** | All containers in a group start and stop together |
| **Shared network** | Containers in a group share the same IP address and port namespace; communicate via `localhost` |
| **Shared storage** | Azure Files volume mounts shared across containers in the group |
| **Multi-container** | Run main container + sidecar containers (log shipper, proxy, init container) |
| **Init containers** | Run to completion before app containers start; for setup/initialization tasks |
| **OS type** | Linux or Windows (not mixed within a group) |

---

### Networking Options

| Option | Description |
|---|---|
| **Public IP** | Default; ACI gets a public IP; map ports explicitly |
| **Private (VNet injection)** | Deploy container group into a delegated subnet; no public IP; accessible only within VNet |
| **DNS name label** | Optional DNS label: `{label}.{region}.azurecontainer.io` for public groups |
| **Custom DNS** | Specify custom DNS servers for the container group |

**VNet requirements for private ACI:**
- Delegate a subnet to `Microsoft.ContainerInstance/containerGroups`
- Container group gets a private IP from the subnet CIDR
- No inbound from internet; communicate with other VNet resources directly

---

### Storage Volumes

| Volume Type | Description |
|---|---|
| **Azure Files (SMB)** | Persistent shared storage; survives container restarts; ReadWriteMany |
| **Azure Files (NFS)** | Premium Azure Files via NFS protocol |
| **gitRepo** | Clone a Git repo into the container at startup (read-only) |
| **Secret** | Mount secrets (Key Vault or inline) as a volume (files in the container) |
| **emptyDir** | Ephemeral scratch space shared between containers in the group; lost on restart |

---

### Container Group Features

| Feature | Description |
|---|---|
| **Restart policy** | `Always` (default), `OnFailure`, `Never` — control container restart behavior |
| **CPU and memory** | Specify per-container CPU (fractional vCPU) and memory (GB); group total determines billing |
| **GPU (N-series)** | Request GPU resources for ML inference workloads (limited region availability) |
| **Managed Identity** | System-assigned or user-assigned managed identity for container access to Azure resources |
| **Environment variables** | Plain text or secure (masked in portal) |
| **Confidential containers** | AMD SEV-SNP hardware attestation for sensitive workloads (limited preview) |
| **Spot containers** | Lower cost; may be evicted when Azure capacity needed; `az container create --priority Spot` |
| **Log analytics** | Forward container logs to Log Analytics workspace for persistent storage |

---

### Use Cases

| Use Case | Description |
|---|---|
| **Simple tasks** | Run a one-off container (data transformation, script execution) without AKS overhead |
| **Burst capacity for AKS** | AKS virtual nodes (using ACI) for rapid scale-out of stateless workloads |
| **Build agents** | CI/CD build containers; fast provisioning, bill only for build time |
| **Dev/test** | Quickly spin up services for testing without persistent infrastructure |
| **Scheduled batch** | Combine with Logic Apps or Azure Functions to trigger container runs on schedule |
| **Sidecar patterns** | Run main app + monitoring/proxy container in same group |

---

### ACI Limitations

- **No autoscaling**: cannot scale replicas based on demand (use Container Apps or AKS for this)
- **No orchestration**: no health checks with restarts for always-running services (limited restart policy)
- **No service mesh**: no built-in mTLS, traffic management
- **Container group limits**: 60 containers per group (practical limit much lower)
- **Networking**: VNet injection requires subnet delegation; limited to container group granularity

---

### ACI vs Container Apps vs AKS

| Criterion | ACI | Container Apps | AKS |
|---|---|---|---|
| **Startup speed** | Seconds | ~10–30 seconds | Node provision: minutes |
| **Autoscaling** | None | KEDA-based | Cluster autoscaler + KEDA |
| **Long-running services** | Limited | Yes | Yes |
| **Orchestration** | No | Yes (serverless K8s) | Full Kubernetes |
| **Cost model** | Per-second per container | Per replica-second | Per node VM |
| **Complexity** | Very low | Low | High |
| **Best for** | Short tasks, burst, dev | Microservices, event-driven | Complex K8s workloads |

---

## Azure Arc

**Purpose**: Extend Azure management, governance, and services to infrastructure running anywhere — on-premises, edge, and other cloud providers. A single control plane for hybrid and multi-cloud environments.

---

### Azure Arc Overview

| Arc Service | Description |
|---|---|
| **Arc-enabled Kubernetes** | Connect any K8s cluster to Azure; apply Azure RBAC, Policy, Defender, GitOps |
| **Arc-enabled Servers** | Connect any Windows/Linux VM to Azure; apply VM extensions, Update Manager, Defender |
| **Arc-enabled Data Services** | Run Azure SQL Managed Instance or PostgreSQL on Arc-enabled K8s (cloud-billed) |
| **Arc-enabled App Services** | Run App Service, Functions, Logic Apps Standard on Arc-enabled K8s |
| **Arc-enabled Machine Learning** | Train ML models on Arc-enabled K8s with Azure ML |

---

### Arc-enabled Kubernetes

Connect any CNCF-conformant Kubernetes cluster (GKE, EKS, RKE, on-premises, edge k3s) to Azure Arc.

**What you get after connecting:**
| Capability | Description |
|---|---|
| **Azure RBAC** | Control K8s API access using Azure role assignments and Entra ID identities |
| **Azure Monitor** | Container Insights, metrics, alerts via Azure Monitor agent extension |
| **Azure Policy (Gatekeeper)** | Enforce governance policies via OPA Gatekeeper on the connected cluster |
| **Defender for Containers** | Threat detection for workloads, control plane, and container images |
| **GitOps (Flux)** | Declarative cluster state management from Git; applies manifests automatically |
| **Azure Key Vault CSI** | Mount Key Vault secrets in pods on Arc-connected clusters |
| **Azure Arc extensions** | Installable add-ons (Flux, Defender, Monitor, App Services, ML) managed from Azure |

**Connection requirements:**
- Cluster must have outbound internet access to Arc endpoints (or private link for Azure Arc)
- `connectedk8s` Azure CLI extension required
- `az connectedk8s connect` installs Arc agents as pods in the cluster

---

### Arc Kubernetes Extensions

Extensions are Azure-managed packages deployed to Arc-enabled clusters:

| Extension | Purpose |
|---|---|
| `microsoft.flux` | GitOps via Flux v2 |
| `microsoft.azuredefender.kubernetes` | Defender for Containers |
| `azuremonitor-containers` | Container Insights / Azure Monitor agent |
| `azure-policy` | OPA Gatekeeper for Azure Policy |
| `microsoft.azurekeyvaultsecretsprovider` | Key Vault CSI driver |
| `microsoft.app.environment.aks-ext` | Azure Container Apps on Arc |
| `microsoft.openservicemesh` | Open Service Mesh (mTLS service mesh) |

---

### GitOps via Flux (Arc)

- `az k8s-configuration flux create` deploys Flux and creates a `FluxConfig` resource in Azure
- Flux syncs manifests from a Git repository (GitHub, Azure Repos, Bitbucket) to the cluster
- Supports Kustomize, Helm, and plain YAML manifests
- Compliance: Azure Policy can require all Arc-enabled clusters to have a Flux configuration

```bash
az k8s-configuration flux create \
  --cluster-name myArcCluster \
  --resource-group myRG \
  --cluster-type connectedClusters \
  --name cluster-config \
  --url https://github.com/myorg/cluster-config \
  --branch main \
  --kustomization name=infra path=./clusters/prod prune=true
```

---

### Arc-enabled Servers

Connect physical or virtual machines (Windows or Linux) from any environment to Azure.

**Capabilities after onboarding:**

| Capability | Description |
|---|---|
| **VM extensions** | Install and manage Azure VM extensions (Custom Script, Log Analytics agent, Dependency agent) |
| **Azure Monitor** | Collect metrics and logs via Azure Monitor agent; send to Log Analytics |
| **Update Manager** | Assess, schedule, and deploy OS updates from Azure portal |
| **Defender for Servers** | Threat protection, vulnerability assessment, JIT VM access |
| **Azure Policy (Guest Configuration)** | Audit and enforce OS configuration (password policies, installed software) |
| **Azure Automanage** | Automate best practice configurations (backup, monitoring, patching) |
| **Change Tracking & Inventory** | Detect file, registry, service, and software changes |

**Onboarding methods:**
- Single machine: `azcmagent connect` (interactive or service principal)
- At scale: service principal + onboarding script (MSI or shell) + configuration management tool (Ansible, SCCM)
- Azure Arc Jumpstart: community reference architectures for various onboarding scenarios

---

### Arc-enabled Data Services

Run Azure managed database services on your Arc-enabled Kubernetes clusters — same software, same management experience as Azure, but running on your infrastructure.

| Service | Description |
|---|---|
| **Azure SQL Managed Instance (Arc)** | Full SQL MI capabilities; cloud billing; cloud-connected or directly-connected mode |
| **PostgreSQL (Arc)** | Azure Database for PostgreSQL; scale-out hyperscale across multiple nodes |

**Key characteristics:**
- **Always up-to-date**: Microsoft pushes updates to your Arc data controller automatically
- **Cloud billing**: pay Azure consumption rates; no separate SQL Server licensing required (or use AHB)
- **Two modes**:
  - **Direct connected**: Arc cluster connects directly to Azure; real-time management and billing
  - **Indirect connected**: periodic upload of usage data; management via `kubectl`/`arcdata` CLI; air-gapped support
- **Data Controller**: namespace-level Arc component managing all data services on the cluster

---

### Arc-enabled App Services

Run Azure PaaS application services on any Arc-enabled Kubernetes cluster:

| Service | Description |
|---|---|
| **App Service** | Web apps on Arc K8s; same App Service features, custom domains, managed TLS |
| **Azure Functions** | Function apps running on Arc K8s infrastructure |
| **Logic Apps Standard** | Logic Apps Standard workflows on Arc K8s |
| **API Management (self-hosted gateway)** | APIM gateway deployed to Arc K8s for on-premises API routing |
| **Event Grid (on K8s)** | Event Grid topics and subscriptions running on Arc K8s |

**Prerequisites:** Arc-enabled K8s cluster, App Service extension installed via `az k8s-extension create`

---

### Arc Jumpstart

- Community-maintained reference implementations at [azurearcjumpstart.io](https://azurearcjumpstart.io)
- Automated scripts (Terraform, ARM, Bicep) to set up Arc demos and PoCs across all Arc scenarios
- Scenarios: Arc servers, Arc K8s, Arc data services, Arc-enabled app services, mixed environments
