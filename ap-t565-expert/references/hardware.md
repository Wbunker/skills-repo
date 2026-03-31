# AP-T565 Hardware & Installation Reference

## Physical Overview

| Item | Value |
|---|---|
| Dimensions | ~200 × 200 × 60 mm (cylindrical/dome form factor) |
| Weight | ~1.1 kg |
| Enclosure | Die-cast aluminum, IP68 rated |
| Operating temp | −40°C to +70°C |
| Storage temp | −40°C to +85°C |
| Humidity | 5%–95% non-condensing |
| Surge protection | Industrial-grade on all ports (Ethernet + SFP) |

## Ports & Interfaces

| Port | Description |
|---|---|
| RJ45 (ETH0) | 10/100/1000M — primary uplink; **PoE in (802.3at)** |
| SFP (ETH1) | 1G fiber uplink (optional redundancy or fiber-fed sites) |
| Console | RJ45 — 115200 baud, 8N1, no flow control |
| Reset | Recessed button — hold 10 s to factory reset |

> **PoE requirement:** 802.3at (PoE+) minimum — 25.5W max draw. Do NOT use 802.3af (15.4W) — AP may fail to boot or disable radios to conserve power.

## LED Indicators

| LED | Color / State | Meaning |
|---|---|---|
| System | Green solid | Normal operation |
| System | Green blinking | Booting or firmware upgrade in progress |
| System | Red solid | Hardware fault |
| System | Off | No power |
| 2.4G radio | Green solid | Radio active |
| 2.4G radio | Off | Radio disabled |
| 5G radio | Green solid | Radio active |
| 5G radio | Off | Radio disabled |
| ETH0 | Green solid | Link up (1000M) |
| ETH0 | Amber solid | Link up (100M) |
| ETH0 | Blinking | Traffic activity |
| ETH0 | Off | No link / no PoE |

> LED behavior during firmware upgrade: System LED blinks rapidly. **Do not reboot or cut power** until solid green returns.

## Pole Mounting

### Kit Contents
- Mounting bracket (hose clamp style or U-bolt, depending on kit version)
- Stainless steel band clamps × 2
- M6 bolts, washers, and lock nuts
- Weatherproof silicone tape for cable entry

### Pole Diameter Compatibility
- Standard: 1.5" to 4" (38–100mm) diameter poles
- Confirm bracket kit at time of order — AP-T565 ships without mount hardware

### Mounting Procedure
1. Attach mounting bracket to pole using stainless steel band clamps; tighten firmly
2. Orient AP so ETH0 port faces down (cable drip loop drainage)
3. Secure AP to bracket with M6 bolts — torque to 3–4 N·m
4. Route Ethernet cable through a weatherproof conduit or use outdoor-rated Cat6 cable
5. Wrap cable entry point with self-fusing silicone tape after connectorizing
6. Apply weatherproof RJ45 boot/cover over the Ethernet port connection

### Height & Orientation
- Recommended pole height: 4–6 m (13–20 ft) above ground — clears RV rooflines, reduces multipath
- Mount vertically with radome facing up (omni antennas polarized vertically)
- Avoid mounting directly under metallic overhangs (corrugated roofs cause reflection/shadowing)

### Cable Routing
- Use shielded outdoor Cat6 (UV-rated, gel-filled preferred) for runs over 30 m
- Max Ethernet run: 100 m (including patch cables)
- Use conduit at pole base to protect cable against mowers, foot traffic

## PoE Budget Planning (Pecan Grove — 27 APs)

| Item | Value |
|---|---|
| AP power draw (max) | 25.5 W |
| AP power draw (typical) | ~18–22 W |
| Total max (27 APs) | ~688 W |
| Total typical (27 APs) | ~500–600 W |

Ensure the PoE switch or midspan injectors provide at least **30W per port** budget. AC-1004 provides 4× PoE ports (60W each) — supplemental PoE switches are required for 27-unit deployments.

## Factory Reset

**Soft reset (web UI):** System → Reboot
**Factory reset (hardware):** Hold recessed reset button for 10 seconds while powered — all settings erased, returns to `admin`/`admin` and `192.168.1.1`

## Quick Start Guide (FS Official)
URL: https://img-en.fs.com/file/user_manual/ap-t565-and-ap-t567-access-point-quick-start-guide.pdf
