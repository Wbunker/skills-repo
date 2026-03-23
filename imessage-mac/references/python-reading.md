# Python — Reading iMessages from chat.db

## Prerequisites

- macOS with Messages.app signed in to iMessage
- Full Disk Access granted to Terminal (or your Python runner)
- Python 3.7+ (uses standard library only for basic usage)

```bash
# Grant FDA to Terminal:
# System Settings > Privacy & Security > Full Disk Access > add Terminal.app
```

---

## Connection Setup

```python
import sqlite3
import os

DB_PATH = os.path.expanduser("~/Library/Messages/chat.db")

# Always open read-only to avoid corrupting the WAL
conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
conn.row_factory = sqlite3.Row  # enables column access by name
cur = conn.cursor()
```

**Never open the live database for writing.** If you need to experiment safely:

```python
import shutil
shutil.copy(DB_PATH, "/tmp/chat_copy.db")
conn = sqlite3.connect("/tmp/chat_copy.db")
```

---

## Reading Recent Messages

```python
import sqlite3
import os
import datetime

DB_PATH = os.path.expanduser("~/Library/Messages/chat.db")
MAC_EPOCH = datetime.datetime(2001, 1, 1)

def convert_timestamp(mac_ts: int) -> datetime.datetime:
    """Convert Mac Absolute Time (nanoseconds since 2001-01-01) to datetime."""
    if mac_ts is None:
        return None
    return MAC_EPOCH + datetime.timedelta(seconds=mac_ts / 1e9)

conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("""
    SELECT
        m.ROWID,
        m.guid,
        m.text,
        m.attributedBody,
        m.is_from_me,
        m.service,
        m.date,
        h.id AS sender_id
    FROM message m
    LEFT JOIN handle h ON h.ROWID = m.handle_id
    ORDER BY m.date DESC
    LIMIT 20
""")

for row in cur.fetchall():
    ts = convert_timestamp(row["date"])
    sender = "me" if row["is_from_me"] else row["sender_id"]
    print(f"[{ts}] {sender}: {row['text']}")

conn.close()
```

---

## Decoding attributedBody (macOS Ventura+)

Since macOS 13 Ventura, many messages store their content in `attributedBody` (a binary plist) rather than `text`. When `text` is NULL or empty, use this decoder:

```python
import plistlib

def decode_attributed_body(blob: bytes) -> str | None:
    """
    Decode an iMessage attributedBody binary blob to plain text.

    The blob is Apple's typedstream/NSKeyedArchiver format.
    We use two methods: plistlib first, then byte-pattern extraction as fallback.
    """
    if blob is None:
        return None

    # Method 1: Try plistlib (binary plist format)
    try:
        plist_data = plistlib.loads(blob)
        # NSAttributedString serialized — may have NS.string key
        if isinstance(plist_data, dict):
            if "NS.string" in plist_data:
                return plist_data["NS.string"]
            # Try nested structures
            for key in ("NSString", "$objects"):
                if key in plist_data:
                    val = plist_data[key]
                    if isinstance(val, str) and len(val) > 0:
                        return val
    except Exception:
        pass

    # Method 2: Byte pattern extraction
    # The NSString value follows this pattern in typedstream format:
    # "NSString" marker + 5 preamble bytes + 1-or-3 length bytes + UTF-8 text
    try:
        ns_string_marker = b"NSString"
        idx = blob.find(ns_string_marker)
        if idx != -1:
            pos = idx + len(ns_string_marker) + 5  # skip 5 preamble bytes
            if pos < len(blob):
                first_byte = blob[pos]
                if first_byte == 0x81:
                    # 3-byte length: next 2 bytes are little-endian length
                    length = int.from_bytes(blob[pos+1:pos+3], "little")
                    pos += 3
                else:
                    length = first_byte
                    pos += 1
                if pos + length <= len(blob):
                    return blob[pos:pos+length].decode("utf-8", errors="replace")
    except Exception:
        pass

    return None


def get_message_text(row) -> str | None:
    """Get text from a message row, handling both text and attributedBody."""
    if row["text"]:
        return row["text"]
    if row["attributedBody"]:
        return decode_attributed_body(bytes(row["attributedBody"]))
    return None
```

### Full reader with attributedBody handling

```python
import sqlite3
import os
import datetime
import plistlib

DB_PATH = os.path.expanduser("~/Library/Messages/chat.db")
MAC_EPOCH = datetime.datetime(2001, 1, 1)

def convert_timestamp(mac_ts):
    if mac_ts is None:
        return None
    return MAC_EPOCH + datetime.timedelta(seconds=mac_ts / 1e9)

def decode_attributed_body(blob):
    if not blob:
        return None
    try:
        plist_data = plistlib.loads(bytes(blob))
        if isinstance(plist_data, dict) and "NS.string" in plist_data:
            return plist_data["NS.string"]
    except Exception:
        pass
    try:
        idx = bytes(blob).find(b"NSString")
        if idx != -1:
            pos = idx + len("NSString") + 5
            b = bytes(blob)
            if b[pos] == 0x81:
                length = int.from_bytes(b[pos+1:pos+3], "little")
                pos += 3
            else:
                length = b[pos]
                pos += 1
            return b[pos:pos+length].decode("utf-8", errors="replace")
    except Exception:
        pass
    return None

def read_messages(chat_identifier=None, limit=50):
    """Read messages, optionally filtered by chat (phone/email)."""
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row

    if chat_identifier:
        query = """
            SELECT
                m.ROWID, m.guid, m.text, m.attributedBody,
                m.is_from_me, m.service, m.date, m.cache_roomnames,
                h.id AS sender_id
            FROM message m
            LEFT JOIN handle h ON h.ROWID = m.handle_id
            JOIN chat_message_join cmj ON cmj.message_id = m.ROWID
            JOIN chat c ON c.ROWID = cmj.chat_id
            WHERE c.chat_identifier = ?
            ORDER BY m.date DESC
            LIMIT ?
        """
        rows = conn.execute(query, (chat_identifier, limit)).fetchall()
    else:
        query = """
            SELECT
                m.ROWID, m.guid, m.text, m.attributedBody,
                m.is_from_me, m.service, m.date, m.cache_roomnames,
                h.id AS sender_id
            FROM message m
            LEFT JOIN handle h ON h.ROWID = m.handle_id
            ORDER BY m.date DESC
            LIMIT ?
        """
        rows = conn.execute(query, (limit,)).fetchall()

    conn.close()

    results = []
    for row in rows:
        text = row["text"] or decode_attributed_body(row["attributedBody"])
        results.append({
            "rowid": row["ROWID"],
            "text": text,
            "sender": "me" if row["is_from_me"] else row["sender_id"],
            "is_from_me": bool(row["is_from_me"]),
            "service": row["service"],
            "timestamp": convert_timestamp(row["date"]),
            "group_chat": row["cache_roomnames"],
        })
    return results


# Example usage
messages = read_messages(chat_identifier="+15555550100", limit=20)
for m in messages:
    print(f"[{m['timestamp']}] {m['sender']}: {m['text']}")
```

---

## List All Conversations

```python
def list_chats(limit=30):
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT
            c.ROWID AS chat_id,
            c.chat_identifier,
            c.display_name,
            c.room_name,
            c.service_name,
            COUNT(m.ROWID) AS message_count,
            datetime(
                MAX(m.date) / 1000000000 + strftime('%s','2001-01-01'),
                'unixepoch', 'localtime'
            ) AS last_message_time
        FROM chat c
        JOIN chat_message_join cmj ON cmj.chat_id = c.ROWID
        JOIN message m ON m.ROWID = cmj.message_id
        GROUP BY c.ROWID
        ORDER BY MAX(m.date) DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

for chat in list_chats():
    print(f"{chat['last_message_time']}  {chat['chat_identifier']}  ({chat['message_count']} messages)")
```

---

## Read Attachments

```python
def get_attachments(chat_identifier=None, limit=50):
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row

    query = """
        SELECT
            a.ROWID,
            a.filename,
            a.mime_type,
            a.transfer_name,
            a.total_bytes,
            datetime(m.date / 1000000000 + strftime('%s','2001-01-01'), 'unixepoch', 'localtime') AS ts,
            h.id AS sender_id,
            m.is_from_me
        FROM attachment a
        JOIN message_attachment_join maj ON maj.attachment_id = a.ROWID
        JOIN message m ON m.ROWID = maj.message_id
        LEFT JOIN handle h ON h.ROWID = m.handle_id
        {chat_filter}
        ORDER BY m.date DESC
        LIMIT ?
    """

    if chat_identifier:
        query = query.format(chat_filter="""
            JOIN chat_message_join cmj ON cmj.message_id = m.ROWID
            JOIN chat c ON c.ROWID = cmj.chat_id
            WHERE c.chat_identifier = ?
        """)
        rows = conn.execute(query, (chat_identifier, limit)).fetchall()
    else:
        query = query.format(chat_filter="")
        rows = conn.execute(query, (limit,)).fetchall()

    conn.close()
    return [dict(r) for r in rows]

for att in get_attachments():
    # Expand ~ in filename paths
    path = os.path.expanduser(att["filename"]) if att["filename"] else None
    exists = os.path.exists(path) if path else False
    print(f"{att['ts']}  {att['mime_type']}  {att['transfer_name']}  exists={exists}")
```

---

## Watch for New Messages (Polling)

```python
import time

def watch_messages(poll_interval=2.0):
    """Poll chat.db for new messages and print them as they arrive."""
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row

    # Get the current max ROWID as a baseline
    last_rowid = conn.execute("SELECT MAX(ROWID) FROM message").fetchone()[0] or 0
    print(f"Watching for new messages (last ROWID: {last_rowid})...")

    try:
        while True:
            time.sleep(poll_interval)
            # Re-open connection to get fresh WAL data
            conn.close()
            conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row

            rows = conn.execute("""
                SELECT m.ROWID, m.text, m.attributedBody, m.is_from_me, m.date, h.id AS sender_id
                FROM message m
                LEFT JOIN handle h ON h.ROWID = m.handle_id
                WHERE m.ROWID > ?
                ORDER BY m.ROWID ASC
            """, (last_rowid,)).fetchall()

            for row in rows:
                last_rowid = row["ROWID"]
                text = row["text"] or decode_attributed_body(row["attributedBody"])
                ts = convert_timestamp(row["date"])
                sender = "me" if row["is_from_me"] else row["sender_id"]
                print(f"[{ts}] {sender}: {text}")
    except KeyboardInterrupt:
        conn.close()

# watch_messages()
```

---

## Third-Party Libraries

### imessage_reader (PyPI)

```bash
pip install imessage-reader
```

```python
from imessage_reader import fetch_data

# Returns list of (name, text, date, service, account, is_from_me) tuples
data = fetch_data.FetchData().get_messages()
for entry in data:
    print(entry)
```

### imessage_tools (GitHub)

```bash
pip install git+https://github.com/my-other-github-account/imessage_tools.git
```

```python
from imessage_tools import read_messages, send_message

# Read last 10 messages
messages = read_messages(
    db_location="~/Library/Messages/chat.db",
    n=10,
    self_number="Me",
    human_readable_date=True
)
for m in messages:
    print(m)

# Send a message
send_message("Hello!", "+15555550100", group_chat=False)
```

### LangChain iMessage Loader

```python
from langchain_community.chat_loaders.imessage import IMessageChatLoader

loader = IMessageChatLoader(path="~/Library/Messages/chat.db")
chat_sessions = loader.load()
```

---

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `OperationalError: unable to open database` | No Full Disk Access | Grant FDA to Terminal in System Settings |
| `text` column is NULL | macOS Ventura+ attributedBody encoding | Use `decode_attributed_body()` |
| Timestamps look wrong | Dividing by wrong factor | Divide by 1e9 (nanoseconds); older macOS used seconds |
| Missing recent messages | WAL not flushed | Re-open connection; or use `PRAGMA wal_checkpoint` |
| Duplicate messages | Joining across multiple chats | Add `DISTINCT` or filter by specific `chat_id` |
| `database is locked` | Messages.app has it open | Use `mode=ro` (read-only) URI parameter |
