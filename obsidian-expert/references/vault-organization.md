# Vault Organization Reference

## Table of Contents
1. [Philosophy: folders vs links vs tags](#philosophy-folders-vs-links-vs-tags)
2. [PARA method](#para-method)
3. [Zettelkasten / slip-box method](#zettelkasten--slip-box-method)
4. [Maps of Content (MOC)](#maps-of-content-moc)
5. [Johnny Decimal system](#johnny-decimal-system)
6. [Inbox / capture workflow](#inbox--capture-workflow)
7. [Note types and naming conventions](#note-types-and-naming-conventions)
8. [Recommended starter structure](#recommended-starter-structure)

---

## Philosophy: folders vs links vs tags

Obsidian supports three organization primitives — use them for different jobs:

| Tool | Best for | Avoid using for |
|------|---------|----------------|
| **Folders** | Broad, stable categories (Projects, Archive, Daily) | Fine-grained topic classification |
| **Links** | Expressing conceptual relationships between ideas | Simple containment (use folders for that) |
| **Tags** | Cross-cutting status/type labels (`#status/active`, `#type/book`) | Replacing folders or links |

**Core principle:** Folders contain; links connect; tags label.

A note about "project budget" belongs in the `Projects/Website Redesign/` folder (folder = container), links to `[[Q2 Financial Overview]]` (link = relationship), and is tagged `#status/in-progress #type/reference` (tag = label).

**Folder-heavy approach:** More familiar to filesystem users. Better for people who want clear hierarchy. Risk: over-nesting; notes get buried; hard to link across folders.

**Link-heavy approach:** Fewer folders (maybe just 4–5 top-level). Notes connect via links. Graph becomes meaningful. Risk: harder to browse if you don't know what you're looking for.

**Practical sweet spot:** 4–6 top-level folders for broad areas + extensive linking within and across them + tags for status/type only.

---

## PARA method

Developed by Tiago Forte. Four top-level folders covering everything:

```
📁 1 - Projects/        ← Active projects with a defined outcome and deadline
📁 2 - Areas/           ← Ongoing responsibilities with no end date
📁 3 - Resources/       ← Topics you're interested in for future reference
📁 4 - Archive/         ← Inactive items from the other three categories
```

**Projects** = has a goal + deadline. "Redesign website", "Write Q1 report", "Plan vacation"
**Areas** = ongoing standard to maintain. "Health", "Finances", "Career", "Relationships"
**Resources** = topics you care about. "Product design", "Cooking", "Note-taking", "Python"
**Archive** = completed projects, retired areas, outdated resources

**The key question for filing:** "Is this note useful for a current active project or ongoing responsibility?" If yes, put it close to that work. If no, Archive or Resources.

**Obsidian PARA tips:**
- Add a number prefix (1, 2, 3, 4) so folders sort in PARA order
- Create a project note for each project in `1 - Projects/` that serves as the hub
- Weekly: move completed project folders to `4 - Archive/`
- Don't over-file: many notes don't need to be in a specific project or area — put them in Resources

---

## Zettelkasten / slip-box method

Developed by Niklas Luhmann (German sociologist). Produces a web of interconnected atomic ideas.

**Three note types:**

| Type | Description | Example |
|------|-------------|---------|
| **Fleeting notes** | Raw captures — quick, messy, temporary | "shower thought: deadlines create focus" |
| **Literature notes** | Summary of source material in your own words | Notes from a book chapter |
| **Permanent notes** | Single atomic idea, written clearly, linked to other permanents | "Artificial deadlines improve focus by creating urgency without real consequence" |

**Atomic note principle:** One idea per note. If a note covers two ideas, split it. Notes should be understandable without reading their source.

**Linking in Zettelkasten:** Every permanent note should link to at least 2–3 others. Don't file by topic — link by idea relationship.

**Unique IDs:** Classic Zettelkasten uses IDs like `202504051430` (timestamp). Obsidian's Unique Note Creator plugin generates these. Use in filenames: `202504051430 Deadlines improve focus.md`.

**Obsidian Zettelkasten structure:**
```
📁 0 - Inbox/           ← Fleeting notes awaiting processing
📁 1 - Literature/      ← Source-based notes
📁 2 - Permanent/       ← Atomic permanent notes (the main collection)
📁 3 - MOCs/            ← Maps of Content (indexes into the permanent notes)
📁 4 - Projects/        ← Output projects using permanent notes
📁 5 - Archive/
```

**Practical note:** Pure Zettelkasten is high-maintenance. Most people benefit from the *principles* (atomic notes, linking by idea) without strict implementation.

---

## Maps of Content (MOC)

Coined by Nick Milo. An MOC is a note that collects and organizes links to related notes — an index or hub.

**MOC vs folder:** A folder is a container with hard boundaries. An MOC is a note that can link to notes anywhere in the vault. One note can appear in multiple MOCs; it can only be in one folder.

**MOC structure:**
```markdown
# Productivity MOC

## Principles
- [[The one thing that matters most each day]]
- [[Energy management over time management]]
- [[Deep work requires protected blocks]]

## Systems
- [[My weekly review process]]
- [[Task capture workflow]]
- [[PARA in my vault]]

## Tools
- [[Obsidian setup notes]]
- [[Notion for team projects]]

## Resources
- [[Deep Work - Book Notes]]
- [[Getting Things Done - Book Notes]]
```

**Types of MOCs:**
- **Topic MOC**: `Productivity MOC`, `Health MOC`, `Finance MOC`
- **Project MOC**: Hub for all notes related to one project
- **Index MOC** (Home note): Top-level navigation for the whole vault

**Home note / dashboard:** A single note (often called `Home` or `Dashboard`) that links to all top-level MOCs. Set as homepage with the Homepage plugin. Contains your most-used links, active projects, and possibly Dataview queries.

**MOC creation trigger:** When you notice 5+ notes linking to each other around a common theme, create an MOC to surface and organize those connections.

---

## Johnny Decimal system

A numeric ID system for files and folders. Less common in Obsidian but useful for people who like numbered structure.

```
10-19 Life admin
  11 Health
  12 Finance
  13 Legal
20-29 Work
  21 Projects
  22 Reference
```

Each note gets an ID: `11.01 Dental records.md`, `12.03 Tax 2024.md`.

**Useful for:** Precise referencing in conversations ("see 12.03"), consistent naming, people who think numerically.

**Less useful for:** Dynamic knowledge work where categories shift.

---

## Inbox / capture workflow

**The inbox problem:** Without a defined inbox, captures end up in random places or don't happen at all.

**Inbox setup:**
1. Create `0 - Inbox/` folder (or `_Inbox/` to sort to top)
2. Configure QuickAdd Capture to append to an `Inbox.md` note, OR set new notes to land in the inbox folder
3. Process inbox regularly (daily or weekly)

**Processing a captured note:**
1. Read it — do you still care? Delete if not.
2. Is it one clear idea? Split if not (Note Refactor plugin helps).
3. Write it in your own words if it's from a source.
4. Link it to at least 2 existing notes.
5. File it in the appropriate folder/MOC.
6. Delete the fleeting capture.

**QuickAdd capture command:** Creates a command that appends text to a specific note with one hotkey. Example: `Alt+C` → type a thought → it appends to `Inbox.md` with a timestamp.

---

## Note types and naming conventions

**Naming approaches:**

| Approach | Example | Good for |
|----------|---------|---------|
| Plain descriptive title | `Deadlines improve focus` | Permanent/concept notes |
| Timestamp prefix | `202504051430 Deadlines improve focus` | Zettelkasten |
| Date prefix | `2025-04-05 Meeting with client` | Meeting/daily notes |
| Type prefix | `📚 Deep Work - Book Notes` | Source notes |
| Folder-based (no prefix) | `Projects/Website Redesign/Brief.md` | Project notes |

**Recommended frontmatter fields:**
```yaml
---
title: Note title
date: 2025-04-05
created: 2025-04-05
tags: []
aliases: []
status: draft          # draft | active | reference | archived
type: note             # note | project | moc | daily | book | meeting | person
---
```

**Type field** lets you filter in Dataview: `WHERE type = "book"` shows all book notes.
**Status field** lets you track progress: `WHERE status = "draft"` surfaces notes to finish.

---

## Recommended starter structure

A practical, flexible starting vault for most people:

```
📁 0 - Inbox/           ← Raw captures, process regularly
📁 1 - Daily/           ← Daily notes (YYYY-MM-DD.md)
📁 2 - Projects/        ← One subfolder per active project
📁 3 - Areas/           ← Ongoing: Health, Finance, Career, etc.
📁 4 - Resources/       ← Reference, reading notes, topics
📁 5 - Archive/         ← Completed/inactive from above
📁 _Templates/          ← All templates (prefixed with _ to sort to top/bottom)
📁 _Attachments/        ← Images and files
```

**Start simple.** Add complexity only when you feel friction. Many people start with 3 folders and evolve from there. The worst vault is the one you spent two weeks organizing instead of using.
