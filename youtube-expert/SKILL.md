---
name: youtube-expert
description: >
  Comprehensive guide to YouTube as a platform and via the YouTube Data API v3.
  Use when the user asks about: creating or managing a YouTube channel, uploading
  videos, optimizing titles/thumbnails/descriptions, understanding YouTube Studio
  analytics, growing a channel, monetization (YPP), live streaming, the YouTube
  algorithm, or building applications with the YouTube Data API v3 (search, video
  metadata, playlists, comments, subscriptions, live broadcasts, quota management,
  OAuth2 authentication).
---

# YouTube Expert

## Navigation — load the relevant reference file(s)

| Topic | Reference file | Load when... |
|-------|---------------|--------------|
| Data API v3 (auth, endpoints, quota) | [references/api-v3.md](references/api-v3.md) | User asks about API integration, code, quota, OAuth |
| Upload workflow, end screens, cards, chapters | [references/creator-studio.md](references/creator-studio.md) | User asks about uploading, optimizing, or editing videos |
| Channel customization, branding, layout | [references/channel-management.md](references/channel-management.md) | User asks about channel setup, banner, handle, sections |
| Analytics (Reach, Engagement, Audience, Revenue) | [references/analytics.md](references/analytics.md) | User asks about metrics, CTR, watch time, RPM, growth |
| Algorithm, discovery, ranking | [references/algorithm.md](references/algorithm.md) | User asks about growth, recommendations, how YouTube ranks content |
| Monetization, YPP requirements, revenue streams | [references/monetization.md](references/monetization.md) | User asks about making money, YPP, memberships, Super Chat |

Load only the file(s) relevant to the current question. Most questions require one file.

---

## Quick facts

- **YouTube Studio desktop**: studio.youtube.com — full control over uploads, analytics, customization, monetization
- **YouTube Studio mobile app**: best for comments, notifications, quick stats; lacks end screens, cards, bulk editing, scheduling, monetization settings
- **YouTube Data API v3 base URL**: `https://www.googleapis.com/youtube/v3/`
- **Daily quota**: 10,000 units per Google Cloud project; resets midnight Pacific Time
- **Most expensive call**: `search.list` = 100 units; use `playlistItems.list` (1 unit) to enumerate a channel's videos instead
- **Key specs**: Thumbnail 1280×720 px, <2 MB · Banner 2560×1440 px (safe zone 1546×423 px) · Profile pic 800×800 px
