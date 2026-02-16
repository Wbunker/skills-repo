# Autoscaling Kubernetes Pods and Nodes

Kubernetes provides multiple autoscaling dimensions: horizontal (more pods), vertical (bigger pods), and cluster-level (more nodes). Effective autoscaling combines these layers so workloads get the resources they need without over-provisioning.

## Metrics Server

The metrics server is the foundation of resource-based autoscaling. It collects CPU and memory usage from kubelets and exposes them through the resource metrics API (`metrics.k8s.io/v1beta1`). HPA and VPA both depend on it.

```bash
# Install metrics-server (check for the latest manifest version)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Verify it is running
kubectl get deployment metrics-server -n kube-system

# Inspect node and pod resource consumption
kubectl top nodes
kubectl top pods -n my-namespace
```

For local clusters (minikube, kind), you may need the `--kubelet-insecure-tls` flag on the metrics-server deployment because kubelets use self-signed certificates.

## Horizontal Pod Autoscaler (HPA)

HPA adjusts the replica count of a Deployment, ReplicaSet, or StatefulSet based on observed metrics. The `autoscaling/v2` API is the current stable version and supports multiple metric types.

### HPA Algorithm

The controller evaluates the scaling ratio every 15 seconds (default `--horizontal-pod-autoscaler-sync-period`):

```
desiredReplicas = ceil( currentReplicas * (currentMetricValue / desiredMetricValue) )
```

When multiple metrics are specified, the controller computes `desiredReplicas` for each metric independently and takes the **maximum**. This means any single metric can trigger a scale-up, but all metrics must agree before a scale-down.

Pods that are not yet ready, that are being deleted, or that have failed are excluded from the calculation. If a pod has not yet reported metrics (still starting), it is treated conservatively during scale-up and ignored during scale-down.

### HPA v2 Spec with Resource Metrics

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-app-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 3
  maxReplicas: 50
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 75
```

The `averageUtilization` value is a percentage of the container's **resource request**, not the node capacity. If a container requests `200m` CPU and the target is 60%, the controller targets `120m` average across all pods.

### Metric Types

HPA v2 supports four metric sources:

| Type | What it measures | Target kinds |
|------|-----------------|--------------|
| `Resource` | CPU or memory per pod (from metrics-server) | `Utilization`, `AverageValue` |
| `Pods` | Custom per-pod metric (averaged across all pods) | `AverageValue` |
| `Object` | A metric from a single Kubernetes object (e.g., Ingress) | `Value`, `AverageValue` |
| `External` | A metric from outside the cluster (e.g., cloud queue depth) | `Value`, `AverageValue` |

#### Pods Metric Example (Custom per-pod)

```yaml
metrics:
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1k"
```

#### Object Metric Example

```yaml
metrics:
  - type: Object
    object:
      describedObject:
        apiVersion: networking.k8s.io/v1
        kind: Ingress
        name: web-app-ingress
      metric:
        name: requests_per_second
      target:
        type: Value
        value: "10k"
```

#### External Metric Example

```yaml
metrics:
  - type: External
    external:
      metric:
        name: pubsub.googleapis.com|subscription|num_undelivered_messages
        selector:
          matchLabels:
            resource.labels.subscription_id: my-subscription
      target:
        type: AverageValue
        averageValue: "30"
```

### Custom Metrics with Prometheus Adapter

To use application-level Prometheus metrics with HPA, deploy the Prometheus adapter. It registers itself as a custom metrics API server (`custom.metrics.k8s.io/v1beta1`) and translates Prometheus queries into the format HPA expects.

Key configuration in the adapter's ConfigMap:

```yaml
rules:
  - seriesQuery: 'http_requests_total{namespace!="",pod!=""}'
    resources:
      overrides:
        namespace: {resource: "namespace"}
        pod: {resource: "pod"}
    name:
      matches: "^(.*)_total$"
      as: "${1}_per_second"
    metricsQuery: 'rate(<<.Series>>{<<.LabelMatchers>>}[2m])'
```

This rule converts `http_requests_total` into `http_requests_per_second`, making it available as a `Pods`-type metric in HPA.

### Scaling Behavior

The `behavior` field gives fine-grained control over scale-up and scale-down velocity, preventing thrashing and allowing asymmetric policies:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: controlled-scaling-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 3
  maxReplicas: 100
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 60
        - type: Pods
          value: 10
          periodSeconds: 60
      selectPolicy: Max
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 120
      selectPolicy: Min
```

**`stabilizationWindowSeconds`**: The controller looks back over this window and picks the highest (scale-up) or lowest (scale-down) recommended replica count. A value of 300 for scale-down means the controller waits until the recommendation has been stable for five minutes. Setting scale-up to 0 allows immediate reaction to load spikes.

**`selectPolicy`**: When multiple policies are defined, this controls which one wins. `Max` picks the policy that allows the largest change (aggressive), `Min` picks the most conservative change, and `Disabled` prevents scaling in that direction entirely.

**Policy types**: `Pods` sets an absolute limit on how many replicas can be added or removed per period. `Percent` sets a percentage of current replicas. In the example above, scale-up uses `Max` between doubling (100%) and adding 10 pods, so at 5 replicas it can add 10 (the `Pods` policy wins), and at 20 replicas it can add 20 (the `Percent` policy wins).

### kubectl Shorthand

For simple CPU-based autoscaling:

```bash
kubectl autoscale deployment web-app --min=3 --max=50 --cpu-percent=60
```

This creates an `autoscaling/v2` HPA targeting CPU utilization. For anything beyond basic CPU targets, write the manifest directly.

## Vertical Pod Autoscaler (VPA)

VPA adjusts the CPU and memory **requests** (and optionally limits) of containers. It is useful for workloads where the correct resource request is unknown or changes over time, particularly for stateful or singleton workloads where horizontal scaling is impractical.

### VPA Components

| Component | Role |
|-----------|------|
| **Recommender** | Monitors resource consumption history and produces recommendations for each container |
| **Updater** | Evicts pods whose requests deviate significantly from the recommendation so they can be recreated with updated values |
| **Admission Controller** | Mutates pod specs at creation time, injecting the recommended requests before the pod starts |

### VPA Spec

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: backend-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
      - containerName: "backend"
        minAllowed:
          cpu: "100m"
          memory: "128Mi"
        maxAllowed:
          cpu: "4"
          memory: "8Gi"
        controlledResources: ["cpu", "memory"]
      - containerName: "sidecar"
        mode: "Off"
```

### Update Modes

| Mode | Behavior |
|------|----------|
| `Off` | Only produces recommendations (visible in the VPA status). No pods are modified. Use this to observe before enabling. |
| `Initial` | Applies recommendations only at pod creation. Running pods are never evicted. |
| `Recreate` | Evicts and recreates pods when recommendations change significantly. |
| `Auto` | Currently behaves like `Recreate`. Future versions may support in-place resource resizing without eviction. |

### VPA vs HPA

VPA and HPA target different axes of scaling, and they can coexist **as long as they do not both control CPU or memory**. The standard pattern is:

- Use HPA on a custom metric (requests per second, queue depth) for horizontal scaling.
- Use VPA to right-size the containers so each replica is efficient.
- Never let both HPA and VPA act on CPU utilization simultaneously. HPA increases replicas to reduce per-pod CPU, while VPA increases per-pod CPU requests, which changes the utilization denominator. The two controllers can fight each other, causing oscillation.

Choose VPA over HPA when the workload cannot be horizontally scaled (databases, singleton controllers) or when the primary problem is over- or under-provisioned requests rather than insufficient replica count.

## Cluster Autoscaler

The Cluster Autoscaler adjusts the number of **nodes** in a cluster. It bridges the gap between pod-level autoscaling and infrastructure capacity.

### How It Works

**Scale-up**: The scheduler marks pods as `Pending` when no node has sufficient resources. The Cluster Autoscaler detects these unschedulable pods, simulates placing them on nodes from each configured node group, and provisions new nodes in the group that best satisfies the demand.

**Scale-down**: Every `--scan-interval` (default 10s), the autoscaler evaluates each node. A node is a candidate for removal when its resource utilization (requests, not usage) is below `--scale-down-utilization-threshold` (default 0.5) and all its pods can be rescheduled elsewhere. Nodes must remain underutilized for `--scale-down-unneeded-time` (default 10m) before removal. Pods with PodDisruptionBudgets, local storage, or restrictive scheduling constraints can block scale-down.

### Cloud Provider Integration

The Cluster Autoscaler has provider-specific implementations:

- **GKE**: Node auto-provisioning can create entirely new node pools. Enable via `gcloud container clusters update --enable-autoscaling --min-nodes=1 --max-nodes=10`.
- **EKS**: Works with Auto Scaling Groups. Each ASG maps to a node group. The autoscaler uses AWS APIs to adjust desired capacity. Nodes must be tagged with `k8s.io/cluster-autoscaler/enabled` and `k8s.io/cluster-autoscaler/<cluster-name>`.
- **AKS**: Integrated directly. Enable per node pool with `az aks nodepool update --enable-cluster-autoscaler --min-count 1 --max-count 10`.

### Key Configuration Parameters

```
--scan-interval=10s                     # How often to re-evaluate the cluster
--scale-down-delay-after-add=10m        # Cooldown after adding a node
--scale-down-delay-after-delete=10s     # Cooldown after removing a node
--scale-down-delay-after-failure=3m     # Cooldown after a failed scale-down
--scale-down-unneeded-time=10m          # How long a node must be underutilized
--scale-down-utilization-threshold=0.5  # Utilization below this triggers consideration
--max-graceful-termination-sec=600      # Time given to pods during node drain
--balance-similar-node-groups=true      # Keep node groups at similar sizes
--skip-nodes-with-local-storage=true    # Protect nodes with emptyDir or hostPath
--skip-nodes-with-system-pods=true      # Protect nodes running kube-system pods
```

### Expanders

When multiple node groups can satisfy pending pods, the **expander** strategy selects which group to scale:

| Expander | Strategy |
|----------|----------|
| `random` | Pick a qualifying node group at random (default) |
| `most-pods` | Choose the group that would schedule the most pending pods |
| `least-waste` | Choose the group that would have the least idle resources after scheduling |
| `price` | Choose the cheapest group (requires cloud pricing integration) |
| `priority` | Choose based on a user-defined priority ConfigMap |

Set the expander with `--expander=least-waste`. Multiple expanders can be chained with a comma (e.g., `--expander=priority,least-waste`): the first expander filters, the next breaks ties.

## Karpenter

Karpenter is an open-source node provisioner originally built for AWS (now expanding to other providers) that replaces the Cluster Autoscaler with a more direct approach. Instead of working with pre-defined node groups and Auto Scaling Groups, Karpenter provisions individual nodes based on pending pod requirements.

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: general-purpose
spec:
  template:
    spec:
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["on-demand", "spot"]
        - key: node.kubernetes.io/instance-type
          operator: In
          values: ["m5.large", "m5.xlarge", "m6i.large", "m6i.xlarge"]
        - key: topology.kubernetes.io/zone
          operator: In
          values: ["us-east-1a", "us-east-1b"]
      nodeClassRef:
        group: karpenter.k8s.aws
        kind: EC2NodeClass
        name: default
  limits:
    cpu: "1000"
    memory: "1000Gi"
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 30s
```

Key advantages over Cluster Autoscaler: Karpenter provisions nodes in seconds rather than minutes, selects instance types directly (no ASG intermediary), supports consolidation (replacing multiple underutilized nodes with fewer right-sized ones), and handles spot interruption natively.

## KEDA (Kubernetes Event-Driven Autoscaling)

KEDA extends HPA with event-driven scaling, including the ability to scale to and from zero. It supports 60+ event sources (scalers) including Kafka, RabbitMQ, AWS SQS, Azure Service Bus, Prometheus, cron schedules, and more.

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: order-processor
  namespace: production
spec:
  scaleTargetRef:
    name: order-processor
  pollingInterval: 15
  cooldownPeriod: 120
  minReplicaCount: 0
  maxReplicaCount: 30
  triggers:
    - type: kafka
      metadata:
        bootstrapServers: kafka.production:9092
        consumerGroup: order-processor
        topic: orders
        lagThreshold: "50"
    - type: prometheus
      metadata:
        serverAddress: http://prometheus.monitoring:9090
        query: sum(rate(http_requests_total{service="order-api"}[2m]))
        threshold: "100"
```

KEDA creates and manages an HPA behind the scenes. When the workload scales to zero, KEDA takes over directly (HPA does not support zero replicas). When the trigger fires, KEDA scales to `minReplicaCount` (or 1) and hands control to the HPA for further scaling.

For job-based workloads, use `ScaledJob` instead of `ScaledObject` to spawn individual Jobs per event.

## Best Practices

**Right-size resource requests first.** Autoscaling depends on accurate requests. If requests are inflated, HPA will undercount utilization and not scale up when needed. If requests are too low, pods get OOMKilled or throttled. Use VPA in `Off` mode to gather recommendations before setting production values.

**Combine HPA with Cluster Autoscaler.** HPA adds pods; Cluster Autoscaler adds nodes to fit them. Without Cluster Autoscaler, HPA-created pods remain `Pending` when the cluster is full. Without HPA, Cluster Autoscaler has no signal to act on. The two are complementary.

**Use asymmetric scaling behavior.** Scale up aggressively to handle traffic spikes. Scale down conservatively to avoid flapping. A `stabilizationWindowSeconds` of 300 on scale-down is a reasonable starting point.

**Set meaningful minReplicas.** At least 2 replicas for high availability. Account for rolling update surge (if `maxSurge=1` and `minReplicas=2`, you temporarily need capacity for 3). Do not set `minReplicas` to 0 with HPA alone; use KEDA if you need scale-to-zero.

**Avoid HPA and VPA on the same resource metric.** If HPA targets CPU and VPA adjusts CPU requests, the controllers will conflict. Either use HPA on custom metrics and VPA on resources, or use one but not both for CPU/memory.

**Configure PodDisruptionBudgets.** When the Cluster Autoscaler or VPA Updater evicts pods, PDBs ensure availability. A PDB with `minAvailable: 50%` lets the autoscaler drain nodes without taking the entire workload offline.

**Monitor autoscaler behavior.** Key signals to watch: HPA `currentReplicas` vs `desiredReplicas`, VPA recommendations vs actual requests, Cluster Autoscaler `unschedulable_pods_count` and `scale_up_in_progress`. Alert on prolonged discrepancies between desired and actual state.
