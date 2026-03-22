# chrome.tabs / chrome.tabGroups / chrome.windows

Docs:
- `https://developer.chrome.com/docs/extensions/reference/api/tabs`
- `https://developer.chrome.com/docs/extensions/reference/api/tabGroups`
- `https://developer.chrome.com/docs/extensions/reference/api/windows`

## chrome.tabs

Permission: `"tabs"` unlocks sensitive `Tab` properties (`url`, `title`, `favIconUrl`).
Without it, those fields are `undefined`. Host permissions needed for `captureVisibleTab()`.

### Tab Object

```ts
interface Tab {
  id?: number;
  windowId: number;
  index: number;
  active: boolean;
  pinned: boolean;
  highlighted: boolean;
  incognito: boolean;
  status: 'unloaded' | 'loading' | 'complete';
  url?: string;         // requires "tabs" permission or host_permissions
  title?: string;       // requires "tabs" permission or host_permissions
  favIconUrl?: string;  // requires "tabs" permission or host_permissions
  groupId: number;      // TAB_GROUP_ID_NONE (-1) if not in a group
  discarded: boolean;
  autoDiscardable: boolean;
  audible?: boolean;
  mutedInfo?: MutedInfo;
  openerTabId?: number;
  lastAccessed?: number;
  frozen?: boolean;
}
```

### Methods

```ts
// Query tabs
chrome.tabs.query({ active: true, currentWindow: true }): Promise<Tab[]>
chrome.tabs.query({ url: 'https://*.example.com/*' }): Promise<Tab[]>
chrome.tabs.query({ groupId: 5, windowId: chrome.windows.WINDOW_ID_CURRENT }): Promise<Tab[]>

// Get single tab
chrome.tabs.get(tabId: number): Promise<Tab>
chrome.tabs.getCurrent(): Promise<Tab | undefined>  // only in extension pages, not SW

// Create / update / remove
chrome.tabs.create({ url, active, pinned, openerTabId, windowId, index }): Promise<Tab>
chrome.tabs.update(tabId?, { url, active, pinned, muted, highlighted, autoDiscardable }): Promise<Tab>
chrome.tabs.remove(tabIds: number | number[]): Promise<void>
chrome.tabs.duplicate(tabId: number): Promise<Tab | undefined>

// Navigation
chrome.tabs.reload(tabId?, { bypassCache? }): Promise<void>
chrome.tabs.goBack(tabId?): Promise<void>
chrome.tabs.goForward(tabId?): Promise<void>

// Move & group
chrome.tabs.move(tabIds, { windowId?, index }): Promise<Tab | Tab[]>
chrome.tabs.group({ tabIds, groupId?, createProperties?: { windowId? } }): Promise<number>  // returns groupId
chrome.tabs.ungroup(tabIds: number | number[]): Promise<void>
chrome.tabs.highlight({ tabs: number[], windowId? }): Promise<Window>

// Capture & messaging
chrome.tabs.captureVisibleTab(windowId?, { format?, quality? }): Promise<string>  // data URL
chrome.tabs.sendMessage(tabId, message, { frameId?, documentId? }?): Promise<any>
chrome.tabs.connect(tabId, { name?, frameId?, documentId? }?): runtime.Port

// Zoom
chrome.tabs.getZoom(tabId?): Promise<number>
chrome.tabs.setZoom(tabId?, zoomFactor: number): Promise<void>
chrome.tabs.getZoomSettings(tabId?): Promise<ZoomSettings>
chrome.tabs.setZoomSettings(tabId?, settings: ZoomSettings): Promise<void>

// Other
chrome.tabs.discard(tabId?): Promise<Tab | undefined>
chrome.tabs.detectLanguage(tabId?): Promise<string>
```

### Events

```ts
chrome.tabs.onCreated.addListener((tab: Tab) => {})
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {})  // changeInfo has changed fields only
chrome.tabs.onRemoved.addListener((tabId, { windowId, isWindowClosing }) => {})
chrome.tabs.onActivated.addListener(({ tabId, windowId }) => {})
chrome.tabs.onMoved.addListener((tabId, { windowId, fromIndex, toIndex }) => {})
chrome.tabs.onAttached.addListener((tabId, { newWindowId, newPosition }) => {})
chrome.tabs.onDetached.addListener((tabId, { oldWindowId, oldPosition }) => {})
chrome.tabs.onHighlighted.addListener(({ windowId, tabIds }) => {})
chrome.tabs.onReplaced.addListener((addedTabId, removedTabId) => {})
chrome.tabs.onZoomChange.addListener(({ tabId, oldZoomFactor, newZoomFactor, zoomSettings }) => {})
```

### Constants
- `chrome.tabs.TAB_ID_NONE = -1`
- `chrome.tabs.TAB_INDEX_NONE = -1`
- `chrome.tabs.MAX_CAPTURE_VISIBLE_TAB_CALLS_PER_SECOND = 2`

---

## chrome.tabGroups

Permission: `"tabGroups"` (Chrome 89+)

### TabGroup Object

```ts
interface TabGroup {
  id: number;
  collapsed: boolean;
  color: 'grey'|'blue'|'red'|'yellow'|'green'|'pink'|'purple'|'cyan'|'orange';
  title?: string;
  windowId: number;
  shared?: boolean;  // Chrome 137+
}
```

### Methods

```ts
chrome.tabGroups.get(groupId: number): Promise<TabGroup>
chrome.tabGroups.query({
  collapsed?: boolean,
  color?: Color,
  title?: string,
  windowId?: number,
  shared?: boolean
}): Promise<TabGroup[]>
chrome.tabGroups.update(groupId, {
  collapsed?: boolean,
  color?: Color,
  title?: string
}): Promise<TabGroup | undefined>
chrome.tabGroups.move(groupId, {
  index: number,
  windowId?: number
}): Promise<TabGroup | undefined>
```

### Events

```ts
chrome.tabGroups.onCreated.addListener((group: TabGroup) => {})
chrome.tabGroups.onUpdated.addListener((group: TabGroup) => {})
chrome.tabGroups.onMoved.addListener((group: TabGroup) => {})
chrome.tabGroups.onRemoved.addListener((group: TabGroup) => {})
```

### Constants
- `chrome.tabGroups.TAB_GROUP_ID_NONE = -1`

### Example: Group all tabs from same domain

```js
async function groupByDomain() {
  const tabs = await chrome.tabs.query({ currentWindow: true });
  const byDomain = {};
  for (const tab of tabs) {
    if (!tab.url) continue;
    const domain = new URL(tab.url).hostname;
    (byDomain[domain] = byDomain[domain] || []).push(tab.id);
  }
  for (const [domain, tabIds] of Object.entries(byDomain)) {
    if (tabIds.length < 2) continue;
    const groupId = await chrome.tabs.group({ tabIds });
    await chrome.tabGroups.update(groupId, { title: domain, color: 'blue' });
  }
}
```

---

## chrome.windows

### Window Object

```ts
interface Window {
  id?: number;
  focused: boolean;
  top?: number;
  left?: number;
  width?: number;
  height?: number;
  tabs?: Tab[];
  incognito: boolean;
  type: 'normal' | 'popup' | 'devtools';
  state: 'normal' | 'minimized' | 'maximized' | 'fullscreen' | 'locked-fullscreen';
  alwaysOnTop: boolean;
  sessionId?: string;
}
```

### Methods

```ts
chrome.windows.get(windowId, { populate?: boolean, windowTypes? }?): Promise<Window>
chrome.windows.getCurrent({ populate?, windowTypes? }?): Promise<Window>
chrome.windows.getLastFocused({ populate?, windowTypes? }?): Promise<Window>
chrome.windows.getAll({ populate?, windowTypes? }?): Promise<Window[]>

chrome.windows.create({
  url?: string | string[],
  tabId?: number,
  left?, top?, width?, height?,
  focused?: boolean,
  incognito?: boolean,
  type?: 'normal' | 'popup',
  state?: WindowState,
  setSelfAsOpener?: boolean
}): Promise<Window | undefined>

chrome.windows.update(windowId, {
  left?, top?, width?, height?,
  focused?: boolean,
  drawAttention?: boolean,
  state?: WindowState
}): Promise<Window>

chrome.windows.remove(windowId: number): Promise<void>
```

### Events

```ts
chrome.windows.onCreated.addListener((window: Window) => {})
chrome.windows.onRemoved.addListener((windowId: number) => {})
chrome.windows.onFocusChanged.addListener((windowId: number) => {})  // WINDOW_ID_NONE if no focus
chrome.windows.onBoundsChanged.addListener((window: Window) => {})
```

### Constants
- `chrome.windows.WINDOW_ID_NONE = -1`
- `chrome.windows.WINDOW_ID_CURRENT = -2`
