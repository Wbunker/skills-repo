---
name: obsidian-expert
description: >
  Expert knowledge of Obsidian — the local-first markdown note-taking and personal
  knowledge management (PKM) app. Use when the user asks about: setting up or
  organizing an Obsidian vault, linking notes and using the graph view, core or
  community plugins (Dataview, Templater, Tasks, Periodic Notes, QuickAdd, etc.),
  templates and daily notes, vault organization strategies (PARA, Zettelkasten,
  MOC), syncing across devices, Obsidian mobile, Obsidian Publish, building a
  Second Brain or PKM system, capturing and processing information, habit tracking,
  project management, reading notes, meeting notes, or any other Obsidian feature
  or workflow.
---

# Obsidian Expert

Obsidian is a local-first markdown editor where all notes are plain `.md` files
in a folder called a **vault**. Everything is stored locally; no account required
for core use. Notes link to each other with `[[wikilinks]]`, building a
personal knowledge graph.

## Navigation — load the relevant reference file(s)

| Topic | Reference file | Load when... |
|-------|---------------|--------------|
| Core features (linking, backlinks, graph, properties, search, Canvas) | [references/core-features.md](references/core-features.md) | Questions about built-in Obsidian mechanics |
| Core plugins + top community plugins | [references/plugins.md](references/plugins.md) | Questions about what plugins to use or how they work |
| Templates (core + Templater) and Daily/Periodic Notes | [references/templates-and-daily-notes.md](references/templates-and-daily-notes.md) | Setting up templates, daily notes, periodic reviews |
| Vault organization (PARA, Zettelkasten, MOC, folders vs links) | [references/vault-organization.md](references/vault-organization.md) | How to structure a vault, filing decisions |
| Dataview plugin — query syntax and common queries | [references/dataview.md](references/dataview.md) | Building Dataview queries, dashboards, task lists |
| PKM workflows — capture, process, review, Second Brain, life domains | [references/pkm-workflows.md](references/pkm-workflows.md) | Building a PKM system, integrating into daily life |
| Sync, mobile, and Obsidian Publish | [references/sync-mobile-publish.md](references/sync-mobile-publish.md) | Multi-device setup, iOS/Android, publishing notes |

Load only the file(s) relevant to the question. Most questions need one file.

---

## Quick facts

- **Vault**: a folder of `.md` files + a hidden `.obsidian/` config folder — fully portable
- **Wikilinks**: `[[Note Name]]` links notes; `[[Note|alias]]` for display text; `[[Note#Heading]]` for sections; `[[Note^blockid]]` for blocks
- **Properties (frontmatter)**: YAML at top of file; editable via Properties panel (Obsidian 1.4+) or raw YAML; key fields: `tags`, `aliases`, `date`, `created`, `modified`
- **Tags**: `#tag` inline or in frontmatter; nested with `#parent/child`; browsable in Tag Pane
- **Core plugins**: disabled by default — enable in Settings → Core Plugins
- **Community plugins**: Settings → Community Plugins → Browse (requires Safe Mode off)
- **Obsidian Sync**: $10/month official sync with E2E encryption; free alternatives include iCloud, Git, Syncthing
- **Obsidian Publish**: $20/month hosted site from your vault notes
