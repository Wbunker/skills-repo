# Advanced Networking — Capabilities Reference

This file covers Cloud NAT, Private Service Connect, Service Directory, Traffic Director, and Network Intelligence Center.

---

## Cloud NAT

### Purpose

Cloud NAT (Network Address Translation) provides managed source NAT for GCE VMs, GKE nodes, and Cloud Run instances that do not have external IP addresses. It allows these resources to initiate outbound connections to the internet without having a public IP, while keeping them unreachable from the internet (no inbound NAT).

### Architecture

- Cloud NAT is a software-defined service — there is no NAT VM or single point of failure.
- Implemented at the hypervisor level; each VM's outbound packets are translated directly.
- Cloud NAT is **regional**: one NAT configuration per region per VPC.
- Cloud NAT is configured on a Cloud Router.
- Multiple VMs share NAT IP addresses using port allocation.

### Key Concepts

| Concept | Description |
|---|---|
| NAT IP addresses | External IPs used for NAT. Auto-allocated (ephemeral from Google's pool) or static (reserved IPs you manage). |
| Minimum ports per VM | Number of ports reserved per VM NIC for NAT. Default: 64. Increase if hitting connection limits. Each port = one concurrent connection. |
| Port allocation | Static (fixed ports per VM) or dynamic (ports allocated on demand up to max-ports-per-vm). |
| Max ports per VM | Upper bound for dynamic allocation. Default: 65536. |
| Subnet selection | NAT all subnets in the region, or specific subnets (and specific primary/secondary ranges). |
| Logging | Log NAT translations (ERRORS_ONLY or ALL) to Cloud Logging. |
| Endpoint-independent mapping | When enabled, the same (external IP, port) is reused for outbound connections from the same VM to different external destinations — required for some peer-to-peer protocols. |

### Use Cases

- VMs in private subnets (no external IP) that need to download packages, call external APIs, access the internet
- GKE pods (alias IP addresses) behind NAT for internet access
- Cloud Run instances connecting to external services (via Serverless VPC Access + Cloud NAT)

### Limitations

- Inbound connections are NOT supported — Cloud NAT is egress-only
- Does not NAT traffic to other GCP resources via private IP (only internet-bound traffic)
- Does not NAT traffic to Google APIs via Private Google Access

---

## Private Service Connect (PSC)

### Purpose

Private Service Connect enables private, VPC-internal access to:
1. **Google APIs** (Cloud Storage, BigQuery, Pub/Sub, etc.) without internet or VPC peering
2. **Third-party managed services** (databases, SaaS APIs published as PSC services)
3. **Your own services** published as PSC producer services (consumer-producer model)

No VPC peering, no internet gateway, no proxy — traffic stays within Google's network on a private endpoint.

### PSC Endpoint for Google APIs

- Create a PSC endpoint (forwarding rule with a private IP in your VPC).
- DNS entry maps `storage.googleapis.com` to the private IP (you configure this in Cloud DNS).
- Traffic to Google APIs routes through the PSC endpoint — stays in your VPC and Google's private network.
- Two PSC endpoint bundles:
  - `all-apis`: all Google APIs
  - `vpc-sc`: only APIs that support VPC Service Controls (stricter, for data exfiltration prevention)

### PSC Consumer-Producer Model (Custom Services)

A service producer publishes a service as a **service attachment**:
- Producer creates an internal load balancer backend
- Producer creates a service attachment referencing the ILB frontend
- Service attachment has a PSC endpoint URL

A service consumer creates a PSC endpoint pointing to the producer's service attachment:
- Consumer creates a forwarding rule with a private IP in their VPC
- Consumer connects to the service using the private IP — traffic never leaves Google's network
- No VPC peering, no IP range overlap issues

**Use cases**: Managed database services, API providers, SaaS companies publishing GCP services, cross-organization private connectivity.

### PSC vs. VPC Peering

| Factor | VPC Peering | Private Service Connect |
|---|---|---|
| CIDR overlap | Not allowed | Allowed — no CIDR visibility between VPCs |
| Transitivity | Not transitive | Consumer → producer (one direction) |
| Route visibility | Subnets visible to both peers | No route exchange; one private IP per endpoint |
| Scale | Limited by CIDR design | One endpoint per service; no peering limits |
| Use case | Full network connectivity between VPCs | Targeted service-level connectivity |

---

## Service Directory

### Purpose

Service Directory is a managed service registry for storing, managing, and querying service endpoints. It provides a centralized place to register services (name, protocol, endpoints) so clients can discover them without hardcoding IPs or hostnames.

### Core Concepts

| Concept | Description |
|---|---|
| Namespace | A logical grouping of services in a project and region. e.g., `production`, `staging`. |
| Service | A named service within a namespace. e.g., `payments-api`, `user-service`. |
| Endpoint | An IP:port pair associated with a service. Each service can have multiple endpoints. Endpoints have metadata (key-value annotations). |

### Integration

- **Cloud DNS**: Automatically creates DNS entries for services in Service Directory. Clients can resolve `service.namespace.googleapis.com` to get the service's IP.
- **Cloud Load Balancing**: Backends in a load balancer can be sourced from Service Directory services.
- **Traffic Director**: Uses Service Directory as the service registry.
- **GKE**: GKE services can be registered in Service Directory automatically.

### Use Cases

- Service discovery for microservices without hard-coded configs
- Centralized endpoint management for hybrid (on-prem + cloud) services
- Health-aware endpoint tracking (mark unhealthy endpoints; clients discover only healthy ones)

---

## Traffic Director

### Purpose

Traffic Director is Google Cloud's fully managed service mesh control plane. It provides advanced traffic management for microservices using the xDS API (Envoy's management API). Applications use Envoy sidecars or proxyless gRPC libraries to receive configuration from Traffic Director.

### Core Capabilities

| Capability | Description |
|---|---|
| Load balancing | Weighted round-robin, ring hash, least request, random |
| Traffic splitting | Canary deployments (send X% to v2, 100-X% to v1) |
| Circuit breaking | Stop sending traffic to unhealthy backends beyond a threshold |
| Retry policy | Automatic retries on specified HTTP status codes |
| Fault injection | Inject latency or errors for chaos engineering |
| Traffic mirroring | Send copy of production traffic to a shadow service |
| Header matching | Route based on HTTP headers (user-agent, x-canary, etc.) |
| Timeout policy | Per-route timeouts |
| Health checking | Service-level health checks (not just TCP-level) |

### Deployment Models

| Model | Description |
|---|---|
| Envoy sidecar | Envoy proxy runs alongside each service; Traffic Director configures Envoy via xDS |
| Proxyless gRPC | gRPC services use the xDS protocol directly without a sidecar proxy; lighter weight |
| GKE integration | Automatic Envoy injection for GKE pods; Traffic Director as control plane |

### Traffic Director vs. Istio

| Factor | Traffic Director | Istio |
|---|---|---|
| Management | Fully managed by Google | Self-managed (Istio control plane) |
| Data plane | Envoy or proxyless gRPC | Envoy (mandatory) |
| Integration | GCP-native (IAM, Cloud Monitoring, Service Directory) | Kubernetes-native |
| Scope | Multi-cluster, cross-region | Single cluster by default (multi-cluster possible) |

---

## Network Intelligence Center

Network Intelligence Center is Google Cloud's network monitoring and observability platform. It provides diagnostic and visibility tools for understanding GCP network topology and troubleshooting connectivity issues.

### Components

#### Network Topology

- Visualizes the network topology of your VPC, including VM instances, subnets, load balancers, VPN tunnels, Interconnect connections.
- Shows traffic volumes between nodes.
- Helps identify misconfigured routes or unexpected traffic patterns.

#### Connectivity Tests

- Reachability analysis tool: given a source and destination (VM, IP address, load balancer, Cloud SQL, GKE pod), determines whether traffic can flow and traces the path.
- Simulates the packet's path through firewall rules, routes, and forwarding rules.
- Identifies blockers (firewall rule denying traffic, route missing, incorrect NAT config).
- Does NOT send actual packets — purely configuration-based analysis.

#### Performance Dashboard

- Shows packet loss and latency metrics between Google Cloud regions and between zones.
- Identifies degraded network performance before it impacts applications.
- Data sourced from Google's internal network monitoring.

#### Firewall Insights

- Analyzes firewall rule usage over a time period.
- Identifies overly permissive rules (allow rules with zero hits).
- Identifies shadowed rules (rules that are always overridden by higher-priority rules).
- Identifies rules with shadow deny (deny rules blocking certain allow rules).
- Provides recommendations for hardening firewall configuration.

#### Network Analyzer

- Automated analysis of network configuration.
- Checks for common misconfigurations: missing firewall rules, BGP route flapping, Interconnect link failures, Cloud NAT port exhaustion, GKE node connectivity issues.
- Surfaces findings in Cloud Monitoring and Security Command Center.

---

## Important Constraints

### Cloud NAT

- **Egress only**: No inbound NAT. Use a load balancer or VM with external IP for inbound connections.
- **Port exhaustion**: If too many concurrent connections are established, VMs may fail to open new connections. Increase `--min-ports-per-vm` or use dynamic allocation.
- **SNAT for all outbound internet**: All traffic from NAT-protected VMs appears to come from the NAT IP(s). External services will see the NAT IP, not the VM IP. This affects IP-based allowlisting at destinations.
- **Static NAT IPs**: Use static IPs when external services allowlist by IP. Dynamic (auto-allocated) IPs can change.

### Private Service Connect

- **Per-service endpoint**: One PSC endpoint per service. For multiple services, create multiple endpoints.
- **Consumer DNS management**: Consumers must configure DNS to resolve service names to PSC endpoint IPs — Cloud DNS private zones recommended.
- **One-directional**: Consumers can reach producers; producers cannot initiate connections back to consumers (unless separate endpoint created).

### Connectivity Tests

- **Configuration-based only**: Connectivity Tests analyze firewall rules, routes, and GCP resources. They do not send actual packets. If a firewall rule allows traffic but a host-level firewall (iptables) blocks it, Connectivity Tests will report "reachable" but packets will actually be blocked.
