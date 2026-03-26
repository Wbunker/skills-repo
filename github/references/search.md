# GitHub Search API

## Table of Contents
1. [Overview and Rate Limits](#overview-and-rate-limits)
2. [Search Endpoints](#search-endpoints)
3. [Qualifier Syntax](#qualifier-syntax)
4. [Repository Search](#repository-search)
5. [Code Search](#code-search)
6. [Issues and PR Search](#issues-and-pr-search)
7. [Commit Search](#commit-search)
8. [User and Org Search](#user-and-org-search)
9. [Topic Search](#topic-search)
10. [Text Match Highlighting](#text-match-highlighting)

---

## Overview and Rate Limits

Search is a separate API with its own rate limits:

| Auth state | Limit |
|---|---|
| Authenticated | 30 requests/minute |
| Unauthenticated | 10 requests/minute |

All search endpoints return up to 1,000 results (10 pages × 100 results). Use more specific qualifiers to narrow results rather than paginating through thousands.

Base pattern:
```
GET /search/{type}?q={query}&sort={field}&order=desc&per_page=100&page=1
```

Response envelope:
```json
{
  "total_count": 1872,
  "incomplete_results": false,
  "items": [...]
}
```

`incomplete_results: true` means the search timed out and results are partial.

---

## Search Endpoints

| Type | Endpoint | Sort options |
|---|---|---|
| Repositories | `GET /search/repositories` | stars, forks, help-wanted-issues, updated |
| Code | `GET /search/code` | indexed (only option) |
| Issues & PRs | `GET /search/issues` | comments, reactions, reactions-+1, reactions--1, reactions-smile, reactions-thinking_face, reactions-heart, reactions-tada, interactions, created, updated |
| Commits | `GET /search/commits` | author-date, committer-date |
| Users | `GET /search/users` | followers, repositories, joined |
| Topics | `GET /search/topics` | (none) |
| Labels | `GET /search/labels` | name, created, updated |

`order` param: `asc` or `desc` (default `desc`)

---

## Qualifier Syntax

Qualifiers narrow search to specific fields. Format: `qualifier:value` — no spaces around `:`.

**Combining qualifiers:**
- Multiple qualifiers in `q` are ANDed: `q=login+error+repo:octocat/hello-world`
- OR: `q=cats OR dogs`
- NOT: `q=cats NOT dogs` or `q=cats -dogs`
- Exact phrase: `q="null pointer exception"`
- Range: `q=stars:>100` `q=size:10..100` `q=created:>=2023-01-01`

**Date range formats:**
- `created:2023-01-01` — exact date
- `created:>=2023-01-01` — on or after
- `created:2023-01-01..2023-12-31` — between
- `created:>2023-01-01` — after (exclusive)

---

## Repository Search

**Common qualifiers:**

| Qualifier | Example | Meaning |
|---|---|---|
| `in:name` | `q=react in:name` | Name contains term |
| `in:description` | `q=kubernetes in:description` | Description contains term |
| `in:readme` | `q=graphql in:readme` | README contains term |
| `in:topics` | `q=machine-learning in:topics` | Has topic |
| `user:` | `q=user:torvalds` | Owned by user |
| `org:` | `q=org:github` | Owned by org |
| `repo:` | `q=repo:rails/rails` | Specific repo |
| `language:` | `q=language:python` | Primary language |
| `stars:` | `q=stars:>1000` | Star count |
| `forks:` | `q=forks:>50` | Fork count |
| `size:` | `q=size:<10000` | Repo size in KB |
| `is:public` / `is:private` | | Visibility |
| `mirror:true` | | Is a mirror |
| `archived:true` | | Is archived |
| `template:true` | | Is a template |
| `topic:` | `q=topic:docker` | Has specific topic |
| `topics:` | `q=topics:>5` | Number of topics |
| `license:` | `q=license:mit` | License type (SPDX identifier) |
| `created:` | `q=created:2023-01-01..2024-01-01` | Creation date |
| `pushed:` | `q=pushed:>2024-01-01` | Last push date |
| `followers:` | `q=followers:>100` | (user search) |
| `has:` | `q=has:sponsorship-file` | Has specific file |
| `good-first-issues:` | `q=good-first-issues:>3` | Issues labeled as good first issue |
| `help-wanted-issues:` | `q=help-wanted-issues:>5` | Help wanted issues count |

**Example — top Python ML repos updated recently:**
```
GET /search/repositories?q=machine-learning+language:python+stars:>500&sort=updated&order=desc
```

---

## Code Search

Code search indexes the default branch of public repositories. For private repos, the user must have access.

**Important limitations:**
- Files > 384 KB are not indexed
- Binary files not indexed
- Vendor/generated code may be excluded
- Results limited to 1,000

**Qualifiers:**

| Qualifier | Example | Meaning |
|---|---|---|
| `repo:` | `q=addClass+repo:jquery/jquery` | Search in specific repo |
| `org:` | `q=import+org:github` | Search across org repos |
| `user:` | `q=octokit+user:github` | Search user's repos |
| `path:` | `q=main+path:app/models` | File path contains |
| `path:` (extension) | `q=path:*.yml` | File extension |
| `language:` | `q=const+language:javascript` | Language |
| `filename:` | `q=filename:Dockerfile` | Exact filename |
| `extension:` | `q=extension:rb` | File extension |
| `in:file` | `q=class Foo in:file` | Match in file content |
| `in:path` | `q=app/models in:path` | Match in file path |

**Example — find all Dockerfiles in a GitHub org:**
```
GET /search/code?q=filename:Dockerfile+org:myorg
```

**Example — find usages of a deprecated function:**
```
GET /search/code?q=oldFunction+language:javascript+repo:owner/repo
```

---

## Issues and PR Search

The `/search/issues` endpoint searches both issues and pull requests.

**Qualifiers:**

| Qualifier | Example | Meaning |
|---|---|---|
| `type:issue` / `type:pr` | | Filter to issues or PRs only |
| `is:open` / `is:closed` / `is:merged` | | State |
| `is:issue` / `is:pr` | | Same as type: |
| `is:public` / `is:private` | | Repo visibility |
| `repo:` | `q=bug+repo:owner/repo` | Specific repo |
| `user:` | `q=type:pr+user:octocat` | PRs by user |
| `org:` | | Org repos |
| `assignee:` | `q=assignee:username` | Assigned to user |
| `author:` | `q=author:username` | Created by user |
| `mentions:` | `q=mentions:username` | Mentions user |
| `commenter:` | `q=commenter:username` | Commented by user |
| `involves:` | `q=involves:username` | Any involvement |
| `label:` | `q=label:bug+label:help-wanted` | Has label(s) |
| `milestone:` | `q=milestone:"v2.0"` | In milestone |
| `project:` | `q=project:org/1` | In project |
| `no:label` / `no:milestone` / `no:assignee` | | Missing metadata |
| `language:` | `q=bug+language:go` | Repo language |
| `state:` | `q=state:closed` | Same as is:closed |
| `created:` | `q=created:>=2024-01-01` | Creation date |
| `updated:` | `q=updated:>=2024-01-01` | Last update |
| `closed:` | `q=closed:2024-01-01..2024-06-01` | Close date |
| `merged:` | `q=merged:>=2024-01-01` | PR merge date |
| `comments:` | `q=comments:>10` | Comment count |
| `reactions:` | `q=reactions:>5` | Reaction count |
| `interactions:` | | Comments + reactions |
| `linked:` | `q=linked:pr` | Linked to a PR |
| `is:draft` | | Draft PR |
| `review:required` | | Review required |
| `review:approved` | | PR approved |
| `review:changes_requested` | | Changes requested |
| `reviewed-by:` | `q=reviewed-by:username` | Reviewed by |
| `review-requested:` | `q=review-requested:username` | Review requested from |
| `team-review-requested:` | | Team review requested |
| `head:` / `base:` | `q=head:feature-branch` | PR branch names |

**Example — open bugs assigned to no one, not labeled as wontfix:**
```
GET /search/issues?q=type:issue+is:open+label:bug+no:assignee+-label:wontfix+repo:owner/repo
```

---

## Commit Search

Searches commits on the default and non-protected branches of public repos.

**Qualifiers:**

| Qualifier | Example | Meaning |
|---|---|---|
| `repo:` | `q=fix+repo:owner/repo` | Specific repo |
| `user:` | | User's public repos |
| `org:` | | Org repos |
| `author:` | `q=author:username` | Commit author login |
| `author-name:` | `q=author-name:"John Doe"` | Author display name |
| `author-email:` | `q=author-email:john@example.com` | Author email |
| `committer:` | `q=committer:username` | Committer login |
| `committer-name:` | | Committer name |
| `committer-email:` | | Committer email |
| `author-date:` | `q=author-date:>=2024-01-01` | Commit author date |
| `committer-date:` | | Committer date |
| `merge:true` / `merge:false` | | Is a merge commit |
| `hash:` | `q=hash:abc1234` | Specific commit SHA |
| `parent:` | `q=parent:abc1234` | Parent commit |
| `tree:` | `q=tree:abc1234` | Specific tree |
| `is:public` / `is:private` | | Repo visibility |

---

## User and Org Search

```
GET /search/users?q={query}
```

**Qualifiers:**

| Qualifier | Example | Meaning |
|---|---|---|
| `type:user` / `type:org` | | Filter to users or orgs |
| `in:login` | `q=tom in:login` | Username contains |
| `in:email` | | Email contains |
| `in:name` | | Display name contains |
| `fullname:` | `q=fullname:"Tom Preston"` | Full name |
| `repos:` | `q=repos:>50` | Public repo count |
| `location:` | `q=location:Berlin` | Profile location |
| `language:` | `q=language:rust` | Used language |
| `created:` | | Account creation date |
| `followers:` | `q=followers:>1000` | Follower count |
| `is:sponsorable` | | Has GitHub Sponsors |

---

## Topic Search

```
GET /search/topics?q={query}
Accept: application/vnd.github+json
```

Topics are repository tags like `machine-learning`, `web-development`, etc.

**Qualifiers:**
- `is:featured` — curated by GitHub
- `is:not-featured`
- `is:curated`
- `repositories:>100` — topics used by many repos
- `created:` — topic creation date

Response items include: `name`, `display_name`, `short_description`, `description`, `created_by`, `featured`, `curated`, `aliases`

---

## Text Match Highlighting

Request highlighted matches for display purposes:

```
Accept: application/vnd.github.text-match+json
```

Items in the response gain a `text_matches` array:
```json
{
  "text_matches": [
    {
      "object_url": "https://api.github.com/...",
      "object_type": "Issue",
      "property": "body",
      "fragment": "...context around the **match**...",
      "matches": [
        { "text": "match", "indices": [25, 30] }
      ]
    }
  ]
}
```

Use this when building search UIs that highlight the matching text.
