# Klydoclock — First-Time Setup

## What's in the Box

- Klydoclock device
- Bluetooth remote control
- 12V/2A USB-C power adapter (supports 110V and 220V)
- 2-meter USB-C cable
- Guidebook

## Before You Start — Network Requirement

**Klydoclock only connects to 2.4 GHz WiFi.** If your router broadcasts a combined 2.4/5 GHz SSID (as most Orbi and mesh systems do by default), the clock will fail to connect. Resolve this before starting setup.

→ See [network-config.md](network-config.md) for how to create a 2.4 GHz-only SSID on Orbi and other routers.

## Step-by-Step Setup

### 1. Charge the Remote

Charge the remote via USB-C (5V–12V) before doing anything else:
- LED flashes **red** while charging
- LED turns **solid blue** when fully charged and ready to pair

### 2. Place and Power On

- Set the clock on a shelf, desk, mantle, or credenza
- Plug the USB-C power adapter into the port on the back of the Klydoclock
- The device powers on automatically — displays boot animation

### 3. Pair the Remote

- Press and hold the **knob on the back** of the remote for 3 seconds
- When the remote LED turns solid blue, pairing is complete
- The remote works via Bluetooth — it does not need line-of-sight

### 4. Connect to WiFi

1. Press **☰ (Menu)** on the remote
2. Navigate to **Wi-Fi** / **Network Setup**
3. A list of available networks appears on screen
4. Select your **2.4 GHz network** (must be a 2.4 GHz-only SSID — see network-config.md)
5. Enter your WiFi password using the remote's scroll wheel:
   - Navigate left/right through characters using the arrow buttons
   - Confirm each character with the center button
   - This is slow — be patient with long passwords
6. The clock connects and downloads its initial content and firmware

### 5. Time Zone

- Time is set automatically via NTP (internet time sync) — no manual timezone input is needed in most cases
- If the time is wrong, it can be manually corrected using the back knob on the remote (rotate to adjust)

### 6. Verify

- Animated Klydo artwork should appear within a minute of connecting
- Clock hands should show the correct local time
- The device is ready to use

## What Requires Internet

| Feature | Needs Internet? |
|---------|----------------|
| First boot / initial setup | **Yes — required** |
| Showing correct time (NTP) | Yes (or set manually) |
| Receiving new Klydos daily | Yes |
| Firmware / ClockOS updates | Yes |
| Displaying already-downloaded Klydos | No |
| Keeping time after first sync | No |

## ClockOS (Firmware)

The operating system is called **ClockOS**. Version history: https://www.klydoclock.com/pages/clockosversion

Updates install automatically when connected to WiFi. Notable recent update: ClockOS 358 added a digital time indicator option and time-setting menu improvements.
