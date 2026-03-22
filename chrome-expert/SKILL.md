---
name: chrome-expert
description: >
  Expert reference for Chrome browser features, Chrome Extension APIs (Manifest V3),
  Chrome DevTools, DevTools Protocol (CDP), and web platform capabilities.
  Use when working with: Chrome extensions (MV3, service workers, chrome.tabs,
  chrome.tabGroups, chrome.storage, chrome.scripting, declarativeNetRequest,
  sidePanel, offscreen documents), Chrome DevTools (panels, Recorder, Performance,
  CDP automation), tab groups, Chrome headless, web capabilities (File System Access,
  Web Share, Web Bluetooth), Privacy Sandbox APIs, or any chrome:// internals.
  Triggers on: Chrome extension, Manifest V3, MV3, chrome.tabs, chrome.tabGroups,
  tab groups, chrome.storage, chrome.scripting, declarativeNetRequest, content scripts,
  service worker extension, Chrome DevTools, DevTools Protocol, CDP, chrome headless,
  headless Chrome, Puppeteer, Playwright Chrome, File System Access API, web capabilities,
  Privacy Sandbox, chrome://flags, chrome://settings, Chrome APIs.
---

# Chrome Expert

Reference for Chrome Extensions (MV3), DevTools, Tab Groups, Web Capabilities,
and the Chrome DevTools Protocol. Current as of **Chrome 135** (March 2026).

## Release Notes & Staying Current

Chrome ships a new stable version every **~4 weeks**.

| Source | URL Pattern |
|--------|-------------|
| New in Chrome (web platform) | `https://developer.chrome.com/blog/new-in-chrome-{N}` |
| New in DevTools | `https://developer.chrome.com/blog/new-in-devtools-{N}` |
| Chrome Platform Status | `https://chromestatus.com/features` |
| Full release notes | `https://developer.chrome.com/release-notes/{N}` |

See [references/release-notes.md](references/release-notes.md) for Chrome 135 highlights and what changed in each major area.

## Reference Files

Load only what's relevant to the task:

### Extensions (Manifest V3)

| File | Load when working with... |
|------|--------------------------|
| [references/extensions/mv3-overview.md](references/extensions/mv3-overview.md) | MV3 manifest format, service workers, MV2→MV3 migration, permissions list |
| [references/extensions/tabs-groups-windows.md](references/extensions/tabs-groups-windows.md) | `chrome.tabs`, `chrome.tabGroups`, `chrome.windows` |
| [references/extensions/storage-runtime-alarms.md](references/extensions/storage-runtime-alarms.md) | `chrome.storage`, `chrome.runtime`, `chrome.alarms` |
| [references/extensions/ui-apis.md](references/extensions/ui-apis.md) | `chrome.action`, `chrome.contextMenus`, `chrome.notifications`, `chrome.sidePanel` |
| [references/extensions/scripting-network.md](references/extensions/scripting-network.md) | `chrome.scripting`, `chrome.declarativeNetRequest`, `chrome.offscreen` |

### DevTools

| File | Load when working with... |
|------|--------------------------|
| [references/devtools.md](references/devtools.md) | DevTools panels (Elements, Network, Performance, Recorder, Memory), latest features |
| [references/cdp.md](references/cdp.md) | Chrome DevTools Protocol — connecting, key domains, automation |

### Web Platform & Browser

| File | Load when working with... |
|------|--------------------------|
| [references/web-capabilities.md](references/web-capabilities.md) | File System Access, Web Share, Web Bluetooth, WebHID, Web Serial, Badging, Window Management |
| [references/headless.md](references/headless.md) | Chrome headless modes (`--headless=new` vs `chrome-headless-shell`), Chrome for Testing |
| [references/privacy-sandbox.md](references/privacy-sandbox.md) | Topics API, Protected Audience, Attribution Reporting, CHIPS, Storage Partitioning |
| [references/chrome-internals.md](references/chrome-internals.md) | `chrome://` URLs, flags system, enterprise policies |

## Key Facts

- **Extensions base URL:** `https://developer.chrome.com/docs/extensions/reference/api/`
- **MV2 is deprecated** — all new extensions must use MV3
- **`/me` doesn't exist in extensions** — use event listeners and `chrome.tabs.query({active: true})` for current tab
- **Service workers have no DOM** — use `chrome.offscreen` for DOM APIs
- **Graph API base:** Graph API has nothing to do with Chrome — don't confuse with Microsoft 365
