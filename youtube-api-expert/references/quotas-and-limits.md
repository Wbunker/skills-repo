# YouTube API — Quotas, Rate Limits & Error Handling

## Quota System Overview

- Default quota: **10,000 units per day** per project
- Quota resets at **midnight Pacific Time**
- Quota is per **Google Cloud project**, shared across all API keys and OAuth clients in that project

---

## Quota Cost by Method

### YouTube Data API v3

| Method | Cost (units) |
|--------|-------------|
| `channels.list` | 1 |
| `videos.list` | 1 |
| `playlists.list` | 1 |
| `playlistItems.list` | 1 |
| `subscriptions.list` | 1 |
| `comments.list` | 1 |
| `commentThreads.list` | 1 |
| `captions.list` | 50 |
| `search.list` | 100 |
| `channels.update` | 50 |
| `videos.update` | 50 |
| `playlists.insert` | 50 |
| `playlists.update` | 50 |
| `playlists.delete` | 50 |
| `playlistItems.insert` | 50 |
| `playlistItems.update` | 50 |
| `playlistItems.delete` | 50 |
| `subscriptions.insert` | 50 |
| `subscriptions.delete` | 50 |
| `comments.insert` | 50 |
| `comments.update` | 50 |
| `commentThreads.insert` | 50 |
| `videos.insert` (upload) | 1600 |
| `videos.delete` | 50 |
| `thumbnails.set` | 50 |
| `captions.insert` | 400 |
| `captions.update` | 400 |
| `livebroadcasts.insert` | 50 |
| `livebroadcasts.bind` | 50 |
| `livebroadcasts.transition` | 50 |

### Budget Planning Example

With 10,000 units/day:
- 100 reads (`videos.list`): costs 100 units
- 10 uploads: costs 16,000 units — **exceeds daily quota alone**
- 100 searches: costs 10,000 units — **uses entire daily quota**

For high-volume upload pipelines, request a quota increase.

---

## Quota Increase

1. Go to Google Cloud Console → APIs & Services → Quotas
2. Filter by "YouTube Data API v3"
3. Click "YouTube Data API v3 — Queries per day" or similar
4. Request increase — provide justification
5. Approval typically takes 2–7 business days

Alternatively: use multiple Google Cloud projects (each gets 10,000 units/day) — but this can violate ToS if done to circumvent limits. Only do this for legitimate separate services.

---

## Rate Limits

Beyond quota, the API enforces rate limits:
- Requests per 100 seconds (user): 100 requests
- Requests per 100 seconds (project): 10,000 requests

These are usually not hit unless making requests in a tight loop without backoff.

---

## Error Handling

### Common Errors

| HTTP Code | Reason | Meaning | Action |
|-----------|--------|---------|--------|
| 400 | `invalidPart` | Invalid `part` parameter | Fix request |
| 400 | `missingRequiredParameter` | Required field missing | Fix request |
| 400 | `invalidChannelId` | Bad channel ID format | Fix channel ID |
| 401 | `authorizationRequired` | Missing/invalid credentials | Add OAuth token |
| 403 | `quotaExceeded` | Daily quota exhausted | Wait until midnight PT |
| 403 | `userRateLimitExceeded` | Per-user rate limit hit | Backoff and retry |
| 403 | `forbidden` | No permission | Check scopes/ownership |
| 403 | `commentsDisabled` | Comments off for this video | Skip, don't fail |
| 404 | `videoNotFound` | Video doesn't exist/is private | Skip or handle |
| 404 | `channelNotFound` | Channel doesn't exist | Skip or handle |
| 404 | `playlistNotFound` | Playlist doesn't exist | Skip or handle |
| 409 | `subscriptionDuplicate` | Already subscribed | Handle gracefully |
| 500 | `backendError` | Transient server error | Exponential backoff |
| 503 | `serviceUnavailable` | Service temporarily down | Exponential backoff |

### Exponential Backoff

```python
import time
import random
from googleapiclient.errors import HttpError

RETRYABLE_STATUS_CODES = {500, 502, 503, 504}
RETRYABLE_REASONS = {"userRateLimitExceeded", "rateLimitExceeded", "backendError"}

def execute_with_backoff(request, max_retries=5):
    for attempt in range(max_retries):
        try:
            return request.execute()
        except HttpError as e:
            code = e.resp.status
            reason = (e.error_details[0].get("reason", "")
                      if e.error_details else "")
            is_retryable = code in RETRYABLE_STATUS_CODES or reason in RETRYABLE_REASONS
            if not is_retryable or attempt == max_retries - 1:
                raise
            wait = (2 ** attempt) + random.uniform(0, 1)  # jitter
            print(f"Retrying in {wait:.1f}s (attempt {attempt+1})...")
            time.sleep(wait)
    raise Exception("Max retries exceeded")
```

### Detecting Quota Errors

```python
from googleapiclient.errors import HttpError
import json

try:
    response = youtube.videos().list(part="snippet", id="VIDEO_ID").execute()
except HttpError as e:
    error_detail = json.loads(e.content.decode())
    reason = error_detail["error"]["errors"][0]["reason"]

    if reason == "quotaExceeded":
        print("Daily quota exhausted. Try again after midnight PT.")
    elif reason == "forbidden":
        print("No permission — check OAuth scopes.")
    elif reason == "videoNotFound":
        print("Video does not exist or is private.")
    else:
        print(f"API error: {reason}")
        raise
```

---

## Batch Requests

Batch multiple API calls into a single HTTP request (counts as 1 HTTP request but each sub-request still costs its normal quota):

```python
from googleapiclient.http import BatchHttpRequest

def callback(request_id, response, exception):
    if exception:
        print(f"Error for {request_id}: {exception}")
    else:
        print(f"Got response for {request_id}: {response['snippet']['title']}")

batch = youtube.new_batch_http_request(callback=callback)

batch.add(youtube.videos().list(part="snippet", id="VIDEO_ID_1"), request_id="video1")
batch.add(youtube.videos().list(part="snippet", id="VIDEO_ID_2"), request_id="video2")
batch.add(youtube.videos().list(part="snippet", id="VIDEO_ID_3"), request_id="video3")

batch.execute()
```

**Important**: Max 50 requests per batch. Batch reduces HTTP overhead but not quota cost.

---

## Quota Monitoring

```python
# Check quota usage in Google Cloud Console:
# APIs & Services → Dashboard → YouTube Data API v3 → Quotas tab

# Or check remaining quota programmatically (not directly available in API)
# — monitor your own counters instead:

class QuotaTracker:
    def __init__(self, daily_limit=10000):
        self.daily_limit = daily_limit
        self.used = 0

    def charge(self, units):
        self.used += units
        remaining = self.daily_limit - self.used
        if remaining < 500:
            print(f"WARNING: Only {remaining} quota units remaining today")
        return remaining > 0

tracker = QuotaTracker()
tracker.charge(100)  # after a search.list
```

---

## The `fields` Parameter

Reduces response payload size without affecting quota cost. Use XPath-like syntax:

```python
# Return only video IDs and view counts (smaller payload)
response = youtube.videos().list(
    part="statistics",
    id="dQw4w9WgXcQ",
    fields="items(id,statistics(viewCount))"
).execute()

# Search returning only titles and nextPageToken
response = youtube.search().list(
    part="snippet",
    q="python",
    fields="items(id,snippet(title,channelTitle)),nextPageToken"
).execute()
```

| Syntax | Meaning |
|--------|---------|
| `items` | Top-level field |
| `items(id,snippet)` | Specific subfields |
| `items(snippet(title,description))` | Nested selection |
| `nextPageToken,items(id)` | Multiple top-level fields |

---

## Best Practices

1. **Cache aggressively** — Video metadata rarely changes. Cache responses for hours or days.
2. **Request minimal parts** — Each part costs quota. Don't request `contentDetails` if you only need `statistics`.
3. **Use `fields` parameter** to reduce response payload size (doesn't save quota but saves bandwidth/parse time).
4. **Avoid `search.list` for known resources** — Use `videos.list`, `channels.list`, or `playlistItems.list` instead.
5. **Use the uploads playlist** instead of search to enumerate channel videos.
6. **Batch video ID lookups** — `videos.list` accepts up to 50 comma-separated IDs per call (1 unit vs 50 individual calls).
7. **Always set `maxResults` to maximum** — reduces total API calls for paginated results.
8. **Store `nextPageToken`** and resume later rather than fetching all pages at once.
9. **Request quota increases** proactively before hitting limits in production.
10. **Never commit `credentials.json` or `token.json`** to version control — add both to `.gitignore`.
