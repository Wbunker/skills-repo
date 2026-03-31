# Chapter 7 — Kerberos-Enabled Applications

## What "Kerberos Support" Means

Applications integrate Kerberos in one of three ways:

| Integration | Mechanism | Notes |
|-------------|-----------|-------|
| **Native Kerberos** | Calls Kerberos API directly | Rare; tightly coupled |
| **GSSAPI** | Uses the Generic Security Services API | Most common; portable |
| **SASL/GSSAPI** | GSSAPI wrapped in SASL framework | Used by IMAP, SMTP, LDAP |

For most applications, configure both: the Kerberos keytab for the service principal AND the application's GSSAPI or SASL config.

## Service Principals and Keytabs

Every Kerberos-aware service needs a service principal and a keytab:

```bash
# Create service principal (no password — random key)
kadmin -q "addprinc -randkey service/host.example.com@EXAMPLE.COM"

# Export to keytab on the service host
kadmin -q "ktadd -k /etc/krb5.keytab service/host.example.com@EXAMPLE.COM"

# Verify
klist -k /etc/krb5.keytab
```

Protect the keytab: `chmod 600 /etc/krb5.keytab`, owned by the service user.

## PAM — Transparent Login (Linux/Unix)

`pam_krb5` allows users to log in with their Kerberos password via SSH, console, sudo, etc., and automatically receive a TGT.

```bash
# Install
yum install pam_krb5      # RHEL
apt-get install libpam-krb5  # Debian

# /etc/pam.d/system-auth (or /etc/pam.d/common-auth on Debian)
auth    required   pam_env.so
auth    sufficient pam_krb5.so minimum_uid=1000
auth    required   pam_unix.so try_first_pass

session optional   pam_krb5.so
```

Key PAM options: `minimum_uid` (skip system accounts), `forwardable` (get forwardable TGT), `renew_lifetime`.

## OpenSSH with GSSAPI

SSH is the most common Kerberos-integrated application. Two modes:

### GSSAPI Authentication (password-less SSO)
User's existing TGT is used to authenticate to SSH without entering a password.

**Server** (`/etc/ssh/sshd_config`):
```
GSSAPIAuthentication yes
GSSAPICleanupCredentials yes
```

**Client** (`~/.ssh/config`):
```
Host *.example.com
    GSSAPIAuthentication yes
    GSSAPIDelegateCredentials yes   # Forward TGT to remote host (use carefully)
```

Service principal needed: `host/server.example.com@EXAMPLE.COM` in `/etc/krb5.keytab`

### GSSAPI Credential Delegation
`GSSAPIDelegateCredentials yes` forwards the user's TGT to the remote host, allowing further Kerberos hops (e.g., `ssh host1` then `ssh host2` without a new kinit). Security trade-off: a compromised host1 can use the forwarded TGT.

## Apache — Web SSO with mod_auth_kerb

Enables browser-based SSO using SPNEGO (Negotiate auth). Users logged into a Kerberos realm get single sign-on to web applications in a browser.

```bash
# Install
yum install mod_auth_kerb
apt-get install libapache2-mod-auth-kerb
```

**Apache configuration:**
```apache
<Location /protected>
    AuthType Kerberos
    AuthName "Kerberos Login"
    KrbAuthRealms EXAMPLE.COM
    KrbServiceName HTTP/webserver.example.com@EXAMPLE.COM
    Krb5Keytab /etc/apache2/http.keytab
    KrbMethodNegotiate on
    KrbMethodK5Passwd off     # SSO only; disable password fallback
    Require valid-user
</Location>
```

**Service principal:**
```bash
kadmin -q "addprinc -randkey HTTP/webserver.example.com"
kadmin -q "ktadd -k /etc/apache2/http.keytab HTTP/webserver.example.com"
```

**Browser setup:** In Firefox, set `network.negotiate-auth.trusted-uris` to `.example.com`. Chrome/Edge respect the system Kerberos config on Linux; on Windows, uses Integrated Windows Authentication natively.

## SASL/GSSAPI — Email and LDAP

Applications using SASL (Cyrus IMAPD, Postfix, OpenLDAP) authenticate via `GSSAPI` SASL mechanism.

**OpenLDAP server** (`/etc/ldap/slapd.conf`):
```
sasl-realm EXAMPLE.COM
sasl-host ldap.example.com
```

**LDAP query with Kerberos:**
```bash
ldapsearch -H ldap://ldap.example.com -Y GSSAPI -b "dc=example,dc=com"
```

Service principal needed: `ldap/ldap.example.com@EXAMPLE.COM`

**Cyrus IMAPD** — configure `sasl_mech_list: GSSAPI` and provide `imap/mailhost.example.com` keytab.

## macOS Kerberos Integration

macOS uses Heimdal internally. The system Kerberos config is at `/etc/krb5.conf` (or symlinked from `/Library/Preferences/edu.mit.Kerberos`). The login window integrates with Kerberos when joined to an AD domain via Directory Utility.

Ticket management: `Ticket Viewer.app` or `kinit`/`klist` in Terminal.

## Summary: Service Principal Naming Convention

| Service | Principal format |
|---------|-----------------|
| SSH | `host/fqdn@REALM` |
| HTTP | `HTTP/fqdn@REALM` |
| LDAP | `ldap/fqdn@REALM` |
| IMAP | `imap/fqdn@REALM` |
| SMTP | `smtp/fqdn@REALM` |
| NFS | `nfs/fqdn@REALM` |
| PostgreSQL | `postgres/fqdn@REALM` |
