# Chapter 12: JMAP — The Modern Alternative to IMAP

## What Is JMAP?

**JMAP** (JSON Meta Application Protocol) is an IETF standard (RFC 8620 core, RFC 8621 for mail) designed as a modern replacement for IMAP. It uses JSON over HTTPS rather than a custom binary/text protocol over a persistent TCP connection.

| | IMAP | JMAP |
|---|------|------|
| Transport | Custom TCP protocol (port 993) | HTTPS (port 443) |
| Data format | RFC 5321 text / literals | JSON |
| Connection model | Persistent stateful TCP | Stateless HTTP + EventSource push |
| Batch operations | Limited (multiple commands) | First-class: one request, many operations |
| Partial sync | CONDSTORE/QRESYNC (complex) | Built-in state tokens |
| Offline support | Client-managed | Built-in change tracking |
| Thread model | THREAD extension | Native threads |
| Push notifications | IDLE (one mailbox at a time) | Push over HTTP EventSource (all mailboxes) |
| Standards | RFC 3501 (1996) / RFC 9051 (2021) | RFC 8620 + 8621 (2019) |

## Why JMAP Exists

IMAP was designed in 1986 for a world where:
- Clients were on fast, persistent connections to the server
- Mobile didn't exist
- One or two folders was typical

JMAP addresses IMAP's real-world pain points:
- **Battery drain**: IMAP IDLE requires a persistent TCP connection per account; JMAP uses HTTP push
- **Slow initial sync**: IMAP requires many round-trips to build a folder list + message list; JMAP batches everything
- **Complex client logic**: CONDSTORE/QRESYNC are hard to implement correctly; JMAP has simple state tokens
- **No standard for contacts/calendars**: IMAP is mail-only; JMAP has JMAP Contacts and JMAP Calendars specs

## JMAP RFCs

| RFC | Covers |
|-----|--------|
| RFC 8620 | JMAP Core (sessions, requests, errors, push) |
| RFC 8621 | JMAP for Mail (Email, Mailbox, Thread, EmailSubmission) |
| RFC 8887 | JMAP over WebSocket |
| RFC 9425 | JMAP Quotas |
| draft-ietf-jmap-contacts | JMAP Contacts (in progress) |
| draft-ietf-jmap-calendars | JMAP Calendars (in progress) |

## How JMAP Works

### Session Discovery

```
GET /.well-known/jmap
→ { "apiUrl": "https://mail.example.com/jmap/api/",
    "eventSourceUrl": "https://mail.example.com/jmap/eventsource/",
    "uploadUrl": "https://mail.example.com/jmap/upload/{accountId}/",
    "downloadUrl": "https://mail.example.com/jmap/download/{accountId}/{blobId}/{name}",
    "capabilities": { "urn:ietf:params:jmap:core": {...},
                      "urn:ietf:params:jmap:mail": {...} } }
```

### Request Structure

All JMAP operations are HTTP POST to the `apiUrl`:

```json
POST /jmap/api/
Authorization: Bearer <token>
Content-Type: application/json

{
  "using": ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:mail"],
  "methodCalls": [
    ["Mailbox/get", { "accountId": "abc123", "ids": null }, "call1"],
    ["Email/query", {
      "accountId": "abc123",
      "filter": { "inMailbox": "inbox-id", "notKeyword": "$seen" },
      "sort": [{ "property": "receivedAt", "isAscending": false }],
      "limit": 20
    }, "call2"],
    ["Email/get", {
      "accountId": "abc123",
      "#ids": { "resultOf": "call2", "name": "Email/query", "path": "/ids" },
      "properties": ["from", "subject", "receivedAt", "preview"]
    }, "call3"]
  ]
}
```

Three operations in a single HTTP request — what IMAP would take 5+ round-trips to do.

### State Tokens and Sync

Every JMAP object type has a `state` string. To sync changes:

```json
["Email/changes", {
  "accountId": "abc123",
  "sinceState": "last-known-state"
}, "c1"]
→ { "created": ["new-id-1"], "updated": ["changed-id"], "destroyed": ["deleted-id"],
    "newState": "current-state", "hasMoreChanges": false }
```

No UIDVALIDITY, no CONDSTORE complexity — just compare state strings.

### Push Notifications

EventSource (Server-Sent Events):
```
GET /jmap/eventsource/?types=*&closeafter=state&ping=300
Authorization: Bearer <token>

data: {"type":"StateChange","changed":{"abc123":{"Email":"new-state","Mailbox":"new-state"}}}
```

WebSocket alternative (RFC 8887) for clients that prefer WS over SSE.

## JMAP vs IMAP in Practice

**Initial sync of a large mailbox:**
- IMAP: `SELECT`, `UID SEARCH ALL`, chunks of `UID FETCH` — many round-trips, minutes for 100k messages
- JMAP: One `Email/query` + `Email/get` batch — seconds

**Checking for new mail (idle client):**
- IMAP: Persistent TCP connection with IDLE command per selected mailbox
- JMAP: Single EventSource connection covers all mailboxes and object types

**Moving a message:**
- IMAP: `UID COPY` + `UID STORE +FLAGS \Deleted` + `UID EXPUNGE` (3 commands)
- JMAP: One `Email/set` with `update: { id: { mailboxIds: { newMailbox: true } } }`

## Server Support

| Server | JMAP Support |
|--------|-------------|
| **Fastmail** | Full; primary protocol for native apps |
| **Stalwart Mail** | Full native JMAP (SMTP + IMAP + JMAP in one binary) |
| **Cyrus IMAP 3.x** | Full JMAP support |
| **Dovecot** | Partial; JMAP proxy plugin available, not native |
| **Gmail** | No JMAP |
| **Office 365** | No JMAP (uses EWS/Graph API instead) |

## Client Support

| Client | JMAP Support |
|--------|-------------|
| Fastmail apps (iOS/Android/web) | Native JMAP |
| **Mimestream** (macOS) | JMAP |
| **Ltt.rs** (Android) | JMAP |
| **Thunderbird** | In development / partial |
| Apple Mail | No |
| Outlook | No |

JMAP client adoption lags server support — most users still reach their JMAP-capable servers via IMAP.

## JMAP Libraries

```
# JavaScript / Node.js
jmap-client-ts     (TypeScript JMAP client)

# Python
jmapc              (https://github.com/halfcrazy/jmapc)

# Go
go-jmap            (https://github.com/emersion/go-jmap)

# Java
jmap-client-java   (Linagora / OpenPaaS)

# Rust
jmap-client        (Stalwart's own Rust library)
```

## JMAP Authentication

JMAP uses standard HTTP authentication:
- **Bearer tokens** (OAuth2) — recommended
- **Basic Auth** over HTTPS — simple but discouraged
- **Session tokens** from custom login

```bash
# Discover session
curl -u user@example.com:password https://mail.example.com/.well-known/jmap

# Use bearer token
curl -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"using":["urn:ietf:params:jmap:core","urn:ietf:params:jmap:mail"],"methodCalls":[["Mailbox/get",{"accountId":"id","ids":null},"c1"]]}' \
     https://mail.example.com/jmap/api/
```

## IMAP and JMAP Coexistence

JMAP and IMAP are not mutually exclusive. In 2026:
- Servers like Cyrus and Stalwart serve both protocols simultaneously
- Fastmail exposes both: use JMAP for native apps, IMAP for legacy clients
- The mailbox/message data model is shared — a message read via IMAP shows as read in JMAP

**Migration path:** Run IMAP today, add JMAP alongside it, migrate clients to JMAP as they gain support.

## DNS for JMAP Discovery

```dns
; SRV record for JMAP session discovery
_jmap._tcp.example.com.  IN SRV  0 1 443 mail.example.com.
```

The `/.well-known/jmap` endpoint is the primary discovery mechanism.

## Summary: Should You Use JMAP?

**Use JMAP now if:**
- You are building a new mail client
- You use Fastmail (it's already your protocol)
- You run Stalwart or Cyrus and want better mobile performance

**Stick with IMAP if:**
- Your clients don't support JMAP yet
- You use Gmail or Office 365 (no JMAP available)
- You need broad client compatibility

**In 2026:** IMAP remains dominant for client compatibility, but JMAP is the right choice for new mail client development and offers meaningfully better performance for mobile and web clients.
