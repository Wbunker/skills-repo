# M5StickC PLUS / PLUS2 — Arduino & PlatformIO (C++)

Programming the StickC in C++. Prefer **M5Unified** (+ **M5GFX**) — it auto-detects PLUS vs PLUS2 and
gives one portable API. Load when writing/uploading sketches or driving any peripheral from C++.

## Contents
- Toolchain setup (Arduino IDE)
- PlatformIO setup
- USB drivers & upload
- Library choice
- Minimal sketch
- Peripheral recipes (display, IMU, buttons, buzzer, IR, RTC, mic, WiFi, power, deep sleep)

## Toolchain Setup (Arduino IDE)
1. Install the **ESP32 boards** (Boards Manager → "esp32" by Espressif) — M5 also offers an M5Stack
   board package; either works with M5Unified.
2. Library Manager → install **M5Unified** (accept the M5GFX dependency). (Legacy alternatives:
   `M5StickCPlus`, `M5StickCPlus2` — device-specific, not portable.)
3. Select board: **"M5StickC Plus"** or **"M5StickC Plus2"**.
4. Pick the serial port; upload.

## PlatformIO Setup
```ini
; platformio.ini
[env:m5stickc-plus]
platform = espressif32
board = m5stick-c            ; closest official board id; works for PLUS
framework = arduino
monitor_speed = 115200
upload_speed = 1500000
lib_deps =
    m5stack/M5Unified
    crankyoldgit/IRremoteESP8266   ; only if sending/receiving IR
```
For **PLUS2** there may be no dedicated PlatformIO board id yet — use `board = m5stick-c` with
`board_build.flash_size = 8MB` and rely on M5Unified for runtime detection, or target the generic
`esp32-pico-devkitm-2`. Verify the flashed device runs; adjust `upload_speed` down if it fails.

## USB Drivers & Upload
- Use a **data** USB-C cable (charge-only cables give no serial port).
- If no port appears, install the USB-serial driver: **CH9102** (PLUS2) or **CP210x/FTDI** depending
  on the unit. macOS may need the driver allowed in System Settings → Privacy & Security.
- Upload baud options: `1500000 / 750000 / 500000 / 250000 / 115200`. Start high; if "Failed to
  connect"/timeout, drop to 115200. Hold no special boot keys — the auto-reset circuit handles it.

## Library Choice
**M5Unified** wraps display (M5GFX), IMU, buttons, speaker, mic, RTC, power, and touch behind one
API and detects the board at runtime — the same binary logic runs on PLUS and PLUS2. Use it unless
you have a specific reason not to.

## Minimal Sketch
```cpp
#include <M5Unified.h>

void setup() {
  auto cfg = M5.config();
  M5.begin(cfg);
  M5.Display.setRotation(3);
  M5.Display.setTextSize(2);
  M5.Display.fillScreen(BLACK);
  M5.Display.println("Hello M5!");
}

void loop() {
  M5.update();
  if (M5.BtnA.wasPressed()) { M5.Speaker.tone(4000, 80); M5.Display.println("A"); }
}
```

## Peripheral Recipes

**Display (M5GFX)** — same API as LovyanGFX/TFT_eSPI:
```cpp
M5.Display.setBrightness(120);          // 0-255 (portable; no AXP192 calls)
M5.Display.fillRect(0,0,135,30, RED);
M5.Display.setTextColor(WHITE);
M5.Display.drawString("Hi", 10, 40);
M5.Display.drawCircle(67,120,20, GREEN);
```

**IMU (MPU6886)** — accel (g) + gyro (deg/s):
```cpp
M5.Imu.update();
auto d = M5.Imu.getImuData();
float ax=d.accel.x, ay=d.accel.y, az=d.accel.z;
float gx=d.gyro.x,  gy=d.gyro.y,  gz=d.gyro.z;
// tilt angle example: atan2(ay, az) * 180/PI
```

**Buttons:**
```cpp
M5.update();
if (M5.BtnA.wasPressed())  {}        // single press
if (M5.BtnA.pressedFor(800)) {}      // long press (ms)
if (M5.BtnB.isPressed())   {}        // held now
```

**Buzzer (passive piezo):**
```cpp
M5.Speaker.tone(2000, 200);          // 2 kHz for 200 ms
M5.Speaker.tone(440);                // start tone; M5.Speaker.stop();
```

**IR transmit** (LED G9 PLUS / G19 PLUS2) with IRremoteESP8266:
```cpp
#include <IRremoteESP8266.h>
#include <IRsend.h>
IRsend irsend(9);                    // use 19 on PLUS2
void setup(){ irsend.begin(); }
void loop(){ irsend.sendNEC(0x20DF10EF, 32); delay(2000); } // example TV power
```

**RTC (BM8563):**
```cpp
auto t = M5.Rtc.getDateTime();       // t.date.year, t.time.hours ...
M5.Rtc.setDateTime({{2026,6,7},{14,30,0}});
```

**Microphone (PDM):**
```cpp
M5.Mic.begin();
int16_t buf[256];
M5.Mic.record(buf, 256, 16000);      // 16 kHz; compute RMS for a sound meter
```

**Wi-Fi / BLE** — stock ESP32:
```cpp
#include <WiFi.h>
WiFi.begin("ssid","pass");
while (WiFi.status()!=WL_CONNECTED) delay(200);
// BLE: #include <BLEDevice.h>  (NimBLE-Arduino is lighter if flash is tight)
```

**Power & deep sleep:**
```cpp
int pct = M5.Power.getBatteryLevel();
M5.Power.powerOff();                  // true off where supported
// timed deep sleep:
esp_sleep_enable_timer_wakeup(60ULL*1000000); // 60 s
esp_deep_sleep_start();
```
On **PLUS2**, M5Unified keeps the GPIO4 HOLD pin high; if you write bare ESP-IDF, set it yourself or
the board powers down off-USB.
