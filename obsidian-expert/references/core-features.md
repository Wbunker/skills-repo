# Obsidian Core Features Reference

## Table of Contents
1. [Vault and file structure](#vault-and-file-structure)
2. [Linking notes](#linking-notes)
3. [Backlinks and outgoing links](#backlinks-and-outgoing-links)
4. [Graph view](#graph-view)
5. [Properties (frontmatter)](#properties-frontmatter)
6. [Tags](#tags)
7. [Search](#search)
8. [Canvas](#canvas)
9. [Workspaces](#workspaces)
10. [Hotkeys and command palette](#hotkeys-and-command-palette)

---

## Vault and file structure

A **vault** is any folder on disk that Obsidian opens. Inside:
- `.md` files = notes
- `.obsidian/` = config folder (plugins, themes, hotkeys, snippets) — do not manually edit unless you know what you're doing
- Attachments folder (configurable) = images, PDFs, other files

Notes are plain markdown — readable and editable in any text editor outside Obsidian. This is intentional: no lock-in.

**Creating notes:**
- `Ctrl/Cmd+N` — new note in current folder
- Click folder → New note
- Type a `[[wikilink]]` to a non-existent note, then click it to create
- Quick Switcher (`Ctrl/Cmd+O`) — type a name; if no match, creates new

**Renaming a note:** F2 or right-click → Rename. Obsidian automatically updates all wikilinks to that note across the vault.

**Moving notes:** Drag in file explorer, or right-click → Move to folder. Links update automatically.

---

## Linking notes

The core power of Obsidian. Links create relationships between ideas.

| Link type | Syntax | Result |
|-----------|--------|--------|
| Basic wikilink | `[[Note Name]]` | Links to that note |
| Aliased link | `[[Note Name\|Display text]]` | Shows "Display text", links to note |
| Heading link | `[[Note Name#Heading]]` | Links to specific heading |
| Block link | `[[Note Name^blockid]]` | Links to specific paragraph/block |
| Embed (transclude) | `![[Note Name]]` | Renders note content inline |
| Embed section | `![[Note Name#Heading]]` | Renders just that section inline |
| Embed block | `![[Note Name^blockid]]` | Renders just that block inline |
| Standard markdown link | `[text](note.md)` | Also works; less common in Obsidian |

**Creating block IDs:** Type `^blockid` at the end of any paragraph (no space before `^`). Then reference with `[[Note^blockid]]`. Obsidian auto-generates IDs if you use autocomplete.

**Link autocomplete:** Type `[[` and start typing — Obsidian searches all note titles and shows a dropdown.

**Unresolved links** (links to non-existent notes) show in a different color. Click to create the note. These are intentional placeholders — write the link first, create the note later.

---

## Backlinks and outgoing links

**Backlinks panel** (right sidebar): Shows every note that links TO the current note. Two sections:
- **Linked mentions**: Notes with explicit `[[wikilinks]]` to this note
- **Unlinked mentions**: Notes that mention the title text but don't have a formal link

Backlinks are how you discover unexpected connections. A note about "focus" appearing in your project notes, health notes, and reading notes reveals a theme.

**Outgoing links panel** (right sidebar): Shows all links FROM the current note. Useful for seeing what's connected and spotting unresolved links.

**Hover preview:** Hover over any link while holding `Ctrl/Cmd` to preview the linked note without opening it. Or enable "Page Preview" core plugin and just hover.

---

## Graph view

Visualizes notes as nodes and links as edges. Open with `Ctrl/Cmd+G`.

**Controls:**
- Scroll to zoom; drag to pan; drag nodes to rearrange (temporary)
- Click a node to open that note
- Search/filter box at top

**Filters panel:**
- **Filters**: Show/hide notes by search query, tags, or path
- **Groups**: Color-code nodes by tag, folder, or path (e.g., all `#project` notes = blue)
- **Display**: Toggle orphans (unlinked notes), tags, attachments
- **Forces**: Adjust node spacing, link distance, repulsion

**Local graph:** Right-click a note → Open local graph. Shows only that note and its directly connected neighbors. Depth slider (1–5) expands the neighborhood. Far more useful day-to-day than the full global graph.

**Global graph use cases:** Spot clusters of related notes, identify orphan notes (nothing links to them), see your most-linked hub notes (bigger nodes).

**Note:** The graph is beautiful but not a daily driver. The backlinks panel is more actionable.

---

## Properties (frontmatter)

YAML metadata at the very top of a note, between `---` delimiters. Obsidian 1.4+ added a **Properties panel** UI — click the properties icon or use `Ctrl/Cmd+;` to open without editing raw YAML.

```yaml
---
title: My Note
tags:
  - project
  - work
aliases:
  - My Note Alias
date: 2025-04-05
status: active
priority: high
---
```

**Built-in property fields Obsidian recognizes:**
| Field | Purpose |
|-------|---------|
| `tags` | Searchable tags; shows in Tag Pane |
| `aliases` | Alternative names for this note; included in link search |
| `cssclasses` | Apply CSS classes to the note view |

**Custom properties** are supported — use any key/value. Dataview and other plugins can query them.

**Property types** (Obsidian 1.4+): text, list, number, checkbox, date, date & time, link. Set type in Properties panel → right-click property name.

**Accessing properties:** Properties panel (sidebar), raw YAML (toggle source mode), Dataview queries, search with `[property:value]`.

---

## Tags

Two places to add tags:
- **Frontmatter**: `tags: [project, work]` or `tags:\n  - project\n  - work`
- **Inline**: `#tag` anywhere in note body

**Nested tags:** `#area/health`, `#area/finance`, `#project/active`. Creates hierarchy in Tag Pane.

**Tag Pane** (core plugin): Shows all tags in vault with note count. Click to search notes with that tag.

**Search by tag:** `tag:#project` in search bar, or `FROM #project` in Dataview.

**Tags vs folders vs links:** See [vault-organization.md](vault-organization.md) for when to use each.

---

## Search

Open with `Ctrl/Cmd+F` (in-note) or `Ctrl/Cmd+Shift+F` (vault-wide search).

**Search operators:**

| Operator | Example | Matches |
|----------|---------|---------|
| `tag:` | `tag:#project` | Notes with that tag |
| `file:` | `file:meeting` | Notes with "meeting" in filename |
| `path:` | `path:Projects/` | Notes in that folder path |
| `content:` | `content:budget` | Notes with "budget" in body (not title) |
| `line:` | `line:(budget Q4)` | Notes with "budget" and "Q4" on same line |
| `section:` | `section:heading text` | Matches within a heading section |
| `block:` | `block:quote text` | Matches within a block |
| `task:` | `task:todo item` | Matches within task lines |
| `[property:value]` | `[status:active]` | Notes with matching frontmatter property |
| Boolean | `meeting AND budget` | Both terms |
| | `meeting OR standup` | Either term |
| | `-cancelled` | Exclude term |
| Regex | `/regexpattern/` | Regex match |

**Saved searches:** Click the bookmark icon next to a search to save it. Appears in Bookmarks panel.

---

## Canvas

A free-form visual workspace — infinite whiteboard. Core plugin, enable in Settings.

Open: `Ctrl/Cmd+Shift+N` (Canvas) or Create new canvas from file explorer.

**Canvas elements:**
- **Notes**: Embed any vault note as a card (changes sync back to the note)
- **Cards**: Standalone text that only exists on the canvas
- **Files**: Images, PDFs, videos embedded directly
- **Links (arrows)**: Connect cards with labeled directional arrows; useful for flowcharts, mind maps

**Canvas use cases:**
- Mind-mapping projects or ideas
- Visual project overview (connect meeting notes, tasks, goals)
- Concept mapping (linking ideas with directional arrows showing relationships)
- Storyboarding or planning sequences
- Visual MOC (Map of Content) — overview of a topic area

**Canvas groups:** Select multiple elements → right-click → Group. Adds a labeled container.

---

## Workspaces

Core plugin. Save and restore window layouts (which notes are open, sidebar state, pane arrangement).

Enable: Settings → Core Plugins → Workspaces.

**Use cases:** Switch between "writing mode" (single focused pane) and "research mode" (multiple panes with references open). Save a "morning review" workspace with daily note + tasks + calendar.

**Commands:** "Manage workspaces", "Load workspace", "Save workspace" — accessible via Command Palette.

---

## Hotkeys and command palette

**Command Palette:** `Ctrl/Cmd+P` — search and run any Obsidian command. The fastest way to access anything.

**Essential default hotkeys:**

| Action | Hotkey |
|--------|--------|
| New note | `Ctrl/Cmd+N` |
| Quick Switcher (open note) | `Ctrl/Cmd+O` |
| Command Palette | `Ctrl/Cmd+P` |
| Search vault | `Ctrl/Cmd+Shift+F` |
| Toggle reading/edit view | `Ctrl/Cmd+E` |
| Open graph | `Ctrl/Cmd+G` |
| Toggle left sidebar | `Ctrl/Cmd+\` |
| Navigate back | `Ctrl/Cmd+Alt+Left` |
| Navigate forward | `Ctrl/Cmd+Alt+Right` |
| Toggle bold | `Ctrl/Cmd+B` |
| Toggle italics | `Ctrl/Cmd+I` |
| Insert link | `Ctrl/Cmd+K` |
| Fold all headings | `Ctrl/Cmd+Shift+→` |

**Custom hotkeys:** Settings → Hotkeys. Search for any command and assign a key combo.

**Split panes:** Drag a tab to the edge of the editor to split. `Ctrl/Cmd+\` splits horizontally. Right-click a tab for split options.
