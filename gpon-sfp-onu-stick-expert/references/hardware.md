# GPON SFP ONU Stick Hardware Reference

## Physical & Form Factor

| Item | Value |
|---|---|
| Form factor | SFP (standard SFP cage — fits SFP and SFP+ slots) |
| Connector | SC/APC simplex (green ferrule) |
| Fiber type | SMF (Single-Mode Fiber) only |
| Length | ~60mm extended (longer than a standard SFP transceiver — "stick" protrudes) |
| Weight | ~20g |
| Power | Drawn entirely from SFP host slot (3.3V, ~1W) — no external supply |

> **Clearance warning:** The stick extends further than a normal SFP module. Verify rack/enclosure has clearance for the protruding body plus the SC/APC fiber pigtail.

## Optical Specifications

| Parameter | Value |
|---|---|
| TX wavelength | 1310 nm (upstream to OLT) |
| RX wavelength | 1490 nm (downstream from OLT) |
| Upstream rate | 1.244 Gbps |
| Downstream rate | 2.488 Gbps |
| GPON class | B+ (28 dB link budget) |
| Max transmission distance | 20 km |
| TX power range | +0.5 to +5 dBm |
| RX sensitivity | −28 dBm (min) |
| RX overload | −8 dBm (max) |

**Healthy operational range:**
- RX power (from OLT): −8 to −28 dBm
- Below −28 dBm: signal too weak (distance, dirty connector, excessive splice loss)
- Above −8 dBm: signal too strong (unexpected; would require no splitter in path)

## SFP Host Interface

The stick presents a copper/electrical interface to the host device's SFP slot, configurable for two speed modes:

| Mode | Speed | `sgmii_mode` | Use case |
|---|---|---|---|
| SGMII | 1G | 3 or 4 | Standard GE host ports |
| HSGMII | 2.5G | 5 | 2.5G/multi-gig host ports |

Check current mode: `onu lanpsg 0`
- Returns `3` = 1G with auto-negotiation
- Returns `4` = 1G without auto-negotiation
- Returns `5` = 2.5G HSGMII

Set mode: `fw_setenv sgmii_mode 5` (reboot required)

> Most switches at Pecan Grove use standard 1G SFP ports — `sgmii_mode 3` or `4` is correct. Only use HSGMII (5) if the host device has a 2.5G/multi-gig SFP+ port.

## DOM / Digital Diagnostic Monitoring

The stick supports DOM (DDMI). Read diagnostics over SSH:

```bash
# Read all DOM values
sfp_i2c -r

# Individual DOM fields (read-only):
# Temperature, Vcc, bias current, TX power, RX power
```

Typical healthy DOM values:
- Temperature: 40–70°C (varies with ambient)
- Vcc: ~3.3V ±5%
- TX power: +0.5 to +5.0 dBm
- RX power: −8 to −28 dBm (depends on fiber plant loss)

## Hardware Internals

| Component | Value |
|---|---|
| Chipset | Lantiq (Intel) PEB98035 |
| CPU | MIPS 34Kc interAptiv @ 400 MHz |
| Flash | 16 MB (dual-image: ~7.4 MB active + ~8 MB standby) |
| RAM | 64 MB |
| Bootloader | U-Boot 2011.12-lantiq-gpon-1.2.24 |
| OS | OpenWRT 14.07_ltq (Linux 3.10.49) |

## Serial Console Access (Emergency Use)

The stick exposes a 3.3V TTL UART via SFP electrical pins — used only when SSH is unavailable:

| SFP Pin | Signal |
|---|---|
| Pin 2 | TX (from stick) |
| Pin 7 | RX (to stick) |
| Pin 14 | GND |
| Pin 15–16 | 3.3V power |

Settings: 115200 baud, 8-N-1, no flow control

> Requires a custom SFP breakout adapter or SFP to UART cable. Not needed for routine operations.

## Fiber Connector

- **SC/APC** (green ferrule, 8° angled polish)
- Do NOT connect SC/UPC (blue ferrule) — reflection loss will degrade upstream signal
- Use a short SC/APC patch cord from the stick to the wall outlet or splice box

## FS Documentation & Resources

- Product page: https://www.fs.com/products/133619.html
- Industrial datasheet: https://img-en.fs.com/file/datasheet/gpon-stick-datasheet.pdf
- GPON-ONU-34-20BI config guide: https://resource.fs.com/mall/resource/gpon-onu-34-20bi-configuration-guide.pdf
- GPON-SFP-ONT-MAC-I config guide: https://resource.fs.com/mall/resource/gpon-sfp-ont-mac-i-configuration-guide.pdf
- Community wiki (hack-gpon.org): https://hack-gpon.org/ont-fs-com-gpon-onu-stick-with-mac/
