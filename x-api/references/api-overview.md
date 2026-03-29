# X API v2 — Capabilities & Tiers Reference

## Table of Contents
1. [What You Can Do via API](#capabilities)
2. [What Is NOT Available via API](#not-available)
3. [Pricing Tiers](#pricing)
4. [Rate Limits](#rate-limits)
5. [Authentication Methods](#auth)

---

## Capabilities

### Posts (Tweets)
- Create, delete, look up posts
- Get timelines: home timeline, user timeline, mentions
- Search recent posts (7 days on Basic, 30 days on Pro, full archive on Enterprise)
- Like/unlike, retweet/unretweet, quote posts
- Hide/unhide replies
- Get tweet counts over time
- Filtered stream — real-time stream matching rules (Pro+)
- Sampled stream — 1% random sample (Pro+)

### Users
- Look up users by ID or username
- Manage follows/followers
- Manage blocks and mutes
- Get follower/following lists

### Direct Messages
- Send and receive DMs (1:1 and group conversations)
- Look up DM conversation history
- Hard limit: 1,440 DM conversations per 24 hours per app

### Media
- Upload images, GIFs, videos via v2 media endpoints
- Update media metadata and subtitles
- **Note:** v1.1 media upload endpoints deprecated in 2025 — use v2 only

### Lists
- Create, update, delete lists
- Add/remove members, get list tweets/members/followers
- Pin/unpin lists

### Spaces (Audio)
- Look up live Spaces
- Search Spaces
- Get Space participants

### Bookmarks
- Get, add, remove bookmarks for the authenticated user

### Trends
- Get top trending topics by location (WOEID)
- Returns top 50 trends; volume data not available on Basic

### Engagement Metrics
- Impressions, likes, reposts, replies, video views returned as fields on post objects
- Only available for posts authored by the authenticated user's app

---

## Not Available via API

These require the Ads API (separate application), browser automation, or are simply unavailable:

| Feature | Notes |
|---------|-------|
| Ads management & analytics | Separate X Ads API — different application process |
| Notification feed | No public endpoint |
| Profile view analytics ("who viewed") | Not exposed |
| Full firehose (100% of public tweets) | Enterprise only |
| Compliance/deletion feeds | Enterprise only (legally required if archiving tweets) |
| Historical data beyond tier limits | Basic = 7 days, Pro = 30 days; no workaround |
| Account suspension/ban detection | Returns 404 or 403, no structured event |
| Trending topic volume data | Not available on Free or Basic |
| Detailed account-level analytics | Beyond basic engagement metrics on posts |

### When to consider browser automation
Only if you need features above that have no API equivalent (e.g., notification feed,
detailed analytics dashboards). The official API covers the vast majority of developer
use cases. Using browser automation against X's terms of service carries account
suspension risk.

---

## Pricing Tiers

| Tier | Cost | Post writes/mo | Post reads/mo | Key features |
|------|------|----------------|---------------|--------------|
| **Free** | $0 | ~500 | Effectively none | Write-only; no search, no timeline, no user lookup |
| **Basic** | $200/mo | ~50,000 | ~10,000–15,000 | Full read/write, 7-day search, user lookup |
| **Pro** | $5,000/mo | ~300,000 | 1,000,000 | Full-archive search, filtered stream, sampled stream |
| **Enterprise** | $42,000+/mo | 50M+ | 50M+ | Full firehose, compliance feeds, custom limits |

**Pay-per-use (launched Feb 2026):** Credits model — ~$0.01/post write, ~$0.005/post read.
Capped at 2M reads/month. Good for sporadic workloads.

**Key restrictions on Free tier (as of 2025):**
- No search (`GET /2/tweets/search/recent`)
- No timeline reads
- No user lookup
- No likes or follows endpoints
- Essentially post-creation only

---

## Rate Limits

Rate limits operate in **two dimensions**:
1. Per-15-minute window (per endpoint)
2. Monthly post consumption quota (per tier)

### Key per-endpoint limits (Basic/Pro, 15-minute windows)

| Endpoint | Per App | Per User |
|----------|---------|----------|
| `GET /2/tweets` (lookup) | 3,500 | 5,000 |
| `GET /2/tweets/search/recent` | 450 | 300 |
| `POST /2/tweets` (create) | 10,000/24hrs | 100/24hrs |
| `GET /2/users/:id/following` | 300 | 300 |
| `POST /2/dm_conversations` | 1,440/24hrs | 1,440/24hrs |
| `GET /2/users/:id/bookmarks` | — | 180 |

### Rate limit headers
Every response includes:
- `x-rate-limit-limit` — window limit
- `x-rate-limit-remaining` — calls left
- `x-rate-limit-reset` — Unix timestamp when window resets

Tweepy raises `tweepy.TooManyRequests` (HTTP 429) when limits are hit.
Use `wait_on_rate_limit=True` in the client to auto-sleep.

---

## Auth

### Bearer Token (App-Only)
- Read-only access to public data
- Generate via: `POST oauth2/token` with API Key + Secret
- Set as `bearer_token` in tweepy.Client
- Cannot perform write operations

### OAuth 1.0a (User Context, Legacy)
- Four credentials: API Key, API Secret, Access Token, Access Token Secret
- Still fully supported; many older examples use this
- Works for all user-context operations

### OAuth 2.0 with PKCE (User Context, Recommended)
- Modern standard; supports fine-grained scopes
- Scopes: `tweet.read`, `tweet.write`, `dm.read`, `dm.write`, `users.read`, `offline.access`
- Required for user-delegated actions (post, DM, follow, like)
- Supports token refresh via `offline.access` scope
