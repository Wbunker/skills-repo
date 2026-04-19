# Nagios Plugins
## Chapter 4: Standard Plugins, Check Commands, Resource Monitoring

---

## Plugin Basics

Every Nagios check is a plugin — an executable that:
1. Performs a check
2. Prints a one-line status message (optionally with `|perfdata`)
3. Exits with code 0/1/2/3

Plugins live in `/usr/local/nagios/libexec/`. Run them manually to test before adding to config.

```bash
/usr/local/nagios/libexec/check_http -H example.com -p 80
# HTTP OK: HTTP/1.1 200 OK - 1234 bytes in 0.123 second response time |time=0.123s;;;0.000000 size=1234B;;;0
```

---

## Network/Service Checks

### check_ping

```ini
define command {
    command_name  check_ping
    command_line  $USER1$/check_ping -H $HOSTADDRESS$ -w $ARG1$ -c $ARG2$ -p 5
}
# Usage: check_ping!100.0,20%!500.0,60%
# -w warn_rta,warn_loss%  -c crit_rta,crit_loss%
```

### check_http

```bash
# Basic HTTP check
check_http -H example.com

# Check specific URL path
check_http -H example.com -u /health

# HTTPS with SSL certificate check
check_http -H example.com --ssl -C 30
# -C 30 = warn if cert expires within 30 days

# Check response time
check_http -H example.com -w 2 -c 5
# -w warn secs  -c crit secs

# Check for string in response
check_http -H example.com -s "Welcome"

# Check with custom port
check_http -H example.com -p 8080
```

### check_tcp / check_udp

```bash
# Check any TCP port
check_tcp -H db.example.com -p 5432

# Check with expected banner
check_tcp -H smtp.example.com -p 25 -e "220"
```

### check_smtp

```bash
check_smtp -H mail.example.com
check_smtp -H mail.example.com -p 587 --starttls
```

### check_ftp

```bash
check_ftp -H ftp.example.com
```

### check_ssh

```bash
check_ssh -H server.example.com
check_ssh -p 2222 -H server.example.com
```

### check_dns

```bash
# Check DNS resolution
check_dns -H example.com -s 8.8.8.8

# Expect a specific result
check_dns -H example.com -a 93.184.216.34
```

---

## Database Checks

### check_mysql

```bash
check_mysql -H db.example.com -u nagios -p secretpass -d nagios

# Check MySQL slave replication lag
check_mysql_slave -H db-slave.example.com -u nagios -p secretpass
```

### check_pgsql

```bash
check_pgsql -H pg.example.com -u nagios -p secretpass -d mydb
```

### check_oracle

Available via `nagios-plugins-oracle` or custom JDBC plugins.

---

## System Resource Checks

### check_disk

```bash
# Check disk space on local partition
check_disk -w 20% -c 10% -p /

# Check multiple partitions
check_disk -w 20% -c 10% -p / -p /var -p /tmp

# Absolute threshold (MB)
check_disk -w 1000 -c 500 -p /data
```

### check_load

```bash
# 1min, 5min, 15min averages
check_load -w 15,10,5 -c 30,25,20
```

### check_procs

```bash
# Ensure httpd is running (at least 1 process)
check_procs -w 1: -c 1: -C httpd

# Ensure not too many zombie processes
check_procs -w 5 -c 10 -s Z

# Exact count
check_procs -w 3:6 -c 2:8 -C nginx
```

### check_users

```bash
# Alert on excessive logged-in users
check_users -w 5 -c 10
```

### check_swap

```bash
check_swap -w 20% -c 10%
# Warns if less than 20% swap free
```

### Memory (no official plugin — common approaches)

```bash
# Option 1: check_mem.pl (community plugin)
check_mem.pl -w 80 -c 90

# Option 2: check_nrpe to run check_mem on remote host
# Option 3: Custom script reading /proc/meminfo
```

---

## Disk Hardware Checks

### check_smart (via smartmontools)

```bash
# Check SMART status of a disk
check_smart -d /dev/sda

# Requires root or sudoers entry for nagios user
```

### check_raid

Available via community plugins (e.g., `check_md_raid` for Linux software RAID):

```bash
check_md_raid
```

---

## Remote File Share Checks

### check_disk for NFS/CIFS

```bash
# Check NFS mount (must be already mounted)
check_disk -w 20% -c 10% -p /mnt/nfs-share
```

### check_nfs (community)

```bash
check_nfs -H nfs-server.example.com -e /exports/data
```

---

## Plugin Arguments in Service Definitions

Arguments are passed via `check_command` using `!` separators:

```ini
define service {
    service_description  HTTP
    check_command        check_http!-w 2 -c 5 -H $HOSTADDRESS$ -u /health
}

define command {
    command_name  check_http
    command_line  $USER1$/check_http $ARG1$
}
```

Or with positional `$ARG1$`, `$ARG2$`:

```ini
define command {
    command_name  check_disk
    command_line  $USER1$/check_disk -w $ARG1$ -c $ARG2$ -p $ARG3$
}

define service {
    service_description  Disk /
    check_command        check_disk!20%!10%!/
}
```

---

## Resource Macros (resource.cfg)

Store sensitive values (credentials, paths) in `resource.cfg` instead of object files:

```ini
# /usr/local/nagios/etc/resource.cfg
$USER1$=/usr/local/nagios/libexec
$USER2$=nagiosuser
$USER3$=secretpassword
```

Then use in commands:
```ini
command_line  $USER1$/check_mysql -u $USER2$ -p $USER3$ -H $HOSTADDRESS$
```

`resource.cfg` is not exposed via the web interface — good for credentials.

---

## Writing a Quick Custom Plugin

```bash
#!/bin/bash
# check_example.sh
THRESHOLD_WARN=$1
THRESHOLD_CRIT=$2

VALUE=$(some_command_that_returns_a_number)

if [ "$VALUE" -ge "$THRESHOLD_CRIT" ]; then
    echo "CRITICAL - value is $VALUE | value=$VALUE;$THRESHOLD_WARN;$THRESHOLD_CRIT"
    exit 2
elif [ "$VALUE" -ge "$THRESHOLD_WARN" ]; then
    echo "WARNING - value is $VALUE | value=$VALUE;$THRESHOLD_WARN;$THRESHOLD_CRIT"
    exit 1
else
    echo "OK - value is $VALUE | value=$VALUE;$THRESHOLD_WARN;$THRESHOLD_CRIT"
    exit 0
fi
```

See [programming.md](programming.md) for full plugin development guidance.

---

## Plugin Testing Workflow

```bash
# 1. Test manually as the nagios user
sudo -u nagios /usr/local/nagios/libexec/check_http -H example.com

# 2. Verify exit code
echo $?

# 3. Add to command definition
# 4. Add service definition using the command
# 5. Reload Nagios
nagios -v /usr/local/nagios/etc/nagios.cfg && systemctl reload nagios

# 6. Check result in web UI or status.dat
```
