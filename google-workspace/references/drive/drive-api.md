# Google Drive API Reference

Base URL: `https://www.googleapis.com/drive/v3/files`

## Table of Contents
1. [Core Concepts](#core-concepts)
2. [Listing Files](#listing-files)
3. [Getting File Metadata](#getting-file-metadata)
4. [Uploading Files](#uploading-files)
5. [Downloading & Exporting](#downloading--exporting)
6. [Updating Files](#updating-files)
7. [Copying & Moving](#copying--moving)
8. [Deleting Files](#deleting-files)
9. [Permissions & Sharing](#permissions--sharing)
10. [Folders](#folders)
11. [Drive Query Syntax](#drive-query-syntax)
12. [MIME Types Reference](#mime-types-reference)

---

## Core Concepts

- **File ID**: Every file and folder in Drive has a unique ID (found in the URL)
- **fields parameter**: Always specify `fields` to limit response size — the full file resource is very large
- **Shortcuts vs Aliases**: `files.list` returns files the user has access to; use `corpora` and `driveId` for Shared Drives
- **Workspace files**: Google Docs/Sheets/Slides/etc. have no size (content is in Workspace format); use `files().export()` to download them as other formats
- **Parents**: Files can have multiple parents (folders); when creating, set `parents` to control location
- **Trashed vs Deleted**: `files().delete()` permanently deletes; `files().update(body={'trashed': True})` moves to trash (recoverable)

---

## Listing Files

```python
service = build('drive', 'v3', credentials=creds)

# List files matching a query
results = service.files().list(
    q="mimeType='application/vnd.google-apps.spreadsheet' and trashed=false",
    fields='nextPageToken, files(id, name, mimeType, modifiedTime, size)',
    orderBy='modifiedTime desc',
    pageSize=100,
).execute()

files = results.get('files', [])
for f in files:
    print(f"{f['name']} ({f['id']}) - {f.get('size', 'N/A')} bytes")
```

### Paginate through all results

```python
def list_all_files(service, query: str, fields: str = 'files(id, name, mimeType)') -> list[dict]:
    """List all files matching a query, handling pagination."""
    all_files = []
    page_token = None

    while True:
        kwargs = {
            'q': query,
            'fields': f'nextPageToken, {fields}',
            'pageSize': 1000,
        }
        if page_token:
            kwargs['pageToken'] = page_token

        result = service.files().list(**kwargs).execute()
        all_files.extend(result.get('files', []))

        page_token = result.get('nextPageToken')
        if not page_token:
            break

    return all_files
```

---

## Getting File Metadata

```python
# Get specific fields
file_meta = service.files().get(
    fileId=file_id,
    fields='id, name, mimeType, size, modifiedTime, createdTime, parents, webViewLink, owners'
).execute()

print(f"Name: {file_meta['name']}")
print(f"Type: {file_meta['mimeType']}")
print(f"Link: {file_meta.get('webViewLink')}")
print(f"Parents: {file_meta.get('parents', [])}")
```

### Useful file fields

| Field | Description |
|-------|-------------|
| `id` | File ID |
| `name` | File name |
| `mimeType` | MIME type |
| `size` | Size in bytes (not set for Workspace files) |
| `createdTime` | RFC 3339 timestamp |
| `modifiedTime` | RFC 3339 timestamp |
| `parents` | List of parent folder IDs |
| `webViewLink` | URL to open in browser |
| `webContentLink` | Direct download URL (non-Workspace files) |
| `owners` | List of owners `[{emailAddress, displayName}]` |
| `sharingUser` | Who shared this file with you |
| `permissions` | Permissions list (requires files.get with permissions field) |
| `starred` | Whether file is starred |
| `trashed` | Whether in trash |
| `description` | File description |
| `thumbnailLink` | Thumbnail URL |

---

## Uploading Files

### Simple upload (< 5 MB)

```python
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
import io

# Upload from file path
def upload_file(service, name: str, filepath: str,
                folder_id: str = None, mime_type: str = None) -> dict:
    """Upload a local file to Drive."""
    if mime_type is None:
        import mimetypes
        mime_type, _ = mimetypes.guess_type(filepath)
        mime_type = mime_type or 'application/octet-stream'

    metadata = {'name': name}
    if folder_id:
        metadata['parents'] = [folder_id]

    media = MediaFileUpload(filepath, mimetype=mime_type, resumable=False)

    return service.files().create(
        body=metadata,
        media_body=media,
        fields='id, name, webViewLink'
    ).execute()

result = upload_file(service, 'report.pdf', '/tmp/report.pdf', folder_id='1abc...')
print(f"Uploaded: {result['id']}")
```

### Upload from bytes/buffer

```python
def upload_bytes(service, name: str, content: bytes,
                 mime_type: str, folder_id: str = None) -> dict:
    metadata = {'name': name}
    if folder_id:
        metadata['parents'] = [folder_id]

    media = MediaIoBaseUpload(io.BytesIO(content), mimetype=mime_type)

    return service.files().create(
        body=metadata,
        media_body=media,
        fields='id, name, webViewLink'
    ).execute()
```

### Resumable upload (> 5 MB)

```python
media = MediaFileUpload(
    'large_video.mp4',
    mimetype='video/mp4',
    resumable=True,
    chunksize=256 * 1024  # 256 KB chunks
)

request = service.files().create(
    body={'name': 'large_video.mp4', 'parents': [folder_id]},
    media_body=media,
    fields='id'
)

response = None
while response is None:
    status, response = request.next_chunk()
    if status:
        print(f"Uploaded {int(status.progress() * 100)}%")

print(f"Done: {response['id']}")
```

### Convert to Google format on upload

```python
# Upload a .xlsx file and convert it to Google Sheets
service.files().create(
    body={
        'name': 'My Spreadsheet',
        'mimeType': 'application/vnd.google-apps.spreadsheet',  # Target format
        'parents': [folder_id]
    },
    media_body=MediaFileUpload(
        'data.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ),
    fields='id'
).execute()
```

---

## Downloading & Exporting

### Download a regular file (non-Workspace)

```python
import io
from googleapiclient.http import MediaIoBaseDownload

def download_file(service, file_id: str, dest_path: str):
    request = service.files().get_media(fileId=file_id)
    with open(dest_path, 'wb') as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"Download {int(status.progress() * 100)}%")

download_file(service, file_id, '/tmp/report.pdf')
```

### Export a Google Workspace file

```python
EXPORT_MIME_TYPES = {
    'application/vnd.google-apps.spreadsheet': {
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'csv':  'text/csv',
        'pdf':  'application/pdf',
        'ods':  'application/x-vnd.oasis.opendocument.spreadsheet',
    },
    'application/vnd.google-apps.document': {
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'pdf':  'application/pdf',
        'txt':  'text/plain',
        'html': 'text/html',
    },
    'application/vnd.google-apps.presentation': {
        'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'pdf':  'application/pdf',
    },
}

def export_google_file(service, file_id: str, export_format: str, dest_path: str):
    content = service.files().export(
        fileId=file_id,
        mimeType=export_format
    ).execute()
    with open(dest_path, 'wb') as f:
        f.write(content)

# Export a Sheet as Excel
export_google_file(
    service, spreadsheet_id,
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'output.xlsx'
)
```

---

## Updating Files

### Update metadata

```python
service.files().update(
    fileId=file_id,
    body={
        'name': 'New Filename.pdf',
        'description': 'Updated description',
        'starred': True,
    }
).execute()
```

### Update file content

```python
service.files().update(
    fileId=file_id,
    media_body=MediaFileUpload('updated_content.pdf', mimetype='application/pdf'),
    fields='id, modifiedTime'
).execute()
```

### Move file to a different folder

```python
# Get current parents first
file_meta = service.files().get(fileId=file_id, fields='parents').execute()
old_parents = ','.join(file_meta.get('parents', []))

service.files().update(
    fileId=file_id,
    addParents=new_folder_id,
    removeParents=old_parents,
    fields='id, parents'
).execute()
```

---

## Copying & Moving

```python
# Copy a file
copy = service.files().copy(
    fileId=file_id,
    body={
        'name': 'Copy of My File',
        'parents': [destination_folder_id]
    },
    fields='id, name'
).execute()
print(f"Copied to: {copy['id']}")
```

---

## Deleting Files

```python
# Permanently delete (irreversible)
service.files().delete(fileId=file_id).execute()

# Move to trash (recoverable)
service.files().update(
    fileId=file_id,
    body={'trashed': True}
).execute()

# Restore from trash
service.files().update(
    fileId=file_id,
    body={'trashed': False}
).execute()
```

---

## Permissions & Sharing

### List permissions

```python
permissions = service.permissions().list(
    fileId=file_id,
    fields='permissions(id, role, type, emailAddress, displayName)'
).execute()

for perm in permissions.get('permissions', []):
    print(f"{perm['type']}: {perm.get('emailAddress', 'anyone')} - {perm['role']}")
```

### Share with a specific user

```python
result = service.permissions().create(
    fileId=file_id,
    body={
        'type': 'user',
        'role': 'writer',          # 'reader' | 'writer' | 'commenter' | 'owner'
        'emailAddress': 'user@example.com'
    },
    sendNotificationEmail=True,
    emailMessage='Sharing this file with you.',
    fields='id'
).execute()
```

### Share with a domain

```python
service.permissions().create(
    fileId=file_id,
    body={
        'type': 'domain',
        'role': 'reader',
        'domain': 'example.com'
    }
).execute()
```

### Make publicly accessible

```python
service.permissions().create(
    fileId=file_id,
    body={
        'type': 'anyone',
        'role': 'reader'
    }
).execute()

# Get the public link
meta = service.files().get(fileId=file_id, fields='webViewLink').execute()
print(f"Public URL: {meta['webViewLink']}")
```

### Remove a permission

```python
service.permissions().delete(
    fileId=file_id,
    permissionId=permission_id
).execute()
```

### Permission roles

| Role | Capabilities |
|------|-------------|
| `reader` | View only |
| `commenter` | View and comment |
| `writer` | Edit, comment, share |
| `fileOrganizer` | Move, rename files in Shared Drives |
| `organizer` | Add/remove members in Shared Drives |
| `owner` | Full control (personal Drive only) |

---

## Folders

```python
# Create a folder
folder = service.files().create(
    body={
        'name': 'My Folder',
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]  # Optional: place inside another folder
    },
    fields='id, name'
).execute()
folder_id = folder['id']

# List contents of a folder
files = service.files().list(
    q=f"'{folder_id}' in parents and trashed=false",
    fields='files(id, name, mimeType, size)'
).execute().get('files', [])
```

---

## Drive Query Syntax

Used in the `q` parameter of `files().list()`.

### Common operators

```python
# Files by type
"mimeType='application/vnd.google-apps.spreadsheet'"
"mimeType='application/vnd.google-apps.document'"
"mimeType='application/vnd.google-apps.folder'"
"mimeType='application/pdf'"

# Name search
"name='exact name'"
"name contains 'partial'"

# Full-text search
"fullText contains 'search term'"

# Date filters
"modifiedTime > '2024-01-01T00:00:00'"
"createdTime > '2024-01-01T00:00:00'"

# Shared with me
"sharedWithMe=true"

# In a folder
"'FOLDER_ID' in parents"

# Starred
"starred=true"

# Not trashed (almost always include this)
"trashed=false"

# Combine with 'and', 'or', 'not'
"mimeType='application/pdf' and modifiedTime > '2024-01-01T00:00:00' and trashed=false"
```

---

## MIME Types Reference

### Google Workspace file types

| Type | MIME Type |
|------|-----------|
| Google Docs | `application/vnd.google-apps.document` |
| Google Sheets | `application/vnd.google-apps.spreadsheet` |
| Google Slides | `application/vnd.google-apps.presentation` |
| Google Forms | `application/vnd.google-apps.form` |
| Google Drawings | `application/vnd.google-apps.drawing` |
| Google Sites | `application/vnd.google-apps.site` |
| Folder | `application/vnd.google-apps.folder` |
| Shortcut | `application/vnd.google-apps.shortcut` |

### Common file types

| Type | MIME Type |
|------|-----------|
| PDF | `application/pdf` |
| Excel | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| Word | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| PowerPoint | `application/vnd.openxmlformats-officedocument.presentationml.presentation` |
| CSV | `text/csv` |
| Plain text | `text/plain` |
| JSON | `application/json` |
| ZIP | `application/zip` |
| PNG | `image/png` |
| JPEG | `image/jpeg` |

### Scope Reference

| Scope | Access |
|-------|--------|
| `https://www.googleapis.com/auth/drive.readonly` | Read all files |
| `https://www.googleapis.com/auth/drive.file` | Only files app created/opened |
| `https://www.googleapis.com/auth/drive.metadata` | View/manage metadata |
| `https://www.googleapis.com/auth/drive.metadata.readonly` | View metadata only |
| `https://www.googleapis.com/auth/drive.appdata` | App-specific folder |
| `https://www.googleapis.com/auth/drive` | Full Drive access |
