# Chapter 9: Deployment and Day-2 Operations

## Rolling Updates

Zero-downtime updates with Kubernetes rolling deployment strategy:

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0      # never take pods down before new ones are ready
      maxSurge: 1            # one extra pod during rollout
```

Readiness probes gate traffic — Kubernetes will not route to a pod until `/health/ready` returns UP, preventing requests from hitting an uninitialized service.

```bash
# Trigger a rolling update
kubectl set image deployment/portfolio portfolio=registry.example.com/portfolio:2.0
kubectl rollout status deployment/portfolio

# Roll back if something is wrong
kubectl rollout undo deployment/portfolio
```

---

## Configuration Updates Without Redeployment

### Updating a ConfigMap

```bash
kubectl create configmap portfolio-config \
  --from-literal=loyalty.gold.threshold=60000 \
  --dry-run=client -o yaml | kubectl apply -f -
```

If the application uses `Provider<T>` injection (not field injection), the new value is picked up on the next invocation without restart:

```java
@Inject
@ConfigProperty(name = "loyalty.gold.threshold")
private Provider<Double> goldThreshold;  // re-read each time .get() is called
```

For field-injected values, a pod restart is required after ConfigMap changes.

---

## Logging and Diagnostics

### Structured JSON Logging (Open Liberty)

Configure in `server.xml`:

```xml
<logging messageFormat="json"
         messageSource="message,trace,accessLog,ffdc,audit"
         traceSpecification="com.example.*=fine"/>
```

JSON log output integrates with Elasticsearch / Kibana (ELK stack) or OpenShift Logging.

### Log Levels

```properties
# microprofile-config.properties or env vars
com.example.PortfolioService=FINE
```

Or in `server.xml`:

```xml
<logging traceSpecification="com.example.portfolio.*=finest:*=info"/>
```

### Open Liberty Request Timing

```xml
<requestTiming slowRequestThreshold="10s"
               hungRequestThreshold="60s"
               sampleRate="1"/>
```

Logs a warning when requests exceed the slow threshold and a thread dump when hung.

---

## Scaling

### Manual Scaling

```bash
kubectl scale deployment portfolio --replicas=5
```

### Autoscaling (HPA)

Requires metrics-server in the cluster:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: portfolio-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: portfolio
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Pods
      pods:
        metric:
          name: portfolio_active_count   # custom MicroProfile metric
        target:
          type: AverageValue
          averageValue: 100
```

---

## Resource Management

Always set both `requests` (scheduling guarantee) and `limits` (runtime cap):

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "1000m"
```

Open Liberty JVM heap sizing — use environment variable rather than hard-coding in `server.xml`:

```yaml
env:
  - name: JVM_ARGS
    value: "-Xmx384m -Xms64m"
```

Or with Open Liberty's `jvmOptions.options` file in the server config directory.

---

## Health Check Tuning for Operations

### Graceful Shutdown

During pod termination, Kubernetes sends SIGTERM then waits `terminationGracePeriodSeconds` before SIGKILL. Open Liberty handles SIGTERM by stopping the HTTP endpoint and draining in-flight requests.

```yaml
spec:
  terminationGracePeriodSeconds: 60
```

### Pre-Stop Hook

Add a sleep to let the load balancer drain connections before Liberty begins shutdown:

```yaml
lifecycle:
  preStop:
    exec:
      command: ["/bin/sh", "-c", "sleep 5"]
```

---

## OpenShift-Specific Operations

### ImageStream and DeploymentConfig

OpenShift can trigger automatic redeployment when a new image is pushed to the registry:

```yaml
triggers:
  - type: ImageChange
    imageChangeParams:
      automatic: true
      containerNames: ["portfolio"]
      from:
        kind: ImageStreamTag
        name: portfolio:latest
```

### Routes (OpenShift Ingress equivalent)

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: portfolio-route
spec:
  to:
    kind: Service
    name: portfolio
  port:
    targetPort: 9080
  tls:
    termination: edge
```

---

## Monitoring in Production

- **Prometheus**: scrape `/metrics` on each pod. Add annotation to enable auto-discovery:
  ```yaml
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "9080"
    prometheus.io/path: "/metrics"
  ```
- **Grafana**: dashboard the MicroProfile Metrics — request rate, error rate, latency percentiles
- **Jaeger**: view distributed traces across Stock Trader services
- **Alerting**: Prometheus alerting rules on circuit breaker open events, error rate spikes, pod restarts
