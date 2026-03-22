# Dropbox Sharing API Reference

## Table of Contents
1. [Shared Links](#shared-links)
2. [Link Settings (Password, Expiry, Visibility)](#link-settings)
3. [Download via Shared Link](#download-via-shared-link)
4. [File Sharing (Add Members)](#file-sharing)
5. [Folder Sharing](#folder-sharing)
6. [Shared Folder Members](#shared-folder-members)

---

## Shared Links

### Create a shared link

```python
import dropbox
from dropbox import sharing

dbx = dropbox.Dropbox('TOKEN')

# Simple: create link with default settings
link = dbx.sharing_create_shared_link_with_settings('/remote/file.pdf')
print(link.url)

# Force download URL (add ?dl=1 or replace www.dropbox.com → dl.dropboxusercontent.com)
download_url = link.url.replace('www.dropbox.com', 'dl.dropboxusercontent.com') \
                        .replace('?dl=0', '?dl=1')
```

### Get existing link (or create)

```python
try:
    link = dbx.sharing_create_shared_link_with_settings('/remote/file.pdf')
    url = link.url
except dropbox.exceptions.ApiError as e:
    # SharedLinkAlreadyExistsError — fetch existing
    if e.error.is_shared_link_already_exists():
        result = dbx.sharing_list_shared_links(
            path='/remote/file.pdf', direct_only=True
        )
        url = result.links[0].url
    else:
        raise
```

### List shared links

```python
# Links for a specific path
result = dbx.sharing_list_shared_links(
    path='/remote/folder',
    direct_only=False,     # True: only links for this exact path
)
for link in result.links:
    print(f"{link.url} - {link.link_permissions}")

# All links (no path filter)
result = dbx.sharing_list_shared_links()
while True:
    for link in result.links:
        print(link.url)
    if not result.has_more:
        break
    result = dbx.sharing_list_shared_links(cursor=result.cursor)
```

### Revoke a shared link

```python
dbx.sharing_revoke_shared_link(url='https://www.dropbox.com/s/abc123/file.pdf?dl=0')
```

---

## Link Settings

```python
from dropbox.sharing import (
    SharedLinkSettings, RequestedVisibility, LinkAudience,
    LinkPermissions, AlphaResolvedVisibility
)

# Link with password and expiry
settings = SharedLinkSettings(
    requested_visibility=RequestedVisibility.password,
    link_password='my-secret-password',
    expires=datetime(2025, 12, 31, 23, 59, 59),  # UTC datetime
)

link = dbx.sharing_create_shared_link_with_settings(
    '/remote/file.pdf',
    settings=settings
)

# Visibility options
# RequestedVisibility.public      - Anyone with link
# RequestedVisibility.team_only   - Team members only (Business)
# RequestedVisibility.password    - Password protected
```

### Update link settings

```python
dbx.sharing_modify_shared_link_settings(
    url=existing_link_url,
    settings=SharedLinkSettings(
        requested_visibility=RequestedVisibility.public,
        expires=datetime(2026, 6, 30),
    ),
    remove_expiration=False,   # True: remove expiration date
)
```

---

## Download via Shared Link

```python
# Download a file via its shared link
metadata, response = dbx.sharing_get_shared_link_file(
    url='https://www.dropbox.com/s/abc123/file.pdf?dl=0',
    path=None,       # Path within linked folder (if link is a folder)
)
with open('downloaded.pdf', 'wb') as f:
    f.write(response.content)

# Get metadata for a shared link (without downloading)
meta = dbx.sharing_get_shared_link_metadata(
    url='https://www.dropbox.com/s/abc123/file.pdf?dl=0'
)
print(f"Name: {meta.name}, Link type: {type(meta).__name__}")
```

---

## File Sharing

Share a file directly with specific users (they can access via their Dropbox):

```python
from dropbox.sharing import MemberSelector, AccessLevel

# Add members to a file
result = dbx.sharing_add_file_member(
    file='/remote/file.pdf',     # Path or shared file ID
    members=[
        dropbox.sharing.MemberSelector.dropbox_id('dbid:AAAbcdef...'),
        dropbox.sharing.MemberSelector.email('user@example.com'),
    ],
    access_level=dropbox.sharing.AccessLevel.viewer,  # .viewer | .editor | .owner
    quiet=False,                  # True: suppress email notification
    add_message_if_pending_exists=True,
)

# List file members
members = dbx.sharing_list_file_members('/remote/file.pdf')
for member in members.users:
    print(f"{member.user.email}: {member.access_type}")

# Remove a file member
dbx.sharing_remove_file_member_2(
    file='/remote/file.pdf',
    member=dropbox.sharing.MemberSelector.email('user@example.com'),
)
```

---

## Folder Sharing

```python
# Share a folder
result = dbx.sharing_share_folder(
    path='/remote/folder',
    member_policy=dropbox.sharing.MemberPolicy.team,  # .team | .anyone
    acl_update_policy=dropbox.sharing.AclUpdatePolicy.owner,  # Who can update membership
    shared_link_policy=dropbox.sharing.SharedLinkPolicy.anyone,
    force_async=False,
)

# If async (large folder), poll for completion
if isinstance(result, dropbox.sharing.ShareFolderLaunch):
    if result.is_async_job_id():
        job_id = result.get_async_job_id()
        while True:
            import time
            status = dbx.sharing_share_folder_check_job_status(job_id)
            if status.is_complete():
                shared_folder_id = status.get_complete().shared_folder_id
                break
            elif status.is_failed():
                raise Exception(f"Share folder failed: {status.get_failed()}")
            time.sleep(1)
    else:
        shared_folder_id = result.get_complete().shared_folder_id
```

---

## Shared Folder Members

```python
# List shared folder members
result = dbx.sharing_list_folder_members(shared_folder_id)
for member in result.users:
    print(f"{member.user.email}: {member.access_type}")

while result.cursor:
    result = dbx.sharing_list_folder_members_continue(result.cursor)
    for member in result.users:
        print(f"{member.user.email}: {member.access_type}")

# Add members to shared folder
dbx.sharing_add_folder_member(
    shared_folder_id=shared_folder_id,
    members=[
        dropbox.sharing.AddMember(
            member=dropbox.sharing.MemberSelector.email('user@example.com'),
            access_level=dropbox.sharing.AccessLevel.editor,
        )
    ],
    quiet=False,
    custom_message='Sharing the project folder with you.',
)

# Update member access level
dbx.sharing_update_folder_member(
    shared_folder_id=shared_folder_id,
    member=dropbox.sharing.MemberSelector.email('user@example.com'),
    access_level=dropbox.sharing.AccessLevel.viewer,
)

# Remove a member
dbx.sharing_remove_folder_member(
    shared_folder_id=shared_folder_id,
    member=dropbox.sharing.MemberSelector.email('user@example.com'),
    leave_a_copy=False,  # True: leave them a copy of the folder contents
)

# Update folder sharing policy
dbx.sharing_update_folder_policy(
    shared_folder_id=shared_folder_id,
    member_policy=dropbox.sharing.MemberPolicy.team,
    acl_update_policy=dropbox.sharing.AclUpdatePolicy.editors,
    shared_link_policy=dropbox.sharing.SharedLinkPolicy.members,
)

# Get folder metadata
meta = dbx.sharing_get_folder_metadata(shared_folder_id)
print(f"Folder: {meta.name}, policy: {meta.policy.member_policy}")
```

### Access levels

| Level | Capability |
|-------|-----------|
| `AccessLevel.viewer` | View and download only |
| `AccessLevel.viewer_no_comment` | View only, no comments |
| `AccessLevel.editor` | View, download, edit, upload |
| `AccessLevel.owner` | Full control including membership |
