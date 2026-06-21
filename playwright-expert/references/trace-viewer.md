# Trace Viewer — Debugging with Traces

A trace is a complete, replayable recording of a test run: every action, before/after DOM snapshots,
a screenshot film-strip, network, console, source, and errors. The **Trace Viewer** is a GUI for
exploring it after the run — the single best tool for debugging failures, especially on CI where you
can't watch the browser.

## Contents
- [The debugging workflow](#the-debugging-workflow)
- [Enabling traces (config)](#enabling-traces-config)
- [Trace modes — which to use](#trace-modes--which-to-use)
- [Recording from the CLI](#recording-from-the-cli)
- [Opening a trace](#opening-a-trace)
- [Reading the Trace Viewer UI](#reading-the-trace-viewer-ui)
- [Snapshots: Before / Action / After](#snapshots-before--action--after)
- [Programmatic tracing (library API)](#programmatic-tracing-library-api)
- [Multiple traces per context: chunks](#multiple-traces-per-context-chunks)
- [Debugging recipes](#debugging-recipes)

## The debugging workflow

1. A test fails (locally or in CI) — make sure a trace was recorded (see modes below).
2. Open the trace: `npx playwright show-trace trace.zip`, or click the trace icon in the HTML report,
   or drag the file onto <https://trace.playwright.dev>.
3. Click the **failing action** (red) in the Actions list → read the **Errors** tab and the
   highlighted **Source** line.
4. Compare the **Before** vs **Action** snapshot to see what the page actually looked like when the
   action ran (wrong element? not visible yet? overlay intercepting the click?).
5. Cross-check the **Console** and **Network** tabs at that moment for the real cause (failed API
   call, JS error, unexpected redirect).

## Enabling traces (config)

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  retries: process.env.CI ? 2 : 0,
  use: {
    trace: 'on-first-retry',   // default in scaffolded configs
  },
});
```

## Trace modes — which to use

| Mode | Behavior | Use when |
|------|----------|----------|
| `'off'` | No tracing | Tracing not needed |
| `'on'` | Trace every test | Local debugging only — **performance-heavy, not for CI** |
| `'retain-on-failure'` | Trace every test, keep only failures | You want a trace for any failure, no retries needed |
| `'on-first-retry'` | Trace only the first retry of a failed test | **Recommended CI default** — cheap, traces only flaky/failing tests |
| `'on-all-retries'` | Trace every retry | Hunting hard-to-reproduce flakes across retries |

> `on-first-retry` records **nothing** on a passing run or the first failing run — only when a failed
> test is retried. If a test fails without retries configured, you get no trace; use
> `retain-on-failure` or `--trace on` instead.

## Recording from the CLI

```bash
npx playwright test --trace on      # force a trace for every test, ignoring config
npx playwright show-report          # open HTML report; click the trace icon next to a test
```

## Opening a trace

```bash
npx playwright show-trace trace.zip                       # local file
npx playwright show-trace https://example.com/trace.zip   # remote file
```

Or use the zero-install web viewer at <https://trace.playwright.dev> (runs fully in-browser, nothing
is uploaded to a server). For a remote trace, pass it as a query param:
```
https://trace.playwright.dev/?trace=https://.../trace.zip
```

Traces are stored in the test output dir and surfaced in the HTML report — click the trace icon on a
test, or open the test and use the Traces section.

## Reading the Trace Viewer UI

| Panel | What it tells you |
|-------|-------------------|
| **Actions** (left) | Every action with the **locator used** and how long it took. Click one to inspect everything about that moment. Failing actions show in red. |
| **Timeline / film-strip** (top) | Screenshot screencast across the run. Hover to scrub; **double-click an action** to select its time range and filter everything to it. |
| **Snapshots** (center) | The live DOM at the selected action — Before / Action / After tabs (see below). Pop out and use browser DevTools on the snapshot; pick a locator against it. |
| **Source** | The exact line of test code for the selected action, highlighted. |
| **Call** | Action metadata: duration, exact locator, strict-mode status, params/keys pressed. |
| **Log** | The behind-the-scenes log Playwright produced — scrolling into view, waiting for visible/stable/enabled, then the action. Shows *why* an action waited or timed out. |
| **Errors** | Error messages for the failure; the timeline marks the error with a red line and the Source tab points at the failing line. |
| **Console** | Browser **and** test console output, with icons distinguishing origin. Double-click an action to filter to that moment. |
| **Network** | Every request, filterable by type/status/method/URL/content-type/duration/size. Click one for headers, body, and response. As of **v1.61** traces (and HAR) also include **WebSocket** requests. |
| **Attachments** | Test attachments — including visual-regression image diffs (actual / expected / overlay slider). |
| **Metadata** | Browser, viewport, duration, and other run metadata. |

## Snapshots: Before / Action / After

With `snapshots` on (the default), Playwright captures full DOM snapshots per action — these are
*interactive*, not images, so you can hover and inspect with DevTools:

| Tab | What it shows |
|-----|---------------|
| **Before** | The page state the instant the action started |
| **Action** | The state during input — highlights the exact click point / target element |
| **After** | The state right after the action completed |

This Before/Action triplet is usually how you diagnose a bad locator or a not-yet-ready element:
if the **Action** snapshot highlights the wrong element (or nothing), the locator is the problem; if
**Before** shows a spinner/overlay, you acted too early.

## Programmatic tracing (library API)

When not using the test runner (raw `playwright` library), drive tracing on the context:

```javascript
const browser = await chromium.launch();
const context = await browser.newContext();

// Start before creating the page.
await context.tracing.start({ screenshots: true, snapshots: true, sources: true });

const page = await context.newPage();
await page.goto('https://playwright.dev');

// Stop and export.
await context.tracing.stop({ path: 'trace.zip' });
```

`tracing.start()` options:

| Option | Meaning |
|--------|---------|
| `screenshots` | Capture screenshots to build the timeline film-strip |
| `snapshots` | Capture interactive DOM snapshots per action + record network |
| `sources` | Include source files for actions (enables the Source tab) |
| `name` | Intermediate trace file name prefix |
| `title` | Trace name shown in the viewer |
| `live` | Write unarchived, live-updating trace files |

`tracing.stop({ path })` exports the trace to a `.zip` (omit `path` to discard).

## Multiple traces per context: chunks

Record several independent traces within one context using chunks:

```javascript
await context.tracing.start({ screenshots: true, snapshots: true });
const page = await context.newPage();
await page.goto('https://playwright.dev');

await context.tracing.startChunk();
await page.getByText('Get Started').click();
await context.tracing.stopChunk({ path: 'trace1.zip' });   // one action

await context.tracing.startChunk();
await page.goto('http://example.com');
await context.tracing.stopChunk({ path: 'trace2.zip' });   // another action
```

`tracing.group(name)` / `tracing.groupEnd()` create nestable visual groups in the viewer — but
prefer `test.step()` when using the test runner.

## Debugging recipes

- **"Element not found / timeout"** → open the trace, click the failing action, read the **Log** tab
  (what it waited for) and the **Before** snapshot (was the element present/visible?). Check the
  **Call** tab for the exact locator.
- **"Worked locally, fails on CI"** → keep `trace: 'on-first-retry'`, download the CI
  `playwright-report/` artifact, open the trace. The film-strip + network tab usually reveal an
  environment difference (timing, missing API, different data).
- **"Clicked the wrong thing"** → the **Action** snapshot highlights what was actually targeted;
  compare to your intended element.
- **"Flaky failure"** → set `trace: 'on-all-retries'` to capture every retry and compare the passing
  vs failing trace side by side.
- **Visual diff failures** → use the **Attachments** tab's actual/expected/overlay slider.

> Trace files can contain sensitive data (cookies, tokens, response bodies). Treat CI trace
> artifacts as secrets.
