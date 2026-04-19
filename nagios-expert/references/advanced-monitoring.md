# Advanced Monitoring
## Chapter 10: Distributed Nagios, Windows Monitoring with NSClient++, Multi-Instance

---

## Distributed Monitoring Architecture

A single Nagios instance doesn't scale to thousands of hosts or work across firewalled network segments. The solution: **multiple Nagios instances** feeding results to a central aggregator.

```
┌──────────────────────────────────────────────────────────────┐
│                    CENTRAL NAGIOS                            │
│  Receives passive check results via NSCA                     │
│  Displays consolidated status for all sites                  │
│  Sends notifications                                         │
└───────────────┬─────────────────────┬────────────────────────┘
                │ NSCA passive results│
    ┌───────────▼──────────┐  ┌───────▼───────────────┐
    │  SATELLITE NAGIOS    │  │  SATELLITE NAGIOS     │
    │  (Site A)            │  │  (Site B)             │
    │  Active checks       │  │  Active checks        │
    │  ocsp_command →      │  │  ocsp_command →       │
    │  send_nsca to central│  │  send_nsca to central │
    └──────────────────────┘  └───────────────────────┘
```

### How It Works

Each satellite Nagios:
1. Runs its own active checks against local hosts
2. Uses `obsess_over_services=1` with an OCSP command that calls `send_nsca`
3. Forwards every check result to the central Nagios as a passive check

The central Nagios:
1. Has all hosts/services defined with `active_checks_enabled 0`, `passive_checks_enabled 1`
2. Receives results from satellites via NSCA
3. Uses `check_freshness` to detect when satellites stop reporting

### Satellite nagios.cfg

```ini
obsess_over_services=1
obsess_over_hosts=1
ocsp_command=submit-check-to-central
ochp_command=submit-host-to-central
```

```ini
define command {
    command_name  submit-check-to-central
    command_line  /usr/local/nagios/libexec/eventhandlers/submit_check_result \
      $HOSTNAME$ '$SERVICEDESC$' $SERVICESTATEID$ '$SERVICEOUTPUT$'
}
```

The `submit_check_result` script:

```bash
#!/bin/bash
# submit_check_result
HOST=$1
SVC=$2
STATE=$3
OUTPUT=$4

printf "%s\t%s\t%s\t%s\n" "$HOST" "$SVC" "$STATE" "$OUTPUT" | \
  /usr/local/nagios/bin/send_nsca -H central.nagios.example.com \
    -c /etc/nagios/send_nsca.cfg
```

### Central Nagios Host/Service Definitions

```ini
define host {
    host_name               web01-site-a
    address                 10.1.1.10
    active_checks_enabled   0
    passive_checks_enabled  1
    check_freshness         1
    freshness_threshold     600   ; 10 minutes
    check_command           check_dummy!2!No data from satellite
    ...
}
```

---

## Monitoring Windows Hosts

Windows cannot run NRPE natively, and SNMP requires additional configuration. The standard solution is **NSClient++** (often called "nsclient" or "NSC").

### NSClient++

NSClient++ is a Windows monitoring agent that:
- Runs as a Windows service
- Exposes metrics via multiple protocols: NRPE, check_nt, NSCA, REST API
- Supports a large built-in check library

### Installing NSClient++ on Windows

1. Download from `nsclient.org` (MSI installer)
2. Run installer; select components: NRPE, check_nt server, NSCA client
3. Configure `nsclient.ini` (typically `C:\Program Files\NSClient++\nsclient.ini`)

### nsclient.ini (basic)

```ini
[/settings/default]
; Allowed hosts (Nagios server IP)
allowed hosts = 192.168.1.50

[/settings/NRPE/server]
; Allow arguments
allow arguments = true
allow nasty characters = false
port = 5666

[/settings/check_mk]
; Enable check_nt compatibility
port = 12489

[/modules]
; Enable protocols
NRPEServer = enabled
CheckExternalScripts = enabled
CheckSystem = enabled
CheckDisk = enabled
CheckEventLog = enabled
```

### NSClient++ Built-in Checks (via NRPE)

```bash
# CPU usage
check_nrpe -H windows01 -c check_cpu -a "warn=load>80" "crit=load>95"

# Memory usage
check_nrpe -H windows01 -c check_memory -a "warn=used>80%" "crit=used>95%"

# Disk space
check_nrpe -H windows01 -c check_drivesize -a "drive=C:" "warn=used>80%" "crit=used>95%"

# Windows service status
check_nrpe -H windows01 -c check_service -a "service=Spooler"

# Event log errors in last hour
check_nrpe -H windows01 -c check_eventlog -a "log=Application" "filter=level=error" "warn=count>0" "crit=count>10"

# Process check
check_nrpe -H windows01 -c check_process -a "process=iis.exe" "crit=state!=started"
```

---

## check_nt (Legacy Windows Monitoring)

Before NSClient++ NRPE support, `check_nt` was standard. It uses TCP port 12489.

```ini
define command {
    command_name  check_nt
    command_line  $USER1$/check_nt -H $HOSTADDRESS$ -p 12489 -s mypassword -v $ARG1$ $ARG2$
}
```

### check_nt Variables

```bash
# CPU usage
check_nt -H windows01 -p 12489 -s password -v CPULOAD -l 5,80,95
# -l interval_minutes,warn%,crit%

# Memory
check_nt -H windows01 -p 12489 -s password -v MEMUSE -w 80 -c 95

# Disk space
check_nt -H windows01 -p 12489 -s password -v USEDDISKSPACE -l c -w 80 -c 95

# Service status
check_nt -H windows01 -p 12489 -s password -v SERVICESTATE -l "Messenger,Spooler"

# Process running
check_nt -H windows01 -p 12489 -s password -v PROCSTATE -d SHOWALL -l "notepad.exe"
```

---

## Nagios Service Definitions for Windows Hosts

```ini
define host {
    use             windows-server   ; template for Windows
    host_name       win-web01
    alias           Windows Web Server 01
    address         192.168.1.100
}

define service {
    use                  generic-service
    host_name            win-web01
    service_description  CPU Load
    check_command        check_nrpe!check_cpu!"warn=load>80" "crit=load>95"
}

define service {
    use                  generic-service
    host_name            win-web01
    service_description  C: Drive Space
    check_command        check_nrpe!check_drivesize!"drive=C:" "warn=used>80%" "crit=used>95%"
}

define service {
    use                  generic-service
    host_name            win-web01
    service_description  IIS Service
    check_command        check_nrpe!check_service!"service=W3SVC"
}
```

---

## Multi-Instance Nagios

Running multiple Nagios instances on one server (less common, but useful):

```bash
# Each instance needs:
# - Its own nagios.cfg with unique:
#   - nagios_user / nagios_group
#   - log_file path
#   - status_file path
#   - command_file path
#   - lock_file path

/usr/local/nagios/bin/nagios -d /etc/nagios/site-a/nagios.cfg
/usr/local/nagios/bin/nagios -d /etc/nagios/site-b/nagios.cfg
```

### Load Balancing

Distribute hosts across instances based on:
- Network segment (each instance in its own segment)
- Geographic location
- Functional group (network devices vs. application servers)
- Check volume (balance check counts for performance)

---

## Performance Tuning for Large Environments

```ini
# nagios.cfg performance settings

# Use worker processes (Nagios 4 default — ensure not disabled)
# Worker count scales with CPU cores

# Reduce unnecessary state retention I/O
retention_update_interval=60   ; write retention.dat every 60 seconds (not every check)

# Tune check scheduling
max_concurrent_checks=0        ; 0 = unlimited (workers handle it)
check_result_reaper_frequency=10  ; how often to harvest check results (seconds)
max_check_result_reaper_time=30   ; max time per reap cycle

# Disable perfdata processing if not using it
process_performance_data=0

# Sleep interval between scheduling loops
sleep_time=0.25
```
