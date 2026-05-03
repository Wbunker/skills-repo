# Chapter 7: Cyrus IMAP

Cyrus IMAP is an enterprise-grade IMAP server developed at Carnegie Mellon University. It is widely used at universities and large ISPs. Unlike Dovecot, Cyrus uses its own proprietary mailbox format and runs as a standalone service not dependent on OS user accounts.

## Current Versions

- **Cyrus IMAP 3.x** — active branch (3.8.x as of 2025)
- Key features: Murder (proxy clustering), CalDAV/CardDAV, JMAP, Sieve, virtual domains

## Install

```bash
# Debian/Ubuntu
apt install cyrus-imapd cyrus-admin

# RHEL/Rocky
dnf install cyrus-imapd

# Start
systemctl enable --now cyrus-imapd
```

## Configuration Files

```
/etc/imapd.conf          # Main Cyrus configuration
/etc/cyrus.conf          # Process/service definitions (like inetd)
/var/lib/cyrus/          # Mailbox database, seen state, etc.
/var/spool/cyrus/mail/   # Mail store
```

## `imapd.conf` Key Settings

```
# Identity
servername: mail.example.com
admins: cyrusadmin

# Mail storage
partition-default: /var/spool/cyrus/mail
metapartition-default: /var/lib/cyrus

# Authentication (SASL)
sasl_pwcheck_method: auxprop
sasl_auxprop_plugin: sasldb
# Or with PAM:
# sasl_pwcheck_method: saslauthd

# TLS
tls_cert_file: /etc/letsencrypt/live/mail.example.com/fullchain.pem
tls_key_file: /etc/letsencrypt/live/mail.example.com/privkey.pem
tls_session_timeout: 1440

# Sieve
sieveusehomedir: 0
sievedir: /var/spool/sieve

# Quotas
defaultquota: 1073741824   # 1 GB in bytes
```

## `cyrus.conf` — Service Definitions

```
START {
  recover  cmd="ctl_cyrusdb -r"
  mboxlist cmd="ctl_mboxlist -m"
}

SERVICES {
  imap     cmd="imapd"    listen="imap"     prefork=5
  imaps    cmd="imapd -s" listen="imaps"    prefork=5
  pop3s    cmd="pop3d -s" listen="pop3s"    prefork=1
  sieve    cmd="timsieved" listen="sieve"   prefork=0
  lmtpunix cmd="lmtpd"   listen="/var/run/cyrus/socket/lmtp" prefork=1
}

EVENTS {
  checkpoint   cmd="ctl_cyrusdb -c" period=30
  delprune     cmd="cyr_expire -E 3" at=0401
  tlsprune     cmd="tls_prune" at=0401
}
```

## User Management with cyradm

`cyradm` is the Cyrus administrative shell.

```bash
# Launch as admin
cyradm --user cyrusadmin --server localhost

# In cyradm:
cyrus> lm                          # list all mailboxes
cyrus> cm user.alice               # create mailbox for alice
cyrus> dm user.alice               # delete alice's mailbox
cyrus> setquota user.alice 1048576 # 1 GB quota (in KB)
cyrus> listquota user.alice
cyrus> lam user.alice              # list ACLs
cyrus> sam user.alice alice lrswipcda  # set full ACL for alice on her own box
cyrus> renm user.alice user.alice_archive  # rename mailbox
```

### ACL Permissions

| Permission | Meaning |
|-----------|---------|
| `l` | lookup (mailbox is visible in LIST) |
| `r` | read messages |
| `s` | keep seen/unseen state |
| `w` | write flags (other than \Seen, \Deleted) |
| `i` | insert (APPEND) |
| `p` | post (deliver via LMTP) |
| `c` | create subfolders |
| `d` | delete messages / expunge |
| `a` | administer (set ACLs) |
| `x` | delete mailbox |
| `t` | set/clear \Deleted flag |
| `e` | perform EXPUNGE |

Full access: `lrswipcda`

## Delivering Mail with LMTP

In Postfix `main.cf`:
```
mailbox_transport = lmtp:unix:/var/run/cyrus/socket/lmtp
```

Or via network LMTP:
```
mailbox_transport = lmtp:inet:localhost:2003
```

## Virtual Domains

```
# imapd.conf
virtdomains: on
defaultdomain: example.com
```

Mailboxes use format `user@domain`:
```bash
cyradm> cm user/alice@otherdomain.com
```

## Sieve with Cyrus (timsieved)

Cyrus includes `timsieved` for ManageSieve (RFC 5804).

Upload a Sieve script with `sieveshell`:
```bash
sieveshell --user alice --server localhost
> put /tmp/alice.sieve myscript
> activate myscript
> list
> quit
```

Or use Roundcube/Thunderbird with ManageSieve plugin (port 4190 or 2000).

## Cyrus Murder (Distributed Clustering)

Cyrus Murder is a proxy/aggregation layer for multi-server Cyrus deployments:
- **Frontend** (mupdate master): receives connections, proxies to backends
- **Backend**: stores mail
- **Mupdate**: the mailbox location database

```
# imapd.conf on frontend
servername: imap-frontend.example.com
mupdate_server: mupdate.example.com
proxyservers: cyrusadmin
```

This is a major feature differentiating Cyrus from Dovecot (which uses director for proxying).

## Useful Cyrus CLI Tools

```bash
# List all mailboxes
ctl_mboxlist -d

# Quota report
quota -d example.com

# Reconstruct damaged mailbox
reconstruct -r user.alice

# Expire deleted messages
cyr_expire -E 7 -D 30  # expunge in 7 days, delete in 30

# Check mailbox consistency
cyrus_deliver -l  # list delivery queues

# Compact/checkpoint database
ctl_cyrusdb -c

# Generate DKIM or examine headers (via Postfix, not Cyrus directly)
```

## Key Differences: Cyrus vs Dovecot

| Aspect | Cyrus | Dovecot |
|--------|-------|---------|
| User accounts | Cyrus-internal, no OS users needed | Can use OS or virtual users |
| Mail format | Proprietary indexed | Maildir, mbox, dbox |
| Clustering | Murder architecture | Dovecot Director / Proxy |
| CalDAV/CardDAV | Built-in (3.x) | Separate plugin/integration |
| JMAP | Built-in (3.x) | Separate (stalwart or plugin) |
| Community | Smaller, academic/ISP | Larger, general-purpose |
| Documentation | Less approachable | Excellent docs |
| Default on | Fewer distros | Most distros default to Dovecot |
