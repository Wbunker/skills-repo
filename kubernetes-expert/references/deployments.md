# Deployments: Deploying Stateless Applications

A Deployment is the standard workload controller for running stateless applications on Kubernetes. It manages a ReplicaSet, which in turn manages Pods. This layering provides declarative updates, rollback history, scaling, and multiple deployment strategies. You never manage ReplicaSets directly when using Deployments; the Deployment controller handles their lifecycle.

## Resource Hierarchy

The ownership chain is Deployment -> ReplicaSet -> Pod. When you update a Deployment's pod template, the controller creates a new ReplicaSet with the updated template and scales it up while scaling the old ReplicaSet down. Old ReplicaSets are retained (with zero replicas) to support rollbacks. Each ReplicaSet corresponds to a revision in the Deployment's history.

```
Deployment (nginx-deploy)
  |
  +-- ReplicaSet (nginx-deploy-6b8d4f7b9c)  [revision 2, current, 3 replicas]
  |     +-- Pod (nginx-deploy-6b8d4f7b9c-x7k2p)
  |     +-- Pod (nginx-deploy-6b8d4f7b9c-m9n3q)
  |     +-- Pod (nginx-deploy-6b8d4f7b9c-r4t8w)
  |
  +-- ReplicaSet (nginx-deploy-5f7b3d9a1e)  [revision 1, old, 0 replicas]
```

## Deployment Spec

A complete Deployment manifest with all significant fields:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
  namespace: production
  labels:
    app: webapp
spec:
  replicas: 3
  revisionHistoryLimit: 10
  progressDeadlineSeconds: 600
  minReadySeconds: 5
  selector:
    matchLabels:
      app: webapp
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
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
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 250m
              memory: 256Mi
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 15
            periodSeconds: 20
```

### Key Fields

**replicas**: The desired number of identical Pods. Defaults to 1 if omitted.

**selector**: Must match `.spec.template.metadata.labels`. This is immutable after creation. The selector ties the Deployment to its ReplicaSets and Pods. Using `matchLabels` is the most common form; `matchExpressions` is available for complex selectors but rarely needed for Deployments.

**template**: The Pod template. Changes to any field within the template (image, env vars, resource limits, volumes) trigger a new rollout. Changes to metadata labels within the template also trigger a rollout. Changes outside the template (such as replicas count) do not.

**revisionHistoryLimit**: Number of old ReplicaSets to retain. Defaults to 10. Set to 0 to discard all history and disable rollbacks. Each retained ReplicaSet consumes a small amount of etcd storage.

**progressDeadlineSeconds**: How long the controller waits for a rollout to make progress before marking it as failed. Defaults to 600 (10 minutes). The timer resets each time progress is made (a new Pod becomes ready). When exceeded, the Deployment's condition is set to `Progressing=False` with reason `ProgressDeadlineExceeded`, but the rollout is not automatically rolled back.

**minReadySeconds**: How long a newly created Pod must be ready (without any container crashing) before it is considered available. Defaults to 0, meaning a Pod is considered available as soon as it is ready. Setting this provides a buffer to catch Pods that start successfully but crash shortly after.

## Deployment Strategies

### RollingUpdate (Default)

Incrementally replaces old Pods with new ones. The two parameters control the pace:

**maxSurge**: Maximum number of Pods that can exist above the desired replica count during the update. Accepts an absolute number or a percentage. Default is 25%. Setting this higher speeds up the rollout by running more new Pods in parallel.

**maxUnavailable**: Maximum number of Pods that can be unavailable during the update. Accepts an absolute number or a percentage. Default is 25%. Setting to 0 ensures full capacity is maintained throughout the rollout (requires maxSurge > 0).

Common configurations:

```yaml
# Zero-downtime: never drop below desired count
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0

# Fast rollout: allow temporary over-provisioning and under-provisioning
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 50%
    maxUnavailable: 50%

# One-at-a-time: conservative, slowest
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 0
    maxUnavailable: 1
```

When `maxSurge: 0` and `maxUnavailable: 0` is specified, the update cannot proceed because no extra Pod can be created and no existing Pod can be removed. This is an invalid configuration.

### Recreate

Terminates all existing Pods before creating new ones. This causes downtime but is necessary when the application cannot tolerate two versions running simultaneously (for example, a legacy app that takes an exclusive database lock on startup).

```yaml
strategy:
  type: Recreate
```

No additional parameters are available for the Recreate strategy.

## Rolling Updates Step by Step

Given a Deployment with 3 replicas, `maxSurge: 1`, and `maxUnavailable: 0`, updating the image from v1 to v2 proceeds as follows:

1. Controller creates a new ReplicaSet (RS-v2) with 1 replica. Total Pods: 3 (v1) + 1 (v2) = 4 (maxSurge allows 1 above desired 3).
2. Once the v2 Pod passes its readiness probe, controller scales RS-v1 down by 1. Total: 2 (v1) + 1 (v2) = 3.
3. Controller scales RS-v2 up by 1. Total: 2 (v1) + 2 (v2) = 4.
4. v2 Pod becomes ready, controller scales RS-v1 down by 1. Total: 1 (v1) + 2 (v2) = 3.
5. Controller scales RS-v2 up by 1. Total: 1 (v1) + 3 (v2) = 4.
6. v2 Pod becomes ready, controller scales RS-v1 down to 0. Total: 0 (v1) + 3 (v2) = 3.

Readiness probes are critical. Without them, the controller considers a Pod ready as soon as all containers are running, which may be before the application can actually serve traffic.

### Monitoring a Rollout

```bash
# Watch rollout progress in real time
kubectl rollout status deployment/webapp

# Check the conditions on the Deployment
kubectl describe deployment webapp

# Watch Pods cycle during a rollout
kubectl get pods -l app=webapp --watch
```

The `rollout status` command exits with code 0 on success, nonzero on failure. This makes it suitable for CI/CD scripts.

### Pausing and Resuming

Pausing a rollout freezes it in its current state, allowing you to make multiple changes to the spec before triggering a single rollout:

```bash
kubectl rollout pause deployment/webapp

# Make several changes; none trigger a rollout while paused
kubectl set image deployment/webapp webapp=webapp:2.2.0
kubectl set resources deployment/webapp -c webapp --limits=cpu=500m,memory=512Mi

# Resume to trigger one combined rollout
kubectl rollout resume deployment/webapp
```

A paused Deployment cannot be rolled back until it is resumed.

## Rollbacks

Every time the pod template changes, a new revision is recorded. View the history:

```bash
kubectl rollout history deployment/webapp
```

Output:

```
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
3         <none>
```

To populate the CHANGE-CAUSE column, annotate the Deployment at update time:

```bash
kubectl annotate deployment/webapp kubernetes.io/change-cause="Update to v2.2.0"
```

Roll back to the previous revision:

```bash
kubectl rollout undo deployment/webapp
```

Roll back to a specific revision:

```bash
kubectl rollout undo deployment/webapp --to-revision=1
```

A rollback is itself a new revision. If you are on revision 3 and roll back to revision 1, revision 1 is removed from the history and the Deployment moves to revision 4 (with the same template as the old revision 1). Inspect a specific revision before reverting:

```bash
kubectl rollout history deployment/webapp --revision=2
```

## Scaling

### Imperative

```bash
kubectl scale deployment/webapp --replicas=5
```

### Declarative

Edit the manifest and apply it:

```yaml
spec:
  replicas: 5
```

```bash
kubectl apply -f webapp-deployment.yaml
```

Scaling does not trigger a new rollout because the pod template is unchanged. The existing ReplicaSet is scaled directly.

For automatic scaling, pair the Deployment with a HorizontalPodAutoscaler. When using an HPA, omit the `replicas` field from the Deployment manifest to avoid conflicts between the HPA controller and the declared replica count.

## Canary Deployment Pattern

Run a small percentage of traffic on a new version by using two Deployments that share a common label matched by a single Service.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: webapp
spec:
  selector:
    app: webapp          # matches both Deployments
  ports:
    - port: 80
      targetPort: 8080
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp-stable
spec:
  replicas: 9
  selector:
    matchLabels:
      app: webapp
      track: stable
  template:
    metadata:
      labels:
        app: webapp
        track: stable
    spec:
      containers:
        - name: webapp
          image: webapp:2.1.0
          ports:
            - containerPort: 8080
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp-canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: webapp
      track: canary
  template:
    metadata:
      labels:
        app: webapp
        track: canary
    spec:
      containers:
        - name: webapp
          image: webapp:2.2.0
          ports:
            - containerPort: 8080
```

The Service selects on `app: webapp`, which matches all 10 Pods. Roughly 10% of traffic goes to the canary. Adjust the ratio by changing the replica counts. Note that the Service selector must only include labels common to both Deployments (`app: webapp`), not the `track` label.

This approach gives coarse-grained traffic splitting. For percentage-based or header-based routing, use a service mesh such as Istio or Linkerd.

## Blue-Green Deployment Pattern

Maintain two full environments. Route traffic by switching the Service selector.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: webapp
      version: blue
  template:
    metadata:
      labels:
        app: webapp
        version: blue
    spec:
      containers:
        - name: webapp
          image: webapp:2.1.0
          ports:
            - containerPort: 8080
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: webapp
      version: green
  template:
    metadata:
      labels:
        app: webapp
        version: green
    spec:
      containers:
        - name: webapp
          image: webapp:2.2.0
          ports:
            - containerPort: 8080
```

The Service currently points to blue:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: webapp
spec:
  selector:
    app: webapp
    version: blue
  ports:
    - port: 80
      targetPort: 8080
```

Switch to green after validating the new version:

```bash
kubectl patch service webapp -p '{"spec":{"selector":{"version":"green"}}}'
```

Instant rollback is a `kubectl patch` back to blue. Once confident, scale down the old Deployment to free resources.

The trade-off is resource cost: both environments run simultaneously at full capacity during the transition.

## Common Troubleshooting

### ImagePullBackOff

The kubelet cannot pull the container image. Causes: image name or tag is wrong, the image does not exist in the registry, or image pull credentials are missing.

```bash
kubectl describe pod <pod-name>    # check Events section
kubectl get events --sort-by=.metadata.creationTimestamp
```

Fix: correct the image name, push the image to the registry, or create an `imagePullSecret` and reference it in the pod spec.

### CrashLoopBackOff

The container starts and exits repeatedly. The kubelet applies an exponential backoff delay (10s, 20s, 40s, up to 5 minutes) before restarting.

```bash
kubectl logs <pod-name> --previous   # logs from the last crashed container
kubectl describe pod <pod-name>      # check exit code and reason
```

Common causes: application error on startup, misconfigured command or args, missing environment variables or config files, failing liveness probe killing a healthy but slow-starting container (increase `initialDelaySeconds` or use a startup probe).

### Stuck Rollouts

A rollout can stall when new Pods never become ready. Symptoms: `kubectl rollout status` hangs, Pods are in Pending or CrashLoopBackOff, the Deployment's `Progressing` condition eventually shows `ProgressDeadlineExceeded`.

```bash
kubectl rollout status deployment/webapp   # shows waiting message
kubectl get rs -l app=webapp               # check which ReplicaSet is scaling
kubectl describe rs <new-replicaset>       # check events for scheduling failures
```

The Deployment controller does not automatically roll back a failed rollout. You must intervene:

```bash
kubectl rollout undo deployment/webapp
```

Common causes: insufficient cluster resources (Pending Pods), failing readiness probes, missing ConfigMaps or Secrets referenced in the pod spec.

### OOMKilled

The container exceeded its memory limit and was terminated by the kernel OOM killer. The Pod's status shows `OOMKilled` with exit code 137.

```bash
kubectl describe pod <pod-name>   # look for "OOMKilled" in Last State
kubectl top pod <pod-name>        # requires metrics-server
```

Fix: increase the container's memory limit, investigate the application for memory leaks, or tune JVM/runtime heap settings. Set requests equal to limits for memory to avoid overcommit-related OOM kills at the node level.
