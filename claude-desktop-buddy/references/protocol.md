# BLE Wire Protocol Reference

Full spec for the Claude Desktop Hardware Buddy BLE protocol.
Source: `REFERENCE.md` in `anthropics/claude-desktop-buddy`.

## Transport

**Service:** Nordic UART Service (NUS)

| Role | UUID |
|------|------|
| Service | `6e400001-b5a3-f393-e0a9-e50e24dcca9e` |
| RX — desktop→device (WRITE) | `6e400002-b5a3-f393-e0a9-e50e24dcca9e` |
| TX — device→desktop (NOTIFY) | `6e400003-b5a3-f393-e0a9-e50e24dcca9e` |

- Advertise name starting with `Claude` (e.g. `Claude-AABB` using last 2 BT MAC bytes)
- Wire format: **UTF-8, newline-delimited JSON** — one object per `\n`
- BLE notifications fragment at MTU boundary — both sides must accumulate bytes until `\n`

---

## Messages: Desktop → Device

### Heartbeat Snapshot

Sent on every state change plus a keepalive every 10 seconds.

```json
{
  "total": 3,
  "running": 1,
  "waiting": 1,
  "msg": "approve: Bash",
  "entries": ["10:42 git push", "10:41 yarn test", "10:39 reading file..."],
  "tokens": 184502,
  "tokens_today": 31200,
  "prompt": {
    "id": "req_abc123",
    "tool": "Bash",
    "hint": "rm -rf /tmp/foo"
  }
}
```

| Field | Meaning |
|-------|---------|
| `total` | Count of all open sessions |
| `running` | Sessions actively generating |
| `waiting` | Sessions blocked on a permission prompt |
| `msg` | One-line summary for small displays |
| `entries` | Recent transcript lines, newest first (capped) |
| `tokens` | Cumulative output tokens since app launch |
| `tokens_today` | Output tokens since local midnight (persists restarts, resets at midnight) |
| `prompt` | Only present when a permission decision is needed |
| `prompt.id` | Echo this back exactly in permission decisions |
| `prompt.tool` | Tool name (e.g. `"Bash"`, `"Edit"`) |
| `prompt.hint` | Short description of what's being requested |

**Key derived signals:**
- `running > 0` → at least one session generating
- `waiting > 0` → permission prompt blocking, alert the user
- `total == 0` → nothing open
- No snapshot for ~30s → treat connection as dead

### Turn Event

Fires once per completed assistant turn.

```json
{
  "evt": "turn",
  "role": "assistant",
  "content": [{ "type": "text", "text": "..." }]
}
```

Events larger than 4KB (UTF-8 bytes) are silently dropped by the desktop.

### One-Shot on Connect

Time sync (sent immediately on connection):
```json
{ "time": [1775731234, -25200] }
```
Fields: `[epoch_seconds, tz_offset_seconds]` (negative = west of UTC)

Owner name:
```json
{ "cmd": "owner", "name": "Felix" }
```

### Commands (expect ack)

Any message with a `cmd` field expects a matching ack:
```json
{ "ack": "<same-as-cmd>", "ok": true, "n": 0 }
```
Set `ok: false` and optionally `"error": "..."` on failure. `n` is a generic counter (bytes written for chunks, otherwise 0).

| Command | Payload | Purpose |
|---------|---------|---------|
| `{"cmd":"status"}` | — | Request device status (see Status Response) |
| `{"cmd":"name","name":"Clawd"}` | display name string | Set device display name |
| `{"cmd":"owner","name":"Felix"}` | owner name string | Set owner name on device |
| `{"cmd":"unpair"}` | — | Erase stored BLE bonds |

---

## Messages: Device → Desktop

### Permission Decision

Send when `prompt` is present in the heartbeat:

```json
{"cmd": "permission", "id": "req_abc123", "decision": "once"}
{"cmd": "permission", "id": "req_abc123", "decision": "deny"}
```

- `id` must match `prompt.id` exactly — mismatch is silently ignored
- `"once"` approves the single tool call; `"deny"` rejects it
- There is no `"always"` option

### Status Response

Reply to `{"cmd":"status"}`:

```json
{
  "ack": "status",
  "ok": true,
  "data": {
    "name": "Clawd",
    "sec": true,
    "bat": { "pct": 87, "mV": 4012, "mA": -120, "usb": true },
    "sys": { "up": 8412, "heap": 84200 },
    "stats": { "appr": 42, "deny": 3, "vel": 8, "nap": 12, "lvl": 5 }
  }
}
```

| Field | Meaning |
|-------|---------|
| `data.name` | Device display name |
| `data.sec` | `true` once LE Secure Connections bonding is complete |
| `data.bat.pct` | Battery percent |
| `data.bat.mV` | Battery voltage in millivolts |
| `data.bat.mA` | Current draw (negative = charging) |
| `data.bat.usb` | `true` if USB power present |
| `data.sys.up` | Uptime in seconds |
| `data.sys.heap` | Free heap in bytes |
| `data.stats.appr` | Lifetime approval count |
| `data.stats.deny` | Lifetime denial count |

All `data` fields are optional — omit what your hardware doesn't have.

---

## Folder Push Protocol

The Hardware Buddy window has a drop target. Dropping a folder streams flat file contents to the device (no recursion, dotfiles skipped). Used for character packs and config blobs. Max 1.8MB total.

```
desktop → device:  {"cmd":"char_begin","name":"bufo","total":184320}
device → desktop:  {"ack":"char_begin","ok":true}

desktop → device:  {"cmd":"file","path":"manifest.json","size":412}
device → desktop:  {"ack":"file","ok":true}

desktop → device:  {"cmd":"chunk","d":"<base64-encoded-bytes>"}
device → desktop:  {"ack":"chunk","ok":true,"n":<bytes_written_so_far>}
  ... repeat chunk/ack until file complete ...

desktop → device:  {"cmd":"file_end"}
device → desktop:  {"ack":"file_end","ok":true,"n":<final_file_size>}

  ... repeat file/chunk/file_end for each file in folder ...

desktop → device:  {"cmd":"char_end"}
device → desktop:  {"ack":"char_end","ok":true}
```

- `char_begin.name` = folder name, unless `manifest.json` has a `"name"` field (that wins)
- Protocol is sequential — wait for each ack before sending the next message
- Chunks are base64-encoded; decode and append to reconstruct the file
- If your device doesn't support folder push, don't ack `char_begin` — desktop times out and reports failure

**Security:** Validate `file.path` before writing. Reject `..` components and absolute paths. The desktop sends whatever filenames are in the dropped folder without sanitizing.

---

## Also available via USB / Bluetooth Classic

The reference firmware wires all three transports (BLE NUS, USB serial, BT Classic SPP) to the same JSON dispatch path. The wire format is identical. BLE is the primary path for production use; USB serial is convenient for development with `tools/test_serial.py`.
