# Layer 1: Research Engine (Scrapers)

Scrapes 9 platforms overnight. By morning, 2,000+ topics sit in SQLite waiting to be scored.

## Table of Contents
- [Base scraper class](#base-scraper-class)
- [Platform-by-platform guide](#platform-by-platform-guide)
- [Chrome extension (passive capture)](#chrome-extension)
- [Running all scrapers](#running-all-scrapers)

## Base Scraper Class

All platform scrapers inherit from this:

```python
# scrapers/base_scraper.py
from datetime import datetime
import sqlite3

class BaseScraper:
    def __init__(self, source_name, db_path="data/content_engine.db"):
        self.source = source_name
        self.db_path = db_path

    def scrape(self):
        raise NotImplementedError

    def store(self, topic: dict):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                INSERT OR IGNORE INTO topics
                    (source, title, url, engagement, engagement_delta, shares, comments, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.source,
                topic["title"],
                topic.get("url", ""),
                topic.get("engagement", 0),
                topic.get("engagement_delta", 0),
                topic.get("shares", 0),
                topic.get("comments", 0),
                datetime.utcnow().isoformat(),
            ))
            conn.commit()
        finally:
            conn.close()
```

## Platform-by-Platform Guide

### Reddit (praw — free, reliable)

```bash
pip install praw
# Register app: https://www.reddit.com/prefs/apps → "script" type
```

```python
# scrapers/reddit_scraper.py
import praw
from .base_scraper import BaseScraper

SUBREDDITS = ["programming", "MachineLearning", "datascience",
              "technology", "artificial", "Python", "webdev"]

class RedditScraper(BaseScraper):
    def __init__(self):
        super().__init__("reddit")
        self.reddit = praw.Reddit(
            client_id=os.environ["REDDIT_CLIENT_ID"],
            client_secret=os.environ["REDDIT_CLIENT_SECRET"],
            user_agent=os.environ["REDDIT_USER_AGENT"],
        )

    def scrape(self):
        for sub in SUBREDDITS:
            for post in self.reddit.subreddit(sub).hot(limit=50):
                self.store({
                    "title": post.title,
                    "url": post.url,
                    "engagement": post.score,
                    "engagement_delta": post.upvote_ratio * post.score,
                    "shares": 0,
                    "comments": post.num_comments,
                })
```

### Hacker News (requests — free, no auth)

```python
# scrapers/hn_scraper.py
import requests
from .base_scraper import BaseScraper

class HNScraper(BaseScraper):
    def __init__(self):
        super().__init__("hackernews")

    def scrape(self):
        top_ids = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json"
        ).json()[:100]
        for story_id in top_ids:
            item = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            ).json()
            if item and item.get("type") == "story":
                self.store({
                    "title": item.get("title", ""),
                    "url": item.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                    "engagement": item.get("score", 0),
                    "comments": item.get("descendants", 0),
                })
```

### GitHub Trending (BeautifulSoup — free, no auth)

```python
# scrapers/github_scraper.py
import requests
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class GitHubTrendingScraper(BaseScraper):
    def __init__(self):
        super().__init__("github")

    def scrape(self):
        for period in ["daily", "weekly"]:
            resp = requests.get(
                f"https://github.com/trending?since={period}",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            soup = BeautifulSoup(resp.text, "html.parser")
            for repo in soup.select("article.Box-row"):
                name = repo.select_one("h2 a")
                stars = repo.select_one(".octicon-star")
                if name:
                    star_count = 0
                    if stars and stars.parent:
                        try:
                            star_count = int(stars.parent.text.strip().replace(",", ""))
                        except ValueError:
                            pass
                    self.store({
                        "title": name.get_text(strip=True).replace("\n", "").replace(" ", "/", 1),
                        "url": f"https://github.com{name['href']}",
                        "engagement": star_count,
                    })
```

### YouTube (yt-dlp — free, no auth needed for metadata)

```bash
pip install yt-dlp
```

```python
# scrapers/youtube_scraper.py
import yt_dlp
from .base_scraper import BaseScraper

CHANNELS = ["@TwoMinutePapers", "@YannicKilcher", "@sentdex"]

class YouTubeScraper(BaseScraper):
    def __init__(self):
        super().__init__("youtube")

    def scrape(self):
        ydl_opts = {"quiet": True, "extract_flat": True, "playlistend": 20}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for channel in CHANNELS:
                info = ydl.extract_info(
                    f"https://www.youtube.com/{channel}/videos", download=False
                )
                for entry in (info.get("entries") or []):
                    self.store({
                        "title": entry.get("title", ""),
                        "url": f"https://youtube.com/watch?v={entry['id']}",
                        "engagement": entry.get("view_count", 0),
                        "comments": entry.get("comment_count", 0),
                    })
```

### Google Trends (pytrends — free but unreliable)

```bash
pip install pytrends
```

```python
# scrapers/trends_scraper.py
import time
from pytrends.request import TrendReq
from .base_scraper import BaseScraper

KEYWORDS = ["AI", "machine learning", "Python", "web development", "data science"]

class TrendsScraper(BaseScraper):
    def __init__(self):
        super().__init__("google_trends")
        self.pytrends = TrendReq(hl="en-US", tz=360)

    def scrape(self):
        try:
            self.pytrends.build_payload(KEYWORDS, timeframe="now 1-d")
            related = self.pytrends.related_queries()
            for kw, data in related.items():
                if data["rising"] is not None:
                    for _, row in data["rising"].head(10).iterrows():
                        self.store({
                            "title": f"{kw}: {row['query']}",
                            "url": "",
                            "engagement": int(row["value"]),
                        })
            time.sleep(60)  # pytrends rate limit
        except Exception:
            pass  # Google Trends breaks often — fail silently
```

### Twitter/X (tweepy — requires paid API)

Only add if you have API access. Free tier is extremely limited.

```python
# scrapers/twitter_scraper.py — optional
import tweepy
from .base_scraper import BaseScraper

class TwitterScraper(BaseScraper):
    def __init__(self):
        super().__init__("twitter")
        self.client = tweepy.Client(bearer_token=os.environ["TWITTER_BEARER_TOKEN"])

    def scrape(self):
        # Search recent tweets on your topics
        query = "(AI OR machinelearning OR Python) lang:en -is:retweet"
        tweets = self.client.search_recent_tweets(
            query=query, max_results=100,
            tweet_fields=["public_metrics", "created_at"]
        )
        for tweet in (tweets.data or []):
            m = tweet.public_metrics
            self.store({
                "title": tweet.text[:200],
                "url": f"https://twitter.com/i/web/status/{tweet.id}",
                "engagement": m["like_count"] + m["retweet_count"],
                "shares": m["retweet_count"],
                "comments": m["reply_count"],
            })
```

### Dev.to / Medium / Product Hunt

```python
# scrapers/devto_scraper.py
import requests
from .base_scraper import BaseScraper

class DevToScraper(BaseScraper):
    def __init__(self):
        super().__init__("devto")

    def scrape(self):
        articles = requests.get(
            "https://dev.to/api/articles?top=7&per_page=50"
        ).json()
        for a in articles:
            self.store({
                "title": a["title"],
                "url": a["url"],
                "engagement": a["public_reactions_count"],
                "comments": a["comments_count"],
            })
```

## Chrome Extension

A lightweight Chrome extension that passively captures posts as you scroll X, LinkedIn, and Reddit.

**manifest.json:**
```json
{
  "manifest_version": 3,
  "name": "Content Engine Capture",
  "version": "1.0",
  "permissions": ["activeTab"],
  "content_scripts": [{
    "matches": ["*://twitter.com/*", "*://x.com/*",
                "*://www.linkedin.com/*", "*://www.reddit.com/*"],
    "js": ["content.js"]
  }]
}
```

**content.js** (simplified):
```javascript
// Observe feed posts and POST to local ingest server
const observer = new MutationObserver(() => {
  document.querySelectorAll('[data-testid="tweet"]').forEach(el => {
    const text = el.innerText.slice(0, 200);
    if (text && !el.dataset.captured) {
      el.dataset.captured = "1";
      fetch("http://localhost:8765/ingest", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ source: "x_passive", title: text, url: location.href })
      }).catch(() => {});
    }
  });
});
observer.observe(document.body, { childList: true, subtree: true });
```

**ingest_server.py:**
```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from data.db import init_db
from scrapers.base_scraper import BaseScraper

class IngestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers["Content-Length"])
        body = json.loads(self.rfile.read(length))
        scraper = BaseScraper(body.get("source", "extension"))
        scraper.store(body)
        self.send_response(200)
        self.end_headers()
    def log_message(self, *args): pass  # silence

if __name__ == "__main__":
    init_db()
    HTTPServer(("localhost", 8765), IngestHandler).serve_forever()
```

## Running All Scrapers

```python
# scrapers/run_all.py
import schedule, time
from scrapers.reddit_scraper import RedditScraper
from scrapers.hn_scraper import HNScraper
from scrapers.github_scraper import GitHubTrendingScraper
from scrapers.youtube_scraper import YouTubeScraper
from scrapers.trends_scraper import TrendsScraper
from scrapers.devto_scraper import DevToScraper

SCRAPERS = [RedditScraper, HNScraper, GitHubTrendingScraper,
            YouTubeScraper, TrendsScraper, DevToScraper]

def run_all():
    for ScraperClass in SCRAPERS:
        try:
            ScraperClass().scrape()
        except Exception as e:
            print(f"{ScraperClass.__name__} failed: {e}")

schedule.every(2).hours.do(run_all)
run_all()  # run immediately on start
while True:
    schedule.run_pending()
    time.sleep(60)
```

Run overnight: `python scrapers/run_all.py &`
