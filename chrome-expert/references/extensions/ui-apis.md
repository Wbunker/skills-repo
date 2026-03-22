# chrome.action / chrome.contextMenus / chrome.notifications / chrome.sidePanel

## chrome.action (Chrome 88+, MV3 only)

Docs: `https://developer.chrome.com/docs/extensions/reference/api/action`

Controls the extension's icon in the toolbar. Replaces `browserAction` and `pageAction` from MV2.

- Badge text: ≤ 4 characters recommended
- Popup size: 25×25 to 800×600 px

### Methods

```ts
// Enable/disable
chrome.action.enable(tabId?: number): Promise<void>
chrome.action.disable(tabId?: number): Promise<void>
chrome.action.isEnabled(tabId?: number): Promise<boolean>  // Chrome 110+

// Open popup programmatically (requires user gesture, Chrome 127+)
chrome.action.openPopup(options?: { windowId?: number }): Promise<void>

// Icon
chrome.action.setIcon(details: { path?: string|object, imageData?, tabId? }): Promise<void>

// Title (tooltip)
chrome.action.setTitle(details: { title: string, tabId? }): Promise<void>
chrome.action.getTitle(details: { tabId? }): Promise<string>

// Popup
chrome.action.setPopup(details: { popup: string, tabId? }): Promise<void>
chrome.action.getPopup(details: { tabId? }): Promise<string>

// Badge text
chrome.action.setBadgeText(details: { text: string, tabId? }): Promise<void>
chrome.action.getBadgeText(details: { tabId? }): Promise<string>

// Badge colors
chrome.action.setBadgeBackgroundColor(details: { color: string|ColorArray, tabId? }): Promise<void>
chrome.action.getBadgeBackgroundColor(details: { tabId? }): Promise<ColorArray>
chrome.action.setBadgeTextColor(details: { color: string|ColorArray, tabId? }): Promise<void>  // Chrome 110+
chrome.action.getBadgeTextColor(details: { tabId? }): Promise<ColorArray>

// User settings
chrome.action.getUserSettings(): Promise<{ isOnToolbar: boolean }>
```

### Events

```ts
chrome.action.onClicked.addListener((tab: Tab) => {})  // only fires when NO popup is set
chrome.action.onUserSettingsChanged.addListener((change) => {})  // Chrome 130+
```

### Per-tab State

All setters accept optional `tabId` to override state for a specific tab.
Without `tabId`, the setting applies globally (all tabs).

---

## chrome.contextMenus

Permission: `"contextMenus"`. Max **6 top-level items** in action menus.
Docs: `https://developer.chrome.com/docs/extensions/reference/api/contextMenus`

### Methods

```ts
chrome.contextMenus.create(properties: CreateProperties, callback?: () => void): number | string

chrome.contextMenus.update(
  id: string | number,
  updateProperties: Partial<CreateProperties>
): Promise<void>

chrome.contextMenus.remove(menuItemId: string | number): Promise<void>
chrome.contextMenus.removeAll(): Promise<void>
```

### CreateProperties

```ts
interface CreateProperties {
  id?: string;
  title?: string;           // use %s for selected text placeholder
  type?: 'normal' | 'checkbox' | 'radio' | 'separator';
  contexts?: ContextType[]; // where menu appears
  parentId?: string | number;
  checked?: boolean;        // for checkbox/radio
  enabled?: boolean;
  visible?: boolean;
  documentUrlPatterns?: string[];
  targetUrlPatterns?: string[];  // for image/link/video/audio items
  onclick?: (info: OnClickData, tab: Tab) => void;
}
```

### ContextType Values

`all` `page` `frame` `selection` `link` `editable` `image` `video` `audio`
`launcher` `action` (replaces `browser_action`/`page_action`)

### Events

```ts
chrome.contextMenus.onClicked.addListener((info: OnClickData, tab?: Tab) => {})
```

`OnClickData`: `menuItemId`, `parentMenuItemId`, `selectionText`, `linkUrl`, `pageUrl`, `frameUrl`, `mediaType`, `srcUrl`, `editable`, `checked`, `wasChecked`

### Example

```js
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'search-selection',
    title: 'Search for "%s"',
    contexts: ['selection'],
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'search-selection') {
    chrome.tabs.create({ url: `https://google.com/search?q=${info.selectionText}` });
  }
});
```

---

## chrome.notifications

Permission: `"notifications"`
Docs: `https://developer.chrome.com/docs/extensions/reference/api/notifications`

### Methods

```ts
chrome.notifications.create(
  notificationId?: string,  // auto-generated if omitted
  options: NotificationOptions
): Promise<string>  // returns notificationId

chrome.notifications.update(
  notificationId: string,
  options: NotificationOptions
): Promise<boolean>

chrome.notifications.clear(notificationId: string): Promise<boolean>
chrome.notifications.getAll(): Promise<Record<string, NotificationOptions>>
chrome.notifications.getPermissionLevel(): Promise<'granted' | 'denied'>
```

### NotificationOptions

```ts
interface NotificationOptions {
  type: 'basic' | 'image' | 'list' | 'progress';  // required on create
  iconUrl: string;   // required
  title: string;     // required
  message: string;   // required
  contextMessage?: string;
  priority?: -2 | -1 | 0 | 1 | 2;  // default 0
  eventTime?: number;
  buttons?: [{ title: string, iconUrl?: string }];  // max 2
  imageUrl?: string;            // type: 'image' only
  items?: { title, message }[]; // type: 'list' only
  progress?: number;            // 0-100, type: 'progress' only
  requireInteraction?: boolean; // don't auto-close (desktop only)
  silent?: boolean;
  appIconMaskUrl?: string;
}
```

### Events

```ts
chrome.notifications.onClicked.addListener((notificationId: string) => {})
chrome.notifications.onButtonClicked.addListener((notificationId, buttonIndex) => {})
chrome.notifications.onClosed.addListener((notificationId, byUser: boolean) => {})
chrome.notifications.onPermissionLevelChanged.addListener((level) => {})  // ChromeOS only
```

---

## chrome.sidePanel (Chrome 114+)

Permission: `"sidePanel"`. Manifest: `"side_panel": { "default_path": "sidepanel.html" }`
Docs: `https://developer.chrome.com/docs/extensions/reference/api/sidePanel`

### Methods

```ts
// Configure panel visibility and path
chrome.sidePanel.setOptions(options: {
  enabled?: boolean,
  path?: string,
  tabId?: number     // per-tab override
}): Promise<void>

chrome.sidePanel.getOptions(options: { tabId?: number }): Promise<PanelOptions>

// Control whether clicking the action icon opens the panel
chrome.sidePanel.setPanelBehavior(behavior: {
  openPanelOnActionClick?: boolean
}): Promise<void>

chrome.sidePanel.getPanelBehavior(): Promise<{ openPanelOnActionClick: boolean }>

// Open/close programmatically (requires user gesture)
chrome.sidePanel.open(options: { tabId?: number, windowId?: number }): Promise<void>  // Chrome 116+
chrome.sidePanel.close(options: { tabId?: number, windowId?: number }): Promise<void> // Chrome 141+

// Layout info
chrome.sidePanel.getLayout(): Promise<{ side: 'left' | 'right' }>  // Chrome 140+
```

### Events (Chrome 141/142+)

```ts
chrome.sidePanel.onOpened.addListener((info: { path, tabId?, windowId }) => {})
chrome.sidePanel.onClosed.addListener((info: { tabId?, windowId }) => {})
```

### Common Pattern

```js
// manifest.json
// "side_panel": { "default_path": "sidepanel.html" }
// "permissions": ["sidePanel"]

// Open panel when action clicked (instead of a popup)
chrome.runtime.onInstalled.addListener(() => {
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
});

// Open panel on specific tab from content script trigger
chrome.runtime.onMessage.addListener((msg, sender) => {
  if (msg.type === 'openPanel') {
    chrome.sidePanel.open({ tabId: sender.tab.id });
  }
});

// Enable panel only on certain sites
chrome.tabs.onUpdated.addListener(async (tabId, info, tab) => {
  if (!tab.url) return;
  const isExample = tab.url.startsWith('https://example.com');
  await chrome.sidePanel.setOptions({ tabId, enabled: isExample });
});
```
