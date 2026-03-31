---
name: ta1910-4gvc-w-expert
description: "Expert guidance for the FS TA1910-4GVC-W XPON (GPON+EPON) fiber home gateway deployed at Pecan Grove RV Park cabins and office/house (16 units, one per structure). Use when the user needs to register an ONU on the OLT3610, configure cabin WiFi or SSID, set up WAN/LAN/DHCP, troubleshoot PON connectivity or fiber signal loss, configure VoIP/POTS ports, perform a factory reset, or manage any aspect of the per-cabin fiber gateway. Covers OLT3610 SN binding, ONU web UI, OMCI/TR-069 management, and per-cabin network isolation."
---

# FS TA1910-4GVC-W Expert

**Device:** FS TA1910-4GVC-W — XPON (GPON+EPON) HGU ONU / Home Gateway
**Deployment:** Pecan Grove RV Park — 16 units (one per cabin + office/house)
**OLT upstream:** FS OLT3610-08GP4S (see `olt3610-expert` skill for OLT-side commands)
**Manufacturer docs:** https://www.fs.com/products/143750.html

## Key Specs

| Item | Value |
|---|---|
| PON standard | XPON — auto-detects GPON (ITU-T G.984) or EPON (IEEE 802.3ah) |
| PON downstream | 2.5 Gbps (GPON) / 1.25 Gbps (EPON) |
| PON upstream | 1.25 Gbps (GPON) / 1.25 Gbps (EPON) |
| LAN ports | 4× GE RJ45 |
| POTS ports | 2× FXS RJ11 (VoIP) |
| RF/CATV | 1× coaxial (passive RF pass-through) |
| USB | 1× USB |
| WiFi standard | 802.11ac (WiFi 5) dual-band |
| WiFi speeds | 300 Mbps @ 2.4 GHz + 867 Mbps @ 5 GHz = 1200 Mbps |
| Antennas | 4× external dual-band |
| Power | Max 14W; AC 100–240V → DC 12V/1.5A adapter |
| Management | Web GUI, CLI, SNMP, TR-069, Telnet, OMCI (from OLT) |

## Default Access

| Method | Details |
|---|---|
| **Web UI** | `http://192.168.123.1` — username `admin` / password `super&123` |
| **OLT OMCI** | Managed remotely by OLT3610 via OMCI protocol after registration |
| **TR-069** | ACS URL configurable; allows remote provisioning from OLT/ACS server |

> **Security:** Change default web UI password on every cabin unit at first login.

## Reference Files

| Topic | File | When to read |
|---|---|---|
| Hardware & LEDs | [references/hardware.md](references/hardware.md) | Physical layout, LED status, ports, power, placement |
| OLT registration | [references/olt-registration.md](references/olt-registration.md) | Binding ONU SN on OLT3610, VLAN setup, OMCI provisioning |
| ONU configuration | [references/configuration.md](references/configuration.md) | Web UI: WAN, LAN, WiFi SSID, DHCP, VoIP, firewall |
| Cabin deployment | [references/cabin-deployment.md](references/cabin-deployment.md) | 16-unit layout, per-cabin isolation, SSID/VLAN strategy, IP plan |
| Troubleshooting | [references/troubleshooting.md](references/troubleshooting.md) | No PON light, no internet, WiFi issues, factory reset |

## Common Workflows

### Register a new cabin ONU on OLT3610
1. Find ONU serial number (label on bottom/back of unit)
2. See [references/olt-registration.md](references/olt-registration.md) → "SN Binding on OLT3610"

### Configure cabin WiFi SSID and password
See [references/configuration.md](references/configuration.md) → "WLAN Configuration"

### Set up ONU WAN connection (bridge vs routing mode)
See [references/configuration.md](references/configuration.md) → "WAN Configuration"

### Provision all 16 cabins consistently
See [references/cabin-deployment.md](references/cabin-deployment.md) → "Provisioning Checklist"

### Troubleshoot cabin with no internet
See [references/troubleshooting.md](references/troubleshooting.md) → "No Internet / WAN Down"

### Factory reset a cabin ONU
See [references/troubleshooting.md](references/troubleshooting.md) → "Factory Reset"

### Set up POTS/VoIP on cabin phone jacks
See [references/configuration.md](references/configuration.md) → "VoIP Configuration"
