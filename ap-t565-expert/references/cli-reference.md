# AP-T565 CLI Reference

> CLI applies to **Fat (standalone) mode**. In Fit mode, use AC-1004 CLI or web UI for AP management.

## Console Access

```
Serial: 115200 baud, 8N1, no flow control
SSH:    ssh admin@<AP-IP>
Telnet: telnet <AP-IP>  (disable in production)
```

## CLI Mode Structure

```
AP>                    # User EXEC (limited commands)
AP#                    # Privileged EXEC (show commands, ping, reload)
AP_config#             # Global configuration mode
AP_config_wlan0#       # WLAN/SSID interface config
AP_config_radio0#      # 2.4 GHz radio config
AP_config_radio1#      # 5 GHz radio config
```

Enter privileged mode: `AP> enable`
Enter global config: `AP# configure terminal`
Exit config mode: `AP_config# exit` or `Ctrl+Z`
Save config: `AP_config# write` or `AP# write memory`

## Show Commands

```bash
# System status
show version                    # Firmware version, uptime, serial number
show running-config             # Full current configuration
show system                     # CPU, memory, temperature

# Wireless status
show ap info                    # AP identity, mode, controller status
show radio                      # Radio 0 (2.4G) and radio 1 (5G) status
show wlan                       # SSID/WLAN list and status
show client                     # All associated clients
show client detail <MAC>        # Per-client RSSI, rate, VLAN, band

# Network
show interface                  # ETH0, ETH1, management IP
show arp                        # ARP table
show vlan                       # VLAN assignments

# Controller / CAPWAP
show capwap                     # Controller connection status
show ap-mode                    # Current mode: fat / fit / cloud
```

## Common Configuration Commands

### Set management IP (standalone mode)
```bash
AP_config# interface vlan 1
AP_config_vlan1# ip address 10.10.10.50 255.255.255.0
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

### Configure radio
```bash
# 2.4 GHz radio
AP_config# radio 0
AP_config_radio0# channel 6
AP_config_radio0# channel-width 20
AP_config_radio0# power 18
AP_config_radio0# no shutdown
AP_config_radio0# exit

# 5 GHz radio
AP_config# radio 1
AP_config_radio1# channel 149
AP_config_radio1# channel-width 40
AP_config_radio1# power 22
AP_config_radio1# no shutdown
AP_config_radio1# exit
```

### Switch AP to Fit mode (controller-managed)
```bash
AP_config# ap-mode fit
AP_config# capwap server <AC-1004-IP>
AP_config# exit
AP# write memory
AP# reload
```

### Switch AP to Fat mode (standalone)
```bash
AP_config# ap-mode fat
AP_config# exit
AP# write memory
AP# reload
```

## Diagnostic Commands

```bash
# Ping test
AP# ping 8.8.8.8

# Check CAPWAP controller reachability
AP# ping <AC-1004-IP>

# Trace route
AP# traceroute <destination-IP>

# Check for rogue APs
AP# show rogue ap

# View wireless interference / spectrum
AP# show rf stats

# Check client association table
AP# show client assoc

# Check packet counters on ETH0
AP# show interface eth0

# Restart wireless service (without full reboot)
AP_config# service wireless restart

# Full reboot
AP# reload
```

## Firmware Upgrade (CLI)

```bash
# Upload via TFTP
AP# upgrade tftp <TFTP-server-IP> <firmware-filename.bin>

# Upload via FTP
AP# upgrade ftp <FTP-IP> <username> <password> <filename.bin>
```

Monitor with `show version` after reboot to confirm new firmware is active.

## Log Commands

```bash
AP# show log                    # Recent system log entries
AP# show log level debug        # Verbose debug logging (use briefly; high CPU)
AP_config# logging host <syslog-IP>  # Send logs to remote syslog server
AP_config# logging level 6      # Informational (default); use 7 for debug
```

## Password & Access Management

```bash
AP_config# username admin privilege 15 password <new-password>
AP_config# no service telnet    # Disable Telnet
AP_config# service ssh          # Ensure SSH enabled
```

## FS CLI Reference Guide
Full syntax documentation: https://img-en.fs.com/file/user_manual/ap-series-cli-reference-guide.pdf
