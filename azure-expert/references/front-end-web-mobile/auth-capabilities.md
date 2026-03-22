# Authentication — Capabilities Reference
For CLI commands, see [auth-cli.md](auth-cli.md).

## App Service Easy Auth (Built-in Authentication)

**Purpose**: Add authentication to Azure App Service, Azure Functions, or Azure Container Apps without writing any authentication code. Easy Auth runs as a middleware layer in front of the application.

### How Easy Auth Works

```
HTTP Request
  → App Service Auth Middleware (validates token / redirects to login)
  → Your Application Code
  ← Response
```

- Intercepts all unauthenticated requests
- Redirects users to identity provider (login page) or returns 401/403
- Validates JWT tokens from identity providers
- Injects user claims as HTTP request headers (`X-MS-CLIENT-PRINCIPAL-*`)
- Manages session cookies and token refresh automatically
- Application code receives the request only after authentication succeeds

### Supported Identity Providers

| Provider | Protocol | Configuration |
|---|---|---|
| **Microsoft (Entra ID)** | OpenID Connect / OAuth 2.0 | App registration in Entra ID; any Microsoft account or Azure AD org |
| **Google** | OpenID Connect / OAuth 2.0 | Google OAuth 2.0 credentials |
| **Facebook** | OAuth 2.0 | Facebook App ID and secret |
| **GitHub** | OAuth 2.0 | GitHub OAuth App credentials |
| **Apple** | OpenID Connect | Apple Sign In configuration |
| **Twitter / X** | OAuth 1.0a | Twitter Developer App credentials |
| **Any OpenID Connect provider** | OpenID Connect | Custom configuration with issuer URL, client ID/secret |

### User Claims via Headers

After authentication, App Service injects these headers:

| Header | Value |
|---|---|
| `X-MS-CLIENT-PRINCIPAL-NAME` | User's display name or email |
| `X-MS-CLIENT-PRINCIPAL-ID` | User's unique identifier from the provider |
| `X-MS-CLIENT-PRINCIPAL-IDP` | Identity provider name (e.g., `aad`, `google`, `github`) |
| `X-MS-CLIENT-PRINCIPAL` | Base64-encoded JSON of all user claims |
| `X-MS-TOKEN-AAD-ACCESS-TOKEN` | Azure AD access token (if requested) |

```python
# Python: Read claims from headers (Flask example)
from flask import request
import base64, json

def get_user():
    claims_header = request.headers.get('X-MS-CLIENT-PRINCIPAL', '')
    if claims_header:
        decoded = base64.b64decode(claims_header).decode('utf-8')
        claims = json.loads(decoded)
        return claims
    return None
```

### Token Store

- Easy Auth stores identity provider tokens (access token, refresh token) in the token store
- Location: `${WEBSITE_CONTENTSHARE}/.auth/tokens/` (backed by Azure Files)
- Access tokens refreshed automatically when expired
- Your app code can access stored tokens via `/.auth/me` endpoint

### API Routes

| Route | Description |
|---|---|
| `/.auth/login/aad` | Sign in with Microsoft (Entra ID) |
| `/.auth/login/google` | Sign in with Google |
| `/.auth/login/github` | Sign in with GitHub |
| `/.auth/login/facebook` | Sign in with Facebook |
| `/.auth/logout` | Sign out (clears session) |
| `/.auth/me` | Get current user claims as JSON (must be authenticated) |
| `/.auth/refresh` | Manually refresh tokens |

---

## Azure Static Web Apps Built-in Authentication

**Purpose**: Zero-configuration authentication for Static Web Apps. Same provider support as Easy Auth but configured via `staticwebapp.config.json` — no code required.

### Configuration

```json
// staticwebapp.config.json
{
  "auth": {
    "identityProviders": {
      "github": {
        "userDetailsClaim": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name"
      },
      "google": {
        "registration": {
          "clientIdSettingName": "GOOGLE_CLIENT_ID",
          "clientSecretSettingName": "GOOGLE_CLIENT_SECRET"
        }
      }
    }
  },
  "routes": [
    {"route": "/api/private/*", "allowedRoles": ["authenticated"]},
    {"route": "/admin/*", "allowedRoles": ["administrator"]},
    {"route": "/profile", "allowedRoles": ["authenticated"]},
    {"route": "/*", "allowedRoles": ["anonymous"]}
  ],
  "responseOverrides": {
    "401": {"statusCode": 302, "redirect": "/.auth/login/github"}
  }
}
```

### SWA Auth Routes

| Route | Description |
|---|---|
| `/.auth/login/github` | GitHub login |
| `/.auth/login/aad` | Microsoft Entra ID login |
| `/.auth/login/google` | Google login |
| `/.auth/login/facebook` | Facebook login |
| `/.auth/login/apple` | Apple login |
| `/.auth/logout?post_logout_redirect_uri=/` | Logout |
| `/.auth/me` | Current user claims JSON |

### Custom Roles

- SWA has two built-in roles: `anonymous` (all users) and `authenticated` (signed-in users)
- Custom roles: assign via Azure Functions API webhook called after login
- Webhook URL configured in `staticwebapp.config.json` under `auth.rolesSource`
- Function receives user claims; returns roles array; used for route authorization

```json
// Custom role assignment via function
{
  "auth": {
    "rolesSource": "/api/get-user-roles"
  }
}
```

```javascript
// /api/get-user-roles: Returns custom roles based on user identity
module.exports = async function(context, req) {
    const { userId, userDetails, identityProvider } = req.body;
    // Look up user in database; determine roles
    const roles = await getUserRoles(userId);
    context.res = { body: { roles } };
};
```

---

## Microsoft Entra External ID

**Purpose**: Customer Identity and Access Management (CIAM) platform. Successor to Azure AD B2C for customer-facing apps. Provides branded sign-up/sign-in, social identity providers, MFA, and conditional access for consumer applications.

### Entra External ID vs Azure AD B2C

| Aspect | Azure AD B2C (Legacy) | Entra External ID |
|---|---|---|
| **Status** | Existing tenants supported; no new features | New platform; recommended for new projects |
| **User flows** | User flows (built-in) + Custom policies | User flows (simpler experience) |
| **Branding** | Company branding on login pages | Native app branding; hosted BYOI |
| **Identity providers** | Social (Google, Facebook, Apple, etc.) + SAML/OIDC federation | Same; broader default set |
| **Extensibility** | Custom policies (Identity Experience Framework XML) | Custom claims (simpler); event extensions via Functions |
| **Tenant type** | B2C tenant (separate from Azure AD) | External tenant (within Entra ID) |
| **Management** | Separate B2C admin portal | Standard Entra admin center |

### Key Capabilities

| Feature | Description |
|---|---|
| **User flows** | Pre-built sign-up, sign-in, password reset, profile editing flows |
| **Custom branding** | Logo, background, CSS customization; native app SDKs for custom UX |
| **Social providers** | Google, Facebook, Apple, GitHub, LinkedIn, Twitter/X, generic OIDC/SAML |
| **Local accounts** | Email + password; phone + OTP; username + password |
| **MFA** | Email OTP, SMS OTP, TOTP authenticator app |
| **Conditional access** | Block risky sign-ins; require MFA based on risk; named locations |
| **Self-service password reset** | User-initiated password reset via email/phone verification |
| **Custom claims** | Add custom attributes to tokens via REST API extensions |
| **MSAL integration** | Microsoft Authentication Library; all platforms |
| **Branded SDK** | Microsoft Authentication Library + Native UX library for iOS/Android |

### User Flow Types

| Flow | Description |
|---|---|
| **Sign up and sign in** | Combined flow: existing users sign in; new users register |
| **Sign in only** | No self-service registration; admin-created accounts only |
| **Password reset** | Self-service password reset |
| **Profile editing** | User updates their profile attributes |

### Token Configuration

- **ID token**: Claims about the user identity (sub, email, name, custom attributes)
- **Access token**: For calling your own APIs; scopes defined in app registration
- **Refresh token**: Lifetime up to 90 days (sliding window)
- **Optional claims**: Add profile claims (given_name, family_name, phone, etc.) to tokens

### MSAL Integration Example

```python
# Python MSAL for Entra External ID
from msal import PublicClientApplication

app = PublicClientApplication(
    CLIENT_ID,
    authority=f"https://{TENANT_NAME}.ciamlogin.com/{TENANT_NAME}.onmicrosoft.com"
)

# Device code flow (for CLI/headless)
flow = app.initiate_device_flow(scopes=["openid", "profile", "offline_access"])
result = app.acquire_token_by_device_flow(flow)

# Interactive (opens browser)
result = app.acquire_token_interactive(scopes=["openid", "profile"])
```

### Migration from Azure AD B2C

1. Create Entra External ID tenant (external tenant type)
2. Recreate user flows in new tenant
3. Migrate app registrations and API scopes
4. Update MSAL configuration: authority URL changes to `{tenant}.ciamlogin.com`
5. Export/import users: use Microsoft Graph API to export B2C users; import to External ID
6. Migrate custom policies to user flow + API extensions (simpler)
7. Test all sign-in/sign-up flows; validate tokens

### Azure AD B2C (Legacy Reference)

> Still valid for existing deployments; no new tenants recommended.

- **User flows**: Declarative policies for common scenarios; customize via portal
- **Custom policies**: XML-based Identity Experience Framework; maximum control; complex
- **B2C tenant**: Separate from work/school Azure AD; `{tenant}.b2clogin.com` endpoints
- **MSAL authority**: `https://{tenant}.b2clogin.com/{tenant}.onmicrosoft.com/B2C_1_signupsignin/v2.0/`
