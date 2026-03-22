# Service Account + Domain-Wide Delegation

For server-to-server access without user interaction. The service account can
impersonate any user in a Google Workspace domain. **Requires Google Workspace
(not available for personal @gmail.com accounts).**

## Table of Contents
1. [Setup](#setup)
2. [Python Implementation](#python-implementation)
3. [Multi-Service Usage](#multi-service-usage)
4. [Key Differences from OAuth User Flow](#key-differences)

---

## Setup

### 1. Create a Service Account

1. Go to **Google Cloud Console → IAM & Admin → Service Accounts**
2. Click **Create Service Account**
3. Name it (e.g., `workspace-automation`)
4. Click **Create and Continue** (no IAM roles needed for Workspace delegation)
5. Click **Done**

### 2. Create and Download JSON Key

1. Click the service account → **Keys** tab
2. **Add Key → Create new key → JSON**
3. Save the downloaded file as `service-account.json`
4. **Never commit this file to version control**

### 3. Note the Client ID

On the service account details page, note the **Unique ID** (numeric string) —
this is the Client ID used for delegation setup.

### 4. Enable Domain-Wide Delegation in Google Workspace Admin

1. Sign in to [admin.google.com](https://admin.google.com) as a super admin
2. Go to **Security → Access and data controls → API controls**
3. Click **Manage Domain Wide Delegation**
4. Click **Add new**
5. Enter the service account's **Client ID** (numeric unique ID)
6. Enter the OAuth scopes (comma-separated) the service account is allowed to use:
   ```
   https://www.googleapis.com/auth/gmail.modify,
   https://www.googleapis.com/auth/spreadsheets,
   https://www.googleapis.com/auth/documents,
   https://www.googleapis.com/auth/drive
   ```
7. Click **Authorize**

---

## Python Implementation

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = 'service-account.json'

def get_service(service_name: str, version: str,
                scopes: list[str], impersonate_email: str):
    """
    Build a Workspace API service using service account delegation.

    Args:
        service_name: API name ('gmail', 'sheets', 'docs', 'slides', 'drive')
        version: API version ('v1', 'v4', etc.)
        scopes: OAuth scopes the service account has been granted
        impersonate_email: Email of the Workspace user to act as

    Returns:
        Authenticated API service resource
    """
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=scopes
    )
    delegated = credentials.with_subject(impersonate_email)
    return build(service_name, version, credentials=delegated)


# Examples
SCOPES_GMAIL  = ['https://www.googleapis.com/auth/gmail.modify']
SCOPES_SHEETS = ['https://www.googleapis.com/auth/spreadsheets']
SCOPES_DRIVE  = ['https://www.googleapis.com/auth/drive']

user = 'alice@yourcompany.com'

gmail_service  = get_service('gmail',  'v1', SCOPES_GMAIL,  user)
sheets_service = get_service('sheets', 'v4', SCOPES_SHEETS, user)
drive_service  = get_service('drive',  'v3', SCOPES_DRIVE,  user)
```

### From service account dict (e.g., from Secret Manager)

```python
import json

service_account_info = json.loads(os.environ['SERVICE_ACCOUNT_JSON'])

credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=SCOPES_GMAIL
)
delegated = credentials.with_subject('alice@yourcompany.com')
gmail_service = build('gmail', 'v1', credentials=delegated)
```

---

## Multi-Service Usage

To use multiple services as the same user, create separate delegated credentials
per service (scopes must match what was granted in the Admin console):

```python
def get_all_services(user_email: str) -> dict:
    """Get all Workspace services delegated to a user."""
    base = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=[
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/documents',
            'https://www.googleapis.com/auth/presentations',
            'https://www.googleapis.com/auth/drive',
        ]
    )
    delegated = base.with_subject(user_email)
    return {
        'gmail':  build('gmail',  'v1', credentials=delegated),
        'sheets': build('sheets', 'v4', credentials=delegated),
        'docs':   build('docs',   'v1', credentials=delegated),
        'slides': build('slides', 'v1', credentials=delegated),
        'drive':  build('drive',  'v3', credentials=delegated),
    }

services = get_all_services('alice@yourcompany.com')
profile = services['gmail'].users().getProfile(userId='me').execute()
```

**Note:** For Gmail, use the impersonated user's email as `userId` OR `'me'` — both work with delegation.

---

## Key Differences from OAuth User Flow

| Aspect | OAuth User Flow | Service Account Delegation |
|--------|----------------|---------------------------|
| User interaction | Browser consent required | None — fully automated |
| Token caching | Required (`token.json`) | Not needed (credentials auto-refresh) |
| Account type | Any Google account | Google Workspace only |
| `userId` in Gmail | Always `'me'` | `'me'` or the impersonated email |
| Setup complexity | Low | Requires Workspace Admin |
| Suitable for | Interactive apps, scripts | Automated servers, batch processing |
| Multi-user access | One user at a time | Can impersonate any domain user |
| Key security | `credentials.json` + `token.json` | `service-account.json` — treat like a password |
