# Google Kubernetes Engine — Capabilities Reference

CLI reference: [gke-cli.md](gke-cli.md)

## Purpose

Fully managed Kubernetes service with deep GCP integration. GKE handles the Kubernetes control plane (API server, etcd, scheduler, controller manager) and provides automated node pool management, OS patching, cluster upgrades, and integration with GCP services including IAM, Cloud Logging, Cloud Monitoring, Artifact Registry, and load balancing. Supports both Autopilot (fully managed nodes) and Standard (user-managed nodes) modes.

---

## Core Concepts

| Concept | Description |
|---|---|
| Cluster | A collection of Compute Engine VMs running Kubernetes. Includes the control plane (managed by Google) and worker nodes. |
| Node pool | A group of nodes within a cluster with the same machine type, OS image, and configuration. A cluster has at least one default node pool. |
| Node | A Compute Engine VM running the Kubernetes kubelet, kube-proxy, and container runtime (containerd). |
| Pod | The smallest deployable unit in Kubernetes. One or more containers sharing network namespace and storage. |
| Workload Identity | Mechanism to grant Kubernetes service accounts access to GCP services without node-level service account keys. Best practice for GCP auth from pods. |
| GKE Autopilot | Fully managed mode where Google manages nodes, node pools, and cluster infrastructure. Billed per Pod resource requests. |
| GKE Standard | User-managed node pools. Full control over node configuration, OS, machine type. Billed per node (VM). |
| Cluster autoscaler | GKE Standard feature that automatically adjusts node pool size based on pending Pod resource requests. |
| Horizontal Pod Autoscaler (HPA) | Kubernetes native autoscaler that adjusts the number of Pod replicas based on CPU/memory/custom metrics. |
| Vertical Pod Autoscaler (VPA) | Recommends and/or automatically adjusts Pod resource requests/limits. Useful for right-sizing workloads. |
| Control plane | Google-managed Kubernetes master components (API server, etcd, scheduler). Regional clusters have multi-zone control planes. |
| Binary Authorization | Policy enforcement that only allows container images from trusted sources (attested by Cloud Build or attestors) to be deployed. |
| Config Sync | GitOps tool (GKE Enterprise) that syncs Kubernetes config from a Git repository or OCI image to the cluster continuously. |

---

## GKE Autopilot vs Standard

| Attribute | Autopilot | Standard |
|---|---|---|
| Node management | Google manages all nodes | User manages node pools |
| Billing model | Per Pod resource requests (CPU, memory, ephemeral storage) | Per node VM (whether Pods are scheduled or not) |
| Node access | No SSH or node-level access | Full SSH access to nodes |
| Node pool configuration | Not configurable | Full control (machine type, disk, OS, taints) |
| Cluster autoscaling | Automatic, per-Pod | Configured per node pool |
| GPU/TPU support | Supported (newer Autopilot) | Full support |
| DaemonSets | Restricted (GKE managed only) | Unrestricted |
| Host-path volumes | Not supported | Supported |
| Privileged containers | Not allowed | Allowed |
| Idle cost | No idle node cost (scale to 0 with no load) | Idle nodes billed even with no Pods |
| Security posture | Hardened by default (CIS benchmarks enforced) | Configurable |
| Release channel | Required | Optional |
| Best for | Standardized workloads, cost efficiency, teams without dedicated platform engineers | Workloads needing custom node config, DaemonSets, privileged access, GPU scheduling control |

---

## Cluster Types

| Type | Description | Use Case |
|---|---|---|
| Zonal cluster | Single-zone control plane and single-zone or multi-zone nodes | Dev/test, cost-sensitive workloads, stateful single-AZ workloads |
| Regional cluster | Multi-zone control plane (3 zones) and multi-zone nodes | Production workloads requiring HA; survives a zone failure |
| Private cluster | Nodes have no public IPs; control plane accessible only via private endpoint (with optional public endpoint restricted by CIDR) | Production security baseline; preferred for all new production clusters |
| Public cluster | Nodes have public IPs (legacy default) | Quick dev/test; not recommended for production |

---

## Node Pool Options

| Option | Details |
|---|---|
| Machine type | Any Compute Engine machine type. Common: `e2-standard-4`, `n2-standard-8`, `c3-standard-4`. Autopilot selects automatically. |
| Disk type | `pd-standard`, `pd-balanced`, `pd-ssd`. Default: `pd-balanced` (100 GB). |
| OS image | `cos_containerd` (Container-Optimized OS, default, recommended), `ubuntu_containerd`, `windows_sac` (Windows). |
| Spot nodes | `--spot` flag enables Spot VMs for node pool; 60-91% cheaper but can be preempted. Use for fault-tolerant workloads. |
| Taints | `key=value:effect` — NoSchedule, NoExecute, PreferNoSchedule. Used to dedicate nodes to specific workloads (e.g., GPU nodes). |
| Labels | Kubernetes node labels for `nodeSelector` and affinity rules in Pod specs. Also set at node pool level. |
| Custom service account | Assign a specific GCP service account to nodes (instead of default Compute SA). Workload Identity is preferred; custom node SA reduces blast radius. |
| Autoscaling | Min/max nodes per pool; cluster autoscaler adds/removes nodes based on Pod pending state. |
| Node auto-provisioning | GKE Standard can automatically create new node pools with appropriate machine types when Pods can't be scheduled. |

---

## GKE Features

### GKE Gateway Controller
Cloud-native implementation of Kubernetes Gateway API (successor to Ingress). Provisions and configures Google Cloud Load Balancers (HTTP(S), Internal, Multi-cluster). Supports advanced traffic management, TLS termination, and routing.

### Cloud DNS Integration
GKE-managed DNS for internal cluster service discovery. `--cluster-dns=clouddns` uses Cloud DNS instead of kube-dns/CoreDNS for improved scalability and Google-managed SLAs.

### Workload Identity Federation
Links Kubernetes service accounts to GCP service accounts (GSAs). Pods using a KSA bound to a GSA can call GCP APIs without key files. Required configuration:
1. Enable Workload Identity on cluster.
2. Annotate KSA with GSA: `iam.gke.io/gcp-service-account=GSA_EMAIL`.
3. Grant GSA the `roles/iam.workloadIdentityUser` role on the KSA.

### Config Connector
Kubernetes operator that allows managing GCP resources (Cloud SQL, Pub/Sub, GCS) using Kubernetes custom resources (CRDs). Enables GitOps-driven GCP resource provisioning.

### GKE Fleet
Unified management plane for multiple GKE clusters (and Anthos registered clusters). Enables Config Sync, Policy Controller, and Service Mesh across a fleet. Required for GKE Enterprise features.

### Backup for GKE
Managed backup service for GKE workloads. Backs up Kubernetes resources and persistent volume data to Cloud Storage. Supports scheduled backup plans and restore.

---

## Networking

### VPC-Native Networking (alias IPs)
All GKE clusters should use VPC-native mode (alias IPs). Pod IPs are assigned from a secondary IP range in the subnet—Pods are directly routable within the VPC without NAT. Enables connecting Pods to Cloud SQL, Memorystore, and other VPC services directly.

### Network Policies
Kubernetes NetworkPolicy resources restrict Pod-to-Pod traffic. Requires `--enable-network-policy` at cluster creation. Enforced by Calico (Standard) or Dataplane V2 (eBPF-based).

### Dataplane V2 (eBPF)
Based on Cilium + eBPF. Replaces iptables for kube-proxy functionality with higher performance and richer observability (per-flow network telemetry). Enabled with `--enable-dataplane-v2`. Required for GKE network policy enforcement in Autopilot.

### Intra-cluster services
- **ClusterIP**: internal service accessible only within cluster
- **NodePort**: accessible via node IP + port
- **LoadBalancer**: provisions a GCP Network Load Balancer (L4) or HTTP(S) Load Balancer (via Ingress/Gateway)
- **Ingress**: provisions and configures GCP HTTP(S) Load Balancer for path-based and host-based routing

---

## Security

### Workload Identity (replacing node SA keys)
Node service account keys stored on nodes are a security risk. Workload Identity is the GKE-recommended way to give Pods GCP API access. Eliminates the need for service account key files entirely.

### Binary Authorization
Enforce attestation policies at deploy time. Only images that have been attested (signed) by trusted authorities (e.g., Cloud Build after successful tests) are admitted by the cluster. Works with Cloud Deploy for supply chain security.

### Shielded GKE Nodes
Enable Shielded VM features on nodes: Secure Boot, vTPM, Integrity Monitoring. Prevents rootkit and bootkit attacks on nodes. Required for many compliance frameworks.

### GKE Secret Encryption (Application-Layer Secrets)
Encrypt Kubernetes Secrets at rest in etcd using a customer-managed Cloud KMS key. Enabled with `--database-encryption-key`.

### Private Clusters
Nodes have RFC 1918 internal IPs only. Control plane accessible via:
- **Private endpoint only**: most secure; requires VPN/Interconnect or Cloud Shell
- **Public endpoint (CIDR restricted)**: control plane has a public IP but only accessible from allowed CIDRs (authorized networks)

---

## When to Use GKE vs Cloud Run vs App Engine

| Signal | Use GKE | Use Cloud Run | Use App Engine |
|---|---|---|---|
| Need Kubernetes primitives (StatefulSets, DaemonSets, CronJobs, custom operators) | Yes | No | No |
| Need to run privileged containers or custom kernel modules | Yes (Standard) | No | No |
| Stateless HTTP containers, auto-scaling, zero management | No | Yes | No |
| Migrating a legacy App Engine Standard app | No | Maybe | Yes (maintain) |
| Multi-tenant workloads needing namespace isolation | Yes | Limited | No |
| Very high concurrency HTTP services without Kubernetes complexity | No | Yes | No |
| Event-driven microservices with complex orchestration | GKE + Eventarc | Cloud Run + Eventarc | No |
| Team has Kubernetes expertise; needs full ecosystem | Yes | No | No |

---

## Important Patterns & Constraints

- **Enable Workload Identity from day one**: retrofitting Workload Identity onto existing clusters is complex. Enable at cluster creation and enforce it for all workloads.
- **Use regional clusters for production**: a regional cluster control plane survives a zone outage. Zonal clusters lose the API server during zone failures.
- **Private clusters are the security default**: use `--enable-private-nodes` and `--master-authorized-networks` for all production clusters.
- **Release channels**: Rapid, Regular, Stable channels for automatic upgrades. Use Stable for production, Regular for staging, Rapid for development. Do not use no-channel for production.
- **Node auto-upgrades and auto-repair**: both should be enabled for all node pools. Manual upgrade management is error-prone.
- **Cluster autoscaler scale-up time**: typically 1-3 minutes to provision a new node. Plan for this in HPA/VPA tuning.
- **PodDisruptionBudgets**: required for graceful node upgrades when using autoscaling. Define PDBs for all production Deployments to prevent all Pods being evicted simultaneously.
- **Kubernetes quotas and LimitRanges**: always define ResourceQuota per namespace and LimitRange to prevent unbounded resource consumption.
- **etcd size limit**: GKE control plane has a ~8 GB etcd limit. Avoid storing large data in ConfigMaps/Secrets; use Cloud Storage or Firestore instead.
- **Container-Optimized OS (COS)**: default node OS; read-only root filesystem, locked-down kubelet. Strongly preferred over Ubuntu for security.
- **Node pool immutability**: machine type cannot be changed on an existing node pool; must create a new pool and drain the old one.
- **GKE cluster creation time**: regional cluster creation takes 4-7 minutes; zonal takes 2-4 minutes.
