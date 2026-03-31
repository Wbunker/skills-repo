# AP-N505 Standalone Configuration Reference

> This guide applies to **Fat (standalone) mode** only. In Fit mode (AC-1004 controller), all config is pushed from the AC-1004 — refer to `ac1004-expert` skill instead.

## Web UI Access

1. Connect laptop to AP via Ethernet (ETH0)
2. Set laptop to static IP `192.168.1.x` (e.g., `192.168.1.100`), subnet `255.255.255.0`
3. Open browser → `http://192.168.1.1`
4. Login: `admin` / `admin` (defaults — change immediately)

### Switching Between Modes

**Web UI:** System → Working Mode → select Fat / Fit / Cloud → Save → Reboot

In **Fit mode**, web UI becomes read-only — all config pushes from AC-1004.

## SSID Configuration

**Path:** Wireless → SSID → Add

| Field | Typical Pavilion Value |
|---|---|
| SSID Name | `PecanGrove-WiFi` |
| Security | WPA2-PSK or WPA3-SAE |
| Passphrase | (site-specific) |
| VLAN | Tag to guest VLAN ID |
| Broadcast SSID | Enabled |
| Max clients per SSID | 50–75 (tune per AP density) |
| Client isolation | Enabled (guest network) |

**Band steering:** Enable under Advanced SSID settings — pushes dual-band clients to 5 GHz automatically.

## Radio Configuration

**Path:** Wireless → Radio

### 2.4 GHz Radio

| Parameter | Recommended Value |
|---|---|
| Enable | Yes |
| Channel | Manual (per pavilion channel plan) or Auto |
| Channel width | 20 MHz |
| TX power | 14–17 dBm |
| Guard interval | Short (400ns) |
| Beacon interval | 100 ms |

### 5 GHz Radio

| Parameter | Recommended Value |
|---|---|
| Enable | Yes |
| Channel | Manual (149/153/157/161 or 36/40/44/48) |
| Channel width | **80 MHz** (standard) or 160 MHz (low-density zones) |
| TX power | 17–20 dBm |
| Guard interval | Short (400ns) |
| Beacon interval | 100 ms |

### 160 MHz Channel Width

To enable 160 MHz on 5 GHz for maximum throughput:

**Path:** Wireless → Radio → 5G → Channel Width → 160 MHz

**Constraints:**
- Only 2 non-overlapping 160 MHz blocks in US 5 GHz band — Ch 36/160 and Ch 149/160
- With 5 APs in one building, enable 160 MHz on at most 2 APs to avoid co-channel interference
- Clients must support 160 MHz (most Wi-Fi 6 phones/laptops do; older devices do not)

### Wi-Fi 6 (802.11ax) Features

| Feature | Setting |
|---|---|
| OFDMA | Enable — increases capacity with many simultaneous clients |
| BSS Color | Enable — reduces co-channel interference indoors |
| MU-MIMO | Enable |
| Target Wake Time (TWT) | Enable — reduces battery drain for IoT/mobile devices |
| WPA3 | Enable alongside WPA2 (transition mode) |

## VLAN Configuration

**Path:** Network → VLAN

```
Example mapping:
  VLAN 1   → Management (untagged on uplink)
  VLAN 100 → Guest WiFi → SSID: PecanGrove-WiFi
  VLAN 200 → Staff WiFi → SSID: PecanGrove-Staff
```

Uplink (ETH0) should carry tagged VLANs for each SSID plus untagged management VLAN.

## Roaming Settings

**Path:** Wireless → Roaming

| Feature | Setting |
|---|---|
| 802.11k (Neighbor Reports) | Enable |
| 802.11v (BSS Transition) | Enable |
| 802.11w (Management Frame Protection) | Enable (required for WPA3) |
| 802.11r (Fast BSS Transition) | Enable — critical in dense 5-AP pavilion |
| Roaming RSSI threshold | −68 dBm (tighter than outdoor; indoor cells are smaller) |

## Security Settings

**Path:** Wireless → Security / System → Security

| Feature | Setting |
|---|---|
| 802.1X | Configure RADIUS server IP/port/secret for enterprise auth |
| MAC-based ACL | Block/allow specific client MACs |
| WIDS | Enable rogue AP detection and wireless intrusion detection |
| Management access | Restrict to management VLAN only |
| SSH | Enable; disable Telnet in production |

## QoS & Bandwidth Control

**Path:** Wireless → QoS or Advanced → Bandwidth Control

- **WMM:** Always enable — required for voice/video quality
- **Per-client limit:** e.g., 15 Mbps down / 5 Mbps up per guest client
- **Per-SSID aggregate limit:** optional cap on total SSID throughput

## System Settings

| Setting | Recommendation |
|---|---|
| Hostname | `AP-N505-PAV-<nn>` (e.g., `AP-N505-PAV-01` through `PAV-05`) |
| NTP | `pool.ntp.org` or local NTP server |
| Syslog | Point to AC-1004 or central syslog server |
| Config backup | System → Backup before any changes |

## FS Official Documentation

- Web config guide: https://img-en.fs.com/file/user_manual/ap-series-web-configuration-guide.pdf
- CLI reference: https://img-en.fs.com/file/user_manual/ap-series-cli-reference-guide.pdf
- WLC software guide: https://img-en.fs.com/file/user_manual/wireless-lan-controller-software-user-guide.pdf
