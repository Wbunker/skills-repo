# Interactive Debugging

Live debugging tools for stepping through Playwright tests and exploring locators. For post-mortem analysis of recorded traces, see [trace-viewer.md](trace-viewer.md).

## Contents

- [UI Mode](#ui-mode) — `--ui` watch mode + time-travel
- [Playwright Inspector](#playwright-inspector) — `--debug`, `page.pause()`
- [VS Code extension](#vs-code-extension) — run/debug/record/pick inline
- [Headed mode & slow motion](#headed-mode--slow-motion)
- [PWDEBUG & verbose logging](#pwdebug--verbose-logging)
- [Codegen](#codegen) — record tests, assertions, Pick Locator
- [Codegen for authenticated / emulated sessions](#codegen-for-authenticated--emulated-sessions)
- [Locator tools](#locator-tools) — `page.pickLocator()`, `locator.normalize()`
- [CLI debugger for agents](#cli-debugger-for-agents) — `--debug=cli`
- [Dashboard for bound browsers](#dashboard-for-bound-browsers)
- [Trace CLI](#trace-cli) — explore traces from the command line
- [Post-failure analysis](#post-failure-analysis)

## UI Mode

Time-travel debugging with watch mode — the primary interactive tool.

```bash
npx playwright test --ui
# Remote (Docker / Codespaces):
npx playwright test --ui-host=0.0.0.0 --ui-port=8080
```

> ⚠️ Binding `0.0.0.0` exposes traces, credentials, and secrets to other machines on the network.

Filter tests by name, `@tag`, project, and status (passed/failed/skipped). Setup-dependency tests must be run manually before dependents.

Panes:
- **Timeline** — color-coded actions/navigations; hover previews snapshots, double-click selects a time range that filters the Actions tab and logs.
- **Actions** — each action's locator + duration; Before/After tabs show DOM state transitions on hover.
- **Source** — highlights the line for the hovered action; "Open in VSCode" jumps to it.
- **Call** — action metadata: time, locator, strict-mode status, key inputs.
- **Log** — backend activity: scrolling, element-wait states, action execution.
- **Errors** — failure messages with red timeline markers.
- **Console** / **Network** — browser+test logs; sortable requests with headers/body on click.
- **Attachments** — visual-diff slider for `toHaveScreenshot` comparisons (see [visual-comparisons.md](visual-comparisons.md)).
- **Metadata** — browser, viewport, duration.

**Watch mode**: click the eye icon per-test (or globally) to auto-re-run on file change.
**Pick Locator**: hover the DOM snapshot to highlight elements; edit in the playground and copy verified locators.
**DOM snapshot pop-out**: detach a snapshot to its own window for independent DevTools inspection.

## Playwright Inspector

```bash
npx playwright test --debug
npx playwright test example.spec.ts:10 --debug   # start at a specific line
npx playwright test --project=chromium --debug
```

- Step through actions with the toolbar; live-edit locators in the **Pick Locator** field.
- When paused on an action, actionability checks (visibility, enabled, stable, scroll position) are already in the **log**.
- Skip stepping from the top by pausing exactly where needed:

```javascript
await page.pause();
```

## VS Code Extension

- Set breakpoints next to line numbers; right-click → **Debug Test** opens the browser in break mode. Error output shows expected vs. received + full call log.
- **Live debugging**: click a locator in the editor to highlight matching element(s) in the browser; edit it and see matches update live.
- **Pick locator** button (testing sidebar) copies a resilient locator (prioritizing role/text/test-id) into the file.
- **Record new** / **Record at cursor** generate or append actions inline.
- Right-click the debug icon → **Select Default Profile** to pick Chromium/Firefox/WebKit.
- Use **Run Test** (not Debug) with **Show Browser** on to keep the session alive for continuous Chrome DevTools use.

## Headed Mode & Slow Motion

```bash
npx playwright test --headed
```

```javascript
await chromium.launch({ headless: false, slowMo: 100 }); // ms delay per action
```

## PWDEBUG & Verbose Logging

```bash
PWDEBUG=console npx playwright test   # opens browser, exposes `playwright` in DevTools console
DEBUG=pw:api npx playwright test      # verbose API logs
```

In the DevTools console: `playwright.$()`, `playwright.$$()`, `playwright.inspect()`, `playwright.locator()`, `playwright.selector()`.

## Codegen

Records interactions into test code, picking the best locator (role > text > test id).

```bash
npx playwright codegen
npx playwright codegen https://playwright.dev
```

Opens a browser + Inspector. Toolbar assertion buttons generate:
- `assert visibility` — element is visible
- `assert text` — element contains text
- `assert value` — input has a value

**Pick Locator**: stop recording, click **Pick Locator**, hover to preview, click to capture.

Useful flags: `--target=python` (language), `--save-trace=trace.zip`, `--ignore-https-errors`,
`--test-id-attribute=data-pw` (match your `testIdAttribute`), `--block-service-workers`.

## Codegen for Authenticated / Emulated Sessions

Record while logged in by persisting/reusing storage state (see [auth.md](auth.md)):

```bash
npx playwright codegen github.com/login --save-storage=auth.json   # log in once, save state
npx playwright codegen --load-storage=auth.json github.com         # replay authenticated
npx playwright codegen --user-data-dir=/path/to/data/ [URL]        # reuse a browser profile
```

Emulation flags (see [emulation.md](emulation.md)):

```bash
npx playwright codegen --device="iPhone 13" playwright.dev
npx playwright codegen --viewport-size="800,600" playwright.dev
npx playwright codegen --color-scheme=dark playwright.dev
npx playwright codegen --timezone="Europe/Rome" --lang="it-IT" playwright.dev
npx playwright codegen --geolocation="41.890221,12.492348" playwright.dev
```

## Locator Tools

```javascript
await page.pickLocator();      // interactive: hover highlights, click returns the Locator (v1.59+)
const best = locator.normalize();  // rewrite to best-practice form (test ids / ARIA roles) (v1.59+)
```

Both aid agentic test generation/maintenance. See [locators.md](locators.md).

## CLI Debugger for Agents

Headless, command-line stepping over `playwright-cli` — built for agents (v1.59+).

```bash
npx playwright test --debug=cli
### Debugging Instructions
- Run "playwright-cli attach tw-87b59e" to attach to this test
```

Then drive it:

```bash
playwright-cli --session tw-87b59e step-over
```

## Dashboard for Bound Browsers

Observe and intervene in browsers launched by tests/agents (v1.59+). See [agent-cli.md](agent-cli.md).

```javascript
const { endpoint } = await browser.bind('my-session', {
  workspaceDir: '/my/project',
});
```

```bash
playwright-cli show          # open the Dashboard listing all bound browsers + statuses
PLAYWRIGHT_DASHBOARD=1 ...    # auto-bind every @playwright/test browser to the Dashboard
```

## Trace CLI

Explore a recorded trace from the command line without the GUI (v1.59+):

```bash
npx playwright trace open test-results/example.spec.ts-chromium/trace.zip
npx playwright trace actions --grep="expect"   # list matching actions
npx playwright trace action 9                  # inspect one action
npx playwright trace snapshot 9 --name after   # dump a DOM snapshot
```

## Inspecting console, errors & requests in-test

Snapshot recent browser activity without wiring event listeners (v1.56+):

```typescript
const msgs = await page.consoleMessages();   // recent console messages
const errs = await page.pageErrors();        // recent uncaught page errors
const reqs = await page.requests();          // recent network requests (see network.md)
```

These are handy assertions/log dumps when a test misbehaves. The HTML reporter's **Speedboard** tab
(v1.57+) lists tests by duration to find slow spots; the merged-report **Timeline** (v1.58+) charts
execution across environments.

## Post-Failure Analysis

The Trace Viewer GUI is the primary tool for analyzing already-recorded failures (CI runs, `trace: 'on-first-retry'`). See [trace-viewer.md](trace-viewer.md).
