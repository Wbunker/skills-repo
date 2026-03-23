# AppleScript / osascript — Sending iMessages on macOS

## Official Support

Apple's Messages.app has AppleScript support documented in its scripting dictionary. There is no other official API. Interaction is exclusively through:
- AppleScript (`.applescript` / `.scpt` files)
- `osascript` command-line tool
- Automator (uses AppleScript under the hood)

## Permissions Required

Before any script can control Messages.app, macOS will prompt for **Automation permission**. The user must click "OK" in the system dialog. This is stored in TCC and does not need to be repeated unless permissions are reset.

You can verify automation permission status in:
`System Settings > Privacy & Security > Automation`

---

## Basic Send — iMessage to Phone Number

```applescript
tell application "Messages"
    set targetService to 1st service whose service type = iMessage
    set targetBuddy to buddy "+15555550100" of targetService
    send "Hello from AppleScript" to targetBuddy
end tell
```

Run from terminal:
```bash
osascript -e 'tell application "Messages"
    set targetService to 1st service whose service type = iMessage
    set targetBuddy to buddy "+15555550100" of targetService
    send "Hello" to targetBuddy
end tell'
```

## Basic Send — iMessage to Email Address

```applescript
tell application "Messages"
    set targetService to 1st service whose service type = iMessage
    set targetBuddy to buddy "user@example.com" of targetService
    send "Hello from AppleScript" to targetBuddy
end tell
```

## Inline Shell One-Liner with Variables

```bash
PHONE="+15555550100"
MSG="Hello from shell script"
osascript <<EOF
tell application "Messages"
    set targetService to 1st service whose service type = iMessage
    set targetBuddy to buddy "$PHONE" of targetService
    send "$MSG" to targetBuddy
end tell
EOF
```

## Send via SMS (non-iMessage)

```applescript
tell application "Messages"
    set targetService to 1st service whose service type = SMS
    set targetBuddy to buddy "+15555550100" of targetService
    send "Hello via SMS" to targetBuddy
end tell
```

## Auto-detect Service (iMessage with SMS fallback)

```applescript
tell application "Messages"
    set thePhone to "+15555550100"
    set theMessage to "Hello"
    try
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy thePhone of targetService
        send theMessage to targetBuddy
    on error
        set targetService to 1st service whose service type = SMS
        set targetBuddy to buddy thePhone of targetService
        send theMessage to targetBuddy
    end try
end tell
```

## Send with Error Handling

```applescript
try
    tell application "Messages"
        if not (exists window 1) then
            -- Messages is not open; you may need to activate it first
        end if
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "+15555550100" of targetService
        send "Hello" to targetBuddy
    end tell
on error errMsg number errNum
    display dialog "Error " & errNum & ": " & errMsg
end try
```

## Send to an Existing Text Chat by Index

```applescript
-- Send to the first conversation in the text chats list
tell application "Messages"
    set theChats to text chats
    send "Hello" to item 1 of theChats
end tell
```

## Send an Attachment / File

```applescript
tell application "Messages"
    set targetService to 1st service whose service type = iMessage
    set targetBuddy to buddy "+15555550100" of targetService
    set theFile to POSIX file "/Users/username/Desktop/photo.jpg"
    send theFile to targetBuddy
end tell
```

Shell wrapper:
```bash
PHONE="+15555550100"
FILE_PATH="/Users/username/Desktop/photo.jpg"
osascript <<EOF
tell application "Messages"
    set targetService to 1st service whose service type = iMessage
    set targetBuddy to buddy "$PHONE" of targetService
    set theFile to POSIX file "$FILE_PATH"
    send theFile to targetBuddy
end tell
EOF
```

## Send to a Group Chat

Group chats must be identified by their `chat_identifier` value from `chat.db`, or by the room name. The most reliable approach is to look up the chat_identifier first:

```bash
# Find group chat identifier in the database
sqlite3 ~/Library/Messages/chat.db "SELECT chat_identifier, display_name FROM chat WHERE room_name IS NOT NULL ORDER BY last_readable_interaction_timestamp DESC LIMIT 20;"
```

Then send to it:
```applescript
tell application "Messages"
    -- Find the chat by its identifier
    set groupChat to (text chats whose name is "My Group Chat Name")
    if (count of groupChat) > 0 then
        send "Hello group" to item 1 of groupChat
    end if
end tell
```

Alternatively, use the `imessage_tools` Python library which handles group chats robustly (see [third-party-tools.md](third-party-tools.md)).

## Send from Command Line with Arguments (.applescript file)

Save as `send_message.applescript`:
```applescript
on run argv
    set thePhone to item 1 of argv
    set theMessage to item 2 of argv
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy thePhone of targetService
        send theMessage to targetBuddy
    end tell
end run
```

Run:
```bash
osascript send_message.applescript "+15555550100" "Hello from script"
```

## Send Attachment with Arguments

Save as `send_attachment.applescript`:
```applescript
on run argv
    set theFile to POSIX file (item 1 of argv)
    set theBuddy to item 2 of argv
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy theBuddy of targetService
        send theFile to targetBuddy
    end tell
end run
```

Run:
```bash
osascript send_attachment.applescript "/path/to/file.jpg" "+15555550100"
```

---

## Receiving / Triggering on Incoming Messages

**This no longer works as of macOS 10.x — Apple removed the ability to trigger an AppleScript on incoming messages.**

The old mechanism (`on message received`) was removed. The only way to react to incoming messages programmatically is to poll `chat.db` for new rows using a file system watcher or a cron/launchd job.

```bash
# Poll for new messages every 5 seconds using the chat.db WAL
# (requires Full Disk Access for Terminal)
while true; do
    sqlite3 ~/Library/Messages/chat.db \
        "SELECT datetime(date/1e9 + strftime('%s','2001-01-01'),'unixepoch','localtime'), text FROM message ORDER BY date DESC LIMIT 1;"
    sleep 5
done
```

For a proper event-driven approach, use the `imsg` CLI tool's `watch` command (see [third-party-tools.md](third-party-tools.md)).

---

## Known AppleScript Limitations

1. **Messages.app must be running** — Scripts that target Messages require it to be open. Some scripts handle this with `tell application "Messages" to activate`.

2. **Not all chats are exposed** — On some systems, only ~200 of potentially 1000+ conversations are accessible via AppleScript's `text chats` collection.

3. **Big Sur regression** — Messages was rewritten in macOS 11. AppleScript behavior became less reliable and has had intermittent regressions through subsequent releases.

4. **Wrong recipient risk** — There are documented cases where Messages sends to the wrong person when using the `buddy` approach if the contact lookup is ambiguous. Always verify the exact identifier used.

5. **No read confirmation from AppleScript** — You cannot check delivery or read status via AppleScript; use `chat.db` queries for that.

6. **Special characters** — Messages with special characters (quotes, backslashes, Unicode) can break shell heredoc approaches. Use `.applescript` files or the `imessage_tools` library instead.

7. **SMS relay requires iPhone** — SMS sending via Messages.app requires an iPhone on the same Apple ID with "Text Message Forwarding" enabled pointing to the Mac.
