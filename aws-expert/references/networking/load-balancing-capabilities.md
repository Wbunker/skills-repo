# AWS Load Balancing — Capabilities Reference
For CLI commands, see [load-balancing-cli.md](load-balancing-cli.md).

## Elastic Load Balancing

**Purpose**: Automatically distribute incoming traffic across multiple targets in one or more Availability Zones with integrated health checking.

### Load Balancer Types

| Type | Layer | Key Characteristics |
|---|---|---|
| **ALB (Application Load Balancer)** | L7 (HTTP/HTTPS) | Content-based routing; ideal for microservices, container workloads, HTTP APIs |
| **NLB (Network Load Balancer)** | L4 (TCP/UDP/TLS) | Ultra-low latency; static IPs per AZ; preserves source IP; supports PrivateLink |
| **GWLB (Gateway Load Balancer)** | L3 (IP packets) | Inline traffic inspection via third-party appliances; bump-in-the-wire pattern |
| **CLB (Classic Load Balancer)** | L4/L7 | Legacy; migration to ALB/NLB recommended |

### Application Load Balancer (ALB)

| Concept | Description |
|---|---|
| **Listener** | Accepts incoming connections on a port/protocol (HTTP:80, HTTPS:443); evaluates rules in priority order |
| **Listener rule** | Conditions + action; conditions include host header, path pattern, HTTP method, query string, HTTP header, source IP |
| **Target group** | Group of targets (EC2, ECS, Lambda, IP) with a health check; routing algorithm: Round Robin (default) or Least Outstanding Requests |
| **Sticky sessions** | Duration-based (load balancer cookie) or application-based (custom cookie); routes user to the same target for the session |
| **Authentication** | Authenticate users via Amazon Cognito User Pools or any OIDC-compatible IdP directly at the ALB (Action type: `authenticate-cognito` or `authenticate-oidc`) |
| **gRPC** | Supported as a target group protocol; routes gRPC traffic to appropriate microservices |
| **Weighted target groups** | A single listener rule can distribute traffic across multiple target groups with weights (blue/green deployments) |
| **Deregistration delay** | Time to wait (default 300s) before deregistering a target so in-flight requests complete (connection draining) |
| **Access logs** | Detailed request logs to S3; include client IP, timestamp, target IP, processing time, status codes; disabled by default |

### Network Load Balancer (NLB)

| Concept | Description |
|---|---|
| **Static IPs** | One static IP per AZ (or Elastic IP); ideal for firewall whitelisting |
| **Source IP preservation** | Client source IP visible to targets by default (unlike ALB) |
| **TLS passthrough** | TCP listener passes TLS to targets without termination; target handles TLS |
| **TLS termination** | NLB terminates TLS and forwards decrypted traffic (requires ACM cert) |
| **Ultra-low latency** | Designed for millions of requests per second with single-digit millisecond latency |
| **PrivateLink support** | NLB is the required load balancer type for creating VPC endpoint services (PrivateLink) |
| **Cross-zone load balancing** | Off by default for NLB (unlike ALB where it's on by default); incurs data transfer charges when enabled |

### Gateway Load Balancer (GWLB)

- Operates at Layer 3 (IP packet level); does not modify IP headers
- Distributes traffic to a fleet of virtual appliances (firewalls, IDS/IPS, deep packet inspection)
- **Bump-in-the-wire pattern**: Traffic enters GWLB endpoint (in a VPC route table), is sent to appliances, inspected, and returned; uses GENEVE encapsulation (port 6081)
- Appliances must support GENEVE protocol
- GWLB endpoints are created in consumer VPCs; GWLB itself lives in the appliance provider VPC

### Health Checks

All load balancer types support health checks. ALB supports HTTP/HTTPS health checks with customizable path and expected response codes. NLB supports TCP, HTTP, HTTPS health checks.
