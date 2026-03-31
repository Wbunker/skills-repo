# Chapter 2 — Kerberos Concepts and Terminology

## The Three As

- **Authentication** — Verifying identity: "Who are you?" Kerberos handles this directly.
- **Authorization** — Determining access: "What are you allowed to do?" Kerberos provides authenticated identity; authorization is handled by the application or a directory service.
- **Auditing** — Recording activity: "What did you do?" Kerberos generates logs at the KDC for every ticket issuance.

## Realms

A **realm** is an administrative domain — a set of principals managed by a single KDC. By convention, realm names are UPPERCASE and often match a DNS domain (e.g., `EXAMPLE.COM`). Clients and services in a realm share trust in that realm's KDC. Multiple realms can establish **cross-realm trust** (see ch08-advanced.md).

## Principals

A principal is a unique identity in a Kerberos realm. Format: `primary/instance@REALM`

| Type | Kerberos 5 example | Notes |
|------|--------------------|-------|
| User | `alice@EXAMPLE.COM` | Instance is optional for users |
| Service | `http/webserver.example.com@EXAMPLE.COM` | `primary` = service name, `instance` = FQDN |
| Host | `host/server.example.com@EXAMPLE.COM` | Used for general host access (rsh, telnet) |
| KDC | `krbtgt/EXAMPLE.COM@EXAMPLE.COM` | The ticket-granting ticket service principal |

Kerberos 4 used a different format: `primary.instance@REALM` (dot separator).

## Keys, Passwords, and Salts

- Each principal has a **long-term key** derived from their password using a string-to-key function
- A **salt** is mixed with the password before hashing to prevent precomputation attacks; salt format differs between Kerberos 4 (username + realm) and Kerberos 5 (configurable)
- The KDC stores these long-term keys in the **Kerberos database** (never the plaintext password)
- Service principals typically have **random keys** (not password-derived), stored in a **keytab file**

## Key Distribution Center (KDC)

The KDC is the trusted third party. It has two logical components:

### Authentication Server (AS)
- Handles the initial login exchange
- Client presents principal name; AS issues a **Ticket Granting Ticket (TGT)**
- The TGT is encrypted with the KDC's own secret key (`krbtgt` principal)

### Ticket Granting Server (TGS)
- Client presents the TGT to get service tickets
- Issues **service tickets** encrypted with the target service's key
- Client never needs to contact the KDC again for that service

## Tickets

A ticket is an encrypted token that proves identity. The client cannot decrypt their own service ticket — it is addressed to the service. Contents include:

- Client principal name
- Server principal name
- Client IP address (optional; Kerberos 5 makes this configurable)
- Validity times: auth time, start time, end time, renew-till time
- **Session key** — a temporary symmetric key shared between client and service
- Ticket flags (see below)

### Ticket Flags

| Flag | Meaning |
|------|---------|
| `FORWARDABLE` | Can be forwarded to another host |
| `PROXIABLE` | A new ticket can be obtained with different addresses |
| `RENEWABLE` | Can be renewed before expiry without re-authenticating |
| `INITIAL` | Obtained directly from AS (not via TGS) |
| `PRE-AUTHENT` | Pre-authentication was used |
| `HW-AUTHENT` | Hardware-based pre-authentication used |

### Ticket Lifetimes
- Default lifetime: **10 hours**
- Default renewable life: **7 days**
- Clock skew tolerance: **5 minutes** (configurable; critical — see ch05)

## Credential Cache

The **credential cache** (ccache) stores tickets on the client. Location:

| Platform | Default location |
|----------|----------------|
| Linux/Unix | `/tmp/krb5cc_<uid>` |
| macOS | Keychain or `/tmp/krb5cc_<uid>` |
| Windows | In-memory (LSASS) |

Use `klist` to view cached tickets, `kdestroy` to clear them.

## Keytab Files

A **keytab** (key table) stores service principal keys for non-interactive (daemon) authentication. The service reads its key from the keytab to decrypt service tickets from clients.

- Default location: `/etc/krb5.keytab`
- Manage with: `ktutil` or `kadmin ktadd`
- Protect carefully: possession of a keytab is equivalent to knowing the service password
