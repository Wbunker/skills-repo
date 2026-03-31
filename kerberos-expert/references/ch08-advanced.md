# Chapter 8 — Advanced Topics

## Cross-Realm Authentication

Multiple Kerberos realms can trust each other, allowing users in one realm to authenticate to services in another.

### How It Works

When a user in `REALM-A` wants to access a service in `REALM-B`:
1. The user's KDC issues a referral ticket to a **cross-realm TGT** (`krbtgt/REALM-B@REALM-A`)
2. The user presents this to `REALM-B`'s KDC
3. `REALM-B`'s KDC issues a service ticket for the target service

### Types of Trust

| Trust type | Description |
|------------|-------------|
| **Direct (bilateral)** | Each realm has a shared key with the other. A↔B means one hop. |
| **Hierarchical** | Realms are organized in a tree. A trust path follows the hierarchy. `US.EXAMPLE.COM → EXAMPLE.COM → EU.EXAMPLE.COM` requires two hops. |
| **Capstone realm** | A common parent realm that all child realms trust. |

### Configuring Cross-Realm Trust

```bash
# On REALM-A's KDC — add cross-realm principal
kadmin.local -q "addprinc -pw SharedSecret krbtgt/REALM-B@REALM-A"

# On REALM-B's KDC — add the reverse
kadmin.local -q "addprinc -pw SharedSecret krbtgt/REALM-A@REALM-B"
# (Same shared secret both sides)
```

**krb5.conf** — add the remote realm and its KDC:
```ini
[realms]
    REALM-B.EXAMPLE.COM = {
        kdc = kdc.realm-b.example.com
    }

[capaths]
    REALM-A.EXAMPLE.COM = {
        REALM-B.EXAMPLE.COM = .
    }
```

### Security Note
Each cross-realm hop adds a trust dependency. A compromised KDC in any trusted realm can impersonate users to all other trusting realms.

## Kerberos 4 / Kerberos 5 Interoperability

For legacy environments still running Kerberos 4 services, MIT provides **krb524d**:

- Runs on the KDC alongside krb5kdc
- Converts Kerberos 5 TGTs into Kerberos 4 tickets
- Clients use `krb524init` to obtain Kerberos 4 credentials from a v5 TGT
- Port: UDP 4444

This is a bridge, not a solution — eliminate all Kerberos 4 usage when possible.

## Windows Active Directory Kerberos

AD is a Kerberos 5 implementation with Microsoft-specific extensions (MS-KILE).

### Microsoft Extensions

**PAC (Privilege Attribute Certificate):**
- Embedded in every ticket as authorization data
- Contains: user SIDs, group memberships, account expiry, password last set
- Windows services use PAC data for access control decisions
- Linux/Unix services typically ignore PAC data (or use it with Samba/SSSD)

**RC4-HMAC encryption:**
- Uses the NT hash (MD4 of Unicode password) as the key
- Supported for compatibility but weaker than AES; disable when possible

**NTLM fallback:**
- Windows clients fall back to NTLM if Kerberos fails
- NTLM has no mutual authentication and is vulnerable to relay attacks
- Ensure Kerberos is working correctly to prevent NTLM fallback

### AD-Specific Ticket Behavior

- AD tickets are large due to PAC data — can exceed UDP MTU, requiring TCP (UDP fragments may be dropped)
- Maximum token size is a known issue in complex environments with many group memberships
- Group Policy controls Kerberos settings (ticket lifetime, clock skew tolerance, etc.)

## Windows and Unix Interoperability

### Unix Clients Authenticating Against AD KDC

Most common modern scenario. MIT Kerberos clients work against AD KDCs.

**krb5.conf for AD:**
```ini
[libdefaults]
    default_realm = AD.EXAMPLE.COM
    dns_lookup_kdc = true
    dns_lookup_realm = false
    ticket_lifetime = 24h
    renew_lifetime = 7d
    forwardable = true
    rdns = false              # Important: AD FQDNs may not reverse-resolve correctly

[realms]
    AD.EXAMPLE.COM = {
        kdc = ad-dc1.example.com
        admin_server = ad-dc1.example.com
        default_domain = example.com
    }

[domain_realm]
    .example.com = AD.EXAMPLE.COM
    example.com = AD.EXAMPLE.COM
```

**Join Unix host to AD:**
Use **SSSD** (System Security Services Daemon) or **Samba/Winbind** to join Linux to AD and map Windows identities to Unix UID/GID.

```bash
# With SSSD + realm
realm join ad.example.com --user administrator
```

### Principal Name Mapping

Windows uses `user@AD.EXAMPLE.COM`; Unix may expect `user` or `user@realm`. Mapping tools:

- `auth_to_local` rules in krb5.conf: translate Kerberos principal names to local Unix usernames
- SSSD `id_provider = ad` handles this automatically with AD schema attributes

```ini
[realms]
    AD.EXAMPLE.COM = {
        auth_to_local = RULE:[1:$1@$0](.*@AD\.EXAMPLE\.COM)s/@.*//
        auth_to_local = DEFAULT
    }
```

### Service Principal Names in AD

AD uses **SPNs** (Service Principal Names) — same concept as Kerberos principals. Manage with:
```
setspn -A HTTP/webserver.example.com DOMAIN\serviceaccount
```

Export a keytab from AD for use on Linux:
```bash
# On Windows (ktpass utility)
ktpass /princ HTTP/webserver.example.com@AD.EXAMPLE.COM \
       /mapuser DOMAIN\serviceaccount \
       /crypto AES256-SHA1 \
       /ptype KRB5_NT_PRINCIPAL \
       /out http.keytab \
       +rndpass
```
