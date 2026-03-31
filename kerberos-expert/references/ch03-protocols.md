# Chapter 3 — Kerberos Protocols

## Needham-Schroeder Protocol (1978)

The theoretical foundation for Kerberos. The core insight: a trusted server (S) can introduce two parties (A and B) by issuing encrypted tokens that prove identity without revealing secrets over the network. Kerberos extends this with timestamps to prevent replay attacks.

## Kerberos 5 Authentication Flow

Three exchanges, each building on the last:

### Exchange 1: AS Exchange (Initial Login)

```
Client → KDC/AS:  AS_REQ
  - Client principal name
  - Requested TGT service name (krbtgt/REALM)
  - Requested ticket lifetime
  - Nonce
  - (Pre-authentication data, if required)

KDC/AS → Client:  AS_REP
  - TGT encrypted with krbtgt key (client cannot read this)
  - Session key encrypted with client's long-term key (client decrypts this)
```

After this: client has a TGT and a TGS session key, cached locally.

### Exchange 2: TGS Exchange (Get a Service Ticket)

```
Client → KDC/TGS:  TGS_REQ
  - TGT (from AS exchange)
  - Authenticator: {timestamp, nonce} encrypted with TGS session key
  - Requested service principal name

KDC/TGS → Client:  TGS_REP
  - Service ticket encrypted with service's long-term key (client cannot read)
  - New session key encrypted with TGS session key
```

After this: client has a service ticket and a service session key.

### Exchange 3: AP Exchange (Access the Service)

```
Client → Service:  AP_REQ
  - Service ticket (from TGS exchange)
  - Authenticator: {timestamp} encrypted with service session key

Service → Client:  AP_REP (for mutual auth)
  - Timestamp + 1, encrypted with service session key
  (proves service holds the correct key)
```

The service decrypts the ticket with its own long-term key to get the session key, then uses the session key to verify the authenticator. The timestamp in the authenticator prevents replay attacks.

## Kerberos 4 vs Kerberos 5

| Feature | Kerberos 4 | Kerberos 5 |
|---------|------------|------------|
| RFC | None (MIT spec) | RFC 4120 |
| Encryption | DES only | Pluggable (AES, 3DES, RC4, etc.) |
| Ticket lifetime | Max 21 hours | Configurable, renewable |
| Cross-realm | Single hop only | Multi-hop hierarchical |
| Pre-authentication | No | Yes (required by default) |
| Addressing | IP-bound tickets | Optional addressing |
| ASN.1 encoding | No | Yes |
| Forwardable tickets | No | Yes |
| Double-DES weakness | Yes | Fixed |

## Pre-Authentication

Without pre-auth, anyone can request a TGT for any principal and receive an AS_REP encrypted with that principal's key — enabling offline dictionary attacks. With pre-authentication, the client must first prove knowledge of the key (by encrypting a timestamp) before the AS issues a TGT. **Always enable pre-authentication.**

The attack against disabled pre-auth is called **AS-REP roasting** (see ch06-security.md).

## Related Protocols and Standards

### GSSAPI (RFC 2743)
Generic Security Services API — a standard C API that abstracts authentication mechanisms. Applications call GSSAPI; Kerberos is plugged in as the mechanism. Enables Kerberos authentication in SSH, LDAP, IMAP, etc. without hard-coding Kerberos calls. The Kerberos GSSAPI mechanism is defined in RFC 4121.

### SPNEGO (RFC 4178)
Simple and Protected GSSAPI Negotiation Mechanism. Allows a client and server to negotiate which GSSAPI mechanism to use (e.g., Kerberos vs. NTLM). Used by web browsers for **Integrated Windows Authentication** — enables SSO from browser to web server via `Negotiate` HTTP authentication.

### SASL (RFC 4422)
Simple Authentication and Security Layer. A framework for plugging authentication into application protocols (IMAP, SMTP, LDAP). The `GSSAPI` SASL mechanism uses Kerberos. Used heavily with email servers and LDAP directories.

### PKINIT (RFC 4556)
Public Key Cryptography for Initial Authentication. Replaces the password-based AS exchange with PKI: the client uses a certificate/private key (e.g., on a smart card) instead of a password. Eliminates the need for the KDC to store password-derived keys.

### MS-KILE
Microsoft's Kerberos extensions for Active Directory. Adds the PAC (Privilege Attribute Certificate) — a Microsoft-specific authorization data field in tickets containing group memberships and SIDs. Also adds support for RC4-HMAC encryption using NT hashes.
