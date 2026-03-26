# Confluence Authentication Reference

## Method Decision Tree

```
Is this a personal script or one-off automation on Confluence Cloud?
  └─ YES → API Token + Basic Auth (simplest)

Is this a personal script or automation on Confluence Data Center?
  └─ YES → Personal Access Token (PAT) + Bearer Auth

Is this a user-facing web app acting on behalf of users?
  └─ YES → OAuth 2.0 (3LO)

Is this an app hosted on Atlassian's Forge platform?
  └─ YES → Forge built-in auth (no token needed)

Is this a Marketplace Connect app?
  └─ YES → JWT with app credentials
```

---

## API Token + Basic Authentication (Cloud)

Best for: scripts, bots, CI/CD pipelines, personal automation against Confluence Cloud.

### Step 1: Generate an API token
Go to: `https://id.atlassian.com/manage/api-tokens`
- Click "Create API token"
- Copy the token immediately — it won't be shown again
- Tokens are per Atlassian account; they work across all Atlassian Cloud products

### Step 2: Construct the header

```python
import base64

email = "you@example.com"
api_token = "YOUR_API_TOKEN"
credentials = base64.b64encode(f"{email}:{api_token}".encode()).decode()
# Use in header: Authorization: Basic <credentials>
```

```
Authorization: Basic eW91QGV4YW1wbGUuY29tOllPVVJfQVBJX1RPS0VO
Content-Type: application/json
Accept: application/json
```

### curl example

```bash
curl -u "you@example.com:YOUR_API_TOKEN" \
  -H "Accept: application/json" \
  "https://your-domain.atlassian.net/wiki/rest/api/content?spaceKey=ENG&limit=10"
```

### Python (requests library)

```python
import requests

CONFLUENCE_BASE = "https://your-domain.atlassian.net/wiki/rest/api"
AUTH = ("you@example.com", "YOUR_API_TOKEN")
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

r = requests.get(f"{CONFLUENCE_BASE}/space", auth=AUTH, headers=HEADERS)
r.raise_for_status()
print(r.json())
```

### Python (atlassian-python-api library)

```bash
pip install atlassian-python-api
```

```python
from atlassian import Confluence

confluence = Confluence(
    url="https://your-domain.atlassian.net",
    username="you@example.com",
    password="YOUR_API_TOKEN",
    cloud=True
)

page = confluence.get_page_by_title(space="ENG", title="My Page")
print(page)
```

---

## Personal Access Tokens — Data Center Only

Data Center (on-premises) does not use API tokens. Instead, use Personal Access Tokens (PATs) with Bearer authentication.

### Generate a PAT
1. Log in to your Confluence Data Center instance
2. Go to: Profile menu → Settings → Personal Access Tokens
3. Click "Create token" and copy it immediately

### Use the PAT

```bash
curl -H "Authorization: Bearer YOUR_PAT_TOKEN" \
  -H "Accept: application/json" \
  "https://confluence.yourcompany.com/wiki/rest/api/space"
```

```python
import requests

CONFLUENCE_BASE = "https://confluence.yourcompany.com/wiki/rest/api"
HEADERS = {
    "Authorization": "Bearer YOUR_PAT_TOKEN",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

r = requests.get(f"{CONFLUENCE_BASE}/space", headers=HEADERS)
```

```python
from atlassian import Confluence

confluence = Confluence(
    url="https://confluence.yourcompany.com",
    token="YOUR_PAT_TOKEN"
)
```

---

## OAuth 2.0 (3LO — Three-Legged OAuth) — Cloud Only

Best for: apps that act on behalf of a user. Requires app registration in the Atlassian developer console.

### Setup

1. Create an OAuth 2.0 app: `https://developer.atlassian.com/console/myapps/`
2. Add the "Confluence API" product and select scopes
3. Set your redirect URI
4. Get your `CLIENT_ID` and `CLIENT_SECRET`

### Authorization flow

**Step 1: Redirect user**
```
GET https://auth.atlassian.com/authorize
  ?audience=api.atlassian.com
  &client_id=YOUR_CLIENT_ID
  &scope=read%3Aconfluence-content.all%20write%3Aconfluence-content
  &redirect_uri=https%3A%2F%2Fyourapp.com%2Fcallback
  &state=RANDOM_STATE_STRING
  &response_type=code
  &prompt=consent
```

**Step 2: Exchange code for tokens**
```http
POST https://auth.atlassian.com/oauth/token
Content-Type: application/json

{
  "grant_type": "authorization_code",
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "code": "AUTH_CODE_FROM_CALLBACK",
  "redirect_uri": "https://yourapp.com/callback"
}
```

**Step 3: Get cloud ID**
```http
GET https://api.atlassian.com/oauth/token/accessible-resources
Authorization: Bearer ACCESS_TOKEN
```
Returns list of sites; each has an `id` field (the cloud ID).

**Step 4: Call the API using cloud ID**
```
https://api.atlassian.com/ex/confluence/{cloudId}/wiki/rest/api/content
Authorization: Bearer ACCESS_TOKEN
```

**Step 5: Refresh access token**
```http
POST https://auth.atlassian.com/oauth/token
{
  "grant_type": "refresh_token",
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "refresh_token": "YOUR_REFRESH_TOKEN"
}
```

### Common Confluence OAuth 2.0 Scopes

Atlassian provides two tiers of scopes. **Classic scopes** (fewer than 50) are recommended for most apps:

| Classic Scope | Access |
|---|---|
| `read:confluence-content.all` | Read pages, blogposts, comments, attachments |
| `write:confluence-content` | Create and update content |
| `read:confluence-space.summary` | Read space details |
| `write:confluence-space` | Create and update spaces |
| `read:confluence-props` | Read content properties |
| `write:confluence-props` | Write content properties |
| `manage:confluence-configuration` | Admin-level configuration |
| `read:confluence-user` | Read user information |
| `offline_access` | Get a refresh token |

**Granular scopes** (80+ available) offer per-resource precision — e.g., `read:page:confluence`, `write:page:confluence`, `read:space:confluence`. Use these when you need minimal-permission apps.

> **Note on v1 deprecation:** Most Confluence Cloud v1 REST API endpoints were deprecated March 31, 2025. The classic OAuth scopes still work with both v1 and v2. Prefer v2 endpoints for new Cloud integrations; v1 remains required for search and some operations not yet migrated to v2.

---

## Forge Apps

Forge apps run on Atlassian's infrastructure. Authentication is handled automatically.

```javascript
import { requestConfluence } from '@forge/api';

const response = await requestConfluence('/wiki/rest/api/space');
const data = await response.json();
```

Scopes declared in `manifest.yml`:
```yaml
permissions:
  scopes:
    - read:confluence-content.all
    - write:confluence-content
```

---

## Connect Apps (JWT)

Connect apps authenticate with JWT signed by the shared secret Atlassian provides during installation.

```javascript
// atlassian-connect-express handles JWT signing automatically
app.get('/page', addon.authenticate(), async (req, res) => {
  const client = addon.httpClient(req);
  const result = await client.get('/wiki/rest/api/space');
  res.json(result);
});
```

---

## Security Notes

- Never commit tokens or secrets to source control; use environment variables or a secrets manager
- API tokens bypass 2FA — treat them as passwords
- PATs (Data Center) are equivalent to passwords — rotate regularly and revoke when unused
- Scope OAuth tokens to the minimum required permissions
- For shared automation accounts, use a dedicated service account, not a personal account
- OAuth 2.0 is strongly preferred over API tokens for any multi-user or customer-facing applications
