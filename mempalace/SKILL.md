---
name: mempalace
description: MemPalace setup, ingestion, search, and knowledge graph expertise. Use when the user wants to install or configure MemPalace, mine conversation history into a palace, query memories via CLI or MCP, understand the palace hierarchy (wings/rooms/drawers), work with the knowledge graph, use the 19 MCP tools with Claude, or understand retrieval accuracy and pipeline stages. MemPalace is a local AI memory system that stores raw verbatim conversation text and retrieves it via ChromaDB embeddings — achieving 96.6% R@5 on LongMemEval with zero API calls.
---

# MemPalace Expert

MemPalace (by Milla Jovovich and Ben Sigman) is a local AI memory system with a radical thesis: **store conversations verbatim, let embeddings do the retrieval**. No summarization, no LLM in the write path, zero cloud costs.

GitHub: https://github.com/milla-jovovich/mempalace

## Core Thesis

Every summarization step loses information. Raw text + good embeddings beats LLM-extracted memory because the full signal stays intact. Result: **96.6% R@5** on LongMemEval at $0/query (vs Mastra 94.87%, Supermemory 85%, Mem0 30–45%).

## Quick Reference — Load by Task

| Task | Reference |
|------|-----------|
| Install, initialize a palace, MCP setup for Claude | [setup.md](references/setup.md) |
| Mine chat exports, supported formats, chunking, CLI | [ingestion.md](references/ingestion.md) |
| Wings, rooms, drawers, closets, halls, tunnels, palace graph | [palace-architecture.md](references/palace-architecture.md) |
| All 19 MCP tools — names, parameters, what each does | [mcp-tools.md](references/mcp-tools.md) |
| 5-stage hybrid retrieval, benchmark numbers, R@5 explained | [retrieval-pipeline.md](references/retrieval-pipeline.md) |
| SQLite knowledge graph, entity detection, temporal queries, preference extraction | [knowledge-graph.md](references/knowledge-graph.md) |
| AAAK lossy format — what it is, when useful, current limitations | [aaak-format.md](references/aaak-format.md) |

## Architecture at a Glance

```
Conversations (raw verbatim)
         │
         ▼ mempalace mine
  ┌──────────────────┐
  │   ChromaDB       │  ← semantic vector search (embeddings)
  │   (drawers)      │
  └──────────────────┘
         │
         ▼ hybrid retrieval
  keyword boost → temporal boost → preference matching → [optional LLM rerank]
         │
  ┌──────────────────┐
  │   SQLite KG      │  ← entity relationships + temporal validity
  └──────────────────┘
         │
    palace graph (BFS over rooms/wings for multi-hop)
```

## Retrieval Accuracy (April 2026)

| Mode | R@5 | API cost |
|------|-----|---------|
| Raw ChromaDB only | 96.6% | $0 |
| Hybrid v4 (no LLM) | 98.4% | $0 |
| Hybrid v4 + Haiku rerank | 99.4% | ~$0.001/query |
| Hybrid v4 + Sonnet rerank | 100% | ~$0.003/query |
| AAAK mode (experimental) | 84.2% | $0 |

**AAAK regresses accuracy by 12.4pp vs raw** — use raw mode for best results.

## Gotchas

- **Raw mode beats AAAK** on every benchmark. Do not switch to AAAK expecting better results; it's an experimental research format.
- `mempalace mine` skips files >10 MB. Split large exports first (`mempalace split`).
- Minimum chunk size is 30 characters — very short messages are dropped silently.
- The "34% palace boost" claimed in early docs is standard ChromaDB metadata filtering, not a proprietary algorithm.
- Contradiction detection exists in code but is **not wired into the main pipeline** as of April 2026.
- After `pip install mempalace`, ChromaDB is the only heavy dependency — it auto-downloads embedding models on first use (~500 MB, requires internet on first run).
- `mempalace wake-up` loads ~170-token context into the LLM; run it at session start when using MCP tools so Claude knows palace structure.
- Benchmark 96.6% is on **LongMemEval** raw mode. Results on other datasets differ — ConvoMem scores 92.9% vs Mem0's 30–45%.
