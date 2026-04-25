# Chapter 10: IMAP Server Security

## Transport Security: TLS

**Always enforce TLS.** Plaintext IMAP over port 143 without STARTTLS is unacceptable on any production system.

### Implicit TLS vs STARTTLS

| Mode | Port | Behavior |
|------|------|----------|
| Implicit TLS (IMAPS) | 993 | TLS negotiated before any IMAP traffic |
| STARTTLS | 143 | Connection starts plain, client issues STARTTLS to upgrade |

**Prefer implicit TLS (port 993).** STARTTLS has a downgrade attack vector (STRIPTLS), though most modern clients mitigate this.

### Dovecot TLS Hardening

```
# conf.d/10-ssl.conf
ssl = required                  # Refuse all plaintext
ssl_min_protocol = TLSv1.2      # Disable TLS 1.0 and 1.1
ssl_cipher_list = EECDH+AESGCM:EDH+AESGCM:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA
ssl_prefer_server_ciphers = yes

# Certificate transparency via OCSP stapling
ssl_stapling = yes
ssl_stapling_verify = yes

ssl_cert = </etc/letsencrypt/live/mail.example.com/fullchain.pem
ssl_key = </etc/letsencrypt/live/mail.example.com/privkey.pem
```

Verify TLS configuration:
```bash
openssl s_client -connect mail.example.com:993 -crlf
testssl.sh mail.example.com:993
```

## Authentication Mechanisms (SASL)

### Common Mechanisms

| Mechanism | Security | Notes |
|-----------|----------|-------|
| `PLAIN` | Password in clear | Safe only over TLS; most common |
| `LOGIN` | Like PLAIN, legacy encoding | Deprecated but widely supported |
| `CRAM-MD5` | Challenge-response, no plaintext | Requires server to store clear/reversible passwords |
| `DIGEST-MD5` | Challenge-response | Deprecated (RFC 6331) |
| `GSSAPI` | Kerberos 5 | Enterprise SSO; no password over wire |
| `XOAUTH2` | OAuth2 bearer token | Required for Gmail/O365 modern auth |
| `OAUTHBEARER` | OAuth2 (RFC 7628) | IETF standard version of XOAUTH2 |
| `SCRAM-SHA-256` | Mutual auth, no plaintext | Modern best practice |

### Dovecot SASL Configuration

```
# conf.d/10-auth.conf
auth_mechanisms = plain login        # Minimum viable
# auth_mechanisms = plain login scram-sha-256 gssapi  # Expanded
disable_plaintext_auth = yes         # Enforce TLS before PLAIN/LOGIN
```

### OAuth2 / XOAUTH2 with Dovecot

For Gmail or Office 365 IMAP access via OAuth2:

```
# conf.d/auth-oauth2.conf.ext (Dovecot 2.3.11+)
passdb {
  driver = oauth2
  mechanisms = xoauth2 oauthbearer
  args = /etc/dovecot/dovecot-oauth2.conf.ext
}
```

```
# /etc/dovecot/dovecot-oauth2.conf.ext
tokeninfo_url = https://oauth2.googleapis.com/tokeninfo?access_token=
introspection_url = https://www.googleapis.com/oauth2/v3/tokeninfo
introspection_mode = post
username_attribute = email
tls_ca_cert_file = /etc/ssl/certs/ca-certificates.crt
```

## Brute-Force Protection

### Fail2ban

Install fail2ban and add IMAP jail:

```bash
apt install fail2ban
```

`/etc/fail2ban/jail.local`:
```ini
[dovecot]
enabled  = true
port     = imap,imaps,pop3,pop3s
filter   = dovecot
logpath  = /var/log/mail.log
maxretry = 5
bantime  = 3600
findtime = 600
```

`/etc/fail2ban/filter.d/dovecot.conf`:
```ini
[Definition]
failregex = auth failed, \d+ attempts in .* rip=<HOST>
            Aborted login .* rip=<HOST>
            Disconnected: .* auth failed .* rip=<HOST>
ignoreregex =
```

### Dovecot Built-in Rate Limiting

```
# conf.d/10-auth.conf
auth_failure_delay = 2 secs         # Slow down failed attempts
```

## Access Control Lists (ACLs)

IMAP ACLs (RFC 4314) allow sharing mailboxes between users.

### Dovecot ACLs

```
# conf.d/20-imap.conf
plugin {
  acl = vfile
}
```

ACL file for a mailbox at `~/Maildir/.Work/dovecot-acl`:
```
user=bob lrs    # bob can lookup, read, and keep seen state
user=carol lrswited  # carol can do more
anyone lr       # everyone can read (for public folders)
```

Via IMAP `SETACL` command:
```
A001 SETACL INBOX.Work bob lrs
A002 GETACL INBOX.Work
A003 DELETEACL INBOX.Work bob
```

### Cyrus ACLs

See `ch07-cyrus.md` — Cyrus uses `sam`/`lam`/`dam` in cyradm.

## Firewall Rules

Expose only required ports:

```bash
# ufw
ufw allow 25/tcp    # SMTP inbound
ufw allow 587/tcp   # Submission
ufw allow 993/tcp   # IMAPS
ufw allow 143/tcp   # IMAP + STARTTLS (optional; disable if only using 993)
ufw deny 110/tcp    # POP3 (block if not needed)
ufw deny 995/tcp    # POP3S (block if not needed)
```

Block IMAP access from outside if this is an internal server:
```bash
# Only allow IMAP from internal network
ufw allow from 10.0.0.0/8 to any port 993
ufw deny 993/tcp
```

## Master User / Admin Access

Dovecot master user allows admins to log in as any user without their password:

```
# conf.d/10-auth.conf
auth_master_user_separator = *

passdb {
  driver = passwd-file
  master = yes
  args = /etc/dovecot/master-users
  result_success = continue
}
```

`/etc/dovecot/master-users`:
```
masteradmin:{SHA256-CRYPT}$5$...
```

Login as master user:
```
# In any IMAP client: username = targetuser*masteradmin
```

## Logging for Security

```
# conf.d/10-logging.conf
log_path = /var/log/dovecot.log
info_log_path = /var/log/dovecot-info.log
debug_log_path = /var/log/dovecot-debug.log

# Log all logins (successful and failed)
auth_verbose = yes

# Log failed authentication details
auth_verbose_passwords = sha1    # Log SHA1 of bad password (for debugging)

# Log IP addresses
login_log_format_elements = user=<%u> method=%m rip=%r lip=%l mpid=%e %c %k
```

## Preventing Information Leakage

### Hide Dovecot Version

```
# conf.d/20-imap.conf
imap_capability = +IMAP4rev1  # Override capability response to hide version
```

### Greeting Message

```
# conf.d/20-imap.conf
login_greeting = Ready.       # Instead of "Dovecot ready." — hides server type
```

## Shared Mailboxes and Public Folders

Shared mailboxes for team access:

```
# conf.d/10-mail.conf
namespace shared {
  type = shared
  separator = /
  prefix = shared/%%u/
  location = maildir:/var/mail/shared/%%u
  subscriptions = no
  list = children
}

namespace public {
  type = public
  separator = /
  prefix = public/
  location = maildir:/var/mail/public
  subscriptions = yes
  list = yes
}
```

Set ACL to allow access:
```bash
# Allow all authenticated users to read the public folder
doveadm acl set -u admin@example.com public lrs
```

## Sieve for Security (Server-side Filtering)

Sieve can quarantine spam, reject unauthorized senders, and enforce organizational policies:

```sieve
require ["fileinto", "reject", "envelope", "spamtest"];

# Reject mail failing SPF/DKIM (set by milter in header)
if header :contains "X-Spam-Status" "Yes" {
  fileinto "Junk";
  stop;
}

# Reject from blocklist
if envelope :is "from" ["blockedsender@evil.com"] {
  reject "Not accepting mail from this sender.";
}
```
