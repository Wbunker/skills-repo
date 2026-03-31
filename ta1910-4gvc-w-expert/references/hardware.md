# TA1910-4GVC-W Hardware Reference

## Physical Overview

| Item | Value |
|---|---|
| Form factor | Desktop/shelf-mount (horizontal, feet included) |
| Power supply | External AC adapter: 100–240V AC input → 12V DC/1.5A output |
| Max power draw | 14W |
| Antennas | 4× detachable external dual-band (screw-on RP-SMA) |

## Ports & Interfaces (Front/Back Panel)

| Port | Label | Description |
|---|---|---|
| PON | PON / FIBER | SC/APC or SC/UPC optical connector — fiber from OLT splitter |
| LAN 1–4 | LAN1–LAN4 | 10/100/1000M RJ45 — connects cabin devices, switch, or TV box |
| POTS 1–2 | TEL1, TEL2 | FXS RJ11 — analog phone jacks for VoIP |
| RF | RF / CATV | F-type coaxial — passive RF pass-through for cable TV |
| USB | USB | USB-A — storage or printer sharing |
| Reset | RESET | Recessed button — hold 10 s for factory reset |
| Power | DC IN | 12V DC barrel jack from included adapter |

> **Fiber connector type:** Confirm SC/APC (green) vs SC/UPC (blue) before connecting — Pecan Grove uses SC/APC on drop cables. Mixing types causes insertion loss.

## LED Indicators

| LED | State | Meaning |
|---|---|---|
| PWR (Power) | Green solid | Powered on normally |
| PWR | Off | No power |
| PON | Green solid | ONU registered and activated on OLT |
| PON | Blinking/flickering | ONU attempting to register (ranging in progress) |
| PON | Off | ONU not activated / no PON signal detected |
| LOS (Loss of Signal) | Red solid | Optical signal below threshold — fiber/connector issue |
| LOS | Off | Optical signal received normally |
| LAN 1–4 | Green solid | Link up (1G) |
| LAN 1–4 | Amber solid | Link up (100M) |
| LAN 1–4 | Blinking | Traffic activity |
| LAN 1–4 | Off | No link |
| WiFi | Green solid | WiFi radio active |
| WiFi | Blinking | WiFi traffic |
| WiFi | Off | WiFi disabled |
| USB | Green solid | USB device connected |

### Reading LED State at a Glance

| PON LED | LOS LED | Meaning |
|---|---|---|
| Green solid | Off | Healthy — ONU registered, fiber good |
| Blinking | Off | Registering — wait up to 3 min before troubleshooting |
| Off | Off | No fiber signal at all, or ONU not bound on OLT |
| Off | Red | Fiber connected but signal too weak (dirty connector, bad splice, excessive bend) |
| Blinking | Red | Signal present but marginal — check connector cleanliness |

## WiFi Specifications

| Parameter | 2.4 GHz | 5 GHz |
|---|---|---|
| Standard | 802.11b/g/n (WiFi 4) | 802.11a/n/ac (WiFi 5) |
| Max rate | 300 Mbps (2×2 MIMO) | 867 Mbps (2×2 MIMO) |
| Channel widths | 20/40 MHz | 20/40/80 MHz |
| Antennas | 2 of the 4 external | 2 of the 4 external |

> **Note:** The TA1910-4GVC-W is WiFi 4/5 (802.11n/ac), NOT WiFi 6. This is sufficient for per-cabin use but differs from the campus APs (AP-T565/AP-N505) which are WiFi 6.

## Physical Placement in Cabin

- Place on a shelf or wall-bracket mount, not enclosed in a cabinet (ventilation needed)
- Position antennas vertically for best omnidirectional coverage
- Keep away from microwaves, cordless phones, and other 2.4G sources
- Fiber pigtail from wall SC/APC port → PON port on ONU (SC/APC to SC/APC patch cord)
- Suggested central location: utility closet, shelf, or entertainment center in cabin

## Factory Reset

**Hardware:** Hold recessed RESET button for 10 seconds while powered on. All settings return to factory defaults (192.168.123.1, admin/super&123).

**Web UI:** Advanced → System Management → Factory Reset → Confirm

> After factory reset, ONU must re-register on OLT3610 (SN binding persists on OLT side — ONU will re-register automatically if SN was previously bound and OLT config is intact).

## Quick Start Guide (FS Official)
ManualsLib: https://www.manualslib.com/manual/2831861/Fs-Ta1910-4gvc-W.html
Product page: https://www.fs.com/products/143750.html
