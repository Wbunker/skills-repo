# TikTok Algorithm and For You Page (FYP)

## How the FYP works

TikTok's For You Page is a personalized content feed driven by a recommendation system that evaluates each video against predicted user interest. Unlike Instagram or YouTube, follower count has minimal impact on initial distribution — every video is independently evaluated.

The system has three primary input signal categories:

### 1. User interactions (highest weight)
- Video completion rate (strongest single signal)
- Re-watches
- Shares (highest engagement signal — outweighs likes)
- Saves (weighted above likes in 2025)
- Comments (quality/length now matters more than count)
- Likes
- "Not interested" reports (negative signal)
- Profile visits from the video

### 2. Video information
- Caption text and keywords
- Hashtags (up to 5; relevance > popularity)
- Audio / sound used
- On-screen text (crawled for keywords)
- Visual content (computer vision analysis)
- Effects and filters used

### 3. User settings and device context
- Language preference
- Country / region
- Device type
- Account age and activity history

---

## Waterfall / batch distribution model

TikTok does not blast videos to a large audience at once. Instead it uses a staged testing system:

### Stage 1 — Follower pool test (2025 update)
New videos are first shown to a subset of your **existing followers**. The algorithm measures:
- Completion rate among followers
- Early shares and saves

This is a 2025/2026 shift from the original model where non-followers were served first.

### Stage 2 — Small FYP batch
If follower engagement is strong, the video is pushed to a small cold audience (~200–500 users) from the broader FYP pool who match the predicted interest profile.

**Key threshold**: ~60–70% completion rate needed to advance (up from ~50% in earlier years).

### Stage 3 — Expanded distribution
Strong stage 2 performance triggers a much larger FYP rollout (10K–100K+ users).

### Stage 4 — Viral loop
Videos that continue to perform above average receive ongoing boosts: 100K–1M+ views, potentially global distribution.

### Timing
- Critical evaluation window: **first 3 hours** after posting
- Full initial cycle: 24–48 hours
- "Delayed virality" is possible: TikTok can re-serve old videos if similar content trends

---

## Primary ranking signals explained

### Completion rate
- The **single most important signal**
- Measures: what percentage of viewers watched to the end
- Re-watches count toward completion rate improvement
- 2025 target threshold for progression: ~60–70%
- Hook quality (first 1-3 seconds) directly drives this metric

### Watch time
- Both absolute watch time and relative completion are tracked
- Search-sourced views require 30+ seconds to count as "qualified" for Creator Rewards

### Shares
- Highest-weighted engagement action
- A share moves your video to someone outside TikTok's existing recommendation pool
- Share rate (shares / views) is a top algorithmic promoter

### Saves
- Signals "I want to return to this" — strong intent indicator
- Weighted above likes in 2025 algorithm

### Comments
- Quality matters more than volume in 2025 — long/substantive comments carry more weight
- Comments also extend the video's visible engagement window

### Likes
- Positive signal but lowest-weighted of the active engagement actions

---

## Hashtags, sounds, and captions as discovery mechanisms

### Hashtags

- Max 5 per post (August 2025 cap)
- Function as **topic signals** not reach multipliers — they tell the algorithm what the content is about
- Recommended mix: 1-2 broad topic tags + 1-2 niche community tags + 1 trending (only if genuinely relevant)
- Stuffing with unrelated popular tags now **reduces** reach by misaligning content with audience

### Sounds

- Trending sounds create a category signal: the algorithm knows what type of content typically uses a given sound
- Using trending sounds can boost distribution by placing content alongside a popular trend
- Original audio: creates a unique sound other creators can reuse, building passive discovery
- Business accounts: limited to TikTok's commercial music library (personal accounts have broader access)

### Captions (SEO / search)

- TikTok is now functionally a **search engine** — 40%+ of Gen Z use it as their primary search tool
- Caption keywords are indexed and influence search result ranking
- Best practice: place primary keyword within the **first 150 characters**
- Keyword placement priority: on-screen text (highest) → voiceover → caption

---

## Account authority vs. individual video performance

TikTok is fundamentally a **video-level** algorithm, not a channel-level one. Any video can go viral regardless of the account's size or history.

However, account-level signals do matter in secondary ways:
- **Niche consistency**: 10–15 consistent topical posts help the algorithm build an accurate "interest profile" for your account, improving audience matching
- **Posting cadence**: Regular posting maintains algorithmic presence
- **Historical engagement**: Accounts with consistently high engagement may receive slightly larger initial test batches
- **Community Guidelines standing**: Violations suppress distribution; repeated violations can permanently reduce reach

### Niche consistency vs. variety

- **Micro-niche specialization outperforms broad variety** in current algorithm behavior (as of 2025)
- Depth over breadth: TikTok rewards accounts that are reliably about a specific topic
- Pivoting niches resets the audience-matching process

---

## 2024-2025 algorithm updates summary

| Update | Details |
|--------|---------|
| Original content priority (2024) | Watermarked reposts from other platforms (Instagram Reels, YouTube Shorts) receive reduced FYP distribution |
| Search/SEO weighting (2024-2025) | Keyword signals in captions, auto-captions (voice-to-text), and on-screen text now materially affect distribution |
| Follower-first testing (2025-2026) | New videos shown to existing followers before cold FYP audiences |
| Higher completion threshold (2025-2026) | ~70% completion rate needed for progression vs ~50% in earlier years |
| Shares > saves > comments > likes (2025) | Engagement hierarchy clarified; saves now outweigh likes |
| Comment quality over quantity (2025) | Substantive comments weighted higher than simple reactions |
| Hashtag cap (August 2025) | 5 hashtag limit enforced — additional tags ignored |
| Scaled diamond rewards (2025) | LIVE gift payout rate now mission-dependent (20%–53% of base value) |
