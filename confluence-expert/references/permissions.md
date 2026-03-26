# Confluence Permissions & Restrictions Reference

## Permissions Architecture

Confluence has two levels of access control:

1. **Space permissions** — control what users/groups can do within a space (view, add, edit, delete, export, admin)
2. **Page-level restrictions** — optional fine-grained read/edit restrictions on individual pages

Space permissions are evaluated first; page restrictions can only further restrict access, never grant more access than space permissions allow.

---

## Space Permissions

### Permission Operations

| Operation key | Description |
|---|---|
| `read` | View space and its content |
| `create` | Create pages and blogposts |
| `delete` | Delete content |
| `export` | Export space content |
| `administer` | Manage space settings and permissions |
| `restrict_content` | Apply content-level restrictions |
| `create_attachment` | Upload attachments |
| `delete_own` | Delete own content only |
| `comment` | Add comments |

### Get Space Permissions (v1)

```bash
GET /rest/api/space/{spaceKey}?expand=permissions
```

Returns the space object with a `permissions` array listing all current grants.

### Get Space Permissions (v2)

```bash
GET /wiki/api/v2/spaces/{spaceId}/permissions?limit=50
```

Response:
```json
{
  "results": [
    {
      "id": "perm123",
      "operation": "read",
      "targetType": "GROUP",
      "targetId": "confluence-users"
    },
    {
      "id": "perm456",
      "operation": "create",
      "targetType": "USER",
      "targetId": "99:abc123-..."
    }
  ],
  "_links": { "next": "..." }
}
```

### Add Space Permission (v1)

```http
POST /rest/api/space/{spaceKey}/permission
{
  "subject": {
    "type": "user",
    "identifier": "99:abc123-..."
  },
  "operation": {
    "key": "create",
    "target": "page"
  }
}
```

```http
POST /rest/api/space/{spaceKey}/permission
{
  "subject": {
    "type": "group",
    "identifier": "engineering-team"
  },
  "operation": {
    "key": "read",
    "target": "space"
  }
}
```

### Add Space Permission (v2)

```http
POST /wiki/api/v2/spaces/{spaceId}/permissions
{
  "operation": "read",
  "targetType": "GROUP",
  "targetId": "engineering-team"
}
```

```http
POST /wiki/api/v2/spaces/{spaceId}/permissions
{
  "operation": "create",
  "targetType": "USER",
  "targetId": "99:abc123-..."
}
```

### Delete Space Permission (v2)

```bash
DELETE /wiki/api/v2/spaces/{spaceId}/permissions/{permissionId}
```

Returns 204 on success.

### Anonymous Access

To grant anonymous (unauthenticated) access to a space:

```http
POST /rest/api/space/{spaceKey}/permission
{
  "subject": {
    "type": "anonymous",
    "identifier": ""
  },
  "operation": {
    "key": "read",
    "target": "space"
  }
}
```

---

## Space Roles (v2 — Cloud Only, Role-Based Access Beta)

Space roles are a newer concept in Cloud that groups operations into named roles.

```bash
# List available roles
GET /wiki/api/v2/space-roles

# Get role assignments for a space
GET /wiki/api/v2/spaces/{spaceId}/role-assignments?limit=50

# Add a role assignment
POST /wiki/api/v2/spaces/{spaceId}/role-assignments
{
  "roleId": "viewer",
  "principal": {
    "type": "user",
    "id": "99:abc123..."
  }
}
```

---

## Page-Level Restrictions

Page restrictions limit access to specific pages beyond what space permissions allow. There are two restriction types:
- `read` — only listed users/groups can view the page
- `update` — only listed users/groups can edit the page

### Get Page Restrictions (v1)

```bash
# All restrictions
GET /rest/api/content/{pageId}/restriction?expand=restrictions.user,restrictions.group

# By operation type
GET /rest/api/content/{pageId}/restriction/byOperation/read
GET /rest/api/content/{pageId}/restriction/byOperation/update
```

Response:
```json
{
  "read": {
    "restrictions": {
      "user": {
        "results": [
          { "accountId": "99:abc123...", "displayName": "John Doe" }
        ]
      },
      "group": {
        "results": [
          { "type": "group", "name": "engineering-leads" }
        ]
      }
    }
  }
}
```

### Set Restrictions (Replaces All Existing)

```http
PUT /rest/api/content/{pageId}/restriction
[
  {
    "operation": "read",
    "restrictions": {
      "user": [
        { "type": "known", "accountId": "99:abc123..." }
      ],
      "group": [
        { "type": "group", "name": "engineering-leads" }
      ]
    }
  },
  {
    "operation": "update",
    "restrictions": {
      "user": [
        { "type": "known", "accountId": "99:abc123..." }
      ],
      "group": []
    }
  }
]
```

### Add a Single User to a Restriction

```http
PUT /rest/api/content/{pageId}/restriction/byOperation/read/byAccountId/{accountId}
```

Returns 200 on success (no body).

### Add a Group to a Restriction

```http
PUT /rest/api/content/{pageId}/restriction/byOperation/read/byGroupId/{groupId}
# or by group name:
PUT /rest/api/content/{pageId}/restriction/byOperation/read/group/{groupName}
```

### Remove a User from a Restriction

```bash
DELETE /rest/api/content/{pageId}/restriction/byOperation/read/byAccountId/{accountId}
```

### Remove All Restrictions (Open to Space Members)

```http
PUT /rest/api/content/{pageId}/restriction
[]
```

Sending an empty array removes all restrictions, making the page accessible to everyone with space access.

---

## User Lookup

### Find a User by Email or Name

```bash
# By email or display name (Cloud)
GET /rest/api/user/search?query=john.doe@example.com&limit=10
GET /rest/api/user/search?query=John Doe&limit=10
```

Response:
```json
{
  "results": [
    {
      "type": "known",
      "accountId": "99:abc123-...",
      "email": "john.doe@example.com",
      "publicName": "John Doe",
      "displayName": "John Doe",
      "profilePicture": { "path": "/aa-avatar/..." }
    }
  ]
}
```

### Get Current User

```bash
GET /rest/api/user/current
```

### Get User by accountId

```bash
GET /rest/api/user?accountId=99:abc123-...
```

### Get Groups a User Belongs To

```bash
GET /rest/api/user/memberof?accountId=99:abc123-...
```

---

## Group Management

### List All Groups

```bash
GET /rest/api/group?limit=50&start=0
```

Response:
```json
{
  "results": [
    {
      "type": "group",
      "name": "engineering-team",
      "id": "group-uuid-123"
    }
  ]
}
```

### Get Members of a Group

```bash
GET /rest/api/group/{groupName}/member?limit=50
GET /rest/api/group/by-id/{groupId}/member?limit=50
```

### Get Group by Name

```bash
GET /rest/api/group/by-name?name=engineering-team
```

### Add User to Group

```http
POST /rest/api/group/{groupName}/user?accountId={accountId}
```

Returns 200 with no body.

### Remove User from Group

```bash
DELETE /rest/api/group/{groupName}/user?accountId={accountId}
```

---

## Python: Resolve Email to accountId

```python
import requests

def get_account_id(domain, auth, email):
    r = requests.get(
        f"https://{domain}.atlassian.net/wiki/rest/api/user/search",
        auth=auth,
        params={"query": email, "limit": 5},
        headers={"Accept": "application/json"}
    )
    r.raise_for_status()
    results = r.json().get("results", [])
    for user in results:
        if user.get("email", "").lower() == email.lower():
            return user["accountId"]
    raise ValueError(f"No user found with email: {email}")
```

## Python: Set Page Read Restriction

```python
def restrict_page_to_group(domain, auth, page_id, group_name):
    """Restricts page reading to a single group."""
    payload = [
        {
            "operation": "read",
            "restrictions": {
                "user": [],
                "group": [{"type": "group", "name": group_name}]
            }
        }
    ]
    r = requests.put(
        f"https://{domain}.atlassian.net/wiki/rest/api/content/{page_id}/restriction",
        auth=auth,
        json=payload,
        headers={"Accept": "application/json", "Content-Type": "application/json"}
    )
    r.raise_for_status()
```

---

## Gotchas

- **Space permissions are evaluated before page restrictions** — a user without space read permission cannot access a page even if listed in its restrictions
- **Restrictions don't grant space access** — adding a user to a page restriction does NOT give them space access; you must grant space permission separately
- **PUT restrictions replaces all** — `PUT /restriction` with a partial list removes any existing restrictions not included; always include the full desired state
- **Group name vs group ID** — the v1 restrictions API accepts group name; the v2 permissions API uses group ID; resolve via `GET /group/by-name`
- **accountId, not username or email** — all user-targeting operations require the accountId (UUID format); look it up via user search first
- **Admin required for space permission changes** — only space admins (or Confluence admins) can modify space permissions; the API returns 403 otherwise
- **Data Center uses usernames** — on Data Center, restriction endpoints accept `username` instead of `accountId`
