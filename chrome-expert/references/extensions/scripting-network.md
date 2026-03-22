# chrome.scripting / chrome.declarativeNetRequest / chrome.offscreen

## chrome.scripting (Chrome 88+)

Permission: `"scripting"` + host permissions for target pages
Docs: `https://developer.chrome.com/docs/extensions/reference/api/scripting`

### executeScript

Inject and run JavaScript in a tab.

```ts
chrome.scripting.executeScript(injection: {
  target: {
    tabId: number,
    frameIds?: number[],    // specific frames; omit for main frame
    documentIds?: string[], // Chrome 106+
    allFrames?: boolean,
  },
  func?: Function,          // function to execute (serialized, no closures)
  args?: any[],             // arguments passed to func
  files?: string[],         // extension file paths to inject
  world?: 'ISOLATED' | 'MAIN',  // Chrome 95+; MAIN = shared with page
  injectImmediately?: boolean,
}): Promise<InjectionResult[]>

// InjectionResult: { frameId, documentId?, result? }
// result = return value of func (must be JSON-serializable)
// If func returns a Promise, Chrome awaits it automatically
```

```js
// Inject a function with arguments
const results = await chrome.scripting.executeScript({
  target: { tabId },
  func: (selector) => document.querySelector(selector)?.textContent,
  args: ['h1'],
});
console.log(results[0].result); // page's h1 text

// Inject into page's own context (MAIN world — shares window/globals)
await chrome.scripting.executeScript({
  target: { tabId },
  world: 'MAIN',
  func: () => { window.myFlag = true; }
});
```

### CSS Injection

```ts
chrome.scripting.insertCSS(injection: {
  target: { tabId, frameIds?, allFrames? },
  css?: string,
  files?: string[],
  origin?: 'AUTHOR' | 'USER',
}): Promise<void>

chrome.scripting.removeCSS(injection): Promise<void>
```

### Dynamic Content Scripts (Chrome 96+)

Register content scripts programmatically (persist across sessions):

```ts
chrome.scripting.registerContentScripts(scripts: RegisteredContentScript[]): Promise<void>
chrome.scripting.updateContentScripts(scripts: RegisteredContentScript[]): Promise<void>
chrome.scripting.unregisterContentScripts(filter?: { ids?: string[] }): Promise<void>
chrome.scripting.getRegisteredContentScripts(filter?: { ids?: string[] }): Promise<RegisteredContentScript[]>
```

```ts
interface RegisteredContentScript {
  id: string;
  matches?: string[];
  excludeMatches?: string[];
  css?: string[];
  js?: string[];
  runAt?: 'document_start' | 'document_end' | 'document_idle';
  allFrames?: boolean;
  world?: 'ISOLATED' | 'MAIN';
  persistAcrossSessions?: boolean;  // default true
}
```

---

## chrome.declarativeNetRequest

Replaces `webRequest` blocking from MV2. Privacy-preserving: extension never sees request content.
Permission: `"declarativeNetRequest"` (+ `"declarativeNetRequestFeedback"` for `getMatchedRules`)
Docs: `https://developer.chrome.com/docs/extensions/reference/api/declarativeNetRequest`

### Rule Structure

```ts
interface Rule {
  id: number;
  priority?: number;    // higher = evaluated first; default 1
  action: {
    type: 'block' | 'redirect' | 'allow' | 'allowAllRequests' | 'upgradeScheme' | 'modifyHeaders';
    redirect?: { url?, regexSubstitution?, transform? };
    requestHeaders?: HeaderOperation[];
    responseHeaders?: HeaderOperation[];
  };
  condition: {
    urlFilter?: string;         // e.g., "||example.com^"
    regexFilter?: string;       // alternative to urlFilter
    resourceTypes?: ResourceType[];
    excludedResourceTypes?: ResourceType[];
    requestDomains?: string[];
    initiatorDomains?: string[];
    excludedRequestDomains?: string[];
    requestMethods?: string[];  // 'get' | 'post' | 'put' | 'delete' | ...
    responseHeaders?: HeaderFilter[];  // Chrome 128+
    tabIds?: number[];          // session rules only
    isUrlFilterCaseSensitive?: boolean;
  };
}
```

`ResourceType`: `main_frame` `sub_frame` `stylesheet` `script` `image` `font`
`object` `xmlhttprequest` `ping` `csp_report` `media` `websocket` `webtransport`
`webbundle` `other`

### Rule Sets

| Type | Limit | Persistence | Method |
|------|-------|-------------|--------|
| Static (in files) | 50 enabled simultaneously | Permanent | `updateEnabledRulesets()` |
| Dynamic | 30,000 | Permanent across sessions | `updateDynamicRules()` |
| Session | 5,000 | Cleared on browser shutdown | `updateSessionRules()` |

### Methods

```ts
// Dynamic rules
chrome.declarativeNetRequest.updateDynamicRules({
  addRules?: Rule[],
  removeRuleIds?: number[]
}): Promise<void>
chrome.declarativeNetRequest.getDynamicRules(filter?: { ruleIds? }): Promise<Rule[]>

// Session rules (ephemeral)
chrome.declarativeNetRequest.updateSessionRules({
  addRules?: Rule[],
  removeRuleIds?: number[]
}): Promise<void>
chrome.declarativeNetRequest.getSessionRules(filter?): Promise<Rule[]>

// Static rulesets (defined in manifest)
chrome.declarativeNetRequest.updateEnabledRulesets({
  enableRulesetIds?: string[],
  disableRulesetIds?: string[]
}): Promise<void>
chrome.declarativeNetRequest.getEnabledRulesets(): Promise<string[]>

// Debugging
chrome.declarativeNetRequest.getMatchedRules(filter?): Promise<{ rulesMatchedInfo }>
chrome.declarativeNetRequest.testMatchOutcome(request, options?): Promise<{ matchedRules }>
```

### Example Rules

```json
[
  {
    "id": 1,
    "priority": 1,
    "action": { "type": "block" },
    "condition": { "urlFilter": "||ads.example.com^", "resourceTypes": ["script", "image"] }
  },
  {
    "id": 2,
    "priority": 1,
    "action": { "type": "upgradeScheme" },
    "condition": { "urlFilter": "||example.com^", "resourceTypes": ["main_frame"] }
  },
  {
    "id": 3,
    "priority": 1,
    "action": {
      "type": "modifyHeaders",
      "requestHeaders": [{ "header": "X-Custom", "operation": "set", "value": "hello" }]
    },
    "condition": { "urlFilter": "||api.example.com^" }
  }
]
```

---

## chrome.offscreen (MV3)

Use for DOM operations that can't be done in a service worker.
Permission: `"offscreen"`
Docs: `https://developer.chrome.com/docs/extensions/reference/api/offscreen`

Only one offscreen document can exist per extension at a time.

### Methods

```ts
chrome.offscreen.createDocument(parameters: {
  url: string,           // relative path to bundled HTML file
  reasons: Reason[],
  justification: string
}): Promise<void>

chrome.offscreen.closeDocument(): Promise<void>
chrome.offscreen.getContexts(): Promise<ExtensionContext[]>  // check if exists
```

### Reason Values

`TESTING` `AUDIO_PLAYBACK` `IFRAME_SCRIPTING` `DOM_SCRAPING` `BLOBS`
`DOM_PARSER` `USER_MEDIA` `DISPLAY_MEDIA` `WEB_RTC` `CLIPBOARD`
`LOCAL_STORAGE` `WORKERS` `BATTERY_STATUS` `MATCH_MEDIA` `GEOLOCATION`

### Pattern: Service Worker ↔ Offscreen Communication

```js
// sw.js — create offscreen document before using DOM
async function ensureOffscreen() {
  const contexts = await chrome.runtime.getContexts({
    contextTypes: ['OFFSCREEN_DOCUMENT']
  });
  if (contexts.length === 0) {
    await chrome.offscreen.createDocument({
      url: 'offscreen.html',
      reasons: ['DOM_PARSER'],
      justification: 'Parse HTML content',
    });
  }
}

// sw.js — send message to offscreen
await ensureOffscreen();
const result = await chrome.runtime.sendMessage({ type: 'parseHTML', html: rawHtml });

// offscreen.js — receive and respond
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'parseHTML') {
    const doc = new DOMParser().parseFromString(msg.html, 'text/html');
    sendResponse({ title: doc.title });
  }
  return true;
});
```
