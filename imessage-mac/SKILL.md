---
name: imessage-mac
description: "Expert guide for interacting with iMessage on macOS programmatically. Use this skill when the user asks about reading iMessages from chat.db, sending messages via AppleScript or osascript, querying the iMessage SQLite database with Python or SQL, iMessage automation, the chat.db schema, attachments storage, TCC permissions for Messages, or any open-source tools that interface with iMessage on Mac. Triggers on: chat.db, iMessage automation, osascript messages, AppleScript Messages, imessage python, imessage sqlite, send imessage terminal, read imessage database, imessage mac scripting, bluebubbles, messages app automation."
---

# iMessage on macOS — Programmatic Interaction Guide

Complete technical reference for reading, querying, and sending iMessages on macOS via AppleScript, SQLite, Python, and third-party tools.

## Quick Reference

| Topic | Reference File |
|-------|---------------|
| chat.db schema, tables, columns, SQL queries | [database-schema.md](references/database-schema.md) |
| AppleScript / osascript sending examples | [applescript-sending.md](references/applescript-sending.md) |
| Python sqlite3 reading examples | [python-reading.md](references/python-reading.md) |
| Permissions (TCC, FDA, Automation) | [permissions.md](references/permissions.md) |
| Third-party tools and open-source projects | [third-party-tools.md](references/third-party-tools.md) |
| Limitations, gotchas, macOS version issues | [limitations.md](references/limitations.md) |

## Core Architecture

iMessage on macOS stores all data locally in a SQLite database at:

```
~/Library/Messages/chat.db
```

There is **no public API** from Apple for programmatic iMessage access. All automation relies on:
1. **AppleScript / osascript** — to send messages via Messages.app (official, but limited)
2. **Direct SQLite queries** — to read messages from `chat.db` (read-only; no write to DB)
3. **File system access** — attachments stored in `~/Library/Messages/Attachments/`

### Key File System Locations

```
~/Library/Messages/
├── chat.db          # Main SQLite database (all messages, chats, handles)
├── chat.db-shm      # SQLite shared memory (WAL mode)
├── chat.db-wal      # SQLite write-ahead log (updates appear here first)
└── Attachments/     # All attachment files, organized in subdirectories
    └── <hex>/       # e.g., 00/00/, 01/01/, etc.
```

The WAL file (`chat.db-wal`) means new messages appear there seconds or minutes before they are checkpointed into `chat.db`. Use `PRAGMA wal_checkpoint;` or simply open in read mode and SQLite will read both automatically.

## Sending Messages — Minimal Examples

### Send an iMessage via osascript (one-liner)

```bash
osascript -e 'tell application "Messages"
  set targetService to 1st service whose service type = iMessage
  set targetBuddy to buddy "+15555550100" of targetService
  send "Hello from terminal" to targetBuddy
end tell'
```

### Send to an email address

```bash
osascript -e 'tell application "Messages"
  set targetService to 1st service whose service type = iMessage
  set targetBuddy to buddy "user@example.com" of targetService
  send "Hello" to targetBuddy
end tell'
```

## Reading Messages — Minimal Example (Python)

```python
import sqlite3

DB = "~/Library/Messages/chat.db"
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("""
    SELECT
        datetime(m.date / 1000000000 + strftime('%s','2001-01-01'), 'unixepoch', 'localtime') AS ts,
        h.id AS sender,
        m.text,
        m.is_from_me
    FROM message m
    JOIN handle h ON h.ROWID = m.handle_id
    ORDER BY m.date DESC
    LIMIT 20
""")
for row in cur.fetchall():
    print(row)
conn.close()
```

**Date conversion note:** Dates are stored as nanoseconds since 2001-01-01 (Mac Absolute Time). Divide by 1,000,000,000 to get seconds, then add the Unix offset for 2001-01-01.

## Critical macOS Version Gotchas

- **macOS Mojave+**: `~/Library/Messages` requires Full Disk Access granted to Terminal/Python.
- **macOS Big Sur (11)**: Messages.app was rewritten; AppleScript reliability degraded.
- **macOS Ventura (13)+**: Many messages are no longer stored as plain text in `message.text`. They are stored as a binary plist blob in `message.attributedBody`. Plain SQL `text` queries will return NULL for these messages — you must decode `attributedBody`.
- **WAL mode**: `chat.db-wal` holds recent writes; always open in read mode to get current data.
