---
name: github
description: >
  Expert guide for working with GitHub's APIs, features, and platform. Use this
  skill whenever the user wants to interact with GitHub repositories, issues,
  pull requests, Actions workflows, webhooks, releases, packages, security
  features, organizations, teams, or authentication; call the GitHub REST or
  GraphQL API; build or configure GitHub Apps or OAuth Apps; set up or debug
  CI/CD pipelines with GitHub Actions; configure branch protection or
  environments; work with GitHub Packages or ghcr.io; query the code search or
  global search API; manage Dependabot, code scanning, or secret scanning
  alerts; or understand any GitHub platform concept. Trigger for any request
  mentioning GitHub, gh CLI, GITHUB_TOKEN, Actions, workflows, octokit, pull
  requests, issues, repos, branches, forks, releases, GitHub Apps, webhooks,
  PAT, or GHCR — even if the user only says "our repo", "our pipeline", or
  "our CI" in a context that implies GitHub.
---

# GitHub Skill

## Platform Overview

GitHub exposes two primary APIs and a rich set of platform features:

| Interface | Base / Endpoint | Best for |
|---|---|---|
| **REST API** | `https://api.github.com` | CRUD operations, straightforward resource access |
| **GraphQL API** | `https://api.github.com/graphql` | Complex queries, related data in one round-trip |
| **GitHub CLI (`gh`)** | local binary | Scripting, local automation, interactive use |
| **Webhooks** | your server receives POSTs | Event-driven integrations |
| **GitHub Actions** | `.github/workflows/*.yml` | CI/CD, automation within GitHub |

---

## Authentication

All API requests require authentication. See `references/auth.md` for full details on each method.

| Method | Header | Best for |
|---|---|---|
| Fine-grained PAT | `Authorization: Bearer TOKEN` | Personal automation, scoped to specific repos |
| Classic PAT | `Authorization: Bearer TOKEN` | Broad access, legacy integrations |
| GitHub App installation token | `Authorization: Bearer TOKEN` | Apps acting on behalf of an org/repo |
| OAuth token | `Authorization: Bearer TOKEN` | User-facing applications |
| `GITHUB_TOKEN` | `Authorization: Bearer ${{ secrets.GITHUB_TOKEN }}` | GitHub Actions only, auto-provisioned |

Every request also needs:
```
Accept: application/vnd.github+json
X-GitHub-Api-Version: 2022-11-28
User-Agent: YourAppName
```

---

## REST API Essentials

### Rate Limits

| Auth type | Requests/hour |
|---|---|
| Authenticated (PAT/App) | 5,000 |
| GitHub App (large installation) | up to 15,000 |
| Unauthenticated | 60 |
| Search API (authenticated) | 30/min |
| Search API (unauthenticated) | 10/min |

Rate limit headers on every response:
```
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4987
X-RateLimit-Reset: 1372700873   # Unix timestamp
X-RateLimit-Used: 13
X-RateLimit-Resource: core
```

On 429 or 403 (secondary rate limit), check `Retry-After` header.

Query current limits: `GET /rate_limit`

### Pagination

```
GET /repos/{owner}/{repo}/issues?per_page=100&page=2
```

- `per_page` max: 100 (default 30)
- Parse `Link` header for cursor navigation:
  ```
  Link: <https://api.github.com/...?page=3>; rel="next",
        <https://api.github.com/...?page=10>; rel="last"
  ```
- `rel` values: `next`, `prev`, `first`, `last`
- When `Link` has no `next`, you're on the last page

### Errors

```json
{
  "message": "Validation Failed",
  "errors": [{ "resource": "Issue", "field": "title", "code": "missing_field" }],
  "documentation_url": "https://docs.github.com/..."
}
```

Common codes: `missing_field`, `already_exists`, `invalid`, `custom`

### Conditional Requests (caching)

```
If-None-Match: "644b5b0155e6404a9cc4bd9d8b1ae730"
If-Modified-Since: Thu, 05 Jul 2012 15:31:30 GMT
```

`304 Not Modified` response means data hasn't changed — use your cached copy and it doesn't count against rate limits.

---

## Key Resource Areas

See the reference files below for endpoint details. Quick orientation:

| Area | Reference | Key tables/endpoints |
|---|---|---|
| Repositories, branches, contents, git data | `references/repositories.md` | `/repos/{owner}/{repo}`, `/repos/{owner}/{repo}/contents/{path}` |
| Issues, labels, milestones, comments | `references/issues-prs.md` | `/repos/{owner}/{repo}/issues` |
| Pull requests, reviews, merge | `references/issues-prs.md` | `/repos/{owner}/{repo}/pulls` |
| Releases and release assets | `references/releases-packages.md` | `/repos/{owner}/{repo}/releases` |
| GitHub Packages, ghcr.io | `references/releases-packages.md` | `/orgs/{org}/packages`, `ghcr.io` |
| Actions workflows, runs, jobs, secrets | `references/actions.md` | `/repos/{owner}/{repo}/actions/` |
| Webhooks, events, payloads | `references/webhooks.md` | `/repos/{owner}/{repo}/hooks` |
| GraphQL queries and mutations | `references/graphql.md` | `POST /graphql` |
| GitHub Apps, OAuth Apps, JWT auth | `references/auth.md` | `/app`, `/app/installations` |
| Code scanning, secret scanning, Dependabot | `references/security.md` | `/repos/{owner}/{repo}/code-scanning/alerts` |
| Search (repos, code, issues, users) | `references/search.md` | `/search/repositories`, `/search/code` |
| Organizations, teams, members | `references/orgs-teams.md` | `/orgs/{org}`, `/orgs/{org}/teams` |

---

## Reference Files

| File | Load when… |
|---|---|
| `references/auth.md` | Setting up PATs, GitHub Apps (JWT + installation tokens), OAuth flows, GITHUB_TOKEN permissions |
| `references/repositories.md` | Repo CRUD, branch/tag management, file contents API, git data (commits, trees, refs) |
| `references/issues-prs.md` | Issues, labels, milestones, PR creation/review/merge, checks API |
| `references/actions.md` | Workflow syntax, triggers, contexts, expressions, secrets, artifacts, reusable workflows, Actions REST API |
| `references/webhooks.md` | Creating webhooks, event types, payload shapes, HMAC validation |
| `references/graphql.md` | GraphQL queries/mutations, pagination (edges/nodes), rate limits, common operations |
| `references/releases-packages.md` | Releases, assets, GitHub Packages (npm/Docker/Maven/etc.), ghcr.io |
| `references/security.md` | Code scanning, secret scanning, Dependabot alerts, security advisories, branch protection |
| `references/search.md` | Repository, code, issue, commit, user search — qualifier syntax and rate limits |
| `references/orgs-teams.md` | Org management, teams, permissions, members, outside collaborators, org-level secrets |

---

## Common Patterns

### List all open PRs for a repo
```
GET /repos/{owner}/{repo}/pulls?state=open&per_page=100
```

### Create an issue
```http
POST /repos/{owner}/{repo}/issues
{"title": "Bug: login fails", "body": "Steps to reproduce...", "labels": ["bug"], "assignees": ["username"]}
```

### Trigger a workflow manually
```http
POST /repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches
{"ref": "main", "inputs": {"environment": "staging"}}
```

### Get file contents
```
GET /repos/{owner}/{repo}/contents/path/to/file.txt
```
Response includes `content` (base64-encoded) and `sha` (needed for updates).

### Update a file
```http
PUT /repos/{owner}/{repo}/contents/path/to/file.txt
{
  "message": "Update config",
  "content": "<base64-encoded content>",
  "sha": "<current file sha>"
}
```

### Merge a PR
```http
PUT /repos/{owner}/{repo}/pulls/{pull_number}/merge
{"merge_method": "squash", "commit_title": "feat: add login (#42)"}
```

---

## GitHub CLI (`gh`) Quick Reference

The `gh` CLI is often faster than raw API calls for interactive or scripted use:

```bash
gh repo clone owner/repo
gh issue list --state open --label bug
gh issue create --title "..." --body "..." --label bug
gh pr create --base main --head feature --title "..." --fill
gh pr merge 42 --squash
gh workflow run ci.yml --ref main
gh api /repos/owner/repo/releases --jq '.[0].tag_name'
gh release create v1.2.0 --notes "Changes..." ./dist/*
```

`gh api` passes raw REST calls with auth handled automatically. Combine with `--jq` for filtering.

---

## Guidance Notes

- **Owner/repo vs node ID** — REST uses `{owner}/{repo}` strings; GraphQL uses opaque global node IDs. Convert with `GET /repos/{owner}/{repo}` → `node_id` field, or query `repository(owner: "...", name: "...")` in GraphQL.

- **API versioning** — Always send `X-GitHub-Api-Version: 2022-11-28`. GitHub deprecates old behavior on a dated schedule and sends `Sunset` headers as warnings.

- **Secondary rate limits** — Triggered by too many concurrent requests or mutation-heavy patterns (creating many issues quickly). Space out writes; watch for `Retry-After`.

- **GitHub App vs PAT** — For production integrations against an org, prefer a GitHub App: it gets higher rate limits, scoped permissions, and audit-log attribution. PATs are simpler for personal automation.

- **Webhooks vs polling** — Prefer webhooks for event-driven workflows. Only poll if you can't receive webhooks (e.g., local dev). Cache ETags to reduce polling cost.
