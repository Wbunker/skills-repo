# Notifications and Events
## Chapter 6: Notification System, Contacts, Escalations, On-Call Rotations

---

## How Notifications Work

Nagios sends notifications when:
1. A host/service enters a **hard** problem state
2. A hard problem is **resolved** (recovery)
3. An **acknowledgement** is posted (optional)
4. A **flap** starts or stops (optional)
5. **Scheduled downtime** starts or ends (optional)

### Notification Decision Flow

```
Hard state change or recovery
         │
         ▼
Is notification_period current?  No → skip
         │Yes
         ▼
Are notifications globally enabled (nagios.cfg)?  No → skip
         │Yes
         ▼
Are notifications enabled on host/service?  No → skip
         │Yes
         ▼
Is host/service in scheduled downtime?  Yes → skip
         │No
         ▼
Is problem acknowledged?  Yes → skip (unless sticky=0 or new state)
         │No
         ▼
Do contact's notification_options match current state?  No → skip
         │Yes
         ▼
Is notification_interval elapsed since last notification?  No → skip
         │Yes
         ▼
Check escalation rules → resolve contact list
         │
         ▼
Execute notification_command for each contact
```

---

## Contact Configuration

```ini
define contact {
    contact_name                  nagiosadmin
    alias                         Nagios Admin
    use                           generic-contact
    email                         admin@example.com
    pager                         5551234567@sms-gateway.example.com

    ; When to notify for services
    service_notification_period   24x7
    service_notification_options  w,u,c,r,f    ; warning,unknown,critical,recovery,flap
    service_notification_commands notify-service-by-email

    ; When to notify for hosts
    host_notification_period      24x7
    host_notification_options     d,u,r,f      ; down,unreachable,recovery,flap
    host_notification_commands    notify-host-by-email
}
```

### Notification Options Reference

**Service states:**

| Option | State |
|--------|-------|
| `w` | WARNING |
| `u` | UNKNOWN |
| `c` | CRITICAL |
| `r` | RECOVERY (OK after problem) |
| `f` | Flapping start/stop |
| `s` | Scheduled downtime start/stop |
| `n` | None (disable all notifications) |

**Host states:**

| Option | State |
|--------|-------|
| `d` | DOWN |
| `u` | UNREACHABLE |
| `r` | RECOVERY |
| `f` | Flapping |
| `s` | Scheduled downtime |
| `n` | None |

---

## Notification Commands

### Email (default)

```ini
define command {
    command_name  notify-service-by-email
    command_line  /usr/bin/printf "%b" "***** Nagios *****\n\nNotification Type: $NOTIFICATIONTYPE$\n\nService: $SERVICEDESC$\nHost: $HOSTALIAS$\nAddress: $HOSTADDRESS$\nState: $SERVICESTATE$\n\nDate/Time: $LONGDATETIME$\n\nAdditional Info:\n\n$SERVICEOUTPUT$" | /bin/mail -s "** $NOTIFICATIONTYPE$ Service Alert: $HOSTALIAS$/$SERVICEDESC$ is $SERVICESTATE$ **" $CONTACTEMAIL$
}

define command {
    command_name  notify-host-by-email
    command_line  /usr/bin/printf "%b" "***** Nagios *****\n\nNotification Type: $NOTIFICATIONTYPE$\n\nHost: $HOSTNAME$\nState: $HOSTSTATE$\nAddress: $HOSTADDRESS$\n\nDate/Time: $LONGDATETIME$\n\nAdditional Info:\n\n$HOSTOUTPUT$" | /bin/mail -s "** $NOTIFICATIONTYPE$ Host Alert: $HOSTNAME$ is $HOSTSTATE$ **" $CONTACTEMAIL$
}
```

### SMS via pager field

```ini
define command {
    command_name  notify-service-by-sms
    command_line  /usr/local/bin/send-sms "$CONTACTPAGER$" "$HOSTNAME$/$SERVICEDESC$ $SERVICESTATE$: $SERVICEOUTPUT$"
}
```

### Webhook (curl)

```ini
define command {
    command_name  notify-service-by-webhook
    command_line  /usr/bin/curl -s -X POST https://hooks.slack.com/... \
      -H 'Content-type: application/json' \
      --data '{"text":"$HOSTNAME$: $SERVICEDESC$ is $SERVICESTATE$"}'
}
```

### Multiple Notification Commands Per Contact

```ini
define contact {
    contact_name                  oncall
    service_notification_commands notify-service-by-email,notify-service-by-sms
}
```

---

## Contact Groups

```ini
define contactgroup {
    contactgroup_name  admins
    alias              System Administrators
    members            nagiosadmin,ops1,ops2
}

define contactgroup {
    contactgroup_name  dba-team
    alias              Database Administrators
    members            dba1,dba2
}
```

Assign contact groups to hosts/services:

```ini
define host {
    host_name      db01
    contact_groups admins,dba-team
}
```

---

## Notification Intervals

```ini
define service {
    notification_interval  60    ; re-notify every 60 minutes while problem persists
    ; 0 = notify once only (no re-notification)
}
```

The first notification fires when the hard state is entered. Subsequent notifications fire every `notification_interval` minutes until:
- The problem recovers
- The problem is acknowledged with sticky=1
- Notifications are disabled

---

## Escalations

Escalations define **additional contacts** to notify if a problem persists beyond a certain number of notifications or time.

### Service Escalation

```ini
define serviceescalation {
    host_name               web01
    service_description     HTTP
    contact_groups          level2-team
    first_notification      3     ; start escalating after 3rd notification
    last_notification       0     ; 0 = escalate indefinitely
    notification_interval   60    ; re-escalation interval
    escalation_period       24x7
    escalation_options      w,c,u ; which states trigger this escalation
}
```

### Host Escalation

```ini
define hostescalation {
    host_name               db01
    contact_groups          management
    first_notification      5
    last_notification       0
    notification_interval   120
}
```

### Escalation Logic

- `first_notification N` — escalation kicks in on the Nth notification (not Nth hard attempt)
- `last_notification 0` — escalation continues indefinitely
- Nagios merges the base contact list with escalation contacts when escalation conditions are met
- Multiple escalation entries can be stacked (e.g., escalate to level 2 on notification 3, to management on notification 5)

---

## On-Call Rotations

Implement on-call rotations using time periods:

```ini
define timeperiod {
    timeperiod_name  week-even
    monday           00:00-24:00
    tuesday          00:00-24:00
    wednesday        00:00-24:00
    thursday         00:00-24:00
    friday           00:00-24:00
    saturday         00:00-24:00
    sunday           00:00-24:00
    ; Use calendar dates to define alternating weeks:
    2024-01-08 / 14  00:00-24:00  ; every 14 days starting 2024-01-08
}

define contact {
    contact_name                  oncall-a
    service_notification_period   week-even
    host_notification_period      week-even
    ...
}

define contact {
    contact_name                  oncall-b
    service_notification_period   week-odd
    host_notification_period      week-odd
    ...
}

define contactgroup {
    contactgroup_name  on-call-rotation
    members            oncall-a,oncall-b
}
```

Nagios checks each contact's `notification_period` at notification time — only contacts whose period is currently active receive the notification.

---

## Acknowledgements

Acknowledging a problem suppresses future re-notifications until the problem state changes.

| Acknowledge Option | Effect |
|-------------------|--------|
| Sticky (checked) | Notification suppression survives state changes within the problem |
| Non-sticky | Suppression lifts if state changes (e.g., CRIT → WARN) |
| Persistent comment | Comment stays even after acknowledgement expires |
| Notify contacts | Sends an acknowledgement notification to contacts |

Via command pipe:

```bash
# Acknowledge service problem
NOW=$(date +%s)
echo "[$NOW] ACKNOWLEDGE_SVC_PROBLEM;web01;HTTP;1;1;1;admin;Investigating issue" \
  > /usr/local/nagios/var/rw/nagios.cmd
# Format: host_name;svc_desc;sticky;notify;persistent;author;comment
```

---

## Scheduled Downtime

During scheduled downtime:
- Checks continue to run
- Problem notifications are suppressed
- A downtime notification is sent at start and end

```bash
# Schedule 2-hour downtime starting now
NOW=$(date +%s)
END=$((NOW + 7200))
echo "[$NOW] SCHEDULE_SVC_DOWNTIME;web01;HTTP;$NOW;$END;1;0;7200;admin;Deployment window" \
  > /usr/local/nagios/var/rw/nagios.cmd
```
