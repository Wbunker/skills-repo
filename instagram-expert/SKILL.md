---
name: instagram-expert
description: >
  Comprehensive guide to Instagram — covers all app features and all developer APIs.
  Use when users ask about:
  (1) Using Instagram effectively: Feed, Stories, Reels, Live, DMs, Explore, Notes, Blend, Friends Map, Highlights
  (2) Creator and business accounts: switching account types, Insights, monetization (Subscriptions, Badges, Gifts, Reels Bonuses), Brand Partnerships, Instagram Shopping
  (3) Privacy and security: private accounts, Close Friends, blocking/restricting/muting, 2FA, passkeys, activity status, data controls
  (4) Instagram Graph API: authentication (Facebook Login vs Instagram Login), tokens, permissions, core nodes/edges for reading media/comments/mentions/hashtags
  (5) Content Publishing API: programmatically posting images, videos, Reels, carousels, Stories; media container flow; scheduling
  (6) Insights, Comments & Mentions API: account/media analytics, comment management, hashtag search, Business Discovery API
  (7) Any question about how Instagram works, best practices, feature comparisons, or developer integration troubleshooting
---

# Instagram Expert

## Quick Navigation

| Task | Reference File |
|---|---|
| Using Instagram features (Feed, Stories, Reels, Live, DMs, Explore, Notes, Blend, Friends Map, Highlights) | [app-features.md](references/app-features.md) |
| Creator/Business accounts, Insights, monetization, Instagram Shopping | [creator-business.md](references/creator-business.md) |
| Privacy settings, security, Close Friends, Restrict vs Block, 2FA | [privacy-security.md](references/privacy-security.md) |
| Instagram Graph API — auth, tokens, permissions, reading media/comments/hashtags | [graph-api.md](references/graph-api.md) |
| Publishing posts, Reels, Stories, carousels via API; scheduling | [publishing-api.md](references/publishing-api.md) |
| Account/media Insights API, comment management, hashtag search, Business Discovery | [insights-comments-api.md](references/insights-comments-api.md) |

---

## Platform Overview

```
Instagram App
├── Content Formats
│   ├── Reels (short video up to 3 min; highest reach)
│   ├── Stories (24-hour ephemeral; Close Friends option)
│   ├── Feed Posts (photos, carousels, long video)
│   ├── Live (real-time broadcast with Badges monetization)
│   └── Notes (60-char ephemeral text; DM inbox)
├── Discovery
│   ├── Feed (Following tab = chronological; Home = algorithmic)
│   ├── Explore (non-follower discovery; topic channels)
│   └── Reels tab (dedicated vertical scroll)
├── Social
│   ├── DMs (messages, View Once media, Blend shared feed)
│   ├── Friends Map (opt-in location sharing)
│   └── Highlights (permanent Story collections on profile)
└── Business/Creator Tools
    ├── Professional Dashboard (Insights + Monetization hub)
    ├── Instagram Shopping (product catalog + in-app checkout)
    └── Creator Marketplace (brand deal discovery)

Instagram API (Meta Developer Platform)
├── Instagram Graph API v22.0 (core data access)
│   ├── Content Publishing API
│   ├── Insights API
│   ├── Comment Management API
│   ├── Hashtag Search API
│   ├── Mentions API
│   └── Business Discovery API
└── Instagram Messaging API (DMs; via Messenger Platform)
```

---

## Critical API Facts (2026)

- **Basic Display API deprecated December 4, 2024** — personal accounts have no API access
- Only **Business** and **Creator** (Professional) accounts can use the Graph API
- **Two auth paths**: Facebook Login (requires linked Facebook Page) OR Instagram Login (no Page needed, 2025+)
- **Publishing limit**: 100 posts per account per 24-hour rolling window (Stories excluded)
- **Reels max duration**: 3 minutes (expanded from 90 seconds in 2026)
- **Hashtag search rate limit**: 30 unique hashtags per user per 7 days
- **Media container flow**: Create container → poll status → publish (videos/Reels require polling)

---

## Loading the Right Reference

Load only what's needed for the user's question:

- **"How does Instagram Explore work?"** → `app-features.md`
- **"Set up Instagram Shopping on my business account"** → `creator-business.md`
- **"How do I use Close Friends?"** → `privacy-security.md`
- **"Authenticate with the Instagram Graph API"** → `graph-api.md`
- **"Post a Reel via the API"** → `publishing-api.md`
- **"Pull insights for my posts programmatically"** → `insights-comments-api.md`
- **"Manage comments and reply via API"** → `insights-comments-api.md`
- **Multi-topic question** → load the 2 most relevant reference files
