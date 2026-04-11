# MemPalace — Knowledge Graph and Entity Detection

## Overview

MemPalace maintains a **SQLite-based knowledge graph** alongside the ChromaDB vector store. It tracks entity relationships with temporal validity windows — facts can be true during one period and false during another.

No cloud, no Neo4j subscription, no external services. Zero cost.

## Knowledge Graph Structure

Each fact is stored as a **triple** with time bounds:

```
(subject, predicate, object, valid_from, valid_to)
```

Examples:
```sql
("Max",   "child_of",       "Alice",           "2015-04-01", NULL)
("Max",   "enrolled_in",    "MIT",              "2024-09-01", NULL)
("Alice", "works_at",       "Acme Corp",        "2020-01-01", "2025-06-30")
("Alice", "prefers",        "TypeScript",       "2023-01-01", NULL)
("Max",   "has_issue",      "sports_injury",    "2026-01-01", "2026-02-15")
```

`valid_to = NULL` means the fact is currently true.

## Core Operations

### Add a fact

```python
# via Python API
kg.add_triple("Alice", "prefers", "vim keybindings", valid_from="2023-01-01")

# via MCP tool
mempalace_kg_add(subject="Alice", predicate="prefers", object="vim keybindings")
```

### Query an entity

```python
# Current facts about Alice
kg.query_entity("Alice")

# Historical query: what was true on January 15, 2026?
kg.query_entity("Alice", as_of="2026-01-15")

# via MCP
mempalace_kg_query(entity="Alice", as_of="2026-01-15")
```

### Invalidate a fact

```python
# Mark sports injury as resolved
kg.invalidate("Max", "has_issue", "sports_injury", ended="2026-02-15")

# via MCP
mempalace_kg_invalidate(subject="Max", predicate="has_issue",
                        object="sports_injury", ended="2026-02-15")
```

### Timeline view

```python
# All facts about Max, in chronological order
kg.timeline("Max")

# via MCP
mempalace_kg_timeline(entity="Max")
```

## Entity Detection (`entity_detector.py`)

When running `mempalace mine`, the entity detector scans conversation text in two passes:

### Pass 1 — Candidate Extraction
- Scans for capitalized words appearing 3+ times in the text
- Filters against a comprehensive stopwords list
- Produces candidate entity names

### Pass 2 — Signal Scoring and Classification

**Person signals** (detected in context around candidate):
- Dialogue markers: `"Alice:"`, `"said"`, `"asked"`
- Action verbs: social verbs in proximity
- Pronouns: he/she/they referring back to the candidate
- Direct address patterns

**Project/tool signals**:
- Versioning: `v2`, `v3.1`
- Code references: `.py`, `.js`, `.ts` extensions
- Project verbs: `building`, `deployed`, `launched`, `shipped`

Requires ≥2 different signal types for high-confidence classification. Mixed signals are marked uncertain for human review.

Results are written to the SQLite KG and the `entity_registry.py` for AAAK code mapping.

## Preference Wing and General Extraction

`general_extractor.py` uses 16 regex patterns to extract preference signals at ingest time when `--extract general` is passed:

**Patterns detected**:
- `"I prefer X over Y"`
- `"I always use X"`
- `"I never X"`
- `"I still remember X"`
- `"I used to X"`
- `"When I was in [context] X"`
- `"Growing up X"`

**Five memory types** extracted and classified:

| Type | Description | Example |
|------|-------------|---------|
| Decision | Explicit choices made | "chose PostgreSQL over MySQL" |
| Preference | Tool/style/personal preferences | "prefers TypeScript" |
| Milestone | Significant achievements | "shipped v2.0 to production" |
| Problem | Documented issues | "auth token expiry bug in March" |
| Emotional context | Sentiment markers | "frustrated with the deploy pipeline" |

Each extracted item becomes a **synthetic document** stored in the preference wing — a concentrated signal that semantic search can find directly, rather than hunting for the relevant sentence buried in a full conversation.

## Knowledge Graph vs. Raw Drawers

| | Raw Drawers (ChromaDB) | Knowledge Graph (SQLite) |
|---|---|---|
| Storage | Full verbatim conversation text | Structured (subject, predicate, object) triples |
| Query type | Semantic similarity | Exact entity/relationship lookup |
| Temporal | Via metadata filtering | First-class: valid_from/valid_to on every fact |
| Best for | "Find conversations about auth" | "What was Alice's role in January?" |
| Updated | At mine time | At mine time + manually via MCP tools |

## Practical Use with Claude (MCP)

```
User: "What does Alice prefer for code style?"
Claude → mempalace_kg_query(entity="Alice")
       → finds: ("Alice", "prefers", "vim keybindings") and ("Alice", "prefers", "TypeScript")
       → also: mempalace_search("Alice code style preferences")
       → combines KG facts + drawer context for full answer

User: "What did we decide about the database in Q1?"
Claude → mempalace_kg_query(entity="database", as_of="2026-03-31")
       → finds decisions valid during Q1
       → mempalace_search("database decision") with temporal boost
```

## KG Stats

```bash
# via MCP: mempalace_kg_stats
# Returns: total entities, triple count by predicate type, active vs. historical fact ratio
```
