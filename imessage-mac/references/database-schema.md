# iMessage chat.db — Database Schema Reference

## Database Location

| Platform | Path |
|----------|------|
| macOS (user) | `~/Library/Messages/chat.db` |
| iOS backup (Mac) | `~/Library/Application Support/MobileSync/Backup/<id>/3d/3d0d7e5fb2ce288813306e4d4636395e047a3d28` |

The database is SQLite 3 in WAL (Write-Ahead Logging) mode. Always open with `mode=ro` (read-only) to avoid corrupting the WAL:

```bash
sqlite3 ~/Library/Messages/chat.db
# or copy first to be safe:
cp ~/Library/Messages/chat.db /tmp/chat_copy.db
sqlite3 /tmp/chat_copy.db
```

---

## Core Tables

### `message` — All messages sent and received

| Column | Type | Description |
|--------|------|-------------|
| ROWID | INTEGER PK | Auto-increment local ID |
| guid | TEXT UNIQUE | Globally unique ID (syncs across devices) |
| text | TEXT | Plain text body (NULL in Ventura+ for rich messages) |
| attributedBody | BLOB | Binary plist (NSAttributedString) — contains text when `text` is NULL |
| handle_id | INTEGER | FK → handle.ROWID (sender/recipient) |
| service | TEXT | `iMessage` or `SMS` |
| account | TEXT | Sending account (e.g., `E:user@icloud.com`) |
| account_guid | TEXT | GUID of sending account |
| date | INTEGER | Nanoseconds since 2001-01-01 (Mac Absolute Time) |
| date_read | INTEGER | When message was read |
| date_delivered | INTEGER | When message was delivered |
| is_from_me | INTEGER | 1 = sent by you, 0 = received |
| is_read | INTEGER | 1 = read |
| is_delivered | INTEGER | 1 = delivered |
| is_sent | INTEGER | 1 = sent |
| is_emote | INTEGER | Tapback/reaction flag |
| is_audio_message | INTEGER | 1 = audio message |
| cache_roomnames | TEXT | Group chat room name |
| associated_message_guid | TEXT | For reactions: GUID of the parent message |
| associated_message_type | INTEGER | 0=normal, 2000-2005=reactions (heart/thumbs up/thumbs down/ha ha/!!/?) , 3000-3005=reaction removal |
| reply_to_guid | TEXT | Thread reply parent GUID |
| error | INTEGER | Error code (0 = none) |
| balloon_bundle_id | TEXT | App extension identifier for iMessage apps |
| expressive_send_style_id | TEXT | Slam, Loud, Gentle, Invisible Ink send effect |
| thread_originator_guid | TEXT | Root message in a thread |

### `handle` — Contact identifiers (phone numbers / emails)

| Column | Type | Description |
|--------|------|-------------|
| ROWID | INTEGER PK | Local ID |
| id | TEXT | Phone number (+E.164) or email address |
| country | TEXT | Country code (e.g., `us`) |
| service | TEXT | `iMessage` or `SMS` |
| uncanonicalized_id | TEXT | Raw ID as entered |

### `chat` — Conversations (1:1 and group)

| Column | Type | Description |
|--------|------|-------------|
| ROWID | INTEGER PK | Local ID |
| guid | TEXT UNIQUE | Globally unique chat ID |
| chat_identifier | TEXT | Phone/email for 1:1; group identifier for groups |
| service_name | TEXT | `iMessage` or `SMS` |
| room_name | TEXT | Group chat name (NULL for 1:1) |
| display_name | TEXT | Custom display name |
| is_archived | INTEGER | 1 = archived |
| last_readable_interaction_timestamp | INTEGER | Timestamp of last message |

### `attachment` — File attachments

| Column | Type | Description |
|--------|------|-------------|
| ROWID | INTEGER PK | Local ID |
| guid | TEXT UNIQUE | Globally unique attachment ID |
| created_date | INTEGER | Creation timestamp (same epoch as message.date) |
| start_date | INTEGER | Transfer start time |
| filename | TEXT | Absolute path on this Mac (e.g., `~/Library/Messages/Attachments/...`) |
| uti | TEXT | Uniform Type Identifier (e.g., `public.jpeg`) |
| mime_type | TEXT | MIME type (e.g., `image/jpeg`) |
| transfer_state | INTEGER | Transfer status (0=unknown, 5=finished) |
| is_outgoing | INTEGER | 1 = sent by you |
| transfer_name | TEXT | Original filename |
| total_bytes | INTEGER | File size in bytes |
| is_sticker | INTEGER | 1 = sticker |
| hide_attachment | INTEGER | 1 = hidden |

### Join Tables

| Table | Columns | Purpose |
|-------|---------|---------|
| `chat_message_join` | chat_id, message_id | Links messages to chats |
| `chat_handle_join` | chat_id, handle_id | Links participants to chats |
| `message_attachment_join` | message_id, attachment_id | Links attachments to messages |

### Other Tables

| Table | Purpose |
|-------|---------|
| `deleted_messages` | Soft-deleted message GUIDs |
| `sync_deleted_messages` | Sync state for deleted messages |
| `sync_deleted_chats` | Sync state for deleted chats |
| `sync_deleted_attachments` | Sync state for deleted attachments |
| `kvtable` | Key-value store for app metadata |
| `_SqliteDatabaseProperties` | DB metadata including `_ClientVersion` |
| `message_processing_task` | Background processing queue |

---

## Timestamp Conversion

iMessage uses **Mac Absolute Time**: nanoseconds since 2001-01-01 00:00:00 UTC.

```sql
-- In SQL (SQLite):
datetime(date / 1000000000 + strftime('%s','2001-01-01'), 'unixepoch', 'localtime')

-- In Python:
import datetime
mac_epoch = datetime.datetime(2001, 1, 1)
ts = mac_epoch + datetime.timedelta(seconds=date_value / 1e9)
```

**Note:** Older macOS versions stored timestamps as seconds (not nanoseconds). If you get unreasonable dates, try dividing by 1 instead of 1e9 — or check if the value is > 1e12 (nanoseconds) vs < 1e10 (seconds).

---

## SQL Query Examples

### All recent messages with sender and timestamp

```sql
SELECT
    datetime(m.date / 1000000000 + strftime('%s','2001-01-01'), 'unixepoch', 'localtime') AS ts,
    h.id AS sender,
    m.text,
    m.is_from_me,
    m.service
FROM message m
JOIN handle h ON h.ROWID = m.handle_id
ORDER BY m.date DESC
LIMIT 50;
```

### Messages in a specific conversation

```sql
SELECT
    datetime(m.date / 1000000000 + strftime('%s','2001-01-01'), 'unixepoch', 'localtime') AS ts,
    h.id AS sender,
    m.text,
    m.is_from_me
FROM message m
JOIN handle h ON h.ROWID = m.handle_id
JOIN chat_message_join cmj ON cmj.message_id = m.ROWID
JOIN chat c ON c.ROWID = cmj.chat_id
WHERE c.chat_identifier = '+15555550100'  -- or 'user@example.com'
ORDER BY m.date ASC;
```

### List all chats with message count

```sql
SELECT
    c.chat_identifier,
    c.display_name,
    c.service_name,
    COUNT(m.ROWID) AS message_count,
    datetime(MAX(m.date) / 1000000000 + strftime('%s','2001-01-01'), 'unixepoch', 'localtime') AS last_message
FROM chat c
JOIN chat_message_join cmj ON cmj.chat_id = c.ROWID
JOIN message m ON m.ROWID = cmj.message_id
GROUP BY c.ROWID
ORDER BY last_message DESC;
```

### Messages from a specific person (all conversations)

```sql
SELECT
    datetime(m.date / 1000000000 + strftime('%s','2001-01-01'), 'unixepoch', 'localtime') AS ts,
    m.text,
    m.is_from_me
FROM message m
JOIN handle h ON h.ROWID = m.handle_id
WHERE h.id LIKE '%5555550100%'
ORDER BY m.date DESC;
```

### Full-text search across all messages

```sql
SELECT
    datetime(m.date / 1000000000 + strftime('%s','2001-01-01'), 'unixepoch', 'localtime') AS ts,
    h.id AS sender,
    m.text
FROM message m
JOIN handle h ON h.ROWID = m.handle_id
WHERE m.text LIKE '%search term%'
ORDER BY m.date DESC
LIMIT 100;
```

### Attachments with file paths

```sql
SELECT
    datetime(m.date / 1000000000 + strftime('%s','2001-01-01'), 'unixepoch', 'localtime') AS ts,
    h.id AS sender,
    a.filename,
    a.mime_type,
    a.transfer_name,
    a.total_bytes
FROM message m
JOIN handle h ON h.ROWID = m.handle_id
JOIN message_attachment_join maj ON maj.message_id = m.ROWID
JOIN attachment a ON a.ROWID = maj.attachment_id
ORDER BY m.date DESC
LIMIT 50;
```

### Messages with both text and attachment info

```sql
SELECT
    datetime(m.date / 1000000000 + strftime('%s','2001-01-01'), 'unixepoch', 'localtime') AS ts,
    h.id AS sender,
    m.text,
    a.filename AS attachment_path,
    a.mime_type
FROM message m
JOIN handle h ON h.ROWID = m.handle_id
LEFT JOIN message_attachment_join maj ON maj.message_id = m.ROWID
LEFT JOIN attachment a ON a.ROWID = maj.attachment_id
JOIN chat_message_join cmj ON cmj.message_id = m.ROWID
WHERE cmj.chat_id = (
    SELECT ROWID FROM chat WHERE chat_identifier = '+15555550100' LIMIT 1
)
ORDER BY m.date ASC;
```

### Messages from me (sent) count by day

```sql
SELECT
    date(m.date / 1000000000 + strftime('%s','2001-01-01'), 'unixepoch', 'localtime') AS day,
    COUNT(*) AS count
FROM message m
WHERE m.is_from_me = 1
GROUP BY day
ORDER BY day DESC
LIMIT 30;
```

### Reactions (tapbacks) on a specific message

```sql
SELECT
    m2.associated_message_type,
    h.id AS reactor,
    datetime(m2.date / 1000000000 + strftime('%s','2001-01-01'), 'unixepoch', 'localtime') AS ts
FROM message m1
JOIN message m2 ON m2.associated_message_guid = m1.guid
JOIN handle h ON h.ROWID = m2.handle_id
WHERE m1.ROWID = 12345  -- substitute target message ROWID
  AND m2.associated_message_type BETWEEN 2000 AND 2005;
```

### Group chat members

```sql
SELECT
    c.chat_identifier,
    c.display_name,
    h.id AS participant
FROM chat c
JOIN chat_handle_join chj ON chj.chat_id = c.ROWID
JOIN handle h ON h.ROWID = chj.handle_id
WHERE c.room_name IS NOT NULL
ORDER BY c.ROWID, h.id;
```

### Get DB schema (inspect in sqlite3 CLI)

```sql
.tables
.schema message
.schema handle
.schema chat
.schema attachment
```

---

## attributedBody Decoding (macOS Ventura+)

When `message.text` is NULL but `message.attributedBody` is not NULL, the text is encoded as a binary Apple typedstream / plist blob. The format is:

```
[preamble bytes] [NSString marker] [length byte(s)] [UTF-8 text] [rest of plist data]
```

### Python Decoding

```python
import plistlib
import re

def decode_attributed_body(blob: bytes) -> str | None:
    """Extract plain text from an iMessage attributedBody blob."""
    if blob is None:
        return None
    try:
        # Method 1: plistlib (works when blob is a valid binary plist)
        plist = plistlib.loads(blob)
        # The root object is an NSAttributedString; its string value is in 'NS.string'
        if isinstance(plist, dict) and "NS.string" in plist:
            return plist["NS.string"]
    except Exception:
        pass

    # Method 2: Regex extraction (fallback — fast but less precise)
    # The NSString content follows a specific byte pattern
    try:
        # Look for the NSString marker and extract following UTF-8 text
        marker = b"NSString\x01\x94\x84\x01+"
        idx = blob.find(b"NSString")
        if idx != -1:
            # Skip past "NSString" + 5 preamble bytes
            pos = idx + len("NSString") + 5
            # Length is 1 byte, or 3 bytes if first byte == 0x81
            if blob[pos] == 0x81:
                length = int.from_bytes(blob[pos+1:pos+3], "little")
                pos += 3
            else:
                length = blob[pos]
                pos += 1
            return blob[pos:pos+length].decode("utf-8", errors="replace")
    except Exception:
        pass

    return None
```

### SQL to get text with fallback to attributedBody

```sql
SELECT
    m.ROWID,
    COALESCE(m.text, hex(m.attributedBody)) AS raw_content,
    m.is_from_me,
    datetime(m.date / 1000000000 + strftime('%s','2001-01-01'), 'unixepoch', 'localtime') AS ts
FROM message m
WHERE m.attributedBody IS NOT NULL AND (m.text IS NULL OR m.text = '')
ORDER BY m.date DESC
LIMIT 10;
```

For the complete Python solution handling both `text` and `attributedBody`, see [python-reading.md](python-reading.md).
