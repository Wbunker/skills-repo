---
name: gpon-sfp-onu-stick-expert
description: "Expert guidance for FS GPON SFP ONU Stick modules (GPON-ONU-34-20BI / GPON-SFP-ONT-MAC-I) deployed at Pecan Grove RV Park (31 units). These sticks plug directly into SFP ports on switches, APs, routers, and OLT uplink ports to provide GPON fiber connectivity without a standalone ONU chassis. Use when the user needs to register a stick on the OLT3610, configure GPON SN or PLOAM password via SSH, set up WAN/bridge mode, troubleshoot PON registration failure, adjust SFP lane speed (1G/2.5G), change management IP, or perform firmware recovery on any of the 31 ONU sticks."
---

# GPON SFP ONU Stick Expert

**Devices:** FS GPON-ONU-34-20BI / GPON-SFP-ONT-MAC-I
**Form factor:** SFP (plugs directly into any SFP/SFP+ port — no separate ONU chassis needed)
**Deployment:** Pecan Grove RV Park — 31 units in device uplink SFP ports and OLT infrastructure ports
**OLT upstream:** FS OLT3610-08GP4S (see `olt3610-expert` skill for OLT-side commands)
**Manufacturer docs:** https://www.fs.com/products/133619.html

## What This Device Does

The ONU stick replaces a full ONU chassis by integrating the GPON MAC directly into an SFP module. Insert into any SFP/SFP+ port → connect SC/APC fiber pigtail → device joins the GPON PON network. The host device's SFP port acts as the WAN/uplink interface.

## Key Specs

| Item | Value |
|---|---|
| GPON standard | ITU-T G.984, Class B+ |
| Upstream rate | 1.244 Gbps (1310 nm TX) |
| Downstream rate | 2.488 Gbps (1490 nm RX) |
| Link budget | 28 dB |
| Max reach | 20 km |
| Connector | SC/APC simplex (SMF) |
| SFP host interface | SGMII (1G) or HSGMII (2.5G) — configurable |
| Operating temp | −40°C to +85°C (industrial) |
| Power | Drawn from host SFP slot — no external supply |
| Chipset | Lantiq PEB98035 (MIPS 34Kc, 400 MHz) |
| Memory | 16 MB flash / 64 MB RAM |
| OS | OpenWRT 14.07_ltq (Linux 3.10.49) |
| DOM/DDM | Yes — temperature, voltage, Tx/Rx power readable |

## Default Access

| Method | Details |
|---|---|
| **SSH** | `ssh ONTUSER@192.168.1.10` — password `7sp!lwUBz1` |
| **Serial console** | 115200 baud, 8-N-1 via SFP pins (2=TX, 7=RX, 14=GND) — requires breakout adapter |
| **Management IP** | 192.168.1.10 (changeable via `fw_setenv ipaddr`) |

> Access the stick via SSH from a host connected to the same device the stick is installed in. The stick's management interface appears as a local network interface on the host.

## Reference Files

| Topic | File | When to read |
|---|---|---|
| Hardware & optical specs | [references/hardware.md](references/hardware.md) | Physical specs, DOM values, SFP interface modes, connector details |
| Stick CLI configuration | [references/stick-configuration.md](references/stick-configuration.md) | SSH commands: SN, PLOAM, LOID, IP, MAC, speed mode, OMCI tuning |
| OLT registration | [references/olt-registration.md](references/olt-registration.md) | Binding stick SN on OLT3610, VLAN service setup, verifying online |
| Deployment | [references/deployment.md](references/deployment.md) | 31-unit layout at Pecan Grove, device types hosting sticks, use cases |
| Troubleshooting | [references/troubleshooting.md](references/troubleshooting.md) | No PON, TX fault, speed mismatch, SSH unreachable, firmware recovery |

## Common Workflows

### Register a new ONU stick on OLT3610
1. Find stick SN: `ssh ONTUSER@192.168.1.10` → `sfp_i2c -i8` (reads current SN)
2. Bind SN on OLT3610: see [references/olt-registration.md](references/olt-registration.md) → "SN Binding"

### Set GPON Serial Number on stick
See [references/stick-configuration.md](references/stick-configuration.md) → "GPON Serial Number"

### Set PLOAM password to match OLT expectation
See [references/stick-configuration.md](references/stick-configuration.md) → "PLOAM Password"

### Change stick management IP (avoid 192.168.1.x conflict)
See [references/stick-configuration.md](references/stick-configuration.md) → "Management IP"

### Switch SFP interface to 2.5G (HSGMII) mode
See [references/stick-configuration.md](references/stick-configuration.md) → "SFP Host Interface Speed"

### Stick inserted but no PON light / won't register
See [references/troubleshooting.md](references/troubleshooting.md) → "No PON Registration"

### Recover bricked or unresponsive stick
See [references/troubleshooting.md](references/troubleshooting.md) → "Firmware Recovery"
