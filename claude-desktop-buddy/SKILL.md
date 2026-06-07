---
name: claude-desktop-buddy
description: >
  Build BLE hardware companions for Claude Desktop — physical devices that display session status,
  pending permission prompts, token counts, and let you approve or deny tool calls from a button.
  Use when designing or implementing any hardware that connects to Claude Desktop over Bluetooth LE:
  the reference M5StickC Plus desk pet, custom approval panels, token meters, e-ink ambient displays,
  wearable bands, or any ESP32/nRF52/Raspberry Pi project using the Nordic UART Service protocol.
  Based on the open-source repo anthropics/claude-desktop-buddy and its REFERENCE.md wire spec.
---

# Claude Desktop Buddy

Build physical hardware that connects to Claude Desktop (macOS/Windows) over Bluetooth LE.
The protocol is hardware-agnostic — any device that speaks BLE Nordic UART Service works.

**Repo:** `https://github.com/anthropics/claude-desktop-buddy`

## Quick Start (Reference Hardware: M5StickC Plus)

```bash
git clone https://github.com/anthropics/claude-desktop-buddy
cd claude-desktop-buddy
pio run -t upload                          # flash firmware
# Previously flashed device: pio run -t erase && pio run -t upload
```

**Pair with Claude Desktop:**
1. Help → Troubleshooting → Enable Developer Mode
2. Developer → Open Hardware Buddy…
3. Click Connect → pick device from BLE list
4. macOS prompts for Bluetooth permission once; grant it

Bridge auto-reconnects — the window is only needed for initial pairing, the stats panel, or dropping character folders.

**Factory reset from device:** hold A → settings → reset → factory reset → tap twice

## Protocol Mental Model

```
Claude Desktop                          Your Device
──────────────                          ───────────
Heartbeat (every 10s or on change) ──► parse JSON state
                                        render display / LEDs
Turn events (per completed turn)   ──► optional: log/display

                    ◄── {"cmd":"permission","id":"...","decision":"once"}
                    ◄── {"cmd":"permission","id":"...","decision":"deny"}
                    ◄── {"ack":"status", "data":{...}}  (reply to poll)
```

**Transport:** BLE Nordic UART Service (NUS), newline-delimited UTF-8 JSON.
Advertise name starting with `Claude` (e.g. `Claude-AABB` using last 2 MAC bytes).

Key derived signals from heartbeat:
- `running > 0` — at least one session generating
- `waiting > 0` — permission prompt is blocking, device should alert
- `total == 0` — nothing open, show sleep state
- No snapshot for ~30s — treat connection as dead

## Reference Files

| File | When to read |
|------|-------------|
| [references/protocol.md](references/protocol.md) | Full wire protocol — all UUIDs, message schemas, ack table, folder-push flow |
| [references/firmware.md](references/firmware.md) | ESP32/M5StickC Plus firmware setup, PlatformIO config, architecture, animation states |
| [references/characters.md](references/characters.md) | Custom character pack format, manifest.json, GIF specs, compression, push workflow |
| [references/alternative-builds.md](references/alternative-builds.md) | 5 non-desk-pet project ideas: traffic light, token meter, e-ink display, approval puck, wearable band |
| [references/security.md](references/security.md) | BLE bonding, LE Secure Connections, encryption requirements, path validation |

## Related

For programming and using the M5StickC PLUS / PLUS2 hardware itself (pinout, sensors, Arduino/UIFlow/
MicroPython, and other project ideas) beyond this BLE buddy, see the `m5stickc-plus-expert` skill.

## Gotchas

- The BLE API only works when Claude Desktop is in **developer mode** — not available in normal mode.
- `prompt.id` must be echoed back exactly in permission decisions; a mismatched id is silently ignored.
- Multi-packet BLE notifications fragment at the MTU boundary — accumulate bytes until `\n` before parsing JSON.
- `tokens_today` resets at local midnight and survives app restarts. `tokens` is cumulative since app launch only.
- The `"once"` decision approves a single tool call; there is no `"always"` option in the protocol.
- Folder push is sequential — send next chunk only after receiving ack for the previous one. No pipelining.
- GIFs for custom characters must be exactly **96px wide**; other widths are not rendered correctly.
- If your device doesn't want pushed files, simply don't ack `char_begin` — desktop times out and reports failure.
- `turn` events larger than 4KB are silently dropped by the desktop.
