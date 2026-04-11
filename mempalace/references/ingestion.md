# MemPalace — Ingesting Conversations

## The Core Command

```bash
mempalace mine <path>                              # mine code projects / docs
mempalace mine <path> --mode convos                # mine chat exports
mempalace mine <path> --mode convos --extract general  # + preference/decision extraction
```

## Supported Conversation Formats

MemPalace auto-detects and normalizes these formats:

| Format | File type | Source |
|--------|-----------|--------|
| Claude AI export | JSON | claude.ai → Export data |
| ChatGPT export | `conversations.json` | ChatGPT → Settings → Export |
| Claude Code sessions | JSONL | `~/.claude/projects/` |
| OpenAI Codex | JSONL | Codex export |
| Slack export | JSON | Slack workspace export |
| Plain text transcripts | `.txt` | Any chat copy-paste |

All formats are normalized to the same internal structure before chunking.

## How Chunking Works

MemPalace splits conversations into "drawers" (retrievable chunks):

**Exchange-pair chunking (preferred)**:
- Triggered when 3+ quote markers (`>`) are found in the file
- One user turn + one AI response = one drawer
- Preserves the Q&A context that makes retrieval meaningful

**Fallback chunking** (when exchange-pair doesn't apply):
1. Paragraph chunks (split on double newlines)
2. 25-line segments (if paragraphs are sparse)

**Minimums and limits**:
- Minimum chunk: 30 characters — shorter chunks are dropped silently
- Files over 10 MB are skipped — split first with `mempalace split`

## Splitting Large Exports

If your chat export is a single large file with multiple sessions concatenated:

```bash
mempalace split ~/chats/big-export.json   # splits into per-session files
mempalace mine ~/chats/                   # then mine the directory
```

## Room Auto-Classification

Each drawer is automatically classified into a room by `room_detector_local.py`:

1. Folder path matching (e.g., `auth/` → authentication room)
2. Filename keyword matching
3. Content keyword scoring (70+ patterns)
4. Fallback to a generic room

Room examples auto-detected: `authentication`, `graphql-migration`, `ci-pipeline`, `database-schema`, `api-design`, `debugging`, `planning`, `architecture`.

To override auto-classification, use `mempalace_add_drawer` MCP tool with explicit wing/room metadata.

## General Extraction (`--extract general`)

When `--extract general` is passed, MemPalace also runs `general_extractor.py` which classifies and indexes:

- **Decisions** — explicit choices made
- **Preferences** — user preferences (16 regex patterns)
- **Milestones** — significant achievements
- **Problems** — documented issues
- **Emotional context** — sentiment markers

Extracted items are stored as synthetic documents in a dedicated **preference wing** — making them first-class searchable entities alongside raw conversation text.

## Mining Code Projects and Docs

Without `--mode convos`, `mempalace mine` treats the path as a project and indexes:
- Source code files
- Markdown documentation
- README files
- Any text-based files

This lets you search your codebase with the same semantic search used for conversations.

## Checking What's Been Mined

```bash
mempalace status                  # total drawers, wing/room counts
mempalace search "your query"     # test that retrieval works
```

Or via MCP tools in Claude: `mempalace_status`, `mempalace_get_taxonomy`.

## Avoiding Duplicates

Before mining, MemPalace checks for existing content:
```bash
# Via CLI (built into mine command automatically)
mempalace mine ~/chats/ --dedupe
```

Or check manually:
```bash
# Via MCP tool
mempalace_check_duplicate  # pass content text to check before adding
```

## Batch Mining a Full Chat History

```bash
# Export ChatGPT history to ~/exports/chatgpt/
# Export Claude history to ~/exports/claude/

mempalace init ~/my-palace
export MEMPAL_DIR=~/my-palace

mempalace mine ~/exports/chatgpt/ --mode convos --extract general
mempalace mine ~/exports/claude/  --mode convos --extract general
mempalace mine ~/projects/myapp   # also index your codebase

mempalace status   # confirm drawer count
mempalace wake-up  # generate session-start context
```

## Background Auto-Mining

```bash
mempalace watch ~/chats/    # polls every 5 minutes for new files, mines automatically
```

Run in a tmux/screen session or as a system service to keep the palace continuously updated.
