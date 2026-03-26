---
name: jira-expert
description: >
  Expert guide for interacting with Jira Cloud via REST API v3, JQL, and webhooks.
  Use this skill whenever the user wants to: query, create, update, or transition Jira
  issues; search with JQL; work with Jira projects, components, or versions; manage
  sprints, boards, or backlogs; register or handle webhooks; manage users, groups, or
  permissions; authenticate to the Jira API (API tokens, OAuth 2.0, Basic auth);
  understand Jira rate limits or pagination; write Python/JavaScript/curl Jira API
  calls; or integrate any external system with Jira. Trigger for any request mentioning
  Jira, JQL, atlassian.net, issue keys (e.g. PROJ-123), tickets, sprints, epics,
  Atlassian, jira-python, jira.js, or Connect/Forge apps — even if the user just says
  "our board", "our tickets", or "our backlog" in a context that implies Jira.
---

# Jira Expert Skill

## Platform Overview

| Interface | Base / Endpoint | Best for |
|---|---|---|
| **REST API v3** | `https://{domain}.atlassian.net/rest/api/3/` | Primary API — all issue/project/user operations |
| **REST API v2** | `https://{domain}.atlassian.net/rest/api/2/` | Legacy; avoid for new integrations |
| **Jira Software API** | `https://{domain}.atlassian.net/rest/agile/1.0/` | Boards, sprints, backlogs |
| **Webhooks (REST reg.)** | `POST /rest/api/3/webhook` | Dynamic event-driven integration |
| **Webhooks (legacy reg.)** | `POST /rest/webhooks/1.0/webhook` | Admin-registered webhooks |
| **JQL** | Query parameter or POST body | Issue search and filtering |
| **Jira Expressions** | `POST /rest/api/3/expression/eval` | Server-side computed logic |

---

## Authentication Quick Reference

All REST API calls require authentication. See `references/auth.md` for full details.

| Method | Header | Best for |
|---|---|---|
| API Token (Basic) | `Authorization: Basic base64(email:token)` | Scripts, bots, personal automation |
| OAuth 2.0 (3LO) | `Authorization: Bearer ACCESS_TOKEN` | User-facing apps acting on behalf of a user |
| Forge app | Handled by Forge runtime | Apps hosted on Atlassian's platform |
| Connect app (JWT) | `Authorization: JWT <jwt>` | Apps registered in Atlassian Marketplace |

Every request also needs:
```
Content-Type: application/json
Accept: application/json
```

Base URL pattern: `https://YOUR-DOMAIN.atlassian.net/rest/api/3/`

---

## Rate Limits (Points-Based — Enforced March 2026)

Jira Cloud uses a **points model**, not a simple request count. A single `GET /issue/{key}` costs ~2 points; a search returning 50 issues costs ~51 points.

| Tier | Hourly quota |
|---|---|
| Free | 65,000 pts/hr |
| Standard | 100,000 + (10 × users) pts/hr |
| Premium | 130,000 + (20 × users) pts/hr |
| Enterprise | 150,000 + (30 × users) pts/hr (max 500k) |

Burst limits: 100 req/sec for GET/POST, 50 req/sec for PUT/DELETE. Per-issue write limits: 20 ops/2s, 100 ops/30s.

On `429`: read `Retry-After` header and back off exponentially. See `references/rate-limits-pagination.md` for full detail.

---

## Pagination

Two styles depending on endpoint:

**Offset pagination** (most endpoints):
```
GET /rest/api/3/search/jql?jql=project=PROJ&startAt=0&maxResults=50
```
- `maxResults` capped at 100 (default 50)
- `total` field in response indicates complete count
- Advance `startAt` by `maxResults` until `startAt >= total`

**Cursor pagination** (newer endpoints):
- Response includes `nextPageToken`
- Pass as query param on next request: `?nextPageToken=<token>`

---

## Key Resource Areas

| Area | Reference file | What's covered |
|---|---|---|
| Authentication (tokens, OAuth, JWT) | `references/auth.md` | API token creation, Basic auth header, OAuth 2.0 scopes, Forge/Connect patterns |
| Issues (CRUD, transitions, comments, attachments, worklogs) | `references/issues.md` | Create/get/update/delete issues, transition workflow states, add comments, upload attachments, log work |
| Search & JQL | `references/search-jql.md` | JQL syntax, all fields/operators/functions, search endpoints (GET and POST), Jira Expressions |
| Projects, components, versions | `references/projects.md` | Project CRUD, components, fix versions, project roles, project types |
| Webhooks | `references/webhooks.md` | All event types, payload structure, registration (REST + admin UI), JQL filtering, HMAC validation, retry behavior |
| Rate limits & pagination | `references/rate-limits-pagination.md` | Points model, quota tiers, response headers, retry strategy, pagination patterns |
| Agile (boards, sprints, backlogs) | `references/agile.md` | Jira Software API — boards, sprints, backlog, ranking, Scrum vs Kanban |
| Users, groups & permissions | `references/users-groups-permissions.md` | User lookup, group membership, permission schemes, project roles |

---

## Common Patterns

### Get a single issue
```
GET /rest/api/3/issue/PROJ-123
GET /rest/api/3/issue/PROJ-123?fields=summary,status,assignee
```

### Create an issue
```http
POST /rest/api/3/issue
{
  "fields": {
    "project": { "key": "PROJ" },
    "summary": "Login fails on Safari",
    "issuetype": { "name": "Bug" },
    "description": {
      "type": "doc", "version": 1,
      "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "Steps to reproduce..." }] }]
    },
    "assignee": { "accountId": "5b10a2844c20165700ede21g" },
    "priority": { "name": "High" }
  }
}
```

> **Note:** Description uses Atlassian Document Format (ADF), not plain text.

### Search with JQL
```
GET /rest/api/3/search/jql?jql=project=PROJ AND status="In Progress" AND assignee=currentUser()&fields=summary,status,assignee&maxResults=50
```

For long JQL queries, use POST:
```http
POST /rest/api/3/search/jql
{ "jql": "project = PROJ AND ...", "fields": ["summary", "status"], "maxResults": 50 }
```

### Transition an issue
```
GET /rest/api/3/issue/PROJ-123/transitions  # get available transition IDs first
POST /rest/api/3/issue/PROJ-123/transitions
{ "transition": { "id": "31" } }
```

### Add a comment
```http
POST /rest/api/3/issue/PROJ-123/comment
{
  "body": {
    "type": "doc", "version": 1,
    "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "Investigated — root cause is X." }] }]
  }
}
```

### Bulk create issues (up to 50)
```http
POST /rest/api/3/issue/bulk
{ "issueUpdates": [ { "fields": { ... } }, { "fields": { ... } } ] }
```

---

## Key Gotchas

- **ADF vs plain text** — All rich-text fields (description, comment body) use Atlassian Document Format (ADF), not plain text or Markdown. Sending a plain string will fail or produce garbage.
- **accountId, not username** — User fields take `accountId` (a UUID-like string), not username or email. Resolve via `GET /rest/api/3/user/search?query=email`.
- **Unbounded JQL banned** — Search endpoints reject JQL with no project/date constraint. Always add a limiting clause.
- **v2 vs v3 field differences** — v3 returns ADF for description; v2 returns plain HTML. Pick one version and stay consistent.
- **Issue key vs issue ID** — Most endpoints accept either; prefer the key (e.g., `PROJ-123`) for readability.
- **Bulk operations have different rate costs** — Returning 100 issues in one search call is far cheaper in points than 100 separate `GET /issue/{key}` calls.
