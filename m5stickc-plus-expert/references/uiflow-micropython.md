# M5StickC PLUS / PLUS2 — UIFlow2 & MicroPython

The no-C++ paths: **UIFlow2** (drag-and-drop blockly that compiles to MicroPython) and writing
**MicroPython** directly. Both run on M5Stack's UIFlow firmware. Load when the user wants visual
programming or Python instead of Arduino.

## Contents
- Flashing UIFlow firmware (M5Burner)
- UIFlow2 workflow
- MicroPython basics (the `M5` module)
- Example: display + button + IMU
- When to use which path

## Flashing UIFlow Firmware (M5Burner)
1. Download **M5Burner** (M5Stack's flasher) for your OS.
2. Connect the StickC over USB; install the USB-serial driver if no port shows (CH9102 on PLUS2).
3. In M5Burner, pick the **UIFlow2** firmware for **StickC PLUS** or **StickC PLUS2**, click **Burn**.
4. On first boot, configure Wi-Fi (or set USB mode). The screen shows an **API key** / device ID used
   to pair with the cloud IDE.

## UIFlow2 Workflow
- Open the web IDE at **flow.m5stack.com** (UIFlow2). Choose **M5StickC PLUS/PLUS2** as the device.
- Connect by **API key** (Wi-Fi/cloud) or **USB** (local).
- Drag blocks: UI widgets (label/image/rect), Hardware (IMU, buttons, IR, speaker, RTC, mic), Units
  (Grove modules), and logic/loops. The right panel shows the **generated MicroPython** live — a good
  way to learn the API, then graduate to writing Python directly.
- Run on-device or download the `.py`.

## MicroPython Basics (the `M5` module)
UIFlow firmware exposes an `M5` module plus hardware sub-modules. Skeleton:
```python
import M5
from M5 import Lcd, Widgets, Imu, BtnA, Speaker

M5.begin()
Lcd.setRotation(3)
Widgets.fillScreen(0x000000)
label = Widgets.Label("Hello", 10, 20, 1.0, 0xFFFFFF, 0x000000, Widgets.FONTS.DejaVu24)

while True:
    M5.update()                 # refresh buttons/sensors
    if BtnA.wasPressed():
        Speaker.tone(4000, 100)
    ax, ay, az = Imu.getAccel() # tuple of g values
    label.setText("ax=%.2f" % ax)
```
- Buttons: `BtnA.wasPressed()`, `BtnA.isPressed()`.
- IMU: `Imu.getAccel()`, `Imu.getGyro()`.
- Display: `Widgets.Label/Rectangle/Image`, `Lcd.print/clear/setBrightness`.
- Speaker: `Speaker.tone(freq, ms)`. IR/RTC/Mic have matching modules.
- Grove **Units** import from the `unit`/`hat` packages, e.g. `from unit import ENVUnit`.

Plain **MicroPython/esptool** (without UIFlow) also works, but UIFlow firmware is the smoothest Python
experience and ships the M5 drivers.

## When to Use Which Path
- **UIFlow2 (blocks):** fastest for beginners, demos, classroom, quick Unit wiring; live-preview the
  generated Python.
- **MicroPython:** more control than blocks, still no compile step; good for logic-heavy scripts.
- **Arduino/PlatformIO (see `arduino.md`):** best performance, smallest/most-controlled binaries,
  BLE/IR libraries, deep sleep, and production firmware. Choose this for anything battery- or
  timing-critical.
