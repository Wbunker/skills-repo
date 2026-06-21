# Assertions

Playwright assertions via `expect` from `@playwright/test`. Web-first matchers auto-retry until they pass or the `expect` timeout (default 5s) elapses — never wrap them in manual waits or `waitFor`. For interacting with elements first, see [actions.md](actions.md) and [locators.md](locators.md). Pixel/visual matchers live in [visual-comparisons.md](visual-comparisons.md).

## Contents

- [Web-first matchers (auto-retrying)](#web-first-matchers-auto-retrying)
- [Negation with .not](#negation-with-not)
- [Soft assertions](#soft-assertions)
- [Custom expect messages](#custom-expect-messages)
- [Per-assertion & global timeout](#per-assertion--global-timeout)
- [expect.configure](#expectconfigure)
- [expect.poll](#expectpoll)
- [expect.toPass](#expecttopass)
- [Non-retrying generic matchers](#non-retrying-generic-matchers)
- [Asymmetric matchers](#asymmetric-matchers)
- [Custom matchers (expect.extend)](#custom-matchers-expectextend)
- [ARIA snapshot assertions](#aria-snapshot-assertions)

## Web-first matchers (auto-retrying)

These poll the page until the condition holds or the timeout is reached. Apply to `Locator`, `Page`, or `APIResponse` as noted. All accept a final `{ timeout }` option.

| Matcher | Target | Asserts |
|---|---|---|
| `toBeAttached()` | Locator | Element is attached to the DOM |
| `toBeVisible()` | Locator | Element is visible |
| `toBeHidden()` | Locator | Element is not visible |
| `toBeEnabled()` | Locator | Element is enabled |
| `toBeDisabled()` | Locator | Element is disabled |
| `toBeChecked()` | Locator | Checkbox/radio is checked (option `{ checked: boolean }`, `{ indeterminate: true }`) |
| `toBeEditable()` | Locator | Element is editable |
| `toBeEmpty()` | Locator | Container has no text/children |
| `toBeFocused()` | Locator | Element is focused |
| `toBeInViewport()` | Locator | Element intersects viewport (option `{ ratio }`, min intersection ratio, default `0`) |
| `toContainText()` | Locator | Element contains the substring/regex (substring match) |
| `toHaveText()` | Locator | Element text matches exactly (string/regex/array) |
| `toHaveValue()` | Locator | Input has value (string/regex) |
| `toHaveValues()` | Locator | Multi-select has options selected |
| `toHaveAttribute()` | Locator | Element has DOM attribute (with optional value) |
| `toHaveClass()` | Locator | Element `class` matches exactly (string/regex/array) |
| `toContainClass()` | Locator | Element's class list contains the given classes (v1.52+) |
| `toHaveCSS()` | Locator | Element has computed CSS property value |
| `toHaveId()` | Locator | Element has `id` |
| `toHaveCount()` | Locator | Locator resolves to exact N elements |
| `toHaveJSProperty()` | Locator | Element has a JS property with value |
| `toHaveRole()` | Locator | Element has the given ARIA role |
| `toHaveAccessibleName()` | Locator | Element has matching accessible name |
| `toHaveAccessibleDescription()` | Locator | Element has matching accessible description |
| `toMatchAriaSnapshot()` | Locator/Page | Subtree matches an ARIA snapshot ([below](#aria-snapshot-assertions)) |
| `toHaveScreenshot()` | Locator/Page | Matches a stored screenshot — see [visual-comparisons.md](visual-comparisons.md) |
| `toHaveTitle()` | Page | Page has title (string/regex) |
| `toHaveURL()` | Page | Page has URL (string/regex/predicate) |
| `toBeOK()` | APIResponse | Response status is 2xx ([network.md](network.md)) |

```typescript
await expect(page.getByText('welcome')).toBeVisible();
await expect(page.getByRole('button')).toHaveCount(3);
await expect(page).toHaveURL(/.*checkout/);
await expect(page.getByTestId('amount')).toHaveText('£100');
```

## Negation with .not

Insert `.not` before any matcher; it inverts and still auto-retries (waits for the condition to become false).

```typescript
expect(value).not.toEqual(0);
await expect(locator).not.toContainText('some text');
```

## Soft assertions

Failed soft assertions record an error but do NOT halt the test, so multiple checks run in one pass. The test still fails at the end.

```typescript
await expect.soft(page.getByTestId('status')).toHaveText('Success');
await expect.soft(page.getByTestId('eta')).toHaveText('1 day');

await page.getByRole('link', { name: 'next page' }).click();
await expect.soft(page.getByRole('heading', { name: 'Make another order' })).toBeVisible();
```

Bail out mid-test if any soft assertion already failed:

```typescript
expect(test.info().errors).toHaveLength(0);
```

`expect.soft.poll(...)` (v1.61+) is the soft variant of [`expect.poll`](#expectpoll):

```typescript
await expect.soft.poll(async () => {
  const response = await page.request.get('https://api.example.com');
  return response.status();
}).toBe(200);
```

## Custom expect messages

Pass a description as the second argument to `expect` / `expect.soft` — surfaces in the report and error output.

```typescript
await expect(page.getByText('Name'), 'should be logged in').toBeVisible();
expect.soft(value, 'my soft assertion').toBe(56);
```

## Per-assertion & global timeout

Per-assertion via the matcher's `{ timeout }` option (ms):

```typescript
await expect(locator).toHaveText('Submit', { timeout: 10_000 });
```

Globally, set `expect.timeout` in [test-config.md](test-config.md):

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  expect: {
    timeout: 10_000,
  },
});
```

## expect.configure

Create a reusable `expect` instance with preset defaults (timeout, soft, message-augmentation).

```typescript
const slowExpect = expect.configure({ timeout: 10000 });
await slowExpect(locator).toHaveText('Submit');

const softExpect = expect.configure({ soft: true });
await softExpect(locator).toHaveText('Submit');
```

## expect.poll

Wrap an arbitrary async function in auto-retrying assertion logic; the returned value is matched with any non-retrying generic matcher.

```typescript
await expect.poll(async () => {
  const response = await page.request.get('https://api.example.com');
  return response.status();
}, {
  message: 'make sure API eventually succeeds',
  timeout: 10000,
}).toBe(200);
```

Custom retry intervals (ms) instead of fixed polling:

```typescript
await expect.poll(async () => {
  const response = await page.request.get('https://api.example.com');
  return response.status();
}, {
  intervals: [1_000, 2_000, 10_000],
  timeout: 60_000,
}).toBe(200);
```

## expect.toPass

Retry an entire block — including nested `expect` calls — until it stops throwing.

```typescript
await expect(async () => {
  const response = await page.request.get('https://api.example.com');
  expect(response.status()).toBe(200);
}).toPass();
```

With custom intervals/timeout:

```typescript
await expect(async () => {
  const response = await page.request.get('https://api.example.com');
  expect(response.status()).toBe(200);
}).toPass({
  intervals: [1_000, 2_000, 10_000],
  timeout: 60_000,
});
```

## Non-retrying generic matchers

For non-web values (numbers, strings, objects). These run once — never use them on a value that needs the page to settle; use a web-first matcher or `expect.poll`/`expect.toPass` instead.

`toBe()`, `toBeCloseTo()`, `toBeDefined()`, `toBeFalsy()`, `toBeGreaterThan()`, `toBeGreaterThanOrEqual()`, `toBeInstanceOf()`, `toBeLessThan()`, `toBeLessThanOrEqual()`, `toBeNaN()`, `toBeNull()`, `toBeTruthy()`, `toBeUndefined()`, `toContain()`, `toContainEqual()`, `toEqual()`, `toHaveLength()`, `toHaveProperty()`, `toMatch()`, `toMatchObject()`, `toStrictEqual()`, `toThrow()`

## Asymmetric matchers

Relaxed nested matching inside generic matchers: `expect.any()`, `expect.anything()`, `expect.arrayContaining()`, `expect.arrayOf()`, `expect.closeTo()`, `expect.objectContaining()`, `expect.stringContaining()`, `expect.stringMatching()`.

```typescript
expect(user).toEqual({
  id: expect.any(Number),
  name: expect.stringContaining('Ada'),
});
```

## Custom matchers (expect.extend)

Extend `expect` with reusable, retry-aware matchers. Respect `this.isNot` for `.not` support.

```typescript
import { expect as baseExpect } from '@playwright/test';
import type { Locator } from '@playwright/test';

export const expect = baseExpect.extend({
  async toHaveAmount(locator: Locator, expected: number, options?: { timeout?: number }) {
    const assertionName = 'toHaveAmount';
    let pass: boolean;
    let matcherResult: any;

    try {
      const expectation = this.isNot ? baseExpect(locator).not : baseExpect(locator);
      await expectation.toHaveAttribute('data-amount', String(expected), options);
      pass = true;
    } catch (e: any) {
      matcherResult = e.matcherResult;
      pass = false;
    }

    if (this.isNot) {
      pass = !pass;
    }

    const message = pass
      ? () => this.utils.matcherHint(assertionName, undefined, undefined, { isNot: this.isNot }) +
          '\n\n' +
          `Locator: ${locator}\n` +
          `Expected: not ${this.utils.printExpected(expected)}\n` +
          (matcherResult ? `Received: ${this.utils.printReceived(matcherResult.actual)}` : '')
      : () => this.utils.matcherHint(assertionName, undefined, undefined, { isNot: this.isNot }) +
          '\n\n' +
          `Locator: ${locator}\n` +
          `Expected: ${this.utils.printExpected(expected)}\n` +
          (matcherResult ? `Received: ${this.utils.printReceived(matcherResult.actual)}` : '');

    return {
      message,
      pass,
      name: assertionName,
      expected,
      actual: matcherResult?.actual,
    };
  },
});
```

Use the exported `expect` (re-export from your fixtures), then:

```typescript
import { test, expect } from './fixtures';

test('amount', async () => {
  await expect(page.locator('.cart')).toHaveAmount(4);
});
```

Merge matchers (and tests) from multiple modules:

```typescript
import { mergeTests, mergeExpects } from '@playwright/test';
import { test as dbTest, expect as dbExpect } from 'database-test-utils';
import { test as a11yTest, expect as a11yExpect } from 'a11y-test-utils';

export const expect = mergeExpects(dbExpect, a11yExpect);
export const test = mergeTests(dbTest, a11yTest);
```

## ARIA snapshot assertions

`toMatchAriaSnapshot` compares an element/page's accessibility tree against a YAML template — resilient to styling/DOM churn, ideal for structural assertions and AI consumption. (To *scan* for WCAG violations rather than pin the tree, use `@axe-core/playwright` — see [accessibility.md](accessibility.md).)

```typescript
toMatchAriaSnapshot(expected: string, options?: { timeout?: number }): Promise<void>
toMatchAriaSnapshot(options?: { name?: string, timeout?: number }): Promise<void>
```

Page-level usage:

```typescript
await expect(page).toMatchAriaSnapshot(`
  - heading "Issues"
  - list:
    - listitem: "Bug report"
    - listitem: "Feature request"
`);
```

Or scope to a locator: `await expect(locator).toMatchAriaSnapshot(\`...\`)`.

YAML node format — `role "name" [attribute=value]`. `role` is the ARIA/HTML role; `"name"` is the accessible name (exact in quotes, or `/regex/`); brackets carry ARIA state (`checked`, `disabled`, `expanded`, `invalid`, `level`, `pressed`, `selected`).

**Partial matching** — omit names/attributes to match loosely:

```typescript
await expect(page).toMatchAriaSnapshot(`
  - checkbox   # matches regardless of checked state
  - button     # matches regardless of label
`);
```

**Regex names** for dynamic text:

```typescript
await expect(page).toMatchAriaSnapshot(`
  - heading /Issues \\d+/
`);
```

**Child-matching mode** — by default a parent matches if it *contains* the listed children in order
(extra children allowed). Tighten with a `/children` directive (`contain` default / `equal` = exact
set & order / `deep-equal` = exact incl. nested):

```typescript
await expect(page.getByRole('list')).toMatchAriaSnapshot(`
  - list:
    - /children: equal
    - listitem: Feature A
    - listitem: Feature B
`);
```

Set it globally via `expect: { toMatchAriaSnapshot: { children: 'equal' } }` in the config. Other YAML
properties: `/url` for links (`- /url: "#more-info"`, regex allowed).

Use the `name` option to store the expected snapshot in an external `.aria.yml` file instead of inline
(`toMatchAriaSnapshot({ name: 'main.aria.yml' })`; path configurable via
`toMatchAriaSnapshot: { pathTemplate }`). Generate/update with `--update-snapshots` (`-u`); pick how
the source is rewritten with `--update-source-method=patch|3way|overwrite` (default `patch` → a
`git apply`-able diff). The codegen "Assert snapshot" button / "Aria snapshot" tab also emits these.

**`boxes` option (v1.60+)** — note this is on the *generator* methods `locator.ariaSnapshot({ boxes: true })` / `page.ariaSnapshot({ boxes: true })`, NOT the assertion. It appends each element's bounding box as `[box=x,y,width,height]`, useful for AI consumption:

```typescript
const snapshot = await page.locator('body').ariaSnapshot({ boxes: true });
// - heading "Issues" [box=12,34,120,28]
```
