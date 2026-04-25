# Chapter 8: Other IMAP Servers and Hosted Providers

## Courier IMAP

Courier IMAP is part of the Courier Mail Server suite. Still maintained but largely superseded by Dovecot for new deployments.

- Maildir++ format (Maildir with quota via `maildirsize`)
- Included with Courier MTA or standalone
- Config: `/etc/courier/imapd` and `/etc/courier/imapd-ssl`

```
# /etc/courier/imapd
IMAPDSTART=YES
MAXDAEMONS=40
MAXPERIP=4
IMAP_EMPTYTRASH=Trash:7

# /etc/courier/imapd-ssl
IMAPDSSLSTART=YES
TLS_CERTFILE=/etc/ssl/private/mail.pem
```

Start: `systemctl start courier-imap courier-imap-ssl`

Courier is not recommended for new deployments. Migrate to Dovecot with `mb2md` (mbox to Maildir conversion is not needed; Courier already uses Maildir).

---

## Exchange IMAP

Microsoft Exchange supports IMAP4 access. It is not as feature-rich as native Exchange (MAPI) but allows non-Outlook clients.

### Enabling IMAP in Exchange

```powershell
# Exchange Management Shell (on-premises)
Set-IMAPSettings -Server MAILSERVER01 -LoginType PlainTextAuthentication
Start-Service MSExchangeIMAP4
Start-Service MSExchangeIMAP4BE
Set-Service MSExchangeIMAP4 -StartupType Automatic
```

### Exchange IMAP Limitations

- No support for IMAP IDLE push notification
- Limited Sieve/server-side filtering
- Folder names may differ from Dovecot conventions
- `INBOX` maps to Exchange Inbox; `Sent Items` is Exchange Sent Items
- Calendar/Contacts not accessible via IMAP (use MAPI/EWS/ActiveSync)

### Office 365 / Microsoft 365 IMAP

- Host: `outlook.office365.com`, port 993 (SSL)
- Authentication: OAuth2 (Modern Authentication) — Basic Auth disabled since October 2022
- Requires App Password or OAuth2 flow for IMAP clients

**OAuth2 for IMAP with Office 365:**
```
# SASL mechanism: XOAUTH2
# Token: base64-encoded string of:
# "user=" + email + chr(1) + "auth=Bearer " + access_token + chr(1) + chr(1)
```

**Enable IMAP for a mailbox (Microsoft 365 Admin):**
```powershell
Set-CASMailbox -Identity user@example.com -IMAPEnabled $true
```

---

## Gmail IMAP

- Host: `imap.gmail.com`, port 993 (SSL)
- Authentication: OAuth2 required (Basic Auth removed 2022)
- Special folders: Gmail uses labels that map to IMAP folders
- `[Gmail]/` prefix for system folders: `[Gmail]/Sent Mail`, `[Gmail]/Trash`, `[Gmail]/All Mail`

### Gmail IMAP Quirks

- `[Gmail]/All Mail` contains every message regardless of label — avoid syncing it with imapsync unless you want duplicates
- Archiving in Gmail = removing `\Inbox` label; message stays in `[Gmail]/All Mail`
- IMAP IDLE is supported
- Google Workspace IMAP behaves similarly

### Gmail-Specific imapsync

```bash
imapsync \
  --host1 imap.gmail.com --user1 old@gmail.com --password1 "app-specific-password" \
  --ssl1 --authmech1 LOGIN \
  --host2 new.example.com --user2 user@example.com --password2 "pass" \
  --ssl2 \
  --regextrans2 's,\[Gmail\]/,,g' \    # Remove [Gmail]/ prefix
  --exclude '\[Gmail\]/All Mail' \    # Skip All Mail (would duplicate everything)
  --exclude '\[Gmail\]/Important' \
  --exclude '\[Gmail\]/Starred'
```

---

## Hosted IMAP Providers

### Fastmail

- IMAP host: `imap.fastmail.com`, port 993
- Full IMAP4rev1 + extensions, IDLE, CONDSTORE, QRESYNC
- ManageSieve on port 4190
- Also supports JMAP (faster than IMAP for Fastmail-native apps)
- App Passwords available for IMAP clients (2FA accounts)

### Proton Mail (ProtonMail Bridge)

- Proton Mail does not offer direct IMAP access — uses E2E encryption
- **Proton Mail Bridge**: local proxy app that exposes IMAP on `127.0.0.1:1143`
- Clients connect to the local bridge, which encrypts/decrypts
- Bridge required for Thunderbird, Apple Mail, Outlook integration

### Migadu

- IMAP host: `imap.migadu.com`, port 993
- Full-featured IMAP with ManageSieve, subaddressing, multi-domain

### Zoho Mail

- IMAP host: `imap.zoho.com`, port 993
- OAuth2 or App Password required for 2FA accounts

---

## Stalwart Mail (Modern Alternative)

Stalwart Mail is a modern, Rust-based mail server with native IMAP4rev2 (RFC 9051) support.

- **IMAP4rev2** support (not just rev1)
- **JMAP** support out of the box
- **SMTP** integrated
- Configuration via web UI or TOML
- SQLite, PostgreSQL, or S3-compatible object storage backends

```bash
# Install
curl -fsSL https://stalw.art/install | bash
# Or Docker
docker run -d -p 993:993 -p 143:143 -p 25:25 stalwartlabs/mail-server:latest
```

Stalwart is worth considering for new installations that want JMAP (used by Fastmail clients for faster sync).

---

## Legacy: UW-IMAP

UW-IMAP (University of Washington IMAP) was the reference IMAP implementation and the server covered in the original "Managing IMAP" book. It is now **effectively dead**:

- Last release: 2007 (imap-2007f)
- Uses mbox format (poor concurrency)
- No virtual users (requires OS accounts)
- **Do not use for new deployments**

If you are running UW-IMAP, migrate to Dovecot immediately. See `ch04-migration.md` for mbox → Maildir conversion.
