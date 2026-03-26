# Quota System — YouTube Data API v3

## Overview

- **Default allocation:** 10,000 units per day per Google Cloud project
- **Quota reset time:** Midnight Pacific Time (PT)
- **Shared pool:** All API keys within the same project share the same quota
- **Invalid requests:** Every API request, even if invalid, costs at least 1 unit
- **No rollover:** Unused quota does not carry over to the next day

---

## Complete Quota Cost Table

### Core Content Resources

| Resource | Method | Cost (units) |
|----------|--------|-------------|
| **videos** | list | 1 |
| | insert | 100 |
| | update | 50 |
| | delete | 50 |
| | rate | 50 |
| | getRating | 1 |
| | reportAbuse | 50 |
| **channels** | list | 1 |
| | update | 50 |
| **playlists** | list | 1 |
| | insert | 50 |
| | update | 50 |
| | delete | 50 |
| **playlistItems** | list | 1 |
| | insert | 50 |
| | update | 50 |
| | delete | 50 |
| **search** | list | 100 |

### Engagement Resources

| Resource | Method | Cost (units) |
|----------|--------|-------------|
| **commentThreads** | list | 1 |
| | insert | 50 |
| **comments** | list | 1 |
| | insert | 50 |
| | update | 50 |
| | delete | 50 |
| | setModerationStatus | 50 |
| **subscriptions** | list | 1 |
| | insert | 50 |
| | delete | 50 |
| **activities** | list | 1 |

### Media and Channel Customization

| Resource | Method | Cost (units) |
|----------|--------|-------------|
| **captions** | list | 50 |
| | insert | 400 |
| | update | 450 |
| | delete | 50 |
| **thumbnails** | set | 50 |
| **channelBanners** | insert | 50 |
| **channelSections** | list | 1 |
| | insert | 50 |
| | update | 50 |
| | delete | 50 |
| **watermarks** | set | 50 |
| | unset | 50 |
| **playlistImages** | list | 1 |
| | insert | 50 |
| | update | 50 |
| | delete | 50 |

### Membership and Reference

| Resource | Method | Cost (units) |
|----------|--------|-------------|
| **members** | list | 1 |
| **membershipsLevels** | list | 1 |
| **videoCategories** | list | 1 |
| **videoAbuseReportReasons** | list | 1 |
| **i18nLanguages** | list | 1 |
| **i18nRegions** | list | 1 |
| **guideCategories** | list | 1 |

### Live Streaming

| Resource | Method | Cost (units) |
|----------|--------|-------------|
| **liveBroadcasts** | list | 1 |
| | insert | 50 |
| | update | 50 |
| | delete | 50 |
| | bind | 50 |
| | transition | 50 |
| | cuepoint | 50 |
| **liveStreams** | list | 1 |
| | insert | 50 |
| | update | 50 |
| | delete | 50 |

---

## Daily Budget Examples

With 10,000 units/day:

| Scenario | Operations per Day |
|----------|--------------------|
| Search-only app | 100 search calls |
| Video detail lookups | 10,000 videos.list calls |
| Mixed: 10 searches + video details | 10 × 100 + 9,000 × 1 = 10,000 units |
| Playlist management (insert items) | 200 playlistItems.insert calls |
| Video uploads | 100 video uploads |
| Reading comments | 10,000 commentThreads.list calls |

---

## Quota Error Response

When quota is exhausted, the API returns HTTP 403:

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

The `reason` field distinguishes:
- `quotaExceeded` — project's daily quota exhausted
- `userRateLimitExceeded` — per-user rate limit hit (short-term)
- `rateLimitExceeded` — general rate limit

---

## Quota Optimization Strategies

### 1. Use the Cheapest Method for the Job

| Task | Expensive | Cheap Alternative |
|------|-----------|-------------------|
| Get channel's videos | search.list (100/call) | channels.list + playlistItems.list (2 units + 1/page) |
| Check if video exists | search.list (100) | videos.list(id=VIDEO_ID) (1 unit) |
| Get channel info by name | search.list (100) | channels.list(forHandle=@name) (1 unit) |
| Get playlist videos | search.list (100) | playlistItems.list (1/page) |

### 2. Batch Requests

Fetch up to 50 items in a single call using comma-separated IDs:

```python
# Bad: 50 separate calls = 50 units
for video_id in video_ids:
    youtube.videos().list(part='statistics', id=video_id).execute()

# Good: 1 call per 50 IDs = 1 unit per 50 videos
for i in range(0, len(video_ids), 50):
    batch_ids = ','.join(video_ids[i:i+50])
    youtube.videos().list(part='statistics', id=batch_ids).execute()
```

### 3. Request Only Needed Parts

Parts determine what data is returned. Request only what you need:

```python
# If you only need view counts:
youtube.videos().list(part='statistics', id='VIDEO_ID').execute()

# Not:
youtube.videos().list(
    part='snippet,contentDetails,statistics,status,fileDetails',
    id='VIDEO_ID'
).execute()
```

Note: Parts do not affect quota cost per call (cost is fixed per method), but they reduce response size and network overhead.

### 4. Use the `fields` Parameter

The `fields` parameter further limits response payload. It does NOT reduce quota cost but reduces bandwidth and parse time:

```python
youtube.videos().list(
    part='statistics',
    id='VIDEO_ID',
    fields='items(id,statistics(viewCount,likeCount))'
).execute()
```

### 5. Implement Application-Level Caching

Cache responses to avoid redundant API calls:

```python
import time
from functools import lru_cache

# Simple TTL cache for video details
_cache = {}

def get_video_details(youtube, video_id, ttl_seconds=3600):
    cache_key = f'video_{video_id}'
    if cache_key in _cache:
        data, timestamp = _cache[cache_key]
        if time.time() - timestamp < ttl_seconds:
            return data

    response = youtube.videos().list(
        part='snippet,statistics',
        id=video_id
    ).execute()

    _cache[cache_key] = (response, time.time())
    return response
```

Recommended cache durations:
- Static metadata (channel name, video title): 24 hours
- Dynamic data (view count, subscriber count): 1–6 hours
- Search results: 30 minutes–1 hour

### 6. Use ETags for Conditional Requests

ETags allow skipping data transfer when content hasn't changed:

```python
# First request: save the ETag
response = youtube.videos().list(part='statistics', id='VIDEO_ID').execute()
etag = response['etag']

# Later request: include ETag header
# If unchanged, returns 304 Not Modified (still costs 1 unit but saves bandwidth)
# The Python client library handles ETags automatically with http.request
```

### 7. Enable GZIP Compression

```python
import httplib2

http = httplib2.Http()
# The google-api-python-client enables gzip by default
# Reduces response payload by 50–80%
```

---

## Requesting Higher Quota

Default quota (10,000 units/day) can be increased by:

1. Complete a **YouTube API Services Compliance Audit** — required before quota extension requests are considered
2. Submit a **Quota Extension Request** through Google Cloud Console
3. Demonstrate legitimate use case, user base, and Terms of Service compliance
4. Google typically responds within 1–3 business days

**Audit requirement:** Projects that exceed the default quota must complete an audit showing compliance with YouTube API Terms of Service. Audit completion is a prerequisite for quota extension approval.

---

## Quota Monitoring

Check current quota usage in Google Cloud Console:
- APIs & Services → YouTube Data API v3 → Quotas
- Monitor `queries per day` metric

Set up quota alerts in Google Cloud Console to receive notifications before exhaustion.

---

## Multiple Projects Pattern

For high-volume applications, distribute quota across multiple Google Cloud projects:

```python
import itertools

API_KEYS = [
    'key_from_project_1',
    'key_from_project_2',
    'key_from_project_3',
]

key_cycle = itertools.cycle(API_KEYS)

def get_youtube_client():
    return build('youtube', 'v3', developerKey=next(key_cycle))
```

**Note:** Each project must be a separate Google Cloud project with YouTube Data API enabled. This approach multiplies available daily quota. Only appropriate for public data (API keys); OAuth flows are tied to individual projects.
