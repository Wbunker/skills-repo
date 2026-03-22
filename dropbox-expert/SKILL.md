---
name: dropbox-expert
description: >
  Expert-level Dropbox integration using the Python SDK and API v2. Use when working
  programmatically with Dropbox: uploading or downloading files, listing folders,
  searching, copying/moving/deleting files, creating shared links, managing file
  permissions, working with file revisions, or automating Dropbox workflows.
  Also covers CLI tools (dbxcli, Dropbox-Uploader) for shell-based access.
  Triggers on: Dropbox API, Dropbox Python SDK, dropbox upload download Python,
  dropbox automation, dropbox shared link, dropbox CLI, dbxcli, dropbox file management,
  dropbox OAuth, dropbox integration, dropbox sharing, dropbox folder sync.
---

# Dropbox Expert

Full Dropbox API v2 reference using the official Python SDK (`pip install dropbox`).

## Installation

```bash
pip install dropbox
```

## Quick Start

```python
import dropbox

dbx = dropbox.Dropbox('YOUR_ACCESS_TOKEN')

# Verify auth
account = dbx.users_get_current_account()
print(account.email)

# List root folder
result = dbx.files_list_folder('')
for entry in result.entries:
    print(entry.name)

# Upload
dbx.files_upload(b'file content', '/remote/path/file.txt')

# Download
metadata, response = dbx.files_download('/remote/path/file.txt')
content = response.content

# Create shared link
link = dbx.sharing_create_shared_link_with_settings('/remote/path/file.txt')
print(link.url)
```

## Two API Domains

| Domain | Purpose |
|--------|---------|
| `https://api.dropboxapi.com/2/` | RPC calls — JSON body in, JSON body out |
| `https://content.dropboxapi.com/2/` | Upload/download — file data in body, JSON args in `Dropbox-API-Arg` header |

The Python SDK handles both automatically.

## Reference Files

Load these based on the task at hand:

| File | When to Read |
|------|-------------|
| [references/auth.md](references/auth.md) | OAuth2 setup, token types, refresh tokens, app registration, scopes |
| [references/files-api.md](references/files-api.md) | Upload (simple + chunked), download, list, copy, move, delete, search, revisions |
| [references/sharing-api.md](references/sharing-api.md) | Shared links (with password/expiry), file/folder member management |
| [references/cli.md](references/cli.md) | dbxcli commands, Dropbox-Uploader bash script |
| [references/error-handling.md](references/error-handling.md) | HTTP error codes, SDK exceptions, rate limits, retry/backoff |

## Scripts

| Script | Purpose |
|--------|---------|
| [scripts/auth.py](scripts/auth.py) | OAuth2 browser flow + token persistence; `get_client()` for use in other scripts |
| [scripts/files.py](scripts/files.py) | Upload (auto simple/chunked), download, list folder, search, copy/move/delete |

## Key Concepts

- **Paths**: Always start with `/` (e.g. `/folder/file.txt`). Root folder = `''` (empty string).
- **No `.execute()`**: SDK methods execute immediately — no builder pattern like Google APIs.
- **Chunked uploads**: Files > 150 MB must use upload sessions; auto-handled in `scripts/files.py`.
- **Rate limits**: HTTP 429 with `Retry-After` header; no published numeric quota.
- **App access**: Either **App Folder** (sandboxed) or **Full Dropbox** — set at app creation, cannot change.
- **Team access**: Use `DropboxTeam` client + `as_user()` to act on behalf of team members.
- **All methods return typed objects**: Use dot notation, not dict access (e.g. `entry.name`, not `entry['name']`).
