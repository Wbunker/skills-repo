# Anti-Patterns in Context Engineering

Patterns that hurt your context layer's effectiveness. Each traces back to the same root: **noise drowning signal**.

---

## Table of Contents

1. [Ball of Mud](#ball-of-mud)
2. [Downloaded Templates](#downloaded-templates)
3. [Detailed Repo Structure](#detailed-repo-structure)
4. [Duplicating Linter Rules](#duplicating-linter-rules)
5. [Task-Specific Guidance in Root](#task-specific-guidance-in-root)
6. [Generic Advice](#generic-advice)
7. [Memories and Session History](#memories-and-session-history)
8. [Over-Engineered Hierarchy](#over-engineered-hierarchy)
9. [Auto-Generated Bloat](#auto-generated-bloat)
10. [Structural Instead of Semantic Chunking](#structural-instead-of-semantic-chunking)

---

## Ball of Mud

**What it looks like:**
```
project/
├── CLAUDE.md (800+ lines - everything dumped here)
└── src/
    └── (no nodes anywhere)
```

**Why it hurts:**
- Every task loads 800 lines (15k+ tokens)
- Agent fixing a button color gets payment processing rules
- Signal drowns in noise
- Hits the ~150 instruction limit—rules silently drop
- Can't selectively load context for different areas

**The fix:** Split into hierarchical nodes at semantic boundaries. Root should be under 60 lines ideal, 300 max.

---

## Downloaded Templates

**What it looks like:**
```markdown
# Best Practices for AI Coding
- Always write tests
- Use meaningful variable names
- Follow SOLID principles
- Document your code
...
```

**Why it hurts:**
- Written for someone else's stack, conventions, architecture
- Loads behaviors that don't match your codebase
- "You only get the behavior you load"—loading wrong behavior actively misleads
- Generic advice the model already knows

**The fix:** Start minimal. Add rules only when you notice repeated problems. Your layer should reflect YOUR codebase.

---

## Detailed Repo Structure

**What it looks like:**
```markdown
project/
├── src/
│   ├── api/          ← Deleted 3 months ago
│   ├── services/     ← Renamed to "modules"
│   └── utils/        ← Still exists
└── tests/
    ├── unit/         ← Now lives in src/__tests__
    └── integration/
```

**Why it hurts:**
- Rots faster than any other content
- Outdated paths point agents to wrong locations
- File counts become incorrect
- Architecture diagrams become misleading

**What to do instead:**
```markdown
Monorepo with apps/ and packages/.
Each feature gets its own directory under /features.
Auth logic lives in /src/auth.
```

Keep it abstract enough to survive refactors. Agent can explore filesystem for specifics.

---

## Duplicating Linter Rules

**What it looks like:**
```markdown
## Code Style
- Use 2-space indentation
- Always use const over let
- Sort imports alphabetically
- Use single quotes for strings
- No trailing commas
```

**Why it hurts:**
- Wastes tokens on rules already enforced by tooling
- Model attention spent on things it can't violate anyway
- Adds noise without adding value

**What to do instead:**
Only include patterns your linter CAN'T enforce:
- Architectural decisions
- Business logic constraints
- "Why" behind patterns

---

## Task-Specific Guidance in Root

**What it looks like:**
```markdown
# CLAUDE.md

## Payment Processing
When implementing payment flows, always check for fraud flags first.
The payment gateway requires a specific header format...

## Email Templates
When editing email templates, run the preview command first...
```

**Why it hurts:**
- Loads on EVERY task, even when irrelevant
- Agent fixing a typo in README gets payment processing rules
- Bloats root with content that applies 5% of the time

**The fix:** Put in `/payment/CLAUDE.md` and `/emails/CLAUDE.md`. Only loads when agent enters that directory.

---

## Generic Advice

**What it looks like:**
```markdown
## Best Practices
- Write clean code
- Use meaningful variable names
- Don't repeat yourself
- Keep functions small
- Document your code
- Use proper error handling
```

**Why it hurts:**
- Pure noise—model already knows this
- Every token competes for attention
- Zero project-specific signal
- Wastes the limited instruction budget

**The test:** For each line, ask: "If I removed this, would Claude do something wrong on most tasks?" If no, delete it.

---

## Memories and Session History

**What it looks like:**
```markdown
## Memories
- 2024-01-15: Learned that the auth system uses JWT tokens
- 2024-01-20: Found that the database connection pool is 10
- 2024-02-03: User prefers tabs over spaces
```

**Why it hurts:**
- Already captured in explore mode and other mechanisms
- Duplicates information
- Phrased as history, not guidance
- Often becomes stale

**The fix:** If important enough to persist, make it:
- A proper instruction (not a memory)
- In the right place in hierarchy
- Phrased as guidance, not history

---

## Over-Engineered Hierarchy

**What it looks like:**
```
project/
├── CLAUDE.md
├── src/CLAUDE.md
├── src/components/CLAUDE.md
├── src/components/Button/CLAUDE.md      ← too granular
├── src/components/Button/styles/CLAUDE.md  ← way too granular
├── src/components/Modal/CLAUDE.md
├── src/utils/CLAUDE.md
├── src/utils/format/CLAUDE.md
├── src/utils/format/date/CLAUDE.md      ← too granular
```

**Why it hurts:**
- Maintenance overhead explodes
- Most nodes have only 1-2 items
- Creating structure without adding signal
- When patterns change, updating dozens of files

**Rule of thumb:** If you can't write 30+ lines of context specific to a directory, you probably don't need a node there. Let the parent cover it.

---

## Auto-Generated Bloat

**What it looks like:**
```markdown
# Project CLAUDE.md
Generated by claude init on 2024-01-15

## Overview
This is a TypeScript project using Node.js.

## Directory Structure
- src/ - Source code
- tests/ - Test files
- docs/ - Documentation

## Available Scripts
- npm start - Start the application
- npm test - Run tests
- npm build - Build the project
```

**Why it hurts:**
- Obvious things that waste tokens
- Generic advice model already knows
- Often incorrect assumptions about codebase
- Filler that dilutes signal

**The fix:** Treat every generated line as suspect. Delete aggressively. Keep only what adds genuine signal.

---

## Structural Instead of Semantic Chunking

**What it looks like:**
```
src/
├── controllers/CLAUDE.md   ← By technical layer
├── services/CLAUDE.md
├── repositories/CLAUDE.md
├── models/CLAUDE.md
```

**Why it hurts:**
- Technical layers don't share vocabulary
- A controller for checkout and a controller for inventory have nothing in common except "controller"
- Summaries become muddy
- Compression quality drops

**Semantic chunking (better):**
```
├── checkout/CLAUDE.md      ← By business domain
├── inventory/CLAUDE.md
├── payments/CLAUDE.md
```

Similar code compresses better together. Domain boundaries have coherent vocabulary.

---

## The "Would It Mislead?" Test

For every line in your node, ask:

> "If the code changes and I forget to update this, would it mislead the agent?"

If yes:
1. Can you phrase it more abstractly?
2. Does it belong in a sub-folder node instead?
3. Should you just remove it and let the agent discover it?

The safest content is content that stays true even when implementation details change.

---

## Summary Table

| Anti-Pattern | Why It Hurts | Fix |
|--------------|--------------|-----|
| Ball of mud | Hits instruction limits, buries signal | Split hierarchically |
| Downloaded templates | Wrong context for your codebase | Write project-specific |
| Detailed structure | Rots fastest, misleads when stale | Keep abstract |
| Linter rules | Wastes tokens on enforced rules | Delete |
| Task-specific in root | Loads when irrelevant | Move to sub-folder |
| Generic advice | Pure noise | Delete |
| Memories | Duplicates mechanisms | Convert to guidance |
| Over-engineered | Maintenance nightmare | Consolidate |
| Auto-generated | Often noise | Audit and prune |
| Structural chunking | Poor compression | Chunk semantically |
