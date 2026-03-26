# Confluence Pages & Blogposts Reference

## Content Types

| Type | v1 `type` field | v2 endpoint | Description |
|---|---|---|---|
| Page | `page` | `/wiki/api/v2/pages` | Standard wiki page |
| Blogpost | `blogpost` | `/wiki/api/v2/blogposts` | Time-stamped blog entry in a space |
| Template | `page` (draft) | — | Page template for creating new pages |
| Comment | `comment` | `/wiki/api/v2/comments` | Footer comment or inline comment |
| Attachment | `attachment` | `/wiki/api/v2/attachments` | File attached to a page |

---

## v1 Page Endpoints

Base: `https://{domain}.atlassian.net/wiki/rest/api/content`

### Get a page

```bash
# Minimal
GET /rest/api/content/12345678

# With body and metadata
GET /rest/api/content/12345678?expand=body.storage,version,ancestors,space,metadata.labels
```

**Key `expand` options:**
| Expand value | What it adds |
|---|---|
| `body.storage` | Page body in storage (XHTML) format |
| `body.view` | Rendered HTML |
| `body.export_view` | Export-ready HTML |
| `body.atlas_doc_format` | Atlassian Document Format (ADF JSON) |
| `version` | Current version number and author |
| `ancestors` | Full ancestor chain (parent, grandparent, …) |
| `space` | Space key and name |
| `metadata.labels` | Page labels |
| `children.page` | Direct child pages |
| `history` | Creation and last update info |
| `restrictions.read.restrictions.user` | Users with explicit read restrictions |

### Find pages by space and/or title

```bash
GET /rest/api/content?spaceKey=ENG&type=page&title=My+Page+Title
GET /rest/api/content?spaceKey=ENG&type=page&limit=50&start=0&expand=version
```

### Create a page

```http
POST /rest/api/content
Content-Type: application/json

{
  "type": "page",
  "title": "My New Page",
  "space": { "key": "ENG" },
  "ancestors": [{ "id": "12345678" }],
  "body": {
    "storage": {
      "value": "<p>Hello, world!</p><p>This is my page.</p>",
      "representation": "storage"
    }
  }
}
```

- `ancestors` — sets the parent page; the **last** element is the direct parent
- Omit `ancestors` to create a top-level page in the space
- `status` can be `"current"` (default, published) or `"draft"` (saved as draft)

### Create a draft (unpublished)

```http
POST /rest/api/content
{
  "type": "page",
  "title": "Work in Progress",
  "space": { "key": "ENG" },
  "status": "draft",
  "body": {
    "storage": {
      "value": "<p>Draft content...</p>",
      "representation": "storage"
    }
  }
}
```

### Update a page (version number required)

Always fetch the current page first to get the version number, then increment by 1:

```python
# Step 1: get current version
r = requests.get(
    f"{CONFLUENCE_BASE}/content/{page_id}",
    auth=AUTH, params={"expand": "version"}
)
current_version = r.json()["version"]["number"]

# Step 2: update with next version number
requests.put(
    f"{CONFLUENCE_BASE}/content/{page_id}",
    auth=AUTH,
    json={
        "type": "page",
        "title": "Updated Title",
        "version": { "number": current_version + 1 },
        "body": {
            "storage": {
                "value": "<p>Updated content</p>",
                "representation": "storage"
            }
        }
    }
)
```

### Delete a page

```bash
DELETE /rest/api/content/12345678
```

This moves the page to trash. To permanently delete (purge from trash):
```bash
DELETE /rest/api/content/12345678?status=trashed
```

### Restore a page from trash

```http
PUT /rest/api/content/12345678
{
  "type": "page",
  "title": "My Page",
  "version": { "number": <N+1> },
  "status": "current"
}
```

---

## v2 Page Endpoints

Base: `https://{domain}.atlassian.net/wiki/api/v2/pages`

### Get a page

```bash
GET /wiki/api/v2/pages/12345678
GET /wiki/api/v2/pages/12345678?body-format=storage
GET /wiki/api/v2/pages/12345678?body-format=atlas_doc_format
```

### List pages in a space

```bash
GET /wiki/api/v2/pages?spaceId=98765&limit=50&status=current
GET /wiki/api/v2/pages?spaceId=98765&title=My+Page
GET /wiki/api/v2/pages?spaceId=98765&sort=title&limit=50
```

Sort options: `id`, `-id`, `title`, `-title`, `created-date`, `-created-date`, `modified-date`, `-modified-date`

### Create a page (v2)

```http
POST /wiki/api/v2/pages
{
  "spaceId": "98765",
  "status": "current",
  "title": "My New Page",
  "parentId": "12345678",
  "body": {
    "representation": "storage",
    "value": "<p>Hello, world!</p>"
  }
}
```

### Update a page (v2 — version required)

```http
PUT /wiki/api/v2/pages/12345678
{
  "id": "12345678",
  "status": "current",
  "title": "Updated Title",
  "version": { "number": 3 },
  "body": {
    "representation": "storage",
    "value": "<p>New content</p>"
  }
}
```

### Get child pages

```bash
GET /wiki/api/v2/pages/12345678/children?limit=50
```

### Get ancestor chain

```bash
GET /wiki/api/v2/pages/12345678/ancestors
```

---

## Page Hierarchy and Navigation

### Move a page to a different parent (v1)

```http
PUT /rest/api/content/12345678
{
  "type": "page",
  "title": "Same Title",
  "version": { "number": <N+1> },
  "ancestors": [{ "id": "NEW_PARENT_ID" }]
}
```

### Get all descendants of a page

```bash
GET /rest/api/content/12345678/descendant/page?limit=50
```

---

## Page Versions and History

### List versions of a page

```bash
GET /rest/api/content/12345678/version?limit=50
```

### Get a specific version

```bash
GET /rest/api/content/12345678/version/3
GET /rest/api/content/12345678/version/3?expand=content
```

### Get page history

```bash
GET /rest/api/content/12345678/history
```

Returns created date, author, and last update.

### Restore a previous version

```http
POST /rest/api/content/12345678/version
{
  "operationKey": "restore",
  "params": { "versionNumber": 2, "message": "Restoring to version 2" }
}
```

---

## Blogposts

Blogposts are time-stamped content entries within a space.

### List blogposts in a space

```bash
GET /rest/api/content?type=blogpost&spaceKey=ENG&limit=25
```

### Create a blogpost

```http
POST /rest/api/content
{
  "type": "blogpost",
  "title": "Q1 Engineering Update",
  "space": { "key": "ENG" },
  "body": {
    "storage": {
      "value": "<p>Here's what we shipped this quarter...</p>",
      "representation": "storage"
    }
  }
}
```

### v2 blogpost endpoints

```bash
GET /wiki/api/v2/blogposts?spaceId=98765&limit=25
POST /wiki/api/v2/blogposts
GET /wiki/api/v2/blogposts/{id}
PUT /wiki/api/v2/blogposts/{id}
DELETE /wiki/api/v2/blogposts/{id}
```

---

## Content Properties (Custom Metadata on Pages)

Arbitrary JSON properties can be attached to any content:

```bash
GET /rest/api/content/12345678/property
POST /rest/api/content/12345678/property
PUT /rest/api/content/12345678/property/{key}
DELETE /rest/api/content/12345678/property/{key}
```

```http
POST /rest/api/content/12345678/property
{
  "key": "deployment-status",
  "value": { "env": "prod", "version": "2.4.1", "deployed_at": "2026-03-25" }
}
```

This is useful for storing structured metadata on pages that external systems can read or update.

---

## Common Patterns

### Find or create a page

```python
def get_or_create_page(confluence_base, auth, space_key, title, parent_id, body_html):
    # Try to find existing page
    r = requests.get(
        f"{confluence_base}/content",
        auth=auth,
        params={"spaceKey": space_key, "title": title, "type": "page", "expand": "version"}
    )
    results = r.json().get("results", [])

    if results:
        page = results[0]
        # Update existing page
        page_id = page["id"]
        new_version = page["version"]["number"] + 1
        requests.put(
            f"{confluence_base}/content/{page_id}",
            auth=auth,
            json={
                "type": "page",
                "title": title,
                "version": {"number": new_version},
                "body": {"storage": {"value": body_html, "representation": "storage"}}
            }
        )
        return page_id
    else:
        # Create new page
        r = requests.post(
            f"{confluence_base}/content",
            auth=auth,
            json={
                "type": "page",
                "title": title,
                "space": {"key": space_key},
                "ancestors": [{"id": parent_id}] if parent_id else [],
                "body": {"storage": {"value": body_html, "representation": "storage"}}
            }
        )
        return r.json()["id"]
```

---

## Gotchas

- **Version number is mandatory on updates** — forgetting it returns a 409 Conflict
- **`ancestors` order** — last element is the direct parent; earlier elements are ancestors further up
- **Deleting sends to trash** — the page is not permanently gone; use `?status=trashed` to purge
- **Title uniqueness is per-space** — two pages in different spaces can have the same title, but within a space titles must be unique
- **Draft pages** — use `status=draft`; they're hidden from normal navigation but visible via API with `status=draft` param
- **Whitespace in titles** — URL-encode spaces as `+` or `%20` when using title as a query param
