# Microsoft Graph Authentication Flows

Microsoft Graph uses OAuth 2.0 / OpenID Connect via the Microsoft identity platform.
All tokens are obtained from:
```
https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token
```

## Flow 0: Azure CLI (Local / Personal Use — Recommended Starting Point)

**No app registration needed. Equivalent to `gcloud auth login`.**

```bash
brew install azure-cli
az login   # opens browser, authenticates as you, stores session locally
```

Then in Python — zero config:

```python
from azure.identity import AzureCliCredential
from msgraph import GraphServiceClient

credential = AzureCliCredential()
graph_client = GraphServiceClient(credential, ["https://graph.microsoft.com/.default"])
```

`AzureCliCredential` reads the token from the local Azure CLI session automatically, handling refresh. Use this for personal assistants and local scripts acting as yourself.

---

## Two Access Scenarios

### 1. Delegated Access (On Behalf of a User)
- A signed-in user authenticates; the app acts on their behalf
- Limited to what the user can access
- Use `/me` endpoints
- Permissions are called "delegated permissions" or "scopes"
- Example flows: Authorization Code, Device Code, Interactive Browser

### 2. App-Only Access (No User / Daemon / Background Service)
- The app authenticates with its own identity using a client secret or certificate
- Can access any user's data if granted application permissions
- No `/me` — use `/users/{user-id}` instead
- Requires admin consent for all permissions
- Flow: Client Credentials Grant
- Scope is always `https://graph.microsoft.com/.default`

## Choosing a Flow

| Scenario | Flow | Best for |
|----------|------|----------|
| Automation/scripts, no user | Client Credentials | Background jobs, scheduled tasks |
| Script run interactively once | Device Code | CLI tools, initial setup |
| Web application | Authorization Code (PKCE) | Web apps with login |
| Desktop app | Interactive Browser | GUI applications |
| Service calling service | On-Behalf-Of | API chains |

## Flow 1: Client Credentials (App-Only) — Most Common for Automation

**No user interaction. Best for scripts and background jobs.**

### Raw HTTP

```http
POST https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token
Content-Type: application/x-www-form-urlencoded

client_id=YOUR_CLIENT_ID
&client_secret=YOUR_CLIENT_SECRET
&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default
&grant_type=client_credentials
```

### Response

```json
{
  "token_type": "Bearer",
  "expires_in": 3599,
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIs..."
}
```

### Python (SDK — Recommended)

```python
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient

credential = ClientSecretCredential(
    tenant_id="YOUR_TENANT_ID",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
)
scopes = ["https://graph.microsoft.com/.default"]
graph_client = GraphServiceClient(credential, scopes)
```

### Python (MSAL — Lower Level)

```python
import msal

app = msal.ConfidentialClientApplication(
    client_id="YOUR_CLIENT_ID",
    authority=f"https://login.microsoftonline.com/YOUR_TENANT_ID",
    client_credential="YOUR_CLIENT_SECRET",
)

result = app.acquire_token_for_client(
    scopes=["https://graph.microsoft.com/.default"]
)

if "access_token" in result:
    token = result["access_token"]
else:
    raise Exception(result.get("error_description"))
```

### Python (Certificate — Production Preferred)

```python
from azure.identity import CertificateCredential
from msgraph import GraphServiceClient

credential = CertificateCredential(
    tenant_id="YOUR_TENANT_ID",
    client_id="YOUR_CLIENT_ID",
    certificate_path="/path/to/certificate.pem",
)
scopes = ["https://graph.microsoft.com/.default"]
graph_client = GraphServiceClient(credential, scopes)
```

## Flow 2: Device Code (Delegated — Interactive CLI)

**User opens a browser on any device to authenticate. Good for scripts.**

```python
from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient

# The user will be shown a URL and code to enter in a browser
credential = DeviceCodeCredential(
    tenant_id="YOUR_TENANT_ID",
    client_id="YOUR_CLIENT_ID",
    # Optional: customize the prompt message
)

scopes = ["Mail.ReadWrite", "Calendars.ReadWrite", "Files.ReadWrite.All"]
graph_client = GraphServiceClient(credential, scopes)

# First API call triggers the device code prompt automatically
```

**Note**: The app registration must have "Allow public client flows" enabled:
- App registration > Authentication > Advanced settings > "Allow public client flows" = Yes

## Flow 3: Authorization Code with PKCE (Delegated — Web Apps)

For web applications where the user logs in via browser. Redirect URI required.

```python
from azure.identity import AuthorizationCodeCredential
from msgraph import GraphServiceClient

# After user redirects back with an authorization code from:
# https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize
# ?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}
# &scope=Mail.ReadWrite+Calendars.ReadWrite

credential = AuthorizationCodeCredential(
    tenant_id="YOUR_TENANT_ID",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",   # For confidential clients
    authorization_code="CODE_FROM_REDIRECT",
    redirect_uri="https://your-app.com/callback",
)

scopes = ["Mail.ReadWrite", "Calendars.ReadWrite"]
graph_client = GraphServiceClient(credential, scopes)
```

## Flow 4: Interactive Browser (Delegated — Desktop Apps)

Opens the system browser automatically for login:

```python
from azure.identity import InteractiveBrowserCredential
from msgraph import GraphServiceClient

credential = InteractiveBrowserCredential(
    tenant_id="YOUR_TENANT_ID",
    client_id="YOUR_CLIENT_ID",
    redirect_uri="http://localhost:8080",
)

scopes = ["User.Read", "Mail.ReadWrite"]
graph_client = GraphServiceClient(credential, scopes)
```

## Making Raw HTTP Calls (Without SDK)

```python
import httpx

# 1. Get token
token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
response = httpx.post(token_url, data={
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "scope": "https://graph.microsoft.com/.default",
    "grant_type": "client_credentials",
})
token = response.json()["access_token"]

# 2. Call Graph API
headers = {"Authorization": f"Bearer {token}"}
r = httpx.get("https://graph.microsoft.com/v1.0/me/messages", headers=headers)
messages = r.json()
```

## Token Caching (MSAL)

MSAL supports in-memory and serializable token caches to avoid re-authenticating:

```python
import msal
import json
import os

cache_file = "token_cache.json"
cache = msal.SerializableTokenCache()

if os.path.exists(cache_file):
    cache.deserialize(open(cache_file).read())

app = msal.ConfidentialClientApplication(
    client_id=CLIENT_ID,
    authority=f"https://login.microsoftonline.com/{TENANT_ID}",
    client_credential=CLIENT_SECRET,
    token_cache=cache,
)

result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

# Save updated cache
if cache.has_state_changed:
    with open(cache_file, "w") as f:
        f.write(cache.serialize())
```

**Add `token_cache.json` to `.gitignore`** — it contains access tokens.

## Admin Consent URL

To grant admin consent without the Entra portal UI:

```
https://login.microsoftonline.com/{tenant}/adminconsent
  ?client_id={client_id}
  &redirect_uri=https://localhost/myapp/permissions
  &state=12345
```

An admin navigates to this URL, logs in, and approves. The response includes
`admin_consent=True` as a query parameter on the redirect.

## Key Facts

- Access tokens expire in **3599 seconds (1 hour)**
- `expires_in` and `ext_expires_in` in the token response
- The SDK (azure-identity) handles token refresh automatically
- For MSAL, call `acquire_token_silently()` before `acquire_token_for_client()` to use cached tokens
- App-only tokens cannot use `/me` — they have no "me" user; always use `/users/{id}`
- Multi-factor authentication (MFA) is supported in delegated flows only
- Conditional Access policies may block app-only access in some tenants
