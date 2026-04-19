# Monitoring Remote Hosts
## Chapter 8: NRPE, SSH-Based Checks, Remote Plugin Execution

---

## The Remote Monitoring Problem

Nagios plugins run **on the Nagios server**. For local checks (disk, CPU, memory) on remote hosts, you need a way to execute plugins on those hosts and return results.

Two approaches:
1. **NRPE** — lightweight daemon on the remote host; Nagios calls it over TCP
2. **SSH** — execute plugin remotely via SSH; no extra daemon needed

---

## NRPE (Nagios Remote Plugin Executor)

NRPE runs as a daemon on the monitored host. The Nagios server uses `check_nrpe` to ask NRPE to run a local plugin and return the result.

```
Nagios server                    Remote host
     │                                │
     │  check_nrpe (TCP 5666)         │
     │───────────────────────────────►│  nrpe daemon
     │◄───────────────────────────────│  runs plugin locally
     │  exit code + output            │
```

### Installing NRPE on the Remote Host

```bash
# From source (on each monitored host)
wget https://github.com/NagiosEnterprises/nrpe/archive/nrpe-4.x.x.tar.gz
tar xzf nrpe-4.x.x.tar.gz
cd nrpe-4.x.x

./configure --enable-command-args   # allow argument passing from Nagios
make all
sudo make install-groups-users  # creates nagios user/group
sudo make install
sudo make install-config        # installs /usr/local/nagios/etc/nrpe.cfg
sudo make install-init          # installs init script
```

Also install Nagios plugins on the remote host:

```bash
# Install plugins on each monitored host
cd nagios-plugins-2.x.x
./configure --with-nagios-user=nagios --with-nagios-group=nagios
make && sudo make install
```

### nrpe.cfg (remote host)

```ini
# /usr/local/nagios/etc/nrpe.cfg

server_port=5666
nrpe_user=nagios
nrpe_group=nagios

# SECURITY: restrict which servers can connect
allowed_hosts=127.0.0.1,192.168.1.50   # Nagios server IP

# Allow arguments from Nagios server (requires --enable-command-args at compile)
dont_blame_nrpe=1

# Define checks
command[check_users]=/usr/local/nagios/libexec/check_users -w 5 -c 10
command[check_load]=/usr/local/nagios/libexec/check_load -w 15,10,5 -c 30,25,20
command[check_disk]=/usr/local/nagios/libexec/check_disk -w 20% -c 10% -p /
command[check_zombie_procs]=/usr/local/nagios/libexec/check_procs -w 5 -c 10 -s Z
command[check_total_procs]=/usr/local/nagios/libexec/check_procs -w 150 -c 200
command[check_swap]=/usr/local/nagios/libexec/check_swap -w 20 -c 10

# With arguments enabled (dont_blame_nrpe=1):
command[check_disk_args]=/usr/local/nagios/libexec/check_disk -w $ARG1$ -c $ARG2$ -p $ARG3$
```

### Start NRPE

```bash
systemctl enable nrpe
systemctl start nrpe
```

### Firewall on Remote Host

```bash
iptables -A INPUT -p tcp --dport 5666 -s 192.168.1.50 -j ACCEPT
```

---

## check_nrpe (Nagios Server Side)

Install `check_nrpe` on the Nagios server (not the remote host):

```bash
cd nrpe-4.x.x
make check_nrpe
sudo make install-plugin   # installs check_nrpe to libexec
```

### Test Connection

```bash
# Run from Nagios server
/usr/local/nagios/libexec/check_nrpe -H remote-host.example.com -c check_load
# Expected: OK - load average: 0.05, 0.03, 0.01|load1=0.05...
```

### Command Definition

```ini
define command {
    command_name  check_nrpe
    command_line  $USER1$/check_nrpe -H $HOSTADDRESS$ -c $ARG1$
}

# With arguments:
define command {
    command_name  check_nrpe_args
    command_line  $USER1$/check_nrpe -H $HOSTADDRESS$ -c $ARG1$ -a $ARG2$
}
```

### Service Definitions Using NRPE

```ini
define service {
    use                  generic-service
    host_name            web01
    service_description  Current Load
    check_command        check_nrpe!check_load
}

define service {
    use                  generic-service
    host_name            web01
    service_description  Disk /
    check_command        check_nrpe_args!check_disk_args!20%!10%!/
}
```

---

## NRPE with SSL

NRPE supports SSL (enabled by default in recent versions). Both sides must have SSL compiled in:

```bash
./configure --with-ssl=/usr/bin/openssl --with-ssl-lib=/usr/lib
```

SSL certificates can be:
- **Auto-generated** (default) — self-signed certs per daemon
- **Custom CA** — deploy your own CA-signed certs for mutual authentication

---

## SSH-Based Remote Checks (check_by_ssh)

Alternative to NRPE: execute plugins on remote hosts via SSH without installing any extra daemon.

### Requirements

- SSH daemon running on remote host
- Nagios user's public key deployed to remote host's `~nagios/.ssh/authorized_keys`
- The plugin must be installed on the remote host

### Setup SSH Key Authentication

```bash
# On Nagios server — generate key for nagios user
sudo -u nagios ssh-keygen -t rsa -b 4096 -N "" -f /usr/local/nagios/.ssh/id_rsa

# Copy public key to remote host
sudo -u nagios ssh-copy-id -i /usr/local/nagios/.ssh/id_rsa.pub nagios@remote-host.example.com

# Or manually append:
cat /usr/local/nagios/.ssh/id_rsa.pub | ssh user@remote-host "cat >> /home/nagios/.ssh/authorized_keys"

# Test
sudo -u nagios ssh nagios@remote-host.example.com /usr/local/nagios/libexec/check_disk -w 20% -c 10% -p /
```

### Command Definition

```ini
define command {
    command_name  check_by_ssh
    command_line  $USER1$/check_by_ssh -H $HOSTADDRESS$ -C "$ARG1$"
}
```

### Service Definitions Using SSH

```ini
define service {
    use                  generic-service
    host_name            web01
    service_description  Disk /
    check_command        check_by_ssh!/usr/local/nagios/libexec/check_disk -w 20% -c 10% -p /
}
```

---

## NRPE vs. SSH Comparison

| Factor | NRPE | check_by_ssh |
|--------|------|--------------|
| **Performance** | Faster (dedicated socket) | Slower (SSH handshake overhead) |
| **Setup** | Extra daemon + firewall rule | Only SSH key deployment |
| **Security** | TCP port 5666 (SSL optional) | SSH (always encrypted) |
| **Firewall** | Port 5666 must be open | Port 22 must be accessible |
| **Credentials** | shared password in nrpe.cfg | SSH key pair |
| **Argument passing** | Requires `dont_blame_nrpe=1` | No restriction (full shell) |
| **Best for** | High check volume, dedicated monitoring | Low volume, SSH already available |

---

## Troubleshooting NRPE

| Problem | Check |
|---------|-------|
| `Connection refused` | NRPE not running; `systemctl status nrpe`; check port 5666 |
| `Access denied` | Nagios server IP not in `allowed_hosts` in nrpe.cfg |
| `NRPE: Command ... not defined` | Command not in nrpe.cfg; typo in command name |
| `NRPE: Unable to read output` | Plugin not installed on remote host; path wrong |
| `SSL handshake failed` | SSL version mismatch between check_nrpe and nrpe daemon |
| Timeout | Firewall blocking port 5666; plugin taking too long |

```bash
# Debug NRPE from Nagios server
/usr/local/nagios/libexec/check_nrpe -H remote-host -c check_load -v

# Test NRPE listening on remote host
telnet remote-host 5666
netstat -tlnp | grep 5666
```
