# Layer 7: Profile DNA

One-time analysis of your past posts that extracts your voice fingerprint. Build this first — both the scoring brain (relevance signal) and the voice writer use it.

## What Profile DNA Contains

```python
{
    "top_performing_formats": ["short_take", "tactical_playbook", "contrarian"],
    "best_hooks": [
        "X things I learned after...",
        "Nobody talks about...",
        "I spent 3 months on X. Here's what actually happened:",
    ],
    "peak_engagement_pillars": ["Python", "AI tools", "developer productivity", "LLMs"],
    "avg_post_length": 187,            # characters for Twitter
    "max_uppercase_ratio": 0.06,       # 6% of chars are uppercase
    "high_engagement_threshold": 150,  # likes that qualify as "high engagement"
    "voice_markers": [
        "here's the thing",
        "most people don't realize",
        "this is underrated",
    ]
}
```

## Collecting Past Posts

**Option A: Twitter/X API** (most accurate, requires paid access)

```python
import tweepy

client = tweepy.Client(bearer_token=os.environ["TWITTER_BEARER_TOKEN"])

def fetch_user_tweets(username: str, max_results: int = 500) -> list[dict]:
    user = client.get_user(username=username)
    tweets = client.get_users_tweets(
        id=user.data.id,
        max_results=min(max_results, 100),
        tweet_fields=["public_metrics", "created_at", "text"],
        exclude=["retweets", "replies"]
    )
    results = []
    for t in (tweets.data or []):
        m = t.public_metrics
        results.append({
            "text": t.text,
            "likes": m["like_count"],
            "retweets": m["retweet_count"],
            "replies": m["reply_count"],
            "impressions": m.get("impression_count", 0),
            "created_at": str(t.created_at),
        })
    return results
```

**Option B: Manual export** (free — always works)

Go to your Twitter/X settings → "Download archive" → extract `data/tweets.js`. Then:

```python
import json, re

def load_from_archive(archive_path: str = "data/tweets.js") -> list[dict]:
    with open(archive_path) as f:
        raw = f.read()
    # Archive file starts with: window.YTD.tweets.part0 = [...]
    json_str = re.sub(r"^window\.\w+\.part\d+\s*=\s*", "", raw.strip())
    tweets_raw = json.loads(json_str)
    results = []
    for item in tweets_raw:
        t = item.get("tweet", item)
        results.append({
            "text": t.get("full_text", ""),
            "likes": int(t.get("favorite_count", 0)),
            "retweets": int(t.get("retweet_count", 0)),
            "replies": 0,
            "created_at": t.get("created_at", ""),
        })
    return results
```

**Option C: LinkedIn export** (free, ~72hr processing)

Settings → Data Privacy → Get a copy of your data → download posts CSV.

## Analysis

```python
# ai/profile_analyzer.py
import json
import re
import sqlite3
from collections import Counter
from anthropic import Anthropic

client = Anthropic()
DB_PATH = "data/content_engine.db"

FORMATS = ["short_take", "tactical_playbook", "qt_contrast",
           "contrarian", "resource_drop", "proof_post"]


def classify_format(text: str) -> str:
    text_lower = text.lower()
    if re.match(r"^\d+\.", text_lower) or "\n1." in text:
        return "tactical_playbook"
    if any(w in text_lower for w in ["everyone thinks", "most people", "wrong about", "unpopular"]):
        return "contrarian"
    if any(w in text_lower for w in ["here are", "top ", "best ", "→"]):
        return "resource_drop"
    if re.match(r"^(i |after |spent |built )", text_lower):
        return "proof_post"
    return "short_take"


def extract_hook(text: str) -> str:
    """First line is the hook."""
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    return lines[0] if lines else ""


def extract_content_pillars(tweets: list[dict], top_n: int = 8) -> list[str]:
    """Use Claude to identify recurring content themes from top posts."""
    top = sorted(tweets, key=lambda t: t["likes"], reverse=True)[:50]
    sample = "\n---\n".join(t["text"] for t in top[:20])

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[{
            "role": "user",
            "content": (
                f"List the {top_n} main content themes/topics in these posts. "
                "Return only a JSON array of short phrases (2-4 words each).\n\n"
                f"{sample}"
            )
        }]
    )
    try:
        text = response.content[0].text.strip()
        # Extract JSON array from response
        match = re.search(r"\[.*?\]", text, re.DOTALL)
        return json.loads(match.group()) if match else []
    except Exception:
        return []


def extract_voice_markers(tweets: list[dict]) -> list[str]:
    """Use Claude to identify recurring phrases unique to this writer."""
    top = sorted(tweets, key=lambda t: t["likes"], reverse=True)[:30]
    sample = "\n---\n".join(t["text"] for t in top[:15])

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[{
            "role": "user",
            "content": (
                "What phrases, sentence patterns, or verbal tics does this writer repeat? "
                "Return only a JSON array of 5-8 short examples.\n\n"
                f"{sample}"
            )
        }]
    )
    try:
        text = response.content[0].text.strip()
        match = re.search(r"\[.*?\]", text, re.DOTALL)
        return json.loads(match.group()) if match else []
    except Exception:
        return []


def build_profile_dna(tweets: list[dict]) -> dict:
    """Build full profile DNA from a list of past tweets."""
    if not tweets:
        raise ValueError("No tweets provided. Fetch past posts first.")

    # Filter out retweets and very short posts
    posts = [t for t in tweets if len(t["text"]) > 40 and not t["text"].startswith("RT ")]

    # Engagement stats
    likes = [t["likes"] for t in posts]
    avg_length = int(sum(len(t["text"]) for t in posts) / max(len(posts), 1))
    high_threshold = sorted(likes, reverse=True)[max(0, len(likes)//10)]  # top 10%

    # Format performance
    format_counter = Counter()
    high_eng = [t for t in posts if t["likes"] >= high_threshold]
    for t in high_eng:
        format_counter[classify_format(t["text"])] += 1
    top_formats = [f for f, _ in format_counter.most_common(3)]
    if not top_formats:
        top_formats = ["short_take"]

    # Hook patterns from high-engagement posts
    hooks = [extract_hook(t["text"]) for t in high_eng[:20] if extract_hook(t["text"])]

    # Uppercase ratio
    all_text = " ".join(t["text"] for t in posts[:100])
    alpha_chars = [c for c in all_text if c.isalpha()]
    uppercase_ratio = sum(1 for c in alpha_chars if c.isupper()) / max(len(alpha_chars), 1)

    # Content pillars and voice markers via Claude
    pillars = extract_content_pillars(posts)
    voice_markers = extract_voice_markers(posts)

    dna = {
        "top_performing_formats": top_formats,
        "best_hooks": hooks[:10],
        "peak_engagement_pillars": pillars,
        "avg_post_length": avg_length,
        "max_uppercase_ratio": round(uppercase_ratio + 0.02, 3),  # small buffer
        "high_engagement_threshold": int(high_threshold),
        "voice_markers": voice_markers,
        "built_at": __import__("datetime").datetime.utcnow().isoformat(),
        "posts_analyzed": len(posts),
    }
    return dna


def save_dna(dna: dict, db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO profile_dna (dna_json) VALUES (?)",
        (json.dumps(dna),)
    )
    conn.commit()
    conn.close()


def load_dna(db_path: str = DB_PATH) -> dict:
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT dna_json FROM profile_dna ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return json.loads(row[0]) if row else {}
```

## Running Profile DNA Setup

One-time setup (run before anything else):

```python
# setup_dna.py — run once
from ai.profile_analyzer import build_profile_dna, save_dna, load_from_archive
from data.db import init_db

init_db()

# Load from Twitter archive (Option B — free)
tweets = load_from_archive("data/tweets.js")
print(f"Loaded {len(tweets)} tweets")

dna = build_profile_dna(tweets)
print(f"Analyzed {dna['posts_analyzed']} posts")
print(f"Content pillars: {dna['peak_engagement_pillars']}")
print(f"Top formats: {dna['top_performing_formats']}")

save_dna(dna)
print("Profile DNA saved.")
```

Run: `python setup_dna.py`

## When to Rebuild DNA

- When your audience or niche changes significantly
- After a major pivot in content topic
- Every 6 months if the system feels misaligned

Rebuilding is just re-running `setup_dna.py` with fresh tweets. The new DNA replaces the old one.

## Gotchas

- **Twitter archive takes ~24 hours to generate.** Request it before setting up the rest of the system.
- **claude-haiku for pillar/marker extraction** keeps costs low — this runs once, not per post.
- **Minimum ~50 posts for reliable DNA.** Fewer than that and the pattern analysis is too noisy. Pad with LinkedIn posts if needed.
- **Don't hardcode DNA.** Always load from the DB with `load_dna()`. Hardcoded DNA won't update when you rebuild.
- **`max_uppercase_ratio` buffer.** Add `+0.02` to the measured ratio as a voice guardian buffer, so normal variation doesn't trigger rewrites.
