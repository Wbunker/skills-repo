# Maintaining BIND
## Chapter 7: rndc, Logging, Zone Transfers, Dynamic Updates, BIND Lifecycle

---

## rndc — Remote Name Daemon Control

`rndc` communicates with `named` over a local (or remote) control channel using a shared secret key.

### rndc.conf Setup

BIND generates a default key at install time (`/etc/rndc.key` or `/etc/bind/rndc.key`). To generate manually:

```bash
rndc-confgen -a         # Auto-generates /etc/rndc.key
rndc-confgen            # Prints full rndc.conf + named.conf controls stanza
```

In `named.conf`:
```
controls {
    inet 127.0.0.1 port 953 allow { 127.0.0.1; } keys { rndc-key; };
};

key "rndc-key" {
    algorithm hmac-sha256;
    secret "base64-encoded-secret==";
};
```

In `/etc/rndc.conf`:
```
options {
    default-key "rndc-key";
    default-server 127.0.0.1;
    default-port 953;
};

key "rndc-key" {
    algorithm hmac-sha256;
    secret "base64-encoded-secret==";
};
```

### rndc Command Reference

```bash
# Zone management
rndc reload                        # Reload all zones from disk
rndc reload example.com            # Reload one zone
rndc reconfig                      # Reload named.conf only (picks up new zones)
rndc freeze                        # Suspend dynamic updates, write journal to zone file
rndc freeze example.com            # Freeze one zone
rndc thaw                          # Resume dynamic updates
rndc sync -clean                   # Sync journal to zone file and remove journal

# Server control
rndc status                        # Server status (version, zones, statistics)
rndc stop                          # Graceful shutdown
rndc halt                          # Immediate shutdown (no flush)
rndc restart                       # Not supported in BIND 9 (use systemctl restart named)

# Zone transfers
rndc retransfer example.com        # Force zone transfer from primary
rndc refresh example.com           # Check serial and transfer if needed

# Cache
rndc flush                         # Flush all caches
rndc flush view viewname           # Flush a specific view's cache
rndc dumpdb -cache                 # Dump cache to dump-file

# Debugging
rndc trace                         # Increment debug level by 1
rndc trace 3                       # Set debug level to 3
rndc notrace                       # Set debug level to 0
rndc querylog on                   # Enable query logging
rndc querylog off                  # Disable query logging

# Statistics
rndc stats                         # Write stats to statistics-file
```

---

## BIND Logging

BIND 9 has a flexible, channel-based logging system. All logging config goes in the `logging` block in `named.conf`.

### Channels

A **channel** defines where log messages go and at what severity:

```
logging {
    channel default_log {
        file "/var/log/named/named.log"
            versions 3           // Keep 3 rotated files
            size 10m;            // Roll when file exceeds 10MB
        severity dynamic;        // Uses current debug level
        print-time yes;
        print-severity yes;
        print-category yes;
    };

    channel queries_log {
        file "/var/log/named/queries.log" versions 5 size 20m;
        severity info;
        print-time yes;
    };

    channel null { null; };      // Discard
    // Other destinations: stderr, syslog facility
    channel syslog_log {
        syslog local2;
        severity notice;
    };
};
```

Severity levels (high to low): `critical`, `error`, `warning`, `notice`, `info`, `debug [level]`, `dynamic`

`dynamic` tracks the current debug level set by `rndc trace`.

### Categories

A **category** routes specific types of messages to a channel:

```
logging {
    category default     { default_log; };    // Catch-all
    category general     { default_log; };    // Miscellaneous
    category queries     { queries_log; };    // All incoming queries
    category query-errors { default_log; };   // Errors on queries
    category database    { null; };           // DB operations (noisy)
    category security    { default_log; };    // Access control decisions
    category config      { default_log; };    // Configuration parsing
    category resolver    { default_log; };    // Recursive resolution
    category xfer-in     { default_log; };    // Inbound zone transfers
    category xfer-out    { default_log; };    // Outbound zone transfers
    category notify      { default_log; };    // NOTIFY messages
    category update      { default_log; };    // Dynamic DNS updates
    category dnssec      { default_log; };    // DNSSEC validation
    category lame-servers { null; };          // Lame delegations (very noisy)
    category edns-disabled { null; };         // EDNS probing (very noisy)
    category rpz         { default_log; };    // Response Policy Zone
};
```

### Enabling Query Logging

```
// In named.conf:
logging {
    channel query_log {
        file "/var/log/named/queries.log" versions 10 size 50m;
        print-time yes;
        severity info;
    };
    category queries { query_log; };
};
```

Or dynamically: `rndc querylog on`

Query log format:
```
client 192.168.1.50#45123 (www.example.com): query: www.example.com IN A + (203.0.113.1)
;; client IP#port (qname): query: qname qclass qtype flags (server-IP)
```
Flags: `+` = recursion desired, `-` = not; `T` = TCP; `S` = signed (TSIG); `E` = EDNS

---

## Zone Transfers

### AXFR (Full Zone Transfer)

Transfers the entire zone. Used when:
- Secondary has no copy of the zone
- Secondary's serial is behind primary by more than `ixfr-from-differences` threshold
- Primary doesn't support IXFR

```bash
# Test AXFR from command line
dig @ns1.example.com example.com AXFR
```

### IXFR (Incremental Zone Transfer)

Transfers only changed records. Primary must have a journal file (`.jnl`). Secondary sends its current serial in the IXFR request; primary sends only the diff.

To force AXFR even when IXFR is available:
```
zone "example.com" { request-ixfr no; };
```

### Zone Transfer Security

**Never allow zone transfers to `any`** — it exposes your entire DNS infrastructure. Restrict to secondary IPs:

```
zone "example.com" {
    type master;
    allow-transfer { 203.0.113.2; 203.0.113.3; };
};
```

Or use TSIG (preferred):
```
zone "example.com" {
    type master;
    allow-transfer { key secondary-transfer-key; };
};
```

---

## Dynamic DNS Updates (RFC 2136)

Named can accept DNS record updates over the network without editing zone files.

### Allowing Updates

In `named.conf`:
```
zone "example.com" {
    type master;
    file "example.com.zone";
    allow-update { key dhcp-key; };   // Only allow updates with this TSIG key
    // OR: allow-update { 127.0.0.1; };  (IP-only, insecure)
};
```

When dynamic updates are enabled, BIND writes changes to a **journal file** (`example.com.zone.jnl`). The journal is applied over the zone file at load time. To make changes permanent in the zone file:

```bash
rndc freeze example.com     # Write journal to zone file, pause updates
# Edit zone file if needed
rndc thaw example.com       # Resume updates
# OR:
rndc sync -clean example.com  # Sync and remove journal
```

### nsupdate

```bash
# Interactive:
nsupdate
> server ns1.example.com
> zone example.com
> update add newhost.example.com 3600 A 203.0.113.99
> update delete oldhost.example.com A
> send
> quit

# With TSIG key file:
nsupdate -k /etc/dhcp/ddns-key.conf

# Batch (from file):
nsupdate updates.txt
```

---

## BIND Startup and Lifecycle

### Systemd

```bash
systemctl start named        # Start
systemctl stop named         # Stop
systemctl restart named      # Full restart (drops cache)
systemctl reload named       # Same as rndc reload
systemctl status named       # Status + recent logs
systemctl enable named       # Enable at boot
journalctl -u named -f       # Follow logs
```

### Named Startup Sequence

1. Read `named.conf` and validate
2. Load root hints (hint zone)
3. Load authoritative zones from disk
4. Start listening on configured interfaces
5. Begin accepting queries

### Zone File Updates (Manual Workflow)

```bash
# 1. Edit zone file
vim /var/named/example.com.zone
# 2. Increment SOA serial
# 3. Validate
named-checkzone example.com /var/named/example.com.zone
# 4. Reload
rndc reload example.com
# 5. Verify
dig @127.0.0.1 www.example.com A +short
```

---

## Statistics

```bash
# Write stats to statistics-file
rndc stats

# Or configure statistics channels (HTTP):
statistics-channels {
    inet 127.0.0.1 port 8053 allow { 127.0.0.1; };
};
# Then: curl http://127.0.0.1:8053/json/v1/
```

Stats include:
- Query counts by type, result (NOERROR, NXDOMAIN, SERVFAIL, etc.)
- Zone transfer statistics
- Cache hit/miss rates
- Socket I/O statistics
- Resolver round-trip timing

---

## Monitoring Checks

```bash
# Is named listening?
ss -tulnp | grep named

# Is it responding?
dig @127.0.0.1 . NS +short +time=2

# Check version (may be hidden for security)
dig @127.0.0.1 version.bind CHAOS TXT +short

# Check statistics
rndc status

# Recent errors
journalctl -u named --since "1 hour ago" | grep -i error
```
