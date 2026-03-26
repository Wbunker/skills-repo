# Channels, Playlists, and PlaylistItems — YouTube Data API v3

---

## Channels Resource

Base URL: `https://www.googleapis.com/youtube/v3/channels`

### Methods

| Method | HTTP | Quota Cost | Notes |
|--------|------|-----------|-------|
| list | GET | 1 unit | Retrieve channel data |
| update | PUT | 50 units | Update branding/settings |

### channels.list

**Endpoint:** `GET https://www.googleapis.com/youtube/v3/channels`

#### Required Parameters

- **part** (string): Comma-separated list of parts to return.

#### Filters — specify exactly one

| Filter | Type | Description |
|--------|------|-------------|
| `id` | string | Comma-separated YouTube channel IDs |
| `mine` | boolean | `true` — returns authenticated user's channel |
| `forHandle` | string | YouTube handle (with or without `@` prefix) |
| `forUsername` | string | YouTube username (legacy) |
| `managedByMe` | boolean | YouTube partner channels managed by authenticated user |

#### Optional Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `maxResults` | integer | 1–50, default 5 |
| `pageToken` | string | Pagination token |
| `hl` | string | Language for localized metadata |
| `onBehalfOfContentOwner` | string | YouTube partner parameter |

#### Part Values

| Part | Contains |
|------|----------|
| `id` | Channel ID only |
| `snippet` | title, description, customUrl, publishedAt, thumbnails, country, defaultLanguage, localized |
| `contentDetails` | relatedPlaylists (uploads, favorites, watchHistory, watchLater, likes) |
| `statistics` | viewCount, subscriberCount, hiddenSubscriberCount, videoCount |
| `status` | privacyStatus, isLinked, longUploadsStatus, madeForKids |
| `brandingSettings` | channel settings, header/profile image, featured content |
| `topicDetails` | topicIds, topicCategories |
| `auditDetails` | overallGoodStanding, communityGuidelinesGoodStanding, etc. |
| `localizations` | localized channel metadata |
| `contentOwnerDetails` | content owner and time linked |

#### Example: Get My Channel

```python
response = youtube.channels().list(
    part='snippet,contentDetails,statistics',
    mine=True
).execute()

channel = response['items'][0]
channel_id = channel['id']
title = channel['snippet']['title']
subscriber_count = channel['statistics']['subscriberCount']

# Get uploads playlist ID for cost-efficient video retrieval
uploads_playlist_id = channel['contentDetails']['relatedPlaylists']['uploads']
```

#### Example: Get Channel by Handle

```python
response = youtube.channels().list(
    part='snippet,statistics',
    forHandle='@MrBeast'
).execute()
```

#### The Uploads Playlist Pattern

Getting all videos from a channel using the uploads playlist is much cheaper than search.list:

```python
# Step 1: Get uploads playlist ID (1 unit)
channel_response = youtube.channels().list(
    part='contentDetails',
    mine=True
).execute()
uploads_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

# Step 2: Paginate through all videos (1 unit per page, up to 50 items/page)
videos = []
next_page_token = None

while True:
    pl_response = youtube.playlistItems().list(
        part='snippet,contentDetails',
        playlistId=uploads_id,
        maxResults=50,
        pageToken=next_page_token
    ).execute()

    videos.extend(pl_response['items'])
    next_page_token = pl_response.get('nextPageToken')

    if not next_page_token:
        break
```

Cost: 1 + N units (where N = number of pages), vs. search.list at 100 units per page.

---

## Playlists Resource

Base URL: `https://www.googleapis.com/youtube/v3/playlists`

### Methods

| Method | HTTP | Quota Cost | Required Scope |
|--------|------|-----------|----------------|
| list | GET | 1 unit | API key or youtube.readonly |
| insert | POST | 50 units | youtube or youtube.force-ssl |
| update | PUT | 50 units | youtube or youtube.force-ssl |
| delete | DELETE | 50 units | youtube or youtube.force-ssl |

### playlists.list

**Endpoint:** `GET https://www.googleapis.com/youtube/v3/playlists`

#### Filters — specify exactly one

| Filter | Type | Description |
|--------|------|-------------|
| `id` | string | Comma-separated playlist IDs |
| `mine` | boolean | `true` — authenticated user's playlists |
| `channelId` | string | All playlists belonging to a channel |

#### Optional Parameters

| Parameter | Type | Default |
|-----------|------|---------|
| `maxResults` | integer | 5 (max 50) |
| `pageToken` | string | — |
| `hl` | string | — |
| `onBehalfOfContentOwner` | string | — |

#### Part Values

| Part | Contains |
|------|----------|
| `id` | Playlist ID |
| `snippet` | publishedAt, channelId, title, description, thumbnails, channelTitle, defaultLanguage, localized |
| `status` | privacyStatus (`public`, `private`, `unlisted`), podcastStatus |
| `contentDetails` | itemCount |
| `player` | Embeddable iframe HTML |
| `localizations` | Localized title/description per language |

#### Example: List My Playlists

```python
playlists = []
next_page_token = None

while True:
    response = youtube.playlists().list(
        part='snippet,contentDetails,status',
        mine=True,
        maxResults=50,
        pageToken=next_page_token
    ).execute()

    playlists.extend(response['items'])
    next_page_token = response.get('nextPageToken')

    if not next_page_token:
        break
```

### playlists.insert

```python
response = youtube.playlists().insert(
    part='snippet,status',
    body={
        'snippet': {
            'title': 'My New Playlist',
            'description': 'Playlist description',
            'defaultLanguage': 'en'
        },
        'status': {
            'privacyStatus': 'public'
        }
    }
).execute()

playlist_id = response['id']
```

### playlists.update

```python
response = youtube.playlists().update(
    part='snippet,status',
    body={
        'id': 'PLAYLIST_ID',
        'snippet': {
            'title': 'Updated Title',
            'description': 'Updated description'
        },
        'status': {
            'privacyStatus': 'private'
        }
    }
).execute()
```

### playlists.delete

```python
youtube.playlists().delete(id='PLAYLIST_ID').execute()
# Returns HTTP 204 No Content
```

### Thumbnail Sizes

| Size | Dimensions |
|------|-----------|
| default | 120 × 90 px |
| medium | 320 × 180 px |
| high | 480 × 360 px |
| standard | 640 × 480 px |
| maxres | 1280 × 720 px |

---

## PlaylistItems Resource

Base URL: `https://www.googleapis.com/youtube/v3/playlistItems`

### Methods

| Method | HTTP | Quota Cost | Required Scope |
|--------|------|-----------|----------------|
| list | GET | 1 unit | API key or youtube.readonly |
| insert | POST | 50 units | youtube or youtube.force-ssl |
| update | PUT | 50 units | youtube or youtube.force-ssl |
| delete | DELETE | 50 units | youtube or youtube.force-ssl |

### playlistItems.list

**Endpoint:** `GET https://www.googleapis.com/youtube/v3/playlistItems`

#### Required Parameters

- **part** (string): Parts to return
- **playlistId** (string): The playlist to retrieve items from

#### Optional Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by comma-separated playlistItem IDs |
| `videoId` | string | Filter to only return items with this video ID |
| `maxResults` | integer | 1–50, default 5 |
| `pageToken` | string | Pagination token |
| `onBehalfOfContentOwner` | string | YouTube partner parameter |

#### Part Values

| Part | Contains |
|------|----------|
| `id` | PlaylistItem ID |
| `snippet` | publishedAt, channelId, title, description, thumbnails, channelTitle, playlistId, position, resourceId (kind + videoId) |
| `contentDetails` | videoId, startAt, endAt, note, videoPublishedAt |
| `status` | videoPrivacyStatus |

#### Accessing the Video ID

```python
# From snippet:
video_id = item['snippet']['resourceId']['videoId']

# From contentDetails:
video_id = item['contentDetails']['videoId']
```

#### Position (Zero-Based Index)

Items are ordered by `snippet.position` starting at 0. Position 0 = first item in playlist.

#### Example: Get All Items in a Playlist

```python
items = []
next_page_token = None

while True:
    response = youtube.playlistItems().list(
        part='snippet,contentDetails',
        playlistId='PLAYLIST_ID',
        maxResults=50,
        pageToken=next_page_token
    ).execute()

    items.extend(response['items'])
    next_page_token = response.get('nextPageToken')

    if not next_page_token:
        break

# Extract video IDs
video_ids = [item['contentDetails']['videoId'] for item in items]
```

### playlistItems.insert

Adds a video to a playlist.

```python
response = youtube.playlistItems().insert(
    part='snippet',
    body={
        'snippet': {
            'playlistId': 'PLAYLIST_ID',
            'resourceId': {
                'kind': 'youtube#video',
                'videoId': 'VIDEO_ID'
            },
            'position': 0  # Optional: 0-based position; omit to append
        }
    }
).execute()

playlist_item_id = response['id']
```

### playlistItems.update

Change a playlist item's position.

```python
response = youtube.playlistItems().update(
    part='snippet',
    body={
        'id': 'PLAYLIST_ITEM_ID',
        'snippet': {
            'playlistId': 'PLAYLIST_ID',
            'resourceId': {
                'kind': 'youtube#video',
                'videoId': 'VIDEO_ID'
            },
            'position': 2  # New 0-based position
        }
    }
).execute()
```

### playlistItems.delete

```python
youtube.playlistItems().delete(id='PLAYLIST_ITEM_ID').execute()
```

**Note:** To delete by video ID, first find the playlistItem ID using list with `videoId` filter:

```python
response = youtube.playlistItems().list(
    part='id',
    playlistId='PLAYLIST_ID',
    videoId='VIDEO_ID'
).execute()

if response['items']:
    playlist_item_id = response['items'][0]['id']
    youtube.playlistItems().delete(id=playlist_item_id).execute()
```

---

## Special / Auto-Generated Playlists

Retrieved via `channels.list(part='contentDetails')`:

| Key | Playlist | Notes |
|-----|----------|-------|
| `relatedPlaylists.uploads` | All uploaded videos | Most important; always exists |
| `relatedPlaylists.likes` | Liked videos | May be private |
| `relatedPlaylists.favorites` | Favorited videos | Legacy feature |
| `relatedPlaylists.watchHistory` | Watch history | Private, authenticated only |
| `relatedPlaylists.watchLater` | Watch later | Private, authenticated only |
