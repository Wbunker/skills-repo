# VS Code Updates & CLI

## Table of Contents
1. [Checking for and Applying Updates](#checking-for-and-applying-updates)
2. [Update Modes](#update-modes)
3. [VS Code CLI Reference](#vs-code-cli-reference)
4. [Refreshing This Skill](#refreshing-this-skill)

---

## Checking for and Applying Updates

VS Code releases a new stable version monthly (the "Update" release notes appear in the What's New panel after each update).

### Check for updates manually
- **macOS**: Code menu → Check for Updates
- **Windows/Linux**: Help menu → Check for Updates

### Verify current version
- **Help menu → About** (shows version, commit, Electron, Node, OS)
- CLI: `code --version`

### Auto-update behavior
By default VS Code checks for updates in the background and prompts you to apply them. A notification appears in the bottom-right corner when an update is ready. Click **Restart to Update** to apply.

---

## Update Modes

Configure via `update.mode` in settings:

| Mode | Behavior |
|------|----------|
| `default` | Download and notify; apply on next launch or manual restart |
| `manual` | No background checks; update only via Help → Check for Updates |
| `start` | Check at startup only |
| `none` | Disable all update checks |

```json
// settings.json
{
  "update.mode": "default"
}
```

### Enable/disable update notifications
```json
{
  "update.showReleaseNotes": true
}
```

---

## VS Code CLI Reference

The `code` command must be on your PATH. On macOS, install via `⌘⇧P` → "Shell Command: Install 'code' command in PATH".

### Open files and folders
```bash
code .                          # open current directory
code path/to/file.js            # open specific file
code path/to/folder             # open folder
code -r .                       # reuse existing window
code -n .                       # open in new window
code --diff file1.js file2.js   # open diff editor
```

### Extensions via CLI
```bash
code --list-extensions                          # list installed
code --list-extensions --show-versions          # with version numbers
code --install-extension publisher.ext-id       # install
code --uninstall-extension publisher.ext-id     # uninstall
code --install-extension my-ext.vsix            # from .vsix file
```

### Diagnostics and info
```bash
code --version                  # VS Code version info
code --status                   # show process diagnostics
code --log trace                # set log level (trace/debug/info/warn/error/off)
```

### Other useful flags
```bash
code --disable-extensions       # launch with all extensions disabled (for troubleshooting)
code --safe-mode                # disable all extensions and customizations
code --wait                     # wait until file is closed before returning (useful for git editor)
```

### Set VS Code as git editor
```bash
git config --global core.editor "code --wait"
```

### Launch a chat session (Copilot)
```bash
code chat "explain the architecture of this repo"
```

---

## Refreshing This Skill

VS Code releases monthly. When updates ship new features that affect this skill's content:

### Steps to update
1. **Check release notes**: https://code.visualstudio.com/updates
2. **Check docs changes**: https://code.visualstudio.com/docs
3. **Update reference files** with new settings keys, shortcuts, or features:
   - New settings → add to `settings-customization.md`
   - New productivity features → add to `productivity-features.md`
   - New recommended extensions → add to `extensions.md`
   - Update CLI flags if changed → update this file
4. **Update SKILL.md** if a new major topic area emerges (e.g., if Copilot grows into a major category worth its own reference file)

### Key pages to scan
| Page | What to look for |
|------|-----------------|
| https://code.visualstudio.com/updates | New features, changed defaults, deprecated settings |
| https://code.visualstudio.com/docs/getstarted/settings | New setting scopes or UI changes |
| https://code.visualstudio.com/docs/configure/command-line | New CLI flags |
| https://code.visualstudio.com/docs/editor/extension-marketplace | Marketplace or extension management changes |

### Version history
This skill was created based on VS Code documentation as of **March 2026** (February 2026 stable release). The February 2026 release included multi-agent Copilot development, faster chat, Claude integration, and improved customization features.
