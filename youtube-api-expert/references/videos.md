# YouTube Data API — Videos Resource

## Videos.list — Read Video Data

Retrieve metadata for one or more videos.

```python
# By video ID(s)
response = youtube.videos().list(
    part="snippet,contentDetails,statistics,status",
    id="VIDEO_ID1,VIDEO_ID2"  # comma-separated, up to 50
).execute()

# Your own uploaded videos (requires OAuth)
response = youtube.videos().list(
    part="snippet,statistics",
    myRating="like"   # "like" or "dislike"
).execute()

# Most popular videos (chart)
response = youtube.videos().list(
    part="snippet,statistics",
    chart="mostPopular",
    regionCode="US",
    videoCategoryId="28"  # Science & Technology
).execute()

video = response["items"][0]
print(video["snippet"]["title"])
print(video["statistics"]["viewCount"])
```

### Part Reference

| Part | Contents | Quota Cost |
|------|----------|-----------|
| `snippet` | title, description, channelId, publishedAt, thumbnails, tags, categoryId | 2 |
| `contentDetails` | duration, dimension, definition, caption, regionRestriction | 2 |
| `statistics` | viewCount, likeCount, commentCount, favoriteCount | 2 |
| `status` | privacyStatus, uploadStatus, embeddable, publicStatsViewable | 2 |
| `player` | embedHtml | 0 |
| `topicDetails` | topicCategories (Wikipedia URLs) | 2 |
| `localizations` | title/description in other languages | 2 |
| `liveStreamingDetails` | scheduledStartTime, actualStartTime, concurrentViewers | 2 |

---

## Videos.insert — Upload a Video

**Required scope**: `youtube` or `youtube.upload`

```python
from googleapiclient.http import MediaFileUpload

def upload_video(youtube, file_path, title, description, tags=None,
                 privacy="private", category_id="22"):
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": category_id  # 22 = People & Blogs
        },
        "status": {
            "privacyStatus": privacy,     # "public", "private", "unlisted"
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(
        file_path,
        mimetype="video/*",
        resumable=True,    # Always use resumable for reliability
        chunksize=1024 * 1024 * 8  # 8MB chunks
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload {int(status.progress() * 100)}%")

    print(f"Upload complete: https://youtu.be/{response['id']}")
    return response["id"]
```

### Video Categories (Common IDs)

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

### Privacy Status Options

- `"public"` — visible to everyone
- `"private"` — only visible to you and people you share with
- `"unlisted"` — anyone with the link can view, not searchable

### Scheduled Publishing

```python
import datetime

body["status"]["privacyStatus"] = "private"
body["status"]["publishAt"] = "2024-12-25T10:00:00Z"  # ISO 8601 UTC
```

---

## Videos.update — Edit Video Metadata

**Required scope**: `youtube`

```python
response = youtube.videos().update(
    part="snippet,status",
    body={
        "id": "VIDEO_ID",
        "snippet": {
            "title": "New Title",
            "description": "Updated description",
            "categoryId": "28",
            "tags": ["python", "tutorial", "coding"]
        },
        "status": {
            "privacyStatus": "public"
        }
    }
).execute()
```

**Note**: You must include `categoryId` in snippet updates even if unchanged.

---

## Videos.delete

**Required scope**: `youtube`

```python
youtube.videos().delete(id="VIDEO_ID").execute()
# Returns empty body on success (HTTP 204)
```

---

## Videos.rate — Like / Dislike

**Required scope**: `youtube`

```python
youtube.videos().rate(
    id="VIDEO_ID",
    rating="like"    # "like", "dislike", or "none"
).execute()
```

---

## Thumbnails.set — Upload Custom Thumbnail

**Required scope**: `youtube`

Requires channel to be verified (phone verification) unless it's your own recent video.

```python
from googleapiclient.http import MediaFileUpload

youtube.thumbnails().set(
    videoId="VIDEO_ID",
    media_body=MediaFileUpload(
        "thumbnail.jpg",
        mimetype="image/jpeg"
    )
).execute()
```

Requirements: JPEG/PNG/GIF, max 2MB, recommended 1280x720 (16:9).

---

## Captions

### List captions

```python
response = youtube.captions().list(
    part="snippet",
    videoId="VIDEO_ID"
).execute()
```

### Upload caption track

```python
from googleapiclient.http import MediaFileUpload

youtube.captions().insert(
    part="snippet",
    body={
        "snippet": {
            "videoId": "VIDEO_ID",
            "language": "en",
            "name": "English",
            "isDraft": False
        }
    },
    media_body=MediaFileUpload(
        "captions.srt",
        mimetype="application/octet-stream",
        resumable=False
    )
).execute()
```

Supported formats: `.srt`, `.vtt`, `.sbv`, `.dfxp`, `.ttml`

---

## Handling Large Video Lists

When getting all videos from a channel, combine Channels.list + PlaylistItems.list on the uploads playlist (more efficient than search):

```python
def get_all_channel_videos(youtube, channel_id):
    # Get the uploads playlist ID
    channel = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    ).execute()
    uploads_id = channel["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # Page through the uploads playlist
    videos = []
    next_page = None
    while True:
        playlist_response = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_id,
            maxResults=50,
            pageToken=next_page
        ).execute()
        videos.extend(playlist_response["items"])
        next_page = playlist_response.get("nextPageToken")
        if not next_page:
            break
    return videos
```

This avoids the 500-result cap on search.list and costs less quota.
