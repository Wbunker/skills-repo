# BLE Security

## Why It Matters

The heartbeat stream includes transcript snippets (`entries[]`), tool names, and command hints (`prompt.hint`). An unencrypted BLE device is sniffable by anyone within radio range (~10-30m) using a cheap nRF Sniffer dongle. Encrypt the link.

## Recommended: LE Secure Connections Bonding

1. **Mark NUS characteristics as encrypted-only** — RX (6e400002), TX (6e400003), and the TX CCCD descriptor should all require an encrypted link.
2. **Advertise DisplayOnly IO capability** — the device shows a 6-digit passkey on screen; the user enters it in the OS pairing dialog on first connect.
3. **First GATT access triggers OS pairing** — Claude Desktop prompts the user for the passkey. After pairing, the link is AES-CCM encrypted using the negotiated LTK.
4. **Subsequent reconnects** reuse the stored LTK without re-prompting.

## Protocol Hooks for Security State

**Report encryption status in status ack:**
```json
{
  "ack": "status",
  "ok": true,
  "data": {
    "sec": true,   // true once LE Secure Connections bonding complete
    ...
  }
}
```
Omit `sec` or set `false` if your device doesn't bond. Claude Desktop's Hardware Buddy window shows this field.

**Handle unpair command:**
```json
// Desktop sends when user clicks "Forget":
{"cmd": "unpair"}

// Device erases stored bonds (LTKs from NVS) and acks:
{"ack": "unpair", "ok": true, "n": 0}
```
After erasing bonds, the next pairing shows a fresh passkey. This is how the user re-pairs a device or transfers it to another computer.

## Unencrypted Devices

Claude Desktop connects to both encrypted and unencrypted devices. The protocol works either way, but transcript content flows in plaintext over an unencrypted link. If your project is for personal/local use in a controlled environment, unencrypted is acceptable. For shared spaces or any deployment where the device isn't physically controlled, use bonding.

## Folder Push Path Validation

The folder-push protocol (`char_begin` / `file` / `chunk`) sends whatever filenames are in the dropped folder without sanitizing. Your device must validate `file.path` before writing:

```python
# Pseudocode — implement in whatever language your firmware uses
def is_safe_path(path):
    # Reject absolute paths
    if path.startswith("/") or path.startswith("\\"):
        return False
    # Reject path traversal
    parts = path.replace("\\", "/").split("/")
    if ".." in parts:
        return False
    # Reject empty or dot-only components
    if any(p == "" or p == "." for p in parts):
        return False
    return True
```

If `file.path` fails validation, send `{"ack":"file","ok":false,"error":"invalid path"}` and abort the transfer.

## ESP32 / M5StickC Plus Implementation Notes

The reference firmware uses NimBLE (via Arduino NimBLE-Arduino) with encrypted-only characteristics. `bleSecure()` returns `true` once the link is bonded; `main.cpp` reads this to populate the `sec` field in status responses. `bleClearBonds()` is called on `{"cmd":"unpair"}` and on factory reset.

## nRF52 Notes

The nRF52840 supports LE Secure Connections natively via the SoftDevice or Zephyr BLE stack. Set `BT_SECURITY_L2` (encryption required) on the NUS service. Use `CONFIG_BT_SMP` in Zephyr. The passkey display flow is handled by the BT_PASSKEY_DISPLAY callback.
