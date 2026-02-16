# Advanced Techniques for Scheduling Pods

The default Kubernetes scheduler (`kube-scheduler`) assigns pods to nodes through a two-phase process, but its behavior is highly configurable. This reference covers every major scheduling mechanism: node selection, affinity rules, taints, topology constraints, priority, and resource-based decisions.

## How the Scheduler Works

The scheduler runs a pipeline for each unscheduled pod:

1. **Filtering (Predicates)** -- eliminates nodes that cannot run the pod. Examples: insufficient CPU or memory, node selector mismatch, taint without matching toleration, port conflict, volume zone mismatch. Any node that fails a single predicate is removed from consideration.

2. **Scoring (Priorities)** -- ranks the remaining nodes. Each scoring plugin assigns a value (0-100) and the scores are weighted and summed. Examples: `LeastRequestedPriority` favors nodes with the most free resources, `BalancedResourceAllocation` favors nodes where CPU and memory utilization are proportional, `ImageLocalityPriority` favors nodes that already have the container image cached.

The highest-scoring node wins. On a tie, the scheduler picks randomly among the tied nodes.

## nodeSelector

The simplest form of node selection. Labels on nodes are matched against a map in the pod spec. All entries must match (logical AND).

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-worker
spec:
  nodeSelector:
    gpu-type: nvidia-a100
    environment: production
  containers:
    - name: trainer
      image: training-job:latest
      resources:
        limits:
          nvidia.com/gpu: 1
```

Label nodes first:

```bash
kubectl label node worker-03 gpu-type=nvidia-a100
kubectl label node worker-03 environment=production
```

`nodeSelector` is a hard constraint. If no node matches, the pod stays `Pending`.

## Node Affinity and Anti-Affinity

Node affinity generalizes `nodeSelector` with richer operators and soft/hard semantics.

### Required (Hard) Affinity

`requiredDuringSchedulingIgnoredDuringExecution` works like `nodeSelector` but supports complex expressions. The pod will not be scheduled unless the rule is satisfied. The `IgnoredDuringExecution` suffix means already-running pods are not evicted if labels change.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: zone-restricted
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: topology.kubernetes.io/zone
                operator: In
                values:
                  - us-east-1a
                  - us-east-1b
              - key: node.kubernetes.io/instance-type
                operator: NotIn
                values:
                  - t3.micro
  containers:
    - name: app
      image: myapp:latest
```

Multiple `matchExpressions` within a single `nodeSelectorTerms` entry are ANDed. Multiple `nodeSelectorTerms` entries are ORed.

### Preferred (Soft) Affinity

`preferredDuringSchedulingIgnoredDuringExecution` expresses a preference the scheduler tries to honor but will violate if necessary. Each preference carries a `weight` (1-100).

```yaml
affinity:
  nodeAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 80
        preference:
          matchExpressions:
            - key: disktype
              operator: In
              values:
                - ssd
      - weight: 20
        preference:
          matchExpressions:
            - key: topology.kubernetes.io/zone
              operator: In
              values:
                - us-east-1a
```

### Operators

| Operator | Meaning | Requires `values` |
|---|---|---|
| `In` | Label value is in the set | Yes |
| `NotIn` | Label value is not in the set | Yes |
| `Exists` | Label key is present (any value) | No |
| `DoesNotExist` | Label key is absent | No |
| `Gt` | Label value (parsed as int) is greater than the supplied value | Yes (single) |
| `Lt` | Label value (parsed as int) is less than the supplied value | Yes (single) |

`Gt` and `Lt` are available for node affinity only, not for pod affinity.

## Pod Affinity and Anti-Affinity

Pod affinity schedules pods relative to other pods rather than node labels. Every pod affinity rule requires a `topologyKey` that defines what "co-located" means.

### topologyKey

- `kubernetes.io/hostname` -- same node
- `topology.kubernetes.io/zone` -- same availability zone
- `topology.kubernetes.io/region` -- same region

The scheduler groups nodes by the value of the topology label, then checks whether the target group already contains a pod matching the `labelSelector`.

### Co-locating Related Pods

Place a cache pod on the same node as the web frontend it serves:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-cache
  labels:
    role: cache
spec:
  affinity:
    podAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchExpressions:
              - key: app
                operator: In
                values:
                  - web-frontend
          topologyKey: kubernetes.io/hostname
  containers:
    - name: redis
      image: redis:7
```

### Spreading Across Zones with Anti-Affinity

Ensure no two replicas of a database land in the same zone:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            - labelSelector:
                matchExpressions:
                  - key: app
                    operator: In
                    values:
                      - postgres
              topologyKey: topology.kubernetes.io/zone
      containers:
        - name: postgres
          image: postgres:16
```

Using `preferredDuringSchedulingIgnoredDuringExecution` instead would make zone spreading best-effort, which is appropriate when the cluster has fewer zones than replicas:

```yaml
podAntiAffinity:
  preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
            - key: app
              operator: In
              values:
                - postgres
        topologyKey: topology.kubernetes.io/zone
```

## Taints and Tolerations

Taints are applied to nodes and repel pods unless those pods carry a matching toleration. This is the inverse of affinity: affinity attracts pods to nodes, taints repel them.

### Taint Effects

| Effect | Behavior |
|---|---|
| `NoSchedule` | New pods without a matching toleration are never scheduled to this node. Existing pods are unaffected. |
| `PreferNoSchedule` | Soft version. The scheduler avoids the node but will use it if no alternatives exist. |
| `NoExecute` | Existing pods without a matching toleration are evicted. New pods are also rejected. |

### Managing Taints

```bash
# Add a taint
kubectl taint nodes worker-01 dedicated=gpu:NoSchedule

# Verify
kubectl describe node worker-01 | grep -A5 Taints

# Remove a taint (trailing minus)
kubectl taint nodes worker-01 dedicated=gpu:NoSchedule-
```

### Toleration Spec

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-pod
spec:
  tolerations:
    - key: dedicated
      operator: Equal
      value: gpu
      effect: NoSchedule
  containers:
    - name: worker
      image: gpu-job:latest
```

The `operator` field accepts `Equal` (default, requires `value`) or `Exists` (matches any value for that key). Omitting `key` with `operator: Exists` matches all taints. Omitting `effect` matches all effects for the given key.

For `NoExecute` taints, `tolerationSeconds` controls how long the pod may remain on the node after the taint is applied:

```yaml
tolerations:
  - key: node.kubernetes.io/not-ready
    operator: Exists
    effect: NoExecute
    tolerationSeconds: 300
```

### Built-in Taints

The node controller automatically applies taints based on node conditions:

| Taint | Condition |
|---|---|
| `node.kubernetes.io/not-ready` | Node `Ready` condition is `False` |
| `node.kubernetes.io/unreachable` | Node `Ready` condition is `Unknown` |
| `node.kubernetes.io/memory-pressure` | Node is under memory pressure |
| `node.kubernetes.io/disk-pressure` | Node is under disk pressure |
| `node.kubernetes.io/pid-pressure` | Node is running low on process IDs |
| `node.kubernetes.io/network-unavailable` | Node network is not configured |
| `node.kubernetes.io/unschedulable` | Node is cordoned |

Kubernetes automatically adds default tolerations for `not-ready` and `unreachable` (with 300s `tolerationSeconds`) to every pod unless the pod already specifies its own.

## Topology Spread Constraints

Topology spread constraints give fine-grained control over how pods distribute across failure domains. They are more flexible than pod anti-affinity for controlling skew.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 6
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: web
        - maxSkew: 2
          topologyKey: kubernetes.io/hostname
          whenUnsatisfiable: ScheduleAnyway
          labelSelector:
            matchLabels:
              app: web
      containers:
        - name: web
          image: nginx:latest
```

### Fields

- **maxSkew** -- the maximum allowed difference in pod count between the most-populated and least-populated topology domain. A `maxSkew` of 1 means perfectly even (or off by one).
- **topologyKey** -- the node label used to define topology domains (zone, node, region, rack, etc.).
- **whenUnsatisfiable** -- `DoNotSchedule` (hard, pod stays Pending) or `ScheduleAnyway` (soft, scheduler still tries to minimize skew).
- **labelSelector** -- selects which pods count toward the spread calculation.

Multiple constraints are ANDed. In the example above the deployment spreads evenly across zones (hard) and approximately evenly across nodes within each zone (soft).

## Pod Priority and Preemption

When cluster resources are scarce, priority and preemption let high-priority pods evict lower-priority ones.

### PriorityClass

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: critical-workload
value: 1000000
globalDefault: false
preemptionPolicy: PreemptLowerPriority
description: "For business-critical production services."
```

Reference it from a pod:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: critical-api
spec:
  priorityClassName: critical-workload
  containers:
    - name: api
      image: api-server:latest
```

### preemptionPolicy

- `PreemptLowerPriority` (default) -- the scheduler can evict lower-priority pods to make room.
- `Never` -- the pod gets priority in the scheduling queue but will never trigger eviction of other pods. Useful for batch workloads that should go first when resources free up naturally.

### System Priority Classes

Kubernetes ships two built-in classes:

| Name | Value | Purpose |
|---|---|---|
| `system-cluster-critical` | 2000000000 | Cluster-level critical pods (e.g., `coredns`) |
| `system-node-critical` | 2000001000 | Node-level critical pods (e.g., `kube-proxy`) |

These are reserved for system components. User workloads should use values below 1000000000.

### Preemption Mechanics

When a high-priority pod is unschedulable, the scheduler identifies a node where removing one or more lower-priority pods would make room. It evicts those pods (respecting their graceful termination period) and schedules the high-priority pod. Pods with `PodDisruptionBudget` protections may still be evicted by preemption if no other option exists.

## Resource-Based Scheduling

The scheduler uses **requests**, not limits, to decide placement. A pod requesting 500m CPU and 256Mi memory will only be placed on a node with at least that much allocatable capacity remaining.

```yaml
containers:
  - name: app
    image: myapp:latest
    resources:
      requests:
        cpu: 500m
        memory: 256Mi
      limits:
        cpu: "1"
        memory: 512Mi
```

Key implications:

- A node with 2 CPU cores allocatable can run four pods requesting 500m each, even if their limits are higher.
- Pods without requests are treated as requesting zero, so they can be scheduled anywhere but are first to be evicted under resource pressure.
- The `LeastRequestedPriority` scoring plugin favors nodes with the largest proportion of unrequested resources, promoting balanced distribution.

## Pod Overhead

Pod overhead accounts for resources consumed by the pod sandbox (runtime, pause container) beyond what the application containers request. This is relevant for VM-based runtimes like Kata Containers.

The overhead is defined in a `RuntimeClass`:

```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: kata
handler: kata-qemu
overhead:
  podFixed:
    cpu: 250m
    memory: 120Mi
```

When a pod references this runtime class, the scheduler adds the overhead to the pod's effective resource requests. A pod requesting 500m CPU under the `kata` runtime class consumes 750m from the node's allocatable capacity.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sandboxed-app
spec:
  runtimeClassName: kata
  containers:
    - name: app
      image: myapp:latest
      resources:
        requests:
          cpu: 500m
          memory: 256Mi
```

## Scheduler Profiles and Custom Schedulers

### Scheduler Profiles

A single `kube-scheduler` instance can expose multiple profiles, each with its own set of plugins. Pods select a profile via `spec.schedulerName`.

Profiles are configured in the scheduler's `KubeSchedulerConfiguration`:

```yaml
apiVersion: kubescheduler.config.k8s.io/v1
kind: KubeSchedulerConfiguration
profiles:
  - schedulerName: default-scheduler
    plugins:
      score:
        enabled:
          - name: NodeResourcesBalancedAllocation
            weight: 1
          - name: ImageLocality
            weight: 1
  - schedulerName: batch-scheduler
    plugins:
      score:
        disabled:
          - name: NodeResourcesBalancedAllocation
        enabled:
          - name: NodeResourcesLeastAllocated
            weight: 2
```

A pod targeting the batch profile:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: batch-job
spec:
  schedulerName: batch-scheduler
  containers:
    - name: worker
      image: batch:latest
```

### Plugin Extension Points

The scheduler framework exposes extension points where plugins run: `PreFilter`, `Filter`, `PostFilter`, `PreScore`, `Score`, `Reserve`, `Permit`, `PreBind`, `Bind`, and `PostBind`. Each built-in scheduling feature is implemented as a plugin at one or more of these extension points. Custom schedulers can be built by implementing the scheduler framework interface and deploying a separate scheduler binary, or more commonly by configuring profiles with different plugin combinations within the default scheduler.

### Running a Custom Scheduler

Deploy a second scheduler as a Deployment in the cluster. Give it a unique name and point pods at it with `spec.schedulerName`. The default scheduler ignores pods that specify a different scheduler name, so multiple schedulers coexist without conflict.
