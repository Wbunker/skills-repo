# Passive Checks and NSCA
## Chapter 7: Passive Check Model, NSCA, Freshness, Obsessive Processing

---

## Active vs. Passive Checks

| | Active | Passive |
|---|--------|---------|
| **Initiator** | Nagios scheduler | External system or script |
| **Timing** | Scheduled by Nagios | Whenever the external system decides |
| **Direction** | Nagios → target | Target → Nagios |
| **Use case** | Standard polling | Event-driven, batch jobs, distributed Nagios |

Passive checks allow Nagios to receive results rather than initiate them. Useful when:
- Nagios cannot reach the host (firewall, NAT)
- A batch job should report its own completion status
- Results come from another monitoring system
- A process reports state changes immediately (event-driven) rather than waiting for the next poll

---

## Enabling Passive Checks

### In nagios.cfg

```ini
accept_passive_service_checks=1
accept_passive_host_checks=1
```

### In Service Definition

```ini
define service {
    host_name               batch-server
    service_description     Nightly Backup
    active_checks_enabled   0     ; disable active checks
    passive_checks_enabled  1     ; accept passive results
    check_command           check_dummy!0!Waiting for result
    ; check_dummy always returns OK — used as placeholder for purely passive services
    check_freshness         1
    freshness_threshold     86400  ; 24 hours in seconds
    ...
}
```

---

## Submitting Passive Check Results

### Via External Command Pipe (local)

```bash
# Submit a service check result
NOW=$(date +%s)
echo "[$NOW] PROCESS_SERVICE_CHECK_RESULT;hostname;service_desc;return_code;output" \
  > /usr/local/nagios/var/rw/nagios.cmd

# Return codes: 0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN
echo "[$NOW] PROCESS_SERVICE_CHECK_RESULT;batch01;Nightly Backup;0;Backup completed: 120GB" \
  > /usr/local/nagios/var/rw/nagios.cmd

# Submit a host check result
echo "[$NOW] PROCESS_HOST_CHECK_RESULT;batch01;0;Host is up and reporting" \
  > /usr/local/nagios/var/rw/nagios.cmd
```

---

## NSCA (Nagios Service Check Acceptor)

NSCA is a daemon that listens for encrypted passive check results over the network and injects them into Nagios via the command pipe.

```
Remote host/script                 Nagios server
     │                                  │
     │  send_nsca (encrypted)           │
     │─────────────────────────────────►│
                                        │  nsca daemon
                                        │  decrypts + validates
                                        │  writes to nagios.cmd
```

### Installing NSCA

```bash
# From source
wget https://github.com/NagiosEnterprises/nsca/archive/nsca-2.x.x.tar.gz
tar xzf nsca-2.x.x.tar.gz
cd nsca-2.x.x
./configure
make
sudo make install    # installs nsca daemon and send_nsca client
```

### nsca.cfg (server side)

```ini
# /usr/local/nagios/etc/nsca.cfg
server_port=5667
nsca_user=nagios
nsca_group=nagios
command_file=/usr/local/nagios/var/rw/nagios.cmd
password=mysecretpassword
decryption_method=8    ; 8 = 256-bit AES
```

### Start NSCA Daemon

```bash
/usr/local/nagios/bin/nsca -c /usr/local/nagios/etc/nsca.cfg --daemon

# Or via xinetd (traditional approach):
# Add /etc/xinetd.d/nsca entry to run nsca per-connection
```

### Firewall

```bash
# Allow NSCA port through firewall
iptables -A INPUT -p tcp --dport 5667 -j ACCEPT
```

---

## send_nsca (client)

Used on remote systems to submit passive check results to the NSCA daemon.

### send_nsca.cfg (client side)

```ini
# /etc/nagios/send_nsca.cfg
password=mysecretpassword
encryption_method=8    ; must match server
```

### Sending a Result

```bash
# Format: hostname\tservice_desc\treturn_code\toutput\n
printf "batch01\tNightly Backup\t0\tBackup OK: 120GB transferred\n" | \
  /usr/local/nagios/bin/send_nsca -H nagios-server.example.com \
    -c /etc/nagios/send_nsca.cfg

# Multiple results in one call (max_packet_age default is 30 seconds)
printf "host1\tHTTP\t0\tHTTP OK\nhost1\tDisk\t1\tDisk 85%% used\n" | \
  /usr/local/nagios/bin/send_nsca -H nagios.example.com -c /etc/nagios/send_nsca.cfg
```

---

## Freshness Checking

Without freshness checking, a passive-only service that stops sending results will remain in its last known state forever — potentially showing OK when it's actually dead.

**Freshness checking** detects stale passive results and triggers an active check or raises an alert.

### Configuration

```ini
# nagios.cfg
check_service_freshness=1
check_host_freshness=1
service_freshness_check_interval=60   ; how often to check freshness (seconds)
```

```ini
define service {
    host_name               batch01
    service_description     Nightly Backup
    active_checks_enabled   0
    passive_checks_enabled  1
    check_freshness         1
    freshness_threshold     90000     ; seconds — 25 hours
    check_command           check_dummy!2!No backup result received in 25 hours!
}
```

When the passive result is older than `freshness_threshold`:
- Nagios forces an active check using `check_command`
- Using `check_dummy!2!...` returns CRITICAL immediately, alerting on the stale result

---

## Obsessive Processing

**Obsessive processing** = forwarding all check results (active AND passive) to an external command for processing.

Useful for:
- Forwarding results to a central Nagios instance (distributed monitoring)
- Feeding results to an external event processor or CMDB

### Enable Obsessive Processing

```ini
# nagios.cfg
obsess_over_services=1
obsess_over_hosts=1

ocsp_command=submit-to-central-nagios   ; "Obsessive Compulsive Service Processor"
ochp_command=submit-host-to-central     ; "Obsessive Compulsive Host Processor"
```

### Example OCSP Command

```ini
define command {
    command_name  submit-to-central-nagios
    command_line  /usr/local/nagios/libexec/eventhandlers/submit_check_result \
      $HOSTNAME$ '$SERVICEDESC$' $SERVICESTATE$ '$SERVICEOUTPUT$'
}
```

The `submit_check_result` script calls `send_nsca` to forward results to the central server.

---

## Passive Check Use Cases

### Cron Job Monitoring

```bash
#!/bin/bash
# In cron job — report result to Nagios at end of job
run_backup && STATUS=0 && MSG="Backup OK" || STATUS=2 && MSG="Backup FAILED"

printf "$(hostname)\tNightly Backup\t$STATUS\t$MSG\n" | \
  /usr/local/nagios/bin/send_nsca -H nagios.example.com -c /etc/nagios/send_nsca.cfg
```

### Application Health Reports

Application sends passive check results when its internal health check detects issues — more timely than Nagios polling:

```python
import subprocess
result = check_db_connection()
status = 0 if result.ok else 2
msg = "DB OK" if result.ok else f"DB FAIL: {result.error}"
subprocess.run(
    ["send_nsca", "-H", "nagios.example.com", "-c", "/etc/nagios/send_nsca.cfg"],
    input=f"appserver01\tDB Connection\t{status}\t{msg}\n",
    text=True
)
```
