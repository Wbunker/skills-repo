# Confluence Search & CQL Reference

## Search Endpoints

| Endpoint | API | Description |
|---|---|---|
| `GET /rest/api/search` | v1 | Full search: content, spaces, users, attachments |
| `GET /rest/api/content/search` | v1 | Content-only CQL search |
| `GET /rest/api/search/user` | v1 | User search (user-specific CQL fields) |

> There is **no search endpoint in v2**. Use v1 search endpoints even when otherwise migrating to v2. Atlassian has confirmed these v1 endpoints will NOT be deprecated.

---

## Basic Usage

```bash
# Simple query
GET /rest/api/search?cql=space=ENG+AND+type=page

# URL-encoded (preferred for complex queries)
GET /rest/api/search?cql=(type%3Dpage+AND+space%3DENG)&limit=25

# Using curl with --data-urlencode (safest)
curl -u email:token -G "https://domain.atlassian.net/wiki/rest/api/search" \
  --data-urlencode "cql=space = ENG AND type = page AND text ~ deployment" \
  --data-urlencode "limit=25"
```

### Query Parameters

| Parameter | Type | Description |
|---|---|---|
| `cql` | string | The CQL query (required) |
| `cqlcontext` | JSON string | Contextual scope: `{"spaceKey":"ENG","contentId":"123"}` |
| `limit` | int | Results per page (default 25, max 100) |
| `start` | int | Offset for pagination |
| `cursor` | string | Cursor for cursor-based pagination |
| `expand` | string | Comma-separated fields to expand (e.g., `content.body.storage`) |
| `excerpt` | string | Excerpt size: `highlight` (default), `indexed`, `none`, `highlight_unescaped` |
| `includeArchivedSpaces` | bool | Include archived spaces in results (default false) |
| `excludeCurrentSpaces` | bool | Exclude current active spaces |

---

## Response Structure

```json
{
  "results": [
    {
      "content": {
        "id": "12345678",
        "type": "page",
        "status": "current",
        "title": "My Page",
        "space": { "key": "ENG", "name": "Engineering" },
        "_links": { "webui": "/display/ENG/My+Page" }
      },
      "title": "My Page",
      "excerpt": "...matching text with <span class='search-matched-tag'>highlighted</span> terms...",
      "url": "/display/ENG/My+Page",
      "resultGlobalContainer": { "title": "Engineering", "displayUrl": "/display/ENG" },
      "resultParentContainer": { "title": "Parent Page", "displayUrl": "..." },
      "entityType": "content",
      "iconCssClass": "page-icon",
      "lastModified": "2026-03-20T14:00:00.000Z",
      "score": 0.87
    }
  ],
  "start": 0,
  "limit": 25,
  "size": 25,
  "totalSize": 142,
  "_links": {
    "next": "/rest/api/search?cql=...&limit=25&start=25",
    "self": "/rest/api/search?cql=..."
  }
}
```

---

## CQL Syntax

A CQL query consists of: `field operator value [AND|OR|NOT field operator value ...]`

```sql
-- Basic
space = ENG
type = page
title = "My Page"

-- Combined
space = ENG AND type = page
label = "release-notes" OR label = "changelog"
NOT space = ARCHIVE

-- Grouping
(type = page AND space = ENG) OR (type = blogpost AND creator = currentUser())

-- Ordering
space = ENG AND type = page ORDER BY lastmodified DESC
type = blogpost ORDER BY created DESC, title ASC
```

---

## CQL Fields

### Content/Structural Fields

| Field | Type | Operators | Example |
|---|---|---|---|
| `id` | CONTENT | `=`, `!=`, `IN`, `NOT IN` | `id = 12345678` |
| `type` | TYPE | `=`, `!=`, `IN`, `NOT IN` | `type IN (page, blogpost)` |
| `title` | TEXT | `=`, `!=`, `~`, `!~` | `title ~ "deployment"` |
| `text` | TEXT | `~`, `!~` | `text ~ "error handling"` |
| `parent` | CONTENT | `=`, `!=`, `IN`, `NOT IN` | `parent = 12345678` |
| `ancestor` | CONTENT | `=`, `!=`, `IN`, `NOT IN` | `ancestor = 12345678` |
| `space` | SPACE | `=`, `!=`, `IN`, `NOT IN` | `space = ENG` |
| `label` | STRING | `=`, `!=`, `IN`, `NOT IN` | `label = "approved"` |
| `macro` | STRING | `=`, `!=`, `IN`, `NOT IN` | `macro = jira` |
| `subtype` | SUBTYPE | `=`, `!=`, `IN`, `NOT IN` | `subtype = live` |
| `pageStatus` | TEXT | `=`, `!=`, `IN`, `NOT IN` | `pageStatus = "Rough draft"` |
| `fileExtension` | TEXT | `=`, `!=`, `IN`, `NOT IN` | `fileExtension = pdf` |

**Valid `type` values:** `page`, `blogpost`, `comment`, `attachment`, `whiteboard`, `database`, `embed`, `folder`

### Date Fields

| Field | Operators | Functions | Example |
|---|---|---|---|
| `created` | `=`, `!=`, `>`, `>=`, `<`, `<=` | All date functions | `created > "2026-01-01"` |
| `lastmodified` | `=`, `!=`, `>`, `>=`, `<`, `<=` | All date functions | `lastmodified >= startOfMonth()` |

Date formats accepted: `"2026-01-15"` or `"2026/01/15"` or `"2026-01-15 09:00"`.

### User Fields

| Field | Type | Operators | Example |
|---|---|---|---|
| `creator` | USER | `=`, `!=`, `IN`, `NOT IN` | `creator = currentUser()` |
| `contributor` | USER | `=`, `!=`, `IN`, `NOT IN` | `contributor = "99:abc..."` |
| `mention` | USER | `=`, `!=`, `IN`, `NOT IN` | `mention = currentUser()` |
| `watcher` | USER | `=`, `!=`, `IN`, `NOT IN` | `watcher = currentUser()` |
| `favourite` / `favorite` | USER | `=`, `!=`, `IN`, `NOT IN` | `favourite = currentUser()` |
| `owner` | OWNER | `=`, `!=`, `IN`, `NOT IN` | `owner = currentUser()` |

> User values use **accountId** (the Atlassian UUID format: `"99:27935d01-XXXX-XXXX-XXXX-a9b8d3b2ae2e"`). Resolve via `GET /rest/api/user/search?query=email`.

> On Cloud: user fields like `user`, `user.fullname`, `user.accountid` are NOT supported on the `/search` endpoint. They only work on `/search/user`.

---

## CQL Operators

| Operator | Symbol | Field Types | Example |
|---|---|---|---|
| Equals | `=` | Non-text | `space = ENG` |
| Not equals | `!=` | Non-text | `type != comment` |
| Greater than | `>` | Date, numeric | `created > "2026-01-01"` |
| Greater or equal | `>=` | Date, numeric | `created >= startOfYear()` |
| Less than | `<` | Date, numeric | `lastmodified < startOfMonth()` |
| Less or equal | `<=` | Date, numeric | `lastmodified <= endOfWeek()` |
| Contains | `~` | Text (title, text) | `title ~ "release"` |
| Does not contain | `!~` | Text (title, text) | `text !~ "deprecated"` |
| In | `IN` | Any | `type IN (page, blogpost)` |
| Not in | `NOT IN` | Any | `space NOT IN (ARCHIVE, TEST)` |
| And | `AND` | — | `space = ENG AND type = page` |
| Or | `OR` | — | `label = "v1" OR label = "v2"` |
| Not | `NOT` | — | `NOT space = ARCHIVE` |

**Text search notes:**
- `~` performs fuzzy/stemmed full-text search, not a substring match
- `title = "My Exact Title"` for exact title match
- `title ~ "deploy"` matches "deployment", "deploying", etc.
- Negative clauses (`NOT`, `!=`, `!~`) cannot be the first clause in a query

---

## CQL Functions

### User Functions

| Function | Fields | Operators | Example |
|---|---|---|---|
| `currentUser()` | creator, contributor, mention, watcher, favourite, owner | `=`, `!=` | `creator = currentUser()` |
| `favouriteSpaces()` | space | `IN`, `NOT IN` | `space IN favouriteSpaces()` |
| `recentlyViewedContent(limit, offset)` | ancestor, content, id, parent | `IN`, `NOT IN` | `id IN recentlyViewedContent(10)` |
| `recentlyViewedSpaces(limit)` | space | `IN`, `NOT IN` | `space IN recentlyViewedSpaces(5)` |

### Date Functions

| Function | Args | Example |
|---|---|---|
| `startOfDay(inc)` | optional `"+1d"`, `"-2w"`, etc. | `created > startOfDay()` |
| `endOfDay(inc)` | optional increment | `lastmodified <= endOfDay()` |
| `startOfWeek(inc)` | optional increment | `created >= startOfWeek()` |
| `endOfWeek(inc)` | optional increment | `created < endOfWeek()` |
| `startOfMonth(inc)` | optional increment | `lastmodified >= startOfMonth()` |
| `endOfMonth(inc)` | optional increment | `created < endOfMonth()` |
| `startOfYear(inc)` | optional increment | `created >= startOfYear()` |
| `endOfYear(inc)` | optional increment | `created < endOfYear()` |
| `now(inc)` | optional increment | `created > now("-4w")` |

Increment format: `(+/-)N(y|M|w|d|h|m)` — e.g., `"-2w"` = 2 weeks ago, `"+1M"` = 1 month from now.

---

## Common CQL Examples

```sql
-- All current pages in a space
type = page AND space = ENG AND status = current

-- Pages modified in the last 7 days
type = page AND lastmodified > now("-1w")

-- Pages created by the current user this year
type = page AND creator = currentUser() AND created >= startOfYear()

-- All content with a specific label
label = "needs-review"

-- Pages in multiple spaces
type = page AND space IN (ENG, DOCS, OPS)

-- Pages with a specific macro
type = page AND macro = jira

-- Pages that mention a specific user
type = page AND mention = "99:abc123..."

-- Attachments with a specific extension
type = attachment AND fileExtension = pdf

-- Recently viewed content
id IN recentlyViewedContent(20)

-- Pages in favourite spaces updated recently
type = page AND space IN favouriteSpaces() AND lastmodified > now("-2w")

-- Full-text search in body
type = page AND space = ENG AND text ~ "kubernetes deployment"

-- Complex: recent blog posts OR my pages
(type = blogpost AND created > now("-1M")) OR (type = page AND creator = currentUser())

-- Pages under a specific parent (all descendants)
ancestor = 12345678 AND type = page

-- Pages that are direct children of a page
parent = 12345678 AND type = page

-- Ordered results
type = page AND space = ENG ORDER BY lastmodified DESC

-- Draft pages
type = page AND space = ENG AND status = draft
```

---

## Expand in Search

Use the `expand` parameter to include content fields in search results:

```bash
# Include body in search results (storage format)
GET /rest/api/search?cql=space=ENG&expand=content.body.storage

# Include version info
GET /rest/api/search?cql=space=ENG&expand=content.version

# Include space details
GET /rest/api/search?cql=type=page&expand=content.space
```

> **Warning:** Adding `body.storage` or `body.export_view` limits results to a maximum of **50 per page** regardless of the `limit` parameter.

---

## Content-Only Search Endpoint

`GET /rest/api/content/search` returns the same response structure as the content API (not the search result wrapper):

```bash
GET /rest/api/content/search?cql=space=ENG+AND+type=page&limit=50&expand=body.storage,version
```

Response is `{ "results": [...], "start": 0, "limit": 50, "size": N }` where each result is a full content object (not a search result wrapper with `excerpt`).

---

## Searching for Users

```bash
# Search for users (name/email)
GET /rest/api/user/search?query=john.doe@example.com

# Get user by accountId
GET /rest/api/user?accountId=99:abc123...

# User-specific CQL search
GET /rest/api/search/user?cql=user.fullname ~ "John"
```

---

## Python Pagination Pattern

```python
import requests

def search_all(domain, auth, cql, expand=None):
    base = f"https://{domain}.atlassian.net/wiki/rest/api/search"
    params = {"cql": cql, "limit": 50}
    if expand:
        params["expand"] = expand
    results = []
    while True:
        r = requests.get(base, auth=auth, params=params, headers={"Accept": "application/json"})
        r.raise_for_status()
        data = r.json()
        results.extend(data["results"])
        if "_links" not in data or "next" not in data["_links"]:
            break
        # Advance offset
        params["start"] = params.get("start", 0) + data["size"]
        if params["start"] >= data.get("totalSize", 0):
            break
    return results
```

---

## Gotchas

- **No v2 search** — the search API lives only in v1; do not try to call `/wiki/api/v2/search`
- **Negative first clause** — CQL rejects queries that start with `NOT`, `!=`, or `!~`; prefix with something positive: `type = page AND NOT space = ARCHIVE`
- **Text search with `expand=body.storage`** — hard limit of 50 results even with higher `limit`
- **User fields on `/search`** — `user`, `user.fullname`, `user.accountid` are prohibited on the general search endpoint; use `/search/user` instead
- **Space key case** — space keys are case-sensitive in CQL; `space = eng` and `space = ENG` may behave differently
- **Archived content** — archived pages are excluded by default; pass `includeArchivedSpaces=true` or query `status = archived`
- **Sorting limitations** — not all fields support ORDER BY; fields where content can have multiple values (like `label`) cannot be used as sort keys
- **`ancestor` vs `parent`** — `parent` matches only direct children; `ancestor` matches all descendants at any depth
