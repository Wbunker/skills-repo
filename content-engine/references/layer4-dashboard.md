# Layer 4: Streamlit Dashboard

A dark-themed command center at `http://localhost:8501` with 5 tabs. The review queue works like a swipe interface — approve or decline, one topic at a time.

## Setup

```bash
mkdir -p .streamlit
cat > .streamlit/config.toml << 'EOF'
[theme]
base = "dark"
primaryColor = "#FF6B35"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#1E2130"
textColor = "#FAFAFA"

[server]
port = 8501
headless = true
EOF
```

Run: `streamlit run gui/dashboard.py`

## Full Dashboard

```python
# gui/dashboard.py
import streamlit as st
import sqlite3
import json
import pandas as pd
from datetime import datetime

DB_PATH = "data/content_engine.db"

st.set_page_config(
    page_title="Content Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def get_conn():
    return sqlite3.connect(DB_PATH)


# ── Tabs ────────────────────────────────────────────────────────────────────
tab_queue, tab_approved, tab_analytics, tab_exports, tab_settings = st.tabs([
    "Review Queue", "Approved", "Analytics", "Exports", "Settings"
])


# ── Tab 1: Review Queue ──────────────────────────────────────────────────────
with tab_queue:
    st.title("Review Queue")
    conn = get_conn()
    topics = conn.execute("""
        SELECT id, source, title, url, score, suggested_format, draft, linkedin_draft
        FROM topics
        WHERE processed = 1 AND action IS NULL AND draft IS NOT NULL
        ORDER BY score DESC
        LIMIT 10
    """).fetchall()
    conn.close()

    if not topics:
        st.info("Queue empty. Run the pipeline to fetch and score new topics.")
    else:
        st.caption(f"{len(topics)} topics to review")
        for row in topics:
            tid, source, title, url, score, fmt, draft, li_draft = row
            with st.container():
                col_meta, col_score = st.columns([4, 1])
                with col_meta:
                    st.markdown(f"### {title}")
                    st.caption(f"**Source:** {source}  ·  **Format:** {fmt or '—'}  ·  [link]({url})")
                with col_score:
                    color = "green" if score >= 7 else "orange" if score >= 5 else "red"
                    st.markdown(
                        f"<h2 style='color:{color};text-align:center'>{score:.1f}</h2>",
                        unsafe_allow_html=True
                    )

                tab_tw, tab_li = st.tabs(["Twitter/X", "LinkedIn"])
                with tab_tw:
                    st.markdown(f"```\n{draft or 'No draft yet'}\n```")
                with tab_li:
                    st.markdown(f"```\n{li_draft or 'No LinkedIn draft yet'}\n```")

                col1, col2, col3 = st.columns([1, 1, 3])
                with col1:
                    if st.button("Approve", key=f"approve_{tid}", type="primary"):
                        _approve_topic(tid)
                        st.rerun()
                with col2:
                    if st.button("Decline", key=f"decline_{tid}"):
                        st.session_state[f"declining_{tid}"] = True

                if st.session_state.get(f"declining_{tid}"):
                    with col3:
                        reason = st.text_input(
                            "Why? (trains the system)", key=f"reason_{tid}"
                        )
                        if st.button("Confirm decline", key=f"confirm_{tid}"):
                            _decline_topic(tid, reason)
                            del st.session_state[f"declining_{tid}"]
                            st.rerun()

                st.divider()


# ── Tab 2: Approved ──────────────────────────────────────────────────────────
with tab_approved:
    st.title("Approved Posts")
    conn = get_conn()
    approved = conn.execute("""
        SELECT id, title, draft, time_slot, exported, timestamp
        FROM topics WHERE action = 'approve'
        ORDER BY timestamp DESC LIMIT 50
    """).fetchall()
    conn.close()

    for tid, title, draft, slot, exported, ts in approved:
        status = "Exported" if exported else "Pending export"
        with st.expander(f"{title[:60]}... | {slot or 'No slot'} | {status}"):
            st.text(draft)
            if not exported:
                slot_choice = st.selectbox(
                    "Time slot", ["8:00 AM", "12:00 PM", "5:00 PM"],
                    key=f"slot_{tid}"
                )
                if st.button("Export", key=f"export_{tid}"):
                    _export_topic(tid, slot_choice, draft)
                    st.rerun()


# ── Tab 3: Analytics ─────────────────────────────────────────────────────────
with tab_analytics:
    st.title("Analytics")
    conn = get_conn()
    df = pd.read_sql("""
        SELECT source, action, score, timestamp
        FROM topics WHERE action IS NOT NULL
    """, conn)
    conn.close()

    if df.empty:
        st.info("No decisions yet. Start approving and declining to see analytics.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Approved", len(df[df.action == "approve"]))
        col2.metric("Declined", len(df[df.action == "decline"]))
        col3.metric("Approval rate",
                    f"{len(df[df.action=='approve']) / len(df) * 100:.0f}%")

        st.subheader("Approvals by source")
        st.bar_chart(df[df.action == "approve"].groupby("source").size())

        st.subheader("Score distribution")
        st.histogram_chart = st.bar_chart(
            df.groupby(df["score"].round(0))["action"].count()
        )


# ── Tab 4: Exports ───────────────────────────────────────────────────────────
with tab_exports:
    st.title("Ready to Post")
    import os, glob
    exports = sorted(glob.glob("exports/*.txt"), reverse=True)
    if not exports:
        st.info("No exports yet. Approve posts and export them from the Approved tab.")
    for path in exports[:20]:
        fname = os.path.basename(path)
        with open(path) as f:
            content = f.read()
        with st.expander(fname):
            st.code(content)


# ── Tab 5: Settings ───────────────────────────────────────────────────────────
with tab_settings:
    st.title("Settings")
    conn = get_conn()
    w = conn.execute(
        "SELECT freshness, velocity, virality, relevance, uniqueness FROM signal_weights WHERE id=1"
    ).fetchone()
    conn.close()

    st.subheader("Current signal weights")
    if w:
        cols = st.columns(5)
        labels = ["freshness","velocity","virality","relevance","uniqueness"]
        for col, label, val in zip(cols, labels, w):
            col.metric(label, f"{val:.0%}")
    st.caption("Weights are updated automatically by the weekly self-learning loop.")

    if st.button("Run pipeline now"):
        import subprocess
        subprocess.Popen(["python", "pipeline.py"])
        st.success("Pipeline started in background.")


# ── Helpers ──────────────────────────────────────────────────────────────────
def _approve_topic(tid: int):
    conn = get_conn()
    conn.execute(
        "UPDATE topics SET action='approve' WHERE id=?", (tid,)
    )
    conn.commit()
    conn.close()


def _decline_topic(tid: int, reason: str):
    conn = get_conn()
    conn.execute(
        "UPDATE topics SET action='decline', decline_note=? WHERE id=?",
        (reason, tid)
    )
    conn.commit()
    conn.close()


def _export_topic(tid: int, slot: str, draft: str):
    import os
    os.makedirs("exports", exist_ok=True)
    conn = get_conn()
    row = conn.execute(
        "SELECT title, linkedin_draft FROM topics WHERE id=?", (tid,)
    ).fetchone()
    title, li_draft = row if row else ("", "")
    filename = f"exports/post_{tid}_{slot.replace(':', '').replace(' ', '')}.txt"
    with open(filename, "w") as f:
        f.write(f"TIME SLOT: {slot}\n")
        f.write(f"TOPIC: {title}\n\n")
        f.write("TWITTER/X:\n\n")
        f.write(draft)
        f.write("\n\n---\n\nLINKEDIN:\n\n")
        f.write(li_draft or "(no LinkedIn draft)")
        f.write("\n")
    conn.execute(
        "UPDATE topics SET time_slot=?, exported=1 WHERE id=?", (slot, tid)
    )
    conn.commit()
    conn.close()
```

## Gotchas

- **`get_conn()` instead of a shared connection.** Streamlit reruns the entire script on interaction — a module-level SQLite connection gets serialized across threads and breaks. Open/close per function.
- **`st.rerun()` must be called after any DB mutation.** Without it, the UI shows stale data until the user manually refreshes.
- **Session state for multi-step decline flow.** The "Why?" text input only shows after clicking Decline. Use `st.session_state` to track which topics are in "confirming decline" state.
- **`subprocess.Popen` for running pipeline.** Don't block the Streamlit thread with long-running operations. Fire and forget, or use a task queue.
