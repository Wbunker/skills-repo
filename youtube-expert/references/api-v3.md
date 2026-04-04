# YouTube Data API v3 Reference

## Table of Contents
1. [Authentication](#authentication)
2. [Core concepts](#core-concepts)
3. [Resources and methods](#resources-and-methods)
4. [Quota costs](#quota-costs)
5. [Key endpoint parameters](#key-endpoint-parameters)
6. [Live streaming API](#live-streaming-api)
7. [Quota optimization patterns](#quota-optimization-patterns)
8. [Error handling](#error-handling)

---

## Authentication

**Base URL:** `https://www.googleapis.com/youtube/v3/`

| Method | When to use |
|--------|-------------|
| API Key (`?key=YOUR_KEY`) | Public data only — video metadata, channel info, public search |
| OAuth 2.0 (`Authorization: Bearer TOKEN`) | Any write operation, private data, user account access |

### OAuth 2.0 scopes

| Scope | Access |
|-------|--------|
| `https://www.googleapis.com/auth/youtube.readonly` | Read user's private data |
| `https://www.googleapis.com/auth/youtube.upload` | Upload videos only |
| `https://www.googleapis.com/auth/youtube` | Full read/write |
| `https://www.googleapis.com/auth/youtube.force-ssl` | Required for write ops on sensitive resources |
| `https://www.googleapis.com/auth/youtubepartner` | Content ID and partner operations |

Token delivery: `Authorization: Bearer TOKEN` header (preferred) or `?access_token=TOKEN` query param.

---

## Core concepts

### `part` parameter
Every request requires `part` (comma-separated). Controls which sections of the resource are returned. Quota cost is fixed per method regardless of how many parts are requested.

Example: `part=snippet,statistics,contentDetails`

### `fields` parameter
Optional XPath-like filter to trim the response payload. Does not affect quota cost but reduces bandwidth.

Example: `fields=items(id,snippet/title,statistics/viewCount)`

### Pagination
All list methods return `nextPageToken` and `prevPageToken`. Pass `pageToken=VALUE` on the next request. Each page is a separate API call costing full quota.

Response also includes `pageInfo.totalResults` and `pageInfo.resultsPerPage`.

---

## Resources and methods

| Resource | Methods available |
|----------|------------------|
| `videos` | list, insert, update, delete, rate, getRating, reportAbuse |
| `channels` | list, update |
| `channelSections` | list, insert, update, delete |
| `channelBanners` | insert |
| `playlists` | list, insert, update, delete |
| `playlistItems` | list, insert, update, delete |
| `playlistImages` | list, insert, update, delete |
| `search` | list |
| `commentThreads` | list, insert |
| `comments` | list, insert, update, delete, setModerationStatus |
| `subscriptions` | list, insert, delete |
| `captions` | list, insert, update, download, delete |
| `thumbnails` | set |
| `watermarks` | set, unset |
| `members` | list (YPP required) |
| `membershipsLevels` | list (YPP required) |
| `activities` | list |
| `liveBroadcasts` | list, insert, update, delete, bind, transition, cuepoint |
| `liveStreams` | list, insert, update, delete |

---

## Quota costs

**Daily default: 10,000 units per Google Cloud project. Resets midnight Pacific Time. Every request costs at least 1 unit, including invalid ones.**

| Resource | Method | Units |
|----------|--------|-------|
| videos | list | 1 |
| videos | insert | 100 |
| videos | update | 50 |
| videos | delete | 50 |
| videos | rate | 50 |
| videos | getRating | 1 |
| channels | list | 1 |
| channels | update | 50 |
| channelBanners | insert | 50 |
| channelSections | list | 1 |
| channelSections | insert / update / delete | 50 |
| playlists | list | 1 |
| playlists | insert / update / delete | 50 |
| playlistItems | list | 1 |
| playlistItems | insert / update / delete | 50 |
| playlistImages | list | 1 |
| playlistImages | insert / update / delete | 50 |
| **search** | **list** | **100** |
| commentThreads | list | 1 |
| commentThreads | insert / update | 50 |
| comments | list | 1 |
| comments | insert / update / delete / setModerationStatus | 50 |
| subscriptions | list | 1 |
| subscriptions | insert / delete | 50 |
| captions | list | 50 |
| captions | insert | 400 |
| captions | update | 450 |
| captions | delete | 50 |
| thumbnails | set | 50 |
| watermarks | set / unset | 50 |
| liveBroadcasts | list | 1 |
| liveBroadcasts | insert / update / delete / bind / transition / cuepoint | 50 |
| liveStreams | list | 1 |
| liveStreams | insert / update / delete | 50 |
| members | list | 1 |
| membershipsLevels | list | 1 |
| activities | list | 1 |
| videoCategories / i18nLanguages / i18nRegions | list | 1 |

> Verify current costs at the [official quota calculator](https://developers.google.com/youtube/v3/determine_quota_cost) — costs have changed historically.

---

## Key endpoint parameters

### `videos.list`

```
GET /videos?part=snippet,statistics,contentDetails&id=VIDEO_ID1,VIDEO_ID2&key=API_KEY
```

**`part` options:** `snippet`, `contentDetails`, `statistics`, `status`, `fileDetails`, `processingDetails`, `liveStreamingDetails`, `localizations`, `player`, `recordingDetails`, `suggestions`, `topicDetails`

**Filter (choose one):** `id` (comma-separated, up to 50), `chart=mostPopular`, `myRating=like|dislike`

**Optional:** `maxResults` (1–50, default 5), `pageToken`, `regionCode` (ISO 3166-1), `videoCategoryId`, `hl`

---

### `channels.list`

```
GET /channels?part=snippet,contentDetails,statistics&forHandle=@channelHandle&key=API_KEY
```

**`part` options:** `snippet`, `contentDetails`, `statistics`, `brandingSettings`, `status`, `topicDetails`, `id`, `localizations`

**Filter (choose one):** `id`, `forHandle` (with or without @), `forUsername`, `mine=true`

**Key:** `contentDetails.relatedPlaylists.uploads` = the uploads playlist ID — use with `playlistItems.list` (1 unit) instead of `search.list` (100 units) to enumerate all channel videos cheaply.

---

### `playlists.list`

```
GET /playlists?part=snippet,contentDetails&channelId=CHANNEL_ID&key=API_KEY
```

**Filter (choose one):** `id`, `channelId`, `mine=true`

**Optional:** `maxResults` (0–50), `pageToken`, `hl`

---

### `playlistItems.list`

```
GET /playlistItems?part=snippet,contentDetails&playlistId=UPLOADS_PLAYLIST_ID&maxResults=50&key=API_KEY
```

Best way to enumerate all videos in a channel — costs 1 unit/page vs. 100 units for `search.list`.

---

### `search.list`

```
GET /search?part=snippet&q=QUERY&type=video&order=date&maxResults=25&key=API_KEY
```

**Only `part=snippet` is supported.**

| Parameter | Options / notes |
|-----------|-----------------|
| `q` | Query string; `-term` excludes, `term\|term` is OR |
| `channelId` | Restrict to a channel |
| `type` | `video`, `channel`, `playlist` (default: all three) |
| `order` | `date`, `rating`, `relevance`, `title`, `videoCount`, `viewCount` |
| `publishedAfter` / `publishedBefore` | RFC 3339 format: `2024-01-01T00:00:00Z` |
| `videoDuration` | `short` (<4 min), `medium` (4–20 min), `long` (>20 min), `any` |
| `videoDefinition` | `high`, `standard`, `any` |
| `eventType` | `completed`, `live`, `upcoming` |
| `regionCode` | ISO 3166-1 country code |
| `relevanceLanguage` | ISO 639-1 language code |

**Cost: 100 units per call.** Cap: `channelId` filter caps at ~500 results total.

---

### `commentThreads.list`

```
GET /commentThreads?part=snippet,replies&videoId=VIDEO_ID&maxResults=100&key=API_KEY
```

**Filter (choose one):** `videoId`, `allThreadsRelatedToChannelId`, `id`

**Optional:** `maxResults` (1–100, default 20), `order` (`time`, `relevance`), `moderationStatus` (`heldForReview`, `likelySpam`, `published`), `searchTerms`, `textFormat` (`html`, `plainText`)

---

## Live streaming API

**Architecture:** A `liveBroadcast` is the YouTube event viewers watch. A `liveStream` is the encoder feed (RTMP/HLS). Each broadcast must be bound to exactly one stream; one stream can serve up to 3 concurrent broadcasts.

**Broadcast lifecycle:**
```
created → ready → testing → live → complete
```
Use `liveBroadcasts.transition` to move between states. `liveBroadcasts.bind` links a broadcast to a stream.

**Common patterns:**
- Single encoder → multiple scheduled events: one stream, many broadcasts
- Full isolation: separate stream per broadcast
- 24/7 feed: one stream split into multiple simultaneous broadcasts (up to 3)

---

## Quota optimization patterns

| Pattern | Savings |
|---------|---------|
| Batch up to 50 IDs: `id=ID1,ID2,...,ID50` | 50 items = 1 unit (vs. 50 units) |
| Use `playlistItems.list` to list channel videos | 1 unit/page vs. 100 for `search.list` |
| Use `channels.list(forHandle=@name)` to look up a channel | 1 unit vs. 100 for `search.list` |
| Cache static metadata 24 hr; dynamic data 1–6 hr; search results 30–60 min | Fewer repeat calls |
| Include saved `ETag` in `If-None-Match` header | 304 Not Modified when unchanged |
| Use `fields` parameter to trim payload | Reduces bandwidth, not quota |
| Multiple Google Cloud projects | Each gets its own 10,000-unit pool |

---

## Error handling

| HTTP status | Meaning |
|-------------|---------|
| 400 | Bad Request — invalid parameter value |
| 401 | Unauthorized — missing/invalid OAuth token |
| 403 | Forbidden — quota exceeded, or insufficient scope |
| 404 | Not Found — resource doesn't exist |
| 409 | Conflict — resource already exists |
| 429 | Too Many Requests — rate limit hit |
| 503 | Service Unavailable — retry with exponential backoff |

**Quota exceeded (403):** Check `error.errors[].reason` for `quotaExceeded` vs. `forbidden`. Quota resets midnight Pacific Time.
