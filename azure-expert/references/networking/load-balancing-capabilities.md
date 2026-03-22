# Azure Load Balancing — Capabilities

## Service Selection Decision Matrix

Choose the right load balancing service based on traffic type, scope, and requirements:

| Requirement | Recommended Service |
|---|---|
| HTTP/HTTPS with WAF globally | Azure Front Door |
| HTTP/HTTPS regionally with WAF | Application Gateway |
| Non-HTTP TCP/UDP within region | Azure Load Balancer |
| Global DNS-based routing | Traffic Manager |
| HTTP + non-HTTP global | Front Door + Load Balancer |
| L7 path-based routing, regional | Application Gateway |
| Backend health-based global failover | Traffic Manager |

### Key Differentiators

| | Azure Load Balancer | Application Gateway | Traffic Manager | Azure Front Door |
|---|---|---|---|---|
| Layer | L4 (Transport) | L7 (Application) | DNS (L4 effectively) | L7 (Application) |
| Scope | Regional | Regional | Global | Global |
| Protocol | TCP, UDP | HTTP, HTTPS, WebSocket | Any | HTTP, HTTPS |
| WAF | No | Yes (WAF v2) | No | Yes |
| TLS Termination | No | Yes | No | Yes |
| Sticky Sessions | Yes (IP hash) | Yes (cookie) | No | Yes (cookie/hash) |
| Path-based routing | No | Yes | No | Yes |

---

## Azure Load Balancer (L4)

### SKUs

| Feature | Basic | Standard |
|---|---|---|
| Availability | No SLA | 99.99% SLA |
| Backend pool | 300 VMs | 1,000 instances |
| Health probes | HTTP, TCP | HTTP, HTTPS, TCP |
| Secure by default | No (open) | Yes (NSG required) |
| Availability Zones | No | Yes (zone-redundant) |
| Outbound rules | No | Yes |
| HTTPS probes | No | Yes |
| HA ports | No | Yes |
| Multi-VNet backend | No | Yes (IP-based pools) |

**Always use Standard SKU for production workloads.** Basic SKU is being retired.

### Frontend IP Configurations

- **External Load Balancer**: public IP frontend; routes inbound internet traffic to backend
- **Internal Load Balancer**: private IP frontend within a VNet; for internal service-to-service routing (e.g., SQL Always On, multi-tier apps)
- A single Load Balancer can have multiple frontend IP configurations

### Backend Pools

- **NIC-based**: associate VM network interfaces directly (same VNet required)
- **IP-based**: specify private/public IPs without NIC association; supports VMs in different VNets, on-premises IPs (cross-region)
- VMSS (Virtual Machine Scale Sets): dynamically managed as instances scale

### Health Probes

Probes test backend availability to route traffic only to healthy instances:

| Probe Type | Details |
|---|---|
| TCP | Connects to port; success = connection established |
| HTTP | GET request; success = HTTP 200 |
| HTTPS | Encrypted GET; success = HTTP 200 (Standard SKU only) |

- Probe interval: 5–15 seconds (default 15s)
- Unhealthy threshold: 2 failures (default)
- Source IP: `168.63.129.16` — must be allowed in NSGs

### Load Balancing Rules

- Maps frontend IP:port to backend pool:port
- Distribution modes: **5-tuple hash** (default: source IP, source port, dest IP, dest port, protocol) or **Source IP affinity** (2-tuple or 3-tuple for session stickiness)
- **Session persistence**: None (default), Client IP, Client IP and Protocol
- **Floating IP**: enables Direct Server Return (DSR) for NVA and SQL AlwaysOn scenarios; backend must configure the frontend IP on loopback

### HA Ports Rule (NVA Use Case)

- Protocol: All, Port: 0 (matches all ports and protocols)
- Standard SKU only; used on **internal load balancers** for NVA (Network Virtual Appliance) scenarios
- Eliminates need for per-port rules when NVA must inspect all traffic

### Inbound NAT Rules

- Maps a specific frontend IP:port to a specific backend VM port
- Supports port ranges (NAT rule → VM pool) for SSH/RDP access to VMSS instances
- Individual NAT rules: single VM targeting
- NAT rule sets: backend pool with port ranges (port offset per instance)

### Outbound Rules (SNAT)

- Define explicit outbound SNAT for backend pool VMs that need internet egress
- Allocate SNAT ports per instance (default: auto; explicit: up to 64,512 per public IP)
- Outbound rules and load balancing rules for same frontend are **mutually exclusive** (use separate frontend IPs)
- **Recommendation**: prefer NAT Gateway over Load Balancer outbound rules for SNAT at scale

### Cross-Region Load Balancer

- Global Standard Load Balancer that distributes traffic across regional Load Balancers
- Provides global failover for non-HTTP workloads (L4 TCP/UDP)
- Backend pools reference regional Standard Load Balancers
- Anycast-like behavior using Anycast IP; traffic routed to nearest healthy region

---

## Application Gateway (L7)

### SKUs

- **Standard v2**: autoscaling, zone redundancy, static VIP, private link
- **WAF v2**: Standard v2 + Web Application Firewall (always use WAF v2 for internet-facing apps)
- Basic: small workloads, no zone redundancy (preview)

**Always use v2 SKUs; v1 is being retired.**

### Core Components

| Component | Description |
|---|---|
| Frontend IP | Public and/or private IP; public = internet-facing, private = internal |
| Listener | Port + protocol (HTTP/HTTPS); Basic (catch-all) or Multi-site (hostname-based) |
| Backend Pool | VMs, VMSS, App Service, IP addresses, FQDNs |
| HTTP Settings | Backend protocol, port, cookie affinity, connection drain, probe, timeout |
| Routing Rule | Maps listener → backend pool via HTTP settings |
| Health Probe | Custom probe path, interval, match conditions |
| URL Path Map | Path-based routing (`/images/*` → pool1, `/api/*` → pool2) |
| Rewrite Rule Set | Modify request/response headers and URLs |

### SSL/TLS

- **SSL Termination**: TLS terminates at App Gateway; backend receives HTTP (or HTTP/2)
- **SSL Offload**: synonymous with termination; reduces backend CPU
- **End-to-End SSL**: re-encrypt traffic from App Gateway to backend using backend cert
- **SSL Policy**: choose minimum TLS version (1.2 recommended), cipher suites
- Supports wildcard and multi-SAN certificates; integrate with Key Vault for cert management

### Web Application Firewall (WAF v2)

- **Detection mode**: logs threats, does not block (use for initial testing)
- **Prevention mode**: blocks requests matching rules (production configuration)
- **Managed Rule Sets**:
  - `OWASP_3.2` (default), `OWASP_3.1`, `OWASP_3.0` — OWASP Top 10 protection
  - `Microsoft_DefaultRuleSet_2.1` — Microsoft managed rules
  - `Microsoft_BotManagerRuleSet_1.0` — bot protection
- **Custom Rules**: own match conditions (IP ranges, geo, headers, URI, query strings) with allow/block/log action
- WAF Policies: standalone resource, can be associated to App Gateway or specific listeners/URI paths
- Exclusions: exclude specific request elements (header, cookie, query arg) from evaluation

### Routing Features

- **URL Path-Based Routing**: different backend pools per URL path; define URL path maps
- **Multi-Site Hosting**: multiple FQDNs on one App Gateway using host header matching; up to 100 listeners
- **Redirects**: HTTP → HTTPS, path redirect, external URL redirect (301/302)
- **URL Rewrite**: modify request/response headers and URL path/query string using conditions
- **HTTP/2**: supported on frontend (client-to-gateway); backend always HTTP/1.1
- **WebSocket**: full WebSocket support

### Autoscaling and Zones

- Min/max instance count; scales based on traffic (0 min instances for cost saving in dev)
- Zone-redundant: spread across availability zones for 99.99% SLA
- Static VIP: public IP doesn't change even during gateway scaling

### Private Link

- Expose App Gateway as a Private Link Service to allow Private Endpoint access from other VNets or subscriptions
- Use case: internal API platform accessed by partner tenants without public internet exposure

---

## Traffic Manager

DNS-based global load balancing. Clients resolve the Traffic Manager FQDN and receive the IP of a selected endpoint. Traffic Manager itself does not sit in the data path — only DNS.

### Routing Methods

| Method | Description | Use Case |
|---|---|---|
| Priority | Active/standby; route to primary unless down | DR failover |
| Weighted | Distribute traffic by weight (1–1000) | A/B testing, gradual migration |
| Performance | Route to lowest-latency endpoint based on client location | Global latency optimization |
| Geographic | Route by client DNS source region | Data sovereignty, regional content |
| Subnet | Route by client IP subnet range | Specific network → specific endpoint |
| MultiValue | Return multiple healthy endpoints; client chooses | High availability for IPv4/IPv6 |

### Endpoint Types

- **Azure endpoints**: Azure resources (App Service, Cloud Service, Public IP, Traffic Manager profile)
- **External endpoints**: non-Azure IPs or FQDNs (on-premises, other clouds)
- **Nested profiles**: Traffic Manager profile as endpoint of another profile; combine routing methods (e.g., Priority + Performance)

### Health Monitoring

- Protocol: HTTP, HTTPS, TCP
- Path: `/` by default; configure a custom health check path (e.g., `/health`)
- Interval: 30s (normal), 10s (fast — requires Standard or higher)
- Tolerations: probing from multiple regions; endpoint degraded when threshold failed

### Key Characteristics and Limitations

- DNS TTL: 60 seconds by default (minimum 0 for testing); clients may cache longer
- **Not a proxy**: no WAF, no TLS offload, no header inspection
- Works with any internet-accessible endpoint
- Real User Measurements (RUM): browser-based latency data for Performance routing
- Traffic View: visualization of traffic patterns and latency by geography
