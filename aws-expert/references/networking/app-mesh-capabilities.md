# AWS App Mesh — Capabilities Reference
For CLI commands, see [app-mesh-cli.md](app-mesh-cli.md).

## AWS App Mesh

**Purpose**: Service mesh providing application-level networking for microservices, enabling traffic control, observability, and security across services regardless of compute type.

### Core Concepts

| Concept | Description |
|---|---|
| **Mesh** | Top-level resource; logical boundary for a set of microservices |
| **Virtual service** | Abstract representation of a service; traffic destination in policies; backed by a virtual router or virtual node |
| **Virtual node** | Logical pointer to a specific microservice deployment (ECS service, Kubernetes deployment, EC2 fleet); has service discovery and listener configuration |
| **Virtual router** | Routes traffic to virtual nodes using rules (prefix-based, header-based, weighted) |
| **Virtual gateway** | Manages ingress traffic into the mesh from external sources |
| **Route** | Traffic routing rules on a virtual router: path, header, method matching with weighted targets |

### Envoy Proxy

- App Mesh uses **Envoy** as its data plane proxy; injected as a sidecar into each task/pod
- Intercepts all inbound and outbound traffic; enforces mesh configuration without code changes
- Emits **metrics** (to CloudWatch), **traces** (to X-Ray or Jaeger), and **access logs** to stdout

### Service Discovery Integration

| Method | Description |
|---|---|
| **AWS Cloud Map** | DNS or API-based discovery; recommended for ECS and EC2 |
| **DNS** | Standard DNS name resolution for virtual nodes |

### Key Features

- **Traffic shifting**: Weighted routing between virtual node versions for canary/blue-green deployments
- **Retry policies**: Automatic retry on specified HTTP status codes or gRPC status codes
- **Circuit breaker**: Outlier detection on virtual nodes to eject unhealthy hosts
- **mTLS**: Mutual TLS between services using ACM Private CA or local file-based certificates
- **Observability**: End-to-end tracing with X-Ray; Envoy stats exported to CloudWatch
