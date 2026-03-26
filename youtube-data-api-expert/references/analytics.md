# YouTube Analytics API vs Data API — YouTube Data API v3

---

## Two Separate APIs

YouTube provides two APIs for analytics data. They have different purposes, endpoints, authentication requirements, and use cases.

| Aspect | YouTube Data API v3 | YouTube Analytics API v2 |
|--------|--------------------|-----------------------------|
| Purpose | CRUD operations on YouTube content | Query analytics/performance metrics |
| Base URL | `googleapis.com/youtube/v3/` | `youtubeanalytics.googleapis.com/v2/` |
| Auth | API key or OAuth 2.0 | OAuth 2.0 required (always) |
| Data | Metadata, content, interaction | Views, watch time, revenue, demographics |
| Latency | Real-time | 24–72 hour delay on data |
| Python lib | `googleapiclient` (youtube v3) | `googleapiclient` (youtubeAnalytics v2) |
| Quota | YouTube Data API quota | Separate YouTube Analytics API quota |

---

## YouTube Analytics API v2

### Install and Authenticate

```python
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Requires youtube.readonly or yt-analytics.readonly scope
SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/yt-analytics.readonly'
]

# After OAuth flow (see auth.md):
analytics = build('youtubeAnalytics', 'v2', credentials=creds)
```

### Required Scopes

| Scope | Access |
|-------|--------|
| `yt-analytics.readonly` | View YouTube Analytics reports |
| `yt-analytics-monetary.readonly` | View monetary analytics (revenue) |
| `youtube.readonly` | Can also be used for basic analytics access |

---

## reports.query — The Core Method

**Endpoint:** `GET https://youtubeanalytics.googleapis.com/v2/reports`

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `ids` | string | `channel==MINE` for own channel, `channel==CHANNEL_ID`, or `contentOwner==OWNER_ID` |
| `startDate` | string | Start date: `YYYY-MM-DD` |
| `endDate` | string | End date: `YYYY-MM-DD` |
| `metrics` | string | Comma-separated metrics (see below) |

### Optional Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dimensions` | string | Comma-separated grouping dimensions |
| `filters` | string | Filter expression, e.g., `video==VIDEO_ID` |
| `sort` | string | Comma-separated metrics to sort by; prefix with `-` for descending |
| `maxResults` | integer | Maximum rows to return |
| `startIndex` | integer | 1-based start row for pagination |
| `currency` | string | ISO 4217 currency code for revenue metrics |

### Basic Example

```python
response = analytics.reports().query(
    ids='channel==MINE',
    startDate='2024-01-01',
    endDate='2024-12-31',
    metrics='views,estimatedMinutesWatched,likes,comments',
    dimensions='day',
    sort='day'
).execute()

# response['columnHeaders'] contains metric names
# response['rows'] contains data as list of lists
headers = [h['name'] for h in response['columnHeaders']]
for row in response.get('rows', []):
    data = dict(zip(headers, row))
    print(data)  # {'day': '2024-01-01', 'views': 1234, ...}
```

---

## Key Metrics

### Viewing Metrics

| Metric | Description |
|--------|-------------|
| `views` | Total video views |
| `estimatedMinutesWatched` | Total watch time in minutes |
| `averageViewDuration` | Average view duration in seconds |
| `averageViewPercentage` | Average % of video watched |
| `annotationClickThroughRate` | Annotation CTR |

### Engagement Metrics

| Metric | Description |
|--------|-------------|
| `likes` | Number of likes |
| `dislikes` | Number of dislikes |
| `comments` | Number of comments |
| `shares` | Number of shares |
| `subscribersGained` | Subscribers gained |
| `subscribersLost` | Subscribers lost |
| `videosAddedToPlaylists` | Times added to playlists |
| `videosRemovedFromPlaylists` | Times removed from playlists |

### Reach Metrics

| Metric | Description |
|--------|-------------|
| `impressions` | Thumbnail impressions |
| `impressionClickThroughRate` | % impressions that led to views |
| `cardClickRate` | Card click-through rate |
| `cardTeaserClickRate` | Card teaser CTR |

### Revenue Metrics (requires monetary scope)

| Metric | Description |
|--------|-------------|
| `estimatedRevenue` | Total estimated revenue |
| `estimatedAdRevenue` | Revenue from ads |
| `estimatedRedPartnerRevenue` | Revenue from YouTube Premium |
| `grossRevenue` | Total gross revenue |
| `adImpressions` | Number of ad impressions |
| `cpm` | Cost per thousand impressions |

---

## Key Dimensions

### Time Dimensions

| Dimension | Groups Data By |
|-----------|---------------|
| `day` | Calendar day (YYYY-MM-DD) |
| `month` | Calendar month (YYYY-MM) |
| `7DayTotals` | 7-day rolling periods |
| `30DayTotals` | 30-day rolling periods |

### Content Dimensions

| Dimension | Groups Data By |
|-----------|---------------|
| `video` | Individual video ID |
| `playlist` | Individual playlist ID |
| `channel` | Channel (for content owners) |
| `group` | YouTube Analytics group |

### Geographic Dimensions

| Dimension | Groups Data By |
|-----------|---------------|
| `country` | ISO 3166-1 alpha-2 country code |
| `province` | US state |
| `continent` | Continent code |
| `subContinent` | Sub-continent code |

### Traffic Source Dimensions

| Dimension | Groups Data By |
|-----------|---------------|
| `insightTrafficSourceType` | Traffic source category |
| `insightTrafficSourceDetail` | Specific traffic source detail |

Traffic source types include: `YT_SEARCH`, `EXT_URL`, `NO_LINK_EMBEDDED`, `SUBSCRIBER`, `YT_CHANNEL`, `YT_PLAYLIST_PAGE`, `RELATED_VIDEO`, `NOTIFICATION`, `YT_OTHER_PAGE`, `DIRECT`, `ADVERTISING`, `END_SCREEN`, `SHORTS`.

### Audience Dimensions

| Dimension | Groups Data By |
|-----------|---------------|
| `ageGroup` | Age group (age13-17, age18-24, age25-34, age35-44, age45-54, age55-64, age65-) |
| `gender` | `female`, `male`, `user_specified` |
| `deviceType` | `DESKTOP`, `MOBILE`, `TABLET`, `TV`, `GAME_CONSOLE` |
| `operatingSystem` | `ANDROID`, `IOS`, `WINDOWS`, `MACINTOSH`, `LINUX`, etc. |

---

## Common Analytics Queries

### Channel Summary (Last 28 Days)

```python
from datetime import datetime, timedelta

end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=28)).strftime('%Y-%m-%d')

response = analytics.reports().query(
    ids='channel==MINE',
    startDate=start_date,
    endDate=end_date,
    metrics='views,estimatedMinutesWatched,subscribersGained,subscribersLost',
    dimensions='day',
    sort='day'
).execute()
```

### Top 10 Videos by Views

```python
response = analytics.reports().query(
    ids='channel==MINE',
    startDate='2024-01-01',
    endDate='2024-12-31',
    metrics='views,estimatedMinutesWatched,likes',
    dimensions='video',
    sort='-views',
    maxResults=10
).execute()
```

### Views by Country

```python
response = analytics.reports().query(
    ids='channel==MINE',
    startDate='2024-01-01',
    endDate='2024-12-31',
    metrics='views,estimatedMinutesWatched',
    dimensions='country',
    sort='-views'
).execute()
```

### Audience Demographics

```python
response = analytics.reports().query(
    ids='channel==MINE',
    startDate='2024-01-01',
    endDate='2024-12-31',
    metrics='viewerPercentage',
    dimensions='ageGroup,gender',
    sort='gender,ageGroup'
).execute()
```

### Analytics for a Specific Video

```python
response = analytics.reports().query(
    ids='channel==MINE',
    startDate='2024-01-01',
    endDate='2024-12-31',
    metrics='views,estimatedMinutesWatched,likes,comments',
    dimensions='day',
    filters='video==VIDEO_ID',
    sort='day'
).execute()
```

### Traffic Sources

```python
response = analytics.reports().query(
    ids='channel==MINE',
    startDate='2024-01-01',
    endDate='2024-12-31',
    metrics='views,estimatedMinutesWatched',
    dimensions='insightTrafficSourceType',
    sort='-views'
).execute()
```

---

## YouTube Reporting API (Bulk Reports)

The YouTube **Reporting** API (separate from Analytics API) is for bulk data downloads — full dataset exports, not targeted queries.

| Feature | Analytics API | Reporting API |
|---------|--------------|---------------|
| Query type | Targeted (custom date/dimension/metric) | Bulk (full daily reports) |
| Filtering | Built-in | Must filter client-side |
| Sorting | Built-in | Must sort client-side |
| Latency | ~24h delay | ~24h delay |
| Report format | JSON rows | CSV files |
| Naming convention | camelCase (`estimatedMinutesWatched`) | snake_case (`estimated_minutes_watched`) |
| Use case | Dashboards, ad-hoc queries | Data warehousing, archiving |

---

## Data API vs Analytics API — What Each Can Answer

| Question | API | Method |
|----------|-----|--------|
| "What is this video's title?" | Data API | `videos.list(part='snippet')` |
| "How many views does this video have?" | Data API | `videos.list(part='statistics')` |
| "What was the view trend last month?" | Analytics API | `reports.query(dimensions='day', metrics='views')` |
| "Which countries watch my content?" | Analytics API | `reports.query(dimensions='country')` |
| "How old is my audience?" | Analytics API | `reports.query(dimensions='ageGroup,gender')` |
| "What traffic sources drive views?" | Analytics API | `reports.query(dimensions='insightTrafficSourceType')` |
| "How much revenue did I earn?" | Analytics API | `reports.query(metrics='estimatedRevenue')` |
| "Which video is trending now?" | Data API | `videos.list(chart='mostPopular')` |
| "Does this channel exist?" | Data API | `channels.list(forHandle='...')` |

---

## Response Parsing Pattern

```python
def parse_analytics_response(response):
    """Convert analytics API response to list of dicts."""
    if 'rows' not in response:
        return []

    headers = [h['name'] for h in response['columnHeaders']]
    return [dict(zip(headers, row)) for row in response['rows']]

# Usage:
response = analytics.reports().query(
    ids='channel==MINE',
    startDate='2024-01-01',
    endDate='2024-01-31',
    metrics='views,estimatedMinutesWatched',
    dimensions='day'
).execute()

data = parse_analytics_response(response)
# [{'day': '2024-01-01', 'views': 1234, 'estimatedMinutesWatched': 5678}, ...]
```
