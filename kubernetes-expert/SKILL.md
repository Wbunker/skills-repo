---
name: kubernetes-expert
description: >
  Expert-level Kubernetes assistance covering cluster architecture, workload
  management, networking, storage, security, and cloud deployments. Use when
  the user is working with Kubernetes, kubectl, Helm, Pods, Deployments,
  StatefulSets, DaemonSets, Services, Ingress, ConfigMaps, Secrets,
  PersistentVolumes, RBAC, ServiceAccounts, NetworkPolicies, namespaces,
  resource quotas, autoscaling (HPA/VPA/cluster), scheduling, taints,
  tolerations, affinity, node selectors, or any Kubernetes resource. Also
  triggers on mentions of EKS, GKE, AKS, kubeadm, minikube, kind, k3s,
  kustomize, container orchestration, pod design patterns (sidecar, init,
  ambassador), rolling updates, blue-green deployments, canary releases,
  liveness/readiness probes, or any Kubernetes API group.
---

# Kubernetes Expert

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                       Control Plane                          │
│  ┌────────────┐ ┌──────────────┐ ┌────────────────────────┐│
│  │ kube-api-  │ │    etcd      │ │  kube-controller-      ││
│  │ server     │ │  (key-value  │ │  manager               ││
│  │            │ │   store)     │ │  (replicas, endpoints,  ││
│  │            │ │              │ │   nodes, SA, tokens)    ││
│  └─────┬──────┘ └──────────────┘ └────────────────────────┘│
│        │        ┌──────────────┐ ┌────────────────────────┐│
│        │        │ kube-        │ │  cloud-controller-     ││
│        │        │ scheduler    │ │  manager (optional)    ││
│        │        └──────────────┘ └────────────────────────┘│
└────────┼────────────────────────────────────────────────────┘
         │ API (REST + gRPC)
         ▼
┌─────────────────────────────────────────────────────────────┐
│                       Worker Nodes                           │
│  ┌──────────┐  ┌──────────────┐  ┌─────────────────┐       │
│  │ kubelet   │  │ kube-proxy   │  │ Container       │       │
│  │ (node     │  │ (Service     │  │ Runtime         │       │
│  │  agent)   │  │  networking) │  │ (containerd/    │       │
│  │           │  │              │  │  CRI-O)         │       │
│  └──────────┘  └──────────────┘  └─────────────────┘       │
│  ┌──────────────────────────────────────────────────┐       │
│  │ Pods   [container(s)] [container(s)] [...]       │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

**Control Plane components:**
- **kube-apiserver** — REST API gateway; all cluster communication goes through it
- **etcd** — distributed key-value store; single source of truth for cluster state
- **kube-scheduler** — assigns Pods to Nodes based on constraints, affinity, resources
- **kube-controller-manager** — runs controllers (Deployment, ReplicaSet, Node, Job, etc.)
- **cloud-controller-manager** — integrates with cloud provider APIs (load balancers, routes, volumes)

**Node components:**
- **kubelet** — ensures containers in Pods are running per the PodSpec
- **kube-proxy** — maintains network rules for Service abstraction (iptables/IPVS)
- **Container runtime** — runs containers (containerd is the standard)

## Core Resource Quick Reference

| Resource | API Group | Short Name | Purpose |
|----------|-----------|------------|---------|
| Pod | core/v1 | `po` | Smallest deployable unit |
| Deployment | apps/v1 | `deploy` | Declarative stateless app management |
| ReplicaSet | apps/v1 | `rs` | Ensures N pod replicas |
| StatefulSet | apps/v1 | `sts` | Stateful app with stable identity |
| DaemonSet | apps/v1 | `ds` | One pod per node |
| Job | batch/v1 | — | Run-to-completion task |
| CronJob | batch/v1 | `cj` | Scheduled Jobs |
| Service | core/v1 | `svc` | Stable network endpoint |
| Ingress | networking.k8s.io/v1 | `ing` | HTTP/HTTPS routing |
| ConfigMap | core/v1 | `cm` | Non-sensitive configuration |
| Secret | core/v1 | — | Sensitive data (base64) |
| PersistentVolumeClaim | core/v1 | `pvc` | Request for storage |
| PersistentVolume | core/v1 | `pv` | Cluster storage resource |
| Namespace | core/v1 | `ns` | Virtual cluster partition |
| ServiceAccount | core/v1 | `sa` | Pod identity for API access |
| Role / ClusterRole | rbac.authorization.k8s.io/v1 | — | Permission rules |
| RoleBinding / ClusterRoleBinding | rbac.authorization.k8s.io/v1 | — | Bind roles to subjects |
| NetworkPolicy | networking.k8s.io/v1 | `netpol` | Pod-level firewall rules |
| HorizontalPodAutoscaler | autoscaling/v2 | `hpa` | Scale pods by metrics |

## Essential kubectl Commands

```bash
# Cluster info
kubectl cluster-info
kubectl get nodes -o wide
kubectl api-resources                    # list all resource types

# Common operations
kubectl get <resource> -n <ns>           # list resources
kubectl describe <resource> <name>       # detailed info
kubectl logs <pod> [-c container]        # container logs
kubectl logs <pod> --previous            # logs from crashed container
kubectl exec -it <pod> -- /bin/sh        # shell into container
kubectl port-forward <pod> 8080:80       # local port forward

# Apply and manage
kubectl apply -f manifest.yaml           # declarative create/update
kubectl delete -f manifest.yaml          # delete from manifest
kubectl diff -f manifest.yaml            # preview changes

# Debugging
kubectl get events --sort-by='.lastTimestamp'
kubectl top pods / kubectl top nodes     # resource usage (metrics-server)
kubectl run debug --image=busybox -it --rm -- sh  # ephemeral debug pod

# Context management
kubectl config get-contexts
kubectl config use-context <name>
kubectl config set-context --current --namespace=<ns>
```

## Pod Lifecycle

```
Pending → ContainerCreating → Running → Succeeded/Failed
                                  ↓
                            Terminating → Terminated
```

**Restart policies:** `Always` (default for Deployments), `OnFailure` (Jobs), `Never`

**Probes:**

| Probe | Purpose | Failure Action |
|-------|---------|----------------|
| `startupProbe` | App finished starting? | Kill + restart container |
| `livenessProbe` | App still healthy? | Kill + restart container |
| `readinessProbe` | Ready to receive traffic? | Remove from Service endpoints |

```yaml
# Probe example
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 15
  failureThreshold: 3
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  periodSeconds: 5
```

## Service Types

| Type | Description | Use Case |
|------|-------------|----------|
| `ClusterIP` | Internal only (default) | Service-to-service |
| `NodePort` | Expose on each node's IP:port (30000-32767) | Dev/testing |
| `LoadBalancer` | Cloud provider external LB | Production external access |
| `ExternalName` | CNAME to external DNS | External service alias |
| `Headless` (ClusterIP: None) | No cluster IP, returns pod IPs | StatefulSet discovery |

## Resource Requests and Limits

```yaml
resources:
  requests:          # scheduling guarantee (reserved)
    cpu: "250m"      # 0.25 CPU cores
    memory: "128Mi"
  limits:            # hard ceiling
    cpu: "500m"      # throttled if exceeded
    memory: "256Mi"  # OOMKilled if exceeded
```

**CPU:** 1 CPU = 1000m (millicores). Requests affect scheduling; limits cause throttling.
**Memory:** Requests affect scheduling; exceeding limits triggers OOMKill.

## Reference Documents

Load these as needed based on the specific topic:

| Topic | File | When to read |
|-------|------|-------------|
| **Introduction** | [references/introduction.md](references/introduction.md) | Kubernetes history, container orchestration concepts, monoliths vs microservices, why Kubernetes (Ch 1) |
| **Architecture** | [references/architecture.md](references/architecture.md) | Control plane internals, etcd, API server, scheduler, controller manager, kubelet, kube-proxy, container runtime, pod creation flow (Ch 2) |
| **Cluster Setup** | [references/cluster-setup.md](references/cluster-setup.md) | Installing clusters with minikube, kind, kubeadm, k3s; kubectl configuration, context management (Ch 3) |
| **Pods** | [references/pods.md](references/pods.md) | Pod spec, multi-container patterns (sidecar, init, ambassador), pod lifecycle, resource limits, probes, restart policies (Ch 4-5) |
| **Namespaces** | [references/namespaces.md](references/namespaces.md) | Namespace management, ResourceQuotas, LimitRanges, cross-namespace communication, multi-tenancy (Ch 6) |
| **Configuration** | [references/configuration.md](references/configuration.md) | ConfigMaps, Secrets, environment variables, volume mounts, immutable configs, secret types, external secret management (Ch 7) |
| **Services** | [references/services.md](references/services.md) | ClusterIP, NodePort, LoadBalancer, ExternalName, headless services, service discovery, DNS, endpoints, session affinity (Ch 8) |
| **Storage** | [references/storage.md](references/storage.md) | Volumes, PersistentVolumes, PersistentVolumeClaims, StorageClasses, dynamic provisioning, access modes, volume types (Ch 9) |
| **Workloads** | [references/workloads.md](references/workloads.md) | ReplicaSets, Jobs, CronJobs, production workload patterns, labels, selectors, annotations (Ch 10) |
| **Deployments** | [references/deployments.md](references/deployments.md) | Deployment strategies (rolling update, recreate), rollbacks, scaling, revision history, canary patterns, blue-green (Ch 11) |
| **StatefulSets** | [references/statefulsets.md](references/statefulsets.md) | Stable network identity, ordered deployment/scaling, volumeClaimTemplates, headless service pairing, update strategies (Ch 12) |
| **DaemonSets** | [references/daemonsets.md](references/daemonsets.md) | Per-node pod scheduling, node selectors, tolerations, update strategies, use cases (logging, monitoring, networking) (Ch 13) |
| **Helm & Operators** | [references/helm.md](references/helm.md) | Helm chart structure, templates, values, repositories, install/upgrade/rollback, creating charts, Kubernetes Operators, Operator SDK (Ch 14) |
| **Cloud Providers** | [references/cloud-providers.md](references/cloud-providers.md) | GKE, EKS, AKS setup and management, managed vs self-managed node pools, cloud-specific features, IAM integration (Ch 15-17) |
| **Security** | [references/auth.md](references/auth.md) | Authentication, RBAC, Roles, ClusterRoles, RoleBindings, ServiceAccounts, NetworkPolicies, PodSecurityStandards, security contexts (Ch 18) |
| **Scheduling** | [references/scheduling.md](references/scheduling.md) | Node selectors, affinity/anti-affinity, taints and tolerations, topology spread, pod priority and preemption, custom schedulers (Ch 19) |
| **Autoscaling** | [references/autoscaling.md](references/autoscaling.md) | HPA, VPA, cluster autoscaler, metrics-server, custom metrics, scaling policies, behavior configuration (Ch 20) |
| **Traffic & Advanced** | [references/ingress.md](references/ingress.md) | Ingress controllers, Ingress resources, TLS, Gateway API, traffic management, multi-cluster strategies, service mesh concepts (Ch 21) |
