# Layer 5: Publisher

Exports approved posts as `.txt` files. Never posts automatically — manual copy/paste protects accounts from automation flags.

## Design Principle

Automated posting can get accounts flagged or suspended. One bad post at the wrong moment can undo months of growth. Manual posting keeps you in control. The publisher's job is just to make copy/paste effortless.

## Export Format

Each `.txt` file contains both platform versions with clear section breaks:

```
TIME SLOT: 12:00 PM
TOPIC: Why Python type hints are actually harmful in small projects

TWITTER/X:

Type hints in Python are great.
Until they're not.

For small scripts and one-off tools, they add noise without value.
No team to communicate with. No IDE integration in a bash pipeline.

Write typed code when there's a human on the other end.

---

LINKEDIN:

I've been writing Python for 12 years and I'll say something unpopular:

Type hints are harmful in small projects.

Not because they're bad — they're excellent when you need them.
But "need" is the key word. For solo scripts, automation tools, or
one-off data transforms, type hints add visual noise without providing
the benefit they were designed for: communicating intent to teammates
and enabling IDE tooling at scale.

Rules exist for teams. Write typed code when there's a human on the other end.

When do you reach for type hints? I'm curious where you draw the line.
```

## Implementation

```python
# publisher/exporter.py
import os
import sqlite3
from datetime import datetime

TIME_SLOTS = ["8:00 AM", "12:00 PM", "5:00 PM"]
EXPORTS_DIR = "exports"


def export_topic(topic_id: int, time_slot: str,
                 db_path: str = "data/content_engine.db") -> str:
    """Export an approved topic as a .txt file. Returns file path."""
    os.makedirs(EXPORTS_DIR, exist_ok=True)

    conn = sqlite3.connect(db_path)
    row = conn.execute("""
        SELECT title, draft, linkedin_draft
        FROM topics WHERE id = ?
    """, (topic_id,)).fetchone()

    if not row:
        conn.close()
        raise ValueError(f"Topic {topic_id} not found")

    title, twitter_draft, linkedin_draft = row

    safe_slot = time_slot.replace(":", "").replace(" ", "")
    filename = f"{EXPORTS_DIR}/post_{topic_id}_{safe_slot}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"TIME SLOT: {time_slot}\n")
        f.write(f"TOPIC: {title}\n\n")
        f.write("TWITTER/X:\n\n")
        f.write(twitter_draft or "(no draft)")
        f.write("\n\n---\n\nLINKEDIN:\n\n")
        f.write(linkedin_draft or "(no LinkedIn draft)")
        f.write("\n")

    conn.execute("""
        UPDATE topics
        SET time_slot = ?, exported = 1, exported_at = ?
        WHERE id = ?
    """, (time_slot, datetime.utcnow().isoformat(), topic_id))
    conn.commit()
    conn.close()

    return filename


def export_all_pending(db_path: str = "data/content_engine.db") -> list[str]:
    """Export all approved but not-yet-exported topics, distributing across time slots."""
    conn = sqlite3.connect(db_path)
    pending = conn.execute("""
        SELECT id FROM topics
        WHERE action = 'approve' AND exported = 0
        ORDER BY score DESC
    """).fetchall()
    conn.close()

    exported = []
    for i, (topic_id,) in enumerate(pending):
        slot = TIME_SLOTS[i % len(TIME_SLOTS)]
        path = export_topic(topic_id, slot, db_path)
        exported.append(path)

    return exported


def list_exports() -> list[dict]:
    """Return all .txt files in exports/, sorted newest first."""
    import glob
    files = sorted(glob.glob(f"{EXPORTS_DIR}/*.txt"), reverse=True)
    result = []
    for path in files:
        stat = os.stat(path)
        result.append({
            "path": path,
            "filename": os.path.basename(path),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        })
    return result
```

## Adding `exported_at` to Schema

If you want to track when posts were exported, add this column during `init_db`:

```sql
ALTER TABLE topics ADD COLUMN exported_at DATETIME;
```

Or include it in the initial `CREATE TABLE` in `data/db.py`.

## Scheduled Export (Optional)

If you prefer exports to be generated automatically after each scoring run:

```python
# In pipeline.py
from publisher.exporter import export_all_pending
export_all_pending()
print(f"Exported posts to {EXPORTS_DIR}/")
```

## Gotchas

- **Never add auto-posting.** No Twitter API calls, no LinkedIn API calls from the publisher. The `.txt` file is the final artifact.
- **LinkedIn versions need ~5x more content.** Ensure `layer3-voice-dna.md` uses `char_limit=1300` for LinkedIn drafts.
- **Slot rotation.** When auto-assigning slots across multiple approved posts, rotate through `["8:00 AM", "12:00 PM", "5:00 PM"]` so you don't queue 5 posts all at 8 AM.
- **Old exports accumulate.** Add a cleanup job or prune manually — files older than 30 days can be deleted safely.
