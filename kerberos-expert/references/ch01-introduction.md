# Chapter 1 — Introduction to Kerberos

## Origins

The name comes from Cerberus, the three-headed dog guarding the underworld in Greek mythology — fitting for a three-party authentication system. Kerberos was developed at MIT in the early 1980s as part of **Project Athena**, which was moving from time-sharing mainframes to distributed client-server workstations. The problem: how do you authenticate users over an untrusted network without sending passwords in the clear?

## What Kerberos Is

Kerberos is a **secure, single-sign-on, trusted third-party mutual authentication service**.

- **Secure** — authentication credentials (tickets) are encrypted; passwords never travel the network
- **Single sign-on (SSO)** — authenticate once, access many services without re-entering credentials
- **Trusted third party** — a central Key Distribution Center (KDC) that both clients and services trust
- **Mutual authentication** — both the client and the server prove their identity to each other

## Goals

1. Centralized authentication via KDCs — one place to manage credentials
2. Secure authentication over untrusted networks using encrypted tickets
3. Enable the three A's: **Authentication** (who are you?), **Authorization** (what can you do?), **Auditing** (what did you do?)

## Version History

| Version | Notes |
|---------|-------|
| v1–v3 | Internal MIT testing only; never publicly released |
| **v4** | First public release, January 24, 1989. Used DES. US export restrictions led to "eBones" (exportable version with weakened crypto). Still found in legacy environments. |
| **v5** | Current standard. RFC 1510 (1993), updated by RFC 4120 (2005). Fixes v4 weaknesses, adds extensible encryption, cross-realm improvements, pre-authentication, and ticket flags. |

Kerberos 4 and 5 are **not protocol-compatible**, though MIT ships krb524d to bridge them for legacy services.

## Related Authentication Systems

- **DCE (Distributed Computing Environment)** — IBM/OSF standard built on top of Kerberos 5; largely legacy today
- **Globus Security Infrastructure** — Used in grid computing; based on Kerberos + PKI
- **SESAME** — European Kerberos-like system adding Role-Based Access Control (RBAC); never widely adopted
- **Active Directory** — Microsoft's Kerberos 5 implementation with proprietary extensions; the dominant Kerberos deployment worldwide
