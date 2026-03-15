# Identity Platform — Capabilities

## Overview

**Identity Platform** is the enterprise-grade upgrade of Firebase Authentication. It provides customer identity and access management (CIAM) for web and mobile applications, with additional features for enterprise use cases, large-scale applications, and SaaS platforms.

**Relationship to Firebase Auth:**
- Identity Platform is the same underlying infrastructure as Firebase Authentication
- Upgrading from Firebase Auth to Identity Platform unlocks additional features (listed below)
- Firebase Auth SDKs work with Identity Platform without code changes
- The upgrade is free and reversible (though reverting loses enterprise config)

---

## Identity Platform vs Firebase Authentication

| Feature | Firebase Auth | Identity Platform |
|---|---|---|
| Email/Password sign-in | Yes | Yes |
| OAuth (Google, Facebook, GitHub, etc.) | Yes | Yes |
| Phone/SMS sign-in | Yes | Yes |
| Anonymous sign-in | Yes | Yes |
| **SAML 2.0 SSO** | No | Yes |
| **OIDC providers** (any OIDC IdP) | No | Yes |
| **Multi-tenancy** | No | Yes |
| **Blocking functions** | No | Yes |
| **Custom SMTP server** | No | Yes |
| **Usage dashboards (MAU reporting)** | No | Yes |
| **Audit logging** | No | Yes |
| **Session revocation API** | No | Yes |
| **Enterprise support SLA** | No | Yes |

---

## Pricing

| Tier | Pricing |
|---|---|
| Free (Spark) | First 100 MAU/month/project |
| Pay-as-you-go | $0.0055/MAU after first 100 (for email, social providers) |
| SAML/OIDC providers | First 50 MAU free; $0.015/MAU after |
| Phone verification | $0.006/SMS (varies by country) |
| Multi-tenancy | Charged per tenant's MAU |

---

## Authentication Providers

### Email/Password

- Classic username/password authentication
- Email verification flow (send verification email)
- Password reset flow
- Email enumeration protection (disable to prevent user enumeration attacks)

### OAuth 2.0 Social Providers

Built-in support (out-of-the-box):
- Google
- Apple
- Facebook
- GitHub
- Microsoft (Azure AD personal accounts)
- Yahoo
- Twitter/X

Configuring requires registering an OAuth app in the provider's developer console and providing client ID + secret.

### SAML 2.0 (Enterprise SSO)

**Identity Platform exclusive** (not available in basic Firebase Auth).

Configure enterprise SSO with any SAML 2.0 Identity Provider:
- **Azure Active Directory (Azure AD / Entra ID)**: most common enterprise IdP
- **Okta**: most common third-party IdP
- **PingFederate / PingOne**: large enterprise deployments
- **Shibboleth**: higher education and government
- **ADFS (Active Directory Federation Services)**: on-premises Microsoft AD federation
- Any SAML 2.0 compliant IdP

**Configuration required:**
- SP (Service Provider) metadata: Identity Platform provides its Entity ID and ACS URL
- IdP metadata: upload XML metadata file from the enterprise IdP
- Attribute mappings: map SAML attributes (email, first name, last name) to Firebase user profile fields

### OIDC Identity Providers

Support for any OIDC-compliant identity provider:
- Azure AD (both personal and enterprise accounts)
- Okta
- Auth0
- Custom OIDC providers
- Line, WeChat, and other regional social providers

**Configuration:** Client ID, Client Secret, Issuer URL (discovery document endpoint).

### Phone Number (SMS)

- SMS verification code sent to phone number
- Sign-in or link phone to existing account
- App verification: automatically validates genuine app installs (App Check integration)
- SafetyNet attestation on Android, App Attest on iOS

---

## Multi-Tenancy

**Multi-tenancy** enables a single Identity Platform project to serve multiple isolated authentication contexts (tenants).

### Use Cases

- **SaaS applications**: each customer organization is a separate tenant; users are isolated per tenant
- **White-label apps**: same application codebase, different authentication configs per brand/client
- **Internal vs external users**: separate tenants for employees vs customers

### Tenant Architecture

```
Identity Platform Project
├── Tenant: "acme-corp" (SAML SSO with Acme's Azure AD)
│   └── Users: john@acme.com, jane@acme.com
├── Tenant: "widgetco" (Google + Email/Password)
│   └── Users: bob@widgetco.com, alice@widgetco.com
└── Tenant: "beta-customers" (Email/Password only)
    └── Users: tester1@gmail.com, tester2@gmail.com
```

### Tenant Configuration

- Each tenant has its own set of enabled sign-in providers
- Each tenant has its own set of SAML/OIDC IdP configurations
- Users exist within a tenant; no cross-tenant user lookup
- Authentication tokens (JWTs) are tenant-scoped
- Admin SDK can manage users per-tenant

### SDK Usage with Tenants

```javascript
// Client-side: specify tenant before sign-in
firebase.auth().tenantId = 'acme-corp';
firebase.auth().signInWithPopup(provider); // signs in as Acme Corp user

// Admin SDK: manage tenant users
const tenantManager = admin.auth().tenantManager();
const tenantClient = tenantManager.authForTenant('acme-corp');
const userRecord = await tenantClient.getUser(uid);
```

---

## Blocking Functions

**Blocking functions** are Cloud Functions that execute synchronously during authentication events, allowing you to:
- Block sign-ins or sign-ups based on custom logic
- Modify user profiles before they are created or signed in
- Enforce custom validation (e.g., only allow @company.com email addresses)

### Supported Events

- **beforeCreate**: runs before a new user is created; can block account creation
- **beforeSignIn**: runs before a user is issued a sign-in token; can block sign-in

### Use Cases

- **Domain restriction**: reject sign-up from non-corporate email domains
- **Account approval workflow**: require admin approval before new accounts are created
- **User enrichment**: populate custom claims from your database before token issuance
- **Risk scoring**: block sign-in from suspicious IPs or failed previous attempts
- **Audit logging**: log every authentication event to your own systems

### Example Blocking Function

```javascript
// Cloud Function: only allow @example.com email addresses to register
const functions = require('firebase-functions');

exports.beforeCreate = functions.auth.user().beforeCreate((user, context) => {
  if (!user.email || !user.email.endsWith('@example.com')) {
    throw new functions.auth.HttpsError(
      'invalid-argument',
      'Only @example.com email addresses are allowed to register.'
    );
  }
  // User creation proceeds normally
});
```

---

## Session Management

### Custom Session Duration

Identity Platform supports configuring session expiration:
- **Persistent sessions**: user stays logged in for up to 365 days
- **Short sessions**: force re-authentication after X hours
- **Session revocation**: admin can revoke all active sessions for a user (e.g., after password reset, account compromise)

### Session Cookies

For server-side rendered apps (not SPAs), use Firebase/Identity Platform session cookies:
- Mint a session cookie via the Admin SDK on server sign-in
- Set as HTTP-only, secure cookie
- Verify on subsequent requests server-side
- Revoke session cookie on logout or suspicious activity

---

## Custom SMTP

By default, Firebase Auth sends emails (verification, password reset) from a Google-owned address. Identity Platform allows:
- Configure your own SMTP server (SendGrid, Mailgun, AWS SES, or your own SMTP)
- Custom `from` email address and display name
- Custom email templates (HTML with variables)
- Localized email templates per language

---

## App Check Integration

**App Check** verifies that requests to Identity Platform come from authentic app instances:
- Android: Google Play Integrity API or SafetyNet
- iOS: App Attest or DeviceCheck
- Web: reCAPTCHA Enterprise or reCAPTCHA v3

Prevents abuse by automated scripts and prevents unauthorized apps from using your Identity Platform project.
