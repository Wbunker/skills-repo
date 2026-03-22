# Azure Container Instances (ACI) — Capabilities Reference

For CLI commands, see [container-instances-cli.md](container-instances-cli.md).

## Azure Container Instances (ACI)

**Purpose**: Run containers on-demand without managing VMs or a container orchestrator. ACI is the fastest way to launch a container in Azure — typically seconds from CLI command to running container. Billed per second of vCPU and memory consumed.

**Best for**: Short-lived tasks, scheduled jobs, sidecar/init patterns, burst capacity for AKS (virtual nodes), event-driven processing, and development/test environments.

**Not ideal for**: Long-running stateful services, workloads requiring persistent storage with high IOPS, complex microservice architectures (use AKS or Container Apps instead).

---

## Container Groups

A **container group** is the fundamental deployment unit in ACI — analogous to a Kubernetes pod:

| Property | Details |
|---|---|
| **Containers** | One or more containers sharing the same lifecycle, network, and volumes |
| **Shared network** | Containers in a group share an IP address and port namespace; communicate via `localhost` |
| **Shared volumes** | Volumes are mounted into the group and shared across containers |
| **Scheduling** | Group is scheduled on a single host; all containers start together |
| **Restart policy** | `Always`, `OnFailure`, or `Never` — applies to all containers in the group |

### Multi-Container Patterns

- **Sidecar**: Main container + sidecar (log forwarder, metrics agent, Envoy proxy)
- **Ambassador**: Main container + ambassador proxy for external service abstraction
- **Adapter**: Main container + adapter to normalize output format

---

## Resource Configuration

| Resource | Range | Notes |
|---|---|---|
| **vCPUs** | 0.1–16 vCPU per group | Minimum 0.1; set per container, total limited by SKU |
| **Memory** | 0.1–64 GB per group | Set per container; proportional to vCPU |
| **GPU** | 1–4 NVIDIA K80/V100 (select regions) | GPU containers require specialized node pools |
| **Confidential** | AMD SEV-SNP (select regions) | Encrypted memory for sensitive workloads |

### Resource Request vs. Limit

- ACI supports resource **requests** (guaranteed minimum); no separate limit concept
- Containers in a group share the requested total vCPU and memory

---

## Networking

### Public IP (default)

- ACI assigns a public IP to the container group
- Expose specific ports (TCP/UDP) on the public IP
- DNS name label: `<label>.<region>.azurecontainer.io`
- No built-in TLS termination; add a reverse proxy sidecar for HTTPS

### VNet Integration (Private IP)

- Deploy container group into a delegated subnet within your VNet
- Container group gets a private IP only (no public IP)
- Access from within VNet, peered VNets, or on-premises via VPN/ExpressRoute
- Enables access to private Azure services (Key Vault, Service Bus, databases) via Private Endpoints
- Requires subnet delegation to `Microsoft.ContainerInstance/containerGroups`
- Cannot combine VNet injection with some features (GPU, Windows containers in some regions)

---

## Volume Mounts

| Volume Type | Description | Use Case |
|---|---|---|
| **Azure Files** | Mount an Azure Files share (SMB) | Persistent storage shared across containers or runs |
| **Azure Files (NFS)** | Mount Azure Files via NFS 3.0 | Linux containers requiring NFS semantics |
| **emptyDir** | Ephemeral empty directory; shared within group | Temporary scratch space, shared between sidecar containers |
| **secret** | Mount Key Vault secrets or encoded values as files | Inject configuration files, TLS certs |
| **configMap** | Mount key-value pairs as files | Configuration injection |
| **gitRepo** | Clone a Git repo at container start (deprecated) | Legacy only |

---

## Init Containers

Init containers run to completion before application containers start:

- Useful for: database migration, fetching configuration, warming up caches, permission setup
- Multiple init containers run sequentially in order
- If any init container fails, the pod restart policy governs retry behavior
- Init containers share volumes with application containers

---

## Restart Policies

| Policy | Behavior | Use Case |
|---|---|---|
| **Always** | Restart all containers in group when any exits | Long-running services, sidecars |
| **OnFailure** | Restart only on non-zero exit code | Batch jobs that may fail and should retry |
| **Never** | Never restart; group terminates when all containers exit | Run-once jobs, CI tasks, one-shot scripts |

---

## Managed Identity

- ACI supports **system-assigned** and **user-assigned** managed identities
- Allows containers to authenticate to Azure Key Vault, Storage, Service Bus, etc. without credentials
- Token available at IMDS endpoint: `http://169.254.169.254/metadata/identity/oauth2/token`
- Compatible with `DefaultAzureCredential` in Azure SDKs

---

## GPU Containers

- Available in select regions (East US, West US, West Europe)
- GPU SKUs: K80 (legacy), V100 (high-performance training/inference)
- Linux containers only; Windows GPU not supported
- Specify `--gpu-sku` and `--gpu-count` at creation
- Useful for short-duration inference jobs without standing up a GPU VM

---

## Confidential Containers

- Uses AMD SEV-SNP hardware isolation
- Memory encrypted with a VM-specific key; not accessible to the host or Azure operators
- Requires `--sku Confidential` at creation
- Supports attestation for verifying workload integrity
- Available for Linux containers in select regions

---

## Virtual Nodes (ACI in AKS)

Virtual nodes allow AKS to burst pods directly to ACI without adding real VMs:

- Install ACI connector as an AKS add-on (`az aks enable-addons --addons virtual-node`)
- Pods scheduled on virtual nodes run as ACI container groups
- Enables infinite burst capacity for stateless workloads
- Not suitable for: stateful workloads, DaemonSets, HostPath volumes, host networking
- Pods are billed at ACI rates, not AKS node rates

---

## Logging and Monitoring

| Feature | Description |
|---|---|
| **Container logs** | `az container logs` streams stdout/stderr from a running container |
| **Container exec** | `az container exec` opens interactive shell in running container |
| **Log Analytics** | Send container logs and events to a Log Analytics workspace |
| **Azure Monitor** | Metrics: CPU/memory utilization per container group |
| **Diagnostic settings** | Export metrics and events to Log Analytics, Event Hubs, or Storage |

---

## Comparison: ACI vs. Container Apps vs. AKS

| Factor | ACI | Container Apps | AKS |
|---|---|---|---|
| **Management overhead** | None | Low | High |
| **Startup time** | ~5–10 seconds | ~20–60 seconds | Minutes (for new nodes) |
| **Scale-to-zero** | Yes (manual) | Yes (KEDA) | Yes (with KEDA + Cluster Autoscaler) |
| **Event-driven scaling** | No | Yes (KEDA built-in) | Yes (KEDA add-on) |
| **Persistent storage** | Azure Files | Azure Files / Disks | Full CSI driver support |
| **Networking** | Public IP or VNet | VNet-integrated | VNet-integrated (CNI) |
| **Use case** | One-off tasks, burst | Microservices, APIs, workers | Full Kubernetes workloads |
| **Pricing** | Per second vCPU+memory | Consumption + dedicated | Node VM cost |
