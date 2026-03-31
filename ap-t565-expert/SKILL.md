---
name: ap-t565-expert
description: "Expert guidance for the FS AP-T565 Wi-Fi 6 outdoor access point deployed at Pecan Grove RV Park (27 units, pole-mounted). Use when the user needs to configure, deploy, troubleshoot, or maintain AP-T565 units — including SSID setup, radio/channel configuration, roaming, PoE, VLAN mapping, controller adoption, standalone management, or physical installation. Covers Fit (AC-1004 controller), Standalone (web UI/CLI), and Airware cloud management modes."
---

# FS AP-T565 Expert

**Device:** FS AP-T565 — Wi-Fi 6 (802.11ax) IP68 Outdoor Access Point
**Deployment:** Pecan Grove RV Park — 27 units, pole-mounted across RV sites
**Controller:** FS AC-1004 (see `ac1004-expert` skill for controller-side config)
**Manufacturer docs:** https://www.fs.com/products/149657.html

## Key Specs

| Item | Value |
|---|---|
| Standard | 802.11ax (Wi-Fi 6) + 802.11a/b/g/n/ac |
| Bands | 2.4 GHz + 5 GHz (dual concurrent) |
| Radio config | 2×2 MU-MIMO, dual radio |
| Max throughput | 2400 Mbps (574 Mbps @ 2.4G + 1201 Mbps @ 5G) |
| TX power | 28 dBm |
| Antenna | Built-in omni — 2.4G: 2×4 dBi, 5G: 2×6 dBi |
| Coverage radius | ~100 m |
| Max VAPs | 32 SSIDs per AP |
| Wired ports | 1× GE RJ45 (PoE in) + 1× 1G SFP + 1× RJ45 console |
| PoE | 802.3at (PoE+, up to 30W) |
| Protection | IP68, industrial surge protection on all ports |
| Operating temp | −40°C to +70°C |
| Modes | Fat (standalone), Fit (controller/CAPWAP), Cloud (Airware) |

## Management Access

| Method | Details |
|---|---|
| **Fit mode (AC-1004)** | AP adopts to controller automatically via CAPWAP; configure via AC-1004 web UI |
| **Standalone web UI** | `http://192.168.1.1` — default `admin` / `admin` (change on first login) |
| **CLI** | Console: 115200 baud, 8N1; SSH/Telnet to AP management IP |
| **Airware cloud** | https://airware-login.fs.com — zero-touch provisioning, bulk config |

> At Pecan Grove, APs run in **Fit mode** under the AC-1004 controller. Use standalone access only for initial setup or recovery.

## Reference Files

| Topic | File | When to read |
|---|---|---|
| Hardware & installation | [references/hardware.md](references/hardware.md) | Physical setup, LED status, pole mounting, PoE wiring |
| RV park deployment | [references/rv-park-deployment.md](references/rv-park-deployment.md) | 27-unit layout, channel plan, coverage design, site config |
| Configuration (standalone) | [references/configuration.md](references/configuration.md) | Standalone SSID, radio, VLAN, roaming, security settings |
| CLI reference | [references/cli-reference.md](references/cli-reference.md) | CLI commands for standalone/fat mode diagnostics |
| Troubleshooting | [references/troubleshooting.md](references/troubleshooting.md) | AP offline, poor signal, auth failures, PoE issues |

## Common Workflows

### Adopt a new AP into AC-1004 (Fit mode)
1. Connect AP's RJ45 port to a PoE switch port on the same network as AC-1004
2. AP boots and broadcasts discovery via DHCP option 43 or multicast
3. On AC-1004 web UI → **AP Management** → check **Unmanaged APs** list
4. Approve/adopt the AP — it downloads config and joins the controller
5. See [references/rv-park-deployment.md](references/rv-park-deployment.md) → "Adopting APs into AC-1004"

### Check AP status and connected clients
See [references/cli-reference.md](references/cli-reference.md) → "Show Commands" (standalone), or use AC-1004 dashboard for controller-managed APs.

### Configure SSIDs, VLANs, or roaming (Fit mode)
All SSID/VLAN/roaming config in Fit mode is done on the AC-1004, not the individual AP.
See `ac1004-expert` → references/ap-management.md and references/vlan-config.md.

### Configure an AP in standalone mode
See [references/configuration.md](references/configuration.md).

### Troubleshoot a dead or offline AP
See [references/troubleshooting.md](references/troubleshooting.md) → "AP Not Coming Online".

### Physical installation (pole mount)
See [references/hardware.md](references/hardware.md) → "Pole Mounting".

### Channel planning for 27-unit deployment
See [references/rv-park-deployment.md](references/rv-park-deployment.md) → "Channel Plan".
