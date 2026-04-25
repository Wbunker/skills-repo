# Chapter 2: IMAP Concepts

## Mailboxes

In IMAP, a **mailbox** is what most users call a "folder." The term "folder" is a client-side UI concept; the protocol uses "mailbox."

- `INBOX` — the special, always-present primary mailbox (case-insensitive in protocol)
- Other mailboxes are hierarchical, separated by a **hierarchy delimiter** (usually `.` or `/`)
- Examples: `INBOX`, `Sent`, `Trash`, `INBOX.Work`, `Archive.2024`

### Mailbox Hierarchy Delimiter

The delimiter is server-specific. Discover it via:
```
A001 LIST "" ""
* LIST (\Noselect) "." ""
```
The second field (`"."`) is the delimiter. Dovecot typically uses `/`; some servers use `.`.

## Messages

Each mailbox contains zero or more **messages**. Messages are immutable once delivered — the content never changes. Only **flags** change.

### Message Sequence Numbers (MSN) vs UIDs

| | MSN | UID |
|---|-----|-----|
| Scope | Per-session, per-mailbox | Permanent, per-mailbox |
| Stability | Changes on EXPUNGE | Never changes |
| Type | 1-based integer | 32-bit unsigned integer |
| Use | Legacy, simple | Reliable sync |

**Always prefer UIDs** for client sync logic. MSNs shift when messages are deleted.

### UIDVALIDITY

A 32-bit value stored per mailbox. If `UIDVALIDITY` changes, all cached UID→message mappings must be invalidated. This happens when:
- Mailbox is deleted and recreated
- Server restores from backup
- Some legacy mbox-format operations

## Flags

Flags are per-message boolean markers. System flags:

| Flag | Meaning |
|------|---------|
| `\Seen` | Message has been read |
| `\Answered` | Message has been replied to |
| `\Flagged` | User-starred / important |
| `\Deleted` | Marked for deletion (not yet removed) |
| `\Draft` | Draft message, not sent |
| `\Recent` | New since last session (set by server, read-only to clients) |

**Deletion is two-step:**
1. `STORE +FLAGS \Deleted` — marks the message
2. `EXPUNGE` — permanently removes all `\Deleted` messages

Client-defined **keyword flags** (e.g., `$Forwarded`, `$Junk`, `$NotJunk`) are also supported by most servers.

## Namespaces (RFC 2342)

Namespaces define where different types of mailboxes live:

| Namespace | Description | Typical prefix |
|-----------|-------------|----------------|
| Personal | User's own mailboxes | (empty) or `INBOX.` |
| Other Users | Access to other users' mail | `Other Users/` or `user/` |
| Shared | Shared/public folders | `Shared/` or `#shared/` |

Discover with:
```
A001 NAMESPACE
* NAMESPACE (("" "/")) (("~" "/")) (("#shared/" "/"))
```

## IMAP Capabilities

The server advertises what it supports via `CAPABILITY`. Always check before using extensions:
```
A001 CAPABILITY
* CAPABILITY IMAP4rev1 IMAP4rev2 SASL-IR LOGIN-REFERRALS
  ID ENABLE IDLE SORT SORT=DISPLAY THREAD=REFERENCES
  THREAD=REFS THREAD=ORDEREDSUBJECT MULTIAPPEND URL-PARTIAL
  CATENATE UNSELECT CHILDREN NAMESPACE UIDPLUS LIST-EXTENDED
  I18NLEVEL=1 CONDSTORE QRESYNC ESEARCH ESORT SEARCHRES
  WITHIN CONTEXT=SEARCH LIST-STATUS BINARY MOVE NOTIFY
  LITERAL- APPENDLIMIT=0 AUTH=PLAIN AUTH=LOGIN STARTTLS
```

## The SELECT State Machine

```
Not Authenticated → Authenticated → Selected
      |                 |               |
   STARTTLS         SELECT/EXAMINE   CLOSE/UNSELECT
   LOGIN/AUTH       CREATE/DELETE    EXPUNGE
                    LIST/LSUB        FETCH/STORE/SEARCH
                    SUBSCRIBE        UID commands
```

`EXAMINE` opens a mailbox **read-only** (no flag changes, no EXPUNGE).

## IMAP Session Response Types

| Type | Example | Meaning |
|------|---------|---------|
| Tagged OK | `A001 OK [READ-WRITE] SELECT completed` | Command succeeded |
| Tagged NO | `A001 NO [TRYCREATE] No such mailbox` | Command failed |
| Tagged BAD | `A001 BAD Unknown command` | Protocol error |
| Untagged `*` | `* 3 EXISTS` | Server data / info |
| Continuation `+` | `+ Ready for literal data` | Send literal data |

## Response Codes

Common bracketed response codes in OK/NO responses:

| Code | Meaning |
|------|---------|
| `[ALERT]` | Important notice the user must see |
| `[BADCHARSET]` | Search charset not supported |
| `[CAPABILITY ...]` | Server capabilities |
| `[PARSE]` | Message parse error |
| `[PERMANENTFLAGS (...)]` | Which flags can be set permanently |
| `[READ-ONLY]` | Mailbox opened read-only |
| `[READ-WRITE]` | Mailbox opened read-write |
| `[TRYCREATE]` | Mailbox doesn't exist; try CREATE |
| `[UIDNEXT n]` | Predicted next UID |
| `[UIDVALIDITY n]` | Current UIDVALIDITY |
| `[UNSEEN n]` | First unseen message sequence number |
| `[APPENDUID n m]` | UID assigned to APPENDed message |
| `[COPYUID n m:n]` | UIDs assigned to COPYed messages |

## Mailbox Attributes

Returned by `LIST` command:

| Attribute | Meaning |
|-----------|---------|
| `\Noselect` | Cannot be selected (container only) |
| `\Marked` | Has new messages since last visit |
| `\Unmarked` | No new messages |
| `\HasChildren` | Has child mailboxes |
| `\HasNoChildren` | No child mailboxes |
| `\Subscribed` | Client has subscribed to it |
| `\NonExistent` | Mailbox doesn't exist (LIST-EXTENDED) |

## Storage Formats

| Format | Description | Used by |
|--------|-------------|---------|
| **Maildir** | One file per message, directory per folder | Dovecot (preferred), Courier |
| **Maildir++** | Maildir + quota support via `maildirsize` | Courier, Dovecot |
| **mbox** | All messages in one file, `From_` line separators | Legacy UW-IMAP |
| **Cyrus native** | Proprietary indexed format | Cyrus IMAP |
| **dbox** | Dovecot's own format (sdbox/mdbox) | Dovecot optional |

**Maildir is strongly recommended** for new installations. mbox has locking problems and poor concurrency.
