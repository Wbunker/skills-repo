# MemPalace — Palace Architecture

## The Spatial Metaphor

MemPalace organizes millions of tokens into a navigable hierarchy inspired by the classical memory palace (method of loci). This structure helps navigation and scoped search — **retrieval accuracy comes from raw embeddings, not the hierarchy itself**.

```
Palace
└── Wing  (project or person — top-level namespace)
    └── Room  (specific topic within the wing)
        ├── Hall  (memory type: decisions, facts, preferences…)
        │   └── Closet  (summary pointing to drawers)
        │       └── Drawer  ← verbatim raw content (what gets retrieved)
        └── Tunnel  (cross-wing link when same room appears in 2+ wings)
```

## Components

### Wings

Top-level namespaces — typically one per project or collaborator.

Examples:
- `backend-api` (a project wing)
- `alice` (a collaborator wing)
- `personal` (your own history wing)
- `preferences` (the auto-generated preference wing)

List wings:
```bash
mempalace status
# or via MCP: mempalace_list_wings
```

### Rooms

A topic within a wing. Each room groups related drawers.

Examples inside a `backend-api` wing:
- `authentication`
- `database-schema`
- `graphql-migration`
- `ci-pipeline`
- `performance-tuning`

Rooms are auto-classified by `room_detector_local.py` at ingest time, or set explicitly when adding drawers manually.

List rooms in a wing:
```bash
# via MCP: mempalace_list_rooms  (wing parameter optional — returns all rooms if omitted)
```

### Drawers

Drawers are the **actual content units** — verbatim raw conversation chunks stored in ChromaDB. This is what retrieval operates on. Every search returns drawer contents.

Drawers have metadata:
- `wing` — which wing
- `room` — which room
- `source_file` — original file path
- `added_by` — ingest method

Add a drawer manually:
```bash
# via MCP: mempalace_add_drawer
# Parameters: content (text), wing, room, source_file (optional)
```

Delete a drawer:
```bash
# via MCP: mempalace_delete_drawer (by drawer ID)
```

### Closets

Closets hold **summaries that point to drawers** — used for quick human browsing and navigation, not for retrieval accuracy. The retrieval engine hits drawers directly.

Think of a closet as a table-of-contents entry that says "the full content is in drawer X."

### Halls

Halls organize memory **types** within a room:
- `facts`
- `events`
- `discoveries`
- `preferences`
- `advice`
- `decisions`

Halls are a sub-level between rooms and drawers for navigating by memory type.

### Tunnels

A tunnel appears automatically when the **same room name** exists in two or more different wings. Tunnels represent cross-project connections.

Example: `authentication` room in `backend-api` wing ↔ `authentication` room in `alice` wing → tunnel links them, allowing BFS traversal to find multi-hop connections.

Find tunnels:
```bash
# via MCP: mempalace_find_tunnels (specify two wings to find bridging rooms)
```

## Palace Graph Navigation

`palace_graph.py` computes the navigation graph on-demand (not stored as a persistent file):

- Scans ChromaDB metadata in 1000-item batches
- Two rooms are connected if they share a wing
- Tunnels appear when same room name is in 2+ wings
- BFS traversal walks multi-hop connections

Navigate from a room:
```bash
# via MCP: mempalace_traverse
# Shows connected rooms and how many hops away
```

Graph stats:
```bash
# via MCP: mempalace_graph_stats
```

## Scoped Search

The palace hierarchy enables scoped searches that reduce noise:

```bash
mempalace search "auth token approach" --wing backend-api
mempalace search "auth token approach" --wing backend-api --room authentication
```

Via MCP `mempalace_search`: pass `wing` and/or `room` parameters to filter.

A scoped search limits ChromaDB to only the matching metadata — effectively restricting retrieval to one project or topic.

## The Preference Wing

One wing is special: the **preference wing** (auto-created by `--extract general`).

At ingest time, 16 regex patterns in `general_extractor.py` scan conversations for preference expressions and write synthetic summary documents to the preference wing. These become first-class searchable entities.

Examples of what gets extracted:
- "User prefers TypeScript over JavaScript"
- "User uses vim keybindings"
- "User is allergic to peanuts"

When a future query touches preferences, the system matches these concentrated synthetic documents rather than hunting for the original sentence buried in a 2000-word conversation.

## Full Taxonomy View

```bash
# via MCP: mempalace_get_taxonomy
# Returns: wing → room → drawer count
```

Example output:
```
backend-api
  └── authentication: 47 drawers
  └── database-schema: 31 drawers
  └── graphql-migration: 12 drawers
alice
  └── authentication: 8 drawers  ← tunnel to backend-api/authentication
  └── code-review: 22 drawers
preferences
  └── tools: 14 drawers
  └── style: 9 drawers
```
