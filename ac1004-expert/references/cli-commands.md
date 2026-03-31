# AC-1004 CLI Command Reference

## Navigation

- [Show / Monitoring](#show--monitoring)
- [System Configuration](#system-configuration)
- [AP Operations](#ap-operations)
- [SNMP & Logging](#snmp--logging)
- [Firmware Upgrade](#firmware-upgrade)

---

## Show / Monitoring

```bash
# AC controller status and configuration
show ac-config

# All AP configurations (running)
show ap-config running

# Specific AP configuration
show ap-config ap-name <AP-NAME>

# Connected wireless clients
show wireless client

# SSID/WLAN summary
show wlan

# Interface status
show interface

# Running configuration
show running-config

# System version / FSOS info
show version

# CPU and memory
show system resource

# VLAN table
show vlan

# MAC address table
show mac-address-table

# SNMP trap configuration
show ac-config        # includes trap switch status

# Syslog buffer
show log
```

---

## System Configuration

```bash
# Enter global config mode
Switch# config

# Set hostname
Switch_config# hostname <NAME>

# Set management IP (service port)
Switch_config# interface gigabitethernet 0/0
Switch_config_ge0/0# ip address <IP> <MASK>
Switch_config_ge0/0# no shutdown

# Default gateway
Switch_config# ip default-gateway <GW-IP>

# DNS server
Switch_config# ip dns-server <DNS-IP>

# Enable SSH (disable Telnet in production)
Switch_config# ssh-server enable

# NTP server
Switch_config# ntp server <NTP-IP>

# Save configuration
Switch_config# write memory
# or
Switch_config# wr

# Reboot
Switch_config# reload
```

---

## AP Operations

```bash
# Enter AP group config (all APs)
Switch_config# ap-config all

# Enter config for a specific AP by name
Switch_config# ap-config ap-name <AP-NAME>

# Bind AP by MAC address (within ap-config mode)
Switch_config_apc# ap-mac <MAC-ADDRESS>

# Remove AP binding
Switch_config_apc# no ap-mac <MAC-ADDRESS>

# Switch AP between fit mode (controller-managed) and fat mode (standalone)
Switch_config_apc# ap-mode fit
Switch_config_apc# ap-mode fat

# Assign radio interface to WLAN/VLAN mapping
Switch_config_apc# radio 1
Switch_config_apc_r1# wlan-vlan-map <WLAN-ID> <VLAN-ID>

# Set AP transmit power
Switch_config_apc_r1# power <level>

# Set AP channel
Switch_config_apc_r1# channel <channel-number>
```

---

## SNMP & Logging

```bash
# Configure SNMP v3 user
Switch_config# snmp-server user <USERNAME> v3 auth sha <AUTH-PASS> priv aes <PRIV-PASS>

# Set SNMP trap host
Switch_config# snmp-server host <NMS-IP> traps version 3 <USERNAME>

# Enable AP join failure traps
Switch_config# ac-config
Switch_config_ac# snmp-trap ap-join enable

# Configure syslog server (up to 5 servers)
Switch_config# logging host <SYSLOG-IP>
Switch_config# logging host <SYSLOG-IP2>

# Set log level (0=emergencies, 7=debug)
Switch_config# logging level <0-7>

# View local log buffer
Switch# show log
```

---

## Firmware Upgrade

The AC-1004 runs **FSOS** and upgrades via TFTP.

**Step 1 — Set up a TFTP server** on a PC in the same network, place the firmware `.bin` file in the TFTP root.

**Step 2 — From AC-1004 CLI:**
```bash
Switch# upgrade download tftp://<TFTP-SERVER-IP>/<firmware-filename>.bin
```

Example filename format: `AC_FSOS11.9(2)B2P5_G2C6-01_07151603_install.bin`

**Step 3 — Verify and reload:**
```bash
Switch# show version
Switch_config# reload
```

> **Do not power off during upgrade.** Use console cable as fallback access in case network drops during upgrade.

**Check current version:**
```bash
Switch# show version
```

**Airware Cloud upgrade (preferred for bulk/scheduled):**
- Log in to https://airware-login.fs.com
- Navigate to Firmware Management → Schedule Upgrade
- Supports simultaneous upgrade of AC and all managed APs
