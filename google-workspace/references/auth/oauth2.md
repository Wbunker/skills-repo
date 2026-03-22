# Google Workspace OAuth 2.0 Authentication

Applies to all Workspace APIs: Gmail, Sheets, Docs, Slides, Drive, Calendar.

## Table of Contents
1. [Prerequisites: Google Cloud Setup](#prerequisites)
2. [Desktop / CLI Flow (run_local_server)](#desktop-cli-flow)
3. [Web Server Flow](#web-server-flow)
4. [Headless / SSH Flow](#headless-flow)
5. [Token Management](#token-management)
6. [Multi-Service Auth (Combined Scopes)](#multi-service-auth)
7. [Scope Reference](#scope-reference)

---

## Prerequisites: Google Cloud Setup

1. Create project at [console.cloud.google.com](https://console.cloud.google.com)
2. Enable the APIs you need: **APIs & Services → Enable APIs**
   - Search and enable: Gmail API, Google Sheets API, Google Docs API, Google Slides API, Google Drive API
3. Configure OAuth consent screen: **APIs & Services → OAuth consent screen**
   - User Type: External (any Google account) or Internal (Google Workspace org only)
   - Add required scopes
4. Create credentials: **APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID**
   - For scripts/CLI: **Desktop app** (allows all localhost redirect URIs automatically)
   - For web apps: **Web application** (requires explicit redirect URIs)
5. Download as `credentials.json`

---

## Desktop / CLI Flow (run_local_server)

Standard flow for scripts and CLI tools. Opens browser for user consent on first run.

```python
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_credentials(
    scopes=SCOPES,
    credentials_file='credentials.json',
    token_file='token.json'
) -> Credentials:
    """
    Get credentials via OAuth browser flow. Caches token for subsequent runs.
    First run opens browser; subsequent runs use cached token.json.
    """
    creds = None

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(
                    f"'{credentials_file}' not found. "
                    "Download from Google Cloud Console > APIs & Services > Credentials."
                )
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
            creds = flow.run_local_server(
                port=0,              # Pick any free port
                access_type='offline',
                prompt='consent',    # Always get refresh_token
            )
        with open(token_file, 'w') as f:
            f.write(creds.to_json())

    return creds

# Build any service from the same credentials
creds = get_credentials(scopes=[
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.readonly',
])
sheets = build('sheets', 'v4', credentials=creds)
drive  = build('drive',  'v3', credentials=creds)
```

### Getting refresh_token reliably

```python
# REQUIRED for long-running scripts / servers
creds = flow.run_local_server(
    port=0,
    access_type='offline',   # Tell Google to issue a refresh_token
    prompt='consent',        # Force consent screen on re-auth (otherwise no refresh_token)
)

assert creds.refresh_token, "No refresh_token! Check access_type='offline' and prompt='consent'."
```

Without `prompt='consent'`, Google only issues a refresh_token on the first authorization. On subsequent runs without it, the token expires after 1 hour with no way to refresh.

### run_local_server() key parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| `port` | `8080` | `0` = pick any free port |
| `access_type` | `'online'` | `'offline'` to get refresh_token |
| `prompt` | (not set) | `'consent'` forces consent screen every time |
| `open_browser` | `True` | Set `False` to print URL instead of opening browser |
| `timeout_seconds` | `None` | Seconds before giving up |
| `success_message` | default | HTML shown in browser after success |

---

## Web Server Flow

For web apps where users authenticate via browser redirect (Flask, FastAPI, etc.).

```python
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Remove in production (HTTPS only)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
REDIRECT_URI = 'https://yourapp.com/oauth/callback'

def create_auth_url():
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return auth_url, state, flow

def exchange_code(flow, authorization_response: str) -> Credentials:
    """Call with the full redirect URL received after consent."""
    flow.fetch_token(authorization_response=authorization_response)
    return flow.credentials
```

**Flask example:**
```python
from flask import Flask, redirect, request, session
app = Flask(__name__)
app.secret_key = 'your-secret-key'

@app.route('/login')
def login():
    auth_url, state, flow = create_auth_url()
    session['flow_state'] = state
    return redirect(auth_url)

@app.route('/oauth/callback')
def callback():
    flow = Flow.from_client_secrets_file('credentials.json', scopes=SCOPES, redirect_uri=REDIRECT_URI)
    creds = exchange_code(flow, request.url)
    # Store: creds.to_json() in database/session
    return 'Authenticated!'
```

---

## Headless / SSH Flow

For servers or SSH sessions without a browser.

```python
from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)

# Prints URL; waits for you to paste the auth code from the browser
creds = flow.run_console()
```

Alternatively, generate the URL on your local machine, authenticate there, copy `token.json` to the server.

---

## Token Management

### Load from file (standard)

```python
from google.oauth2.credentials import Credentials

creds = Credentials.from_authorized_user_file('token.json', SCOPES)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
```

### Load from environment variable (deployment)

```python
import json, os
from google.oauth2.credentials import Credentials

def creds_from_env(env_var='GOOGLE_TOKEN_JSON', scopes=SCOPES):
    token_json = os.environ.get(env_var)
    if not token_json:
        raise EnvironmentError(f"Env var '{env_var}' not set")
    info = json.loads(token_json)
    creds = Credentials.from_authorized_user_info(info, scopes)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds
```

Store `token.json` contents as `GOOGLE_TOKEN_JSON` in your environment.

### Token refresh

Access tokens expire after 1 hour. The library refreshes automatically if you call:

```python
from google.auth.transport.requests import Request

if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    # Save updated token
    with open('token.json', 'w') as f:
        f.write(creds.to_json())
```

### Revoke / logout

```python
import requests

requests.post(
    'https://oauth2.googleapis.com/revoke',
    params={'token': creds.token},
    headers={'content-type': 'application/x-www-form-urlencoded'}
)
import os
os.remove('token.json')
```

---

## Multi-Service Auth (Combined Scopes)

You can authenticate once with all required scopes and build multiple services from the same credentials:

```python
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/drive',
]

creds = get_credentials(scopes=SCOPES)
gmail  = build('gmail',  'v1', credentials=creds)
sheets = build('sheets', 'v4', credentials=creds)
docs   = build('docs',   'v1', credentials=creds)
slides = build('slides', 'v1', credentials=creds)
drive  = build('drive',  'v3', credentials=creds)
```

**Scope changes invalidate cached tokens.** Delete `token.json` and re-authenticate whenever you add or remove scopes.

---

## Scope Reference

Use the minimum scopes required. Narrower scopes require less justification in the OAuth consent screen review.

### Gmail

| Scope | Access |
|-------|--------|
| `gmail.readonly` | Read all resources |
| `gmail.send` | Send only |
| `gmail.compose` | Create/read/update drafts; send |
| `gmail.modify` | All except permanent delete |
| `gmail.labels` | Label CRUD only |
| `gmail.metadata` | Headers/metadata only, no body |
| `gmail.settings.basic` | Filters, send-as, vacation, IMAP/POP |
| `gmail.settings.sharing` | Forwarding, delegation |
| `mail.google.com` | Full access |

### Sheets

| Scope | Access |
|-------|--------|
| `spreadsheets.readonly` | Read spreadsheets and cell data |
| `spreadsheets` | Full read/write access |
| `drive.readonly` | Read all Drive files (broader than needed for Sheets) |

### Docs

| Scope | Access |
|-------|--------|
| `documents.readonly` | Read documents |
| `documents` | Full read/write access |

### Slides

| Scope | Access |
|-------|--------|
| `presentations.readonly` | Read presentations |
| `presentations` | Full read/write access |

### Drive

| Scope | Access |
|-------|--------|
| `drive.readonly` | Read all files |
| `drive.file` | Only files created/opened by the app |
| `drive.appdata` | App-specific hidden folder only |
| `drive.metadata` | View/manage metadata, no file content |
| `drive.metadata.readonly` | View metadata only |
| `drive` | Full Drive access |

All scope URIs are prefixed with `https://www.googleapis.com/auth/`.
