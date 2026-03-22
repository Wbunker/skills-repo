# Azure Kubernetes Service (AKS) — Capabilities Reference

For CLI commands, see [aks-cli.md](aks-cli.md).

## Azure Kubernetes Service (AKS)

**Purpose**: Fully managed Kubernetes service. Azure manages the control plane (API server, etcd, scheduler) at no charge. You pay only for the agent nodes (VMs) and associated storage/networking. Standard Kubernetes tooling (kubectl, Helm, kustomize) works natively.

---

## Cluster Architecture

### Control Plane (Azure-managed)

| Component | Description |
|---|---|
| **API Server** | Exposes the Kubernetes API; accessed via `kubectl` or internal cluster components |
| **etcd** | Distributed key-value store for all cluster state; managed and backed up by Azure |
| **Controller Manager** | Runs Kubernetes controllers (Deployment, ReplicaSet, Node, etc.) |
| **Scheduler** | Assigns pods to nodes based on resource requests, affinity, and taints/tolerations |
| **Cloud Controller Manager** | Integrates Kubernetes with Azure resources (Load Balancers, Managed Disks, VNets) |

### Node Pools

| Type | Purpose | Notes |
|---|---|---|
| **System node pool** | Run critical system pods (CoreDNS, kube-proxy, metrics-server, tunnel-front) | Required; tainted with `CriticalAddonsOnly=true:NoSchedule`; should not run application workloads |
| **User node pool** | Run application workloads | Can be added, scaled, upgraded, or deleted independently; supports multiple pools |

### Multi-Node Pool Design Patterns

- Separate pools by workload type: CPU-intensive, GPU, Windows, memory-optimized
- Use node labels and nodeSelector/nodeAffinity to pin workloads to specific pools
- Use taints and tolerations to prevent unwanted scheduling
- Use spot node pools for fault-tolerant batch workloads

---

## Node Pool Options

| Feature | Description |
|---|---|
| **VM sizes** | Any Azure VM size; use D/E-series for general workloads, N-series for GPU, L-series for high IOPS |
| **OS** | Linux (Ubuntu or Azure Linux / Mariner); Windows Server 2022 |
| **Availability Zones** | Spread nodes across zones 1, 2, 3 for zone-redundant workloads |
| **Spot node pools** | Up to 90% discount; interruptible; use with `cluster-autoscaler` and `kubectl drain` on eviction |
| **Node autoscaler** | Cluster Autoscaler scales node count based on pending pods and resource utilization |
| **Node auto-provisioner (NAP)** | Uses Karpenter to provision right-sized nodes dynamically; eliminates need for fixed VM size selection |
| **Ephemeral OS disks** | OS disk backed by VM temp storage; faster boot, lower cost; no persistent state |
| **Node labels and taints** | Applied at pool creation; inherited by all nodes; used for workload scheduling |
| **Max pods per node** | Default 30 (kubenet) or 30–250 (Azure CNI); set at pool creation |

---

## Networking Models

| Model | Description | Use Case |
|---|---|---|
| **kubenet** | Nodes get VNet IP; pods get an internal IP with NAT; simpler | Small clusters; limited IP needs |
| **Azure CNI** | Every pod gets a real VNet IP; no NAT; required for Windows, Proximity, and Private Link | Production; direct pod access from other VNets |
| **Azure CNI Overlay** | Pods get IPs from a separate overlay network; nodes get VNet IPs | Conserve VNet IP space; preferred for large clusters |
| **Azure CNI with Dynamic IP Allocation** | Pre-allocates pod IPs per node from a separate subnet; reduces waste | Balance between CNI and IP conservation |
| **Cilium (BYO CNI)** | eBPF-based networking; advanced network policy; Hubble observability | Advanced network policy, performance |
| **BYOC (Bring Your Own CNI)** | Install any CNI (Calico, Cilium) manually | Custom requirements |

### Network Policy

- **Azure Network Policy Manager**: Built-in; supports basic NetworkPolicy rules
- **Calico**: Full Kubernetes NetworkPolicy + Calico GlobalNetworkPolicy
- **Cilium**: eBPF-based; L7 policy (HTTP, gRPC); Hubble for observability
- Set at cluster creation; cannot change post-deployment without recreation

---

## AKS Add-ons

Add-ons are Microsoft-managed extensions deployed and upgraded by AKS automatically.

| Add-on | Description |
|---|---|
| **Azure Monitor (Container Insights)** | Container-level metrics and logs to Log Analytics; powers Azure Monitor dashboards |
| **Azure Policy (Gatekeeper)** | Enforce OPA-based policies on Kubernetes resources (pod security, image registry, label requirements) |
| **Ingress Application Gateway (AGIC)** | Application Gateway as Kubernetes ingress; WAF + L7 load balancing |
| **Key Vault CSI Driver** | Mount Key Vault secrets as volume or environment variables; rotates secrets automatically |
| **HTTP Application Routing** | Simple ingress with Azure DNS; development/test only |
| **KEDA (Kubernetes Event-Driven Autoscaling)** | Scale deployments based on external event sources (Service Bus, Event Hubs, HTTP, custom) |
| **Dapr** | Distributed application runtime; pub/sub, service invocation, state management, secrets |
| **Open Service Mesh (OSM)** | Lightweight SMI-compliant service mesh; deprecated in favor of Istio add-on |
| **Istio** | Full service mesh with traffic management, mTLS, and observability |
| **Azure Blob CSI driver** | Mount Azure Blob containers as Kubernetes volumes (NFS or fuse) |
| **Azure Disk CSI driver** | Dynamic provisioning of Managed Disks; default storage class |
| **Azure File CSI driver** | Mount Azure Files shares as ReadWriteMany volumes |

---

## Workload Identity (Federated)

Workload Identity is the preferred mechanism for granting pods access to Azure services without credentials.

### How It Works

1. Create a **user-assigned managed identity** in Azure
2. Create a **Kubernetes service account** with Workload Identity annotations
3. Establish a **federated identity credential** linking the service account to the managed identity
4. Grant the managed identity RBAC on target Azure resources
5. Pods annotated with the service account receive an OIDC token; Azure AD exchanges it for an access token

### Why It Replaced AAD Pod Identity

- Pod Identity used a DaemonSet with privileged access; Workload Identity uses standard OIDC federation
- No privileged DaemonSet required
- Works with any Azure SDK that supports `DefaultAzureCredential`
- Supported on all AKS networking models

---

## KEDA — Event-Driven Autoscaling

KEDA (add-on or standalone) enables scale-to-zero and event-driven scaling beyond CPU/memory:

| Scaler | Scales on |
|---|---|
| **Azure Service Bus** | Queue depth or topic subscription message count |
| **Azure Event Hubs** | Consumer group lag |
| **Azure Storage Queue** | Queue message count |
| **Azure Blob Storage** | Blob count trigger |
| **Prometheus** | Custom Prometheus metric |
| **HTTP** | HTTP request rate (using HTTP add-on) |
| **MySQL / PostgreSQL** | Query result |
| **Kafka** | Consumer group lag |
| **CPU / Memory** | Standard HPA with KEDA ScaledObject |

---

## Cluster Upgrades

| Aspect | Details |
|---|---|
| **Control plane upgrade** | Azure upgrades control plane with zero downtime; command: `az aks upgrade --kubernetes-version` |
| **Node pool upgrade** | Rolling upgrade of nodes; cordon + drain + replace with new version |
| **Node surge** | Extra nodes provisioned during upgrade (`--max-surge`); reduces disruption |
| **Auto-upgrade channels** | `none`, `patch`, `stable`, `rapid`, `node-image`; automates version upgrades |
| **Node OS upgrade** | Separate from Kubernetes version; set via `--node-os-upgrade-channel` |
| **Supported versions** | AKS supports 3 minor versions + current; upgrade within 1 year before support ends |
| **Version skew** | AKS allows ±2 minor version skew between control plane and node pools |

---

## Azure Container Storage

Azure Container Storage (preview/GA) provides managed storage pools for AKS:

- **Azure Disks pool**: Dynamic Persistent Volume provisioning from a shared disk pool; supports NVMe
- **Ephemeral disk (local NVMe) pool**: Expose VM's local NVMe as fast ephemeral storage
- **Azure Elastic SAN pool**: iSCSI-based shared storage pool
- Integrates with Kubernetes StorageClass and PVC workflows

---

## Entra ID Integration

| Feature | Description |
|---|---|
| **Entra ID RBAC for Kubernetes** | Use Azure RBAC to control kubectl access (no kubeconfig credential sharing) |
| **Local accounts** | Disabled by default in new clusters; use `--disable-local-accounts` |
| **Conditional Access** | Apply MFA, device compliance to kubectl access |
| **Kubernetes RBAC** | Native Kubernetes ClusterRoleBinding / RoleBinding (works alongside or instead of Azure RBAC) |

---

## Azure Policy for Kubernetes

Implements OPA Gatekeeper policies from Azure Policy; built-in initiative for Kubernetes:

| Built-in Policy | Enforcement |
|---|---|
| Require containers to run as non-root | Deny pod if `runAsNonRoot` not set |
| Require read-only root filesystem | Deny pod with writable root FS |
| Disallow privileged containers | Deny `privileged: true` |
| Require resource limits | Deny pods without CPU/memory limits |
| Restrict allowed container registries | Deny images not from approved registries |
| Enforce Pod Security Standards (restricted) | Enforce full restricted PSS profile |

---

## Key Architecture Decisions

| Decision | Options | Recommendation |
|---|---|---|
| Networking model | kubenet / Azure CNI / Azure CNI Overlay | Azure CNI Overlay for new production clusters |
| Node pool OS | Ubuntu / Azure Linux (Mariner) | Azure Linux for lower image size and attack surface |
| Identity | Service Principal / Managed Identity | System-assigned Managed Identity (default for new clusters) |
| DNS service | CoreDNS | Default; customize with ConfigMap for split-horizon DNS |
| Ingress | AGIC / NGINX / Traefik | AGIC for WAF integration; NGINX for flexibility |
| Storage class | Azure Disk (default) / Azure Files / Azure Blob | Azure Disk for RWO; Azure Files for RWX; Blob for object semantics |
| Secrets | Kubernetes secrets / Key Vault CSI | Key Vault CSI + Workload Identity for production |
