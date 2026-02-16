# Pods: Running Containers in Kubernetes

A Pod is the smallest deployable unit in Kubernetes. It represents a single instance of a running process and encapsulates one or more containers that share networking (same IP, localhost communication) and storage. Every container in Kubernetes runs inside a Pod.

## Pod Spec Fundamentals

The Pod spec defines the desired state of a Pod. The top-level fields control scheduling, networking, volumes, and the containers themselves.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
  namespace: default
  labels:
    app: myapp
    version: v1
spec:
  restartPolicy: Always
  dnsPolicy: ClusterFirst
  serviceAccountName: default
  terminationGracePeriodSeconds: 30
  nodeSelector:
    disktype: ssd
  containers:
    - name: app
      image: myapp:1.0
  volumes:
    - name: data
      emptyDir: {}
```

### `restartPolicy`

Applies to all containers in the Pod. Possible values:

| Policy | Behavior |
|---|---|
| `Always` | Restart containers regardless of exit code. Default for Pods managed by controllers (Deployments, etc.). |
| `OnFailure` | Restart only if the container exits with a non-zero code. Common for Jobs. |
| `Never` | Never restart. The Pod eventually reaches a terminal phase. Common for one-shot Jobs. |

Restarts use exponential backoff: 10s, 20s, 40s, capped at 5 minutes. The backoff resets after 10 minutes of successful running.

### `dnsPolicy`

Controls how DNS resolution is configured inside Pod containers.

| Policy | Behavior |
|---|---|
| `ClusterFirst` | Default. Queries go to the cluster DNS service (CoreDNS). Falls back to upstream if not resolved. |
| `Default` | Inherits DNS config from the node the Pod runs on. |
| `ClusterFirstWithHostNet` | Use when `hostNetwork: true` but you still want cluster DNS. |
| `None` | Ignores all Kubernetes DNS settings. Requires `dnsConfig` to supply nameservers manually. |

```yaml
spec:
  dnsPolicy: None
  dnsConfig:
    nameservers:
      - 8.8.8.8
    searches:
      - my.dns.search.suffix
    options:
      - name: ndots
        value: "2"
```

### `volumes`

Volumes are declared at the Pod level and mounted into containers via `volumeMounts`. Common volume types:

```yaml
spec:
  volumes:
    - name: scratch
      emptyDir: {}                    # ephemeral, deleted with Pod
    - name: config
      configMap:
        name: app-config              # project ConfigMap keys as files
    - name: creds
      secret:
        secretName: app-secret        # project Secret keys as files
    - name: persistent
      persistentVolumeClaim:
        claimName: data-pvc           # bind to a PVC
    - name: host-path
      hostPath:
        path: /var/log/app
        type: DirectoryOrCreate
```

## Container Spec

Each entry in `spec.containers` defines a single container within the Pod.

```yaml
containers:
  - name: app
    image: registry.example.com/myapp:1.2.3
    imagePullPolicy: IfNotPresent
    command: ["/bin/sh"]
    args: ["-c", "echo hello && exec myapp --port=8080"]
    workingDir: /app
    env:
      - name: APP_ENV
        value: "production"
      - name: DB_PASSWORD
        valueFrom:
          secretKeyRef:
            name: db-creds
            key: password
      - name: POD_NAME
        valueFrom:
          fieldRef:
            fieldPath: metadata.name
      - name: CPU_LIMIT
        valueFrom:
          resourceFieldRef:
            resource: limits.cpu
    envFrom:
      - configMapRef:
          name: app-env-config
    ports:
      - name: http
        containerPort: 8080
        protocol: TCP
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 500m
        memory: 256Mi
    volumeMounts:
      - name: scratch
        mountPath: /tmp/data
      - name: config
        mountPath: /etc/app/config
        readOnly: true
      - name: creds
        mountPath: /etc/app/secrets
        readOnly: true
```

### `command` and `args`

These override the container image's `ENTRYPOINT` and `CMD`:

| Dockerfile | Pod spec | What runs |
|---|---|---|
| `ENTRYPOINT ["/app"]`, `CMD ["--help"]` | neither set | `/app --help` |
| `ENTRYPOINT ["/app"]`, `CMD ["--help"]` | `args: ["--version"]` | `/app --version` |
| `ENTRYPOINT ["/app"]` | `command: ["/bin/sh"]` | `/bin/sh` |
| any | `command: ["/bin/sh"]`, `args: ["-c", "echo hi"]` | `/bin/sh -c "echo hi"` |

Key rule: `command` replaces `ENTRYPOINT`. `args` replaces `CMD`. If only `args` is set, the image's `ENTRYPOINT` is preserved.

### Image Pull Policies

| Policy | Behavior |
|---|---|
| `IfNotPresent` | Pull only if the image is not already cached on the node. Default when a tag other than `:latest` is specified. |
| `Always` | Always contact the registry (but may use cached layers). Default when tag is `:latest` or omitted. |
| `Never` | Never pull. The image must already exist on the node. |

Best practice: always use a specific image tag or digest, never rely on `:latest` in production.

### `ports`

Declaring `containerPort` is informational and documentary. It does not actually open or restrict ports. However, named ports can be referenced by Services and probes.

## Pod Lifecycle

A Pod transitions through a series of phases recorded in `status.phase`:

```
Pending --> Running --> Succeeded
                   \--> Failed
```

| Phase | Meaning |
|---|---|
| `Pending` | Pod accepted but one or more containers not yet running. Includes time spent scheduling, pulling images, and running init containers. |
| `Running` | Pod bound to a node and at least one container is running or starting/restarting. |
| `Succeeded` | All containers terminated with exit code 0 and will not restart. Terminal state. |
| `Failed` | All containers terminated and at least one exited with a non-zero code. Terminal state. |
| `Unknown` | Pod state cannot be determined, typically due to node communication failure. |

### Container States

Each container within a Pod has its own state, reported in `status.containerStatuses[].state`:

- **Waiting** -- container is not yet running (pulling image, blocked by init container, CrashLoopBackOff). The `reason` field gives specifics.
- **Running** -- container is executing. `startedAt` records the time.
- **Terminated** -- container finished execution. `exitCode`, `reason`, `startedAt`, `finishedAt` are available.

Check states with:

```
kubectl get pod myapp -o jsonpath='{.status.containerStatuses[*].state}'
```

### Pod Conditions

`status.conditions` provides more granular status. Key condition types:

| Condition | Meaning |
|---|---|
| `PodScheduled` | Pod has been assigned to a node. |
| `Initialized` | All init containers completed successfully. |
| `ContainersReady` | All containers in the Pod are ready. |
| `Ready` | Pod is ready to serve traffic. Gates Services and endpoints. |

## Probes

Probes let the kubelet monitor container health. There are three probe types, each using one of four probe mechanisms.

### Probe Types

**Startup probe** -- Runs first. Until it succeeds, liveness and readiness probes are disabled. Use for containers with slow initialization. If it fails beyond `failureThreshold`, the container is killed and subject to `restartPolicy`.

**Liveness probe** -- Checks if the container is alive. If it fails, the kubelet kills the container and applies `restartPolicy`. Use to detect deadlocks or unrecoverable states.

**Readiness probe** -- Checks if the container is ready to accept traffic. If it fails, the Pod's IP is removed from Service endpoints. The container is NOT restarted. Use when a container needs to load data or wait for dependencies.

### Probe Mechanisms

```yaml
containers:
  - name: app
    image: myapp:1.0

    startupProbe:
      httpGet:
        path: /healthz
        port: 8080
      failureThreshold: 30
      periodSeconds: 10          # gives up to 300s to start

    livenessProbe:
      httpGet:
        path: /healthz
        port: http               # named port reference
        httpHeaders:
          - name: X-Custom-Header
            value: LivenessCheck
      initialDelaySeconds: 0
      periodSeconds: 10
      timeoutSeconds: 1
      failureThreshold: 3
      successThreshold: 1

    readinessProbe:
      tcpSocket:
        port: 8080
      periodSeconds: 5
      failureThreshold: 3
```

The four mechanisms:

```yaml
# HTTP GET -- success is any status 200-399
httpGet:
  path: /ready
  port: 8080
  scheme: HTTPS                  # optional, default HTTP

# TCP Socket -- success if the port is open
tcpSocket:
  port: 3306

# Exec -- success if the command exits 0
exec:
  command:
    - cat
    - /tmp/healthy

# gRPC -- success if the gRPC health check returns SERVING
grpc:
  port: 50051
  service: my.package.MyService  # optional, defaults to ""
```

### Probe Configuration Fields

| Field | Default | Description |
|---|---|---|
| `initialDelaySeconds` | 0 | Seconds to wait after container start before probing. Prefer `startupProbe` over large delay values. |
| `periodSeconds` | 10 | How often to probe. |
| `timeoutSeconds` | 1 | Seconds before the probe times out. |
| `successThreshold` | 1 | Consecutive successes needed. Must be 1 for liveness and startup. |
| `failureThreshold` | 3 | Consecutive failures before taking action. |

## Resource Requests and Limits

Resource management controls how the scheduler places Pods and how the kubelet enforces constraints.

```yaml
resources:
  requests:
    cpu: 250m         # 0.25 cores -- used for scheduling
    memory: 64Mi      # used for scheduling
  limits:
    cpu: 500m         # throttled (not killed) if exceeded
    memory: 128Mi     # OOMKilled if exceeded
```

**CPU** is compressible. When a container exceeds its CPU limit, it is throttled (given less CPU time), not terminated. CPU is measured in millicores: `1000m` = 1 full core.

**Memory** is incompressible. When a container exceeds its memory limit, it is OOMKilled by the kernel. Memory is measured in bytes with suffixes: `Ki`, `Mi`, `Gi` (powers of 1024) or `k`, `M`, `G` (powers of 1000).

Requests affect scheduling: the scheduler only places the Pod on a node that has enough allocatable resources to satisfy the sum of all container requests in the Pod. Limits enforce runtime boundaries.

### QoS Classes

Kubernetes assigns a Quality of Service class to each Pod based on its resource declarations. The QoS class determines eviction priority under node memory pressure.

**Guaranteed** -- Highest priority. Every container in the Pod sets both `requests` and `limits` for CPU and memory, and they are equal.

```yaml
resources:
  requests:
    cpu: 500m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 256Mi
```

**Burstable** -- At least one container has a request or limit set, but the Pod does not qualify for Guaranteed.

```yaml
resources:
  requests:
    cpu: 100m
    memory: 64Mi
  # no limits, or limits differ from requests
```

**BestEffort** -- Lowest priority, evicted first. No container in the Pod specifies any resource requests or limits.

```yaml
resources: {}    # or omit entirely
```

Eviction order under pressure: BestEffort first, then Burstable (sorted by usage relative to request), then Guaranteed last.

## Security Context

Security context configures privilege and access control at the Pod and container level.

```yaml
spec:
  securityContext:                  # Pod-level: applies to all containers
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000                  # group applied to mounted volumes
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: app
      image: myapp:1.0
      securityContext:             # container-level: overrides Pod-level
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL
          add:
            - NET_BIND_SERVICE
```

Key fields:

| Field | Scope | Description |
|---|---|---|
| `runAsNonRoot` | Pod/Container | Kubelet validates the container does not run as UID 0. |
| `runAsUser` | Pod/Container | UID to run the container process. |
| `runAsGroup` | Pod/Container | Primary GID for the container process. |
| `fsGroup` | Pod | GID applied to all volumes mounted in the Pod. Files created will be owned by this group. |
| `readOnlyRootFilesystem` | Container | Mount the root filesystem as read-only. Forces explicit volume usage for writes. |
| `allowPrivilegeEscalation` | Container | Controls whether a process can gain more privileges than its parent. Set `false` for defense in depth. |
| `capabilities` | Container | Fine-grained Linux capability control. Drop `ALL` and add back only what is needed. |

## Multi-Container Pods

Multiple containers in a single Pod share the network namespace (same IP, communicate over `localhost`) and can share volumes. This enables several well-known patterns.

### Init Containers

Init containers run sequentially before any app container starts. Each must complete successfully (exit 0) before the next one begins. If an init container fails, the kubelet retries it according to `restartPolicy`.

Use cases: waiting for a dependency, populating a shared volume, running database migrations, fetching configuration.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  initContainers:
    - name: wait-for-db
      image: busybox:1.36
      command:
        - sh
        - -c
        - |
          until nc -z db-service 5432; do
            echo "waiting for database..."
            sleep 2
          done
    - name: init-schema
      image: myapp-migrations:1.0
      command: ["./migrate", "--up"]
      env:
        - name: DB_HOST
          value: db-service
  containers:
    - name: app
      image: myapp:1.0
```

Init containers:
- Always run to completion (they do not have probes).
- Run in the order declared, one at a time.
- Must all succeed before the Pod moves to `Running` phase.
- Resource requests/limits are handled separately (the effective Pod request is the max of init container requests vs. the sum of app container requests).

### Sidecar Pattern

A sidecar container extends or enhances the main container without modifying it. The sidecar runs for the entire lifetime of the Pod alongside the main container.

Common use cases: log collection, monitoring agents, service mesh proxies.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-with-logging
spec:
  containers:
    - name: web
      image: nginx:1.25
      volumeMounts:
        - name: logs
          mountPath: /var/log/nginx
    - name: log-shipper
      image: fluentbit:2.1
      volumeMounts:
        - name: logs
          mountPath: /var/log/nginx
          readOnly: true
        - name: fluentbit-config
          mountPath: /fluent-bit/etc
      resources:
        requests:
          cpu: 50m
          memory: 32Mi
        limits:
          cpu: 100m
          memory: 64Mi
  volumes:
    - name: logs
      emptyDir: {}
    - name: fluentbit-config
      configMap:
        name: fluentbit-config
```

Since Kubernetes 1.28, native sidecar containers can be declared as init containers with `restartPolicy: Always`. These start before app containers, run for the Pod's lifetime, and are properly terminated during shutdown:

```yaml
spec:
  initContainers:
    - name: istio-proxy
      image: istio/proxyv2:1.20
      restartPolicy: Always         # makes this a native sidecar
      ports:
        - containerPort: 15090
      resources:
        requests:
          cpu: 100m
          memory: 128Mi
  containers:
    - name: app
      image: myapp:1.0
```

### Ambassador Pattern

An ambassador container proxies network connections from the main container to external services. The app connects to `localhost` and the ambassador handles discovery, routing, or protocol translation.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-ambassador
spec:
  containers:
    - name: app
      image: myapp:1.0
      env:
        - name: REDIS_HOST
          value: "localhost"        # talks to ambassador on localhost
        - name: REDIS_PORT
          value: "6379"
    - name: redis-ambassador
      image: malexer/twemproxy:latest
      ports:
        - containerPort: 6379
      volumeMounts:
        - name: config
          mountPath: /etc/twemproxy
  volumes:
    - name: config
      configMap:
        name: twemproxy-config
```

The app only knows about localhost:6379. The ambassador handles connection pooling and routing to the actual Redis cluster.

### Adapter Pattern

An adapter container transforms the output of the main container into a format expected by an external consumer. The main container writes its native output; the adapter reads, transforms, and exposes it.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-adapter
spec:
  containers:
    - name: app
      image: legacy-app:2.0
      volumeMounts:
        - name: logs
          mountPath: /var/log/app
    - name: log-adapter
      image: log-transformer:1.0
      command:
        - /adapter
        - --input=/var/log/app/output.log
        - --format=json
        - --listen=:9090
      ports:
        - name: metrics
          containerPort: 9090
      volumeMounts:
        - name: logs
          mountPath: /var/log/app
          readOnly: true
  volumes:
    - name: logs
      emptyDir: {}
```

A common real-world adapter converts application-specific metrics or logs into a standard format (Prometheus exposition format, structured JSON).

## Pod DNS

Every Pod in the cluster gets a DNS entry. The cluster DNS service (CoreDNS) provides resolution.

### Service DNS

Services get a DNS A record: `<service-name>.<namespace>.svc.cluster.local`. This is the primary mechanism for service discovery.

### Pod DNS

Pods get a DNS A record based on their IP (dashes replace dots): `10-244-1-5.<namespace>.pod.cluster.local`. This is rarely used directly.

### Search Domains

By default (`dnsPolicy: ClusterFirst`), containers are configured with search domains so short names resolve:

```
search <namespace>.svc.cluster.local svc.cluster.local cluster.local
```

This means a Pod in namespace `prod` can resolve:
- `myservice` resolves to `myservice.prod.svc.cluster.local`
- `myservice.other-ns` resolves to `myservice.other-ns.svc.cluster.local`

### `hostname` and `subdomain`

Setting `hostname` and `subdomain` on a Pod creates a more predictable DNS entry when paired with a headless Service:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-0
spec:
  hostname: myapp-0
  subdomain: myapp-headless        # must match a headless Service name
  containers:
    - name: app
      image: myapp:1.0
---
apiVersion: v1
kind: Service
metadata:
  name: myapp-headless
spec:
  clusterIP: None
  selector:
    app: myapp
  ports:
    - port: 8080
```

This creates the DNS record: `myapp-0.myapp-headless.<namespace>.svc.cluster.local`.

### `ndots` and DNS Performance

The default `ndots` value is 5, meaning any name with fewer than 5 dots is treated as a relative name and appended with each search domain before trying it as-is. For external names like `api.example.com` (2 dots), this causes up to 4 failed lookups before the final absolute query succeeds.

Mitigation strategies:
- Use FQDNs with a trailing dot in application config: `api.example.com.`
- Reduce `ndots` in the Pod's `dnsConfig` if external lookups dominate.

```yaml
spec:
  dnsConfig:
    options:
      - name: ndots
        value: "2"
```
