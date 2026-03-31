# Chapter 5 — Troubleshooting Kerberos

## Quick Decision Tree

```
Authentication failing?
├── Can you get a TGT? (kinit -V username)
│   ├── NO → Problem is client ↔ KDC
│   │   ├── Clock skew? → Sync clocks (NTP)
│   │   ├── "Principal unknown"? → addprinc in kadmin
│   │   ├── "Cannot contact KDC"? → firewall/DNS/port 88
│   │   └── "Preauthentication failed"? → Wrong password or enctype mismatch
│   └── YES → Problem is client ↔ service
│       ├── "Server not found in Kerberos database"? → Missing service principal
│       ├── Keytab issue? → Check ktutil list, re-run ktadd
│       ├── Clock skew between client and service host? → Sync clocks
│       └── Enctype mismatch? → Check supported_enctypes in kdc.conf
└── Works for some users/services but not others → Principal-specific issue
```

## Debugging Tools

### Verbose kinit

```bash
kinit -V username           # Show ticket acquisition steps
KRB5_TRACE=/dev/stderr kinit username   # Full protocol trace (Kerberos 5 only)
```

### Environment Variables

```bash
KRB5_TRACE=/dev/stderr      # Print detailed trace of all Kerberos operations
KRB5_CONFIG=/path/to/krb5.conf  # Override config file
KRB5CCNAME=FILE:/tmp/mycc   # Override credential cache location
```

### Inspect Tickets

```bash
klist -v                    # Verbose ticket info (times, flags, enctypes)
klist -e                    # Show encryption types for each ticket
klist -f                    # Show ticket flags
```

### Inspect Keytabs

```bash
ktutil
  rkt /etc/krb5.keytab      # Read keytab
  list                      # Show principals, kvno, enctype
  quit

klist -k /etc/krb5.keytab   # Quick keytab listing
klist -k -t /etc/krb5.keytab  # Include timestamps
```

### Network Capture

```bash
tcpdump -i eth0 port 88     # Capture Kerberos traffic
# Wireshark has a Kerberos dissector for full protocol decode
```

### KDC Logs

Default log location (configure in `[logging]` section of krb5.conf):
```
/var/log/krb5kdc.log
/var/log/kadmind.log
```

## Error Catalog

| Error | Cause | Fix |
|-------|-------|-----|
| `Clock skew too great` | Client/KDC clocks differ by >5 min | Sync NTP on all hosts |
| `Client not found in Kerberos database` | Principal doesn't exist | `kadmin: addprinc username` |
| `Server not found in Kerberos database` | Service principal missing | `kadmin: addprinc -randkey service/host` |
| `Preauthentication failed` | Wrong password, or enctype mismatch | Verify password; check enctypes |
| `Cannot contact any KDC for realm` | KDC unreachable | Check firewall (port 88), DNS, KDC service running |
| `Ticket expired` | TGT or service ticket past end time | `kinit` again to get fresh TGT |
| `Credentials cache file permissions incorrect` | Wrong ownership on ccache | Check `ls -la /tmp/krb5cc_*`; fix ownership |
| `Key version number for principal...not available` | Keytab has old KVNO | Re-run `ktadd` to refresh keytab after `cpw` |
| `No credentials cache found` | No TGT; forgot to kinit | Run `kinit` |
| `KDC has no support for encryption type` | enctype in request not supported by KDC | Add enctype to `supported_enctypes` in kdc.conf |
| `Message stream modified` | Tampering or network corruption | Investigate MITM; check network integrity |
| `Decrypt integrity check failed` | Wrong key / corrupted ticket | KVNO mismatch; re-issue keytab |

## Common Scenarios

### Clock Skew
Most common issue in new deployments. Even a few minutes off causes `KRB_AP_ERR_SKEW`. Fix:
```bash
# Install and start NTP
systemctl enable --now chronyd
chronyc makestep     # Force immediate sync
date                 # Verify
```

### Keytab KVNO Mismatch
When a service principal's password is changed (via `cpw`), the KVNO (key version number) increments. The old keytab becomes invalid. Fix:
```bash
kadmin -q "ktadd -k /etc/krb5.keytab service/host.example.com"
```

### Wrong Realm / Principal Name
Kerberos is case-sensitive. `alice@EXAMPLE.COM` ≠ `alice@example.com`. Realm names must be UPPERCASE. Check `[domain_realm]` mapping in krb5.conf.

### DNS Reverse Lookup Failures
If `rdns = true` (default), Kerberos resolves the service hostname via reverse DNS before constructing the principal name. If reverse DNS is wrong, principal lookup fails. Fix: set `rdns = false` in `[libdefaults]` or fix DNS.
