# GPON SFP ONU Stick Deployment — Pecan Grove (31 Units)

## Deployment Overview

| Item | Value |
|---|---|
| Total sticks | 31 units |
| Models | GPON-ONU-34-20BI / GPON-SFP-ONT-MAC-I (industrial) |
| OLT upstream | FS OLT3610-08GP4S (8 PON ports) |
| Purpose | Provide GPON fiber connectivity directly to devices via their SFP ports |
| No separate ONU chassis | The stick IS the ONU — inserted into the host device's SFP slot |

## What "Plugs Into Device Uplink Ports" Means

Traditional FTTH: `OLT → fiber → standalone ONU box → Ethernet → device`

With ONU sticks at Pecan Grove: `OLT → fiber → SFP stick (in device) → device SFP port`

The stick eliminates the standalone ONU box entirely. Any network device with an SFP/SFP+ uplink port can connect directly to the GPON fiber network.

## Typical Host Device Types at Pecan Grove

| Host device type | Connection | Why stick instead of ONU box |
|---|---|---|
| Network switches (with SFP uplink) | Stick in SFP uplink port | Switch gets fiber WAN directly; no ONU box needed |
| OLT3610 SFP uplink ports | Stick in OLT uplink SFP | Uplinks OLT3610 to backbone GPON network |
| Routers/gateways (with SFP) | Stick in WAN SFP | Router gets GPON WAN without a separate ONU |
| Outdoor APs (if SFP-equipped) | Stick in SFP port | AP gets direct fiber uplink at pole |

## PON Port Allocation (OLT3610)

OLT3610 has 8 PON ports. With 31 ONU sticks plus the 16 cabin TA1910-4GVC-W ONUs (total 47 ONUs), distribution across PON ports:

```
PON port 0 → 1:32 splitter → up to 32 ONU sticks (zone A infrastructure)
PON port 1 → 1:32 splitter → up to 32 ONU sticks (zone B infrastructure)
PON ports 2–3 → TA1910-4GVC-W cabin ONUs (16 units, see ta1910-4gvc-w-expert)
PON ports 4–7 → spare / expansion
```

> Adjust based on actual fiber plant layout. One 1:32 splitter per PON port can serve all 31 sticks from a single OLT port.

## Management IP Plan

All sticks default to `192.168.1.10`. To manage sticks individually, assign unique IPs:

```
Stick 01: 192.168.1.11
Stick 02: 192.168.1.12
...
Stick 31: 192.168.1.41
```

Set per stick: `fw_setenv ipaddr 192.168.1.XX && fw_setenv gatewayip 192.168.1.1`

Each stick is only reachable from its host device's local network. SSH access requires being on the same device or VLAN as the stick.

## Naming Convention

Track sticks in a deployment log with:
| Field | Example |
|---|---|
| Stick ID | STICK-01 through STICK-31 |
| GPON SN | 48575443AABBCCDD |
| Host device | SW-POOL-01 (switch at pool building) |
| Host SFP slot | SFP uplink port 1 |
| PON port on OLT | gpon 0/0, ONU-ID 1 |
| Mgmt IP | 192.168.1.11 |

## SFP Compatibility Notes

The ONU stick is SFP form factor — it fits standard 1G SFP cages. For 2.5G/SFP+ hosts:
- Stick fits physically in SFP+ slots (backward compatible)
- Set `sgmii_mode 5` (HSGMII) on the stick for 2.5G host interfaces
- Default `sgmii_mode 3` (1G) for standard GE SFP host ports

## Fiber Infrastructure Requirements

Each stick needs:
1. An SC/APC patch cord from the stick to the nearest wall outlet or fiber panel
2. The wall outlet connects to the PON distribution fiber (via splitter to OLT3610)
3. Fiber connector at stick must be SC/APC (green) — NOT SC/UPC (blue)

**Cable routing:**
- Stick protrudes ~60mm from SFP cage — allow bend radius ≥ 30mm for SC/APC pigtail
- Use a right-angle SC/APC adapter if SFP cage is in a tight enclosure
- Protect fiber near the stick from physical stress (zip tie pigtail to chassis after 10cm of free length)

## Hot-Plug Capability

ONU sticks support hot-plugging — insertion and removal without powering down the host device. However:
- After insertion, allow ~60 seconds for GPON ranging and registration
- After removal, OLT detects ONU offline within ~30 seconds
- Re-insertion triggers automatic re-registration (no OLT changes needed if SN binding persists)

## Deployment Checklist (Per Stick)

- [ ] Record stick GPON SN from label or `sfp_i2c -i8`
- [ ] Insert stick into host device SFP port
- [ ] Connect SC/APC patch cord from stick to PON fiber distribution
- [ ] Verify host device shows SFP link up
- [ ] SSH to stick: `ssh ONTUSER@192.168.1.10`
- [ ] Set unique management IP: `fw_setenv ipaddr 192.168.1.XX`
- [ ] Confirm/set SN if needed: `sfp_i2c -i8`
- [ ] Bind SN on OLT3610 (see olt-registration.md)
- [ ] Verify PON registration: `show gpon onu` on OLT3610
- [ ] Configure service VLAN on OLT for this ONU-ID
- [ ] Verify host device has GPON uplink connectivity (ping through fiber)
- [ ] Record ONU-ID, management IP, and host device in deployment log
