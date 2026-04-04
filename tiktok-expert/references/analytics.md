# TikTok Analytics (TikTok Studio)

## Accessing analytics

- **Web**: studio.tiktok.com → Analytics
- **Mobile**: Profile → Menu (☰) → Creator tools → Analytics
- Requires a Pro account (Creator or Business) — free to upgrade in settings
- Data available up to 365 days in arrears (with variable lookback windows per tab)

---

## Analytics tabs overview

### Overview tab

Provides account-level health snapshot for a selected date range (7, 28, or 60 days, or custom).

| Metric | Description |
|--------|-------------|
| Video views | Total views across all videos in the period |
| Profile views | Number of times your profile page was visited |
| Likes | Total likes received on all content |
| Comments | Total comments received |
| Shares | Total shares of your content |
| Followers net change | New followers minus unfollows |
| Live views | Total views from LIVE sessions (if applicable) |

### Content tab

Per-video performance breakdown. Shows all videos posted in the selected period.

| Metric | Description |
|--------|-------------|
| Total plays / video views | Times the video was watched (any duration) |
| Total watch time | Sum of all viewing time (hours/minutes) |
| Average watch time | Total watch time ÷ total plays |
| Full video watches | Count of viewers who watched to the end |
| Completion rate | Full video watches ÷ total plays × 100% |
| Likes | Reactions on this video |
| Comments | Comments on this video |
| Shares | Shares of this video |
| Saves | Times viewers saved this video |
| Profile visits from video | Profile views attributable to this video |
| New followers from video | Follows attributed to this video |
| Reached audience | Unique accounts that saw the video |
| Traffic source breakdown | Where views came from (see below) |

Clicking into any video shows a full analytics panel with all of the above metrics and the traffic source breakdown.

### Follower tab

Audience intelligence about your current followers.

| Metric | Description |
|--------|-------------|
| Total followers | Current follower count |
| Net followers | Followers gained minus lost in the period |
| Gender breakdown | % male / female / other |
| Top territories | Top countries and regions of followers |
| Follower activity | Hours and days when followers are most active on TikTok (critical for post timing) |
| Videos your followers watched | Popular videos among your audience (including others' content) |
| Sounds your followers listened to | Trending sounds popular with your audience |

### LIVE tab (if applicable)

Separate analytics for LIVE sessions. See the `live.md` reference for LIVE-specific metrics.

---

## Traffic source types

Understanding where views come from is critical for strategy. Available in the Content tab per-video.

| Source | Description |
|--------|-------------|
| For You | FYP algorithm recommendation — cold audience discovery |
| Following | Shown to people who follow you in their Following feed |
| Search | User found the video via TikTok search |
| Profile | Viewer visited your profile and tapped the video |
| Sound | Viewer was browsing a sound page and found your video |
| Hashtag | Viewer tapped a hashtag and found your video |
| Following feed | Related to Following (sometimes reported separately) |
| Personal Profile | Shares to personal pages / direct links |
| Other | Shares via DM, external links, etc. |

**Interpretation guide**:
- High "For You" % = algorithmic reach; algorithm is distributing broadly
- High "Search" % = strong SEO/keyword optimization; content matches search intent
- High "Following" % = engaged existing audience; low cold reach
- High "Sound" % = trending sound association is driving discovery

---

## Key performance metrics definitions

### Completion rate
`full_video_watches / total_plays × 100`

The single most algorithm-critical metric. Targets:
- Under 30 seconds: aim for 80%+
- 30–60 seconds: aim for 60%+
- 1–3 minutes: aim for 40%+
- 3+ minutes: aim for 25%+

### Average watch time
`total_watch_time / total_plays`

Tells you how many seconds viewers stayed on average. Compare against video length to understand where drop-off is occurring.

### Engagement rate
`(likes + comments + shares + saves) / views × 100`

Typical TikTok engagement rates: 3–9% is average; 10%+ is strong.

### Profile visit rate
`profile_visits_from_video / total_plays × 100`

Indicates how compelling the video is as a channel driver.

### Follower conversion rate
`new_followers_from_video / total_plays × 100`

Measures how effectively a video converts viewers into followers.

---

## Analytics data windows and limitations

- Content analytics: available from day of post
- Follower analytics: 7 / 28 / 60 day windows
- LIVE analytics: per-session breakdown
- Data is approximate (not fully precise in real-time)
- Historical data beyond 365 days is not accessible natively — export to CSV for archiving
- No A/B testing tool built into TikTok Studio natively

---

## Exporting analytics data

- **Web**: Analytics → Download data (CSV export)
- Exports include: video ID, post date, plays, likes, comments, shares, reach, average watch time
- Third-party tools (Sprout Social, Iconosquare, Social Insider) provide more granular and historical analytics with competitive benchmarking
