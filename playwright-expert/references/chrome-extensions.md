# Testing Chrome Extensions

Extensions load **only in Chromium, via a persistent context** (Chrome/Edge removed the side-loading
flags). Run headed or in the new headless mode. The pattern: launch a persistent context with the
extension args, then derive the extension ID from its background service worker.

## Contents
- [Launching with an extension](#launching-with-an-extension)
- [Getting the extension ID](#getting-the-extension-id)
- [Fixtures (context + extensionId)](#fixtures-context--extensionid)
- [Testing the popup](#testing-the-popup)
- [MV2 vs MV3 & caveats](#mv2-vs-mv3--caveats)

## Launching with an extension

```javascript
const { chromium } = require('playwright');
const path = require('path');

const pathToExtension = path.join(__dirname, 'my-extension');
const context = await chromium.launchPersistentContext('', {
  channel: 'chromium',
  args: [
    `--disable-extensions-except=${pathToExtension}`,
    `--load-extension=${pathToExtension}`,
  ],
});
```

See [library-api.md](library-api.md#persistent-context) for persistent-context basics.

## Getting the extension ID

The ID is the host segment of the background service worker's URL (MV3):

```javascript
let [serviceWorker] = context.serviceWorkers();
if (!serviceWorker)
  serviceWorker = await context.waitForEvent('serviceworker');
const extensionId = serviceWorker.url().split('/')[2];
```

## Fixtures (context + extensionId)

Wrap it in [fixtures](fixtures.md) so every test gets a configured `context` and the `extensionId`:

```typescript
// fixtures.ts
import { test as base, chromium, type BrowserContext } from '@playwright/test';
import path from 'path';

export const test = base.extend<{
  context: BrowserContext;
  extensionId: string;
}>({
  context: async ({ }, use) => {
    const pathToExtension = path.join(__dirname, 'my-extension');
    const context = await chromium.launchPersistentContext('', {
      channel: 'chromium',
      args: [
        `--disable-extensions-except=${pathToExtension}`,
        `--load-extension=${pathToExtension}`,
      ],
    });
    await use(context);
    await context.close();
  },
  extensionId: async ({ context }, use) => {
    let [serviceWorker] = context.serviceWorkers();
    if (!serviceWorker)
      serviceWorker = await context.waitForEvent('serviceworker');
    const extensionId = serviceWorker.url().split('/')[2];
    await use(extensionId);
  },
});

export const expect = test.expect;
```

```typescript
// usage
import { test, expect } from './fixtures';

test('content script changes the page', async ({ page }) => {
  await page.goto('https://example.com');
  await expect(page.locator('body')).toHaveText('Changed by my-extension');
});
```

## Testing the popup

Navigate to the extension's popup via its `chrome-extension://` URL:

```typescript
test('popup page', async ({ page, extensionId }) => {
  await page.goto(`chrome-extension://${extensionId}/popup.html`);
  await expect(page.locator('body')).toHaveText('my-extension popup');
});
```

## MV2 vs MV3 & caveats

- **MV3** uses a **service worker** (`context.serviceWorkers()` / `waitForEvent('serviceworker')`).
  **MV2** uses a background **page** (`context.backgroundPages()` / `waitForEvent('backgroundpage')`).
- **Service-worker suspension (MV3):** an `evaluate()` already in flight when the worker suspends
  throws `Service Worker restarted`; new calls queue transparently after restart.
- A persistent context shares no state with other tests — use a per-test context (the fixture above)
  for isolation, and an empty `''` userDataDir for a fresh profile each run.
