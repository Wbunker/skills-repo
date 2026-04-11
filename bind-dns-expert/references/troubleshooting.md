# Troubleshooting DNS and BIND
## Chapters 12–14: dig/nslookup, Reading Debug Output, Common Failures

---

## Chapter 12: dig and nslookup

### dig — The Primary DNS Query Tool

`dig` (Domain Information Groper) is the standard tool for DNS diagnostics. Always prefer `dig` over `nslookup` for scripting and diagnostics.

#### Basic Usage

```bash
# Simple A query
dig www.example.com

# Query specific type
dig www.example.com AAAA
dig example.com MX
dig example.com NS
dig example.com SOA
dig example.com ANY

# Query a specific server
dig @8.8.8.8 www.example.com A
dig @ns1.example.com www.example.com A

# Reverse lookup
dig -x 203.0.113.10
dig -x 2001:db8::10

# Short output (just the answer)
dig www.example.com A +short

# Request DNSSEC records
dig www.example.com A +dnssec
```

#### Key dig Options

```bash
# Output control
+short          # Print answer RRs only
+noall +answer  # Print only the answer section
+nocomments     # Remove comment lines
+nocmd          # No version/query header
+stats          # Show query statistics (timing, server)
+nostats        # Hide statistics

# Query behavior
+time=5         # Timeout in seconds (default: 5)
+tries=3        # Number of retries
+tcp            # Force TCP (instead of UDP)
+vc             # Same as +tcp (virtual circuit)
+ignore         # Ignore truncation flag (don't switch to TCP)
+notcp          # Force UDP even for large responses

# DNS flags
+rd             # Recursion desired (default)
+nords          # Disable recursion (for testing authoritative)
+aa             # Request authoritative answer (rarely needed)
+cd             # Checking disabled (disable DNSSEC validation)
+dnssec         # Request DNSSEC records (DO bit)

# Tracing
+trace          # Trace from root (simulates resolution path)
+identify       # Show server that sent each answer

# Format
+multiline      # Pretty-print SOA and other records
+onesoa         # Show only one SOA in AXFR
```

#### Useful dig Invocations

```bash
# Full trace from root to answer:
dig +trace www.example.com A

# Test DNSSEC validation chain:
dig +trace +dnssec www.example.com A

# Check if a zone is signed:
dig example.com DNSKEY +short

# Get DS record (for submitting to registrar):
dig example.com DS @parent-ns

# Check SOA serial (compare primary vs. secondary):
dig @ns1.example.com example.com SOA +short
dig @ns2.example.com example.com SOA +short

# Zone transfer test (should fail from external):
dig @ns1.example.com example.com AXFR

# Query with EDNS disabled (test broken EDNS servers):
dig www.example.com A +noedns

# Query with TCP (test firewall):
dig @ns1.example.com www.example.com A +tcp

# Batch queries from file:
dig -f queries.txt +noall +answer

# Check propagation (query multiple servers):
for ns in 8.8.8.8 1.1.1.1 9.9.9.9; do
    echo "=== $ns ==="; dig @$ns www.example.com A +short
done
```

#### dig Output Anatomy

```
; <<>> DiG 9.18.1 <<>> www.example.com A
;; global options: +cmd

;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 12345
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 2, ADDITIONAL: 3

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags: do; udp: 4096
;; QUESTION SECTION:
;www.example.com.               IN      A

;; ANSWER SECTION:
www.example.com.        3600    IN      A       203.0.113.20

;; AUTHORITY SECTION:
example.com.            86400   IN      NS      ns1.example.com.
example.com.            86400   IN      NS      ns2.example.com.

;; ADDITIONAL SECTION:
ns1.example.com.        3600    IN      A       203.0.113.1
ns2.example.com.        3600    IN      A       203.0.113.2

;; Query time: 5 msec
;; SERVER: 203.0.113.1#53(203.0.113.1)
;; WHEN: Mon Mar 15 10:00:00 UTC 2024
;; MSG SIZE  rcvd: 140
```

**Flags decoded:**
- `qr` — this is a response (not a query)
- `aa` — authoritative answer (server has authority for this zone)
- `rd` — recursion desired (client requested recursion)
- `ra` — recursion available (server supports recursion)
- `tc` — truncated (response was cut off; retry with TCP)
- `cd` — checking disabled (DNSSEC validation skipped)
- `ad` — authentic data (DNSSEC validation succeeded)

**Status codes:**
- `NOERROR` — successful
- `NXDOMAIN` — name does not exist
- `SERVFAIL` — server failed (often DNSSEC validation failure)
- `REFUSED` — server refused the query (ACL or recursion restriction)
- `NOTIMP` — query type not implemented
- `FORMERR` — malformed query (often EDNS issue)

---

### nslookup

Legacy tool; still widely available. Interactive or non-interactive mode.

```bash
# Non-interactive:
nslookup www.example.com
nslookup www.example.com 8.8.8.8     # Query specific server
nslookup -type=MX example.com
nslookup -type=NS example.com
nslookup -debug www.example.com       # Debug output

# Interactive:
nslookup
> server 8.8.8.8
> set type=MX
> example.com
> set debug
> www.example.com
> exit
```

`nslookup` quirks to know:
- May not respect `/etc/hosts` for all queries
- "Non-authoritative answer" just means it came from cache — not a problem
- `server 8.8.8.8` changes the server for the session only

---

## Chapter 13: Reading BIND Debugging Output

### Enabling Debug Logging

```bash
# At runtime:
rndc trace           # Increment debug level by 1 (starts at 0)
rndc trace 3         # Set to specific level
rndc notrace         # Reset to 0 (disable)

# On startup:
named -g -d 3        # Foreground, debug level 3

# In named.conf (permanent):
logging {
    channel default_log {
        severity debug 3;   # Log debug level 3 and above
    };
};
```

### Debug Levels

| Level | Output |
|-------|--------|
| 0 | Normal operation messages only |
| 1 | Basic per-query information |
| 2 | Detailed query processing |
| 3 | Cache operations, zone loading |
| 5+ | Very detailed (internal state, memory) |
| 10+ | Extremely verbose; heavy performance impact |

Use level 1–2 for query tracing, level 3 for zone load issues, level 5+ only briefly for deep debugging.

### Debug Output Patterns

**Query processing (level 1):**
```
client 192.168.1.50#45123 (www.example.com): view internal: query: www.example.com IN A + (203.0.113.1)
client 192.168.1.50#45123: query response: www.example.com IN A NOERROR
```

**Zone transfer (level 1):**
```
transfer of 'example.com/IN' from 203.0.113.1#53: connected
transfer of 'example.com/IN' from 203.0.113.1#53: Transfer completed: 1 messages, 25 records, 1234 bytes, 0.003 secs
```

**DNSSEC validation failure (level 1):**
```
validating example.com/DNSKEY: got insecure response; parent indicates it should be secure
validating www.example.com/A: got insecure response
```

---

## Chapter 14: Troubleshooting Common Problems

### Diagnostic Decision Tree

```
DNS problem?
├── Name doesn't resolve at all
│   ├── Check named is running: systemctl status named
│   ├── Check it's listening: ss -ulnp | grep :53
│   ├── Test locally: dig @127.0.0.1 www.example.com A
│   ├── Check firewall: nft list ruleset | grep 53 / iptables -L -n | grep 53
│   └── Check named.conf syntax: named-checkconf
├── Wrong answer returned
│   ├── Check which server answered: dig +identify www.example.com
│   ├── Check if cached: dig +norecurse @resolver www.example.com
│   ├── Flush cache and retry: rndc flush
│   └── Query authoritative directly: dig @ns1.example.com www.example.com
├── Slow resolution
│   ├── Check RTT in dig stats (+stats)
│   ├── Check forwarder availability
│   ├── Check for lame delegations in logs
│   └── Check network path: traceroute to resolver/authoritative
├── Zone transfer failing
│   ├── Check allow-transfer on primary
│   ├── Check TSIG key matches on both sides
│   ├── Test AXFR manually: dig @primary example.com AXFR
│   └── Check firewall: TCP port 53 allowed between servers
└── DNSSEC validation failure
    ├── Test without validation: dig +cd www.example.com
    ├── Check zone signatures: dig example.com DNSKEY +dnssec
    ├── Check DS in parent: dig example.com DS @parent-ns
    └── Check RRSIG expiry: dig www.example.com A +dnssec → check RRSIG dates
```

### Common Failure Patterns

#### 1. NXDOMAIN for a Hostname That Should Exist

```bash
dig @ns1.example.com missing.example.com A
# Returns NXDOMAIN

# Check: Is the record in the zone file?
grep missing /var/named/example.com.zone

# Check: Was the zone reloaded after adding the record?
rndc reload example.com

# Check: Does named-checkzone report any errors?
named-checkzone example.com /var/named/example.com.zone

# Check: Trailing dot missing (record pointing to wrong name)?
# "mail.example.com" without trailing dot = "mail.example.com.example.com."
```

#### 2. SERVFAIL

Usually indicates DNSSEC validation failure or a server error:

```bash
# Test without DNSSEC validation:
dig +cd www.example.com A
# If this works but without +cd fails → DNSSEC problem

# Check RRSIG validity period:
dig www.example.com RRSIG +short
# RRSIG expiration date must be in the future

# Check DS in parent zone:
dig example.com DS @parent-ns +short

# Resign if signatures are expired:
rndc sign example.com   # For inline-signing zones
```

#### 3. Zone Transfer Fails

```bash
# Test from secondary manually:
dig @203.0.113.1 example.com AXFR

# Common causes:
# a) allow-transfer restricts to different IP (check primary ACL)
# b) TSIG key mismatch — check algorithm and secret match on both sides
# c) Firewall blocks TCP port 53
# d) SOA serial on secondary >= primary (no transfer needed — not actually a failure)

# Check secondary logs:
journalctl -u named | grep "example.com"
# Look for: "not authoritative for", "transfer of", "TSIG"
```

#### 4. Lame Delegation

A server listed in NS records doesn't answer authoritatively for the zone:

```bash
# Check which servers are listed:
dig example.com NS @8.8.8.8

# Query each listed NS for SOA:
dig @ns1.example.com example.com SOA
# If it returns REFUSED or no AA flag → lame server

# Fix: Either fix the server's configuration, or remove it from NS records
```

#### 5. Cache Poisoning / Stale Cache

```bash
# Flush entire cache:
rndc flush

# Flush a specific name:
rndc flushname www.example.com

# Flush a specific view's cache:
rndc flush internal
```

#### 6. Named Won't Start

```bash
# Check config syntax:
named-checkconf -z      # Also checks all zone files

# Check each zone file:
named-checkzone example.com /var/named/example.com.zone

# Start in foreground with debug:
named -g -d 1

# Common causes:
# - Port 53 already in use: ss -ulnp | grep :53
# - Permission denied on zone files: ls -l /var/named/
# - SELinux/AppArmor blocking: ausearch -c named / aa-status
# - listen-on specifies an IP that doesn't exist on this host
```

#### 7. Split DNS: Internal Clients Getting External View

```bash
# Confirm which view is being matched:
rndc trace 1
# Then make a query and check logs for "view internal:" or "view external:"

# Verify match-clients ACL covers the client:
# - Check the client's source IP
# - Check ACL definitions and order
# - First matching view wins

# Test from specific source:
dig -b 10.0.0.1 @127.0.0.1 www.example.com A   # Simulate internal client
```

#### 8. Slow DNS / High Query Times

```bash
# Check query time in dig:
dig www.example.com +stats | grep "Query time"

# If slow on first query, fast on second → resolver cache working but first lookup slow
# → Check forwarder latency or root server reachability

# Check forwarder responsiveness:
dig @8.8.8.8 www.example.com +time=2

# Check BIND statistics:
rndc stats && cat /var/named/data/named_stats.txt | grep -A5 "Incoming Queries"

# Check for lame server messages in logs (repeated lame referrals add latency):
journalctl -u named | grep lame
```

#### 9. EDNS Problems

Some old/broken devices/firewalls don't handle EDNS correctly:

```bash
# Test without EDNS:
dig www.example.com A +noedns

# If +noedns works but normal query fails → EDNS problem

# Workaround in named.conf for specific broken servers:
server 1.2.3.4 {
    edns no;
};
# Or reduce EDNS buffer size:
server 1.2.3.4 {
    edns-udp-size 512;
};
```

---

### Quick Reference: Query Flags to Test With

| Test | Command | What It Confirms |
|------|---------|-----------------|
| Basic resolution | `dig www.example.com A` | Resolver works |
| Authoritative test | `dig @ns1.example.com www.example.com A` | Authoritative server works |
| No recursion | `dig @ns1.example.com www.example.com A +nords` | Auth-only behavior |
| TCP path | `dig @ns1.example.com www.example.com A +tcp` | TCP port 53 open |
| Full trace | `dig +trace www.example.com A` | Delegation chain intact |
| DNSSEC validation | `dig www.example.com A +dnssec` | AD bit = valid |
| Skip validation | `dig www.example.com A +cd` | Bypass DNSSEC check |
| Reverse PTR | `dig -x 203.0.113.20` | Reverse zone works |
| Zone transfer | `dig @ns1 example.com AXFR` | Transfer allowed/blocked |
| Cache check | `dig +norecurse @resolver www.example.com` | Is answer in cache? |

### Useful Diagnostic Sequence for a New Server

```bash
# 1. Verify named is running and listening
systemctl status named
ss -ulnp | grep :53

# 2. Test localhost resolution
dig @127.0.0.1 . NS +short

# 3. Test authoritative zones
dig @127.0.0.1 www.example.com A +short
dig @127.0.0.1 example.com SOA +short
dig @127.0.0.1 example.com NS +short

# 4. Test reverse zones
dig @127.0.0.1 -x 203.0.113.20 +short

# 5. Test zone transfer (from secondary)
dig @primary-ip example.com AXFR | head -20

# 6. Test DNSSEC (if enabled)
dig @127.0.0.1 www.example.com A +dnssec | grep -E "RRSIG|flags"

# 7. Check logs for errors
journalctl -u named --since "5 minutes ago" | grep -iE "error|failed|refused|lame"
```
