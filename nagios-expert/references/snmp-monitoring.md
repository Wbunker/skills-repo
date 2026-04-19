# SNMP Monitoring
## Chapter 9: SNMP Fundamentals, check_snmp, Network Device Monitoring

---

## What Is SNMP?

SNMP (Simple Network Management Protocol) is an industry-standard protocol for monitoring and managing network devices. Nagios uses it primarily to query metrics from:
- Routers and switches
- UPS and PDU devices
- Printers
- Any Linux/Unix/Windows host with an SNMP agent

SNMP operates on **UDP port 161** (queries) and **UDP port 162** (traps).

---

## SNMP Versions

| Version | Authentication | Encryption | Notes |
|---------|---------------|------------|-------|
| v1 | Community string (plaintext) | None | Legacy; avoid |
| v2c | Community string (plaintext) | None | Most common in practice |
| v3 | Username + auth password | Optional DES/AES | Secure; recommended |

---

## SNMP Concepts

### OIDs (Object Identifiers)

Every metric in SNMP is identified by a dotted numeric OID:

```
1.3.6.1.2.1.1.1.0    = sysDescr (system description)
1.3.6.1.2.1.1.3.0    = sysUpTime
1.3.6.1.2.1.25.3.3.1.2  = hrProcessorLoad (CPU load)
1.3.6.1.4.1.2021.11.11.0 = UCD-SNMP memFreePercent
```

### MIBs (Management Information Base)

MIBs are text files that translate OIDs to human-readable names. The `snmpwalk` command uses MIBs to resolve names.

Common MIBs:
- **SNMPv2-MIB** — system info, uptime
- **IF-MIB** — network interface stats
- **HOST-RESOURCES-MIB** — CPU, memory, disk, processes
- **UCD-SNMP-MIB** — Linux-specific (load, memory, disk)

---

## Installing SNMP Tools

```bash
# Nagios server — needs snmp utilities for check_snmp
apt-get install -y snmp snmp-mibs-downloader  # Debian/Ubuntu
yum install -y net-snmp net-snmp-utils         # RHEL/CentOS
```

---

## Configuring SNMP on the Monitored Host

### Linux (net-snmp)

```bash
# /etc/snmp/snmpd.conf — minimal SNMPv2c read-only config
rocommunity  public  192.168.1.50    # allow read from Nagios server only
syslocation  "Rack 3, DC East"
syscontact   admin@example.com
```

```bash
systemctl enable snmpd
systemctl start snmpd
```

### Network Devices (routers/switches)

Configure via vendor CLI (Cisco, Juniper, etc.):

```
snmp-server community public RO
snmp-server location "Rack 3"
snmp-server contact admin@example.com
```

---

## snmpwalk — Explore an SNMP Agent

```bash
# Walk the entire MIB tree (verbose — use specific OIDs in practice)
snmpwalk -v 2c -c public 192.168.1.100

# Get system description
snmpwalk -v 2c -c public 192.168.1.100 system

# Get CPU load
snmpwalk -v 2c -c public 192.168.1.100 .1.3.6.1.4.1.2021.10

# Get interface stats
snmpwalk -v 2c -c public 192.168.1.100 ifTable

# Get a single OID
snmpget -v 2c -c public 192.168.1.100 .1.3.6.1.2.1.1.3.0
```

---

## check_snmp Plugin

```bash
# Syntax
check_snmp -H hostname -o OID -w warn -c crit -C community -v version
```

### Basic Examples

```bash
# Check system uptime (in timeticks — 100ths of a second)
check_snmp -H router01 -o .1.3.6.1.2.1.1.3.0 -C public

# Check CPU load (UCD-SNMP 1min average)
check_snmp -H linux01 -o .1.3.6.1.4.1.2021.10.1.3.1 -w 80 -c 95 -C public -v 2c

# Check free memory percentage
check_snmp -H linux01 -o .1.3.6.1.4.1.2021.11.11.0 -w 20: -c 10: -C public -v 2c
# 20: = warn if value is less than 20 (colon prefix = lower bound)

# Check interface operational status (1=up, 2=down)
check_snmp -H switch01 -o .1.3.6.1.2.1.2.2.1.8.1 -C public --string=1
# --string=1 means alert if value != "1"
```

### Multiple OIDs

```bash
check_snmp -H router01 \
  -o .1.3.6.1.2.1.2.2.1.10.1,.1.3.6.1.2.1.2.2.1.16.1 \
  -C public -v 2c
# Returns both ifInOctets and ifOutOctets for interface 1
```

---

## check_snmp in Nagios Config

```ini
define command {
    command_name  check_snmp
    command_line  $USER1$/check_snmp -H $HOSTADDRESS$ -o $ARG1$ -C $ARG2$ -v 2c -w $ARG3$ -c $ARG4$
}

define service {
    use                  generic-service
    host_name            switch01
    service_description  CPU Load
    check_command        check_snmp!.1.3.6.1.4.1.2021.10.1.3.1!public!80!95
}
```

---

## Monitoring Network Infrastructure

### Router/Switch Interface Traffic

```ini
# Interface bandwidth (check_if_traffic from community plugins, or custom)
define command {
    command_name  check_snmp_int
    command_line  $USER1$/check_snmp_int.pl -H $HOSTADDRESS$ -C $ARG1$ -n $ARG2$ -w $ARG3$ -c $ARG4$
}

define service {
    use                  generic-service
    host_name            core-router
    service_description  GigabitEthernet0/0
    check_command        check_snmp_int!public!GigabitEthernet0/0!80%!95%
}
```

### BGP/OSPF Peer State (Cisco)

```bash
# BGP neighbor state (Cisco MIB)
check_snmp -H router01 -o .1.3.6.1.4.1.9.9.187.1.2.5.1.3.1.4.192.168.100.1 -C public --string=6
# 6 = established
```

### UPS Monitoring (APC)

```bash
# Battery charge percentage (PowerNet MIB)
check_snmp -H ups01 -o .1.3.6.1.4.1.318.1.1.1.2.2.1.0 -C public -w 50: -c 25:
# 50: = warn if battery below 50%

# Time on battery (minutes)
check_snmp -H ups01 -o .1.3.6.1.4.1.318.1.1.1.2.2.3.0 -C public -w 5 -c 10
```

---

## SNMPv3 with check_snmp

SNMPv3 provides authentication and optional encryption:

```bash
check_snmp -H router01 \
  -o .1.3.6.1.2.1.1.3.0 \
  -P 3 \                      # use SNMPv3
  -U nagiosuser \             # username
  -L authPriv \               # security level: noAuthNoPriv | authNoPriv | authPriv
  -a SHA \                    # auth protocol: MD5 | SHA
  -A authpassword123 \        # auth password
  -x AES \                    # priv protocol: DES | AES
  -X privpassword456          # priv password
```

### SNMPv3 Config on Linux Host (/etc/snmp/snmpd.conf)

```
createUser nagiosuser SHA authpassword123 AES privpassword456
rouser nagiosuser priv
```

---

## Common SNMP OID Reference

| OID | Name | Notes |
|-----|------|-------|
| `.1.3.6.1.2.1.1.1.0` | sysDescr | System description |
| `.1.3.6.1.2.1.1.3.0` | sysUpTime | Uptime in timeticks |
| `.1.3.6.1.2.1.1.5.0` | sysName | Hostname |
| `.1.3.6.1.2.1.2.2.1.8.X` | ifOperStatus | Interface X status (1=up) |
| `.1.3.6.1.2.1.2.2.1.10.X` | ifInOctets | Interface X incoming bytes |
| `.1.3.6.1.2.1.2.2.1.16.X` | ifOutOctets | Interface X outgoing bytes |
| `.1.3.6.1.4.1.2021.10.1.3.1` | UCD load 1min | Linux CPU 1-min avg |
| `.1.3.6.1.4.1.2021.10.1.3.2` | UCD load 5min | Linux CPU 5-min avg |
| `.1.3.6.1.4.1.2021.10.1.3.3` | UCD load 15min | Linux CPU 15-min avg |
| `.1.3.6.1.4.1.2021.11.11.0` | memFreePercent | Linux free memory % |
| `.1.3.6.1.2.1.25.3.3.1.2.X` | hrProcessorLoad | CPU usage % for CPU X |
