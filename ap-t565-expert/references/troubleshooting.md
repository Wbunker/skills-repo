# AP-T565 Troubleshooting Reference

## Quick Diagnostic Checklist

Before deep-diving any issue, check these first:
- [ ] ETH0 LED solid green (link up + PoE)
- [ ] System LED solid green (booted, not in error state)
- [ ] Radio LEDs green (radios active)
- [ ] Can ping AP management IP from controller/laptop
- [ ] AP visible in AC-1004 "Managed APs" list (Fit mode)

---

## AP Not Coming Online (No Power / No Boot)

**Symptom:** All LEDs off, AP not discoverable

1. Verify PoE switch port is **802.3at** — 802.3af (15.4W) is insufficient
2. Check ETH0 LED on PoE switch — if off, check cable continuity (max 100m, outdoor Cat6)
3. Test with a different PoE port or midspan injector to isolate PoE switch port failure
4. Verify cable is not damaged (UV/weather degradation on outdoor runs)
5. Check PoE budget: ensure switch has available wattage (25.5W per AP)

**PoE reset remotely:** On managed PoE switch, cycle PoE on the port (disable/enable) to force reboot.

---

## AP Boots but Won't Join Controller (Fit Mode)

**Symptom:** System LED green, but AP not appearing in AC-1004

1. Confirm AP and AC-1004 are on the same L2 network (VLAN) or that DHCP option 43 is configured with controller IP
2. Check firewall/ACL: CAPWAP uses **UDP 5246 (control)** and **UDP 5247 (data)** — must be allowed
3. On AC-1004: **Wireless → AP Management → Unmanaged APs** — look for AP by MAC address
4. Verify AP is in Fit mode: console into AP → `show ap-mode`
5. Force controller IP: `AP_config# capwap server <AC-1004-IP>`
6. Check AC-1004 has not hit max AP limit (64 for AC-1004)
7. Review AC-1004 logs: **System → Logs → AP Events** for rejection reason

---

## AP Offline in Controller (Was Working)

**Symptom:** AP shows offline in AC-1004 dashboard

1. Check physical power: walk to pole, verify LEDs
2. PoE reset from managed switch port
3. Ping AP management IP: `ping <AP-IP>` from AC-1004 or same network
4. Check for CAPWAP heartbeat timeout: AC-1004 → AP detail → last seen timestamp
5. Review syslog for AP disconnect events (time-correlate with any switch/power events)
6. If multiple APs went offline simultaneously → likely uplink switch failure, not individual AP issue

---

## Poor Wi-Fi Signal / Coverage Gaps in RV Sites

**Symptom:** Clients report weak signal, slow speeds, or disconnection near certain sites

1. Check AP mounting height and orientation — AP should be at 4–6 m, radome pointing up
2. Identify if issue is 2.4G or 5G specific:
   - 5G has shorter range — clients far from pole may only get 2.4G
   - Large RVs (Class A/C) block 5G significantly; 2.4G penetrates better
3. Check TX power setting — if too low, coverage gap; if too high in dense areas, co-channel interference
4. Run `show client detail <MAC>` (standalone) or check AC-1004 client stats — look at RSSI and data rate
5. Check channel utilization: high utilization on 2.4G Ch 6 may indicate neighboring AP on same channel
6. Consider adjusting channel plan if interference detected (see rv-park-deployment.md)

**Recommended RSSI thresholds:**
- Good: > −65 dBm
- Acceptable: −65 to −75 dBm
- Poor: < −75 dBm (client will struggle at 5 GHz)

---

## Client Authentication Failures

**Symptom:** Clients see SSID but can't connect; "wrong password" or "authentication timeout"

1. Verify SSID password is correct (case-sensitive)
2. Check client is connecting to the right SSID (not a neighboring park's same name)
3. For WPA3: older clients (pre-2018 devices) may not support SAE — ensure WPA2/WPA3 transition mode is enabled
4. For 802.1X/RADIUS: verify RADIUS server is reachable from AP; check shared secret
5. Check MAC ACL: client MAC may be blocked — review AC-1004 → Security → MAC ACL list
6. Check client isolation: AP-to-AP isolation is correct but client-to-internet should work
7. Review auth logs: AC-1004 → Logs → Auth Events (Fit mode) or `show log` (standalone)

---

## Slow Speeds / Low Throughput

**Symptom:** Clients connect but speeds are far below expected

1. Check band: is client on 2.4G (max ~100–200 Mbps real-world) or 5G (max ~400–800 Mbps)?
   - Enable band steering to move dual-band capable clients to 5G
2. Check channel congestion: use `show rf stats` or AC-1004 RF analytics — look for high co-channel utilization
3. Check bandwidth limits: per-client or per-SSID caps configured on AC-1004 or standalone AP
4. Check client count per AP: >50 simultaneous active clients on one AP causes congestion
5. Check ETH0 uplink speed: `show interface eth0` — should be 1000M full-duplex
6. Check for rogue APs: `show rogue ap` — unauthorized APs on same channels degrade performance
7. Verify OFDMA and MU-MIMO are enabled in Wi-Fi 6 settings

---

## AP Keeps Rebooting / System LED Blinking

**Symptom:** System LED blinks repeatedly; AP not stable

1. Check power: marginal 802.3at PoE source can cause instability under full radio load
2. Check operating temperature: AP at ambient >70°C will thermal-throttle; check direct sunlight exposure
3. Check firmware: corrupted firmware can cause boot loop — perform factory reset and re-flash
4. Review logs before reboot: if accessible, `show log` for crash/watchdog messages
5. Factory reset: hold reset button 10 s → reconfigure from scratch

---

## Firmware Upgrade Issues

**Symptom:** AP stuck in upgrade state; System LED blinking long after expected completion

1. **Do not cut power** while System LED is blinking — this corrupts firmware
2. Wait up to 10 minutes for large firmware files
3. If stuck >15 minutes: console in — check `show version` for current state
4. If bricked: use console to enter recovery mode (AP-T565 supports TFTP recovery boot)
   - Set PC to 192.168.1.100, TFTP server at 192.168.1.100
   - Hold reset during boot to enter recovery
   - AP fetches `firmware.bin` from TFTP server automatically

---

## LED Reference Quick Card

| LED + State | Meaning |
|---|---|
| System green solid | Normal |
| System green blinking | Booting / upgrading |
| System red solid | Hardware fault |
| System off | No power |
| ETH0 off | No link / no PoE |
| ETH0 green solid | 1G link |
| Radio LED off | Radio disabled or error |

---

## Log Collection for FS Support

When opening a support ticket with FS:
```bash
AP# show version          # Firmware and serial
AP# show running-config   # Full config
AP# show log              # System log
AP# show client           # Client table
```

Export via: System → Backup → Download Diagnostic Report (web UI, standalone mode)

FS Support: https://www.fs.com/products_support.html
