# Jira Rate Limits & Pagination Reference

## Points-Based Rate Limiting (Enforced March 2026)

Jira Cloud no longer counts raw requests — it measures **points**, where each API call consumes points based on operational complexity.

### Points calculation
```
Total points = base cost + (object count × object cost)
```

| Object category | Cost per object |
|---|---|
| Core domain objects (Issues, Projects, Dashboards) | 1 pt |
| Identity & access (Users, Groups, Permissions) | 2 pts |
| Write / modify / delete operations | 1 pt (flat, regardless of scope) |
| Base cost per request | 1 pt |

**Examples:**
| Request | Points |
|---|---|
| `GET /issue/{key}` (1 issue) | ~2 pts |
| `GET /search/jql` returning 50 issues | ~51 pts |
| `GET /search/jql` returning 100 issues | ~101 pts |
| `POST /issue` (create 1) | ~2 pts |
| `POST /issue/bulk` (create 50) | ~51 pts |
| `GET /user` | ~3 pts |

**Implication:** Fetching 100 issues in one search call costs ~101 pts. Fetching them individually costs ~200 pts. Always prefer bulk/search over loops of single-resource GETs.

---

## Quota Tiers

| Plan | Hourly quota | Formula |
|---|---|---|
| Free | 65,000 pts/hr | fixed |
| Standard | 100,000 + (10 × users) pts/hr | scales with seat count |
| Premium | 130,000 + (20 × users) pts/hr | scales with seat count |
| Enterprise | 150,000 + (30 × users) pts/hr | max 500,000 pts/hr |

---

## Burst Limits (Per-Second)

In addition to the hourly quota:

| Operation type | Burst limit |
|---|---|
| GET / POST | 100 req/sec |
| PUT / DELETE | 50 req/sec |
| Per-issue writes | 20 ops/2s, 100 ops/30s |

---

## Rate Limit Response Headers

Returned on every response:

| Header | Meaning |
|---|---|
| `X-RateLimit-Limit` | Maximum quota for the period |
| `X-RateLimit-Remaining` | Points/requests remaining |
| `X-RateLimit-Reset` | Unix timestamp when quota resets (included on 429) |
| `RateLimit-Reason` | Which limit was hit: `QuotaExceeded`, `BurstLimitExceeded`, `PerIssueLimitExceeded` |
| `Retry-After` | Seconds to wait before retrying |
| `Beta-RateLimit-Policy` | (Informational) quota definition |
| `Beta-RateLimit` | (Informational) remaining + reset |

When you receive `HTTP 429 Too Many Requests`, always read `Retry-After` and `RateLimit-Reason`.

---

## Retry Strategy

### By `RateLimit-Reason`

| Reason | Strategy |
|---|---|
| `QuotaExceeded` (hourly) | Pause ALL requests until `X-RateLimit-Reset` timestamp |
| `BurstLimitExceeded` | Slow down this specific endpoint; add delay between calls |
| `PerIssueLimitExceeded` | Add delays between writes to the same issue |

### Exponential backoff with jitter (Python)

```python
import time
import random
import requests

def jira_request_with_retry(method, url, max_retries=4, **kwargs):
    for attempt in range(max_retries + 1):
        response = requests.request(method, url, **kwargs)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 2 ** attempt))
            jitter = random.uniform(0, 1)
            wait = retry_after + jitter
            print(f"Rate limited. Waiting {wait:.1f}s (attempt {attempt+1})")
            time.sleep(wait)
            continue

        response.raise_for_status()
        return response

    raise Exception(f"Max retries exceeded for {url}")
```

### Backoff schedule
- Attempt 1: wait 2s + jitter
- Attempt 2: wait 4s + jitter
- Attempt 3: wait 8s + jitter
- Attempt 4: wait 16s + jitter
- Cap retries at 4; surface error to caller after that

---

## Optimization Strategies

### Request only needed fields
Every field costs points. Exclude what you don't need:
```
GET /rest/api/3/search/jql?jql=...&fields=summary,status,assignee
```

### Use search instead of individual GETs
```python
# SLOW (100 pts × N issues):
for key in issue_keys:
    issue = get(f"/issue/{key}")

# FAST (101 pts for 100 issues):
issues = post("/search/jql", json={
    "jql": f"issueKey in ({','.join(issue_keys)})",
    "fields": ["summary", "status"]
})
```

### Cache stable data
Project lists, issue types, workflow schemes, and user data change infrequently. Cache them with a TTL of 5–60 minutes.

### Spread writes over time
For bulk updates to many issues, add small delays (50–100ms) between writes to stay under per-issue limits:
```python
for issue_key in issues_to_update:
    update_issue(issue_key, fields)
    time.sleep(0.1)  # 100ms between writes
```

### Use webhooks instead of polling
Polling `GET /search/jql` every minute to detect changes costs points continuously. A webhook fires only when something happens — far more efficient and real-time.

### Batch bulk operations
Use `/rest/api/3/issue/bulk` for creating multiple issues instead of looping `POST /issue`.

---

## Pagination

### Offset-based pagination (most endpoints)

```
GET /rest/api/3/search/jql?jql=project=PROJ&startAt=0&maxResults=100
```

Response:
```json
{
  "startAt": 0,
  "maxResults": 100,
  "total": 342,
  "issues": [...]
}
```

Advance: `startAt += maxResults` until `startAt >= total`.

```python
def paginate_jql(jira, jql, fields, page_size=100):
    start = 0
    while True:
        data = jira.post("/rest/api/3/search/jql", json={
            "jql": jql,
            "fields": fields,
            "startAt": start,
            "maxResults": page_size
        }).json()

        yield from data["issues"]

        start += page_size
        if start >= data["total"]:
            break
```

`maxResults` cap is **100** for most search endpoints. Requesting more than 100 returns 100 with no error.

### Cursor-based pagination (newer endpoints, e.g., project search)

Response:
```json
{
  "isLast": false,
  "nextPageToken": "eyJsaW1pdCI6NTAsInN0YXJ0Ijo1MH0="
}
```

Next request:
```
GET /rest/api/3/project/search?nextPageToken=eyJsaW1pdCI6NTAsInN0YXJ0Ijo1MH0=
```

Cursor tokens are opaque — do not attempt to decode or construct them manually. Continue until `isLast: true` or no `nextPageToken` in response.

### Which style to use

| Endpoint | Pagination style |
|---|---|
| `/rest/api/3/search/jql` | Offset (`startAt` / `maxResults` / `total`) |
| `/rest/api/3/project/search` | Cursor (`nextPageToken`) |
| `/rest/api/3/issue/{key}/comment` | Offset |
| `/rest/api/3/issue/{key}/worklog` | Offset |
| `/rest/api/3/users/search` | Offset |
| `/rest/agile/1.0/board` | Offset |
| `/rest/agile/1.0/board/{id}/sprint` | Offset |

When in doubt, check the response — if it contains `total`, use offset. If it contains `nextPageToken`, use cursor.
