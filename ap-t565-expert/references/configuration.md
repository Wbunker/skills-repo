# AP-T565 Standalone Configuration Reference

> This guide applies to **Fat (standalone) mode** only. In Fit mode (AC-1004 controller), all config is managed from the AC-1004 — refer to `ac1004-expert` skill instead.

## Web UI Access

1. Connect laptop to AP via Ethernet (ETH0)
2. Set laptop to static IP `192.168.1.x` (e.g., `192.168.1.100`), subnet `255.255.255.0`
3. Open browser → `http://192.168.1.1`
4. Login: `admin` / `admin` (defaults — change immediately)

### Switching Between Modes

**Web UI:** System → Working Mode → select Fat / Fit / Cloud → Save → Reboot

In **Fit mode**, the web UI becomes read-only — all config pushes from AC-1004.

## SSID Configuration

**Path:** Wireless → SSID → Add

| Field | Typical RV Park Value |
|---|---|
| SSID Name | `PecanGrove-WiFi` |
| Security | WPA2-PSK or WPA3-SAE |
| Passphrase | (site-specific) |
| VLAN | Tag to guest VLAN ID |
| Broadcast SSID | Enabled |
| Max clients per SSID | 50–100 (tune per AP) |
| Client isolation | Enabled (guest network) |

**Band steering:** Enable under Advanced SSID settings to push dual-band clients to 5 GHz.

## Radio Configuration

**Path:** Wireless → Radio

### 2.4 GHz Radio

| Parameter | Recommended Value |
|---|---|
| Enable | Yes |
| Channel | Manual (per channel plan) or Auto |
| Channel width | 20 MHz |
| TX power | 17–20 dBm |
| Guard interval | Short (400ns) |
| Beacon interval | 100 ms |
| DTIM | 1 |

### 5 GHz Radio

| Parameter | Recommended Value |
|---|---|
| Enable | Yes |
| Channel | Manual (149/153/157/161 preferred) or Auto |
| Channel width | 40 MHz |
| TX power | 20–23 dBm |
| Guard interval | Short (400ns) |
| Beacon interval | 100 ms |
| DTIM | 1 |

### Wi-Fi 6 (802.11ax) Features

| Feature | Setting |
|---|---|
| OFDMA | Enable (increases capacity in dense environments) |
| BSS Color | Enable (reduces co-channel interference) |
| MU-MIMO | Enable |
| Target Wake Time (TWT) | Enable (reduces IoT device battery drain) |
| WPA3 | Enable alongside WPA2 (transition mode for compatibility) |

## VLAN Configuration

**Path:** Network → VLAN

- Management VLAN: AP management traffic (separate from guest data)
- Native/untagged: Management VLAN on ETH0
- Tagged VLANs: Map each SSID to its VLAN ID

```
Example VLAN mapping:
  VLAN 1   → Management (untagged on uplink)
  VLAN 100 → Guest WiFi → SSID: PecanGrove-WiFi
  VLAN 200 → Staff WiFi → SSID: PecanGrove-Staff
```

## Roaming Settings

**Path:** Wireless → Roaming (or Advanced → Fast Roaming)

| Feature | Setting |
|---|---|
| 802.11k (Neighbor Reports) | Enable |
| 802.11v (BSS Transition) | Enable |
| 802.11w (Management Frame Protection) | Enable (required for WPA3) |
| 802.11r (Fast BSS Transition) | Enable (use with WPA2-Enterprise; optional with PSK) |
| Roaming RSSI threshold | −70 dBm |

## Security Settings

**Path:** Wireless → Security / System → Security

| Feature | Setting |
|---|---|
| 802.1X authentication | Configure RADIUS server IP/port/secret if using enterprise auth |
| MAC-based ACL | Add/block specific client MACs |
| WIDS (Wireless IDS) | Enable rogue AP detection and intrusion detection |
| Rogue AP countermeasure | Enable to actively de-auth clients connecting to rogue APs |
| Management access | Restrict web UI to management VLAN only |
| SSH | Enable; disable Telnet in production |

## QoS & Bandwidth Control

**Path:** Wireless → QoS or Advanced → Bandwidth Control

- WMM (Wi-Fi Multimedia): Always enable — required for voice/video QoS
- Per-client bandwidth limit: Set upload/download caps (e.g., 10 Mbps/25 Mbps per guest client)
- Per-SSID bandwidth limit: Aggregate cap on SSID total throughput

## System Settings

**Path:** System

| Setting | Recommendation |
|---|---|
| Hostname | `AP-T565-<site-ID>` (e.g., `AP-T565-A01` for row A, unit 1) |
| NTP server | Configure to local NTP or `pool.ntp.org` |
| Syslog | Point to AC-1004 or central syslog server IP |
| Firmware upgrade | System → Upgrade → upload `.bin` file from FS support portal |
| Config backup | System → Backup → save `.cfg` file before any changes |

## FS Official Documentation

- Web config guide: https://img-en.fs.com/file/user_manual/ap-series-web-configuration-guide.pdf
- CLI reference: https://img-en.fs.com/file/user_manual/ap-series-cli-reference-guide.pdf
- WLC software guide: https://img-en.fs.com/file/user_manual/wireless-lan-controller-software-user-guide.pdf
