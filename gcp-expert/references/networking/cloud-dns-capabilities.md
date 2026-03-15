# Cloud DNS — Capabilities Reference

## Purpose

Cloud DNS is a scalable, high-availability managed DNS service built on Google's global Anycast network. It provides authoritative DNS for public internet domains and private DNS for internal GCP resources. Cloud DNS serves billions of DNS queries per day with low latency and 100% SLA for managed zones.

---

## Core Concepts

| Concept | Description |
|---|---|
| Managed zone | A container for DNS records corresponding to a DNS domain. Can be public (internet-facing) or private (VPC-internal). |
| Public zone | Authoritative DNS for an internet domain. Responses visible to any DNS client on the internet. |
| Private zone | DNS zone visible only within specified VPC networks. Internal service discovery and split-horizon DNS. |
| Record set | A group of DNS records with the same name and type. e.g., `www.example.com A 34.120.1.2, 34.120.1.3`. |
| DNS policy | Configures inbound DNS forwarding (allows on-premises resolvers to query Cloud DNS private zones) or outbound forwarding (forwards specific zones to on-premises resolvers). |
| Peering zone | A private zone that forwards queries to another VPC's private zone. Enables DNS resolution across peered or Shared VPC networks. |
| Response policy zone (RPZ) | Overrides DNS responses for specific FQDNs or wildcards within a VPC. Used to block, redirect, or rewrite specific DNS queries. |
| DNSSEC | DNS Security Extensions. Signs zone records cryptographically to prevent DNS spoofing and cache poisoning. |
| Cloud Domains | Domain registration service integrated with Cloud DNS. Register and manage domain names within GCP. |

---

## Managed Zone Types

### Public Zones

- Authoritative DNS for internet-facing domains.
- Accessible by any client on the internet.
- Example: managing `A`, `CNAME`, `MX`, `TXT` records for `example.com`.
- Requires updating NS records at your domain registrar to point to Cloud DNS nameservers.
- Google-assigned NS records: `ns-cloud-{a,b,c,d}1.googledomains.com`.

### Private Zones

- Visible only within specified VPC networks (configured at zone level).
- Used for:
  - Internal service discovery (`myservice.internal.example.com`)
  - Split-horizon DNS (same domain, different records internally vs. externally)
  - Cloud SQL, GKE, Memorystore internal endpoint naming
- A private zone can be associated with multiple VPCs across multiple projects.
- Resolution order: private zones take precedence over public DNS for clients in the VPC.

### Forwarding Zones

- A special private zone that forwards queries for a domain to specified DNS resolvers.
- Use for: forwarding queries for on-premises domains (e.g., `corp.example.com`) to on-premises DNS servers via Cloud VPN or Interconnect.
- Supports both forwarding to external resolvers and internal GCP resolver IPs.

### Peering Zones

- A private zone in VPC-A that delegates queries to another VPC's (VPC-B's) Cloud DNS private zones.
- Used when VPC-A needs to resolve records managed in VPC-B's private zone.
- Simpler than duplicating zone data: VPC-B owns the data; VPC-A delegates.
- Common in Shared VPC and hub-spoke architectures.

---

## Supported Record Types

| Type | Description | Example |
|---|---|---|
| A | IPv4 address | `www A 34.120.1.2` |
| AAAA | IPv6 address | `www AAAA 2001:db8::1` |
| CNAME | Canonical name (alias) | `api CNAME www.example.com.` |
| MX | Mail exchanger | `@ MX 10 mail.example.com.` |
| TXT | Text record (SPF, DKIM, verification) | `@ TXT "v=spf1 include:_spf.google.com ~all"` |
| SRV | Service locator | `_http._tcp SRV 0 5 80 www.example.com.` |
| NS | Name server delegation | `sub NS ns1.sub.example.com.` |
| SOA | Start of authority | Auto-managed by Cloud DNS |
| PTR | Reverse DNS | `2.1.120.34.in-addr.arpa PTR www.example.com.` |
| CAA | Certificate Authority Authorization | `@ CAA 0 issue "letsencrypt.org"` |
| ALIAS / ANAME | Apex CNAME workaround (Cloud DNS specific) | `@ A` with `--routing-policy` |
| DS | DNSSEC delegation signer | Auto-managed for DNSSEC |

---

## DNS Policies

DNS policies configure how Cloud DNS resolves queries within a VPC network.

### Inbound DNS Forwarding

Enables on-premises DNS resolvers (connected via Cloud VPN or Interconnect) to resolve Cloud DNS private zones:
- Cloud DNS creates forwarding IP addresses in each subnet of the VPC (accessible from on-premises via VPN/Interconnect).
- On-premises DNS servers forward queries for GCP-hosted domains to these inbound forwarder IPs.

### Outbound DNS Forwarding (Alternative DNS)

Configures an alternative DNS resolver for the VPC:
- By default, VMs use Google's internal metadata DNS resolver (`169.254.169.254`).
- With an outbound DNS policy, specific domains are forwarded to custom resolvers (e.g., on-premises DNS, custom resolver).
- Used for: resolving on-premises domain names from GCP VMs; custom DNS filtering.

---

## Response Policy Zones (RPZ)

RPZ allows overriding DNS responses for specific domains within a VPC:
- Define rules for FQDNs or wildcards.
- Actions: `passThrough` (no override), `localData` (return custom records), `behavior: do_not_resolve` (return NXDOMAIN).
- Use cases: block malware domains, redirect internal service endpoints, override third-party DNS for testing.

---

## DNSSEC

DNSSEC adds cryptographic signatures to DNS records to prevent:
- DNS spoofing (returning fake records)
- Cache poisoning attacks

### DNSSEC Key Types

| Key Type | Description |
|---|---|
| Key Signing Key (KSK) | Signs the DNSKEY record set. Typically uploaded to the parent zone (registrar) as a DS record. |
| Zone Signing Key (ZSK) | Signs all other records in the zone. Rotated more frequently than KSK. |

### DNSSEC Workflow

1. Activate DNSSEC on the Cloud DNS zone → Cloud DNS generates KSK and ZSK
2. Retrieve the DS record (hash of the KSK public key)
3. Add the DS record to the parent zone (registrar or parent DNS) — this establishes the chain of trust
4. DNSSEC is now active; clients can validate signatures

---

## Cloud Domains

Cloud Domains provides domain registration integrated with GCP:
- Register domain names and automatically configure Cloud DNS nameservers.
- Manage WHOIS information, DNSSEC, domain transfers within GCP Console.
- Supported TLDs: `.com`, `.net`, `.org`, `.io`, `.dev`, `.app`, and many more.
- Billing via GCP billing account.

---

## Private DNS in GCP Architecture

### Split-Horizon DNS

Same domain name, different records inside vs. outside the VPC:
- Public zone: `api.example.com A 34.120.5.10` (public load balancer IP)
- Private zone: `api.example.com A 10.10.0.5` (internal load balancer IP)
- VMs inside the VPC query the private zone and get the internal IP.
- External clients get the public IP.

### Automatic Private DNS for GCP Services

GCP services automatically create DNS entries in a private zone associated with the VPC:
- Cloud SQL: `IP_ADDRESS` is the private IP — add DNS manually or use the connection name.
- GKE: cluster DNS via CoreDNS within the cluster.
- Memorystore: private IP, add your own DNS record.
- Cloud Run: `*.run.app` (public), internal services use Serverless VPC Access + DNS.

---

## Important Constraints

- **CNAME at zone apex not supported**: You cannot use a CNAME for the root domain (`@`) in a standard zone. Use Load Balancer static IP + A record instead.
- **TTL minimums**: Cloud DNS enforces a minimum TTL of 0 seconds (you can set TTL to 0, but most resolvers will still cache briefly).
- **Zone transfer**: Cloud DNS does not support traditional AXFR zone transfers. Use the API/CLI to export records.
- **Private zone resolution order**: If multiple private zones match a query (e.g., `example.com` and `api.example.com`), the most specific zone wins.
- **100% SLA**: Cloud DNS provides a 100% uptime SLA for managed zone queries.
- **Record limits**: Default 10,000 resource record sets per zone; can be increased via quota request.
- **DNSSEC and non-DNSSEC**: Enabling DNSSEC on an existing zone has a propagation delay. Plan for this during migrations.
