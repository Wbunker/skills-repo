# Chapter 3: IMAP Clients

## Client Configuration Essentials

Every IMAP client needs:
- **Incoming server hostname** (e.g., `mail.example.com`)
- **Port**: 993 (implicit TLS) or 143 (STARTTLS)
- **Encryption**: Always use TLS — never plain. Prefer implicit TLS (993) over STARTTLS (143)
- **Username**: usually full email address (`user@example.com`) or bare username
- **Authentication**: Password, OAuth2, or GSSAPI/Kerberos

## Port and Encryption Reference

| Port | Protocol | Notes |
|------|----------|-------|
| 143 | IMAP + STARTTLS | STARTTLS upgrades plain → TLS mid-session |
| 993 | IMAPS | TLS from first byte; preferred |
| 143 | IMAP plain | **Never use in production** |

## Thunderbird

**Auto-configure:** Thunderbird uses Mozilla's autoconfig and provider ISP configs. For custom servers, configure manually:

Settings → Account Settings → Server Settings:
- Server type: IMAP Mail Server
- Server Name: `mail.example.com`
- Port: 993
- Connection security: SSL/TLS
- Authentication method: Normal password (or OAuth2 if configured)

**Thunderbird-specific features:**
- Offline folders: right-click mailbox → Properties → Synchronize
- Message filters: Tools → Message Filters (Sieve if server supports ManageSieve)
- Account name in server settings controls NAMESPACE mapping
- `about:config` key `mail.server.serverN.namespace.personal` to override namespace

## Apple Mail (macOS / iOS)

**macOS:** System Preferences → Internet Accounts → Add Account → Other Mail Account, or Mail → Preferences → Accounts → +

- Select IMAP, enter server, username, password
- Advanced tab: set port to 993, TLS on
- IMAP Path Prefix: leave blank for Dovecot/Cyrus with proper namespace; set to `INBOX` for some legacy servers

**iOS:** Settings → Mail → Accounts → Add Account → Other → Add Mail Account
- Same fields; iOS auto-selects 993/TLS when "Use SSL" is on

**Known Apple Mail quirks:**
- Apple Mail stores Sent/Trash/Junk on server but may use different folder names than server defaults
- "IMAP Path Prefix" in advanced settings maps to the personal namespace prefix
- Apple Mail does not support ManageSieve; use Thunderbird or webmail for server-side filters

## Microsoft Outlook

**Outlook 365 / 2021 / 2019:**
File → Add Account → manual setup:
- Account type: IMAP
- Incoming: `mail.example.com`, port 993, SSL/TLS
- Outgoing: your SMTP server

**Outlook IMAP limitations:**
- Outlook was optimized for Exchange/MAPI; IMAP support is functional but lacks some sync features
- "Sent Items" folder may need to be manually mapped (Account Settings → More Settings → Sent Items)
- Outlook does not use IMAP IDLE; it polls on a schedule
- For best experience, prefer Outlook with Exchange or use Thunderbird for pure IMAP

**Outlook with OAuth2 (Modern Authentication):**
- Required for Office 365 / Gmail since Basic Auth deprecation (2022)
- Outlook handles this transparently for hosted Microsoft/Google accounts
- For self-hosted servers with OAuth2 (e.g., Dovecot + Keycloak), Outlook 2021+ supports it via SASL XOAUTH2

## Mobile Clients

### iOS Mail
- Settings → Mail → Accounts → Add Account → Other
- Port 993, SSL on
- Auto-syncs via IMAP IDLE when app is foreground

### Android (Gmail app)
- Add account → Other → manual IMAP
- Supports IMAP IDLE for push notifications
- OAuth2 required for Gmail accounts

### K-9 Mail (Android, open source)
- Full IMAP feature support including IDLE, NAMESPACE, QUOTA
- Settings → Add Account → IMAP
- "Incoming server settings": port 993, SSL/TLS, check certificate
- Push mail via IMAP IDLE: Account Settings → Fetching mail → Push Classes

### FairEmail (Android, open source)
- Privacy-focused; supports IMAP IDLE, S/MIME, OpenPGP
- Wizard auto-detects server settings from email domain

## Autoconfig / Autodiscover

Clients use these mechanisms to auto-populate settings from the email domain:

**Mozilla autoconfig** (Thunderbird, K-9):
- `https://autoconfig.example.com/mail/config-v1.1.xml`
- `https://example.com/.well-known/autoconfig/mail/config-v1.1.xml`

**Microsoft Autodiscover** (Outlook):
- `https://autodiscover.example.com/autodiscover/autodiscover.xml`
- DNS SRV: `_autodiscover._tcp.example.com`

**DNS SRV records** (RFC 6186):
```
_imap._tcp.example.com.    IN SRV  0 1 143  mail.example.com.
_imaps._tcp.example.com.   IN SRV  0 1 993  mail.example.com.
```

## Webmail Clients

| Client | Backend | Notes |
|--------|---------|-------|
| Roundcube | PHP, IMAP | Most popular open-source; supports ManageSieve |
| SOGo | Objective-C | Groupware: calendar, contacts, tasks |
| Rainloop / Snappymail | PHP | Lightweight; Snappymail is maintained fork |
| Dovecot's Pigeonhole | Sieve | Server-side filtering UI |

## Offline / Sync Tools

| Tool | Use Case |
|------|---------|
| `offlineimap` | Sync IMAP to local Maildir; bi-directional |
| `mbsync` / `isync` | Faster alternative to offlineimap |
| `getmail6` | Fetch-only tool; supports IMAP and POP3 |
| `notmuch` | Index and search local mail archive |
| `mu` / `mu4e` | Emacs mail client using local Maildir |

## Testing IMAP with Telnet / OpenSSL

Manual session for debugging:
```bash
# Implicit TLS (port 993)
openssl s_client -connect mail.example.com:993 -crlf

# STARTTLS (port 143)
openssl s_client -connect mail.example.com:143 -starttls imap -crlf

# After connecting, authenticate:
A001 CAPABILITY
A002 LOGIN username password
A003 LIST "" "*"
A004 SELECT INBOX
A005 FETCH 1 (FLAGS ENVELOPE)
A006 LOGOUT
```
