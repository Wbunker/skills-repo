# Templates and Daily Notes Reference

## Table of Contents
1. [Core Templates plugin](#core-templates-plugin)
2. [Templater plugin](#templater-plugin)
3. [Daily Notes setup](#daily-notes-setup)
4. [Periodic Notes (weekly, monthly, quarterly, yearly)](#periodic-notes)
5. [Daily note template designs](#daily-note-template-designs)
6. [Folder templates with Templater](#folder-templates-with-templater)
7. [Core Templates vs Templater — when to use each](#core-templates-vs-templater)

---

## Core Templates plugin

Enable: Settings → Core Plugins → Templates.

**Setup:**
1. Create a folder for templates (e.g., `_Templates/` or `00-Meta/Templates/`)
2. Settings → Templates → Template folder location → point to that folder
3. Create `.md` files in the folder — each is a template

**Inserting a template:** Open a note → Command Palette → "Templates: Insert template" → pick template. Or assign a hotkey.

**Core template variables:**

| Variable | Output |
|----------|--------|
| `{{date}}` | Today's date in default format |
| `{{date:YYYY-MM-DD}}` | Date in custom format |
| `{{time}}` | Current time |
| `{{time:HH:mm}}` | Time in custom format |
| `{{title}}` | The current note's filename (without extension) |

**Date format tokens** (Moment.js): `YYYY` year, `MM` month, `DD` day, `ddd` short weekday, `dddd` full weekday, `HH` 24h hour, `mm` minutes.

**Limitation:** Core Templates inserts static text. It cannot prompt for input, run logic, or auto-apply on note creation.

---

## Templater plugin

The power upgrade for templates. Install: Community Plugins → "Templater" (by SilentVoid13).

**Setup:**
1. Settings → Templater → Template folder location (same folder as core Templates, or a new one)
2. Enable "Trigger Templater on new file creation" for auto-apply
3. Optionally enable "Automatic jump to cursor" to land cursor inside template

**Syntax:** Uses `<% %>` tags (not `{{ }}`). Always use Templater syntax in Templater templates.

### Common Templater functions

**Date and time:**
```
<% tp.date.now("YYYY-MM-DD") %>           ← today
<% tp.date.now("ddd, MMM D YYYY") %>      ← Mon, Apr 5 2025
<% tp.date.yesterday("YYYY-MM-DD") %>     ← yesterday
<% tp.date.tomorrow("YYYY-MM-DD") %>      ← tomorrow
<% tp.date.now("YYYY-MM-DD", 7) %>        ← 7 days from now
<% tp.date.now("YYYY-[W]ww") %>           ← week number: 2025-W14
```

**File info:**
```
<% tp.file.title %>                        ← note filename without extension
<% tp.file.folder() %>                     ← folder path
<% tp.file.creation_date("YYYY-MM-DD") %> ← when file was created
<% tp.file.last_modified_date() %>         ← last modified
<% tp.file.path() %>                       ← full file path
```

**Cursor placement:**
```
<% tp.file.cursor() %>                     ← place cursor here after insertion
<% tp.file.cursor(1) %>                    ← numbered cursor stop (tab to next)
```

**User input:**
```
<% tp.system.prompt("Enter title") %>      ← shows input dialog
<% tp.system.suggester(["Option A", "Option B"], ["a", "b"]) %>  ← dropdown
```

**Clipboard:**
```
<% tp.system.clipboard() %>               ← pastes clipboard content
```

**Conditional logic:**
```
<% if (tp.file.folder() === "Projects") { %>
## Status
<% } %>
```

**Linking:**
```
[[<% tp.date.now("YYYY-MM-DD") %>]]       ← link to today's daily note
```

### Example Templater note template
```markdown
---
title: <% tp.file.title %>
date: <% tp.date.now("YYYY-MM-DD") %>
tags: []
---

# <% tp.file.title %>

<% tp.file.cursor(1) %>
```

---

## Daily Notes setup

**Option A: Core Daily Notes plugin**
1. Enable Settings → Core Plugins → Daily Notes
2. Settings → Daily Notes:
   - **Date format**: `YYYY-MM-DD` (ISO) or `YYYY-MM-DD dddd` (includes weekday)
   - **New file location**: folder like `Daily/` or `Journal/YYYY/`
   - **Template file**: path to your daily note template
   - **Open on startup**: toggle on/off

**Option B: Periodic Notes plugin** (recommended — more flexible)
Replaces core Daily Notes. Adds weekly, monthly, quarterly, yearly notes.
Install: "Periodic Notes" (by Liam Cain).

**Periodic Notes setup:**
- Enable daily, weekly, monthly notes per section
- Set format, folder, and template for each type
- Pairs with Calendar plugin for sidebar navigation

**Daily note folder structure options:**
- `Daily/2025-04-05.md` — flat folder, easy to manage
- `Daily/2025/04/2025-04-05.md` — nested by year/month, cleaner long-term
- `Journal/2025-04-05 Saturday.md` — filename includes weekday

---

## Periodic Notes

### Weekly note
- Format suggestion: `YYYY-[W]ww` → `2025-W14`
- Template: pulls in the week's daily notes, sets weekly goals/review
- Opened from Calendar plugin by clicking week number

### Monthly note
- Format suggestion: `YYYY-MM` → `2025-04`
- Template: monthly goals, habit tracker summary, key events

### Quarterly note
- Format suggestion: `YYYY-[Q]Q` → `2025-Q2`
- Template: quarterly goals (OKRs), project list, major decisions

### Yearly note
- Format suggestion: `YYYY` → `2025`
- Template: year theme, yearly goals, major life events, reading list

---

## Daily note template designs

### Minimal daily note
```markdown
---
date: <% tp.date.now("YYYY-MM-DD") %>
tags: [daily]
---

# <% tp.date.now("ddd, MMM D YYYY") %>

## Focus
- [ ] <% tp.file.cursor(1) %>

## Notes

## Journal

```

### Life management daily note
```markdown
---
date: <% tp.date.now("YYYY-MM-DD") %>
tags: [daily]
week: "[[<% tp.date.now("YYYY-[W]ww") %>]]"
---

# <% tp.date.now("dddd, MMMM D, YYYY") %>

## Top 3 priorities
- [ ] 
- [ ] 
- [ ] 

## Schedule / time blocks


## Tasks due today
```tasks
due today
not done
sort by priority
```

## Notes & captures


## End of day reflection
**What went well:**

**What could improve:**

**Grateful for:**

```

### Weekly review template
```markdown
---
date: <% tp.date.now("YYYY-MM-DD") %>
week: <% tp.date.now("[W]ww") %>
tags: [weekly]
---

# Week <% tp.date.now("ww") %> — <% tp.date.now("YYYY") %>

## Review: last week
**Projects moved forward:**

**Goals progress:**

**What to carry forward:**

## Plan: this week
**Theme / focus:**

**Key deliverables:**

| Day | Focus |
|-----|-------|
| Mon | |
| Tue | |
| Wed | |
| Thu | |
| Fri | |

## Habit review
| Habit | M | T | W | T | F | S | S |
|-------|---|---|---|---|---|---|---|
| Exercise | | | | | | | |
| Reading | | | | | | | |

## Notes

```

---

## Folder templates with Templater

Auto-apply a template when a note is created in a specific folder.

**Setup:** Settings → Templater → Folder Templates → Add:
- Folder: `Projects/`
- Template: `_Templates/project.md`

Now every new note created inside `Projects/` automatically gets the project template applied.

**Common folder → template mappings:**
| Folder | Template |
|--------|---------|
| `Daily/` | daily-note.md |
| `Projects/` | project.md |
| `Books/` | book-note.md |
| `People/` | person.md |
| `Meetings/` | meeting.md |

---

## Core Templates vs Templater

| Feature | Core Templates | Templater |
|---------|---------------|-----------|
| Basic text insertion | ✓ | ✓ |
| Date/time variables | Basic | Full Moment.js |
| Auto-apply on creation | ✗ | ✓ |
| Folder-based auto-templates | ✗ | ✓ |
| User input prompts | ✗ | ✓ |
| JavaScript logic | ✗ | ✓ |
| File/folder metadata | ✗ | ✓ |
| Complexity | None | Moderate |

**Recommendation:** Install Templater and use it exclusively. Disable core Templates if you use Templater — having both causes confusion about which template syntax to use.
