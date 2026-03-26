# YouTube Data API — Channels Resource

## Channels.list — Get Channel Data

```python
# Your own channel (requires OAuth with youtube.readonly or youtube scope)
response = youtube.channels().list(
    part="snippet,contentDetails,statistics,brandingSettings",
    mine=True
).execute()

# By channel ID
response = youtube.channels().list(
    part="snippet,statistics",
    id="UCxxxxxxxxxxxxxxxxxxxxxx"
).execute()

# By handle (@ username) — use forHandle parameter
response = youtube.channels().list(
    part="snippet,statistics",
    forHandle="mkbhd"   # without the @
).execute()

# By custom URL (legacy)
response = youtube.channels().list(
    part="snippet",
    forUsername="GoogleDevelopers"
).execute()

channel = response["items"][0]
print(channel["snippet"]["title"])
print(channel["statistics"]["subscriberCount"])
print(channel["statistics"]["videoCount"])
```

### Part Reference

| Part | Contents |
|------|----------|
| `snippet` | title, description, customUrl, publishedAt, thumbnails, defaultLanguage, country |
| `contentDetails` | relatedPlaylists (uploads, likes, favorites) |
| `statistics` | viewCount, subscriberCount, videoCount, hiddenSubscriberCount |
| `brandingSettings` | channel title, description, keywords, defaultTab, featuredChannelsUrls |
| `status` | privacyStatus, isLinked, madeForKids |
| `topicDetails` | topicCategories |

### Get Uploads Playlist ID

The uploads playlist contains all public videos from a channel. This is the efficient way to enumerate channel videos:

```python
uploads_playlist_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]
# e.g., "UUxxxxxxxxxxxxxxxxxxxxxx" (note double U prefix vs UC for channel ID)
```

---

## Channels.update — Update Channel Metadata

**Required scope**: `youtube`

```python
response = youtube.channels().update(
    part="brandingSettings",
    body={
        "id": "CHANNEL_ID",
        "brandingSettings": {
            "channel": {
                "title": "My Channel",
                "description": "Channel description",
                "keywords": "python tutorial coding",
                "defaultLanguage": "en",
                "country": "US"
            }
        }
    }
).execute()
```

### Update Channel Localizations

```python
youtube.channels().update(
    part="localizations",
    body={
        "id": "CHANNEL_ID",
        "localizations": {
            "es": {
                "title": "Mi Canal",
                "description": "Descripción del canal"
            }
        }
    }
).execute()
```

---

## Channel Sections

Channel sections organize content on the channel homepage.

### List sections

```python
response = youtube.channelSections().list(
    part="snippet,contentDetails",
    channelId="CHANNEL_ID"
).execute()
```

### Create a section

```python
youtube.channelSections().insert(
    part="snippet,contentDetails",
    body={
        "snippet": {
            "type": "singlePlaylist",    # see types below
            "title": "Featured Videos",
            "position": 0               # 0 = top
        },
        "contentDetails": {
            "playlists": ["PLAYLIST_ID"]
        }
    }
).execute()
```

### Section Types

| type | Description |
|------|-------------|
| `singlePlaylist` | A specific playlist |
| `multiplePlaylists` | Multiple playlists |
| `popularUploads` | Auto: most popular videos |
| `recentUploads` | Auto: newest videos |
| `recentPosts` | Community posts |
| `featuredChannels` | Other channels to feature |
| `subscriptions` | User's subscriptions (mine only) |
| `likedPlaylists` | User's liked playlists |

---

## Subscriptions

### List your subscriptions

```python
# Requires OAuth + youtube.readonly scope
response = youtube.subscriptions().list(
    part="snippet",
    mine=True,
    maxResults=50
).execute()
```

### Check if subscribed to a channel

```python
response = youtube.subscriptions().list(
    part="snippet",
    forChannelId="CHANNEL_ID",
    mine=True
).execute()
is_subscribed = len(response.get("items", [])) > 0
```

### Subscribe to a channel

```python
youtube.subscriptions().insert(
    part="snippet",
    body={
        "snippet": {
            "resourceId": {
                "kind": "youtube#channel",
                "channelId": "CHANNEL_ID"
            }
        }
    }
).execute()
```

### Unsubscribe

```python
# First get the subscription ID
subs = youtube.subscriptions().list(
    part="id",
    forChannelId="CHANNEL_ID",
    mine=True
).execute()
subscription_id = subs["items"][0]["id"]

youtube.subscriptions().delete(id=subscription_id).execute()
```

---

## Channel Members (Memberships)

Members are YouTube channel subscribers who pay for membership.

**Required scope**: `youtube.channel-memberships.creator`

```python
# List channel members
response = youtube.members().list(
    part="snippet",
    mode="listMembers",     # or "listAllMembers"
    maxResults=1000
).execute()

# List membership levels
response = youtube.membershipsLevels().list(
    part="snippet",
    mine=True
).execute()
```

---

## Common Patterns

### Get channel ID from handle

```python
def get_channel_id(youtube, handle):
    response = youtube.channels().list(
        part="id",
        forHandle=handle
    ).execute()
    if response["items"]:
        return response["items"][0]["id"]
    return None
```

### Get channel statistics summary

```python
def channel_stats(youtube):
    response = youtube.channels().list(
        part="statistics,snippet",
        mine=True
    ).execute()
    ch = response["items"][0]
    return {
        "title": ch["snippet"]["title"],
        "subscribers": int(ch["statistics"].get("subscriberCount", 0)),
        "views": int(ch["statistics"]["viewCount"]),
        "videos": int(ch["statistics"]["videoCount"])
    }
```
