# Jira Issues Reference

## Issue Endpoints Overview

| Operation | Method | Path |
|---|---|---|
| Get issue | GET | `/rest/api/3/issue/{issueIdOrKey}` |
| Create issue | POST | `/rest/api/3/issue` |
| Update issue | PUT | `/rest/api/3/issue/{issueIdOrKey}` |
| Delete issue | DELETE | `/rest/api/3/issue/{issueIdOrKey}` |
| Bulk create | POST | `/rest/api/3/issue/bulk` |
| Get create metadata | GET | `/rest/api/3/issue/createmeta` |
| Get edit metadata | GET | `/rest/api/3/issue/{key}/editmeta` |
| Get transitions | GET | `/rest/api/3/issue/{key}/transitions` |
| Transition issue | POST | `/rest/api/3/issue/{key}/transitions` |
| Get comments | GET | `/rest/api/3/issue/{key}/comment` |
| Add comment | POST | `/rest/api/3/issue/{key}/comment` |
| Update comment | PUT | `/rest/api/3/issue/{key}/comment/{id}` |
| Delete comment | DELETE | `/rest/api/3/issue/{key}/comment/{id}` |
| Get attachments | GET | `/rest/api/3/issue/{key}?fields=attachment` |
| Add attachment | POST | `/rest/api/3/issue/{key}/attachments` |
| Get worklogs | GET | `/rest/api/3/issue/{key}/worklog` |
| Add worklog | POST | `/rest/api/3/issue/{key}/worklog` |
| Get issue links | GET | (included in issue response) |
| Link issues | POST | `/rest/api/3/issueLink` |
| Assign issue | PUT | `/rest/api/3/issue/{key}/assignee` |
| Get watchers | GET | `/rest/api/3/issue/{key}/watchers` |
| Add watcher | POST | `/rest/api/3/issue/{key}/watchers` |

---

## Atlassian Document Format (ADF)

All rich-text fields (description, comment body, etc.) in API v3 use ADF — **not plain text or Markdown**.

### Minimal ADF paragraph
```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [
        { "type": "text", "text": "Your text here." }
      ]
    }
  ]
}
```

### ADF with formatting
```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "heading",
      "attrs": { "level": 2 },
      "content": [{ "type": "text", "text": "Steps to Reproduce" }]
    },
    {
      "type": "bulletList",
      "content": [
        {
          "type": "listItem",
          "content": [{
            "type": "paragraph",
            "content": [{ "type": "text", "text": "Step 1" }]
          }]
        }
      ]
    },
    {
      "type": "codeBlock",
      "attrs": { "language": "python" },
      "content": [{ "type": "text", "text": "print('hello')" }]
    }
  ]
}
```

> **Tip:** If you only need plain text, use `v2` API — description returns/accepts HTML strings. For v3, always wrap in ADF.

---

## Create Issue

```http
POST /rest/api/3/issue
Content-Type: application/json

{
  "fields": {
    "project":     { "key": "PROJ" },
    "summary":     "Login fails on Safari 17",
    "issuetype":   { "name": "Bug" },
    "priority":    { "name": "High" },
    "assignee":    { "accountId": "5b10a2844c20165700ede21g" },
    "reporter":    { "accountId": "5b10a2844c20165700ede21g" },
    "labels":      ["frontend", "auth"],
    "components":  [{ "name": "Login" }],
    "fixVersions": [{ "name": "2.4.0" }],
    "duedate":     "2026-04-15",
    "description": {
      "type": "doc", "version": 1,
      "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "Describe bug here" }] }]
    },
    "customfield_10016": "EPIC-42"
  }
}
```

**Response 201:**
```json
{ "id": "10001", "key": "PROJ-42", "self": "https://your-domain.atlassian.net/rest/api/3/issue/10001" }
```

### Getting valid field values before creating

Use the create metadata endpoint to discover valid issue types, fields, and their allowed values for a project:
```
GET /rest/api/3/issue/createmeta?projectKeys=PROJ&expand=projects.issuetypes.fields
```

Custom field IDs look like `customfield_10016` — use the metadata endpoint to map them to display names.

---

## Bulk Create (up to 50 issues)

```http
POST /rest/api/3/issue/bulk
{
  "issueUpdates": [
    { "fields": { "project": { "key": "PROJ" }, "summary": "Bug 1", "issuetype": { "name": "Bug" } } },
    { "fields": { "project": { "key": "PROJ" }, "summary": "Bug 2", "issuetype": { "name": "Bug" } } }
  ]
}
```

Response includes an array of created issues and a separate array of any errors.

---

## Update Issue

Use `update` for field operations (add/remove/set); use `fields` for direct field replacement.

```http
PUT /rest/api/3/issue/PROJ-123
{
  "fields": {
    "summary": "Updated summary",
    "priority": { "name": "Medium" }
  },
  "update": {
    "labels": [
      { "add": "regression" },
      { "remove": "frontend" }
    ],
    "comment": [
      { "add": { "body": { "type": "doc", "version": 1, "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "Auto-updating via API" }] }] } } }
    ]
  }
}
```

Returns `204 No Content` on success.

---

## Transitions (Workflow State Changes)

### Step 1: Get available transitions
```
GET /rest/api/3/issue/PROJ-123/transitions
```
```json
{
  "transitions": [
    { "id": "11", "name": "To Do" },
    { "id": "21", "name": "In Progress" },
    { "id": "31", "name": "Done" }
  ]
}
```

Transition IDs are workflow-specific — always fetch them dynamically; don't hardcode.

### Step 2: Perform transition
```http
POST /rest/api/3/issue/PROJ-123/transitions
{
  "transition": { "id": "31" },
  "fields": {
    "resolution": { "name": "Fixed" }
  },
  "update": {
    "comment": [
      { "add": { "body": { "type": "doc", "version": 1, "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "Marking as done." }] }] } } }
    ]
  }
}
```

Returns `204 No Content` on success.

### Transition to a specific status by name (Python helper)
```python
def transition_to(jira_client, issue_key, target_status):
    transitions = jira_client.get(f"/rest/api/3/issue/{issue_key}/transitions").json()
    for t in transitions["transitions"]:
        if t["name"].lower() == target_status.lower():
            jira_client.post(
                f"/rest/api/3/issue/{issue_key}/transitions",
                json={"transition": {"id": t["id"]}}
            )
            return
    raise ValueError(f"No transition to '{target_status}' found")
```

---

## Comments

### Get comments (paginated)
```
GET /rest/api/3/issue/PROJ-123/comment?startAt=0&maxResults=50&orderBy=created
```

### Add comment
```http
POST /rest/api/3/issue/PROJ-123/comment
{
  "body": {
    "type": "doc", "version": 1,
    "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "Comment text." }] }]
  },
  "visibility": {
    "type": "role",
    "value": "Service Desk Team"
  }
}
```

The optional `visibility` field restricts comment to a role or group.

### Update comment
```http
PUT /rest/api/3/issue/PROJ-123/comment/10001
{
  "body": { "type": "doc", "version": 1, "content": [...] }
}
```

---

## Attachments

### Upload attachment
```bash
curl -X POST \
  -H "Authorization: Basic ..." \
  -H "X-Atlassian-Token: no-check" \
  -F "file=@/path/to/screenshot.png" \
  "https://your-domain.atlassian.net/rest/api/3/issue/PROJ-123/attachments"
```

> **Important:** Attachments require the `X-Atlassian-Token: no-check` header to bypass XSRF protection. Do NOT set `Content-Type` — let curl set it automatically for multipart.

```python
import requests

files = {"file": ("screenshot.png", open("screenshot.png", "rb"), "image/png")}
r = requests.post(
    f"{JIRA_BASE}/issue/PROJ-123/attachments",
    auth=AUTH,
    headers={"X-Atlassian-Token": "no-check"},
    files=files
)
```

Response is an array of attachment objects with `id`, `filename`, `content` (download URL), `size`.

---

## Worklogs (Time Tracking)

### Add worklog
```http
POST /rest/api/3/issue/PROJ-123/worklog
{
  "timeSpent": "3h 30m",
  "started": "2026-03-25T09:00:00.000+0000",
  "comment": {
    "type": "doc", "version": 1,
    "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "Debugging session." }] }]
  }
}
```

`timeSpent` formats: `1h`, `30m`, `1h 30m`, `1d` (1d = 8h by default, configurable).
`started` must be ISO 8601 with milliseconds and timezone.

### Get worklogs
```
GET /rest/api/3/issue/PROJ-123/worklog
```

---

## Issue Links

### Get link types
```
GET /rest/api/3/issueLinkType
```
Returns types like: "Blocks", "Clones", "Duplicate", "Relates".

### Create link
```http
POST /rest/api/3/issueLink
{
  "type": { "name": "Blocks" },
  "inwardIssue": { "key": "PROJ-123" },
  "outwardIssue": { "key": "PROJ-124" }
}
```

Link direction matters: for "Blocks", `inwardIssue` is the blocker.

---

## Assign Issue

```http
PUT /rest/api/3/issue/PROJ-123/assignee
{ "accountId": "5b10a2844c20165700ede21g" }
```

To unassign: `{ "accountId": null }`

---

## Delete Issue

```
DELETE /rest/api/3/issue/PROJ-123
```

Add `?deleteSubtasks=true` to also delete subtasks (required if issue has them).

Returns `204 No Content`.

---

## Getting Field Metadata

To discover custom field IDs and valid values for a project:
```
GET /rest/api/3/issue/createmeta?projectKeys=PROJ&expand=projects.issuetypes.fields
```

To see editable fields on an existing issue:
```
GET /rest/api/3/issue/PROJ-123/editmeta
```

Custom fields appear as `customfield_XXXXX`. Map display names to IDs using the metadata endpoints.
