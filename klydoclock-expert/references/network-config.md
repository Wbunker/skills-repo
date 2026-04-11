# Klydoclock — Network Configuration

## The Core Problem

Klydoclock **only supports 2.4 GHz WiFi**. It cannot see or connect to 5 GHz networks.

Most modern mesh routers — including Netgear Orbi — use **band steering**: they broadcast a single SSID name and automatically route devices to 2.4 GHz or 5 GHz depending on signal strength. Klydoclock gets confused by this and fails to connect, because it cannot distinguish which band it's on during the handshake.

**Solution:** Create a separate, dedicated 2.4 GHz-only SSID and connect Klydoclock to that.

---

## Orbi-Specific Solutions

Orbi officially states it does not support splitting bands into two separate SSIDs through the normal UI. However, these workarounds reliably create a separate 2.4 GHz network.

---

### Option 1: IoT Band (Orbi WiFi 6 / WiFi 6E — easiest)

If your Orbi system is **WiFi 6 or WiFi 6E** (RBK860S, RBK863S, RBKE963, or similar):

1. Log in to the Orbi admin UI: `http://orbilogin.com` or `http://192.168.1.1`
2. Go to **Wireless** → **IoT Settings** (or **Wireless IoT**)
3. Enable **IoT Network**
4. Set the band to **2.4 GHz only**
5. Give it a distinct SSID name (e.g., `Orbi-IoT`)
6. Set a password
7. Save and wait ~30 seconds for the network to broadcast
8. Connect Klydoclock to this new IoT SSID

This is the cleanest solution — it requires no command-line access and doesn't change your main network.

---

### Option 2: Telnet / debug.htm (all Orbi models — permanent)

This creates a permanently separate 2.4 GHz SSID by modifying Orbi's internal configuration. Requires comfort with command-line tools.

**Step 1 — Enable Telnet via debug page**

1. Log into Orbi admin UI
2. In the browser address bar, change the URL to: `http://orbilogin.com/debug.htm`
3. Check the box labeled **Enable Telnet**
4. Click **Apply**

**Step 2 — Connect via Telnet**

```bash
telnet 192.168.1.1
# Login with your Orbi admin username and password
```

**Step 3 — Rename the 2.4 GHz SSID**

```bash
# View current SSIDs
config get wl_ssid      # 2.4 GHz name
config get wla_ssid     # 5 GHz name

# Give the 2.4 GHz network a different name
config set wl_ssid="MyHome-2.4G"
config commit
```

**Step 4 — Disable WiFi Son (band-steering) on firmware 2.5+**

```bash
config set wifison-monitor_stop=1
config commit
```

**Step 5 — Reboot**

```bash
reboot
```

After reboot, two separate SSIDs will appear: one for 2.4 GHz (`MyHome-2.4G`) and your original SSID for 5 GHz. Connect Klydoclock to the 2.4 GHz one.

> **Note:** Orbi firmware updates can revert these changes. If WiFi stops working on the Klydoclock after an Orbi update, re-run these steps.

---

### Option 3: Reduce 5 GHz Power (temporary workaround)

This forces the clock to connect on 2.4 GHz during initial setup by making 5 GHz nearly invisible. It's a workaround for setup only — the networks remain merged after setup.

1. Log into Orbi admin
2. Go to **Wireless Settings** → **Transmit Power Control**
3. Set **5 GHz transmit power to 25%**
4. Move the Klydoclock **far from the router** (another room if possible)
5. Power cycle the Klydoclock
6. Complete WiFi setup — it should connect on 2.4 GHz due to weak 5 GHz signal
7. After setup succeeds, you can restore the 5 GHz power to 100%

> **Caveat:** The merged SSID may continue to cause problems over time as band steering re-routes the device. Option 1 or 2 is more reliable long-term.

---

### Option 4: WiFi Extender (no router changes required)

If you'd rather not modify the Orbi configuration at all:

1. Add any WiFi range extender (Netgear, TP-Link, etc.) to your network
2. Configure the extender to broadcast a **2.4 GHz-only SSID** (most extenders allow this)
3. Connect Klydoclock to the extender's 2.4 GHz SSID
4. Place the extender within range of the clock's install location

---

## Other Mesh / Router Systems

### Google Nest / Google WiFi

Google Home app does not expose separate band controls for the main SSID. Options:

- Enable **Guest Network** and set it to 2.4 GHz only in the Google Home app → **Settings → Network → Guest**
- Or use a separate 2.4 GHz extender (Option 4 above)

### Eero

Eero also uses band steering with no UI to split bands. Use:
- A dedicated IoT network via the Eero app (Settings → Network → Add network → IoT)
- Or an extender

### TP-Link Deco

Deco supports splitting bands in the Deco app:
- Open Deco app → **More** → **Advanced** → **Wireless**
- Disable **Smart Connect** to expose separate 2.4 GHz and 5 GHz SSIDs
- Connect Klydoclock to the 2.4 GHz SSID

### Standard (non-mesh) Routers

Most traditional routers (ASUS, TP-Link Archer, Netgear Nighthawk) already broadcast separate 2.4 GHz and 5 GHz SSIDs by default — look for two network names, often `NetworkName` and `NetworkName_5G`. Connect Klydoclock to the one **without** the `_5G` suffix.

---

## After Connecting to a New Network

If you need to switch the Klydoclock to a different WiFi network (e.g., after reconfiguring your router):

1. Press **☰ (Menu)** on the remote
2. Navigate to **Settings** → **Wi-Fi** → **Change Wi-Fi Network**
3. Select the new 2.4 GHz SSID from the list
4. Enter the password using the remote scroll wheel
5. The clock reconnects within ~30 seconds

---

## Technical WiFi Specs (from FCC filing)

- Protocol: 802.11 b/g/n (2.4 GHz only)
- Max output power: 14.41 EIRP dBm
- Bluetooth (remote): BLE 9.61 EIRP dBm, EDR 7.78 EIRP dBm
