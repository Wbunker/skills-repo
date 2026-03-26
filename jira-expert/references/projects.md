# Jira Projects Reference

## Project Endpoints

| Operation | Method | Path |
|---|---|---|
| List all projects | GET | `/rest/api/3/project/search` |
| Get project | GET | `/rest/api/3/project/{projectIdOrKey}` |
| Create project | POST | `/rest/api/3/project` |
| Update project | PUT | `/rest/api/3/project/{projectIdOrKey}` |
| Delete project | DELETE | `/rest/api/3/project/{projectIdOrKey}` |
| Get project types | GET | `/rest/api/3/project/type` |
| Validate project key | GET | `/rest/api/3/projectvalidate/key?key=PROJ` |
| Get components | GET | `/rest/api/3/project/{key}/components` |
| Create component | POST | `/rest/api/3/component` |
| Update component | PUT | `/rest/api/3/component/{id}` |
| Delete component | DELETE | `/rest/api/3/component/{id}` |
| Get versions | GET | `/rest/api/3/project/{key}/versions` |
| Get versions (paginated) | GET | `/rest/api/3/project/{key}/version` |
| Create version | POST | `/rest/api/3/version` |
| Update version | PUT | `/rest/api/3/version/{id}` |
| Release version | PUT | `/rest/api/3/version/{id}` |
| Delete version | DELETE | `/rest/api/3/version/{id}` |
| Get project roles | GET | `/rest/api/3/project/{key}/role` |
| Get role actors | GET | `/rest/api/3/project/{key}/role/{roleId}` |
| Add role actors | POST | `/rest/api/3/project/{key}/role/{roleId}` |
| Remove role actor | DELETE | `/rest/api/3/project/{key}/role/{roleId}` |
| Get project features | GET | `/rest/api/3/project/{key}/features` |
| Set project feature | PUT | `/rest/api/3/project/{key}/features/{featureKey}` |
| Get project properties | GET | `/rest/api/3/project/{key}/properties` |
| Set project property | PUT | `/rest/api/3/project/{key}/properties/{propertyKey}` |

---

## Project Types

Jira Cloud has three project template styles:

| Type | `projectTypeKey` | Description |
|---|---|---|
| Software (Scrum) | `software` | Scrum boards, sprints, backlogs |
| Software (Kanban) | `software` | Kanban boards |
| Business (Team-managed) | `business` | Simple task management |
| Service Management | `service_desk` | Jira Service Management (JSM) |

Project templates are separate from types — use `GET /rest/api/3/project/type` for available types and `GET /rest/api/3/project/template` for templates.

---

## List Projects

```
GET /rest/api/3/project/search?query=PROJ&maxResults=50&startAt=0
```

Query params:
- `query` — filter by name or key
- `typeKey` — filter by `software`, `business`, `service_desk`
- `status` — `live`, `archived`, `deleted`
- `expand` — `description`, `projectKeys`, `lead`, `issueTypes`, `url`
- `properties` — filter by project properties
- `orderBy` — `name`, `key`, `lastIssueUpdatedTime`

Response:
```json
{
  "total": 15,
  "startAt": 0,
  "maxResults": 50,
  "isLast": true,
  "values": [
    { "id": "10000", "key": "PROJ", "name": "My Project", "projectTypeKey": "software" }
  ]
}
```

---

## Get Single Project

```
GET /rest/api/3/project/PROJ?expand=description,lead,issueTypes,url,projectKeys
```

Returns: `id`, `key`, `name`, `description`, `lead`, `components`, `versions`, `issueTypes`, `roles`, `avatarUrls`.

---

## Create Project

```http
POST /rest/api/3/project
{
  "key": "NEWP",
  "name": "New Project",
  "description": "Optional description",
  "projectTypeKey": "software",
  "projectTemplateKey": "com.pyxis.greenhopper.jira:gh-scrum-template",
  "leadAccountId": "5b10a2844c20165700ede21g",
  "assigneeType": "UNASSIGNED",
  "avatarId": 10200,
  "issueSecurityScheme": 10000,
  "permissionScheme": 10000,
  "notificationScheme": 10000
}
```

**Common template keys:**
- Scrum: `com.pyxis.greenhopper.jira:gh-scrum-template`
- Kanban: `com.pyxis.greenhopper.jira:gh-kanban-template`
- Business: `com.atlassian.jira-core-project-templates:jira-core-simplified-task-tracking`

**Response 201:** Returns project object with `id`, `key`, `self`.

---

## Components

Components are sub-sections of a project for categorizing issues.

### Create component
```http
POST /rest/api/3/component
{
  "project": "PROJ",
  "name": "Frontend",
  "description": "UI and client-side code",
  "leadAccountId": "5b10a2844c20165700ede21g",
  "assigneeType": "PROJECT_LEAD"
}
```

`assigneeType` options: `UNASSIGNED`, `PROJECT_LEAD`, `COMPONENT_LEAD`, `PROJECT_DEFAULT`

### List components
```
GET /rest/api/3/project/PROJ/components
```

---

## Versions (Fix Versions / Releases)

Versions represent planned releases used in `fixVersions` and `affectedVersions` fields.

### Create version
```http
POST /rest/api/3/version
{
  "project": "PROJ",
  "name": "2.4.0",
  "description": "Q2 release",
  "startDate": "2026-04-01",
  "releaseDate": "2026-06-30",
  "released": false,
  "archived": false
}
```

### Release a version
```http
PUT /rest/api/3/version/{versionId}
{
  "released": true,
  "releaseDate": "2026-06-28"
}
```

### Get unresolved issue count for version
```
GET /rest/api/3/version/{versionId}/unresolvedIssueCount
```

### Move unresolved issues to another version
```http
POST /rest/api/3/version/{versionId}/removeAndSwap
{
  "moveAffectedIssuesTo": "anotherVersionId",
  "moveFixIssuesTo": "anotherVersionId"
}
```

---

## Project Roles

Roles define permission sets within a project (e.g., Administrator, Developer, Viewer).

### List roles in a project
```
GET /rest/api/3/project/PROJ/role
```
Returns a map of role names to their self URLs.

### Get actors in a role
```
GET /rest/api/3/project/PROJ/role/{roleId}
```
Returns users and groups assigned to the role.

### Add members to a role
```http
POST /rest/api/3/project/PROJ/role/{roleId}
{
  "user": ["accountId1", "accountId2"],
  "group": ["jira-developers"]
}
```

### Remove a member from a role
```
DELETE /rest/api/3/project/PROJ/role/{roleId}?user=accountId1
DELETE /rest/api/3/project/PROJ/role/{roleId}?groupId=jira-developers
```

---

## Project Features

Toggle project features (like sprints, roadmap, releases):

```
GET /rest/api/3/project/PROJ/features
```

```http
PUT /rest/api/3/project/PROJ/features/{featureKey}
{ "state": "ENABLED" }
```

Common feature keys: `jsw.agility.backlog`, `jsw.agility.board`, `jsw.classic.releases`, `jsw.agility.roadmap`

---

## Project Properties (Custom Metadata)

Store arbitrary key-value data on a project for use by integrations:

```http
PUT /rest/api/3/project/PROJ/properties/my-integration-config
{
  "enabled": true,
  "webhook_url": "https://example.com/hook"
}
```

```
GET /rest/api/3/project/PROJ/properties/my-integration-config
DELETE /rest/api/3/project/PROJ/properties/my-integration-config
```

---

## Archive / Restore / Delete

```
POST /rest/api/3/project/PROJ/archive   # soft archive
POST /rest/api/3/project/PROJ/restore   # restore from archive
DELETE /rest/api/3/project/PROJ         # permanent delete
```

Archived projects hide from most views but retain all data. Delete is irreversible.
