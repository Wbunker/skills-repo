# Third-Party Tools for iMessage on macOS

## CLI Tools

### imsg (steipete/imsg)
**GitHub:** https://github.com/steipete/imsg
**Language:** Swift / compiled binary
**macOS requirement:** macOS 14+
**Approach:** Reads `chat.db` directly (read-only); sends via AppleScript

The most comprehensive single-binary CLI tool. Event-driven message watching via filesystem notifications.

```bash
# Build from source
git clone https://github.com/steipete/imsg
cd imsg && make build
./bin/imsg --help

# List recent chats
imsg chats --limit 20 --json

# View conversation history
imsg history --chat-id +15555550100 --limit 50 --attachments --json

# Stream new messages in real time
imsg watch --json

# Watch a specific chat
imsg watch --chat-id +15555550100 --json

# Send a message
imsg send --to +15555550100 --text "Hello"
imsg send --to +15555550100 --file /path/to/image.jpg --service imessage

# Send with service selection
imsg send --to user@example.com --text "Hello" --service auto
```

**Permissions needed:** Full Disk Access + Automation (Messages)

---

### imessage-cli (macos-cli-tools)
**GitHub:** https://github.com/macos-cli-tools/imessage-cli
**Language:** TypeScript / Bun
**Features:** 44 commands including semantic search, spam detection, bulk operations

```bash
# Example usage
imessage-cli messages list
imessage-cli messages send --to "+15555550100" --body "Hello"
imessage-cli chats list
```

---

## Python Libraries

### imessage_tools
**GitHub:** https://github.com/my-other-github-account/imessage_tools
**Approach:** Reads `chat.db` + decodes `attributedBody`; sends via AppleScript subprocess
**Best for:** Ventura+ compatibility (handles attributedBody encoding)

```bash
pip install git+https://github.com/my-other-github-account/imessage_tools.git
```

```python
from imessage_tools import read_messages, send_message

# Read messages (handles attributedBody automatically)
messages = read_messages(
    db_location="~/Library/Messages/chat.db",
    n=10,                     # number of messages; None = all
    self_number="Me",         # label to use for yourself
    human_readable_date=True  # True = string date, False = raw timestamp
)

for m in messages:
    print(m)
# Returns list of dicts with keys:
# rowid, body, phone_number, is_from_me, cache_roomname, group_chat_name, date

# Send to individual
send_message("Hello!", "+15555550100", group_chat=False)

# Send to group chat (group chat must already be named on this Mac)
send_message("Hello group!", "My Group Name", group_chat=True)
```

---

### imessage_reader (niftycode)
**GitHub:** https://github.com/niftycode/imessage_reader
**PyPI:** `pip install imessage-reader`
**Approach:** Forensic tool, read-only

```bash
pip install imessage-reader
```

```python
from imessage_reader import fetch_data

fd = fetch_data.FetchData()

# Get all messages
messages = fd.get_messages()
# Returns list of (name, text, date, service, account, is_from_me) tuples

# Write to Excel
fd.show_in_excel()

# Print statistics
fd.statistics()
```

---

### pymessage-lite (mattrajca)
**GitHub:** https://github.com/mattrajca/pymessage-lite
**Approach:** Simple read-only library, direct sqlite3

```python
import pymessage

# Get all handles (contacts)
handles = pymessage.get_handles()

# Get messages for a handle
messages = pymessage.get_messages(handle)
```

---

### py-iMessage (Rolstenhouse)
**GitHub:** https://github.com/Rolstenhouse/py-iMessage
**Approach:** Send-only via AppleScript subprocess

```python
from imessage import iMessage

im = iMessage()
im.send("+15555550100", "Hello from Python")
```

---

### LangChain iMessage Chat Loader
**Package:** `langchain-community`
**Use case:** Load iMessage history into LangChain for LLM processing

```python
from langchain_community.chat_loaders.imessage import IMessageChatLoader
from langchain_community.chat_loaders.utils import map_ai_messages

loader = IMessageChatLoader(path="~/Library/Messages/chat.db")
raw_messages = loader.load()

# Map messages to ai/human roles based on sender
chat_sessions = list(map_ai_messages(raw_messages, sender="Me"))
```

---

## Server / Bridge Tools

### BlueBubbles
**Website:** https://bluebubbles.app
**GitHub:** https://github.com/BlueBubblesApp
**Type:** Mac server + cross-platform clients (Android, Windows, Linux, Web)
**Approach:** Runs a server on the Mac; proxies iMessage to other devices
**License:** Open source

BlueBubbles is the most production-ready solution for accessing iMessage from non-Apple devices. The Mac server:
- Reads `chat.db` for message history
- Sends messages via AppleScript
- Uses filesystem watching for real-time message delivery
- Exposes a REST API and WebSocket API

**Requirements:** macOS with Messages.app signed in, Full Disk Access for server process

**API Example (local REST):**
```bash
# Get chats
curl http://localhost:1234/api/v1/chat?password=yourpassword

# Send message
curl -X POST http://localhost:1234/api/v1/message/text \
  -H "Content-Type: application/json" \
  -d '{"chatGuid": "iMessage;-;+15555550100", "message": "Hello", "password": "yourpassword"}'
```

---

### mautrix-imessage (Beeper/Matrix bridge)
**GitHub:** https://github.com/beeper/imessage
**Type:** Matrix protocol bridge
**Approach:** Bridges iMessage to Matrix; runs on Mac
**Use case:** Access iMessage from Matrix clients (Element, etc.)

This was developed by Beeper and is now open source. It runs on the Mac with Full Disk Access and Automation permissions, and bridges iMessage conversations to the Matrix protocol.

---

### Beeper (Historical context)
Beeper previously offered iMessage bridging via:
1. A Mac-hosted bridge (same as mautrix-imessage)
2. "Beeper Mini" (Android app, Dec 2023) — connected directly to Apple servers without a Mac, but was shut down by Apple in Jan 2024

The Mac-hosted bridge approach remains the only stable iMessage access method for non-Apple devices.

---

## Shell / Utility Scripts

### GitHub Gist: hepcat72 (SMS + iMessage with fallback)
https://gist.github.com/hepcat72/6b7abd9000e8b108ecdb76e12da1257e
Features: attachment support, service fallback, environment variable config

### GitHub Gist: homam (simple send by chat index or buddy name)
https://gist.github.com/homam/0119797f5870d046a362

### imessage-anywhere (drbh)
**GitHub:** https://github.com/drbh/imessage-anywhere
A Flask web app that polls `chat.db` and renders messages in a browser. Primarily a demo.

---

## Forensic / Analysis Tools

### plaso (log2timeline)
**GitHub:** https://github.com/log2timeline/plaso
Forensic timeline tool with an iMessage parser (`plaso/parsers/sqlite_plugins/imessage.py`).
Used by digital forensics professionals to extract iMessage data from disk images.

---

## Comparison Table

| Tool | Language | Read | Send | Ventura+ | Stars (approx) |
|------|----------|------|------|----------|----------------|
| imsg | Swift | Yes | Yes (AppleScript) | Yes | ~1k |
| imessage-cli | TypeScript | Yes | Yes | Yes | ~500 |
| imessage_tools | Python | Yes | Yes | Yes | ~300 |
| imessage_reader | Python | Yes | No | Partial | ~200 |
| pymessage-lite | Python | Yes | No | No | ~200 |
| BlueBubbles | Go/JS | Yes | Yes | Yes | ~3k |
| mautrix-imessage | Go | Yes | Yes | Yes | ~1k |
