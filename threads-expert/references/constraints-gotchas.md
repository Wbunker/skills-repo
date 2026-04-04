# Threads Constraints, Gotchas, and Key Differences

## What the Threads API Cannot Do

These are hard limitations as of early 2026:

| Cannot Do | Notes |
|---|---|
| Send or read DMs | DMs exist in the app but are not accessible via API |
| Read other users' posts/profiles without their auth | Threads API is user-centric (OAuth); no server-side public content scraping |
| Access Stories | Threads has no Stories format (ghost posts are the ephemeral analog); not in API |
| Post Reels or Live video | No Reels or Live equivalent on Threads |
| Schedule posts natively | No `publish_time` parameter; scheduling requires third-party tooling |
| Manage ads | Ads are managed via Meta Marketing API / Ads Manager, not the Threads API |
| Access following/followers lists | Not a supported endpoint |
| Post on behalf of any user (without their OAuth grant) | Requires per-user OAuth — no admin-style posting to arbitrary accounts |
| Access private profiles' follower demographics | Private profiles cannot extend permission grants |
| Import or export contact lists | Not supported |
| Access data before April 13, 2024 | Insights `since`/`until` parameters don't work before this date |
| Get both demographic breakdowns in one call | Only one `follower_demographics` breakdown per API request (country OR city OR age OR gender) |
| Get per-post engagement for a custom date range | Post-level insights return totals, not time-series |

---

## Rate Limit Gotchas

- **250 posts per profile per 24-hour moving window** — not a rolling midnight reset but a true 24-hour sliding window
- Replies are excluded from the 250-post limit — only top-level posts count
- If you hit the rate limit, implement **exponential backoff** before retrying (1s → 2s → 4s → ...)
- Monitor `X-RateLimit-*` response headers to track remaining quota in real time
- Video containers require at least **30 seconds** between creation and publish step — failure to wait causes publish errors
- The `creation_id` from the container step expires — publish containers promptly; do not let them sit for hours

---

## App Review and Permission Gotchas

- Each OAuth scope requires a **separate app review** — plan for 2–4 weeks per permission
- While awaiting review, you can only publish to your own account and designated Tester accounts
- Your screencasts for app review must show the **full user journey** for each permission, not just an API call
- Apps must have a **publicly accessible server** for media hosting — Threads downloads the media at publish time; localhost URLs will fail
- `threads_basic` is required for ALL API calls — always request it even if you only need one other scope
- Public profiles' permission grants expire after 90 days; build token refresh logic early

---

## Publishing Gotchas

- Text limit is 500 characters — **URLs do not consume characters** in the character count, but emojis count at their UTF-8 byte length
- Image URLs must be publicly accessible at publish time — Threads fetches the image from the URL
- Video containers have a 30-second minimum wait before publishing — automate a `sleep` or polling check in your pipeline
- Carousel items must be created individually first (with `is_carousel_item: true`), then assembled — you cannot bundle them in one request
- Carousel items are uploaded to their own container IDs — keep track of IDs before assembling the parent carousel
- `reply_control` must be set at publish time — it cannot be changed after posting via API
- **No editing posts via API** — the Threads API does not support post editing (edit is available in-app)
- Post text attachments cannot be edited after posting (in-app or via API)
- `REPOST_FACADE` media types return empty insight arrays — don't treat this as an error

---

## Algorithm and Reach Considerations

- **Cross-posting from Instagram is penalized** — the algorithm detects and deprioritizes posts that are obviously cross-posted from Instagram (watermarks, different formatting, identical timing)
- Native Threads content outperforms cross-posts consistently
- Topic tags drive more reach — always include a relevant topic tag
- The algorithm weights **recency + engagement velocity** — a fast burst of early replies/likes boosts a post's reach window
- **"Rage bait" is actively filtered** — low-quality engagement-bait content (inflammatory questions, misleading hooks) is deprioritized since October 2024
- The For You feed provides strong non-follower discovery, but Meta is reducing unconnected reach in 2025–2026 to reward genuine follower relationships
- **Reply activity signals relevance** — threads (chains) with active replies are boosted; ghost replies are not helpful

---

## Policy Restrictions

- Must comply with **Meta's Community Standards** and **Threads Supplemental Privacy Policy**
- API developers must comply with the **Meta Platform Terms** and **Developer Policies**
- Threads prohibits: spam, coordinated inauthentic behavior, impersonation, hate speech, misinformation
- **No bulk follow/unfollow automation** — the API does not expose follow/unfollow endpoints; any such automation via unofficial means violates terms
- You may not use the API to scrape or archive other users' content at scale
- App ads and reply moderation features for ads have additional advertiser-specific policies

---

## Differences: Threads API vs Instagram Graph API

| Dimension | Threads API | Instagram Graph API |
|---|---|---|
| Base URL | `graph.threads.net/v1.0/` | `graph.facebook.com/v{n}/` |
| Identity / App type | Threads use case in Meta app | Instagram Business/Creator Login |
| Content types | Text-first; images, video, carousels, polls, GIFs, voice notes | Images, video, Reels, Stories, carousels |
| DMs | Not accessible via API | Instagram Messaging API (separate product) |
| Stories | Not available | Full Stories publishing support |
| Reels | Not a Threads concept | Reels publishing endpoint available |
| Shopping | Not available | Instagram Shopping / Product Catalog |
| Hashtag search | Topic tag search available | Hashtag search endpoint available |
| Business Discovery | Not available | Business Discovery API (view public biz profile) |
| Mentions webhook | Yes (for Threads) | Yes (for Instagram) |
| Insights metrics | Views, likes, replies, reposts, quotes | Impressions, reach, saves, profile visits, website clicks |
| Follower demographics | Country, city, age, gender (one per call) | More detailed breakdowns available |
| Carousel size | Up to 20 items | Up to 10 items |
| Video max length | 5 minutes | Reels up to 15 min; Feed video up to 60 min |
| Token host | `graph.threads.net` | `graph.facebook.com` |
| Scheduling parameter | Not available (third-party only) | Not native either — third-party or Meta Business Suite |
| Platform philosophy | Text-first, conversational | Visual-first (photos, video) |

---

## Threads vs X (Twitter) — Key Differences for Creators

| Feature | Threads | X / Twitter |
|---|---|---|
| Character limit | 500 (+ 10,000 text attachment) | 280 (free) / 25,000 (Premium) |
| URL in post | URLs don't count against limit | URLs count as 23 chars |
| Hashtags | Topic tags preferred; hashtags supported | Hashtags central to discovery |
| DMs | Yes (July 2025) | Yes |
| Lists | No native lists | Lists are a core feature |
| Algorithm | For You + Following feeds | Similar dual-feed model |
| API access | OAuth per-user; 250 posts/day | OAuth; tiered API access with costs |
| Ads | Meta Ads Manager | X Ads platform |
| Verification | Meta Verified ($11.99–$14.99/mo) | X Premium ($8–$22/mo) |
| Fediverse | Yes (ActivityPub, opt-in) | No |
| Scheduled posts | No native; third-party only | Via X API `scheduled_at` parameter |

---

## Common Developer Mistakes

1. **Forgetting the 30-second wait** before publishing video containers — causes `MEDIA_NOT_READY` errors
2. **Using localhost URLs** for media — Threads must be able to reach the URL at publish time
3. **Not requesting `threads_basic`** alongside other scopes — all calls require it
4. **Treating carousel item IDs as post IDs** — carousel items are not published posts; only the parent carousel container becomes the post
5. **Polling insights before data is ready** — some metrics (`views`, `shares`) are marked "in development" and may return empty or partial data
6. **Missing `follower_demographics` follower threshold** — requesting demographics with under 100 followers returns an error, not empty data
7. **Assuming Instagram Graph API patterns apply** — the Threads API is a different product with different endpoints and scopes; do not mix `graph.facebook.com` and `graph.threads.net` calls
8. **Not refreshing long-lived tokens** — 60-day expiry with no automatic refresh; build proactive refresh before expiry
9. **Using Tenor GIF URLs after March 31, 2026** — Tenor support was sunset; use GIPHY only
