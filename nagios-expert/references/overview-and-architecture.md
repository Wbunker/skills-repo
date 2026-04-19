# Nagios Overview and Architecture
## Chapter 1: Concepts, States, Scheduling, and Core Architecture

---

## What Is Nagios?

Nagios is an open-source IT infrastructure monitoring system. It monitors hosts and services, alerts staff when things go wrong, and notifies them when problems are resolved. Key capabilities:

- **Host monitoring**: Is a server/device reachable?
- **Service monitoring**: Is a specific service (HTTP, SSH, DB) responding correctly?
- **Alerting**: Notify on-call contacts via email, SMS, paging
- **Event handlers**: Auto-remediate by triggering scripts on state changes
- **Trending**: Feed performance data to external RRD/graphing systems

### What's New in Nagios 4

- **Multi-threaded check execution**: Runs checks in parallel worker processes instead of forking per check — dramatically improves performance at scale
- **Core workers**: Background processes absorb check load without the overhead of individual fork/exec cycles
- **Better logging and performance**: Reduced I/O, improved scheduling fairness
- **Query Handler**: General-purpose socket interface for external integration (see query-handler.md)

---

## Core Object Model

```
┌──────────┐        ┌──────────┐
│   Host   │───────►│ Service  │
│          │  1:N   │          │
│ hostname │        │ svc name │
│ address  │        │ check cmd│
│ contacts │        │ contacts │
└──────────┘        └──────────┘
     │                    │
     └──────────┬──────────┘
                ▼
        ┌──────────────┐
        │   Contact /  │
        │ ContactGroup │
        └──────────────┘
```

### Hosts
- Represent network-connected devices (servers, routers, printers)
- Have an `address` (IP or hostname) used by check commands
- Have their own UP/DOWN/UNREACHABLE states

### Services
- Represent something being checked on a host (HTTP port, disk space, CPU load)
- Always belong to exactly one host
- Have OK/WARNING/CRITICAL/UNKNOWN states

### Commands
- Shell templates that define how to run a plugin
- Use macros (`$HOSTADDRESS$`, `$ARG1$`) for dynamic values

### Contacts and Contact Groups
- Who to notify when problems occur
- Contacts have notification commands (e.g., send email)
- Contact groups bundle multiple contacts for assignment to hosts/services

---

## Check Scheduling

Nagios uses an **interval-based scheduler**. Each host/service has:

| Parameter | Meaning |
|-----------|---------|
| `check_interval` | How often to run checks when state is OK (in minutes) |
| `retry_interval` | How often to re-check when in soft problem state |
| `max_check_attempts` | How many failures before transitioning to hard state |

### Check Execution Flow

```
Scheduled check time arrives
        │
        ▼
  Run check plugin
        │
   ┌────┴────┐
   │  Result │
   └────┬────┘
        │
  ┌─────▼──────┐       ┌────────────────────────────┐
  │   OK?       │──Yes─►│ Reset attempt counter      │
  └─────┬───────┘       │ Schedule next at check_interval│
        │No             └────────────────────────────┘
        ▼
  ┌────────────────┐
  │ Increment      │
  │ attempt counter│
  └───────┬────────┘
          │
  attempt < max?──Yes──► Soft state, retry at retry_interval
          │No
          ▼
     Hard state → Send notifications
```

---

## Soft States and Hard States

The **soft/hard state distinction** is fundamental to Nagios design. It prevents alert floods from transient failures.

### Soft State
- Occurs on the **first through (N-1)th** consecutive failures
- Nagios re-checks at `retry_interval` (usually shorter than `check_interval`)
- **No notifications are sent**
- Displayed in the web interface but not yet "official"

### Hard State
- Occurs after **Nth consecutive failure** (`max_check_attempts` reached)
- **Notifications are sent** to contacts
- State is now "official" — event handlers fire
- Remains hard until the service recovers (or is manually acknowledged)

### Hard Recovery
- When a service in hard problem state returns to OK
- Sends a recovery notification (if configured)
- Resets attempt counter

### Typical Configuration

```
max_check_attempts  3     ; 3 strikes before hard state
check_interval      5     ; check every 5 min when OK
retry_interval      1     ; re-check every 1 min in soft state
```

---

## Host States

| State | Meaning |
|-------|---------|
| UP | Host is reachable and responding |
| DOWN | Host check failing |
| UNREACHABLE | Host's parent(s) are DOWN; host may be fine but unreachable from Nagios |

### Parent/Child Relationships

Nagios models network topology via `parents` directive. If a router (parent) goes DOWN, all hosts behind it become UNREACHABLE rather than DOWN. This:
- Prevents notification floods for all downstream hosts
- Accurately represents root cause vs. symptom

```
define host {
    host_name   web01
    parents     core-router
}
```

---

## Flap Detection

**Flapping** = a host/service changing states too frequently (oscillating).

Nagios tracks the percentage of state changes over the last 21 check results. If the change rate exceeds `high_flap_threshold` (default 30%), the host/service is considered flapping.

### Flapping Behavior
- Nagios sends a "started flapping" notification
- Suppresses normal problem/recovery notifications while flapping
- Stops flapping when rate drops below `low_flap_threshold` (default 20%)

### Disable Flap Detection

```
define service {
    flap_detection_enabled  0
}
```

---

## Event Handlers

Event handlers are optional scripts that run when a host/service changes state. Uses:
- Auto-restart a crashed service
- Page on-call on first hard critical
- Trigger a runbook via webhook

```
define service {
    event_handler  restart-httpd
}

define command {
    command_name  restart-httpd
    command_line  /usr/local/nagios/libexec/eventhandlers/restart-httpd $SERVICESTATE$ $SERVICESTATETYPE$ $SERVICEATTEMPT$
}
```

Event handler receives state, state type (SOFT/HARD), and attempt number as arguments. Typically only act on HARD states.

---

## Performance Data

Many plugins output performance data after a `|` pipe character:

```
DISK OK - free space: / 18295 MB (73%);|/=6734MB;20000;23000;0;25045
```

Nagios passes this to external programs via `process_performance_data=1` and `host/service_perfdata_command` directives. Common consumers:
- **PNP4Nagios** — RRDtool-based graphs
- **Graphite/InfluxDB** — time-series databases
- **Grafana** — dashboarding with metric storage backend

---

## Key Architecture Files

| File/Dir | Purpose |
|----------|---------|
| `/usr/local/nagios/etc/nagios.cfg` | Main configuration file |
| `/usr/local/nagios/etc/cgi.cfg` | Web interface configuration |
| `/usr/local/nagios/etc/objects/` | Host, service, command definitions |
| `/usr/local/nagios/var/nagios.log` | Event and alert log |
| `/usr/local/nagios/var/status.dat` | Live status (read by CGIs) |
| `/usr/local/nagios/var/nagios.cmd` | External command pipe (FIFO) |
| `/usr/local/nagios/libexec/` | Plugin executables |
