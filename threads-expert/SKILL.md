---
name: threads-expert
description: >
  Comprehensive guide to Meta Threads — covers all consumer app features and the Threads developer API.
  Use when users ask about:
  (1) Using Threads: post types, character/media limits, For You vs Following feeds, replies/reposts/quotes/likes, search, topic tags, trending, profiles, DMs, pinned posts, cross-posting to Instagram, ActivityPub/fediverse integration
  (2) Creator and business use: verification badges (Meta Verified), analytics in-app vs API, monetization options, scheduling posts (native vs third-party), ads on Threads
  (3) Threads API: authentication (OAuth 2.0 scopes, token types), publishing workflow (container model), reading profiles/threads/replies, insights/analytics endpoints, webhooks, rate limits, app review process
  (4) Key constraints and gotchas: what the API cannot do, policy restrictions, algorithm/reach considerations, differences from Instagram Graph API
  (5) Recent 2025-2026 feature additions and API changes
---

# Threads Expert

## Quick Navigation

| Task | Reference File |
|---|---|
| App features — post types, limits, feeds, search, DMs, fediverse, recent updates | [app-features.md](references/app-features.md) |
| Creator and business tools — verification, analytics, monetization, scheduling, ads | [creator-business.md](references/creator-business.md) |
| Threads API — auth, scopes, tokens, publishing workflow, reading data, insights, webhooks | [threads-api.md](references/threads-api.md) |
| API constraints, gotchas, policy, algorithm, differences from Instagram API | [constraints-gotchas.md](references/constraints-gotchas.md) |

---

## Platform Overview

```
Threads Consumer App (threads.net + iOS/Android)
├── Post Types
│   ├── Text (500 chars) + Text Attachment (10,000 chars)
│   ├── Images (up to 10 per post, 8 MB each, JPEG/PNG/WebP/GIF)
│   ├── Video (up to 5 min, 1 GB, MP4/MOV)
│   ├── Carousels (up to 20 mixed images/videos)
│   ├── Polls (up to 4 options)
│   ├── GIFs (via GIPHY integration)
│   ├── Voice notes
│   └── Ghost posts (auto-archive after 24 hrs)
├── Feeds
│   ├── For You (algorithmic recommendations)
│   └── Following (chronological, accounts you follow)
├── Discovery
│   ├── Topic tags (not hashtags — interest-based categorization)
│   ├── Search (keyword, username, "From: username" syntax, date filters)
│   └── Trending Now (US; AI-generated summaries)
├── Social
│   ├── Replies (threaded conversations)
│   ├── Reposts, Quotes, Likes
│   ├── DMs (launched July 2025; group chats up to 50 users)
│   └── Communities (topic-based groups; US + South Korea)
├── Profile
│   ├── Bio (150 chars), up to 5 links, interest tags
│   ├── Pinned posts
│   ├── Cross-post to Instagram Stories
│   └── Active status indicator
└── Fediverse
    └── ActivityPub opt-in (posts visible on Mastodon, etc.)

Threads API (graph.threads.net/v1.0)
├── Publishing — two-step container model
├── Reading — profiles, threads, replies
├── Insights — post + user metrics
├── Webhooks — real-time event notifications
└── oEmbed + Web Intents — embedding and sharing
```

---

## Key Numbers at a Glance

| Item | Limit |
|---|---|
| Post text | 500 characters |
| Text attachment | 10,000 characters |
| Bio | 150 characters |
| Images per post | 10 (app) / 20 (carousel via API) |
| Max image file size | 8 MB |
| Max video length | 5 minutes |
| Max video file size | 1 GB (API) / ~500 MB (app) |
| Video formats | MP4 (H.264/HEVC), MOV |
| Image formats | JPEG, PNG, WebP, GIF |
| Poll options | Up to 4 |
| API posts per 24 hours | 250 (replies excluded) |
| Long-lived token validity | 60 days (refreshable) |
| Monthly active users | 400 million+ (August 2025) |

---

## Core Concepts

**Topic Tags vs Hashtags** — Threads uses topic tags, not traditional hashtags. They serve as interest markers to help posts reach people who care about a subject. Posts with a topic tag typically get more views. Hashtags are supported but not prominently promoted; emoji hashtags are also supported.

**Two-Feed System** — "For You" is algorithmic (similar to TikTok FYP); "Following" shows only accounts you follow in roughly chronological order. Meta has been rebalancing the algorithm to give more weight to people you follow.

**Fediverse Integration** — Threads implements ActivityPub. Users who opt in can have their posts seen on Mastodon, BookWyrm, WriteFreely, and other federated platforms. A dedicated Fediverse feed inside Threads shows posts from federated apps; users can search for fediverse profiles by handle. Replies from Threads to fediverse posts are not yet supported in all contexts.

**Threads vs Instagram Connection** — Threads accounts are linked to Instagram but can now be created independently (May 2025). The platforms share identity (profile name, photo) and follower relationships can be imported, but each has its own feed and content.
