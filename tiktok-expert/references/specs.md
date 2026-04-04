# TikTok Platform Specs and Limits

## Video specifications

### Length

| Upload method | Maximum length |
|--------------|---------------|
| Pre-recorded upload (web/app) | **60 minutes** |
| In-app recording | **10 minutes** |
| TikTok Ads (in-feed) | 60 seconds (recommended <15s for ads) |
| Creator Rewards Program eligibility | **Minimum 1 minute** |

### Resolution and aspect ratio

| Spec | Recommended | Also supported |
|------|-------------|---------------|
| Aspect ratio | **9:16** (vertical) | 16:9, 1:1 |
| Resolution | **1080 × 1920 px** (Full HD) | 720×1280 minimum |
| Minimum resolution | 720×1280 | — |

Note: 9:16 vertical is strongly preferred — horizontal and square videos get smaller playback area and lower FYP distribution.

### File size

| Context | Limit |
|---------|-------|
| iOS app upload | Up to **287.6 MB** |
| Android app upload | Up to **72 MB** |
| Web upload (videos ≤3 min) | Up to **500 MB** |
| Web upload (videos 3–10 min) | Up to **2 GB** |
| Video ads | Up to **500 MB** |
| Content Posting API (FILE_UPLOAD) | No explicit cap; chunked upload supports large files |

### File formats

| Type | Supported formats |
|------|------------------|
| Preferred | **MP4, MOV** |
| Also supported | AVI, MPEG, 3GP, WebM |
| Video codec | H.264 recommended |
| Audio codec | AAC recommended |

### Frame rate

| Rate | Support |
|------|---------|
| Recommended | **30 fps** |
| Also supported | 23.98, 24, 25, 29.97, 30, 60 fps |

---

## Caption (description) limits

| Parameter | Value |
|-----------|-------|
| Maximum characters | **4,000** (expanded from 2,200; updated 2024/2025) |
| Visible before truncation | ~100–150 characters |
| Clickable links | Not supported in captions |
| Emoji support | Yes |

---

## Hashtag limits

| Parameter | Value |
|-----------|-------|
| Maximum hashtags registered per post | **5** (as of August 13, 2025) |
| Behavior if >5 used | Only first 5 are indexed; additional are ignored |
| Recommended strategy | 1-2 broad + 1-2 niche + 1 trending (if relevant) |

---

## Profile limits

| Element | Limit |
|---------|-------|
| Username | 1–24 characters; letters, numbers, underscores, periods |
| Display name | Up to 30 characters |
| Bio | **160 characters** (expanded from 80; rollout occurred mid-2025) |
| Link in bio | 1 clickable URL (requires Business or Creator account in some regions) |
| Profile photo | JPG/PNG; recommended 200×200 px minimum |

Note: Bio character limit was increased from 80 to 160 characters during a 2025 rollout. Some accounts may still show the 80-character limit if the update hasn't reached them.

---

## Comment limits

| Parameter | Value |
|-----------|-------|
| Maximum comment length | **150 characters** |
| Comment replies | Supported |
| Comment threads | Limited depth |

---

## Photo post specs

| Parameter | Value |
|-----------|-------|
| Formats | JPG, PNG, WebP |
| Aspect ratio | 9:16, 1:1, or 3:4 supported |
| Maximum photos per carousel | Up to **35 images** |
| Minimum resolution | 720×960 px (for 3:4); 720×1280 px (for 9:16) |

---

## LIVE streaming specs

| Parameter | Value |
|-----------|-------|
| Minimum followers to go LIVE | **1,000** |
| Minimum age (LIVE Gifts) | **18** |
| Maximum LIVE duration | No hard cap; TikTok recommends natural session lengths |
| Desktop streaming protocol | RTMP |
| Max co-hosts (multi-guest) | **20** |
| Video resolution (recommended) | 1080p (1920×1080) at 30fps |
| Recommended bitrate (streaming) | 2,500–4,000 kbps |

---

## TikTok Series specs

| Parameter | Value |
|-----------|-------|
| Maximum videos per Series | **80** |
| Maximum video length | **20 minutes per episode** |
| Price range | **$0.99 – $189.99 USD** |
| Content format | Pre-recorded video only |

---

## Scheduling limits

| Parameter | Value |
|-----------|-------|
| Platform | Web (studio.tiktok.com) only |
| Minimum advance time | ~15 minutes |
| Maximum advance scheduling | ~10 days (240 hours) |

---

## API limits (summary)

| Parameter | Value |
|-----------|-------|
| Base URL | `https://open.tiktokapis.com` |
| API version | v2 |
| Access token TTL | 86,400 seconds (24 hours) |
| Refresh token TTL | 31,536,000 seconds (~1 year) |
| Content Posting API: init rate limit | 6 requests/minute per user token |
| Chunked upload: min chunk size | 5 MB |
| Chunked upload: max chunk size | 64 MB (final chunk up to 128 MB) |
| Chunked upload: max chunks | 1,000 |
| Display API: max video IDs per query | 20 |
| Research API: requests per day | 1,000 |
| Research API: records per day (Video/Comments) | 100,000 |
| Research API: records per day (Followers/Following) | 2,000,000 |

---

## Quick-reference summary card

```
Video:        9:16, 1080×1920px, MP4/MOV, H.264+AAC
Length:       Up to 60 min (upload), 10 min (in-app record)
File size:    Up to 2 GB (web, 3-10min videos)
Caption:      4,000 characters max
Hashtags:     5 max (Aug 2025)
Bio:          160 characters (expanded 2025)
Link in bio:  1 URL
Comment:      150 characters
Series:       80 videos, 20 min each, $0.99–$189.99
LIVE:         1K followers, 18+, up to 20 co-hosts
Schedule:     Web only, up to 10 days ahead
API base:     https://open.tiktokapis.com/v2/
```
