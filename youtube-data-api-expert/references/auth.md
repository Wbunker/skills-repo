# Authentication — YouTube Data API v3

## Authentication Methods Overview

| Method | Use Case | Supports Write Ops | User Interaction |
|--------|----------|--------------------|-----------------|
| API Key | Public data only | No | No |
| OAuth 2.0 | User account data | Yes | Yes (first time) |
| Service Account | Server-to-server | Limited | No |

---

## API Key Authentication

Used for requests that only access public data. No user authorization required.

**Setup:**
1. Google Cloud Console → APIs & Services → Credentials → Create Credentials → API Key
2. Enable YouTube Data API v3 on the project
3. Restrict the key (recommended): HTTP referrers, IP addresses, or API restriction

**Usage:**
```
GET https://www.googleapis.com/youtube/v3/videos?id=VIDEO_ID&part=snippet&key=YOUR_API_KEY
```

Or with Python client library:
```python
from googleapiclient.discovery import build

youtube = build('youtube', 'v3', developerKey='YOUR_API_KEY')
response = youtube.videos().list(part='snippet', id='VIDEO_ID').execute()
```

**Limitations:**
- Cannot access private user data
- Cannot perform write operations
- Shares the same project quota (10,000 units/day)

---

## OAuth 2.0 — Installed App Flow (Desktop / CLI)

This is the standard pattern for scripts and desktop applications accessing a user's YouTube account. Uses `credentials.json` (downloaded from Google Cloud Console) and persists tokens to `token.json` or `token.pickle`.

### Setup Steps

1. Google Cloud Console → APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID
2. Application type: **Desktop app** (previously "Other")
3. Download the JSON file — this is `credentials.json` (also called `client_secret_*.json`)
4. Store `credentials.json` securely; do not commit to version control

### Python Pattern (google-auth-oauthlib)

**Install dependencies:**
```bash
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

**Standard token.json pattern:**
```python
import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
CLIENT_SECRETS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def get_authenticated_service():
    creds = None

    # Load existing token if present
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no valid credentials, run the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)  # Opens browser

        # Persist token for future runs
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())

    return build('youtube', 'v3', credentials=creds)

youtube = get_authenticated_service()
```

**Alternative: token.pickle pattern (older style):**
```python
import pickle

def get_authenticated_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as f:
            pickle.dump(creds, f)

    return build('youtube', 'v3', credentials=creds)
```

### What Happens on First Run

1. `run_local_server(port=0)` opens a browser window to `accounts.google.com/o/oauth2/v2/auth`
2. User signs in and grants requested scopes
3. Google redirects to `http://localhost:{random_port}/` with `?code=AUTH_CODE`
4. Library exchanges code for access token + refresh token
5. Tokens saved to `token.json` / `token.pickle`

**Subsequent runs:** Loads tokens from file; if expired, auto-refreshes using `refresh_token` (no user interaction needed).

### credentials.json Structure
```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "client_secret": "YOUR_CLIENT_SECRET",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "redirect_uris": ["http://localhost"]
  }
}
```

### token.json Structure (after authorization)
```json
{
  "token": "ya29.ACCESS_TOKEN",
  "refresh_token": "1//REFRESH_TOKEN",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
  "client_secret": "YOUR_CLIENT_SECRET",
  "scopes": ["https://www.googleapis.com/auth/youtube.force-ssl"],
  "expiry": "2024-01-01T00:00:00Z"
}
```

**Critical:** The `refresh_token` is only issued once (on first authorization). If lost, the user must re-authorize. Keep `token.json` / `token.pickle` secure and backed up.

---

## OAuth 2.0 — Server-Side Web App Flow

For web applications where the user authorizes through a browser redirect.

```python
from google_auth_oauthlib.flow import Flow

flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=SCOPES,
    redirect_uri='https://yourapp.com/oauth2callback'
)

# Generate authorization URL
authorization_url, state = flow.authorization_url(
    access_type='offline',       # Required to get refresh_token
    include_granted_scopes='true'
)
# Redirect user to authorization_url

# In callback handler:
flow.fetch_token(authorization_response=request.url)
credentials = flow.credentials
# Store credentials.token and credentials.refresh_token securely
```

**Key parameters:**
- `access_type='offline'` — required to receive a refresh token
- `include_granted_scopes='true'` — enables incremental authorization

---

## OAuth 2.0 Scopes

| Scope | URI | Capabilities |
|-------|-----|--------------|
| `youtube.readonly` | `.../auth/youtube.readonly` | Read any YouTube data accessible to the user |
| `youtube` | `.../auth/youtube` | Full account management (read + write) |
| `youtube.upload` | `.../auth/youtube.upload` | Upload videos, manage uploads |
| `youtube.force-ssl` | `.../auth/youtube.force-ssl` | Edit/delete videos, comments, captions; required for sensitive writes |
| `youtubepartner` | `.../auth/youtubepartner` | YouTube partner / content owner operations |

Full URI prefix: `https://www.googleapis.com/auth/`

**Which operations require which scope:**

| Operation | Minimum Scope |
|-----------|---------------|
| videos.list (public) | API key only |
| videos.list (private/mine) | youtube.readonly |
| videos.insert | youtube.upload |
| videos.update, videos.delete | youtube or youtube.force-ssl |
| videos.rate | youtube or youtube.force-ssl |
| playlists.insert/update/delete | youtube or youtube.force-ssl |
| subscriptions.insert/delete | youtube or youtube.force-ssl |
| comments.insert/update/delete | youtube.force-ssl |
| channels.update | youtube or youtube.force-ssl |
| liveBroadcasts/liveStreams | youtube |

---

## Service Accounts

Service accounts have **very limited** support for the YouTube Data API. Unlike most Google APIs, YouTube accounts are personal — a service account cannot "be" a YouTube channel.

**What service accounts CAN do:**
- Access YouTube Analytics API on behalf of a content owner (using `onBehalfOfContentOwner` parameter with YouTube partner accounts)
- Used in G Suite / Workspace contexts with domain-wide delegation (rare)

**What service accounts CANNOT do:**
- Act as a regular YouTube user account
- Upload videos to a personal channel
- Access a user's subscriptions or playlists without explicit delegation

For most YouTube Data API use cases, OAuth 2.0 is the correct approach.

---

## Token Refresh and Expiry

- Access tokens expire after **1 hour**
- Refresh tokens do not expire unless:
  - User revokes access in Google Account settings
  - App has been inactive for 6 months
  - Project exceeds refresh token limit (creates new token, invalidating oldest)
  - User changes password (in some cases)

**Manual token refresh:**
```python
from google.auth.transport.requests import Request

if creds.expired and creds.refresh_token:
    creds.refresh(Request())
```

**Token revocation:**
```python
import requests
requests.post('https://oauth2.googleapis.com/revoke',
              params={'token': creds.token})
```

---

## Authorization Flow (Manual / Raw HTTP)

For reference — the library handles this automatically:

1. Redirect user to:
   ```
   https://accounts.google.com/o/oauth2/v2/auth
     ?client_id=CLIENT_ID
     &redirect_uri=REDIRECT_URI
     &response_type=code
     &scope=SCOPE
     &access_type=offline
     &state=RANDOM_STATE
   ```

2. Exchange authorization code for tokens:
   ```
   POST https://oauth2.googleapis.com/token
   Body: code=AUTH_CODE&client_id=...&client_secret=...
         &redirect_uri=...&grant_type=authorization_code
   ```

3. Response includes `access_token`, `refresh_token`, `expires_in`, `scope`

4. Refresh when expired:
   ```
   POST https://oauth2.googleapis.com/token
   Body: grant_type=refresh_token&refresh_token=...
         &client_id=...&client_secret=...
   ```
