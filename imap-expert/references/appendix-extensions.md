# Appendix B: IMAP Extensions Reference

## How to Check for Extension Support

```
A001 CAPABILITY
* CAPABILITY IMAP4rev1 IMAP4rev2 IDLE NAMESPACE QUOTA ...
```

Always check `CAPABILITY` before using an extension. After `LOGIN`/`AUTHENTICATE`, the server may advertise different (expanded) capabilities.

Use `ENABLE` (RFC 5161) to activate extensions that require opt-in:
```
A001 ENABLE CONDSTORE QRESYNC
* ENABLED CONDSTORE QRESYNC
A001 OK
```

---

## IDLE — Push New Mail Notification (RFC 2177)

Allows the client to wait for server notifications instead of polling.

```
A001 IDLE
+ idling
* 43 EXISTS     ← new message arrived
* 1 RECENT
DONE            ← client sends DONE to stop IDLE
A001 OK IDLE terminated
```

- Server must send at least one continuation every 30 minutes (keep-alive)
- Client should send `DONE` and re-`IDLE` periodically to refresh
- Maximum IDLE time per RFC: 29 minutes recommended

---

## NAMESPACE — Multiple Mailbox Roots (RFC 2342)

Exposes personal, other-users, and shared namespaces:

```
A001 NAMESPACE
* NAMESPACE (("" "/")) (("Other Users/" "/")) (("Shared Folders/" "/"))
A001 OK
```

Fields: `((personal-prefix separator))  ((other-users-prefix separator))  ((shared-prefix separator))`

---

## UIDPLUS — Reliable APPEND/COPY Results (RFC 4315)

Returns assigned UIDs from `APPEND` and `COPY`:

```
A001 APPEND INBOX (\Seen) {123}
...message data...
A001 OK [APPENDUID 1234567890 42] APPEND completed
     ^^ UIDVALIDITY             ^ assigned UID

A002 COPY 1:3 Archive
A002 OK [COPYUID 1234567890 1:3 101:103] COPY completed
         ^^ UIDVALIDITY  ^source UIDs ^dest UIDs
```

Also enables `UID EXPUNGE uid-set` — expunge only specific UIDs.

---

## QUOTA — Mailbox Quotas (RFC 2087 / RFC 9208)

```
A001 GETQUOTAROOT INBOX
* QUOTAROOT INBOX quota-root-name
* QUOTA quota-root-name (STORAGE 512 10240)
                                ^used  ^limit (in KB)
A001 OK Getquotaroot completed.

A002 SETQUOTA "" (STORAGE 20480)   # Admin only
```

Resource types:
| Type | Units |
|------|-------|
| `STORAGE` | Kilobytes |
| `MESSAGE` | Message count |
| `MAILBOX` | Mailbox count |

---

## SORT — Server-side Sorting (RFC 5256)

Sort messages on the server without fetching all headers:

```
A001 SORT (DATE REVERSE SIZE) UTF-8 ALL
* SORT 5 3 4 1 2
A001 OK Sort completed.
```

Sort criteria: `ARRIVAL`, `CC`, `DATE`, `FROM`, `REVERSE`, `SIZE`, `SUBJECT`, `TO`, `DISPLAYFROM`, `DISPLAYTO`

`UID SORT` is the UID-based variant.

---

## THREAD — Conversation Threading (RFC 5256)

```
A001 THREAD REFERENCES UTF-8 ALL
* THREAD (1)(2 3)(4 5 (6 7)(8))
A001 OK Thread completed.
```

Algorithms:
- `REFERENCES` — based on `References:` and `In-Reply-To:` headers (best)
- `ORDEREDSUBJECT` — groups by subject, then sorts by date

---

## CONDSTORE — Conditional STORE / Change Tracking (RFC 7162)

Allows fetching only messages changed since a given `MODSEQ`:

```
A001 ENABLE CONDSTORE
A002 SELECT INBOX
* OK [HIGHESTMODSEQ 1234] Highest
A002 OK

# Fetch changes since MODSEQ 1000:
A003 UID FETCH 1:* (FLAGS) (CHANGEDSINCE 1000)
* 5 FETCH (UID 42 MODSEQ (1234) FLAGS (\Seen))
A003 OK Fetch completed.

# Conditional STORE (only set if MODSEQ matches):
A004 STORE 1 (UNCHANGEDSINCE 1230) +FLAGS (\Flagged)
```

---

## QRESYNC — Quick Mailbox Resynchronization (RFC 7162)

Efficiently sync a client after reconnect (replaces full re-fetch):

```
A001 ENABLE QRESYNC
A002 SELECT INBOX (QRESYNC (1234567890 1000))
                             ^UIDVALIDITY ^last-known-MODSEQ
* VANISHED (EARLIER) 5,10,15   ← UIDs that were expunged
* 8 FETCH (UID 44 MODSEQ (1234) FLAGS (\Seen))  ← changed messages
A002 OK
```

QRESYNC requires CONDSTORE to be enabled.

---

## MOVE — Atomic Move (RFC 6851)

`COPY` + `STORE \Deleted` + `EXPUNGE` in a single atomic operation:

```
A001 MOVE 1:3 "Archive"
* OK [COPYUID 1234 1:3 101:103]
* EXPUNGE 1
* EXPUNGE 1
* EXPUNGE 1
A001 OK Move completed.
```

`UID MOVE` is the UID-based variant.

---

## UNSELECT — Close Without Expunge (RFC 3691)

Like `CLOSE` but does not expunge `\Deleted` messages:

```
A001 UNSELECT
A001 OK Unselect completed.
```

---

## ID — Client/Server Identification (RFC 2971)

Exchange name/version information:

```
A001 ID ("name" "Thunderbird" "version" "102.0" "os" "Linux")
* ID ("name" "Dovecot" "version" "2.3.21")
A001 OK ID completed.
```

---

## COMPRESS — Data Compression (RFC 4978)

Compress the IMAP stream after authentication:

```
A001 COMPRESS DEFLATE
A001 OK Begin compression.
[subsequent data is DEFLATE-compressed]
```

Useful over slow or metered links. Overlaps with TLS compression (avoid combining).

---

## SPECIAL-USE — Folder Role Flags (RFC 6154)

Servers advertise standard role flags on folders so clients auto-detect them:

| Flag | Folder Role |
|------|-------------|
| `\All` | All messages (like Gmail's All Mail) |
| `\Archive` | Archive folder |
| `\Drafts` | Drafts |
| `\Flagged` | Starred/important messages |
| `\Junk` | Spam/junk |
| `\Sent` | Sent messages |
| `\Trash` | Deleted items |

```
A001 LIST "" "*" RETURN (SPECIAL-USE)
* LIST (\Sent \HasNoChildren) "/" Sent
* LIST (\Trash \HasNoChildren) "/" Trash
A001 OK
```

Set in Dovecot via `conf.d/15-mailboxes.conf` (see `ch06-dovecot.md`).

---

## WITHIN — Age-based Search (RFC 5032)

```
A001 SEARCH YOUNGER 86400    # Messages newer than 24 hours
A002 SEARCH OLDER 2592000    # Messages older than 30 days
```

Values are in seconds.

---

## ESEARCH — Extended SEARCH Response (RFC 4731)

Returns richer results than plain `SEARCH`:

```
A001 ESEARCH RETURN (MIN MAX COUNT ALL) UNSEEN
* ESEARCH (TAG "A001") MIN 3 MAX 12 COUNT 4 ALL 3,5,9,12
A001 OK
```

`RETURN` options: `MIN`, `MAX`, `COUNT`, `ALL`, `SAVE` (saves result for later use with `$`)

---

## NOTIFY — Push Mailbox Events (RFC 5465)

Subscribe to events across multiple mailboxes without selecting each:

```
A001 NOTIFY SET STATUS (personal INBOX (MessageNew MessageExpunge FlagChange))
A001 OK
```

Event types: `MessageNew`, `MessageExpunge`, `FlagChange`, `AnnotationChange`, `MailboxName`, `SubscriptionChange`, `MailboxMetadataChange`

---

## OBJECTID — Stable Identifiers (RFC 8474)

Provides stable identifiers for mailboxes and messages (for sync tools):

```
A001 FETCH 1 (EMAILID THREADID)
* 1 FETCH (EMAILID (M6d952af73ebe2cedaa507e7b628b5f4f) THREADID (T64b22af3ebe21cedaa505e7b648b5f4f))
```

---

## CATENATE — Efficient Append from URLs (RFC 4469)

Build messages server-side from existing parts:

```
A001 APPEND Sent (\Seen) CATENATE (TEXT {header-len}
...headers...
 URL "/INBOX;UID=123/;SECTION=1")
```

---

## BINARY — Native Binary FETCH (RFC 3516)

Fetch binary content without base64 encoding overhead:

```
A001 FETCH 1 BINARY[1]
* 1 FETCH (BINARY[1] {binary-data-len}
...raw bytes...)
```
