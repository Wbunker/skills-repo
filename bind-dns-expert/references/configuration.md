# BIND Configuration
## Chapters 3–4: Installation, named.conf, Zone Files, Primary and Secondary Setup

---

## Getting BIND

### Installation

```bash
# RHEL/CentOS/Rocky/Alma
dnf install bind bind-utils

# Debian/Ubuntu
apt install bind9 bind9-dnsutils

# FreeBSD (included in base; or ports)
pkg install bind918

# Verify version
named -v
```

BIND 9 binaries:
- `named` — the name server daemon
- `named-checkconf` — validate named.conf
- `named-checkzone` — validate a zone file
- `rndc` — remote name daemon control
- `dig` — DNS query tool
- `nsupdate` — dynamic DNS update client

---

## File Layout (Typical)

```
/etc/named.conf              Main configuration
/etc/named/                  Additional config snippets (include files)
/var/named/                  Zone data files
/var/named/slaves/           Secondary (slave) zone files
/var/run/named/named.pid     PID file
/var/named/data/named.stats  Statistics (after rndc stats)
```

Debian/Ubuntu uses `/etc/bind/` and `/var/cache/bind/` instead.

---

## named.conf Structure

```
// named.conf
// Comments: C++ style (//) or C style (/* */) or shell style (#)

options {
    directory "/var/named";           // Working directory for relative paths
    listen-on { 192.0.2.1; };        // Which interfaces to listen on (default: all)
    listen-on-v6 { none; };
    allow-query { any; };             // Who may query (default: any for authoritative)
    allow-recursion { 127.0.0.1; 192.168.0.0/24; };  // Only trusted clients
    recursion yes;                    // Allow recursive queries
    forwarders { 8.8.8.8; 8.8.4.4; };  // Forward unresolved queries here
    forward only;                     // Don't recurse if forwarders fail (use 'first' to fall back)
    dnssec-validation auto;           // Enable DNSSEC validation (uses managed-keys)
    pid-file "/var/run/named/named.pid";
    dump-file "/var/named/data/cache_dump.db";
    statistics-file "/var/named/data/named_stats.txt";
};

logging {
    channel default_log {
        file "/var/log/named/named.log" versions 3 size 5m;
        severity dynamic;
        print-time yes;
        print-severity yes;
        print-category yes;
    };
    category default { default_log; };
    category queries { default_log; };
};

// Root hints
zone "." IN {
    type hint;
    file "named.ca";      // Root hints file (download from Internic)
};

// Localhost zones
zone "localhost" IN {
    type master;
    file "localhost.zone";
    allow-update { none; };
};

zone "0.0.127.in-addr.arpa" IN {
    type master;
    file "named.localhost";
    allow-update { none; };
};

// Your zone
zone "example.com" IN {
    type master;
    file "example.com.zone";
    allow-update { none; };
    allow-transfer { 192.0.2.2; };   // Secondary servers only
};

// Reverse zone
zone "113.0.203.in-addr.arpa" IN {
    type master;
    file "203.0.113.zone";
    allow-update { none; };
    allow-transfer { 192.0.2.2; };
};
```

### Key options Explained

| Option | Description |
|--------|-------------|
| `directory` | Base path for relative file names in zone statements |
| `listen-on` | Interfaces to accept queries on (restrict to avoid amplification) |
| `allow-query` | IP/network allowed to query; use `any` for public authoritative servers |
| `allow-recursion` | Who gets recursive service; restrict to internal clients |
| `allow-transfer` | Who may perform zone transfers (restrict to secondary IPs) |
| `forwarders` | Upstream resolvers; used with `forward first` or `forward only` |
| `recursion` | Enable/disable recursive resolution |
| `dnssec-validation` | `auto` (uses built-in trust anchors), `yes` (requires explicit trust anchor), `no` |
| `notify` | Send NOTIFY to secondaries on zone change (default `yes`) |
| `also-notify` | Additional IPs to NOTIFY beyond zone's NS records |

---

## Zone File Syntax

### Directives

```
$TTL 3600              ; Default TTL for records that omit explicit TTL
$ORIGIN example.com.   ; Default domain for relative names (usually set to zone name)
```

### SOA Record (Required, Zone Apex)

```
@    IN  SOA  ns1.example.com.  hostmaster.example.com. (
     2024031501   ; Serial
     3600         ; Refresh
     900          ; Retry
     604800       ; Expire (7 days)
     300          ; Negative TTL (5 min)
)
```

`@` refers to `$ORIGIN`. The SOA's `MNAME` (ns1.example.com.) should be the primary server. The `RNAME` field (hostmaster.example.com.) encodes an email address: the first `.` becomes `@` — so this means `hostmaster@example.com`.

### Complete Zone File Example

```
$TTL 3600
$ORIGIN example.com.

@       IN  SOA  ns1.example.com.  hostmaster.example.com. (
                 2024031501  3600  900  604800  300 )

; Name servers
@       IN  NS   ns1.example.com.
@       IN  NS   ns2.example.com.

; Mail exchangers
@       IN  MX   10  mail1.example.com.
@       IN  MX   20  mail2.example.com.

; Address records (glue for NS hosts in this zone)
ns1     IN  A    203.0.113.1
ns2     IN  A    203.0.113.2
mail1   IN  A    203.0.113.10
mail2   IN  A    203.0.113.11

; Web
www     IN  A    203.0.113.20
www     IN  AAAA 2001:db8::20
@       IN  A    203.0.113.20     ; Bare domain (zone apex)

; Alias
ftp     IN  CNAME  www.example.com.

; SPF
@       IN  TXT  "v=spf1 mx a ~all"
```

### Relative vs. Absolute Names

- **Relative**: `www` → expanded to `www.example.com.` using `$ORIGIN`
- **Absolute (FQDN)**: `www.example.com.` — trailing dot required; without it, `$ORIGIN` is appended
- **Common mistake**: Writing `ns1.example.com` (no trailing dot) in rdata fields → becomes `ns1.example.com.example.com.`

---

## Reverse Zone Files

Reverse zones map IP addresses to hostnames. The zone name is the network octets in reverse with `.in-addr.arpa.` appended.

For `203.0.113.0/24` → zone `113.0.203.in-addr.arpa.`

```
$TTL 3600
$ORIGIN 113.0.203.in-addr.arpa.

@       IN  SOA  ns1.example.com.  hostmaster.example.com. (
                 2024031501  3600  900  604800  300 )
@       IN  NS   ns1.example.com.
@       IN  NS   ns2.example.com.

1       IN  PTR  ns1.example.com.
2       IN  PTR  ns2.example.com.
10      IN  PTR  mail1.example.com.
20      IN  PTR  www.example.com.
```

For a `/16` network (e.g., `10.0.0.0/16`): zone is `0.10.in-addr.arpa.`
For a `/8` network (e.g., `10.0.0.0/8`): zone is `10.in-addr.arpa.`

### Classless Reverse Delegation (RFC 2317)

For subnets smaller than `/24` (delegating a portion of a `/24` to another organization):

```
; In the ISP's 113.0.203.in-addr.arpa zone:
$ORIGIN 113.0.203.in-addr.arpa.

; Delegate 203.0.113.128/25 to customer
128/25    IN  NS  ns1.customer.example.
129       IN  CNAME  129.128/25.113.0.203.in-addr.arpa.
130       IN  CNAME  130.128/25.113.0.203.in-addr.arpa.
; ... (one CNAME per address in the /25)
```

---

## Setting Up a Primary (Master) Server

1. Install BIND
2. Get/update root hints: `named.ca` (download from ftp.rs.internic.net/domain/named.root)
3. Write `named.conf` with zone declarations
4. Write zone files
5. Validate:
   ```bash
   named-checkconf
   named-checkzone example.com /var/named/example.com.zone
   ```
6. Start BIND:
   ```bash
   systemctl start named   # RHEL/Debian with systemd
   named -f -g             # Foreground debug mode
   ```
7. Test:
   ```bash
   dig @127.0.0.1 www.example.com A
   dig @127.0.0.1 example.com MX
   dig @127.0.0.1 -x 203.0.113.20
   ```

---

## Setting Up a Secondary (Slave) Server

On the secondary, `named.conf` uses `type slave` (BIND 8/9) or `type secondary` (BIND 9.11+):

```
zone "example.com" IN {
    type slave;              // or: type secondary;
    masters { 203.0.113.1; };  // Primary's IP
    file "slaves/example.com.zone";  // Local cache of transferred zone
    allow-transfer { none; };  // Don't allow further transfers from this secondary
};
```

On the primary, allow the secondary to transfer:
```
zone "example.com" IN {
    type master;
    file "example.com.zone";
    allow-transfer { 203.0.113.2; };  // Secondary's IP
    also-notify   { 203.0.113.2; };   // Explicit NOTIFY (optional if NS records include it)
};
```

**Zone Transfer Process:**
1. Primary sends NOTIFY to secondaries when zone changes
2. Secondary sends SOA query to check serial number
3. If primary serial > secondary serial → secondary requests AXFR (full) or IXFR (incremental)
4. BIND 9 uses IXFR by default; falls back to AXFR if primary doesn't support it

---

## Caching-Only Name Server

A server that is not authoritative for any zone but provides recursive resolution:

```
options {
    directory "/var/named";
    recursion yes;
    allow-recursion { 10.0.0.0/8; 192.168.0.0/16; };
    dnssec-validation auto;
};

zone "." IN {
    type hint;
    file "named.ca";
};

// Optionally, make localhost resolution authoritative:
zone "localhost" IN { type master; file "localhost.zone"; };
zone "0.0.127.in-addr.arpa" IN { type master; file "named.localhost"; };
```

---

## Validation Commands

```bash
# Check named.conf syntax
named-checkconf /etc/named.conf

# Check a zone file
named-checkzone example.com /var/named/example.com.zone

# Check reverse zone
named-checkzone 113.0.203.in-addr.arpa /var/named/203.0.113.zone

# Check with journaling enabled (for dynamic zones)
named-checkzone -j example.com /var/named/example.com.zone
```

Common errors caught:
- Missing trailing dot on FQDNs in rdata
- SOA serial not incrementing
- Duplicate records
- Syntax errors in resource records
- `$ORIGIN` misuse
