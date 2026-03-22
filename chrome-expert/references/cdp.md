# Chrome DevTools Protocol (CDP)

Docs: `https://chromedevtools.github.io/devtools-protocol/`

CDP lets you automate Chrome programmatically — inspect DOM, intercept network, capture screenshots,
debug JavaScript, and more. Puppeteer and Playwright are built on top of CDP.

## Protocol Versions

| Version | Stability | Notes |
|---------|-----------|-------|
| Tip-of-tree | Unstable | Latest features, may change between Chrome releases |
| Stable 1.3 | Stable | Subset of Chrome 64; safe for production automation |
| v8-inspector | Node.js | Used by Node.js debugger |

## Connecting to Chrome

### Launch Chrome with Remote Debugging

```bash
# Full Chrome (headless)
google-chrome --headless=new --remote-debugging-port=9222

# Or non-headless (for interactive debugging)
google-chrome --remote-debugging-port=9222

# Specify user data dir (avoid conflicts with running Chrome)
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug
```

### Discover Available Targets

```bash
# Browser info + WebSocket URL
curl http://localhost:9222/json/version

# List open tabs/targets
curl http://localhost:9222/json/list

# Full protocol definition as JSON
curl http://localhost:9222/json/protocol
```

```json
// Response from /json/version
{
  "Browser": "Chrome/135.0.0.0",
  "webSocketDebuggerUrl": "ws://localhost:9222/devtools/browser/...",
  "V8-Version": "13.5.212.7"
}
```

### WebSocket Connection

```python
import asyncio
import json
import websockets

async def cdp_example():
    # Connect to a page target
    async with websockets.connect("ws://localhost:9222/devtools/page/{targetId}") as ws:
        # Send a command
        await ws.send(json.dumps({
            "id": 1,
            "method": "Page.navigate",
            "params": { "url": "https://example.com" }
        }))
        response = json.loads(await ws.recv())
        print(response)

asyncio.run(cdp_example())
```

### Python with `playwright` or `pycdp`

```python
# Playwright (recommended — wraps CDP)
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()
    await page.goto("https://example.com")
    title = await page.title()
    await browser.close()

# Direct CDP via playwright
cdp = await page.context.new_cdp_session(page)
await cdp.send("Network.enable")
await cdp.send("Network.setExtraHTTPHeaders", { "headers": { "X-Custom": "value" } })
```

## Key CDP Domains

### Page

```js
Page.navigate({ url })           // Navigate to URL
Page.reload({ ignoreCache? })    // Reload page
Page.captureScreenshot({         // Take screenshot
  format: 'png' | 'jpeg' | 'webp',
  quality?,                      // 0-100, jpeg only
  clip?: { x, y, width, height, scale },
  captureBeyondViewport?: boolean
})
Page.printToPDF({                // Print to PDF
  landscape?, paperWidth?, paperHeight?,
  marginTop/Bottom/Left/Right?,
  printBackground?, scale?
})
Page.getFrameTree()              // Get all frames
Page.enable()                    // Enable Page domain events
```

Events: `Page.loadEventFired`, `Page.domContentEventFired`, `Page.navigatedWithinDocument`, `Page.frameNavigated`

### Network

```js
Network.enable({ maxTotalBufferSize?, maxResourceBufferSize? })
Network.disable()
Network.setExtraHTTPHeaders({ headers })   // Add headers to all requests
Network.setCacheDisabled({ cacheDisabled })
Network.emulateNetworkConditions({
  offline, latency, downloadThroughput, uploadThroughput
})
Network.setBlockedURLs({ urls })           // Block URL patterns
Network.getCookies({ urls? })
Network.setCookie({ name, value, url, domain?, path?, secure?, httpOnly?, sameSite?, expires? })
Network.clearBrowserCookies()
Network.getResponseBody({ requestId })     // Get response body after request
```

Events: `Network.requestWillBeSent`, `Network.responseReceived`, `Network.loadingFinished`, `Network.loadingFailed`

### DOM

```js
DOM.getDocument({ depth? })                          // Get root DOM node
DOM.querySelector({ nodeId, selector })              // CSS selector
DOM.querySelectorAll({ nodeId, selector })
DOM.getAttributes({ nodeId })                        // All attributes
DOM.setAttributeValue({ nodeId, name, value })
DOM.removeAttribute({ nodeId, name })
DOM.getOuterHTML({ nodeId? })
DOM.setOuterHTML({ nodeId, outerHTML })
DOM.focus({ nodeId? })
DOM.scrollIntoViewIfNeeded({ nodeId? })
DOM.getBoxModel({ nodeId? })                         // Position and size
```

### Runtime

```js
Runtime.evaluate({
  expression: string,
  returnByValue?: boolean,       // return value instead of reference
  awaitPromise?: boolean,
  userGesture?: boolean,         // simulate user gesture
  contextId?: number,
})
// Returns: { result: RemoteObject, exceptionDetails? }

Runtime.callFunctionOn({
  functionDeclaration: string,
  objectId?: string,
  arguments?: CallArgument[],
  returnByValue?: boolean,
  awaitPromise?: boolean,
})

Runtime.getProperties({ objectId, ownProperties? })  // Enumerate object properties
```

### Input

```js
Input.dispatchMouseEvent({ type, x, y, button?, clickCount?, modifiers? })
// type: 'mousePressed' | 'mouseReleased' | 'mouseMoved' | 'mouseWheel'

Input.dispatchKeyEvent({ type, key, code?, modifiers? })
// type: 'keyDown' | 'keyUp' | 'rawKeyDown' | 'char'

Input.insertText({ text })  // Type text directly

Input.dispatchTouchEvent({ type, touchPoints })
```

### Emulation

```js
Emulation.setDeviceMetricsOverride({
  width, height, deviceScaleFactor,
  mobile, screenWidth?, screenHeight?,
})
Emulation.setGeolocationOverride({ latitude, longitude, accuracy })
Emulation.setUserAgentOverride({ userAgent })
Emulation.setTimezoneOverride({ timezoneId })  // e.g. 'America/New_York'
Emulation.setLocaleOverride({ locale })        // e.g. 'fr-FR'
Emulation.setCPUThrottlingRate({ rate })       // 1 = no throttle, 4 = 4x slower
```

### Target (Browser-level)

```js
Target.getTargets()              // List all targets (pages, workers, etc.)
Target.createTarget({ url })     // Open new tab
Target.closeTarget({ targetId })
Target.attachToTarget({ targetId, flatten? })
```

### Fetch (Request Interception)

```js
Fetch.enable({ patterns?: [{ urlPattern, resourceType?, requestStage? }] })
// requestStage: 'Request' | 'Response'

Fetch.disable()

// After enable, Fetch.requestPaused fires for matching requests:
Fetch.continueRequest({ requestId, url?, headers?, postData? })
Fetch.fulfillRequest({ requestId, responseCode, responseHeaders, body? })
Fetch.failRequest({ requestId, errorReason })
Fetch.getResponseBody({ requestId })
Fetch.continueResponse({ requestId, responseCode?, responseHeaders? })
```

### CSS

```js
CSS.enable()
CSS.getComputedStyleForNode({ nodeId })
CSS.getMatchedStylesForNode({ nodeId })
CSS.setStyleTexts({ edits: [{ styleSheetId, range, text }] })
```

## Protocol Message Format

All messages are JSON over WebSocket.

**Command (client → Chrome):**
```json
{ "id": 1, "method": "Page.navigate", "params": { "url": "https://example.com" } }
```

**Response (Chrome → client):**
```json
{ "id": 1, "result": { "frameId": "...", "loaderId": "..." } }
```

**Error response:**
```json
{ "id": 1, "error": { "code": -32600, "message": "Invalid Request" } }
```

**Event (Chrome → client, no id):**
```json
{ "method": "Network.responseReceived", "params": { "requestId": "...", ... } }
```

## Multiple DevTools Clients

Chrome 63+ supports multiple simultaneous CDP clients. All clients receive the same events.
Commands from different clients are interleaved — coordinate if needed.
