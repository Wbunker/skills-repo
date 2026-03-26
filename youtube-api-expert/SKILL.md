---
name: youtube-api-expert
description: YouTube Data API v3 and YouTube Analytics API expertise. Use when building YouTube integrations, automating channel management, uploading videos programmatically, searching YouTube content, managing playlists, reading channel analytics, working with live streams, or doing anything with the Google YouTube APIs. Covers OAuth 2.0 authentication for a user's own account, API key setup, quota management, all core resources (Videos, Channels, Playlists, Search, Comments, LiveBroadcasts), and Python/REST usage patterns. Trigger whenever the user mentions YouTube API, youtube data api, uploading to YouTube from code, reading YouTube analytics, managing a YouTube channel programmatically, or any task involving google-api-python-client with YouTube.
---

# YouTube Data API v3 Expert

Based on the official Google YouTube Data API v3 documentation and YouTube Analytics API reference.

## API Landscape

```
┌─────────────────────────────────────────────────────────────────┐
│                    YOUTUBE API SURFACE                          │
│                                                                 │
│  ┌──────────────────────┐    ┌──────────────────────────────┐  │
│  │  YouTube Data API v3 │    │  YouTube Analytics API       │  │
│  │                      │    │                              │  │
│  │  Videos              │    │  Channel reports             │  │
│  │  Channels            │    │  Content owner reports       │  │
│  │  Playlists           │    │  Realtime reports            │  │
│  │  Search              │    │  Metrics & dimensions        │  │
│  │  Comments            │    │                              │  │
│  │  Subscriptions       │    └──────────────────────────────┘  │
│  │  LiveBroadcasts      │                                       │
│  │  LiveStreams          │    ┌──────────────────────────────┐  │
│  │  Members             │    │  YouTube Reporting API       │  │
│  └──────────────────────┘    │  (bulk data downloads)       │  │
│                              └──────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  AUTHENTICATION LAYER                    │  │
│  │                                                          │  │
│  │   API Key (public data only)                             │  │
│  │   OAuth 2.0 (user account — read/write own channel)     │  │
│  │   Service Account (limited; needs domain delegation)    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Reference

| Task | Reference File |
|------|---------------|
| OAuth 2.0 setup, API key, scopes, credentials.json, token refresh | [auth.md](references/auth.md) |
| Videos: upload, list, update, delete, captions, thumbnails | [videos.md](references/videos.md) |
| Channels: list, update, branding, sections, channel info | [channels.md](references/channels.md) |
| Playlists and PlaylistItems: create, manage, reorder | [playlists.md](references/playlists.md) |
| Search: filters, types, ordering, pagination patterns | [search.md](references/search.md) |
| Comments and CommentThreads: list, post, moderate | [comments.md](references/comments.md) |
| LiveBroadcasts and LiveStreams: create, bind, transition | [live.md](references/live.md) |
| Quotas, rate limits, cost table, error handling, best practices | [quotas-and-limits.md](references/quotas-and-limits.md) |
| YouTube Analytics API: metrics, dimensions, reports, filters | [analytics.md](references/analytics.md) |

## Reference Files Overview

| File | Topics |
|------|--------|
| `auth.md` | Google Cloud Console setup, OAuth 2.0 desktop flow, credentials.json, token.json, scopes, API key, service accounts, Python client setup |
| `videos.md` | Videos.list (parts), Videos.insert (resumable upload), Videos.update, Videos.delete, Captions, Thumbnails, video status/privacy |
| `channels.md` | Channels.list by id/mine/forHandle, Channels.update, branding settings, channel statistics, channel sections |
| `playlists.md` | Playlists.list/insert/update/delete, PlaylistItems.list/insert/update/delete, reordering items |
| `search.md` | Search.list parameters, type filters (video/channel/playlist), order options, regionCode, videoDuration, pageToken pagination |
| `comments.md` | CommentThreads.list/insert, Comments.list/insert/update/setModerationStatus/markAsSpam/delete, reply handling |
| `live.md` | LiveBroadcasts.insert/list/update/bind/transition/delete, LiveStreams.insert/list/update/delete, stream key management |
| `quotas-and-limits.md` | 10,000 unit/day quota, per-method costs, quota errors (403 quotaExceeded), exponential backoff, batch requests |
| `analytics.md` | Reports.query, dimensions, metrics, filters, date ranges, channel vs content owner scope, yt-analytics scopes |

## Core Concept: Parts

Every resource response is controlled by the `part` parameter. You only get (and pay quota for) the parts you request:

```python
# Request only what you need — each part costs quota
youtube.videos().list(
    part="snippet,statistics",   # snippet=2, statistics=2 units
    id="dQw4w9WgXcQ"
).execute()
```

Common parts by resource:
- **Videos**: `snippet`, `contentDetails`, `statistics`, `status`, `player`, `localizations`, `topicDetails`
- **Channels**: `snippet`, `contentDetails`, `statistics`, `brandingSettings`, `status`
- **Playlists**: `snippet`, `contentDetails`, `status`, `player`
- **Search results**: `snippet` (only part available)

## Decision Trees

### Which Auth Method?

```
What data are you accessing?
├── Public data only (videos, channels, public playlists)
│   └── API Key — simple, no OAuth needed
│       └── youtube.videos().list(part="snippet", key="YOUR_KEY")
├── Reading/writing YOUR own channel's data
│   └── OAuth 2.0 — user account flow (credentials.json + token.json)
│       └── Scopes: youtube.readonly (read) or youtube (read+write)
├── Uploading videos, managing private content
│   └── OAuth 2.0 with youtube or youtube.upload scope
├── Accessing another user's data (with their permission)
│   └── OAuth 2.0 — user authorizes, you get their token
└── Server-to-server for YouTube (rare)
    └── Service accounts — only works if user grants domain-wide delegation
        └── Most YouTube operations require user OAuth, not service accounts
```

### Which API for Analytics?

```
What analytics do you need?
├── View counts, likes, subscriber count (basic, public)
│   └── YouTube Data API — Videos.list or Channels.list statistics part
├── Detailed analytics (watch time, traffic sources, demographics)
│   └── YouTube Analytics API — Reports.query
│       └── Requires youtube.readonly or yt-analytics.readonly scope
├── Bulk historical data downloads
│   └── YouTube Reporting API — for large datasets, async jobs
└── Realtime data (last 48 hours)
    └── YouTube Analytics API with realtimeReport resource
```

### Video Upload Flow

```
Upload a video
├── Step 1: Authenticate with youtube or youtube.upload scope
├── Step 2: Prepare metadata (snippet, status)
├── Step 3: Use MediaFileUpload for resumable upload
│   └── Required for files >5MB (use always for reliability)
├── Step 4: Videos.insert() — returns videoId
├── Step 5: (Optional) Upload thumbnail via Thumbnails.set()
└── Step 6: (Optional) Add to playlist via PlaylistItems.insert()
```

## Python Client Setup (Quick Start)

```python
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os

SCOPES = ["https://www.googleapis.com/auth/youtube"]

def get_authenticated_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)

youtube = get_authenticated_service()
```

See [auth.md](references/auth.md) for full setup including Google Cloud Console steps.

## Key Quotas at a Glance

| Operation | Cost (units) |
|-----------|-------------|
| read (list) | 1–3 |
| write (insert/update) | 50 |
| delete | 50 |
| search.list | 100 |
| upload (video insert) | 1600 |
| **Daily default limit** | **10,000 units** |

See [quotas-and-limits.md](references/quotas-and-limits.md) for full cost table and quota increase process.
