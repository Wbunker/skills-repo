# Chapter 1: Why IMAP?

## The Problem IMAP Solves

Before IMAP, POP3 was the standard for retrieving email. POP3 was designed for a single-computer world: download messages to one machine and delete them from the server. IMAP was designed for multi-device, server-centric mail storage — the model that defines email today.

## IMAP vs POP3 vs Exchange/MAPI

| Dimension | IMAP4 | POP3 | Exchange/MAPI |
|-----------|-------|------|----------------|
| Mail stored | On server | Downloaded locally | On server |
| Multi-device | Full sync | Manual/workaround | Full sync |
| Folder sync | Yes | No | Yes |
| Flags sync | Yes | No | Yes |
| Offline access | Via local cache | Native | Via Cached Mode |
| Open standard | Yes (RFC 3501/9051) | Yes (RFC 1939) | No (proprietary) |
| Client choice | Any IMAP client | Any POP client | Outlook-centric |
| Server options | Many open-source | Many open-source | Exchange only |

## Historical Context

- **1986**: IMAP created by Mark Crispin at Stanford
- **1988**: IMAP2 (RFC 1064)
- **1994**: IMAP4 (RFC 1730)
- **1996**: IMAP4rev1 (RFC 2060, superseded by RFC 3501 in 2003)
- **2021**: IMAP4rev2 (RFC 9051) — consolidates extensions, deprecates some legacy behaviors

## When to Choose IMAP

**Choose IMAP when:**
- Users access email from multiple devices (phone + laptop + web)
- Shared/group mailboxes are needed
- Archiving on the server is a requirement
- You want client flexibility (not tied to Outlook/Exchange)
- Migration to a different server should be possible

**Consider Exchange/hosted when:**
- Deep calendar/contacts/tasks sync across devices is essential
- Organization is already Microsoft-centric
- You need rich shared calendar and resource scheduling

**POP3 is appropriate for:**
- Single-device legacy setups
- Very low bandwidth environments where full server sync is impractical
- Archiving from a server with limited storage (fetch + delete model)

## The IMAP Model

```
+------------------+       IMAP (port 143/993)      +------------------+
|   Mail Client    | <----------------------------> |   IMAP Server    |
| (Thunderbird,    |                                | (Dovecot, Cyrus) |
|  Apple Mail,     |                                |                  |
|  Outlook, etc.)  |                                | Mailbox Storage  |
+------------------+                                | (Maildir/mbox)   |
                                                    +------------------+
                                                           |
                                                    +------------------+
                                                    |   MTA/MDA        |
                                                    | (Postfix, etc.)  |
                                                    +------------------+
```

Mail is **delivered** by the MTA/MDA into the mailbox store. The IMAP server provides **access** to that store. The client never has the authoritative copy — the server does.

## Modern IMAP Ecosystem

**Open-source IMAP servers (current):**
- **Dovecot** — most widely deployed, excellent performance, active development
- **Cyrus IMAP** — enterprise-grade, used at scale (Carnegie Mellon, ISPs)
- **Stalwart Mail** — modern Rust-based, IMAP4rev2 native

**Commercial/hosted:**
- Microsoft Exchange (IMAP access available, but MAPI is preferred)
- Office 365 / Microsoft 365 (IMAP on port 993)
- Gmail (IMAP on smtp.gmail.com:993, OAuth2 required for modern auth)
- Fastmail, ProtonMail Bridge, Migadu — hosted with full IMAP

**MTA pairings (delivery into IMAP store):**
- Postfix + Dovecot LMTP (most common)
- Postfix + Dovecot LDA (local delivery agent)
- Sendmail + Cyrus IMAP
