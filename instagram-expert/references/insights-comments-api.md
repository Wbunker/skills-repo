# Instagram Insights, Comments & Mentions API

## Table of Contents
1. [Insights API](#insights-api)
2. [Comment Management API](#comment-management-api)
3. [Mentions API](#mentions-api)
4. [Hashtag Search API](#hashtag-search-api)
5. [Business Discovery API](#business-discovery-api)

---

## Insights API

Retrieve analytics for accounts and individual media objects.

**Required permission:** `instagram_manage_insights`

### Account-Level Insights

```bash
GET /{ig-user-id}/insights
  ?metric={comma-separated-metrics}
  &period={period}
  &since={unix-timestamp}      # Optional date range
  &until={unix-timestamp}
  &access_token={token}
```

**Period options:** `day`, `week`, `days_28`, `month`, `lifetime`

**Available metrics by period:**

| Metric | day | week | days_28 | month | lifetime |
|---|---|---|---|---|---|
| `impressions` | ✓ | ✓ | ✓ | ✓ | |
| `reach` | ✓ | ✓ | ✓ | ✓ | |
| `profile_views` | ✓ | ✓ | ✓ | ✓ | |
| `website_clicks` | ✓ | ✓ | ✓ | ✓ | |
| `email_contacts` | ✓ | ✓ | ✓ | ✓ | |
| `phone_call_clicks` | ✓ | ✓ | ✓ | ✓ | |
| `direction_clicks` | ✓ | ✓ | ✓ | ✓ | |
| `follower_count` | ✓ | | | | |
| `get_directions_clicks` | ✓ | | | | |
| `accounts_engaged` | ✓ | ✓ | ✓ | ✓ | |
| `total_interactions` | ✓ | ✓ | ✓ | ✓ | |

**Example — last 30 days reach and impressions:**
```bash
GET /{ig-user-id}/insights?metric=impressions,reach,profile_views&period=days_28&access_token={token}
```

### Audience Demographics Insights

```bash
GET /{ig-user-id}/insights
  ?metric=audience_city,audience_country,audience_gender_age,audience_locale
  &period=lifetime
  &access_token={token}
```

**Note:** Demographic metrics only available with `period=lifetime`.

### Follower/Following Counts

```bash
GET /{ig-user-id}?fields=followers_count,follows_count,media_count&access_token={token}
```

### Media-Level Insights

```bash
GET /{ig-media-id}/insights?metric={metrics}&access_token={token}
```

**Metrics by media type:**

**Images and Videos (feed):**
- `impressions`, `reach`, `saved`, `video_views`, `plays`
- `likes`, `comments`, `shares`
- `profile_visits`, `follows`
- `total_interactions`

**Reels:**
- `plays`, `reach`, `saved`, `comments`, `likes`, `shares`
- `total_interactions`
- `ig_reels_avg_watch_time`, `ig_reels_video_view_total_time`

**Stories (only while live; expires after 24h):**
- `impressions`, `reach`
- `taps_forward`, `taps_back`, `exits`
- `replies`
- `navigation` (combination metric)

**Carousel Albums:**
- `impressions`, `reach`, `saved`
- `carousel_album_impressions`, `carousel_album_reach`, `carousel_album_saved`

**Example — Reel insights:**
```bash
GET /{ig-media-id}/insights
  ?metric=plays,reach,saved,comments,likes,shares,ig_reels_avg_watch_time
  &access_token={token}
```

### Getting Insights for All Recent Media

```bash
# Get all media IDs first
GET /{ig-user-id}/media?fields=id,timestamp,media_type&limit=20&access_token={token}

# Then batch-fetch insights for each media ID
# Use Facebook Graph API batch requests to reduce calls:
POST https://graph.facebook.com/v22.0/
  body:
    access_token={token}
    batch=[
      {"method":"GET","relative_url":"{media-id-1}/insights?metric=impressions,reach,saved"},
      {"method":"GET","relative_url":"{media-id-2}/insights?metric=impressions,reach,saved"}
    ]
```

---

## Comment Management API

**Required permission:** `instagram_manage_comments`

### Read Comments

```bash
# Get all comments on a media object
GET /{ig-media-id}/comments
  ?fields=id,text,username,timestamp,like_count,replies{id,text,username,timestamp}
  &access_token={token}

# Get a single comment
GET /{ig-comment-id}?fields=text,username,timestamp&access_token={token}
```

### Reply to a Comment

```bash
POST /{ig-comment-id}/replies
  body:
    message=Thanks for commenting!
    access_token={token}
```

### Reply to a Top-Level Comment on Media

```bash
POST /{ig-media-id}/comments
  body:
    message=Great question!
    access_token={token}
```

### Hide / Unhide a Comment

```bash
POST /{ig-comment-id}
  body:
    hide=true    # or false to unhide
    access_token={token}
```

### Delete a Comment

```bash
DELETE /{ig-comment-id}?access_token={token}
```

### Enable / Disable Comments on a Media Object

```bash
POST /{ig-media-id}
  body:
    comment_enabled=false    # or true
    access_token={token}
```

---

## Mentions API

Track when your account is @mentioned in posts and comments.

**Required permission:** `instagram_manage_comments` (for mentions in comments), `instagram_basic` (for tagged media)

### Get Media Where Your Account is Tagged

```bash
GET /{ig-user-id}/tags
  ?fields=id,media_type,permalink,timestamp,like_count
  &access_token={token}
```

### Get Media Where Your Account is Mentioned in Caption

Use the `mentioned_media` field on the IG user:
```bash
GET /{ig-user-id}?fields=mentioned_media.fields(id,media_type,permalink,timestamp)&access_token={token}
```

### Get a Mentioned Comment's Details

When your account is mentioned in a comment (via webhook), use:
```bash
GET /{ig-user-id}?fields=mentioned_comment.fields(text,timestamp)
  &commented_media_id={ig-media-id}
  &access_token={token}
```

### Webhook for Real-Time Mentions

Set up a webhook for the `mentions` field to receive instant notifications:
```json
{
  "field": "mentions",
  "value": {
    "media_id": "...",
    "comment_id": "...",   // present if mentioned in a comment
    "mentioned_media_id": "..."
  }
}
```

---

## Hashtag Search API

Discover content using specific hashtags.

**Rate limit:** Up to 30 unique hashtags per IG user per 7 days

### Step 1: Get the Hashtag ID

```bash
GET /ig_hashtag_search
  ?user_id={ig-user-id}
  &q=coffee
  &access_token={token}
# Response: {"data": [{"id": "17843830134"}]}
```

IDs are stable — cache them to avoid repeated lookups.

### Step 2: Query Top or Recent Media

```bash
# Top media (most relevant/popular)
GET /{ig-hashtag-id}/top_media
  ?user_id={ig-user-id}
  &fields=id,media_type,permalink,like_count,comments_count,timestamp
  &access_token={token}

# Recent media (most recent)
GET /{ig-hashtag-id}/recent_media
  ?user_id={ig-user-id}
  &fields=id,media_type,permalink,timestamp
  &access_token={token}
```

**Returned fields** (limited for privacy): `id`, `media_type`, `permalink`, `timestamp`
- `like_count` and `comments_count` only available on your own media or when you're the account querying
- Cannot access full media URLs or captions of other users' posts via hashtag search

### Get Hashtag Name

```bash
GET /{ig-hashtag-id}?fields=name&access_token={token}
```

### Get Recently Searched Hashtags

```bash
GET /{ig-user-id}/recently_searched_hashtags?access_token={token}
```

---

## Business Discovery API

Look up basic public information about other Instagram Business/Creator accounts by username.

**Use case:** Competitor research, influencer discovery, brand monitoring

```bash
GET /{your-ig-user-id}?
  fields=business_discovery.fields(
    username,
    name,
    biography,
    followers_count,
    follows_count,
    media_count,
    website,
    profile_picture_url,
    media{id,media_type,permalink,like_count,comments_count,timestamp}
  )
  &username={target-username}
  &access_token={token}
```

**Rate limit:** 30 lookups per user per 7 days

**Requirements:**
- Your account must be a Business or Creator account
- Target account must also be a Business or Creator account
- Personal accounts are not discoverable via this API

**Returned data:** Public profile info + their recent media metadata (no private content)
