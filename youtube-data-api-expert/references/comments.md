# Comments and CommentThreads — YouTube Data API v3

## Overview

YouTube has two related comment resources:
- **CommentThreads**: Top-level comments + their reply threads
- **Comments**: Individual comments (both top-level and replies)

Use `commentThreads.list` to retrieve top-level comments on a video or channel.
Use `comments.list` to retrieve replies to a specific comment thread.
Use `comments.insert` to post a reply. Use `commentThreads.insert` to post a new top-level comment.

---

## CommentThreads Resource

Base URL: `https://www.googleapis.com/youtube/v3/commentThreads`

### Methods

| Method | HTTP | Quota Cost | Notes |
|--------|------|-----------|-------|
| list | GET | 1 unit | Get top-level comment threads |
| insert | POST | 50 units | Create new top-level comment |

### commentThreads.list

**Endpoint:** `GET https://www.googleapis.com/youtube/v3/commentThreads`

#### Required Parameters

- **part**: `id`, `snippet`, `replies` (comma-separated)

#### Filters — specify exactly one

| Filter | Type | Description |
|--------|------|-------------|
| `videoId` | string | All comment threads for a specific video |
| `id` | string | Comma-separated comment thread IDs |
| `allThreadsRelatedToChannelId` | string | All comments across the channel (video comments + channel comments) |

**Note:** `channelId` filter (comments posted directly to channel page) is also supported but different from `allThreadsRelatedToChannelId`.

#### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `maxResults` | integer | 20 | Items per page (1–100) — does NOT work with `id` filter |
| `moderationStatus` | string | `published` | `heldForReview`, `likelySpam`, `published`, `rejected`; requires channel/video owner auth |
| `order` | string | `time` | `time` (newest first) or `relevance`; does NOT work with `id` |
| `pageToken` | string | — | Pagination; does NOT work with `id` |
| `searchTerms` | string | — | Filter to comments containing this text; does NOT work with `id` |
| `textFormat` | string | `html` | `html` or `plainText` |

#### Part Values

| Part | Contains |
|------|----------|
| `id` | Comment thread ID |
| `snippet` | `topLevelComment` (full comment resource), `channelId`, `videoId`, `canReply`, `totalReplyCount`, `isPublic` |
| `replies` | `comments[]` — up to 5 most recent replies (use comments.list for all) |

#### Response Structure

```json
{
  "kind": "youtube#commentThreadListResponse",
  "etag": "...",
  "nextPageToken": "TOKEN",
  "pageInfo": {
    "totalResults": 1234,
    "resultsPerPage": 20
  },
  "items": [
    {
      "kind": "youtube#commentThread",
      "id": "THREAD_ID",
      "snippet": {
        "channelId": "CHANNEL_ID",
        "videoId": "VIDEO_ID",
        "topLevelComment": {
          "kind": "youtube#comment",
          "id": "COMMENT_ID",
          "snippet": {
            "videoId": "VIDEO_ID",
            "textDisplay": "Great video!",
            "textOriginal": "Great video!",
            "authorDisplayName": "User Name",
            "authorProfileImageUrl": "https://...",
            "authorChannelUrl": "http://www.youtube.com/channel/...",
            "authorChannelId": {"value": "CHANNEL_ID"},
            "likeCount": 42,
            "publishedAt": "2024-01-01T12:00:00.000Z",
            "updatedAt": "2024-01-01T12:00:00.000Z"
          }
        },
        "canReply": true,
        "totalReplyCount": 5,
        "isPublic": true
      },
      "replies": {
        "comments": [...]
      }
    }
  ]
}
```

#### Example: Get Video Comments

```python
comments = []
next_page_token = None

while True:
    response = youtube.commentThreads().list(
        part='snippet,replies',
        videoId='VIDEO_ID',
        maxResults=100,
        order='time',
        textFormat='plainText',
        pageToken=next_page_token
    ).execute()

    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']
        comments.append({
            'id': item['snippet']['topLevelComment']['id'],
            'thread_id': item['id'],
            'text': comment['textDisplay'],
            'author': comment['authorDisplayName'],
            'likes': comment['likeCount'],
            'published_at': comment['publishedAt'],
            'reply_count': item['snippet']['totalReplyCount']
        })

    next_page_token = response.get('nextPageToken')
    if not next_page_token:
        break
```

#### Example: Search Comments by Text

```python
response = youtube.commentThreads().list(
    part='snippet',
    videoId='VIDEO_ID',
    searchTerms='question',
    maxResults=50
).execute()
```

### commentThreads.insert

Creates a new top-level comment on a video.

```python
response = youtube.commentThreads().insert(
    part='snippet',
    body={
        'snippet': {
            'videoId': 'VIDEO_ID',
            'topLevelComment': {
                'snippet': {
                    'textOriginal': 'This is my comment!'
                }
            }
        }
    }
).execute()

new_comment_id = response['snippet']['topLevelComment']['id']
```

---

## Comments Resource

Base URL: `https://www.googleapis.com/youtube/v3/comments`

### Methods

| Method | HTTP | Quota Cost | Notes |
|--------|------|-----------|-------|
| list | GET | 1 unit | Get replies to a thread |
| insert | POST | 50 units | Post a reply |
| update | PUT | 50 units | Edit your comment |
| delete | DELETE | 50 units | Delete a comment |
| setModerationStatus | POST | 50 units | Moderate comments (owner only) |

### comments.list

Used to retrieve all replies to a comment thread (not just the 5 returned in `commentThreads.list(part='replies')`).

```python
response = youtube.comments().list(
    part='snippet',
    parentId='COMMENT_THREAD_ID',  # The top-level comment's ID
    maxResults=100,
    textFormat='plainText'
).execute()

replies = response['items']
```

#### Filters

| Filter | Type | Description |
|--------|------|-------------|
| `id` | string | Comma-separated comment IDs |
| `parentId` | string | Thread ID — returns all replies |

### comments.insert (Reply to a Comment)

```python
response = youtube.comments().insert(
    part='snippet',
    body={
        'snippet': {
            'parentId': 'PARENT_COMMENT_ID',  # The comment being replied to
            'textOriginal': 'Thanks for your comment!'
        }
    }
).execute()
```

### comments.update

```python
response = youtube.comments().update(
    part='snippet',
    body={
        'id': 'COMMENT_ID',
        'snippet': {
            'textOriginal': 'Updated comment text'
        }
    }
).execute()
```

### comments.delete

```python
youtube.comments().delete(id='COMMENT_ID').execute()
```

### comments.setModerationStatus

Requires authentication as the channel or video owner.

```python
youtube.comments().setModerationStatus(
    id='COMMENT_ID1,COMMENT_ID2',
    moderationStatus='rejected',  # or 'heldForReview', 'published'
    banAuthor=False  # True to ban the comment author
).execute()
```

#### Moderation Status Values

| Value | Meaning |
|-------|---------|
| `published` | Comment is visible to all users |
| `heldForReview` | Held for manual review (not visible to others) |
| `likelySpam` | Marked as likely spam (not visible to others) |
| `rejected` | Rejected; comment removed (author sees it as published) |

---

## Comment Properties

The `snippet` of a comment resource contains:

| Property | Type | Description |
|----------|------|-------------|
| `textDisplay` | string | HTML-formatted comment text |
| `textOriginal` | string | Plain text as author wrote it (owner/auth only) |
| `authorDisplayName` | string | Comment author's name |
| `authorProfileImageUrl` | string | Author's profile image URL |
| `authorChannelUrl` | string | Author's channel URL |
| `authorChannelId.value` | string | Author's channel ID |
| `parentId` | string | Present for replies; ID of parent comment |
| `likeCount` | integer | Number of likes on the comment |
| `viewerRating` | string | `like` or `none` (authenticated user's rating) |
| `canRate` | boolean | Whether current user can rate this comment |
| `moderationStatus` | string | Only visible to channel/video owner |
| `publishedAt` | datetime | When comment was posted |
| `updatedAt` | datetime | When comment was last edited |

---

## Important Restrictions

1. **Comments disabled on some videos**: If comments are disabled, `commentThreads.list` returns an empty result or error. Check `snippet.commentCount` from `videos.list(part='statistics')` first.

2. **Made for Kids**: Videos marked as "made for kids" have comments disabled.

3. **Reply depth**: YouTube only supports two levels — top-level comments and replies. Replies cannot be replied to further; they all appear as replies to the top-level comment.

4. **5-reply preview**: `commentThreads.list(part='replies')` returns at most 5 replies. Use `comments.list(parentId=...)` for all replies.

5. **Moderation status filter**: The `moderationStatus` parameter in `commentThreads.list` requires the authenticated user to be the channel or video owner.

6. **textOriginal privacy**: `textOriginal` is only returned to the comment's author or the video/channel owner.

---

## Comment Workflow Pattern

```python
# Full comment retrieval workflow
def get_all_comments(youtube, video_id):
    """Get all top-level comments and their replies for a video."""
    all_comments = []
    next_page_token = None

    while True:
        # Get top-level comment threads
        threads_response = youtube.commentThreads().list(
            part='snippet,replies',
            videoId=video_id,
            maxResults=100,
            textFormat='plainText',
            pageToken=next_page_token
        ).execute()

        for thread in threads_response['items']:
            top_comment = thread['snippet']['topLevelComment']['snippet']
            all_comments.append({
                'type': 'comment',
                'id': thread['snippet']['topLevelComment']['id'],
                'text': top_comment['textDisplay'],
                'author': top_comment['authorDisplayName'],
                'likes': top_comment['likeCount'],
                'published_at': top_comment['publishedAt'],
                'reply_count': thread['snippet']['totalReplyCount']
            })

            # If there are more replies than shown, fetch them all
            if (thread['snippet']['totalReplyCount'] > 5 and
                    'replies' in thread):
                replies_response = youtube.comments().list(
                    part='snippet',
                    parentId=thread['id'],
                    maxResults=100
                ).execute()

                for reply in replies_response['items']:
                    r = reply['snippet']
                    all_comments.append({
                        'type': 'reply',
                        'id': reply['id'],
                        'parent_id': thread['id'],
                        'text': r['textDisplay'],
                        'author': r['authorDisplayName'],
                        'likes': r['likeCount'],
                        'published_at': r['publishedAt']
                    })

        next_page_token = threads_response.get('nextPageToken')
        if not next_page_token:
            break

    return all_comments
```
