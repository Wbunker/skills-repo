# Instagram Content Publishing API

## Table of Contents
1. [Overview & Limits](#overview--limits)
2. [Publishing Flow](#publishing-flow)
3. [Single Image Post](#single-image-post)
4. [Single Video Post](#single-video-post)
5. [Reels](#reels)
6. [Carousel Posts](#carousel-posts)
7. [Stories](#stories)
8. [Scheduling Posts](#scheduling-posts)
9. [Container Status Codes](#container-status-codes)

---

## Overview & Limits

The Content Publishing API lets you programmatically publish to Instagram Business and Creator accounts.

**Required permission:** `instagram_content_publish`

**Limits:**
- **100 posts** per Instagram account per 24-hour rolling window
- Carousels count as **1 post** (not per-item)
- Stories do **not** count toward the 100-post limit
- Reels count as **1 post**

**Supported media types:** Single image, Single video, Reel, Carousel (mixed image/video), Story (image or video)

**Not supported via API:** Live video, Notes, Threads posts

---

## Publishing Flow

All media publishing follows a two-step pattern:

```
Step 1: Create a media container
  POST /{ig-user-id}/media
  → Returns container_id

Step 2: Check container status (for video/Reels/Stories)
  GET /{container-id}?fields=status_code
  → Poll until FINISHED

Step 3: Publish the container
  POST /{ig-user-id}/media_publish
    body: creation_id={container-id}
  → Returns published media id
```

Images are processed synchronously — no polling needed. Videos, Reels, and Stories require polling.

---

## Single Image Post

```bash
# Step 1: Create container
POST /{ig-user-id}/media
  body:
    image_url=https://example.com/photo.jpg   # Must be publicly accessible HTTPS URL
    caption=My caption here #hashtag
    location_id={facebook-place-id}           # Optional
    user_tags=[{"username":"someuser","x":0.5,"y":0.5}]  # Optional; tag people
    access_token={token}

# Response: {"id": "{container-id}"}

# Step 2: Publish immediately (images don't need status polling)
POST /{ig-user-id}/media_publish
  body:
    creation_id={container-id}
    access_token={token}
```

**Image requirements:**
- Format: JPEG (recommended), PNG, BMP, TIFF, WEBP
- Max size: 8MB
- Aspect ratios: 4:5 (portrait), 1:1 (square), 1.91:1 (landscape)
- Min width: 320px; Max width: 1440px

---

## Single Video Post

```bash
# Step 1: Create container
POST /{ig-user-id}/media
  body:
    media_type=VIDEO
    video_url=https://example.com/video.mp4   # Publicly accessible HTTPS URL
    caption=Video caption #hashtag
    thumb_offset=1000                         # Optional; millisecond offset for cover frame
    access_token={token}

# Step 2: Poll status until FINISHED
GET /{container-id}?fields=status_code&access_token={token}
# status_code values: EXPIRED | ERROR | FINISHED | IN_PROGRESS | PUBLISHED

# Step 3: Publish
POST /{ig-user-id}/media_publish
  body:
    creation_id={container-id}
    access_token={token}
```

**Video requirements:**
- Format: MOV or MP4 (H.264 codec, AAC audio)
- Max size: 100MB
- Min duration: 3 seconds; Max: 60 minutes (feed video)
- Aspect ratio: 4:5 recommended for feed

---

## Reels

```bash
# Step 1: Create Reel container
POST /{ig-user-id}/media
  body:
    media_type=REELS
    video_url=https://example.com/reel.mp4
    caption=Reel caption #hashtag
    share_to_feed=true                        # Show in Feed (true) or Reels tab only (false)
    thumb_offset=1000                         # Cover frame in milliseconds
    access_token={token}

# Step 2: Poll status
GET /{container-id}?fields=status_code&access_token={token}

# Step 3: Publish
POST /{ig-user-id}/media_publish
  body:
    creation_id={container-id}
    access_token={token}
```

**Reels requirements:**
- Format: MOV or MP4 (H.264, AAC audio)
- Aspect ratio: 9:16 (vertical); 1080×1920px recommended
- Max duration: **3 minutes** (2026 — expanded from 90 seconds)
- Max file size: 1GB
- Min duration: 3 seconds
- Frame rate: 23–60 fps

**Note:** Audio must be either original audio or properly licensed. Copyrighted music added via the API is not officially supported — users should add music through the app.

---

## Carousel Posts

Carousel = a single post with 2–10 images/videos users can swipe through.

```bash
# Step 1: Create item containers for each card
POST /{ig-user-id}/media
  body: image_url=https://example.com/img1.jpg&is_carousel_item=true&access_token={token}
# Repeat for each card (up to 10 items)
# Collect all container IDs

# Step 2: Create the carousel container
POST /{ig-user-id}/media
  body:
    media_type=CAROUSEL
    children={container-id-1},{container-id-2},{container-id-3}
    caption=Carousel caption here
    access_token={token}

# Step 3: Publish
POST /{ig-user-id}/media_publish
  body:
    creation_id={carousel-container-id}
    access_token={token}
```

**Carousel requirements:**
- 2–10 items per carousel
- Mix images and videos in the same carousel
- Each item must be `is_carousel_item=true`
- Videos in carousels: max 60 seconds each
- All items must be the same aspect ratio (1:1 recommended for mixed)

---

## Stories

```bash
# Image Story
POST /{ig-user-id}/media
  body:
    media_type=STORIES
    image_url=https://example.com/story.jpg
    access_token={token}

# Video Story
POST /{ig-user-id}/media
  body:
    media_type=STORIES
    video_url=https://example.com/story.mp4
    access_token={token}

# Poll status (video only)
GET /{container-id}?fields=status_code&access_token={token}

# Publish
POST /{ig-user-id}/media_publish
  body:
    creation_id={container-id}
    access_token={token}
```

**Story requirements:**
- Aspect ratio: 9:16 (1080×1920px)
- Image: JPEG, PNG; max 8MB
- Video: MOV or MP4; max 100MB; 1–15 seconds

**Limitation:** Interactive stickers (polls, questions, links) cannot be added via the API — they can only be added through the Instagram app.

---

## Scheduling Posts

Schedule a post up to 75 days in the future.

```bash
# Step 1: Create the container with a scheduled_publish_time
POST /{ig-user-id}/media
  body:
    image_url=https://example.com/photo.jpg
    caption=Scheduled post
    published=false
    scheduled_publish_time=1714521600    # Unix timestamp (must be 10 min–75 days in future)
    access_token={token}

# Step 2: Check scheduled media list
GET /{ig-user-id}/media?fields=id,caption,scheduled_publish_time,status&access_token={token}

# Step 3: To publish early or update the scheduled time
POST /{container-id}
  body:
    scheduled_publish_time={new-unix-timestamp}
    access_token={token}

# Step 4: To cancel a scheduled post — delete the container
DELETE /{container-id}?access_token={token}
```

---

## Container Status Codes

Poll `GET /{container-id}?fields=status_code` until you see `FINISHED` before publishing.

| Status | Meaning |
|---|---|
| `IN_PROGRESS` | Media is still being processed; continue polling |
| `FINISHED` | Ready to publish |
| `PUBLISHED` | Already published (if `published=true` was used) |
| `ERROR` | Processing failed; check `status` field for error details |
| `EXPIRED` | Container expired (24 hours after creation) without publishing |

**Polling strategy:**
```
Poll every 5 seconds for 30 seconds
Then poll every 30 seconds for 5 minutes
Then poll every 2 minutes (images rarely need this long)
Fail/alert after 10 minutes
```

**On ERROR:**
```bash
GET /{container-id}?fields=status,status_code&access_token={token}
# status field will have error details (e.g., "Video format not supported")
```
