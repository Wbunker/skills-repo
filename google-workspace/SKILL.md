---
name: google-workspace
description: >
  Expert-level Google Workspace API integration using Python. Use when working
  programmatically with Gmail (email/labels/threads/drafts), Google Sheets
  (reading/writing cells, formatting, charts), Google Docs (creating/editing
  documents, inserting content), Google Slides (presentations, shapes, layouts),
  or Google Drive (file management, sharing, permissions). Covers
  google-api-python-client v2.x, OAuth 2.0 (desktop, web server, headless),
  service account domain-wide delegation, and all major API resource types.
  Triggers on: Gmail API, Sheets API, Docs API, Slides API, Drive API,
  google-api-python-client, Google Workspace Python, send email Python,
  read Gmail Python, gmail oauth, gmail automation, read/write spreadsheet Python,
  sheets automation, google docs Python, create presentation Python, google drive
  Python, workspace automation, google apps script alternative, email bot.
---

# Google Workspace Expert

Full API reference for Gmail, Sheets, Docs, Slides, and Drive using
`google-api-python-client` v2.x (REST/JSON over HTTPS).

## Installation

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Quick Start

```python
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os

# Adjust scopes for the services you need
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/drive',
]

def get_credentials(scopes=SCOPES, token_file='token.json', creds_file='credentials.json'):
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, scopes)
            creds = flow.run_local_server(port=0)
        with open(token_file, 'w') as f:
            f.write(creds.to_json())
    return creds

creds = get_credentials()
gmail   = build('gmail',         'v1', credentials=creds)
sheets  = build('sheets',        'v4', credentials=creds)
docs    = build('docs',          'v1', credentials=creds)
slides  = build('slides',        'v1', credentials=creds)
drive   = build('drive',         'v3', credentials=creds)
```

## Service Discovery Names

| Product | Service name | Version |
|---------|-------------|---------|
| Gmail | `gmail` | `v1` |
| Sheets | `sheets` | `v4` |
| Docs | `docs` | `v1` |
| Slides | `slides` | `v1` |
| Drive | `drive` | `v3` |
| Calendar | `calendar` | `v3` |

## Key Concepts (All Services)

- **`execute()`**: Required to fire the HTTP call — building a request object does NOT send it
- **`credentials.json`**: OAuth client credentials downloaded from Google Cloud Console
- **`token.json`**: Cached OAuth tokens (access + refresh) — add to `.gitignore`
- **Scopes**: Request only the scopes you need; changing scopes invalidates existing tokens
- **`userId='me'`** (Gmail): Always use `'me'` for the authenticated user
- **Workspace vs Consumer**: Service account delegation requires Google Workspace, not @gmail.com
- **Quota units**: Each API call consumes quota — use batch operations and caching

## Reference Files

Load these based on the task at hand:

### Authentication
| File | When to Read |
|------|-------------|
| [references/auth/oauth2.md](references/auth/oauth2.md) | OAuth flows, credentials setup, token refresh, web server flow, headless auth |
| [references/auth/service-account-delegation.md](references/auth/service-account-delegation.md) | Server-to-server access, impersonating Workspace users |

### Gmail
| File | When to Read |
|------|-------------|
| [references/gmail/authentication.md](references/gmail/authentication.md) | Gmail-specific scopes |
| [references/gmail/api-reference.md](references/gmail/api-reference.md) | Full messages/threads/labels/drafts/history/settings method reference |
| [references/gmail/message-format.md](references/gmail/message-format.md) | MIME parsing, body extraction, attachment handling, creating messages |
| [references/gmail/search-operators.md](references/gmail/search-operators.md) | Gmail query syntax for `q` parameter |
| [references/gmail/push-notifications.md](references/gmail/push-notifications.md) | Pub/Sub watch, historyId incremental sync |
| [references/gmail/error-handling.md](references/gmail/error-handling.md) | HttpError codes, quota limits, retry/backoff |
| [references/gmail/settings-api.md](references/gmail/settings-api.md) | Filters, forwarding, send-as, vacation, IMAP/POP, delegates |

### Sheets
| File | When to Read |
|------|-------------|
| [references/sheets/sheets-api.md](references/sheets/sheets-api.md) | Full Sheets API: values read/write, formatting, named ranges, charts |

### Docs
| File | When to Read |
|------|-------------|
| [references/docs/docs-api.md](references/docs/docs-api.md) | Full Docs API: batchUpdate requests, document structure, reading content |

### Slides
| File | When to Read |
|------|-------------|
| [references/slides/slides-api.md](references/slides/slides-api.md) | Full Slides API: presentations, slides, shapes, text, layouts |

### Drive
| File | When to Read |
|------|-------------|
| [references/drive/drive-api.md](references/drive/drive-api.md) | File management, permissions, sharing, upload, export |

## Scripts

| Script | Purpose |
|--------|---------|
| [scripts/auth.py](scripts/auth.py) | Shared auth: OAuth user flow + service account for any Workspace service |
| [scripts/gmail/auth.py](scripts/gmail/auth.py) | Gmail-specific auth helper |
| [scripts/gmail/send_email.py](scripts/gmail/send_email.py) | Send plain text, HTML, attachments, replies |
| [scripts/gmail/list_messages.py](scripts/gmail/list_messages.py) | Search, list, paginate, batch-fetch messages |
| [scripts/gmail/parse_message.py](scripts/gmail/parse_message.py) | Full MIME parsing with structured output |
| [scripts/gmail/batch_operations.py](scripts/gmail/batch_operations.py) | Bulk modify/delete/archive |
| [scripts/gmail/watch_inbox.py](scripts/gmail/watch_inbox.py) | Push notification setup and incremental sync |
| [scripts/sheets/sheets_read_write.py](scripts/sheets/sheets_read_write.py) | Read/write cells, batch updates, append rows |
| [scripts/docs/docs_edit.py](scripts/docs/docs_edit.py) | Create docs, insert text, replace placeholders, read content |
| [scripts/drive/drive_files.py](scripts/drive/drive_files.py) | List/upload/download/share/export Drive files |
