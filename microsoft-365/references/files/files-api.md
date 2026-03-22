# OneDrive and SharePoint Files API (Microsoft Graph)

Access files on OneDrive (personal and business) and SharePoint document libraries
via the Drive API in Microsoft Graph.

## Permissions

| Scenario | Delegated | Application |
|----------|-----------|-------------|
| Read user's own files | `Files.Read` | — |
| Read any accessible file | `Files.Read.All` | `Files.Read.All` |
| Read + write user's files | `Files.ReadWrite` | — |
| Read + write all files | `Files.ReadWrite.All` | `Files.ReadWrite.All` |
| SharePoint sites (read) | `Sites.Read.All` | `Sites.Read.All` |
| SharePoint sites (write) | `Sites.ReadWrite.All` | `Sites.ReadWrite.All` |

## Key Concepts

- **Drive**: A logical container of files (a user's OneDrive or a SharePoint document library)
- **DriveItem**: An item in a drive — file, folder, or shortcut
- **driveItem.id**: Unique ID within its drive (use for API calls)
- **SharePoint files**: Accessed via site drives — same Drive API, different root paths

## Drive Root Paths

```
/me/drive                              # Signed-in user's OneDrive
/me/drives                             # All drives accessible to the user
/users/{user-id}/drive                 # Another user's OneDrive (app-only)
/drives/{drive-id}                     # A specific drive by ID
/groups/{group-id}/drive               # A Microsoft 365 group's document library
/sites/{site-id}/drive                 # A SharePoint site's default document library
/sites/{site-id}/drives               # All document libraries in a SharePoint site
```

## List Files and Folders

```python
from msgraph import GraphServiceClient
from msgraph.generated.users.item.drive.root.children.children_request_builder import (
    ChildrenRequestBuilder,
)
from kiota_abstractions.base_request_configuration import RequestConfiguration

async def list_root_items(graph_client):
    """List files and folders in the root of the user's OneDrive."""
    query_params = ChildrenRequestBuilder.ChildrenRequestBuilderGetQueryParameters(
        select=["id", "name", "size", "lastModifiedDateTime", "file", "folder", "webUrl"],
    )
    config = RequestConfiguration(query_parameters=query_params)
    items = await graph_client.me.drive.root.children.get(request_configuration=config)
    return items.value

async def list_folder_contents(graph_client, folder_id):
    """List contents of a specific folder by item ID."""
    items = await graph_client.me.drive.items.by_drive_item_id(
        folder_id
    ).children.get()
    return items.value

async def list_by_path(graph_client, path):
    """List contents of a folder by path (e.g., 'Documents/Reports')."""
    items = await graph_client.me.drive.root.item_with_path(path).children.get()
    return items.value
```

## Get a File's Metadata

```python
# By item ID
item = await graph_client.me.drive.items.by_drive_item_id("ITEM_ID").get()

# By path
item = await graph_client.me.drive.root.item_with_path("Documents/report.xlsx").get()

# Properties available:
# item.id                          Unique item ID
# item.name                        File/folder name
# item.size                        Size in bytes
# item.web_url                     Browser-accessible URL
# item.last_modified_date_time     Last modified datetime
# item.created_date_time           Creation datetime
# item.created_by.user.display_name
# item.file.mime_type              MIME type (only on files, not folders)
# item.folder.child_count          Number of children (only on folders)
# item.download_url                Pre-authenticated download URL (@microsoft.graph.downloadUrl)
```

## Download a File

```python
import httpx

async def download_file(graph_client, item_id, save_path):
    # Method 1: Get download URL and download directly
    item = await graph_client.me.drive.items.by_drive_item_id(item_id).get()
    download_url = item.additional_data.get("@microsoft.graph.downloadUrl")

    async with httpx.AsyncClient() as client:
        response = await client.get(download_url, follow_redirects=True)
        with open(save_path, "wb") as f:
            f.write(response.content)

async def download_file_content(graph_client, item_id, save_path):
    # Method 2: Stream content directly via Graph SDK
    content = await graph_client.me.drive.items.by_drive_item_id(item_id).content.get()
    with open(save_path, "wb") as f:
        f.write(content)
```

## Upload a File (Simple — Under 4 MB)

```python
async def upload_file_simple(graph_client, local_path, remote_folder_path, filename=None):
    """
    Upload a small file (< 4 MB) to a specific folder path.
    remote_folder_path: OneDrive path like 'Documents/Reports'
    """
    filename = filename or local_path.split("/")[-1]
    with open(local_path, "rb") as f:
        content = f.read()

    item = await graph_client.me.drive.root.item_with_path(
        f"{remote_folder_path}/{filename}"
    ).content.put(content)
    return item
```

## Upload a Large File (Upload Session — Over 4 MB)

```python
from msgraph.generated.models.upload_session import UploadSession
from msgraph.generated.users.item.drive.items.item.create_upload_session.create_upload_session_post_request_body import (
    CreateUploadSessionPostRequestBody,
)
from msgraph.generated.models.drive_item_uploadable_properties import (
    DriveItemUploadableProperties,
)
import os, math, httpx

async def upload_large_file(graph_client, local_path, remote_path):
    """
    Upload a large file using resumable upload session.
    remote_path: full path like 'Documents/bigfile.zip'
    """
    file_size = os.path.getsize(local_path)
    filename = os.path.basename(local_path)

    # 1. Create upload session
    request_body = CreateUploadSessionPostRequestBody(
        item=DriveItemUploadableProperties(
            additional_data={"@microsoft.graph.conflictBehavior": "replace"}
        )
    )
    session = await graph_client.me.drive.root.item_with_path(remote_path).create_upload_session.post(
        request_body
    )
    upload_url = session.upload_url

    # 2. Upload in 4 MB chunks
    chunk_size = 4 * 1024 * 1024  # 4 MB
    async with httpx.AsyncClient() as client:
        with open(local_path, "rb") as f:
            chunk_num = 0
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                start = chunk_num * chunk_size
                end = start + len(chunk) - 1
                headers = {
                    "Content-Length": str(len(chunk)),
                    "Content-Range": f"bytes {start}-{end}/{file_size}",
                }
                response = await client.put(upload_url, content=chunk, headers=headers)
                if response.status_code in (200, 201):
                    return response.json()  # Upload complete
                chunk_num += 1
```

## Create a Folder

```python
from msgraph.generated.models.drive_item import DriveItem
from msgraph.generated.models.folder import Folder

async def create_folder(graph_client, parent_id, folder_name):
    new_folder = DriveItem(
        name=folder_name,
        folder=Folder(),
        additional_data={"@microsoft.graph.conflictBehavior": "rename"},
    )
    created = await graph_client.me.drive.items.by_drive_item_id(
        parent_id
    ).children.post(new_folder)
    return created
```

## Copy and Move Items

```python
from msgraph.generated.users.item.drive.items.item.copy.copy_post_request_body import (
    CopyPostRequestBody,
)
from msgraph.generated.models.item_reference import ItemReference

# Copy item to another folder
await graph_client.me.drive.items.by_drive_item_id(item_id).copy.post(
    CopyPostRequestBody(
        parent_reference=ItemReference(id="DESTINATION_FOLDER_ID"),
        name="Copy of file.docx",  # Optional new name
    )
)

# Move item (PATCH with new parent reference)
from msgraph.generated.models.drive_item import DriveItem

await graph_client.me.drive.items.by_drive_item_id(item_id).patch(
    DriveItem(
        parent_reference=ItemReference(id="DESTINATION_FOLDER_ID"),
        name="renamed-file.docx",  # Optional rename during move
    )
)
```

## Delete an Item

```python
await graph_client.me.drive.items.by_drive_item_id(item_id).delete()
# Deleted items go to recycle bin / deleted items, not permanently deleted
```

## Create a Sharing Link

```python
from msgraph.generated.users.item.drive.items.item.create_link.create_link_post_request_body import (
    CreateLinkPostRequestBody,
)

async def create_share_link(graph_client, item_id, link_type="view", scope="anonymous"):
    """
    link_type: 'view', 'edit', 'embed'
    scope: 'anonymous' (anyone with link), 'organization' (org only)
    """
    result = await graph_client.me.drive.items.by_drive_item_id(item_id).create_link.post(
        CreateLinkPostRequestBody(type=link_type, scope=scope)
    )
    return result.link.web_url
```

## Share with Specific Users (Invite)

```python
from msgraph.generated.users.item.drive.items.item.invite.invite_post_request_body import (
    InvitePostRequestBody,
)
from msgraph.generated.models.drive_recipient import DriveRecipient

result = await graph_client.me.drive.items.by_drive_item_id(item_id).invite.post(
    InvitePostRequestBody(
        recipients=[DriveRecipient(email="colleague@example.com")],
        roles=["read"],   # or ["write"]
        send_invitation=True,
        message="Sharing this with you.",
    )
)
```

## Search for Files

```python
from msgraph.generated.users.item.drive.search_with_q.search_with_q_request_builder import (
    SearchWithQRequestBuilder,
)

async def search_files(graph_client, query):
    results = await graph_client.me.drive.search_with_q(q=query).get()
    return results.value
    # Returns driveItem objects matching the query
```

## Access SharePoint Files

```python
# Get a SharePoint site by hostname and path
site = await graph_client.sites.by_site_id(
    "example.sharepoint.com:/sites/mysite:"
).get()

# List document libraries (drives) in the site
drives = await graph_client.sites.by_site_id(site.id).drives.get()

# Access files in a specific drive
items = await graph_client.sites.by_site_id(site.id).drives.by_drive_id(
    drives.value[0].id
).root.children.get()
```

## Conflict Behavior Options

When uploading or creating items, use `@microsoft.graph.conflictBehavior`:
- `"replace"`: Overwrite existing item
- `"rename"`: Auto-rename (e.g., `file (1).docx`)
- `"fail"`: Return an error if item exists (default)

## Track Changes (Delta)

For syncing, use delta queries instead of listing all files each time:

```python
# First sync: get all items + delta token
result = await graph_client.me.drive.root.delta.get()
items = result.value
delta_link = result.odata_delta_link  # Save this for next sync

# Subsequent syncs: only get changed items
result = await graph_client.me.drive.root.delta.with_url(delta_link).get()
changed_items = result.value  # Only items changed since last delta token
new_delta_link = result.odata_delta_link
```
