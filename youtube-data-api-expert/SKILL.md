---
name: youtube-data-api-expert
description: YouTube Data API v3 expertise covering authentication (OAuth 2.0, API keys, service accounts), all core resources (Videos, Channels, Playlists, PlaylistItems, Search, Comments, Subscriptions, LiveBroadcasts, LiveStreams), quota system, video upload (resumable protocol), pagination, error handling, and YouTube Analytics API. Use when building YouTube integrations, automating channel management, uploading videos programmatically, searching content, managing playlists, reading comments, or working with live streaming via the Google API Python client library.
---

# YouTube Data API v3 Expert

Based on official Google YouTube Data API v3 documentation (developers.google.com/youtube/v3).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    YOUTUBE DATA API v3                          │
│                                                                 │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐    │
│  │   API KEY    │  │  OAUTH 2.0    │  │ SERVICE ACCOUNT  │    │
│  │ Public data  │  │ User account  │  │ Server-to-server │    │
│  │ Read-only    │  │ Full access   │  │ (limited scope)  │    │
│  └──────┬───────┘  └──────┬────────┘  └────────┬─────────┘    │
│         └─────────────────┼───────────────────── ┘             │
│                           ▼                                     │
│              ┌────────────────────────┐                        │
│              │   googleapis.com/      │                        │
│              │   youtube/v3/{method}  │                        │
│              └────────────┬───────────┘                        │
│                           │                                     │
│   ┌───────────┬───────────┼───────────┬───────────┐           │
│   ▼           ▼           ▼           ▼           ▼           │
│ Videos   Channels   Playlists    Search    Comments           │
│ Subs   PlaylistItems  Captions  LiveBroadcast LiveStream      │
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐      │
│  │  QUOTA SYSTEM: 10,000 units/day per project          │      │
│  │  list=1  write=50  search=100  video.insert=100      │      │
│  └─────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Reference

| Task | Reference |
|------|-----------|
| OAuth 2.0 flow, API keys, scopes, credentials.json/token.json Python pattern | [auth.md](references/auth.md) |
| Videos resource: list, insert, update, delete, rate; video upload | [videos.md](references/videos.md) |
| Channels, Playlists, PlaylistItems | [channels-playlists.md](references/channels-playlists.md) |
| Search.list parameters, filters, restrictions | [search.md](references/search.md) |
| Comments, CommentThreads: list, insert, moderation | [comments.md](references/comments.md) |
| Subscriptions, LiveBroadcasts, LiveStreams | [subscriptions-and-live.md](references/subscriptions-and-live.md) |
| Quota costs per method, daily limits, optimization strategies | [quota.md](references/quota.md) |
| Pagination (pageToken), error handling, exponential backoff, best practices | [operations.md](references/operations.md) |
| YouTube Analytics API vs Data API, reports.query, metrics/dimensions | [analytics.md](references/analytics.md) |

## Reference Files

| File | Topics |
|------|--------|
| `auth.md` | OAuth 2.0 installed app flow, API keys, scopes, credentials.json, token.json/pickle, Python InstalledAppFlow pattern, refresh tokens, service accounts |
| `videos.md` | videos.list parameters and filters, videos.insert multipart/resumable upload, update/delete, rate/getRating, part values, video status/privacy |
| `channels-playlists.md` | channels.list filters (mine, forHandle, id), playlists CRUD, playlistItems CRUD, special playlists, channel snippet/statistics/contentDetails |
| `search.md` | search.list required/optional parameters, type filter (video/channel/playlist), video-only filters, order options, 100-unit cost, 500-video channel cap |
| `comments.md` | commentThreads.list filters (videoId, channelId), comments.list, insert replies, setModerationStatus, moderation status values, 1-unit list cost |
| `subscriptions-and-live.md` | subscriptions.list (mine, mySubscribers, forChannelId), liveBroadcast lifecycle/transitions, liveStream CDN settings, bind operation |
| `quota.md` | Complete quota cost table for all methods, 10,000 unit daily limit, reset time, quota optimization, requesting higher quota, quotaExceeded errors |
| `operations.md` | Pagination with pageToken/nextPageToken, error codes (quotaExceeded, forbidden, notFound), exponential backoff, fields parameter, ETags, batching |
| `analytics.md` | YouTube Analytics API vs Data API, reports.query method, key metrics (views, estimatedMinutesWatched), dimensions, channel vs video reports, Reporting API |

## Core Decision Trees

### Which Authentication Method?

```
What data do you need to access?
├── Public data only (video metadata, public playlists, search)
│   └── API Key → simple, no user interaction, append ?key=API_KEY
├── User's own account data (uploads, private videos, subscriptions)
│   ├── Desktop/CLI app → OAuth 2.0 InstalledAppFlow
│   │   └── credentials.json + token.json/pickle pattern
│   ├── Web app → OAuth 2.0 server-side flow (Flow, not InstalledAppFlow)
│   └── Mobile app → OAuth 2.0 with PKCE
└── Server-to-server (no user interaction)
    └── Service account → limited YouTube support, mainly for
        YouTube Content ID / partner APIs, NOT standard Data API
```

### Which Scope to Request?

```
What operations does your app need?
├── Read public data only → use API key (no OAuth needed)
├── Read user's private data (subscriptions, liked videos)
│   └── youtube.readonly
├── Upload videos only
│   └── youtube.upload
├── Full account management (playlists, settings, comments)
│   └── youtube (full access)
├── Edit/delete videos, captions, comments securely
│   └── youtube.force-ssl (required for write ops on sensitive data)
└── YouTube partner / content owner operations
    └── youtubepartner
```

### Which Resource for the Task?

```
What do you want to do?
├── Find videos by keyword/topic → search.list (100 units, type=video)
├── Get video details by ID → videos.list (1 unit, id=VIDEO_ID)
├── Upload a video → videos.insert (100 units, resumable protocol)
├── Get my channel info → channels.list (1 unit, mine=true)
├── Get a channel's videos → search.list (channelId=X, type=video)
│   OR channels.list to get uploads playlist ID →
│       playlistItems.list (1 unit each page, cheaper than search)
├── Manage playlists → playlists.insert/update/delete (50 units each)
├── Add video to playlist → playlistItems.insert (50 units)
├── Read video comments → commentThreads.list (1 unit, videoId=X)
├── Reply to a comment → comments.insert (50 units)
├── Check my subscriptions → subscriptions.list (1 unit, mine=true)
├── Go live → liveBroadcasts.insert + liveStreams.insert + bind
└── Get analytics → YouTube Analytics API (separate API)
```

### Video Upload Decision

```
How large is the video file?
├── < 5 MB → simple multipart upload
│   POST /upload/youtube/v3/videos?uploadType=multipart
├── >= 5 MB (recommended for all) → resumable upload
│   1. POST to initiate → get session URI (Location header)
│   2. PUT session URI with file data
│   3. On 5xx → exponential backoff + check upload status
│   4. On 308 Resume Incomplete → resume from Range header offset
│   └── Success: 201 Created with video resource
└── Chunked resumable (large files / unreliable network)
    └── Split into 256 KB multiples, PUT sequentially
```

## Key Concepts

### Parts System
Every API request requires a `part` parameter specifying which sections to return/write. Parts have quota implications only in terms of what data is accessible — the per-call quota cost is fixed per method regardless of parts requested.

Common parts by resource:
- **Videos**: `snippet`, `contentDetails`, `statistics`, `status`, `fileDetails`, `processingDetails`, `liveStreamingDetails`
- **Channels**: `snippet`, `contentDetails`, `statistics`, `brandingSettings`, `status`, `topicDetails`
- **Playlists**: `snippet`, `status`, `contentDetails`, `player`, `localizations`
- **Search**: only `snippet` is supported

### Privacy Status Values
`public` | `private` | `unlisted`

Unverified API projects that upload videos will have them set to `private` by default until a compliance audit is passed.

### Quota Reset
Daily quota resets at **midnight Pacific Time** (PT). All API keys within the same Google Cloud project share the same 10,000-unit pool.

### The Uploads Playlist Pattern (Cost-Efficient Channel Video Retrieval)
```
1. channels.list(mine=true, part=contentDetails)  → 1 unit
   → response.items[0].contentDetails.relatedPlaylists.uploads
2. playlistItems.list(playlistId=UPLOADS_ID, part=snippet)  → 1 unit/page
```
This is far cheaper than search.list (100 units/call) for retrieving a channel's own videos.
