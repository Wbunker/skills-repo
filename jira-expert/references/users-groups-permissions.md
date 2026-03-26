# Jira Users, Groups & Permissions Reference

## Users

### Key concept: accountId
All user references in Jira Cloud use `accountId` — a UUID-like string (e.g., `5b10a2844c20165700ede21g`), NOT usernames or email addresses. Display names and emails can change; accountId is stable.

| Operation | Method | Path |
|---|---|---|
| Get current user | GET | `/rest/api/3/myself` |
| Get user by accountId | GET | `/rest/api/3/user?accountId={id}` |
| Search users | GET | `/rest/api/3/user/search?query={email_or_name}` |
| Search assignable users | GET | `/rest/api/3/user/assignable/search?project={key}` |
| Search assignable for issue | GET | `/rest/api/3/user/assignable/search?issueKey={key}` |
| Get bulk users | GET | `/rest/api/3/user/bulk?accountId={id1}&accountId={id2}` |
| List all users | GET | `/rest/api/3/users/search` |
| Create user | POST | `/rest/api/3/user` |
| Update user | PUT | `/rest/api/3/user?accountId={id}` |
| Deactivate user | PUT | `/rest/api/3/user?accountId={id}` |
| Delete user | DELETE | `/rest/api/3/user?accountId={id}` |

### Resolve email to accountId
```
GET /rest/api/3/user/search?query=alice@example.com
```

Returns an array — use the first result's `accountId`.

```python
def get_account_id(jira, email):
    results = jira.get(f"/rest/api/3/user/search?query={email}").json()
    if results:
        return results[0]["accountId"]
    raise ValueError(f"User not found: {email}")
```

### Get current user
```
GET /rest/api/3/myself
```
Returns the authenticated user's full profile including `accountId`, `emailAddress`, `displayName`, `groups`.

### Search users assignable to a project
```
GET /rest/api/3/user/assignable/search?project=PROJ&query=alice
```

### Bulk user lookup
```
GET /rest/api/3/user/bulk?accountId=id1&accountId=id2&accountId=id3
```
More efficient than individual lookups when resolving many users.

---

## Groups

| Operation | Method | Path |
|---|---|---|
| Get group | GET | `/rest/api/3/group?groupname={name}` |
| Get group by ID | GET | `/rest/api/3/group?groupId={id}` |
| Create group | POST | `/rest/api/3/group` |
| Remove group | DELETE | `/rest/api/3/group?groupname={name}` |
| List groups | GET | `/rest/api/3/groups/picker?query={search}` |
| Get group members | GET | `/rest/api/3/group/member?groupname={name}` |
| Add user to group | POST | `/rest/api/3/group/user?groupname={name}` |
| Remove user from group | DELETE | `/rest/api/3/group/user?groupname={name}&accountId={id}` |

### List groups (search)
```
GET /rest/api/3/groups/picker?query=jira-dev&maxResults=50
```

### Get members of a group (paginated)
```
GET /rest/api/3/group/member?groupname=jira-developers&startAt=0&maxResults=50
```

### Add user to group
```http
POST /rest/api/3/group/user?groupname=jira-developers
{
  "accountId": "5b10a2844c20165700ede21g"
}
```

---

## Project Roles

Project roles define who has what access within a specific project (as opposed to global groups).

| Role | Typical access |
|---|---|
| Administrator | Manage project settings |
| Developer / Member | Create and edit issues |
| Viewer / Read-only | View issues only |
| Service Desk Team | JSM agent access |

### Get all project roles
```
GET /rest/api/3/project/PROJ/role
```

### Get members of a specific role
```
GET /rest/api/3/project/PROJ/role/{roleId}
```

Returns `actors` array with user accountIds and group names.

### Add user to project role
```http
POST /rest/api/3/project/PROJ/role/{roleId}
{
  "user": ["accountId1"],
  "group": ["jira-developers"]
}
```

### Remove user from project role
```
DELETE /rest/api/3/project/PROJ/role/{roleId}?user=accountId1
DELETE /rest/api/3/project/PROJ/role/{roleId}?group=jira-developers
```

---

## Permissions

### Check my permissions
```
GET /rest/api/3/mypermissions?projectKey=PROJ
GET /rest/api/3/mypermissions?issueKey=PROJ-123
```

Returns an object with permission names and `havePermission: true/false`.

### Get all permission schemes
```
GET /rest/api/3/permissionscheme
```

### Get a specific permission scheme
```
GET /rest/api/3/permissionscheme/{schemeId}?expand=permissions
```

### Common permission names
| Permission | Description |
|---|---|
| `BROWSE_PROJECTS` | View project and its issues |
| `CREATE_ISSUES` | Create new issues |
| `EDIT_ISSUES` | Edit existing issues |
| `ASSIGN_ISSUES` | Assign issues to users |
| `RESOLVE_ISSUES` | Transition to resolved |
| `DELETE_ISSUES` | Delete issues |
| `ADD_COMMENTS` | Add comments |
| `EDIT_ALL_COMMENTS` | Edit any comment |
| `DELETE_ALL_COMMENTS` | Delete any comment |
| `CREATE_ATTACHMENTS` | Attach files |
| `DELETE_ALL_ATTACHMENTS` | Delete any attachment |
| `WORK_ON_ISSUES` | Log work (worklogs) |
| `MANAGE_SPRINTS_PERMISSION` | Create/start/close sprints |
| `ADMINISTER_PROJECTS` | Manage project settings |
| `PROJECT_ADMIN` | Full project administration |

### Check if user has permission (admin use)
```
POST /rest/api/3/permissions/check
{
  "globalPermissions": ["ADMINISTER"],
  "projectPermissions": [
    {
      "permissions": ["BROWSE_PROJECTS", "CREATE_ISSUES"],
      "projects": [10000],
      "issues": [10001, 10002]
    }
  ]
}
```

---

## Global Permissions

```
GET /rest/api/3/permissions
```

Lists all global Jira permissions (ADMINISTER, USE, SYSTEM_ADMIN, etc.).

---

## User Properties (Custom Metadata)

Store per-user custom data visible to your integration:
```http
PUT /rest/api/3/user/properties/{propertyKey}?accountId={id}
{
  "onboardingComplete": true,
  "timezone": "America/Chicago"
}

GET /rest/api/3/user/properties/{propertyKey}?accountId={id}
DELETE /rest/api/3/user/properties/{propertyKey}?accountId={id}
```

---

## Common Patterns

### Find accountId from email, then assign issue
```python
# 1. Resolve email to accountId
users = jira.get("/rest/api/3/user/search?query=alice@example.com").json()
account_id = users[0]["accountId"]

# 2. Assign issue
jira.put(
    "/rest/api/3/issue/PROJ-123/assignee",
    json={"accountId": account_id}
)
```

### Check if current user is project admin
```python
perms = jira.get("/rest/api/3/mypermissions?projectKey=PROJ").json()
is_admin = perms["permissions"]["ADMINISTER_PROJECTS"]["havePermission"]
```

### List all members of a project role
```python
roles = jira.get("/rest/api/3/project/PROJ/role").json()
dev_role_url = roles.get("Developer") or roles.get("Member")
role_id = dev_role_url.split("/")[-1]

role_details = jira.get(f"/rest/api/3/project/PROJ/role/{role_id}").json()
for actor in role_details["actors"]:
    if actor["type"] == "atlassian-user-role-actor":
        print(f"User: {actor['displayName']} ({actor['actorUser']['accountId']})")
    elif actor["type"] == "atlassian-group-role-actor":
        print(f"Group: {actor['name']}")
```
