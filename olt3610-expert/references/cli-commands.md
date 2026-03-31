# OLT3610-08GP4S CLI Command Reference

## Navigation

- [Show / Monitoring](#show--monitoring)
- [Interface & Port Config](#interface--port-config)
- [ONU Operations](#onu-operations)
- [SNMP](#snmp)
- [Firmware](#firmware)
- [System](#system)

---

## Show / Monitoring

```bash
# ONU registration status on all PON ports
Switch# show gpon onu

# ONU status on specific port
Switch# show gpon onu interface gpon 0/X

# Optical power levels (OLT TX and ONU RX)
Switch# show gpon onu optical-info interface gpon 0/X

# Interface summary
Switch# show interface

# Running configuration
Switch# show running-config

# Version / system info
Switch# show version

# MAC address table
Switch# show mac-address-table

# VLAN table
Switch# show vlan

# CPU and memory utilization
Switch# show system resource
```

---

## Interface & Port Config

```bash
# Enter PON port config mode
Switch_config# interface gpon 0/X

# Enter uplink port config (SFP example)
Switch_config# interface gigabitethernet 0/X

# Set port description
Switch_config_gpon0/X# description "Site-A PON Port"

# Shut / no shut a port
Switch_config_gpon0/X# shutdown
Switch_config_gpon0/X# no shutdown

# Adjust TX power level (reduces power by N dB)
Switch_config_gpon0/X# gpon powerlevel-tx-mode 0   # Normal (default)
Switch_config_gpon0/X# gpon powerlevel-tx-mode 1   # Normal - 3 dB
Switch_config_gpon0/X# gpon powerlevel-tx-mode 2   # Normal - 6 dB
```

---

## ONU Operations

```bash
# Set authentication method to serial number on a PON port
Switch_config# interface gpon 0/X
Switch_config_gpon0/X# gpon onu-authen-method sn

# Bind ONU by serial number
Switch_config_gpon0/X# gpon bind-onu sn <SERIAL_NUMBER>

# Unbind / remove an ONU
Switch_config_gpon0/X# no gpon bind-onu sn <SERIAL_NUMBER>

# Check rogue ONU detection alarms
Switch# show alarm

# Remote reboot an ONU (via OMCI)
Switch_config# onu reboot interface gpon 0/X onu <ONU-ID>
```

---

## SNMP

```bash
# Set SNMP community (RW)
Switch_config# snmp-server community 0 RW

# Set SNMP trap host
Switch_config# snmp-server host <NMS-IP> authentication configure snmp

# Verify SNMP config
Switch# show snmp
```

---

## Firmware

### Web UI method (local upgrade)
1. Navigate to `http://<OLT-IP>` → System Management → System Software
2. Choose File → select firmware binary → Upgrade
3. **Do not power off during upgrade**

### AmpCon-PON method (recommended for batch/scheduled)
- Supports simultaneous upgrade of 2,000+ OLTs and ONUs
- Access via AmpCon-PON web interface → Firmware Management → Schedule Upgrade
- Provides rollback capability if upgrade fails

### Check current firmware version
```bash
Switch# show version
```

---

## System

```bash
# Save running config to startup
Switch_config# wr all

# Reload system (reboot)
Switch_config# reload

# Set hostname
Switch_config# hostname <NAME>

# Set management IP on MGMT port
Switch_config# interface mgmt 0
Switch_config_mgmt0# ip address <IP> <MASK>
Switch_config_mgmt0# no shutdown

# Set in-band management IP on uplink port
Switch_config# interface gigabitethernet 0/X
Switch_config_ge0/X# ip address <IP> <MASK>

# NTP server
Switch_config# ntp server <NTP-IP>

# Syslog server
Switch_config# logging host <SYSLOG-IP>
```
