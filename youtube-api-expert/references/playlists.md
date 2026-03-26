# YouTube Data API — Playlists & PlaylistItems

## Playlists.list

```python
# Your own playlists (requires OAuth)
response = youtube.playlists().list(
    part="snippet,contentDetails,status",
    mine=True,
    maxResults=50
).execute()

# Playlists from a specific channel
response = youtube.playlists().list(
    part="snippet,contentDetails",
    channelId="CHANNEL_ID",
    maxResults=50
).execute()

# Specific playlist by ID
response = youtube.playlists().list(
    part="snippet,contentDetails,status",
    id="PLAYLIST_ID"
).execute()

playlist = response["items"][0]
print(playlist["snippet"]["title"])
print(playlist["contentDetails"]["itemCount"])
```

### Pagination

```python
def get_all_playlists(youtube):
    playlists = []
    next_page = None
    while True:
        response = youtube.playlists().list(
            part="snippet,contentDetails",
            mine=True,
            maxResults=50,
            pageToken=next_page
        ).execute()
        playlists.extend(response["items"])
        next_page = response.get("nextPageToken")
        if not next_page:
            break
    return playlists
```

---

## Playlists.insert — Create a Playlist

**Required scope**: `youtube`

```python
response = youtube.playlists().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": "My Playlist",
            "description": "Playlist description",
            "tags": ["tutorial", "python"],
            "defaultLanguage": "en"
        },
        "status": {
            "privacyStatus": "public"   # "public", "private", "unlisted"
        }
    }
).execute()

playlist_id = response["id"]
print(f"Created playlist: {playlist_id}")
```

---

## Playlists.update — Edit Playlist

**Required scope**: `youtube`

```python
youtube.playlists().update(
    part="snippet,status",
    body={
        "id": "PLAYLIST_ID",
        "snippet": {
            "title": "Updated Title",
            "description": "New description"
        },
        "status": {
            "privacyStatus": "unlisted"
        }
    }
).execute()
```

---

## Playlists.delete

**Required scope**: `youtube`

```python
youtube.playlists().delete(id="PLAYLIST_ID").execute()
```

---

## PlaylistItems.list — Get Videos in a Playlist

```python
def get_playlist_videos(youtube, playlist_id):
    videos = []
    next_page = None
    while True:
        response = youtube.playlistItems().list(
            part="snippet,contentDetails,status",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page
        ).execute()
        videos.extend(response["items"])
        next_page = response.get("nextPageToken")
        if not next_page:
            break
    return videos

# Each item has:
# item["snippet"]["title"] — video title
# item["snippet"]["resourceId"]["videoId"] — the video ID
# item["snippet"]["position"] — 0-indexed position in playlist
# item["contentDetails"]["videoId"] — same video ID
# item["contentDetails"]["videoPublishedAt"] — when video was published
# item["status"]["videoPrivacyStatus"] — "public", "private", "unlisted"
```

---

## PlaylistItems.insert — Add Video to Playlist

**Required scope**: `youtube`

```python
def add_video_to_playlist(youtube, playlist_id, video_id, position=None):
    body = {
        "snippet": {
            "playlistId": playlist_id,
            "resourceId": {
                "kind": "youtube#video",
                "videoId": video_id
            }
        }
    }
    if position is not None:
        body["snippet"]["position"] = position  # 0-indexed

    return youtube.playlistItems().insert(
        part="snippet",
        body=body
    ).execute()
```

---

## PlaylistItems.update — Reorder a Video

To move a video to a different position, update its `position` field:

```python
def move_playlist_item(youtube, playlist_item_id, playlist_id, video_id, new_position):
    youtube.playlistItems().update(
        part="snippet",
        body={
            "id": playlist_item_id,
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                },
                "position": new_position
            }
        }
    ).execute()
```

Get `playlist_item_id` from PlaylistItems.list — it's `item["id"]`, distinct from the video ID.

---

## PlaylistItems.delete — Remove Video from Playlist

```python
# playlist_item_id is item["id"] from PlaylistItems.list
youtube.playlistItems().delete(id="PLAYLIST_ITEM_ID").execute()
```

---

## Common Patterns

### Add uploaded video to playlist immediately after upload

```python
video_id = upload_video(youtube, "video.mp4", "My Video", "Description")
add_video_to_playlist(youtube, "PLAYLIST_ID", video_id)
```

### Sync a playlist — add if missing, remove if not in source list

```python
def sync_playlist(youtube, playlist_id, desired_video_ids):
    current_items = get_playlist_videos(youtube, playlist_id)
    current_ids = {item["snippet"]["resourceId"]["videoId"]: item["id"]
                   for item in current_items}

    # Add missing videos
    for video_id in desired_video_ids:
        if video_id not in current_ids:
            add_video_to_playlist(youtube, playlist_id, video_id)

    # Remove extra videos
    for video_id, item_id in current_ids.items():
        if video_id not in desired_video_ids:
            youtube.playlistItems().delete(id=item_id).execute()
```

### Get all video IDs from a channel's uploads

```python
def get_channel_video_ids(youtube, channel_id):
    # Get uploads playlist ID
    ch = youtube.channels().list(
        part="contentDetails", id=channel_id
    ).execute()
    uploads_id = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # Get all videos from uploads playlist
    items = get_playlist_videos(youtube, uploads_id)
    return [item["snippet"]["resourceId"]["videoId"] for item in items]
```
