# Chapter 6: Dovecot

Dovecot is the most widely deployed open-source IMAP/POP3 server. It replaced UW-IMAP as the de facto standard. This chapter covers current Dovecot (2.3.x / 2.4.x).

## Install

```bash
# Debian/Ubuntu
apt install dovecot-imapd dovecot-pop3d dovecot-lmtpd

# RHEL/Rocky
dnf install dovecot

# With LDAP/SQL support
apt install dovecot-ldap dovecot-mysql dovecot-pgsql
```

## Configuration Layout

```
/etc/dovecot/
├── dovecot.conf          # Main config (includes conf.d/*)
└── conf.d/
    ├── 10-auth.conf      # Authentication
    ├── 10-logging.conf   # Logging
    ├── 10-mail.conf      # Mail location and storage
    ├── 10-master.conf    # Service sockets and processes
    ├── 10-ssl.conf       # TLS configuration
    ├── 15-mailboxes.conf # Special-use mailbox definitions
    ├── 20-imap.conf      # IMAP-specific settings
    ├── 20-lmtp.conf      # LMTP delivery
    ├── 90-sieve.conf     # Sieve filtering
    ├── auth-ldap.conf.ext
    ├── auth-sql.conf.ext
    └── auth-passwdfile.conf.ext
```

## Minimal Working Configuration

### `/etc/dovecot/dovecot.conf`
```
protocols = imap lmtp
```

### `conf.d/10-mail.conf`
```
# Maildir for system users
mail_location = maildir:~/Maildir

# Virtual users in /var/mail/vhosts
# mail_location = maildir:/var/mail/vhosts/%d/%n/Maildir
```

### `conf.d/10-auth.conf`
```
disable_plaintext_auth = yes
auth_mechanisms = plain login

# Uncomment one:
!include auth-system.conf.ext
# !include auth-ldap.conf.ext
# !include auth-sql.conf.ext
```

### `conf.d/10-ssl.conf`
```
ssl = required
ssl_cert = </etc/letsencrypt/live/mail.example.com/fullchain.pem
ssl_key = </etc/letsencrypt/live/mail.example.com/privkey.pem
ssl_min_protocol = TLSv1.2
ssl_cipher_list = EECDH+AESGCM:EDH+AESGCM
ssl_prefer_server_ciphers = yes
```

### `conf.d/10-master.conf` (LMTP socket for Postfix)
```
service lmtp {
  unix_listener /var/spool/postfix/private/dovecot-lmtp {
    mode = 0600
    user = postfix
    group = postfix
  }
}
service auth {
  unix_listener /var/spool/postfix/private/auth {
    mode = 0666
    user = postfix
    group = postfix
  }
}
```

## Authentication: SQL (Virtual Users)

### `conf.d/auth-sql.conf.ext`
```
passdb {
  driver = sql
  args = /etc/dovecot/dovecot-sql.conf.ext
}
userdb {
  driver = sql
  args = /etc/dovecot/dovecot-sql.conf.ext
}
```

### `/etc/dovecot/dovecot-sql.conf.ext`
```
driver = mysql
connect = host=127.0.0.1 dbname=mailserver user=mail password=secret

default_pass_scheme = SHA512-CRYPT

password_query = \
  SELECT password FROM users \
  WHERE username = '%u'

user_query = \
  SELECT 5000 AS uid, 5000 AS gid, \
    CONCAT('/var/mail/vhosts/', domain, '/', local_part) AS home \
  FROM users \
  WHERE username = '%u'
```

## Authentication: LDAP

### `/etc/dovecot/dovecot-ldap.conf.ext`
```
hosts = ldap.example.com
dn = cn=dovecot,dc=example,dc=com
dnpass = bindpassword
ldap_version = 3
base = ou=users,dc=example,dc=com
user_attrs = homeDirectory=home,uidNumber=uid,gidNumber=gid
user_filter = (&(objectClass=posixAccount)(uid=%u))
pass_attrs = uid=user,userPassword=password
pass_filter = (&(objectClass=posixAccount)(uid=%u))
default_pass_scheme = CRYPT
```

## Namespaces

```
# conf.d/10-mail.conf or conf.d/15-mailboxes.conf
namespace inbox {
  type = private
  separator = /
  prefix =
  inbox = yes

  mailbox Drafts   { special_use = \Drafts;   auto = subscribe; }
  mailbox Junk     { special_use = \Junk;     auto = subscribe; }
  mailbox Sent     { special_use = \Sent;     auto = subscribe; }
  mailbox Trash    { special_use = \Trash;    auto = subscribe; }
  mailbox Archive  { special_use = \Archive;  auto = no; }
}
```

`special_use` maps to RFC 6154 LIST-EXTENDED special-use flags, which clients use to auto-detect folder roles.

## Quota

```
# conf.d/90-quota.conf
plugin {
  quota = maildir:User quota
  quota_rule = *:storage=10G
  quota_rule2 = Trash:storage=+100M  # Trash gets extra 100 MB
  quota_warning = storage=95%% quota-warning 95 %u
  quota_warning2 = storage=80%% quota-warning 80 %u
}

service quota-warning {
  executable = script /usr/lib/dovecot/quota-warning.sh
  unix_listener quota-warning {
    user = dovecot
  }
}
```

Check quota:
```bash
doveadm quota get -u user@example.com
```

## Full-Text Search (FTS)

Dovecot supports FTS via plugins. Xapian (via `fts_xapian`) is the current recommendation:

```bash
apt install dovecot-fts-xapian
```

```
# conf.d/90-fts.conf
plugin {
  fts = xapian
  fts_xapian = partial=2 full=20
  fts_autoindex = yes
  fts_autoindex_exclude = \Junk
}
```

Trigger initial index:
```bash
doveadm index -u user@example.com -q '*'
```

## Sieve Filtering

Sieve is server-side mail filtering (RFC 5228). Dovecot uses the Pigeonhole plugin:

```bash
apt install dovecot-sieve dovecot-managesieved
```

```
# conf.d/90-sieve.conf
plugin {
  sieve = file:~/sieve;active=~/.dovecot.sieve
  sieve_default = /var/lib/dovecot/sieve/default.sieve
}
service managesieve-login {
  inet_listener sieve { port = 4190; }
}
service managesieve { }
```

Example Sieve script (`~/.dovecot.sieve`):
```sieve
require ["fileinto", "reject", "envelope"];

if envelope :is "to" "spam-trap@example.com" {
  reject "Not accepting mail here.";
}
if header :contains "Subject" "[BULK]" {
  fileinto "Junk";
  stop;
}
```

## LMTP Integration with Postfix

In Postfix `main.cf`:
```
mailbox_transport = lmtp:unix:private/dovecot-lmtp
virtual_transport = lmtp:unix:private/dovecot-lmtp
```

For virtual domains:
```
virtual_mailbox_domains = mysql:/etc/postfix/mysql-virtual-mailbox-domains.cf
virtual_mailbox_maps = mysql:/etc/postfix/mysql-virtual-mailbox-maps.cf
virtual_alias_maps = mysql:/etc/postfix/mysql-virtual-alias-maps.cf
```

## Useful doveadm Commands

```bash
# List all users' mail locations
doveadm user '*'

# Force password check
doveadm auth test user@example.com password

# Show user's mailboxes
doveadm mailbox list -u user@example.com

# Expunge old Trash messages
doveadm expunge -u user@example.com mailbox Trash savedbefore 30d

# Move messages
doveadm move -u user@example.com Junk mailbox INBOX subject "Buy Now"

# Check quota
doveadm quota get -u user@example.com

# Rebuild index
doveadm index -u user@example.com '*'

# Kick active connection
doveadm kick user@example.com

# Who is logged in
doveadm who

# Show stats
doveadm stats dump
```

## Log Locations

```
/var/log/mail.log        # Debian/Ubuntu (via syslog)
/var/log/maillog         # RHEL/Rocky
journalctl -u dovecot    # systemd systems
```

Enable verbose auth logging for debugging:
```
# conf.d/10-logging.conf
auth_verbose = yes
auth_debug = yes
mail_debug = yes
```
