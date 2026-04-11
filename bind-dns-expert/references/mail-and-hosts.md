# DNS and Electronic Mail / Configuring Hosts
## Chapters 5–6: MX Records, Mail Routing, resolv.conf, nsswitch.conf

---

## Chapter 5: DNS and Electronic Mail

### How Mail Routing Works

When a mail transfer agent (MTA) sends email to `user@example.com`:

1. MTA queries DNS for `example.com MX` records
2. DNS returns a list of mail exchangers sorted by preference (lower = higher priority)
3. MTA attempts delivery to the lowest-preference (highest-priority) host first
4. On failure, it tries the next higher preference value
5. If all MX hosts fail, MTA queues and retries

**Critical rule:** MTAs must not deliver to A records directly if MX records exist. The MX lookup is mandatory.

### MX Record Syntax

```
; Format: name  ttl  class  MX  preference  exchange
example.com.    3600  IN  MX  10  mail1.example.com.
example.com.    3600  IN  MX  20  mail2.example.com.
example.com.    3600  IN  MX  30  mail3.backup-provider.com.
```

**Preference values:** Any positive integer. Common conventions:
- `10` = primary
- `20` = secondary
- `30+` = backup/fallback

When multiple MX records have the **same preference**, the sending MTA selects one at random (load balancing).

### Mail Exchanger Address Records

Every MX hostname **must** have a corresponding A (and/or AAAA) record. The MX target must be a hostname that resolves to an address — never a CNAME. When the MX target is in the same zone, include its A record in the zone file (as "additional" data that resolvers may cache).

```
; Zone: example.com
$TTL 3600
@       IN  MX  10  mail1.example.com.
@       IN  MX  20  mail2.example.com.

mail1   IN  A   203.0.113.10
mail2   IN  A   203.0.113.11
```

### Local Delivery: `@` vs. the Hostname

A mail server that appears in its own MX record will deliver locally. If `mail1.example.com` has an MX record pointing to itself (or the zone apex's MX resolves to it), the MTA delivers locally rather than relaying.

### Wildcards in MX Records

A wildcard MX record catches mail for any undefined subdomain:

```
*.example.com.    3600  IN  MX  10  mail1.example.com.
```

This catches `user@foo.example.com`, `user@bar.example.com`, etc., but **not** `user@example.com` (zone apex is not covered by wildcard) and **not** explicitly defined subdomains (wildcard only applies where no other record exists for that name).

### Null MX (RFC 7505)

To explicitly declare a domain does not accept email (prevents fallback to A record):

```
example.com.    3600  IN  MX  0  .
```

The `.` (root) as the exchange, with preference 0, tells sending MTAs this domain accepts no mail.

### Mail Forwarding and Relaying Patterns

```
Scenario 1: Simple MX
  → MTA delivers directly to mail1.example.com

Scenario 2: Firewall relay
  mail1.example.com = external gateway (port 25 open)
  → relay to internal mail1-internal.example.com (not in MX, not externally accessible)

Scenario 3: Hosted email (e.g., Google Workspace)
  @  IN  MX  1   aspmx.l.google.com.
  @  IN  MX  5   alt1.aspmx.l.google.com.
  @  IN  MX  10  alt2.aspmx.l.google.com.
```

### SPF, DKIM, and DMARC (DNS-Based)

These are not BIND-specific but are DNS-published:

**SPF** (Sender Policy Framework) — TXT record:
```
example.com.  TXT  "v=spf1 ip4:203.0.113.0/24 mx include:_spf.google.com ~all"
```
Modifiers: `+` (pass), `-` (fail), `~` (softfail), `?` (neutral)

**DKIM** — Public key in TXT record:
```
selector._domainkey.example.com.  TXT  "v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3..."
```

**DMARC** — Policy TXT record:
```
_dmarc.example.com.  TXT  "v=DMARC1; p=quarantine; rua=mailto:dmarc@example.com"
```

---

## Chapter 6: Configuring Hosts

### resolv.conf

`/etc/resolv.conf` configures the stub resolver on UNIX/Linux systems:

```
# /etc/resolv.conf

# Up to 3 name server IPs (tried in order)
nameserver 192.168.1.1
nameserver 8.8.8.8
nameserver 8.8.4.4

# Search list: tried in order when a name has fewer dots than ndots
search example.com corp.example.com

# Alternative to search: single default domain
# domain example.com   (mutually exclusive with search)

# Options
options ndots:5         # Names with <5 dots get search appended (default: 1)
options timeout:2       # Seconds to wait per nameserver query (default: 5)
options attempts:3      # Retries per nameserver (default: 2)
options rotate          # Round-robin nameserver selection
options single-request  # Send A and AAAA queries sequentially, not in parallel
```

**`ndots` behavior:**
- If name has ≥ ndots dots → tried as absolute first, then with search domains appended
- If name has < ndots dots → search domains tried first, then absolute
- Default ndots=1: `www` gets search appended; `www.example.com` is tried as-is first

**`search` vs. `domain`:**
- `domain` sets a single default domain and the search list to that domain
- `search` sets a multi-domain search list; overrides `domain` if both present
- Maximum 6 domains in the search list (implementation limit)
- Longer search lists = more DNS queries per lookup; keep it short

### systemd-resolved (Modern Linux)

On systemd-based systems, `/etc/resolv.conf` may be a symlink to:
- `/run/systemd/resolve/stub-resolv.conf` → stub at 127.0.0.53
- `/run/systemd/resolve/resolv.conf` → actual upstream resolvers

Manage via:
```bash
resolvectl status
resolvectl dns eth0 192.168.1.1
resolvectl domain eth0 example.com
```

### nsswitch.conf

`/etc/nsswitch.conf` controls the **order** of name resolution (not just DNS):

```
# /etc/nsswitch.conf
hosts:    files dns myhostname
```

Sources:
- `files` → `/etc/hosts`
- `dns` → configured resolvers (resolv.conf)
- `myhostname` → systemd hostname resolution
- `mdns4_minimal` → mDNS for `.local` names (Avahi/nss-mdns)
- `nis` → NIS/YP (legacy)

**Order matters:** `files dns` means check `/etc/hosts` first, then DNS. To always prefer DNS: `dns files`.

**Actions (in brackets):**
```
hosts: files [NOTFOUND=return] dns
```
If `/etc/hosts` returns NOTFOUND, return immediately (don't try DNS). Actions: `return`, `continue`, `merge`.

### /etc/hosts

```
# /etc/hosts
127.0.0.1   localhost
::1         localhost ip6-localhost ip6-loopback
203.0.113.10  www.example.com  www

# Multiple aliases on one line are all valid
192.168.1.100  server1.example.com  server1  app-server
```

Format: `IP address` followed by canonical name, then optional aliases.

### host.conf (Legacy)

On older systems, `/etc/host.conf` controlled resolution order before nsswitch:
```
order hosts,bind
multi on
```
Largely superseded by nsswitch.conf on modern systems; may still be present.

### DNS Search and Negative Caching Impact

Each unqualified name lookup with a 3-entry search list generates **3 DNS queries** if not found (one per domain in the search list). Short TTL on NXDOMAIN (the SOA negative TTL field) controls how long these failures are cached.

Keep search lists short and use FQDNs (with trailing dot) in application configs where possible.

### Testing Host Resolution

```bash
# Uses nsswitch.conf (full resolution path including /etc/hosts)
getent hosts www.example.com

# DNS only (bypasses /etc/hosts)
dig www.example.com
host www.example.com

# Check what resolver a process will use
cat /etc/resolv.conf
resolvectl status   # systemd-resolved systems
```
