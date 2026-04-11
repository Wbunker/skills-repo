# MemPalace — AAAK Format

## What AAAK Is

AAAK is a **lossy symbolic summarization format** — not lossless compression. Original text **cannot** be reconstructed from AAAK output.

The name is deliberately unexplained. The README says: "Don't ask; it's a whole story of its own."

**Current status**: Experimental. AAAK mode scores 84.2% R@5 vs raw mode's 96.6% — a 12.4pp regression. Do not use AAAK for retrieval-critical applications.

## When AAAK Might Be Useful

- When you want a human-skimmable compact summary (not for retrieval)
- When loading context into an LLM that already knows what to look for (AAAK is native LLM-readable)
- At truly massive scale (millions of repeated entity references) — entity code deduplication may eventually provide token savings, but this hasn't been demonstrated on real corpora yet
- The agent diary feature uses AAAK internally for session notes

## AAAK Format Specification

### Header

```
FILE_NUM|PRIMARY_ENTITY|DATE|TITLE
```

Example:
```
047|ALC|2026-03-15|Auth migration decision
```

### Zettel (main content unit)

```
ZID:ENTITIES|topic_keywords|"key_quote"|WEIGHT|EMOTIONS|FLAGS
```

Fields:
- **ZID**: Numeric ID for this zettel
- **ENTITIES**: 3-char uppercase entity codes separated by `+` (from entity registry)
- **topic_keywords**: Top-frequency content words (proper nouns and CamelCase boosted), underscore-separated
- **key_quote**: 55-char max key sentence fragment, scored by decision keywords and length
- **WEIGHT**: Float 0–1, relevance/importance score
- **EMOTIONS**: 3–4 char codes from the 30+ emotion library (see below), joined with `+`
- **FLAGS**: Significance tags (see below)

Example zettel:
```
001:ALC+BOB|GraphQL_REST_API|"chose GraphQL over REST for flexibility"|0.85|determ+convict|DECISION
```

### Tunnel

Cross-reference between two zettels:
```
T:ZID_A<->ZID_B|label
```

### Arc

Emotional trajectory across the conversation:
```
ARC:emotion_start->emotion_mid->emotion_end
```

---

## Entity Codes

Entities are mapped to 3-character uppercase codes in `entity_registry.py`:

| Entity | Code |
|--------|------|
| Alice | ALC |
| Bob | BOB |
| Max | MAX |
| PostgreSQL | PQS |
| GraphQL | GQL |

Codes are project-local (configured per palace). At scale, repeating `ALC` instead of `Alice` 1000 times saves tokens — in theory.

**Gotcha**: Hash collisions are a known risk in high-precision domains (legal, medical) where entity disambiguation matters. See Issue #95.

---

## FLAGS Reference

| Flag | Meaning |
|------|---------|
| `ORIGIN` | Birth of something new (project start, new relationship) |
| `CORE` | Identity or belief pillar |
| `SENSITIVE` | Requires careful handling |
| `PIVOT` | Emotional or directional turning point |
| `GENESIS` | Led to existing outcomes (retrospectively important) |
| `DECISION` | Explicit choice moment |
| `TECHNICAL` | Implementation details |

---

## EMOTIONS Reference (30+ codes)

| Code | Emotion | Code | Emotion |
|------|---------|------|---------|
| `vul` | vulnerable | `joy` | joy |
| `fear` | fear | `trust` | trust |
| `grief` | grief | `wonder` | wonder |
| `rage` | rage | `love` | love |
| `determ` | determined | `convict` | conviction |
| `hope` | hope | `doubt` | doubt |
| `pride` | pride | `shame` | shame |
| `anx` | anxious | `calm` | calm |

---

## Token Economics (Honest Assessment)

The README's own example:
- Input English: 66 tokens
- AAAK output: 73 tokens

At small scales, AAAK **adds** tokens, not saves them. Token savings require a large corpus with many repeated entity references — the threshold hasn't been demonstrated in practice.

Community member panuhorsmalahti (Issue #43) caught that the README used `len(text)//3` as a tokenizer heuristic instead of an actual tokenizer (e.g., tiktoken). The authors corrected this in the April 2026 README update.

---

## AAAK vs Raw — Decision Guide

```
Use CASE → Recommendation

Retrieval accuracy matters most → Raw mode (96.6% vs 84.2%)
Human-skimmable session summary → AAAK (compact, readable)
Agent diary entries → AAAK (built-in to diary tools)
Context loading into LLM → AAAK if entity codes are configured
Large corpus, millions of entity occurrences → AAAK may help (unproven)
Legal / medical precision → Raw mode (avoid entity code collisions)
Default recommendation → Raw mode for everything
```

---

## Getting the AAAK Spec

If you need to parse or generate AAAK in a conversation:

```bash
# via MCP: mempalace_get_aaak_spec
# Returns the full dialect specification for use in LLM prompts
```
