# AWS Route 53 — Capabilities Reference
For CLI commands, see [route53-cli.md](route53-cli.md).

## Amazon Route 53

**Purpose**: Highly available and scalable DNS web service for domain registration, DNS routing, and health checking.

### Hosted Zones

| Type | Description |
|---|---|
| **Public hosted zone** | Serves DNS queries from the internet; used for publicly accessible domains |
| **Private hosted zone** | Serves DNS queries only within associated VPCs; supports split-horizon DNS |

**Private hosted zone DNS resolution**: Requires `enableDnsHostnames` and `enableDnsSupport` set to `true` on associated VPCs.

### Record Types

| Record | Description |
|---|---|
| **A** | Maps name to IPv4 address(es) |
| **AAAA** | Maps name to IPv6 address(es) |
| **CNAME** | Alias for another domain name; cannot be used at zone apex |
| **ALIAS** | Route 53-specific; maps a name to an AWS resource (ALB, CloudFront, S3 static website, etc.); can be used at zone apex; no extra charge for queries |
| **MX** | Mail exchange records; specifies mail servers and priority |
| **TXT** | Text data; used for SPF, DKIM, domain verification |
| **NS** | Name server records; identifies authoritative DNS servers for the zone |
| **SOA** | Start of authority; administrative information about the zone |
| **SRV** | Service location; specifies host, port, priority, weight |
| **CAA** | Certification Authority Authorization; specifies which CAs may issue certs for the domain |
| **PTR** | Reverse DNS lookup; maps IP to domain |

### Routing Policies

| Policy | Description | Use case |
|---|---|---|
| **Simple** | Returns one or more values; no health check evaluation per value | Single resource; no routing logic needed |
| **Weighted** | Distributes traffic by assigned weight (0–255) | Blue/green deployments, A/B testing, gradual traffic shifts |
| **Latency-based** | Routes to the region with lowest measured latency for the user | Multi-region deployments for best performance |
| **Failover** | Active-passive failover; routes to primary unless health check fails | DR setups; always-on primary with standby |
| **Geolocation** | Routes based on user's geographic location (continent, country, subdivision) | Serve localized content; compliance/regulatory routing |
| **Geoproximity** | Routes based on geographic location of users and resources; bias value expands/shrinks region coverage | Fine-tuned global traffic distribution; requires Traffic Flow |
| **Multivalue answer** | Returns up to 8 healthy records; client-side load balancing | Simple load balancing with health check filtering |
| **IP-based** | Routes based on the client's IP CIDR range | Route ISP or office traffic to specific endpoints |

### Health Checks

| Type | Description |
|---|---|
| **Endpoint health check** | HTTP, HTTPS, or TCP check against an IP or domain; check interval 10s or 30s |
| **Calculated health check** | Aggregates multiple health checks (AND/OR logic); monitors a parent record |
| **CloudWatch alarm health check** | Monitors the state of a CloudWatch alarm |

Health checks can trigger **SNS notifications** and are used in Failover and other routing policies to remove unhealthy endpoints.

### Route 53 Resolver

| Component | Description |
|---|---|
| **Default resolver** | VPC+2 IP; resolves AWS internal DNS and public DNS for VPC resources |
| **Inbound endpoint** | ENIs in your VPC that accept DNS queries forwarded from on-premises DNS servers into Route 53 |
| **Outbound endpoint** | ENIs in your VPC that forward DNS queries from VPC to on-premises DNS servers |
| **Forwarding rule** | Associates a domain name (e.g., `corp.example.com`) with target IP addresses; applied to VPCs |
| **System rule** | Handles resolution for Route 53 private hosted zones and AWS internal domains; cannot be deleted |
| **Resolver DNS Firewall** | Block or allow outbound DNS queries based on domain lists; protects against DNS-based data exfiltration and C2 callback domains |

### Route 53 Resolver DNS Firewall

**Purpose**: Filter DNS queries made by resources in your VPCs. Block known-malicious domains, allow only approved domains, or alert on suspicious queries — without requiring any agents or changes to applications.

#### Core Concepts

| Concept | Description |
|---|---|
| **Rule group** | Container for DNS Firewall rules; associated with one or more VPCs; evaluated in priority order |
| **Rule** | Matches DNS query names against a domain list; action is `BLOCK`, `ALERT`, or `ALLOW` |
| **Domain list** | Ordered set of domain name patterns (exact match or wildcard `*.example.com`); can be AWS-managed or custom |
| **AWS-managed domain lists** | Pre-built lists maintained by AWS: `AWSManagedDomainsMalwareDomainList`, `AWSManagedDomainsAggregateThreatList`, `AWSManagedDomainsBotnetCommandandControl`, etc. |
| **BLOCK action** | Returns NODATA or NXDOMAIN to the querying resource; optionally return a custom override domain (CNAME redirect) |
| **ALERT action** | Logs the query match to CloudWatch Logs/Firewall logs without blocking |
| **ALLOW action** | Explicitly allow a domain list; useful for carve-outs within a broader BLOCK rule |
| **Fail-open / Fail-closed** | Controls behavior if the firewall is unavailable: `ALLOW` (fail-open, default) lets queries through; `BLOCK` (fail-closed) drops all DNS |

#### Evaluation Order

Rules within a rule group are evaluated by ascending priority (lower number = higher priority). First matching rule wins. Multiple rule groups associated with the same VPC are evaluated in the order they were associated.

```
VPC DNS query (port 53 to VPC+2)
  → Rule group (priority 1 association)
      Rule priority 100: ALLOW list (corporate approved domains)
      Rule priority 200: BLOCK list (AWS Managed Malware list) → NODATA
      Rule priority 300: BLOCK list (custom blocked domains) → NXDOMAIN
  → Rule group (priority 2 association)
      ...
  → Default: ALLOW (if no rule matched)
```

#### Key Features

- **Managed domain lists**: AWS continuously updates threat intelligence lists — no maintenance required
- **Custom domain lists**: Up to 100,000 domains per list; supports wildcard patterns (`*.evil.example`)
- **Override response**: BLOCK rules can return a custom CNAME so internal monitoring can handle requests that would otherwise go to malicious domains
- **Firewall logs**: DNS Firewall query logs flow through Route 53 Resolver query logging (CloudWatch Logs or S3)
- **RAM sharing**: Rule groups can be shared across accounts via AWS Resource Access Manager, enabling centralized security team management
- **No agent required**: Applies to all DNS traffic from VPC resources automatically (uses VPC+2 resolver)

#### Additional Features

| Feature | Description |
|---|---|
| **DNSSEC** | Signs records in public hosted zones; validate with KMS asymmetric key; protect against DNS spoofing |
| **Domain registration** | Register and transfer domains; supports 400+ TLDs; integrated with Route 53 DNS automatically |
| **Route 53 Profiles** | Share DNS configurations (private hosted zones, resolver rules) across multiple VPCs and accounts |
| **Traffic Flow** | Visual policy editor for complex routing; supports versioning and rollback |
| **Query logging** | Log DNS queries to CloudWatch Logs or S3 for security analysis |
