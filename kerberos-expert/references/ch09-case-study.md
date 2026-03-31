# Chapter 9 — Case Study: End-to-End Kerberos Deployment

A worked example of deploying Kerberos in a realistic mixed organization.

## The Organization

**Acme Corp** — 500 employees, mixed environment:
- Linux servers running web apps, databases, file servers
- Windows workstations (AD-joined) and Linux workstations
- Goal: unified SSO — users authenticate once and access Linux services without re-entering passwords

## Planning Decisions

### Realm Structure
Single realm: `ACME.COM` — one organizational unit, one KDC. Realm name matches DNS domain in UPPERCASE.

### KDC Topology
- **Master KDC:** `kdc1.acme.com` — dedicated hardened VM; writable database
- **Slave KDC:** `kdc2.acme.com` — second datacenter; read-only replica via kprop

### Implementation Choice
MIT Kerberos 5 on Linux KDCs; client workstations use either MIT krb5 (Linux) or native AD Kerberos (Windows) with cross-realm trust to `ACME.COM`.

### Services to Kerberize
Priority order: SSH → web apps → LDAP → email

## Implementation Walkthrough

### Step 1: KDC Setup

```bash
# Install on kdc1.acme.com
yum install krb5-server krb5-libs krb5-workstation

# /etc/krb5.conf
[libdefaults]
    default_realm = ACME.COM
    dns_lookup_kdc = true

[realms]
    ACME.COM = {
        kdc = kdc1.acme.com
        kdc = kdc2.acme.com
        admin_server = kdc1.acme.com
    }

[domain_realm]
    .acme.com = ACME.COM
    acme.com = ACME.COM

# Create database
kdb5_util create -s -r ACME.COM

# Set admin ACL
echo "*/admin@ACME.COM  *" > /var/kerberos/krb5kdc/kadm5.acl

# Start services
systemctl enable --now krb5kdc kadmin

# Bootstrap admin
kadmin.local -q "addprinc admin/admin"
```

### Step 2: DNS SRV Records

```dns
_kerberos._udp.acme.com.  IN SRV 10 0 88 kdc1.acme.com.
_kerberos._tcp.acme.com.  IN SRV 10 0 88 kdc1.acme.com.
_kerberos._udp.acme.com.  IN SRV 20 0 88 kdc2.acme.com.
_kerberos.acme.com.       IN TXT "ACME.COM"
```

### Step 3: Add User Principals

```bash
# Bulk import from HR export
while IFS=, read user pass; do
    kadmin.local -q "addprinc -pw $pass $user"
done < users.csv

# Force password change on first login
kadmin.local -q "modprinc +needchange alice"
```

### Step 4: Kerberize SSH (First Service)

On each Linux server:
```bash
# Add host principal
kadmin -q "addprinc -randkey host/server1.acme.com"
kadmin -q "ktadd -k /etc/krb5.keytab host/server1.acme.com"

# /etc/ssh/sshd_config
GSSAPIAuthentication yes
GSSAPICleanupCredentials yes

systemctl restart sshd
```

**Test:**
```bash
kinit alice
ssh server1.acme.com     # Should log in without password prompt
klist                    # TGT and host service ticket visible
```

### Step 5: Kerberize Web Apps (Apache + mod_auth_kerb)

```bash
kadmin -q "addprinc -randkey HTTP/webapp.acme.com"
kadmin -q "ktadd -k /etc/httpd/http.keytab HTTP/webapp.acme.com"
chown apache:apache /etc/httpd/http.keytab
chmod 400 /etc/httpd/http.keytab
```

Apache config (see ch07-applications.md for full details).

### Step 6: Slave KDC Replication

```bash
# On master: add kpropd acl on slave
# /var/kerberos/krb5kdc/kpropd.acl (on slave):
host/kdc1.acme.com@ACME.COM

# On slave: start kpropd
systemctl enable --now kprop

# On master: push database
kdb5_util dump /var/kerberos/krb5kdc/slave_datatrans
kprop -r ACME.COM -f /var/kerberos/krb5kdc/slave_datatrans kdc2.acme.com

# Add to master cron:
# */15 * * * * /usr/sbin/kprop kdc2.acme.com
```

### Step 7: Windows Workstations

Configure AD cross-realm trust so Windows users with a Windows TGT can obtain tickets for `ACME.COM` services (see ch08-advanced.md for cross-realm setup).

## Rollout Notes

- Roll out one service at a time; validate SSO works before moving to the next
- Keep non-Kerberos authentication (passwords) as fallback during transition
- Monitor KDC logs (`/var/log/krb5kdc.log`) for error spikes during rollout
- Communicate to users: "you'll log in once and get access everywhere" — reduces help desk load
- Document all service principals and keytab locations in a configuration management tool
