# AWS App Mesh — Capabilities Reference
For CLI commands, see [app-mesh-cli.md](app-mesh-cli.md).

## AWS App Mesh

**Purpose**: Service mesh providing application-level networking for services running on ECS, EKS, and EC2; standardizes service-to-service communication with traffic control, retries, and observability via Envoy proxies.

> **Note**: AWS will end support for App Mesh on September 30, 2026. For new workloads, prefer ECS Service Connect (for ECS) or a Kubernetes-native service mesh.

### Key Concepts

| Concept | Description |
|---|---|
| **Mesh** | Top-level resource; logical boundary for the service network; name becomes the DNS suffix |
| **Virtual node** | Logical pointer to an actual service (ECS service, Kubernetes deployment, EC2 instances); has a service discovery config (DNS or Cloud Map) and listener(s) |
| **Virtual service** | Abstract named service (e.g., `payments.svc.cluster.local`); backed by a virtual node (direct) or virtual router (with routing rules) |
| **Virtual router** | Receives traffic for a virtual service and applies routing rules to distribute it to virtual nodes |
| **Route** | Rule on a virtual router; supports weighted targets (canary/blue-green), HTTP/gRPC header matching, path matching, retry policies, timeout policies |
| **Virtual gateway** | Ingress point into the mesh from outside; backed by an Envoy Gateway proxy deployment |
| **Gateway route** | Routing rule on a virtual gateway; directs inbound traffic to virtual services |
| **Envoy proxy** | Sidecar container in each task/pod; reads App Mesh config from the control plane; intercepts all inbound and outbound traffic |

### Envoy Sidecar Injection

- **ECS**: Add the Envoy container to the task definition manually; set `APPMESH_VIRTUAL_NODE_NAME` environment variable
- **Kubernetes**: Use the App Mesh Controller for Kubernetes (Helm chart); enables automatic sidecar injection via mutating admission webhook

### Service Discovery Integration

| Option | Description |
|---|---|
| **AWS Cloud Map** | Virtual node uses Cloud Map namespace + service name; App Mesh resolves via Cloud Map API |
| **DNS** | Virtual node uses a DNS hostname; Envoy resolves via VPC DNS |

### Observability

| Feature | Description |
|---|---|
| **Metrics** | Envoy emits Prometheus-compatible metrics; configure export to CloudWatch via ADOT or CloudWatch agent |
| **Traces** | Envoy emits trace data; configure backend to AWS X-Ray or Jaeger |
| **Access logs** | Configure Envoy access log path in virtual node; collect via CloudWatch Logs or FireLens |

### Traffic Control Patterns

- **Weighted routing**: Split traffic between virtual nodes (e.g., 90% stable / 10% canary) on a route
- **Retry policy**: Automatically retry on specific HTTP status codes or gRPC status codes
- **Timeout policy**: Set per-request and per-retry timeouts on routes
- **Circuit breaker**: Configure outlier detection on virtual nodes to eject unhealthy hosts
