# YouTube Data API — Live Streaming

## Overview

YouTube live streaming uses two resources:
- **LiveBroadcast** — the YouTube event/video that viewers see and that appears on the channel
- **LiveStream** — the video ingestion endpoint (stream key + RTMP URL) that your encoder connects to

These must be **bound together** before going live.

```
Your encoder → LiveStream (RTMP ingest) → LiveBroadcast (YouTube event) → Viewers
```

**Required scope**: `youtube`

---

## LiveBroadcasts.insert — Create a Broadcast

```python
from datetime import datetime, timezone, timedelta

# Schedule a broadcast 1 hour from now
scheduled_start = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

response = youtube.liveBroadcasts().insert(
    part="snippet,status,contentDetails",
    body={
        "snippet": {
            "title": "My Live Stream",
            "description": "Live stream description",
            "scheduledStartTime": scheduled_start
        },
        "status": {
            "privacyStatus": "public",          # "public", "private", "unlisted"
            "selfDeclaredMadeForKids": False
        },
        "contentDetails": {
            "enableAutoStart": False,    # auto-start when encoder connects
            "enableAutoStop": False,     # auto-stop when encoder disconnects
            "recordFromStart": True,     # save VOD after stream ends
            "enableDvr": True,           # allow viewers to rewind
            "latencyPreference": "normal"  # "normal", "low", "ultraLow"
        }
    }
).execute()

broadcast_id = response["id"]
print(f"Broadcast created: https://youtu.be/{broadcast_id}")
```

---

## LiveStreams.insert — Create a Stream Ingest Point

```python
response = youtube.liveStreams().insert(
    part="snippet,cdn",
    body={
        "snippet": {
            "title": "My Stream Key"
        },
        "cdn": {
            "frameRate": "60fps",         # "30fps" or "60fps"
            "ingestionType": "rtmp",       # only "rtmp" is supported
            "resolution": "1080p"          # "1080p", "720p", "480p", "360p", "240p"
        }
    }
).execute()

stream_id = response["id"]
stream_key = response["cdn"]["ingestionInfo"]["streamName"]
rtmp_url = response["cdn"]["ingestionInfo"]["ingestionAddress"]
print(f"Stream key: {stream_key}")
print(f"RTMP URL: {rtmp_url}")
# Configure your encoder: Server = rtmp_url, Stream key = stream_key
```

---

## LiveBroadcasts.bind — Bind Broadcast to Stream

After creating both, bind them together:

```python
response = youtube.liveBroadcasts().bind(
    part="id,contentDetails",
    id=broadcast_id,
    streamId=stream_id
).execute()
print("Bound successfully")
```

---

## LiveBroadcasts.transition — Control Broadcast State

A broadcast goes through these states:

```
created → ready → testing → live → complete
```

| State | Description |
|-------|-------------|
| `created` | Broadcast created, not ready |
| `ready` | Configured and ready to go live |
| `testing` | In test mode (preview only, not visible to public) |
| `live` | Actively streaming to viewers |
| `complete` | Stream ended |

```python
# Transition to testing (encoder must be connected and healthy)
youtube.liveBroadcasts().transition(
    broadcastStatus="testing",
    id=broadcast_id,
    part="id,status"
).execute()

# Go live
youtube.liveBroadcasts().transition(
    broadcastStatus="live",
    id=broadcast_id,
    part="id,status"
).execute()

# End the stream
youtube.liveBroadcasts().transition(
    broadcastStatus="complete",
    id=broadcast_id,
    part="id,status"
).execute()
```

---

## LiveBroadcasts.list — Check Broadcast Status

```python
# List your upcoming and active broadcasts
response = youtube.liveBroadcasts().list(
    part="snippet,status,contentDetails",
    broadcastStatus="upcoming",   # "upcoming", "active", "completed", "all"
    mine=True
).execute()

# Check specific broadcast
response = youtube.liveBroadcasts().list(
    part="snippet,status",
    id=broadcast_id
).execute()

status = response["items"][0]["status"]["lifeCycleStatus"]
print(f"Broadcast status: {status}")
```

---

## LiveStreams.list — Check Stream Health

```python
response = youtube.liveStreams().list(
    part="snippet,cdn,status",
    id=stream_id
).execute()

stream = response["items"][0]
stream_status = stream["status"]["streamStatus"]  # "active", "inactive", "error"
health = stream["status"]["healthStatus"]["status"]  # "good", "ok", "bad", "noData"
print(f"Stream status: {stream_status}, Health: {health}")
```

---

## LiveBroadcasts.update — Edit Broadcast

```python
youtube.liveBroadcasts().update(
    part="snippet,status",
    body={
        "id": broadcast_id,
        "snippet": {
            "title": "Updated Title",
            "description": "Updated description",
            "scheduledStartTime": "2024-12-25T18:00:00Z"
        },
        "status": {
            "privacyStatus": "public"
        }
    }
).execute()
```

---

## LiveBroadcasts.delete

```python
# Only broadcasts in "created" or "ready" state can be deleted
youtube.liveBroadcasts().delete(id=broadcast_id).execute()
```

---

## Live Chat

During a live broadcast, you can read and send chat messages:

```python
# Get live chat ID from the broadcast
response = youtube.liveBroadcasts().list(
    part="snippet",
    id=broadcast_id
).execute()
live_chat_id = response["items"][0]["snippet"]["liveChatId"]

# Read chat messages
messages = youtube.liveChatMessages().list(
    liveChatId=live_chat_id,
    part="snippet,authorDetails"
).execute()

for msg in messages["items"]:
    print(f"{msg['authorDetails']['displayName']}: {msg['snippet']['displayMessage']}")

# Poll for new messages using nextPageToken + pollingIntervalMillis
next_page = messages.get("nextPageToken")
poll_interval_ms = messages.get("pollingIntervalMillis", 5000)

# Send a chat message (as the channel owner)
youtube.liveChatMessages().insert(
    part="snippet",
    body={
        "snippet": {
            "liveChatId": live_chat_id,
            "type": "textMessageEvent",
            "textMessageDetails": {
                "messageText": "Welcome to the stream!"
            }
        }
    }
).execute()
```

---

## Full Live Stream Workflow

```python
def start_live_stream(youtube, title, description="", privacy="public"):
    from datetime import datetime, timezone

    # 1. Create broadcast
    broadcast = youtube.liveBroadcasts().insert(
        part="snippet,status,contentDetails",
        body={
            "snippet": {"title": title, "description": description,
                        "scheduledStartTime": datetime.now(timezone.utc).isoformat()},
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
            "contentDetails": {"recordFromStart": True, "enableDvr": True,
                               "latencyPreference": "low"}
        }
    ).execute()

    # 2. Create stream ingest
    stream = youtube.liveStreams().insert(
        part="snippet,cdn",
        body={
            "snippet": {"title": f"{title} - stream"},
            "cdn": {"frameRate": "30fps", "ingestionType": "rtmp", "resolution": "1080p"}
        }
    ).execute()

    # 3. Bind
    youtube.liveBroadcasts().bind(
        part="id,contentDetails",
        id=broadcast["id"],
        streamId=stream["id"]
    ).execute()

    return {
        "broadcast_id": broadcast["id"],
        "stream_id": stream["id"],
        "rtmp_url": stream["cdn"]["ingestionInfo"]["ingestionAddress"],
        "stream_key": stream["cdn"]["ingestionInfo"]["streamName"],
        "watch_url": f"https://youtu.be/{broadcast['id']}"
    }
```
