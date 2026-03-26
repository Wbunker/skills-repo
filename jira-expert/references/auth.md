# Jira Authentication Reference

## Method Decision Tree

```
Is this a personal script or one-off automation?
  └─ YES → API Token + Basic Auth (simplest)

Is this a user-facing web app acting on behalf of users?
  └─ YES → OAuth 2.0 (3LO)

Is this an app hosted on Atlassian's Forge platform?
  └─ YES → Forge built-in auth (no token needed)

Is this a Marketplace Connect app?
  └─ YES → JWT with app credentials
```

---

## API Token + Basic Authentication

Best for: scripts, bots, CI/CD pipelines, personal automation.

### Step 1: Generate an API token
Go to: `https://id.atlassian.com/manage/api-tokens`
- Click "Create API token"
- Copy the token immediately — it won't be shown again
- Tokens are per Atlassian account and can be revoked individually

### Step 2: Construct the header

```python
import base64

email = "you@example.com"
api_token = "YOUR_API_TOKEN"
credentials = base64.b64encode(f"{email}:{api_token}".encode()).decode()
# credentials = "eW91QGV4YW1wbGUuY29tOllPVVJfQVBJX1RPS0VO"
```

```
Authorization: Basic eW91QGV4YW1wbGUuY29tOllPVVJfQVBJX1RPS0VO
Content-Type: application/json
Accept: application/json
```

### curl example

```bash
curl -X GET \
  -H "Authorization: Basic $(echo -n 'you@example.com:YOUR_API_TOKEN' | base64)" \
  -H "Content-Type: application/json" \
  "https://your-domain.atlassian.net/rest/api/3/myself"
```

Or using curl's `-u` shorthand (which Base64-encodes automatically):
```bash
curl -u "you@example.com:YOUR_API_TOKEN" \
  "https://your-domain.atlassian.net/rest/api/3/issue/PROJ-1"
```

### Python (requests library)

```python
import requests

JIRA_BASE = "https://your-domain.atlassian.net/rest/api/3"
AUTH = ("you@example.com", "YOUR_API_TOKEN")
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

r = requests.get(f"{JIRA_BASE}/myself", auth=AUTH, headers=HEADERS)
r.raise_for_status()
print(r.json())
```

### Using the `jira` Python library

```bash
pip install jira
```

```python
from jira import JIRA

jira = JIRA(
    server="https://your-domain.atlassian.net",
    basic_auth=("you@example.com", "YOUR_API_TOKEN")
)

issue = jira.issue("PROJ-123")
print(issue.fields.summary)
```

### JavaScript (node-fetch / jira.js)

```bash
npm install @atlaskit/jira-rest-js-client
# or
npm install jira.js
```

```javascript
import { Version3Client } from 'jira.js';

const client = new Version3Client({
  host: 'https://your-domain.atlassian.net',
  authentication: {
    basic: {
      email: 'you@example.com',
      apiToken: 'YOUR_API_TOKEN',
    },
  },
});

const issue = await client.issues.getIssue({ issueIdOrKey: 'PROJ-123' });
```

---

## OAuth 2.0 (3LO — Three-Legged OAuth)

Best for: apps that act on behalf of a user (user grants consent). Requires Atlassian developer account and app registration.

### Setup

1. Create an OAuth 2.0 app at: `https://developer.atlassian.com/console/myapps/`
2. Add the "Jira API" product and select scopes
3. Set your redirect URI (callback URL)
4. Get your `CLIENT_ID` and `CLIENT_SECRET`

### Authorization flow

**Step 1: Redirect user to Atlassian authorization URL**
```
GET https://auth.atlassian.com/authorize
  ?audience=api.atlassian.com
  &client_id=YOUR_CLIENT_ID
  &scope=read%3Ajira-work%20write%3Ajira-work
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

Response:
```json
{
  "access_token": "eyJ...",
  "expires_in": 3600,
  "token_type": "Bearer",
  "refresh_token": "eyJ..."
}
```

**Step 3: Get accessible resources (to get cloud ID)**
```http
GET https://api.atlassian.com/oauth/token/accessible-resources
Authorization: Bearer ACCESS_TOKEN
```

Returns array of sites the user has access to, each with a `cloudId`.

**Step 4: Make API calls using cloud ID**
```
https://api.atlassian.com/ex/jira/{cloudId}/rest/api/3/issue/PROJ-123
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

### Common OAuth 2.0 Scopes

| Scope | Access |
|---|---|
| `read:jira-work` | Read issues, projects, comments, worklogs |
| `write:jira-work` | Create/update issues, comments, worklogs |
| `read:jira-user` | Read user profiles |
| `manage:jira-project` | Administer projects |
| `manage:jira-configuration` | Administer Jira instance |
| `offline_access` | Get a refresh token |

---

## Forge Apps

Forge apps run on Atlassian's infrastructure. Authentication is handled by the runtime — no token management required.

```javascript
// Forge: use the @forge/api requestJira helper
import { requestJira } from '@forge/api';

const response = await requestJira('/rest/api/3/issue/PROJ-123');
const issue = await response.json();
```

Scopes are declared in `manifest.yml`:
```yaml
permissions:
  scopes:
    - read:jira-work
    - write:jira-work
```

---

## Connect Apps (JWT)

Connect apps run on your own server and authenticate with JWT signed by your app's shared secret.

JWT claims required: `iss` (client key), `iat` (issued at), `exp` (expiry, max 180s), `qsh` (query string hash).

Atlassian provides Connect libraries (e.g., `atlassian-connect-express` for Node.js) that handle JWT signing automatically.

---

## Security Notes

- Never commit API tokens to source control; use environment variables or a secrets manager
- API tokens bypass 2FA — treat them as passwords
- Scope OAuth tokens to minimum required permissions
- Rotate tokens periodically; revoke them immediately if compromised
- Basic auth is fine for internal scripts; use OAuth 2.0 for anything user-facing
- Apps that instruct users to generate tokens and pass them to the app violate Atlassian's security policy
- CAPTCHA may activate after repeated authentication failures, blocking REST auth temporarily — watch for `X-Seraph-LoginReason: AUTHENTICATION_DENIED`
