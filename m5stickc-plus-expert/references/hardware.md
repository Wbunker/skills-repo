# M5StickC PLUS / PLUS2 — Hardware & Pinout

Specs, GPIO maps, peripheral addresses, the critical PLUS-vs-PLUS2 differences, and the HAT/Unit
ecosystem. Load when wiring, porting code between variants, or choosing add-ons.

## Contents
- Specs at a glance (PLUS vs PLUS2)
- The critical power difference
- GPIO map — built-in peripherals
- Display, Grove, and header pins
- Onboard peripherals (addresses)
- Ecosystem: HATs, Units, Watch
- Power & battery

## Specs at a Glance

| | M5StickC PLUS | M5StickC PLUS2 |
|---|---|---|
| SoC | ESP32-PICO-D4, dual-core 240 MHz | ESP32-PICO-V3-02, dual-core 240 MHz |
| Flash / RAM | 4 MB / 520 KB SRAM | 8 MB / 2 MB PSRAM |
| Battery | 120 mAh | 200 mAh |
| Power mgmt | **AXP192 PMU** | **No PMU** — GPIO4 HOLD circuit |
| USB-serial | (data USB-C) | CH9102 |
| Display | 1.14" 135×240 TFT, ST7789v2 | same |
| IMU | MPU6886 (6-axis) | same |
| Other | IR, RTC (BM8563), PDM mic (SPM1423), passive buzzer, red LED, 2 buttons, Grove | same |
| Size | 48 × 24 × 13.5 mm | ~ same |

## The Critical Power Difference

**PLUS (AXP192):** the PMU controls rails, screen backlight brightness, battery voltage/current
reads, and power-off. Old `M5StickCPlus` code talks to AXP192 directly.

**PLUS2 (no AXP192):**
- **GPIO4 = HOLD/power pin.** Must be driven **HIGH after boot** to keep the device on; driving it
  **LOW powers off.** `M5Unified`'s `M5.begin()` handles this — bare-metal code must set it itself.
- **Wake sources:** RTC IRQ, or press the power/Button-C (**G35**) for 2+ s.
- **With USB connected:** a 6 s button press enters sleep instead of full shutdown.
- **Battery voltage:** read via **G38** (ADC), not a PMU register.

> Portable rule: use `M5Unified` (`M5.Power`, `M5.Display.setBrightness`) and never assume AXP192.

## GPIO Map — Built-in Peripherals

| Function | PLUS | PLUS2 |
|---|---|---|
| Button A (front "M5") | G37 | G37 |
| Button B (side) | G39 | G39 |
| Button C / power-wake | via AXP192 | **G35** |
| HOLD (keep power on) | — (AXP192) | **G4** |
| Red LED | G10 | **G19** |
| IR transmitter | G9 | **G19** (shared w/ LED) |
| Passive buzzer | G2 | G2 |
| Mic clock / data | G0 / G34 | G0 / G34 |
| Battery voltage ADC | AXP192 | **G38** |

## Display, Grove, and Header Pins

**TFT (ST7789v2, SPI):**

| Signal | PLUS | PLUS2 |
|---|---|---|
| MOSI | G15 | G15 |
| CLK | G13 | G13 |
| DC | G23 | **G14** |
| RST | G18 | **G12** |
| CS | G5 | G5 |
| Backlight | (AXP192) | **G27** |

**Grove port (HY2.0-4P):** GND (black) · 5V (red) · **G32** (yellow) · **G33** (white) —
usable as I2C (SDA G32 / SCL G33 by convention on Units), UART, or GPIO.

**Top HAT header / external pins:** `G0, G25/G26, G36, G26, G32, G33` exposed (varies slightly by
variant). G0 doubles as the mic clock and a boot strap — avoid driving it at reset.

## Onboard Peripherals (I2C addresses)

Internal I2C bus is **SDA G21 / SCL G22**:
- **MPU6886** IMU @ `0x68` — accel + gyro (no magnetometer; "getImuData" returns accel/gyro).
- **AXP192** PMU @ `0x34` — **PLUS only**.
- **BM8563** RTC @ `0x51`.
- **SPM1423** PDM microphone (not I2C — clock G0, data G34).
- **ST7789v2** display (SPI, pins above).
- IR LED and red LED as noted; buzzer is a passive piezo (needs a driven frequency).

## Ecosystem: HATs, Units, Watch

- **HATs** stack on the 8-pin top header (e.g., ENV HAT, PIR HAT, Joystick HAT, Servo/“8Servos”,
  Speaker HAT, Watch strap, NeoPixel). They use the header GPIOs above.
- **Units** chain off the **Grove** port (I2C/UART/GPIO) — ENV IV (temp/humidity/pressure), PIR,
  ToF distance, RFID, GPS, relay, etc. I2C Units can be daisy-chained.
- **Watch HAT / strap** turns the StickC into a wrist device (RTC + IMU + display = smartwatch/step
  counter). Great for wearable projects.

## Power & Battery

- Charge via **USB-C**. Built-in LiPo is small (120/200 mAh) — expect short untethered runtime;
  use deep sleep for battery projects.
- `M5.Power.getBatteryLevel()` (%) and charging state via M5Unified.
- **Deep sleep:** ESP32 `esp_deep_sleep_start()`; wake on timer or button. On PLUS2 remember the
  GPIO4 HOLD behavior; on PLUS the AXP192 can cut rails for true off.
