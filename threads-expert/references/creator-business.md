# Creator and Business Use on Threads

## Account Types

Threads has three account modes:
- **Personal** — standard user account
- **Creator** — unlocks analytics and creator tools; linked to Instagram Professional account
- **Business** — same analytics access as Creator; linked to Instagram Business account

Switching to Creator or Business is done through your linked Instagram account's professional dashboard. Since September 2025, Threads can also be created and used without an Instagram account, though follower metrics and some features require Instagram linkage.

---

## Verification Badges

### Meta Verified (Paid)
- Blue checkmark via subscription: **$11.99–$14.99/month** (pricing varies by region and platform)
- Available to any user — no need to be a public figure
- Requires: government-issued ID verification; in some regions, a selfie video to confirm identity
- Identity must match the profile name and photo
- Verification appears within ~48 hours of approval
- **Benefits**: blue badge, proactive impersonation monitoring (Meta removes fake accounts), increased credibility with new audiences
- Available in US, UK, most of Europe, Australia, and parts of Latin America (as of 2025)
- Managed through Meta's subscription portal: `meta.com/meta-verified/`

### Traditional (Legacy) Free Verification
- Reserved for notable public figures, celebrities, major brands, and organizations
- Apply through the Instagram verification request flow (Threads inherits the badge)
- Not guaranteed; stricter requirements; Meta's discretion

### Key Note
- There is no separate verification application process on Threads — the blue badge on Threads mirrors your Instagram verification status
- If you are Meta Verified on Instagram, the badge appears on your Threads profile

---

## Analytics: In-App (Threads Insights)

### Access Requirements
- Available to all users with **100+ followers** (not limited to Creator/Business accounts)
- Mobile (iOS/Android): available to all users since January 2025
- Desktop (threads.net): available since August 2024

### Metrics Available In-App
| Metric | Notes |
|---|---|
| Total views | Over the past 7, 30, or 90 days |
| Interactions | Likes, replies, reposts, quotes — aggregate |
| Follower growth | Gain/loss over time |
| Top posts by views | Identify best-performing content |
| Top posts by likes | Secondary ranking |
| Link clicks | Up to 5 bio links + post links (added May 2025) |
| Audience demographics | Age, gender, location (added July 2025) |
| Post view sources | Home feed, profile, search, activity tab, Instagram, Facebook (added July 2025) |

### What Is NOT Tracked Natively
- No impressions vs. reach breakdown (follower vs. non-follower)
- No profile visit count (available on Instagram, not Threads)
- No content-type breakdown (equivalent of Reels vs. Posts)
- No watch time or video replay data
- No "sends per reach" metric
- Engagement is calculated at the account level across all activity in the window, not per post for a specific date range — limits accurate weekly/monthly reporting on specific content

### Workarounds for Gaps
- Use UTM parameters on links to track referral traffic in Google Analytics
- Use third-party social media management tools (Sendible, Sprout Social, Hootsuite, Buffer)
- Manual tracking in spreadsheets for longitudinal performance
- Qualitative monitoring of replies and quote posts for sentiment

---

## Analytics: Via API

See `threads-api.md` for full Insights API reference. Summary of what's available programmatically:

**Post-level**: views, likes, replies, reposts, quotes, shares (some in development)
**User-level**: views, likes, replies, reposts, quotes, followers_count, follower_demographics, link clicks
**Date ranges**: Unix timestamp `since`/`until` (data reliable from June 1, 2024; no data before April 13, 2024)
**Breakdowns**: country, city, age, gender (one at a time; 100+ followers required)

---

## Scheduling Posts

### Native Scheduling
- As of early 2026, **no native "Schedule" button** exists in the Threads app or website
- Scheduling was in testing as of December 2024 but had not launched as a full feature to all users as of the knowledge cutoff

### Via API (Third-Party Tools)
- The Threads API itself does not have a built-in `publish_time` scheduling parameter — publishing is immediate upon calling `threads_publish`
- **Scheduling is achieved by third-party tools** that hold the post and call the API at the desired time
- Tools that support Threads scheduling (as of 2025–2026): Buffer, Hootsuite, Sprout Social, Later, Sendible, SocialBee, PostEverywhere, Ayrshare, Postproxy

### Scheduling Limitations
- **Replies cannot be scheduled** in most tools (the API doesn't block it, but the multi-step auth makes it complex)
- **Thread sequences** (multi-post threads/chains) require scheduling each post a few minutes apart
- Posts scheduled via API are treated identically by the algorithm to manually posted content — no reach penalty

---

## Monetization

### No Direct Creator Payouts (as of 2026)
- Meta's cash bonus program for Threads posts **ended July 2025**
- There is no current creator revenue-share or direct payout program on Threads

### Indirect Monetization Channels
- **Brand deals and sponsored posts** — no built-in marketplace on Threads yet, but the Instagram Creator Marketplace is expanding to include Threads creators (high-performing creators get discoverable badges for brands)
- **Affiliate links** — post links in bio (up to 5) or include them in posts; track with UTM parameters
- **Traffic funnel** — drive followers to paid products (courses, newsletters, communities, Patreon, etc.)
- **Brand awareness** — Threads presence builds audience that converts on other platforms

### Ads on Threads (for Brands/Advertisers)
- Ads launched in limited testing in January 2025 (US + Japan)
- Expanded globally to all eligible advertisers: May 2025
- Global rollout to all users: January 2026
- Managed through Meta Ads Manager (not a Threads-specific ads tool)
- Ad formats: standard Meta ad formats placed in Threads feeds
- Advantage+ catalog ads added October 2025
- App ads for Threads added February 2026
- Reply moderation for Threads ads added March 2026
- **Threads-specific ad metrics** (quote posts, thread replies) are NOT yet available in Ads Manager — you see standard metrics: impressions, clicks, conversions, cost per result
- Not all Instagram demographic breakdowns are available for Threads ads

---

## Business Account Features

- Access to Threads Insights (same as all users with 100+ followers, but Professional Dashboard on Instagram provides unified view)
- Managed through the **Instagram Professional Dashboard** — the primary hub for Creator/Business accounts spanning both platforms
- Creator Marketplace access (brand deal discovery) — expanding to Threads
- Account switching during post composition (useful for multi-brand management)
- Reply moderation tools: hide, delete, and manage replies; approval workflow for pending replies (added February 2026)

---

## Content Strategy Notes for Creators

- **Topic tags outperform no-tag posts** — always tag with a relevant topic
- **Text-first content** performs well; Threads rewards conversational posts over polished brand content
- **Native content outperforms cross-posted content** from Instagram — the algorithm deprioritizes content that appears to be a cross-post
- The **For You feed** gives significant discovery reach to non-followers; new accounts can grow quickly
- Meta is rebalancing the algorithm (2025–2026) to weight followed accounts more heavily — connected reach up, unconnected reach slightly down
- "Rage bait" and low-quality engagement-bait content is actively deprioritized (October 2024 policy update)
- **Spoiler tags** are useful for creators sharing sensitive or plot-sensitive content
- **Ghost posts** (24-hour auto-archive) can be used for time-sensitive content or testing messages
- Links in posts are supported but **not clickable inline** — direct followers to a bio link or instruct them to click the link in comments
