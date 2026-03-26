# YouTube API Authentication

## Overview

The YouTube Data API supports three credential types:

| Type | Use Case | Accesses Private Data? |
|------|----------|----------------------|
| API Key | Public data only | No |
| OAuth 2.0 | User's own channel | Yes |
| Service Account | Server-to-server | Rarely (needs delegation) |

**Most YouTube tasks require OAuth 2.0** because the API acts on behalf of a YouTube user account.

---

## Step 1: Google Cloud Console Setup

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (or select existing)
3. Enable the YouTube Data API v3:
   - APIs & Services → Library → search "YouTube Data API v3" → Enable
4. If using Analytics: also enable "YouTube Analytics API"
5. Create credentials:
   - APIs & Services → Credentials → Create Credentials

---

## OAuth 2.0 — Desktop/Script Flow (Most Common)

This is the pattern for scripts running on your own machine accessing your own YouTube channel.

### Create OAuth Client ID

1. Create Credentials → OAuth client ID
2. Application type: **Desktop app**
3. Download JSON → save as `credentials.json` in your project
4. Add your Google account email as a **Test User** (OAuth consent screen → Test users) while app is in testing mode

### credentials.json Structure

```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["http://localhost"]
  }
}
```

### Python Auth Flow

```python
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

# Choose scopes for your use case (see Scopes section below)
SCOPES = ["https://www.googleapis.com/auth/youtube"]

def get_youtube_client():
    creds = None

    # Load cached token if it exists
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # Refresh or re-authenticate if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Opens browser for user authorization (first run only)
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Cache token for future runs
        with open("token.json", "w") as f:
            f.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)
```

**First run**: opens browser → user signs in → grants permissions → `token.json` created.
**Subsequent runs**: uses cached `token.json`, auto-refreshes if expired.

### Required packages

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

---

## OAuth Scopes

Request only the scopes you need — Google reviews scope usage for production apps.

| Scope | Access |
|-------|--------|
| `https://www.googleapis.com/auth/youtube.readonly` | Read-only access to your YouTube account |
| `https://www.googleapis.com/auth/youtube` | Manage your YouTube account (read + write) |
| `https://www.googleapis.com/auth/youtube.upload` | Upload videos only (more limited than youtube) |
| `https://www.googleapis.com/auth/youtube.force-ssl` | Manage your account (requires HTTPS) |
| `https://www.googleapis.com/auth/youtubepartner` | View and manage YouTube assets (CMS partners) |
| `https://www.googleapis.com/auth/yt-analytics.readonly` | View YouTube Analytics reports |
| `https://www.googleapis.com/auth/yt-analytics-monetary.readonly` | View monetary YouTube Analytics reports |

**Typical scope combinations:**
- Read-only scripts: `youtube.readonly`
- Upload + manage: `youtube` or `["youtube", "youtube.upload"]`
- Analytics: `["youtube.readonly", "yt-analytics.readonly"]`

---

## API Key — Public Data

Use an API key for unauthenticated requests to public data (no user login required).

### Create API Key

1. APIs & Services → Credentials → Create Credentials → API key
2. (Recommended) Restrict key: API restrictions → YouTube Data API v3

### Python Usage

```python
from googleapiclient.discovery import build

youtube = build("youtube", "v3", developerKey="YOUR_API_KEY")

# Works for public data
response = youtube.videos().list(
    part="snippet,statistics",
    id="dQw4w9WgXcQ"
).execute()
```

**Limitations**: Cannot access private videos, user-specific data, or perform writes.

---

## Service Accounts

Service accounts are generally **not suitable** for YouTube API unless you have a YouTube Content Management System (CMS) account with domain-wide delegation. The YouTube Data API requires user OAuth 2.0 for most operations — service accounts cannot "act as" a YouTube user the way they can in Google Drive or Gmail.

**Exception**: YouTube Analytics API for content owners (CMS partners) can use service accounts if the content owner grants access.

---

## Web Application Flow (for deployed apps)

For web apps where users authorize your app to access their YouTube:

```python
from google_auth_oauthlib.flow import Flow

flow = Flow.from_client_secrets_file(
    "credentials.json",
    scopes=SCOPES,
    redirect_uri="https://yourdomain.com/oauth2callback"
)

# Generate authorization URL to redirect user to
auth_url, state = flow.authorization_url(
    access_type="offline",   # get refresh_token
    include_granted_scopes="true"
)

# After user authorizes, exchange code for credentials
flow.fetch_token(code=request.args.get("code"))
credentials = flow.credentials
```

---

## Token Management

```python
# Check if token needs refresh
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

# Access token (short-lived, ~1 hour)
print(creds.token)

# Refresh token (long-lived, use to get new access tokens)
print(creds.refresh_token)

# Expiry
print(creds.expiry)

# Revoke access
import google.auth.transport.requests
requests = google.auth.transport.requests.Request()
google.oauth2.credentials.Credentials.revoke(requests)
```

---

## OAuth Consent Screen — Testing vs Production

While your app is in **testing** mode:
- Only test users you've explicitly added can authorize
- Token expiry: 7 days (refresh tokens expire after 7 days in testing)
- No Google review required

For **production** (any Google account can authorize):
- Submit app for Google verification/review
- Required if using sensitive scopes (youtube, youtube.upload, etc.)
- Provide privacy policy URL, app homepage, and justification for each scope

---

## Common Auth Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `redirect_uri_mismatch` | Redirect URI not in console | Add `http://localhost` to authorized redirect URIs |
| `access_denied` | User denied or email not in test users | Add email to OAuth consent screen test users |
| `invalid_grant` | Refresh token expired/revoked | Delete `token.json`, re-authenticate |
| `Token has been expired or revoked` | Testing mode token (7-day limit) | Re-auth or move to production |
| `insufficient_authentication_scopes` | Wrong scopes | Add required scope to SCOPES list, delete token.json, re-auth |
