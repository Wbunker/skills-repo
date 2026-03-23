# macOS Permissions for iMessage Automation

## Two Separate Permission Types Needed

Accessing and automating iMessage on macOS requires two distinct TCC (Transparency, Consent, and Control) permissions:

| Operation | Permission Needed | Where to Grant |
|-----------|------------------|----------------|
| Read `chat.db` (SQLite access) | **Full Disk Access (FDA)** | System Settings > Privacy & Security > Full Disk Access |
| Send messages via AppleScript / osascript | **Automation (control Messages.app)** | System Settings > Privacy & Security > Automation |

---

## Full Disk Access (FDA)

`~/Library/Messages/` is protected by macOS since **Mojave (10.14)**. Without FDA, any attempt to open `chat.db` will fail with:

```
OperationalError: unable to open database file
```

or the file will appear empty/inaccessible.

### Granting FDA

1. Open **System Settings** (macOS Ventura+) or **System Preferences** (older)
2. Go to **Privacy & Security > Full Disk Access**
3. Click the `+` button and add:
   - **Terminal.app** — if running Python scripts or sqlite3 from Terminal
   - **Python** (the specific binary, e.g., `/usr/local/bin/python3`) — if running Python directly
   - Your IDE or editor — if running scripts from within it
   - **iTerm2.app** — if using iTerm2 instead of Terminal
4. Toggle the switch to ON

### Verifying FDA

```bash
# This should succeed if FDA is granted to Terminal
sqlite3 ~/Library/Messages/chat.db ".tables"
```

If it returns nothing or errors, FDA is not granted.

### Important: Application-specific FDA

FDA is granted **per application**. If you grant it to Terminal but run a Python script via a different process (e.g., a background agent, a GUI app, or a different terminal emulator), that process will NOT have access. Each app needs its own FDA grant.

---

## Automation Permission (for Sending)

When an AppleScript or osascript first attempts to control Messages.app, macOS displays a dialog:

> "[App] wants access to control Messages. Allowing control will provide access to documents and data in Messages, and to perform actions within that app."

The user must click **OK** to grant this permission.

### Where It Lives

`System Settings > Privacy & Security > Automation`

You'll see the app listed there (e.g., Terminal → Messages: ON).

### Granting Programmatically (CLI — admin required)

```bash
# Reset Automation permission so the dialog re-appears (requires sudo)
tccutil reset AppleEvents com.apple.Terminal
```

### Checking Automation Permission

If a script runs silently and no message is sent (no error either), it usually means Automation permission was denied without a dialog (possible if previously denied). Reset with `tccutil` above.

---

## Contacts Permission (optional but useful)

To resolve phone numbers/emails to contact names, you need Contacts access:

`System Settings > Privacy & Security > Contacts`

This is only needed if your script calls the Contacts database. Reading `chat.db` does not require Contacts permission — the `handle.id` field gives raw phone numbers and emails.

---

## TCC Database Locations

macOS stores TCC permissions in SQLite databases:

| Scope | Path |
|-------|------|
| User-level | `~/Library/Application Support/com.apple.TCC/TCC.db` |
| System-level | `/Library/Application Support/com.apple.TCC/TCC.db` |

**Do not modify these directly.** Use `tccutil` or System Settings instead.

```bash
# View grants for your user (requires FDA or SIP disabled)
sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db \
  "SELECT client, service, allowed FROM access WHERE service='kTCCServiceSystemPolicyAllFiles';"
```

---

## SIP (System Integrity Protection)

SIP does not directly block iMessage access, but it does:
- Prevent modification of the TCC system database
- Block certain debugging/injection techniques

SIP does not need to be disabled for normal `chat.db` reading or AppleScript sending.

---

## Sandbox Restrictions

If you are building a **macOS app** (not a Terminal script) that needs to access Messages:
- The app must declare `com.apple.security.personal-information.messages` entitlement — **Apple does not grant this entitlement to third-party apps.** It is reserved for Apple.
- There is no App Store path to accessing iMessage data from a sandboxed app.
- Only non-sandboxed apps (outside the App Store) can request FDA through the system dialog.

**This is why all iMessage automation tools are distributed outside the App Store.**

---

## Summary: Minimum Setup for Common Tasks

### Read messages with Python from Terminal

```
Terminal → Full Disk Access: ON
```

```bash
# Test
python3 -c "import sqlite3; conn = sqlite3.connect('file:' + __import__('os').path.expanduser('~/Library/Messages/chat.db') + '?mode=ro', uri=True); print('OK:', conn.execute('.tables').fetchall())"
```

### Send messages via osascript from Terminal

```
Terminal → Automation → Messages: ON  (granted by system dialog on first run)
```

```bash
# Test (will prompt for permission if not already granted)
osascript -e 'tell application "Messages" to get name of every service'
```

### Both (read and send)

```
Terminal → Full Disk Access: ON
Terminal → Automation → Messages: ON
```
