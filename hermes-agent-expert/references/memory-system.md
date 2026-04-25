# Hermes Agent Memory System

## Four-Tier Architecture

Hermes stratifies memory by urgency — fast tiers inject at startup, slower tiers are queried on-demand.

| Tier | Storage | Limit | Injection |
|---|---|---|---|
| 1 — Agent Notes | `~/.hermes/memories/MEMORY.md` | 2,200 chars (~800 tokens) | Auto at session start |
| 2 — User Profile | `~/.hermes/memories/USER.md` | 1,375 chars (~500 tokens) | Auto at session start |
| 3 — Session Archive | `~/.hermes/state.db` (SQLite FTS5) | Unlimited | On-demand query |
| 4 — External Plugins | LightRAG, Mem0, Honcho, etc. | Unlimited | On-demand |

**Total always-on context: ~1,300 tokens** (Tiers 1 + 2 combined).

---

## Tier 1 — MEMORY.md (Agent Notes)

What the agent writes here:
- Environment facts (tech stack, server config, project conventions)
- Operational lessons learned
- Your correction patterns and preferences
- Completed milestone markers

What the agent skips:
- Trivial or easily re-discoverable info
- Raw data dumps
- Session-specific ephemera

**Capacity:** When full, the `memory` tool returns an error specifying current usage. The agent must consolidate or remove entries before adding new ones.

### Memory Tool Actions

| Action | Behavior |
|---|---|
| `add` | Insert new entry |
| `replace` | Update via substring matching |
| `remove` | Delete via substring matching |

No `read` action — memory auto-injects into context at session start.

---

## Tier 2 — USER.md (User Profile)

Persistent model of who you are:
- Technical proficiency and role
- Communication style preferences
- Timezone and working hours
- Explicit preferences and corrections
- Long-term goals and project context

Honcho dialectic user modeling can augment this tier with semantic understanding of your patterns over time.

---

## Frozen Snapshot Pattern

Both Tier 1 and Tier 2 use a "frozen snapshot" approach:

1. At session start, both files are read and injected into the system prompt — **once**
2. Changes made during the session persist to disk **immediately**
3. Those changes do **not** modify the active system prompt until the **next session**

**Why:** Mutating the prompt mid-conversation invalidates the LLM's prefix cache, spiking latency. The frozen pattern preserves cache across the entire session.

---

## Periodic Nudge Mechanism

Instead of passively waiting for the user to trigger memory saves, the Hermes runtime actively prompts the agent during idle moments to:
1. Evaluate recent interactions
2. Extract critical facts before the context window fills up
3. Write extractions to MEMORY.md or USER.md

**Use-it-or-lose-it:** Facts the agent doesn't flag during the explicit flush don't survive context compression.

---

## Tier 3 — Session Archive (SQLite FTS5)

All CLI and messaging sessions are stored in `~/.hermes/state.db` with FTS5 full-text search.

- Query past conversations from weeks or months ago
- LLM-powered summarization on search results
- The agent queries this automatically when it needs historical context

No size limit — grows indefinitely.

---

## Tier 4 — External Memory Plugins

8 optional providers that run **alongside** built-in memory (not replacing it):

| Plugin | Strength |
|---|---|
| Honcho | Dialectic user modeling; cross-session user understanding |
| Mem0 | Semantic memory search |
| OpenViking | Graph-based recall |
| Hindsight | Retrospective learning |
| Holographic | Distributed memory patterns |
| RetainDB | Persistent structured knowledge |
| ByteRover | Scalable key-value memory |
| Supermemory | Enterprise-grade cross-agent recall |

**Recommendation:** For most single-server setups, the SQLite FTS5 (Tier 3) provides the best balance of speed and recall. Only add Tier 4 plugins for enterprise-scale multi-agent workflows or when semantic similarity search is a hard requirement.

---

## Memory Security

Before any content is injected into the system prompt, memory entries are scanned for:
- Prompt injection instructions
- Credential exfiltration patterns
- Invisible Unicode characters
- Hidden suspicious HTML comments

Content matching threat patterns is blocked before it reaches the model.

---

## Memory Config in config.yaml

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200        # ~800 tokens
  user_char_limit: 1375          # ~500 tokens
```
