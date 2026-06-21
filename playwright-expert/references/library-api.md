# Playwright Library API

Using the Playwright **library** directly (`playwright` package) for automation, scraping, and standalone scripts — without the `@playwright/test` runner. For tests, prefer the runner (see [writing-tests.md](writing-tests.md)).

## Contents
- [Library vs test runner](#library-vs-test-runner)
- [Install](#install)
- [Launching browsers](#launching-browsers)
- [Browser contexts](#browser-contexts)
- [Persistent context](#persistent-context)
- [storageState](#storagestate)
- [Pages & lifecycle](#pages--lifecycle)
- [Multiple contexts & pages](#multiple-contexts--pages)
- [Connecting to existing browsers](#connecting-to-existing-browsers)
- [Electron & Android (experimental)](#electron--android-experimental)
- [WebView2 apps](#webview2-apps)
- [bind / unbind](#bind--unbind)
- [Managing browser binaries](#managing-browser-binaries)
- [Complete minimal script](#complete-minimal-script)

## Library vs test runner

> "Under most circumstances, for end-to-end testing, you'll want to use `@playwright/test` (Playwright Test), and not `playwright` (Playwright Library) directly."

Use the **library** (`playwright`) for: scraping, automation scripts, bots, screenshot/PDF generation, embedding browser control in an app. Use the **test runner** (`@playwright/test`) when you want fixtures, auto-contexts, web-first assertions, parallelization, config matrices, and reporters — see [writing-tests.md](writing-tests.md), [fixtures.md](fixtures.md), [test-config.md](test-config.md).

## Install

```bash
npm i -D playwright              # library only
npm i -D @playwright/test        # test runner (includes the library)
```

Then download browser binaries:

```bash
npx playwright install chromium firefox webkit
```

Or auto-download via helper packages (no separate `install` step):

```bash
npm i -D @playwright/browser-chromium @playwright/browser-firefox @playwright/browser-webkit
```

## Launching browsers

```javascript
const { chromium, firefox, webkit } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  // ... use browser
  await browser.close();
})();
```

`browserType.launch(options) → Promise<Browser>`. Key options:

- `headless` [boolean] — run headless. Defaults to `true`.
- `slowMo` [number] — slow each operation by N ms (debugging).
- `args` [Array<string>] — extra browser CLI args.
- `channel` [string] — branded distribution channel.
- `ignoreDefaultArgs` [boolean | Array<string>] — drop Playwright's default args.

```javascript
firefox.launch({ headless: false, slowMo: 50 });

const browser = await chromium.launch({
  ignoreDefaultArgs: ['--mute-audio']
});
```

**Channels** run the installed branded browser instead of Playwright's bundled Chromium:

```javascript
const browser = await chromium.launch({ channel: 'chrome' });   // also 'msedge'
```

Available channels: `chrome`, `msedge`, `chrome-beta`, `msedge-beta`, `chrome-dev`, `msedge-dev`, `chrome-canary`, `msedge-canary`. See [emulation.md](emulation.md) for device/viewport options.

> **Chrome for Testing (v1.57+):** the default Chromium is now a Chrome-for-Testing build — headed runs use `chrome`, headless uses `chrome-headless-shell` (arm64 Linux still uses Chromium).
> **Removed (v1.58):** the `devtools` launch option — use `args: ['--auto-open-devtools-for-tabs']` instead.

## Browser contexts

A `BrowserContext` is an isolated "incognito" session — separate cookies, storage, and cache. Cheap to create; use one per independent user/session.

```javascript
const browser = await chromium.launch();
const context = await browser.newContext();
const page = await context.newPage();
await context.close();
await browser.close();
```

`browser.newContext(options) → Promise<BrowserContext>`. Pass emulation/device options here (see [emulation.md](emulation.md)):

```javascript
const { chromium, devices } = require('playwright');
const context = await browser.newContext(devices['iPhone 11']);
```

## Persistent context

`browserType.launchPersistentContext(userDataDir, options) → Promise<BrowserContext>` launches a browser with a **persistent on-disk profile** (cookies, localStorage, extensions survive across runs) and returns the single context. Closing the context closes the browser.

```javascript
const { chromium } = require('playwright');

const context = await chromium.launchPersistentContext('/path/to/user-data-dir', {
  headless: false,
  channel: 'chrome',
});
const page = await context.newPage();
await page.goto('https://example.com');
// no browser handle — close the context
await context.close();
```

## storageState

For lightweight, file-based session reuse (instead of a full persistent profile), pass `storageState` to `newContext`:

```javascript
const context = await browser.newContext({ storageState: 'state.json' });
```

> "Populates context with given storage state. This option can be used to initialize context with logged-in information obtained via `browserContext.storageState()`."

Full save/restore auth recipe (including `storageState({ path })`) is in [auth.md](auth.md).

## Pages & lifecycle

`context.newPage() → Promise<Page>` creates a tab inside a context.

`browser.newPage(options) → Promise<Page>` is a shortcut that creates a **new context + page**; closing the page closes that context. Use it only for one-off single-page scripts — it does not share state with other pages.

```javascript
const browser = await webkit.launch();
const page = await browser.newPage();   // implicit context
await page.goto('https://playwright.dev/');
await browser.close();
```

For navigation, actions, and waiting, see [actions.md](actions.md) and [locators.md](locators.md); for assertions in non-test scripts, see [assertions.md](assertions.md).

## Multiple contexts & pages

Isolate parallel sessions (e.g. two logged-in users) in one browser process:

```javascript
const browser = await chromium.launch();
const userContext = await browser.newContext();
const adminContext = await browser.newContext();
const adminPage = await adminContext.newPage();
const userPage = await userContext.newPage();
```

## Connecting to existing browsers

**connectOverCDP** — attach to a running Chromium over the Chrome DevTools Protocol (the browser must be started with `--remote-debugging-port`):

```javascript
const browser = await playwright.chromium.connectOverCDP('http://localhost:9222');
```

`browserType.connectOverCDP(endpointURL, options) → Promise<Browser>`. Chromium only. Options:

- `noDefaults` [boolean] *(v1.60+)* — "When true, Playwright will not apply its default overrides to existing default browser context."
- `artifactsDir` [string] *(v1.61+)* — "If specified, browser artifacts (traces, downloads) are saved into this directory."
- `isLocal` [boolean] *(v1.58+)* — hint that the CDP server runs on the same host, enabling filesystem optimizations.

**connect** — attach to a Playwright server started via `BrowserType.launchServer()`:

```javascript
// server process
const server = await chromium.launchServer({ port: 9876 });   // → BrowserServer
const wsEndpoint = server.wsEndpoint();
// ... later: await server.close()  (or server.kill())

// client process
const browser = await chromium.connect(wsEndpoint);
```

`browserType.connect(wsEndpoint, options) → Promise<Browser>` — options include `headers`, `slowMo`,
`timeout`, `exposeNetwork` (let the remote browser reach the client's network). Client and server
major+minor versions must match. **BrowserServer** (`launchServer`'s return) exposes `wsEndpoint()`,
`process()`, `close()`, `kill()`, and `on('close')` — use it to run a shared/remote browser farm that
many `connect()` clients dial into.

### Raw CDP access (Chromium)

Drop to the Chrome DevTools Protocol when Playwright lacks an API for something:

```javascript
const session = await context.newCDPSession(page);   // page/frame-scoped CDP
await session.send('Animation.enable');
const rate = await session.send('Animation.getPlaybackRate');
session.on('Animation.animationCreated', () => {});  // or on('event', ({method, params}) => …)
await session.detach();                               // stop the session
const browserSession = await browser.newBrowserCDPSession();  // browser-scoped CDP
```

Other `Browser` members: `version()`, `isConnected()`, `browserType()`, `contexts()`, and
`on('disconnected')`.

## Electron & Android (experimental)

Catch timeouts specifically with `playwright.errors.TimeoutError` (thrown by `waitFor`, actions with a
`timeout`, `launch`, etc.):

```javascript
try {
  await page.locator('text=Foo').click({ timeout: 100 });
} catch (error) {
  if (error instanceof playwright.errors.TimeoutError) console.log('Timeout!');
}
```

The `playwright` module also exposes experimental entry points (and `playwright.errors.TimeoutError`
for catching timeouts):

```javascript
const { _electron: electron } = require('playwright');
const app = await electron.launch({ args: ['main.js'] });  // launch an Electron app
const window = await app.firstWindow();                     // drive its BrowserWindow like a Page
// reach into the Electron MAIN process (the key Electron capability):
const appPath = await app.evaluate(async ({ app }) => app.getAppPath());
await window.click('text=Click me');
await app.close();
```

`ElectronApplication` also has `windows()`, `browserWindow(page)`, `context()` (for context-wide
routing), `evaluateHandle()`, and `on('window')`/`on('close')`.

```javascript
const { _android: android } = require('playwright');
const [device] = await android.devices();    // attach to a connected Android device (adb)
const context = await device.launchBrowser();// drive Chrome for Android as a normal context/page
const page = await context.newPage();
await page.goto('https://webkit.org/');
await device.shell('am start -n com.android.chrome/...');  // raw shell; also installApk/push, model/serial/info
await context.close();
await device.close();
```

`AndroidDevice` also drives **native** UI: `device.input` (`tap`/`swipe`/`drag`/`press`/`type`),
widget gestures (`tap`/`fill`/`scroll`/`fling`/`longTap`/`pinchOpen`/`pinchClose`/`swipe`), `wait()`,
`screenshot()`, and `device.open()` → an `AndroidSocket`. For app WebViews, `device.webView()` returns
an `AndroidWebView` whose `.page()` gives a normal Playwright `Page`.

Both are experimental (underscore-prefixed) and Chromium-only; APIs may change. For desktop web views
on Windows see [WebView2 apps](#webview2-apps).

## WebView2 apps

WebView2 is a WinForms control that renders web content via Edge/Chromium — automate it over CDP.
Launch the host app with a remote-debugging port (env var `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS`),
then `connectOverCDP` and grab the existing context/page:

```javascript
const browser = await playwright.chromium.connectOverCDP('http://localhost:9222');
const context = browser.contexts()[0];
const page = context.pages()[0];
```

```bash
# the WinForms app reads these before creating the WebView2 control:
WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--remote-debugging-port=9222
WEBVIEW2_USER_DATA_FOLDER=/unique/dir/per/worker   # required for parallel tests (else they share one profile)
```

Wrap the app spawn + `connectOverCDP` in a worker-scoped `browser` [fixture](fixtures.md) (one CDP
port and user-data dir per `workerIndex`) for parallel runs.

## bind / unbind

*(v1.59+)* Expose an already-launched `Browser` to external clients — the Playwright CLI, MCP, debugging tools, or other Playwright clients — over a server endpoint, without relaunching.

```javascript
const browser = await chromium.launch();
const { endpoint } = await browser.bind('my-session');   // optional: { host, port, metadata, workspaceDir }
// ... share `endpoint` with a CLI/MCP/another client
await browser.unbind();
```

- `browser.bind(title, options) → Promise<Object>` — returns an object with an `endpoint` property. `title` identifies the server; options: `host`, `port`, `metadata`, `workspaceDir`.
- `browser.unbind() → Promise<void>` — unbinds the previously bound server.

Useful for handing a live browser to the agent CLI or MCP-driven tooling — see [agent-cli.md](agent-cli.md) and [debugging.md](debugging.md).

## Managing browser binaries

```bash
npx playwright install                          # install default browsers
npx playwright install webkit                   # one browser
npx playwright install --with-deps chromium     # + Linux system deps
npx playwright install --with-deps --only-shell # headless shell only (skip full Chromium)
npx playwright install --with-deps --no-shell   # new headless mode, no shell
npx playwright install --list                   # list installed browsers
npx playwright uninstall                         # remove this project's browsers
npx playwright uninstall --all                   # remove all Playwright browsers
```

Channels (`chrome`/`msedge`) use a system-installed branded browser, so they don't require `npx playwright install`.

Download-control env vars (corporate networks / CI caching):

| Var | Effect |
|---|---|
| `PLAYWRIGHT_DOWNLOAD_HOST` | Fetch browser binaries from an internal mirror instead of the Microsoft CDN (per-browser: `PLAYWRIGHT_FIREFOX_DOWNLOAD_HOST`, …). |
| `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD` | Skip the automatic browser download on `npm install`. |
| `PLAYWRIGHT_BROWSERS_PATH` | Install/look up browsers in a shared path (good for CI caches); `=0` installs into the local `node_modules` (hermetic). |
| `PLAYWRIGHT_SKIP_BROWSER_GC` | `=1` disables automatic removal of stale browser builds. |
| `HTTPS_PROXY` | Download through a proxy. `NODE_EXTRA_CA_CERTS` adds a custom CA for the download. |

**Headless modes:** the default Chromium download includes `chrome-headless-shell` (fast, used by
headless runs). For the *new* headless mode (real Chrome rendering) use `channel: 'chromium'`, and
install accordingly — `npx playwright install --only-shell` (shell only) or `--no-shell` (new mode,
skip the shell).

## Complete minimal script

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });   // launch
  const context = await browser.newContext();                    // isolated session
  const page = await context.newPage();                          // tab
  await page.goto('https://playwright.dev/');                    // navigate
  await page.getByRole('link', { name: 'Get started' }).click(); // action
  await page.screenshot({ path: 'example.png' });
  await context.close();
  await browser.close();                                         // close
})();
```

Run with `node my-script.js`.

> **Tracing:** in library mode, start/stop tracing on the context (`context.tracing.start/stop`) and open with `npx playwright show-trace` — see [trace-viewer.md](trace-viewer.md). For request interception/mocking in scripts, see [network.md](network.md).
