---
name: confluence-expert
description: >
  Expert guide for interacting with Confluence Cloud and Data Center via REST API (v1 and v2),
  CQL search, and webhooks. Use this skill whenever the user wants to: create, read, update,
  or delete Confluence pages, spaces, blogposts, attachments, or comments; search with CQL;
  manage labels or content hierarchy; set space/page permissions or restrictions; register
  or handle webhooks; authenticate to the Confluence API (API tokens, OAuth 2.0, PAT for
  Data Center); understand storage format, wiki markup, or Atlassian Document Format (ADF);
  work with page versions or history; write Python/JavaScript/curl Confluence API calls; or
  integrate any external system with Confluence. Trigger for any request mentioning Confluence,
  wiki pages, CQL, space keys, atlassian.net/wiki, Confluence macros, blueprints, page IDs,
  or any Confluence concepts — even if the user says "our wiki", "our knowledge base", or
  "our docs" in a context that implies Confluence.
---

# Confluence Expert Skill

## Platform Overview

| Interface | Base URL | Best for |
|---|---|---|
| **REST API v2** | `https://{domain}.atlassian.net/wiki/api/v2/` | **Preferred for Cloud** — cleaner design, actively developed |
| **REST API v1** | `https://{domain}.atlassian.net/wiki/rest/api/` | Legacy Cloud (being deprecated) + Data Center; still required for search, some permissions |
| **Data Center v1** | `https://{host}/wiki/rest/api/` | On-prem/DC deployments — v1 only |
| **CQL Search** | `GET /rest/api/search?cql=...` | Full-text + metadata search (v1; confirmed NOT deprecated) |
| **Webhooks** | `POST /rest/webhooks/1.0/webhook` | Event-driven integration |

**v1 vs v2 quick rule:**
- **Cloud**: Use v2 for all new integrations. Most v1 Cloud endpoints were deprecated March 31, 2025.
  - Exceptions still requiring v1: `search`, `content/search`, space-level labels, some legacy operations
- **Data Center**: v1 only — v2 does not exist on Data Center

---

## Authentication Quick Reference

All REST API calls require authentication. See `references/auth.md` for full details.

| Method | Header | Best for |
|---|---|---|
| API Token (Basic) | `Authorization: Basic base64(email:token)` | Scripts, bots, personal automation (Cloud) |
| Personal Access Token | `Authorization: Bearer PAT_TOKEN` | Scripts and bots on Data Center |
| OAuth 2.0 (3LO) | `Authorization: Bearer ACCESS_TOKEN` | User-facing apps acting on behalf of a user |
| Forge app | Handled by Forge runtime | Apps on Atlassian's platform |
| Connect app (JWT) | `Authorization: JWT <jwt>` | Marketplace apps |

Every request also needs:
```
Content-Type: application/json
Accept: application/json
```

Base URL: `https://YOUR-DOMAIN.atlassian.net/wiki/rest/api/`

---

## Rate Limits

Confluence Cloud uses Atlassian's points-based rate limiting (same system as Jira).

| Behavior | Detail |
|---|---|
| Throttled response | `HTTP 429` with `Retry-After` header |
| Strategy | Exponential backoff; read `Retry-After` value |
| Burst limit | ~10 concurrent requests recommended max |

See `references/rate-limits-pagination.md` for full details.

---

## Pagination

**v1 (offset-based):**
```
GET /rest/api/content?spaceKey=PROJ&start=0&limit=25
```
- `limit` capped at 100 (default 25); use 50 for most queries
- Response includes `_links.next` when more pages exist
- `size` field shows items returned; `start` + `size` advances the cursor

**v2 (cursor-based):**
```
GET /wiki/api/v2/pages?spaceId=98765&limit=50&cursor=<token>
```
- Response includes `_links.next` with cursor in URL
- Extract and pass `cursor` param to next request

---

## Key Resource Areas

| Area | Reference file | What's covered |
|---|---|---|
| Authentication (API token, OAuth, PAT, Forge) | `references/auth.md` | Token creation, Basic auth header, OAuth 2.0 scopes, DC PATs, Forge/Connect |
| Spaces (CRUD, hierarchy, content listing) | `references/spaces.md` | Create/get/update/delete spaces, list space content, space types, homepage |
| Pages and blogposts (CRUD, versions, ancestors) | `references/pages.md` | Create/get/update/delete pages, move pages, page hierarchy, versions/history, blogposts |
| Content body formats (storage, ADF, wiki markup) | `references/content-formats.md` | Storage format (XHTML), ADF, wiki markup, body representation param, macros in storage format |
| Search & CQL | `references/search-cql.md` | CQL syntax, all fields/operators/functions, search endpoints, excerpt and expand |
| Attachments, comments & labels | `references/attachments-comments-labels.md` | File upload, inline/footer comments, label CRUD, attachment metadata |
| Permissions & restrictions | `references/permissions.md` | Space permissions, page-level restrictions, user/group lookup |
| Webhooks | `references/webhooks.md` | All event types, payload structure, registration, HMAC validation, retry behavior |
| Rate limits & pagination | `references/rate-limits-pagination.md` | Quota, retry strategy, v1 offset pagination, v2 cursor pagination |

---

## Common Patterns

### Get a page by ID (v1)
```bash
GET /rest/api/content/12345678
GET /rest/api/content/12345678?expand=body.storage,version,ancestors,space
```

### Get a page by ID (v2)
```bash
GET /wiki/api/v2/pages/12345678
GET /wiki/api/v2/pages/12345678?body-format=storage
```

### Find pages in a space by title
```bash
GET /rest/api/content?spaceKey=ENG&title=My+Page+Title&type=page&expand=body.storage
```

### Create a page (v1)
```http
POST /rest/api/content
{
  "type": "page",
  "title": "My New Page",
  "space": { "key": "ENG" },
  "ancestors": [{ "id": "12345678" }],
  "body": {
    "storage": {
      "value": "<p>Hello, world!</p>",
      "representation": "storage"
    }
  }
}
```

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

### Update a page (v1 — version number required)
```http
PUT /rest/api/content/12345678
{
  "type": "page",
  "title": "Updated Title",
  "version": { "number": 2 },
  "body": {
    "storage": {
      "value": "<p>Updated content</p>",
      "representation": "storage"
    }
  }
}
```

### Search with CQL
```bash
GET /rest/api/search?cql=space=ENG+AND+type=page+AND+text~%22deployment%22&limit=25&expand=content.body.storage
```

### Add a label to a page
```http
POST /rest/api/content/12345678/label
[
  { "prefix": "global", "name": "my-label" }
]
```

### Upload an attachment
```http
POST /rest/api/content/12345678/child/attachment
X-Atlassian-Token: no-check
Content-Type: multipart/form-data
[binary file + comment field]
```

### Get child pages
```bash
# v1
GET /rest/api/content/12345678/child/page?limit=50

# v2
GET /wiki/api/v2/pages/12345678/children?limit=50
```

---

## Key Gotchas

- **Storage format, not plain text** — Page body must be valid XHTML storage format or ADF. Sending a plain string will create a page with literal HTML-escaped text.
- **Version number is mandatory for updates (v1)** — Every PUT to update a page requires the *next* version number. Fetch current version first, then increment by 1.
- **`X-Atlassian-Token: no-check` for file uploads** — The CSRF protection header must be sent when uploading attachments; omitting it returns 403.
- **Space key vs Space ID** — v1 uses space *key* (e.g., `ENG`); v2 uses numeric space *ID*. Resolve via `GET /wiki/api/v2/spaces?keys=ENG`.
- **Page ID vs Content ID** — They're the same thing in v1. In v2, pages and blogposts have separate endpoints but share the same ID namespace.
- **Ancestor order matters** — When creating a page with ancestors, the last item in the array is the direct parent.
- **CQL `text~` is full-text, not substring** — It searches the indexed content, not a literal substring match. Use `title=` for exact title matching.
- **Deleted content still has IDs** — `GET /rest/api/content/{id}` on a deleted page returns 404; use `?status=trashed` to access trash.
- **OAuth 2.0 uses cloud ID, not domain** — For OAuth-authenticated calls, the base is `https://api.atlassian.com/ex/confluence/{cloudId}/wiki/rest/api/` not the direct domain URL.
