# AP-N505 CLI Reference

> CLI applies to **Fat (standalone) mode**. In Fit mode, use AC-1004 CLI or web UI for AP management.

## Console Access

```
Serial: 115200 baud, 8N1, no flow control  (RJ45 console port)
SSH:    ssh admin@<AP-IP>
Telnet: telnet <AP-IP>  (disable in production)
```

## CLI Mode Structure

```
AP>                    # User EXEC
AP#                    # Privileged EXEC
AP_config#             # Global configuration
AP_config_wlan0#       # WLAN/SSID interface config
AP_config_radio0#      # 2.4 GHz radio config
AP_config_radio1#      # 5 GHz radio config
```

Enter privileged mode: `AP> enable`
Enter global config: `AP# configure terminal`
Save config: `AP_config# write` or `AP# write memory`
Exit config: `AP_config# exit` or `Ctrl+Z`

## Show Commands

```bash
# System
show version                    # Firmware version, uptime, serial number
show running-config             # Full current configuration
show system                     # CPU, memory, temperature

# Wireless
show ap info                    # AP identity, mode, controller status
show radio                      # Radio 0 (2.4G) and radio 1 (5G) status, current channel/width
show wlan                       # SSID list and status
show client                     # All associated clients
show client detail <MAC>        # Per-client RSSI, data rate, VLAN, band, 802.11 capabilities

# Network
show interface                  # ETH0, ETH1, management IP, speed/duplex
show arp                        # ARP table
show vlan                       # VLAN assignments

# Controller
show capwap                     # Controller connection status and IP
show ap-mode                    # Current mode: fat / fit / cloud
```

## Common Configuration Commands

### Set management IP
```bash
AP_config# interface vlan 1
AP_config_vlan1# ip address 10.10.10.51 255.255.255.0
AP_config_vlan1# exit
AP_config# ip default-gateway 10.10.10.1
```

### Configure SSID
```bash
AP_config# wlan PecanGrove-WiFi
AP_config_wlan0# ssid PecanGrove-WiFi
AP_config_wlan0# security wpa2-psk
AP_config_wlan0# wpa-passphrase <passphrase>
AP_config_wlan0# vlan 100
AP_config_wlan0# no shutdown
AP_config_wlan0# exit
```

### Configure 2.4G radio
```bash
AP_config# radio 0
AP_config_radio0# channel 6
AP_config_radio0# channel-width 20
AP_config_radio0# power 15
AP_config_radio0# no shutdown
AP_config_radio0# exit
```

### Configure 5G radio (80 MHz)
```bash
AP_config# radio 1
AP_config_radio1# channel 149
AP_config_radio1# channel-width 80
AP_config_radio1# power 18
AP_config_radio1# no shutdown
AP_config_radio1# exit
```

### Configure 5G radio (160 MHz — maximum throughput)
```bash
AP_config# radio 1
AP_config_radio1# channel 36
AP_config_radio1# channel-width 160
AP_config_radio1# power 18
AP_config_radio1# no shutdown
AP_config_radio1# exit
```

> Valid 160 MHz channels (US): **36** (covers 36–48+100–144) or **149** (covers 149–161)
> Only 2 non-overlapping 160 MHz channels available — use sparingly in multi-AP deployments.

### Switch to Fit mode (controller-managed)
```bash
AP_config# ap-mode fit
AP_config# capwap server <AC-1004-IP>
AP_config# exit
AP# write memory
AP# reload
```

### Switch to Fat mode (standalone)
```bash
AP_config# ap-mode fat
AP_config# exit
AP# write memory
AP# reload
```

## Diagnostic Commands

```bash
AP# ping <destination>
AP# ping <AC-1004-IP>
AP# traceroute <destination>

AP# show rogue ap               # Rogue/unauthorized APs detected
AP# show rf stats               # Per-radio channel utilization and interference
AP# show client assoc           # Client association table
AP# show interface eth0         # ETH0 link state, speed, packet counters

AP_config# service wireless restart   # Restart radios without full reboot
AP# reload                            # Full reboot
```

## Firmware Upgrade (CLI)

```bash
AP# upgrade tftp <TFTP-server-IP> <firmware-filename.bin>
AP# upgrade ftp <FTP-IP> <username> <password> <filename.bin>
```

Confirm with `show version` after reboot.

## Logging

```bash
AP# show log
AP# show log level debug                  # Verbose (use briefly)
AP_config# logging host <syslog-IP>
AP_config# logging level 6                # Informational
```

## Password & Access

```bash
AP_config# username admin privilege 15 password <new-password>
AP_config# no service telnet
AP_config# service ssh
```

## FS CLI Reference Guide
Full syntax: https://img-en.fs.com/file/user_manual/ap-series-cli-reference-guide.pdf
