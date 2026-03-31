# TA1910-4GVC-W Troubleshooting Reference

## Quick LED Diagnostic

| PON | LOS | Action |
|---|---|---|
| Green solid | Off | Healthy — check WAN/LAN config if no internet |
| Blinking | Off | Registering — wait 3 min; if persists, bind SN on OLT |
| Off | Off | No fiber signal or ONU not bound on OLT |
| Off/blink | Red | Fiber signal problem — clean connector, check splice |

---

## No Power / Unit Won't Boot

1. Verify power adapter is plugged in at both wall and ONU DC IN port
2. Check wall outlet is live
3. Test with a known-good 12V/1.5A adapter
4. If PWR LED stays off with confirmed good power: hardware failure — replace unit

---

## PON LED Won't Go Solid (ONU Not Registering)

**Symptom:** PWR green, PON blinking or off after 3+ minutes

**Step 1 — Check OLT binding:**
```bash
# On OLT3610 — look for this ONU in discovery list
Switch# show gpon onu
```
If ONU SN appears as "unbound" or "auto-discovered", bind it:
```bash
Switch_config# interface gpon 0/<port>
Switch_config_gpon0/X# gpon bind-onu sn <SN>
Switch_config_gpon0/X# exit
Switch_config# wr all
```

**Step 2 — Check LOS LED:**
- LOS red: fiber signal loss → clean the SC/APC connector at both ONU and wall outlet
- Clean procedure: use dust cap blow-out, then IEC 61300-3-35 compliant cleaner pen

**Step 3 — Check fiber path:**
- Confirm correct SC/APC (green) connectors — do NOT mix with SC/UPC (blue)
- Check for tight bends in fiber drop cable (bend radius > 30mm)
- Verify splitter port is connected; count splitter legs if shared

**Step 4 — Check optical power on OLT:**
```bash
Switch# show gpon onu optical-info <ONU-ID>
```
- Acceptable Rx power: −8 to −28 dBm (GPON class B+)
- Below −28 dBm: signal too weak → check connectors, splice loss, fiber length
- Above −8 dBm: signal too strong (unlikely with splitter, but check for direct connection)

---

## No Internet After PON Registered

**Symptom:** PON LED solid green, but cabin devices have no internet

1. **Check WAN status:** ONU web UI → Status → WAN — is WAN connection "Connected"?
2. **Check WAN VLAN:** WAN → WAN Connection → confirm VLAN ID matches OLT service VLAN
3. **Check WAN mode:** Routing mode should be enabled with NAT on
4. **Check DHCP on WAN:** If mode is DHCP, confirm ONU got an IP on WAN interface (shown in Status)
5. **Check PPPoE credentials:** If WAN type is PPPoE, verify username/password are correct
6. **Test from ONU itself:** Some models have a ping test — Service → Diagnostics → Ping 8.8.8.8
7. **Verify on OLT:** Check that the ONU service-port VLAN mapping is correct:
   ```bash
   Switch# show gpon onu service-port <ONU-ID>
   ```

---

## Cabin Devices Not Getting DHCP / Wrong IP Range

**Symptom:** Device connected to LAN port shows 169.254.x.x (APIPA) or wrong subnet

1. ONU web UI → LAN → confirm DHCP server is **Enabled**
2. Check DHCP pool range is not exhausted: Status → LAN → DHCP Client List
3. Try releasing/renewing IP on client device
4. If device shows 192.168.123.x but no internet: WAN issue (see above)
5. Check LAN port cable and link LED on ONU

---

## WiFi Issues

### Clients Can't Find SSID
1. ONU web UI → WLAN → 2.4G / 5G → confirm **Enable** is checked
2. Confirm **Broadcast SSID** is enabled (not hidden)
3. Reboot ONU if radio was recently toggled

### Clients Connect but No Internet
- WiFi association is working but WAN is down — see "No Internet After PON Registered"

### WiFi Signal Weak Inside Cabin
1. Reposition ONU closer to center of cabin — antennas should be vertical
2. Move ONU off the floor and out of enclosed cabinets
3. Check antennas are screwed on finger-tight (hand-tight; not loose)
4. 5 GHz has shorter range than 2.4 GHz — if far end of cabin is weak, clients will use 2.4G automatically

### WiFi Password Not Working
1. Confirm WPA2-PSK (AES) is set — not WEP or TKIP
2. Verify password in WLAN settings (passwords are case-sensitive)
3. Have client "forget" the network and reconnect from scratch

---

## Web UI Not Accessible

**Symptom:** Can't reach `http://192.168.123.1`

1. Confirm laptop is plugged into LAN1–LAN4 (not the PON port)
2. Verify laptop obtained a 192.168.123.x IP via DHCP; if not, set static 192.168.123.100/24
3. Try `http://` not `https://` — ONU web UI is HTTP only by default
4. Try a different browser or clear browser cache
5. Check if ONU is in bridge mode (bridge mode disables ONU's DHCP/web UI from LAN side) — if so, connect via the management VLAN or reconfigure from OLT via OMCI/TR-069

---

## Admin Password Lost / Locked Out

1. **Factory reset** (only option): hold RESET button 10 seconds — all config erased
2. ONU returns to `admin` / `super&123` and `192.168.123.1`
3. Re-provision from scratch using the cabin provisioning checklist

---

## Factory Reset

**Hardware method:**
1. While ONU is powered on, hold the recessed RESET button for **10 seconds**
2. All LEDs will cycle; ONU reboots with factory defaults
3. PON LED will re-register (solid green) if SN was already bound on OLT — no OLT changes needed

**Web UI method:**
Advanced → Factory Reset → Confirm

> After reset, re-run the full cabin provisioning checklist to restore SSID, password, WAN VLAN, and other settings.

---

## ONU Shows "Online" on OLT but Service Is Down

1. Check OMCI service-port mapping on OLT:
   ```bash
   Switch# show gpon onu service-port <ONU-ID>
   ```
2. Verify VLAN tagging on OLT service-port matches ONU WAN VLAN config
3. Check upstream bandwidth profile — ONU may be online but rate-limited to 0
4. Re-push OMCI config from OLT:
   ```bash
   Switch_config_gpon0/X# onu <ONU-ID> reset
   ```
   (This resets OMCI state — ONU re-registers and receives fresh config push)

---

## Firmware Upgrade Fails / ONU Stuck in Upgrade

1. Do NOT cut power during firmware upgrade — PWR LED blinks during process
2. Wait up to 10 minutes; ONU reboots automatically when complete
3. If stuck > 15 minutes: power cycle ONU — it will boot into recovery firmware
4. Verify firmware file matches exact model: TA1910-4GVC-W (not TA1910-4GVC or similar variants)
5. If ONU won't boot after bad flash: contact FS support for TFTP recovery procedure

---

## VoIP / POTS Not Working

1. VoIP → SIP settings: verify SIP server IP, port (5060), username, password
2. Verify WAN is connected and SIP traffic is not blocked by firewall
3. If VoIP traffic is on a separate VLAN: ensure VoIP WAN service-port is configured on OLT with the correct VLAN
4. Test: pick up handset connected to TEL1 — dial tone = SIP registered; silence = SIP registration failed
5. Check SIP registration status: VoIP → Status → Registration Status

---

## FS Support & Resources

- Product page: https://www.fs.com/products/143750.html
- FS support portal: https://www.fs.com/products_support.html
- ONU onboarding guide: https://www.fs.com/blog/guide-to-easily-onboarding-configuring-onu-case-of-fs-oltonu-4517.html
- ManualsLib quick start: https://www.manualslib.com/manual/2831861/Fs-Ta1910-4gvc-W.html
