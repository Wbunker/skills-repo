# YouTube Studio Analytics Reference

## Table of Contents
1. [Accessing Analytics](#accessing-analytics)
2. [Overview tab](#overview-tab)
3. [Reach tab](#reach-tab)
4. [Engagement tab](#engagement-tab)
5. [Audience tab](#audience-tab)
6. [Revenue tab (YPP only)](#revenue-tab-ypp-only)
7. [Research tab](#research-tab)
8. [Video-level vs channel-level analytics](#video-level-vs-channel-level-analytics)
9. [Key metric benchmarks](#key-metric-benchmarks)

---

## Accessing Analytics

- **Channel analytics**: studio.youtube.com → Analytics
- **Video analytics**: studio.youtube.com → Content → select video → Analytics
- **Date range**: Adjustable; default last 28 days; can compare periods
- **Advanced mode**: Click "Advanced mode" for custom reports, CSV export, and comparison charts

---

## Overview tab

Channel health snapshot. Shows totals for the selected period:

| Metric | What it tells you |
|--------|------------------|
| Views | Total video plays (≥30 seconds for ads; no minimum for organic) |
| Watch time (hours) | Total cumulative minutes watched, expressed in hours |
| Subscribers (net) | Gained minus lost subscribers in the period |
| Estimated revenue | Total earnings (YPP only) |
| Real-time views | Live counter of views in last 48 hours (updates continuously) |
| Top videos | Ranked by views in the period |

Use the Overview tab to spot anomalies — a sudden views spike without a proportional watch time increase may indicate click-bait or a misleading thumbnail.

---

## Reach tab

Discovery funnel — how viewers find your content.

### Core metrics

| Metric | Definition |
|--------|-----------|
| **Impressions** | Times thumbnails were shown on YouTube surfaces (home, search, suggested, notifications) |
| **Impressions CTR** | % of impressions that became views — the primary thumbnail+title effectiveness signal |
| **Views** | Actual views that resulted from those impressions |
| **Unique viewers** | Estimated distinct individuals (not sessions or plays) |

### CTR benchmarks
- **Below 2%**: Algorithm reduces distribution — thumbnail or title needs rework
- **2–4%**: Average — room for improvement
- **4–6%**: Healthy range for most channels
- **Above 10%**: Exceptional topic-audience fit or very niche audience

**CTR alone is not the goal.** High CTR + low watch time = misleading thumbnail. YouTube tests both in combination. A click that immediately bounces is worse than no click.

### Traffic sources

| Source | What it means |
|--------|--------------|
| YouTube Search | Viewer searched a term and clicked your video |
| Browse features | Home page and trending tab recommendations |
| Suggested videos | Appeared alongside or after another video |
| External | Traffic from outside YouTube (links, embeds) |
| Playlists | Played from within a playlist |
| Channel pages | Viewer visited your channel directly |
| Notifications | Subscriber clicked a notification |
| Shorts feed | Appeared in the Shorts vertical feed |
| Direct / Unknown | Direct URL access or unclassified traffic |

Traffic source mix shapes strategy:
- High Search → keyword-optimized content is working; improve CTR
- High Browse → algorithm is recommending you; watch time is strong
- High External → build/leverage external audiences; diversification risk if platform changes

---

## Engagement tab

Watch quality — how deeply viewers engage.

| Metric | Definition |
|--------|-----------|
| **Watch time** | Total cumulative hours in the period — primary ranking signal |
| **Average view duration (AVD)** | Mean minutes watched per play |
| **Average percentage viewed (APV)** | % of video length watched on average |
| **Audience retention curve** | Frame-by-frame drop-off visualization per video |
| **Likes** | Thumbs-up count |
| **Comments** | Total comments |
| **Shares** | Shares via the Share button |
| **Saves** | Added to Watch Later or playlists |
| **End screen CTR** | % of end screen impressions that were clicked |
| **Card CTR** | % of card impressions that were clicked |
| **Subscriber growth from video** | Net subscribers gained from this specific video |

### Reading the audience retention curve
- The curve always starts at 100% and trends down
- **Sharp drop at 0:00–0:30**: Intro is not hooking viewers — too slow, misleading thumbnail
- **Gradual steady decline**: Normal; no major problems
- **Sharp drop at a specific point**: That moment is losing viewers — cut or rework it
- **Flat sections or bumps**: Viewers are rewatching — strong content at that point
- **Re-watch above 100%**: Indicates replay value (tutorials, recipes)

### APV benchmarks
- Short videos (<5 min): Target ≥70% APV
- Mid-length (5–15 min): Target ≥50–60% APV
- Long-form (>20 min): 40–50% APV is acceptable
- These are guides, not hard rules — compare against your own channel averages

---

## Audience tab

Who is watching and when.

| Metric | Definition |
|--------|-----------|
| **Returning viewers** | Watched at least one of your videos in the last 28 days |
| **New viewers** | First time watching your content |
| **Watch time from subscribers** | % of watch time from people subscribed to you |
| **Unique viewers** | Estimated distinct individuals |

### Demographics

| Dimension | Breakdowns available |
|-----------|---------------------|
| Age | 13–17, 18–24, 25–34, 35–44, 45–54, 55–64, 65+ |
| Gender | Female, Male, User-specified |
| Geography | Country and city level |
| Device type | Mobile, Desktop, Tablet, TV, Game console |

**Device distribution context (2025 averages):**
- Mobile: ~63% of watch time
- Desktop: ~18%
- TV: ~12%
- Tablet: ~5%
- Design thumbnails for mobile-first (small screens)

### When your viewers are on YouTube
Heatmap showing relative viewer activity by hour and day of week.
- Use this to schedule uploads and community posts
- Post 2–4 hours before peak activity to allow indexing time
- Higher activity times = more competition from other uploads too

### Subscriber vs non-subscriber watch time
- Healthy channels: 40–60% of watch time from non-subscribers (discovery working)
- If >80% from subscribers: channel is not reaching new audiences; SEO or thumbnails may need work
- If <20% from subscribers: retention and loyalty may be weak

---

## Revenue tab (YPP only)

Available only to YouTube Partner Program members.

| Metric | Definition |
|--------|-----------|
| **Estimated revenue** | Total earnings from all monetization streams |
| **RPM (Revenue Per Mille)** | Your actual earnings per 1,000 views (after YouTube's 45% cut) |
| **CPM (Cost Per Mille)** | Advertiser cost per 1,000 ad impressions (before YouTube's cut) |
| **Monetized playbacks** | Views that generated at least one ad impression |
| **Ad impressions** | Total ads shown across your videos |

### RPM vs CPM
- **CPM** = what advertisers pay. Varies widely by niche, season, geography, and ad type.
- **RPM** = what you actually earn. RPM ≈ CPM × 55% × (monetized playback rate).
- 2025 average global CPM: ~$3.50; average RPM: ~$1.50–$4 (varies widely by niche)
- High-CPM niches: Finance, Legal, B2B SaaS, Insurance, Real Estate, Health
- Low-CPM niches: Entertainment, Gaming, Music (general audience)

### Revenue streams breakdown
| Stream | Where it shows |
|--------|---------------|
| Ad revenue | Video views with ads (skippable, non-skippable, bumper, overlay, display) |
| YouTube Premium revenue | Share of Premium subscribers' fees based on their watch time on your channel |
| Channel memberships | Monthly recurring fan payments |
| Super Chat / Super Stickers | Fan payments during live streams |
| Super Thanks | One-time tips on regular videos |
| YouTube Shopping | Product affiliate/own product revenue |

### Seasonality patterns
- CPM peaks: Q4 (Oct–Dec) — holiday advertising spend is highest
- CPM troughs: Q1 (Jan) — advertiser budgets reset and are slow to ramp
- Plan for lower Q1 revenue even with the same views

---

## Research tab

Content opportunity discovery tool.

| Feature | What it shows |
|---------|--------------|
| Audience search queries | What your current viewers search on YouTube |
| Trending topics | Topics gaining search velocity in your niche |
| Content gaps | High search demand + few existing videos = opportunity |
| Related terms | Alternative phrasings for the same topic |

**High-value opportunity signal:** High search volume + low competition + topic fits your channel = strong video idea.

The Research tab is based on your channel's existing audience, making it more relevant than general YouTube search trends.

---

## Video-level vs channel-level analytics

Most metrics are available both at the channel level and per-video level.

**Channel-level**: Aggregate view of all content — useful for trend identification and overall health.

**Video-level**: Per-video breakdown — use to understand why individual videos overperform or underperform relative to channel average.

**Comparison workflow:**
1. Identify your top 5 videos by watch time (not just views)
2. Look at their retention curves for patterns (hook length, pacing, chapter structure)
3. Apply those patterns to future videos
4. Identify lowest-performing videos — check if they are hurting channel recommendations

---

## Key metric benchmarks

These are general guides. Compare against your own channel averages first.

| Metric | Benchmark |
|--------|-----------|
| Impressions CTR | 4–6% healthy; >10% exceptional |
| APV (short video <5 min) | ≥70% |
| APV (mid-length 5–15 min) | ≥50–60% |
| APV (long-form >20 min) | 40–50% |
| Watch time from non-subscribers | 40–60% |
| Subscriber growth per 1,000 views | 0.5–2% (varies hugely by channel type) |
| Comment rate per view | 0.1–0.5% typical |
