# Device & Environment Emulation

Simulate devices, viewports, locale, timezone, geolocation, permissions, color scheme, user agent, network, and JS state. Every option below applies at three levels: global `use` in config, per-`projects[].use`, or per-test/block via `test.use()`. Lower (more specific) levels override higher ones.

## Contents
- [Devices registry](#devices-registry)
- [Viewport](#viewport)
- [isMobile / hasTouch / deviceScaleFactor](#ismobile--hastouch--devicescalefactor)
- [Locale & timezone](#locale--timezone)
- [Permissions](#permissions)
- [Geolocation](#geolocation)
- [Color scheme & media](#color-scheme--media)
- [User agent](#user-agent)
- [Offline mode](#offline-mode)
- [JavaScript disabled](#javascript-disabled)
- [Application levels](#application-levels)

## Devices registry

`devices` ships pre-configured `userAgent`, `viewport`, `deviceScaleFactor`, `isMobile`, `hasTouch` bundles. Spread into a project's `use`:

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'Mobile Safari', use: { ...devices['iPhone 13'] } },
  ],
});
```

Library form, plus unsetting a baked-in option (e.g. platform-agnostic UA):

```javascript
const { chromium, devices } = require('playwright');
const browser = await chromium.launch();
const context = await browser.newContext({
  ...devices['iPhone 13'],
});
// override a single device field
const context2 = await browser.newContext({
  ...devices['Desktop Chrome'],
  userAgent: undefined,
});
```

## Viewport

```typescript
// per-project: device + custom viewport
export default defineConfig({
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], viewport: { width: 1280, height: 720 } },
    },
  ],
});
```

```typescript
// per-test / per-block
test.use({ viewport: { width: 1600, height: 1200 } });

test.describe('specific viewport block', () => {
  test.use({ viewport: { width: 1600, height: 1200 } });
  test('my test', async ({ page }) => { /* ... */ });
});
```

Runtime resize (changes only this page, not the context default):

```javascript
await page.setViewportSize({ width: 1600, height: 1200 });
```

Set `viewport: null` to disable the fixed viewport and use the actual OS window size (headed Chromium
only — pair with `launchOptions` window sizing):

```typescript
test.use({ viewport: null });
```

## isMobile / hasTouch / deviceScaleFactor

- `isMobile` — consider meta viewport tag and enable touch events.
- `hasTouch` — enable touch input.
- `deviceScaleFactor` — DPR; `2` for retina/high-DPI.

```typescript
export default defineConfig({
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'], isMobile: false } },
  ],
});
```

```javascript
// high-DPI screenshots
const context = await browser.newContext({
  viewport: { width: 2560, height: 1440 },
  deviceScaleFactor: 2,
});
```

## Locale & timezone

Affects browser `navigator.language`, number/date formatting, `Accept-Language`, and `Date`/`Intl` timezone. Does **not** change the test runner's clock — use the `TZ` env var for that.

```typescript
// global
export default defineConfig({
  use: { locale: 'en-GB', timezoneId: 'Europe/Paris' },
});
```

```typescript
// per-test
test.use({ locale: 'de-DE', timezoneId: 'Europe/Berlin' });

test('my test for de lang in Berlin timezone', async ({ page }) => {
  await page.goto('https://www.bing.com');
});
```

```javascript
const context = await browser.newContext({ locale: 'de-DE', timezoneId: 'Europe/Berlin' });
```

## Permissions

Grant ahead of time via `permissions` in `use`, or at runtime (optionally origin-scoped).

```typescript
// global
export default defineConfig({ use: { permissions: ['notifications'] } });
```

```typescript
// origin-scoped grant
test.beforeEach(async ({ context }) => {
  await context.grantPermissions(['notifications'], { origin: 'https://skype.com' });
});

test('first', async ({ page }) => {
  // page has notifications permission for https://skype.com
});
```

```javascript
await context.clearPermissions();
```

## Geolocation

Requires the `geolocation` permission. Spoofs `navigator.geolocation`.

```typescript
// global
export default defineConfig({
  use: {
    geolocation: { longitude: 12.492507, latitude: 41.889938 },
    permissions: ['geolocation'],
  },
});
```

```typescript
// per-test + change mid-test (applies to all pages in the context)
test.use({
  geolocation: { longitude: 41.890221, latitude: 12.492348 },
  permissions: ['geolocation'],
});

test('my test with geolocation', async ({ page, context }) => {
  await context.setGeolocation({ longitude: 48.858455, latitude: 2.294474 });
});
```

```javascript
const context = await browser.newContext({
  geolocation: { longitude: 41.890221, latitude: 12.492348 },
  permissions: ['geolocation'],
});
```

## Color scheme & media

`colorScheme` drives `prefers-color-scheme`. `page.emulateMedia` also covers `media` (`screen`/`print`), `reducedMotion`, `forcedColors`, and `contrast`.

```typescript
// global
export default defineConfig({ use: { colorScheme: 'dark' } });
```

```typescript
// per-test
test.use({ colorScheme: 'dark' }); // or 'light'

test('my test with dark mode', async ({ page }) => { /* ... */ });
```

```javascript
const page = await browser.newPage({ colorScheme: 'dark' }); // or 'light'

// runtime changes
await page.emulateMedia({ colorScheme: 'dark' });
await page.emulateMedia({ media: 'print' });
await page.emulateMedia({ reducedMotion: 'reduce' });   // 'reduce' | 'no-preference'
await page.emulateMedia({ forcedColors: 'active' });     // 'active' | 'none'
await page.emulateMedia({ contrast: 'more' });           // 'more' | 'no-preference'
```

## User agent

```typescript
test.use({ userAgent: 'My user agent' });

test('my user agent test', async ({ page }) => { /* ... */ });
```

```javascript
const context = await browser.newContext({ userAgent: 'My user agent' });
```

## Offline mode

Emulate network loss at config level, or toggle at runtime on the context.

```typescript
export default defineConfig({ use: { offline: true } });
```

```javascript
await context.setOffline(true);
await context.setOffline(false);
```

## JavaScript disabled

```typescript
test.use({ javaScriptEnabled: false });

test('test with no JavaScript', async ({ page }) => { /* ... */ });
```

```javascript
const context = await browser.newContext({ javaScriptEnabled: false });
```

## Application levels

1. **Global** — `defineConfig({ use: { ... } })` applies to every project/test.
2. **Per-project** — `projects[].use` overrides global for that project (where `...devices[...]` usually lives).
3. **Per-test / per-block** — `test.use({ ... })` (or inside `test.describe`) overrides both; `test.beforeEach` + context methods (`grantPermissions`, `setGeolocation`, `setOffline`, `setViewportSize`, `emulateMedia`) for runtime changes.

See also: [test-config.md](./test-config.md), [test-organization.md](./test-organization.md), [fixtures.md](./fixtures.md), [network.md](./network.md), [visual-comparisons.md](./visual-comparisons.md).
