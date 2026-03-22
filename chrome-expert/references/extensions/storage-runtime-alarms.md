# chrome.storage / chrome.runtime / chrome.alarms

## chrome.storage

No permission needed for `storage`... wait — permission `"storage"` IS required.
Docs: `https://developer.chrome.com/docs/extensions/reference/api/storage`

### Storage Areas Comparison

| Area | Quota | Persistence | Notes |
|------|-------|-------------|-------|
| `local` | 10 MB (removed with `unlimitedStorage`) | Until extension uninstalled | Content scripts accessible by default |
| `sync` | 100 KB total / 8 KB per item / 512 items / 120 writes/min | Syncs across signed-in devices | Falls back to local if not signed in |
| `session` | 10 MB | Cleared on browser restart or extension reload | Not accessible from content scripts by default |
| `managed` | Admin-configured | Read-only | Enterprise/policy managed |

### Methods (same on all areas)

```ts
// Read
chrome.storage.local.get(keys?: string | string[] | Record<string, any>): Promise<Record<string, any>>
// keys = null/undefined → get all; string[] → get those keys; object → get with defaults

// Write
chrome.storage.local.set(items: Record<string, any>): Promise<void>

// Delete
chrome.storage.local.remove(keys: string | string[]): Promise<void>
chrome.storage.local.clear(): Promise<void>

// Meta
chrome.storage.local.getKeys(): Promise<string[]>
chrome.storage.local.getBytesInUse(keys?: string | string[]): Promise<number>

// Session only — control content script access
chrome.storage.session.setAccessLevel({
  accessLevel: 'TRUSTED_CONTEXTS' | 'TRUSTED_AND_UNTRUSTED_CONTEXTS'
}): Promise<void>
```

### Change Events

```ts
// Global — all areas
chrome.storage.onChanged.addListener((
  changes: Record<string, { oldValue?: any, newValue?: any }>,
  areaName: 'local' | 'sync' | 'session' | 'managed'
) => {})

// Per-area
chrome.storage.local.onChanged.addListener((changes) => {})
```

### Common Patterns

```js
// Get with defaults
const { theme = 'light', count = 0 } = await chrome.storage.local.get({ theme: 'light', count: 0 });

// Atomic update
const { visits = 0 } = await chrome.storage.local.get('visits');
await chrome.storage.local.set({ visits: visits + 1 });

// Watch for changes
chrome.storage.onChanged.addListener((changes, area) => {
  if (area === 'sync' && changes.theme) {
    applyTheme(changes.theme.newValue);
  }
});
```

**Never use** `window.localStorage` or `window.sessionStorage` in service workers — they're unavailable.

---

## chrome.runtime

No permission required (except `"nativeMessaging"` for native messaging).
Docs: `https://developer.chrome.com/docs/extensions/reference/api/runtime`

### Properties

```ts
chrome.runtime.id: string          // Extension ID
chrome.runtime.lastError: { message?: string } | undefined  // Set after failed callback-style call
```

### Messaging

```ts
// Send one-time message (returns promise or uses callback)
chrome.runtime.sendMessage(
  extensionId?: string,  // omit to send to own extension
  message: any,
  options?: { includeTlsChannelId?: boolean }
): Promise<any>

// Long-lived connection
chrome.runtime.connect(extensionId?, { name?, includeTlsChannelId? }?): Port
// Port: { name, postMessage(msg), disconnect(), onMessage, onDisconnect }

// Native messaging
chrome.runtime.sendNativeMessage(application: string, message: object): Promise<any>
chrome.runtime.connectNative(application: string): Port
```

### Lifecycle

```ts
chrome.runtime.onInstalled.addListener(({ reason, previousVersion?, id? }) => {
  // reason: 'install' | 'update' | 'chrome_update' | 'shared_module_update'
})

chrome.runtime.onStartup.addListener(() => {})  // browser profile started

chrome.runtime.onUpdateAvailable.addListener(({ version }) => {
  // New version available but not yet applied
  chrome.runtime.reload(); // apply update now
})

chrome.runtime.onSuspend.addListener(() => {})         // service worker about to unload
chrome.runtime.onSuspendCanceled.addListener(() => {}) // suspend was cancelled
```

### Message Listeners

```ts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  // sender.tab — Tab that sent message (if from content script)
  // sender.frameId, sender.url, sender.origin
  // sender.documentId (Chrome 106+)
  sendResponse({ ok: true });
  return true; // REQUIRED if sendResponse is called asynchronously
})

chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {})  // from other extensions
chrome.runtime.onConnect.addListener((port: Port) => {})
chrome.runtime.onConnectExternal.addListener((port: Port) => {})
```

### Utilities

```ts
chrome.runtime.getManifest(): object           // parsed manifest.json
chrome.runtime.getURL(path: string): string    // chrome-extension://{id}/{path}
chrome.runtime.openOptionsPage(): Promise<void>
chrome.runtime.getPlatformInfo(): Promise<{ os, arch, nacl_arch }>
chrome.runtime.reload(): void                  // reload extension
chrome.runtime.setUninstallURL(url: string): Promise<void>
chrome.runtime.requestUpdateCheck(): Promise<{ status, version? }>
```

### ContextType (Chrome 114+)

```ts
type ContextType = 'TAB' | 'POPUP' | 'BACKGROUND' | 'OFFSCREEN_DOCUMENT' | 'SIDE_PANEL' | 'DEVELOPER_TOOLS'
```

---

## chrome.alarms

Permission: `"alarms"`
Docs: `https://developer.chrome.com/docs/extensions/reference/api/alarms`

- Minimum interval: **30 seconds** (Chrome 120+; was 1 minute before)
- Maximum concurrent alarms: **500**
- Alarms persist across service worker restarts — use for scheduled tasks

### Methods

```ts
chrome.alarms.create(
  name?: string,
  alarmInfo: {
    when?: number,           // absolute time (ms since epoch)
    delayInMinutes?: number, // delay before first fire
    periodInMinutes?: number // repeat interval; omit for one-shot
  }
): Promise<void>

chrome.alarms.get(name?: string): Promise<Alarm | undefined>
chrome.alarms.getAll(): Promise<Alarm[]>
chrome.alarms.clear(name?: string): Promise<boolean>
chrome.alarms.clearAll(): Promise<boolean>
```

### Alarm Object

```ts
interface Alarm {
  name: string;
  scheduledTime: number;  // ms since epoch
  periodInMinutes?: number;
}
```

### Events

```ts
chrome.alarms.onAlarm.addListener((alarm: Alarm) => {})
```

### Examples

```js
// One-shot alarm 5 minutes from now
await chrome.alarms.create('check-updates', { delayInMinutes: 5 });

// Repeating every 30 minutes
await chrome.alarms.create('sync', { periodInMinutes: 30 });

// Handle alarm in service worker
chrome.alarms.onAlarm.addListener(async alarm => {
  if (alarm.name === 'sync') {
    await doSync();
  }
});

// Schedule on install
chrome.runtime.onInstalled.addListener(() => {
  chrome.alarms.create('daily-cleanup', {
    delayInMinutes: 1440,
    periodInMinutes: 1440
  });
});
```
