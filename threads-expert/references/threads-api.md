# Threads API — Developer Reference

## Overview

The Threads API is Meta's official developer platform for programmatic access to Threads. It is hosted at `graph.threads.net` (not `graph.facebook.com`) and is separate from the Instagram Graph API.

- **Base URL**: `https://graph.threads.net/v1.0/`
- **Protocol**: HTTPS only
- **Format**: JSON responses
- **Auth**: OAuth 2.0 with short-lived and long-lived user access tokens

API access requires creating a Meta app with the "Threads" use case selected in the Meta for Developers portal.

---

## Authentication

### OAuth 2.0 Flow

1. Redirect user to authorization window:
   ```
   GET https://threads.net/oauth/authorize
     ?client_id={app-id}
     &redirect_uri={redirect-uri}
     &scope=threads_basic,threads_content_publish
     &response_type=code
   ```

2. User grants permissions; system redirects to your `redirect_uri` with a `code` parameter

3. Exchange the code for a short-lived token:
   ```
   POST https://graph.threads.net/oauth/access_token
   Body: client_id, client_secret, code, grant_type=authorization_code, redirect_uri
   ```
   Returns: `{ "access_token": "THQVJ...", "user_id": 17841405793187218 }`
   **Authorization codes are valid for 1 hour and can only be used once.**

4. Optionally upgrade to a long-lived token:
   - Exchange short-lived token via the refresh endpoint
   - Long-lived tokens are valid for **60 days**
   - Refreshable within the 60-day window before expiry
   - Tokens are app-scoped (unique per app + user pair)

### Token Expiration Notes
- Short-lived tokens: ~1 hour
- Long-lived tokens: 60 days, refreshable
- Permission grants from **public profiles** expire after 90 days (token refresh extends this)
- Permission grants from **private profiles** cannot be extended — require re-authorization

---

## OAuth Scopes / Permissions

All Threads API calls require `threads_basic`. Additional scopes unlock specific functionality.

| Scope | Purpose | App Review Required |
|---|---|---|
| `threads_basic` | Read profile info and user's own published media | Yes (basic review) |
| `threads_content_publish` | Publish posts on behalf of user | Yes |
| `threads_read_replies` | GET operations on replies (read conversations) | Yes |
| `threads_manage_replies` | POST/DELETE on replies (hide, delete, reply) | Yes |
| `threads_manage_insights` | GET analytics/insights for posts and account | Yes |
| `threads_share_to_instagram` | Cross-share posts to Instagram Stories (added Mar 2026) | Yes |

**App Review Process**:
- Meta reviews each scope/permission separately
- Typical review timeline: **2–4 weeks per permission**
- Screencasts must show the full user journey for each permission requested
- During review, you can publish to your own account and accounts registered as Testers in your Meta developer app — sufficient for development and testing

---

## Publishing: Creating Posts

All publishing uses a **two-step container model**:

### Step 1 — Create Media Container

```
POST https://graph.threads.net/v1.0/{user-id}/threads
```

**Text Post**
```json
{
  "media_type": "TEXT",
  "text": "Your post content here",
  "access_token": "..."
}
```

**Image Post**
```json
{
  "media_type": "IMAGE",
  "image_url": "https://your-server.com/image.jpg",
  "text": "Optional caption",
  "access_token": "..."
}
```
Image specs: JPEG or PNG, max 8 MB, 320–1440 px wide, aspect ratio up to 10:1, sRGB color space

**Video Post**
```json
{
  "media_type": "VIDEO",
  "video_url": "https://your-server.com/video.mp4",
  "text": "Optional caption",
  "access_token": "..."
}
```
Video specs: MP4 or MOV, H.264 or HEVC codec, 23–60 FPS, max 1920 px wide, max 5 minutes, max 1 GB, AAC audio up to 48 kHz (mono or stereo)

Returns: `{ "id": "{container-id}" }`

### Step 2 — Publish Container

```
POST https://graph.threads.net/v1.0/{user-id}/threads_publish
Body: { "creation_id": "{container-id}", "access_token": "..." }
```

**Important**: Wait at least **30 seconds** between creating and publishing, especially for video (processing time).

Returns the published Thread's `id`.

---

## Publishing: Carousels

Three-step process:

**Step 1** — Create each carousel item (add `"is_carousel_item": true`):
```json
{
  "media_type": "IMAGE",
  "image_url": "https://...",
  "is_carousel_item": true,
  "access_token": "..."
}
```
Repeat for each item. Returns an item `id` for each.

**Step 2** — Create carousel container:
```json
{
  "media_type": "CAROUSEL",
  "children": "ITEM_ID_1,ITEM_ID_2,ITEM_ID_3",
  "text": "Carousel caption",
  "access_token": "..."
}
```
Supports **2–20 items**, images and/or videos mixed.

**Step 3** — Publish with `threads_publish` endpoint (same as single posts).

---

## Publishing: Replies

To reply to an existing post, add `reply_to_id` to the container creation:

```json
{
  "media_type": "TEXT",
  "text": "My reply",
  "reply_to_id": "{original-post-id}",
  "access_token": "..."
}
```

**Replies do NOT count against the 250 posts/day rate limit** — only new top-level posts do.

---

## Publishing: Reply Controls

Control who can reply to your post with the `reply_control` parameter:

| Value | Who can reply |
|---|---|
| `everyone` | Default; anyone |
| `followers` | Only accounts that follow you |
| `mentioned_only` | Only accounts you @mention in the post |

---

## Publishing: GIFs, Polls, Ghost Posts, Spoiler Tags

**GIFs** (October 2025 via API, February 2026 GIPHY-only):
- Specify GIPHY GIF URL; Tenor support ended March 31, 2026

**Polls**: Create polls with up to 4 options via the API

**Ghost Posts** (December 2025): Posts that auto-archive after 24 hours — available via API

**Spoiler Tags** (October 2025): Tag post content as a spoiler so it requires a tap to reveal

**Text Attachments** (October 2025): Long-form content up to 10,000 characters attached to a post

---

## Publishing: Cross-Posting to Instagram Stories

Requires `threads_share_to_instagram` scope (added March 25, 2026):
- Shares the Threads post as an Instagram Story
- Reply moderation for Threads ads also became available simultaneously

---

## Reading: User Profile

```
GET https://graph.threads.net/v1.0/{user-id}
  ?fields=id,username,name,threads_profile_picture_url,threads_biography
  &access_token=...
```

Available fields: `id`, `username`, `name`, `threads_profile_picture_url`, `threads_biography`, `followers_count` (requires 100+ followers)

---

## Reading: User's Threads

```
GET https://graph.threads.net/v1.0/{user-id}/threads
  ?fields=id,media_type,text,timestamp,permalink,shortcode,is_quote_post
  &access_token=...
```

Available fields per post: `id`, `media_type`, `media_url`, `permalink`, `owner`, `username`, `text`, `timestamp`, `shortcode`, `thumbnail_url`, `children`, `is_quote_post`

---

## Reading: Replies

```
GET https://graph.threads.net/v1.0/{threads-media-id}/replies
  &access_token=...
```

Requires `threads_read_replies` scope.

---

## Reading: Search

- Keyword search and topic tag search available via API
- Posts can be searched by topic to facilitate content discovery

---

## Insights (Analytics) API

Requires `threads_manage_insights` scope.

### Post-Level Insights
```
GET https://graph.threads.net/v1.0/{threads-media-id}/insights
  ?metric=views,likes,replies,reposts,quotes,shares
  &access_token=...
```

| Metric | Description |
|---|---|
| `views` | Times post was played or displayed (in development) |
| `likes` | Like count |
| `replies` | Reply count (total for root posts; direct only for replies) |
| `reposts` | Repost count |
| `quotes` | Quote post count |
| `shares` | Shares (in development) |

Note: `REPOST_FACADE` posts return empty arrays. Nested replies are excluded from reply counts.

### User-Level Insights
```
GET https://graph.threads.net/v1.0/{user-id}/threads_insights
  ?metric=views,likes,replies,reposts,quotes,followers_count,follower_demographics
  &since=UNIX_TIMESTAMP
  &until=UNIX_TIMESTAMP
  &access_token=...
```

| Metric Type | Metrics |
|---|---|
| Time series | `views` |
| Total values | `likes`, `replies` (top-level only), `reposts`, `quotes`, `followers_count` |
| Link totals | `clicks` |
| Demographics | `follower_demographics` (breakdown: country, city, age, gender) |

**Demographic caveats**:
- Minimum **100 followers** required to access `follower_demographics`
- Only **one breakdown parameter** allowed per request
- `followers_count` and `follower_demographics` ignore `since`/`until` date parameters

**Date range caveats**:
- `since` and `until` do NOT work for dates before **April 13, 2024**
- User insights reliability begins **June 1, 2024**

---

## Webhooks

Threads supports webhooks for real-time event notifications — no polling required.

Supported webhook events include:
- **Mentions**: instant notification when a user mentions your account in a post
- **Replies**: real-time notification of replies to your posts

Webhook setup follows the standard Meta webhook verification flow (hub.verify_token, hub.challenge).

Webhooks can also be used for reply moderation workflows.

---

## oEmbed and Web Intents

**oEmbed** — Embed Threads posts on external websites:
- `GET https://www.threads.net/oembed?url={post-permalink}`
- As of March 3, 2026: **no access token required** for oEmbed requests

**Web Intents** (expanded March 2026):
- Pre-populate the compose UI for users clicking a link
- Parameters for creating new posts, replies, and quote posts
- Useful for "Click to post on Threads" call-to-action buttons

---

## Rate Limits

| Limit | Value |
|---|---|
| API-published posts per 24-hour moving window | **250 posts per profile** |
| Replies | Not counted against the 250 post limit |
| Rate limit headers | Check `X-RateLimit-*` headers in API responses |
| Retry strategy | Exponential backoff (1s → 2s → 4s → ...) |

---

## API Versioning

- Base URL includes version: `https://graph.threads.net/v1.0/`
- Check `developers.facebook.com/docs/threads/changelog/` for version updates
- The changelog is also mirrored on Threads at `@threadsapi.changelog`

---

## Key API Changelog Entries (2025–2026)

| Date | Change |
|---|---|
| Mar 25, 2026 | `threads_share_to_instagram` scope; reply moderation for ads |
| Mar 19, 2026 | Web Intents support for replies and quote posts |
| Mar 3, 2026 | oEmbed without access tokens |
| Feb 27, 2026 | GIPHY GIF support; Tenor API sunset March 31, 2026 |
| Feb 17, 2026 | App ads introduced for Threads advertising platform |
| Dec 15, 2025 | Ghost posts available via API |
| Oct 28, 2025 | Advantage+ catalog ads; image carousels supported |
| Oct 17, 2025 | GIF attachment capability |
| Oct 3, 2025 | Spoiler tags and text attachments |
| Sep 23, 2025 | API opened to non-Instagram-linked Threads profiles (except follower metrics) |
| Mid-2025 | Keyword and topic tag search; location tagging; poll creation; quote posts; webhooks; alt text; carousel (up to 20 items) |
| Jul 2024 | Initial Threads API launch |
