# Test Organization

Structuring suites with `test.describe`, hooks, steps, annotations, tags, parameterization, and retry/parallel modes. All examples use `@playwright/test` (TypeScript).

## Contents

- [Grouping with test.describe](#grouping-with-testdescribe)
- [Hooks vs fixtures](#hooks-vs-fixtures)
- [test.step](#teststep)
- [Annotations (skip / fixme / fail / slow / only)](#annotations-skip--fixme--fail--slow--only)
- [Custom annotations](#custom-annotations)
- [Tags and filtering](#tags-and-filtering)
- [Parameterized tests](#parameterized-tests)
- [test.use for scoped options](#testuse-for-scoped-options)
- [test.abort](#testabort)
- [TestInfo (the second test argument)](#testinfo-the-second-test-argument)
- [Retries and flaky detection](#retries-and-flaky-detection)
- [test.describe.configure (mode / retries / timeout)](#testdescribeconfigure-mode--retries--timeout)

## Grouping with test.describe

```typescript
import { test, expect } from '@playwright/test';

test.describe('two tests', () => {
  test('one', async ({ page }) => { /* ... */ });
  test('two', async ({ page }) => { /* ... */ });
});
```

Nesting and anonymous groups are allowed (callback-only, no title) — useful to scope hooks/options to a subset. Add `{ tag }` / `{ annotation }` as the optional second arg (see [Tags](#tags-and-filtering)).

## Hooks vs fixtures

```typescript
test.beforeEach(async ({ page }) => {
  console.log(`Running ${test.info().title}`);
  await page.goto('https://my.start.url/');
});

test.afterEach(async ({ page }) => {
  console.log(`Finished ${test.info().title} with status ${test.info().status}`);
});

test.beforeAll(async () => { console.log('Before tests'); });
test.afterAll(async () => { console.log('Done with tests'); });
```

- `beforeEach`/`afterEach` run per test; `beforeAll`/`afterAll` run **once per worker** (re-run when a worker restarts after failure).
- Hooks receive the same fixtures and `TestInfo` as tests. `afterEach`/`afterAll` keep running all hooks even if one fails.
- Scope: a hook applies to its enclosing file or `describe` group.

**Prefer fixtures over hooks** for setup/teardown that produces a value or needs automatic cleanup — fixtures compose, run on-demand, and tear down in reverse order. Use hooks for side-effecting steps shared by every test (navigation, logging). See [fixtures.md](fixtures.md).

## test.step

```typescript
const user = await test.step('Log in', async () => {
  // ...
  return 'john';        // step returns its callback's value
});
```

Boxed step — failures point to the `test.step` call site, not the internal line (good for reusable helpers):

```typescript
await test.step('login', async () => { /* ... */ }, { box: true });
```

The callback receives a `TestStepInfo` — `step.skip(condition?, description?)` to skip a step at
runtime (v1.51+), and `step.attach(name, options)` to attach data from within the step:

```typescript
await test.step('check behavior', async step => {
  step.skip(browserName === 'webkit', 'Unavailable in WebKit');
  // ...
});
```

## Annotations (skip / fixme / fail / slow / only)

```typescript
test.skip('skip this test', async ({ page }) => { /* not run */ });
test.fixme('to be fixed', async ({ page }) => { /* not run, marked broken */ });
test.fail('not yet ready', async ({ page }) => { /* run, must fail */ });
test.only('focus this test', async ({ page }) => { /* only focused tests run */ });
```

| Form | Behavior |
|------|----------|
| `test.skip` | Not run (irrelevant). |
| `test.fixme` | Not run (known broken). |
| `test.fail` | Run; **expected to fail** — errors if it passes. |
| `test.slow` | Runs with **triple** the timeout. |
| `test.only` | Run only focused tests/suites. |

Conditional forms — `test.X(condition, reason)` inside the body or a hook:

```typescript
test('skip this test', async ({ page, browserName }) => {
  test.skip(browserName === 'firefox', 'Still working on it');
});

test.beforeEach(async ({ page, isMobile }) => {
  test.fixme(isMobile, 'Settings page does not work in mobile yet');
  await page.goto('http://localhost:3000/settings');
});

test('slow test', async ({ page }) => {
  test.slow();   // triples timeout for this test
});
```

`test.slow()` cannot be used in `beforeAll`/`afterAll`. `skip`/`fixme`/`fail` abort execution at the call site once the condition is true.

Less-common variants: `test.fail.only` (v1.49+, focus a single should-fail test), `test.step.skip` (v1.50+, skip a step), and `test.describe.fixme` (mark a whole group as broken/not-run).

Group-level conditional skip (callback form receives fixtures):

```typescript
test.describe('chromium only', () => {
  test.skip(({ browserName }) => browserName !== 'chromium', 'Chromium only!');
  test('test 1', async ({ page }) => { /* ... */ });
});
```

## Custom annotations

Attach metadata via the test details object (second arg):

```typescript
test('test login page', {
  annotation: {
    type: 'issue',
    description: 'https://github.com/microsoft/playwright/issues/23180',
  },
}, async ({ page }) => { /* ... */ });

test('test full report', {
  annotation: [
    { type: 'issue', description: 'https://github.com/microsoft/playwright/issues/23180' },
    { type: 'performance', description: 'very slow test!' },
  ],
}, async ({ page }) => { /* ... */ });
```

Push annotations at runtime via `test.info()`:

```typescript
test('example test', async ({ page, browser }) => {
  test.info().annotations.push({
    type: 'browser version',
    description: browser.version(),
  });
});
```

Annotations appear in reports (HTML reporter renders type/description).

## Tags and filtering

> Run-wide tagging: `testConfig.tag` (v1.57+) in `playwright.config.ts` adds tags to **every** test in
> the run — useful for labeling merged reports. See [test-config.md](test-config.md).

Tag via the details object (`@`-prefixed by convention) or inline in the title:

```typescript
test('test login page', { tag: '@fast' }, async ({ page }) => { /* ... */ });

test('test full report @slow', async ({ page }) => { /* ... */ });   // inline @-token

test('test full report', { tag: ['@slow', '@vrt'] }, async ({ page }) => { /* ... */ });
```

Tag a whole group:

```typescript
test.describe('group', { tag: '@report' }, () => {
  test('test report header', async ({ page }) => { /* ... */ });
});
```

Filter from the CLI:

```bash
npx playwright test --grep @fast                       # -g shorthand
npx playwright test --grep-invert @fast                # -G shorthand (v1.61+)
npx playwright test --grep "@fast|@slow"               # OR
npx playwright test --grep "(?=.*@fast)(?=.*@slow)"    # AND (lookaheads)
```

`--grep`/`-g` and `--grep-invert`/`-G` match against the test title **including** tags.

## Parameterized tests

Generate tests in a loop (use `forEach`/`for`, not async iteration):

```typescript
[
  { name: 'Alice', expected: 'Hello, Alice!' },
  { name: 'Bob', expected: 'Hello, Bob!' },
  { name: 'Charlie', expected: 'Hello, Charlie!' },
].forEach(({ name, expected }) => {
  test(`testing with ${name}`, async ({ page }) => {
    await page.goto(`https://example.com/greet?name=${name}`);
    await expect(page.getByRole('heading')).toHaveText(expected);
  });
});
```

To run hooks per-iteration with the loop variable, wrap each iteration in `test.describe`:

```typescript
[
  { name: 'Alice', expected: 'Hello, Alice!' },
  { name: 'Bob', expected: 'Hello, Bob!' },
].forEach(({ name, expected }) => {
  test.describe(() => {
    test.beforeEach(async ({ page }) => {
      await page.goto(`https://example.com/greet?name=${name}`);
    });
    test(`testing with ${expected}`, async ({ page }) => {
      await expect(page.getByRole('heading')).toHaveText(expected);
    });
  });
});
```

Generate from CSV (or any data source) at collection time:

```typescript
import fs from 'fs';
import path from 'path';
import { test } from '@playwright/test';
import { parse } from 'csv-parse/sync';

const records = parse(fs.readFileSync(path.join(__dirname, 'input.csv')), {
  columns: true,
  skip_empty_lines: true,
});

for (const record of records) {
  test(`foo: ${record.test_case}`, async ({ page }) => {
    console.log(record.test_case, record.some_value, record.some_other_value);
  });
}
```

**Parameterized projects** — declare a custom option, then vary it per project so the *same* tests run under each parameter. See [test-config.md](test-config.md) for project config.

```typescript
// my-test.ts
import { test as base } from '@playwright/test';

export type TestOptions = { person: string };

export const test = base.extend<TestOptions>({
  person: ['John', { option: true }],   // default value, marked as an option
});
```

```typescript
// example.spec.ts
import { test } from './my-test';

test('test 1', async ({ page, person }) => {
  await page.goto(`/index.html`);
  await expect(page.locator('#node')).toContainText(person);
});
```

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';
import type { TestOptions } from './my-test';

export default defineConfig<TestOptions>({
  projects: [
    { name: 'alice', use: { person: 'Alice' } },
    { name: 'bob', use: { person: 'Bob' } },
  ],
});
```

An option can also feed a fixture (e.g. log in as `person` before each test):

```typescript
export const test = base.extend<TestOptions>({
  person: ['John', { option: true }],
  page: async ({ page, person }, use) => {
    await page.goto('/chat');
    await page.getByLabel('User Name').fill(person);
    await page.getByText('Enter chat room').click();
    await use(page);
  },
});
```

See [fixtures.md](fixtures.md) for the fixture mechanics.

**Environment variables** are the simplest parameter source — pass secrets or an environment at the
command line (`USER_NAME=me PASSWORD=secret npx playwright test`) and read `process.env.*` in tests,
or load a `.env` file via `dotenv` in the config. See
[test-config.md](test-config.md#env-driven-config).

## test.use for scoped options

Override fixtures/options for an entire file or `describe` group:

```typescript
test.use({ locale: 'en-US' });

test('test with locale', async ({ page }) => {
  // Browser context is created with the specified locale
});
```

Place it at file top-level (whole file) or inside a `describe` (that group only). See [emulation.md](emulation.md) for context options.

## test.abort

`(v1.60+)` Abort the currently running test from a fixture, hook, or route handler by throwing — the test is marked failed immediately:

```typescript
test('does not publish', async ({ page }) => {
  await page.route('**/publish', route => {
    test.abort('Tests must not publish to shared page');
    return route.abort();
  });
});
```

## TestInfo (the second test argument)

Every test/hook/fixture can take a second `testInfo` arg exposing run metadata and utilities:

```typescript
test('example', async ({ page }, testInfo) => {
  testInfo.retry;            // current retry attempt (0 = first run)
  testInfo.project.name;     // active project; testInfo.config for the full config
  testInfo.status;           // outcome (in afterEach); testInfo.expectedStatus
  testInfo.tags;             // tags on this test (v1.43+); testInfo.testId
  testInfo.setTimeout(60_000);
  testInfo.skip(cond, 'why'); testInfo.fail(); testInfo.fixme(); testInfo.slow();

  // attach a file/buffer to the report (shown in HTML report / trace Attachments)
  await testInfo.attach('screenshot', { body: await page.screenshot(), contentType: 'image/png' });
  const tmp = testInfo.outputPath('data.json');   // safe per-test temp path
});
```

`testInfo.attach` is the canonical way to surface artifacts (see [accessibility.md](accessibility.md));
`outputPath`/`outputDir` give scratch space cleaned between runs. Worker-scoped fixtures get the
slimmer `WorkerInfo` (`config`, `project`, `workerIndex`, `parallelIndex`).

## Retries and flaky detection

A **flaky** test is one that fails then passes on retry. Configure retries globally or per run:

```bash
npx playwright test --retries=3
```

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  retries: 3,
});
```

Detect a retry at runtime via `testInfo.retry` (0 on first attempt) to reset state:

```typescript
import { test, expect } from '@playwright/test';

test('my test', async ({ page }, testInfo) => {
  if (testInfo.retry)
    await cleanSomeCachesOnTheServer();
  // ...
});
```

Scope retries to a group with `test.describe.configure`:

```typescript
test.describe(() => {
  test.describe.configure({ retries: 2 });
  test('test 1', async ({ page }) => { /* ... */ });
  test('test 2', async ({ page }) => { /* ... */ });
});
```

## test.describe.configure (mode / retries / timeout)

Configure execution `mode` (`'default' | 'parallel' | 'serial'`), `retries`, and `timeout` for the enclosing scope:

```typescript
test.describe.configure({ mode: 'parallel' });
test('runs in parallel 1', async ({ page }) => {});
test('runs in parallel 2', async ({ page }) => {});
```

**Serial mode** — tests share a worker and run in order; if one fails, the rest are skipped (and on retry the whole group reruns):

```typescript
import { test } from '@playwright/test';

test.describe.configure({ mode: 'serial' });

test.beforeAll(async () => { /* ... */ });
test('first good', async ({ page }) => { /* ... */ });
test('second flaky', async ({ page }) => { /* ... */ });
test('third good', async ({ page }) => { /* ... */ });
```

Share one page across a serial group:

```typescript
import { test, type Page } from '@playwright/test';

test.describe.configure({ mode: 'serial' });
let page: Page;

test.beforeAll(async ({ browser }) => {
  page = await browser.newPage();
});

test.afterAll(async () => {
  await page.close();
});

test('runs first', async () => {
  await page.goto('https://playwright.dev/');
});

test('runs second', async () => {
  await page.getByText('Get Started').click();
});
```

`test.describe.serial(...)` / `test.describe.parallel(...)` exist but are **deprecated** — prefer `test.describe.configure({ mode })`.
