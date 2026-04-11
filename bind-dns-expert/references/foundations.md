# DNS Foundations
## Chapters 1–2: Background, How DNS Works, Resource Records, Resolution

---

## Why DNS Exists

Before DNS, the entire Internet's host-to-address mapping lived in a single flat file, `HOSTS.TXT`, maintained by SRI-NIC and downloaded by every host. As ARPANET grew, this became untenable:
- Single point of update (and failure)
- No consistency — different hosts had different versions
- Traffic explosion: thousands of FTP downloads daily
- Name collisions across organizations

DNS (Domain Name System), designed by Paul Mockapetris in 1983 (RFC 882, 883; later 1034, 1035), replaced this with a distributed, hierarchical, delegated database.

---

## The DNS Namespace

### Hierarchy and Zones

```
                        . (root)
                  ──────┼──────
                .com  .net  .org  .edu  .gov  .uk ...
                /
           example.com
           /         \
      www.example.com  mail.example.com
```

- **Root zone** (`.`): 13 root server clusters (a–m.root-servers.net), operated by different organizations
- **Top-level domains (TLDs)**: Generic (`.com`, `.net`, `.org`) and country-code (`.uk`, `.de`, `.jp`)
- **Second-level domains**: Registered by organizations (`example.com`)
- **Subdomains**: Further delegated (`dev.example.com`, `us.sales.example.com`)

### Domain vs. Zone

A **domain** is a subtree of the namespace. A **zone** is the portion of the namespace a single name server (or set of servers) is **authoritative** for.

```
example.com domain
├── example.com zone (SOA at example.com)
│   ├── www.example.com
│   ├── mail.example.com
│   └── (delegation point) dev.example.com → NS dev-ns.example.com
└── dev.example.com zone (separate SOA, separate name server)
    ├── gitlab.dev.example.com
    └── ci.dev.example.com
```

A zone begins at an SOA record and ends at delegation points (NS records pointing to child zones).

---

## Name Servers

### Types

| Type | Description |
|------|-------------|
| **Primary (master)** | Loads zone data from local disk files; the authoritative source |
| **Secondary (slave)** | Loads zone via zone transfer (AXFR/IXFR) from another server; auto-syncs |
| **Caching-only** | Not authoritative for any zone; resolves queries and caches results |
| **Forwarder** | Forwards queries to a designated resolver instead of resolving recursively |

### Authoritative vs. Recursive

- **Authoritative answer**: Server has direct knowledge of the zone (AA bit set in response)
- **Recursive resolver**: Walks the tree from root to answer on behalf of a client
- **Iterative query**: Server returns a referral ("ask this server instead") rather than answering

A single BIND instance can be both authoritative and recursive, but this is a security anti-pattern — keep them separate.

---

## Resolution Process (Recursive)

```
1. Client asks its configured resolver: "What is the IP of www.example.com?"
2. Resolver checks cache → not found
3. Resolver asks a root server: "www.example.com?"
   Root replies: "I don't know, but try .com TLD servers: a.gtld-servers.net, ..."
4. Resolver asks TLD server: "www.example.com?"
   TLD replies: "I don't know, but example.com NS is ns1.example.com (1.2.3.4)"
5. Resolver asks ns1.example.com: "www.example.com?"
   Auth server replies: "www.example.com A 1.2.3.100" (authoritative answer)
6. Resolver caches result, returns to client
```

**Key points:**
- Each referral step returns NS records + glue (A records for those NS hosts)
- Results are cached per their TTL
- Negative answers (NXDOMAIN) are also cached per the SOA's negative TTL

---

## Resource Records

Every DNS record follows this format:
```
name        [ttl]  class  type  rdata
```
- `name`: Owner name (relative to zone, or FQDN with trailing dot)
- `ttl`: Optional; defaults to `$TTL` directive or SOA minimum
- `class`: Almost always `IN` (Internet)
- `type`: Record type (A, AAAA, MX, etc.)
- `rdata`: Record-type-specific data

### SOA — Start of Authority

```
example.com.  86400  IN  SOA  ns1.example.com.  hostmaster.example.com. (
    2024010101  ; Serial: increment on every change (YYYYMMDDnn format)
    3600        ; Refresh: how often secondaries poll for updates (seconds)
    900         ; Retry: secondary retry interval after failed refresh
    604800      ; Expire: secondary stops serving if no refresh for this long
    300         ; Negative TTL: how long NXDOMAIN/NODATA is cached
)
```

Serial format: use `YYYYMMDDnn` (e.g., `2024031501` = March 15, 2024, change 01). Secondaries compare serials; if primary's serial > secondary's serial, a zone transfer is initiated.

### NS — Name Server

```
example.com.    86400  IN  NS  ns1.example.com.
example.com.    86400  IN  NS  ns2.example.com.
```

NS records at the zone apex identify authoritative servers. NS records at a delegation point (inside a parent zone) are **delegation NS records** — they point to child zone servers. Glue A records are required when the NS hostname is within the delegated zone.

### A and AAAA — Address Records

```
www.example.com.    3600  IN  A      203.0.113.10
www.example.com.    3600  IN  AAAA   2001:db8::10
```

Multiple A/AAAA records for the same name implement **round-robin load distribution**.

### CNAME — Canonical Name (Alias)

```
ftp.example.com.    3600  IN  CNAME  www.example.com.
```

**Rules:**
- The CNAME target must itself resolve (no CNAME chain loops)
- A CNAME cannot coexist with other record types for the same name (except DNSSEC records)
- Never put a CNAME at the zone apex (use A/AAAA there instead)
- MX and NS records must not point to CNAMEs

### MX — Mail Exchanger

```
example.com.    3600  IN  MX  10  mail1.example.com.
example.com.    3600  IN  MX  20  mail2.example.com.
```

Lower preference number = higher priority. If `10` is unreachable, senders try `20`. The MX target must be an A/AAAA record, never a CNAME.

### PTR — Pointer (Reverse DNS)

```
10.113.0.203.in-addr.arpa.    3600  IN  PTR  www.example.com.
```

Reverse zone for `203.0.113.0/24` is `113.0.203.in-addr.arpa.` (octets reversed). For IPv6, use `ip6.arpa.` with nibble-reversed address.

### TXT — Text

```
example.com.    3600  IN  TXT  "v=spf1 mx ~all"
_dmarc.example.com.  3600  IN  TXT  "v=DMARC1; p=quarantine"
```

Used for SPF, DKIM, DMARC, domain verification tokens, and other freeform data.

### SRV — Service Locator

```
_sip._tcp.example.com.  3600  IN  SRV  10  20  5060  sip.example.com.
;                                      pri wt  port  target
```

Fields: priority (lower = preferred), weight (for same-priority selection), port, target hostname.

### NAPTR — Naming Authority Pointer

Used for ENUM (mapping phone numbers to URIs) and SIP. Complex; rarely configured manually.

### Other Record Types

| Type | Use |
|------|-----|
| `HINFO` | Host info (CPU, OS) — largely obsolete, security risk |
| `LOC` | Geographic location — rarely used |
| `SSHFP` | SSH fingerprints for DANE-like verification |
| `TLSA` | TLS certificate association (DANE) |
| `CAA` | Certificate Authority Authorization |
| `DS` | Delegation Signer — DNSSEC glue in parent zone |
| `DNSKEY` | Public key for DNSSEC zone signing |
| `RRSIG` | Signature over an RRset |
| `NSEC/NSEC3` | Authenticated denial of existence (DNSSEC) |

---

## Caching and TTLs

- Every record returned has a TTL; resolvers decrement it as time passes
- Cached records are reused until TTL expires (reduces load on authoritative servers)
- **Negative TTL** (from SOA field 5): how long NXDOMAIN/NODATA responses are cached
- Lowering TTLs before infrastructure changes reduces propagation lag

### Cache Poisoning

Attackers attempt to inject false records into resolver caches. Mitigations:
- Randomize source ports and query IDs (Kaminsky attack defense — now standard)
- DNSSEC (cryptographic validation, the only complete solution)
- Restrict recursive queries to trusted clients (access control)

---

## The `/etc/hosts` File

Still consulted first (per nsswitch.conf) on most systems. Format:
```
127.0.0.1   localhost
203.0.113.10  www.example.com  www
```

---

## BIND Version History (Context)

| Version | Notes |
|---------|-------|
| BIND 4 | Original; flat config; largely obsolete |
| BIND 8 | Modern config syntax (named.conf); still found on legacy systems |
| BIND 9 | Current; IPv6, DNSSEC, views, IXFR, TSIG, LDAP; this book's primary focus |
| BIND 10/Bundy | Rewrite project (abandoned) |
| BIND 9.x | Ongoing releases: 9.11 (LTS), 9.16 (LTS), 9.18 (LTS) |
