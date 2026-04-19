# Advanced Configuration
## Chapter 5: Templates, Inheritance, Macros, Time Periods, Servicegroups, Flapping

---

## Object Types

Nagios has six core configurable object types:

| Object | Description |
|--------|-------------|
| `host` | A monitored device |
| `service` | A check associated with a host |
| `command` | A shell command template |
| `contact` | A person to notify |
| `contactgroup` | A group of contacts |
| `timeperiod` | A named schedule (when checks/notifications apply) |
| `hostgroup` | Logical grouping of hosts |
| `servicegroup` | Logical grouping of services across hosts |

---

## Templates and Inheritance

Templates eliminate repetition. Any object with `register 0` is a template — it won't be instantiated as a real object.

### Defining a Template

```ini
define host {
    name                    linux-server    ; template name (not host_name)
    use                     generic-host    ; can chain templates
    check_period            24x7
    check_interval          5
    retry_interval          1
    max_check_attempts      10
    check_command           check-host-alive
    notification_period     workhours
    notification_interval   120
    notification_options    d,u,r
    contact_groups          admins
    register                0               ; REQUIRED — do not instantiate
}
```

### Using a Template

```ini
define host {
    use         linux-server    ; inherit all values above
    host_name   web01
    alias       Web Server 01
    address     192.168.1.10
    ; override specific values here
    notification_period  24x7   ; override template's workhours
}
```

### Chaining Templates (Multiple Inheritance)

```ini
define host {
    use         linux-server,monitored-by-ops   ; comma-separated, left wins
    host_name   db01
    address     192.168.1.20
}
```

Values from the first named template take precedence over subsequent ones.

---

## Inheritance Behavior

### Simple Value Inheritance

A directive in the child **always overrides** the parent:

```
Parent:  check_interval  5
Child:   check_interval  10   → Result: 10
Child:   (not set)            → Result: 5 (inherited)
```

### Additive Inheritance

Use `+` prefix to **append** to a parent list rather than replace it:

```ini
define host {
    use            base-template
    contact_groups +extra-team    ; adds extra-team to whatever base-template has
}
```

### Null Value (Explicit Remove)

Use `null` to explicitly unset an inherited value:

```ini
define service {
    use             generic-service
    event_handler   null    ; explicitly disable inherited event handler
}
```

---

## Macros

Macros are placeholders in command definitions that Nagios replaces at runtime.

### Standard Host/Service Macros

| Macro | Value |
|-------|-------|
| `$HOSTNAME$` | Host's `host_name` |
| `$HOSTADDRESS$` | Host's IP/address |
| `$HOSTALIAS$` | Host's `alias` |
| `$HOSTSTATE$` | UP, DOWN, UNREACHABLE |
| `$SERVICESTATE$` | OK, WARNING, CRITICAL, UNKNOWN |
| `$SERVICEDESC$` | Service's `service_description` |
| `$SERVICEOUTPUT$` | First line of plugin output |
| `$LONGSERVICEOUTPUT$` | Full plugin output (all lines) |
| `$SERVICEPERFDATA$` | Performance data string |
| `$SERVICEATTEMPT$` | Current check attempt number |
| `$MAXSERVICEATTEMPTS$` | `max_check_attempts` value |
| `$SERVICESTATETYPE$` | SOFT or HARD |

### Time Macros

| Macro | Value |
|-------|-------|
| `$TIMET$` | Current Unix timestamp |
| `$LONGDATETIME$` | Human-readable date/time |
| `$SHORTDATETIME$` | Short date/time format |

### Contact Macros (in notification commands)

| Macro | Value |
|-------|-------|
| `$CONTACTNAME$` | Contact's `contact_name` |
| `$CONTACTEMAIL$` | Contact's `email` |
| `$CONTACTPAGER$` | Contact's `pager` |

### Argument Macros

`$ARG1$` through `$ARG32$` — set via `!` separators in `check_command`:

```ini
check_command  check_http!-w 2 -c 5   ; $ARG1$ = "-w 2 -c 5"
```

### User-Defined Macros (resource.cfg)

`$USER1$` through `$USER256$` — defined in `resource.cfg`:

```ini
$USER1$=/usr/local/nagios/libexec
$USER2$=my_db_password
```

---

## Time Periods

Time periods define when checks and notifications are active. Referenced by `check_period` and `notification_period` on hosts and services.

### Syntax

```ini
define timeperiod {
    timeperiod_name  24x7
    alias            24 Hours A Day, 7 Days A Week
    sunday           00:00-24:00
    monday           00:00-24:00
    tuesday          00:00-24:00
    wednesday        00:00-24:00
    thursday         00:00-24:00
    friday           00:00-24:00
    saturday         00:00-24:00
}

define timeperiod {
    timeperiod_name  workhours
    alias            Standard Work Hours
    monday           09:00-17:00
    tuesday          09:00-17:00
    wednesday        09:00-17:00
    thursday         09:00-17:00
    friday           09:00-17:00
}

define timeperiod {
    timeperiod_name  nonworkhours
    alias            After Hours
    use              24x7
    exclude          workhours    ; 24x7 minus workhours
}
```

### Using Time Periods

```ini
define service {
    check_period          24x7       ; check always
    notification_period   workhours  ; only notify during business hours
}
```

---

## Host Groups and Service Groups

### Host Groups — Logical Grouping for UI and Bulk Assignment

```ini
define hostgroup {
    hostgroup_name  web-servers
    alias           Web Servers
    members         web01,web02,web03
}

# Or use hostgroup_name in host definitions:
define host {
    host_name       web04
    hostgroups      web-servers,prod-servers
}
```

### Apply a Service to an Entire Hostgroup

```ini
define service {
    use                  generic-service
    hostgroup_name       web-servers      ; applies to all members
    service_description  HTTP
    check_command        check_http
}
```

### Service Groups

```ini
define servicegroup {
    servicegroup_name  web-checks
    alias             Web Service Checks
    members           web01,HTTP, web01,HTTPS, web02,HTTP
    ; format: host_name,service_description pairs
}
```

---

## Flapping Configuration

```ini
define service {
    flap_detection_enabled   1
    low_flap_threshold       20.0   ; % — stop flapping below this
    high_flap_threshold      30.0   ; % — start flapping above this
    flap_detection_options   o,w,c,u  ; states that count toward flap detection
}
```

Global defaults in nagios.cfg:

```ini
enable_flap_detection=1
low_service_flap_threshold=20.0
high_service_flap_threshold=30.0
```

---

## Dependency Configuration

### Service Dependencies

Prevent a service check or notification if a dependent service is in a problem state:

```ini
define servicedependency {
    host_name                       web01
    service_description             Apache
    dependent_host_name             web01
    dependent_service_description   HTTP
    execution_failure_criteria      w,u,c    ; don't run HTTP check if Apache is WARN/UNKNOWN/CRIT
    notification_failure_criteria   w,u,c    ; don't notify about HTTP if Apache already alerting
}
```

### Host Dependencies

```ini
define hostdependency {
    host_name              core-router
    dependent_host_name    web01
    notification_failure_criteria  d,u  ; suppress web01 DOWN if core-router is already down
}
```

---

## Practical Configuration Layout

For any environment beyond a handful of hosts, use a directory-based layout:

```
/usr/local/nagios/etc/
├── nagios.cfg         (cfg_dir=/usr/local/nagios/etc/servers/ etc.)
├── objects/
│   ├── commands.cfg
│   ├── contacts.cfg
│   ├── timeperiods.cfg
│   └── templates.cfg
└── servers/
    ├── web-servers.cfg
    ├── db-servers.cfg
    └── network-devices.cfg
```

One `.cfg` file per logical group keeps configs manageable as infrastructure scales.
