# ONU/ONT Management — OLT3610-08GP4S

## Overview

The OLT3610-08GP4S supports up to **128 ONUs per PON port** (1,024 total). Authentication uses serial number (SN) or password methods. Full remote configuration is handled via **OMCI** (ITU-T G.988).

---

## ONU Registration Process

The OLT performs a 3-step bring-up sequence automatically when an ONU connects:

1. **SN_Request** — OLT broadcasts serial number request
2. **Ranging_Request** — OLT determines fiber delay compensation
3. **Password_Request** — OLT sends password challenge (if password auth enabled)

The OLT will only complete registration if the ONU's SN (or password) is bound in the config.

---

## Binding an ONU (SN Method — Recommended)

```bash
Switch_config# interface gpon 0/X          # X = PON port 0–7
Switch_config_gpon0/X# gpon onu-authen-method sn
Switch_config_gpon0/X# gpon bind-onu sn <SERIAL_NUMBER>
Switch_config_gpon0/X# exit
Switch_config# wr all
```

**Finding the serial number:**
- Label on the ONU hardware (e.g., `4244434DF79D0F8C`)
- OLT discovery output before binding: `Switch# show gpon onu interface gpon 0/X`
  - Unbound ONUs appear in discovery list with status `DISCOVER`

---

## Removing / Replacing an ONU

```bash
Switch_config# interface gpon 0/X
Switch_config_gpon0/X# no gpon bind-onu sn <OLD_SERIAL>
Switch_config_gpon0/X# gpon bind-onu sn <NEW_SERIAL>
Switch_config_gpon0/X# exit
Switch_config# wr all
```

---

## Checking ONU Status

```bash
# All ONUs on a port
Switch# show gpon onu interface gpon 0/X

# Optical signal levels (critical for diagnostics)
Switch# show gpon onu optical-info interface gpon 0/X
```

**ONU RX power must be in range: -8 to -27 dBm**
- Above -8 dBm → signal too strong → add optical attenuator
- Below -27 dBm → signal too weak → check fiber, connectors, splitter ratios

---

## ONU States

| State | Meaning |
|---|---|
| `ONLINE` | Registered and passing traffic |
| `OFFLINE` | Was registered, now disconnected |
| `DISCOVER` | OLT sees ONU but it is not yet bound |
| `RANGING` | In bring-up process |

---

## Remote ONU Configuration via OMCI

OMCI (ITU-T G.988) allows the OLT to remotely configure ONU services without touching the ONU directly. Capabilities include:

- Service VLAN mapping
- QoS / bandwidth profiles
- Port enable/disable
- Firmware upgrades
- Remote reboot

```bash
# Remote reboot an ONU
Switch_config# onu reboot interface gpon 0/X onu <ONU-ID>
```

---

## Multi-Vendor ONU Compatibility

The OLT3610-08GP4S is confirmed interoperable with multi-vendor ONUs via OMCI. For full remote management and batch firmware upgrades of FS ONUs, use **AmpCon-PON**.

---

## ONU Firmware Upgrade

**Via AmpCon-PON (preferred):**
- Batch upgrade all ONUs simultaneously
- Scheduled maintenance windows
- Rollback capability

**Via OMCI (individual):**
- Initiated from OLT CLI
- ONU must be online

**Compatible FS ONU families:** GPON, E-GPON, XG-PON, MDU (with 1G–10G, optional PoE/WiFi/POTS interfaces)
