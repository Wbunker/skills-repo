# AP-N505 Hardware & Installation Reference

## Physical Overview

| Item | Value |
|---|---|
| Dimensions | 220 × 220 × 49 mm (8.66" × 8.66" × 1.92") |
| Enclosure | Plastic, indoor-rated (not IP-rated — indoor use only) |
| Operating temp | −10°C to +50°C |
| Storage temp | −40°C to +70°C |
| Humidity | 5%–95% non-condensing |

## Ports & Interfaces

| Port | Description |
|---|---|
| RJ45 (ETH0) | 10/100/1000M — primary uplink; **PoE in (802.3af, 12.95W)** |
| SFP (ETH1) | 2.5G — optional high-speed uplink (fiber or DAC) |
| Console | RJ45 — 115200 baud, 8N1, no flow control |
| Reset | Recessed button — hold 10 s to factory reset |

> **PoE note:** AP-N505 uses **802.3af** (standard PoE, up to 15.4W). It does NOT require 802.3at (PoE+). Any 802.3af-capable switch port or the AC-1004's built-in PoE ports will power it.

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

> During firmware upgrade, System LED blinks. **Do not cut power** until solid green returns.

## Ceiling Mounting

The AP-N505 ships with a mounting bracket that clips to standard drop-ceiling grid systems or screws to solid ceilings.

### Supported Mount Types
- **T-bar (suspended ceiling grid)** — most common in pavilions; clips directly onto T-bar rails
- **Keel (triangular suspended ceiling)** — bracket adapter required
- **Beam / solid ceiling** — screw-mount via bracket into ceiling substrate
- **Threaded rod** — suspends AP below ceiling using rod through bracket center hole

### T-Bar Ceiling Installation (most common at Pavilion)
1. Hold mounting bracket against T-bar grid at desired position
2. Rotate bracket to lock onto T-bar rails (quarter-turn, click to engage)
3. Route Ethernet cable through ceiling plenum to bracket cable entry
4. Align AP buckle holes with bracket studs; push and rotate to lock AP onto bracket
5. Confirm AP is seated — gentle tug should not release it

### Solid Ceiling / Beam Installation
1. Hold bracket against ceiling at desired location
2. Mark 4 mounting hole positions — center-to-center: 53 mm (2.09")
3. Drill 4× 6 mm holes; insert anchors if drilling into drywall/plaster
4. Secure bracket with M4 screws
5. Attach AP to bracket (push and rotate to lock)

### Orientation
- Mount AP with flat face toward the floor (antennas point down)
- Keep AP horizontal — tilted mounting reduces omni-pattern effectiveness
- Avoid mounting inside ceiling tiles or above ceiling panels — signal will be blocked

### Cable Management
- Indoor Cat5e or Cat6 (non-shielded) is fine for plenum runs
- Max Ethernet run: 100 m (including patch cables)
- Use plenum-rated cable inside ceiling space (fire code)
- Zip-tie cable to T-bar grid to prevent pull strain on RJ45 port

## PoE Budget Planning (Pavilion — 5 APs)

| Item | Value |
|---|---|
| AP power draw (max) | 12.95 W |
| AP power draw (typical) | ~10–12 W |
| Total max (5 APs) | ~65 W |
| Total typical (5 APs) | ~55 W |

5 APs draw well within the AC-1004's 4× PoE port budget (60W each). If all 5 APs connect through AC-1004 PoE ports, no additional PoE switch is needed.

> AC-1004 has 4× PoE ports — if all 5 pavilion APs connect here, add a small 802.3af PoE switch for the 5th AP, or use a midspan injector.

## Factory Reset

**Soft reset (web UI):** System → Reboot
**Factory reset (hardware):** Hold recessed reset button 10 seconds while powered — all settings erased, returns to `admin`/`admin` and `192.168.1.1`

## Official Documentation
- Quick Start Guide (V1): https://resource.fs.com/mall/file/user_manual/ap-n505-access-point-quick-start-guide.pdf
- Quick Start Guide (V2): https://resource.fs.com/mall/doc/20231130161503hr58jm.pdf
- Datasheet: https://img-en.fs.com/file/datasheet/ap-n505-access-point-datasheet.pdf
