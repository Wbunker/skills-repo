# DaemonSets: Maintaining Pod Singletons on Nodes

A DaemonSet ensures that exactly one copy of a pod runs on every node (or a selected subset of nodes) in the cluster. When nodes join the cluster, the DaemonSet automatically schedules a pod onto them; when nodes are removed, those pods are garbage collected. This one-pod-per-node guarantee makes DaemonSets the correct abstraction for node-level infrastructure concerns such as log collection, monitoring, networking, and storage.

## DaemonSet Spec

A DaemonSet spec closely resembles a Deployment spec but omits `replicas`, since the number of pods is determined by the number of matching nodes.

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-agent
  namespace: kube-system
  labels:
    app: node-agent
spec:
  selector:
    matchLabels:
      app: node-agent
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 0
  template:
    metadata:
      labels:
        app: node-agent
    spec:
      containers:
        - name: agent
          image: example/node-agent:1.4
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 250m
              memory: 256Mi
```

- **selector**: An immutable label selector that must match the pod template labels. Cannot be changed after creation.
- **template**: The pod specification applied to every matching node.
- **updateStrategy**: Controls how pods are replaced when the template changes. Defaults to `RollingUpdate`.

## How DaemonSets Schedule Pods

Since Kubernetes 1.12, DaemonSet pods are scheduled by the default kube-scheduler rather than the DaemonSet controller itself. The controller creates a pod for each eligible node and sets a `NodeAffinity` term targeting that node, then the scheduler handles binding. This unified approach gives DaemonSet pods access to the same priority, preemption, and affinity features available to all other pods.

The DaemonSet controller watches node events continuously. When a new node registers and transitions to `Ready`, the controller creates a pod targeting that node. When a node is deleted, the associated pod is cleaned up through owner references and garbage collection.

## Node Selectors and Node Affinity

To restrict a DaemonSet to a subset of nodes, use `nodeSelector` for simple label matching:

```yaml
spec:
  template:
    spec:
      nodeSelector:
        node-role: edge-gateway
      containers:
        - name: proxy
          image: envoyproxy/envoy:v1.28
```

For richer expressions, use node affinity with `requiredDuringSchedulingIgnoredDuringExecution` (hard constraints) or `preferredDuringSchedulingIgnoredDuringExecution` (soft preferences):

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: kubernetes.io/arch
              operator: In
              values: [amd64, arm64]
            - key: node.kubernetes.io/instance-type
              operator: NotIn
              values: [t3.nano]
```

This schedules the DaemonSet on amd64 and arm64 nodes while excluding undersized instances.

## Tolerations

By default, DaemonSet pods are not scheduled on tainted nodes. The DaemonSet controller automatically adds tolerations for `node.kubernetes.io/not-ready` and `node.kubernetes.io/unreachable` so pods survive node problems. For control plane nodes or custom taints, add tolerations explicitly:

```yaml
spec:
  template:
    spec:
      tolerations:
        - key: node-role.kubernetes.io/control-plane
          operator: Exists
          effect: NoSchedule
        - key: node.kubernetes.io/disk-pressure
          operator: Exists
          effect: NoSchedule
```

To tolerate all taints unconditionally (common for critical infrastructure daemons):

```yaml
tolerations:
  - operator: Exists
```

## Update Strategies

### RollingUpdate

The default strategy. Pods are replaced one (or more) at a time across nodes:

- **maxUnavailable**: Maximum number (or percentage) of pods that can be unavailable during the update. Higher values speed up rollouts at the cost of reduced coverage. Default is 1.
- **maxSurge**: Maximum number (or percentage) of extra pods created above the desired count. When non-zero, a new pod is created on the node before the old one is deleted, enabling zero-downtime updates. `maxSurge` and `maxUnavailable` cannot both be zero.

For zero-downtime updates on network or storage daemons:

```yaml
updateStrategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 0
    maxSurge: 1
```

### OnDelete

Pods are only replaced when manually deleted, giving operators full control over the rollout cadence:

```yaml
updateStrategy:
  type: OnDelete
```

After updating the DaemonSet template, delete pods selectively to trigger replacement with `kubectl delete pod <pod-name>`.

## Common Use Cases

### Log Collection (Fluent Bit, Fluentd, Filebeat)

A log shipper on every node collecting container logs from host paths:

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluent-bit
  namespace: logging
spec:
  selector:
    matchLabels:
      app: fluent-bit
  template:
    metadata:
      labels:
        app: fluent-bit
    spec:
      tolerations:
        - operator: Exists
      containers:
        - name: fluent-bit
          image: fluent/fluent-bit:2.2
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: 200m
              memory: 256Mi
          volumeMounts:
            - name: varlog
              mountPath: /var/log
              readOnly: true
      volumes:
        - name: varlog
          hostPath:
            path: /var/log
```

### Node Monitoring (Prometheus Node Exporter, Datadog Agent)

Monitoring agents need `hostNetwork` and `hostPID` for direct access to node-level metrics:

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
    spec:
      hostNetwork: true
      hostPID: true
      tolerations:
        - operator: Exists
      containers:
        - name: node-exporter
          image: prom/node-exporter:v1.7.0
          ports:
            - containerPort: 9100
              hostPort: 9100
          args:
            - --path.procfs=/host/proc
            - --path.sysfs=/host/sys
          volumeMounts:
            - name: proc
              mountPath: /host/proc
              readOnly: true
            - name: sys
              mountPath: /host/sys
              readOnly: true
      volumes:
        - name: proc
          hostPath:
            path: /proc
        - name: sys
          hostPath:
            path: /sys
```

### Network Plugins (Calico, Cilium, Weave)

CNI plugins deploy as DaemonSets to configure pod networking on every node. They typically require privileged access and host networking, and use `OnDelete` or `RollingUpdate` with `maxSurge: 1` because a gap in network coverage can partition the node.

### Storage Daemons (Ceph, GlusterFS)

Distributed storage systems run per-node daemons to manage local disks. These DaemonSets use `nodeSelector` or node affinity to target only nodes with attached storage devices.

## DaemonSet vs Deployment

| Concern | DaemonSet | Deployment |
|---|---|---|
| Pod count | One per matching node | Explicit replica count |
| Scaling | Automatic with cluster size | Manual or via HPA |
| Node coverage | Guaranteed per-node presence | No node-level guarantee |
| Scheduling | Tied to node identity | Placed by scheduler freely |
| Use case | Node-level infrastructure | Application workloads |

Use a DaemonSet when the workload must run on every node and is logically tied to the node itself. Use a Deployment when you need a specific number of replicas distributed across the cluster without regard for which nodes they land on.

## Resource Management and Priority

DaemonSet pods compete for resources on every node, so resource discipline is critical. Always set both `requests` and `limits`. Requests should reflect steady-state consumption so the scheduler accounts for DaemonSet overhead when placing other workloads. Remember that DaemonSet resource requests are multiplied by the number of nodes: a 256Mi request across 100 nodes consumes 25Gi of cluster memory.

For critical DaemonSets, assign a high `PriorityClass` to prevent eviction under resource pressure. DaemonSet pods can preempt lower-priority pods when resources are scarce. The built-in `system-node-critical` and `system-cluster-critical` priority classes should be used for essential kube-system DaemonSets:

```yaml
spec:
  template:
    spec:
      priorityClassName: system-node-critical
```

## DaemonSet Status and Monitoring

```bash
kubectl get daemonset -n kube-system
kubectl describe daemonset node-exporter -n monitoring
kubectl rollout status daemonset/fluent-bit -n logging
```

Key status fields:

- **desiredNumberScheduled**: Nodes that should run the pod.
- **currentNumberScheduled**: Nodes where the pod is currently scheduled.
- **numberReady**: Pods that have passed readiness checks.
- **numberMisscheduled**: Pods running on nodes where they should not be.
- **updatedNumberScheduled**: Pods running the latest template version during a rolling update.

A healthy DaemonSet shows `desired == current == ready` and `misscheduled == 0`. Any deviation warrants investigation into node conditions, taints, resource pressure, or image pull failures.

Roll back a failed update with `kubectl rollout undo daemonset/node-agent -n kube-system`.
