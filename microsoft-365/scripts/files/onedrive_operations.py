"""
OneDrive file operations via Microsoft Graph API.

Supports: list, upload (small and large), download, create folders,
share, move, copy, search, and delete.

Requirements:
    pip install msgraph-sdk azure-identity httpx python-dotenv

Permissions needed:
    - Delegated: Files.ReadWrite.All
    - Application: Files.ReadWrite.All
"""

import asyncio
import os
import math
from pathlib import Path
import httpx
from msgraph import GraphServiceClient
from msgraph.generated.models.drive_item import DriveItem
from msgraph.generated.models.folder import Folder
from msgraph.generated.models.item_reference import ItemReference
from msgraph.generated.users.item.drive.items.item.create_upload_session.create_upload_session_post_request_body import (
    CreateUploadSessionPostRequestBody,
)
from msgraph.generated.models.drive_item_uploadable_properties import (
    DriveItemUploadableProperties,
)
from msgraph.generated.users.item.drive.items.item.create_link.create_link_post_request_body import (
    CreateLinkPostRequestBody,
)
from msgraph.generated.users.item.drive.items.item.invite.invite_post_request_body import (
    InvitePostRequestBody,
)
from msgraph.generated.models.drive_recipient import DriveRecipient


SMALL_FILE_THRESHOLD = 4 * 1024 * 1024  # 4 MB


async def list_files(
    graph_client: GraphServiceClient,
    folder_path: str = None,
    folder_id: str = None,
) -> list:
    """
    List files and folders.

    Args:
        folder_path: OneDrive relative path (e.g., 'Documents/Reports')
                     None = root
        folder_id: Item ID of the folder (use instead of path if known)

    Returns:
        List of DriveItem objects
    """
    if folder_id:
        result = await graph_client.me.drive.items.by_drive_item_id(
            folder_id
        ).children.get()
    elif folder_path:
        result = await graph_client.me.drive.root.item_with_path(
            folder_path
        ).children.get()
    else:
        result = await graph_client.me.drive.root.children.get()

    return result.value or []


async def get_item(
    graph_client: GraphServiceClient,
    item_path: str = None,
    item_id: str = None,
) -> object:
    """
    Get a DriveItem by path or ID.

    Args:
        item_path: Relative path, e.g. 'Documents/report.xlsx'
        item_id: Item ID (more stable than path)
    """
    if item_id:
        return await graph_client.me.drive.items.by_drive_item_id(item_id).get()
    elif item_path:
        return await graph_client.me.drive.root.item_with_path(item_path).get()
    else:
        raise ValueError("Either item_path or item_id must be provided")


async def download_file(
    graph_client: GraphServiceClient,
    save_path: str,
    item_path: str = None,
    item_id: str = None,
) -> Path:
    """
    Download a file from OneDrive.

    Args:
        save_path: Local path to save the file
        item_path: OneDrive relative path
        item_id: Item ID

    Returns:
        Path to the downloaded file
    """
    item = await get_item(graph_client, item_path, item_id)
    download_url = item.additional_data.get("@microsoft.graph.downloadUrl")

    if not download_url:
        # Fallback: get content directly
        if item_id:
            content = await graph_client.me.drive.items.by_drive_item_id(
                item_id
            ).content.get()
        else:
            content = await graph_client.me.drive.root.item_with_path(
                item_path
            ).content.get()

        Path(save_path).write_bytes(content)
    else:
        async with httpx.AsyncClient() as client:
            response = await client.get(download_url, follow_redirects=True)
            response.raise_for_status()
            Path(save_path).write_bytes(response.content)

    print(f"Downloaded to: {save_path}")
    return Path(save_path)


async def upload_file(
    graph_client: GraphServiceClient,
    local_path: str,
    remote_folder_path: str = None,
    remote_folder_id: str = None,
    filename: str = None,
    conflict_behavior: str = "replace",
) -> object:
    """
    Upload a file to OneDrive. Automatically uses upload session for large files.

    Args:
        local_path: Path to local file
        remote_folder_path: Destination folder path (e.g., 'Documents')
        remote_folder_id: Destination folder item ID (alternative to path)
        filename: Override filename (defaults to local filename)
        conflict_behavior: 'replace', 'rename', or 'fail'

    Returns:
        Created DriveItem
    """
    file_path = Path(local_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {local_path}")

    filename = filename or file_path.name
    file_size = file_path.stat().st_size

    if file_size < SMALL_FILE_THRESHOLD:
        return await _upload_small_file(
            graph_client, file_path, filename, remote_folder_path, remote_folder_id, conflict_behavior
        )
    else:
        return await _upload_large_file(
            graph_client, file_path, filename, remote_folder_path, remote_folder_id, conflict_behavior
        )


async def _upload_small_file(
    graph_client, file_path, filename, folder_path, folder_id, conflict_behavior
):
    """Upload a file smaller than 4 MB using simple PUT."""
    content = file_path.read_bytes()

    if folder_id:
        remote_path = f"{folder_id}:/{filename}:"
        # Use item ID path for small upload
        item = await graph_client.me.drive.items.by_drive_item_id(
            f"{folder_id}:/{filename}:"
        ).content.put(content)
    elif folder_path:
        full_path = f"{folder_path.rstrip('/')}/{filename}"
        item = await graph_client.me.drive.root.item_with_path(full_path).content.put(content)
    else:
        item = await graph_client.me.drive.root.item_with_path(filename).content.put(content)

    print(f"Uploaded {filename} ({file_path.stat().st_size:,} bytes)")
    return item


async def _upload_large_file(
    graph_client, file_path, filename, folder_path, folder_id, conflict_behavior
):
    """Upload a large file using resumable upload session."""
    file_size = file_path.stat().st_size
    chunk_size = 4 * 1024 * 1024  # 4 MB chunks

    # Build remote path
    if folder_path:
        remote_path = f"{folder_path.rstrip('/')}/{filename}"
    else:
        remote_path = filename

    # Create upload session
    request_body = CreateUploadSessionPostRequestBody(
        item=DriveItemUploadableProperties(
            additional_data={"@microsoft.graph.conflictBehavior": conflict_behavior}
        )
    )
    session = await graph_client.me.drive.root.item_with_path(
        remote_path
    ).create_upload_session.post(request_body)

    upload_url = session.upload_url
    print(f"Uploading {filename} ({file_size:,} bytes) via session...")

    async with httpx.AsyncClient() as client:
        with open(file_path, "rb") as f:
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
                    print(f"Upload complete!")
                    return response.json()
                elif response.status_code == 202:
                    pct = int((end + 1) / file_size * 100)
                    print(f"Progress: {pct}% ({end + 1:,}/{file_size:,} bytes)")
                else:
                    response.raise_for_status()

                chunk_num += 1


async def create_folder(
    graph_client: GraphServiceClient,
    folder_name: str,
    parent_path: str = None,
    parent_id: str = None,
) -> object:
    """
    Create a folder in OneDrive.

    Args:
        folder_name: Name of the new folder
        parent_path: Path to parent folder (e.g., 'Documents')
        parent_id: Item ID of parent folder

    Returns:
        Created DriveItem
    """
    new_folder = DriveItem(
        name=folder_name,
        folder=Folder(),
        additional_data={"@microsoft.graph.conflictBehavior": "rename"},
    )

    if parent_id:
        created = await graph_client.me.drive.items.by_drive_item_id(
            parent_id
        ).children.post(new_folder)
    elif parent_path:
        item = await graph_client.me.drive.root.item_with_path(parent_path).get()
        created = await graph_client.me.drive.items.by_drive_item_id(
            item.id
        ).children.post(new_folder)
    else:
        created = await graph_client.me.drive.root.children.post(new_folder)

    print(f"Created folder: {folder_name} (ID: {created.id})")
    return created


async def create_share_link(
    graph_client: GraphServiceClient,
    item_id: str,
    link_type: str = "view",
    scope: str = "organization",
    expiration_days: int = None,
) -> str:
    """
    Create a sharing link for a file or folder.

    Args:
        item_id: Item ID to share
        link_type: 'view', 'edit', or 'embed'
        scope: 'anonymous' (anyone with link) or 'organization' (tenant only)
        expiration_days: Number of days until link expires (optional)

    Returns:
        Sharing URL
    """
    request_body = CreateLinkPostRequestBody(
        type=link_type,
        scope=scope,
    )

    if expiration_days:
        from datetime import datetime, timedelta, timezone
        expires = datetime.now(timezone.utc) + timedelta(days=expiration_days)
        request_body.expiration_date_time = expires

    result = await graph_client.me.drive.items.by_drive_item_id(
        item_id
    ).create_link.post(request_body)

    url = result.link.web_url
    print(f"Share link: {url}")
    return url


async def move_item(
    graph_client: GraphServiceClient,
    item_id: str,
    destination_folder_id: str,
    new_name: str = None,
) -> object:
    """Move a DriveItem to a different folder."""
    update = DriveItem(
        parent_reference=ItemReference(id=destination_folder_id),
    )
    if new_name:
        update.name = new_name

    return await graph_client.me.drive.items.by_drive_item_id(item_id).patch(update)


async def delete_item(
    graph_client: GraphServiceClient,
    item_id: str,
) -> None:
    """Delete a DriveItem (moves to recycle bin)."""
    await graph_client.me.drive.items.by_drive_item_id(item_id).delete()
    print(f"Deleted item: {item_id}")


async def search_files(
    graph_client: GraphServiceClient,
    query: str,
) -> list:
    """
    Search for files by name or content.

    Returns:
        List of matching DriveItem objects
    """
    results = await graph_client.me.drive.search_with_q(q=query).get()
    return results.value or []


# --- Example Usage ---
if __name__ == "__main__":
    from dotenv import load_dotenv
    from azure.identity import DeviceCodeCredential

    load_dotenv()

    async def main():
        credential = DeviceCodeCredential(
            tenant_id=os.environ.get("AZURE_TENANT_ID", "common"),
            client_id=os.environ["AZURE_CLIENT_ID"],
        )
        graph = GraphServiceClient(credential, ["Files.ReadWrite.All"])

        # List root files
        print("=== OneDrive Root ===")
        items = await list_files(graph)
        for item in items[:10]:
            kind = "DIR " if item.folder else "FILE"
            size = f"{item.size:,}" if item.size else "-"
            print(f"[{kind}] {item.name:<40} {size:>12} bytes  {item.id}")

        # Search for files
        print("\n=== Search: 'report' ===")
        results = await search_files(graph, "report")
        for item in results[:5]:
            print(f"  {item.name} - {item.web_url}")

        # Upload a file
        # item = await upload_file(graph, "local_file.txt", remote_folder_path="Documents")

        # Create a folder
        # folder = await create_folder(graph, "My New Folder", parent_path="Documents")

        # Get a share link
        # url = await create_share_link(graph, item_id="ITEM_ID", link_type="view", scope="organization")

    asyncio.run(main())
