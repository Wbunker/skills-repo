# What's New in Playwright

A changelog/highlights index summarizing recent Playwright releases. Each feature names the exact API and links to the sibling reference that documents it in depth. Most recent release first.

## Contents

- [1.61](#161) — WebAuthn passkeys, Web Storage API, expanded video modes, WebSocket in HAR/trace
- [1.60](#160) — first-class HAR recording, `locator.drop()`, page-level aria snapshots, `test.abort()`, `getByRole` description
- [1.59](#159) — `page.screencast` capture API, `browser.bind()`, agentic `--debug=cli`, storage state
- [1.58](#158) — report Timeline, `system` theme, `connectOverCDP({ isLocal })`; removed `_react`/`_vue` selectors
- [1.57](#157) — Chrome for Testing, `webServer.wait`, `locator.describe()`, service-worker routing
- [1.56](#156) — **Test Agents** (planner/generator/healer), `page.consoleMessages()`/`pageErrors()`/`requests()`
- [Browser versions](#browser-versions)

## 1.61

- WebAuthn virtual authenticator / passkeys via `browserContext.credentials` with `credentials.create()` and `credentials.install()` — see [auth.md](auth.md).
- Web Storage API: `page.localStorage` and `page.sessionStorage` with `setItem()`, `getItem()`, `items()` — see [auth.md](auth.md) (storage state) and [actions.md](actions.md).
- Network response details: `apiResponse.securityDetails()` and `apiResponse.serverAddr()` — see [network.md](network.md).
- `browserType.connectOverCDP()` gains an `artifactsDir` option for artifact storage — see [library-api.md](library-api.md).
- `screencast.showActions()` cursor decoration option, and `screencast.start()` callback now receives a frame timestamp — see [screencast.md](screencast.md).
- Expanded `testOptions.video` modes: `'on-all-retries'`, `'retain-on-first-failure'`, `'retain-on-failure-and-retries'` — see [visual-comparisons.md](visual-comparisons.md).
- `expect.soft.poll(...)` support — see [assertions.md](assertions.md).
- Config introspection: `fullConfig.argv` (snapshot of process arguments) and `fullConfig.failOnFlakyTests` — see [test-config.md](test-config.md).
- `testInfo.errors` lists `AggregateError` sub-errors separately — see [debugging.md](debugging.md).
- `-G` command-line shorthand for `--grep-invert` — see [test-organization.md](test-organization.md).
- HAR and trace recordings now include WebSocket requests — see [network.md](network.md) and [trace-viewer.md](trace-viewer.md).
- Ubuntu 26.04 support — see [tooling.md](tooling.md).

### Breaking changes / removals

- No breaking removals listed in the 1.61 release notes.

## 1.60

- First-class HAR recording: `tracing.startHar()` / `tracing.stopHar()` with `Disposable` support — see [network.md](network.md).
- `locator.drop()` simulates external drag-and-drop for files and clipboard data — see [actions.md](actions.md).
- Page-level aria snapshots: `expect(page).toMatchAriaSnapshot()` now works on `Page` (in addition to `Locator`); `locator.ariaSnapshot()` / `page.ariaSnapshot()` gain a `boxes` option appending bounding boxes — see [assertions.md](assertions.md).
- `test.abort()` aborts the currently running test with an optional message — see [test-organization.md](test-organization.md).
- `getByRole()` gains a `description` option for accessible-description matching — see [locators.md](locators.md) and [actions.md](actions.md).
- BrowserContext lifecycle events: `browser.on('context')` plus context-level `on('download')`, `on('frameattached')`, `on('framedetached')`, `on('framenavigated')`, `on('pageclose')`, `on('pageload')` — see [library-api.md](library-api.md).
- `expect(locator).toHaveCSS()` gains a `pseudo` option for `::before`/`::after` styles — see [assertions.md](assertions.md).
- `locator.highlight()` gains a `style` option; `page.hideHighlight()` clears highlights — see [debugging.md](debugging.md).
- `webSocketRoute.protocols()` returns requested WebSocket subprotocols — see [network.md](network.md).
- `browserType.connectOverCDP()` gains a `noDefaults` option to disable default overrides — see [library-api.md](library-api.md).
- `webError.location()` mirrors `consoleMessage.location()`; `consoleMessage.location()` exposes `line`/`column` (`lineNumber`/`columnNumber` deprecated) — see [debugging.md](debugging.md).
- `testInfoError.errorContext` surfaces diagnostic context; `reporter.onError()` receives a `workerInfo` argument — see [debugging.md](debugging.md) and [test-config.md](test-config.md).
- `testProject.snapshotPathTemplate` gains a `{testFileBaseName}` token — see [visual-comparisons.md](visual-comparisons.md).
- HTML reporter improvements: `.zip` file support, attachment indicators, `repeatEachIndex` display; Trace Viewer JSON/form body pretty-print toggle — see [trace-viewer.md](trace-viewer.md).

### Breaking changes / removals

- Removed `Locator.ariaRef()` — see [assertions.md](assertions.md).
- Removed the `handle` option on `BrowserContext.exposeBinding` / `Page.exposeBinding` — see [library-api.md](library-api.md).
- Removed the `logger` option on `BrowserType.connect` / `connectOverCDP` — see [library-api.md](library-api.md).
- Removed the `videosPath` / `videoSize` context options — see [visual-comparisons.md](visual-comparisons.md).

## 1.59

- `page.screencast` unified video capture API: `screencast.start()` / `screencast.stop()` (with `onFrame` callback), `screencast.showActions()` / `screencast.hideActions()`, `screencast.showChapter()`, `screencast.showOverlay()`, `screencast.showOverlays()` / `screencast.hideOverlays()` — see [screencast.md](screencast.md).
- `browser.bind()` makes a launched browser available for CLI/MCP/client connection (optional `host`/`port`); `browser.unbind()` stops accepting new connections — see [library-api.md](library-api.md).
- Storage state: `browserContext.setStorageState()` clears and sets new storage state atomically — see [auth.md](auth.md).
- Console/error capture: `page.clearConsoleMessages()` / `page.clearPageErrors()`, `page.consoleMessages()` / `page.pageErrors()` with a `filter` option, and `consoleMessage.timestamp()` — see [debugging.md](debugging.md).
- Context utilities: `browserContext.debugger` (programmatic debugger control) and `browserContext.isClosed()` — see [library-api.md](library-api.md).
- Request/response: `request.existingResponse()` (returns response without waiting) and `response.httpVersion()` — see [network.md](network.md).
- CDP session events: `cdpSession.on('event')` / `cdpSession.on('close')` — see [library-api.md](library-api.md).
- `tracing.start()` gains a `live` option for real-time updates; `browserType.launch()` gains an `artifactsDir` option — see [trace-viewer.md](trace-viewer.md) and [library-api.md](library-api.md).
- Aria snapshots: `page.ariaSnapshot()` captures page-level snapshot; `locator.ariaSnapshot()` gains `depth` and `mode` options — see [assertions.md](assertions.md).
- Locator authoring: `locator.normalize()` converts to best-practice locators; `page.pickLocator()` / `page.cancelPickLocator()` for interactive element selection — see [locators.md](locators.md).
- Trace/video mode `'retain-on-failure-and-retries'` retains all traces on failure — see [visual-comparisons.md](visual-comparisons.md).
- UI Mode source-change filtering; UI Mode and Trace Viewer improved action filtering; HTML Reporter run lists per worker and step search filtering — see [trace-viewer.md](trace-viewer.md) and [debugging.md](debugging.md).
- CLI: `playwright-cli attach` connects to a bound browser; `playwright-cli show` Dashboard displays bound browsers; `npx playwright test --debug=cli` agentic test debugging; `npx playwright trace` CLI analysis commands — see [agent-cli.md](agent-cli.md), [screencast.md](screencast.md), and [debugging.md](debugging.md).

### Breaking changes / removals

- Removed macOS 14 support for WebKit — see [tooling.md](tooling.md).
- Removed the `@playwright/experimental-ct-svelte` package — see [components.md](components.md).
- `junit` reporter now differentiates failure vs. error types — see [test-config.md](test-config.md).

## 1.58

- HTML report **Timeline** chart (merged-report Speedboard tab) showing test execution across environments — see [debugging.md](debugging.md).
- UI Mode / Trace Viewer: new `'system'` theme (follows OS), in-editor search (Cmd/Ctrl+F), reorganized network panel, auto-formatted JSON — see [trace-viewer.md](trace-viewer.md).
- `browserType.connectOverCDP()` gains an `isLocal` option for filesystem optimizations when on the same host as the CDP server — see [library-api.md](library-api.md).

### Breaking changes / removals

- Removed the `_react` / `_vue` selector engines and the `:light` selector suffix — use role/text/CSS locators instead. See [locators.md](locators.md).
- Removed the `devtools` option from `browserType.launch()` — use `args: ['--auto-open-devtools-for-tabs']`. See [library-api.md](library-api.md).
- Dropped macOS 13 support for WebKit — see [tooling.md](tooling.md).

## 1.57

- **Chrome for Testing**: Playwright now runs Chrome-for-Testing builds instead of Chromium (headed = `chrome`, headless = `chrome-headless-shell`; arm64 Linux still uses Chromium) — see [library-api.md](library-api.md).
- `testConfig.webServer` gains a `wait` field (regex on stdout/stderr, with named capture groups → env vars) to wait for server readiness — see [test-config.md](test-config.md).
- `testConfig.tag` adds tags to every test in a run (handy for merged reports) — see [test-organization.md](test-organization.md).
- `locator.describe()` sets a human-readable description (used by `locator.toString()` and traces); `locator.description()` reads it back — see [locators.md](locators.md).
- `locator.click()` / `locator.dragTo()` accept a `steps` option configuring intermediate mousemove events — see [actions.md](actions.md).
- Service-worker network requests are now reported and routable via BrowserContext (Chromium); disable with `PLAYWRIGHT_DISABLE_SERVICE_WORKER_NETWORK` — see [network.md](network.md).
- `worker.on('console')` event and `worker.waitForEvent()` console support; HTML reporter **Speedboard** tab (tests by duration) — see [debugging.md](debugging.md).

### Breaking changes / removals

- Removed `page.accessibility` (3-year deprecation) — use an external library such as Axe. See [assertions.md](assertions.md).
- Dropped Chromium extension manifest v2 support.

## 1.56

- **Test Agents**: three LLM-driven agent definitions — planner, generator, healer — generated with `npx playwright init-agents --loop=claude` (also `vscode`/`codex`/`opencode`). See [test-agents.md](test-agents.md).
- Recent-activity getters: `page.consoleMessages()`, `page.pageErrors()`, `page.requests()` — see [debugging.md](debugging.md) and [network.md](network.md).
- CLI `--test-list` / `--test-list-invert` to run an explicit list of tests from a file — see [tooling.md](tooling.md).
- UI Mode / HTML reporter: single-worker run, mirror `--update-snapshots`, merge/collapse blocks, toggle "Copy prompt"; aria snapshots now render input `placeholder` — see [debugging.md](debugging.md) and [assertions.md](assertions.md).

### Breaking changes / removals

- `browserContext.on('backgroundpage')` deprecated (not emitted); `browserContext.backgroundPages()` returns an empty list — see [library-api.md](library-api.md).

## Browser versions

| Release | Chromium | Firefox | WebKit |
| --- | --- | --- | --- |
| 1.61 | 149.0.7827.55 | 151.0 | 26.5 |
| 1.60 | 148.0.7778.96 | 150.0.2 | 26.4 |
| 1.59 | 147.0.7727.15 | 148.0.2 | 26.4 |
| 1.58 | 145.0.7632.6 | 146.0.1 | 26.0 |
| 1.57 | 143.0.7499.4 | 144.0.2 | 26.0 |
| 1.56 | 141.0.7390.37 | 142.0.1 | 26.0 |
