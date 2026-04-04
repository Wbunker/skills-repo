# YouTube Algorithm Reference

## Table of Contents
1. [How YouTube recommends content](#how-youtube-recommends-content)
2. [Primary ranking signals](#primary-ranking-signals)
3. [Personalization signals](#personalization-signals)
4. [Shorts algorithm (separate system)](#shorts-algorithm-separate-system)
5. [Discovery surfaces](#discovery-surfaces)
6. [What the algorithm does NOT care about](#what-the-algorithm-does-not-care-about)
7. [Common algorithm mistakes](#common-algorithm-mistakes)
8. [Strategy implications](#strategy-implications)

---

## How YouTube recommends content

YouTube's recommendation system has two goals:
1. **Help viewers find videos they want to watch**
2. **Keep viewers on the platform longer**

The algorithm is not a single ranking system — it operates per surface (home, search, suggested, Shorts feed, notifications) with different weightings per surface. What works for search ranking may differ from what gets pushed on the home feed.

**Key insight (2025+):** YouTube shifted to **satisfaction-weighted discovery**. A viewer who watches a short video completely and clicks Like signals more satisfaction than a viewer who watches 40% of a long video. Raw watch time is still important at the channel level, but per-video viewer satisfaction scores are increasingly weighted.

---

## Primary ranking signals

### 1. Click-Through Rate (CTR)
- Definition: % of impressions (thumbnail shown) that became a view
- **Driven by:** thumbnail quality + title quality, working together
- YouTube tests content with a small audience first. Low CTR → reduced distribution
- Target: 4–6% for most channels; 2% minimum to maintain distribution
- CTR is a short-term signal. YouTube also looks at what happens after the click.

### 2. Watch time (absolute hours)
- The strongest channel-level ranking signal for long-form content
- Total cumulative hours watched across all your videos — builds over time
- A channel with 10 hours total watch time will be deprioritized vs. one with 10,000 hours
- **Implication:** Consistency compounds. More uploads = more total watch time = more recommendation weight

### 3. Average view duration / audience retention
- How much of each video the average viewer watches
- YouTube cares about *sustained attention*, not just completion
- Target: Hold >70% of viewers through the midpoint; don't let viewers leave in the first 30 seconds
- The retention curve is the diagnostic tool — see [analytics.md](analytics.md)

### 4. Viewer satisfaction signals
- YouTube runs post-watch surveys asking "Was this video worth your time?"
- Survey results are weighted heavily — they reflect actual satisfaction vs. passive behavior
- Satisfaction correlates with: delivery on the thumbnail/title promise, practical value, emotional engagement
- **Clickbait backfires**: High CTR + low satisfaction = algorithmic suppression

### 5. Session continuation
- Does the viewer continue watching YouTube after your video ends?
- YouTube rewards videos that keep users on the platform
- **End screens** that recommend related YouTube videos (not external links) signal positively
- Playlists increase session continuation by auto-playing the next video

### 6. Engagement signals
- Likes, comments, shares, saves — but only when correlated with watch time
- A video with many likes but low watch time is suspicious; a video with deep watch time and few likes is fine
- "Not interested" clicks and dislikes suppress distribution
- **Shares** are the strongest engagement signal — sharing is a high-intent action

### 7. Return viewership
- Viewers who come back to your channel repeatedly signal loyalty
- YouTube rewards channels that build consistent audiences vs. one-hit viral videos
- Returning viewers influence how much the algorithm promotes new uploads to your subscriber base

---

## Personalization signals

YouTube's algorithm is heavily personalized. For any given viewer, it weighs:

- **Watch history**: What topics and channels has this person watched?
- **Subscriptions**: What channels are they subscribed to?
- **Like/dislike/not interested history**: Explicit feedback signals
- **Time of day and device**: Viewing behavior differs by context (TV in evening, mobile on commute)
- **Watch-together patterns**: What do people who watch X also watch? (collaborative filtering)
- **Geographic and language preferences**

**Implication:** Your video may be shown to different audience segments based on personalization. A video about beginner cooking will be pushed to cooking beginners, not cooking experts, even on the same platform.

---

## Shorts algorithm (separate system)

**As of late 2025, YouTube Shorts runs a fully independent algorithm from long-form.** Shorts performance does not help or hurt long-form recommendations, and vice versa.

### Shorts-specific signals
| Signal | Weight |
|--------|--------|
| **Swipe-through rate** (inverse) | High — swiping past = negative signal |
| **Loop rate** | High — rewatching signals strong content |
| **Shares** | High — most powerful Shorts signal |
| **Average percentage viewed** | High — completion matters for short content |
| CTR | N/A — Shorts use swipe interface, not click interface |
| Likes | Medium |
| Comments | Medium |

### Shorts strategy implications
- Hooks must work in the **first 0.5–1 second** (swipe decision is near-instant)
- Loops are rewarded — design videos that are naturally re-watchable or loop seamlessly
- Shorts audience does not automatically convert to long-form subscribers
- Use Shorts to reach new audiences; use long-form to monetize and retain them

---

## Discovery surfaces

| Surface | How content is selected |
|---------|------------------------|
| **Home feed** | Personalized; based on watch history, subscriptions, trending topics |
| **YouTube Search** | Title, description, captions, tags; relevance + engagement for the keyword |
| **Suggested videos** | Videos watched together with the just-watched video (collaborative filtering) |
| **Subscriptions feed** | Chronological uploads from subscribed channels |
| **Trending / Explore** | Regional popularity; usually news, sports, entertainment — hard to optimize for |
| **Notifications** | Sent to subscribers who have notifications enabled (~10–30% of subscribers) |
| **Shorts feed** | Shorts-specific; see above |
| **Email digests** | YouTube sends weekly email summaries to subscribers |

**Search vs. recommendation strategy:**
- **Search-optimized content**: Evergreen topics, tutorial/how-to, answers to specific questions. Builds steady long-term traffic. Optimize title and description for keywords.
- **Recommendation-optimized content**: Engaging, broad-appeal, trending topics, high retention. Drives spikes of traffic from home feed and suggested videos.
- Best channels do both: use search for baseline traffic and use retention-focused content to earn algorithm recommendations.

---

## What the algorithm does NOT care about

Common myths, debunked:

| Myth | Reality |
|------|---------|
| Post at the perfect time of day | Time of posting has minimal direct impact; audience availability matters more |
| Tag stuffing improves ranking | Tags have very low weight; title and description matter much more |
| More uploads always = more growth | Consistent quality > high frequency; infrequent high-quality uploads beat frequent poor-quality ones |
| Buying subscribers/views helps | Fake engagement is detected and penalized; inflates metrics without real signals |
| YouTube demonetization hurts recommendations | Monetization status does not directly affect recommendations |
| Longer videos always rank higher | Length doesn't matter; *retention rate at that length* matters |
| Using #shorts hashtag guarantees Shorts distribution | Aspect ratio and length (<60 seconds) determine Shorts classification, not hashtags alone |

---

## Common algorithm mistakes

1. **Thumbnail-title mismatch**: Clicking a thumbnail and finding different content than expected drives immediate exits and survey dissatisfaction
2. **Too-long intros**: Recapping what the video will cover before delivering it kills retention in the first 30 seconds — get to value immediately
3. **Inconsistent posting that breaks momentum**: Algorithm rewards channels that upload consistently; a 3-month gap resets recommendation momentum
4. **Ignoring the retention curve**: Most creators never read their retention data — it's the clearest signal of where content is failing
5. **Optimizing for views over watch time**: A video with 100K views at 10% APV is worse than 10K views at 70% APV for algorithmic placement
6. **Switching niches abruptly**: The algorithm has built a picture of your audience; a sudden niche change confuses personalization and reduces distribution

---

## Strategy implications

### For new channels (0–1K subscribers)
- Focus on **search-optimized content** — search is the most merit-based discovery surface
- Long-tail keywords ("how to do X in Y specific situation") have lower competition than broad terms
- Build a library of 20–30 videos before expecting significant algorithmic support
- Optimize thumbnail CTR aggressively — it's your primary lever early on

### For growing channels (1K–100K subscribers)
- Balance search and recommendation content
- Analyze which videos drive the most subscriber growth (not just views)
- Identify your "gateway videos" — the ones non-subscribers find first — and optimize them
- Build playlists to increase session continuation

### For established channels (100K+)
- Audience signals are well-established; algorithm promotes reliably to known audience
- Experiment with content variations; you have enough data to measure impact
- Protect watch time per video — one low-retention video can reduce recommendations on subsequent uploads temporarily
- Evergreen content continues to compound — a tutorial from 2 years ago can still drive 30% of daily views
