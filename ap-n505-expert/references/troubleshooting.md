# AP-N505 Troubleshooting Reference

## Quick Diagnostic Checklist

- [ ] ETH0 LED solid green (link up + PoE)
- [ ] System LED solid green (booted, not in error)
- [ ] Radio LEDs green (radios active)
- [ ] Can ping AP management IP
- [ ] AP visible in AC-1004 "Managed APs" list (Fit mode)

---

## AP Not Coming Online (No Power / No Boot)

**Symptom:** All LEDs off

1. Verify PoE switch port supports **802.3af** — AP-N505 only needs 12.95W; 802.3af (15.4W budget) is sufficient
2. Check ETH0 cable — max 100 m, Cat5e or better
3. Swap to a different PoE port to rule out port failure
4. Check PoE switch per-port budget — if switch is overloaded, lower-priority ports shut down
5. Try with a known-good PoE injector to isolate switch vs. AP vs. cable

> **Common mistake:** Assuming 802.3at is required. AP-N505 uses 802.3af — standard PoE switches and all AC-1004 PoE ports are compatible.

---

## AP Boots but Won't Join Controller (Fit Mode)

**Symptom:** System LED green, AP missing from AC-1004

1. Confirm AP and AC-1004 are on the same L2 VLAN, or DHCP option 43 points to AC-1004 IP
2. Check firewall/ACL: CAPWAP uses **UDP 5246 (control)** and **UDP 5247 (data)**
3. On AC-1004: **Wireless → AP Management → Unmanaged APs** — look for AP by MAC
4. Verify AP is in Fit mode: console → `show ap-mode`
5. Force controller: `AP_config# capwap server <AC-1004-IP>`
6. Verify AC-1004 has capacity (max 64 APs)
7. Review AC-1004 logs: **System → Logs → AP Events**

---

## AP Offline in Controller (Was Working)

**Symptom:** AP shows offline in AC-1004 dashboard

1. Check physical: LEDs at AP location
2. PoE reset: disable/enable PoE on switch port to reboot AP remotely
3. Ping AP management IP from AC-1004 or same subnet
4. Check AC-1004 → AP detail → last-seen timestamp for when it dropped
5. Correlate with syslog: power event, switch reboot, VLAN change?
6. Multiple APs offline at once → suspect uplink switch or VLAN config change, not individual AP

---

## Poor Signal / Coverage Gaps in Pavilion

**Symptom:** Weak signal or dead spots in parts of the pavilion

1. Check mounting position — AP should be ceiling-mounted centrally above the coverage zone, not in a corner
2. Verify AP is mounted face-down (flat face toward floor) — mounting upside-down cuts signal significantly
3. Metal roof panels, HVAC ducts, and structural beams cause shadowing on 5 GHz
4. Check TX power: `show radio` — if power is set too low (< 14 dBm), edge coverage suffers
5. 5 GHz range is shorter than 2.4 GHz indoors — verify band steering is not forcing all clients to 5G beyond its range
6. Check client RSSI on AC-1004 dashboard — below −75 dBm indicates coverage gap

**Rule of thumb for pavilion coverage:**
- −65 dBm: excellent
- −65 to −72 dBm: good
- −72 to −78 dBm: marginal
- < −78 dBm: poor — client will drop or get very slow

---

## Slow Speeds / Low Throughput

**Symptom:** Clients connect but throughput is far below expected

1. **Check band:** Is client on 2.4G or 5G?
   - 2.4G: ~100–150 Mbps real-world max; if client needs more, enable band steering
   - 5G at 80 MHz: ~300–500 Mbps; 160 MHz: ~500–800 Mbps
2. **Check channel utilization:** `show rf stats` — high utilization means congestion; try different channel
3. **Check client count:** > 50 active clients on one AP causes congestion — consider redistributing load
4. **Check 160 MHz config:** If you enabled 160 MHz but adjacent APs share the same 160 MHz block, co-channel interference degrades performance more than the wider channel gains
5. **Check bandwidth limits:** Per-client or per-SSID caps on AC-1004 may be the bottleneck
6. **Check ETH0 speed:** `show interface eth0` — should be 1000M full-duplex; if 100M, check cable quality/length
7. **Check for rogue APs:** `show rogue ap` — unauthorized APs on same channels cause severe interference indoors

---

## Client Authentication Failures

**Symptom:** Clients see SSID but fail to connect

1. Verify passphrase (case-sensitive)
2. **WPA3 compatibility:** Pre-2019 devices may not support WPA3-SAE — ensure WPA2/WPA3 transition mode is enabled, not WPA3-only
3. **MAC ACL:** Check if client MAC is blocked in AC-1004 → Security → MAC ACL
4. **RADIUS issues (enterprise auth):** Verify RADIUS server IP, port (1812), and shared secret; check RADIUS server logs
5. Review auth logs: AC-1004 → Logs → Auth Events

---

## 160 MHz Not Working / No Speed Improvement

**Symptom:** 5G radio set to 160 MHz but clients still show 80 MHz speeds

1. Verify client supports 160 MHz — check AC-1004 client detail for capability flags
2. Confirm no co-channel interference: only 2 non-overlapping 160 MHz channels in US — if another AP in range uses same 160 MHz block, fallback occurs
3. Check regulatory domain setting — some country configs restrict 160 MHz
4. Confirm channel is set to 36 or 149 (the base channels for the two 160 MHz blocks)
5. Some clients only use 160 MHz when signal is strong (> −65 dBm) — verify RSSI

---

## AP Keeps Rebooting / Unstable

**Symptom:** System LED blinks repeatedly or AP cycle-boots

1. Check operating temperature — pavilion environments can get hot; AP-N505 max is 50°C
2. Verify PoE: marginal 802.3af source (right at 15.4W limit) may be insufficient; test with dedicated injector
3. Corrupted firmware → factory reset and re-flash
4. Console in before reboot → `show log` for watchdog/crash messages

---

## LED Quick Reference

| LED + State | Meaning |
|---|---|
| System green solid | Normal |
| System green blinking | Booting / upgrading — do not cut power |
| System red solid | Hardware fault |
| System off | No power |
| ETH0 off | No link or no PoE |
| ETH0 green solid | 1G link |
| Radio off | Radio disabled or fault |

---

## Log Collection for FS Support

```bash
AP# show version
AP# show running-config
AP# show log
AP# show client
```

Or: System → Backup → Diagnostic Report (web UI, standalone mode)

FS Support: https://www.fs.com/products_support.html
