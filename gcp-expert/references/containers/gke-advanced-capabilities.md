# GKE Deep Dive — Advanced Capabilities

## GKE Modes: Standard vs Autopilot

### GKE Standard
You manage node pools (machine types, sizes, disk, taints, labels). You are responsible for node configuration, node upgrades (though Google automates them on the release channel), and node-level security. You pay for provisioned node resources whether pods use them or not. Standard mode gives full control over the data plane, enabling advanced node configurations (GPU nodes, TPU nodes, custom machine families, confidential nodes, gVisor sandbox nodes).

### GKE Autopilot
Google manages all nodes — you define pods and Google provisions the right underlying infrastructure. Billing is per pod (CPU, memory, ephemeral storage requested), not per node. Autopilot enforces secure pod specs by default (no privileged containers, no host network, no host PID, resource requests required). Best choice for most new workloads; eliminates node management overhead.

**Autopilot limitations**:
- No host network, host PID, host IPC in pod specs.
- No DaemonSets (use node-local services differently).
- No SSH to nodes.
- No custom node images.
- GPU nodes available but as a standard GPU compute class.

---

## GKE Enterprise (Fleet)

GKE Enterprise is a product tier (requires paid subscription) that adds multi-cluster management, policy, and service mesh capabilities on top of GKE Standard and Autopilot.

### Fleet (formerly Environ)

A **Fleet** is a logical grouping of GKE clusters (and Anthos clusters on other clouds/on-prem) under a single management scope. Fleet membership enables:
- Unified configuration management across clusters.
- Cross-cluster service discovery (Multi-cluster Services).
- Global load balancing (Multi-cluster Ingress).
- Centralized policy enforcement (Policy Controller).
- Managed Service Mesh (Anthos Service Mesh).

Register any GKE cluster into the Fleet of the host project. The host project is the "fleet host project" — the Fleet control plane is anchored there.

### Config Sync

Config Sync is a GitOps tool that continuously synchronizes Kubernetes resource manifests from a Git repository (GitHub, GitLab, Cloud Source Repositories) or OCI image (Artifact Registry) to one or more clusters in a Fleet.

**Key features**:
- Reconciles the live cluster state against the desired state in Git.
- Supports Kustomize overlays for environment-specific configuration.
- Supports Helm charts as the source of truth.
- Supports namespace-scoped (`RepoSync`) and cluster-scoped (`RootSync`) sync objects.
- Drift detection: any manual change to a managed resource is reverted to match Git.
- Multi-cluster: same Git config applies to all registered clusters (or per-cluster overrides with branches/paths).

**When to use**: any production GKE deployment where manifest changes go through Git PR review rather than direct `kubectl apply`.

### Policy Controller

Policy Controller (based on OPA Gatekeeper) enforces custom admission policies on all resource creation/update in enrolled clusters.

**Components**:
- **Constraint Templates**: define a policy schema using Rego (OPA policy language); compiled to a CRD.
- **Constraints**: instantiate a Constraint Template with specific parameters (e.g., require all pods to have resource limits; deny container images not from Artifact Registry; require specific labels).
- **Audit**: periodically scan existing resources for policy violations; reports violations in Constraint status.
- **Policy Bundle**: Google-provided bundles of pre-written constraints for CIS Kubernetes benchmarks, Pod Security Standards, NIST 800-53, etc.

**Common use cases**:
- Require all containers to have CPU/memory requests and limits.
- Restrict container image sources to your Artifact Registry repository.
- Require all Namespaces to have a specific label (e.g., `team`, `environment`).
- Block use of `latest` image tag.
- Enforce Pod Security Standards (baseline, restricted) as Constraints.

### Anthos Service Mesh (ASM)

ASM is Google's managed distribution of Istio. It provides:
- **mTLS**: automatic mutual TLS between all services in the mesh.
- **Traffic management**: fine-grained routing (VirtualService, DestinationRule), retries, timeouts, circuit breaking, traffic shifting.
- **Observability**: service-level metrics (golden signals: latency, traffic, errors, saturation), distributed tracing (Cloud Trace), topology visualization in GCP console.
- **Authorization policies**: RBAC policies controlling which services can call which endpoints.

ASM can be deployed as **managed ASM** (Google manages the control plane; you manage the data plane sidecar injection) or **in-cluster** (full Istio control plane in your cluster). Managed ASM is recommended for new deployments.

---

## GKE Networking

### VPC-Native Networking

GKE VPC-native clusters use **alias IP ranges** for Pod IPs. Each node gets a secondary IP range from the VPC subnet; pod IPs are drawn from this range. Benefits:
- Pod IPs are native VPC IPs — routable from other VPCs, VPNs, Interconnect.
- Cloud Load Balancer can communicate with pods directly (container-native load balancing).
- No overlay network performance overhead.

Node IP, Pod CIDR, and Service CIDR are all configured at cluster creation time. Plan these CIDRs carefully — they cannot be easily changed.

### Container-Native Load Balancing (NEG-based)

With VPC-native clusters, GCP load balancers can use **Network Endpoint Groups (NEGs)** as backends. NEGs contain pod endpoints (IP:port) directly — the load balancer sends traffic directly to pods, bypassing kube-proxy and NodePort. Benefits:
- True health checking at the pod level (not node level).
- Connection termination closer to the pod.
- Better load distribution (no hot nodes).

Enabling: add the `cloud.google.com/neg: '{"ingress": true}'` annotation to a Kubernetes Service, or GKE does it automatically for Services backed by an Ingress.

### GKE Gateway API

GKE Gateway API is the replacement for Kubernetes Ingress in GKE. It implements the Kubernetes Gateway API specification (GatewayClass, Gateway, HTTPRoute resources) and maps them to GCP load balancer resources.

**GatewayClasses in GKE**:
- `gke-l7-global-external-managed`: External Application Load Balancer (global, HTTP/S, CDN-capable).
- `gke-l7-regional-external-managed`: External Application Load Balancer (regional).
- `gke-l7-rilb`: Internal Application Load Balancer (regional, private VPC).
- `gke-l7-cross-cluster-internal`: Multi-cluster internal load balancer (for Multi-cluster Ingress).

**Why use Gateway API over Ingress**:
- Role-based: infrastructure admins manage GatewayClasses/Gateways; app teams manage HTTPRoutes.
- More expressive routing: header matching, query param matching, traffic splitting natively in spec.
- Multiple backends per route (traffic splitting for canary deployments).
- HTTPRoute, TLSRoute, TCPRoute — different protocols.

### GKE Dataplane V2 (Cilium/eBPF)

GKE Dataplane V2 replaces iptables-based kube-proxy with Cilium (eBPF) for packet processing in the kernel.

**Benefits**:
- Higher throughput and lower latency than iptables (kernel eBPF programs instead of iptables rules).
- **Network Policy observability**: Cilium Network Policy enforcement events visible in GKE console and Cloud Logging.
- **L7 network policy**: enforce policy based on HTTP path, method, headers (not just IP/port).
- **FQDN-based network policy**: allow traffic to `*.example.com` by DNS name.
- Node-local DNS caching built in.

Enable at cluster creation with `--enable-dataplane-v2`. Cannot be enabled on existing clusters without recreation.

---

## Multi-Cluster Features

### Multi-Cluster Ingress (MCI)

Multi-Cluster Ingress deploys a single global external Application Load Balancer that routes traffic to pods across multiple GKE clusters in multiple regions.

**How it works**:
- The Fleet host project runs the MCI controller.
- A `MultiClusterIngress` resource (and `MultiClusterService`) in the config cluster defines the load balancer.
- The MCI controller creates a global HTTP(S) Load Balancer with backends in each cluster region.
- Requests are routed to the nearest healthy cluster (anycast routing via Google's network).

**Use cases**: global applications that need sub-20ms latency worldwide; active-active multi-region deployments; failover across regions.

### Multi-Cluster Services (MCS)

Multi-Cluster Services enables cross-cluster service discovery. A `ServiceExport` in one cluster makes a Service available to other clusters in the Fleet. A `ServiceImport` in consuming clusters creates a virtual service that load balances across all exported endpoints.

**Use cases**: allow a service in cluster-A (us-central1) to call a service deployed in cluster-B (europe-west1) using a stable internal DNS name without exposing it externally.

---

## GKE Security

### Workload Identity

Workload Identity is the recommended way to grant GKE workloads access to GCP APIs without service account key files. Each Kubernetes ServiceAccount is bound to a GCP Service Account; the pod's metadata server automatically issues short-lived access tokens.

**Binding**: `gcloud iam service-accounts add-iam-policy-binding GCP_SA_EMAIL --member="serviceAccount:PROJECT.svc.id.goog[NAMESPACE/KSA]" --role="roles/iam.workloadIdentityUser"`

Then annotate the Kubernetes ServiceAccount: `kubectl annotate serviceaccount KSA iam.gke.io/gcp-service-account=GCP_SA_EMAIL`

### Binary Authorization

Binary Authorization requires container images to be signed (by Cloud Build or Sigstore) before they can be deployed to GKE. Policies specify which attestors (signers) must have signed an image for each cluster. Blocks deployment of unsigned or unverified images.

### Shielded GKE Nodes

Shielded nodes provide verified boot integrity for GKE nodes using:
- **Secure Boot**: only signed firmware, kernel, and OS are loaded.
- **vTPM (Virtual Trusted Platform Module)**: hardware-rooted trust; integrity measurement.
- **Integrity Monitoring**: baseline boot measurements stored; deviations detected and alerted.

### GKE Sandbox (gVisor)

gVisor provides an additional container isolation layer by intercepting and handling kernel system calls in userspace (not the host kernel). Use for running untrusted workloads or multi-tenant environments where you need stronger isolation than standard namespaces+cgroups.

Enable on a node pool with `--sandbox=gvisor`. Not all syscalls are supported — test your application compatibility. Slight performance overhead due to syscall interception.

### Confidential GKE Nodes

Run GKE nodes on Confidential VMs (AMD SEV — Secure Encrypted Virtualization). Memory is encrypted in hardware; even Google SREs cannot read VM memory. Use for regulated workloads (financial, healthcare, government) requiring hardware-level data-in-use encryption.

---

## Node Autoscaling

### Cluster Autoscaler (Standard mode)

Cluster Autoscaler (CA) scales node pools up when pods are Pending due to insufficient resources, and scales down when nodes are underutilized. Configure `--min-nodes` and `--max-nodes` per node pool.

**Important**: CA respects Pod Disruption Budgets (PDB) during scale-down. Pods with no PDB can be evicted immediately; pods with PDB are evicted only when the budget allows.

### Node Auto-Provisioning (NAP)

Node Auto-Provisioning extends CA to automatically create new node pools (with appropriate machine types and accelerators) when no existing node pool can accommodate a pending pod's requirements. GKE selects the cheapest machine type that satisfies the pod's resource requests. Also deletes node pools when no longer needed.

Enable with `gcloud container clusters update --enable-autoprovisioning`.

### Vertical Pod Autoscaler (VPA)

VPA adjusts individual pod CPU/memory requests and limits based on historical usage data from Metrics Server. Modes:
- **Off**: only provides recommendations (read from VPA object status), does not change pods.
- **Initial**: sets requests only at pod creation; does not update running pods.
- **Auto**: evicts and recreates pods with new resource requests when recommendations deviate significantly. Causes brief pod restarts.

VPA and HPA (Horizontal Pod Autoscaler) on the same deployment can conflict; do not use both for the same resource metric. Use VPA for CPU/memory; HPA for custom metrics (queue depth, RPS).

---

## Release Channels

Release channels automate GKE control plane and node version upgrades:

| Channel | Kubernetes version | Use case |
|---|---|---|
| Rapid | Latest available; weeks after upstream release | Testing new features, compatibility validation |
| Regular | 2-3 months after Rapid | Most production workloads (default) |
| Stable | 4-5 months after Rapid | Conservative, risk-averse production workloads |

Within a channel, Google manages minor version upgrades for control planes automatically. Node upgrades are configurable (auto-upgrade enabled by default). Maintenance windows and exclusions can restrict when upgrades occur.
