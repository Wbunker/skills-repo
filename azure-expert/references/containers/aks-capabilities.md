# AKS — Advanced Capabilities Reference
For CLI commands, see [aks-cli.md](aks-cli.md).
For basic cluster creation and setup, see [compute/aks-capabilities.md](../compute/aks-capabilities.md).

## Azure Kubernetes Service (AKS) — Advanced Operational Topics

**Purpose**: Managed Kubernetes service on Azure. This document focuses on advanced operational topics: node pool management, networking deep dive, add-ons, storage, RBAC, GitOps, autoscaling, and cluster lifecycle.

---

## Node Pool Management

| Node Pool Type | Description | Use Case |
|---|---|---|
| **System node pool** | Required; hosts critical Kubernetes system pods (coredns, metrics-server, tunnelfront); tainted to prevent user workloads | Always present; use dedicated system pool for reliability |
| **User node pool** | Runs user workloads; can be scaled to zero when not needed | Application workloads |
| **Windows node pool** | Runs Windows Server containers; requires at least one Linux system pool | .NET Framework apps, Windows-specific workloads |
| **Spot node pool** | Uses Azure Spot VMs; evictable; up to 90% cost savings | Batch processing, fault-tolerant stateless apps |
| **Dedicated node pool** | Labeled/tainted for specific workload types | Compliance isolation, GPU workloads, specialized hardware |

### Node Pool Operations

- **Taints**: prevent scheduling of workloads that don't explicitly tolerate the taint
  - System pool auto-taint: `CriticalAddonsOnly=true:NoSchedule`
  - Custom taints: `az aks nodepool add --node-taints key=value:NoSchedule`
- **Labels**: used with `nodeSelector` or `nodeAffinity` for workload placement
  - Custom labels: `az aks nodepool add --labels environment=production tier=frontend`
- **Node pool upgrades**: upgrade node image independently of Kubernetes version with `--node-image-only`
- **Scale to zero**: user node pools can be scaled to 0 nodes (system pools: minimum 1)

---

## Networking Deep Dive

### Network Plugin Comparison

| Plugin | Pod IP Source | Scale | Notes |
|---|---|---|---|
| **kubenet** | Private CIDR (NAT to VNet) | Small-medium clusters | Simple; pods not directly routable on VNet; limited to 400 nodes without UDRs |
| **Azure CNI** | VNet subnet IPs | Large clusters (large IP space) | Direct pod connectivity; each pod uses a VNet IP; requires large subnet |
| **Azure CNI Overlay** | Private CIDR (not VNet) | Large clusters | Better IP efficiency; pods on overlay network; recommended for new large clusters |
| **Azure CNI Dynamic IP Allocation** | VNet IPs, dynamically allocated | Large clusters | Efficient IP usage from nodepool subnet; supports pod subnet |
| **BYOCNI** | Bring your own | Any | Install custom CNI (e.g., Cilium) after cluster creation |

### Azure CNI Overlay (Recommended for Large Clusters)
- Pods get IPs from a private CIDR (not routable on VNet directly)
- Nodes remain on VNet subnet (VNet IPs)
- Scales to thousands of pods without consuming VNet IP space
- Outbound traffic from pods is NATted through the node's VNet IP
- Supports network policies (Azure Network Policy Manager or Calico)

### Network Policies
- **Azure Network Policy Manager (NPM)**: built-in Azure implementation; supports standard Kubernetes NetworkPolicy
- **Calico**: open-source; richer policy features; works with both kubenet and Azure CNI
- **Cilium**: eBPF-based; requires BYOCNI; advanced L7 policies, observability
- Enable at cluster creation: `--network-policy azure` or `--network-policy calico`

### Ingress Controllers

| Controller | Description | Best For |
|---|---|---|
| **NGINX Ingress Controller** | Community standard; Helm-deployed; high flexibility | General HTTP/HTTPS routing |
| **Azure Application Gateway Ingress Controller (AGIC)** | Uses Azure Application Gateway as ingress; WAF integration | WAF, SSL offload, path-based routing, Azure-native |
| **Web Application Routing (managed)** | AKS add-on for managed NGINX + DNS (Azure DNS) + cert-manager (Let's Encrypt) | Simplified ingress with automatic TLS and DNS |
| **Azure Front Door** | Global load balancer with CDN, WAF; configure via Ingress annotations with AGIC | Multi-region, global routing |

---

## Add-ons and Extensions

### Monitoring
- **Container Insights** (Azure Monitor agent add-on): collects container logs, metrics, and events; sends to Log Analytics workspace
  - Enable: `az aks enable-addons --addons monitoring --workspace-resource-id {workspace-id}`
  - Metrics: CPU/memory by container, node, pod, namespace
  - Live logs: stream container stdout/stderr in real-time from portal
  - Recommended alerts: OOM kills, pod restarts, node conditions, CPU throttling

### Key Vault CSI Driver
- Mount Azure Key Vault secrets, keys, and certificates as Kubernetes volumes
- `SecretProviderClass` CRD: declares what to sync from Key Vault and how to map to Kubernetes secrets
- Authentication: Workload Identity (preferred) or managed identity
- Sync as Kubernetes secret: enable `--enable-secret-rotation` to auto-rotate synced secrets
- Enable: `az aks enable-addons --addons azure-keyvault-secrets-provider`

### KEDA (Kubernetes-based Event Driven Autoscaling)
- Scale deployments and jobs based on external event sources (Service Bus, Event Hubs, Queue Storage, HTTP, Cron, Prometheus, and 50+ KEDA scalers)
- `ScaledObject` CRD: references a Kubernetes Deployment/StatefulSet and a trigger
- `ScaledJob` CRD: scales Kubernetes Jobs for batch workloads
- Enable: `az aks enable-addons --addons keda`
- Example scaler: scale based on Service Bus queue length, targeting N messages per replica

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: my-scaler
spec:
  scaleTargetRef:
    name: my-deployment
  minReplicaCount: 0
  maxReplicaCount: 20
  triggers:
  - type: azure-servicebus
    metadata:
      queueName: myQueue
      namespace: myServiceBusNS
      messageCount: "5"
    authenticationRef:
      name: my-keda-auth
```

### Dapr (Distributed Application Runtime)
- Sidecar framework injected alongside application containers
- Capabilities: service invocation, pub/sub messaging, state management, secrets, bindings, actors, observability
- Enable: `az aks enable-addons --addons dapr`
- Components defined as Kubernetes CRDs (`Component` resource): configure state store (Redis, Cosmos DB), pub/sub (Service Bus, Event Hubs), secrets (Key Vault)
- Dapr sidecars injected via namespace annotation: `dapr.io/enabled: "true"`

### Azure Policy for Kubernetes (Gatekeeper)
- Enforce Rego policies on Kubernetes resources via OPA Gatekeeper
- Azure Policy definitions mapped to `ConstraintTemplate` and `Constraint` CRDs
- Built-in policies: disallow privileged containers, require resource limits, allowed container images, require labels
- Enable: `az aks enable-addons --addons azure-policy`
- View compliance in Azure Policy portal

### Workload Identity (Preferred: replaces AAD Pod Identity)
- Federated identity: link a Kubernetes Service Account to an Azure Managed Identity via OIDC federation
- No credentials stored in the cluster; pods get short-lived tokens via OIDC token projection
- Flow: Pod → projected token → Azure AD OIDC token exchange → Azure resource access
- Enable: `az aks update --enable-workload-identity --enable-oidc-issuer`
- Setup: create managed identity → create federated credential → create K8s ServiceAccount with annotation → deploy pod with SA

### Web Application Routing
- Managed NGINX ingress controller + Azure DNS integration + cert-manager (Let's Encrypt)
- Annotate Ingress resources with `kubernetes.azure.com/use-osm-mtls: "true"` or standard NGINX annotations
- Automatic TLS certificate provisioning from Let's Encrypt
- DNS record creation in Azure DNS zone on ingress deployment
- Enable: `az aks enable-addons --addons web_application_routing`

---

## Storage

| Storage Class | Protocol | Access Mode | Use Case |
|---|---|---|---|
| **Azure Disk (CSI)** | Block (iSCSI/NVMe) | ReadWriteOnce | Single-pod databases, stateful apps |
| **Azure Files (CSI)** | SMB / NFS | ReadWriteMany | Shared storage, multi-pod access |
| **Azure Blob (CSI)** | NFS 3.0 / BlobFuse2 | ReadWriteMany (NFS), ReadWriteOnce (Fuse) | Large files, data lakes, cold storage |
| **Azure Container Storage** | Block volumes pool | ReadWriteOnce | High-performance ephemeral or persistent block storage |

### Azure Container Storage
- Native block storage service built for Kubernetes; pools of storage exposed as PVs
- Storage pool types: Azure Disks, ephemeral disk (NVMe/local SSD), Elastic SAN
- Ephemeral disk: ultra-low latency using local NVMe on the node; best for scratch/temp storage
- Enable as AKS extension: `az aks update --enable-azure-container-storage azureDisk`

### Dynamic Provisioning
- PersistentVolumeClaims (PVCs) with StorageClass trigger dynamic provisioning
- Default StorageClasses in AKS: `managed-csi` (Azure Disk), `azurefile-csi` (Azure Files), `managed-csi-premium`
- Retain policy: `Retain` keeps disk after PVC deletion; `Delete` removes disk (default)

---

## GitOps with Flux

- **Flux** AKS extension: declarative cluster state management from Git repositories
- Cluster state defined in Git (YAML manifests, Helm charts, Kustomize); Flux reconciles actual state to desired
- `GitRepository` CRD: reference to a Git repo; `Kustomization` CRD: path within repo to apply
- Enable: `az aks enable-addons --addons flux` or `az k8s-extension create --extension-type flux`
- Multi-tenancy: restrict which namespaces a `GitRepository` source can be used in
- Notifications: Flux can send alerts to Slack, Teams, or webhook on reconciliation events
- Image automation: `ImageUpdateAutomation` CRD to automatically update image tags in Git when new images are pushed to ACR

---

## RBAC and Identity

### Kubernetes RBAC
- Native Kubernetes RBAC: `Role`/`ClusterRole` + `RoleBinding`/`ClusterRoleBinding`
- Bind Azure AD (Entra ID) groups to Kubernetes roles for enterprise access management

### Entra ID Integration
- AKS-managed Entra ID integration: Azure AD groups → Kubernetes RBAC groups
- `az aks get-credentials` fetches kubeconfig with Entra ID authentication
- Token refresh handled automatically; MFA and Conditional Access honored

### Azure RBAC for Kubernetes
- Use Azure RBAC roles (instead of or in addition to Kubernetes RBAC) to authorize K8s API access
- Built-in roles: `Azure Kubernetes Service RBAC Admin`, `Azure Kubernetes Service RBAC Cluster Admin`, `Azure Kubernetes Service RBAC Reader`, `Azure Kubernetes Service RBAC Writer`
- Enable: `az aks create --enable-azure-rbac`

---

## Cluster Autoscaling

### Cluster Autoscaler
- Adds or removes nodes based on pending pod scheduling pressure
- Configuration per node pool: `--enable-cluster-autoscaler --min-count N --max-count M`
- Scale-down: node removed when underutilized for a configurable period (default 10 min)
- Profile settings: `--cluster-autoscaler-profile scale-down-unneeded-time=10m scan-interval=10s`

### Node Auto-Provisioner (NAP) — Karpenter-based
- Replaces cluster autoscaler for dynamic right-sized node provisioning
- Karpenter evaluates pending pods and provisions the optimal node type (size, family, SKU) to fit workloads
- `NodePool` CRD: constraints on what node types can be provisioned (VM families, OS, taints)
- Faster scale-up than cluster autoscaler (provisions new node directly without pre-defined pool)
- Enable: `az aks update --node-provisioning-mode Auto`

---

## Cluster Upgrades

### Kubernetes Version Management
- AKS supports N-2 Kubernetes minor versions (e.g., if 1.30 is latest, 1.28 is minimum)
- Version support window: each minor version supported ~1 year
- Upgrade path: sequential minor version upgrades only (e.g., 1.28 → 1.29 → 1.30)
- Check available versions: `az aks get-versions --location eastus --output table`

### Auto-upgrade Channels

| Channel | Behavior |
|---|---|
| `none` | No automatic upgrades (default) |
| `patch` | Auto-upgrade to latest stable patch within current minor version |
| `stable` | Auto-upgrade to latest stable patch of N-1 minor version |
| `rapid` | Auto-upgrade to latest stable patch of latest minor version |
| `node-image` | Auto-upgrade node OS image only; does not upgrade Kubernetes version |

### Planned Maintenance Windows
- Control when automatic upgrades and maintenance tasks occur
- Configure maintenance window: day of week, start hour, duration
- `az aks maintenanceconfiguration add --name default --weekday Saturday --start-hour 1`

### Upgrade Process
1. Control plane upgraded first (no downtime for managed AKS control plane)
2. Node pools upgraded: surge upgrade (add N extra nodes, drain old nodes, remove)
3. `--max-surge` controls how many extra nodes added during upgrade (default 1, use 33% for faster upgrades)

---

## Cost Optimization for AKS

| Strategy | Description |
|---|---|
| **Spot node pools** | Up to 90% savings for fault-tolerant batch workloads |
| **Scale to zero user pools** | Scale user node pools to 0 when not needed (dev clusters overnight) |
| **Stop/start cluster** | `az aks stop` deallocates all nodes (preserves state); `az aks start` restores |
| **Reserved Instances for nodes** | Buy reserved VM instances for the underlying node VM SKU |
| **Right-size node pools** | Use `az aks nodepool update --min-count --max-count` to match actual workload needs |
| **Azure Container Storage ephemeral** | Use local NVMe for scratch storage vs premium disks |
| **B-series nodes** | Burstable VMs for dev node pools with variable CPU needs |
