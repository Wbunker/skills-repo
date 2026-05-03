# Chapter 11: Self-Hosted Email Stacks (2026)

In 2026, most self-hosted IMAP deployments use a pre-integrated stack rather than configuring Dovecot from scratch. These stacks wrap Postfix + Dovecot (or equivalent) with web UIs, automated TLS, spam filtering, and admin panels.

## Mailcow

The most popular self-hosted stack. Runs as Docker Compose.

**Components:**
- Postfix (MTA)
- Dovecot (IMAP/POP3)
- SOGo (webmail + CalDAV/CardDAV)
- Rspamd (spam filtering)
- ClamAV (antivirus, optional)
- Nginx (reverse proxy)
- MariaDB + Redis

**Install:**
```bash
git clone https://github.com/mailcow/mailcow-dockerized
cd mailcow-dockerized
./generate_config.sh   # prompts for hostname
docker compose up -d
```

**Key files:**
```
mailcow.conf           # Main config (MAILCOW_HOSTNAME, etc.)
docker-compose.yml
data/conf/postfix/
data/conf/dovecot/
data/conf/rspamd/
```

**Web UI:** `https://mail.example.com` — manages domains, mailboxes, aliases, DKIM, spam policies

**IMAP access:** port 993 (IMAPS), standard Dovecot under the hood — all `ch06-dovecot.md` applies

**Update:**
```bash
./update.sh
```

**Mailcow-specific customizations:**
- Custom Dovecot settings go in `data/conf/dovecot/extra.conf`
- Custom Postfix in `data/conf/postfix/extra.cf`
- Rspamd web UI at `https://mail.example.com/rspamd`

---

## Mailu

Lighter-weight Docker stack. Simpler than Mailcow; fewer moving parts.

**Components:**
- Postfix (MTA)
- Dovecot (IMAP)
- Roundcube or SnappyMail (webmail)
- Rspamd (spam)
- Nginx (reverse proxy)
- SQLite or PostgreSQL

**Install via setup wizard:**
```
https://setup.mailu.io/2024/   # generates docker-compose.yml + mailu.env
```

Then:
```bash
docker compose -p mailu up -d
```

**Config file:** `mailu.env` — all settings in one place:
```
DOMAIN=example.com
HOSTNAMES=mail.example.com
SECRET_KEY=...
TLS_FLAVOR=letsencrypt
WEBMAIL=roundcube
SPAM_THRESHOLD=80
```

**Differences from Mailcow:**
| | Mailcow | Mailu |
|---|---------|-------|
| Complexity | Higher | Lower |
| Web UI | Full-featured | Simpler |
| CalDAV/CardDAV | Via SOGo | No (use separate) |
| Groupware | Yes (SOGo) | No |
| Config | Per-service files | Single .env |
| Community | Larger | Smaller |

---

## docker-mailserver

Minimal, config-file-driven. No web UI — everything via CLI or config files. Good for ops-heavy teams who want control without a UI.

**Repo:** `https://github.com/docker-mailserver/docker-mailserver`

**Single container** (unlike Mailcow's ~15):
```bash
docker run -d \
  --name mailserver \
  -p 25:25 -p 143:143 -p 465:465 -p 587:587 -p 993:993 \
  -v ./docker-data/dms/mail-data/:/var/mail/ \
  -v ./docker-data/dms/mail-state/:/var/mail-state/ \
  -v ./docker-data/dms/mail-logs/:/var/log/mail/ \
  -v ./docker-data/dms/config/:/tmp/docker-mailserver/ \
  -v /etc/letsencrypt:/etc/letsencrypt:ro \
  --env-file .env \
  mailserver/docker-mailserver:latest
```

**Manage accounts with `setup.sh`:**
```bash
./setup.sh email add user@example.com password
./setup.sh email list
./setup.sh alias add alias@example.com user@example.com
./setup.sh config dkim
```

**Spam:** Rspamd or SpamAssassin (configurable)

**Best for:** Small setups, homelabs, infrastructure-as-code deployments

---

## Mail-in-a-Box

One-command setup for a complete mail server on a fresh Ubuntu VPS. Opinionated and non-customizable — designed for non-ops users.

```bash
curl -s https://mailinabox.email/setup.sh | sudo bash
```

**Installs:** Postfix, Dovecot, Roundcube, Nextcloud (contacts/calendar), Nginx, Let's Encrypt, Fail2ban, Spamassassin, DKIM/SPF/DMARC

**Admin panel:** `https://box.example.com/admin`

**Constraints:**
- Requires a fresh Ubuntu 22.04 LTS VPS
- Does not support multi-server / clustering
- Updates via `mailinabox` command
- Do not manually edit config files — the setup script will overwrite them

**Best for:** Non-technical users or those who want a complete server with zero manual config

---

## Stalwart Mail (Self-contained)

Not a stack — a single Rust binary that handles SMTP, IMAP, JMAP, ManageSieve, and admin UI. Notable because it replaces the entire Postfix + Dovecot combination.

```bash
# Docker
docker run -d \
  -p 25:25 -p 993:993 -p 443:443 -p 8080:8080 \
  -v stalwart-data:/opt/stalwart \
  stalwartlabs/mail-server:latest

# Or bare-metal install script
curl -fsSL https://stalw.art/install | bash
```

**Admin UI:** `http://localhost:8080`

**Key differentiators vs Dovecot stacks:**
- Single binary — no separate MTA
- Native IMAP4rev2 (RFC 9051)
- Native JMAP (RFC 8620)
- WebAdmin with full configuration UI
- Built-in spam filtering (bayes + greylisting)
- S3-compatible object storage backend option

**Config:** TOML files or entirely via the web UI

---

## Choosing a Stack

| Need | Recommended |
|------|-------------|
| Full-featured with groupware (calendar, contacts) | **Mailcow** |
| Simple, low-maintenance | **Mailu** |
| Infrastructure-as-code, no UI needed | **docker-mailserver** |
| Non-technical user, one VPS | **Mail-in-a-Box** |
| Modern single binary, JMAP | **Stalwart Mail** |
| Enterprise, clustering, custom integrations | **Bare Dovecot + Postfix** |

---

## Stack vs Bare Dovecot: When to Go Bare

Use a raw Dovecot + Postfix setup (ch06-dovecot.md) when:
- You need deep customization beyond what stack config files expose
- You are integrating with an existing LDAP/AD/SSO
- You are running a multi-server architecture (Dovecot Director, Cyrus Murder)
- You need custom Sieve rules, quota policies, or ACL schemes
- Compliance requirements demand auditability of every config line
