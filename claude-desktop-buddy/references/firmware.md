# Firmware Reference (ESP32 / M5StickC Plus)

Reference firmware architecture for the `anthropics/claude-desktop-buddy` repo.
Read this when working with the ESP32 firmware, setting up PlatformIO, or porting to new hardware.

## Hardware

**Reference board:** M5StickC Plus (~$25)
- ESP32 MCU
- 135×240 color TFT display
- Two buttons: A (front face), B (right side)
- IMU (accelerometer for shake detection)
- USB-C charging, onboard battery
- Red LED (pin 10, active-low)

Any ESP32 board works with driver substitution (swap M5StickCPlus lib calls for your pin layout).

## PlatformIO Setup

```ini
# platformio.ini
[env:m5stickc-plus]
platform = espressif32
board = m5stick-c
framework = arduino
monitor_speed = 115200
board_build.filesystem = littlefs
board_build.partitions = no_ota.csv
board_build.f_cpu = 160000000L
build_flags =
    -DCORE_DEBUG_LEVEL=0
build_src_filter = +<*> +<buddies/>
lib_deps =
    m5stack/M5StickCPlus
    bitbank2/AnimatedGIF @ ^2.1.1
    bblanchon/ArduinoJson @ ^7.0.0
```

**Flash commands:**
```bash
pio run -t upload
pio run -t erase && pio run -t upload   # if previously flashed with something else
pio device monitor                       # serial monitor at 115200
```

## Source File Map

```
src/
├── main.cpp          — setup/loop, display rendering, button handling, state machine
├── ble_bridge.cpp/h  — BLE NUS init, connect/disconnect, read/write, bond management
├── buddy.cpp/h       — ASCII character renderer, species selection, animation loop
├── buddy_common.h    — shared types for ASCII buddy system
├── character.cpp/h   — GIF character renderer (AnimatedGIF lib), LittleFS reads
├── data.h            — TamaState struct (heartbeat fields), JSON parsing
├── stats.h           — approval/denial counters, level/velocity tracking
├── xfer.h            — folder-push receive state machine
└── buddies/          — 18 ASCII buddy implementations (axolotl, blob, cat, duck, etc.)
```

## Seven Animation States

State transitions are driven by the heartbeat `total`/`running`/`waiting` fields and device events.

| State | Trigger | Visual |
|-------|---------|--------|
| `sleep` | Bridge disconnected (`total == 0` or no BLE) | Eyes closed, slow breathing |
| `idle` | Connected, nothing happening | Blinks, looks around |
| `busy` | `running > 0` | Sweating, frantic movement |
| `attention` | `waiting > 0` | Alert, LED blinks red |
| `celebrate` | Every 50K cumulative tokens | Confetti, bouncing |
| `dizzy` | IMU shake detected | Spiral eyes, wobbling |
| `heart` | Permission approved within 5 seconds | Floating hearts |

State priority: `attention` > `busy` > `celebrate` > `idle` > `sleep`.
One-shot states (`dizzy`, `heart`, `celebrate`) play once then revert to base state.

## Button Mapping

| Button | Short press | Long press |
|--------|------------|------------|
| A (front) | Approve pending permission (`"once"`) | Open settings menu |
| B (right) | Deny pending permission (`"deny"`) | — |

When no permission is pending, A/B cycle display modes (normal / pet view / info).

## Display Modes

The device cycles through three display modes:
1. **Normal** — status panel: session counts, token totals, recent entries, permission hint
2. **Pet** — full-screen character animation
3. **Info** — device info pages: BT name, battery, heap, approval stats, passkey (during pairing)

## BLE Name Advertising

The firmware reads the last 2 bytes of the BT MAC address and builds the name at boot:
```cpp
snprintf(btName, sizeof(btName), "Claude-%02X%02X", mac[4], mac[5]);
bleInit(btName);
```
This keeps multiple devices distinguishable in the desktop picker.

## Character System

Two rendering modes, switchable from the device menu:

1. **ASCII mode** — 18 built-in character species drawn with TFT primitives (no file system needed)
2. **GIF mode** — AnimatedGIF library reads GIF files from LittleFS, installed via folder push

Cycle through them with the device menu or `nextPet()`. The selected species/mode persists to NVS across reboots (key: `"species"`; value `0xFF` = GIF mode).

## Development Tools

```bash
# Flash a character pack over USB (faster than BLE drop)
python3 tools/flash_character.py characters/bufo

# Prepare/compress GIFs for a custom character pack
python3 tools/prep_character.py <source-folder>

# Interactive serial test (simulates heartbeats)
python3 tools/test_serial.py

# Test folder-push file transfer
python3 tools/test_xfer.py
```

## Porting to Other ESP32 Boards

To use hardware other than M5StickC Plus:
1. Change `board` in `platformio.ini` to match your board
2. Replace `M5StickCPlus` lib with appropriate display/button drivers
3. Update pin definitions in `main.cpp` (LED pin, display dimensions `W`/`H`)
4. Keep `ble_bridge.cpp` and `data.h` unchanged — they're hardware-independent
