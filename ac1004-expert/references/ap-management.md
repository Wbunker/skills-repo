# AP Management — AC-1004

## Overview

The AC-1004 manages up to **64 Wi-Fi 6 APs** using the **CAPWAP protocol** (encrypted control/data channel). APs operate in **fit mode** (controller-managed, default) or **fat mode** (standalone, no controller needed).

---

## Adopting an AP

### Prerequisites
- AP must be on the same Layer 2 network as the AC-1004, OR reachable via Layer 3 with CAPWAP routing
- AP must be in **fit mode** (factory default)
- AP's Native VLAN on the upstream switch port must match the AC-1004's management VLAN

### Adoption Process (automatic)
1. Connect AP to a PoE port on the AC-1004 (or to a PoE switch with IP connectivity to the AC)
2. AP receives DHCP address and discovers the AC via broadcast or DHCP option 43
3. AP appears in Web UI: **Config → AP Management** with status `Online`
4. Optionally bind AP by MAC to lock it to a named config:

```bash
Switch_config# ap-config ap-name <DESCRIPTIVE-NAME>
Switch_config_apc# ap-mac <AP-MAC-ADDRESS>
Switch_config_apc# exit
Switch_config# wr
```

### Verify AP is online
```bash
Switch# show ap-config running
```
Web UI: Config → AP Management — AP shows `Online` status.

---

## Configuring APs

### Apply settings to ALL APs
```bash
Switch_config# ap-config all
Switch_config_apc# [configuration commands]
```
> `ap-config ap-name` settings **take priority** over `ap-config all` settings for that specific AP.

### Apply settings to a specific AP
```bash
Switch_config# ap-config ap-name <AP-NAME>
Switch_config_apc# [configuration commands]
```

### Assign WLAN/SSID to a radio
```bash
Switch_config# ap-config ap-name <AP-NAME>
Switch_config_apc# radio 1
Switch_config_apc_r1# wlan-vlan-map <WLAN-ID> <VLAN-ID>
Switch_config_apc_r1# exit
```

### Set radio power and channel
```bash
Switch_config_apc_r1# power <level>        # Auto or specific level
Switch_config_apc_r1# channel <number>     # e.g., 1, 6, 11 for 2.4GHz; 36, 40, 44... for 5GHz
```

---

## AP Modes

| Mode | Description | Use case |
|---|---|---|
| **Fit mode** | Controller-managed; config pushed from AC | Normal operation at Pecan Grove |
| **Fat mode** | Standalone; configured independently | Temporary standalone use or recovery |

Switch modes via CLI:
```bash
Switch_config_apc# ap-mode fit    # Return to controller mode
Switch_config_apc# ap-mode fat    # Switch to standalone mode
```

---

## Removing an AP

```bash
Switch_config# ap-config ap-name <AP-NAME>
Switch_config_apc# no ap-mac <AP-MAC-ADDRESS>
Switch_config_apc# exit
Switch_config# wr
```

Physically disconnect the AP from the network.

---

## Seamless Roaming

The AC-1004 supports seamless L2 and L3 roaming — clients maintain sessions, voice calls, and data connections when moving between APs without topology changes or re-authentication. No special configuration is required beyond standard AP adoption.

---

## AP Backup Groups

The AC-1004 supports AP backup groups for controller redundancy. If the primary AC fails, APs fail over to the backup AC. Configure via Web UI: Config → AP Management → Backup Groups.

---

## Airware Cloud AP Management

**Zero-Touch Provisioning:** Scan QR code on AP packaging → AP auto-adopts with pre-loaded config. No console or manual CLI needed.

**Bulk configuration:** Apply SSID, VLAN, and radio settings to all APs at once from the Airware dashboard.

**Topology view:** Auto-discovered network map showing all APs, their signal coverage, and connected clients.

Login: https://airware-login.fs.com
