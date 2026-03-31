# TA1910-4GVC-W Web UI Configuration Reference

## Web UI Access

1. Connect laptop to any LAN port (LAN1–LAN4) on the ONU
2. Set laptop to DHCP — ONU assigns 192.168.123.x
3. Browse to `http://192.168.123.1`
4. Login: `admin` / `super&123` (factory default — change immediately)

## Web UI Menu Structure

```
Status      — PON status, WAN connection, LAN devices, WiFi clients
LAN         — IPv4/IPv6 LAN address, DHCP server settings, IGMP snooping
WLAN        — 2.4G and 5G SSID, password, channel, security, enable/disable
WAN         — PON WAN connections (bridge or routing mode, VLAN, DHCP/PPPoE)
Service     — DHCP relay, DNS proxy, RIP, IP filtering, firewall
VoIP        — SIP server, POTS port auth, caller ID, codec settings
Advanced    — TR-069, system management, LOID/SN, factory reset, firmware
```

---

## WAN Configuration

**Path:** WAN → WAN Connection → Add / Edit

The ONU can operate in two WAN modes per service:

### Routing Mode (typical for cabin internet)
- ONU acts as NAT router — cabin devices get private IPs (192.168.123.x)
- ONU obtains public/ISP IP via DHCP or PPPoE on its PON WAN interface
- **Recommended for cabin use** — provides per-cabin NAT isolation

| Field | Value |
|---|---|
| Connection name | Internet |
| Mode | Routing |
| VLAN ID | Match OLT service VLAN (e.g., 100) — confirm with OLT config |
| IP type | DHCP (OLT BRAS assigns IP) or PPPoE (if ISP uses PPPoE) |
| Enable NAT | Yes |
| Enable Firewall | Yes |

### Bridge Mode (less common — for transparent L2)
- ONU passes traffic through without NAT — device on LAN gets public IP directly
- Use only if a separate router behind the ONU handles NAT/routing
- Not typical for individual cabins

### Saving WAN Changes
After editing: **Save** → ONU applies changes. PON LED may briefly flicker during WAN service restart.

---

## LAN Configuration

**Path:** LAN → IPv4

| Field | Default | Notes |
|---|---|---|
| LAN IP | 192.168.123.1 | Change per-cabin to avoid conflicts if bridging |
| Subnet | 255.255.255.0 | /24 — 253 usable addresses |
| DHCP server | Enabled | |
| DHCP start | 192.168.123.100 | |
| DHCP end | 192.168.123.200 | |
| Lease time | 24 hours | |
| DNS server 1 | 8.8.8.8 | Or OLT/ISP-provided DNS |

**Per-cabin IP addressing:** All 16 ONUs default to the same 192.168.123.0/24 subnet. This is fine since each ONU is isolated by NAT — cabin subnets are not routed between cabins.

---

## WLAN Configuration

**Path:** WLAN → 2.4G / 5G

### Basic SSID Setup

| Field | Recommended Value |
|---|---|
| SSID | `PecanGrove-Cabin-<NN>` (e.g., `PecanGrove-Cabin-01`) |
| Security | WPA2-PSK (AES) |
| Passphrase | Cabin-specific (see cabin deployment plan) |
| Broadcast SSID | Enabled |
| Enable | Yes (both bands) |

### 2.4 GHz Radio Settings

| Parameter | Recommended |
|---|---|
| Channel | Auto or manual (1, 6, or 11) |
| Channel width | 20 MHz (20/40 MHz auto is OK) |
| TX power | Medium (auto or 17 dBm) |
| Mode | 802.11b/g/n mixed |

### 5 GHz Radio Settings

| Parameter | Recommended |
|---|---|
| Channel | Auto or manual (36, 40, 44, 48, 149, 153, 157, 161) |
| Channel width | 80 MHz for best throughput |
| TX power | Auto or high (20 dBm max) |
| Mode | 802.11a/n/ac mixed |

### Disabling WiFi (if cabin has wired-only guests)
WLAN → 2.4G → Enable: Off
WLAN → 5G → Enable: Off

---

## VoIP Configuration

**Path:** VoIP → SIP Settings

| Field | Value |
|---|---|
| SIP server | VoIP provider SIP server IP/hostname |
| SIP port | 5060 (default) |
| Account / User | Phone number or SIP username |
| Password | SIP account password |
| Registration mode | Register |

VoIP is optional at Pecan Grove — POTS ports only function if a SIP provider is configured. If no VoIP service, leave VoIP settings empty; POTS ports remain inactive.

---

## Firewall & Service

**Path:** Service → Firewall / IP Filtering

| Feature | Recommendation |
|---|---|
| Firewall | Enabled (default) — blocks unsolicited inbound traffic |
| IP filtering | Optional — block specific outbound destinations |
| Port forwarding | Service → Port Forwarding — expose cabin device services (e.g., NVR) |
| DMZ | Service → DMZ — expose one device fully (not recommended for cabins) |

---

## Advanced Settings

**Path:** Advanced

| Feature | Notes |
|---|---|
| Firmware upgrade | Advanced → Firmware Upgrade → upload `.bin` from FS support portal |
| System time / NTP | Advanced → System Time — set NTP server (pool.ntp.org) |
| Config backup | Advanced → Config Backup — save `.cfg` before changes |
| Factory reset | Advanced → Factory Reset (or hold RESET button 10 s) |
| TR-069 | Advanced → TR-069 — ACS URL for remote provisioning |
| LOID / SN | Advanced → PON Settings — view or set LOID/SN for OLT auth |
| Password change | Advanced → Account Management — change admin password |

---

## FS Documentation Links
- ONU onboarding guide: https://www.fs.com/blog/guide-to-easily-onboarding-configuring-onu-case-of-fs-oltonu-4517.html
- ManualsLib quick start: https://www.manualslib.com/manual/2831861/Fs-Ta1910-4gvc-W.html
