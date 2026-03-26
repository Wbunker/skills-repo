# Search Resource — YouTube Data API v3

## Overview

`search.list` is the most expensive read operation at **100 units per call**. Use alternatives when possible (see Cost Reduction section below).

Base URL: `https://www.googleapis.com/youtube/v3/search`

| Method | HTTP | Quota Cost | Scope |
|--------|------|-----------|-------|
| list | GET | 100 units | API key or youtube.readonly |

---

## search.list

**Endpoint:** `GET https://www.googleapis.com/youtube/v3/search`

### Required Parameters

- **part**: Must be `snippet` (only supported value for search)

### Filter Parameters (select at most one of the exclusive ones)

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Search query. Supports `-term` (NOT) and `term1\|term2` (OR) |
| `channelId` | string | Limit results to a specific channel |
| `type` | string | `video`, `channel`, `playlist`, or comma-separated combination (default: all three) |
| `forMine` | boolean | `true` — search only authenticated user's videos (requires `type=video`) |
| `forDeveloper` | boolean | `true` — limit to videos uploaded via developer's app |
| `forContentOwner` | boolean | `true` — restrict to videos owned by content owner |

### Optional Parameters — General

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `maxResults` | integer | 5 | Items per page (0–50) |
| `pageToken` | string | — | Pagination token |
| `order` | string | `relevance` | Sort: `date`, `rating`, `relevance`, `title`, `videoCount`, `viewCount` |
| `publishedAfter` | datetime | — | RFC 3339 format, e.g., `2024-01-01T00:00:00Z` |
| `publishedBefore` | datetime | — | RFC 3339 format |
| `regionCode` | string | — | ISO 3166-1 alpha-2 country code |
| `relevanceLanguage` | string | — | ISO 639-1 language code (influences but doesn't filter results) |
| `safeSearch` | string | `moderate` | `moderate`, `none`, or `strict` |
| `channelType` | string | `any` | `any` or `show` |

### Optional Parameters — Video-Only Filters (require `type=video`)

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `eventType` | string | `completed`, `live`, `upcoming` | Filter by broadcast state |
| `videoCaption` | string | `any`, `closedCaption`, `none` | Caption availability |
| `videoCategoryId` | string | Category ID | Filter by video category |
| `videoDefinition` | string | `any`, `high`, `standard` | HD vs SD |
| `videoDimension` | string | `2d`, `3d`, `any` | Video dimension |
| `videoDuration` | string | `any`, `short`, `medium`, `long` | short <4m, medium 4-20m, long >20m |
| `videoEmbeddable` | string | `any`, `true` | Embeddable videos only |
| `videoLicense` | string | `any`, `creativeCommon`, `youtube` | License type |
| `videoSyndicated` | string | `any`, `true` | Can be played outside YouTube |
| `videoType` | string | `any`, `episode`, `movie` | Video type |
| `videoPaidProductPlacement` | string | `any`, `true` | Has paid product placement |
| `location` | string | `lat,lng` | Geographic center point |
| `locationRadius` | string | e.g., `10km`, `100mi` | Radius from location (max 1000 km) |
| `topicId` | string | Topic ID | Freebase topic ID |

### Response Structure

```json
{
  "kind": "youtube#searchListResponse",
  "etag": "...",
  "nextPageToken": "TOKEN",
  "prevPageToken": "TOKEN",
  "regionCode": "US",
  "pageInfo": {
    "totalResults": 1234,
    "resultsPerPage": 5
  },
  "items": [
    {
      "kind": "youtube#searchResult",
      "etag": "...",
      "id": {
        "kind": "youtube#video",
        "videoId": "dQw4w9WgXcQ"
      },
      "snippet": {
        "publishedAt": "2009-10-25T06:57:33Z",
        "channelId": "UCuAXFkgsw1L7xaCfnd5JJOw",
        "title": "Rick Astley - Never Gonna Give You Up",
        "description": "...",
        "thumbnails": {...},
        "channelTitle": "Rick Astley",
        "liveBroadcastContent": "none"
      }
    }
  ]
}
```

**Note:** Search results contain `snippet` data only. To get `statistics`, `contentDetails`, etc., take the returned IDs and make a separate `videos.list` call (1 unit).

### Extracting IDs by Type

```python
# For type=video
video_id = item['id']['videoId']

# For type=channel
channel_id = item['id']['channelId']

# For type=playlist
playlist_id = item['id']['playlistId']
```

---

## Common Search Patterns

### Basic Keyword Search

```python
response = youtube.search().list(
    part='snippet',
    q='python tutorial',
    type='video',
    maxResults=25,
    order='viewCount',
    videoDuration='medium'
).execute()

video_ids = [item['id']['videoId'] for item in response['items']]
```

### Get Full Video Details After Search

```python
# Search is 100 units, then videos.list is 1 unit
search_response = youtube.search().list(
    part='snippet',
    q='machine learning',
    type='video',
    maxResults=10
).execute()

ids = ','.join(item['id']['videoId'] for item in search_response['items'])

videos_response = youtube.videos().list(
    part='snippet,statistics,contentDetails',
    id=ids
).execute()
```

### Search a Specific Channel

```python
response = youtube.search().list(
    part='snippet',
    channelId='CHANNEL_ID',
    q='tutorial',
    type='video',
    order='date',
    maxResults=50
).execute()
```

**Limitation:** Channel search returns at most 500 videos when `channelId` is used without `forContentOwner`. For complete channel video listings, use the uploads playlist pattern instead.

### Find Live Streams

```python
response = youtube.search().list(
    part='snippet',
    q='gaming',
    type='video',
    eventType='live',
    maxResults=25
).execute()
```

### Search with Date Range

```python
response = youtube.search().list(
    part='snippet',
    q='python',
    type='video',
    publishedAfter='2024-01-01T00:00:00Z',
    publishedBefore='2024-12-31T23:59:59Z',
    order='date'
).execute()
```

### Geographic Search

```python
response = youtube.search().list(
    part='snippet',
    q='coffee shop',
    type='video',
    location='37.7749,-122.4194',  # San Francisco
    locationRadius='10km'
).execute()
```

---

## Known Limitations

1. **500 video cap**: When filtering by `channelId`, results are capped at approximately 500 videos regardless of pagination.
2. **`totalResults` is approximate**: The `pageInfo.totalResults` value is an estimate, not an exact count.
3. **Search-only part**: Only `snippet` is supported as a part for search results.
4. **Quota cost**: At 100 units per call, exhausting the daily 10,000-unit quota requires only 100 search requests.
5. **Pagination limit**: Even with pagination, you cannot retrieve more than roughly 500 results for most query/filter combinations.

---

## Cost Reduction Alternatives

| Use Case | Expensive Way | Cheaper Alternative |
|----------|--------------|---------------------|
| Get all my channel's videos | search.list (100/call) | channels.list + playlistItems.list (1+1/call) |
| Get video details by ID | search.list (100/call) | videos.list (1/call) |
| Get a playlist's videos | search.list (100/call) | playlistItems.list (1/call) |
| Get channel info by name | search.list (100/call) | channels.list with forHandle (1/call) |

Only use `search.list` when you genuinely need keyword/topic-based discovery across YouTube at large.

---

## Topic IDs (Common Freebase IDs)

| Topic | ID |
|-------|-----|
| Music | `/m/04rlf` |
| Gaming | `/m/0bzvm2` |
| Sports | `/m/06ntj` |
| Entertainment | `/m/02jjt` |
| Lifestyle | `/m/019_rr` |
| Society | `/m/098wr` |
| Technology | `/m/07c1v` |
| Knowledge | `/m/01k8wb` |

Use with `topicId` parameter to filter search results by subject area.
