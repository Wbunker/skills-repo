# Tweepy v4 Guide for X API v2

tweepy is the most widely used Python client for the X API.
Install: `pip install tweepy`

## Table of Contents
1. [Client Setup](#setup)
2. [Common Operations](#operations)
3. [Streaming](#streaming)
4. [Pagination](#pagination)
5. [Rate Limit Handling](#rate-limits)
6. [Other Python Libraries](#alternatives)

---

## Setup

### Read-only (Bearer Token)
```python
import tweepy

client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")
```

### User context — OAuth 1.0a (post, DM, like, follow)
```python
client = tweepy.Client(
    consumer_key="API_KEY",
    consumer_secret="API_KEY_SECRET",
    access_token="ACCESS_TOKEN",
    access_token_secret="ACCESS_TOKEN_SECRET",
)
```

### User context — OAuth 2.0 (recommended for new projects)
```python
# Step 1: Generate auth URL and redirect user
oauth2_user_handler = tweepy.OAuth2UserHandler(
    client_id="CLIENT_ID",
    redirect_uri="https://your-app/callback",
    scope=["tweet.read", "tweet.write", "users.read", "offline.access"],
    client_secret="CLIENT_SECRET",
)
auth_url = oauth2_user_handler.get_authorization_url()

# Step 2: After user authorizes, exchange code for token
access_token = oauth2_user_handler.fetch_token("CALLBACK_URL_WITH_CODE")

# Step 3: Use token
client = tweepy.Client(oauth2_session=oauth2_user_handler)
```

### Auto rate-limit handling
```python
client = tweepy.Client(
    bearer_token="...",
    wait_on_rate_limit=True,  # auto-sleeps when rate limit hit
)
```

---

## Operations

### Post a tweet
```python
response = client.create_tweet(text="Hello from the X API!")
tweet_id = response.data["id"]
```

### Post with media
```python
# Media upload still uses v1.1 API via tweepy.API (v2 media upload in beta)
auth = tweepy.OAuth1UserHandler("API_KEY", "API_KEY_SECRET", "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET")
api = tweepy.API(auth)
media = api.media_upload("image.jpg")

client.create_tweet(text="Tweet with image", media_ids=[media.media_id])
```

### Delete a tweet
```python
client.delete_tweet(tweet_id)
```

### Search recent tweets (Basic tier required)
```python
response = client.search_recent_tweets(
    query="python -is:retweet",
    max_results=10,
    tweet_fields=["created_at", "author_id", "public_metrics"],
)
for tweet in response.data:
    print(tweet.text, tweet.public_metrics)
```

### Get a user's timeline
```python
user = client.get_user(username="username")
tweets = client.get_users_tweets(
    id=user.data.id,
    max_results=10,
    tweet_fields=["created_at", "public_metrics"],
)
```

### Get mentions
```python
me = client.get_me()
mentions = client.get_users_mentions(
    id=me.data.id,
    tweet_fields=["created_at", "author_id"],
)
```

### Like / Unlike
```python
me = client.get_me()
client.like(me.data.id, tweet_id)
client.unlike(me.data.id, tweet_id)
```

### Follow / Unfollow
```python
me = client.get_me()
target = client.get_user(username="someuser")
client.follow_user(me.data.id, target.data.id)
client.unfollow_user(me.data.id, target.data.id)
```

### Send a DM
```python
response = client.create_direct_message(
    participant_id="TARGET_USER_ID",
    text="Hello!",
)
```

### Look up a user
```python
user = client.get_user(
    username="username",
    user_fields=["description", "public_metrics", "created_at"],
)
print(user.data.public_metrics)  # followers_count, following_count, tweet_count
```

---

## Streaming

### Filtered stream (Pro tier required)
```python
class MyStream(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        print(tweet.text)

    def on_error(self, status):
        print(f"Error: {status}")

stream = MyStream(bearer_token="BEARER_TOKEN")

# Add rules (keywords, users, etc.)
stream.add_rules(tweepy.StreamRule("python OR django"))

# Start streaming
stream.filter(tweet_fields=["author_id", "created_at"])
```

### Sampled stream (Pro tier required)
```python
class SampleStream(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        print(tweet.text)

stream = SampleStream(bearer_token="BEARER_TOKEN")
stream.sample()
```

---

## Pagination

Use `tweepy.Paginator` to automatically handle multi-page results:

```python
# Get all recent tweets matching a query (up to 100 per page)
for tweet in tweepy.Paginator(
    client.search_recent_tweets,
    query="python",
    tweet_fields=["created_at"],
    max_results=100,
).flatten(limit=1000):  # limit total results
    print(tweet.text)
```

---

## Rate Limit Handling

```python
import time

def safe_request(fn, *args, **kwargs):
    """Retry once after waiting if rate limited."""
    try:
        return fn(*args, **kwargs)
    except tweepy.TooManyRequests as e:
        reset_time = int(e.response.headers.get("x-rate-limit-reset", time.time() + 60))
        sleep_secs = max(reset_time - time.time() + 1, 1)
        print(f"Rate limited. Sleeping {sleep_secs:.0f}s...")
        time.sleep(sleep_secs)
        return fn(*args, **kwargs)
```

Or simply use `wait_on_rate_limit=True` on the client for automatic handling.

---

## Alternatives

| Library | Install | Best for |
|---------|---------|----------|
| **tweepy** | `pip install tweepy` | General use; largest community |
| **twarc2** | `pip install twarc` | Research/archival; bulk collection; CLI-first |
| **python-twitter-v2** | `pip install python-twitter-v2` | Pure v2 API; alternative design |
| **X official SDK** | See docs.x.com | Official support; async; type hints |

**twarc2** is especially useful for large-scale data collection — it handles rate limits
automatically and is designed for academic/research workflows.
