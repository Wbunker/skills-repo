# Nagios Web Interface
## Chapter 3: Web UI Setup, Apache Config, Users, CGIs

---

## Architecture

The Nagios web interface is CGI-based. Apache (or another web server) executes CGI programs in `/usr/local/nagios/sbin/` that read `status.dat` and `nagios.log` to render pages.

```
Browser → Apache → CGI programs (sbin/) → status.dat / nagios.log
                      ↓
                   cgi.cfg (controls access and display)
```

---

## Apache Configuration

### Install Apache Config (source install)

```bash
sudo make install-webconf
# Creates /etc/apache2/conf-enabled/nagios.conf  (Debian)
# or /etc/httpd/conf.d/nagios.conf  (RHEL)
```

### Manual Apache Config (if needed)

```apache
ScriptAlias /nagios/cgi-bin "/usr/local/nagios/sbin"
<Directory "/usr/local/nagios/sbin">
    Options ExecCGI
    AllowOverride None
    Order allow,deny
    Allow from all
    AuthName "Nagios Access"
    AuthType Basic
    AuthUserFile /usr/local/nagios/etc/htpasswd.users
    Require valid-user
</Directory>

Alias /nagios "/usr/local/nagios/share"
<Directory "/usr/local/nagios/share">
    Options None
    AllowOverride None
    Order allow,deny
    Allow from all
    AuthName "Nagios Access"
    AuthType Basic
    AuthUserFile /usr/local/nagios/etc/htpasswd.users
    Require valid-user
</Directory>
```

### Enable CGI Module

```bash
# Apache 2.4 on Debian/Ubuntu
a2enmod cgi
service apache2 restart

# RHEL — CGI is typically already enabled
```

---

## Creating Administrative Users

### Add First User

```bash
htpasswd -c /usr/local/nagios/etc/htpasswd.users nagiosadmin
# -c creates the file; omit -c for subsequent users
```

### Add Additional Users

```bash
htpasswd /usr/local/nagios/etc/htpasswd.users operator1
```

### Remove a User

```bash
htpasswd -D /usr/local/nagios/etc/htpasswd.users olduser
```

---

## cgi.cfg — Access Control

`cgi.cfg` controls who can see and control what in the web interface.

### Key Directives

```ini
# Who can see all hosts/services
authorized_for_all_hosts=nagiosadmin
authorized_for_all_services=nagiosadmin

# Who can view system information (process info, performance)
authorized_for_system_information=nagiosadmin

# Who can issue commands (acknowledge, schedule downtime, etc.)
authorized_for_all_host_commands=nagiosadmin
authorized_for_all_service_commands=nagiosadmin

# Who can view configuration data
authorized_for_configuration_information=nagiosadmin

# Read-only user (can see everything but issue no commands)
authorized_for_all_hosts=nagiosadmin,readonly_user
```

### Per-Object Authorization

Alternatively, assign contacts directly to hosts/services:

```ini
define host {
    host_name   web01
    contacts    nagiosadmin,ops-team
}
```

Users listed as contacts automatically have view access to that host and its services.

---

## CGI Programs

| CGI | URL path | Function |
|-----|----------|----------|
| `status.cgi` | `/nagios/cgi-bin/status.cgi` | Main status overview — hosts and services |
| `statusmap.cgi` | `/nagios/cgi-bin/statusmap.cgi` | Network topology map |
| `history.cgi` | `/nagios/cgi-bin/history.cgi` | Alert history |
| `notifications.cgi` | `/nagios/cgi-bin/notifications.cgi` | Notification log |
| `outages.cgi` | `/nagios/cgi-bin/outages.cgi` | Current network outages |
| `config.cgi` | `/nagios/cgi-bin/config.cgi` | View current configuration |
| `extinfo.cgi` | `/nagios/cgi-bin/extinfo.cgi` | Extended info for hosts/services |
| `cmd.cgi` | `/nagios/cgi-bin/cmd.cgi` | Issue external commands |
| `tac.cgi` | `/nagios/cgi-bin/tac.cgi` | Tactical overview dashboard |

### Default URL

`http://<server>/nagios/`

---

## Common Web Interface Actions

### Acknowledge a Problem

1. Click on the problem host/service
2. Click **Acknowledge this service problem**
3. Enter a comment; optionally enable sticky/notify
4. Submit

Via command pipe:
```bash
echo "[$(date +%s)] ACKNOWLEDGE_SVC_PROBLEM;web01;HTTP;1;1;1;nagiosadmin;Investigating" > /usr/local/nagios/var/rw/nagios.cmd
```

### Schedule Downtime

1. Navigate to host/service
2. Click **Schedule downtime for this service**
3. Set start/end times and comment
4. Submit — Nagios suppresses notifications during the window

### Force Immediate Check

1. Click on the service
2. Click **Re-schedule the next check** → set to now
3. Or use **Run check command** from the service detail page

---

## Troubleshooting the Web Interface

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| 403 Forbidden | CGI module not enabled or wrong permissions | `a2enmod cgi`, check directory permissions |
| 500 Internal Server Error | CGI program not executable | `chmod +x /usr/local/nagios/sbin/*.cgi` |
| Login prompt loops | Wrong htpasswd file path in Apache config | Verify `AuthUserFile` path |
| "You are not authorized" | User not in cgi.cfg authorized lists | Add user to appropriate `authorized_for_*` lines |
| Blank page | Apache CGI not finding status.dat | Check `status_file=` in nagios.cfg matches what CGIs expect |

### Verify Apache Can Execute CGIs

```bash
ls -la /usr/local/nagios/sbin/
# All .cgi files should be executable (-rwxr-xr-x)
```

### Check Apache Error Log

```bash
tail -f /var/log/apache2/error.log   # Debian
tail -f /var/log/httpd/error_log     # RHEL
```

---

## Third-Party Web Interfaces

| Tool | Description |
|------|-------------|
| **Thruk** | Feature-rich drop-in replacement UI; supports multiple backends |
| **Naemon** | Nagios core fork with improved web UI (Thruk-based) |
| **Check_MK** | Extended monitoring platform with its own UI built on Nagios |
| **NagVis** | Customizable status maps (floor plans, geographic maps) |
| **PNP4Nagios** | Performance data graphing using RRDtool |

### Command-Line Alternatives

```bash
# nagiostats — live performance statistics
/usr/local/nagios/bin/nagiostats

# Read status.dat directly
grep "service_description\|current_state" /usr/local/nagios/var/status.dat | head -40
```
