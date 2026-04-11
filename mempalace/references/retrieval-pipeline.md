# MemPalace — Retrieval Pipeline and Benchmarks

## What R@5 Means

**Recall@5 (R@5)**: Given a question, does the correct conversation appear in the top 5 results? Measured across a test set of N questions.

- 96.6% R@5 on 500 questions = 483 correct, 17 misses
- 85% R@5 = ~75 misses per 500 questions — roughly 1-in-7 queries fails

In practice: the difference between 85% and 96.6% is the difference between "useful sometimes" and "I can rely on this."

## Benchmark Results (April 2026)

### LongMemEval (500 questions)

| Mode | R@5 | Cost/query | Notes |
|------|-----|-----------|-------|
| Raw ChromaDB (baseline) | 96.6% | $0 | Zero API calls |
| Hybrid v1 (keyword boost) | 97.8% | $0 | +1.2pp |
| Hybrid v2 (temporal boost) | 98.4% | $0 | +0.6pp |
| Hybrid v3 (preference extraction) | 98.4% | $0 | +0.6pp (without LLM) |
| Hybrid v4 + Haiku rerank | 99.4% | ~$0.001 | 3 misses out of 500 |
| Hybrid v4 + Sonnet rerank | 100% | ~$0.003 | 0 misses |
| AAAK mode | 84.2% | $0 | -12.4pp vs raw |

### Category Breakdown (Hybrid v4 + Haiku)

| Category | R@5 | N |
|----------|-----|---|
| Knowledge-update | 100% | 78 |
| Multi-session | 100% | 133 |
| Single-session-user | 100% | 70 |
| Temporal reasoning | 99.2% | 133 |
| Single-session-preference | 96.7% | 30 |

Weakest category (preference) is because regex-based extraction misses non-standard preference expressions.

### ConvoMem (75,000+ QA pairs)

| System | Score |
|--------|-------|
| MemPalace | 92.9% |
| Mem0 | 30–45% |

### Competitive Comparison (LongMemEval R@5)

| System | R@5 |
|--------|-----|
| MemPalace (Hybrid + Sonnet) | 100% |
| MemPalace (raw, free) | 96.6% |
| Mastra | 94.87% |
| Hindsight | 91.4% |
| Supermemory | 85% |
| Mem0 | 30–45% (ConvoMem) |

## The Five-Stage Pipeline

### Stage 0: Raw ChromaDB (baseline — 96.6% R@5)

- Widen retrieval from top 10 to top 50 candidates
- Pure semantic vector search against verbatim drawer content
- This alone achieves 96.6% — no keyword matching, no date logic

This is the **default mode** and the recommended starting point. It's free and has no dependencies beyond ChromaDB.

### Stage 1: Keyword Overlap Re-ranking (+1.2pp → 97.8%)

Fixes semantic search's blind spot: exact keyword matches.

```
fused_distance = distance × (1.0 − 0.30 × keyword_overlap)
```

- Non-stop words extracted from query (40+ stop words filtered: "what", "when", "where", "how", etc.)
- Overlap computed against each candidate document
- Up to 30% distance reduction for strong keyword matches

**Example**: "What did I say about GraphQL?" — raw embeddings might rank a semantically similar but different doc higher; keyword boost ensures the exact word "GraphQL" counts.

### Stage 2: Temporal Date Boost (+0.6pp → 98.4%)

Fixes time-based queries ("What did we discuss a couple days ago?").

- Regex patterns detect temporal references: "N days ago", "a couple days ago", "last week", "N months ago", "recently"
- Computes target date window from reference
- Up to 40% distance reduction for temporally-matching documents
- Two-pass retrieval for "what you told me" queries:
  - First pass: user-turn-only index
  - Second pass: full conversation re-indexed from top 5 results

### Stage 3: Preference Extraction (no-LLM: 98.4%, +LLM: 99.4%)

- Expands rerank candidate pool from top 10 → top 20
- Preference wing synthetic documents participate in ranking
- Queries about tools, habits, preferences now find concentrated signal docs

### Stage 4: LLM Reranking (optional — +1.0pp with Haiku)

The only stage that costs money.

- Top 20 candidates sent to Claude Haiku (or Sonnet) with relevance judgment prompt
- Haiku: ~$0.001/query → 99.4% R@5
- Sonnet: ~$0.003/query → 100% R@5

Enable via search parameter or CLI flag (exact flag TBD in your version — check `mempalace search --help`).

## Why Raw Beats AAAK

AAAK lossy compression drops R@5 from 96.6% to 84.2% — a 12.4pp regression. The information lost during compression hurts retrieval more than any token savings help.

The AAAK experiment empirically proves the raw text thesis: **any lossy compression degrades retrieval accuracy**. See [aaak-format.md](aaak-format.md) for details on when AAAK might still be useful.

## Independent Reproducibility

Community member gizmax (Issue #39) independently reproduced the 96.6% result on an M2 Ultra Mac Studio in under 5 minutes. The benchmark is reproducible:

```bash
mempalace benchmark    # runs retrieval smoke test against local data
```

## Benchmark Caveats (from April 7, 2026 author correction)

The MemPalace authors published a correction note in the README:

1. **96.6% is raw mode** — not AAAK mode
2. **Token counting** used rough heuristics (`len(text)//3`) in early docs, not a real tokenizer
3. **"+34% palace boost"** is standard ChromaDB metadata filtering, not a proprietary algorithm
4. **Contradiction detection** exists in code but is not yet integrated into the main retrieval pipeline
5. LoCoMo ground truth contains some errors (noted by community review)

Their summary: "We'd rather be right than impressive."
