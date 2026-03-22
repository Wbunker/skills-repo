---
name: vscode-expert
description: Visual Studio Code expert guide for using and customizing VS Code. Use this skill when the user asks about VS Code features, settings, keybindings, themes, extensions, snippets, profiles, tasks, the integrated terminal, debugging, productivity tips, or how to update VS Code. Also use when the user wants to customize their editor, explore the extension marketplace, or learn keyboard shortcuts. Triggers on: VS Code settings, VSCode customization, VS Code extensions, VS Code keybindings, VS Code themes, VS Code profiles, VS Code tasks, VS Code terminal, VS Code update, VS Code CLI, code editor tips.
---

# VS Code Expert

A guide to using, customizing, and maintaining Visual Studio Code.

## Quick Reference

| Topic | Reference File |
|-------|---------------|
| Settings, keybindings, themes, snippets, profiles | [settings-customization.md](references/settings-customization.md) |
| IntelliSense, multi-cursor, tasks, terminal, debugging | [productivity-features.md](references/productivity-features.md) |
| Extension marketplace, management, recommendations | [extensions.md](references/extensions.md) |
| Updates, CLI commands, refreshing this skill | [updates.md](references/updates.md) |

## Core Concepts

### Settings Scopes (highest precedence wins)

```
Policy > Language-specific > Workspace > Remote > User > Default
```

- **User settings** — global, stored in `settings.json` in your VS Code config folder
- **Workspace settings** — `.vscode/settings.json` (per-project; commit to repo for team sharing)

### Essential Keyboard Shortcuts

| Action | Mac | Windows/Linux |
|--------|-----|---------------|
| Command Palette | `⌘⇧P` | `Ctrl+Shift+P` |
| Open Settings UI | `⌘,` | `Ctrl+,` |
| Open Settings JSON | `⌘⇧P` → "Open User Settings (JSON)" | same |
| Keyboard Shortcuts | `⌘K ⌘S` | `Ctrl+K Ctrl+S` |
| Extensions | `⌘⇧X` | `Ctrl+Shift+X` |
| Integrated Terminal | `` Ctrl+` `` | `` Ctrl+` `` |
| Quick Open file | `⌘P` | `Ctrl+P` |
| Go to Symbol | `⌘⇧O` | `Ctrl+Shift+O` |

## Common Tasks

### Open settings
```
⌘, (Mac) / Ctrl+, (Windows/Linux)
```
Or edit JSON directly: `⌘⇧P` → "Preferences: Open User Settings (JSON)"

### Install an extension
```
⌘⇧X → search → Install
```
Or via CLI: `code --install-extension <publisher.extension-id>`

### Apply a theme
```
⌘⇧P → "Preferences: Color Theme" → select
```

### Check for VS Code updates
- **macOS**: Code menu → Check for Updates
- **Windows/Linux**: Help menu → Check for Updates
- See [updates.md](references/updates.md) for update modes and CLI details

## Reading the Reference Files

Load the relevant reference file based on the user's question:

- **Customizing the editor** (settings, keys, themes, snippets, profiles) → [settings-customization.md](references/settings-customization.md)
- **Working faster** (IntelliSense, multi-cursor, navigation, tasks, terminal) → [productivity-features.md](references/productivity-features.md)
- **Extensions** (finding, installing, managing) → [extensions.md](references/extensions.md)
- **Updates or CLI** → [updates.md](references/updates.md)

## Refreshing This Skill

VS Code releases monthly updates. To keep this skill current:

1. Check https://code.visualstudio.com/updates for the latest release notes
2. Review https://code.visualstudio.com/docs for new or changed documentation
3. Update the relevant reference files with new features, settings, or shortcuts
4. Update this SKILL.md if new major topic areas emerge
