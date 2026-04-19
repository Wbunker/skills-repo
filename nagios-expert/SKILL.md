---
name: nagios-expert
description: Nagios 4 monitoring expertise covering installation, configuration, plugins, remote monitoring (NRPE/SSH/SNMP), passive checks, notifications, escalations, distributed monitoring, Windows monitoring, custom plugin development, and the Query Handler. Use when setting up Nagios, writing check commands, configuring hosts/services, troubleshooting alerts, extending Nagios with custom checks, or designing distributed monitoring architectures. Based on "Learning Nagios 4" by Wojciech Kocjan.
---

# Nagios 4 Expert

Based on *Learning Nagios 4* by Wojciech Kocjan (Packt Publishing).

## Nagios Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        NAGIOS 4 CORE                            │
│                                                                 │
│  ┌─────────────┐   ┌──────────────┐   ┌────────────────────┐   │
│  │  Scheduler  │──►│ Check Engine │──►│  State Machine     │   │
│  │  (timing)   │   │  (active /   │   │  soft → hard state │   │
│  └─────────────┘   │   passive)   │   └────────────────────┘   │
│                    └──────────────┘            │                │
│                           ▲                    ▼                │
│  ┌──────────────┐         │          ┌────────────────────┐    │
│  │  Passive     │─────────┘          │  Notification      │    │
│  │  Check Input │  (NSCA / cmd pipe) │  Engine            │    │
│  │  (NSCA/ext)  │                    └────────────────────┘    │
│  └──────────────┘                             │                 │
│                                               ▼                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Contacts · Contact Groups · Escalations · Time Periods│    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
         │                                     │
         ▼                                     ▼
  ┌─────────────┐                     ┌─────────────────┐
  │  Plugins    │                     │   Web Interface  │
  │  (check_*)  │                     │   (CGI / API)    │
  └─────────────┘                     └─────────────────┘
```

## Quick Reference

| Task | Reference |
|------|-----------|
| Concepts, states, soft/hard, architecture | [overview-and-architecture.md](references/overview-and-architecture.md) |
| Install, compile, packages, service setup | [installation.md](references/installation.md) |
| Web UI, Apache config, admin users, CGIs | [web-interface.md](references/web-interface.md) |
| Standard plugins, check_* commands, service checks | [plugins.md](references/plugins.md) |
| Object config, templates, inheritance, macros, flapping | [configuration.md](references/configuration.md) |
| Notifications, contacts, escalations, time periods | [notifications.md](references/notifications.md) |
| Passive checks, NSCA, freshness, obsessive processing | [passive-checks.md](references/passive-checks.md) |
| NRPE, SSH checks, remote plugin execution | [remote-monitoring.md](references/remote-monitoring.md) |
| SNMP monitoring, check_snmp, network devices | [snmp-monitoring.md](references/snmp-monitoring.md) |
| Distributed monitoring, Windows/NSClient++, multi-instance | [advanced-monitoring.md](references/advanced-monitoring.md) |
| Custom plugins (C, scripting), cloud/VMware monitoring | [programming.md](references/programming.md) |
| Query Handler, Unix sockets, NERD, external integration | [query-handler.md](references/query-handler.md) |

## Reference Files

| File | Chapters | Topics |
|------|----------|--------|
| `overview-and-architecture.md` | 1 | Core concepts, host/service model, check scheduling, soft/hard states, flap detection, event handlers |
| `installation.md` | 2 | Compile from source, packages, users/groups, nagios.cfg, CGI config, service startup |
| `web-interface.md` | 3 | Apache/httpd config, htpasswd, CGI programs, status maps, third-party UIs |
| `plugins.md` | 4 | check_http, check_smtp, check_mysql, check_disk, check_load, check_mem, check_smart, check_nfs |
| `configuration.md` | 5 | Host/service/command objects, templates, additive inheritance, macros, timeperiods, servicegroups, flapping |
| `notifications.md` | 6 | Notification logic, contact/contactgroup, notification commands, escalations, on-call rotations |
| `passive-checks.md` | 7 | Passive check model, NSCA daemon, send_nsca, freshness thresholds, obsessive service/host processor |
| `remote-monitoring.md` | 8 | NRPE install/config, check_nrpe, SSH-based checks, command arguments, NRPE vs SSH tradeoffs |
| `snmp-monitoring.md` | 9 | SNMP v1/v2c/v3, check_snmp, OID paths, snmpwalk, MIBs, router/switch monitoring |
| `advanced-monitoring.md` | 10 | Distributed Nagios, passive result aggregation, Windows with NSClient++, check_nt, multi-master |
| `programming.md` | 11 | Plugin API contract, exit codes, C/libnagios, scripting plugins, website/VMware/AWS monitoring |
| `query-handler.md` | 12 | Query Handler protocol, Unix domain sockets, NERD (Nagios Event Radio Dispatcher), async events |

## Core Decision Trees

### How Should I Monitor This?

```
What are you trying to monitor?
├── Local service on Nagios host → Active check with check_* plugin
├── Remote Linux/Unix host
│   ├── Need lightweight, secure → NRPE (check_nrpe)
│   ├── Already have SSH keys → SSH-based check (check_by_ssh)
│   └── Network device (router/switch/UPS) → SNMP (check_snmp)
├── Remote Windows host → NSClient++ + check_nt / check_nrpe
├── External system pushes results → Passive checks (NSCA)
│   ├── Results from other Nagios → Distributed monitoring
│   └── Results from app/script → send_nsca
└── Need bidirectional integration → Query Handler (ch12)
```

### What State Will Nagios Report?

```
Check result received
├── OK (exit 0) → Service/Host UP
├── WARNING (exit 1) → Soft WARNING state
│   └── Repeated max_check_attempts times → Hard WARNING
├── CRITICAL (exit 2) → Soft CRITICAL state
│   └── Repeated max_check_attempts times → Hard CRITICAL
│       └── Notifications sent for hard states
└── UNKNOWN (exit 3) → Check execution problem
```

### Which Notification Reaches Whom?

```
Hard state change or recovery
├── Is current time in notification_period? No → skip
├── Are notifications enabled globally + for host/service? No → skip
├── Is host/service in downtime or acknowledged? Yes → skip
├── Contact's service/host_notification_options match state? No → skip
├── Escalation rules match (attempt count, time period)? → use escalation contacts
└── Send notification via contact's notification_command
```

## Key Concepts

### Soft vs. Hard States

| State Type | Trigger | Notifications? |
|------------|---------|----------------|
| **Soft** | First N-1 failures (`max_check_attempts - 1`) | No |
| **Hard** | Nth consecutive failure | Yes |
| **Hard recovery** | OK after hard problem | Yes |

Prevents notification storms from transient blips. Set `max_check_attempts 3` for most services.

### Plugin Exit Code Contract

| Exit Code | Meaning | Nagios State |
|-----------|---------|--------------|
| 0 | OK | OK |
| 1 | Warning threshold exceeded | WARNING |
| 2 | Critical threshold exceeded | CRITICAL |
| 3 | Plugin could not execute check | UNKNOWN |

Every Nagios plugin must honor this contract. The single line of stdout becomes the status message; subsequent lines become long output.

### Object Inheritance

```
define host {
    name                 linux-base    ; template name
    check_interval       5
    max_check_attempts   3
    register             0             ; do not instantiate this template
}

define host {
    use                  linux-base    ; inherit above
    host_name            web01
    address              192.168.1.10
}
```

`use` copies all values; overriding a field in the child always wins. Use `+` prefix for additive inheritance on list fields (e.g., `+contact_groups`).
