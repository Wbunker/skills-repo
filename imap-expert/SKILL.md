---
name: imap-expert
description: >
  Deep expertise on IMAP email protocol and server administration, grounded in
  "Managing IMAP" by Dianna Mullet and Kevin Mullet (O'Reilly). Covers current
  implementations: Dovecot, Cyrus IMAP, Exchange/Office 365, hosted providers.
  Use when asked about: IMAP vs POP3 differences, mailbox/folder management,
  flags and UIDs, IMAP namespaces, IMAP capabilities, configuring or tuning
  Dovecot, Cyrus IMAP, Courier, or Exchange IMAP; IMAP client configuration
  (Thunderbird, Apple Mail, Outlook, iOS/Android), SASL authentication, TLS/
  SSL, STARTTLS, OAuth2 for IMAP, IMAP IDLE, IMAP quota, SORT/THREAD
  extensions, performance tuning, scaling IMAP infrastructure, mailbox
  migration, imapsync, offlineimap, IMAP protocol commands and responses,
  IMAP4rev1 (RFC 3501) vs IMAP4rev2 (RFC 9051), debugging IMAP errors,
  shared mailboxes, public folders, sieve filtering, or self-hosted stacks
  (Mailcow, Mailu, docker-mailserver, Mail-in-a-Box, Stalwart Mail); or when
  asked about JMAP (RFC 8620/8621) as a modern alternative to IMAP.
---

# IMAP Expert

Based on *Managing IMAP* by Dianna Mullet and Kevin Mullet (O'Reilly), updated for current software.

## Reference Map

Load only the file(s) that match the user's task.

| Task / Question | Load |
|----------------|------|
| "What is IMAP?", IMAP vs POP3 vs Exchange, rationale, history | `references/ch01-why-imap.md` |
| Mailboxes, folders, flags, UIDs, namespaces, capabilities, IMAP concepts | `references/ch02-concepts.md` |
| Client setup: Thunderbird, Apple Mail, Outlook, iOS, Android, K-9 | `references/ch03-clients.md` |
| Migration from POP3, mailbox import/export, imapsync, offlineimap | `references/ch04-migration.md` |
| Capacity planning, storage layout, directory integration, prerequisites | `references/ch05-planning.md` |
| Dovecot install, configure, `dovecot.conf`, auth, maildir/mbox, LDA, LMTP | `references/ch06-dovecot.md` |
| Cyrus IMAP install, configure, `imapd.conf`, murder/frontend, sieve | `references/ch07-cyrus.md` |
| Courier IMAP, Exchange IMAP, Office 365, Gmail IMAP, hosted providers | `references/ch08-other-servers.md` |
| Performance tuning, caching, proxying, scaling, load balancing | `references/ch09-performance.md` |
| TLS, STARTTLS, SASL, OAuth2, GSSAPI, ACLs, firewall rules, hardening | `references/ch10-security.md` |
| Self-hosted stacks: Mailcow, Mailu, docker-mailserver, Mail-in-a-Box, Stalwart | `references/ch11-stacks.md` |
| JMAP (RFC 8620/8621): modern IMAP alternative, server/client support, how it works | `references/ch12-jmap.md` |
| Protocol commands/responses, IMAP4rev1 vs IMAP4rev2 (RFC 9051), raw sessions | `references/appendix-protocol.md` |
| IMAP extensions: IDLE, NAMESPACE, QUOTA, SORT, THREAD, COMPRESS, CONDSTORE | `references/appendix-extensions.md` |

## Quick Facts

- IMAP listens on **port 143** (STARTTLS) and **993** (implicit TLS / IMAPS)
- IMAP4rev1 = **RFC 3501** (2003); IMAP4rev2 = **RFC 9051** (2021)
- POP3 **deletes from server by default**; IMAP **keeps mail on server**
- Dovecot is the dominant open-source IMAP server today (replaced UW-IMAP)
- IMAP UIDs are **32-bit unsigned integers**, monotonically increasing per mailbox
- The `\Seen`, `\Answered`, `\Flagged`, `\Deleted`, `\Draft`, `\Recent` flags are standard
- `EXPUNGE` is required to permanently remove messages marked `\Deleted`
- **IMAP IDLE** (RFC 2177) enables push-like new-mail notification without polling
