# Chapter 4: Migration to IMAP

## Migration Scenarios

1. **POP3 → IMAP**: Users have local mail stored in a desktop client; moving to server-centric IMAP
2. **IMAP server → IMAP server**: Moving between servers (UW-IMAP → Dovecot, Exchange → Dovecot, etc.)
3. **Hosted → self-hosted** or **self-hosted → hosted**: Gmail → Dovecot, or vice versa
4. **mbox → Maildir**: Storage format conversion within the same server

## POP3 → IMAP Migration

### Strategy
1. Stand up the new IMAP server
2. Have users upload their local mail via their mail client
3. Switch DNS MX records and/or reconfigure clients to point to IMAP

### Uploading Local Mail from a Client

**Thunderbird:**
- Set up the IMAP account alongside the existing POP3 account
- Drag folders from the POP3 account to the IMAP INBOX or a subfolder
- Thunderbird will upload messages via IMAP APPEND

**Apple Mail:**
- Set up IMAP account, then drag messages from Local Folders to the IMAP mailbox

**Outlook:**
- Set up IMAP account, copy folders via drag in the left pane

## IMAP → IMAP Migration with imapsync

`imapsync` is the standard tool for server-to-server IMAP migration.

### Install

```bash
# Debian/Ubuntu
apt install imapsync

# RHEL/Rocky
dnf install imapsync

# macOS
brew install imapsync
```

### Basic Usage

```bash
imapsync \
  --host1 source.example.com --user1 user@example.com --password1 'oldpass' \
  --host2 dest.example.com   --user2 user@example.com --password2 'newpass' \
  --ssl1 --ssl2
```

### Dry Run First

```bash
imapsync \
  --host1 source.example.com --user1 user@example.com --password1 'oldpass' \
  --host2 dest.example.com   --user2 user@example.com --password2 'newpass' \
  --ssl1 --ssl2 \
  --dry   # simulate only
```

### Useful imapsync Options

| Option | Effect |
|--------|--------|
| `--dry` | Dry run, no changes |
| `--ssl1` / `--ssl2` | Use TLS for source/dest |
| `--tls1` / `--tls2` | STARTTLS for source/dest |
| `--authmech1 PLAIN` | Force SASL mechanism |
| `--exclude 'Spam'` | Skip mailboxes matching regex |
| `--folder 'INBOX'` | Only sync specified folder |
| `--delete2` | Delete dest messages not on source |
| `--expunge1` | Expunge source after sync |
| `--skipcrossduplicates` | Skip if message exists in multiple folders |
| `--maxsize 52428800` | Skip messages larger than 50 MB |
| `--addheader` | Add `X-IMAP-IMAPSYNC` dedup header |
| `--regextrans2 's/INBOX\.//'` | Rename folders during transfer |

### Migrating All Users (Admin / Script)

```bash
#!/bin/bash
# migrate_all.sh
while IFS=: read -r user oldpass newpass; do
  echo "Migrating $user..."
  imapsync \
    --host1 old.example.com --user1 "$user" --password1 "$oldpass" \
    --host2 new.example.com --user2 "$user" --password2 "$newpass" \
    --ssl1 --ssl2 \
    --logfile "/var/log/imapsync/${user}.log" &
done < users.csv
wait
echo "All done"
```

### Admin Access Migration (Dovecot master user)

If source or destination supports admin/impersonation:
```bash
# Dovecot master user: admin*targetuser
imapsync \
  --host1 old.example.com \
  --user1 "admin*user@example.com" \
  --password1 'adminpassword' \
  --authmech1 PLAIN \
  --host2 new.example.com \
  --user2 "user@example.com" \
  --password2 'newpassword' \
  --ssl1 --ssl2
```

## mbsync / isync (Alternative to imapsync)

`mbsync` (part of the `isync` package) is lighter-weight; good for personal migrations.

```bash
apt install isync
```

Example `.mbsyncrc`:
```
IMAPAccount source
Host source.example.com
User user@example.com
Pass oldpassword
SSLType IMAPS
CertificateFile /etc/ssl/certs/ca-certificates.crt

IMAPAccount dest
Host dest.example.com
User user@example.com
Pass newpassword
SSLType IMAPS
CertificateFile /etc/ssl/certs/ca-certificates.crt

IMAPStore source-remote
Account source

IMAPStore dest-remote
Account dest

Channel migrate
Far :source-remote:
Near :dest-remote:
Patterns *
Create Near
Sync All
Expunge None
```

```bash
mbsync --all --config ~/.mbsyncrc
```

## mbox to Maildir Conversion

If migrating from a legacy mbox-based server (UW-IMAP) to Maildir (Dovecot):

```bash
# Using mb2md
apt install mb2md
mb2md -s /var/spool/mail/username -d /home/username/Maildir

# Dovecot's own conversion
# Set mail_location to accept both, then use doveadm
doveadm -f flow sync -u username -R \
  "mbox:/var/mail/username:INBOX=/var/spool/mail/username"
```

## Post-Migration Checklist

- [ ] All folders/subfolders present on destination
- [ ] Message counts match source
- [ ] Flags (Seen, Answered, Flagged) preserved
- [ ] Folder subscriptions recreated
- [ ] Client reconfigured to point to new server
- [ ] Sieve/filter rules migrated (ManageSieve or server config)
- [ ] Shared mailboxes/ACLs recreated
- [ ] Quota settings applied
- [ ] Old server decommissioned after verification period

## Cutover Strategy

**Recommended staged approach:**
1. Pre-sync: run imapsync before cutover to copy bulk of mail
2. Cutover window: stop delivery to old server (or reduce MX TTL 48h ahead)
3. Final sync: run imapsync one more time for delta
4. Switch MX records to new server
5. Reconfigure clients (or use autodiscover)
6. Monitor for bounces and stragglers for 1–2 weeks
