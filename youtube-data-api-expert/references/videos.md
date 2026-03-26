# Videos Resource — YouTube Data API v3

Base URL: `https://www.googleapis.com/youtube/v3/videos`

## Methods Summary

| Method | HTTP | Quota Cost | Required Scope |
|--------|------|-----------|----------------|
| list | GET | 1 unit | API key or youtube.readonly |
| insert | POST (multipart/resumable) | 100 units | youtube.upload or youtube |
| update | PUT | 50 units | youtube or youtube.force-ssl |
| delete | DELETE | 50 units | youtube or youtube.force-ssl |
| rate | POST | 50 units | youtube or youtube.force-ssl |
| getRating | GET | 1 unit | youtube.readonly |
| reportAbuse | POST | 50 units | youtube or youtube.force-ssl |

---

## videos.list

Retrieves video resources matching request parameters.

**Endpoint:** `GET https://www.googleapis.com/youtube/v3/videos`

### Required Parameters

- **part** (string, required): Comma-separated list of parts to include in response.

### Filters — specify exactly one

| Filter | Type | Description |
|--------|------|-------------|
| `id` | string | Comma-separated video IDs (up to 50) |
| `chart` | string | `mostPopular` — trending videos in a region/category |
| `myRating` | string | `like` or `dislike` — videos rated by authenticated user |

### Optional Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `maxResults` | integer | 1–50, default 5 (only for `chart` or `myRating` filters) |
| `pageToken` | string | Token for result page navigation |
| `regionCode` | string | ISO 3166-1 alpha-2 country code (for `chart`) |
| `videoCategoryId` | string | Category filter for `chart` (default: 0 = all) |
| `hl` | string | Language code for localized metadata |
| `maxHeight` | integer | Embedded player max height (72–8192 px) |
| `maxWidth` | integer | Embedded player max width (72–8192 px) |
| `onBehalfOfContentOwner` | string | YouTube partner parameter |

### Part Values and Content

| Part | Contains | Notes |
|------|----------|-------|
| `id` | Video ID only | Cheapest; always included |
| `snippet` | Title, description, channelId, publishedAt, thumbnails, tags, categoryId, defaultLanguage | Core metadata |
| `contentDetails` | Duration (ISO 8601), dimension (2d/3d), definition (hd/sd), caption, licensedContent, regionRestriction, contentRating | Video specs |
| `statistics` | viewCount, likeCount, commentCount | dislikeCount restricted to video owner |
| `status` | uploadStatus, privacyStatus, publishAt, license, embeddable, publicStatsViewable, madeForKids | Privacy/publish settings |
| `player` | Embeddable iframe HTML | Use with maxHeight/maxWidth |
| `topicDetails` | topicIds, relevantTopicIds, topicCategories | Freebase topic IDs |
| `recordingDetails` | recordingDate, location | Where/when recorded |
| `fileDetails` | fileName, fileSize, fileType, container, videoStreams, audioStreams | Requires owner auth |
| `processingDetails` | processingStatus, processingProgress, thumbnailsAvailability | Upload processing state |
| `suggestions` | processingErrors, processingWarnings, processingHints, tagSuggestions, editorSuggestions | Requires owner auth |
| `liveStreamingDetails` | actualStartTime, actualEndTime, scheduledStartTime, concurrentViewers | Live/archived streams |
| `localizations` | Localized title/description per language code | i18n support |
| `paidProductPlacementDetails` | hasPaidProductPlacement | Sponsorship disclosure |

### Privacy Status Values
`public` | `private` | `unlisted`

### Example: Fetch video details
```python
response = youtube.videos().list(
    part='snippet,statistics,contentDetails',
    id='dQw4w9WgXcQ'
).execute()

video = response['items'][0]
title = video['snippet']['title']
views = video['statistics']['viewCount']
duration = video['contentDetails']['duration']  # e.g., "PT3M33S"
```

### Example: Get trending videos
```python
response = youtube.videos().list(
    part='snippet,statistics',
    chart='mostPopular',
    regionCode='US',
    maxResults=50
).execute()
```

### Example: Get my liked videos
```python
response = youtube.videos().list(
    part='snippet',
    myRating='like',
    maxResults=50
).execute()
```

---

## videos.insert (Upload)

**Quota cost: 100 units**

Two upload methods:
- **Multipart upload** (`uploadType=multipart`): metadata + video in one request; suitable for small files < 5 MB
- **Resumable upload** (`uploadType=resumable`): recommended for all video files; handles interruptions

### Resumable Upload Protocol (Recommended)

#### Step 1: Initiate Upload Session

```
POST https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json; charset=UTF-8
X-Upload-Content-Length: FILE_SIZE_IN_BYTES
X-Upload-Content-Type: video/mp4

{
  "snippet": {
    "title": "My Video Title",
    "description": "Video description",
    "tags": ["tag1", "tag2"],
    "categoryId": "22"
  },
  "status": {
    "privacyStatus": "private",
    "embeddable": true,
    "license": "youtube"
  }
}
```

Response: `200 OK` with `Location: https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&upload_id=SESSION_ID`

#### Step 2: Upload Video Data

```
PUT {location_uri_from_step_1}
Authorization: Bearer ACCESS_TOKEN
Content-Length: FILE_SIZE
Content-Type: video/mp4

[binary video data]
```

Response: `201 Created` with full video resource on success.

#### Step 3: Handle Interruptions

On 5xx error or network failure:
```
PUT {session_uri}
Authorization: Bearer ACCESS_TOKEN
Content-Length: 0
Content-Range: bytes */TOTAL_FILE_SIZE
```

Response: `308 Resume Incomplete` with `Range: bytes=0-LAST_BYTE_RECEIVED`
- Resume by sending remaining bytes: `Content-Range: bytes NEXT_BYTE-LAST_BYTE/TOTAL`

On `404 Not Found`: session expired, restart from Step 1.

### Python Upload with google-api-python-client

```python
from googleapiclient.http import MediaFileUpload

def upload_video(youtube, file_path, title, description, category_id='22',
                 privacy='private', tags=None):
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags or [],
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': privacy,
            'selfDeclaredMadeForKids': False
        }
    }

    media = MediaFileUpload(
        file_path,
        mimetype='video/*',
        resumable=True,
        chunksize=1024 * 1024 * 10  # 10 MB chunks
    )

    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media,
        notifySubscribers=True
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f'Upload progress: {int(status.progress() * 100)}%')

    return response['id']  # Returns video ID
```

### Required Parameters

- **part** (string): Must include parts matching the request body properties being set. Minimum: `snippet,status`

### Optional Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `notifySubscribers` | boolean | Send upload notification to subscribers (default: True) |
| `onBehalfOfContentOwner` | string | YouTube partner parameter |
| `onBehalfOfContentOwnerChannel` | string | YouTube partner parameter |

### Upload Constraints
- Maximum file size: **256 GB**
- Accepted MIME types: `video/*`, `application/octet-stream`
- Unverified projects: uploaded videos default to `private` status

### Video Category IDs (Common)
| ID | Category |
|----|----------|
| 1 | Film & Animation |
| 2 | Autos & Vehicles |
| 10 | Music |
| 15 | Pets & Animals |
| 17 | Sports |
| 20 | Gaming |
| 22 | People & Blogs |
| 23 | Comedy |
| 24 | Entertainment |
| 25 | News & Politics |
| 26 | Howto & Style |
| 27 | Education |
| 28 | Science & Technology |
| 29 | Nonprofits & Activism |

---

## videos.update

Modifies video metadata. Cannot change the video file itself.

```python
response = youtube.videos().update(
    part='snippet,status',
    body={
        'id': 'VIDEO_ID',
        'snippet': {
            'title': 'Updated Title',
            'description': 'Updated description',
            'categoryId': '22'
        },
        'status': {
            'privacyStatus': 'public'
        }
    }
).execute()
```

**Note:** The `snippet` part requires `categoryId` to be included even if not changing it; omitting it causes an error.

---

## videos.delete

```python
youtube.videos().delete(id='VIDEO_ID').execute()
# Returns HTTP 204 No Content on success
```

---

## videos.rate

```python
youtube.videos().rate(
    id='VIDEO_ID',
    rating='like'  # 'like', 'dislike', or 'none'
).execute()
```

---

## videos.getRating

```python
response = youtube.videos().getRating(
    id='VIDEO_ID1,VIDEO_ID2'
).execute()
# response['items'] contains [{videoId, rating}, ...]
```

---

## Duration Format (ISO 8601)

`contentDetails.duration` uses ISO 8601 duration format:
- `PT1H2M3S` = 1 hour, 2 minutes, 3 seconds
- `PT3M33S` = 3 minutes, 33 seconds
- `P0D` = 0 seconds (live stream)

Parse in Python:
```python
import isodate
duration = isodate.parse_duration('PT3M33S')
total_seconds = duration.total_seconds()  # 213.0
```

---

## Processing Status Values

After upload, `processingDetails.processingStatus`:
- `uploading` — video is being uploaded
- `processing` — video is processing (transcoding)
- `succeeded` — processing complete, video available
- `failed` — processing failed
- `terminated` — processing terminated

Poll with videos.list(part='processingDetails') until `succeeded`.
