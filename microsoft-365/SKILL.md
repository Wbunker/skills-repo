---
name: microsoft-365
description: >
  Expert-level Microsoft 365 API integration using Python and the Microsoft Graph API.
  Use when working programmatically with Outlook/Exchange (email, calendar, contacts),
  OneDrive/SharePoint (file management, sharing), Excel Online (workbooks, worksheets,
  ranges, tables, charts), Microsoft Teams (messages, channels, meetings), or any
  Microsoft 365 service. Covers Microsoft Graph SDK for Python (msgraph-sdk), MSAL
  authentication (delegated and app-only/client credentials), Azure App Registration,
  and all major Graph API resource types.
  Triggers on: Microsoft Graph API, Microsoft 365 API, Outlook API, Exchange API,
  OneDrive API, SharePoint API, Teams API, Excel API, Graph SDK Python, MSAL Python,
  azure app registration, send email Outlook Python, read Outlook Python, outlook
  automation, read/write Excel Python, excel automation, teams message Python, onedrive
  Python, microsoft 365 automation, office 365 API, graph explorer, msgraph-sdk,
  azure active directory, entra ID, client credentials flow, delegated auth.
---

# Microsoft 365 Expert

Full API reference for Outlook Mail, Calendar, Contacts, OneDrive/SharePoint Files,
Excel Online, and Microsoft Teams using the Microsoft Graph API
(`https://graph.microsoft.com/v1.0`).

## Installation

```bash
# Microsoft Graph Python SDK + Azure Identity for auth
pip install msgraph-sdk azure-identity

# Optional: MSAL directly for lower-level token control
pip install msal
```

## Quick Start (Local / Personal Use — No App Registration)

Like `gcloud auth login`, the Azure CLI lets you authenticate as yourself with no app registration needed:

```bash
brew install azure-cli
az login   # opens browser, done
```

Then in Python:

```python
from azure.identity import AzureCliCredential
from msgraph import GraphServiceClient

credential = AzureCliCredential()
scopes = ["https://graph.microsoft.com/.default"]
graph_client = GraphServiceClient(credential, scopes)
```

That's it — no tenant ID, client ID, or secrets required for local personal-assistant use.

## Quick Start (App-Only / Client Credentials)

For automation without a signed-in user (background services, scripts that need their own identity):

```python
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient

# From your Azure App Registration
TENANT_ID     = "YOUR_TENANT_ID"
CLIENT_ID     = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"

credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
)

scopes = ["https://graph.microsoft.com/.default"]
graph_client = GraphServiceClient(credential, scopes)
```

## Quick Start (Delegated / Device Code)

For acting on behalf of a user without the Azure CLI (e.g. on a server):

```python
from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient

credential = DeviceCodeCredential(
    tenant_id="YOUR_TENANT_ID",
    client_id="YOUR_CLIENT_ID",
)

scopes = [
    "Mail.ReadWrite",
    "Calendars.ReadWrite",
    "Files.ReadWrite.All",
    "Chat.ReadWrite",
    "Contacts.ReadWrite",
]
graph_client = GraphServiceClient(credential, scopes)
```

## Microsoft 365 App Equivalents

| Google Workspace | Microsoft 365 | Graph API Resource |
|------------------|---------------|--------------------|
| Gmail | Outlook / Exchange Online | `/me/messages`, `/me/mailFolders` |
| Google Docs | Word Online | SharePoint/OneDrive `.docx` files |
| Google Sheets | Excel Online | `/me/drive/items/{id}/workbook/` |
| Google Slides | PowerPoint Online | SharePoint/OneDrive `.pptx` files |
| Google Drive | OneDrive / SharePoint | `/me/drive`, `/drives/{id}` |
| Google Meet | Microsoft Teams Meetings | `/me/onlineMeetings` |
| Google Calendar | Outlook Calendar | `/me/calendar`, `/me/events` |
| Google Forms | Microsoft Forms | (limited Graph API support) |
| Google Contacts | Outlook Contacts | `/me/contacts` |
| Google Chat | Microsoft Teams Chat | `/me/chats`, `/chats/{id}/messages` |

## Key Concepts

- **Base URL**: `https://graph.microsoft.com/v1.0/` (stable) or `.../beta/` (preview)
- **`/me` alias**: Refers to the signed-in user; only usable in delegated flows
- **`/users/{user-id}`**: Access any user's data; requires app-only or admin-delegated permissions
- **Scopes**: Delegated permissions use names like `Mail.Read`; app-only tokens always use `https://graph.microsoft.com/.default`
- **Admin consent**: Application permissions (app-only) always require a tenant admin to grant consent
- **`Authorization: Bearer {token}`**: All Graph API calls require this header
- **OData**: Graph uses OData query params: `$select`, `$filter`, `$orderby`, `$top`, `$skip`, `$expand`
- **Throttling**: HTTP 429 with `Retry-After` header; SDK handles retries automatically

## Reference Files

Load these based on the task at hand:

### Authentication
| File | When to Read |
|------|-------------|
| [references/auth/azure-app-registration.md](references/auth/azure-app-registration.md) | Setting up Azure App Registration, client ID/secret, redirect URIs, admin consent |
| [references/auth/auth-flows.md](references/auth/auth-flows.md) | OAuth 2.0 flows: client credentials, device code, auth code, delegated vs app-only |

### Mail (Outlook/Exchange)
| File | When to Read |
|------|-------------|
| [references/mail/mail-api.md](references/mail/mail-api.md) | Full Outlook Mail API: read, send, reply, folders, search, attachments, rules |

### Calendar
| File | When to Read |
|------|-------------|
| [references/calendar/calendar-api.md](references/calendar/calendar-api.md) | Calendar API: events, meetings, free/busy, attendees, recurrence |

### Files (OneDrive / SharePoint)
| File | When to Read |
|------|-------------|
| [references/files/files-api.md](references/files/files-api.md) | OneDrive and SharePoint file operations: upload, download, list, share, move |

### Excel Online
| File | When to Read |
|------|-------------|
| [references/excel/excel-api.md](references/excel/excel-api.md) | Excel workbook API: worksheets, ranges, tables, charts, sessions, functions |

### Teams
| File | When to Read |
|------|-------------|
| [references/teams/teams-api.md](references/teams/teams-api.md) | Teams API: channels, messages, chats, meetings, members, online meetings |

### Contacts
| File | When to Read |
|------|-------------|
| [references/contacts/contacts-api.md](references/contacts/contacts-api.md) | Outlook Contacts API: list, create, update, delete contacts and contact folders |

## Scripts

| Script | Purpose |
|--------|---------|
| [scripts/auth/app_only_auth.py](scripts/auth/app_only_auth.py) | Client credentials (app-only) auth for background automation |
| [scripts/auth/delegated_auth.py](scripts/auth/delegated_auth.py) | Device code + token cache for delegated user auth |
| [scripts/mail/send_email.py](scripts/mail/send_email.py) | Send plain text and HTML email via Outlook |
| [scripts/mail/list_messages.py](scripts/mail/list_messages.py) | Search, list, read, and paginate messages |
| [scripts/files/onedrive_operations.py](scripts/files/onedrive_operations.py) | Upload, download, list, and share OneDrive files |
| [scripts/teams/send_message.py](scripts/teams/send_message.py) | Send messages to Teams channels and chats |
