# Alternative Hardware Builds

Five project ideas beyond the reference desk pet. All use the same BLE NUS protocol.

---

## 1. Approval Traffic Light

**What:** Three LEDs on top of your monitor. Green = idle, yellow = busy, red = waiting for approval. Tap a button to approve.

**BOM:** ~$8 — any microcontroller with BLE + 3 LEDs + 1 button

**Core logic:**
```
on heartbeat:
  if waiting > 0:  light red, listen for button press
  elif running > 0: light yellow
  else:             light green

on button press (when red):
  send {"cmd":"permission","id": last_prompt_id,"decision":"once"}
```

Only one message type received (heartbeat), one sent (permission). Minimal firmware — suitable for a bare nRF52 or ESP32-C3.

---

## 2. Token Burn Meter

**What:** An analog servo gauge showing `tokens_today` against a daily budget. Like a speedometer on your desk.

**Hardware:** Any BLE MCU + hobby servo motor + printed dial face. Mount next to monitor.

**Core logic:**
```
daily_budget = 100000   # configure to taste
on heartbeat:
  angle = map(tokens_today, 0, daily_budget, 0, 180)
  set_servo(angle)
  if tokens_today > daily_budget * 0.8:
    blink_warning_LED()
```

Update every 10s (on heartbeat). Print a dial face with a red zone above your threshold. Satisfying for Max subscribers watching rate limits. `tokens_today` persists across app restarts and resets at local midnight.

---

## 3. Session Ambient Display

**What:** An e-ink display (always on, no backlight) showing the last few transcript `entries[]` from the heartbeat. Set it next to your keyboard.

**Hardware:** Waveshare 2.13" e-ink + any BLE MCU (ESP32 or nRF52 with SPI)

**Core logic:**
```
last_entries = []
on heartbeat:
  if entries != last_entries:
    render last 5-6 lines of entries[] on e-ink
    last_entries = entries
```

Only refresh on content change — e-ink is slow (~2s partial refresh) and draws power only during refresh, so battery lasts weeks. Diff `entries` before refreshing to avoid flicker. Render newest entry at top.

**Why e-ink:** Low power, always readable in sunlight, no backlight fatigue. Gives passive ambient awareness without switching windows.

---

## 4. CI/CD Approval Puck

**What:** A single large button in a 3D-printed enclosure. Lights up when Claude needs approval. Smack it to approve.

**Hardware:** ESP32 or nRF52 + 1 large momentary button + 1 NeoPixel ring

**Core logic:**
```
on heartbeat:
  if waiting > 0:
    set_neopixel(RED, pulsing)
    store last_prompt_id
  else:
    set_neopixel(GREEN, slow_pulse)

on button press:
  if last_prompt_id:
    send {"cmd":"permission","id":last_prompt_id,"decision":"once"}
    last_prompt_id = null
    set_neopixel(GREEN, flash_celebrate)
```

Simplest possible Buddy implementation. One NeoPixel ring, one button, one message type. Good for engineers who find the desk pet too whimsical.

---

## 5. Wearable Notification Band

**What:** An nRF52 wristband that vibrates when Claude needs approval. Tap the band to approve from anywhere — kitchen, meeting room, garden.

**Hardware:** nRF52840 dev board or reflashed fitness tracker + vibration motor

**BLE range:** ~30m indoors on nRF52840

**Core logic:**
```
on heartbeat:
  if waiting > 0 and not already_vibrating:
    vibrate(pattern=[200ms, 100ms, 200ms])  # two short pulses = "needs approval"
    store last_prompt_id
  if running == 0 and total == 0:
    vibrate(pattern=[500ms])                # one long = "session complete"

on tap gesture (accelerometer):
  if last_prompt_id:
    send {"cmd":"permission","id":last_prompt_id,"decision":"once"}
```

No screen required — vibration patterns carry all needed information. Use a single LED for confirmation feedback. The band doesn't render transcript or token data; it only reacts to `waiting > 0`.

**nRF52 notes:** Use the Nordic NUS GATT service (same UUIDs as ESP32 implementation). Zephyr RTOS or Arduino framework both work. The nRF52840 supports LE Secure Connections natively — enable bonding for encrypted transport.
