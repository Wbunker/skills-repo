# Klydoclock — Remote Control and Settings

## Remote Overview

The Klydoclock remote is a Bluetooth device. It must be charged before first use and paired to the clock.

**Charging**: USB-C port on the remote (5V–12V). Red LED = charging, solid blue = full / ready.

**Pairing**: Hold the back knob for 3 seconds until the LED turns solid blue.

**Range**: Bluetooth — works through walls, no line-of-sight required.

---

## Button Reference

| Button / Control | Action |
|-----------------|--------|
| **☰ (Menu)** | Open / close the main menu |
| **← (Left arrow)** | Previous Klydo |
| **→ (Right arrow)** | Next Klydo |
| **Center / SELECT / ♥** | Toggle favorite on the current Klydo (heart icon appears on screen) |
| **Back knob (rotate)** | Scrub frame-by-frame through the current animation |
| **Back knob (press)** | Snap clock hands to current correct time |
| **Back knob (hold 3s)** | Pair remote to clock |

---

## Main Menu Structure

Access with **☰**. Navigate with **← →** arrows. Select with the center button.

```
Menu
├── Browse
│   ├── All Klydos          — full library
│   ├── Favorites           — your hearted Klydos
│   └── Collections         — themed groups curated by Klydo
├── Settings
│   ├── Wi-Fi               — change network, view connection status
│   ├── Display
│   │   ├── Cycle Frequency — how often animation changes
│   │   └── Digital Clock   — show/hide digital time overlay (ClockOS 358+)
│   ├── Time                — manual time adjustment
│   └── About               — firmware version, device info
└── Sleep / Wake            — dim or wake the display
```

---

## Changing Display Settings

### Animation Cycle Frequency

Controls how often the Klydo animation automatically changes:

1. **☰** → Settings → Display → Cycle Frequency
2. Choose: **1 min / 5 min / 15 min / 60 min / 6 hours / 24 hours / Fixed**
3. "Fixed" = manual only (only changes when you press ← →)

### Digital Clock Overlay

Added in ClockOS 358. Shows the current time in digital numerals alongside the analog hands.

1. **☰** → Settings → Display → Digital Clock
2. Toggle on/off

### Manual Time Adjustment

If time is wrong (e.g., offline or NTP failed):

1. **☰** → Settings → Time
2. Use ← → to adjust hours/minutes
3. Confirm with center button

Or: press the back knob on the remote to snap the hands to the current NTP time instantly (requires internet).

---

## Changing WiFi Network

1. **☰** → Settings → Wi-Fi → Change Wi-Fi Network
2. Select your 2.4 GHz SSID from the list
3. Enter password using the scroll wheel:
   - ← → to move through the character list (a–z, A–Z, 0–9, symbols)
   - Center to confirm each character
   - Backspace character is at the end of the list
4. Select the checkmark / confirm when the full password is entered
5. Clock reconnects; success confirmation appears on screen

> **Tip for long passwords**: Write out the password before starting. Scroll-wheel entry is slow; mistakes require backspacing one character at a time.

---

## Managing Favorites

- While a Klydo is displayed, press the **center / ♥ button** to heart it
- A heart icon appears briefly on the display confirming the save
- Press again to remove from favorites
- Browse all favorites: **☰** → Browse → Favorites

---

## Sleep and Wake

The display can be dimmed or turned off:

- Press **☰** and navigate to **Sleep** to dim the display
- Press any remote button or the menu button to wake it

Auto-sleep settings (if available in your ClockOS version) can be configured in **Settings → Display**.

---

## Remote Pairing (re-pairing after battery swap or reset)

1. Make sure the clock is powered on and showing a display
2. Hold the **back knob** on the remote for **3 seconds**
3. Remote LED turns solid blue = paired and ready
4. Test with **← →** to confirm Klydo navigation works
