---
name: olt3610-expert
description: "Expert guidance for the FS OLT3610-08GP4S 8-port GPON Optical Line Terminal used at Pecan Grove RV Park. Use when the user needs to register or troubleshoot ONU/ONT devices, configure VLANs or bandwidth profiles, run CLI commands, monitor optical power levels, update firmware, manage the fiber network, or troubleshoot connectivity issues on the GPON network. Covers CLI, web UI, SNMP, and AmpCon-PON management methods."
---

# FS OLT3610-08GP4S Expert

**Device:** FS OLT3610-08GP4S — 8-port GPON OLT (Layer 3, Broadcom chipset)
**Location:** Pecan Grove RV Park fiber network hub
**Manufacturer docs:** https://www.fs.com/products/143753.html

## Key Specs

| Item | Value |
|---|---|
| GPON ports | 8x (ITU-T G.984/G.988) |
| Max ONUs | 1,024 (128 per PON port) |
| Downstream | 2.5 Gbps per PON port |
| Upstream | 1.25 Gbps per PON port |
| Uplinks | 4x 10G SFP+ + 4x 1G SFP + 4x GE combo |
| Management | CLI, Web UI (HTTP/HTTPS), SNMP, SSH, Telnet, TR-069 |

## CLI Access

**Console serial:** 9600 bps, 8N1, no flow control
**SSH/Telnet:** via MGMT port or in-band uplink IP

**CLI mode structure:**
```
Switch>                         # User EXEC
Switch#                         # Privileged EXEC
Switch_config#                  # Global config
Switch_config_gpon0/X#          # Per-PON-port config (X = 0–7)
```

**Save config:** `Switch_config# wr all`

## Reference Files

| Topic | File | When to read |
|---|---|---|
| CLI commands | [references/cli-commands.md](references/cli-commands.md) | Any CLI task, port config, show commands |
| ONU management | [references/onu-management.md](references/onu-management.md) | Registering, binding, or troubleshooting ONUs |
| VLAN & bandwidth | [references/vlan-bandwidth.md](references/vlan-bandwidth.md) | VLAN config, DBA profiles, QoS, bandwidth limits |
| Troubleshooting | [references/troubleshooting.md](references/troubleshooting.md) | Any connectivity issue, rogue ONU, optical power problems |

## Common Workflows

### Register a new ONU (SN method)
1. Connect ONU fiber to PON port
2. Read serial number from ONU label or `show gpon onu` discovery output
3. See [references/onu-management.md](references/onu-management.md) → "Binding an ONU"

### Check why an ONU is offline
See [references/troubleshooting.md](references/troubleshooting.md) → "ONU Not Registering"

### Set bandwidth limit for a subscriber
See [references/vlan-bandwidth.md](references/vlan-bandwidth.md) → "DBA Profiles"

### Firmware update
See [references/cli-commands.md](references/cli-commands.md) → "Firmware"

## Management Interfaces

- **Web UI:** `http://<OLT-IP>` — dashboard, ONU status, basic config
- **AmpCon-PON:** FS centralized NMS; batch ONU firmware upgrades, topology view, fault detection
- **SNMP:** community string configurable via CLI; trap host for NMS integration
- **MGMT port:** dedicated out-of-band management (configure IP manually; no default)
