# Chapter 5: Planning Your IMAP Installation

## Choosing a Server

| Server | Best For | Avoid If |
|--------|----------|----------|
| **Dovecot** | Most deployments; excellent docs, active dev, Postfix integration | No reason to avoid |
| **Cyrus IMAP** | Large ISPs, murder clustering, deep groupware integration | Small shops (complex) |
| **Stalwart Mail** | Modern, Rust-based, IMAP4rev2 native, JMAP | Requires newer OS |
| **Exchange IMAP** | Already running Exchange | Standalone IMAP is better |
| **Hosted (Fastmail, etc.)** | No ops staff, minimal budget for infra | Regulatory/data-residency needs |

**For new deployments: choose Dovecot + Postfix.** It is the industry default for self-hosted IMAP.

## Hardware Sizing

### Storage

IMAP is storage-intensive — mail lives on the server permanently.

| User Profile | Avg Mailbox Size | Notes |
|-------------|-----------------|-------|
| Light user | 1–5 GB | Basic correspondence |
| Business user | 5–20 GB | Attachments, long history |
| Power user | 20–50 GB+ | Heavy attachments, archives |

**Sizing formula:**
```
Total storage = (avg mailbox size × user count) × 2.5
(factor 2.5 = 1.5× for growth + backup headroom)
```

**Storage recommendations:**
- Use **Maildir** format — one file per message, avoids mbox locking
- Mount mail store on dedicated partition or LVM volume
- Use XFS or ext4 with `dir_index` for large directories
- SSD for active mail; HDD or object storage for archival

### I/O Profile

IMAP is read-heavy with bursts of sequential writes at delivery. Key metrics:
- **IOPS**: 1–5 IOPS per concurrent active user
- **RAM**: Cache improves performance significantly; budget 1–2 GB per 1000 users
- **Concurrent connections**: IMAP IDLE keeps connections open — 1 persistent connection per active client

### CPU

IMAP is not CPU-intensive unless you run server-side full-text search (FTS). With FTS (Solr, Xapian, Lucene):
- Indexing can spike CPU on large mailboxes
- Run FTS on a separate process or machine if possible

## Network and Firewall

### Required Ports

| Port | Protocol | Required By |
|------|----------|------------|
| 25 | SMTP | Inbound mail delivery (MX) |
| 587 | Submission | Authenticated SMTP from clients |
| 993 | IMAPS | IMAP clients (implicit TLS) |
| 143 | IMAP+STARTTLS | Optional; some clients need it |
| 4190 | ManageSieve | Sieve script management by clients |

### Firewall Rules (example: nftables)

```nft
table inet filter {
  chain input {
    tcp dport { 25, 587, 993, 143, 4190 } accept
    tcp dport 22 accept  # SSH admin
    ct state established,related accept
    drop
  }
}
```

## Directory Integration

Most organizations want IMAP authentication tied to a directory.

### LDAP

Dovecot supports LDAP authentication natively:
```
# /etc/dovecot/conf.d/auth-ldap.conf.ext
passdb {
  driver = ldap
  args = /etc/dovecot/dovecot-ldap.conf.ext
}
userdb {
  driver = ldap
  args = /etc/dovecot/dovecot-ldap.conf.ext
}
```

### Active Directory

- Use LDAP passdb with AD (Kerberos GSSAPI or LDAP bind)
- Or use `auth_mechanisms = gssapi` with a Kerberos keytab
- Dovecot can use `%u` (username) and `%d` (domain) for multi-domain AD setups

### Local Users vs Virtual Users

| Mode | Storage | Auth | Use When |
|------|---------|------|---------|
| System users | `/home/user/Maildir` | PAM / `/etc/passwd` | Small single-domain setups |
| Virtual users | `/var/mail/vhosts/domain/user` | SQL or LDAP | Multi-domain hosting |

Virtual user example (MySQL):
```sql
CREATE TABLE users (
  username VARCHAR(100) NOT NULL,
  domain   VARCHAR(100) NOT NULL,
  password VARCHAR(255) NOT NULL,
  uid      INT DEFAULT 5000,
  gid      INT DEFAULT 5000,
  home     VARCHAR(255),
  PRIMARY KEY (username, domain)
);
```

## DNS Setup

Required DNS records for a mail server:

```dns
; MX record
example.com.        IN MX  10  mail.example.com.

; A / AAAA for mail server
mail.example.com.   IN A   203.0.113.10
mail.example.com.   IN AAAA 2001:db8::1

; PTR (reverse DNS — required for SMTP reputation)
10.113.0.203.in-addr.arpa.  IN PTR  mail.example.com.

; SPF
example.com.  IN TXT  "v=spf1 mx -all"

; DKIM (add after generating key)
mail._domainkey.example.com.  IN TXT  "v=DKIM1; k=rsa; p=..."

; DMARC
_dmarc.example.com.  IN TXT  "v=DMARC1; p=quarantine; rua=mailto:dmarc@example.com"

; Autoconfig
autoconfig.example.com.  IN A  203.0.113.10

; SRV for IMAP
_imaps._tcp.example.com.  IN SRV  0 1 993 mail.example.com.
```

## TLS Certificate

Use Let's Encrypt via certbot:
```bash
certbot certonly --standalone -d mail.example.com
# Renew hook to reload Dovecot:
# /etc/letsencrypt/renewal-hooks/deploy/reload-dovecot.sh
# #!/bin/bash
# systemctl reload dovecot
```

Certificate paths:
- Cert: `/etc/letsencrypt/live/mail.example.com/fullchain.pem`
- Key: `/etc/letsencrypt/live/mail.example.com/privkey.pem`

## Pre-Installation Checklist

- [ ] OS chosen (Debian/Ubuntu LTS or RHEL/Rocky recommended)
- [ ] Hostname set and resolvable (`hostname -f` returns FQDN)
- [ ] PTR / rDNS set with ISP for mail IP
- [ ] Firewall rules applied
- [ ] TLS certificate obtained
- [ ] Storage partition mounted at `/var/mail` or `/home`
- [ ] Directory (LDAP/AD/SQL) or local user list ready
- [ ] DNS MX, SPF, DKIM, DMARC planned
