---
name: content-engine
description: "Build and operate a 7-layer automated content creation system that scrapes 9 platforms, scores topics with a weighted signal brain, writes drafts in your voice using Claude API, and self-improves weekly from your approve/decline decisions. Use when a user wants to automate social media content research, draft generation, voice matching, or build a personal content pipeline that reduces daily effort to 10 minutes. Stack: Python + SQLite + Streamlit + Claude API (~$15/month)."
---

# Content Engine

A self-improving content pipeline: scrape → score → draft in your voice → review in 10 min/day → learn from decisions.

## Architecture

```
/content-engine
├── scrapers/              # Layer 1: 9 platform scrapers
├── extension/             # Browser extension (X, LinkedIn, Reddit passive capture)
├── ai/
│   ├── ranker.py          # Layer 2: 5-signal scoring brain
│   ├── content_writer.py  # Layer 3: voice DNA writer
│   ├── profile_analyzer.py # Layer 7: profile DNA builder
│   └── sentiment_analyzer.py
├── publisher/             # Layer 5: export + time slots
├── gui/dashboard.py       # Layer 4: Streamlit command center
├── ingest_server.py       # localhost server for Chrome extension
└── data/content_engine.db # SQLite — everything stored locally
```

## Build Order

Build layers in this sequence (each depends on the previous):

| Step | Layer | What it does | Reference |
|------|-------|-------------|-----------|
| 1 | Layer 7 | Profile DNA — analyze past posts for voice/format patterns | [layer7-profile-dna.md](references/layer7-profile-dna.md) |
| 2 | Layer 1 | Research engine — scrape 9 platforms into SQLite | [layer1-scrapers.md](references/layer1-scrapers.md) |
| 3 | Layer 2 | Scoring brain — 5 weighted signals, top 10 filter | [layer2-scoring.md](references/layer2-scoring.md) |
| 4 | Layer 3 | Voice DNA writer — 6 formats + voice guardian | [layer3-voice-dna.md](references/layer3-voice-dna.md) |
| 5 | Layer 4 | Streamlit dashboard — approve/decline review queue | [layer4-dashboard.md](references/layer4-dashboard.md) |
| 6 | Layer 5 | Publisher — export .txt for manual posting | [layer5-publisher.md](references/layer5-publisher.md) |
| 7 | Layer 6 | Self-learning loop — weekly retune from decisions | [layer6-self-learning.md](references/layer6-self-learning.md) |

Start with Layer 7 because profile DNA feeds both relevance scoring (Layer 2) and voice writing (Layer 3).

## Daily Workflow

```
Wake up → open http://localhost:8501
→ Review queue: 10 topics, 10 minutes
→ Approve 3–5, decline rest (add note when declining — this trains the system)
→ Pick time slots for approved posts
→ Export .txt → copy/paste → post manually
→ Done
```

## Setup

```bash
mkdir content-engine && cd content-engine
pip install anthropic streamlit praw tweepy pytrends \
    requests beautifulsoup4 sentence-transformers schedule
```

Environment variables:
```bash
ANTHROPIC_API_KEY=sk-ant-...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=content-engine/1.0
# Twitter/X bearer token optional — free tier very limited
TWITTER_BEARER_TOKEN=...
```

## Database Schema

Initialize once on first run:

```python
# data/db.py
import sqlite3

def init_db(path="data/content_engine.db"):
    conn = sqlite3.connect(path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY,
            source TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT UNIQUE,
            engagement INTEGER DEFAULT 0,
            engagement_delta INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            processed BOOLEAN DEFAULT 0,
            score REAL,
            suggested_format TEXT,
            draft TEXT,
            linkedin_draft TEXT,
            action TEXT,          -- 'approve' | 'decline' | NULL
            decline_note TEXT,
            time_slot TEXT,
            exported BOOLEAN DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS signal_weights (
            id INTEGER PRIMARY KEY,
            freshness REAL DEFAULT 0.20,
            velocity REAL DEFAULT 0.25,
            virality REAL DEFAULT 0.25,
            relevance REAL DEFAULT 0.20,
            uniqueness REAL DEFAULT 0.10,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS profile_dna (
            id INTEGER PRIMARY KEY,
            dna_json TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        INSERT OR IGNORE INTO signal_weights (id) VALUES (1);
        CREATE INDEX IF NOT EXISTS idx_processed ON topics(processed);
        CREATE INDEX IF NOT EXISTS idx_score ON topics(score DESC);
        CREATE INDEX IF NOT EXISTS idx_action ON topics(action);
    """)
    conn.commit()
    return conn
```

## Gotchas

- **Never auto-post.** Manual copy/paste is intentional — automated posting risks account flags. The publisher exports .txt only.
- **Build profile DNA first.** Relevance scoring and voice writing both require `profile_dna` in the DB before they work correctly.
- **pytrends is unreliable.** Google Trends scraping breaks frequently; wrap every call in try/except with silent fallback. Consider SerpAPI for production.
- **Twitter/X API costs money.** Free tier is extremely limited ($200/month for meaningful volume). Prioritize Reddit, HN, GitHub Trending, and YouTube for free reliable data; add X only if budget allows.
- **Voice guardian runs before any draft is surfaced.** If it fails, the system rewrites automatically — the user should never see corporate language or hashtags.
- **Weekly retune needs sufficient data.** Run retuning only when you have 20+ decisions in the window. Too few decisions produces noisy weight updates.
- **SQLite `url UNIQUE` constraint deduplicates for free.** Use `INSERT OR IGNORE` in every scraper.
- **`st.rerun()` after every approve/decline.** Otherwise Streamlit shows stale state until next manual refresh.
- **Profile DNA must be rebuilt when your audience or content focus changes.** It's not automatically updated — it's a one-time snapshot you refresh manually.
