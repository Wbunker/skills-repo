# Chrome Extensions — Manifest V3 Overview

Docs: `https://developer.chrome.com/docs/extensions/mv3/intro`

## MV2 → MV3 Key Changes

| MV2 | MV3 | Reason |
|-----|-----|--------|
| Background pages (persistent) | Service workers (event-driven) | Performance |
| `webRequest` blocking | `declarativeNetRequest` | Privacy |
| Remotely hosted code allowed | Eliminated | Security |
| DOM access in background | Use Offscreen Documents API | Consistency |

**MV2 is deprecated.** All new extensions must use MV3.

## manifest.json Template (MV3)

```json
{
  "manifest_version": 3,
  "name": "My Extension",
  "version": "1.0.0",
  "description": "...",
  "minimum_chrome_version": "120",

  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  },

  "action": {
    "default_popup": "popup.html",
    "default_icon": "icons/icon48.png",
    "default_title": "My Extension"
  },

  "background": {
    "service_worker": "sw.js",
    "type": "module"
  },

  "content_scripts": [{
    "matches": ["https://*.example.com/*"],
    "js": ["content.js"],
    "run_at": "document_idle"
  }],

  "side_panel": {
    "default_path": "sidepanel.html"
  },

  "permissions": ["tabs", "storage", "alarms", "contextMenus", "notifications"],
  "host_permissions": ["https://*.example.com/*"],
  "optional_permissions": ["bookmarks"],
  "optional_host_permissions": ["https://*/*"],

  "web_accessible_resources": [{
    "resources": ["assets/*.png"],
    "matches": ["https://*.example.com/*"]
  }],

  "options_ui": {
    "page": "options.html",
    "open_in_tab": false
  },

  "commands": {
    "_execute_action": { "suggested_key": { "default": "Alt+Shift+E" } },
    "my-command": { "suggested_key": { "default": "Alt+Shift+U" }, "description": "Do something" }
  }
}
```

## Service Workers (Background)

- No DOM access — use `chrome.offscreen` for DOM APIs
- No `window`, `document`, `localStorage` — use `chrome.storage.session` for ephemeral state
- Event-driven: loaded on demand, unloaded when idle
- Register events at top level (not inside callbacks) so they're registered on startup

```js
// sw.js — register all listeners at top level
chrome.runtime.onInstalled.addListener(({ reason }) => {
  if (reason === 'install') console.log('First install');
});

chrome.tabs.onActivated.addListener(({ tabId }) => {
  chrome.tabs.get(tabId, tab => console.log(tab.url));
});

chrome.alarms.onAlarm.addListener(alarm => {
  console.log('Alarm fired:', alarm.name);
});
```

## Permissions List

All available permissions for `"permissions"` field:

`activeTab` `alarms` `audio` `bookmarks` `browsingData` `clipboardRead` `clipboardWrite`
`contentSettings` `contextMenus` `cookies` `debugger` `declarativeContent`
`declarativeNetRequest` `declarativeNetRequestFeedback` `dns` `downloads` `favicon`
`fontSettings` `gcm` `geolocation` `history` `identity` `idle` `management`
`nativeMessaging` `notifications` `offscreen` `pageCapture` `power` `privacy` `proxy`
`readingList` `scripting` `search` `sessions` `sidePanel` `storage`
`system.cpu` `system.display` `system.memory` `system.storage`
`tabCapture` `tabGroups` `tabs` `topSites` `tts` `ttsEngine`
`unlimitedStorage` `userScripts` `vpnProvider` `webNavigation` `webRequest`

**Sensitive permissions** (show a warning to users at install):
`bookmarks`, `browsingData`, `clipboardRead`, `clipboardWrite`, `contentSettings`,
`declarativeNetRequest`, `downloads`, `history`, `management`, `nativeMessaging`,
`pageCapture`, `privacy`, `proxy`, `tabs`, `topSites`

**Host permissions** are separate from `permissions` in MV3:
```json
"host_permissions": ["https://example.com/*", "https://*/*"]
```

## Content Scripts

Run in the context of web pages (isolated world by default).

```json
"content_scripts": [{
  "matches": ["https://*.example.com/*"],
  "exclude_matches": ["https://example.com/admin/*"],
  "js": ["content.js"],
  "css": ["content.css"],
  "run_at": "document_idle",   // document_start | document_end | document_idle
  "all_frames": false,
  "world": "ISOLATED"          // ISOLATED | MAIN (Chrome 95+)
}]
```

Communicate with service worker via `chrome.runtime.sendMessage()` / `chrome.runtime.connect()`.

## Message Passing Patterns

```js
// One-time message: content script → service worker
// content.js
chrome.runtime.sendMessage({ type: 'getData' }, response => {
  console.log(response.data);
});

// sw.js
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'getData') {
    sendResponse({ data: 'hello' });
  }
  return true; // keep channel open for async sendResponse
});

// Tab → extension message
// sw.js → content.js
chrome.tabs.sendMessage(tabId, { type: 'highlight' });
```

## Extension Pages

- **Popup** — small HTML page opened by clicking the action icon. Closes when loses focus.
- **Options page** — settings page; opens via `chrome.runtime.openOptionsPage()` or right-click extension icon
- **Side panel** — persistent panel in browser sidebar (Chrome 114+); see `chrome.sidePanel`
- **Devtools page** — page loaded when DevTools opens; can add custom panels/sidebars
- **Offscreen document** — hidden background page for DOM access (see `chrome.offscreen`)
