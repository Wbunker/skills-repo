# Appendix A: IMAP Protocol Reference

## Standards

| RFC | Title | Status |
|-----|-------|--------|
| RFC 9051 | IMAP4rev2 | Current (2021) |
| RFC 3501 | IMAP4rev1 | Previous standard (2003) |
| RFC 2177 | IMAP IDLE | Extension |
| RFC 2342 | IMAP NAMESPACE | Extension |
| RFC 2971 | IMAP ID Extension | Extension |
| RFC 3516 | IMAP BINARY Extension | Extension |
| RFC 4314 | IMAP ACL Extension | Extension |
| RFC 4315 | IMAP UIDPLUS | Extension |
| RFC 4466 | Syntax updates to IMAP | Extension |
| RFC 4551 | IMAP CONDSTORE | Extension |
| RFC 5032 | IMAP WITHIN | Extension |
| RFC 5161 | IMAP ENABLE | Extension |
| RFC 5182 | IMAP SEARCHRES | Extension |
| RFC 5256 | IMAP SORT and THREAD | Extension |
| RFC 5267 | IMAP CONTEXT=SEARCH | Extension |
| RFC 5465 | IMAP NOTIFY | Extension |
| RFC 6154 | IMAP Special-Use Mailboxes | Extension |
| RFC 7162 | IMAP CONDSTORE and QRESYNC | Update |
| RFC 7888 | IMAP Non-synchronizing Literals | Extension |
| RFC 8437 | IMAP UNAUTHENTICATE | Extension |
| RFC 8474 | IMAP OBJECTID | Extension |

## IMAP4rev2 Key Changes from rev1 (RFC 9051)

- `LSUB` command deprecated (replaced by `LIST` with `SUBSCRIBED` select option)
- `RFC822`, `RFC822.HEADER`, `RFC822.TEXT` deprecated (use `BODY[]`, `BODY[HEADER]`, etc.)
- `BODY` response deprecated (use `BODYSTRUCTURE`)
- `\Recent` flag deprecated
- `STATUS` allowed on selected mailbox
- `NAMESPACE`, `UIDPLUS`, `ESEARCH`, `LIST-EXTENDED`, `SASL-IR`, `ID`, `MOVE`, `LITERAL-`, `UNSELECT`, `STATUS=SIZE`, `ENABLE` are now baseline (not extensions)
- Internationalization: UTF-8 allowed in mailbox names

## Connection States

```
[Not Authenticated]
  ↓ LOGIN / AUTHENTICATE
[Authenticated]
  ↓ SELECT / EXAMINE
[Selected]
  ↓ CLOSE / UNSELECT
[Authenticated]
  ↓ LOGOUT
[Logout]
```

## Commands by State

### Any State
| Command | Syntax | Description |
|---------|--------|-------------|
| `CAPABILITY` | `A001 CAPABILITY` | List server capabilities |
| `NOOP` | `A001 NOOP` | Ping; server may send unsolicited updates |
| `LOGOUT` | `A001 LOGOUT` | End session |
| `ID` | `A001 ID ("name" "Thunderbird" "version" "102")` | Client identification |

### Not Authenticated
| Command | Syntax | Description |
|---------|--------|-------------|
| `STARTTLS` | `A001 STARTTLS` | Upgrade to TLS |
| `LOGIN` | `A001 LOGIN user pass` | Plain authentication |
| `AUTHENTICATE` | `A001 AUTHENTICATE PLAIN` | SASL authentication |

### Authenticated
| Command | Syntax | Description |
|---------|--------|-------------|
| `SELECT` | `A001 SELECT INBOX` | Open mailbox read-write |
| `EXAMINE` | `A001 EXAMINE INBOX` | Open mailbox read-only |
| `CREATE` | `A001 CREATE "Work/Projects"` | Create mailbox |
| `DELETE` | `A001 DELETE "Work/Projects"` | Delete mailbox |
| `RENAME` | `A001 RENAME "OldName" "NewName"` | Rename mailbox |
| `SUBSCRIBE` | `A001 SUBSCRIBE INBOX` | Subscribe to mailbox |
| `UNSUBSCRIBE` | `A001 UNSUBSCRIBE INBOX` | Unsubscribe |
| `LIST` | `A001 LIST "" "*"` | List mailboxes |
| `LSUB` | `A001 LSUB "" "*"` | List subscribed (rev1; deprecated in rev2) |
| `STATUS` | `A001 STATUS INBOX (MESSAGES UNSEEN)` | Mailbox status |
| `APPEND` | `A001 APPEND INBOX (\Seen) {310}` | Upload message |
| `NAMESPACE` | `A001 NAMESPACE` | List namespaces |

### Selected
| Command | Syntax | Description |
|---------|--------|-------------|
| `CHECK` | `A001 CHECK` | Checkpoint / housekeeping |
| `CLOSE` | `A001 CLOSE` | Expunge + close |
| `UNSELECT` | `A001 UNSELECT` | Close without expunge (RFC 3691) |
| `EXPUNGE` | `A001 EXPUNGE` | Remove \Deleted messages |
| `SEARCH` | `A001 SEARCH UNSEEN` | Search messages |
| `FETCH` | `A001 FETCH 1:3 (FLAGS BODY[HEADER])` | Retrieve message data |
| `STORE` | `A001 STORE 1 +FLAGS (\Seen)` | Modify flags |
| `COPY` | `A001 COPY 1:3 "Archive"` | Copy messages |
| `MOVE` | `A001 MOVE 1:3 "Archive"` | Move messages (RFC 6851) |
| `UID` | `A001 UID FETCH 1234 (FLAGS)` | UID-based variant of commands |
| `IDLE` | `A001 IDLE` | Wait for server notifications |

## FETCH Data Items

```
BODY[]              - Full message
BODY[HEADER]        - Headers only
BODY[HEADER.FIELDS (From To Subject Date)] - Specific headers
BODY[TEXT]          - Body text
BODY[1]             - First MIME part
BODY[1.TEXT]        - Text of first MIME part
BODY[1.MIME]        - MIME header of first part
BODYSTRUCTURE       - Full MIME structure (parsed)
ENVELOPE            - Parsed envelope (From, To, Subject, Date, etc.)
FLAGS               - Message flags
INTERNALDATE        - Server receipt date
RFC822.SIZE         - Message size in bytes
UID                 - Message UID
```

## SEARCH Keys

```
ALL           All messages
ANSWERED      Has \Answered
UNANSWERED    No \Answered
SEEN          Has \Seen
UNSEEN        No \Seen (unread)
FLAGGED       Has \Flagged
UNFLAGGED     No \Flagged
DELETED       Has \Deleted
UNDELETED     No \Deleted
DRAFT         Has \Draft
UNDRAFT       No \Draft
NEW           \Recent and no \Seen
OLD           No \Recent
RECENT        Has \Recent (deprecated in IMAP4rev2)
BEFORE date   Received before date (DD-Mon-YYYY)
ON date       Received on date
SINCE date    Received since date
SENTBEFORE date  Date: header before date
SENTON date
SENTSINCE date
LARGER n      Larger than n bytes
SMALLER n     Smaller than n bytes
FROM string   From: contains string
TO string     To: contains string
CC string     Cc: contains string
BCC string    Bcc: contains string
SUBJECT string Subject: contains string
BODY string   Body contains string
TEXT string   Header or body contains string
HEADER field string  Named header contains string
UID uid-set   Specific UIDs
keyword       Has keyword flag
UNKEYWORD kw  No keyword flag
NOT criterion Logical NOT
OR c1 c2      Logical OR (AND is implicit)
```

## IMAP IDLE Session Example

```
C: A001 SELECT INBOX
S: * 42 EXISTS
S: * 3 RECENT
S: A001 OK [READ-WRITE] SELECT completed

C: A002 IDLE
S: + idling

... time passes, new message arrives ...

S: * 43 EXISTS
S: * 1 RECENT

C: DONE
S: A002 OK IDLE terminated
```

## Literal Data Syntax

For sending binary/large data (e.g., APPEND):
```
C: A001 APPEND INBOX (\Seen) {310}
S: + Ready for literal data
C: <310 bytes of RFC 5322 message>
S: A001 OK [APPENDUID 1234 5678] APPEND completed
```

Non-synchronizing literal (RFC 7888 — `LITERAL+` capability):
```
C: A001 APPEND INBOX (\Seen) {310+}
C: <310 bytes immediately without waiting for continuation>
```

## Raw IMAP Session Example

```bash
openssl s_client -connect mail.example.com:993 -crlf -quiet
```

```
* OK Dovecot ready.
A1 CAPABILITY
* CAPABILITY IMAP4rev1 IMAP4rev2 SASL-IR AUTH=PLAIN ...
A1 OK Pre-login capabilities listed.

A2 LOGIN user@example.com mypassword
A2 OK Logged in.

A3 LIST "" "*"
* LIST (\HasNoChildren) "/" INBOX
* LIST (\HasNoChildren \Sent) "/" Sent
* LIST (\HasNoChildren \Trash) "/" Trash
A3 OK List completed.

A4 SELECT INBOX
* 12 EXISTS
* 0 RECENT
* OK [UNSEEN 3] Message 3 is first unseen
* OK [UIDVALIDITY 1234567890] UIDs valid
* OK [UIDNEXT 456] Predicted next UID
* FLAGS (\Answered \Flagged \Deleted \Seen \Draft)
* OK [PERMANENTFLAGS (\Answered \Flagged \Deleted \Seen \Draft \*)] Flags permitted.
A4 OK [READ-WRITE] Select completed.

A5 FETCH 1:3 (FLAGS ENVELOPE)
* 1 FETCH (FLAGS (\Seen) ENVELOPE (...))
* 2 FETCH (FLAGS () ENVELOPE (...))
* 3 FETCH (FLAGS () ENVELOPE (...))
A5 OK Fetch completed.

A6 LOGOUT
* BYE Logging out
A6 OK Logout completed.
```
