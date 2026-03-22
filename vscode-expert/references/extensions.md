# VS Code Extensions

## Table of Contents
1. [Finding & Installing Extensions](#finding--installing-extensions)
2. [Managing Extensions](#managing-extensions)
3. [Workspace Recommendations](#workspace-recommendations)
4. [Recommended Extensions by Category](#recommended-extensions-by-category)

---

## Finding & Installing Extensions

### Open Extensions view
- `⌘⇧X` (Mac) / `Ctrl+Shift+X` (Win/Linux)
- Click Extensions icon in Activity Bar

### Install an extension
1. Search in Extensions view → click **Install**
2. Via CLI: `code --install-extension <publisher.extension-id>`
3. From `.vsix` file: `⌘⇧P` → "Extensions: Install from VSIX"

### Find extension ID
Hover over an extension in the marketplace → the ID is shown below the name, or find it in the extension's detail page URL.

### Browse categories
Use the filter icon or prefix searches with `@category:` in the search bar:
- `@category:themes`
- `@category:linters`
- `@category:debuggers`
- `@category:formatters`
- `@popular` — most installed extensions
- `@recommended` — workspace-specific recommendations

---

## Managing Extensions

### Enable / Disable
Right-click an extension in the Extensions view → Enable / Disable (globally or for workspace only). Disabling is useful for troubleshooting without uninstalling.

### Update extensions
- Extensions auto-update by default
- Disable auto-update: `⌘⇧P` → "Extensions: Disable Auto Update for All Extensions"
- Update manually: Extensions view → `...` menu → "Update"

### Per-extension auto-update control
Right-click extension → "Enable Auto Update" or "Disable Auto Update"

### Install a specific version
Right-click extension → "Install Another Version" → select from list

### Install pre-release version
Extension detail page → dropdown on Install button → "Install Pre-Release Version"

### Uninstall
Right-click extension → Uninstall

### List installed extensions via CLI
```bash
code --list-extensions
code --list-extensions --show-versions
```

---

## Workspace Recommendations

Share a set of recommended extensions with your team by adding `extensions.json` to `.vscode/`:

```json
// .vscode/extensions.json
{
  "recommendations": [
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "ms-python.python",
    "eamodio.gitlens"
  ],
  "unwantedRecommendations": [
    "ms-vscode.vscode-typescript-tslint-plugin"
  ]
}
```

When teammates open the project, VS Code prompts them to install recommended extensions.

### Generate recommendations from installed extensions
`⌘⇧P` → "Extensions: Configure Recommended Extensions (Workspace Folder)"

---

## Recommended Extensions by Category

### Formatting & Linting
| Extension | ID | Purpose |
|-----------|-----|---------|
| Prettier | `esbenp.prettier-vscode` | Opinionated code formatter (JS/TS/CSS/HTML/JSON/Markdown) |
| ESLint | `dbaeumer.vscode-eslint` | JavaScript/TypeScript linting |
| Pylint / Ruff | `ms-python.pylint` / `charliermarsh.ruff` | Python linting |
| EditorConfig | `editorconfig.editorconfig` | Enforce consistent coding styles |

### Languages
| Extension | ID | Purpose |
|-----------|-----|---------|
| Python | `ms-python.python` | Python language support |
| Pylance | `ms-python.vscode-pylance` | Fast Python IntelliSense |
| Go | `golang.go` | Go language support |
| Rust Analyzer | `rust-lang.rust-analyzer` | Rust language support |
| C/C++ | `ms-vscode.cpptools` | C/C++ IntelliSense, debugging |
| Java Extension Pack | `vscjava.vscode-java-pack` | Java support bundle |
| YAML | `redhat.vscode-yaml` | YAML validation and completion |
| Even Better TOML | `tamasfe.even-better-toml` | TOML support |

### Git & Collaboration
| Extension | ID | Purpose |
|-----------|-----|---------|
| GitLens | `eamodio.gitlens` | Enhanced Git annotations, history, blame |
| Git Graph | `mhutchie.git-graph` | Visual branch and commit graph |
| GitHub Pull Requests | `github.vscode-pull-request-github` | Manage PRs from within VS Code |

### AI & Copilot
| Extension | ID | Purpose |
|-----------|-----|---------|
| GitHub Copilot | `github.copilot` | AI code completions |
| GitHub Copilot Chat | `github.copilot-chat` | AI chat assistant in editor |

### Productivity
| Extension | ID | Purpose |
|-----------|-----|---------|
| Path Intellisense | `christian-kohler.path-intellisense` | Autocomplete file paths |
| Auto Rename Tag | `formulahendry.auto-rename-tag` | Auto-rename paired HTML/XML tags |
| Todo Highlight | `wayou.vscode-todo-highlight` | Highlight TODO/FIXME comments |
| Better Comments | `aaron-bond.better-comments` | Colored comment annotations |
| Bookmarks | `alefragnani.bookmarks` | Mark and jump to lines |
| Project Manager | `alefragnani.project-manager` | Switch between projects quickly |

### Remote & Containers
| Extension | ID | Purpose |
|-----------|-----|---------|
| Remote - SSH | `ms-vscode-remote.remote-ssh` | Develop on remote machines via SSH |
| Dev Containers | `ms-vscode-remote.remote-containers` | Develop inside Docker containers |
| WSL | `ms-vscode-remote.remote-wsl` | Windows Subsystem for Linux |

### Themes & UI
| Extension | ID | Purpose |
|-----------|-----|---------|
| One Dark Pro | `zhuangtongfa.material-theme` | Popular dark theme |
| Dracula | `dracula-theme.theme-dracula` | Dracula color theme |
| Material Icon Theme | `pkief.material-icon-theme` | Rich file/folder icons |
| Indent Rainbow | `oderwat.indent-rainbow` | Colorize indentation levels |
| Bracket Pair Colorizer | built-in since v1.67 | Use `editor.bracketPairColorization.enabled: true` |

### Database & API
| Extension | ID | Purpose |
|-----------|-----|---------|
| REST Client | `humao.rest-client` | Send HTTP requests from `.http` files |
| Thunder Client | `rangav.vscode-thunder-client` | Lightweight Postman alternative |
| SQLTools | `mtxr.sqltools` | Database explorer and query runner |
