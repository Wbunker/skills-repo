# iMessage Automation — Limitations, Gotchas, and macOS Version History

## What IS Possible

| Capability | Method | Notes |
|-----------|--------|-------|
| Send iMessage to phone number | AppleScript / osascript | Contact must be known to Messages.app |
| Send iMessage to email | AppleScript / osascript | Same requirement |
| Send SMS (via iPhone relay) | AppleScript / osascript | Requires iPhone on same Apple ID with Text Message Forwarding enabled |
| Send file/attachment | AppleScript / osascript | Provide POSIX file path |
| Read all message history | Direct SQLite on chat.db | Requires Full Disk Access |
| Search messages | SQL query on chat.db | Full text search via `LIKE` or FTS5 |
| List all conversations | SQL query on chat.db | |
| Get attachment file paths | SQL query on chat.db | `attachment.filename` column |
| React to incoming messages | Poll chat.db or use `imsg watch` | No push; must poll or use filesystem watch |
| Send to group chat | AppleScript (limited) or imessage_tools | Group chat must exist and be named |
| Read reactions (tapbacks) | SQL query on chat.db | Via `associated_message_type` column |
| Read thread replies | SQL query on chat.db | Via `thread_originator_guid` / `reply_to_guid` |

---

## What is NOT Possible

| Capability | Why Not Possible |
|-----------|-----------------|
| Receive message push notifications / callbacks | Apple removed the AppleScript `on message received` handler; no event API |
| Read iMessage end-to-end encrypted content from another device | E2E encryption; content is only decrypted on the local device |
| Send iMessage from a non-Apple device without a Mac | Apple requires an Apple ID authenticated on Apple hardware |
| Access iMessage from a sandboxed App Store app | Apple does not grant the `com.apple.security.personal-information.messages` entitlement to third parties |
| Mark messages as read programmatically | No API; only Messages.app can mark messages read |
| Delete messages programmatically | No public API; writing to chat.db is unsupported and dangerous |
| Create new iMessage accounts | Must use Apple ID credentials through Apple's servers |
| Read iMessages not synced to the Mac | iCloud Message sync must be enabled, or messages only exist on iPhone |
| Access FaceTime from automation | No AppleScript dictionary for FaceTime calls |
| Send Tapbacks/reactions programmatically | AppleScript cannot send tapbacks |
| Send "invisible ink" or other message effects | Not exposed in AppleScript |

---

## macOS Version-Specific Issues

### macOS Mojave (10.14) — 2018
- **Introduced:** Full Disk Access (FDA) requirement for `~/Library/Messages/`
- Before Mojave, any app could read `chat.db` without special permissions

### macOS Catalina (10.15) — 2019
- FDA enforcement tightened; Terminal and Python both need explicit FDA grants
- SQLite clients (TablePlus, DB Browser) also need FDA

### macOS Big Sur (11) — 2020
- **Messages.app was rewritten** as a Mac Catalyst app (iOS codebase ported to Mac)
- AppleScript dictionary support degraded significantly
- Known issue: Scripts may send to wrong recipients in edge cases
- Only ~200 of many more conversations may be accessible via AppleScript's `text chats`
- Occasional silent failures where messages appear to send but do not

### macOS Monterey (12) — 2021
- No major new iMessage automation changes
- `SharePlay` iMessage extensions added (not scriptable)
- Undo send and message editing not exposed via AppleScript

### macOS Ventura (13) — 2022 — MAJOR BREAKING CHANGE
- **attributedBody encoding**: Many messages are no longer stored as plain text in `message.text`. The content is in `message.attributedBody` as a binary plist (NSAttributedString / typedstream format)
- Scripts and tools that read `message.text` directly will get NULL for these messages
- Fix: Decode `attributedBody` using plistlib or byte-pattern extraction (see [python-reading.md](python-reading.md))
- Not all messages are affected — some still have plain `text` content; the pattern seems related to message length, content, and sender

### macOS Sonoma (14) — 2023
- iMessage Contact Key Verification (Advanced Data Protection) — does not affect local `chat.db` access but means some metadata may be more restricted
- No new AppleScript capabilities added
- `imsg` tool by steipete requires macOS 14+

### macOS Sequoia (15) — 2024
- RCS support added to Messages (Rich Communication Services)
- RCS messages stored in `chat.db` under service type `SMS` (they use the SMS infrastructure column but may be RCS)
- No new automation APIs

---

## Encryption Considerations

iMessage uses **end-to-end encryption**:
- Messages are encrypted in transit between devices using per-device keys
- On your local Mac, messages are stored **decrypted** in `chat.db` — they are readable by any process with filesystem access to that file
- iCloud Messages backup (if enabled) stores messages encrypted at rest; Apple holds the keys for standard backup, but Advanced Data Protection uses user-held keys
- There is no way to read iMessages from another person's device or from encrypted transit

**For forensic/legal purposes:** The plaintext in `chat.db` is the most accessible source; device extraction tools (Cellebrite, etc.) use this same database.

---

## Common Gotchas

### 1. `text` is NULL in Ventura+
The `message.text` column is NULL for many messages in macOS 13+. You must also check `attributedBody`. See [database-schema.md](database-schema.md) for the decoder.

### 2. Timestamps seem wrong
- Divide by 1,000,000,000 (nanoseconds), not 1 (seconds)
- Older macOS versions stored as seconds; divide by the right factor based on the magnitude of the value
- All timestamps are in UTC; use `'localtime'` modifier in SQLite for local time

### 3. WAL file has newer data than chat.db
SQLite WAL mode means `chat.db-wal` contains the most recent writes. Always open in read mode (`mode=ro`) and SQLite automatically reads both files. Do NOT try to manually merge the WAL.

### 4. Messages to group chats fail silently
AppleScript's group chat support is unreliable. Use the chat index approach or `imessage_tools` library.

### 5. Contact not found error
```
Error: Messages got an error: Invalid parameter.
```
This means Messages.app doesn't recognize the phone number or email as a known contact/buddy. The contact must:
- Have previously exchanged a message with you, OR
- Be in your Contacts with an iMessage-registered identifier
- Phone numbers must be in E.164 format (`+15555550100`, not `555-555-0100`)

### 6. Permissions reset after macOS update
Major macOS updates sometimes reset TCC permissions. Re-grant FDA and Automation after major updates.

### 7. Multiple accounts / phone numbers
If the Mac is signed into multiple Apple IDs or has multiple phone numbers, `1st service whose service type = iMessage` picks the first one. Be explicit if you have multiple:
```applescript
-- List all services
tell application "Messages"
    get every service
end tell
```

### 8. Script runs but nothing happens
Likely causes:
- Automation permission was previously denied — reset with `tccutil reset AppleEvents com.apple.Terminal`
- Messages.app is not running — add `tell application "Messages" to activate` first
- The buddy doesn't exist — use `exists` check

### 9. Attachment paths use `~` shorthand
The `attachment.filename` column stores paths like `~/Library/Messages/Attachments/...`. Expand with `os.path.expanduser()` in Python before checking if the file exists.

### 10. Deleted messages still in DB
The `deleted_messages` table tracks soft-deleted messages. The `message` table may still contain rows for deleted messages. Filter with `WHERE m.ROWID NOT IN (SELECT message_id FROM deleted_messages)` if needed.

---

## Security and Privacy Considerations

- Granting Full Disk Access to Terminal gives that terminal access to essentially everything on the Mac, not just Messages
- Any script reading `chat.db` gets your complete message history including content, timestamps, and contact information
- Third-party tools like BlueBubbles that run as a background server should be treated with appropriate trust level
- The `chat.db` file should be treated as highly sensitive data
