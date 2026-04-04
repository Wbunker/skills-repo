# Instagram Graph API

## Table of Contents
1. [Overview & Requirements](#overview--requirements)
2. [Authentication](#authentication)
3. [Permissions](#permissions)
4. [Core Nodes & Edges](#core-nodes--edges)
5. [Webhooks](#webhooks)
6. [Rate Limits](#rate-limits)
7. [Error Handling](#error-handling)

---

## Overview & Requirements

The Instagram Graph API allows programmatic access to Instagram Business and Creator accounts. It is built on top of the Facebook Graph API.

**Base URL:** `https://graph.facebook.com/v{version}/{endpoint}`
**Current version:** v22.0
**Reference:** developers.facebook.com/docs/instagram-platform

### Account Requirements
- Instagram account must be **Business** or **Creator** (Professional) type
- **Basic Display API was deprecated December 4, 2024** — no personal account API access exists
- Historically required a connected Facebook Page; new "Instagram API with Instagram Login" (2025+) allows access without a linked Page for Professional accounts

### Two Auth Paths

| Path | Facebook Page Required | Use Case |
|---|---|---|
| **Facebook Login** (legacy) | Yes | Most established integrations |
| **Instagram Login** (new, 2025+) | No | Simpler setup for new apps with Professional accounts |

---

## Authentication

### Path 1: Facebook Login (with Facebook Page)

**Step 1** — OAuth Authorization URL:
```
https://www.facebook.com/v22.0/dialog/oauth?
  client_id={app-id}
  &redirect_uri={redirect-uri}
  &scope=instagram_basic,instagram_content_publish,pages_show_list
  &response_type=code
```

**Step 2** — Exchange code for User Access Token:
```bash
GET https://graph.facebook.com/v22.0/oauth/access_token?
  client_id={app-id}
  &redirect_uri={redirect-uri}
  &client_secret={app-secret}
  &code={code}
```

**Step 3** — Get the Instagram Business Account ID:
```bash
GET /me/accounts?access_token={user-token}
# Returns Pages with their tokens

GET /{page-id}?fields=instagram_business_account&access_token={page-token}
# Returns the Instagram account ID linked to the Page
```

**Step 4** — Extend to long-lived User Token (60 days):
```bash
GET https://graph.facebook.com/v22.0/oauth/access_token?
  grant_type=fb_exchange_token
  &client_id={app-id}
  &client_secret={app-secret}
  &fb_exchange_token={short-lived-token}
```

**Step 5** — Get a non-expiring Page Token:
```bash
GET /{page-id}?fields=access_token&access_token={long-lived-user-token}
```

### Path 2: Instagram Login (no Facebook Page required)

Available for new apps using the Instagram Platform product:
1. Add "Instagram" product in App Dashboard (not "Facebook Login")
2. OAuth flow uses `https://api.instagram.com/oauth/authorize`
3. Returns an Instagram User Access Token directly
4. Works with Professional (Business/Creator) accounts only
5. Access is limited to that Instagram user's own account data

**Reference:** developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login

### Debugging a Token
```bash
GET https://graph.facebook.com/debug_token?
  input_token={token-to-check}
  &access_token={app-id}|{app-secret}
```

---

## Permissions

### Key Instagram Permissions

| Permission | Access |
|---|---|
| `instagram_basic` | Read profile, media, and basic account info |
| `instagram_content_publish` | Publish posts, Reels, and Stories |
| `instagram_manage_comments` | Read, hide, and reply to comments |
| `instagram_manage_insights` | Read account and media insights |
| `instagram_manage_messages` | Read and send DMs (limited to some account types) |
| `pages_show_list` | List Facebook Pages the user manages |
| `pages_read_engagement` | Read Page content (needed for some Instagram endpoints) |
| `business_management` | Manage Business Manager assets |

### App Review
- Basic permissions (`instagram_basic`) work in development mode without review
- Publishing, insights, comment management, and messaging require **App Review** from Meta
- App must demonstrate actual use case during review

---

## Core Nodes & Edges

### Instagram Business Account Node (`/{ig-user-id}`)

Get the IG User ID first via the Page lookup above.

```bash
# Read profile
GET /{ig-user-id}?fields=id,username,name,biography,followers_count,media_count,website

# Get all media
GET /{ig-user-id}/media?fields=id,media_type,timestamp,like_count,comments_count

# Get Stories (only live Stories — expires after 24hrs)
GET /{ig-user-id}/stories?fields=id,media_type,timestamp

# Account-level insights
GET /{ig-user-id}/insights?metric=impressions,reach,profile_views&period=day

# Hashtag search (get hashtag ID first, then query)
GET /ig_hashtag_search?user_id={ig-user-id}&q=coffee

# Business discovery (look up other public accounts by username)
GET /{ig-user-id}?fields=business_discovery.fields(username,followers_count,media_count,media)
```

### Media Node (`/{ig-media-id}`)

```bash
# Get media details
GET /{ig-media-id}?fields=id,media_type,media_url,thumbnail_url,permalink,timestamp,like_count,comments_count

# Get comments on a media object
GET /{ig-media-id}/comments?fields=id,text,username,timestamp

# Get insights for a specific media object
GET /{ig-media-id}/insights?metric=impressions,reach,saved,video_views

# Get carousel children
GET /{ig-media-id}/children?fields=id,media_type,media_url
```

**Media types:** `IMAGE`, `VIDEO`, `CAROUSEL_ALBUM`, `REEL`

### Comment Node (`/{ig-comment-id}`)

```bash
# Read a comment
GET /{ig-comment-id}?fields=text,username,timestamp,replies{text,username}

# Reply to a comment
POST /{ig-comment-id}/replies
  body: message=Thanks for your comment!

# Hide/unhide a comment
POST /{ig-comment-id}
  body: hide=true

# Delete a comment
DELETE /{ig-comment-id}
```

### Hashtag Node (`/{ig-hashtag-id}`)

```bash
# Step 1: Get hashtag ID (search is per-user for rate limit purposes)
GET /ig_hashtag_search?user_id={ig-user-id}&q=coffee
# Returns: { "data": [{ "id": "17843830..."}] }

# Step 2: Query top or recent media for that hashtag
GET /{ig-hashtag-id}/top_media?user_id={ig-user-id}&fields=id,media_type,permalink
GET /{ig-hashtag-id}/recent_media?user_id={ig-user-id}&fields=id,media_type,permalink

# Get hashtag info
GET /{ig-hashtag-id}?fields=name
```

**Rate limit:** 30 unique hashtags per user per 7 days

### Mentions

When your account is @mentioned in a post or comment:

```bash
# Get media where your account is tagged
GET /{ig-user-id}/tags?fields=id,media_type,permalink,timestamp

# Get media where your account is mentioned in a caption
GET /{ig-user-id}?fields=mentioned_media.fields(id,media_type,permalink)
```

### Messaging (DMs)

```bash
# Get conversations
GET /{ig-user-id}/conversations?fields=id,participants,messages{message,from,created_time}

# Send a message (requires instagram_manage_messages permission + approval)
POST /me/messages
  body: recipient={id:"{ig-scoped-user-id}"}, message={text:"Hello"}
```

---

## Webhooks

Subscribe to real-time events instead of polling.

**Subscribe to fields:**
```bash
POST https://graph.facebook.com/v22.0/{app-id}/subscriptions
  body:
    object=instagram
    callback_url=https://yourserver.com/webhook
    fields=mentions,comments,messages
    verify_token=your_secret
    access_token={app-token}
```

**Webhook must:**
- Accept GET for verification: return `hub.challenge` when `hub.verify_token` matches
- Accept POST for event delivery within 20 seconds

**Available webhook fields:**
- `mentions` — when your account is @mentioned
- `comments` — new comments on your media
- `story_insights` — when a Story expires (insights available)
- `messages` — incoming DMs

---

## Rate Limits

| Limit | Threshold |
|---|---|
| Graph API calls | 200 calls/hour per user per app |
| Content publishing | 100 posts per 24-hour rolling window |
| Hashtag searches | 30 unique hashtags per user per 7 days |
| Business Discovery | 30 lookups per user per 7 days |

**Response headers to monitor:**
- `X-App-Usage` — current app-level consumption percentage
- `X-Business-Use-Case-Usage` — per-feature usage

**Best practices:**
- Use webhooks instead of polling for comment/mention events
- Cache media and profile data (it rarely changes)
- Batch fields in a single request: `?fields=id,username,followers_count,media_count`

---

## Error Handling

Common error codes:

| Code | Meaning | Action |
|---|---|---|
| `10` | Permission denied / App not approved | Check permissions and App Review status |
| `100` | Invalid parameter | Fix the request |
| `190` | Access token expired or invalid | Re-authenticate user |
| `200` | Permissions error | User needs to re-grant permission |
| `4` | App-level rate limit | Slow down, implement backoff |
| `17` | User-level rate limit | Back off for this user |
| `32` | Page-level rate limit | Back off for this Page |
| `368` | Account blocked for policy violation | User account is restricted |

**Error response format:**
```json
{
  "error": {
    "message": "Invalid OAuth access token.",
    "type": "OAuthException",
    "code": 190,
    "fbtrace_id": "A..."
  }
}
```
