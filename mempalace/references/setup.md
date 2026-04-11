# MemPalace — Setup and Installation

## Requirements

- Python 3.9+
- Dependencies: `chromadb >=0.5.0,<0.7` and `pyyaml >=6.0,<7`
- ~500 MB disk for ChromaDB embedding model (auto-downloaded on first use; requires internet)

## Install

```bash
pip install mempalace
```

## Initialize a Palace

A "world" is the directory that holds all your palace data (ChromaDB collection + SQLite KG).

```bash
mempalace init ~/my-palace
```

This creates:
```
~/my-palace/
  chroma/        ← ChromaDB vector store (all drawers)
  kg.sqlite      ← knowledge graph (entity relationships)
  .mempalace/    ← palace metadata and hook state
```

You can have multiple worlds (one per project, one personal, etc.).

## Connect to Claude via MCP

Add MemPalace as an MCP server so Claude can query your memories directly:

```bash
claude mcp add mempalace -- python -m mempalace.mcp_server
```

Then at the start of each Claude session, run:

```bash
mempalace wake-up
```

This loads ~170 tokens of palace context (wing list, drawer counts) so Claude knows what's stored before you start asking questions.

Or use the MCP tool directly in conversation: call `mempalace_status` to get the palace overview.

## MCP Server — Manual Start

```bash
python -m mempalace.mcp_server
```

The server runs locally on stdio transport (no port binding). Claude Code connects to it automatically after `claude mcp add`.

## Environment Variable

```bash
export MEMPAL_DIR=~/my-palace
```

Set this to make all CLI commands use your palace directory without needing to pass `--world` each time. Useful for shell profiles and automation hooks.

## Auto-Ingest Hook (optional)

MemPalace ships a pre-compact hook that automatically mines conversations when triggered by Claude Code's `/compact` command:

```bash
# Add to claude hooks config
mempal_precompact_hook.sh
```

Or use the file-watcher for background auto-mining:

```bash
mempalace watch ~/chats/   # auto-mines every 5 minutes
```

## Verify Installation

```bash
mempalace status            # should show palace stats (0 drawers on fresh install)
mempalace benchmark         # smoke-test retrieval pipeline
```

## Cost Summary

| Operation | Cost |
|-----------|------|
| `mempalace mine` (ingest) | $0 — local embeddings only |
| `mempalace search` (raw mode) | $0 |
| `mempalace search` (hybrid, no LLM) | $0 |
| Optional Haiku rerank | ~$0.001/query |
| Optional Sonnet rerank | ~$0.003/query |
| Annual cost (5 searches/day, no rerank) | ~$0/year |
| Annual cost (5 searches/day + Haiku rerank) | ~$1.80/year |

Comparison: Zep subscription ~$25+/mo; LLM-based summarization pipelines ~$507/year for similar usage.
