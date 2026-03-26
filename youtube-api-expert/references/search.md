# YouTube Data API — Search

## Search.list — Core Usage

Search is the most expensive API call: **100 quota units per request**.

```python
response = youtube.search().list(
    part="snippet",       # only "snippet" is available for search results
    q="python tutorial",
    type="video",         # "video", "channel", "playlist", or comma-separated
    maxResults=25         # 0–50, default 5
).execute()

for item in response["items"]:
    kind = item["id"]["kind"]  # "youtube#video", "youtube#channel", etc.
    if kind == "youtube#video":
        print(item["id"]["videoId"], item["snippet"]["title"])
    elif kind == "youtube#channel":
        print(item["id"]["channelId"], item["snippet"]["title"])
    elif kind == "youtube#playlist":
        print(item["id"]["playlistId"], item["snippet"]["title"])
```

---

## Parameters Reference

### Query & Type

| Parameter | Values | Description |
|-----------|--------|-------------|
| `q` | string | Search query (use `\|` for OR, `-` for NOT) |
| `type` | `video`, `channel`, `playlist` | Filter by result type |
| `maxResults` | 0–50 | Results per page (default 5) |

### Video Filters (only apply when `type="video"`)

| Parameter | Values | Description |
|-----------|--------|-------------|
| `videoDuration` | `any`, `short`, `medium`, `long` | short <4min, medium 4-20min, long >20min |
| `videoDefinition` | `any`, `high`, `standard` | HD vs SD |
| `videoCaption` | `any`, `closedCaption`, `none` | Caption availability |
| `videoType` | `any`, `episode`, `movie` | Video type |
| `videoLicense` | `any`, `creativeCommon`, `youtube` | License type |
| `videoEmbeddable` | `any`, `true` | Only embeddable videos |
| `videoCategoryId` | category ID string | Filter by category |
| `videoSyndicated` | `any`, `true` | Videos playable outside youtube.com |

### Location & Region

| Parameter | Values | Description |
|-----------|--------|-------------|
| `regionCode` | ISO 3166-1 alpha-2 (e.g., `"US"`) | Results relevant to region |
| `relevanceLanguage` | ISO 639-1 (e.g., `"en"`) | Results in language |
| `location` | `"37.42307,-122.08427"` | Lat,long for geo search |
| `locationRadius` | `"10km"`, `"5mi"` | Radius around location |

### Ordering

| Parameter | Values |
|-----------|--------|
| `order` | `relevance` (default), `date`, `rating`, `title`, `videoCount`, `viewCount` |

### Date Filtering

```python
from datetime import datetime, timezone

response = youtube.search().list(
    part="snippet",
    q="python",
    type="video",
    publishedAfter="2024-01-01T00:00:00Z",   # RFC 3339 format
    publishedBefore="2024-12-31T23:59:59Z",
    order="date"
).execute()
```

### Channel-Scoped Search

```python
# Search within a specific channel
response = youtube.search().list(
    part="snippet",
    q="tutorial",
    channelId="CHANNEL_ID",
    type="video",
    order="date"
).execute()
```

---

## Pagination

```python
def search_all_pages(youtube, query, max_pages=3, **kwargs):
    results = []
    next_page = None
    page = 0

    while page < max_pages:
        response = youtube.search().list(
            part="snippet",
            q=query,
            maxResults=50,
            pageToken=next_page,
            **kwargs
        ).execute()

        results.extend(response["items"])
        next_page = response.get("nextPageToken")
        page += 1

        if not next_page:
            break

    return results
```

**Important**: Each page costs 100 quota units. 3 pages = 300 units. Be conservative.

---

## Quota-Efficient Alternatives to Search

Search costs 100 units/call. For many use cases, cheaper alternatives exist:

| Use Case | Instead of search | Cheaper Alternative | Cost |
|----------|------------------|---------------------|------|
| All videos from a channel | search with channelId | PlaylistItems.list on uploads playlist | 1 unit |
| Video by ID | search for video | Videos.list with id= | 1 unit |
| Channel by handle | search for channel | Channels.list with forHandle= | 1 unit |
| Popular videos | search with chart | Videos.list with chart=mostPopular | 1 unit |

Use `search.list` only when you genuinely need text/keyword search.

---

## Search Limitations

- Maximum 500 results per query (even with pagination through nextPageToken)
- `snippet` is the **only** part available — you cannot get `statistics` or `contentDetails` from search results directly
- To get full video details after searching, batch the video IDs into a Videos.list call:

```python
# Search returns snippets only
search_results = youtube.search().list(
    part="snippet", q="python", type="video", maxResults=10
).execute()

# Get full details for found videos
video_ids = [item["id"]["videoId"] for item in search_results["items"]]
videos = youtube.videos().list(
    part="snippet,statistics,contentDetails",
    id=",".join(video_ids)
).execute()
```

---

## Example: Find recent videos mentioning a topic in a channel

```python
def find_channel_videos_about(youtube, channel_id, query, days_back=30):
    from datetime import datetime, timedelta, timezone

    since = (datetime.now(timezone.utc) - timedelta(days=days_back)).isoformat()

    response = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        q=query,
        type="video",
        order="date",
        publishedAfter=since,
        maxResults=50
    ).execute()

    return [
        {
            "id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "published": item["snippet"]["publishedAt"]
        }
        for item in response.get("items", [])
    ]
```
