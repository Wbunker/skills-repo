# Obsidian Plugins Reference

## Table of Contents
1. [Core plugins](#core-plugins)
2. [Community plugins — essential](#community-plugins--essential)
3. [Community plugins — productivity and life management](#community-plugins--productivity-and-life-management)
4. [Community plugins — appearance and UI](#community-plugins--appearance-and-ui)
5. [Plugin installation](#plugin-installation)

---

## Core plugins

Built-in plugins — enable/disable in Settings → Core Plugins. All are off by default except a few.

| Plugin | What it does |
|--------|-------------|
| **Backlinks** | Shows what notes link to the current note; linked + unlinked mentions |
| **Bookmarks** | Bookmark notes, headings, searches, graph views, blocks for quick access |
| **Canvas** | Infinite whiteboard for visual note-making; cards, embeds, arrows |
| **Command palette** | `Ctrl/Cmd+P` search for any command |
| **Daily notes** | Creates a dated note each day with optional template; opens on startup |
| **File recovery** | Auto-snapshots every 5 min; recover deleted/overwritten notes (up to 90 days) |
| **Files** | Core file explorer sidebar |
| **Format converter** | One-time conversion from Roam/Bear markdown formats |
| **Graph view** | Global and local graph visualization |
| **Note composer** | Merge notes or extract selection into a new note |
| **Outgoing links** | Shows links FROM current note; spot unresolved links |
| **Outline** | Shows heading structure of current note in sidebar |
| **Page preview** | Hover over a link to preview note content |
| **Properties view** | Browse all properties across vault |
| **Quick switcher** | `Ctrl/Cmd+O` fuzzy search to open any note |
| **Random note** | Opens a random vault note — good for rediscovering old notes |
| **Search** | Vault-wide full text search |
| **Slash commands** | Type `/` in editor to trigger commands inline |
| **Slides** | Turn a note into a presentation using `---` slide breaks |
| **Sync** | Official Obsidian Sync (paid); see sync-mobile-publish.md |
| **Tag pane** | Browse all tags; click to search |
| **Templates** | Basic template insertion with `{{date}}`, `{{time}}`, `{{title}}` |
| **Unique note creator** | Creates notes with a timestamp-based unique ID (Zettelkasten style) |
| **Word count** | Shows word/character count in status bar |
| **Workspaces** | Save/restore window layout configurations |

---

## Community plugins — essential

These are the highest-impact community plugins. Most serious Obsidian users install at least Dataview and Templater.

### Dataview
Query your vault like a database. Write `TABLE`, `LIST`, `TASK`, or `CALENDAR` queries in code blocks to dynamically display notes matching criteria.

See [dataview.md](dataview.md) for full query reference.

**Install:** Community Plugins → search "Dataview" (by Michael Brenan)

---

### Templater
Advanced templating engine. Replaces core Templates for most users. Supports JavaScript expressions, file operations, date formatting, user prompts, folder-based auto-templates.

See [templates-and-daily-notes.md](templates-and-daily-notes.md) for syntax and setup.

**Key advantage over core Templates:** Dynamic content at note creation time (not just static text).

**Install:** "Templater" (by SilentVoid13)

---

### Tasks
Manages tasks across the entire vault. Tracks due dates, recurrence, completion, priority. Renders task queries anywhere.

**Task format:**
```
- [ ] Task description 📅 2025-04-10 🔁 every week
- [x] Completed task ✅ 2025-04-05
```

**Emoji fields:** 📅 due, ⏳ scheduled, 🛫 start, ✅ done, 🔁 recurrence, ⏫ high priority, 🔼 medium, 🔽 low

**Query block:**
````
```tasks
not done
due today
sort by priority
```
````

**Install:** "Tasks" (by Clare Macrae / obsidian-tasks-group)

---

### Periodic Notes
Extends Daily Notes to support weekly, monthly, quarterly, and yearly notes — each with its own template and folder. Integrates with Calendar plugin for navigation.

See [templates-and-daily-notes.md](templates-and-daily-notes.md).

**Install:** "Periodic Notes" (by Liam Cain)

---

### Calendar
Renders a monthly calendar in the sidebar. Clicking a date opens/creates the daily note for that day. Works with Periodic Notes for week/month navigation.

**Install:** "Calendar" (by Liam Cain)

---

### QuickAdd
Power tool for rapid note creation. Four action types:
- **Template**: Create a note from a template with one command
- **Capture**: Append or prepend text to a specific note instantly (great for inbox)
- **Macro**: Chain multiple actions
- **Multi**: Menu of multiple QuickAdd choices

**Best use:** `Capture to Inbox` command — instant capture without leaving current note.

**Install:** "QuickAdd" (by Christian Houmann)

---

### Excalidraw
Full Excalidraw drawing tool embedded in Obsidian. Create diagrams, sketches, mind maps as `.excalidraw` files that live in your vault. Link to vault notes from within drawings.

**Install:** "Excalidraw" (by Zsolt Viczian)

---

### Obsidian Git
Auto-commits vault to a Git repository on a schedule. Provides version history, backup, and optional sync via GitHub/GitLab (free alternative to Obsidian Sync).

**Setup:** Initialize git repo in vault folder, configure remote, set auto-commit interval (e.g., every 10 min).

**Install:** "Obsidian Git" (by Vinzent Hofer)

---

## Community plugins — productivity and life management

### Kanban
Markdown-based Kanban board. Each board is a `.md` file with cards in lists. Cards can be notes, tasks, or plain text. Drag to reorder.

**Install:** "Kanban" (by mgmeyers)

---

### Projects (formerly DB Folder)
Spreadsheet/database view of notes in a folder. Define columns from frontmatter properties. Multiple views: table, board, calendar, gallery. Good for book lists, project tracking, CRM.

**Install:** "Projects" (by Marcus Olsson)

---

### Commander
Add custom commands to the toolbar, ribbon, context menu, or status bar. Hide commands you never use. Rearrange the ribbon.

**Install:** "Commander" (by phibr0)

---

### Breadcrumbs
Creates hierarchical navigation between notes using frontmatter fields (`up`, `down`, `same`, `next`, `prev`). Renders a breadcrumb trail at top of notes. Good for structured note hierarchies.

**Install:** "Breadcrumbs" (by SkepticMystic)

---

### Note Refactor
Extract a selection or a heading's content into a new note with one command. Auto-replaces the selection with a link to the new note.

**Great for:** Splitting large notes when a topic grows big enough to deserve its own note.

**Install:** "Note Refactor" (by James Lynch)

---

### Advanced Tables
Better markdown table editing — tab to move between cells, auto-format, formula support, export to CSV.

**Install:** "Advanced Tables" (by Tony Grosinger)

---

### Linter
Auto-formats notes on save: consistent YAML, heading levels, whitespace, list formatting, date fields. Configurable rules.

**Install:** "Linter" (by platers)

---

### Metadata Menu
Manage frontmatter properties with a GUI. Define property types and dropdown options per note type. Creates a button/menu for editing metadata without touching YAML.

**Install:** "Metadata Menu" (by mdelobelle)

---

### Homepage
Sets a specific note or Canvas as the home page that opens when Obsidian launches. Great for a dashboard note.

**Install:** "Homepage" (by mirnovov)

---

### Banners
Add a banner image (hero image) to the top of a note using a frontmatter `banner` property pointing to an image path or URL.

**Install:** "Banners" (by noatpad)

---

## Community plugins — appearance and UI

### Style Settings
Required by many themes and plugins to expose customization settings. Install alongside any theme that lists it as a dependency.

**Install:** "Style Settings" (by mgmeyers)

---

### Minimal Theme Settings
If using Minimal theme (most popular Obsidian theme), this companion plugin exposes color, layout, and focus mode options.

---

### Popular themes
- **Minimal** — clean, highly customizable, wide community support
- **Things** — inspired by Things 3 task manager aesthetic
- **AnuPpuccin** — Catppuccin color palette, colorful and modern
- **Sanctum** — calm, focused writing aesthetic
- **Shimmering Focus** — distraction-free; hides UI when not in use

Install themes: Settings → Appearance → Themes → Manage.

---

## Plugin installation

1. Settings → Community Plugins
2. Turn off Safe Mode (one-time)
3. Click Browse
4. Search plugin name → Install → Enable

**Plugin data:** Stored in `.obsidian/plugins/[plugin-name]/`. Safe to back up.

**Updating plugins:** Settings → Community Plugins → Check for updates (or enable auto-update).

**Troubleshooting:** If Obsidian breaks, start with Safe Mode (`--safe` flag or hold Shift on launch) to disable all plugins, then re-enable one by one.
