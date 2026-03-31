# Chapter 4 — Implementing Kerberos

## Planning Your Installation

### Choose an Implementation

| Implementation | Best for |
|---------------|----------|
| **MIT Kerberos 5** | Linux/Unix; the reference implementation; most documentation |
| **Heimdal** | Linux/Unix alternative; BSD licensed; used by macOS internally |
| **Windows Active Directory** | Windows-centric environments; Microsoft's v5 with extensions |

For mixed environments, MIT Kerberos on Unix authenticating against an AD KDC is very common.

### Realm Design

- Use a single realm unless you have distinct organizational boundaries requiring separation
- Name the realm after your DNS domain in UPPERCASE: `EXAMPLE.COM`
- Plan for **one master KDC** and **one or more slave KDCs** for redundancy
- The master KDC holds the writable database; slaves hold read-only replicas propagated via `kprop`

### KDC Topology

- KDCs should be **dedicated, hardened machines** — they are the most sensitive hosts in your infrastructure
- Place at least one KDC in each major network segment to minimize authentication latency
- Clients fail over to slave KDCs automatically when the master is unavailable

## Before You Begin

1. **Time synchronization** — Configure NTP on all KDCs and clients. Kerberos requires clocks to agree within 5 minutes (default). Use `chronyd` or `ntpd`.
2. **DNS** — All hosts must have forward and reverse DNS entries. Kerberos relies heavily on DNS for principal name resolution.
3. **Firewall ports** — Open UDP+TCP 88 (Kerberos), 464 (kpasswd), 749 (kadmin remote) between clients and KDCs.
4. **Hostnames** — Use FQDNs consistently. Mismatched hostnames cause principal lookup failures.

## KDC Installation (MIT Kerberos 5)

```bash
# Install packages (RHEL/CentOS)
yum install krb5-server krb5-libs krb5-workstation

# Install packages (Debian/Ubuntu)
apt-get install krb5-kdc krb5-admin-server
```

### Configure `/etc/krb5.conf` (on KDC and all clients)

```ini
[libdefaults]
    default_realm = EXAMPLE.COM
    dns_lookup_realm = false
    dns_lookup_kdc = true
    ticket_lifetime = 24h
    renew_lifetime = 7d
    forwardable = true

[realms]
    EXAMPLE.COM = {
        kdc = kdc1.example.com
        kdc = kdc2.example.com
        admin_server = kdc1.example.com
    }

[domain_realm]
    .example.com = EXAMPLE.COM
    example.com = EXAMPLE.COM
```

### Configure `/var/kerberos/krb5kdc/kdc.conf`

```ini
[kdcdefaults]
    kdc_ports = 88
    kdc_tcp_ports = 88

[realms]
    EXAMPLE.COM = {
        master_key_type = aes256-cts
        acl_file = /var/kerberos/krb5kdc/kadm5.acl
        dict_file = /usr/share/dict/words
        admin_keytab = /var/kerberos/krb5kdc/kadm5.keytab
        supported_enctypes = aes256-cts:normal aes128-cts:normal
        max_life = 1d
        max_renewable_life = 7d
    }
```

### Create the Database and Start KDC

```bash
# Create the KDC database
kdb5_util create -s -r EXAMPLE.COM

# Set ACLs for admin (edit /var/kerberos/krb5kdc/kadm5.acl)
# */admin@EXAMPLE.COM  *

# Start services
systemctl enable --now krb5kdc kadmin

# Create admin principal
kadmin.local -q "addprinc admin/admin"
```

## DNS SRV Records for KDC Autodiscovery

When `dns_lookup_kdc = true`, clients find KDCs via DNS without hardcoding them in krb5.conf:

```dns
_kerberos._udp.example.com.  IN SRV 10 0 88 kdc1.example.com.
_kerberos._tcp.example.com.  IN SRV 10 0 88 kdc1.example.com.
_kerberos._udp.example.com.  IN SRV 20 0 88 kdc2.example.com.
_kpasswd._udp.example.com.   IN SRV 10 0 464 kdc1.example.com.
_kerberos-adm._tcp.example.com. IN SRV 10 0 749 kdc1.example.com.
_kerberos.example.com.       IN TXT "EXAMPLE.COM"
```

## Client and Application Server Setup

### Add User Principals

```bash
kadmin.local -q "addprinc alice"
kadmin.local -q "addprinc bob"
```

### Add Service Principals and Generate Keytabs

```bash
# Add the service principal
kadmin.local -q "addprinc -randkey host/server.example.com"
kadmin.local -q "addprinc -randkey http/webserver.example.com"

# Export to keytab on the service host
kadmin.local -q "ktadd -k /etc/krb5.keytab host/server.example.com"
```

### Client Ticket Operations

```bash
kinit alice                    # Get TGT (prompts for password)
kinit -k -t /etc/krb5.keytab host/server.example.com  # Keytab-based (non-interactive)
klist                          # List cached tickets
klist -e                       # Show encryption types
kdestroy                       # Destroy ticket cache
kinit -R                       # Renew TGT (if RENEWABLE flag set)
```

## Slave KDC Replication

```bash
# On master: configure kpropd on slaves, then push database
kprop -r EXAMPLE.COM -f /var/kerberos/krb5kdc/slave_datatrans kdc2.example.com

# Automate with cron (run on master):
# */5 * * * * /usr/sbin/kprop kdc2.example.com
```
