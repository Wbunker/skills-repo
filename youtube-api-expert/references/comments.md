# YouTube Data API — Comments

## Overview

Two resources handle comments:
- **CommentThreads** — top-level comments (plus reply counts)
- **Comments** — individual comments, including replies

---

## CommentThreads.list — Get Top-Level Comments

```python
# Comments on a specific video
response = youtube.commentThreads().list(
    part="snippet,replies",
    videoId="VIDEO_ID",
    maxResults=100,
    order="relevance"   # "relevance" or "time"
).execute()

for thread in response["items"]:
    top_comment = thread["snippet"]["topLevelComment"]["snippet"]
    print(f"{top_comment['authorDisplayName']}: {top_comment['textDisplay']}")
    print(f"Likes: {top_comment['likeCount']}, Replies: {thread['snippet']['totalReplyCount']}")

    # Access included replies (up to 5 inline)
    if "replies" in thread:
        for reply in thread["replies"]["comments"]:
            print(f"  -> {reply['snippet']['authorDisplayName']}: {reply['snippet']['textDisplay']}")
```

### Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `videoId` | video ID | Comments for a video |
| `channelId` | channel ID | Comments across the channel (including video comments) |
| `id` | thread ID(s) | Specific thread(s) |
| `order` | `relevance`, `time` | Sort order |
| `searchTerms` | string | Filter by keyword |
| `maxResults` | 1–100 | Results per page |
| `moderationStatus` | `published`, `heldForReview`, `likelySpam`, `rejected` | Filter by moderation state |

### Part Reference

| Part | Contents |
|------|----------|
| `snippet` | Top-level comment text, author, likeCount, totalReplyCount, publishedAt |
| `replies` | Up to 5 most recent replies inline |

---

## Pagination

```python
def get_all_comments(youtube, video_id):
    comments = []
    next_page = None
    while True:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=next_page
        ).execute()
        comments.extend(response["items"])
        next_page = response.get("nextPageToken")
        if not next_page:
            break
    return comments
```

---

## CommentThreads.insert — Post a Top-Level Comment

**Required scope**: `youtube.force-ssl`

```python
response = youtube.commentThreads().insert(
    part="snippet",
    body={
        "snippet": {
            "videoId": "VIDEO_ID",
            "topLevelComment": {
                "snippet": {
                    "textOriginal": "Great video!"
                }
            }
        }
    }
).execute()
print(f"Comment ID: {response['id']}")
```

---

## Comments.list — Get Replies to a Thread

```python
response = youtube.comments().list(
    part="snippet",
    parentId="COMMENT_THREAD_ID",   # the thread ID, not the top comment ID
    maxResults=100
).execute()

for reply in response["items"]:
    print(f"{reply['snippet']['authorDisplayName']}: {reply['snippet']['textDisplay']}")
```

---

## Comments.insert — Reply to a Comment

**Required scope**: `youtube.force-ssl`

```python
youtube.comments().insert(
    part="snippet",
    body={
        "snippet": {
            "parentId": "COMMENT_THREAD_ID",
            "textOriginal": "Thanks for your comment!"
        }
    }
).execute()
```

---

## Comments.update — Edit a Comment

**Required scope**: `youtube.force-ssl`

Can only edit your own comments.

```python
youtube.comments().update(
    part="snippet",
    body={
        "id": "COMMENT_ID",
        "snippet": {
            "textOriginal": "Updated comment text"
        }
    }
).execute()
```

---

## Comments.delete

**Required scope**: `youtube.force-ssl`

Can delete your own comments, or any comment on your own videos.

```python
youtube.comments().delete(id="COMMENT_ID").execute()
```

---

## Comments.setModerationStatus — Moderate Comments

**Required scope**: `youtube.force-ssl`

Only works on comments on your own videos.

```python
youtube.comments().setModerationStatus(
    id="COMMENT_ID1,COMMENT_ID2",
    moderationStatus="published",    # "published", "heldForReview", or "rejected"
    banAuthor=False   # True to ban the commenter from commenting on your channel
).execute()
```

---

## Comments.markAsSpam

**Required scope**: `youtube.force-ssl`

```python
youtube.comments().markAsSpam(id="COMMENT_ID").execute()
```

---

## Disable/Enable Comments on a Video

Comments are controlled via the video's status, not through the Comments API directly:

```python
# Disable comments
youtube.videos().update(
    part="status",
    body={
        "id": "VIDEO_ID",
        "status": {
            "privacyStatus": "public"  # keep existing privacy
        }
    }
).execute()
# Note: to disable comments use the "commentPolicy" field if available,
# or manage via YouTube Studio — the API doesn't directly expose a simple toggle
```

---

## Common Pattern: Comment Analysis

```python
def analyze_video_comments(youtube, video_id, max_pages=5):
    """Get comment sentiment data for a video."""
    all_comments = []
    next_page = None
    page = 0

    while page < max_pages:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            order="relevance",
            pageToken=next_page
        ).execute()

        for thread in response["items"]:
            snippet = thread["snippet"]["topLevelComment"]["snippet"]
            all_comments.append({
                "id": thread["id"],
                "text": snippet["textOriginal"],
                "author": snippet["authorDisplayName"],
                "likes": snippet["likeCount"],
                "replies": thread["snippet"]["totalReplyCount"],
                "published": snippet["publishedAt"]
            })

        next_page = response.get("nextPageToken")
        page += 1
        if not next_page:
            break

    return all_comments
```
