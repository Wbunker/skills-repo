# Dataview Plugin Reference

## Table of Contents
1. [Setup and basics](#setup-and-basics)
2. [Query types](#query-types)
3. [DQL syntax](#dql-syntax)
4. [FROM sources](#from-sources)
5. [WHERE filters](#where-filters)
6. [Metadata fields](#metadata-fields)
7. [Common useful queries](#common-useful-queries)
8. [Inline queries](#inline-queries)
9. [Dataviewjs overview](#dataviewjs-overview)
10. [Performance tips](#performance-tips)

---

## Setup and basics

Install: Community Plugins → "Dataview" (by Michael Brenan).

Settings → Dataview:
- Enable JavaScript queries: on (needed for `dataviewjs`)
- Inline query prefix: `=` (default)
- Enable inline queries: on

**How it works:** Dataview indexes all notes in real time. Frontmatter properties become queryable fields. Implicit fields (file.name, file.ctime, file.tags, etc.) are available on every note.

Queries live in code blocks with the `dataview` language tag:

````markdown
```dataview
TABLE file.name, status, date
FROM "Projects"
WHERE status = "active"
SORT date DESC
```
````

Queries render dynamically — the result updates automatically as notes change.

---

## Query types

| Type | Output | Best for |
|------|--------|---------|
| `LIST` | Bulleted list of note links | Simple note lists |
| `TABLE` | Table with columns | Multi-field views, dashboards |
| `TASK` | Interactive task list | Task management |
| `CALENDAR` | Monthly calendar with dots on dates | Visualizing activity over time |

---

## DQL syntax

Full query structure:
```
[QUERY TYPE] [fields]
FROM [source]
WHERE [condition]
SORT [field] [ASC|DESC]
LIMIT [n]
FLATTEN [field] AS [alias]
GROUP BY [field]
```

Only the query type line is required. All other clauses are optional.

---

## FROM sources

```
FROM "folder/path"          ← notes in a specific folder
FROM #tag                   ← notes with a tag
FROM [[Note Name]]          ← notes that link to or from a note
FROM outgoing([[Note]])     ← notes linked FROM the note
FROM incoming([[Note]])     ← notes linking TO the note (backlinks)
FROM "folder" AND #tag      ← combine with AND / OR / NOT
FROM -"_Templates"          ← exclude a folder
```

---

## WHERE filters

```
WHERE status = "active"
WHERE status != "archived"
WHERE date >= date(today)
WHERE date >= date(today) - dur(7 days)
WHERE file.tags contains "#project"
WHERE contains(file.tags, "#book")
WHERE length(file.inlinks) > 5       ← notes with more than 5 backlinks
WHERE file.name != this.file.name    ← exclude current note from results
WHERE !completed                      ← boolean false check
WHERE due AND due <= date(today)      ← has due date and it's today or past
```

**Date literals:**
```
date(today)
date(tomorrow)
date(yesterday)
date(2025-04-05)
date(now)          ← includes time
```

**Duration literals:**
```
dur(7 days)
dur(1 week)
dur(3 months)
date(today) - dur(30 days)    ← 30 days ago
```

---

## Metadata fields

### Implicit fields (available on every note, no frontmatter needed)

| Field | Value |
|-------|-------|
| `file.name` | Filename without extension |
| `file.path` | Full path including folder |
| `file.folder` | Folder path |
| `file.ext` | File extension |
| `file.size` | File size in bytes |
| `file.ctime` | Creation date |
| `file.mtime` | Last modified date |
| `file.tags` | All tags (frontmatter + inline) as list |
| `file.etags` | Exact tags (no ancestor expansion) |
| `file.inlinks` | Notes linking TO this note |
| `file.outlinks` | Notes linked FROM this note |
| `file.aliases` | Aliases list |
| `file.day` | Date from filename if it matches date format |

### Explicit fields (from frontmatter)

Any frontmatter property is queryable directly by its key name:
```yaml
---
status: active
priority: high
date: 2025-04-05
rating: 4
---
```
Then: `WHERE status = "active"` and `SORT priority DESC`.

### Inline fields

Set a field value inline in note body:
```
Status:: active
Due:: 2025-04-10
```
Then queryable the same as frontmatter: `WHERE Status = "active"`.

---

## Common useful queries

### All active projects
````
```dataview
TABLE date, status, priority
FROM "Projects"
WHERE status = "active"
SORT priority DESC
```
````

### Tasks due today or overdue
````
```dataview
TASK
WHERE !completed
AND due <= date(today)
SORT due ASC
```
````

### All uncompleted tasks across vault
````
```dataview
TASK
WHERE !completed
GROUP BY file.link
```
````

### Recently modified notes (last 7 days)
````
```dataview
LIST
FROM ""
WHERE file.mtime >= date(today) - dur(7 days)
SORT file.mtime DESC
LIMIT 20
```
````

### All book notes with rating
````
```dataview
TABLE author, rating, status
FROM #book OR "Books"
SORT rating DESC
```
````

### Notes created this week
````
```dataview
LIST
FROM ""
WHERE file.ctime >= date(today) - dur(7 days)
SORT file.ctime DESC
```
````

### Orphan notes (nothing links to them)
````
```dataview
LIST
FROM ""
WHERE length(file.inlinks) = 0
AND file.name != "Home"
SORT file.name ASC
```
````

### All people notes (personal CRM)
````
```dataview
TABLE company, last-contact, relationship
FROM "People"
SORT last-contact DESC
```
````

### Reading list (unread books)
````
```dataview
TABLE author, genre, date-added
FROM "Books"
WHERE status = "to-read"
SORT date-added DESC
```
````

### Meeting notes from last 30 days
````
```dataview
LIST
FROM "Meetings"
WHERE file.ctime >= date(today) - dur(30 days)
SORT file.ctime DESC
```
````

### Notes by tag count (most-tagged topics)
````
```dataview
TABLE length(file.tags) AS "Tag count", file.tags
FROM ""
WHERE length(file.tags) > 3
SORT length(file.tags) DESC
```
````

### Habit tracker from daily notes
````
```dataview
TABLE exercised, meditated, read
FROM "Daily"
WHERE file.day >= date(today) - dur(7 days)
SORT file.day DESC
```
````
(Requires daily notes to have boolean frontmatter fields like `exercised: true`)

### Calendar view of daily notes
````
```dataview
CALENDAR file.day
FROM "Daily"
```
````

---

## Inline queries

Render a single value inline in note body text.

**Syntax:** `` `= expression` `` (backtick + = sign)

```markdown
Today is `= date(today)`.
This note was created `= this.file.ctime`.
Days since created: `= date(today) - this.file.ctime`.
Active projects: `= length(filter(dv.pages('"Projects"'), p => p.status = "active"))`.
```

---

## Dataviewjs overview

Write JavaScript for complex queries. Use when DQL isn't expressive enough.

````
```dataviewjs
// List all notes with more than 10 backlinks
const notes = dv.pages()
  .where(p => p.file.inlinks.length > 10)
  .sort(p => p.file.inlinks.length, 'desc');
dv.table(["Note", "Backlinks"], 
  notes.map(p => [p.file.link, p.file.inlinks.length]));
```
````

**Key dataviewjs APIs:**
- `dv.pages("source")` — query pages
- `dv.current()` — current note
- `dv.table(headers, rows)` — render table
- `dv.list(items)` — render list
- `dv.taskList(tasks)` — render tasks
- `dv.header(level, text)` — render heading

---

## Performance tips

- Dataview re-runs all queries on every vault change — many complex queries slow Obsidian
- Use specific `FROM "folder"` instead of `FROM ""` (all notes) when possible
- Add `LIMIT 50` to large result queries
- Avoid `length(file.inlinks)` on large vaults — expensive
- Cache-heavy operations: disable auto-refresh in Dataview settings and refresh manually if needed
