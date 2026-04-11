# MemPalace — All 19 MCP Tools

After `claude mcp add mempalace -- python -m mempalace.mcp_server`, these tools are available to Claude in any conversation.

Run `mempalace wake-up` at the start of a session to pre-load palace context (~170 tokens).

---

## Read / Search Tools (7)

### `mempalace_status`
Palace overview — total drawer count, wing list, room counts.
Use at session start or when asked "what's in my palace?"

### `mempalace_list_wings`
List all wings with their drawer counts.
```
Parameters: none
```

### `mempalace_list_rooms`
List rooms within a wing (or all rooms if no wing specified).
```
Parameters:
  wing: string (optional) — filter to one wing
```

### `mempalace_get_taxonomy`
Full hierarchy: every wing → every room → drawer count.
Use to understand palace structure before navigating.
```
Parameters: none
```

### `mempalace_search`
**The primary retrieval tool.** Semantic search with similarity scores against all drawers.
```
Parameters:
  query:   string (required, max 500 chars)
  limit:   int    (optional, default 5) — number of results
  wing:    string (optional) — scope to one wing
  room:    string (optional) — scope to one room
  context: bool   (optional) — include surrounding drawer context
```
Returns drawer content, similarity score, wing/room metadata.

### `mempalace_check_duplicate`
Check whether content already exists in the palace before adding.
```
Parameters:
  content: string — text to check
```
Returns similarity score against nearest existing drawer.

### `mempalace_get_aaak_spec`
Return the AAAK dialect specification (for LLMs that need to parse/generate AAAK format).
See [aaak-format.md](aaak-format.md) for full AAAK documentation.

---

## Knowledge Graph Tools (5)

### `mempalace_kg_query`
Query entity relationships with optional temporal filtering.
```
Parameters:
  entity:  string (required) — entity name to query
  as_of:   string (optional) — ISO date for historical query ("what was true on 2026-01-15?")
```
Returns triples: (subject, predicate, object, valid_from, valid_to)

### `mempalace_kg_add`
Add a fact to the knowledge graph.
```
Parameters:
  subject:    string (required)
  predicate:  string (required)
  object:     string (required)
  valid_from: string (optional) — ISO date
  valid_to:   string (optional) — ISO date (leave empty if still true)
```

### `mempalace_kg_invalidate`
Mark a fact as no longer true (set its `valid_to` date).
```
Parameters:
  subject:   string (required)
  predicate: string (required)
  object:    string (required)
  ended:     string (required) — ISO date when fact stopped being true
```

### `mempalace_kg_timeline`
Chronological fact timeline for an entity.
```
Parameters:
  entity: string (required)
```
Returns all facts about the entity ordered by valid_from date.

### `mempalace_kg_stats`
Knowledge graph overview — total entity count, triple count by type.
```
Parameters: none
```

---

## Navigation Tools (3)

### `mempalace_traverse`
Walk the palace graph from a starting room and show connected rooms/wings.
Useful for multi-hop discovery: "what else is related to this topic?"
```
Parameters:
  room: string (required) — starting room name
  wing: string (optional) — starting wing (required if room name is ambiguous)
  hops: int   (optional, default 2) — how many hops to traverse
```

### `mempalace_find_tunnels`
Find rooms that bridge two wings — rooms that appear in both.
```
Parameters:
  wing_a: string (required)
  wing_b: string (required)
```
Returns list of room names present in both wings (the tunnels).

### `mempalace_graph_stats`
Palace graph overview — total rooms, connections, tunnel count.
```
Parameters: none
```

---

## Write Tools (2)

### `mempalace_add_drawer`
File verbatim content as a new drawer with explicit metadata.
Use when you want to store content that wasn't auto-mined (notes, decisions, snippets).
```
Parameters:
  content:     string (required) — verbatim text to store
  wing:        string (required) — which wing
  room:        string (required) — which room
  source_file: string (optional) — origin reference
```

### `mempalace_delete_drawer`
Delete a drawer by its ID.
```
Parameters:
  drawer_id: string (required) — ID returned by search results
```

---

## Agent Diary Tools (2)

The agent diary allows Claude to maintain a personal log of session notes, observations, and decisions in AAAK format.

### `mempalace_diary_write`
Write an entry to the agent's personal diary (stored in AAAK format).
```
Parameters:
  content: string (required) — diary entry text
```

### `mempalace_diary_read`
Read recent diary entries.
```
Parameters:
  limit: int (optional, default 10) — number of recent entries to return
```

---

## Typical Usage Pattern in a Claude Session

```
1. Session start:
   → mempalace_status          (what's in the palace?)
   → mempalace_wake-up         (load context summary)

2. When user asks about past work:
   → mempalace_search("query", limit=5)
   → show relevant drawer content

3. When user asks about entities/relationships:
   → mempalace_kg_query("entity name")
   → or mempalace_kg_timeline for history

4. When storing new content during session:
   → mempalace_add_drawer(content, wing, room)

5. When exploring connections:
   → mempalace_traverse(room) or mempalace_find_tunnels(wing_a, wing_b)
```
