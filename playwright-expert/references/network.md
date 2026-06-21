# Network

Observing, routing, mocking, and recording network traffic — HTTP, WebSocket, and API requests. All examples use TypeScript with `@playwright/test`.

## Contents

- [Observing requests & responses](#observing-requests--responses)
- [Waiting for requests/responses](#waiting-for-requestsresponses)
- [URL matching](#url-matching)
- [Routing & mocking](#routing--mocking)
- [Modifying requests](#modifying-requests)
- [Modifying responses](#modifying-responses)
- [HAR record & replay](#har-record--replay)
- [Tracing HAR](#tracing-har-v160)
- [API testing (`request` fixture)](#api-testing-request-fixture)
- [WebSocket mocking](#websocket-mocking)
- [Mocking browser APIs](#mocking-browser-apis)
- [Service workers](#service-workers)
- [Network `use` options](#network-use-options)

## Observing requests & responses

`route` intercepts; `page.on` only observes (cannot modify).

```typescript
page.on('request', request => console.log('>>', request.method(), request.url()));
page.on('response', response => console.log('<<', response.status(), response.url()));
await page.goto('https://example.com');
```

WebSocket frames are observe-only via events (to *mock*, see [WebSocket mocking](#websocket-mocking)):

```typescript
page.on('websocket', ws => {
  console.log(`opened: ${ws.url()}`);
  ws.on('framesent', event => console.log(event.payload));
  ws.on('framereceived', event => console.log(event.payload));
  ws.on('close', () => console.log('closed'));
});
```

## Waiting for requests/responses

Start the wait *before* the action, then await after — avoids races.

```typescript
const responsePromise = page.waitForResponse('**/api/fetch_data');   // glob
await page.getByText('Update').click();
const response = await responsePromise;
```

```typescript
const responsePromise = page.waitForResponse(/\.jpeg$/);             // regex
const responsePromise = page.waitForResponse(r => r.url().includes(token) && r.status() === 200); // predicate
```

`page.waitForRequest(urlOrPredicate)` is the request-side equivalent.

Recent-activity getters (v1.56+): `page.requests()`, `page.consoleMessages()`, and `page.pageErrors()` return the most recent items without wiring up event listeners — see [debugging.md](debugging.md). **Service workers (v1.57+):** their network requests are now reported and routable through the BrowserContext (Chromium only); disable via `PLAYWRIGHT_DISABLE_SERVICE_WORKER_NETWORK`.

## URL matching

All routing/waiting APIs accept the same matcher forms:

- **Glob**: `*` matches any char except `/`; `**` matches any incl. `/`; `?` is literal `?`; `{png,jpg}` alternation; `\` escapes. e.g. `'**/*.{png,jpg,jpeg}'`, `'*/**/api/v1/fruits'`.
- **RegExp**: `/\.css$/`.
- **Predicate**: `(url: URL) => boolean`.

Glob matching is against the full URL, including query string. Relative globs resolve against `baseURL`.

## Routing & mocking

`page.route(url, handler)` (page-scoped) and `context.route(url, handler)` (all pages in context). Handler receives a `Route`; you must terminate it with exactly one of `fulfill` / `continue` / `abort` / `fallback`.

```typescript
// Mock a JSON response — never hits the network
await page.route('*/**/api/v1/fruits', async route => {
  const json = [{ name: 'Strawberry', id: 21 }];
  await route.fulfill({ json });
});
```

```typescript
// Raw body / status
await page.route('**/api/fetch_data', route => route.fulfill({ status: 200, body: testData }));
await context.route('**/api/login', route => route.fulfill({ status: 200, body: 'accept' }));
```

```typescript
// Abort selectively (block images/css for speed)
await page.route('**/*.{png,jpg,jpeg}', route => route.abort());
await context.route(/\.css$/, route => route.abort());
await page.route('**/*', route =>
  route.request().resourceType() === 'image' ? route.abort() : route.continue());
```

**`route.fallback()`** defers to the next-registered matching handler. Handlers run in **reverse registration order** (last registered runs first); `fallback()` chains downward. Use it to layer overrides:

```typescript
await page.route('**/*', route => route.continue());                 // registered first → runs last
await page.route('**/*', async route => {                            // runs first
  const headers = route.request().headers();
  headers['x-test'] = '1';
  await route.fallback({ headers });                                 // pass overrides down the chain
});
```

`route.continue()` and `route.fallback()` accept the same override options: `url`, `method`, `headers`, `postData`.

## Modifying requests

```typescript
await page.route('**/*', async route => {
  const headers = route.request().headers();
  delete headers['X-Secret'];
  await route.continue({ headers });
});

await page.route('**/*', route => route.continue({ method: 'POST' }));
```

## Modifying responses

`route.fetch()` performs the real request and returns an `APIResponse`; pass it as `response` to `fulfill`, overriding `body`/`json`/`headers` as needed.

```typescript
// Text rewrite
await page.route('**/title.html', async route => {
  const response = await route.fetch();
  let body = await response.text();
  body = body.replace('<title>', '<title>My prefix:');
  await route.fulfill({
    response,
    body,
    headers: { ...response.headers(), 'content-type': 'text/html' },
  });
});

// JSON augment
await page.route('*/**/api/v1/fruits', async route => {
  const response = await route.fetch();
  const json = await response.json();
  json.push({ name: 'Loquat', id: 100 });
  await route.fulfill({ response, json });
});
```

## HAR record & replay

**Replay** from a recorded HAR with `page.routeFromHAR(har, options)` (also `context.routeFromHAR`):

```typescript
await page.routeFromHAR('./hars/fruit.har', {
  url: '*/**/api/v1/fruits',   // string | RegExp — only route matching entries
  update: false,               // true = re-record HAR from live network
});
await page.goto('https://demo.playwright.dev/api-mocking');
```

`routeFromHAR` options:
- `url`: `string | RegExp` — limit which requests are served/recorded from this HAR.
- `update`: `boolean` — when `true`, record the HAR with live traffic instead of replaying.
- `updateContent`: `'embed' | 'attach'` — resource-body storage policy when updating.
- `updateMode`: `'full' | 'minimal'` — `minimal` records only routing-essential info.
- `notFound`: `'abort' | 'fallback'` — behavior when no HAR entry matches (`abort` = fail, `fallback` = hit network).

**Record** via context option `recordHar` (in `browser.newContext` / `newPage` / test `use`):

```typescript
recordHar: {
  path: string,                          // required
  content: 'omit' | 'embed' | 'attach',  // default: attach for .zip, embed otherwise
  mode: 'full' | 'minimal',              // minimal = routing info only
  urlFilter: string | RegExp,            // glob or regex
  // omitContent: boolean                // deprecated — use `content`
}
```

## Tracing HAR (v1.60+)

`context.tracing.startHar(path, options)` records a HAR into a running trace; returns a `Disposable` for `await using` auto-cleanup.

```typescript
await context.tracing.startHar('trace.har');
const page = await context.newPage();
await page.goto('https://playwright.dev');
await context.tracing.stopHar();
```

`startHar` options:
- `content`: `'omit' | 'embed' | 'attach'` — default `attach` for `.zip`, `embed` otherwise.
- `mode`: `'full' | 'minimal'` — `minimal` records only routing info.
- `urlFilter`: `string | RegExp`.
- `resourcesDir`: `string` — where response bodies go when `content: 'attach'`.

`startHar(): Promise<Disposable>` / `stopHar(): Promise<void>`.

## API testing (`request` fixture)

The `request` fixture is an `APIRequestContext` — full HTTP client, isolated from the browser, shares the test's `baseURL` and `extraHTTPHeaders`. Methods: `get` `post` `put` `patch` `delete` `head` `fetch`.

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    baseURL: 'https://api.github.com',
    extraHTTPHeaders: {
      'Accept': 'application/vnd.github.v3+json',
      'Authorization': `token ${process.env.API_TOKEN}`,
    },
  },
});
```

```typescript
test('create + read issue', async ({ request }) => {
  const created = await request.post(`/repos/${USER}/${REPO}/issues`, {
    data: { title: '[Bug] report 1', body: 'Bug description' },
  });
  await expect(created).toBeOK();                    // status 200-299

  const issues = await request.get(`/repos/${USER}/${REPO}/issues`);
  expect(await issues.json()).toContainEqual(
    expect.objectContaining({ title: '[Bug] report 1' }));
});
```

Request options: `data` (JSON/string/Buffer), `params` (query), `headers`, `multipart` (file uploads), `form`, `timeout`, `failOnStatusCode`.

**Manual context** (e.g. mix API setup with a browser test) — dispose when done:

```typescript
let apiContext: APIRequestContext;
test.beforeAll(async ({ playwright }) => {
  apiContext = await playwright.request.newContext({
    baseURL: 'https://api.github.com',
    extraHTTPHeaders: { 'Authorization': `token ${process.env.API_TOKEN}` },
  });
});
test.afterAll(async () => { await apiContext.dispose(); });
```

**Reuse auth across API + browser** via `storageState` (see also [auth.md](auth.md)):

```typescript
const requestContext = await request.newContext({
  httpCredentials: { username: 'user', password: 'passwd' },
});
await requestContext.get('https://api.example.com/login');
await requestContext.storageState({ path: 'state.json' });

const context = await browser.newContext({ storageState: 'state.json' });
```

`context.request` shares cookies with its `BrowserContext`; `playwright.request.newContext()` is fully isolated.

## WebSocket mocking

`page.routeWebSocket(url, handler)` intercepts WS connections. The handler gets a `WebSocketRoute`. By default a routed socket does **not** connect to the real server — call `connectToServer()` to bridge it.

```typescript
// Pure mock — no server
await page.routeWebSocket('wss://example.com/ws', ws => {
  ws.onMessage(message => {
    if (message === 'request')
      ws.send('response');
  });
});
```

```typescript
// Intercept + forward to real server, modifying en route
await page.routeWebSocket('/ws', ws => {
  const server = ws.connectToServer();
  ws.onMessage(message => {
    server.send(message === 'request' ? 'request2' : message);
  });
});
```

Calling `onMessage()` disables automatic page→server forwarding; your handler then controls routing. After `connectToServer()`, server→page also auto-forwards unless you override.

`WebSocketRoute` methods:
- `connectToServer(): WebSocketRoute` — connect to real server, returns the server-side route.
- `send(message: string | Buffer): void`
- `onMessage(handler: (message: string) => void | Promise<void>): void`
- `onClose(handler: (code?: number, reason?: string) => void | Promise<void>): void`
- `close(options?: { code?: number; reason?: string }): Promise<void>`
- `url(): string`
- `protocols(): string[]` — requested subprotocols (v1.60+)

```typescript
// Subprotocol negotiation (v1.60+)
await page.routeWebSocket('wss://example.com/ws', ws => {
  if (ws.protocols().includes('chat.v2'))
    ws.onMessage(msg => ws.send(JSON.stringify({ version: 2, echo: msg })));
  else
    ws.close({ code: 1002, reason: 'Unsupported protocol' });
});
```

> Traces now capture WebSocket requests (v1.61+) — inspect frames in the [Trace Viewer](trace-viewer.md).

## Mocking browser APIs

Use `page.addInitScript(fn)` to inject a mock **before any page script runs** (call before navigation). Common for `navigator.*`, `geolocation`, custom globals. See also [emulation.md](emulation.md).

```typescript
await page.addInitScript(() => {
  const mockBattery = {
    level: 0.75, charging: true,
    chargingTime: 1800, dischargingTime: Infinity,
    addEventListener: () => {},
  };
  window.navigator.getBattery = async () => mockBattery;
});
```

Read-only properties need `Object.defineProperty`:

```typescript
await page.addInitScript(() => {
  Object.defineProperty(Object.getPrototypeOf(navigator), 'cookieEnabled', { value: false });
});
```

Stateful mock with event dispatch (expose on `window` to drive it from tests):

```typescript
await page.addInitScript(() => {
  class BatteryMock {
    level = 0.10; charging = false;
    _levelListeners: Array<() => void> = [];
    addEventListener(name: string, cb: () => void) {
      if (name === 'levelchange') this._levelListeners.push(cb);
    }
    _setLevel(v: number) { this.level = v; this._levelListeners.forEach(cb => cb()); }
  }
  const mockBattery = new BatteryMock();
  (window.navigator as any).getBattery = async () => mockBattery;
  (window as any).mockBattery = mockBattery;
});
```

## Service workers

By default (`serviceWorkers: 'allow'`) requests made *by* a service worker are reported and routable
(Chromium). Set `serviceWorkers: 'block'` to disable SW registration entirely — useful when an MSW/SW
mock interferes with your own `route` handlers, or for predictable network interception.

```typescript
// playwright.config.ts — or test.use({ serviceWorkers: 'block' })
use: { serviceWorkers: 'block' }
```

Distinguish and route SW-owned requests:

```typescript
await context.route('**', async route => {
  if (route.request().serviceWorker())
    await route.fulfill({ status: 200, contentType: 'text/plain', body: 'from sw' });
  else
    await route.continue();
});
```

- `request.serviceWorker()` — the `Worker` that issued the request (or `null`).
- `response.fromServiceWorker()` — `true` if the SW's Cache/`respondWith` served it.
- Wait for the worker via `context.waitForEvent('serviceworker')`, and (if needed) for activation
  before evaluating against it.
- **Limitation:** requests for the *updated* service-worker main script can't currently be routed.
- Globally disable just the network-events behavior with `PLAYWRIGHT_DISABLE_SERVICE_WORKER_NETWORK`.

## Network `use` options

Context-wide network behavior is set in `use` (config / project / `test.use`) rather than per-route —
full list in [test-config.md](test-config.md#the-use-block):

```typescript
use: {
  extraHTTPHeaders: { Authorization: `token ${process.env.API_TOKEN}` },  // sent with every request
  httpCredentials: { username: 'user', password: 'pass' },                // HTTP basic auth
  ignoreHTTPSErrors: true,                                                 // accept self-signed certs
  offline: true,                                                          // emulate no connectivity
  acceptDownloads: true,                                                  // default; auto-accept downloads
  proxy: { server: 'http://myproxy:3128', bypass: '.internal.com' },
  clientCertificates: [{ origin: 'https://example.com', certPath: 'cert.pem', keyPath: 'key.pem' }],
}
```

`extraHTTPHeaders`, `httpCredentials`, and `baseURL` are shared by the [`request` fixture](#api-testing-request-fixture)
too. `proxy` can also be set per-context in [library mode](library-api.md).

---

Related: [actions.md](actions.md) · [auth.md](auth.md) · [emulation.md](emulation.md) · [trace-viewer.md](trace-viewer.md) · [test-config.md](test-config.md) · [library-api.md](library-api.md)
