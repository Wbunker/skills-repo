# Gmail Authentication & Scopes

> For OAuth2 flows (desktop, web server, headless, token management), see
> [references/auth/oauth2.md](../auth/oauth2.md).
>
> For service account domain-wide delegation, see
> [references/auth/service-account-delegation.md](../auth/service-account-delegation.md).

## Gmail Quick Auth

```python
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service(token_file='token.json', credentials_file='credentials.json'):
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0, access_type='offline', prompt='consent')
        with open(token_file, 'w') as f:
            f.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

service = get_gmail_service()
```

## Gmail Scope Reference

| Scope | Access |
|-------|--------|
| `gmail.readonly` | Read all resources including settings |
| `gmail.send` | Send only (no read) |
| `gmail.compose` | Create, read, update drafts; send |
| `gmail.modify` | All except permanently delete |
| `gmail.labels` | Create/modify/delete labels only |
| `gmail.metadata` | Headers and metadata only, no body |
| `gmail.settings.basic` | Manage basic settings (filters, send-as, vacation, IMAP/POP) |
| `gmail.settings.sharing` | Manage sensitive settings (delegation, forwarding) |
| `mail.google.com` | Full access (legacy IMAP scope) |

All scope URIs are prefixed with `https://www.googleapis.com/auth/`.

**Scope selection guidance:**
- Monitoring/analytics → `gmail.readonly` or `gmail.metadata`
- Automated replies → `gmail.send` or `gmail.compose`
- Inbox management bot → `gmail.modify`
- Email archiving tool → `gmail.readonly`
- Filter management → `gmail.settings.basic`
- Admin delegation → `gmail.settings.sharing`

**Note:** `gmail.metadata` scope **cannot** use the `q` search parameter in `messages.list()`. If you need to search, use `gmail.readonly` or higher.

Changing scopes after initial auth requires re-authorization (delete `token.json` and re-run).
