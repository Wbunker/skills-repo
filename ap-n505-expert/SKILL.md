---
name: ap-n505-expert
description: "Expert guidance for the FS AP-N505 Wi-Fi 6 indoor access point deployed at Pecan Grove RV Park Pavilion (5 units, ceiling-mounted). Use when the user needs to configure, deploy, troubleshoot, or maintain AP-N505 units — including SSID setup, radio/channel/160MHz configuration, roaming, PoE, VLAN mapping, controller adoption, standalone management, or physical ceiling installation. Covers Fit (AC-1004 controller), Standalone (web UI/CLI), and Airware cloud management modes."
---

# FS AP-N505 Expert

**Device:** FS AP-N505 — Wi-Fi 6 (802.11ax) Indoor Access Point
**Deployment:** Pecan Grove RV Park Pavilion — 5 units, ceiling-mounted
**Controller:** FS AC-1004 (see `ac1004-expert` skill for controller-side config)
**Manufacturer docs:** https://www.fs.com/products/149656.html

## Key Specs

| Item | Value |
|---|---|
| Standard | 802.11ax (Wi-Fi 6) + 802.11a/b/g/n/ac |
| Bands | 2.4 GHz + 5 GHz (dual concurrent) |
| Radio config | 2×2 MU-MIMO, dual radio |
| Max throughput | 3000 Mbps (574 Mbps @ 2.4G + 2402 Mbps @ 5G w/ 160 MHz) |
| TX power | 20 dBm (adjustable) |
| Antenna | Built-in omni — 2.4G: 2×3 dBi, 5G: 2×3 dBi |
| Recommended clients | 64 concurrent per AP |
| Wired ports | 1× GE RJ45 (PoE in) + 1× 2.5G SFP + 1× RJ45 console |
| PoE | **802.3af** (12.95W) — standard PoE sufficient |
| Dimensions | 220 × 220 × 49 mm |
| Operating temp | −10°C to +50°C |
| Mounting | T-bar ceiling, keel ceiling, beam, threaded rod |
| Modes | Fat (standalone), Fit (controller/CAPWAP), Cloud (Airware) |

> **PoE note:** AP-N505 requires only 802.3af (15.4W budget) — unlike the outdoor AP-T565 (which needs 802.3at/30W). Standard PoE switches and the AC-1004's built-in PoE ports are sufficient.

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
| Hardware & installation | [references/hardware.md](references/hardware.md) | Physical setup, LED status, ceiling mounting (T-bar/keel), PoE wiring |
| Pavilion deployment | [references/pavilion-deployment.md](references/pavilion-deployment.md) | 5-unit indoor layout, channel plan, 160MHz config, coverage design |
| Configuration (standalone) | [references/configuration.md](references/configuration.md) | Standalone SSID, radio, VLAN, roaming, 160MHz, WPA3, QoS |
| CLI reference | [references/cli-reference.md](references/cli-reference.md) | CLI commands for standalone/fat mode diagnostics |
| Troubleshooting | [references/troubleshooting.md](references/troubleshooting.md) | AP offline, poor signal, auth failures, PoE issues |

## Common Workflows

### Adopt a new AP into AC-1004 (Fit mode)
1. Connect AP's RJ45 port to any 802.3af PoE switch port on same network as AC-1004
2. AP boots and discovers controller via DHCP option 43 or multicast
3. On AC-1004 web UI → **AP Management** → **Unmanaged APs** tab
4. Click **Adopt** — AP downloads config profile and reboots into Fit mode
5. See [references/pavilion-deployment.md](references/pavilion-deployment.md) → "Adopting APs into AC-1004"

### Configure SSIDs, VLANs, or roaming (Fit mode)
All SSID/VLAN/roaming config in Fit mode is done on the AC-1004, not the individual AP.
See `ac1004-expert` → references/ap-management.md and references/vlan-config.md.

### Enable 160 MHz for maximum 5 GHz throughput
See [references/pavilion-deployment.md](references/pavilion-deployment.md) → "160 MHz Channel Configuration".

### Configure an AP in standalone mode
See [references/configuration.md](references/configuration.md).

### Troubleshoot a dead or offline AP
See [references/troubleshooting.md](references/troubleshooting.md) → "AP Not Coming Online".

### Physical ceiling installation
See [references/hardware.md](references/hardware.md) → "Ceiling Mounting".
