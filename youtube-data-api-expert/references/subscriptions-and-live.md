# Subscriptions, LiveBroadcasts, and LiveStreams — YouTube Data API v3

---

## Subscriptions Resource

Base URL: `https://www.googleapis.com/youtube/v3/subscriptions`

### Methods

| Method | HTTP | Quota Cost | Required Scope |
|--------|------|-----------|----------------|
| list | GET | 1 unit | youtube.readonly |
| insert | POST | 50 units | youtube or youtube.force-ssl |
| delete | DELETE | 50 units | youtube or youtube.force-ssl |

### subscriptions.list

**Endpoint:** `GET https://www.googleapis.com/youtube/v3/subscriptions`

#### Required Parameters

- **part**: `id`, `snippet`, `contentDetails`, `subscriberSnippet` (comma-separated)

#### Filters — specify exactly one

| Filter | Type | Description |
|--------|------|-------------|
| `channelId` | string | Return subscriptions for a specific channel |
| `id` | string | Comma-separated subscription IDs |
| `mine` | boolean | `true` — authenticated user's subscriptions |
| `myRecentSubscribers` | boolean | `true` — subscribers to authenticated user (reverse chronological) |
| `mySubscribers` | boolean | `true` — subscribers to authenticated user (unordered) |

#### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `forChannelId` | string | — | Filter `mine` results to only show subscription to specified channel IDs (comma-separated); used to check if subscribed |
| `maxResults` | integer | 5 | Items per page (0–50) |
| `order` | string | `relevance` | `alphabetical`, `relevance`, `unread` |
| `pageToken` | string | — | Pagination token |
| `onBehalfOfContentOwner` | string | — | YouTube partner parameter |
| `onBehalfOfContentOwnerChannel` | string | — | YouTube partner parameter |

#### Part Values

| Part | Contains |
|------|----------|
| `id` | Subscription ID |
| `snippet` | publishedAt, title, description, resourceId (channelId), channelId, thumbnails |
| `contentDetails` | totalItemCount, newItemCount, activityType (`all` or `uploads`) |
| `subscriberSnippet` | subscriberChannelId, title, description, thumbnails |

#### Example: Get My Subscriptions

```python
subscriptions = []
next_page_token = None

while True:
    response = youtube.subscriptions().list(
        part='snippet,contentDetails',
        mine=True,
        maxResults=50,
        order='alphabetical',
        pageToken=next_page_token
    ).execute()

    subscriptions.extend(response['items'])
    next_page_token = response.get('nextPageToken')

    if not next_page_token:
        break

# Get subscribed channel IDs
channel_ids = [s['snippet']['resourceId']['channelId'] for s in subscriptions]
```

#### Example: Check If Subscribed to a Channel

```python
response = youtube.subscriptions().list(
    part='id',
    mine=True,
    forChannelId='CHANNEL_ID'
).execute()

is_subscribed = len(response.get('items', [])) > 0
```

#### Example: Get My Subscribers

```python
response = youtube.subscriptions().list(
    part='subscriberSnippet',
    mySubscribers=True,
    maxResults=50
).execute()

for sub in response['items']:
    print(sub['subscriberSnippet']['title'])
```

### subscriptions.insert

Subscribe the authenticated user to a channel.

```python
response = youtube.subscriptions().insert(
    part='snippet',
    body={
        'snippet': {
            'resourceId': {
                'kind': 'youtube#channel',
                'channelId': 'CHANNEL_ID_TO_SUBSCRIBE_TO'
            }
        }
    }
).execute()

subscription_id = response['id']
```

### subscriptions.delete

Unsubscribe from a channel.

```python
# First, find the subscription ID
response = youtube.subscriptions().list(
    part='id',
    mine=True,
    forChannelId='CHANNEL_ID'
).execute()

if response['items']:
    subscription_id = response['items'][0]['id']
    youtube.subscriptions().delete(id=subscription_id).execute()
```

---

## LiveBroadcasts Resource

Base URL: `https://www.googleapis.com/youtube/v3/liveBroadcasts`

A `liveBroadcast` represents the YouTube event that viewers watch. It must be bound to a `liveStream` (the actual video feed from the encoder).

### Methods

| Method | HTTP | Quota Cost | Notes |
|--------|------|-----------|-------|
| list | GET | 1 unit | Retrieve broadcast info |
| insert | POST | 50 units | Create a new broadcast |
| update | PUT | 50 units | Modify broadcast settings |
| delete | DELETE | 50 units | Delete a broadcast |
| bind | POST | 50 units | Bind/unbind broadcast to a stream |
| transition | POST | 50 units | Change broadcast status |
| cuepoint | POST | 50 units | Insert ad cuepoint |

### Broadcast Lifecycle

```
[insert] → created → [configure] → ready
                                     │
                          [transition testStarting]
                                     ↓
                                 testStarting → testing (visible to broadcaster only)
                                     │
                          [transition liveStarting]
                                     ↓
                                 liveStarting → live (public)
                                     │
                          [transition complete]
                                     ↓
                                 complete (broadcast ended)
```

**Key requirement before transitioning:** Verify `liveStreams.list(part='status')` shows `status.streamStatus = 'active'` before transitioning to `testing` or `live`.

### liveBroadcasts.list

```python
# Get active broadcasts
response = youtube.liveBroadcasts().list(
    part='id,snippet,contentDetails,status',
    broadcastStatus='active'  # 'all', 'active', 'completed', 'upcoming'
).execute()
```

#### Key Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `part` | string | `id`, `snippet`, `contentDetails`, `status`, `monetizationDetails` |
| `broadcastStatus` | string | `all`, `active`, `completed`, `upcoming` |
| `id` | string | Comma-separated broadcast IDs |
| `mine` | boolean | `true` — authenticated user's broadcasts |

#### Status Values

| Status | Meaning |
|--------|---------|
| `created` | Created but not fully configured |
| `ready` | Fully configured, ready for testing or live |
| `testStarting` | Transitioning to testing |
| `testing` | In test mode (broadcaster only) |
| `liveStarting` | Transitioning to live |
| `live` | Currently streaming to viewers |
| `complete` | Broadcast ended |
| `revoked` | Removed by administrator |

### liveBroadcasts.insert

```python
from datetime import datetime, timezone, timedelta

scheduled_start = datetime.now(timezone.utc) + timedelta(hours=1)

response = youtube.liveBroadcasts().insert(
    part='snippet,status,contentDetails',
    body={
        'snippet': {
            'title': 'My Live Stream',
            'description': 'Stream description',
            'scheduledStartTime': scheduled_start.isoformat()
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        },
        'contentDetails': {
            'enableAutoStart': True,
            'enableAutoStop': True,
            'enableDvr': True,
            'enableEmbed': True,
            'recordFromStart': True,
            'latencyPreference': 'normal'  # 'ultraLow', 'low', 'normal'
        }
    }
).execute()

broadcast_id = response['id']
```

### liveBroadcasts.transition

```python
# Start testing
youtube.liveBroadcasts().transition(
    broadcastStatus='testing',
    id=broadcast_id,
    part='id,status'
).execute()

# Go live
youtube.liveBroadcasts().transition(
    broadcastStatus='live',
    id=broadcast_id,
    part='id,status'
).execute()

# End broadcast
youtube.liveBroadcasts().transition(
    broadcastStatus='complete',
    id=broadcast_id,
    part='id,status'
).execute()
```

### liveBroadcasts.bind

Bind a broadcast to a stream (or unbind by omitting `streamId`):

```python
response = youtube.liveBroadcasts().bind(
    id=broadcast_id,
    part='id,contentDetails',
    streamId=stream_id
).execute()
```

---

## LiveStreams Resource

Base URL: `https://www.googleapis.com/youtube/v3/liveStreams`

A `liveStream` is the video feed sent from an encoder (OBS, RTMP encoder, etc.) to YouTube. One stream can be bound to multiple broadcasts (e.g., reuse a stream key for recurring shows).

### Methods

| Method | HTTP | Quota Cost | Notes |
|--------|------|-----------|-------|
| list | GET | 1 unit | Retrieve stream info |
| insert | POST | 50 units | Create a new stream |
| update | PUT | 50 units | Modify stream settings |
| delete | DELETE | 50 units | Delete a stream |

### liveStreams.insert

```python
response = youtube.liveStreams().insert(
    part='snippet,cdn,contentDetails,status',
    body={
        'snippet': {
            'title': 'My Stream'
        },
        'cdn': {
            'frameRate': '60fps',      # '30fps', '60fps', 'variable'
            'ingestionType': 'rtmp',   # 'rtmp', 'dash', 'hls'
            'resolution': '1080p'      # '240p','360p','480p','720p','1080p','1440p','2160p','variable'
        },
        'contentDetails': {
            'isReusable': True  # Reuse stream key across multiple broadcasts
        }
    }
).execute()

stream_id = response['id']
rtmp_url = response['cdn']['ingestionInfo']['ingestionAddress']
stream_key = response['cdn']['ingestionInfo']['streamName']
```

### Stream CDN Settings

| Field | Values | Description |
|-------|--------|-------------|
| `ingestionType` | `rtmp`, `dash`, `hls` | Streaming protocol |
| `resolution` | `240p` through `2160p`, `variable` | Stream resolution |
| `frameRate` | `30fps`, `60fps`, `variable` | Frame rate |

### Ingestion Info (from cdn.ingestionInfo)

| Field | Description |
|-------|-------------|
| `ingestionAddress` | Primary RTMP URL (use this in encoder) |
| `backupIngestionAddress` | Backup RTMP URL |
| `rtmpsIngestionAddress` | Secure RTMP (RTMPS) endpoint |
| `streamName` | Stream key to configure in encoder |

### Stream Status Values

| Status | Meaning |
|--------|---------|
| `active` | YouTube is receiving video |
| `created` | Stream created but not receiving video |
| `error` | Stream in error state |
| `inactive` | No video for extended period |
| `ready` | Stream configured and ready |

### liveStreams.list

```python
response = youtube.liveStreams().list(
    part='id,snippet,cdn,status',
    mine=True
).execute()

for stream in response['items']:
    print(f"Stream: {stream['snippet']['title']}")
    print(f"Status: {stream['status']['streamStatus']}")
    print(f"RTMP URL: {stream['cdn']['ingestionInfo']['ingestionAddress']}")
    print(f"Stream Key: {stream['cdn']['ingestionInfo']['streamName']}")
```

---

## Complete Live Streaming Workflow

```python
def start_live_stream(youtube, title, description):
    """Complete flow: create stream, create broadcast, bind, and go live."""

    # 1. Create a live stream (the encoder connection)
    stream = youtube.liveStreams().insert(
        part='snippet,cdn,status',
        body={
            'snippet': {'title': f'{title} Stream'},
            'cdn': {
                'ingestionType': 'rtmp',
                'resolution': '1080p',
                'frameRate': '30fps'
            }
        }
    ).execute()

    stream_id = stream['id']
    rtmp_url = stream['cdn']['ingestionInfo']['ingestionAddress']
    stream_key = stream['cdn']['ingestionInfo']['streamName']
    print(f"Configure encoder with: {rtmp_url}/{stream_key}")

    # 2. Create the broadcast (what viewers see)
    from datetime import datetime, timezone, timedelta
    broadcast = youtube.liveBroadcasts().insert(
        part='snippet,status,contentDetails',
        body={
            'snippet': {
                'title': title,
                'description': description,
                'scheduledStartTime': (
                    datetime.now(timezone.utc) + timedelta(minutes=5)
                ).isoformat()
            },
            'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False},
            'contentDetails': {'enableDvr': True, 'recordFromStart': True}
        }
    ).execute()

    broadcast_id = broadcast['id']

    # 3. Bind stream to broadcast
    youtube.liveBroadcasts().bind(
        id=broadcast_id,
        part='id,contentDetails',
        streamId=stream_id
    ).execute()

    # 4. Wait for stream to become active (encoder must be sending video)
    import time
    while True:
        status = youtube.liveStreams().list(
            part='status', id=stream_id
        ).execute()['items'][0]['status']['streamStatus']

        if status == 'active':
            break
        print(f"Stream status: {status}, waiting...")
        time.sleep(5)

    # 5. Transition to testing, then live
    youtube.liveBroadcasts().transition(
        broadcastStatus='testing', id=broadcast_id, part='id,status'
    ).execute()

    # Optionally verify testing, then:
    youtube.liveBroadcasts().transition(
        broadcastStatus='live', id=broadcast_id, part='id,status'
    ).execute()

    return broadcast_id, stream_id, stream_key
```
