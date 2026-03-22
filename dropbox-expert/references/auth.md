# Dropbox Authentication

## Table of Contents
1. [App Registration](#app-registration)
2. [Token Types](#token-types)
3. [OAuth2 Authorization Code Flow](#oauth2-authorization-code-flow)
4. [PKCE Flow (Desktop/Mobile/CLI)](#pkce-flow)
5. [Short-Lived vs Long-Lived Tokens](#short-lived-vs-long-lived-tokens)
6. [Token Storage & Refresh](#token-storage--refresh)
7. [Team Auth](#team-auth)
8. [Scopes Reference](#scopes-reference)

---

## App Registration

1. Go to [dropbox.com/developers/apps](https://www.dropbox.com/developers/apps)
2. Click **Create app**
3. Choose API type: **Scoped access** (required for new apps)
4. Choose access: **App folder** (sandboxed to one folder) or **Full Dropbox**
5. Name your app
6. In **Permissions** tab: enable the scopes your app needs
7. In **Settings** tab: note your **App key** and **App secret**
8. Add **Redirect URIs** for OAuth (e.g. `http://localhost:8080` for CLI apps)

**App Folder vs Full Dropbox**: Cannot be changed after creation. App Folder is easier to get approved; Full Dropbox requires justification and Dropbox approval for production use.

**Development limit**: Max 500 linked users. After 50 users, must apply for production status within 2 weeks.

---

## Token Types

| Type | Header | Use Case |
|------|--------|---------|
| User token | `Authorization: Bearer <USER_TOKEN>` | Act on a specific user's files |
| Team token | `Authorization: Bearer <TEAM_TOKEN>` | Team-level operations (members, groups) |
| App token | `Authorization: Basic base64(key:secret)` | App-level calls without user context |
| Select-User | Team token + `Dropbox-API-Select-User: <member_id>` | Act on behalf of a team member |
| Select-Admin | Team token + `Dropbox-API-Select-Admin: <admin_id>` | Act as team admin |

---

## OAuth2 Authorization Code Flow

### Step 1: Build the authorization URL

```python
import dropbox
from dropbox import DropboxOAuth2Flow

APP_KEY = 'your_app_key'
APP_SECRET = 'your_app_secret'
REDIRECT_URI = 'http://localhost:8080/callback'

# Session state token (use a random string in production)
auth_flow = DropboxOAuth2Flow(
    consumer_key=APP_KEY,
    redirect_uri=REDIRECT_URI,
    session={'key': 'state_token'},
    csrf_token_session_key='key',
    consumer_secret=APP_SECRET,
    token_access_type='offline',  # Request refresh token
)

authorize_url = auth_flow.start()
print(f"Visit: {authorize_url}")
```

### Step 2: Exchange code for tokens

```python
# After user authorizes, Dropbox redirects to REDIRECT_URI with ?code=...&state=...
oauth_result = auth_flow.finish({
    'code': 'AUTH_CODE_FROM_REDIRECT',
    'state': 'state_token'
})

access_token = oauth_result.access_token
refresh_token = oauth_result.refresh_token   # Only with token_access_type='offline'
account_id = oauth_result.account_id
user_id = oauth_result.user_id

# Build client
dbx = dropbox.Dropbox(oauth2_access_token=access_token)
```

### Simple CLI auth (no web server needed)

```python
# DropboxOAuth2FlowNoRedirect for scripts/CLI — user copies code from browser
from dropbox import DropboxOAuth2FlowNoRedirect

auth_flow = DropboxOAuth2FlowNoRedirect(
    consumer_key=APP_KEY,
    consumer_secret=APP_SECRET,
    token_access_type='offline',
)

authorize_url = auth_flow.start()
print(f"1. Visit: {authorize_url}")
print("2. Click 'Allow'")
auth_code = input("3. Paste the authorization code: ").strip()

oauth_result = auth_flow.finish(auth_code)
access_token = oauth_result.access_token
refresh_token = oauth_result.refresh_token
```

---

## PKCE Flow

For apps that cannot securely store a client secret (mobile, desktop, SPA). Uses a `code_verifier` + `code_challenge` instead of the client secret.

```python
import secrets, hashlib, base64

# Generate PKCE verifier and challenge
code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=').decode()
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode()).digest()
).rstrip(b'=').decode()

# Authorization URL (no client_secret needed)
from urllib.parse import urlencode
params = {
    'client_id': APP_KEY,
    'response_type': 'code',
    'redirect_uri': REDIRECT_URI,
    'code_challenge': code_challenge,
    'code_challenge_method': 'S256',
    'token_access_type': 'offline',
}
auth_url = f"https://www.dropbox.com/oauth2/authorize?{urlencode(params)}"

# Token exchange (use code_verifier instead of client_secret)
import requests
resp = requests.post('https://api.dropboxapi.com/oauth2/token', data={
    'code': auth_code,
    'grant_type': 'authorization_code',
    'redirect_uri': REDIRECT_URI,
    'code_verifier': code_verifier,
    'client_id': APP_KEY,
})
tokens = resp.json()
access_token = tokens['access_token']
refresh_token = tokens.get('refresh_token')
```

---

## Short-Lived vs Long-Lived Tokens

| Token Type | Lifetime | How to Get |
|-----------|---------|-----------|
| Short-lived access token | ~4 hours | OAuth flow with `token_access_type='offline'` |
| Long-lived access token (legacy) | Never expires | **Deprecated** — Dropbox App Console still generates these for testing |
| Refresh token | Indefinite (until revoked) | OAuth flow with `token_access_type='offline'` |

**For production**: Always use short-lived tokens + refresh tokens. Long-lived tokens are a security risk.

**For development/testing**: You can generate a legacy long-lived token from the App Console → **Settings** → **Generated access token** (shows only if no refresh token flow is configured).

---

## Token Storage & Refresh

```python
import json, os
import dropbox

TOKEN_FILE = '.dropbox_token.json'

def save_tokens(access_token: str, refresh_token: str = None):
    data = {'access_token': access_token}
    if refresh_token:
        data['refresh_token'] = refresh_token
    with open(TOKEN_FILE, 'w') as f:
        json.dump(data, f)

def load_tokens() -> dict:
    if not os.path.exists(TOKEN_FILE):
        return {}
    with open(TOKEN_FILE) as f:
        return json.load(f)

def get_client(app_key: str = None, app_secret: str = None) -> dropbox.Dropbox:
    """
    Get authenticated Dropbox client.
    Uses refresh token if available; falls back to stored access token.
    """
    tokens = load_tokens()

    if tokens.get('refresh_token') and app_key and app_secret:
        # SDK handles refresh automatically when given oauth2_refresh_token
        return dropbox.Dropbox(
            oauth2_refresh_token=tokens['refresh_token'],
            app_key=app_key,
            app_secret=app_secret,
        )
    elif tokens.get('access_token'):
        return dropbox.Dropbox(tokens['access_token'])
    else:
        raise ValueError("No tokens found. Run auth setup first.")


# Manual token refresh (if not using SDK auto-refresh)
def refresh_access_token(refresh_token: str, app_key: str, app_secret: str) -> str:
    import requests
    resp = requests.post('https://api.dropboxapi.com/oauth2/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': app_key,
        'client_secret': app_secret,
    })
    resp.raise_for_status()
    return resp.json()['access_token']
```

**SDK auto-refresh**: When constructing `Dropbox` with `oauth2_refresh_token` + `app_key` + `app_secret`, the SDK automatically refreshes the access token when it expires.

```python
# Preferred: SDK manages refresh automatically
dbx = dropbox.Dropbox(
    oauth2_refresh_token=refresh_token,
    app_key=APP_KEY,
    app_secret=APP_SECRET,
)
```

---

## Team Auth

```python
# Team client: access team-level APIs
team_dbx = dropbox.DropboxTeam(oauth2_access_token=TEAM_TOKEN)

# List team members
members = team_dbx.team_members_list()
for member in members.members:
    print(f"{member.profile.email}: {member.profile.team_member_id}")

# Act as a specific team member
user_dbx = team_dbx.as_user(member_id='dbmid:...')
files = user_dbx.files_list_folder('').entries  # Access member's files

# Act as admin
admin_dbx = team_dbx.as_admin(admin_id='dbmid:...')
```

---

## Scopes Reference

Requested at app creation (Permissions tab) and during OAuth. Cannot be broader than what the app was approved for.

| Scope | Access |
|-------|--------|
| `account_info.read` | Read account info |
| `files.metadata.read` | Read file/folder metadata (not content) |
| `files.metadata.write` | Write file/folder metadata |
| `files.content.read` | Read file content (download) |
| `files.content.write` | Upload, edit, delete files |
| `sharing.read` | Read shared links and folder memberships |
| `sharing.write` | Create/modify shared links and folder memberships |
| `file_requests.read` | Read file requests |
| `file_requests.write` | Create/modify file requests |
| `contacts.read` | Read contacts |
| `team_info.read` | Read team info |
| `team_data.member` | Read team member info |
| `team_data.governance.read` | Read team governance policies |
| `team_data.governance.write` | Write team governance policies |
| `events.read` | Read team event log (Business only) |

**Minimum scopes for common tasks:**
- Read-only file access: `files.metadata.read` + `files.content.read`
- Upload/manage files: `files.metadata.write` + `files.content.write`
- Create shared links: `sharing.write`
- Full file management: all four `files.*` scopes + `sharing.write`
