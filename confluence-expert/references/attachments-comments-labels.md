# Attachments, Comments, and Labels Reference

## Attachments

### Upload an Attachment (v1)

```bash
POST /rest/api/content/{pageId}/child/attachment
X-Atlassian-Token: no-check
Content-Type: multipart/form-data
```

The `X-Atlassian-Token: no-check` header is **required** — omitting it returns 403 (CSRF protection).

```bash
# curl example
curl -u "email:token" \
  -X POST \
  -H "X-Atlassian-Token: no-check" \
  -F "file=@/path/to/report.pdf" \
  -F "comment=Quarterly report" \
  "https://domain.atlassian.net/wiki/rest/api/content/12345678/child/attachment"
```

```python
import requests

def upload_attachment(domain, auth, page_id, filepath, comment=""):
    with open(filepath, "rb") as f:
        r = requests.post(
            f"https://{domain}.atlassian.net/wiki/rest/api/content/{page_id}/child/attachment",
            auth=auth,
            headers={"X-Atlassian-Token": "no-check"},
            files={"file": (filepath.name, f, "application/octet-stream")},
            data={"comment": comment}
        )
    r.raise_for_status()
    return r.json()
```

### Update an Existing Attachment

To update (replace) an existing attachment, use the attachment's content ID:

```bash
POST /rest/api/content/{attachmentId}/data
X-Atlassian-Token: no-check
Content-Type: multipart/form-data

# -F "file=@/new/version.pdf" -F "comment=Updated version"
```

### List Attachments on a Page

```bash
# v1
GET /rest/api/content/{pageId}/child/attachment?limit=50

# v2
GET /wiki/api/v2/pages/{pageId}/attachments?limit=50
GET /wiki/api/v2/attachments/{attachmentId}
GET /wiki/api/v2/blogposts/{blogpostId}/attachments
GET /wiki/api/v2/custom-content/{id}/attachments
GET /wiki/api/v2/labels/{id}/attachments
```

### Download an Attachment

```bash
GET /rest/api/content/{attachmentId}/data
```

This streams the file binary. The attachment's `_links.download` field in the metadata also provides the download URL.

### Attachment Metadata Response

```json
{
  "id": "att12345",
  "type": "attachment",
  "status": "current",
  "title": "report.pdf",
  "metadata": {
    "comment": "Quarterly report",
    "mediaType": "application/pdf"
  },
  "extensions": {
    "fileSize": 102400,
    "mediaType": "application/pdf"
  },
  "_links": {
    "download": "/download/attachments/12345678/report.pdf?version=1",
    "webui": "/display/ENG/My+Page?preview=%2Fattachments%2F12345678%2Freport.pdf"
  }
}
```

### Delete an Attachment

```bash
# Move to trash
DELETE /rest/api/content/{attachmentId}

# Permanent delete
DELETE /rest/api/content/{attachmentId}?status=trashed
```

---

## Comments

Confluence has two types of comments:
- **Footer comments** — appear at the bottom of a page
- **Inline comments** — anchored to specific text within the page

### List Comments on a Page

```bash
# v1 — footer comments
GET /rest/api/content/{pageId}/child/comment?limit=50&expand=body.storage

# v1 — inline comments
GET /rest/api/content/{pageId}/child/comment?limit=50&location=inline&expand=body.storage

# v2
GET /wiki/api/v2/pages/{pageId}/footer-comments?limit=50
GET /wiki/api/v2/pages/{pageId}/inline-comments?limit=50
GET /wiki/api/v2/footer-comments/{commentId}
GET /wiki/api/v2/inline-comments/{commentId}
```

### Create a Footer Comment (v1)

```http
POST /rest/api/content
Content-Type: application/json

{
  "type": "comment",
  "container": {
    "id": "12345678",
    "type": "page"
  },
  "body": {
    "storage": {
      "value": "<p>This is my comment.</p>",
      "representation": "storage"
    }
  }
}
```

### Create a Footer Comment (v2)

```http
POST /wiki/api/v2/footer-comments
{
  "pageId": "12345678",
  "body": {
    "representation": "storage",
    "value": "<p>This is my comment.</p>"
  }
}
```

### Reply to a Comment

```http
POST /rest/api/content
{
  "type": "comment",
  "container": { "id": "12345678", "type": "page" },
  "ancestors": [{ "id": "parentCommentId" }],
  "body": {
    "storage": {
      "value": "<p>Reply text here.</p>",
      "representation": "storage"
    }
  }
}
```

### Update a Comment

```http
PUT /rest/api/content/{commentId}
{
  "type": "comment",
  "version": { "number": 2 },
  "body": {
    "storage": {
      "value": "<p>Updated comment text.</p>",
      "representation": "storage"
    }
  }
}
```

### Delete a Comment

```bash
DELETE /rest/api/content/{commentId}
```

---

## Labels

Labels are tags that can be applied to pages, blogposts, attachments, and custom content. They are not supported on spaces in the v2 API (space labels use v1 only).

### Get Labels on a Page

```bash
# v1
GET /rest/api/content/{pageId}/label

# v2 include param
GET /wiki/api/v2/pages/{pageId}?include-labels=true

# v2 dedicated endpoint
GET /wiki/api/v2/pages/{pageId}/labels
GET /wiki/api/v2/blogposts/{id}/labels
GET /wiki/api/v2/attachments/{id}/labels
GET /wiki/api/v2/custom-content/{id}/labels
```

v1 response:
```json
{
  "results": [
    { "prefix": "global", "name": "release-notes", "id": "label_123", "label": "release-notes" },
    { "prefix": "global", "name": "approved", "id": "label_456", "label": "approved" }
  ]
}
```

### Add Labels to a Page

```http
POST /rest/api/content/{pageId}/label
Content-Type: application/json

[
  { "prefix": "global", "name": "release-notes" },
  { "prefix": "global", "name": "v2.1" }
]
```

Label prefixes:
- `global` — standard user-added labels
- `my` — personal labels (visible only to creator)
- `team` — team labels

### Remove a Label from a Page

```bash
# v1 — by label name
DELETE /rest/api/content/{pageId}/label/{labelName}
DELETE /rest/api/content/{pageId}/label?name={labelName}
```

### Find All Content with a Label (CQL)

```bash
GET /rest/api/search?cql=label="release-notes"+AND+type=page&limit=50
```

Or using the v2 labels endpoint:

```bash
# Get all pages with a label ID
GET /wiki/api/v2/labels/{labelId}/pages?limit=50
```

### Get Label Info and Usage

```bash
GET /rest/api/label?name=release-notes
GET /rest/api/label?prefix=global&name=release-notes
```

---

## Python Utility: Add Labels

```python
import requests

def add_labels(domain, auth, page_id, label_names):
    payload = [{"prefix": "global", "name": name} for name in label_names]
    r = requests.post(
        f"https://{domain}.atlassian.net/wiki/rest/api/content/{page_id}/label",
        auth=auth,
        json=payload,
        headers={"Accept": "application/json", "Content-Type": "application/json"}
    )
    r.raise_for_status()
    return r.json()

add_labels("mycompany", ("me@example.com", "token"), "12345678", ["approved", "v3.0"])
```

---

## Gotchas

- **`X-Atlassian-Token: no-check` is required for all attachment uploads** — without it you get a 403 even with valid credentials
- **Attachment size limits** — Confluence enforces per-file and per-space attachment size limits configured by the admin; the API returns 413 if exceeded
- **Comment version increment** — like pages, updating a comment via v1 PUT requires the next version number
- **Labels are case-insensitive but stored lowercase** — adding `"Release-Notes"` and `"release-notes"` are the same label
- **Space labels** — to list space-level labels, use v1: `GET /rest/api/space/{key}?expand=metadata.labels`; v2 has no space-labels endpoint
- **Inline comments require anchors** — creating inline comments via API requires knowing the anchor text/ID where the comment should attach; simpler to use footer comments programmatically
- **Attachment IDs start with `att`** — the full content ID for an attachment is like `att12345`, but numeric-only when used as a page ID
