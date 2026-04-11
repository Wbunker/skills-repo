---
name: bind-dns-expert
description: BIND DNS expertise covering DNS fundamentals, zone configuration, BIND setup and maintenance, mail routing, subdomain delegation, DNSSEC/TSIG security, BIND 9 features, and troubleshooting. Use when configuring name servers, writing zone files, debugging DNS resolution, setting up DNSSEC, delegating subdomains, troubleshooting lookup failures, or administering BIND. Based on "DNS and BIND, 5th Edition" by Cricket Liu (O'Reilly, 2006).
---

# BIND DNS Expert

Based on "DNS and BIND, 5th Edition" by Cricket Liu (O'Reilly, 2006).

## DNS Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    DNS HIERARCHY                             │
│                                                             │
│                        . (root)                             │
│                   /    |    \                               │
│                .com  .net  .org  ... (TLDs)                │
│               /    \                                        │
│          example  acme  ...  (second-level domains)        │
│          /     \                                            │
│        www    mail  (hostnames / subdomains)                │
│                                                             │
│  RESOLUTION FLOW:                                           │
│  Resolver → Recursive NS → Root → TLD → Auth NS → Answer  │
└─────────────────────────────────────────────────────────────┘
```

## Quick Reference

| Task | Reference |
|------|-----------|
| DNS concepts, hierarchy, zones, resource records, resolution | [foundations.md](references/foundations.md) |
| Installing BIND, named.conf, zone files, primary/secondary setup | [configuration.md](references/configuration.md) |
| MX records, mail routing, resolv.conf, nsswitch.conf | [mail-and-hosts.md](references/mail-and-hosts.md) |
| rndc, logging, statistics, reloading, monitoring | [maintenance.md](references/maintenance.md) |
| Subdomains, delegation, load distribution, large-scale DNS | [domain-management.md](references/domain-management.md) |
| TSIG, DNSSEC, views, ACLs, response policy zones | [security-advanced.md](references/security-advanced.md) |
| BIND 9 specifics: forwarders, views, RPZ, catalog zones | [bind9-features.md](references/bind9-features.md) |
| dig, nslookup, debug output, troubleshooting common failures | [troubleshooting.md](references/troubleshooting.md) |

## Reference Files

| File | Chapters | Topics |
|------|----------|--------|
| `foundations.md` | 1–2 | DNS history, namespace hierarchy, zones, name server types, resolution process, all resource record types |
| `configuration.md` | 3–4 | BIND installation, named.conf structure, zone file syntax, primary and secondary server setup, hints file |
| `mail-and-hosts.md` | 5–6 | MX records, mail routing, wildcard MX, resolv.conf options, nsswitch.conf, host.conf |
| `maintenance.md` | 7 | rndc commands, syslog/named logging, statistics, zone transfers, dynamic updates, BIND lifecycle |
| `domain-management.md` | 8–9 | Subdomains vs. delegation, NS/glue records, round-robin load distribution, large-scale architecture |
| `security-advanced.md` | 10 | TSIG key-based authentication, DNSSEC signing and validation, views, ACLs, RPZ |
| `bind9-features.md` | 11 | BIND 9 architecture, named.conf BIND 9 options, forwarders, views, catalog zones, rate limiting |
| `troubleshooting.md` | 12–14 | dig/nslookup command reference, reading debug output, common failure patterns and fixes |

## Core Decision Trees

### What do you need to do?

```
DNS task?
├── Understand how DNS works → foundations.md
│   ├── Resolution process, caching, TTLs
│   ├── Zone vs. domain distinction
│   └── Resource record types (A, AAAA, CNAME, MX, NS, SOA, PTR, SRV...)
├── Set up a name server → configuration.md
│   ├── New primary (authoritative) server
│   ├── Secondary / slave server
│   └── Caching-only resolver
├── Configure email (MX) → mail-and-hosts.md
│   ├── Basic MX records
│   ├── Backup mail servers (priority)
│   └── Wildcard MX for subdomains
├── Configure clients → mail-and-hosts.md
│   ├── resolv.conf (search, nameserver, options)
│   └── nsswitch.conf (resolution order)
├── Manage running BIND → maintenance.md
│   ├── Reload zones, freeze/thaw
│   ├── rndc commands
│   └── Log analysis
├── Grow / restructure domain → domain-management.md
│   ├── Create a subdomain
│   ├── Delegate to child zone
│   └── Load balancing with round-robin
├── Secure DNS → security-advanced.md
│   ├── Restrict zone transfers (ACLs)
│   ├── Sign zone with DNSSEC
│   ├── TSIG for server-to-server auth
│   └── Split DNS with views
└── Debug a problem → troubleshooting.md
    ├── dig / nslookup queries
    ├── Reading BIND debug output
    └── Common failure diagnosis
```

### Is this a zone or a domain?

```
Term clarification:
├── Domain = administrative boundary (example.com and all descendants)
├── Zone = portion of namespace a server is authoritative for
│   ├── A domain with no delegated subdomains = one zone
│   └── Delegated subdomain = separate zone with its own SOA
└── One domain can span multiple zones (after delegation)
```

## Key Concepts

### SOA Record — The Zone's Identity Card

```
example.com.  IN  SOA  ns1.example.com.  hostmaster.example.com. (
    2024010101  ; Serial (YYYYMMDDnn)
    3600        ; Refresh — how often secondaries check for updates
    900         ; Retry — how often secondary retries after failure
    604800      ; Expire — how long secondary serves without refresh
    300         ; Negative TTL — how long NXDOMAIN is cached
)
```

### Name Server Types

| Type | Role |
|------|------|
| **Primary (master)** | Reads zone data from disk; single source of truth |
| **Secondary (slave)** | Loads zone via AXFR from primary; automatic failover |
| **Caching-only** | No authoritative data; caches recursive query results |
| **Forwarder** | Passes queries to another resolver instead of going recursive |
| **Stealth/hidden primary** | Authoritative but not listed in NS records; secondaries are public-facing |

### TTL Strategy

```
Record type          Recommended TTL
─────────────────────────────────────
SOA negative TTL     300–3600s (5 min–1 hr)
NS records           86400s (24 hr)
A/AAAA (stable)      3600–86400s
A/AAAA (changing)    300–600s (before change), raise after
MX records           3600–86400s
CNAME                3600s
TXT/SPF              3600s
```
