# Visual Comparisons, Screenshots & Video

Pixel-diff snapshot assertions, ad-hoc screenshots, and video recording in `@playwright/test`.

## Contents
- [Visual comparisons (`toHaveScreenshot`)](#visual-comparisons-tohavescreenshot)
- [Snapshot naming & directory layout](#snapshot-naming--directory-layout)
- [Updating baselines](#updating-baselines)
- [`toHaveScreenshot` options](#tohavescreenshot-options)
- [`toMatchSnapshot` for arbitrary content](#tomatchsnapshot-for-arbitrary-content)
- [Reviewing diffs](#reviewing-diffs)
- [Ad-hoc screenshots](#ad-hoc-screenshots)
- [Video recording](#video-recording)

## Visual comparisons (`toHaveScreenshot`)

```typescript
import { test, expect } from '@playwright/test';

test('example test', async ({ page }) => {
  await page.goto('https://playwright.dev');
  await expect(page).toHaveScreenshot();
});
```

**First run generates the baseline, then fails** — there is no reference image to compare against, so the first run writes the baseline and reports the test as failed. Re-run to get a passing comparison. On generation, Playwright retries the capture until two consecutive screenshots match before saving the baseline (built-in stabilization).

Works on a page or any locator:

```typescript
await expect(page.getByRole('button')).toHaveScreenshot();
```

Custom name (recommended for stability across reorders):

```typescript
await expect(page).toHaveScreenshot('landing.png');
// path segments
await expect(page).toHaveScreenshot(['relative', 'path', 'to', 'snapshot.png']);
```

`toHaveScreenshot` is a retrying web-first assertion — it polls until the screenshot matches or the timeout elapses, so it's stable against in-flight rendering.

## Snapshot naming & directory layout

Auto-generated name pattern: `{testName}-{number}-{projectName}-{platform}.png` (e.g. `example-test-1-chromium-darwin.png`). Platform suffix means baselines are OS-specific — generate them in the same environment (or container) used in CI.

Default layout, next to the test file:

```
tests/
  example.spec.ts
  example.spec.ts-snapshots/
    example-test-1-chromium-darwin.png
```

Customize location/name with `snapshotPathTemplate` in config — see [test-config.md](./test-config.md). Commit baselines to version control.

## Updating baselines

```bash
npx playwright test --update-snapshots
# short flag
npx playwright test -u
```

Update only a subset by passing a test file/grep along with `--update-snapshots`. `--update-snapshots=changed` updates only mismatched snapshots (vs `all`).

## `toHaveScreenshot` options

```typescript
await expect(page).toHaveScreenshot({ maxDiffPixels: 100 });
```

| Option | Purpose |
|---|---|
| `maxDiffPixels` | Max number of differing pixels allowed. |
| `maxDiffPixelRatio` | Max ratio (0–1) of differing pixels to total. |
| `threshold` | Per-pixel YIQ color-distance tolerance, 0–1 (default `0.2`). |
| `animations: 'disabled'` | Freeze CSS animations/transitions to their end state (default for `toHaveScreenshot`). Use `'allow'` to keep them. |
| `caret: 'hide'` | Hide the text caret (default). `'initial'` keeps it. |
| `mask` | Array of locators painted over with a solid box. |
| `maskColor` | CSS color for masked boxes (default pink `#FF00FF`). |
| `stylePath` | CSS file(s) applied before capture to hide volatile elements. |
| `fullPage` | Capture the full scrollable page (page screenshots only). |
| `clip` | `{ x, y, width, height }` region to capture. |
| `omitBackground` | Transparent background for PNG. |
| `scale` | `'css'` (default) or `'device'` for hi-DPI. |
| `timeout` | Max time for the retrying assertion. |

Mask volatile regions:

```typescript
await expect(page).toHaveScreenshot({
  mask: [page.locator('.ad-banner')],
  maskColor: '#FF00FF',
});
```

Hide elements with injected CSS (`screenshot.css`):

```css
iframe {
  visibility: hidden;
}
```

```typescript
await expect(page).toHaveScreenshot({ stylePath: path.join(__dirname, 'screenshot.css') });
```

Configure globally in `playwright.config.ts`:

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  expect: {
    toHaveScreenshot: {
      maxDiffPixels: 100,
      stylePath: './screenshot.css',
    },
  },
});
```

## `toMatchSnapshot` for arbitrary content

Compare text or binary buffers (not just images):

```typescript
expect(await page.textContent('.hero__title')).toMatchSnapshot('hero.txt');
```

Stored in the same `{testFile}-snapshots/` directory; updated with `--update-snapshots`. Prefer `toHaveScreenshot`/`toMatchAriaSnapshot` for visuals; reserve `toMatchSnapshot` for arbitrary text/binary.

## Reviewing diffs

On mismatch, Playwright writes three images as test attachments: **expected**, **actual**, and **diff**.

- **HTML report** (`npx playwright show-report`): the failed test shows a side-by-side / slider diff viewer for the three images.
- **Trace viewer**: open the trace's **Attachments** tab to inspect the same images. See [trace-viewer.md](./trace-viewer.md).

## Ad-hoc screenshots

Not assertions — just capture an image to disk or buffer.

```typescript
// to file
await page.screenshot({ path: 'screenshot.png' });

// full scrollable page
await page.screenshot({ path: 'screenshot.png', fullPage: true });

// to buffer (no path)
const buffer = await page.screenshot();
console.log(buffer.toString('base64'));

// single element
await page.locator('.header').screenshot({ path: 'screenshot.png' });
```

Common options (shared by `page.screenshot` and `locator.screenshot`):

| Option | Purpose |
|---|---|
| `path` | Output file; extension (`.png`/`.jpg`) infers the format. |
| `fullPage` | Full scrollable page (page only). |
| `clip` | `{ x, y, width, height }` capture region. |
| `mask` / `maskColor` | Cover locators with a solid box. |
| `animations: 'disabled'` | Freeze animations to end state. |
| `type: 'png' \| 'jpeg'` | Explicit format when no `path`. |
| `quality` | 0–100, JPEG only. |
| `omitBackground` | Transparent background (PNG/`type:'png'`). |
| `scale: 'css' \| 'device'` | DPI scaling. |
| `caret: 'hide' \| 'initial'` | Text caret handling. |
| `timeout` | Capture timeout. |

```typescript
await page.screenshot({
  path: 'clip.jpg',
  type: 'jpeg',
  quality: 80,
  clip: { x: 0, y: 0, width: 640, height: 480 },
  mask: [page.locator('.secret')],
  animations: 'disabled',
});
```

## Video recording

Configure via the `video` test option in `playwright.config.ts`:

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    video: 'on-first-retry',
  },
});
```

Modes:

| Mode | Behavior |
|---|---|
| `'off'` | No video (default). |
| `'on'` | Record every test (large artifacts). |
| `'on-first-retry'` | Record only on the first retry. |
| `'retain-on-failure'` | Record all, keep only for failed tests. |
| `'on-all-retries'` | Record on every retry (v1.61+). |
| `'retain-on-first-failure'` | Record the first run; keep only if it fails (v1.61+). |
| `'retain-on-failure-and-retries'` | Keep on failure and on any retry (v1.61+). |

Access the recording programmatically via `page.video()` — `path()` (file location), `saveAs(path)`
(copy elsewhere; waits for recording to finish), `delete()`. In library mode, enable with the
`recordVideo: { dir, size }` context option; the file is finalized when the context closes.

Set size and (optionally) on-frame action/test annotations:

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    video: {
      mode: 'on-first-retry',
      size: { width: 640, height: 480 },
      show: {
        actions: {
          duration: 500,
          position: 'top-right',
          fontSize: 14,
        },
        test: {
          level: 'step',
          position: 'top-left',
          fontSize: 12,
        },
      },
    },
  },
});
```

Access the recorded file path (video is only available after the page/context closes):

```typescript
const path = await page.video().path();
```

Library (non-test) recording:

```typescript
const context = await browser.newContext({ recordVideo: { dir: 'videos/' } });
// ...
await context.close();
```

Videos are slow-motion screen captures; for action-annotated, step-by-step playback prefer the trace's screencast — see [screencast.md](./screencast.md) and [trace-viewer.md](./trace-viewer.md).
