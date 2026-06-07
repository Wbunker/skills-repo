# M5StickC PLUS / PLUS2 — Project Ideas

Cool things to build, matched to the StickC's onboard hardware, with build notes (libraries, Units,
gotchas). Each maps to peripherals covered in `hardware.md` and recipes in `arduino.md`.

## Quick picker

| Want to… | Project | Uses |
|---|---|---|
| Control any TV/AC/stereo | Universal IR remote / TV-B-Gone | IR LED, buttons, display |
| Wave to do things | Gesture wand / motion controller | IMU, BLE |
| Track steps / wear it | Smartwatch / step counter | IMU, RTC, Watch HAT |
| Watch room conditions | Wi-Fi sensor dashboard | ENV Unit, Wi-Fi, MQTT |
| Type/trigger macros | BLE HID keypad / presenter | BLE, buttons |
| Stay on schedule | Desk clock + Pomodoro timer | RTC, buzzer, display |
| Measure noise | Sound-level / clap meter | PDM mic |
| Catch motion | PIR alarm w/ push alert | PIR Unit/HAT, Wi-Fi |
| Play | Tilt mini-game | IMU, display, buzzer |
| See Claude status | Claude Desktop Buddy desk pet | BLE (see `claude-desktop-buddy` skill) |

## Projects

### 1. Universal IR Remote / TV-B-Gone
Send IR codes to control TVs, ACs, and stereos; cycle "power off" codes like TV-B-Gone, or map
buttons to specific devices. **Build:** `IRremoteESP8266` (`IRsend` on G9 PLUS / G19 PLUS2); store
codes in an array; BtnA = next device, BtnB = send. Add an IR *receiver* Unit to **learn** codes from
existing remotes. Extend: expose over Wi-Fi for Home Assistant.

### 2. Gesture Wand / Motion Controller
Read the MPU6886 to detect flicks, tilts, and shakes; act on them or send as BLE HID / Wi-Fi
commands (e.g., slide control, light toggle, game pad). **Build:** `M5.Imu` accel/gyro → threshold or
simple gesture classifier; send via `BLEDevice`/NimBLE as a HID. Tilt angle = `atan2(accel.y, accel.z)`.

### 3. Smartwatch / Step Counter (Watch HAT)
Wear it: show time from the **BM8563 RTC**, count steps from accel peaks, buzz alarms. **Build:** Watch
HAT strap; RTC for time, IMU for steps, deep sleep between updates for battery. UIFlow has watch-face
blocks for a fast start.

### 4. Wi-Fi Environmental Dashboard
Read temp/humidity/pressure from an **ENV IV Unit** (Grove) and show on-screen + publish to **MQTT /
Home Assistant / InfluxDB**. **Build:** `M5Unified` + Unit driver + `WiFi.h` + PubSubClient (MQTT).
Battery-friendly with deep-sleep reporting intervals.

### 5. BLE HID Keypad / Presenter / Macro Pad
Turn the two buttons (+ tilt) into a Bluetooth keyboard/mouse: slide clicker, mute toggle, custom
shortcuts. **Build:** `ESP32-BLE-Keyboard` / NimBLE HID; map BtnA/BtnB and IMU gestures to keystrokes.

### 6. Desk Clock + Pomodoro Timer
RTC clock face with a 25/5 Pomodoro cycle, buzzer chime, and a progress bar. **Build:** `M5.Rtc`,
`M5.Display` progress arc, `M5.Speaker.tone` for chimes; BtnA start/pause, BtnB reset.

### 7. Sound-Level / Clap Meter
Use the PDM mic to show a live dB-ish bar, peak hold, or clap-to-toggle. **Build:** `M5.Mic.record`
into a buffer, compute RMS, map to a bar; double-clap detection via peak timing. (FFT with `arduinoFFT`
for a spectrum.)

### 8. PIR Motion Alarm with Push Notification
Detect motion (PIR Unit/HAT), flash the screen + buzz, and send a phone alert. **Build:** PIR digital
input → Wi-Fi → ntfy/Telegram/IFTTT webhook; log timestamps with the RTC.

### 9. Tilt Mini-Game
A maze/ball/breakout controlled by tilting the stick. **Build:** IMU for control, M5GFX for sprites,
buzzer for SFX, buttons to start. Great first graphics project on the 135×240 screen.

### 10. Claude Desktop Buddy (BLE desk pet)
Show Claude session status, token counts, and approve/deny tool prompts from the button — an animated
desk pet. **Build:** use the dedicated **`claude-desktop-buddy`** skill (PlatformIO firmware + Nordic
UART Service protocol + character animations). This is the device's flagship "official" project.

### 11. Home Assistant / ESPHome Node
Adopt the StickC into Home Assistant via **ESPHome** (community config exists for PLUS2): expose the
buttons, IMU, and an IR remote as HA entities with no custom firmware code.

### 12. Wi-Fi Scanner / RSSI Meter
Scan nearby APs and chart signal strength / channel use on-screen — a pocket Wi-Fi analyzer. **Build:**
`WiFi.scanNetworks()` → bar chart. *(Keep to passive scanning of your own networks; active attacks /
deauth tooling are out of scope and often illegal.)*

## Tips for Any Project
- Start in **UIFlow2** to prototype Unit wiring, then port hot paths to **Arduino** for battery/timing.
- The battery is tiny — design around **deep sleep** and short wake bursts.
- Chain sensors via **Grove Units** (I2C) instead of soldering; mind the PLUS2 GPIO4 HOLD pin in any
  custom power code.
- Keep a button reserved for a clean **power off / menu** so a hung sketch is recoverable.
