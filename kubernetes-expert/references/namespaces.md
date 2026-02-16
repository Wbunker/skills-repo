# Namespaces, Quotas, and Limits for Multi-Tenancy

Namespaces partition a single Kubernetes cluster into virtual sub-clusters. They provide scope for resource names, a target for access control policies, and a boundary for resource quotas. Together with ResourceQuotas, LimitRanges, and NetworkPolicies, namespaces form the foundation of multi-tenancy in Kubernetes.

## What Namespaces Are

A namespace is a Kubernetes object that divides cluster resources into logically named groups. Resources within a namespace must have unique names, but the same name can be reused across different namespaces. Namespaces do not nest -- they are a flat structure.

Namespaces affect DNS resolution. A Service named `api` in namespace `staging` is reachable at `api.staging.svc.cluster.local`.

## Default Namespaces

Every cluster ships with four namespaces:

| Namespace | Purpose |
|---|---|
| `default` | Where objects land when no namespace is specified. Suitable for experimentation but not recommended for production workloads. |
| `kube-system` | Control-plane components (API server, scheduler, controller-manager, CoreDNS, kube-proxy). Avoid deploying application workloads here. |
| `kube-public` | Readable by all users, including unauthenticated ones. Conventionally holds cluster-wide public information such as the `cluster-info` ConfigMap. |
| `kube-node-lease` | Holds Lease objects used by the kubelet heartbeat mechanism. Each node gets a corresponding Lease that the control plane uses to detect node failures efficiently. |

## Creating and Managing Namespaces

### Imperative

```bash
kubectl create namespace team-backend
kubectl delete namespace team-backend   # deletes ALL resources inside
```

### Declarative

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: team-backend
  labels:
    team: backend
    env: production
```

Labels on namespaces are important because they are used as selectors for NetworkPolicies and for applying Pod Security Standards via the `pod-security.kubernetes.io/*` labels.

### Listing and Inspecting

```bash
kubectl get namespaces
kubectl describe namespace team-backend
```

## Setting the Default Namespace in Context

Rather than passing `-n <namespace>` on every command, set a default namespace in your kubeconfig context:

```bash
kubectl config set-context --current --namespace=team-backend
```

Verify the active namespace:

```bash
kubectl config view --minify --output 'jsonpath={..namespace}'
```

## Namespace-Scoped vs Cluster-Scoped Resources

Not every Kubernetes resource lives inside a namespace.

**Namespace-scoped** (partial list): Pods, Services, Deployments, ReplicaSets, ConfigMaps, Secrets, ServiceAccounts, Roles, RoleBindings, PersistentVolumeClaims, ResourceQuotas, LimitRanges, NetworkPolicies, Jobs, CronJobs.

**Cluster-scoped** (partial list): Nodes, PersistentVolumes, Namespaces, ClusterRoles, ClusterRoleBindings, StorageClasses, IngressClasses, CustomResourceDefinitions, PriorityClasses.

Discover the full lists programmatically:

```bash
kubectl api-resources --namespaced=true
kubectl api-resources --namespaced=false
```

## ResourceQuotas

A ResourceQuota constrains the aggregate resource consumption within a namespace. When a quota is active, every Pod or container creation request must include explicit resource requests/limits for any compute resource tracked by the quota, or it will be rejected.

### Compute Quotas

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: team-backend
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
```

### Object Count Quotas

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: object-quota
  namespace: team-backend
spec:
  hard:
    pods: "50"
    services: "10"
    services.loadbalancers: "2"
    services.nodeports: "0"
    secrets: "20"
    configmaps: "20"
    persistentvolumeclaims: "10"
```

Setting `services.nodeports: "0"` is a common technique to prevent teams from exposing services directly via NodePort.

### Storage Quotas

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: storage-quota
  namespace: team-backend
spec:
  hard:
    requests.storage: 100Gi
    persistentvolumeclaims: "10"
    fast-ssd.storageclass.storage.k8s.io/requests.storage: 50Gi
```

### Scoped Quotas

Quotas can be scoped to specific priority classes or termination behaviors:

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: high-priority-quota
  namespace: team-backend
spec:
  hard:
    pods: "5"
    requests.cpu: "4"
  scopeSelector:
    matchExpressions:
      - scopeName: PriorityClass
        operator: In
        values:
          - high-priority
```

Check current quota consumption:

```bash
kubectl get resourcequota -n team-backend
kubectl describe resourcequota compute-quota -n team-backend
```

## LimitRanges

While ResourceQuotas cap the total for a namespace, LimitRanges constrain individual Pods and containers. They set default, minimum, and maximum resource values.

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: container-limits
  namespace: team-backend
spec:
  limits:
    - type: Container
      default:
        cpu: 500m
        memory: 256Mi
      defaultRequest:
        cpu: 100m
        memory: 128Mi
      min:
        cpu: 50m
        memory: 64Mi
      max:
        cpu: "2"
        memory: 2Gi
    - type: Pod
      max:
        cpu: "4"
        memory: 4Gi
    - type: PersistentVolumeClaim
      min:
        storage: 1Gi
      max:
        storage: 50Gi
```

Key behaviors:

- **`default`**: Applied as the container's `limits` when none are specified.
- **`defaultRequest`**: Applied as the container's `requests` when none are specified.
- **`min` / `max`**: Admission is rejected if a container specifies values outside this range.
- The Pod-level type constrains the sum of all containers in a single Pod.
- LimitRanges work with ResourceQuotas: the defaults injected by a LimitRange satisfy the requirement that quotas impose for explicit resource values.

## Cross-Namespace Communication

Pods in different namespaces can communicate freely at the network level by default. Services are accessible across namespaces using their fully qualified DNS name:

```
<service-name>.<namespace>.svc.cluster.local
```

For example, a frontend Pod in `team-frontend` can reach a backend Service:

```yaml
env:
  - name: BACKEND_URL
    value: "http://api.team-backend.svc.cluster.local:8080"
```

Referencing a ServiceAccount from another namespace in an RBAC RoleBinding is also valid -- a ClusterRole can be bound to a ServiceAccount in any namespace:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: team-backend
subjects:
  - kind: ServiceAccount
    name: monitoring-sa
    namespace: monitoring
roleRef:
  kind: ClusterRole
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

## Namespace Isolation with NetworkPolicies

By default there is no network isolation between namespaces. NetworkPolicies restrict traffic at the namespace boundary.

### Deny All Ingress Within a Namespace

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: team-backend
spec:
  podSelector: {}
  policyTypes:
    - Ingress
```

### Allow Traffic Only From a Specific Namespace

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-frontend
  namespace: team-backend
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              team: frontend
      ports:
        - protocol: TCP
          port: 8080
```

This requires that the `team-frontend` namespace carries the label `team: frontend`. NetworkPolicies require a CNI plugin that supports them (Calico, Cilium, Weave Net). The default kubenet CNI does not enforce NetworkPolicies.

## Multi-Tenancy Patterns

### Namespace-per-Team

Each team gets a dedicated namespace with its own quotas, limit ranges, RBAC roles, and network policies. Teams operate independently and own all resources within their namespace.

### Namespace-per-Environment

Separate namespaces for `dev`, `staging`, and `production`. The same manifests are deployed across environments using kustomize overlays or Helm value files with environment-specific quotas and configurations.

### Namespace-per-Application

Each microservice or application gets its own namespace. Useful when applications have distinct lifecycle, scaling, and access requirements.

### Hybrid

Combine patterns by convention, for example `team-backend-prod`, `team-backend-staging`. This provides both team and environment isolation, though it increases the number of namespaces to manage.

## Best Practices

**Naming conventions.** Adopt a consistent scheme such as `<team>-<env>` or `<project>-<component>`. Use labels generously for filtering and policy targeting.

**Always set ResourceQuotas and LimitRanges in shared clusters.** Without quotas, a single namespace can starve others of resources. Without LimitRanges, individual Pods can consume the entire quota.

**Apply a default-deny NetworkPolicy to every namespace.** Then explicitly allow required traffic. This follows the principle of least privilege at the network layer.

**Use RBAC RoleBindings scoped to namespaces.** Grant teams admin access within their namespace and nothing outside of it. Avoid ClusterRoleBindings for application teams.

**Label namespaces consistently.** Labels drive NetworkPolicy selectors and Pod Security Standards enforcement (`pod-security.kubernetes.io/enforce: restricted`).

**Avoid the default namespace.** Route all workloads to explicitly named namespaces. Some organizations create an admission webhook or policy that rejects resources targeting `default`.

**Plan for namespace lifecycle.** Deleting a namespace deletes everything inside it, including Secrets, PVCs, and running Pods. Use finalizers or external tooling to protect critical namespaces from accidental deletion.

**Monitor quota usage.** Expose `kube_resourcequota` metrics via kube-state-metrics and set alerts when teams approach their limits, so quotas do not silently block deployments.
