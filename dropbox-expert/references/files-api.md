# Dropbox Files API Reference

## Table of Contents
1. [Path Conventions](#path-conventions)
2. [Upload: Simple (≤150 MB)](#upload-simple)
3. [Upload: Chunked Sessions (>150 MB)](#upload-chunked-sessions)
4. [Batch Uploads](#batch-uploads)
5. [Download](#download)
6. [List Folder](#list-folder)
7. [Get Metadata](#get-metadata)
8. [Copy, Move, Delete](#copy-move-delete)
9. [Search](#search)
10. [Revisions](#revisions)
11. [File Properties (Custom Metadata)](#file-properties)

---

## Path Conventions

- All paths start with `/`: `/folder/file.txt`, `/photos/vacation/img.jpg`
- Root folder is `''` (empty string), **not** `'/'`
- Case-insensitive on most platforms, but Dropbox preserves case
- Namespace paths (team folders): `ns:<namespace_id>/path/to/file`

---

## Upload: Simple (≤150 MB)

```python
import dropbox
from dropbox.files import WriteMode

dbx = dropbox.Dropbox('TOKEN')

# Basic upload
with open('/local/file.txt', 'rb') as f:
    dbx.files_upload(f.read(), '/remote/file.txt')

# With options
with open('/local/report.pdf', 'rb') as f:
    meta = dbx.files_upload(
        f.read(),
        '/remote/reports/report.pdf',
        mode=WriteMode.overwrite,    # WriteMode.add (fail if exists) | WriteMode.overwrite | WriteMode.update(rev)
        autorename=False,            # True: auto-rename if name conflict
        mute=False,                  # True: suppress desktop notifications
        strict_conflict=False,       # True: error if exact revision conflict
    )

print(f"Uploaded: {meta.path_display}, size={meta.size}, rev={meta.rev}")
```

### WriteMode options

| Mode | Behavior |
|------|---------|
| `WriteMode.add` | Upload new file; error if path exists (default) |
| `WriteMode.overwrite` | Overwrite if exists, create if not |
| `WriteMode.update(rev)` | Update specific revision; error if rev doesn't match |

---

## Upload: Chunked Sessions (>150 MB)

For files larger than 150 MB. Also useful for resumable uploads or streaming.

```python
import dropbox
from dropbox.files import CommitInfo, WriteMode, UploadSessionCursor

CHUNK_SIZE = 4 * 1024 * 1024  # 4 MB (must be multiple of 4 MB)

def upload_large_file(dbx, local_path: str, remote_path: str):
    file_size = os.path.getsize(local_path)

    with open(local_path, 'rb') as f:
        # Start session with first chunk
        first_chunk = f.read(CHUNK_SIZE)
        session_start = dbx.files_upload_session_start(first_chunk)
        session_id = session_start.session_id
        offset = len(first_chunk)

        # Append remaining chunks
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            cursor = UploadSessionCursor(session_id=session_id, offset=offset)
            is_last = f.tell() >= file_size
            if is_last:
                break
            dbx.files_upload_session_append_v2(chunk, cursor)
            offset += len(chunk)
            print(f"  Uploaded {offset}/{file_size} bytes ({offset*100//file_size}%)")

        # Finish session
        commit = CommitInfo(
            path=remote_path,
            mode=WriteMode.overwrite,
        )
        cursor = UploadSessionCursor(session_id=session_id, offset=offset)
        # Include any remaining data in the finish call
        f.seek(offset)
        final_chunk = f.read()
        meta = dbx.files_upload_session_finish(final_chunk, cursor, commit)

    print(f"Upload complete: {meta.path_display}")
    return meta
```

### Simplified chunked upload (cleaner pattern)

```python
def upload_file(dbx, local_path: str, remote_path: str,
                chunk_size: int = 4 * 1024 * 1024) -> object:
    """Upload file, auto-choosing simple vs chunked based on size."""
    file_size = os.path.getsize(local_path)

    with open(local_path, 'rb') as f:
        if file_size <= 150 * 1024 * 1024:
            return dbx.files_upload(f.read(), remote_path,
                                     mode=WriteMode.overwrite)

        # Chunked upload
        session_id = None
        offset = 0

        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break

            if session_id is None:
                result = dbx.files_upload_session_start(chunk)
                session_id = result.session_id
            else:
                cursor = UploadSessionCursor(session_id=session_id, offset=offset)
                remaining = file_size - offset - len(chunk)
                if remaining <= 0:
                    commit = CommitInfo(path=remote_path, mode=WriteMode.overwrite)
                    return dbx.files_upload_session_finish(chunk, cursor, commit)
                dbx.files_upload_session_append_v2(chunk, cursor)

            offset += len(chunk)

        # Handle edge case: single chunk that ends the session
        cursor = UploadSessionCursor(session_id=session_id, offset=offset)
        commit = CommitInfo(path=remote_path, mode=WriteMode.overwrite)
        return dbx.files_upload_session_finish(b'', cursor, commit)
```

---

## Batch Uploads

Up to 1,000 upload sessions can be started/finished in batch:

```python
# Start batch sessions
entries = [{'close': False}] * len(file_list)
result = dbx.files_upload_session_start_batch(num_sessions=len(file_list))
session_ids = result.session_ids

# Append data and finish
finish_args = []
for session_id, local_path, remote_path in zip(session_ids, local_files, remote_paths):
    with open(local_path, 'rb') as f:
        data = f.read()
    cursor = UploadSessionCursor(session_id=session_id, offset=0)
    commit = CommitInfo(path=remote_path, mode=WriteMode.overwrite)
    finish_args.append(dropbox.files.UploadSessionFinishArg(cursor=cursor, commit=commit))

# Batch finish
result = dbx.files_upload_session_finish_batch(finish_args)
# Poll for completion if async
```

---

## Download

```python
# Download to memory
metadata, response = dbx.files_download('/remote/file.txt')
content = response.content  # bytes
text = response.text        # decoded string (for text files)

# Download to file
metadata, response = dbx.files_download('/remote/report.pdf')
with open('/local/report.pdf', 'wb') as f:
    f.write(response.content)

# Download to file (streaming, for large files)
dbx.files_download_to_file('/local/large_file.zip', '/remote/large_file.zip')

# Metadata fields on downloaded file
print(metadata.name)          # filename
print(metadata.path_display)  # full path
print(metadata.size)          # bytes
print(metadata.rev)           # revision hash
print(metadata.server_modified)  # datetime
print(metadata.client_modified)  # datetime
print(metadata.content_hash)  # content hash
```

---

## List Folder

```python
# List folder (first page)
result = dbx.files_list_folder(
    path='',                    # '' = root; '/folder' = subfolder
    recursive=False,            # True: list all descendants
    include_media_info=False,   # True: photo/video dimensions, GPS
    include_deleted=False,      # True: include recently deleted items
    include_has_explicit_shared_members=False,
    limit=100,                  # Max entries per page (max 2000)
)

for entry in result.entries:
    if isinstance(entry, dropbox.files.FolderMetadata):
        print(f"[DIR] {entry.path_display}")
    elif isinstance(entry, dropbox.files.FileMetadata):
        print(f"[FILE] {entry.path_display} ({entry.size} bytes)")
    elif isinstance(entry, dropbox.files.DeletedMetadata):
        print(f"[DEL] {entry.path_display}")

# Paginate
while result.has_more:
    result = dbx.files_list_folder_continue(result.cursor)
    for entry in result.entries:
        print(entry.path_display)
```

### List all files recursively

```python
def list_all(dbx, path: str = '') -> list:
    """Return all FileMetadata entries recursively."""
    files = []
    result = dbx.files_list_folder(path, recursive=True)

    while True:
        files.extend(e for e in result.entries
                     if isinstance(e, dropbox.files.FileMetadata))
        if not result.has_more:
            break
        result = dbx.files_list_folder_continue(result.cursor)

    return files
```

### Long-poll for changes (delta sync)

```python
# Get initial cursor
result = dbx.files_list_folder_get_latest_cursor(path='', recursive=True)
cursor = result.cursor

# Long-poll: blocks until there are changes (up to 30 seconds)
while True:
    poll_result = dbx.files_list_folder_longpoll(cursor, timeout=30)
    if poll_result.changes:
        result = dbx.files_list_folder_continue(cursor)
        for entry in result.entries:
            print(f"Changed: {entry.path_display}")
        cursor = result.cursor
```

---

## Get Metadata

```python
# File or folder metadata
meta = dbx.files_get_metadata(
    path='/remote/file.txt',
    include_media_info=False,
    include_deleted=False,
    include_has_explicit_shared_members=False,
)

# Type check
if isinstance(meta, dropbox.files.FileMetadata):
    print(f"File: {meta.name}, size={meta.size}, rev={meta.rev}")
elif isinstance(meta, dropbox.files.FolderMetadata):
    print(f"Folder: {meta.name}, id={meta.id}")
```

---

## Copy, Move, Delete

```python
# Copy
result = dbx.files_copy_v2(
    from_path='/source/file.txt',
    to_path='/dest/file.txt',
    allow_shared_folder=False,
    autorename=False,
    allow_ownership_transfer=False,
)
new_meta = result.metadata

# Move (also renames)
result = dbx.files_move_v2(
    from_path='/old/location/file.txt',
    to_path='/new/location/file.txt',
    allow_shared_folder=False,
    autorename=False,
    allow_ownership_transfer=False,
)

# Delete
result = dbx.files_delete_v2('/remote/file.txt')
# result.metadata is the deleted entry's metadata

# Create folder
meta = dbx.files_create_folder_v2('/new/folder/path', autorename=False)
```

---

## Search

```python
from dropbox.files import SearchOptions, FileCategory, SearchOrderBy

# Basic search
results = dbx.files_search_v2(
    query='invoice',
    options=SearchOptions(
        path='',                    # '' = entire Dropbox
        max_results=100,
        order_by=SearchOrderBy.relevance,
        file_status=dropbox.files.FileStatus.active,
        filename_only=False,        # True: search filename only, not content
        file_categories=[FileCategory.pdf, FileCategory.spreadsheet],  # Optional filter
    )
)

for match in results.matches:
    meta = match.metadata.get_metadata()
    print(f"{meta.path_display} ({type(meta).__name__})")

# Paginate
while results.has_more:
    results = dbx.files_search_continue_v2(results.cursor)
    for match in results.matches:
        print(match.metadata.get_metadata().path_display)
```

### File categories for filtering

`pdf`, `image`, `doc`, `spreadsheet`, `presentation`, `audio`, `video`, `folder`, `paper`, `others`

---

## Revisions

```python
# List revisions (up to 10 by default, max 100)
revisions = dbx.files_list_revisions(
    path='/remote/document.docx',
    mode=dropbox.files.ListRevisionsMode.path,
    limit=10,
)

for entry in revisions.entries:
    print(f"Rev: {entry.rev}, modified: {entry.server_modified}, size: {entry.size}")

# Restore a specific revision
dbx.files_restore(
    path='/remote/document.docx',
    rev='a1b2c3d4e5f6'  # Rev hash from list_revisions
)
```

---

## File Properties (Custom Metadata)

Attach custom key-value metadata to files:

```python
from dropbox.file_properties import PropertyGroup, PropertyField

# First create a template (one-time setup)
template = dbx.file_properties_templates_add_for_user(
    name='Document Metadata',
    description='Custom metadata for documents',
    fields=[
        dropbox.file_properties.PropertyFieldTemplate(
            name='Project',
            description='Project name',
            type=dropbox.file_properties.PropertyType.string
        ),
        dropbox.file_properties.PropertyFieldTemplate(
            name='Status',
            description='Document status',
            type=dropbox.file_properties.PropertyType.string
        ),
    ]
)
template_id = template.template_id

# Add properties to a file
dbx.file_properties_properties_add(
    path='/remote/document.docx',
    property_groups=[
        PropertyGroup(
            template_id=template_id,
            fields=[
                PropertyField(name='Project', value='Alpha'),
                PropertyField(name='Status', value='Draft'),
            ]
        )
    ]
)

# Search by property
results = dbx.file_properties_properties_search([
    dropbox.file_properties.PropertiesSearchQuery(
        queries=[
            dropbox.file_properties.PropertiesSearchCriterion(
                query='Alpha',
                mode=dropbox.file_properties.SearchMode.field_name('Project'),
                logical_operator=dropbox.file_properties.LogicalOperator.or_operator
            )
        ],
        template_filter=dropbox.file_properties.TemplateFilter.filter_some([template_id])
    )
])
```
