"""
Google Drive Files Script
Covers: list, upload, download, export, copy, move, delete, share.
"""
import io
import os
import mimetypes
from pathlib import Path
from typing import Optional

from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError


# ---------------------------------------------------------------------------
# Listing
# ---------------------------------------------------------------------------

def list_files(service, query: str = 'trashed=false',
               fields: str = 'files(id, name, mimeType, size, modifiedTime)',
               order_by: str = 'modifiedTime desc',
               page_size: int = 100) -> list[dict]:
    """
    List files matching a query (first page).

    Args:
        query: Drive query string. See references/drive/drive-api.md for syntax.
        fields: Fields to return.
        order_by: Sort order.
        page_size: Max results per page (max 1000).

    Returns:
        List of file metadata dicts.
    """
    result = service.files().list(
        q=query,
        fields=f'nextPageToken, {fields}',
        orderBy=order_by,
        pageSize=page_size,
    ).execute()
    return result.get('files', [])


def list_all_files(service, query: str = 'trashed=false',
                   fields: str = 'files(id, name, mimeType, size, modifiedTime)',
                   order_by: str = 'name') -> list[dict]:
    """
    List all files matching a query, handling pagination automatically.
    """
    all_files = []
    page_token = None

    while True:
        kwargs = {
            'q': query,
            'fields': f'nextPageToken, {fields}',
            'orderBy': order_by,
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


def list_folder_contents(service, folder_id: str,
                          include_folders: bool = True) -> list[dict]:
    """List all files/folders directly inside a folder."""
    q = f"'{folder_id}' in parents and trashed=false"
    if not include_folders:
        q += " and mimeType != 'application/vnd.google-apps.folder'"

    return list_all_files(
        service, q,
        fields='files(id, name, mimeType, size, modifiedTime, webViewLink)'
    )


def get_file_metadata(service, file_id: str,
                       fields: str = 'id, name, mimeType, size, modifiedTime, '
                                     'createdTime, parents, webViewLink, owners') -> dict:
    """Get metadata for a specific file."""
    return service.files().get(fileId=file_id, fields=fields).execute()


def find_by_name(service, name: str, parent_id: str = None,
                  mime_type: str = None) -> list[dict]:
    """Find files by exact name."""
    q = f"name='{name}' and trashed=false"
    if parent_id:
        q += f" and '{parent_id}' in parents"
    if mime_type:
        q += f" and mimeType='{mime_type}'"
    return list_all_files(service, q)


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

def upload_file(service, name: str, filepath: str,
                folder_id: str = None,
                mime_type: str = None,
                convert_to_google_format: bool = False) -> dict:
    """
    Upload a local file to Google Drive.

    Args:
        name: Name in Drive.
        filepath: Local file path.
        folder_id: Parent folder ID (root if None).
        mime_type: Override MIME type (auto-detected if None).
        convert_to_google_format: If True, convert Office files to Google format.

    Returns:
        File resource with id, name, webViewLink.
    """
    if mime_type is None:
        detected, _ = mimetypes.guess_type(filepath)
        mime_type = detected or 'application/octet-stream'

    metadata = {'name': name}
    if folder_id:
        metadata['parents'] = [folder_id]

    # Map Office → Google formats for conversion
    CONVERT_MAP = {
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            'application/vnd.google-apps.spreadsheet',
        'application/vnd.ms-excel':
            'application/vnd.google-apps.spreadsheet',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            'application/vnd.google-apps.document',
        'application/msword':
            'application/vnd.google-apps.document',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation':
            'application/vnd.google-apps.presentation',
        'text/csv':
            'application/vnd.google-apps.spreadsheet',
    }
    if convert_to_google_format and mime_type in CONVERT_MAP:
        metadata['mimeType'] = CONVERT_MAP[mime_type]

    file_size = os.path.getsize(filepath)
    resumable = file_size > 5 * 1024 * 1024  # 5 MB threshold

    media = MediaFileUpload(filepath, mimetype=mime_type, resumable=resumable)

    if resumable:
        request = service.files().create(
            body=metadata, media_body=media,
            fields='id, name, webViewLink'
        )
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"  Uploading {name}: {int(status.progress() * 100)}%")
        return response
    else:
        return service.files().create(
            body=metadata, media_body=media,
            fields='id, name, webViewLink'
        ).execute()


def upload_bytes(service, name: str, content: bytes,
                 mime_type: str, folder_id: str = None) -> dict:
    """Upload in-memory bytes to Drive."""
    metadata = {'name': name}
    if folder_id:
        metadata['parents'] = [folder_id]

    media = MediaIoBaseUpload(io.BytesIO(content), mimetype=mime_type)
    return service.files().create(
        body=metadata, media_body=media,
        fields='id, name, webViewLink'
    ).execute()


# ---------------------------------------------------------------------------
# Download & Export
# ---------------------------------------------------------------------------

def download_file(service, file_id: str, dest_path: str,
                  show_progress: bool = False):
    """Download a regular (non-Workspace) file."""
    request = service.files().get_media(fileId=file_id)
    Path(dest_path).parent.mkdir(parents=True, exist_ok=True)

    with open(dest_path, 'wb') as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if show_progress and status:
                print(f"  Downloading: {int(status.progress() * 100)}%")


def export_google_file(service, file_id: str, export_mime: str,
                        dest_path: str):
    """
    Export a Google Workspace file (Docs/Sheets/Slides) to another format.

    Common export_mime values:
        - Google Doc  → 'application/pdf' | 'text/plain' |
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        - Google Sheet → 'application/pdf' | 'text/csv' |
                         'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        - Google Slides → 'application/pdf' |
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    """
    content = service.files().export(fileId=file_id, mimeType=export_mime).execute()
    Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
    with open(dest_path, 'wb') as f:
        f.write(content)


def download_as_pdf(service, file_id: str, dest_path: str):
    """Export any Google Workspace file as PDF."""
    export_google_file(service, file_id, 'application/pdf', dest_path)


# ---------------------------------------------------------------------------
# Folders
# ---------------------------------------------------------------------------

def create_folder(service, name: str, parent_id: str = None) -> dict:
    """Create a folder in Drive."""
    metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        metadata['parents'] = [parent_id]

    return service.files().create(
        body=metadata,
        fields='id, name, webViewLink'
    ).execute()


def get_or_create_folder(service, name: str, parent_id: str = None) -> str:
    """Get a folder ID by name, creating it if it doesn't exist."""
    q = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        q += f" and '{parent_id}' in parents"

    results = list_files(service, q, fields='files(id, name)')
    if results:
        return results[0]['id']

    folder = create_folder(service, name, parent_id)
    return folder['id']


# ---------------------------------------------------------------------------
# Copy, Move, Delete
# ---------------------------------------------------------------------------

def copy_file(service, file_id: str, new_name: str,
              folder_id: str = None) -> dict:
    """Copy a file. Returns the new file resource."""
    body = {'name': new_name}
    if folder_id:
        body['parents'] = [folder_id]
    return service.files().copy(
        fileId=file_id, body=body, fields='id, name, webViewLink'
    ).execute()


def move_file(service, file_id: str, new_folder_id: str) -> dict:
    """Move a file to a different folder."""
    file_meta = service.files().get(fileId=file_id, fields='parents').execute()
    old_parents = ','.join(file_meta.get('parents', []))

    return service.files().update(
        fileId=file_id,
        addParents=new_folder_id,
        removeParents=old_parents,
        fields='id, parents'
    ).execute()


def rename_file(service, file_id: str, new_name: str) -> dict:
    """Rename a file."""
    return service.files().update(
        fileId=file_id,
        body={'name': new_name},
        fields='id, name'
    ).execute()


def trash_file(service, file_id: str):
    """Move a file to trash (recoverable)."""
    service.files().update(fileId=file_id, body={'trashed': True}).execute()


def restore_file(service, file_id: str):
    """Restore a file from trash."""
    service.files().update(fileId=file_id, body={'trashed': False}).execute()


def delete_file(service, file_id: str):
    """Permanently delete a file. This is IRREVERSIBLE."""
    service.files().delete(fileId=file_id).execute()


# ---------------------------------------------------------------------------
# Permissions & Sharing
# ---------------------------------------------------------------------------

def share_with_user(service, file_id: str, email: str,
                     role: str = 'reader',
                     send_notification: bool = True,
                     message: str = None) -> dict:
    """
    Share a file with a specific user.

    Args:
        role: 'reader' | 'commenter' | 'writer' | 'owner'
    """
    kwargs = {
        'fileId': file_id,
        'body': {'type': 'user', 'role': role, 'emailAddress': email},
        'sendNotificationEmail': send_notification,
        'fields': 'id'
    }
    if message:
        kwargs['emailMessage'] = message

    return service.permissions().create(**kwargs).execute()


def share_with_domain(service, file_id: str, domain: str,
                       role: str = 'reader') -> dict:
    """Share a file with everyone in a domain."""
    return service.permissions().create(
        fileId=file_id,
        body={'type': 'domain', 'role': role, 'domain': domain},
        fields='id'
    ).execute()


def make_public(service, file_id: str, role: str = 'reader') -> str:
    """
    Make a file publicly accessible.

    Returns:
        Public URL (webViewLink).
    """
    service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': role},
        fields='id'
    ).execute()

    meta = service.files().get(fileId=file_id, fields='webViewLink').execute()
    return meta.get('webViewLink', '')


def remove_permission(service, file_id: str, permission_id: str):
    """Remove a permission from a file."""
    service.permissions().delete(fileId=file_id, permissionId=permission_id).execute()


def list_permissions(service, file_id: str) -> list[dict]:
    """List all permissions on a file."""
    result = service.permissions().list(
        fileId=file_id,
        fields='permissions(id, role, type, emailAddress, displayName)'
    ).execute()
    return result.get('permissions', [])


# ---------------------------------------------------------------------------
# Example
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    from auth import get_service

    drive = get_service('drive', 'v3', scopes=['https://www.googleapis.com/auth/drive'])

    # List recent files
    print("=== Recent Files ===")
    files = list_files(drive, 'trashed=false', order_by='modifiedTime desc',
                        page_size=5)
    for f in files:
        print(f"  {f['name']} ({f['mimeType']}) - {f['id']}")

    # Create a folder
    folder = create_folder(drive, 'Test Folder')
    print(f"\nCreated folder: {folder['id']}")

    # Upload a file
    # result = upload_file(drive, 'test.txt', '/tmp/test.txt', folder_id=folder['id'])
    # print(f"Uploaded: {result['id']}")
