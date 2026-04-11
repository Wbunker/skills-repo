# Klydoclock — Troubleshooting

## WiFi / Network Issues

### Clock won't connect to WiFi

**Most likely cause:** Your router is broadcasting a combined 2.4/5 GHz SSID. Klydoclock only supports 2.4 GHz.

→ See [network-config.md](network-config.md) for router-specific solutions.

**Other causes to check:**
- Wrong password (scroll-wheel entry is error-prone — double-check)
- Router is too far away — move clock closer during setup
- Router requires a client certificate or captive portal — Klydoclock cannot authenticate on such networks
- SSID contains unusual characters — try renaming the 2.4 GHz SSID to simple alphanumeric if other fixes fail

**Steps:**
1. Confirm a 2.4 GHz-only SSID is visible on your phone before trying to connect the clock
2. Power cycle the clock (unplug 30 seconds, replug)
3. Press ☰ → Settings → Wi-Fi → Change Wi-Fi Network
4. Select the 2.4 GHz SSID and re-enter the password carefully

### Clock was connected, now it's not

- Check whether your router firmware updated and reset band settings (Orbi is known for this)
- Check whether the 2.4 GHz SSID password changed
- Re-run the WiFi change procedure: ☰ → Settings → Wi-Fi → Change Wi-Fi Network

### Clock shows old content / no new Klydos downloading

- Clock is offline. Verify WiFi connection in Settings → Wi-Fi
- If connected but content isn't updating, power cycle the clock
- Content updates happen automatically in the background when connected — no manual trigger needed

---

## Display Issues

### Screen is black / clock won't turn on

1. Verify the USB-C cable is firmly seated in both the clock and the power adapter
2. Try a different USB-C cable — the included cable occasionally fails
3. Try a different USB-C power source (the clock requires 12V/2A; a laptop charger providing only 5V may not be sufficient)
4. Power cycle: unplug for 30 seconds, replug
5. If still black after 2 minutes, contact Klydo support

### Display is frozen on one animation

1. Power cycle the clock (unplug → wait 30 seconds → replug)
2. If it freezes repeatedly, check for a firmware update when back online (ClockOS updates often fix stability issues)

### Clock hands show wrong time

- If online: press the back knob on the remote to snap hands to NTP time
- If offline: ☰ → Settings → Time → adjust manually
- Verify your timezone if NTP time is consistently offset

### Animation quality looks poor / pixelated

- This is a display hardware issue. Contact support at https://www.klydoclock.com/pages/support

---

## Remote Control Issues

### Remote does nothing

1. Confirm the remote is charged — LED should be solid blue when fully charged and paired
2. Re-pair: hold the back knob for 3 seconds until LED turns solid blue
3. If still unresponsive, check for physical obstruction between remote and clock (Bluetooth, so walls are usually fine — but metal objects close to either device can interfere)
4. Try charging the remote fully from flat — partial charge can cause erratic behavior

### Remote paired but some buttons don't work

- Power cycle the clock
- Re-pair the remote (hold back knob 3 seconds)
- If specific buttons are stuck/broken, contact Klydo support

### Accidentally navigated to a screen you can't exit

- Press ☰ to return to the main menu from any submenu
- If the menu is unresponsive, power cycle the clock and re-pair the remote

---

## Boot / Startup Issues

### Clock keeps rebooting / restarting loop

1. Check power supply — must be 12V/2A; underpowered supply causes boot loops
2. Try the original included power adapter
3. Ensure the USB-C cable is not damaged or intermittently connected
4. If boot loop persists across power adapters and cables, contact support

### Clock boots but displays a black screen with the clock hands visible

- This is normal during initial setup before Klydos are downloaded
- Connect to WiFi (☰ → Wi-Fi setup) — Klydos will download automatically within a few minutes

---

## Firmware / Software Issues

### How to check firmware version

☰ → Settings → About → Firmware / ClockOS Version

Current version history: https://www.klydoclock.com/pages/clockosversion

### How to update

Updates install automatically when the clock is connected to WiFi. There is no manual update trigger. If you need a specific version applied, power cycle the clock while online — it checks for updates on boot.

---

## Support Contact

Official support: https://www.klydoclock.com/pages/support

> **Note:** User reports indicate response times can be slow (days to over a week). When contacting support, include your ClockOS version (from ☰ → Settings → About) and a description of exactly what happens vs. what you expected.
