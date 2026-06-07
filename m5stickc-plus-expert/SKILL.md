---
name: m5stickc-plus-expert
description: >
  Expert for programming and using the M5Stack M5StickC PLUS and M5StickC PLUS2 — the stick-shaped
  ESP32-PICO mini IoT dev kit with a 1.14" TFT, 6-axis IMU (MPU6886), IR transmitter, microphone,
  RTC, buzzer, buttons, and Grove port. Use when the user wants to: program/flash the StickC PLUS or
  PLUS2 (Arduino IDE, PlatformIO, UIFlow2, or MicroPython); find a GPIO/pinout or peripheral address;
  read the IMU/buttons/mic, drive the display, send IR, play tones, use the RTC, or read battery/power;
  connect HATs or Grove Units; get the PLUS-vs-PLUS2 differences (AXP192 vs GPIO4 HOLD pin, pin
  remaps); wear it as a watch; or pick and build a project. Triggers: "M5StickC", "StickC Plus",
  "M5StickC PLUS2", "M5Stack stick", "ESP32-PICO", "M5Unified", "UIFlow", "MPU6886", "flash my stick",
  "stick pinout", "IR remote with the stick", "M5 watch".
tools: Read
---

# M5StickC PLUS / PLUS2 Expert

The **M5StickC PLUS** and **M5StickC PLUS2** are pocket ESP32 dev kits in a ~48×24×14 mm stick.
Onboard: 1.14" 135×240 TFT (ST7789v2), 6-axis IMU (MPU6886), IR LED, PDM mic (SPM1423), RTC
(BM8563), passive buzzer, 2 buttons + power/wake, red LED, USB-C, and a Grove (I2C/UART/GPIO) port.
They stack **HATs** (top header) and chain **Grove Units**, and can be worn as a watch with the Watch HAT.

> **Know which variant you have — it changes the pins and power code.** PLUS uses an **AXP192 PMU**;
> PLUS2 **removes it** and uses a **GPIO4 HOLD pin** you must drive HIGH to stay powered. Several
> GPIOs differ. See `references/hardware.md` before wiring or porting code.

## How to Use This Skill

Progressive disclosure — load only what the task needs:

| Task | Load |
|---|---|
| Pinout / GPIO map, peripheral I2C addresses, specs, PLUS-vs-PLUS2 differences, HATs & Grove Units, power/battery, wearing it as a watch | `references/hardware.md` |
| Program in C++ (Arduino IDE or PlatformIO): M5Unified API, display/IMU/buttons/buzzer/IR/RTC/mic/WiFi/power, example sketches, upload settings, USB drivers | `references/arduino.md` |
| Program visually or in Python: UIFlow2 blockly, MicroPython, flashing firmware with M5Burner | `references/uiflow-micropython.md` |
| Project ideas with build notes (IR universal remote, gesture wand, Wi-Fi sensor dashboard, BLE HID, clock/timer, sound meter, games, Claude Desktop Buddy, …) | `references/projects.md` |

## Quick Start (Arduino + M5Unified — works on both variants)

`M5Unified` auto-detects the board, so it's the recommended library for new projects (handles the
PLUS/PLUS2 differences for you). Install **M5Unified** (pulls in **M5GFX**) via Library Manager,
select board **"M5StickC Plus"** or **"M5StickC Plus2"**, and upload.

```cpp
#include <M5Unified.h>

void setup() {
  auto cfg = M5.config();
  M5.begin(cfg);                 // inits display, IMU, buttons, power, etc.
  M5.Display.setRotation(3);     // landscape
  M5.Display.setTextSize(2);
  M5.Display.println("Hello M5!");
}

void loop() {
  M5.update();                   // refresh buttons / sensors every loop
  if (M5.BtnA.wasPressed()) {    // BtnA = big front button (G37)
    M5.Speaker.tone(4000, 100);  // passive buzzer
    M5.Display.println("A!");
  }
}
```

Upload baud: try **1500000**; drop to **115200** if uploads fail. Details + PlatformIO config: `references/arduino.md`.

## API Cheat Sheet (M5Unified)

| Need | Call |
|---|---|
| Init / per-loop refresh | `M5.begin(M5.config())` · `M5.update()` |
| Screen (M5GFX) | `M5.Display.print/fillScreen/drawString/setRotation/setBrightness` |
| Buttons | `M5.BtnA` / `M5.BtnB` → `.wasPressed() .isPressed() .wasReleased()` |
| IMU (MPU6886) | `M5.Imu.update()` then `M5.Imu.getImuData()` → `.accel.x .gyro.y` |
| Buzzer | `M5.Speaker.tone(freqHz, ms)` |
| Battery / power | `M5.Power.getBatteryLevel()` · `M5.Power.powerOff()` |
| RTC (BM8563) | `M5.Rtc.getDateTime()` / `setDateTime()` |
| Mic (PDM) | `M5.Mic.begin()` · `M5.Mic.record(buf, len, rate)` |

IR send needs `IRremoteESP8266` (IR LED on **G9** PLUS / **G19** PLUS2). Wi-Fi/BLE use the stock ESP32 `WiFi.h` / `BLEDevice.h`.

## Gotchas

- **PLUS2 powers off if GPIO4 (HOLD) goes LOW.** On PLUS2, set the hold pin HIGH early (M5Unified does this in `M5.begin`); custom/bare code that doesn't will shut off the moment USB is unplugged.
- **No AXP192 on PLUS2.** Code that calls AXP192 (screen brightness, battery voltage, power off) from the old `M5StickCPlus` library won't work on PLUS2 — use `M5Unified` (`M5.Power`, `M5.Display.setBrightness`) for portability.
- **Pin remaps between variants:** IR/LED, DC, RST, battery-sense, and the wake button all moved. Never reuse raw GPIO numbers across PLUS and PLUS2 — check `references/hardware.md`.
- **Buttons:** BtnA = front "M5" button (G37), BtnB = side button (G39). The power button is separate (PLUS: via AXP192; PLUS2: 6 s press / G35 wake).
- **The buzzer is passive** — you must drive a frequency (`tone`), not just set a pin HIGH.
- **No serial port?** Install the USB-serial driver (PLUS2 = CH9102; some sticks = CP210x/FTDI) and use a *data* USB-C cable, not charge-only.
- **Library choice:** prefer **M5Unified + M5GFX**. The legacy `M5StickCPlus` / `M5StickCPlus2` libraries are device-specific and don't port between variants.
- **Pin G0 / G36 / G25-26** are exposed but shared (G0 = mic clock / boot strap; G36/G25/G26 on the header) — mind conflicts when adding HATs.

## Related

- To build the BLE **Claude Desktop Buddy** desk pet on this hardware, use the existing
  `claude-desktop-buddy` skill (it covers the firmware + Nordic-UART protocol). This skill covers the
  device generally; that one covers that specific project.
