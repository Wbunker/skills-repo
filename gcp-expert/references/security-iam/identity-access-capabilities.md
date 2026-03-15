# Identity & Access — Capabilities

## Cloud Identity

### Purpose
Cloud Identity is Google's managed Identity-as-a-Service (IDaaS) for managing users, groups, and devices for an organization. It provides the identity layer for GCP (and Google Workspace) — all users accessing GCP resources must have a Google identity, and Cloud Identity is how organizations manage those identities.

### Free vs Premium
| Feature | Free | Premium |
|---|---|---|
| User and group management | Yes | Yes |
| SSO with SAML/OIDC | Yes | Yes |
| Basic device management | No | Yes |
| Advanced mobile device management (MDM) | No | Yes |
| Context-aware access | No | Yes |
| Advanced audit and reporting | No | Yes |
| Endpoint verification | No | Yes |

### Core capabilities
- **User management**: create, modify, suspend, delete users; manage password policies; enforce 2FA/MFA (TOTP, security keys, phone prompts)
- **Group management**: nested groups; dynamic groups (auto-membership based on user attributes); security groups for IAM bindings
- **Single Sign-On (SSO)**: act as an SAML 2.0 or OIDC IdP for third-party SaaS applications; also act as a SAML SP (service provider) consuming external IdPs
- **Directory synchronization**: sync users and groups from Active Directory, LDAP, or HR systems using Google Cloud Directory Sync (GCDS) or third-party connectors
- **External identity federation**: integrate Azure AD, Okta, Ping Identity, ADFS as the authoritative IdP; users authenticate at the external IdP, then access GCP
- **Admin console**: web-based management interface at admin.google.com; full API access via Admin SDK

---

## Identity Platform (Firebase Authentication)

### Purpose
Identity Platform (formerly Firebase Authentication when offered only through Firebase; now also available standalone in GCP) provides **customer-facing authentication** for web and mobile applications. It is not for managing internal employee identities; it is for managing your end-users' accounts.

### Authentication providers supported
| Category | Providers |
|---|---|
| Email/Password | Native email+password, passwordless email link |
| Phone | SMS OTP |
| Social | Google, Facebook, Apple, Twitter (X), GitHub, Microsoft, Yahoo |
| SAML 2.0 | Enterprise SAML (Okta, AD FS, Azure AD) |
| OIDC | Custom OIDC providers |
| Anonymous | Temporary anonymous sessions that can be upgraded |
| Custom | JWT-based custom authentication from your own system |

### Key features
- **Multi-tenancy**: Separate authentication namespaces (tenants) within one project; useful for B2B SaaS where each customer gets an isolated identity space
- **Blocking functions**: Cloud Functions triggered before account creation or sign-in to allow/deny or enrich the user
- **Linked accounts**: allow users to link multiple providers to one account (e.g., sign in with Google or email on the same account)
- **Email enumeration protection**: optionally block email-based enumeration attacks
- **Multi-factor authentication (MFA)**: TOTP and SMS MFA for email+password and federated users
- **Session management**: configurable session duration; token revocation
- **User management API**: create, update, delete, disable users; list users; batch import
- **Admin SDK**: server-side user management in Node.js, Python, Java, Go, etc.
- **Identity Platform vs Firebase Auth**: same underlying service; Identity Platform has SLAs, CMEK support, multi-tenancy, and enterprise support; Firebase Auth is the simpler free tier for mobile apps

---

## Cloud Identity-Aware Proxy (IAP)

### Purpose
IAP provides **zero-trust access to internal applications** hosted on GCP without requiring a VPN. It acts as an application-layer access control layer, verifying that the user is authenticated and authorized before proxying the request to the backend application.

### How it works
1. User navigates to the protected application URL.
2. IAP intercepts the request.
3. If the user is not authenticated, IAP redirects to the Google sign-in page (OAuth 2.0 flow).
4. After authentication, IAP verifies the user has the `roles/iap.httpsResourceAccessor` binding on the IAP resource.
5. If authorized, IAP forwards the request to the backend, injecting `X-Goog-Authenticated-User-Email` and `X-Goog-IAP-JWT-Assertion` headers.
6. The backend application can optionally validate the IAP JWT header to prevent direct access bypassing IAP.

### Supported backends
- App Engine (Standard and Flexible) — configured at service or version level
- Cloud Run — configured via IAP tunnel or direct IAP integration
- Compute Engine (Backend Services in a load balancer)
- GKE (via BackendConfig resource)
- On-premises applications (via IAP connector and Cloud Interconnect/VPN)

### TCP Tunneling
IAP can create encrypted tunnels to TCP services (SSH, RDP, database ports) on private Compute Engine instances **without exposing them to the internet**:
- User runs `gcloud compute start-iap-tunnel INSTANCE PORT` locally.
- The command creates a WebSocket tunnel through IAP to the VM.
- No public IP required on the VM; firewall rules allow only IAP's IP range (`35.235.240.0/20`).
- IAM binding controls who can tunnel.

### Context-Aware Access
Combine IAP with Access Context Manager to add device trust conditions:
- Allow access only from managed (Endpoint Verified) devices
- Require specific OS versions, encryption status, or certificate presence
- Corporate network (IP range) requirements

### IAP JWT validation (backend verification)
Backend applications should validate the `X-Goog-IAP-JWT-Assertion` JWT to ensure requests came through IAP and not via a direct IP bypass. Use Google's public keys at `https://www.gstatic.com/iap/verify/public_key` for validation.

---

## BeyondCorp Enterprise

### Purpose
BeyondCorp Enterprise is Google's zero-trust access solution for enterprise workforces, extending IAP with device management, endpoint verification, and policy-based access for all applications (internal and SaaS).

### Components
- **Identity-Aware Proxy (IAP)**: the access proxy for GCP-hosted applications
- **Chrome Enterprise**: browser-based device trust; policies enforced via Chrome browser
- **Endpoint Verification**: agent installed on managed endpoints that reports device compliance status (OS version, disk encryption, screen lock, certificates) to Cloud Identity
- **Access Context Manager**: access levels that combine user identity, device trust, and network context into reusable conditions
- **Context-Aware Access**: apply access levels to IAP, Google Workspace, SaaS apps, and GCP IAM

### Access levels (examples)
- `HIGH_TRUST`: Endpoint Verified + managed device + corporate network
- `MEDIUM_TRUST`: Endpoint Verified + managed device (any network)
- `CORP_NETWORK_ONLY`: access restricted to specific IP ranges

### Applying access levels
Access levels can be applied to:
- IAP-protected applications (via IAP settings)
- Google Workspace admin-defined apps
- GCP IAM bindings (via `request.auth.access_levels` in IAM conditions)
- VPC Service Controls perimeters

### BeyondCorp vs Traditional VPN
| | Traditional VPN | BeyondCorp |
|---|---|---|
| Trust model | Network perimeter (inside VPN = trusted) | Zero-trust (every request verified) |
| User experience | VPN client required | Browser-based (no client for web apps) |
| Device trust | All devices in network perimeter treated equally | Per-device verification |
| Access granularity | All resources on VPN subnet | Per-application policy |
| Scalability | VPN gateway bottleneck | Cloud-scale proxy |

---

## Managed Service for Microsoft Active Directory (Managed AD)

### Purpose
A fully managed Microsoft Active Directory service running in GCP. Designed for organizations running Windows workloads that require traditional AD (LDAP, Kerberos, Group Policy, DNS, NTLMv2, and Active Directory-aware applications) without managing AD domain controllers.

### Key features
- Managed domain controllers (Google manages patching, replication, backups)
- Deploy in one or more GCP regions for high availability
- **Trust with on-premises AD**: create a two-way or one-way forest trust with your on-premises Active Directory for unified identity (users authenticate with their corp AD credentials to access GCP resources)
- **Domain join**: GCP Compute Engine Windows VMs can join the managed domain
- **Group Policy Objects (GPOs)**: manage Windows VMs via standard AD GPOs
- **LDAP**: applications using LDAP for directory queries can point to Managed AD
- **Schema extensions**: limited schema extensions supported
- Peering: extend the managed domain to additional GCP projects or VPCs via VPC peering or Shared VPC

### Use cases
- Lift-and-shift Windows applications that require domain join
- File servers on GCP (Cloud Filestore with SMB + AD authentication)
- Remote Desktop Services deployments
- Legacy applications using Kerberos or NTLM authentication

---

## Workforce Identity Federation

Workforce Identity Federation (distinct from Workload Identity Federation) allows **external human users** (employees using a corporate IdP like Okta, Azure AD, or ADFS) to access GCP resources using their existing enterprise credentials, without requiring Google accounts or Cloud Identity licensing.

### How it works
1. Create a **Workforce Identity Pool** (org-level resource).
2. Configure a **SAML or OIDC provider** pointing to the corporate IdP.
3. Define attribute mappings (map IdP claims to Google attributes: `google.subject`, `google.email`, `google.groups`).
4. Grant IAM bindings using workforce pool principal identifiers.
5. Users authenticate at their corporate IdP → receive a short-lived Google token via STS token exchange → access GCP.

### Comparison: Cloud Identity vs Workforce Identity Federation

| | Cloud Identity | Workforce Identity Federation |
|---|---|---|
| User provisioning | Users exist as Google identities | Users exist only in the external IdP |
| License cost | Per-user (Free or Premium) | No per-user Google license needed |
| Google account features | Full Google account (Gmail, Drive, etc.) | GCP access only |
| Setup complexity | Lower; user management in Google Admin | Higher; requires IdP and attribute mapping config |
| Best for | Organizations standardizing on Google | Organizations wanting to reuse existing enterprise IdP without Google accounts |

---

## Best Practices

1. **Use groups for IAM assignments**: assign roles to Google Groups, not individual users; manage membership in Cloud Identity or Google Workspace.
2. **Enforce MFA/2-step verification**: require security keys (FIDO2/WebAuthn) or TOTP for all admin and developer accounts.
3. **Use IAP for internal tool access**: replace VPN with IAP for web applications; use IAP TCP tunneling for SSH/RDP to private VMs.
4. **Enable Endpoint Verification** for developer and admin workstations; use access levels to enforce device trust for sensitive applications.
5. **Prefer Workforce Identity Federation** for enterprise environments with existing IdPs — avoid creating Google accounts for all employees if a corporate IdP already exists.
6. **Restrict external IdP configuration to org admins**: the ability to configure SSO and external identity federation should be strictly controlled.
7. **Use Cloud Identity dynamic groups** to auto-assign IAM based on user attributes (department, location) rather than manually managing group membership.
8. **Validate IAP JWTs** in backend applications: don't rely solely on IAP for authorization; verify the JWT header to detect direct-to-backend requests.
9. **Rotate service account credentials** used for GCDS (Cloud Directory Sync) regularly and restrict them to only the necessary Admin SDK scopes.
10. **Audit Identity Platform tenants**: regularly review user accounts and anonymous session counts in Identity Platform for abnormal activity patterns.
