# Running Production-Grade Kubernetes Workloads

This reference covers the metadata, batch processing, and operational patterns that make Kubernetes workloads production-ready. Labels and annotations organize resources. Jobs and CronJobs handle batch and scheduled work. Production patterns such as graceful shutdown, Pod Disruption Budgets, and PriorityClasses ensure reliability under real-world conditions.

## Labels

Labels are key-value pairs attached to any Kubernetes object. They are the primary mechanism for organizing, selecting, and grouping resources. Unlike names, labels are not unique; many objects can share the same label.

### Syntax Rules

- Keys and values must be 63 characters or fewer.
- Keys can include an optional prefix separated by a slash: `prefix/name`. The prefix must be a DNS subdomain (253 characters max). The name segment must start and end with an alphanumeric character and may contain dashes, underscores, and dots.
- Values follow the same character rules as key names. An empty string is a valid value.
- The `kubernetes.io/` and `k8s.io/` prefixes are reserved for Kubernetes core components.

### Common Label Conventions

The recommended set of labels provides a consistent vocabulary across teams and tooling:

```yaml
metadata:
  labels:
    app.kubernetes.io/name: webapp
    app.kubernetes.io/version: "2.4.1"
    app.kubernetes.io/component: frontend
    app.kubernetes.io/part-of: online-store
    app.kubernetes.io/managed-by: helm
```

Shorter labels are common in practice and perfectly valid:

| Label         | Purpose                                  | Example Values                   |
|---------------|------------------------------------------|----------------------------------|
| `app`         | Identifies the application               | `webapp`, `api`, `worker`        |
| `version`     | Release or image tag                     | `v2.4.1`, `latest`              |
| `tier`        | Architectural layer                      | `frontend`, `backend`, `cache`   |
| `environment` | Deployment stage                         | `dev`, `staging`, `production`   |
| `team`        | Owning team                              | `platform`, `payments`           |

### Applying Labels

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-api
  labels:
    app: payment-api
    tier: backend
    environment: production
    version: v3.1.0
spec:
  selector:
    matchLabels:
      app: payment-api
  template:
    metadata:
      labels:
        app: payment-api
        tier: backend
        environment: production
        version: v3.1.0
    spec:
      containers:
        - name: payment-api
          image: payment-api:3.1.0
```

Labels on the Deployment metadata are for selecting the Deployment itself. Labels in the pod template are for selecting the Pods. The selector must match a subset of the pod template labels.

## Selectors

Selectors filter resources by their labels. They appear in Service specs, Deployment specs, `kubectl` queries, and network policies.

### Equality-Based Selectors

Match on exact key-value equality or inequality:

```bash
# Select all Pods in production
kubectl get pods -l environment=production

# Select Pods that are NOT in the cache tier
kubectl get pods -l tier!=cache

# Combine multiple requirements (AND logic)
kubectl get pods -l app=webapp,environment=production
```

### Set-Based Selectors

Match against a set of values using `In`, `NotIn`, `Exists`, and `DoesNotExist`:

```bash
# Pods in staging or production
kubectl get pods -l 'environment in (staging, production)'

# Pods not in the frontend tier
kubectl get pods -l 'tier notin (frontend)'

# Pods that have a "release" label (any value)
kubectl get pods -l 'release'

# Pods that do not have an "experimental" label
kubectl get pods -l '!experimental'
```

### matchLabels and matchExpressions in Specs

Controller specs like Deployments, ReplicaSets, and Jobs use structured selector fields:

```yaml
selector:
  matchLabels:
    app: webapp
    environment: production
  matchExpressions:
    - key: tier
      operator: In
      values:
        - frontend
        - backend
    - key: experimental
      operator: DoesNotExist
```

`matchLabels` is a shorthand for equality-based requirements. `matchExpressions` supports the full set-based operators: `In`, `NotIn`, `Exists`, `DoesNotExist`. When both are specified, all requirements are ANDed together.

## Annotations

Annotations are key-value pairs for non-identifying metadata. They follow the same key syntax as labels but have no length limit on values. Annotations cannot be used in selectors.

Common uses:

```yaml
metadata:
  annotations:
    kubernetes.io/change-cause: "Rollout v3.1.0 with payment retry logic"
    prometheus.io/scrape: "true"
    prometheus.io/port: "9090"
    deployment.kubernetes.io/revision: "7"
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"apps/v1",...}
```

Annotations are used by tools and controllers to store configuration, build metadata, monitoring directives, and operational notes. They are the correct place for data that does not need to be queried via selectors.

## ReplicaSets

A ReplicaSet ensures a specified number of identical Pod replicas are running at all times. In practice, you never create ReplicaSets directly. Deployments manage ReplicaSets for you, adding rollout, rollback, and update strategy logic on top.

### ReplicaSet Spec

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: webapp-rs
  labels:
    app: webapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
        - name: webapp
          image: webapp:2.1.0
          ports:
            - containerPort: 8080
```

The ReplicaSet controller continuously reconciles the actual Pod count against the desired `replicas` value. If a Pod is deleted or fails, the controller creates a replacement. If there are too many Pods matching the selector (for example, from manual creation), the controller terminates the excess.

### Relationship with Deployments

When a Deployment creates or updates a ReplicaSet, it sets an `ownerReference` on the ReplicaSet pointing back to the Deployment. This establishes the ownership chain: Deployment -> ReplicaSet -> Pod. Deleting a Deployment cascades to its ReplicaSets and their Pods.

The Deployment controller uses the ReplicaSet's selector (not its name) to find its Pods. This is why the selector is immutable after creation: changing it would orphan existing Pods and break the ownership model.

If you find yourself wanting to create a standalone ReplicaSet, use a Deployment instead. The only exception is rare cases where you need custom update orchestration that Deployments do not support.

## Jobs

A Job creates one or more Pods and ensures that a specified number of them successfully terminate. Jobs are for batch work: data processing, migrations, report generation, or any run-to-completion task.

### Basic Job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration
spec:
  template:
    spec:
      containers:
        - name: migrate
          image: myapp:3.1.0
          command: ["./migrate", "--target", "v42"]
      restartPolicy: Never
```

The `restartPolicy` must be `Never` or `OnFailure`. It cannot be `Always` (that is for long-running workloads managed by Deployments).

### Key Fields

**completions**: The number of Pods that must successfully complete. Defaults to 1. Set this higher for work-queue patterns where each Pod processes one unit of work.

**parallelism**: The maximum number of Pods running concurrently. Defaults to 1. When `completions` is set, the controller launches up to `parallelism` Pods at a time until the total successful completions reaches the target.

**backoffLimit**: The number of retries before the Job is considered failed. Defaults to 6. Each Pod failure (exit code != 0 with `restartPolicy: Never`, or container restart limit reached with `restartPolicy: OnFailure`) counts as one retry. The controller uses exponential backoff (10s, 20s, 40s, capped at 6 minutes) between retries.

**activeDeadlineSeconds**: A hard time limit for the entire Job, measured from when the Job first starts a Pod. When exceeded, all running Pods are terminated and the Job is marked as failed with reason `DeadlineExceeded`. This is a safety net for Jobs that might hang indefinitely.

**ttlSecondsAfterFinished**: Automatically cleans up the Job and its Pods after the specified number of seconds following completion (success or failure). Without this, finished Jobs and their Pods remain until manually deleted.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: batch-processor
spec:
  completions: 10
  parallelism: 3
  backoffLimit: 4
  activeDeadlineSeconds: 3600
  ttlSecondsAfterFinished: 300
  template:
    spec:
      containers:
        - name: processor
          image: batch-worker:1.0.0
          command: ["./process"]
      restartPolicy: Never
```

This Job runs 10 completions, 3 at a time, allows 4 failures, must finish within 1 hour, and is cleaned up 5 minutes after it completes.

### Indexed Jobs

When `completionMode: Indexed` is set, each Pod receives a unique index (0 through completions-1) in the `JOB_COMPLETION_INDEX` environment variable. This lets each Pod process a distinct shard of work without external coordination.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: shard-processor
spec:
  completions: 5
  parallelism: 5
  completionMode: Indexed
  template:
    spec:
      containers:
        - name: worker
          image: shard-worker:1.0.0
          command: ["./process-shard"]
          env:
            - name: SHARD
              value: "$(JOB_COMPLETION_INDEX)"
      restartPolicy: Never
```

Each Pod knows its index and can use it to determine which partition of data to process. Index 0 processes the first shard, index 1 the second, and so on.

## CronJobs

A CronJob creates Jobs on a repeating schedule. It is the Kubernetes equivalent of the Unix cron daemon.

### Schedule Syntax

The schedule field uses standard cron format with five fields:

```
# ┌───────────── minute (0-59)
# │ ┌───────────── hour (0-23)
# │ │ ┌───────────── day of month (1-31)
# │ │ │ ┌───────────── month (1-12)
# │ │ │ │ ┌───────────── day of week (0-6, Sunday=0)
# │ │ │ │ │
# * * * * *
```

Examples:

| Schedule          | Meaning                            |
|-------------------|------------------------------------|
| `*/15 * * * *`    | Every 15 minutes                   |
| `0 * * * *`       | Every hour on the hour             |
| `0 2 * * *`       | Daily at 2:00 AM                   |
| `0 0 * * 0`       | Weekly on Sunday at midnight       |
| `0 9 1 * *`       | First day of each month at 9:00 AM |

### CronJob Spec

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-report
spec:
  schedule: "0 2 * * *"
  concurrencyPolicy: Forbid
  startingDeadlineSeconds: 600
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 5
  suspend: false
  jobTemplate:
    spec:
      activeDeadlineSeconds: 7200
      ttlSecondsAfterFinished: 86400
      template:
        spec:
          containers:
            - name: report
              image: report-generator:2.0.0
              command: ["./generate-report", "--date", "yesterday"]
          restartPolicy: OnFailure
```

### Key Fields

**concurrencyPolicy**: Controls what happens when a new Job is due but the previous one is still running.

| Policy    | Behavior                                                              |
|-----------|-----------------------------------------------------------------------|
| `Allow`   | Default. Multiple Jobs can run concurrently. No overlap protection.   |
| `Forbid`  | Skips the new Job run if the previous one is still active.            |
| `Replace` | Terminates the currently running Job and starts a new one.            |

`Forbid` is the safest choice for most production workloads. It prevents resource contention and data corruption from overlapping runs.

**startingDeadlineSeconds**: If the CronJob controller misses a scheduled run (due to controller downtime, for example), it can still start the Job if less than `startingDeadlineSeconds` have elapsed since the missed time. If too many runs have been missed (more than 100), the CronJob is not started and an event is logged. This field is critical for reliability. Without it, a controller restart could cause a burst of back-scheduled Jobs.

**successfulJobsHistoryLimit**: Number of completed Jobs to retain. Defaults to 3. Set to 0 to retain none.

**failedJobsHistoryLimit**: Number of failed Jobs to retain. Defaults to 1.

**suspend**: When set to `true`, the CronJob controller stops creating new Jobs on schedule. Existing running Jobs are not affected. This is useful for temporarily pausing a scheduled workload during maintenance without deleting the CronJob.

## Production Patterns

### Graceful Shutdown with preStop Hooks

When Kubernetes terminates a Pod (during a rollout, scale-down, or node drain), it follows a specific sequence:

1. The Pod is marked as `Terminating` and removed from Service endpoints.
2. The `preStop` hook runs (if defined).
3. SIGTERM is sent to all containers.
4. The kubelet waits up to `terminationGracePeriodSeconds` (default 30 seconds) for containers to exit.
5. SIGKILL is sent to any containers still running.

The problem: step 1 (endpoint removal) and step 3 (SIGTERM) happen concurrently. In-flight requests can arrive at the Pod after it receives SIGTERM. A `preStop` hook with a short sleep gives load balancers time to update:

```yaml
spec:
  terminationGracePeriodSeconds: 60
  containers:
    - name: webapp
      image: webapp:3.1.0
      lifecycle:
        preStop:
          exec:
            command: ["sh", "-c", "sleep 5"]
      ports:
        - containerPort: 8080
```

The sleep in the `preStop` hook delays SIGTERM delivery by 5 seconds, giving kube-proxy and ingress controllers time to remove the Pod from their backends. The application should also handle SIGTERM by stopping acceptance of new connections and draining existing ones.

**terminationGracePeriodSeconds** is the total budget for the entire shutdown sequence (preStop hook + SIGTERM handling). If your `preStop` hook takes 5 seconds and your application needs 30 seconds to drain connections, set this to at least 40 seconds. If the application does not exit within this window, it receives SIGKILL.

### Pod Disruption Budgets

A PodDisruptionBudget (PDB) limits the number of Pods that can be voluntarily disrupted at one time. Voluntary disruptions include node drains (`kubectl drain`), cluster autoscaler scale-downs, and rolling updates. Involuntary disruptions (node crashes, OOM kills) are not governed by PDBs.

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: webapp-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: webapp
```

Alternatively, use `maxUnavailable`:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: webapp-pdb
spec:
  maxUnavailable: 1
  selector:
    matchLabels:
      app: webapp
```

`minAvailable` and `maxUnavailable` are mutually exclusive. Both accept an integer or a percentage. With `minAvailable: 2` and 3 replicas, only 1 Pod can be disrupted at a time. With `maxUnavailable: 1`, the same constraint applies regardless of the current replica count.

PDBs are respected by the eviction API. If draining a node would violate a PDB, the drain command blocks until it is safe to proceed. This prevents cluster operations from taking down too many Pods of a critical workload simultaneously.

A PDB with `maxUnavailable: 0` or `minAvailable` equal to the replica count blocks all voluntary disruptions. This can prevent node drains and cluster upgrades from completing. Use such tight budgets only when absolutely necessary.

### PriorityClasses

PriorityClasses assign scheduling priority to Pods. When the cluster is under resource pressure, the scheduler can preempt (evict) lower-priority Pods to make room for higher-priority ones.

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: critical-workload
value: 1000000
globalDefault: false
preemptionPolicy: PreemptLowerPriority
description: "For production-critical services that must always run."
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: batch-low
value: 100
globalDefault: false
preemptionPolicy: Never
description: "For batch jobs that can wait for resources without preempting others."
```

Assign a PriorityClass to a Pod:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: payment-api
  template:
    metadata:
      labels:
        app: payment-api
    spec:
      priorityClassName: critical-workload
      containers:
        - name: payment-api
          image: payment-api:3.1.0
```

Key details:

- Higher `value` means higher priority. The range is -2147483648 to 1000000000. Values above 1000000000 are reserved for system-critical Pods.
- `globalDefault: true` sets this PriorityClass as the default for all Pods that do not specify one. Only one PriorityClass can be the global default.
- `preemptionPolicy: Never` means Pods with this class are prioritized in the scheduling queue but will not evict other Pods. This is useful for batch workloads that should get resources when available but should not disrupt running services.
- Two built-in PriorityClasses exist: `system-cluster-critical` (2000000000) and `system-node-critical` (2000001000). These are for cluster infrastructure components only.

A well-structured priority scheme for most clusters:

| PriorityClass        | Value     | Preemption | Use Case                              |
|----------------------|-----------|------------|---------------------------------------|
| `system-critical`    | 2000000000| Yes        | Cluster infrastructure (built-in)     |
| `critical-workload`  | 1000000   | Yes        | Revenue-critical production services  |
| `default`            | 0         | Yes        | Standard workloads (global default)   |
| `batch-low`          | 100       | Never      | Batch jobs, dev workloads             |

PriorityClasses interact with Pod Disruption Budgets and resource requests. A high-priority Pod can preempt a lower-priority Pod, but only if the lower-priority Pod is not protected by a PDB that would be violated. In practice, set resource requests accurately so the scheduler can make informed preemption decisions.
