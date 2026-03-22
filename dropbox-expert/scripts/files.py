"""
Dropbox File Operations Script

Covers: upload (simple + chunked auto-select), download, list folder,
        search, copy, move, delete, create folder, get metadata.

Usage:
    from files import upload, download, list_folder

    dbx = get_client()  # from auth.py
    upload(dbx, '/local/file.pdf', '/remote/file.pdf')
    download(dbx, '/remote/file.pdf', '/local/file.pdf')
"""
import os
import time
from pathlib import Path
from typing import Optional, Generator

import dropbox
from dropbox.files import (
    WriteMode, FileMetadata, FolderMetadata, DeletedMetadata,
    CommitInfo, UploadSessionCursor, SearchOptions, FileCategory,
)
from dropbox.exceptions import ApiError

CHUNK_SIZE = 4 * 1024 * 1024   # 4 MB — must be multiple of 4 MB
SIMPLE_UPLOAD_LIMIT = 150 * 1024 * 1024  # 150 MB


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

def upload(dbx: dropbox.Dropbox, local_path: str, remote_path: str,
           overwrite: bool = True, autorename: bool = False,
           mute: bool = False, show_progress: bool = True) -> FileMetadata:
    """
    Upload a file to Dropbox. Auto-selects simple or chunked upload.

    Args:
        local_path: Path to the local file.
        remote_path: Destination path in Dropbox (must start with /).
        overwrite: If True, overwrite existing file. If False, fail on conflict.
        autorename: If True, auto-rename on conflict (only with overwrite=False).
        mute: If True, suppress desktop notifications.
        show_progress: If True, print progress for chunked uploads.

    Returns:
        FileMetadata for the uploaded file.
    """
    file_size = os.path.getsize(local_path)
    mode = WriteMode.overwrite if overwrite else WriteMode.add

    with open(local_path, 'rb') as f:
        if file_size <= SIMPLE_UPLOAD_LIMIT:
            return dbx.files_upload(
                f.read(), remote_path,
                mode=mode,
                autorename=autorename,
                mute=mute,
            )
        else:
            return _chunked_upload(
                dbx, f, remote_path, file_size,
                mode=mode, show_progress=show_progress
            )


def _chunked_upload(dbx, f, remote_path: str, file_size: int,
                     mode=WriteMode.overwrite, show_progress=True) -> FileMetadata:
    """Internal: upload a file using upload sessions (for files > 150 MB)."""
    session_id = None
    offset = 0

    while True:
        chunk = f.read(CHUNK_SIZE)
        if not chunk:
            break

        if session_id is None:
            # Start session with first chunk
            result = dbx.files_upload_session_start(chunk)
            session_id = result.session_id
        else:
            cursor = UploadSessionCursor(session_id=session_id, offset=offset)
            remaining_after = file_size - offset - len(chunk)

            if remaining_after <= 0:
                # This is the last chunk — finish the session
                commit = CommitInfo(path=remote_path, mode=mode)
                # Read any extra bytes (shouldn't happen, but safe)
                final = chunk + f.read()
                if show_progress:
                    print(f"  Finalizing upload: {remote_path}")
                return dbx.files_upload_session_finish(final, cursor, commit)

            dbx.files_upload_session_append_v2(chunk, cursor)

        offset += len(chunk)
        if show_progress:
            pct = min(100, int(offset * 100 / file_size))
            print(f"  Uploading {Path(remote_path).name}: {pct}% ({offset/1024/1024:.1f} MB)")

    # Handle case where file fits in exactly one chunk
    cursor = UploadSessionCursor(session_id=session_id, offset=offset)
    commit = CommitInfo(path=remote_path, mode=mode)
    return dbx.files_upload_session_finish(b'', cursor, commit)


def upload_bytes(dbx: dropbox.Dropbox, data: bytes, remote_path: str,
                  overwrite: bool = True) -> FileMetadata:
    """Upload in-memory bytes to Dropbox."""
    mode = WriteMode.overwrite if overwrite else WriteMode.add
    return dbx.files_upload(data, remote_path, mode=mode)


def upload_folder(dbx: dropbox.Dropbox, local_dir: str, remote_dir: str,
                   overwrite: bool = True, show_progress: bool = True) -> list:
    """
    Recursively upload a local directory to Dropbox.

    Returns:
        List of (local_path, remote_path, FileMetadata) tuples.
    """
    results = []
    local_dir = Path(local_dir)

    for local_file in local_dir.rglob('*'):
        if local_file.is_file():
            relative = local_file.relative_to(local_dir)
            remote_path = f"{remote_dir}/{relative}".replace('\\', '/')
            if show_progress:
                print(f"Uploading: {local_file} → {remote_path}")
            meta = upload(dbx, str(local_file), remote_path, overwrite=overwrite,
                          show_progress=False)
            results.append((str(local_file), remote_path, meta))

    return results


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

def download(dbx: dropbox.Dropbox, remote_path: str, local_path: str) -> FileMetadata:
    """
    Download a file from Dropbox.

    Returns:
        FileMetadata for the downloaded file.
    """
    Path(local_path).parent.mkdir(parents=True, exist_ok=True)
    metadata, response = dbx.files_download(remote_path)
    with open(local_path, 'wb') as f:
        f.write(response.content)
    return metadata


def download_to_bytes(dbx: dropbox.Dropbox, remote_path: str) -> tuple[FileMetadata, bytes]:
    """Download a file and return (metadata, bytes)."""
    metadata, response = dbx.files_download(remote_path)
    return metadata, response.content


def download_folder(dbx: dropbox.Dropbox, remote_dir: str, local_dir: str,
                     show_progress: bool = True) -> list:
    """
    Download all files in a Dropbox folder recursively.

    Returns:
        List of (remote_path, local_path) tuples.
    """
    results = []
    for entry in iter_folder(dbx, remote_dir, recursive=True):
        if isinstance(entry, FileMetadata):
            # Reconstruct local path
            relative = entry.path_display[len(remote_dir):].lstrip('/')
            local_path = os.path.join(local_dir, relative.replace('/', os.sep))
            if show_progress:
                print(f"Downloading: {entry.path_display} → {local_path}")
            download(dbx, entry.path_display, local_path)
            results.append((entry.path_display, local_path))
    return results


# ---------------------------------------------------------------------------
# List & Iterate
# ---------------------------------------------------------------------------

def list_folder(dbx: dropbox.Dropbox, path: str = '',
                 recursive: bool = False,
                 include_deleted: bool = False) -> list:
    """
    List contents of a folder (all pages).

    Args:
        path: Dropbox path. '' = root.
        recursive: If True, include all descendants.

    Returns:
        List of FileMetadata, FolderMetadata, or DeletedMetadata objects.
    """
    return list(iter_folder(dbx, path, recursive=recursive,
                             include_deleted=include_deleted))


def iter_folder(dbx: dropbox.Dropbox, path: str = '',
                 recursive: bool = False,
                 include_deleted: bool = False) -> Generator:
    """
    Generator that yields folder entries one page at a time (memory-efficient).
    """
    result = dbx.files_list_folder(
        path=path,
        recursive=recursive,
        include_deleted=include_deleted,
        limit=2000,
    )
    while True:
        yield from result.entries
        if not result.has_more:
            break
        result = dbx.files_list_folder_continue(result.cursor)


def list_files_only(dbx: dropbox.Dropbox, path: str = '',
                     recursive: bool = False) -> list[FileMetadata]:
    """Return only FileMetadata entries (excludes folders and deleted items)."""
    return [e for e in iter_folder(dbx, path, recursive=recursive)
            if isinstance(e, FileMetadata)]


def list_folders_only(dbx: dropbox.Dropbox, path: str = '') -> list[FolderMetadata]:
    """Return only FolderMetadata entries (non-recursive)."""
    return [e for e in iter_folder(dbx, path)
            if isinstance(e, FolderMetadata)]


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------

def get_metadata(dbx: dropbox.Dropbox, path: str) -> Optional[object]:
    """
    Get metadata for a file or folder. Returns None if path not found.
    """
    try:
        return dbx.files_get_metadata(path)
    except ApiError as e:
        if e.error.is_path() and e.error.get_path().is_not_found():
            return None
        raise


def exists(dbx: dropbox.Dropbox, path: str) -> bool:
    """Return True if the path exists in Dropbox."""
    return get_metadata(dbx, path) is not None


# ---------------------------------------------------------------------------
# Copy, Move, Delete
# ---------------------------------------------------------------------------

def copy(dbx: dropbox.Dropbox, from_path: str, to_path: str,
          autorename: bool = False) -> FileMetadata:
    """Copy a file or folder."""
    result = dbx.files_copy_v2(from_path, to_path, autorename=autorename)
    return result.metadata


def move(dbx: dropbox.Dropbox, from_path: str, to_path: str,
          autorename: bool = False) -> FileMetadata:
    """Move or rename a file or folder."""
    result = dbx.files_move_v2(from_path, to_path, autorename=autorename)
    return result.metadata


def delete(dbx: dropbox.Dropbox, path: str) -> object:
    """Delete a file or folder (moves to trash). Returns deleted entry metadata."""
    result = dbx.files_delete_v2(path)
    return result.metadata


def create_folder(dbx: dropbox.Dropbox, path: str,
                   autorename: bool = False) -> FolderMetadata:
    """Create a new folder."""
    result = dbx.files_create_folder_v2(path, autorename=autorename)
    return result.metadata


def get_or_create_folder(dbx: dropbox.Dropbox, path: str) -> FolderMetadata:
    """Return folder metadata, creating the folder if it doesn't exist."""
    meta = get_metadata(dbx, path)
    if meta is None:
        return create_folder(dbx, path)
    if isinstance(meta, FolderMetadata):
        return meta
    raise ValueError(f"Path exists but is not a folder: {path}")


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search(dbx: dropbox.Dropbox, query: str, path: str = '',
            max_results: int = 100,
            filename_only: bool = False,
            file_categories: list = None) -> list[FileMetadata]:
    """
    Search Dropbox files.

    Args:
        query: Search query string.
        path: Restrict search to this folder ('' = all of Dropbox).
        max_results: Max results to return.
        filename_only: If True, search filename only (not content).
        file_categories: Optional list of FileCategory values to filter by.
            e.g. [FileCategory.pdf, FileCategory.image]

    Returns:
        List of FileMetadata objects.
    """
    options_kwargs = {
        'path': path,
        'max_results': max_results,
        'filename_only': filename_only,
    }
    if file_categories:
        options_kwargs['file_categories'] = file_categories

    options = SearchOptions(**options_kwargs)
    results = dbx.files_search_v2(query=query, options=options)

    entries = []
    while True:
        for match in results.matches:
            meta = match.metadata.get_metadata()
            if isinstance(meta, FileMetadata):
                entries.append(meta)
        if not results.has_more:
            break
        results = dbx.files_search_continue_v2(results.cursor)

    return entries[:max_results]


# ---------------------------------------------------------------------------
# Shared links (quick helpers — see references/sharing-api.md for full API)
# ---------------------------------------------------------------------------

def get_or_create_link(dbx: dropbox.Dropbox, path: str) -> str:
    """Get existing shared link URL or create a new one."""
    try:
        link = dbx.sharing_create_shared_link_with_settings(path)
        return link.url
    except ApiError as e:
        if e.error.is_shared_link_already_exists():
            result = dbx.sharing_list_shared_links(path=path, direct_only=True)
            if result.links:
                return result.links[0].url
        raise


def to_download_url(shared_url: str) -> str:
    """Convert a Dropbox shared link to a direct download URL."""
    return shared_url.replace('www.dropbox.com', 'dl.dropboxusercontent.com') \
                     .replace('?dl=0', '?dl=1') \
                     .replace('&dl=0', '&dl=1')


# ---------------------------------------------------------------------------
# Example / quick test
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from auth import get_client

    dbx = get_client()

    # List root folder
    print("=== Root folder contents ===")
    for entry in list_folder(dbx, ''):
        icon = '[DIR]' if isinstance(entry, FolderMetadata) else '[FILE]'
        size = f" ({entry.size:,} bytes)" if isinstance(entry, FileMetadata) else ''
        print(f"  {icon} {entry.name}{size}")

    # Space usage
    usage = dbx.users_get_space_usage()
    used_gb = usage.used / (1024**3)
    print(f"\nStorage used: {used_gb:.2f} GB")
