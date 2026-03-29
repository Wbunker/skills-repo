---
name: x-api
description: >
  Expert knowledge of the X (formerly Twitter) API v2 for developers building
  applications, bots, or agents that interact with X. Covers what is and isn't
  possible via the official API, authentication setup, tier selection, Python
  integration with tweepy, and rate limit management. Use when the user asks
  about: posting tweets, reading timelines, searching X, DMs, follows/likes,
  building X bots, X API pricing/tiers, authenticating with X, tweepy usage,
  or whether a specific X feature is available via API. Also triggers on
  "Twitter API", "X developer", "tweet programmatically", or any reference to
  building on top of X/Twitter.
---

# X API v2

X (formerly Twitter) has a REST API (v2) for programmatic access to posts,
users, DMs, lists, and more.

## Quick orientation

Read `references/api-overview.md` for: capabilities by category, pricing tiers,
what is NOT available via API, and when browser automation might be needed.

Read `references/tweepy-guide.md` for: Python setup with tweepy, auth patterns,
common operations, streaming, and rate limit handling.

## Authentication decision tree

| Goal | Method |
|------|--------|
| Read public data only | Bearer Token (app-only) |
| Post, DM, like, follow as a user | OAuth 2.0 with PKCE (or OAuth 1.0a) |
| Server-to-server (no user) | OAuth 2.0 App-Only |

**Setup steps:**
1. Create a project + app at developer.x.com
2. Enable required permissions (read/write/DM) on the app
3. Store credentials: `API_KEY`, `API_KEY_SECRET`, `ACCESS_TOKEN`, `ACCESS_TOKEN_SECRET`, `BEARER_TOKEN`

## Tier selection guide

| Need | Minimum tier |
|------|-------------|
| Just post tweets | Free ($0) |
| Read timelines, search, user lookup | Basic ($200/mo) |
| Filtered stream, full-archive search | Pro ($5,000/mo) |
| Firehose, compliance feeds | Enterprise (negotiate) |

> **Note:** Free tier is post-only as of 2025. Reading anything (search, timeline, profiles) requires Basic or higher.

## Recommended Python library

**tweepy** is the standard choice: `pip install tweepy`

- Use `tweepy.Client` for all v2 endpoints
- Use `tweepy.API` only if you need legacy v1.1 features (avoid for new code)

See `references/tweepy-guide.md` for patterns and examples.

## Common pitfalls

- **Media uploads**: Must use v2 media endpoints (v1.1 deprecated 2025)
- **Rate limits**: Two dimensions — per-15-minute window AND monthly post quota
- **Free tier reads**: All read endpoints return 429 or 403 on Free tier
- **DM rate limit**: 1,440 DM conversations per 24 hours regardless of tier
- **v1.1 search**: Deprecated; use `GET /2/tweets/search/recent` instead
