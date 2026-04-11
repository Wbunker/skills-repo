# BIND 9 Features
## Chapter 11: BIND 9 Architecture, named.conf Options, Forwarders, Views, Catalog Zones, Rate Limiting

---

## BIND 9 Architecture

BIND 9 was a complete rewrite of BIND 8, introducing:
- Multi-threading (configurable task system)
- Pluggable modules (DLZ, SDB)
- Full DNSSEC implementation
- IPv6 support
- View support (split DNS)
- TSIG
- IXFR (incremental zone transfers)
- EDNS0 support
- `rndc` replaces `ndc` for control

### Process Model

BIND 9 uses a single multi-threaded process (`named`) with:
- A task management system (event-driven)
- I/O subsystem for network and file operations
- Separate threads for different work types (query processing, zone transfers, signing)

Check active threads:
```bash
rndc status           # Shows task count
rndc stats            # Detailed per-thread statistics
```

---

## named.conf: BIND 9 Specific Options

### Global Options (BIND 9 additions beyond BIND 8)

```
options {
    // ── Resolver behavior ──────────────────────────────
    dnssec-validation auto;         // Validate DNSSEC (auto = use built-in root trust anchor)
    dnssec-lookaside no;            // DLV is deprecated; set no (BIND 9.11+)
    managed-keys-directory "/var/named/dynamic";  // Store auto-managed trust anchors

    // ── Query handling ─────────────────────────────────
    minimal-responses yes;          // Don't send unsolicited additional section
    qname-minimization strict;      // RFC 7816 privacy: minimize qname in referrals
    empty-zones-enable yes;         // RFC 1918 and similar: answer authoritatively for these
    auth-nxdomain no;               // RFC 2308: don't set AA on NXDOMAIN (default BIND 9.4+)

    // ── Performance ────────────────────────────────────
    max-cache-size 256m;            // Limit cache size
    max-cache-ttl 86400;            // Cap TTL of cached records
    max-ncache-ttl 3600;            // Cap negative cache TTL
    recursive-clients 1000;         // Max simultaneous recursive queries
    tcp-clients 150;                // Max simultaneous TCP connections

    // ── Transfers ──────────────────────────────────────
    transfers-in 10;                // Max simultaneous inbound zone transfers
    transfers-out 10;               // Max outbound
    transfers-per-ns 2;             // Max transfers per remote server

    // ── Logging shorthand ──────────────────────────────
    querylog no;                    // Disable query logging unless rndc querylog on
};
```

### EDNS Options

```
options {
    edns-udp-size 4096;             // EDNS0 UDP buffer size advertised to clients
    max-udp-size 4096;              // Max UDP response size
    // Limit for specific servers with broken EDNS:
    // server 1.2.3.4 { edns no; };
};
```

---

## Forwarders and Forwarding

### Forward All Queries

Route all recursive queries through an upstream resolver:

```
options {
    forwarders { 8.8.8.8; 8.8.4.4; };
    forward only;     // Don't try to resolve recursively if forwarders fail
    // OR:
    // forward first;  // Try forwarders; fall back to recursive if forwarders fail/refuse
};
```

**Use cases:**
- Organization must route all DNS through a central proxy/filter
- Firewall blocks outbound port 53 except to specific servers
- Caching all queries at a central point (RPZ, logging)

### Per-Zone Forwarding

Override forwarding for specific zones — useful for internal domains that the upstream resolver won't know:

```
zone "internal.example.com" {
    type forward;
    forwarders { 10.0.0.1; 10.0.0.2; };   // Internal DNS servers
    forward only;
};

zone "example.com" {
    type forward;
    forwarders { 8.8.8.8; };
    forward first;
};
```

### Conditional Forwarding Pattern

Split-brain DNS via type forward zones + views:

```
view "internal" {
    match-clients { 10.0.0.0/8; };
    // Internal clients resolve internal.example.com locally
    zone "internal.example.com" {
        type master;
        file "internal.example.com.zone";
    };
    // Forward everything else to corporate resolver
    zone "." {
        type forward;
        forwarders { 10.0.0.1; };
    };
};
```

---

## Views (BIND 9)

See also [security-advanced.md](security-advanced.md) for split-DNS configuration.

### Match Conditions

Views can match on:
- `match-clients` — source IP of the query
- `match-destinations` — destination IP (server's interface the query arrived on)
- `match-recursive-only` — only match recursive queries

```
view "on-vpn" {
    match-clients { key vpn-client-key; };   // Match by TSIG key
    // Trusted VPN clients get internal view
};

view "via-interface-eth1" {
    match-destinations { 10.0.0.1; };        // Match by destination IP
};
```

### View Inheritance

Options set in a view override global options for that view. Zone-level options override view options.

Order of precedence: **zone options > view options > global options**

### All Zones in Views

Once you use views, **all** zone declarations must be inside views — including localhost and root hints:

```
view "internal" {
    match-clients { 10.0.0.0/8; };
    zone "." { type hint; file "named.ca"; };
    zone "localhost" { type master; file "localhost.zone"; };
    zone "example.com" { type master; file "example.com.internal.zone"; };
};

view "external" {
    match-clients { any; };
    zone "." { type hint; file "named.ca"; };
    zone "example.com" { type master; file "example.com.external.zone"; };
};
```

---

## Catalog Zones (BIND 9.11+)

A catalog zone is a special zone that contains a list of member zones. When you add a zone to the catalog, all catalog consumers (secondaries) automatically create that zone — no manual config changes on each secondary.

### Setting Up Catalog Zones

**On the primary (catalog producer):**
```
zone "catalog.example.com" {
    type master;
    file "catalog.example.com.zone";
    allow-transfer { 203.0.113.2; };
};
```

**Catalog zone file:**
```
$TTL 3600
@    IN  SOA  ns1.example.com.  hostmaster.example.com. (1 3600 900 604800 300)
@    IN  NS   ns1.example.com.
@    IN  TXT  "2"         ; catalog version

; Each member zone is listed as a PTR record with a unique hash label:
uniquehash1.zones.catalog.example.com.  IN  PTR  zone1.example.com.
uniquehash2.zones.catalog.example.com.  IN  PTR  zone2.example.com.
```

**On secondaries (catalog consumer):**
```
options {
    catalog-zones {
        zone "catalog.example.com"
            default-masters { 203.0.113.1; }
            in-memory no
            zone-directory "/var/named/slaves";
    };
};

zone "catalog.example.com" {
    type slave;
    masters { 203.0.113.1; };
    file "slaves/catalog.example.com.zone";
};
```

The secondary will automatically create and transfer all zones listed in the catalog.

---

## DLZ — Dynamically Loadable Zones (BIND 9.8+)

DLZ allows BIND to load zone data from external databases (MySQL, PostgreSQL, LDAP, etc.) instead of flat files:

```
dlz "mysql-zones" {
    database "mysql
        {host=127.0.0.1 dbname=dns ssl=false}
        {select zone from dns_records where zone='%zone%'}
        {select ttl, type, mx_priority, case lower(type) when 'soa' then concat_ws(' ', data, resp_person, serial, refresh, retry, expire, minimum) else data end from dns_records where zone='%zone%' and host='%record%'}
        ...
    ";
};
```

DLZ modules available: MySQL, PostgreSQL, LDAP, filesystem, BDB.

**Note:** DLZ performance can be a bottleneck at high query rates — each query may require a database lookup. Use with caching or for low-traffic internal zones.

---

## GeoIP / Geolocation Responses (BIND 9.10+ with GeoIP2)

Serve different answers based on client geography:

```
options {
    geoip-directory "/usr/share/GeoIP";   // GeoLite2 database path
};

view "north-america" {
    match-clients { geoip country US; geoip country CA; geoip country MX; };
    zone "example.com" {
        type master;
        file "example.com.na.zone";    // Points to North American CDN IPs
    };
};

view "europe" {
    match-clients { geoip continent EU; };
    zone "example.com" {
        type master;
        file "example.com.eu.zone";    // Points to European CDN IPs
    };
};
```

---

## DNS over TLS / DNS over HTTPS (BIND 9.18+)

BIND 9.18 introduced native DoT and DoH support:

```
options {
    listen-on port 853 tls local-tls { any; };          // DoT
    listen-on port 443 tls local-tls http default { any; };  // DoH
};

tls local-tls {
    key-file "/etc/ssl/private/named.key";
    cert-file "/etc/ssl/certs/named.crt";
    protocols { TLSv1.2; TLSv1.3; };
    ciphers "HIGH:!aNULL:!MD5:!RC4";
    prefer-server-ciphers yes;
    session-tickets no;
};
```

---

## Stub Zones

A stub zone contains only NS records (and glue) for a zone — similar to a delegation but maintained via zone transfer from another server. Useful for pointing internal resolvers at authoritative servers for specific domains:

```
zone "partner.example.org" {
    type stub;
    masters { 198.51.100.1; };   // Server to pull NS records from
    file "slaves/partner.example.org.stub";
};
```

Stub zones are automatically updated (NS records refreshed) like secondary zones.

---

## BIND 9 Versions and LTS

| Version | Status | Notes |
|---------|--------|-------|
| 9.11 | EOL | First LTS; still found in older RHEL/CentOS |
| 9.16 | LTS | Major modernization; PKCS#11, DoT/DoH groundwork |
| 9.18 | LTS (current) | Native DoT, DoH, HTTPS records, full RFC 8198 (aggressive negative caching) |
| 9.20 | Development | Ongoing improvements |

Check version: `named -v`

**RHEL/CentOS/Rocky 8** ships BIND 9.11; RHEL 9 ships 9.16. Ubuntu 22.04 ships 9.18.
