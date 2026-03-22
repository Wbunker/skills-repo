# VS Code Settings & Customization

## Table of Contents
1. [Settings](#settings)
2. [Keybindings](#keybindings)
3. [Themes](#themes)
4. [Snippets](#snippets)
5. [Profiles](#profiles)

---

## Settings

### Settings scopes (highest precedence wins)
```
Policy > Language-specific > Workspace > Remote > User > Default
```

### Accessing settings
- **Settings UI**: `⌘,` (Mac) / `Ctrl+,` (Win/Linux)
- **Settings JSON**: `⌘⇧P` → "Preferences: Open User Settings (JSON)"
- **Workspace settings**: `⌘⇧P` → "Preferences: Open Workspace Settings"

### Settings file locations
- **User**: `~/Library/Application Support/Code/User/settings.json` (Mac)
  - `%APPDATA%\Code\User\settings.json` (Windows)
  - `~/.config/Code/User/settings.json` (Linux)
- **Workspace**: `.vscode/settings.json` in project root

### Useful search filters in Settings UI
| Filter | Shows |
|--------|-------|
| `@modified` | Only settings you've changed |
| `@tag:advanced` | Advanced settings |
| `@lang:python` | Python-specific settings |
| `@feature:editor` | Editor feature settings |

### Common settings to configure
```json
{
  "editor.fontSize": 14,
  "editor.fontFamily": "Fira Code, Menlo, monospace",
  "editor.fontLigatures": true,
  "editor.tabSize": 2,
  "editor.wordWrap": "on",
  "editor.formatOnSave": true,
  "editor.formatOnPaste": true,
  "editor.minimap.enabled": false,
  "editor.lineNumbers": "relative",
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 1000,
  "workbench.colorTheme": "One Dark Pro",
  "terminal.integrated.fontSize": 13
}
```

### Language-specific settings
```json
{
  "[python]": {
    "editor.tabSize": 4,
    "editor.formatOnSave": true
  },
  "[markdown]": {
    "editor.wordWrap": "on",
    "editor.quickSuggestions": false
  }
}
```

---

## Keybindings

### Accessing keyboard shortcuts
- **Keyboard Shortcuts UI**: `⌘K ⌘S` (Mac) / `Ctrl+K Ctrl+S` (Win/Linux)
- **keybindings.json**: `⌘⇧P` → "Preferences: Open Keyboard Shortcuts (JSON)"

### Adding a custom keybinding (keybindings.json)
```json
[
  {
    "key": "ctrl+shift+d",
    "command": "editor.action.duplicateSelection"
  },
  {
    "key": "cmd+k cmd+t",
    "command": "workbench.action.selectTheme",
    "when": "!inQuickOpen"
  }
]
```

### Chord shortcuts (two-key sequences)
```json
{
  "key": "ctrl+k ctrl+c",
  "command": "editor.action.addCommentLine"
}
```

### Context-specific shortcuts ("when" clause examples)
| Clause | Meaning |
|--------|---------|
| `editorFocus` | When the editor has focus |
| `terminalFocus` | When the terminal has focus |
| `inQuickOpen` | When the Quick Open box is open |
| `editorLangId == 'python'` | In Python files only |
| `!editorReadonly` | When file is not read-only |

### Keymap extensions (adopt another editor's shortcuts)
- Vim: `vscodevim.vim`
- Sublime Text: `ms-vscode.sublime-keybindings`
- Emacs: `hiro-sun.vscode-emacs`

---

## Themes

### Apply a color theme
```
⌘⇧P → "Preferences: Color Theme" → select
```

### Apply an icon theme
```
⌘⇧P → "Preferences: File Icon Theme" → select
```

### Install theme extensions
```
⌘⇧X → search theme name → Install
```

### Popular themes
- **Dark**: One Dark Pro, Dracula, Monokai Pro, Tokyo Night, GitHub Dark
- **Light**: GitHub Light, Solarized Light, Quiet Light
- **High contrast**: built-in "High Contrast"

### Customize a theme (settings.json)
```json
{
  "editor.tokenColorCustomizations": {
    "[One Dark Pro]": {
      "comments": "#888888",
      "strings": "#98c379"
    }
  },
  "workbench.colorCustomizations": {
    "statusBar.background": "#1a1a2e",
    "editorLineNumber.activeForeground": "#e5c07b"
  }
}
```

---

## Snippets

### Create user snippets
```
⌘⇧P → "Preferences: Configure User Snippets" → select language or global
```

### Snippet format
```json
{
  "Console log": {
    "prefix": "clg",
    "body": [
      "console.log('$1');",
      "$2"
    ],
    "description": "Log output to console"
  },
  "Arrow function": {
    "prefix": "af",
    "body": "const ${1:name} = (${2:params}) => {\n\t$3\n};",
    "description": "Arrow function"
  }
}
```

### Snippet variables
| Variable | Value |
|----------|-------|
| `$TM_FILENAME` | Current filename |
| `$TM_DIRECTORY` | Directory of current file |
| `$CURRENT_DATE` | Current date (DD) |
| `$CURRENT_YEAR` | Current year |
| `$CLIPBOARD` | Clipboard contents |
| `$TM_SELECTED_TEXT` | Currently selected text |

### Trigger snippets
- Type prefix, then `Tab` to expand
- Or open IntelliSense with `Ctrl+Space` and select snippet

---

## Profiles

Profiles let you save and switch between complete configurations (settings, extensions, keybindings, snippets, themes).

### Create a profile
```
⌘⇧P → "Profiles: Create Profile"
```
Or: Manage gear icon (bottom-left) → Profiles → Create Profile

### Switch profiles
```
Manage gear icon → Profiles → select profile
```

### Export/import profiles
- **Export**: `⌘⇧P` → "Profiles: Export Profile" → saves as `.code-profile` file or Gist
- **Import**: `⌘⇧P` → "Profiles: Import Profile" → from file or URL

### Profile use cases
- **Work** profile: company extensions, stricter linting
- **Personal** profile: minimal, preferred theme
- **Language-specific**: Python profile with data science extensions, etc.

### Workspace-specific profile
Associate a profile with a workspace folder via the Profiles UI — VS Code auto-switches when opening that folder.
