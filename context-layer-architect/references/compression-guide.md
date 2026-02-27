# Compression Guide

How to achieve high compression ratios in your context layer.

---

## Table of Contents

1. [The Compression Mindset](#the-compression-mindset)
2. [Why Compression Matters](#why-compression-matters)
3. [Semantic vs Structural Chunking](#semantic-vs-structural-chunking)
4. [Compression Math](#compression-math)
5. [Hierarchical Summarization](#hierarchical-summarization)
6. [The Least Common Ancestor Principle](#the-least-common-ancestor-principle)
7. [Token Budgets](#token-budgets)

---

## The Compression Mindset

**The context layer is NOT documentation. It's a compression system.**

Documentation tries to be complete. Compression tries to be minimal.

Goal: **Maximum signal per token loaded.**

You have a 3.2M line codebase (~24M tokens). Context window holds 100-200k tokens. Even filling it degrades signal-to-noise. Instruction following breaks past ~150 rules.

Solution: Compress millions of tokens into the minimum an agent needs to operate safely in each area.

---

## Why Compression Matters

### Without compression:

Agent searches, reads files, accumulates noise. By the time it understands the settlement system, it's consumed 60-120k tokens of exploration—most dead ends.

### With flat CLAUDE.md (2000 lines, 14k tokens):

Every task loads 14k tokens. Agent working on fraud gets settlement rules. Signal drowns in noise. Instruction limits hit.

### With hierarchical compression:

```
Root node:              380 tokens
├── settlement/
│   └── CLAUDE.md:      720 tokens
│       └── reconciliation/
│           └── CLAUDE.md:  540 tokens
```

Task in `reconciliation/` loads: 380 + 720 + 540 = **1,640 tokens**.

That's 1,640 tokens covering behavior spanning ~350k tokens of code. **213x compression ratio.**

---

## Semantic vs Structural Chunking

### Structural chunking (by folder):

```
src/
├── controllers/CLAUDE.md
├── services/CLAUDE.md
├── repositories/CLAUDE.md
```

**Why it fails:** A controller for checkout and a controller for inventory share nothing except "controller." Vocabulary fragments. Summary becomes muddy. Compression degrades.

### Semantic chunking (by responsibility):

```
├── checkout/CLAUDE.md
├── inventory/CLAUDE.md
├── payments/CLAUDE.md
```

**Why it works:** Similar code compresses better together. Each area has coherent vocabulary. Summaries are dense and coherent.

### How to identify semantic boundaries:

1. **Distinct responsibilities?** Name it in one phrase: "handles settlement with banks"
2. **Area-specific invariants?** "Never reprocess settled batch" → settlement node
3. **Guidance needed for newcomers?** 30-minute explanation → capture it
4. **Tribal knowledge not in code?** Historical decisions, incidents → capture it

---

## Compression Math

| Area | Raw Code | Node Tokens | Compression |
|------|----------|-------------|-------------|
| Root (overview) | N/A | 400 | — |
| settlement/ | 360k lines | 720 | 500x |
| reconciliation/ | 72k lines | 540 | 133x |
| fraud/ | 180k lines | 650 | 277x |

**Task in reconciliation/** loads 1,660 tokens of highly relevant context instead of 24M tokens of raw code or 14k tokens of mixed-relevance flat file.

### Compression sweet spots:

- **2k token file → 1k node:** Poor ratio, lots of overhead
- **64k token chunk → 2-3k node:** Excellent ratio
- **20k-64k token chunks:** Sweet spot for meaningful compression

---

## Hierarchical Summarization

**Key mechanic:** When capturing a parent, summarize child nodes—not raw code.

### Fractal compression:

```
Leaf nodes:    Compress raw code into dense context
Parent nodes:  Compress their children's nodes
Root node:     Compress subsystem summaries
```

Each layer stands on stable, already-compressed context from below.

A 1.8k token parent might cover 180k tokens of underlying code because it's summarizing already-compressed children.

### Build leaf-first:

1. Start with well-contained subsystems (reconciliation, then settlement)
2. Each captured node makes adjacent captures easier
3. Parent nodes become straightforward once children exist
4. Root is last—it summarizes everything below

---

## The Least Common Ancestor Principle

When a fact applies to multiple areas, where does it go?

**Answer:** The Least Common Ancestor (LCA)—the shallowest node covering all relevant paths.

### Example:

Auth config applies to payment/, billing/, and api/. The LCA is root.

```
project/
├── CLAUDE.md              ← Shared auth config lives here
├── services/
│   ├── payment/CLAUDE.md  ← Uses auth
│   └── billing/CLAUDE.md  ← Uses auth
└── api/
    └── CLAUDE.md          ← Uses auth
```

### Why LCA works:

- **Not in each leaf:** Duplication drifts out of sync
- **Not deeper than necessary:** Loads when irrelevant
- **At LCA:** Loads exactly when needed, nowhere else

---

## Token Budgets

### Node size limits:

| Level | Ideal | Max | Why |
|-------|-------|-----|-----|
| Root | 50 lines | 300 lines | Loads on EVERY task |
| Subsystem | 100 lines | 200 lines | Loads when in area |
| Leaf | 60 lines | 100 lines | Specific focus |

### When nodes get too long:

If approaching limits, you're probably mixing concerns. Split into children.

Remember: models start dropping rules past ~150 instructions. A 300-line node with 50+ rules is pushing limits.

### The 30-line test:

If you can't write 30+ lines specific to a directory, you probably don't need a node there. Let parent cover it.

---

## Before/After: Real Compression

### Before (fintech startup):

```
project/
└── CLAUDE.md (2400 lines, 16.5k tokens)
```

Every task loads 16.5k tokens. Compression ratio: terrible.

### After (hierarchical):

```
project/
├── CLAUDE.md (45 lines, 410 tokens)
├── processing/
│   └── CLAUDE.md (90 lines, 680 tokens)
├── settlement/
│   ├── CLAUDE.md (110 lines, 820 tokens)
│   └── reconciliation/
│       └── CLAUDE.md (75 lines, 530 tokens)
├── fraud/
│   ├── CLAUDE.md (95 lines, 720 tokens)
│   └── models/
│       └── CLAUDE.md (60 lines, 420 tokens)
└── merchant-portal/
    └── CLAUDE.md (55 lines, 380 tokens)
```

### Results:

| Task Location | Nodes Loaded | Total Tokens | vs. Flat |
|---------------|--------------|--------------|----------|
| reconciliation/ | root + settlement + reconciliation | 1,760 | 9x less |
| merchant-portal/ | root + merchant-portal | 790 | 21x less |
| fraud/models/ | root + fraud + models | 1,550 | 11x less |

Each gets exactly what it needs. No noise from unrelated subsystems.

---

## Summary

| Principle | Application |
|-----------|-------------|
| Compression over documentation | Maximum signal per token |
| Semantic chunking | Group by responsibility, not folder |
| Leaf-first capture | Children stabilize before parents |
| Fractal summarization | Parents compress children |
| LCA placement | Shared facts at shallowest covering node |
| Token budgets | Stay within instruction-following limits |

**Compression is how you win the signal-to-noise game.**
