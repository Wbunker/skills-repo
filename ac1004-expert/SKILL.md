---
name: ac1004-expert
description: "Expert guidance for the FS AC-1004 802.11ax Wireless LAN Controller used at Pecan Grove RV Park. Use when the user needs to manage APs, configure SSIDs or VLANs, set up authentication or captive portal, review logs, update firmware, control per-user bandwidth, troubleshoot Wi-Fi connectivity, or perform routine maintenance on the wireless network. Covers CLI, web UI, SNMP, and Airware cloud management."
---

# FS AC-1004 Wireless LAN Controller Expert

**Device:** FS AC-1004 — 802.11ax Wi-Fi 6 Wireless LAN Controller (AC + PoE switch + gateway)
**Location:** Pecan Grove RV Park wireless network hub
**Manufacturer docs:** https://www.fs.com/products/141375.html

## Key Specs

| Item | Value |
|---|---|
| Standard | 802.11ax (Wi-Fi 6) |
| Max APs managed | 64 Wi-Fi 6 APs |
| Max concurrent users | 4,000 |
| Ports | 1x 1GbE service + 4x 1GbE PoE + RJ45 console + USB |
| VLAN support | 1,000 VLANs |
| AP protocol | CAPWAP (encrypted) |
| Throughput | 5 Gbps aggregate |
| Management | CLI, Web UI (HTTP/HTTPS), SNMP v3, Airware cloud, SSH, Telnet |
| OS | FSOS (FiberStore Operating System) |

## Access & Default Credentials

| Method | Details |
|---|---|
| **Web UI** | `http://192.168.1.1` — username `admin` / password `admin` |
| **Console** | 115200 baud, 8N1, no flow control (RJ45 → RS232 → USB adapter) |
| **SSH/Telnet** | `192.168.1.1` (Telnet insecure — use SSH in production) |
| **Airware cloud** | https://airware-login.fs.com |

> **Security note:** Change default `admin/admin` credentials immediately on initial setup.
> Account lockout: 5 wrong password attempts = 1 minute lockout.

## Reference Files

| Topic | File | When to read |
|---|---|---|
| CLI commands | [references/cli-commands.md](references/cli-commands.md) | Any CLI task, show commands, system config |
| AP management | [references/ap-management.md](references/ap-management.md) | Adding/removing APs, AP modes, CAPWAP, roaming |
| Auth & access control | [references/auth-access.md](references/auth-access.md) | SSIDs, captive portal, RADIUS, MAC auth, bandwidth limits |
| VLAN configuration | [references/vlan-config.md](references/vlan-config.md) | VLAN creation, WLAN-to-VLAN mapping, guest isolation |
| Troubleshooting | [references/troubleshooting.md](references/troubleshooting.md) | AP offline, auth failures, slow speeds, log review |

## Common Workflows

### Add a new AP
See [references/ap-management.md](references/ap-management.md) → "Adopting an AP"

### Set up a guest SSID with captive portal
See [references/auth-access.md](references/auth-access.md) → "Captive Portal / Web Authentication"

### Limit bandwidth per user
See [references/auth-access.md](references/auth-access.md) → "Per-User Bandwidth Control"

### Create a new SSID mapped to a VLAN
See [references/vlan-config.md](references/vlan-config.md) → "WLAN-to-VLAN Mapping"

### Firmware update
See [references/cli-commands.md](references/cli-commands.md) → "Firmware Upgrade"

### Review logs / check for issues
See [references/troubleshooting.md](references/troubleshooting.md) → "Log Review"

## Management Interfaces

- **Web UI:** Primary interface for day-to-day AP and user management
- **Airware Cloud:** FS centralized cloud NMS — zero-touch provisioning, bulk config, AI fault detection, real-time telemetry
- **SNMP v3:** Trap alerts for AP join failures and system events
- **Console:** Recovery access and initial setup; always available even if network is misconfigured
