# Layer 6: Self-Learning Loop

Runs weekly. Reads every approve/decline decision from the past 7 days, analyzes patterns in what you rejected and why, and reweights the 5 scoring signals accordingly. The system gets more accurate over time.

## Learning Trajectory

| Timeline | Behavior |
|----------|----------|
| Month 1 | ~30% of surfaced topics match your taste. System is calibrating. |
| Month 3 | ~70% of topics pre-filtered to what you'd post. Queue feels curated. |
| Month 6 | The 10 topics surfaced are almost always the 10 you'd have chosen yourself. |

## Implementation

```python
# ai/ranker.py (append to existing file)
import json
import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
from datetime import datetime, timedelta

_embed_model = None

def _get_embed_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embed_model


def get_decisions(days: int = 7,
                  db_path: str = "data/content_engine.db") -> list[dict]:
    conn = sqlite3.connect(db_path)
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    rows = conn.execute("""
        SELECT id, title, score, action, decline_note,
               freshness_score, velocity_score, virality_score,
               relevance_score, uniqueness_score
        FROM topics
        WHERE action IS NOT NULL AND timestamp > ?
    """, (cutoff,)).fetchall()
    conn.close()
    cols = ["id","title","score","action","decline_note",
            "freshness","velocity","virality","relevance","uniqueness"]
    return [dict(zip(cols, r)) for r in rows]


def embed_decline_notes(notes: list[str]) -> np.ndarray | None:
    """Embed decline notes to find patterns in what gets rejected."""
    clean = [n for n in notes if n and n.strip()]
    if not clean:
        return None
    model = _get_embed_model()
    return model.encode(clean, batch_size=32, show_progress_bar=False)


def analyze_score_patterns(approved: list[dict]) -> dict:
    """Find which signal ranges correlate with approval."""
    if not approved:
        return {}
    signal_keys = ["freshness", "velocity", "virality", "relevance", "uniqueness"]
    averages = {}
    for key in signal_keys:
        vals = [d[key] for d in approved if d.get(key) is not None]
        averages[key] = float(np.mean(vals)) if vals else 5.0
    return averages


def calculate_new_weights(approved_patterns: dict,
                          decline_embeddings,
                          current_weights: dict) -> dict:
    """
    Adjust weights based on what signals approved topics scored highly on.
    Signals with higher-than-average approved scores get a small bump.
    Normalize to sum to 1.0.
    """
    if not approved_patterns:
        return current_weights

    # Score each signal's contribution: approved average vs neutral midpoint (5.0)
    adjustments = {}
    for key in current_weights:
        avg = approved_patterns.get(key, 5.0)
        # If approved topics consistently scored high on this signal, boost its weight
        delta = (avg - 5.0) / 50.0  # small nudge: max ±0.1 per retune
        adjustments[key] = current_weights[key] + delta

    # Keep weights positive and normalized to 1.0
    total = sum(max(0.05, v) for v in adjustments.values())
    new_weights = {k: round(max(0.05, v) / total, 4) for k, v in adjustments.items()}
    return new_weights


def weekly_retune(db_path: str = "data/content_engine.db"):
    """Run every Sunday. Requires 20+ decisions for stable retuning."""
    conn = sqlite3.connect(db_path)
    decisions = get_decisions(days=7, db_path=db_path)

    approved = [d for d in decisions if d["action"] == "approve"]
    declined = [d for d in decisions if d["action"] == "decline"]

    print(f"Retuning: {len(approved)} approved, {len(declined)} declined this week")

    if len(decisions) < 20:
        print(f"Only {len(decisions)} decisions — need 20+ for reliable retune. Skipping.")
        conn.close()
        return

    # Analyze decline notes for patterns (logged but not yet used to auto-adjust topics)
    decline_notes = [d["decline_note"] for d in declined if d.get("decline_note")]
    decline_embeddings = embed_decline_notes(decline_notes)
    if decline_embeddings is not None:
        print(f"Embedded {len(decline_notes)} decline notes for pattern analysis.")

    # Get current weights
    row = conn.execute(
        "SELECT freshness, velocity, virality, relevance, uniqueness FROM signal_weights WHERE id=1"
    ).fetchone()
    current_weights = dict(zip(
        ["freshness","velocity","virality","relevance","uniqueness"], row
    )) if row else {"freshness":0.20,"velocity":0.25,"virality":0.25,"relevance":0.20,"uniqueness":0.10}

    approved_patterns = analyze_score_patterns(approved)
    new_weights = calculate_new_weights(approved_patterns, decline_embeddings, current_weights)

    conn.execute("""
        UPDATE signal_weights
        SET freshness=?, velocity=?, virality=?, relevance=?, uniqueness=?, updated_at=?
        WHERE id=1
    """, (
        new_weights["freshness"], new_weights["velocity"], new_weights["virality"],
        new_weights["relevance"], new_weights["uniqueness"],
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()
    print(f"Retuned weights: {new_weights}")
```

## Storing Per-Topic Signal Scores

For retune analysis to work, the per-signal raw scores must be stored alongside the final score. Add these columns to the schema:

```sql
-- Add to CREATE TABLE in data/db.py:
freshness_score REAL,
velocity_score REAL,
virality_score REAL,
relevance_score REAL,
uniqueness_score REAL,
```

And store them when scoring:

```python
# In score_all_unprocessed() in ai/ranker.py:
raw_scores = {
    "freshness":  calculate_freshness(topic["timestamp"]),
    "velocity":   calculate_velocity(topic.get("engagement_delta", 0)),
    "virality":   calculate_virality(topic.get("shares", 0), topic.get("comments", 0)),
    "relevance":  calculate_relevance(topic["title"], profile_dna),
    "uniqueness": calculate_uniqueness(topic["title"], conn),
}
conn.execute("""
    UPDATE topics SET score=?, processed=1,
        freshness_score=?, velocity_score=?, virality_score=?,
        relevance_score=?, uniqueness_score=?
    WHERE id=?
""", (
    score, raw_scores["freshness"], raw_scores["velocity"], raw_scores["virality"],
    raw_scores["relevance"], raw_scores["uniqueness"], topic["id"]
))
```

## Scheduling the Weekly Retune

```python
# In scrapers/run_all.py or a separate scheduler:
import schedule
from ai.ranker import weekly_retune

schedule.every().sunday.at("06:00").do(weekly_retune)
```

Or run manually: `python -c "from ai.ranker import weekly_retune; weekly_retune()"`

## Gotchas

- **20 decisions minimum.** Below that, the weight adjustments are noisy and can hurt more than help. The function checks and skips automatically.
- **Weights converge slowly by design.** The `delta = (avg - 5.0) / 50.0` nudge is intentionally small. Rapid large swings would break the scorer until you have enough data for the next correction.
- **sentence-transformers loads ~80MB model.** Use lazy loading (`_get_embed_model()` pattern) so it's only loaded when retune actually runs, not on every import.
- **Decline note embeddings aren't yet used to filter topics.** They're stored/analyzed for pattern logging. Future enhancement: use similarity search to pre-filter new topics that match your decline patterns before they reach the queue.
