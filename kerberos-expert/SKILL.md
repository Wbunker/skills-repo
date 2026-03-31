---
name: kerberos-expert
description: >
  Deep expertise on the Kerberos authentication protocol based on "Kerberos:
  The Definitive Guide" by Jason Garman. Use when asked about: Kerberos
  concepts (realms, principals, tickets, KDC, TGS, keytabs), protocol
  internals (AS/TGS exchange, Kerberos v4 vs v5, GSSAPI, PKINIT, SPNEGO),
  deploying or configuring a KDC (MIT Kerberos, Heimdal, Active Directory),
  troubleshooting Kerberos errors (clock skew, principal not found, keytab
  issues), security (AS-REP roasting, ticket attacks, KDC hardening, firewall
  config), Kerberos-enabled applications (SSH, PAM, Apache mod_auth_kerb,
  SASL, LDAP), cross-realm authentication, Windows/Unix interoperability with
  Active Directory, krb5.conf configuration, kadmin commands, kinit/klist/
  kdestroy usage, or single sign-on (SSO) design with Kerberos.
---

# Kerberos Expert

Based on *Kerberos: The Definitive Guide* by Jason Garman (O'Reilly).

## Reference Map

Load the reference file that matches the user's task. Load only what is needed.

| Task / Question | Load |
|----------------|------|
| "What is Kerberos?", history, v4 vs v5, overview | `references/ch01-introduction.md` |
| Terminology, realms, principals, tickets, KDC, TGS, keys | `references/ch02-concepts.md` |
| Protocol internals, message flows, GSSAPI, PKINIT, SPNEGO | `references/ch03-protocols.md` |
| Installing KDC, planning deployment, krb5.conf, client setup | `references/ch04-implementation.md` |
| Debugging errors, clock skew, error codes, KRB5_TRACE | `references/ch05-troubleshooting.md` |
| Attacks, security hardening, firewalls, NAT, auditing | `references/ch06-security.md` |
| PAM, SSH, Apache, SASL, keytabs, application config | `references/ch07-applications.md` |
| Cross-realm trust, Windows/AD interop, MS Kerberos extensions | `references/ch08-advanced.md` |
| End-to-end deployment example, realm design walkthrough | `references/ch09-case-study.md` |
| PKINIT, smart cards, AES encryption, future extensions | `references/ch10-futures.md` |
| kadmin, kinit, klist, kdestroy, ktutil, krb5.conf syntax | `references/appendix-admin.md` |

## Quick Facts

- Kerberos uses **UDP/TCP port 88** (authentication), **464** (kpasswd), **749** (kadmin)
- Clocks must be within **5 minutes** of each other (default skew tolerance)
- Tickets have a default **lifetime of 10 hours**, renewable up to **7 days**
- The **KDC never sends passwords** in the clear — all secrets travel encrypted
- Kerberos 5 is defined in **RFC 4120** (obsoletes RFC 1510)
