---
name: wiki
description: >
  Plain-Markdown personal knowledge wiki (llm-wiki pattern). Use when reading or writing
  wiki articles in wiki/notes/, updating wiki/index.md or wiki/log.md, running any
  wiki:* pipeline command (ingest, status, consolidate), or answering questions about
  wiki structure, article format, tag taxonomy, or cross-linking conventions.
  The wiki is tool-agnostic — plain .md files readable in any Markdown editor.
---

# wbunker-wiki

Will Bunker's personal knowledge wiki. Plain `.md` files — no proprietary format,
viewable in any Markdown editor (VS Code, Obsidian, iA Writer, GitHub, etc.).

**Article conventions and tag taxonomy:** See [references/article-format.md](references/article-format.md)

---

## Paths

| Path | Purpose |
|------|---------|
| `wiki/` | Wiki root (separate git repo, gitignored from mac-notebook) |
| `wiki/CLAUDE.md` | Schema: article conventions, tag taxonomy, operations |
| `wiki/index.md` | Master catalog — every article listed with one-line summary |
| `wiki/log.md` | Append-only operation log |
| `wiki/notes/` | LLM-generated wiki articles (.md files) |
| `wiki/raw/` | Gitignored — immutable source documents, stays local only |
| `wiki/raw/emails/` | Fetched Gmail messages as markdown |
| `wiki/raw/imessages/` | Fetched iMessage threads as markdown |
| `wiki/raw/processed_ids.json` | Gmail: tracks fetched/skipped IDs + last_ingest date |
| `wiki/raw/processed_messages.json` | iMessage: tracks last_ingest + per-chat last_rowid |
| `wiki/raw/contacts_cache.json` | iMessage: phone/email → display name cache |
| `wiki/scripts/` | Pipeline scripts |

---

## Scripts

Run from `wiki/scripts/` with `pyenv exec python3 <script>`:

| Script | Purpose | Key args |
|--------|---------|---------|
| `fetch_gmail.py` | Fetch Gmail → raw/emails/, update processed_ids.json | `--from YYYY-MM-DD --to YYYY-MM-DD` |
| `build_manifest.py` | Reconstruct Gmail manifest from processed_ids.json | `--from --to --stats` |
| `fetch_imessages.py` | Fetch iMessage threads → raw/imessages/, update processed_messages.json | `--from YYYY-MM-DD --to YYYY-MM-DD --stats` |
| `resolve_contacts.py` | Build/refresh contacts_cache.json from AddressBook | `[phone_or_email] --rebuild` |
| `decode_attributed_body.py` | Decode NSArchiver blobs from chat.db | `<rowid> --sample N --verify` |

All fetch scripts default `--from` to `last_ingest` from their state file (fallback: 7 days ago).

---

## Install

To install the generic wiki commands into any Claude Code project:

```bash
python3 .claude/skills/wiki/scripts/install.py [/path/to/project]
```

Copies `ingest.md`, `status.md`, `consolidate.md` from `commands/` into `.claude/commands/wiki/`
in the target project, registering them as `/wiki:ingest`, `/wiki:status`, `/wiki:consolidate`.
Accepts `--dry-run` to preview. Restart Claude Code after installing.

---

## Commands

These Claude Code slash commands run the wiki pipeline:

| Command | What it does |
|---------|-------------|
| `/wiki:ingest` | Master orchestrator — runs Gmail + iMessage in parallel, merges by domain |
| `/wiki:ingest-gmail` | Gmail only — fetch + classify + ingest |
| `/wiki:ingest-imessage` | iMessage only — fetch + classify + ingest |
| `/wiki:ingest-ai-news` | Ingest an AI news briefing into the AI Landscape section |
| `/wiki:consolidate` | Weekly lint — orphan resolution, stale flagging, cross-link audit |
| `/wiki:status` | Pipeline state, article counts, recent log |


---

## Agent Model Assignments

| Task | Model | Reason |
|------|-------|--------|
| Classify (email or thread → domain/relevance) | **haiku** | High volume, simple tagging |
| Wiki ingest per domain | **sonnet** | Synthesis + writing quality |
| Consolidate — orphan/stale check | **haiku** | Pattern matching, mechanical |
| Consolidate — article updates | **sonnet** | Cross-linking requires judgment |
| Status report | **haiku** | Read-only, no synthesis |

---

## iMessage Notes

- chat.db at `~/Library/Messages/chat.db` — requires Full Disk Access for Terminal
- Message text stored in `attributedBody` (NSArchiver blob) since macOS Ventura — `decode_attributed_body.py` handles this
- Contact resolution: AddressBook SQLite (4,737 contacts) + contacts.md (curated wins)
- Tapbacks filtered by `associated_message_type` 2000-2006
- Short-code SMS (≤6 digit handles) filtered as noise
- Minimum 5 substantive messages per thread per window to save
