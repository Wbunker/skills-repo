# Writing Tests

Orientation for authoring tests with `@playwright/test`: structure, isolation, and the Page Object
Model. The deep references for the three pillars live in their own files — this page links to them.

## Contents
- [Test structure & hooks](#test-structure--hooks)
- [The three pillars (locators, actions, assertions)](#the-three-pillars-locators-actions-assertions)
- [Test isolation](#test-isolation)
- [Page Object Model](#page-object-model)

## Test structure & hooks

```typescript
import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
  await page.goto('https://playwright.dev/');
  await expect(page).toHaveTitle(/Playwright/);
});
```

Group with `test.describe()` and use lifecycle hooks (`beforeEach`, `afterEach`, `beforeAll`,
`afterAll`):

```typescript
test.describe('navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://playwright.dev/');
  });

  test('main navigation', async ({ page }) => {
    await expect(page).toHaveURL('https://playwright.dev/');
  });
});
```

> Prefer **fixtures** over `beforeEach` for anything reusable or conditional — they are lazy and
> dependency-injected. See [fixtures.md](fixtures.md). For describe/step/tags/annotations/parameter-
> ization and retries, see [test-organization.md](test-organization.md).

## The three pillars (locators, actions, assertions)

A test almost always: **locate** an element → **act** on it → **assert** the result.

```typescript
const getStarted = page.getByRole('link', { name: 'Get started' }); // 1. locate
await getStarted.click();                                            // 2. act
await expect(page.getByRole('heading', { name: 'Installation' }))    // 3. assert
  .toBeVisible();
```

- **Locate** — prefer user-facing locators: `getByRole` → `getByText`/`getByLabel`/`getByPlaceholder`
  → `getByTestId` → CSS/XPath (last resort). Locators are lazy, strict, and auto-retrying. Full
  reference incl. filtering, chaining, `.and`/`.or`, lists, and other engines:
  [locators.md](locators.md).
- **Act** — `click`, `fill`, `check`, `selectOption`, `hover`, `press`, `setInputFiles`, drag/drop,
  dialogs, downloads, frames, clock. Playwright runs **actionability checks** and auto-waits, so
  explicit sleeps are an anti-pattern. Full reference: [actions.md](actions.md).
- **Assert** — use **web-first** matchers (`toBeVisible`, `toHaveText`, `toHaveURL`, …) which
  **auto-retry** until the condition holds; always `await` them. Never `await locator.isVisible()`
  then assert the boolean (no retry → flaky). Reserve sync matchers (`toEqual`, `toContain`) for
  plain values. Full reference incl. soft/poll/custom/aria: [assertions.md](assertions.md).

## Test isolation

Every test gets a fresh `page` inside an isolated `BrowserContext` — "equivalent to a brand new
browser profile." No state carries between tests, so they run in any order and in parallel. Share
expensive setup safely via worker-scoped [fixtures](fixtures.md); reuse a signed-in session via
[auth.md](auth.md).

## Page Object Model

A page object encapsulates selectors + interactions for part of the app, giving a higher-level API
and a single place to update selectors.

```typescript
// playwright-dev-page.ts
import { expect, type Locator, type Page } from '@playwright/test';

export class PlaywrightDevPage {
  readonly page: Page;
  readonly getStartedLink: Locator;
  readonly gettingStartedHeader: Locator;
  readonly tocList: Locator;

  constructor(page: Page) {
    this.page = page;
    this.getStartedLink = page.locator('a', { hasText: 'Get started' });
    this.gettingStartedHeader = page.locator('h1', { hasText: 'Installation' });
    this.tocList = page.locator('article div.markdown ul > li > a');
  }

  async goto() {
    await this.page.goto('https://playwright.dev');
  }

  async getStarted() {
    await this.getStartedLink.first().click();
    await expect(this.gettingStartedHeader).toBeVisible();
  }
}
```

```typescript
// in a test
import { test, expect } from '@playwright/test';
import { PlaywrightDevPage } from './playwright-dev-page';

test('table of contents', async ({ page }) => {
  const playwrightDev = new PlaywrightDevPage(page);
  await playwrightDev.goto();
  await playwrightDev.getStarted();
  await expect(playwrightDev.tocList).toHaveText([
    'How to install Playwright',
    "What's installed",
    'How to run the example test',
    'How to open the HTML test report',
  ]);
});
```

For maximum DRYness, expose the page object as a **fixture** so tests get a ready-to-use instance by
name — see [fixtures.md](fixtures.md#page-objects-as-fixtures).
