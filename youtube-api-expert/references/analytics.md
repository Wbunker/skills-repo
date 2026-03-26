# YouTube Analytics API

## Overview

The YouTube Analytics API provides detailed performance data beyond what's available in the Data API's `statistics` part.

| Data Source | What You Get |
|-------------|-------------|
| YouTube Data API (`statistics` part) | viewCount, likeCount, commentCount, subscriberCount — public totals |
| YouTube Analytics API | Watch time, traffic sources, demographics, revenue, retention — detailed breakdowns |
| YouTube Reporting API | Bulk downloads of historical reports for large datasets |

**Base URL**: `https://youtubeanalytics.googleapis.com/v2/reports`

**Required scopes**:
- `https://www.googleapis.com/auth/yt-analytics.readonly` — standard analytics
- `https://www.googleapis.com/auth/yt-analytics-monetary.readonly` — revenue data

---

## Setup

```python
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly"
]

# Use same OAuth flow as Data API (see auth.md)
# Build both clients if you need both APIs
youtube = build("youtube", "v3", credentials=creds)
youtube_analytics = build("youtubeAnalytics", "v2", credentials=creds)
```

---

## Reports.query — Core Method

```python
response = youtube_analytics.reports().query(
    ids="channel==MINE",           # or "channel==CHANNEL_ID"
    startDate="2024-01-01",        # YYYY-MM-DD
    endDate="2024-12-31",
    metrics="views,estimatedMinutesWatched,likes,comments,shares",
    dimensions="day",              # break down by day
    sort="-views"                  # sort descending by views
).execute()

# Response structure
headers = [col["name"] for col in response["columnHeaders"]]
for row in response["rows"]:
    record = dict(zip(headers, row))
    print(record)
```

---

## Metrics Reference

### Engagement Metrics

| Metric | Description |
|--------|-------------|
| `views` | Number of video views |
| `estimatedMinutesWatched` | Total minutes watched |
| `averageViewDuration` | Average seconds per view |
| `averageViewPercentage` | Average % of video watched |
| `likes` | Likes |
| `dislikes` | Dislikes (limited availability) |
| `comments` | Comment count |
| `shares` | Number of shares |
| `subscribersGained` | New subscribers |
| `subscribersLost` | Subscribers lost |
| `videosAddedToPlaylists` | Times added to playlists |
| `videosRemovedFromPlaylists` | Times removed from playlists |

### Revenue Metrics (requires monetary scope)

| Metric | Description |
|--------|-------------|
| `estimatedRevenue` | Total estimated revenue (USD) |
| `estimatedAdRevenue` | Ad revenue |
| `grossRevenue` | Gross revenue |
| `cpm` | Cost per 1000 impressions |
| `monetizedPlaybacks` | Playbacks with at least one ad |
| `adImpressions` | Number of ad impressions |

### Card & Annotation Metrics

| Metric | Description |
|--------|-------------|
| `cardImpressions` | Card impressions |
| `cardClicks` | Card clicks |
| `cardClickRate` | Card click-through rate |
| `annotationClickThroughRate` | Annotation CTR |

---

## Dimensions Reference

### Time Dimensions

| Dimension | Description |
|-----------|-------------|
| `day` | Per-day breakdown (YYYY-MM-DD) |
| `week` | Per-week (YYYY-MM-DD of week start) |
| `month` | Per-month (YYYY-MM) |

### Content Dimensions

| Dimension | Description |
|-----------|-------------|
| `video` | Per-video breakdown |
| `playlist` | Per-playlist |
| `group` | Per analytics group |

### Audience Dimensions

| Dimension | Description |
|-----------|-------------|
| `ageGroup` | age13-17, age18-24, age25-34, age35-44, age45-54, age55-64, age65- |
| `gender` | male, female, userSpecified |
| `country` | ISO 3166-1 alpha-2 country code |
| `province` | US states (US-XX format) |
| `subscribedStatus` | SUBSCRIBED or UNSUBSCRIBED |
| `youtubeProduct` | CORE, GAMING, KIDS, UNKNOWN |

### Traffic Source Dimensions

| Dimension | Description |
|-----------|-------------|
| `insightTrafficSourceType` | Traffic source type |
| `insightTrafficSourceDetail` | Specific source within type |

Traffic source types: `YT_SEARCH`, `EXT_URL`, `PLAYLIST`, `SUGGESTED_VIDEOS`, `SUBSCRIBER`, `NO_LINK_EMBEDDED`, `YT_CHANNEL`, `NOTIFICATION`, `END_SCREEN`, `CARD`, `VIDEO_REMIXES`, `SHORTS`

### Playback Location Dimensions

| Dimension | Description |
|-----------|-------------|
| `insightPlaybackLocationType` | Where video was played |
| `insightPlaybackLocationDetail` | Specific location detail |

Playback location types: `WATCH`, `YT_OTHER_PAGE`, `EXTERNAL`, `MOBILE`, `SEARCH`

### Device Dimensions

| Dimension | Description |
|-----------|-------------|
| `deviceType` | DESKTOP, MOBILE, TABLET, GAME_CONSOLE, TV, UNKNOWN_PLATFORM |
| `operatingSystem` | ANDROID, IOS, WINDOWS, LINUX, MACINTOSH, etc. |

---

## Common Report Examples

### Daily views for your channel (last 30 days)

```python
from datetime import date, timedelta

end = date.today().isoformat()
start = (date.today() - timedelta(days=30)).isoformat()

response = youtube_analytics.reports().query(
    ids="channel==MINE",
    startDate=start,
    endDate=end,
    metrics="views,estimatedMinutesWatched,subscribersGained",
    dimensions="day",
    sort="day"
).execute()
```

### Top 10 videos by watch time

```python
response = youtube_analytics.reports().query(
    ids="channel==MINE",
    startDate="2024-01-01",
    endDate="2024-12-31",
    metrics="views,estimatedMinutesWatched,averageViewDuration",
    dimensions="video",
    sort="-estimatedMinutesWatched",
    maxResults=10
).execute()
```

### Traffic sources breakdown

```python
response = youtube_analytics.reports().query(
    ids="channel==MINE",
    startDate="2024-01-01",
    endDate="2024-12-31",
    metrics="views,estimatedMinutesWatched",
    dimensions="insightTrafficSourceType",
    sort="-views"
).execute()
```

### Demographics (age + gender)

```python
response = youtube_analytics.reports().query(
    ids="channel==MINE",
    startDate="2024-01-01",
    endDate="2024-12-31",
    metrics="viewerPercentage",
    dimensions="ageGroup,gender"
).execute()
```

### Stats for a specific video

```python
response = youtube_analytics.reports().query(
    ids="channel==MINE",
    startDate="2024-01-01",
    endDate="2024-12-31",
    metrics="views,estimatedMinutesWatched,likes,comments",
    dimensions="day",
    filters="video==VIDEO_ID",
    sort="day"
).execute()
```

### Geographic breakdown

```python
response = youtube_analytics.reports().query(
    ids="channel==MINE",
    startDate="2024-01-01",
    endDate="2024-12-31",
    metrics="views,estimatedMinutesWatched",
    dimensions="country",
    sort="-views",
    maxResults=25
).execute()
```

---

## Filters

Use the `filters` parameter to scope results:

```python
# Single video
filters="video==VIDEO_ID"

# Multiple videos
filters="video==VIDEO_ID1,VIDEO_ID2"

# Specific country
filters="country==US"

# Combined filters (semicolon = AND)
filters="video==VIDEO_ID;country==US"

# Subscribers only
filters="subscribedStatus==SUBSCRIBED"
```

---

## Audience Retention (Watch Time Reports)

Audience retention is available via a specialized endpoint:

```python
response = youtube_analytics.reports().query(
    ids="channel==MINE",
    startDate="2024-01-01",
    endDate="2024-12-31",
    metrics="audienceWatchRatio,relativeRetentionPerformance",
    dimensions="elapsedVideoTimeRatio",
    filters="video==VIDEO_ID"
).execute()
# Returns data points for percentage of video elapsed vs. retention rate
```

---

## Response Structure

```python
response = youtube_analytics.reports().query(...).execute()

# Headers
headers = [col["name"] for col in response["columnHeaders"]]
# e.g., ["day", "views", "estimatedMinutesWatched"]

# Data rows
for row in response.get("rows", []):
    record = dict(zip(headers, row))
    # {"day": "2024-01-15", "views": 1234, "estimatedMinutesWatched": 5678}

# Total rows available (for pagination)
total = response.get("rowCount", 0)
```

---

## YouTube Reporting API (Bulk Downloads)

For large-scale historical data, use the Reporting API instead:

```python
reporting = build("youtubereporting", "v1", credentials=creds)

# List available report types
report_types = reporting.reportTypes().list(includeSystemManaged=True).execute()

# Create a reporting job
job = reporting.jobs().create(
    body={
        "name": "Channel basic stats",
        "reportTypeId": "channel_basic_a2"  # channel basic activity report
    }
).execute()

# List generated reports (available after ~24 hours)
reports = reporting.jobs().reports().list(jobId=job["id"]).execute()

# Download a report
import urllib.request
report_url = reports["reports"][0]["downloadUrl"]
# Use authenticated HTTP to download (not plain urllib)
```
