# TikTok Developer APIs

## Overview

Developer portal: https://developers.tiktok.com  
Base URL for all v2 API calls: `https://open.tiktokapis.com`  
API version prefix: `/v2/`  
OAuth v1 reached end-of-life **February 29, 2024** — all integrations must use v2.

### Available API products

| Product | Purpose | Access |
|---------|---------|--------|
| Login Kit | OAuth 2.0 login with TikTok credentials | Open (requires app registration) |
| Content Posting API | Post videos/photos to user profiles | Requires audit for public posting |
| Display API | Read user's own videos and profile info | Open (requires app registration) |
| Research API | Query public video, user, and comment data | Restricted — academic/non-profit only |
| Commercial Content API | Branded content / ad disclosure tools | Business accounts |
| TikTok for Business API | Ad management, Spark Ads | Business / agency accounts |

---

## Authentication: OAuth 2.0

All user-level API calls require OAuth 2.0 authorization. App-only (server-to-server) tokens are supported for the Research API.

### Authorization flow (v2)

1. Redirect user to TikTok authorization endpoint:
   ```
   https://www.tiktok.com/v2/auth/authorize/
     ?client_key=YOUR_CLIENT_KEY
     &scope=user.info.basic,video.list
     &response_type=code
     &redirect_uri=YOUR_REDIRECT_URI
     &state=RANDOM_STATE
   ```

2. Exchange authorization code for tokens:
   ```
   POST https://open.tiktokapis.com/v2/oauth/token/
   Content-Type: application/x-www-form-urlencoded

   client_key=...
   &client_secret=...
   &code=...
   &grant_type=authorization_code
   &redirect_uri=...
   ```

3. Response includes:
   - `access_token` — expires in **86,400 seconds (24 hours)**
   - `refresh_token` — expires in **31,536,000 seconds (~1 year)**
   - `open_id` — unique user identifier
   - `scope` — comma-separated list of granted scopes

4. Refresh access token:
   ```
   POST https://open.tiktokapis.com/v2/oauth/token/
   grant_type=refresh_token
   &client_key=...
   &client_secret=...
   &refresh_token=...
   ```

### Key scopes

| Scope | Product | Purpose |
|-------|---------|---------|
| `user.info.basic` | Login Kit / Display API | Display name, avatar, open_id — granted by default |
| `user.info.profile` | Display API | Full profile: follower count, bio, etc. |
| `user.info.stats` | Display API | Follower/following/likes counts |
| `video.list` | Display API | Read user's own video list |
| `video.upload` | Content Posting API | Upload video file to TikTok servers |
| `video.publish` | Content Posting API | Directly publish video to user's profile |
| `video.views` | Display API | View counts on user's videos |

Requesting scopes: In the Developer Portal, add scopes per app on the app configuration page. Each user must individually authorize your app for any scope.

---

## Content Posting API

Allows apps to post videos or photos to a user's TikTok profile on their behalf.

**Important:** Unaudited clients can only post to **private (inbox) mode** — content is visible only to the creator as a draft. After a successful audit of your integration, public posting is unlocked.

### Two upload methods

| Method | Description |
|--------|-------------|
| `FILE_UPLOAD` | Your server sends the video bytes to TikTok via chunked PUT |
| `PULL_FROM_URL` | You provide a public URL; TikTok fetches the file itself |

### Video upload flow (FILE_UPLOAD)

**Step 1 — Initialize upload**
```
POST https://open.tiktokapis.com/v2/post/publish/video/init/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "post_info": {
    "title": "My video caption",
    "privacy_level": "PUBLIC_TO_EVERYONE",
    "disable_duet": false,
    "disable_comment": false,
    "disable_stitch": false,
    "video_cover_timestamp_ms": 1000
  },
  "source_info": {
    "source": "FILE_UPLOAD",
    "video_size": 50000000,
    "chunk_size": 10000000,
    "total_chunk_count": 5
  }
}
```

Response includes:
- `publish_id` — use to check status later
- `upload_url` — PUT chunks here

**Step 2 — Upload chunks**

Each PUT request uploads one chunk:
```
PUT {upload_url}
Content-Range: bytes {start}-{end}/{total}
Content-Length: {chunk_size}
Content-Type: video/mp4

[binary chunk data]
```

Chunking rules:
- Minimum chunk size: **5 MB** (except final chunk)
- Maximum chunk size: **64 MB** per chunk (final chunk can be up to 128 MB)
- Videos under 5 MB: single chunk (chunk_size = video_size)
- Maximum chunks: **1,000**
- Chunks must be uploaded **sequentially**

**Step 3 — Poll for status**
```
POST https://open.tiktokapis.com/v2/post/publish/status/fetch/
Authorization: Bearer {access_token}

{ "publish_id": "..." }
```

Status values: `PROCESSING_UPLOAD`, `PROCESSING_DOWNLOAD`, `PUBLISH_COMPLETE`, `FAILED`

### Direct post vs inbox post

- **Direct post** (`/v2/post/publish/video/init/`): publishes to public profile (requires audit)
- **Inbox/draft** (`/v2/post/publish/inbox/video/init/`): saves to creator's drafts only

### Photo post

```
POST https://open.tiktokapis.com/v2/post/publish/content/init/
```

Supports posting photo carousels. Requires `photo.publish` scope.

### Post parameters

| Parameter | Notes |
|-----------|-------|
| `title` | Caption text — up to 4,000 characters |
| `privacy_level` | `PUBLIC_TO_EVERYONE`, `MUTUAL_FOLLOW_FRIENDS`, `SELF_ONLY` |
| `disable_duet` | Boolean |
| `disable_stitch` | Boolean |
| `disable_comment` | Boolean |
| `video_cover_timestamp_ms` | Millisecond offset for cover frame |
| `brand_content_toggle` | Mark as branded/sponsored content |
| `brand_organic_toggle` | Mark as organic brand content |

### Rate limits (Content Posting API)

- Upload initialization: **6 requests per minute** per user access token
- General v2 API: varies by endpoint; multiple rate limit dimensions (user-level, app-level, endpoint-level, time-window)

---

## Display API

Allows reading a user's own TikTok profile and video data. Requires user authorization (not for reading other users' content — use Research API for that).

### Endpoints

**Get user info**
```
GET https://open.tiktokapis.com/v2/user/info/
  ?fields=open_id,union_id,avatar_url,display_name,bio_description,profile_deep_link,is_verified,follower_count,following_count,likes_count,video_count
Authorization: Bearer {access_token}
```

**List user videos**
```
GET https://open.tiktokapis.com/v2/video/list/
  ?fields=id,title,cover_image_url,share_url,video_description,duration,height,width,title,embed_html,embed_link,like_count,comment_count,share_count,view_count
Authorization: Bearer {access_token}
```

Returns videos sorted by `create_time` descending. Supports cursor-based pagination.

**Query specific videos by ID**
```
POST https://open.tiktokapis.com/v2/video/query/
Authorization: Bearer {access_token}

{ "filters": { "video_ids": ["vid1", "vid2"] } }
```

Up to **20 video IDs** per request.

---

## Research API

Provides access to **public** TikTok data for academic research. Not for commercial use.

### Eligibility

- Applicants must be affiliated with a **non-profit academic institution** in the US or Europe
- Applications reviewed at: https://developers.tiktok.com/products/research-api/
- Contact: Research-API@tiktok.com for quota increases

### Authentication

Uses **client credentials** flow (app-only, no user authorization):
```
POST https://open.tiktokapis.com/v2/oauth/token/
grant_type=client_credentials
&client_key=...
&client_secret=...
```

### Endpoints

**Video query**
```
POST https://open.tiktokapis.com/v2/research/video/query/
```
Search public videos with filters (date range, hashtag, keyword, region, etc.). Returns up to 100 videos per request.

Available fields: `id`, `video_description`, `create_time`, `region_code`, `share_count`, `view_count`, `like_count`, `comment_count`, `music_id`, `hashtag_names`, `username`, `effect_ids`, `playlist_id`, `voice_to_text`

**User info**
```
POST https://open.tiktokapis.com/v2/research/user/info/
```
Returns public profile data: bio, follower/following counts, likes count, video count, verified status.

**Comment query**
```
POST https://open.tiktokapis.com/v2/research/video/comment/list/
```
Returns comments for a given video ID: comment text, like count, reply count, create time.

**Followers/following lists**
```
POST https://open.tiktokapis.com/v2/research/user/followers/
POST https://open.tiktokapis.com/v2/research/user/following/
```

### Rate limits and quotas

| Limit | Value |
|-------|-------|
| Daily request limit | 1,000 requests/day |
| Records per day (Video + Comments API) | 100,000 records (100 per request × 1,000 calls) |
| Records per day (Followers/Following API) | 2,000,000 records (20,000 calls/day) |
| Daily reset | 12:00 AM UTC |

---

## Login Kit

Provides "Login with TikTok" for web and mobile apps. Available on iOS, Android, Desktop, and Web.

- Based on OAuth 2.0 authorization code flow
- `user.info.basic` scope is granted automatically
- Provides: `display_name`, `avatar_url`, `open_id`, `union_id`
- `union_id` is consistent across multiple apps owned by the same developer account

### App registration requirements

All API products require:
1. Register at developers.tiktok.com
2. Create a TikTok app (client_key + client_secret)
3. Configure redirect URIs
4. Request required scopes
5. Complete audit process for any publishing functionality
