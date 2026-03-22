# VS Code Productivity Features

## Table of Contents
1. [IntelliSense](#intellisense)
2. [Multi-Cursor Editing](#multi-cursor-editing)
3. [Code Navigation](#code-navigation)
4. [Formatting & Refactoring](#formatting--refactoring)
5. [Tasks](#tasks)
6. [Integrated Terminal](#integrated-terminal)
7. [Debugging](#debugging)
8. [Source Control (Git)](#source-control-git)

---

## IntelliSense

IntelliSense provides code completions, parameter info, quick info, and member lists.

### Trigger manually
- `Ctrl+Space` — trigger suggestions
- `Ctrl+Shift+Space` — trigger parameter hints

### Completion types shown in suggestion list
| Icon | Type |
|------|------|
| `abc` | Text |
| `()` | Method/Function |
| `{}` | Variable |
| `<>` | Snippet |
| `#` | Color |

### Settings
```json
{
  "editor.suggestOnTriggerCharacters": true,
  "editor.acceptSuggestionOnTab": "on",
  "editor.quickSuggestionsDelay": 10,
  "editor.parameterHints.enabled": true
}
```

### Language support
Full IntelliSense works out-of-the-box for JavaScript, TypeScript, HTML, CSS, JSON. For Python, install the **Pylance** extension (`ms-python.vscode-pylance`).

---

## Multi-Cursor Editing

### Add cursors
| Action | Mac | Windows/Linux |
|--------|-----|---------------|
| Click to add cursor | `⌥+click` | `Alt+click` |
| Add cursor above | `⌥⌘↑` | `Ctrl+Alt+Up` |
| Add cursor below | `⌥⌘↓` | `Ctrl+Alt+Down` |
| Select next occurrence | `⌘D` | `Ctrl+D` |
| Select all occurrences | `⌘⇧L` | `Ctrl+Shift+L` |
| Column (box) select | `⌥⇧drag` | `Shift+Alt+drag` |

### Tips
- Press `Escape` to collapse all cursors back to one
- `⌘D` / `Ctrl+D` finds the next occurrence of current selection — press repeatedly to add more
- Use column selection to add identical text to multiple lines at once

---

## Code Navigation

### File and symbol navigation
| Action | Mac | Windows/Linux |
|--------|-----|---------------|
| Quick Open (file) | `⌘P` | `Ctrl+P` |
| Go to Symbol in file | `⌘⇧O` | `Ctrl+Shift+O` |
| Go to Symbol in workspace | `⌘T` | `Ctrl+T` |
| Go to Line | `Ctrl+G` | `Ctrl+G` |
| Go to Definition | `F12` | `F12` |
| Peek Definition | `⌥F12` | `Alt+F12` |
| Find References | `⇧F12` | `Shift+F12` |
| Go Back / Forward | `Ctrl+-` / `Ctrl+Shift+-` | same |

### Search
| Action | Mac | Windows/Linux |
|--------|-----|---------------|
| Find in file | `⌘F` | `Ctrl+F` |
| Replace in file | `⌘H` | `Ctrl+H` |
| Find in workspace | `⌘⇧F` | `Ctrl+Shift+F` |
| Replace in workspace | `⌘⇧H` | `Ctrl+Shift+H` |

Search supports **regex** (`.* ` button) and **preserve case** when replacing.

### Breadcrumbs
Enable with `⌘⇧P` → "View: Toggle Breadcrumbs". Shows file path and symbol hierarchy at the top of the editor.

### Code folding
- `⌘⌥[` / `Ctrl+Shift+[` — fold region
- `⌘⌥]` / `Ctrl+Shift+]` — unfold region
- `⌘K ⌘0` — fold all
- `⌘K ⌘J` — unfold all

---

## Formatting & Refactoring

### Format document/selection
- `⇧⌥F` (Mac) / `Shift+Alt+F` (Win/Linux) — format entire document
- `⌘K ⌘F` (Mac) / `Ctrl+K Ctrl+F` (Win/Linux) — format selection

### Auto-format settings
```json
{
  "editor.formatOnSave": true,
  "editor.formatOnPaste": true,
  "editor.formatOnType": false,
  "editor.defaultFormatter": "esbenp.prettier-vscode"
}
```

### Refactoring actions
- `⌘.` (Mac) / `Ctrl+.` (Win/Linux) — Quick Fix / Code Actions
- Right-click → Refactor (rename, extract function, extract variable)
- `F2` — rename symbol across all files

---

## Tasks

Tasks integrate external build tools (npm, make, webpack, etc.) directly into VS Code.

### Run a task
```
⌘⇧P → "Tasks: Run Task"
```
Or `Ctrl+Shift+B` to run the default build task.

### Create tasks.json
```
⌘⇧P → "Tasks: Configure Task" → select template
```
Saved to `.vscode/tasks.json`.

### tasks.json example
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Build",
      "type": "shell",
      "command": "npm run build",
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      },
      "problemMatcher": ["$tsc"]
    },
    {
      "label": "Test",
      "type": "shell",
      "command": "npm test",
      "group": "test"
    }
  ]
}
```

### Auto-detected tasks
VS Code auto-detects tasks from: `package.json` scripts, `Gruntfile.js`, `Gulpfile.js`, `Makefile`.

---

## Integrated Terminal

### Open terminal
- `` Ctrl+` `` — toggle terminal panel
- `⌘⇧5` (Mac) / `Ctrl+Shift+5` (Win/Linux) — split terminal

### Multiple terminals
- `+` button in terminal panel to create new terminal
- Dropdown to switch between terminals
- Name terminals for easier identification

### Configure default shell
```json
{
  "terminal.integrated.defaultProfile.osx": "zsh",
  "terminal.integrated.defaultProfile.windows": "PowerShell",
  "terminal.integrated.defaultProfile.linux": "bash"
}
```

### Useful terminal settings
```json
{
  "terminal.integrated.fontSize": 13,
  "terminal.integrated.fontFamily": "MesloLGS NF",
  "terminal.integrated.scrollback": 5000,
  "terminal.integrated.copyOnSelection": true,
  "terminal.integrated.cursorStyle": "line",
  "terminal.integrated.cwd": "${workspaceFolder}"
}
```

### Shell integration
When enabled, VS Code decorates the terminal with command status indicators (✓/✗) and allows navigating between commands with `Ctrl+Up/Down`.

```json
{ "terminal.integrated.shellIntegration.enabled": true }
```

### Send selection to terminal
`⌘⇧P` → "Terminal: Run Selected Text in Active Terminal"

---

## Debugging

### Start debugging
- `F5` — start/continue
- `⇧F5` — stop
- `Ctrl+⇧F5` — restart
- `F9` — toggle breakpoint
- `F10` — step over
- `F11` — step into
- `⇧F11` — step out

### launch.json (debug configuration)
```
Run → Add Configuration → select environment
```
Saved to `.vscode/launch.json`.

### Example launch.json (Node.js)
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Launch Program",
      "program": "${workspaceFolder}/index.js",
      "env": { "NODE_ENV": "development" }
    }
  ]
}
```

### Example launch.json (Python)
```json
{
  "type": "python",
  "request": "launch",
  "name": "Python: Current File",
  "program": "${file}",
  "console": "integratedTerminal"
}
```

### Debug console
Evaluate expressions while paused: open with `⌘⇧Y` (Mac) / `Ctrl+Shift+Y` (Win/Linux).

---

## Source Control (Git)

### Basic git workflow in VS Code
- **Source Control panel**: `⌘⇧G` (Mac) / `Ctrl+Shift+G` (Win/Linux)
- Stage files by clicking `+` next to changed files
- Write commit message and press `⌘Enter` / `Ctrl+Enter`

### Inline blame and diff
- **Gutter indicators** show changed lines (blue = modified, green = added, red = deleted)
- Click gutter indicator to see inline diff
- `⌘⇧P` → "Git: Show Line History" for blame

### Git settings
```json
{
  "git.autofetch": true,
  "git.confirmSync": false,
  "git.enableSmartCommit": true,
  "editor.inlineSuggest.enabled": true
}
```

### Recommended Git extensions
- **GitLens** (`eamodio.gitlens`) — rich git annotations, history, blame
- **Git Graph** (`mhutchie.git-graph`) — visual branch graph
