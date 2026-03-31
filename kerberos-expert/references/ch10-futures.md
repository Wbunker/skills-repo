# Chapter 10 — Kerberos Futures

## PKINIT — Public Key Initial Authentication (RFC 4556)

PKINIT replaces the password-based AS exchange with public-key cryptography. Instead of encrypting a timestamp with a password-derived key, the client uses a **certificate and private key** to prove identity to the KDC.

### How It Works
1. KDC is configured with a CA certificate (trusts certs signed by that CA)
2. Client has a certificate (from the CA) and its private key
3. AS_REQ includes the client's certificate and a signature
4. KDC verifies the signature and certificate chain, then issues a TGT
5. No password needed — eliminates password-based attacks

### Benefits
- No more AS-REP roasting (no password to crack)
- Enables **smart card** and hardware token authentication
- Fits naturally into PKI-heavy enterprise environments
- Private key never leaves the hardware token (if using smart card)

### KDC Configuration (MIT Kerberos)
```ini
# kdc.conf
[kdcdefaults]
    pkinit_identity = FILE:/var/kerberos/krb5kdc/kdc.pem,/var/kerberos/krb5kdc/kdckey.pem
    pkinit_anchors = FILE:/etc/pki/ca-trust/source/anchors/ca.pem
```

## Smart Cards

Smart cards store the user's private key in tamper-resistant hardware. The private key never leaves the card; the card performs cryptographic operations internally.

With PKINIT:
- User inserts smart card and enters PIN (instead of password)
- Card performs AS_REQ signature on-chip
- KDC verifies and issues TGT

**Practical integration:**
- Linux: use `pam_pkcs11` or `pam_p11` with OpenSC for card access
- Windows: native smart card support via CryptoAPI
- macOS: CryptoTokenKit framework

## AES Encryption

The original Kerberos 5 implementations used DES (Data Encryption Standard, 56-bit) — now trivially broken. The evolution:

| Enctype | Status |
|---------|--------|
| `des-cbc-crc` | Broken; removed from MIT Kerberos 1.18+ |
| `des-cbc-md5` | Broken; removed from MIT Kerberos 1.18+ |
| `des3-cbc-sha1` | Legacy; avoid |
| `arcfour-hmac` (RC4) | Used by Windows; avoid if possible |
| `aes128-cts-hmac-sha1-96` | Current standard; good |
| **`aes256-cts-hmac-sha1-96`** | **Preferred; use this** |
| `aes128-cts-hmac-sha256-128` | RFC 8009; stronger HMAC |
| `aes256-cts-hmac-sha384-192` | RFC 8009; strongest available |

**Recommended configuration:**
```ini
[libdefaults]
    default_tgs_enctypes = aes256-cts aes128-cts
    default_tkt_enctypes = aes256-cts aes128-cts
    permitted_enctypes = aes256-cts aes128-cts
```

## Kerberos Referrals (RFC 6806)

Traditional cross-realm authentication requires the client to know the target realm. Referrals allow the KDC to tell the client "go ask that KDC instead" — the client doesn't need to be pre-configured with realm topology.

The AS can return referrals in AS_REP pointing the client to the correct KDC for their account. Simplifies cross-realm deployments dramatically, especially in large enterprises.

## Web Services and Modern Context

### SPNEGO in Browsers
All major browsers (Chrome, Firefox, Edge, Safari) support SPNEGO/Negotiate for single sign-on to internal web applications. This is now mature and widely deployed in enterprises.

### Kerberos in Cloud / Hybrid Environments
- **Azure AD Kerberos** — Azure AD can issue Kerberos tickets for on-premises resources, enabling cloud-joined clients to access Kerberos-protected on-prem services
- **AWS Directory Service** — Managed AD with Kerberos support
- Kerberos is increasingly used as a bridge between on-premises and cloud identity systems

### Constrained Delegation (S4U Extensions)
Microsoft's Service-for-User (S4U) extensions allow a service to request tickets on behalf of users without the user's credentials being present. Used in multi-tier web applications where the middle tier needs to delegate to a backend service as the user.
