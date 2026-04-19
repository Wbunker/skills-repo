# Nagios Installation
## Chapter 2: Installing Nagios 4 from Source and Packages

---

## Installation Methods

| Method | Best For |
|--------|----------|
| **Compile from source** | Latest version, full control, custom paths |
| **Package manager** | Ease of install, system integration, distro-managed updates |

---

## Compile from Source (Recommended for Full Control)

### Prerequisites

```bash
# RHEL/CentOS/Fedora
yum install -y gcc glibc glibc-common gd gd-devel make net-snmp openssl-devel

# Debian/Ubuntu
apt-get install -y build-essential libgd-dev libssl-dev libnet-snmp-perl
```

### Users and Groups

Nagios requires a dedicated system user and group:

```bash
useradd -m -s /bin/bash nagios
groupadd nagcmd
usermod -aG nagcmd nagios
usermod -aG nagcmd www-data   # or apache, nginx — web server user
```

### Download and Compile Nagios Core

```bash
cd /tmp
wget https://github.com/NagiosEnterprises/nagioscore/archive/nagios-4.x.x.tar.gz
tar xzf nagios-4.x.x.tar.gz
cd nagioscore-nagios-4.x.x

./configure --with-nagios-group=nagios --with-command-group=nagcmd
make all
sudo make install          # installs binaries
sudo make install-init     # installs init script
sudo make install-commandmode  # sets permissions on command pipe
sudo make install-config   # installs sample config files
sudo make install-webconf  # installs Apache config
```

### Install Nagios Plugins

```bash
cd /tmp
wget https://nagios-plugins.org/download/nagios-plugins-2.x.x.tar.gz
tar xzf nagios-plugins-2.x.x.tar.gz
cd nagios-plugins-2.x.x

./configure --with-nagios-user=nagios --with-nagios-group=nagios
make
sudo make install
```

Plugins install to `/usr/local/nagios/libexec/`.

---

## Package Installation

### RHEL/CentOS (EPEL)

```bash
yum install -y epel-release
yum install -y nagios nagios-plugins-all
```

### Debian/Ubuntu

```bash
apt-get install -y nagios4 nagios-plugins
```

Package paths differ from source installs:
- Config: `/etc/nagios4/` (Debian) vs `/etc/nagios/` (RHEL)
- Plugins: `/usr/lib/nagios/plugins/`
- Logs: `/var/log/nagios4/`

---

## Initial Configuration

### nagios.cfg — Main Config

Key directives to verify after install:

```ini
# nagios.cfg
log_file=/usr/local/nagios/var/nagios.log
cfg_file=/usr/local/nagios/etc/objects/commands.cfg
cfg_file=/usr/local/nagios/etc/objects/contacts.cfg
cfg_file=/usr/local/nagios/etc/objects/timeperiods.cfg
cfg_file=/usr/local/nagios/etc/objects/templates.cfg
cfg_dir=/usr/local/nagios/etc/servers/   # load all .cfg in this dir

check_external_commands=1
command_file=/usr/local/nagios/var/rw/nagios.cmd

nagios_user=nagios
nagios_group=nagios
```

### Minimal contacts.cfg

```ini
define contact {
    contact_name                    nagiosadmin
    use                             generic-contact
    alias                           Nagios Admin
    email                           admin@example.com
}

define contactgroup {
    contactgroup_name               admins
    alias                           Nagios Administrators
    members                         nagiosadmin
}
```

### Minimal localhost.cfg

```ini
define host {
    use                             linux-server
    host_name                       localhost
    alias                           localhost
    address                         127.0.0.1
    max_check_attempts              5
    check_period                    24x7
    notification_interval           30
    notification_period             24x7
}

define service {
    use                             generic-service
    host_name                       localhost
    service_description             PING
    check_command                   check_ping!100.0,20%!500.0,60%
}
```

---

## Verifying Configuration

**Always verify config before starting/reloading Nagios:**

```bash
/usr/local/nagios/bin/nagios -v /usr/local/nagios/etc/nagios.cfg
```

Output:
```
Total Warnings: 0
Total Errors:   0
Things look okay - No serious problems were detected during the pre-flight check
```

Common errors:
- Missing referenced objects (e.g., undefined contact in contactgroup)
- Circular template inheritance
- Duplicate object names
- Missing required directives (e.g., `check_command` on a service)

---

## Service Management

### systemd (modern distros)

```bash
systemctl enable nagios
systemctl start nagios
systemctl status nagios
systemctl reload nagios   # reload config without restart (sends SIGHUP)
```

### SysV init

```bash
service nagios start
service nagios reload
/etc/init.d/nagios checkconfig
```

### Manual reload (signal)

```bash
kill -HUP $(cat /usr/local/nagios/var/nagios.lock)
```

---

## Directory Structure (Source Install)

```
/usr/local/nagios/
├── bin/
│   └── nagios            ← main daemon
├── etc/
│   ├── nagios.cfg        ← main config
│   ├── cgi.cfg           ← web interface config
│   └── objects/          ← host/service/command definitions
├── libexec/              ← check_* plugins
├── sbin/                 ← CGI programs
├── share/                ← web interface files
└── var/
    ├── nagios.log
    ├── status.dat
    ├── nagios.lock       ← PID file
    └── rw/
        └── nagios.cmd    ← external command FIFO
```

---

## Upgrading Nagios

```bash
# Stop nagios, compile new version, then:
make install              # overwrites binaries only
# Config files are NOT overwritten by make install
systemctl restart nagios
```

Always run `nagios -v` after upgrading to catch config compatibility issues.
