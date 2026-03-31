# Troubleshooting — AC-1004

## Quick Diagnosis Index

- [AP Not Adopting / Offline](#ap-not-adopting--offline)
- [Clients Can't Connect to SSID](#clients-cant-connect-to-ssid)
- [Captive Portal Not Redirecting](#captive-portal-not-redirecting)
- [Slow Wi-Fi / High Latency](#slow-wi-fi--high-latency)
- [Management GUI Inaccessible](#management-gui-inaccessible)
- [Log Review](#log-review)
- [SNMP Traps Not Firing](#snmp-traps-not-firing)

---

## AP Not Adopting / Offline

**Step 1 — Verify AP is visible in Web UI:**
Web UI: Config → AP Management — look for the AP in the list.
```bash
Switch# show ap-config running
```

**Step 2 — Check physical layer:**
- Confirm PoE port LED is lit (PoE delivering power)
- AP LED status: solid green = normal; flashing = booting/searching for AC

**Step 3 — Check IP connectivity:**
```bash
Switch# ping <AP-IP>
```
If ping fails:
- Verify DHCP is assigning an IP to the AP
- Verify Native VLAN on the switch port matches the AC management VLAN
- Verify no ACL is blocking CAPWAP (UDP 5246/5247)

**Step 4 — Check AP mode:**
AP must be in **fit mode** to adopt. If it was manually set to fat mode:
```bash
Switch_config# ap-config ap-name <AP-NAME>
Switch_config_apc# ap-mode fit
Switch_config_apc# exit
Switch_config# wr
```

**Step 5 — Check SNMP trap for AP join failure:**
```bash
Switch# show ac-config
```
If traps are configured, an alert fires when AP fails to join. Check NMS or syslog server.

**Step 6 — Layer 3 CAPWAP (AP on different subnet):**
AP must be able to reach the AC's IP. Verify routing and that CAPWAP (UDP 5246, 5247) is not blocked by firewall.

---

## Clients Can't Connect to SSID

**Check SSID is broadcasting:**
```bash
Switch# show wlan
```
SSID must be `up` / enabled.

**Check WLAN-to-VLAN mapping:**
```bash
Switch# show ap-config running
```
Verify the WLAN ID is mapped to the correct VLAN on the radio.

**Check uplink trunk:**
Ensure the VLAN is allowed on the uplink port trunk:
```bash
Switch# show interface gigabitethernet 0/0 switchport
```

**Check PSK or auth config:**
- WPA2/WPA3-PSK: verify password is correct in wlan config
- 802.1X: test RADIUS connectivity — `Switch# show radius statistics`
- Portal: see Captive Portal section below

**Check client blacklist:**
Web UI: Config → WLAN → MAC Filter — confirm client MAC is not blocked.

---

## Captive Portal Not Redirecting

1. Verify Web Authentication is enabled on the SSID: Web UI → Config → WLAN → Security
2. Verify client received a DHCP address in the correct VLAN
3. Verify DNS is resolving — portal redirect requires DNS to return AC-1004's IP for any domain
4. Check that client has no cached network settings (forget network, reconnect)
5. On the upstream router, ensure VLAN 20 (guest) traffic is NOT blocked from reaching AC-1004's portal IP before authentication
6. Test by navigating to `http://192.168.1.1` directly in the browser

---

## Slow Wi-Fi / High Latency

**Check connected client count per AP:**
Web UI: Monitor → AP Management → select AP → Client Count
- If >30 clients per AP, consider adding APs or enabling band steering to 5GHz

**Check per-user bandwidth limits:**
```bash
Switch# show wlan <WLAN-ID>
```
Verify bandwidth limits are set appropriately for site capacity.

**Check for channel interference:**
Web UI: Monitor → RF Environment → check channel utilization and interference
- High utilization (>70%) = congested channel; change AP channel manually

**Check uplink saturation:**
```bash
Switch# show interface gigabitethernet 0/0
```
If uplink is maxed out, the bottleneck is the ISP connection, not Wi-Fi.

**Check for rogue clients consuming bandwidth:**
Web UI: Monitor → Wireless Clients → sort by traffic usage → kick/block heavy abusers

---

## Management GUI Inaccessible

**Try console access first:**
- Connect via RJ45 console cable → RS232 → USB adapter
- 115200 baud, 8N1, no flow control (PuTTY / SecureCRT)
- Login: `admin` / `admin` (or current password)

**Check management IP:**
```bash
Switch# show interface
Switch# show running-config interface gigabitethernet 0/0
```

**Account lockout:**
Wait 1 minute after 5 failed login attempts, then retry.

**Reset to factory defaults (last resort):**
Hold the physical reset button on the AC-1004 for 10+ seconds while powered on. This wipes all configuration — reconnect via console and rebuild.

---

## Log Review

### View local log buffer
```bash
Switch# show log
```

### Key events to look for
| Log keyword | Meaning |
|---|---|
| `AP join` / `AP leave` | AP connected or disconnected from controller |
| `auth fail` | Authentication failure for a wireless client |
| `CAPWAP` | Control channel events between AC and APs |
| `RADIUS` | RADIUS server reachability or auth issues |
| `portal` | Captive portal login events |
| `CPU high` | Resource spike — may indicate attack or bug |

### Remote syslog (up to 5 servers)
```bash
Switch_config# logging host <SYSLOG-SERVER-IP>
Switch_config# logging level 6     # 6 = informational; 7 = debug (verbose)
```

### Airware Cloud logs
Real-time event stream, AI-based fault detection, and historical log access:
https://airware-login.fs.com → Monitor → Events

---

## SNMP Traps Not Firing

```bash
# Verify trap host and community are configured
Switch# show ac-config

# Reconfigure if missing
Switch_config# snmp-server host <NMS-IP> traps version 3 <USERNAME>
Switch_config# ac-config
Switch_config_ac# snmp-trap ap-join enable
Switch_config_ac# exit
Switch_config# wr
```

Verify NMS server is listening on UDP 162 and not blocked by firewall.
