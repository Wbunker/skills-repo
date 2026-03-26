# Pagination, Error Handling, and Best Practices — YouTube Data API v3

---

## Pagination with pageToken

Most `list` methods support pagination via `nextPageToken` and `prevPageToken`.

### How It Works

1. Make initial request — response includes `nextPageToken` if more results exist
2. Pass `nextPageToken` as `pageToken` in next request
3. Continue until no `nextPageToken` in response

### Response Structure (pagination fields)

```json
{
  "kind": "youtube#videoListResponse",
  "nextPageToken": "CAUQAA",
  "prevPageToken": "CAoQAA",
  "pageInfo": {
    "totalResults": 1337,
    "resultsPerPage": 50
  },
  "items": [...]
}
```

**Note:** `pageInfo.totalResults` is often an estimate (approximate), not an exact count.

### Standard Pagination Pattern

```python
def paginate_all(youtube_list_method, **kwargs):
    """Generic helper to collect all pages of results."""
    all_items = []
    next_page_token = None

    while True:
        response = youtube_list_method(
            **kwargs,
            pageToken=next_page_token
        ).execute()

        all_items.extend(response.get('items', []))
        next_page_token = response.get('nextPageToken')

        if not next_page_token:
            break

    return all_items

# Usage example:
videos = paginate_all(
    youtube.playlistItems().list,
    part='snippet,contentDetails',
    playlistId='PLxxxxxx',
    maxResults=50
)
```

### maxResults Limits by Resource

| Resource | Max per Page | Default |
|----------|-------------|---------|
| videos.list | 50 | 5 |
| channels.list | 50 | 5 |
| playlists.list | 50 | 5 |
| playlistItems.list | 50 | 5 |
| search.list | 50 | 5 |
| commentThreads.list | 100 | 20 |
| comments.list | 100 | 20 |
| subscriptions.list | 50 | 5 |
| liveBroadcasts.list | 50 | 5 |

**Always set maxResults to the maximum** to minimize API calls and quota consumption.

---

## Error Handling

### Common Error Response Format

```json
{
  "error": {
    "code": 403,
    "message": "The caller does not have permission",
    "errors": [
      {
        "message": "The caller does not have permission",
        "domain": "youtube.quota",
        "reason": "quotaExceeded"
      }
    ]
  }
}
```

### Error Codes and Reasons

| HTTP Code | Reason | Description | Action |
|-----------|--------|-------------|--------|
| 400 | `invalidPart` | Invalid `part` parameter value | Fix request |
| 400 | `missingRequiredParameter` | Required parameter missing | Fix request |
| 400 | `invalidChannelId` | Channel ID format invalid | Fix channel ID |
| 401 | `authorizationRequired` | Authentication required | Add OAuth token |
| 403 | `quotaExceeded` | Daily quota exhausted | Wait for reset (midnight PT) |
| 403 | `userRateLimitExceeded` | Per-user rate limit exceeded | Backoff and retry |
| 403 | `forbidden` | Operation not permitted | Check scopes/ownership |
| 403 | `commentsDisabled` | Comments turned off for video | Skip video |
| 404 | `videoNotFound` | Video ID does not exist | Skip or handle |
| 404 | `channelNotFound` | Channel ID does not exist | Skip or handle |
| 404 | `playlistNotFound` | Playlist does not exist | Skip or handle |
| 409 | `subscriptionDuplicate` | Already subscribed | Handle gracefully |
| 500 | `internalError` | Transient server error | Exponential backoff |
| 503 | `serviceUnavailable` | Service temporarily unavailable | Exponential backoff |

### Catching Errors with Python Client

```python
from googleapiclient.errors import HttpError

try:
    response = youtube.videos().list(
        part='snippet',
        id='VIDEO_ID'
    ).execute()
except HttpError as e:
    error_code = e.resp.status
    error_reason = e.error_details[0]['reason'] if e.error_details else 'unknown'

    if error_code == 403 and error_reason == 'quotaExceeded':
        print("Quota exhausted. Wait until midnight PT.")
    elif error_code == 403 and error_reason == 'userRateLimitExceeded':
        # Retry with backoff
        pass
    elif error_code == 404:
        print(f"Resource not found: {e}")
    else:
        raise
```

---

## Exponential Backoff

For transient errors (5xx, `userRateLimitExceeded`), implement exponential backoff with jitter.

### Pattern

```python
import time
import random
from googleapiclient.errors import HttpError

RETRYABLE_STATUS_CODES = {500, 502, 503, 504}
RETRYABLE_REASONS = {'userRateLimitExceeded', 'rateLimitExceeded', 'backendError'}

def execute_with_backoff(request, max_retries=5):
    """Execute an API request with exponential backoff on transient errors."""
    for attempt in range(max_retries):
        try:
            return request.execute()

        except HttpError as e:
            error_code = e.resp.status
            error_reason = ''

            if e.error_details:
                error_reason = e.error_details[0].get('reason', '')

            # Determine if retryable
            is_retryable = (
                error_code in RETRYABLE_STATUS_CODES or
                error_reason in RETRYABLE_REASONS
            )

            if not is_retryable or attempt == max_retries - 1:
                raise

            # Exponential backoff: 2^attempt seconds + random jitter
            sleep_time = (2 ** attempt) + random.uniform(0, 1)
            print(f"Attempt {attempt + 1} failed ({error_code}/{error_reason}). "
                  f"Retrying in {sleep_time:.1f}s...")
            time.sleep(sleep_time)

    raise Exception("Max retries exceeded")

# Usage:
try:
    response = execute_with_backoff(
        youtube.videos().list(part='snippet', id='VIDEO_ID')
    )
except HttpError as e:
    print(f"Non-retryable error: {e}")
```

### Backoff Schedule

| Attempt | Wait (base) | With jitter |
|---------|-------------|-------------|
| 1 | 2s | 2.0–3.0s |
| 2 | 4s | 4.0–5.0s |
| 3 | 8s | 8.0–9.0s |
| 4 | 16s | 16.0–17.0s |
| 5 | 32s | 32.0–33.0s |

**Do not retry** `quotaExceeded` (403) — quota won't recover until midnight PT. Do not retry `forbidden` (403), `notFound` (404), or client errors (4xx) without fixing the request.

---

## Rate Limiting

### Per-User Rate Limits

In addition to the daily quota, YouTube enforces per-user rate limits to prevent individual users from consuming excessive resources in a short window. The `userRateLimitExceeded` error indicates this limit was hit.

**Mitigation:**
- Add delays between requests in batch operations
- Implement the backoff pattern above
- Spread requests over time rather than bursting

### Recommended Request Pacing

For bulk operations, add a small delay between pages:

```python
import time

next_page_token = None
while True:
    response = youtube.playlistItems().list(
        part='snippet',
        playlistId='PLAYLIST_ID',
        maxResults=50,
        pageToken=next_page_token
    ).execute()

    process_items(response['items'])

    next_page_token = response.get('nextPageToken')
    if not next_page_token:
        break

    time.sleep(0.1)  # 100ms delay between pages
```

---

## ETags and Conditional Requests

ETags reduce redundant data transfer when content hasn't changed. The quota cost is still charged, but bandwidth and parse time are saved.

```python
# Save ETag from first response
response = youtube.videos().list(part='statistics', id='VIDEO_ID').execute()
etag = response['etag']

# The Python client library uses http.request objects; to pass ETags manually:
# Include 'If-None-Match: ETAG' header in subsequent requests
# 304 Not Modified returned if unchanged
```

---

## The `fields` Parameter

Reduces response payload size without affecting quota cost. Uses XPath-like syntax.

```python
# Return only video IDs and view counts
response = youtube.videos().list(
    part='statistics',
    id='dQw4w9WgXcQ',
    fields='items(id,statistics(viewCount))'
).execute()
# Response: {"items": [{"id": "dQw4w9WgXcQ", "statistics": {"viewCount": "1400000000"}}]}

# Return only snippet title and channel
response = youtube.search().list(
    part='snippet',
    q='python',
    fields='items(id,snippet(title,channelTitle)),nextPageToken'
).execute()
```

### Fields Syntax

| Syntax | Meaning |
|--------|---------|
| `items` | Top-level field |
| `items(id,snippet)` | Specific subfields |
| `items/snippet/title` | Nested path |
| `items(snippet(title,description))` | Nested selection |
| `nextPageToken,items(id)` | Multiple top-level fields |

---

## Best Practices Summary

### Request Efficiency
- Always set `maxResults` to the maximum allowed value
- Batch video ID lookups (up to 50 per `videos.list` call)
- Use `fields` parameter to limit response size
- Cache responses: static data 24h, dynamic data 1–6h
- Request only needed `part` values

### Cost Optimization
- Prefer `playlistItems.list` over `search.list` for channel video enumeration
- Use `videos.list(id=...)` over `search.list` when you have video IDs
- Use `channels.list(forHandle=...)` over `search.list` for channel lookup
- Monitor quota in Google Cloud Console daily

### Error Resilience
- Implement exponential backoff for 5xx errors and `userRateLimitExceeded`
- Never retry `quotaExceeded` until after midnight PT reset
- Handle `commentsDisabled` gracefully (skip, don't fail)
- Check that `items` array is non-empty before accessing `items[0]`

### Authentication
- Store `token.json` / `token.pickle` securely; never commit to version control
- Store `credentials.json` / `client_secret.json` securely
- Request only the scopes your application actually needs (principle of least privilege)
- Handle token expiry and refresh proactively

### Upload Best Practices
- Always use resumable upload for video files of any size
- Use 10 MB chunks for reliable networks; smaller chunks for unreliable
- Implement resume logic for long uploads
- Poll `processingDetails.processingStatus` until `succeeded` before publishing

---

## Complete Robust API Client Pattern

```python
import os
import time
import random
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def get_youtube():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as f:
            f.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)


def api_call(request, max_retries=5):
    for attempt in range(max_retries):
        try:
            return request.execute()
        except HttpError as e:
            code = e.resp.status
            reason = (e.error_details[0].get('reason', '')
                      if e.error_details else '')
            if code in (500, 502, 503, 504) or reason in (
                    'userRateLimitExceeded', 'rateLimitExceeded'):
                if attempt < max_retries - 1:
                    wait = (2 ** attempt) + random.random()
                    time.sleep(wait)
                    continue
            raise
    raise RuntimeError("Max retries exceeded")


def get_all_pages(list_method, **kwargs):
    items = []
    page_token = None
    while True:
        resp = api_call(list_method(**kwargs, pageToken=page_token,
                                    maxResults=50))
        items.extend(resp.get('items', []))
        page_token = resp.get('nextPageToken')
        if not page_token:
            break
    return items
```
