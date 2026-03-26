# Confluence Spaces Reference

## Space Concepts

A **space** is the top-level container in Confluence. All pages, blogposts, and attachments live inside a space.

| Space Type | Description |
|---|---|
| `global` | Team/project spaces visible to all members |
| `personal` | Created automatically for each user; key is `~accountId` |
| `archived` | Preserved but hidden from main navigation |

Space **key** is a short uppercase identifier (e.g., `ENG`, `DOCS`, `~user123`). Space **ID** is a numeric ID used in v2 endpoints.

---

## v1 Space Endpoints

Base: `https://{domain}.atlassian.net/wiki/rest/api/space`

### List all spaces

```bash
GET /rest/api/space?limit=50&start=0
GET /rest/api/space?type=global&limit=50
GET /rest/api/space?spaceKey=ENG,DOCS   # filter by keys
GET /rest/api/space?expand=description.plain,homepage,metadata.labels
```

**Response:**
```json
{
  "results": [
    {
      "id": 98765,
      "key": "ENG",
      "name": "Engineering",
      "type": "global",
      "_links": {
        "webui": "/spaces/ENG",
        "self": "https://domain.atlassian.net/wiki/rest/api/space/ENG"
      }
    }
  ],
  "start": 0,
  "limit": 50,
  "size": 12
}
```

### Get a single space

```bash
GET /rest/api/space/ENG
GET /rest/api/space/ENG?expand=description.plain,homepage,metadata.labels,permissions
```

### Create a space

```http
POST /rest/api/space
{
  "key": "MYSPACE",
  "name": "My New Space",
  "description": {
    "plain": {
      "value": "A space for my team.",
      "representation": "plain"
    }
  }
}
```

### Create a personal space

```http
POST /rest/api/space/_private
{
  "key": "~userAccountId",
  "name": "My Personal Space"
}
```

### Update a space

```http
PUT /rest/api/space/ENG
{
  "name": "Engineering Team",
  "description": {
    "plain": {
      "value": "Updated description.",
      "representation": "plain"
    }
  },
  "homepage": { "id": "12345678" }
}
```

### Delete a space

```bash
DELETE /rest/api/space/ENG
```

Returns a long-running task; poll `GET /rest/api/longtask/{taskId}` to check completion.

### List content in a space

```bash
# All content
GET /rest/api/space/ENG/content?limit=25

# Pages only
GET /rest/api/space/ENG/content/page?limit=50&depth=all

# Blogposts only
GET /rest/api/space/ENG/content/blogpost?limit=50

# Root-level pages only (no depth param or depth=root)
GET /rest/api/space/ENG/content/page?depth=root&limit=50
```

---

## v2 Space Endpoints

Base: `https://{domain}.atlassian.net/wiki/api/v2/spaces`

### List spaces

```bash
GET /wiki/api/v2/spaces?limit=50
GET /wiki/api/v2/spaces?keys=ENG,DOCS
GET /wiki/api/v2/spaces?type=global&sort=name
```

**Response:**
```json
{
  "results": [
    {
      "id": "98765",
      "key": "ENG",
      "name": "Engineering",
      "type": "global",
      "status": "current",
      "homepageId": "12345678",
      "_links": { "webui": "/spaces/ENG" }
    }
  ],
  "_links": { "next": "/wiki/api/v2/spaces?cursor=abc123" }
}
```

### Get a space by ID

```bash
GET /wiki/api/v2/spaces/98765
```

### Get space by key (resolve key → ID)

```bash
GET /wiki/api/v2/spaces?keys=ENG&limit=1
# Extract the id from the first result
```

### Get pages in a space (v2)

```bash
GET /wiki/api/v2/pages?spaceId=98765&limit=50
GET /wiki/api/v2/pages?spaceId=98765&status=current&sort=title
```

---

## Space Permissions Overview

Space-level permissions control who can view, add, edit, and admin content within a space.

Read `references/permissions.md` for full details on managing space permissions via the API.

Key permission types:
- `read` — view space content
- `write` — create/edit pages and blogposts
- `export` — export space content
- `administer` — manage space settings and permissions

---

## Space Properties (Custom Metadata)

You can store arbitrary key/value properties on a space:

```bash
GET /rest/api/space/ENG/property
POST /rest/api/space/ENG/property
PUT /rest/api/space/ENG/property/{key}
DELETE /rest/api/space/ENG/property/{key}
```

```http
POST /rest/api/space/ENG/property
{
  "key": "team-slack-channel",
  "value": "#engineering"
}
```

---

## Common Patterns

### Find a space ID from its key (for v2 API)

```python
import requests

def get_space_id(domain, auth, space_key):
    r = requests.get(
        f"https://{domain}.atlassian.net/wiki/api/v2/spaces",
        auth=auth,
        params={"keys": space_key, "limit": 1},
        headers={"Accept": "application/json"}
    )
    r.raise_for_status()
    results = r.json()["results"]
    if not results:
        raise ValueError(f"Space '{space_key}' not found")
    return results[0]["id"]
```

### List all global spaces with pagination

```python
def get_all_spaces(domain, auth):
    spaces = []
    start = 0
    limit = 50
    while True:
        r = requests.get(
            f"https://{domain}.atlassian.net/wiki/rest/api/space",
            auth=auth,
            params={"type": "global", "start": start, "limit": limit},
            headers={"Accept": "application/json"}
        )
        r.raise_for_status()
        data = r.json()
        spaces.extend(data["results"])
        if "_links" not in data or "next" not in data["_links"]:
            break
        start += limit
    return spaces
```

---

## Gotchas

- **Space key is immutable** — once created, the key cannot be changed via API
- **Personal space keys** use `~` prefix followed by the user's account ID (not username)
- **Archived spaces** are excluded from `GET /space` by default; add `?status=archived` to include them
- **Space deletion is async** — the DELETE call returns immediately but deletion runs as a background task
- **v2 uses numeric IDs** — you must resolve a space key to an ID before using v2 endpoints; the key alone won't work
