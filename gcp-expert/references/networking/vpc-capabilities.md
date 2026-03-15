# VPC — Capabilities Reference

## Purpose

Google Cloud VPC (Virtual Private Cloud) provides a global software-defined network for isolating and connecting GCP resources. Unlike AWS VPCs (which are regional), a GCP VPC network is a global resource — subnets are regional, but the VPC itself spans all regions. Resources in different regions within the same VPC can communicate using internal IPs without VPN or peering.

---

## Core Concepts

| Concept | Description |
|---|---|
| VPC network | A global resource defining the network namespace. Contains subnets, firewall rules, and routes. Each project has a default VPC (not recommended for production). |
| Subnet | A regional IPv4 (and optionally IPv6) CIDR range. VMs in a subnet get an IP from that range. Subnets span all zones within a region. |
| Firewall rule | Stateful packet filter applied to VMs based on tags, service accounts, or CIDR ranges. Applied to the VPC, not individual subnets. |
| Route | Determines next-hop for traffic from a VPC. Default routes: internet gateway (0.0.0.0/0) and inter-subnet routing within the VPC. |
| VPC peering | Connects two VPC networks (same or different projects/organizations). Traffic is exchanged using internal IPs. Peering is not transitive. |
| Shared VPC | A VPC in a host project shared with one or more service projects. Centralizes network management while allowing separate billing/IAM per project. |
| Private Google Access | Enables VMs without external IPs to reach Google APIs and services (storage.googleapis.com, etc.) using internal routing instead of the internet. |
| Alias IP range | Secondary IP ranges assigned to a VM's network interface. Used by GKE for pod IP addresses. |
| Internal IP | RFC 1918 IP address assigned from a subnet. Not routable on the internet. |
| External IP | Publicly routable IP address. Ephemeral (re-assigned on VM stop) or static (reserved, always yours). |
| Flow logs | Per-subnet logging of network flows (source/destination IP, port, protocol, bytes). Stored in Cloud Logging. Used for monitoring, security forensics, billing analysis. |
| Network tag | String label attached to a VM. Used in firewall rules to target specific instances. Multiple tags per VM. |
| Service account firewall rule | Firewall rules can target VMs running as a specific service account instead of using network tags. More secure than tags (service accounts cannot be self-applied). |

---

## VPC Architecture: Global vs. Regional Contrast

| Feature | GCP VPC | AWS VPC |
|---|---|---|
| Scope | Global (one VPC spans all regions) | Regional (separate VPC per region) |
| Subnets | Regional | Availability Zone-specific |
| Cross-region internal routing | Built-in — subnets in same VPC route internally | Requires VPC peering or Transit Gateway |
| Peering | Non-transitive | Non-transitive (TGW for hub-spoke) |
| IPv6 | Optional per-subnet | Optional per-subnet |

A single GCP VPC can have subnets in `us-central1`, `europe-west1`, and `asia-east1`. VMs in all three regions can communicate using internal IPs with no additional configuration.

---

## Subnet Modes

| Mode | Description | Recommendation |
|---|---|---|
| Auto mode | Automatically creates one `/20` subnet per region using predefined CIDR ranges (10.128.0.0/9). New regions get subnets automatically. | Use only for demos and exploration. NOT for production. |
| Custom mode | You define all subnets, CIDRs, and regions. No automatic subnets. | Required for production — gives full CIDR control. |

**Converting auto to custom**: A network can be converted from auto to custom mode (one-way; cannot revert).

---

## IP Address Management

### Primary Ranges

Each subnet has one primary IPv4 CIDR range. VMs get their primary internal IP from this range.

### Secondary Ranges

Subnets can have secondary IPv4 ranges. Used for:
- GKE Pod IPs (Alias IP mode)
- GKE Service IPs
- Additional IP addresses for VMs with Alias IPs

### IPv6

- Stack type per subnet: IPv4 only, or IPv4 + IPv6 (dual stack)
- IPv6 access type: Internal (ULA addresses, /64 per VM) or External (globally routable, /64 per VM)
- Required for IPv6 workloads; not enabled by default

---

## Firewall Rules

### Rule Properties

| Property | Values | Notes |
|---|---|---|
| Direction | INGRESS or EGRESS | Ingress = incoming to VM; Egress = outgoing from VM |
| Priority | 1–65535 | Lower number = higher priority. Default rules are at 65534 and 65535. |
| Action | ALLOW or DENY | Deny rules log if logging is enabled |
| Protocol/Port | tcp, udp, icmp, esp, ah, sctp, or all; specific ports e.g. tcp:80,443 | |
| Target | All instances, network tags, service account | Service account targets are more secure |
| Source (ingress) | CIDR ranges, network tags, service accounts | |
| Destination (egress) | CIDR ranges | |
| Logging | Enabled or disabled | Logs ingested into Cloud Logging |

### Default Firewall Rules (Default Network)

| Rule | Direction | Priority | Action | Description |
|---|---|---|---|---|
| default-allow-internal | Ingress | 65534 | Allow | All traffic between instances in VPC |
| default-allow-ssh | Ingress | 65534 | Allow | SSH (TCP:22) from 0.0.0.0/0 |
| default-allow-rdp | Ingress | 65534 | Allow | RDP (TCP:3389) from 0.0.0.0/0 |
| default-allow-icmp | Ingress | 65534 | Allow | ICMP from 0.0.0.0/0 |
| (implied) | Ingress | 65535 | Deny | All other ingress |
| (implied) | Egress | 65535 | Allow | All egress |

**For production custom VPCs**: Delete or do not create permissive default rules. Create explicit allow rules for required traffic only.

### Firewall Rule Best Practices

- Use service account targets instead of network tags for microservice-to-microservice rules.
- Enable firewall rule logging for security-critical rules (adds cost per logged flow).
- Use `deny` rules at high priority to block known-bad IP ranges before allow rules fire.
- Use the lowest-privilege principle: no rule should be broader than necessary.
- Avoid `--source-ranges=0.0.0.0/0` on production environments except for port 443 on web servers.

---

## VPC Peering

- Connects two VPC networks; VMs in each can communicate using internal IPs.
- Peering must be created from **both** sides (each VPC must initiate a peering to the other).
- **Not transitive**: if VPC-A peers with VPC-B and VPC-B peers with VPC-C, VPC-A cannot reach VPC-C through VPC-B.
- Custom static routes and dynamic routes are not automatically exported across peerings (unless explicitly configured).
- CIDR ranges in peered VPCs must not overlap.
- Use cases: separate-project microservices, connecting a third-party VPC (e.g., Cloud SQL private IP uses VPC peering internally).

---

## Shared VPC

### Architecture

- **Host project**: owns the VPC network and all subnets. Network Admin manages firewall rules, routes, subnets.
- **Service projects**: attached to the host project. VMs in service projects use subnets from the host VPC. Each service project manages its own resources (VMs, GKE clusters) but they run on the shared network.

### Benefits

- Centralized network management with delegated billing and IAM per project.
- Consistent firewall rules across all service projects.
- Single VPC enables all projects to use private IPs to communicate without peering.

### Shared VPC vs. VPC Peering

| Factor | Shared VPC | VPC Peering |
|---|---|---|
| Use case | Multiple teams sharing one corporate network | Connecting two separate networks |
| CIDR design | Centralized; subnets allocated per project/team | Each VPC has its own CIDR; no overlap allowed |
| Billing | VM charges in service projects; network in host | Each project pays for its own resources |
| Admin model | Organization Admin enables; Network Admin manages | Each VPC owner configures their side |
| Transitivity | All service projects can reach each other | Non-transitive |

---

## Private Google Access

Allows VMs without external IPs to access Google APIs and services (Cloud Storage, BigQuery, Pub/Sub, etc.) without routing traffic over the internet.

- Enabled per subnet: `--enable-private-ip-google-access`
- Traffic routes through Google's network internally (to 199.36.153.4/30 for `restricted.googleapis.com` or 199.36.153.8/30 for `private.googleapis.com`)
- **Private Google Access for on-prem**: on-premises hosts can reach Google APIs over Interconnect/VPN using DNS forwarding to `private.googleapis.com` or `restricted.googleapis.com`
- **VPC Service Controls**: use `restricted.googleapis.com` endpoint with VPC Service Controls to prevent data exfiltration to external Google services

---

## Routes

| Route Type | Description |
|---|---|
| System-generated subnet routes | Automatically created for each subnet; routes traffic within the VPC to the correct subnet |
| Default internet gateway route | `0.0.0.0/0` → default-internet-gateway; allows VMs with external IPs to reach the internet |
| Static routes | Manually created; custom next-hops (VPN tunnel, instance, IP address) |
| Dynamic routes (BGP) | Propagated by Cloud Router from VPN tunnels and Interconnect VLAN attachments |
| Policy-based routes | Route traffic based on protocol/port as well as destination (e.g., route all TCP:443 to a firewall appliance) |

---

## Flow Logs

VPC Flow Logs record network flows for all VMs in a subnet:
- **Log fields**: source/destination IP and port, protocol, bytes, packets, direction, start/end time, VM metadata, geographic info
- **Sampling rate**: configurable (0.5 default = 50% of flows sampled); reduce to lower cost
- **Aggregation interval**: 5s, 30s, 1m, 5m, 10m (longer interval = fewer log entries = lower cost)
- **Storage**: Cloud Logging (exported to BigQuery, GCS, or Pub/Sub for analysis)
- **Use cases**: network debugging, security analysis, compliance, billing analysis (egress cost breakdown)

---

## Important Constraints

- **Auto mode CIDR range**: auto mode VPCs use `10.128.0.0/9`. This conflicts with many on-premises RFC 1918 ranges. Always use custom mode for any VPC that will connect to on-premises.
- **Subnet CIDR cannot overlap**: subnets within the same VPC (or across peered VPCs) must have non-overlapping CIDR ranges. Plan carefully before deploying.
- **Firewall rules are stateful**: return traffic for allowed connections is automatically permitted. No need to create separate egress rules for responses to ingress traffic.
- **Maximum subnets per VPC**: 1000 secondary ranges per subnet; 7000 subnets per VPC.
- **VPC peering CIDR conflict**: peered VPCs must not have overlapping CIDR ranges (primary or secondary). This constraint makes ad-hoc peering difficult if CIDR ranges were not planned in advance.
- **Shared VPC requires Organization**: Shared VPC is only available in Google Cloud Organizations, not standalone projects.
- **No broadcast or multicast**: VPC does not support broadcast or multicast. Use Pub/Sub or unicast protocols for multi-consumer patterns.
