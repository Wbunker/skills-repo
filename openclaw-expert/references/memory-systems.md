# Memory Systems

Memory architecture, daily logs, curated memory, external providers, and context management.

## Table of Contents

- [Memory Architecture Overview](#memory-architecture-overview)
- [Core Memory Files](#core-memory-files)
- [Daily Log Pattern](#daily-log-pattern)
- [Curated Memory (MEMORY.md)](#curated-memory-memorymd)
- [Production Memory Layout](#production-memory-layout)
- [SaaS-Replacement Workspace](#saas-replacement-workspace)
- [External Memory Providers](#external-memory-providers)
- [Context Window Management](#context-window-management)
- [Memory Maintenance](#memory-maintenance)

---

## Memory Architecture Overview

```
Memory System
├── Short-term: Daily logs (memory/YYYY-MM-DD.md)
│   └── Everything from today's work — auto-appended
├── Long-term: MEMORY.md (curated summary)
│   └── Patterns, preferences, key decisions — manually maintained
├── Identity: SOUL.md (personality + rules)
│   └── Loaded every conversation — keep under 60 lines
└── Operational: AGENTS.md, HEARTBEAT.md
    └── Rules, health checks — loaded as needed
```

OpenClaw agents have no built-in persistent memory across sessions. Memory is achieved through files that are loaded into context at conversation start.

## Core Memory Files

| File | Purpose | Loaded when | Size guideline |
|------|---------|-------------|---------------|
| `SOUL.md` | Identity, personality, core rules | Every session | 40-60 lines |
| `MEMORY.md` | Curated long-term knowledge | Every session | < 200 lines |
| `AGENTS.md` | Operational rules, tool usage | Every session | < 100 lines |
| `HEARTBEAT.md` | Periodic self-check checklist | Cron trigger | 20-40 lines |
| `BOOT.md` | Startup recovery instructions | On crash/restart | < 50 lines |
| `memory/YYYY-MM-DD.md` | Daily activity log | On reference | Unlimited |

## Daily Log Pattern

Auto-append a structured log for each day:

```markdown
<!-- memory/2026-03-01.md -->
# 2026-03-01

## Tasks completed
- Deployed newsletter agent v2
- Fixed Twitter rate limit handling

## Decisions made
- Switched from Opus to Sonnet for routine tasks (saves ~$30/week)
- Added 2-minute cooldown on competitor price checks

## Issues encountered
- Supabase RLS policy blocked agent writes — fixed by adding service role
- Memory file exceeded 300 lines — ran compaction

## Notes for tomorrow
- Follow up on client invoice #1247
- Test new ElevenLabs voice model
```

### Automatic daily logging

```yaml
# Cron: Append to daily log at end of day
- name: "day-wrap"
  schedule: "0 23 * * *"
  prompt: >
    Review today's activity. Append a summary to memory/$(date +%Y-%m-%d).md
    covering: tasks completed, decisions made, issues encountered,
    and notes for tomorrow. Be concise.
```

## Curated Memory (MEMORY.md)

MEMORY.md is the **most important memory file** — it's loaded every session and contains distilled knowledge.

### Structure

```markdown
# Memory

## User preferences
- Prefers concise responses, no emojis
- Tech stack: Next.js, Supabase, Tailwind
- Timezone: EST, working hours 9am-6pm

## Project context
- Main project: SaaS dashboard for [client]
- Database: Supabase with RLS on all tables
- Deployment: Vercel (frontend), VPS (OpenClaw agents)

## Recurring patterns
- Monday: weekly planning + content calendar review
- Friday: invoice generation + expense reconciliation
- Monthly: subscription audit + API key rotation

## Key decisions (with rationale)
- 2026-02-15: Use Sonnet for routine, Opus for complex (cost)
- 2026-02-20: Telegram as primary interface (reliability + free)
- 2026-02-25: One-writer-many-readers for shared files (avoid conflicts)

## Learned corrections
- Don't post tweets before 9am EST (low engagement)
- Always check RLS policies before INSERT operations
- Client prefers bullet points over paragraphs in reports
```

### Rules for MEMORY.md

1. **Keep under 200 lines** — this loads every session
2. **Update, don't append** — replace outdated entries
3. **Include rationale** — "why" matters more than "what"
4. **Date key decisions** — makes it easy to revisit
5. **Prune weekly** — remove no-longer-relevant items

## Production Memory Layout

### 6-folder pattern for complex setups

```
memory/
├── soul/           # Identity files (SOUL.md, IDENTITY.md)
├── user/           # User preferences, contacts, accounts
├── daily/          # Daily logs (YYYY-MM-DD.md)
├── projects/       # Per-project context and state
├── meetings/       # Meeting notes and action items
├── archive/        # Compacted old daily logs
└── index.md        # What's where — loaded to navigate
```

### Index file pattern

```markdown
<!-- memory/index.md -->
# Memory Index

## Active projects
- Project Alpha: projects/alpha.md (client dashboard)
- Project Beta: projects/beta.md (newsletter system)

## Recent daily logs
- Today: daily/2026-03-01.md
- Yesterday: daily/2026-02-28.md

## Key references
- Client contacts: user/contacts.md
- API keys status: user/api-keys.md
- Content calendar: projects/content-calendar.md
```

## SaaS-Replacement Workspace

Use OpenClaw to replace Notion, Todoist, habit trackers, and other productivity apps with plain markdown files:

```
workspace/
├── HABITS.md          # Daily habit tracking (streaks, check-ins)
├── MEMORY.md          # Long-term notes and context
├── NOTES.md           # Notes and important links categorized and stored
├── PROJECTS.md        # Active projects and tasks (to dos)
├── PROFILE.md         # Personal preferences (agent's "bible" to reference)
├── USER.md            # Quick-reference identity card (passed every session)
└── drafts/            # Article drafts, ideas, etc.
```

### Git-backed notes (replacing Notion)

Every change is a git commit. Nightly cron pushes to a private GitHub repo.

```yaml
- name: "nightly-backup"
  schedule: "0 23 * * *"
  prompt: >
    Commit all workspace changes to git and push to the private repo.
    Include a summary commit message of today's changes.
```

**Why this beats Notion**: Tool-agnostic (markdown), version-controlled (diff, blame, revert), AI-native (agent reads/writes directly), free (GitHub private repos), portable (if OpenClaw disappears, files remain).

### Voice note workflow

Send a voice message on WhatsApp → agent transcribes via Gemini → parses actionable items → files them in the right places (PROJECTS.md, NOTES.md, calendar).

## External Memory Providers

### QMD (Query-able Memory Database)

Built-in OpenClaw memory system for semantic search across memory files:

```json
{
  "memory": {
    "provider": "qmd",
    "path": "~/.openclaw/memory",
    "indexOnWrite": true
  }
}
```

Allows agents to query memory semantically rather than loading entire files.

### Mem0

External memory layer with automatic extraction and retrieval:

```json
{
  "memory": {
    "provider": "mem0",
    "apiKey": "${MEM0_API_KEY}",
    "userId": "main-agent"
  }
}
```

### Cognee

Knowledge graph-based memory for complex relationship tracking:

```json
{
  "memory": {
    "provider": "cognee",
    "endpoint": "http://localhost:8000",
    "graphDb": "neo4j"
  }
}
```

### Obsidian integration

Use Obsidian vault as a knowledge base:

```json
{
  "memory": {
    "provider": "obsidian",
    "vaultPath": "/path/to/obsidian/vault",
    "indexTags": ["openclaw", "agent-memory"]
  }
}
```

### Comparison

| Provider | Best for | Persistence | Search | Cost |
|----------|---------|-------------|--------|------|
| Local files | Simple setups, full control | File system | Grep/read | Free |
| QMD | Semantic search, built-in | File system | Semantic | Free |
| Mem0 | Automatic extraction | Cloud | Semantic | API usage |
| Cognee | Relationship mapping | Graph DB | Graph + semantic | Self-hosted |
| Obsidian | Existing knowledge base | File system | Tags + links | Free |

## Context Window Management

### The core constraint

Every file loaded into context uses tokens. Overloading context degrades agent performance.

### Rules

1. **SOUL.md: 40-60 lines max** — loaded every session
2. **MEMORY.md: < 200 lines** — loaded every session
3. **Daily logs: only today + yesterday** — older logs on demand
4. **Reference files: on demand** — don't auto-load large references
5. **One task at a time** — don't load multiple project contexts simultaneously

### Memory loading strategy

```
Session start:
  1. Load SOUL.md (always)
  2. Load MEMORY.md (always)
  3. Load AGENTS.md (always)
  4. Load today's daily log (if exists)
  5. Load task-specific context (on demand)
```

## Memory Maintenance

### Weekly compaction

```yaml
- name: "weekly-compaction"
  schedule: "0 2 * * 0"    # Sunday 2am
  prompt: >
    Compact memory: 1) Archive daily logs older than 7 days to archive/.
    2) Extract key patterns from archived logs into MEMORY.md.
    3) Remove redundant or outdated entries from MEMORY.md.
    4) Ensure MEMORY.md stays under 200 lines.
```

### Monthly deep clean

```yaml
- name: "monthly-memory-audit"
  schedule: "0 3 1 * *"    # 1st of month, 3am
  prompt: >
    Full memory audit: 1) Review all entries in MEMORY.md — remove anything
    no longer relevant. 2) Check project files — archive completed projects.
    3) Verify user preferences are still accurate. 4) Update index.md.
    5) Report changes made.
```
