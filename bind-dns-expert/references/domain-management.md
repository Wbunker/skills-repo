# Domain Management
## Chapters 8–9: Growing Your Domain, Parenting, Subdomains, Delegation

---

## Chapter 8: Growing Your Domain

### Organizing a Large Zone

As a domain grows, several strategies help manage scale:

**Multiple name servers:** Always run at least 2 authoritative servers (primary + secondary). The public NS records should list all servers so resolvers can fall back.

**Geographic distribution:** Place secondaries in different data centers and regions to reduce latency and improve resilience.

**Stealth (hidden) primary:** The primary server is not listed in NS records — only secondaries are publicly advertised. This protects the primary from direct attack and simplifies firewall rules.

```
; Public NS records (only secondaries listed):
example.com.  IN  NS  ns1-pub.example.com.
example.com.  IN  NS  ns2-pub.example.com.

; Secondary servers transfer from hidden primary at 10.0.0.1
; Primary named.conf:
zone "example.com" {
    type master;
    file "example.com.zone";
    also-notify { 203.0.113.100; 203.0.113.101; };   // Public secondaries
    allow-transfer { 203.0.113.100; 203.0.113.101; };
};
```

### Round-Robin Load Distribution

Multiple A records on the same name provide simple load balancing. BIND returns them in rotating order:

```
www.example.com.  IN  A  203.0.113.10
www.example.com.  IN  A  203.0.113.11
www.example.com.  IN  A  203.0.113.12
```

**Limitations:**
- No health checking — dead servers still receive traffic
- DNS caching means clients may get "stale" rotations
- Resolvers may reorder answers (RFC 3484 / Happy Eyeballs may pick the "best")
- For real load balancing, use a load balancer or anycast; DNS round-robin is supplementary

**`rrset-order` in BIND:**
```
options {
    rrset-order {
        class IN type A name "www.example.com" order cyclic;
        order random;   // Default: random order
    };
};
```
Options: `cyclic` (rotate), `random` (shuffle), `fixed` (as defined in zone file).

### TTL Tuning for Changes

Before a planned change (IP migration, server move):
1. Lower TTL to 300–600 seconds 24+ hours before the change
2. Make the change
3. Wait 2× old TTL for the change to propagate
4. Raise TTL back to normal after confirming

```
; Before change (lower TTL):
www.example.com.  600  IN  A  203.0.113.10

; After change:
www.example.com.  600  IN  A  203.0.113.20

; 24 hours after change, raise TTL:
www.example.com.  86400  IN  A  203.0.113.20
```

### CNAME Chains and Limitations

CNAMEs are useful for aliasing but have restrictions:
- **No CNAME at zone apex:** The zone name must have SOA, NS, and usually A records — a CNAME would replace all of them (use `ALIAS`/`ANAME` flattening in modern DNS providers for apex CNAME-like behavior)
- **No MX/NS pointing to CNAME:** MX and NS targets must resolve to A/AAAA records directly
- **Avoid deep chains:** Each CNAME adds a lookup round-trip; most resolvers follow up to 8 levels

---

## Chapter 9: Parenting — Creating Subdomains and Delegating

### Subdomain vs. Delegation

**Subdomain within the same zone:** Records for `dev.example.com` in the `example.com` zone file — no delegation, no separate SOA.

```
; In example.com zone — NOT delegated, just a host in the same zone:
dev.example.com.    IN  A  10.0.0.50
```

**Delegated subdomain:** `dev.example.com` becomes its own zone with its own SOA, managed on different name servers.

```
; In example.com zone — delegating dev.example.com to separate servers:
dev.example.com.    IN  NS  ns1.dev.example.com.
dev.example.com.    IN  NS  ns2.dev.example.com.

; Glue records (required because NS is within delegated zone):
ns1.dev.example.com.  IN  A  10.0.0.10
ns2.dev.example.com.  IN  A  10.0.0.11
```

### When to Delegate

Delegate when:
- A team/department wants administrative control over their own DNS
- The subdomain is large enough to warrant separate management
- The subdomain runs on different infrastructure / different security boundary
- You want different TTLs or DNSSEC policies in the subdomain

Don't delegate when:
- The subdomain is small and managed by the same team
- You want to keep DNS simple and centralized

### Glue Records

**Glue** is required when the NS records for a delegated zone point to hostnames **within** that delegated zone. Without glue, the resolver has a circular dependency: to find `ns1.dev.example.com`, it needs to look up `dev.example.com` — but it needs `ns1.dev.example.com` to do that.

The parent zone (`example.com`) must include A records for the delegating NS hosts:

```
; Parent zone: example.com
; Delegation:
dev         IN  NS  ns1.dev.example.com.
dev         IN  NS  ns2.dev.example.com.

; Glue (NS targets are in the child zone — glue needed):
ns1.dev     IN  A   10.0.0.10
ns2.dev     IN  A   10.0.0.11
```

If the NS hosts are **outside** the delegated zone (e.g., `ns1.third-party.net`), no glue is needed in the parent.

**Always verify glue is in place:**
```bash
dig @parent-ns dev.example.com NS        # Should return NS + glue in additional section
dig @root-server dev.example.com NS      # Trace from root
```

### Configuring the Child Zone

On the name servers for `dev.example.com`:

**named.conf:**
```
zone "dev.example.com" {
    type master;
    file "dev.example.com.zone";
    allow-transfer { 10.0.0.11; };
};
```

**dev.example.com.zone:**
```
$TTL 3600
$ORIGIN dev.example.com.

@       IN  SOA  ns1.dev.example.com.  hostmaster.dev.example.com. (
                 2024031501  3600  900  604800  300 )
@       IN  NS   ns1.dev.example.com.
@       IN  NS   ns2.dev.example.com.

ns1     IN  A    10.0.0.10
ns2     IN  A    10.0.0.11

; Child zone records
gitlab  IN  A    10.0.0.50
ci      IN  A    10.0.0.51
```

### Verifying Delegation

```bash
# Check that parent zone delegates correctly:
dig @ns1.example.com dev.example.com NS

# Check that child zone is authoritative:
dig @10.0.0.10 gitlab.dev.example.com A

# Trace the full resolution path:
dig +trace gitlab.dev.example.com A

# Check for lame delegation (NS doesn't answer for the zone):
dig @10.0.0.10 dev.example.com SOA
```

A **lame server** is one listed in an NS record that either doesn't respond or doesn't have authority for the zone. Lame delegations cause slow resolution and errors. BIND logs lame servers in the `lame-servers` category.

### SOA Serial Management During Delegation

After creating a child zone:
1. Add delegation NS + glue records to parent zone
2. Increment parent zone SOA serial
3. Reload parent (`rndc reload example.com`)
4. Verify parent sends correct referral
5. Start child zone servers

### Reverse Delegation

For IP space you own, request reverse delegation from your ISP or ARIN:
- ISP delegates `113.0.203.in-addr.arpa` to your name servers
- You manage PTR records for your addresses

ISP's zone must contain:
```
; In ISP's zone (0.203.in-addr.arpa):
113     IN  NS  ns1.example.com.
113     IN  NS  ns2.example.com.
```

Your `113.0.203.in-addr.arpa` zone:
```
$TTL 3600
@       IN  SOA  ns1.example.com.  hostmaster.example.com. (2024031501 3600 900 604800 300)
@       IN  NS   ns1.example.com.
@       IN  NS   ns2.example.com.

1       IN  PTR  ns1.example.com.
20      IN  PTR  www.example.com.
```

### Large-Scale Architecture Patterns

**Primary + multiple secondaries:**
```
            [Hidden Primary]
                   |
          ┌────────┼────────┐
    [ns1-pub]   [ns2-pub]  [ns3-pub]
    US-East      EU-West    APAC
```

**Anycast DNS:**
Multiple servers advertise the same IP via BGP routing; queries are served by the topologically closest node. Used by major DNS providers and root servers.

**Zone signing at primary, secondaries serve signed zone:**
- Sign zone on primary (or use inline-signing)
- Secondaries receive signed zone via AXFR — no signing keys needed on secondaries

### Common Parenting Mistakes

| Mistake | Consequence |
|---------|-------------|
| Missing glue records | Circular lookup dependency; zone unreachable |
| Glue in child zone only (not parent) | Parent sends referral without addresses |
| Parent NS records out of sync with child | Stale delegation; lame servers |
| Forgetting to increment SOA serial | Secondaries don't transfer; stale data |
| Delegating to a non-responsive server | Lame delegation, slow/failed resolution |
| Using the same SOA serial format inconsistently | Serial wrap-around confusion |
