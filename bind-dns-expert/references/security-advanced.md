# Advanced Features and Security
## Chapter 10: TSIG, DNSSEC, Views, ACLs, Response Policy Zones

---

## Access Control Lists (ACLs)

BIND's `acl` statement creates named address match lists used across configuration.

```
// Define reusable ACLs
acl "trusted-internal" {
    10.0.0.0/8;
    192.168.0.0/16;
    172.16.0.0/12;
    127.0.0.1;
    ::1;
};

acl "secondary-servers" {
    203.0.113.2;   // ns2
    203.0.113.3;   // ns3
};

options {
    allow-query     { any; };                    // Public queries OK
    allow-recursion { trusted-internal; };       // Only internal clients get recursion
    allow-transfer  { secondary-servers; };      // Only secondaries can transfer
};
```

### Applying ACLs to Zones

```
zone "internal.example.com" {
    type master;
    file "internal.zone";
    allow-query    { trusted-internal; };   // Hide from external
    allow-transfer { secondary-servers; };
    allow-update   { none; };
};
```

### ACL Match Elements

- IPv4 CIDR: `192.168.0.0/24`
- IPv6 CIDR: `2001:db8::/32`
- Named ACL: `trusted-internal`
- TSIG key: `key "transfer-key"`
- `any` — matches all
- `none` — matches nothing
- `!` prefix — negation: `!10.0.0.0/8` excludes that range
- `localhost` — built-in: all loopback interfaces
- `localnets` — built-in: all directly connected networks

---

## TSIG — Transaction Signature

TSIG (RFC 2845) authenticates DNS messages (zone transfers, NOTIFY, dynamic updates, rndc) using shared HMAC keys. Prevents unauthorized transfers and spoofed updates.

### Generating a TSIG Key

```bash
# Generate with tsig-keygen (BIND 9.9+)
tsig-keygen -a hmac-sha256 secondary-transfer-key

# Output (add to named.conf on both servers):
key "secondary-transfer-key" {
    algorithm hmac-sha256;
    secret "base64encodedkeyhere==";
};
```

Supported algorithms: `hmac-md5` (legacy), `hmac-sha1`, `hmac-sha224`, `hmac-sha256` (recommended), `hmac-sha384`, `hmac-sha512`.

### Configuring TSIG for Zone Transfers

**On the primary (`named.conf`):**
```
key "secondary-transfer-key" {
    algorithm hmac-sha256;
    secret "base64encodedkeyhere==";
};

server 203.0.113.2 {
    keys { secondary-transfer-key; };   // Use this key when talking to this server
};

zone "example.com" {
    type master;
    file "example.com.zone";
    allow-transfer { key secondary-transfer-key; };   // Only allow with valid TSIG
};
```

**On the secondary (`named.conf`):**
```
key "secondary-transfer-key" {
    algorithm hmac-sha256;
    secret "base64encodedkeyhere==";     // Must match primary exactly
};

server 203.0.113.1 {
    keys { secondary-transfer-key; };
};

zone "example.com" {
    type slave;
    masters { 203.0.113.1; };
    file "slaves/example.com.zone";
};
```

### TSIG for Dynamic Updates

```
key "ddns-key" {
    algorithm hmac-sha256;
    secret "another-base64-key==";
};

zone "example.com" {
    type master;
    allow-update { key ddns-key; };
};
```

Test with nsupdate:
```bash
nsupdate -k /etc/named/ddns-key.conf
> server 127.0.0.1
> update add test.example.com 60 A 10.0.0.99
> send
```

---

## Views

Views allow a single BIND instance to return different answers to different clients — typically split DNS: internal clients see private addresses, external clients see public addresses.

### Basic Split-DNS Configuration

```
acl "internal" { 10.0.0.0/8; 192.168.0.0/16; };

view "internal" {
    match-clients { internal; };
    recursion yes;
    allow-recursion { internal; };

    zone "example.com" {
        type master;
        file "example.com.internal.zone";  // Has private IPs (10.x.x.x)
    };

    zone "." { type hint; file "named.ca"; };
};

view "external" {
    match-clients { any; };
    recursion no;

    zone "example.com" {
        type master;
        file "example.com.external.zone";  // Has public IPs
    };
};
```

**Rules:**
- All zones must be declared inside views if views are used — you cannot mix view and non-view zones
- Views are matched in order; first match wins
- Root hints zone must be in every view that does recursion
- TSIG keys can be used with `match-clients { key mykey; }` to route by key

### Views with DNSSEC

Each view needs its own DNSSEC configuration:
```
view "external" {
    dnssec-validation auto;
    zone "example.com" {
        type master;
        file "example.com.zone.signed";
        auto-dnssec maintain;
        inline-signing yes;
    };
};
```

---

## DNSSEC — DNS Security Extensions

DNSSEC adds cryptographic signatures to DNS data, allowing resolvers to verify that records are authentic and unmodified.

### How DNSSEC Works

```
Zone signing:
1. Zone has DNSKEY records (public keys)
2. Each RRset is signed with RRSIG records (digital signatures)
3. NSEC/NSEC3 records prove negative existence (NXDOMAIN is authenticated)
4. DS records in parent zone create a chain of trust

Validation:
1. Resolver gets DNSKEY for zone
2. Checks DS record in parent zone matches DNSKEY
3. Verifies RRSIG on returned records using DNSKEY
4. Chains up to the root (whose trust anchor is built into BIND)
```

### Key Types

| Key | Abbreviation | Purpose |
|-----|-------------|---------|
| Zone Signing Key | ZSK | Signs individual RRsets (rotated frequently, e.g., monthly) |
| Key Signing Key | KSK | Signs the DNSKEY RRset only (rotated rarely, e.g., annually) |

The KSK's fingerprint (DS record) is published in the parent zone by the registrar/registry.

### Setting Up DNSSEC (Manual Method)

```bash
# 1. Generate KSK and ZSK
cd /var/named
dnssec-keygen -a RSASHA256 -b 2048 -f KSK example.com     # KSK
dnssec-keygen -a RSASHA256 -b 1024 example.com             # ZSK
# Generates Kexample.com.+008+NNNNN.key and .private files

# 2. Include public keys in zone file
echo '$INCLUDE Kexample.com.+008+NNNNN.key'   >> example.com.zone  # KSK
echo '$INCLUDE Kexample.com.+008+MMMMM.key'   >> example.com.zone  # ZSK

# 3. Sign the zone
dnssec-signzone -o example.com -t example.com.zone
# Creates: example.com.zone.signed

# 4. Use signed zone in named.conf
zone "example.com" {
    type master;
    file "example.com.zone.signed";   // Use signed file
};

# 5. Get DS record for parent
dnssec-dsfromkey Kexample.com.+008+NNNNN.key    // From KSK
# Submit DS record to registrar
```

### Inline Signing (Recommended for BIND 9.9+)

Avoids manual signing; BIND signs automatically when the zone is loaded or updated:

```
zone "example.com" {
    type master;
    file "example.com.zone";       // Unsigned; BIND manages signed version
    key-directory "/var/named/keys/example.com";   // Where BIND looks for keys
    auto-dnssec maintain;          // Automatically sign, re-sign, roll keys
    inline-signing yes;            // Sign on the fly without modifying zone file
    serial-update-method unixtime; // Auto-increment serial on signing
};
```

BIND auto-signs and re-signs before RRSIGs expire (default: resign 2× the signature-validity-interval before expiry).

### DNSSEC Validation

To enable validation on a recursive resolver:

```
options {
    dnssec-validation auto;   // Uses built-in root trust anchor (recommended)
    // Or: dnssec-validation yes;  // Requires explicit trusted-keys/managed-keys
};
```

To test DNSSEC validation:
```bash
dig +dnssec www.example.com A            # Request DNSSEC records
dig +sigchase www.example.com A          # Chase signature chain (older dig)
dig @127.0.0.1 dnssec-failed.example.com A   # Should return SERVFAIL if DNSSEC works
```

### NSEC vs. NSEC3

- **NSEC**: Proves nonexistence by listing the next name in canonical order. Allows zone enumeration (zone walking) — can reveal all names in the zone.
- **NSEC3**: Uses hashed names — prevents zone walking. Use with `opt-out` for large zones with many unsigned delegations.

```bash
# Configure NSEC3 (add to zone or use with dnssec-signzone):
dnssec-signzone -3 $(openssl rand -hex 8) -H 10 -o example.com example.com.zone
# -3: use NSEC3; random salt; 10 iterations
```

### DS Record and Registrar

After signing, get the DS record and submit to your registrar:

```bash
dnssec-dsfromkey -a SHA-256 Kexample.com.+013+NNNNN.key
# example.com. IN DS NNNNN 13 2 [hash]
```

Most registrars accept this via their web UI or API. The registrar publishes it in the TLD zone.

### Key Rollover

**ZSK rollover (pre-publish method):**
1. Generate new ZSK, add public key to zone (DNSKEY)
2. Wait for old ZSK's max TTL to expire (resolvers cache the new DNSKEY)
3. Sign zone with new ZSK
4. Wait for old signatures to expire
5. Remove old ZSK from zone

**KSK rollover (double-signature method):**
1. Generate new KSK, add to zone
2. Submit new DS record to parent (both DS records active simultaneously)
3. Wait for old DS TTL to expire
4. Remove old KSK from zone
5. Remove old DS from parent

`auto-dnssec maintain` handles ZSK rollover automatically. KSK rollover requires parent interaction.

---

## Response Policy Zones (RPZ)

RPZ (DNS Firewall) lets BIND intercept and modify DNS responses based on policy rules, used for: malware blocking, phishing protection, split horizon, parental controls.

```
// named.conf:
options {
    response-policy {
        zone "rpz.example.com";
        zone "rpz.threat-intel.com";
    };
};

zone "rpz.example.com" {
    type master;
    file "rpz.example.com.zone";
    // Or type slave for a threat feed
};
```

**RPZ zone file triggers:**
```
; Block a domain (NXDOMAIN):
malware.example.com         IN  CNAME  .

; Redirect a domain to walled garden:
phishing.example.com        IN  A  192.168.100.1

; Block a specific IP (RPF_IP trigger):
32.1.2.3.4.rpz-ip           IN  CNAME  .

; Block any name served by a specific NS:
ns1.malware-registrar.com.rpz-nsdname  IN  CNAME .
```

Wildcards in RPZ:
```
*.malware.example.com  IN  CNAME .    ; Block all subdomains
```

RPZ actions:
- `CNAME .` → NXDOMAIN (block)
- `CNAME *.` → NODATA
- `A 127.0.0.1` → Redirect to walled garden
- `CNAME rpz-passthru.` → Allow through (whitelist, overrides other policies)
- `CNAME rpz-drop.` → Drop (no response)

---

## Additional Security Hardening

### Hide Version String

```
options {
    version "not disclosed";
};
// Test: dig @ns1.example.com version.bind CHAOS TXT
```

### Rate Limiting (DNS Amplification Defense)

```
options {
    rate-limit {
        responses-per-second 10;
        referrals-per-second 5;
        errors-per-second 5;
        all-per-second 1000;
        slip 2;              // 1-in-N responses are real (rest are truncated/dropped)
        window 15;           // Counting window in seconds
        log-only no;         // Set yes to monitor without enforcing
    };
};
```

### Minimal Responses

Return only the records directly requested (no additional section data), reducing amplification:

```
options {
    minimal-responses yes;
};
```

### Restricting Recursion

```
options {
    recursion yes;
    allow-recursion { 10.0.0.0/8; 127.0.0.1; };  // Internal only
    allow-query-cache { 10.0.0.0/8; 127.0.0.1; }; // Cache access also restricted
};
```
