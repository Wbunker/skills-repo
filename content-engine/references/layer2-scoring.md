# Layer 2: Scoring Brain

Filters 2,000+ scraped topics down to the top 10 using 5 weighted signals. The weights start at defaults and are retuned weekly by Layer 6.

## Signal Weights

| Signal | Default Weight | What it measures |
|--------|---------------|-----------------|
| velocity | 25% | How fast engagement is growing (delta) |
| virality | 25% | Shares + comments ratio |
| freshness | 20% | How recent the topic is |
| relevance | 20% | Match to your profile DNA content pillars |
| uniqueness | 10% | How novel vs. already-posted topics |

Velocity + virality = 50% of score. Trending *right now* beats just popular.

## Implementation

```python
# ai/ranker.py
import sqlite3
import json
from datetime import datetime, timedelta
from data.db import init_db

def load_profile_dna(conn) -> dict:
    row = conn.execute(
        "SELECT dna_json FROM profile_dna ORDER BY id DESC LIMIT 1"
    ).fetchone()
    return json.loads(row[0]) if row else {}

def load_weights(conn) -> dict:
    row = conn.execute(
        "SELECT freshness, velocity, virality, relevance, uniqueness FROM signal_weights WHERE id=1"
    ).fetchone()
    if row:
        return dict(zip(["freshness","velocity","virality","relevance","uniqueness"], row))
    return {"freshness":0.20,"velocity":0.25,"virality":0.25,"relevance":0.20,"uniqueness":0.10}

def calculate_freshness(timestamp_str: str) -> float:
    """Score 0-10: 10 = within 1 hour, 0 = older than 48 hours."""
    try:
        ts = datetime.fromisoformat(timestamp_str)
        age_hours = (datetime.utcnow() - ts).total_seconds() / 3600
        if age_hours < 1:
            return 10.0
        elif age_hours < 6:
            return 8.0
        elif age_hours < 12:
            return 6.0
        elif age_hours < 24:
            return 4.0
        elif age_hours < 48:
            return 2.0
        return 0.0
    except Exception:
        return 3.0

def calculate_velocity(engagement_delta: int) -> float:
    """Score 0-10 based on engagement delta (points gained recently)."""
    if engagement_delta >= 1000: return 10.0
    elif engagement_delta >= 500: return 8.0
    elif engagement_delta >= 200: return 6.0
    elif engagement_delta >= 100: return 4.0
    elif engagement_delta >= 50:  return 2.0
    return 1.0

def calculate_virality(shares: int, comments: int) -> float:
    """Score 0-10 based on shares + weighted comments."""
    combined = shares + (comments * 0.5)
    if combined >= 500: return 10.0
    elif combined >= 200: return 8.0
    elif combined >= 100: return 6.0
    elif combined >= 50:  return 4.0
    elif combined >= 20:  return 2.0
    return 1.0

def calculate_relevance(title: str, profile_dna: dict) -> float:
    """Score 0-10 based on keyword overlap with your content pillars."""
    if not profile_dna:
        return 5.0  # neutral if no DNA yet
    pillars = profile_dna.get("peak_engagement_pillars", [])
    if not pillars:
        return 5.0
    title_lower = title.lower()
    matches = sum(1 for pillar in pillars if pillar.lower() in title_lower)
    return min(10.0, matches * 3.0 + 1.0)

def calculate_uniqueness(title: str, conn) -> float:
    """Score 0-10: lower if similar topics were recently approved."""
    recent = conn.execute("""
        SELECT title FROM topics
        WHERE action = 'approve'
        AND timestamp > datetime('now', '-7 days')
    """).fetchall()
    if not recent:
        return 8.0
    title_words = set(title.lower().split())
    for (past_title,) in recent:
        past_words = set(past_title.lower().split())
        overlap = len(title_words & past_words) / max(len(title_words), 1)
        if overlap > 0.6:
            return 2.0  # very similar to something you already approved
    return 8.0

def score_topic(topic: dict, profile_dna: dict, weights: dict, conn) -> float:
    raw = {
        "freshness":  calculate_freshness(topic["timestamp"]),
        "velocity":   calculate_velocity(topic.get("engagement_delta", 0)),
        "virality":   calculate_virality(topic.get("shares", 0), topic.get("comments", 0)),
        "relevance":  calculate_relevance(topic["title"], profile_dna),
        "uniqueness": calculate_uniqueness(topic["title"], conn),
    }
    total = sum(raw[k] * weights[k] for k in raw)

    # Late bloomer rule: velocity >= 8 gets a floor of 7.0
    if raw["velocity"] >= 8:
        total = max(total, 7.0)

    return round(total, 2)

def score_all_unprocessed():
    conn = init_db()
    profile_dna = load_profile_dna(conn)
    weights = load_weights(conn)

    unprocessed = conn.execute("""
        SELECT id, source, title, url, engagement, engagement_delta,
               shares, comments, timestamp
        FROM topics WHERE processed = 0
    """).fetchall()

    cols = ["id","source","title","url","engagement","engagement_delta",
            "shares","comments","timestamp"]
    for row in unprocessed:
        topic = dict(zip(cols, row))
        score = score_topic(topic, profile_dna, weights, conn)
        conn.execute(
            "UPDATE topics SET score=?, processed=1 WHERE id=?",
            (score, topic["id"])
        )
    conn.commit()
    conn.close()

def get_top_n(n=10, db_path="data/content_engine.db") -> list[dict]:
    """Return top N scored topics not yet actioned."""
    conn = sqlite3.connect(db_path)
    rows = conn.execute("""
        SELECT id, source, title, url, score, engagement, timestamp
        FROM topics
        WHERE processed = 1 AND action IS NULL AND score IS NOT NULL
        ORDER BY score DESC
        LIMIT ?
    """, (n,)).fetchall()
    conn.close()
    cols = ["id","source","title","url","score","engagement","timestamp"]
    return [dict(zip(cols, r)) for r in rows]
```

## Late Bloomer Rule

```python
# Any topic with velocity >= 8 gets a minimum score of 7.0
# This surfaces stories about to explode before they're widely covered
if raw["velocity"] >= 8:
    total = max(total, 7.0)
```

This catches early-stage viral content even if freshness or relevance are low.

## Running the Scorer

```python
# In your main pipeline or scheduled job:
from ai.ranker import score_all_unprocessed, get_top_n

score_all_unprocessed()
top_topics = get_top_n(10)
```

Run after scrapers complete — scores all unprocessed rows, then the dashboard fetches top 10.
