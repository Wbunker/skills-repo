# Chapter 6 — Kerberos Security

## Attack Vectors

### AS-REP Roasting
When pre-authentication is **disabled** for a principal, any attacker can request a TGT for that account. The KDC responds with an AS_REP encrypted with the user's key (derived from their password). The attacker captures this response and performs an **offline dictionary attack** to crack the password.

**Mitigation:** Always enable pre-authentication (it is the default in MIT Kerberos). Audit with:
```bash
kadmin.local -q "getprinc username" | grep -i "requires pre"
# Should show: "REQUIRES_PRE_AUTH" flag
```

### Ticket Cracking / Kerberoasting
An authenticated user can request a service ticket for any SPN in the realm. The service ticket is encrypted with the service account's key. If the service account has a weak password, an attacker can crack the ticket offline.

**Mitigation:**
- Use **random, high-entropy keys** for service principals (`addprinc -randkey`)
- Use `AES256-CTS` encryption (computationally expensive to crack)
- Avoid using password-protected service principals where possible

### Replay Attacks
A captured authenticator could theoretically be replayed. Kerberos defends against this with:
- Timestamps in authenticators (rejected if outside clock skew window)
- **Replay cache** on the server side — the KDC and application servers track recently seen authenticators

### Pass-the-Ticket
An attacker with access to a credential cache file can steal tickets and use them directly without knowing the password. Tickets are valid until they expire.

**Mitigation:**
- Protect ccache files (default `/tmp/krb5cc_<uid>` — only readable by owner)
- Use short ticket lifetimes for sensitive services
- Use `kdestroy` in logout scripts

### Credential Forwarding Abuse
Forwardable tickets can be forwarded to another host, which can then act on behalf of the user. If a compromised intermediate host receives a forwardable TGT, it can impersonate the user to other services.

**Mitigation:** Do not grant `forwardable` tickets by default unless required for delegation (e.g., multi-tier applications). Configure per-service.

### Kerberos 4 Weaknesses
- Used single-DES (56-bit) — trivially crackable today
- No pre-authentication
- Double-DES cross-realm flaw (known cryptographic weakness)
- All Kerberos 4 usage should be eliminated

## Protecting the KDC

The KDC is the most critical host in a Kerberos infrastructure. Compromise = total realm compromise.

- **Physical security** — KDC should be in a locked server room
- **Minimal software** — Run nothing else on the KDC host; no web servers, no user accounts
- **Firewall** — Only allow port 88 (UDP+TCP) and 749 (kadmin, restricted to admin IPs) inbound
- **Offline master key** — Store the stash file (`/var/kerberos/krb5kdc/.k5.REALM`) securely; back up the database with `kdb5_util dump`
- **Slave KDCs** — Provide redundancy; slaves don't need port 749 open
- **OS hardening** — Minimize installed packages, apply patches, use SELinux/AppArmor

### KDC Backup

```bash
# Dump database (run on master)
kdb5_util dump /var/kerberos/krb5kdc/kerberos.dump

# Store dump + stash file + kdc.conf off-site securely
```

## Firewalls and NAT

Kerberos has challenges with firewalls and NAT:

| Port | Protocol | Purpose |
|------|----------|---------|
| 88 | UDP + TCP | Kerberos authentication |
| 464 | UDP + TCP | kpasswd (password changes) |
| 749 | TCP | kadmin (admin protocol) |

**NAT Issues:**
- Kerberos 4 embedded IP addresses in tickets — NAT breaks this completely
- Kerberos 5 makes addresses optional (`no_addresses = true` in krb5.conf) — NAT works when addresses are omitted
- For clients behind NAT: set `no_addresses = true` or `noaddresses = true` in `[libdefaults]`

**Firewall rules** must allow KDC ports from all client subnets. Use TCP fallback when UDP packets are fragmented (large Kerberos 5 tickets with PAC data can exceed 1500 bytes).

Force TCP:
```ini
[libdefaults]
    udp_preference_limit = 1  # Forces TCP
```

## Auditing

The KDC logs every authentication event. Enable logging in `krb5.conf`:

```ini
[logging]
    kdc = FILE:/var/log/krb5kdc.log
    admin_server = FILE:/var/log/kadmind.log
    default = SYSLOG:NOTICE:DAEMON
```

Each successful TGT and service ticket issuance is logged with timestamp, principal, and client address. Forward logs to a SIEM for correlation and alerting.

## Strong Encryption Recommendations

Prefer **AES256-CTS-HMAC-SHA1-96** and **AES128-CTS-HMAC-SHA1-96**. Disable legacy DES and RC4-HMAC where possible:

```ini
[libdefaults]
    default_tgs_enctypes = aes256-cts aes128-cts
    default_tkt_enctypes = aes256-cts aes128-cts
    permitted_enctypes = aes256-cts aes128-cts
```

Disable RC4-HMAC (NT Hash-based) unless required for Windows XP/2003 compatibility.
