# Chrome Release Notes Reference

## How to Stay Current

Chrome releases a new stable version every **~4 weeks**. To update this skill:

1. Check `https://developer.chrome.com/blog/new-in-chrome-{N}` for web platform changes
2. Check `https://developer.chrome.com/blog/new-in-devtools-{N}` for DevTools changes
3. Update the "Current as of Chrome X" line in SKILL.md
4. Update any API signatures or feature notes that changed

| Resource | URL |
|----------|-----|
| Web platform blog | `https://developer.chrome.com/blog/new-in-chrome-{N}` |
| DevTools blog | `https://developer.chrome.com/blog/new-in-devtools-{N}` |
| Structured release notes | `https://developer.chrome.com/release-notes/{N}` |
| Chrome Platform Status | `https://chromestatus.com/features` |
| All Chrome blog posts | `https://developer.chrome.com/blog` |

## Chrome 135 (March 2026) — Current

### Web Platform
- **CSS Carousels** — `::scroll-button()` and `::scroll-marker()` pseudo-elements for scroll containers
- **`command`/`commandfor` HTML attributes** — Declarative button behavior; replaces `popovertarget`/`popovertargetaction`
- **CSS `shape()` function** — For `clip-path` and `offset-path`; supports CSS units and math
- **Float16Array** — Now Baseline Newly Available
- **Observable API** — Standard reactive data stream primitive
- **Web Speech API** — `MediaStreamTrack` support added

### DevTools 135
- **Performance panel:** Origin/script links in Summary tab; LCP phase field data overlay; network dependency tree insight; heaviest stack highlighting
- **Elements panel:** Full-page accessibility tree view enabled by default (toggle DOM ↔ Accessibility)
- **Lighthouse:** Updated to 12.4.0
- **Network panel:** Empty states with actionable guidance

### Extensions
- `chrome.tabGroups.shared` property added (Chrome 137 preview — check if landed)
- `chrome.sidePanel.close()` added (Chrome 141)
- `chrome.sidePanel.onOpened` / `onClosed` events (Chrome 141/142)
- `chrome.action.onUserSettingsChanged` event (Chrome 130)

## Version History Highlights

| Version | Notable Changes |
|---------|----------------|
| 135 | CSS Carousels, `command`/`commandfor` attrs, CSS `shape()`, Observable API |
| 134 | — |
| 130 | `chrome.action.onUserSettingsChanged` |
| 128 | `declarativeNetRequest` responseHeaders condition |
| 127 | `chrome.sidePanel.open()` |
| 120 | `chrome.alarms` min interval reduced to 30s (was 1 min); `chrome-headless-shell` standalone binary |
| 116 | `chrome.sidePanel.open()` requires user gesture |
| 115 | `chrome.runtime.ContextType`, `onUserScriptConnect/Message` |
| 114 | `chrome.sidePanel` API |
| 106 | `documentId`, `documentLifecycle` on MessageSender |
| 97 | Recorder panel in DevTools |
| 96 | `chrome.scripting` dynamic content scripts |
| 95 | `ExecutionWorld` in `chrome.scripting` |
| 89 | `chrome.tabGroups` API |
| 88 | MV3 support; `chrome.action`; `chrome.scripting` |
