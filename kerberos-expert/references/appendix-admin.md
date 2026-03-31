# Appendix — Administration Reference

## Table of Contents
1. [kinit](#kinit)
2. [klist](#klist)
3. [kdestroy](#kdestroy)
4. [ktutil](#ktutil)
5. [kadmin / kadmin.local](#kadmin)
6. [kdb5_util](#kdb5_util)
7. [kprop / kpropd](#kprop)
8. [krb5.conf Reference](#krb5conf)
9. [kdc.conf Reference](#kdcconf)

---

## kinit

Obtain a TGT (or any Kerberos ticket).

```bash
kinit                              # TGT for current user
kinit alice                        # TGT for alice
kinit alice@REALM.COM              # Specify realm
kinit -l 4h alice                  # 4-hour lifetime
kinit -r 2d alice                  # Renewable for 2 days
kinit -R                           # Renew existing TGT
kinit -f                           # Forwardable TGT
kinit -k                           # Use default keytab (/etc/krb5.keytab)
kinit -k -t /path/to.keytab princ  # Specific keytab
kinit -V alice                     # Verbose output
kinit -S service/host alice        # Get specific service ticket instead of TGT
```

---

## klist

List cached tickets.

```bash
klist                       # List TGT and service tickets
klist -v                    # Verbose (all ticket fields)
klist -e                    # Show encryption types
klist -f                    # Show ticket flags
klist -a                    # Show ticket addresses
klist -c FILE:/tmp/mycc     # Specific credential cache
klist -k                    # List default keytab
klist -k /path/to.keytab    # List specific keytab
klist -k -t /path/to.keytab # Include timestamps in keytab listing
```

---

## kdestroy

Destroy credential cache.

```bash
kdestroy                    # Destroy default ccache
kdestroy -c FILE:/tmp/mycc  # Destroy specific ccache
kdestroy -A                 # Destroy all ccaches for current user
```

---

## ktutil

Keytab management utility (interactive).

```
ktutil
  rkt /etc/krb5.keytab            # Read keytab into memory
  wkt /etc/krb5.keytab.new        # Write memory to keytab
  list                            # List entries (slot, kvno, principal, enctype)
  addent -password -p princ -k 1 -e aes256-cts  # Add entry with password
  addent -key -p princ -k 1 -e aes256-cts        # Add entry with hex key
  delent <slot>                   # Delete entry by slot number
  clear                           # Clear all entries from memory
  quit
```

---

## kadmin

Remote admin client. `kadmin.local` runs directly on the KDC (bypasses network auth).

```bash
kadmin -p admin/admin          # Connect as admin/admin principal
kadmin.local                   # Local admin (on KDC only)
kadmin -q "command"            # Run single command and exit
```

### Principal Management

```bash
addprinc alice                         # Add user principal (prompts for password)
addprinc -pw SecretPass alice          # Add with specified password
addprinc -randkey host/server.com      # Add service principal (random key)
addprinc -x dn="cn=alice,dc=..." alice # Add with LDAP attributes

delprinc alice                         # Delete principal

modprinc -maxlife 8h alice             # Change max ticket life
modprinc +needchange alice             # Force password change on next login
modprinc -allow_tix alice             # Disable principal (deny tickets)
modprinc +allow_tix alice             # Re-enable principal

cpw alice                              # Change password (prompts)
cpw -pw NewPass alice                  # Change password (specify)
cpw -randkey host/server.com           # Set random key (rotates KVNO)

getprinc alice                         # Show principal details
listprincs                             # List all principals
listprincs alice*                      # List matching principals
```

### Keytab Management

```bash
ktadd -k /etc/krb5.keytab host/server.com        # Add to keytab
ktadd -k /etc/krb5.keytab -e aes256-cts host/s.  # Specific enctype
ktremove -k /etc/krb5.keytab host/server.com      # Remove from keytab
```

### Policy Management

```bash
addpol -minlength 8 -minclasses 2 default_policy  # Add password policy
modpol -maxlife 90d default_policy                 # Modify policy
getpol default_policy                              # Show policy
delpol default_policy                              # Delete policy
listpols                                           # List all policies
modprinc -policy default_policy alice              # Assign policy to principal
```

---

## kdb5_util

Database management (run on KDC only).

```bash
kdb5_util create -s -r REALM.COM       # Create new database
kdb5_util destroy                      # Destroy database (DESTRUCTIVE)
kdb5_util dump /path/to/dump           # Dump database to file
kdb5_util load /path/to/dump           # Load database from dump
kdb5_util stash                        # Create/update stash file
```

---

## kprop / kpropd

Database replication to slave KDCs.

```bash
# On master: dump and push
kdb5_util dump /var/kerberos/krb5kdc/slave_datatrans
kprop -r REALM.COM -f /var/kerberos/krb5kdc/slave_datatrans kdc2.example.com

# On slave: kpropd runs as a service listening for propagation
# /var/kerberos/krb5kdc/kpropd.acl must contain master's host principal:
# host/kdc1.example.com@REALM.COM
```

---

## krb5.conf Reference

`/etc/krb5.conf` — client and KDC configuration.

```ini
[libdefaults]
    default_realm = EXAMPLE.COM
    dns_lookup_realm = false       # Discover realm via DNS TXT records
    dns_lookup_kdc = true          # Discover KDC via DNS SRV records
    ticket_lifetime = 24h          # Default TGT lifetime
    renew_lifetime = 7d            # Default renewable lifetime
    forwardable = true             # Request forwardable tickets
    proxiable = false
    rdns = false                   # Don't reverse-resolve for service principal lookup
    no_addresses = true            # Omit IP from tickets (required for NAT)
    udp_preference_limit = 1       # Force TCP (use when UDP fragmentation is a problem)
    default_tgs_enctypes = aes256-cts aes128-cts
    default_tkt_enctypes = aes256-cts aes128-cts
    permitted_enctypes = aes256-cts aes128-cts

[realms]
    EXAMPLE.COM = {
        kdc = kdc1.example.com:88
        kdc = kdc2.example.com:88
        admin_server = kdc1.example.com:749
        default_domain = example.com
        # auth_to_local rules for principal→username mapping
        auth_to_local = RULE:[1:$1@$0](.*@EXAMPLE\.COM)s/@.*//
        auth_to_local = DEFAULT
    }

[domain_realm]
    .example.com = EXAMPLE.COM
    example.com = EXAMPLE.COM

[logging]
    kdc = FILE:/var/log/krb5kdc.log
    admin_server = FILE:/var/log/kadmind.log
    default = SYSLOG:NOTICE:DAEMON

[appdefaults]
    pam = {
        minimum_uid = 1000
        forwardable = true
    }

[capaths]
    # Cross-realm traversal paths
    REALM-A.COM = {
        REALM-B.COM = .
    }
```

---

## kdc.conf Reference

`/var/kerberos/krb5kdc/kdc.conf` — KDC-specific configuration.

```ini
[kdcdefaults]
    kdc_ports = 88
    kdc_tcp_ports = 88
    restrict_anonymous_to_tgt = true   # Prevent anon PKINIT abuse

[realms]
    EXAMPLE.COM = {
        master_key_type = aes256-cts
        acl_file = /var/kerberos/krb5kdc/kadm5.acl
        dict_file = /usr/share/dict/words          # Password dictionary check
        admin_keytab = /var/kerberos/krb5kdc/kadm5.keytab
        supported_enctypes = aes256-cts:normal aes128-cts:normal
        max_life = 1d                  # Maximum ticket lifetime
        max_renewable_life = 7d        # Maximum renewable lifetime
        master_key_name = K/M          # Master key principal
        # PKINIT (if using smart cards / certs)
        pkinit_identity = FILE:/var/kerberos/krb5kdc/kdc.pem,...
        pkinit_anchors = FILE:/etc/pki/ca.pem
    }
```

### kadm5.acl — Admin ACL File

```
# Format: principal  permissions  [target_principal]  [restrictions]
*/admin@EXAMPLE.COM  *                     # Full admin rights
alice@EXAMPLE.COM    cpw                   # Can only change passwords
alice@EXAMPLE.COM    aci  *@EXAMPLE.COM    # Add, change, inspect any principal
```

Permission letters: `a`=add, `d`=delete, `m`=modify, `c`=change_password, `i`=inquire, `l`=list, `p`=propagate, `x`/`*`=all
