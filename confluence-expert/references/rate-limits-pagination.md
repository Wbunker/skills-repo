# Confluence Rate Limits & Pagination Reference

## Rate Limiting (Cloud)

Confluence Cloud uses the same **points-based rate limiting** system as Jira Cloud (enforced March 2, 2026). Limits are applied per OAuth app (client_id) or per API token user account.

### Quota Tiers (Hourly)

| Plan | Hourly quota |
|---|---|
| Free | 65,000 pts/hr |
| Standard | 100,000 + (10 × users) pts/hr |
| Premium | 130,000 + (20 × users) pts/hr |
| Enterprise | 150,000 + (30 × users) pts/hr (max 500,000) |

### Rate Limit Response Headers

| Header | Description |
|---|---|
| `X-RateLimit-Limit` | Your hourly quota in points |
| `X-RateLimit-Remaining` | Points remaining in current window |
| `X-RateLimit-Reset` | Unix timestamp when the window resets |
| `Retry-After` | Seconds to wait after a 429 |

### Response on Throttle

```
HTTP 429 Too Many Requests
Retry-After: 30
Content-Type: application/json

{"statusCode": 429, "message": "Rate limit exceeded. Retry after 30 seconds."}
```

Always read the `Retry-After` header value (in seconds) and wait before retrying.

### General Guidance

- Burst limit: ~10 concurrent requests recommended maximum
- Page writes (create/update) cost more points than reads
- Bulk operations (fetching one page of 50 items) cost far fewer points than 50 individual GETs
- Use exponential backoff with jitter universally

Data Center does not enforce API rate limits by default; configurable by admins.

---

## Retry Strategy

```python
import time
import requests

def make_request_with_retry(method, url, max_retries=5, **kwargs):
    for attempt in range(max_retries):
        response = method(url, **kwargs)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 2 ** attempt))
            time.sleep(retry_after)
            continue

        if response.status_code >= 500:
            time.sleep(2 ** attempt)
            continue

        response.raise_for_status()
        return response

    raise Exception(f"Request failed after {max_retries} retries: {url}")
```

---

## Pagination — v1 API (Offset-Based)

v1 uses `start` and `limit` query parameters.

| Parameter | Default | Max | Description |
|---|---|---|---|
| `start` | 0 | — | Zero-based offset |
| `limit` | 25 | 100 (200 for some) | Items per page |

### Response Structure

```json
{
  "results": [...],
  "start": 0,
  "limit": 25,
  "size": 25,
  "_links": {
    "next": "/rest/api/content?spaceKey=ENG&start=25&limit=25",
    "self": "/rest/api/content?spaceKey=ENG&start=0&limit=25"
  }
}
```

- `size` — items returned in this page (may be less than `limit` on the last page)
- `_links.next` — absent on the last page; presence means more items exist
- Most v1 endpoints do NOT return a `total` count

### Generic v1 Paginator

```python
import requests

def paginate_v1(domain, auth, path, params=None, limit=50):
    """Yields all items from a v1 paginated endpoint."""
    base = f"https://{domain}.atlassian.net/wiki"
    params = dict(params or {})
    params["limit"] = limit
    params.setdefault("start", 0)

    while True:
        r = requests.get(
            f"{base}{path}", auth=auth, params=params,
            headers={"Accept": "application/json"}
        )
        r.raise_for_status()
        data = r.json()
        yield from data.get("results", [])

        if "_links" not in data or "next" not in data["_links"]:
            break
        params["start"] += data.get("size", limit)

# Usage:
for page in paginate_v1("mycompany", auth, "/rest/api/space/ENG/content/page"):
    print(page["title"])
```

---

## Pagination — v2 API (Cursor-Based)

v2 uses an opaque `cursor` token returned in `_links.next`.

### Response Structure

```json
{
  "results": [...],
  "_links": {
    "next": "/wiki/api/v2/pages?spaceId=98765&limit=50&cursor=eyJsaW1pdCI6NTB9",
    "self": "/wiki/api/v2/pages?spaceId=98765&limit=50"
  }
}
```

When `_links.next` is absent, you're on the last page.

### Generic v2 Paginator

```python
from urllib.parse import urlparse, parse_qs

def paginate_v2(domain, auth, path, params=None, limit=50):
    """Yields all items from a v2 cursor-paginated endpoint."""
    base = f"https://{domain}.atlassian.net"
    params = dict(params or {})
    params["limit"] = limit

    while True:
        r = requests.get(
            f"{base}{path}", auth=auth, params=params,
            headers={"Accept": "application/json"}
        )
        r.raise_for_status()
        data = r.json()
        yield from data.get("results", [])

        next_link = data.get("_links", {}).get("next")
        if not next_link:
            break

        qs = parse_qs(urlparse(next_link).query)
        cursor = qs.get("cursor", [None])[0]
        if not cursor:
            break

        # On cursor pages, pass only cursor + limit (drop original filters)
        params = {"cursor": cursor, "limit": limit}

# Usage:
for page in paginate_v2("mycompany", auth, "/wiki/api/v2/pages", {"spaceId": "98765"}):
    print(page["title"])
```

---

## Endpoint-Specific Limits

| Endpoint | Default | Max |
|---|---|---|
| `GET /rest/api/content` | 25 | 100 |
| `GET /rest/api/space` | 25 | 100 |
| `GET /rest/api/search` | 25 | 100 |
| `GET /rest/api/content/{id}/child/page` | 25 | 100 |
| `GET /rest/api/group` | 25 | 200 |
| `GET /wiki/api/v2/pages` | 25 | 250 |
| `GET /wiki/api/v2/spaces` | 25 | 250 |
| `GET /wiki/api/v2/blogposts` | 25 | 250 |

> Expanding `body.storage` or `body.export_view` in search caps results at **50** regardless of `limit`.

---

## Bulk Operations Pattern

For fetching all pages with body content from a large space:

```python
import time
import concurrent.futures

def fetch_body(domain, auth, page_id):
    r = requests.get(
        f"https://{domain}.atlassian.net/wiki/rest/api/content/{page_id}",
        auth=auth, params={"expand": "body.storage"},
        headers={"Accept": "application/json"}
    )
    r.raise_for_status()
    return r.json()

def export_space_pages(domain, auth, space_key, max_workers=5):
    ids = [p["id"] for p in paginate_v1(domain, auth, f"/rest/api/space/{space_key}/content/page")]
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(fetch_body, domain, auth, pid): pid for pid in ids}
        for f in concurrent.futures.as_completed(futures):
            try:
                results.append(f.result())
            except Exception as e:
                print(f"Failed {futures[f]}: {e}")
            time.sleep(0.1)
    return results
```

---

## Gotchas

- **`size` is page size, not total** — v1 responses rarely include a total count; check `_links.next` rather than comparing `size` to any total
- **v2 cursor is opaque** — extract from `_links.next` URL; don't construct or decode it manually
- **Clear params on v2 cursor pages** — pass *only* cursor and limit on subsequent calls; including original filter params alongside a cursor may cause unexpected behavior
- **Body expand limits search to 50** — expanding `body.storage` in search results overrides your `limit` and caps at 50
- **Rate limits apply per credential** — if multiple scripts share the same API token, they share the same quota pool
- **Data Center has no cursor** — offset pagination only; no `cursor` param
