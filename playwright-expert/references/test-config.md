# Playwright Test Configuration

Full reference for `playwright.config.ts` — top-level options, the `use` block, projects, parallelism, sharding, timeouts, global setup/teardown, web servers, and reporters. All examples use TypeScript with `@playwright/test`.

## Contents

- [Representative config](#representative-config)
- [Top-level options](#top-level-options)
- [The `use` block](#the-use-block)
- [Projects](#projects)
- [Parallelism](#parallelism)
- [Sharding](#sharding)
- [Timeouts](#timeouts)
- [Global setup & teardown](#global-setup--teardown)
- [Web server](#web-server)
- [Reporters](#reporters)
- [Env-driven config](#env-driven-config)
- [Config validation (v1.60+)](#config-validation-v160)

## Representative config

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  timeout: 30_000,
  expect: { timeout: 5_000 },
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

`defineConfig` is the typed wrapper — always prefer it over a bare object for autocompletion and validation.

## Top-level options

| Option | Notes |
|---|---|
| `testDir` | Directory containing test files. |
| `testMatch` | Glob/regex of test files. Default `**/*.@(spec|test).?(c|m)[jt]s?(x)`. |
| `testIgnore` | Patterns excluded from discovery. |
| `fullyParallel` | Run all tests in all files in parallel. Default `false`. Settable per-project. |
| `forbidOnly` | Fail the run if any `test.only` is present. Use `!!process.env.CI`. |
| `retries` | Max retries per test. |
| `workers` | Concurrent worker processes. Accepts a number or percentage string (e.g. `'50%'`). |
| `maxFailures` | Stop after N failures. |
| `grep` / `grepInvert` | Run / skip tests whose title matches a regex (config-level `-g`/`-G`). |
| `repeatEach` | Run each test N times (flake hunting). |
| `reportSlowTests` | `{ max, threshold }` — flag slow test files. |
| `preserveOutput` | `'always'` \| `'never'` \| `'failures-only'` — keep `outputDir` artifacts. |
| `updateSnapshots` | `'all'` \| `'changed'` \| `'missing'` \| `'none'` — snapshot update policy. |
| `name` | Run label, surfaced in reports/merged reports. |
| `quiet` | Suppress stdout/stderr from tests. |
| `snapshotDir` | Base dir for snapshots (with `snapshotPathTemplate`). |
| `tsconfig` | Path to a single `tsconfig` applied to all imported test files. |
| `captureGitInfo` | `{ commit, diff }` — embed git commit/diff metadata into the report. |
| `reporter` | See [Reporters](#reporters). |
| `timeout` | Per-test timeout, ms. Default `30_000`. |
| `globalTimeout` | Whole-run timeout, ms. Default none. |
| `expect` | Assertion config (`timeout`, `toHaveScreenshot`, `toMatchSnapshot`). |
| `outputDir` | Folder for artifacts (screenshots, videos, traces). Default `test-results`. |
| `snapshotPathTemplate` | Template for snapshot file paths (see below). |
| `metadata` | Arbitrary key/values surfaced in reports. |
| `globalSetup` / `globalTeardown` | Path to function module — see [Global setup & teardown](#global-setup--teardown). |
| `projects` | See [Projects](#projects). |
| `webServer` | See [Web server](#web-server). |

```typescript
expect: {
  timeout: 5000,
  toHaveScreenshot: { maxDiffPixels: 10 },
  toMatchSnapshot: { maxDiffPixelRatio: 0.1 },
}
```

`snapshotPathTemplate` tokens include `{testDir}`, `{testFileDir}`, `{testFileName}`, `{testFileBaseName}` (filename without extension, v1.60+), `{arg}` (snapshot name without extension), `{ext}`, `{projectName}`, `{platform}`:

```typescript
export default defineConfig({
  snapshotPathTemplate: '{testDir}/__screenshots__/{testFileBaseName}/{arg}{ext}',
});
```

## The `use` block

`use` sets browser/context/page options inherited by all tests. Override at three levels (most
specific wins): config `use` → `projects[].use` → `test.use({ ... })` per file/describe. The full
option set, grouped as the docs group them:

**Basic**
| Option | Purpose |
|---|---|
| `baseURL` | Base URL for relative `page.goto('/path')`, `request`, etc. |
| `storageState` | Seed cookies/localStorage/IndexedDB (auth) — see [auth.md](auth.md). |
| `headless` | Run without a visible window. Default `true`. |
| `browserName` | `'chromium'` \| `'firefox'` \| `'webkit'`. |
| `channel` | Branded build: `'chrome'`, `'msedge'`, … — see [library-api.md](library-api.md). |

**Emulation** (deep dive: [emulation.md](emulation.md))
| Option | Purpose |
|---|---|
| `viewport` | `{ width, height }` or `null` to disable. |
| `colorScheme` | `'light'` \| `'dark'` \| `'no-preference'`. |
| `locale`, `timezoneId` | Browser locale / timezone. |
| `geolocation`, `permissions` | Coordinates + granted permissions. |
| `userAgent`, `deviceScaleFactor`, `isMobile`, `hasTouch`, `screen` | Device traits. |
| `forcedColors`, `reducedMotion`, `contrast` | Media-feature emulation (`active`/`reduce`/`more`, …). |
| `javaScriptEnabled` | Disable JS for a test. |

**Network** (deep dive: [network.md](network.md))
| Option | Purpose |
|---|---|
| `acceptDownloads` | Auto-accept downloads. Default `true`. |
| `extraHTTPHeaders` | Headers sent with every request. |
| `httpCredentials` | HTTP basic-auth `{ username, password }`. |
| `ignoreHTTPSErrors` | Ignore TLS errors. |
| `offline` | Emulate offline. |
| `proxy` | `{ server, bypass, username, password }`. |
| `clientCertificates` | Per-origin client certs for mTLS. |

**Recording**
| Option | Purpose |
|---|---|
| `screenshot` | `'off'` \| `'on'` \| `'only-on-failure'` — see [visual-comparisons.md](visual-comparisons.md). |
| `trace` | `off`/`on`/`retain-on-failure`/`on-first-retry`/`on-all-retries`/`retain-on-first-failure`/`retain-on-failure-and-retries` — see [trace-viewer.md](trace-viewer.md). |
| `video` | Same modes as `trace` — see [visual-comparisons.md](visual-comparisons.md). |

**Other**
| Option | Purpose |
|---|---|
| `actionTimeout`, `navigationTimeout` | Per-action / per-navigation timeout (ms). `0` = no limit. |
| `testIdAttribute` | Attribute for `getByTestId`. Default `data-testid`. |
| `bypassCSP` | Bypass Content-Security-Policy. |
| `launchOptions` | Passed to `browserType.launch()` (e.g. `slowMo`, `args`). |
| `contextOptions` | Passed to `browser.newContext()`. |
| `connectOptions` | Passed to `browserType.connect()`. |

```typescript
use: {
  baseURL: 'http://localhost:3000',   // enables relative page.goto('/path')
  trace: 'on-first-retry',
  screenshot: 'only-on-failure',
  locale: 'en-US',
  timezoneId: 'America/Chicago',
  httpCredentials: { username: 'user', password: 'pass' },
  launchOptions: { slowMo: 50 },
}
```

Reset an inherited option to its default in a single test/block with a fixture override:

```typescript
test.use({ baseURL: [async ({}, use) => use(undefined), { scope: 'test' }] });
```

## Projects

A project is a logical group of tests sharing config — used for multiple browsers, environments, or test splits. Each entry takes its own `use`, `testMatch`/`testIgnore`, `retries`, `timeout`, `dependencies`, `teardown`, `fullyParallel`.

Multiple browsers / channels:

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'Mobile Chrome', use: { ...devices['Pixel 5'] } },
    { name: 'Mobile Safari', use: { ...devices['iPhone 12'] } },
    { name: 'Microsoft Edge', use: { ...devices['Desktop Edge'], channel: 'msedge' } },
    { name: 'Google Chrome', use: { ...devices['Desktop Chrome'], channel: 'chrome' } },
  ],
});
```

Environments and test splits:

```typescript
export default defineConfig({
  timeout: 60000,
  projects: [
    { name: 'staging', use: { baseURL: 'staging.example.com' }, retries: 2 },
    { name: 'production', use: { baseURL: 'production.example.com' }, retries: 0 },
    { name: 'Smoke', testMatch: /.*smoke.spec.ts/, retries: 0 },
    { name: 'Default', testIgnore: /.*smoke.spec.ts/, retries: 2 },
  ],
});
```

### Dependencies & teardown

`dependencies` is a list of projects that must finish before this project runs; if a dependency fails, dependents are skipped. A project's `teardown` names another project that runs after all projects depending on it complete.

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  projects: [
    { name: 'setup', testMatch: '**/*.setup.ts' },
    { name: 'chromium', use: { ...devices['Desktop Chrome'] }, dependencies: ['setup'] },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] }, dependencies: ['setup'] },
    { name: 'webkit', use: { ...devices['Desktop Safari'] }, dependencies: ['setup'] },
  ],
});
```

Run only selected projects without their dependencies via `--no-deps`. See [Global setup & teardown](#global-setup--teardown) for the setup/teardown-project pattern.

## Parallelism

Default: test **files** run in parallel; tests **within a file** run in order in the same worker.

```typescript
export default defineConfig({
  workers: process.env.CI ? 2 : undefined,  // number or '50%'
  fullyParallel: true,                       // also parallelize tests within each file
});
```

```bash
npx playwright test --workers 4
npx playwright test --workers=1   # disable parallelism
```

Per-file / per-describe control with `test.describe.configure`:

```typescript
import { test } from '@playwright/test';

test.describe.configure({ mode: 'parallel' });   // file-level

test('runs in parallel 1', async ({ page }) => { /* ... */ });
test('runs in parallel 2', async ({ page }) => { /* ... */ });
```

Opt a describe block back out of fully-parallel:

```typescript
test.describe('runs in parallel with other describes', () => {
  test.describe.configure({ mode: 'default' });
  test('in order 1', async ({ page }) => {});
  test('in order 2', async ({ page }) => {});
});
```

Serial mode — tests share state, and if one fails the rest are skipped:

```typescript
import { test, type Page } from '@playwright/test';

test.describe.configure({ mode: 'serial' });

let page: Page;

test.beforeAll(async ({ browser }) => {
  page = await browser.newPage();
});

test('runs first', async () => {
  await page.goto('https://playwright.dev/');
});

test('runs second', async () => {
  await page.getByText('Get Started').click();
});
```

### Isolating a chunk of data-mutating tests (shared-state contention)

When a group of tests mutates **shared server state** they cannot safely run in
parallel — even with per-test data isolation, some resources are inherently
shared. The classic example: an **ordered list** (sidebar order, ranks, board
columns). Each row owns a `position`, so "move X up" is a read-modify-write
across the *whole sibling list*; two such tests overlapping clobber each other's
positions on the backend (a real race, not a test bug). Symptom: a reorder
assertion passes alone and in isolation but flakes only in the full parallel
suite, and only for the test that asserts global order.

Fixes, in order of preference:
- **Data-partition the chunk** — give the contending tests their own account /
  team / workspace so the "shared" list isn't shared. Scales best; keeps them
  parallel. Key per-slot resources on `parallelIndex` (below).
- **Serialize the chunk** — run just those tests in one worker, in order. Under
  `fullyParallel: true`, both `mode: 'default'` and `mode: 'serial'` on a
  `describe` collapse that block to a single worker. **Prefer `'default'`**: it
  runs in order but keeps tests *independent*, so one failure doesn't skip the
  rest (`'serial'` cascades skips — only for genuinely dependent flows that
  share a page/state). Scope it as tightly as possible — a whole serialized
  feature is the long pole of the suite.

**playwright-bdd** has no sub-feature grouping: the `@mode:default|serial|parallel`
special tag applies at the **Feature** level (or to a single scenario's own
describe, which can't group siblings). So a serial *chunk* = its own `.feature`
file tagged `@mode:default`; keep the parallel-safe scenarios in a separate
feature. Verify it actually serialized by watching wall-clock jump (one worker)
and the emitted `test.describe.configure({mode})` in `.features-gen/`.

Always *prove persistence* for a mutation, not just the optimistic UI: after the
write, **reload** and assert the post-reload DOM — it can only come from the
backend GET, so it confirms the change committed (and incidentally removes
optimistic-state flakiness). Await the mutation's network response before
reloading so the reload reads settled state.

Worker/parallel indices (via `testInfo` or env):

```typescript
process.env.TEST_WORKER_INDEX     // unique per worker
process.env.TEST_PARALLEL_INDEX   // 0 .. workers-1
testInfo.workerIndex
testInfo.parallelIndex
```

When a worker restarts after a failure, `workerIndex` gets a **new** value but `parallelIndex` stays
constant — key it on `parallelIndex` to reuse a per-slot resource (e.g. a database account, see
[auth.md](auth.md#per-worker-authentication)). Workers are isolated OS processes (own browser) and
cannot share memory; pass data via the filesystem or a server.

```typescript
export default defineConfig({
  maxFailures: process.env.CI ? 10 : undefined,
});
```

## Sharding

Split the suite across machines with `--shard=x/y`:

```bash
npx playwright test --shard=1/4
npx playwright test --shard=2/4
npx playwright test --shard=3/4
npx playwright test --shard=4/4
```

**Balancing:** with `fullyParallel: true` shards split at the **individual-test** level (even
distribution); without it, they split at the **file** level — uneven file sizes cause imbalance, so
prefer `fullyParallel` for even shards.

Emit blob reports on CI, then merge into a single report:

```typescript
// playwright.config.ts
export default defineConfig({
  testDir: './tests',
  reporter: process.env.CI ? 'blob' : 'html',
});
```

```bash
npx playwright merge-reports --reporter html ./all-blob-reports
npx playwright merge-reports --reporter=html,github ./blob-reports
npx playwright merge-reports --config=merge.config.ts ./blob-reports
```

```typescript
// merge.config.ts
export default {
  testDir: 'e2e',
  reporter: [['html', { open: 'never' }]],
};
```

GitHub Actions — fan out with a matrix, upload each shard's blob, then a dependent job downloads all
blobs and merges them:

```yaml
jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        shardIndex: [1, 2, 3, 4]
        shardTotal: [4]
    steps:
      - run: npx playwright test --shard=${{ matrix.shardIndex }}/${{ matrix.shardTotal }}
      - if: ${{ !cancelled() }}
        uses: actions/upload-artifact@v4
        with:
          name: blob-report-${{ matrix.shardIndex }}
          path: blob-report
          retention-days: 1

  merge-reports:
    if: ${{ !cancelled() }}
    needs: [test]
    steps:
      - uses: actions/download-artifact@v5
        with:
          path: all-blob-reports
          pattern: blob-report-*
          merge-multiple: true
      - run: npx playwright merge-reports --reporter html ./all-blob-reports
      - uses: actions/upload-artifact@v4
        with:
          name: html-report--attempt-${{ github.run_attempt }}
          path: playwright-report
          retention-days: 14
```

Tag blob reports per environment so merged reports stay distinguishable:

```typescript
export default defineConfig({
  reporter: process.env.CI ? 'blob' : 'html',
  tag: process.env.CI_ENVIRONMENT_NAME,
});
```

## Timeouts

| Timeout | Default | Scope |
|---|---|---|
| Test | 30,000 ms | each test |
| Expect | 5,000 ms | each assertion |
| Action | none | each action (`click`, `fill`, …) |
| Navigation | none | each navigation |
| Global | none | whole run |
| beforeAll/afterAll | 30,000 ms | the hook |
| Fixture | none | individual fixture |

```typescript
export default defineConfig({
  timeout: 120_000,             // per-test
  globalTimeout: 3_600_000,     // whole run
  expect: { timeout: 10_000 },  // assertions
  use: {
    actionTimeout: 10 * 1000,
    navigationTimeout: 30 * 1000,
  },
});
```

Per-test and per-hook:

```typescript
test('slow test', async ({ page }) => {
  test.slow();             // triples the default test timeout
});

test('very slow test', async ({ page }) => {
  test.setTimeout(120_000);
});

test.beforeEach(async ({ page }, testInfo) => {
  testInfo.setTimeout(testInfo.timeout + 30_000);
});

test.beforeAll(async () => {
  test.setTimeout(60000);
});
```

Per-assertion / per-action:

```typescript
await expect(locator).toHaveText('hello', { timeout: 10_000 });
await page.goto('https://playwright.dev', { timeout: 30000 });
await page.getByText('Get Started').click({ timeout: 10000 });
```

Fixture timeout:

```typescript
import { test as base, expect } from '@playwright/test';

const test = base.extend<{ slowFixture: string }>({
  slowFixture: [async ({}, use) => {
    await use('hello');
  }, { timeout: 60_000 }],
});
```

## Global setup & teardown

Two ways to run code once before/after the whole suite. **Prefer setup/teardown projects** —
`globalSetup`/`globalTeardown` functions lack reporting, tracing, and fixtures:

| | Setup/teardown **projects** | `globalSetup`/`globalTeardown` |
|---|---|---|
| Shown in HTML report | ✅ | ❌ |
| Traces recorded | ✅ | ❌ |
| Fixtures available | ✅ | ❌ (manual `browserType.launch()`) |
| Parallelism / retries | ✅ | ❌ |
| Config `use` applied | ✅ | ❌ (ignored) |

### Option 1 — setup/teardown projects (recommended)

A `setup` project runs as a dependency; its `teardown` project runs after dependents finish. Setup/teardown are real tests, so they get fixtures, tracing, and reporting.

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  projects: [
    { name: 'setup db', testMatch: /global\.setup\.ts/, teardown: 'cleanup db' },
    { name: 'cleanup db', testMatch: /global\.teardown\.ts/ },
    {
      name: 'chromium with db',
      use: { ...devices['Desktop Chrome'] },
      dependencies: ['setup db'],
    },
  ],
});
```

```typescript
// tests/global.setup.ts
import { test as setup } from '@playwright/test';

setup('create new database', async ({ }) => {
  console.log('creating new database...');
});
```

```typescript
// tests/global.teardown.ts
import { test as teardown } from '@playwright/test';

teardown('delete database', async ({ }) => {
  console.log('deleting test database...');
});
```

### Option 2 — globalSetup / globalTeardown functions

A single function runs once before/after everything. No fixtures or reporting; commonly used to produce `storageState` or set `process.env`.

```typescript
export default defineConfig({
  globalSetup: require.resolve('./global-setup'),
  globalTeardown: require.resolve('./global-teardown'),
  use: {
    baseURL: 'http://localhost:3000/',
    storageState: 'state.json',
  },
});
```

```typescript
// global-setup.ts
import { chromium, type FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  const { baseURL, storageState } = config.projects[0].use;
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(baseURL!);
  await page.getByLabel('User Name').fill('user');
  await page.getByLabel('Password').fill('password');
  await page.getByText('Sign in').click();
  await page.context().storageState({ path: storageState as string });
  await browser.close();
}

export default globalSetup;
```

Passing data to tests via env vars set in `globalSetup`:

```typescript
async function globalSetup(config: FullConfig) {
  process.env.FOO = 'some data';
  process.env.BAR = JSON.stringify({ some: 'data' });
}
```

```typescript
test('test', async ({ page }) => {
  const { FOO, BAR } = process.env;
  expect(FOO).toEqual('some data');
  const complexData = JSON.parse(BAR);
});
```

Since `globalSetup` isn't traced, wrap it in `try/catch` and call `context.tracing.start(...)` /
`stop({ path })` yourself to debug setup failures — or just use Option 1, which traces automatically.

## Web server

Playwright starts (or reuses) a dev server before the run. `url` should return a 2xx/3xx/400/401/402/403 status when ready.

| Key | Notes |
|---|---|
| `command` | Shell command to start the server. |
| `url` | URL polled until ready. Prefer over deprecated `port`. |
| `reuseExistingServer` | Reuse a server already on `url`; else start `command`. Use `!process.env.CI`. |
| `timeout` | Startup wait, ms. Default `60000`. |
| `cwd` | Working dir of spawned process. Default = config file dir. |
| `env` | Env for command. Defaults to `process.env` + `PLAYWRIGHT_TEST=1`. |
| `stdout` | `'ignore'` (default) or `'pipe'`. |
| `stderr` | `'pipe'` (default) or `'ignore'`. |
| `ignoreHTTPSErrors` | Ignore HTTPS errors fetching `url`. Default `false`. |
| `gracefulShutdown` | How to stop the server, e.g. `{ signal: 'SIGTERM', timeout: 500 }`; default force-`SIGKILL`s the process group. |
| `name` | Label prefixed to the server's log messages (used with multiple servers). |
| `wait` | (v1.57+) Wait for readiness by matching a regex on output instead of polling `url`, e.g. `wait: { stdout: /Listening on port (?<port>\d+)/ }`. Named capture groups populate env vars usable in tests. |

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
    stdout: 'ignore',
    stderr: 'pipe',
  },
  use: { baseURL: 'http://localhost:3000' },
});
```

Multiple servers — pass an array:

```typescript
export default defineConfig({
  webServer: [
    {
      command: 'npm run start',
      url: 'http://localhost:3000',
      name: 'Frontend',
      timeout: 120 * 1000,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: 'npm run backend',
      url: 'http://localhost:3333',
      name: 'Backend',
      timeout: 120 * 1000,
      reuseExistingServer: !process.env.CI,
    },
  ],
  use: { baseURL: 'http://localhost:3000' },
});
```

## Reporters

`reporter` accepts a name string, or an array of `[name, options]` tuples for multiple reporters. Default: `list` locally, `dot` on CI.

```typescript
reporter: [
  ['list'],
  ['json', { outputFile: 'test-results.json' }],
]
```

| Reporter | Use |
|---|---|
| `list` | Default off-CI; one line per test. |
| `line` | Concise; single updating line. |
| `dot` | Default on CI; one char per test (`·` pass, `F` fail, `×` retry, `±` flaky). |
| `html` | Self-contained browsable report. |
| `json` | Full machine-readable result object. |
| `junit` | JUnit XML for CI integrations. |
| `blob` | Raw results + attachments for `merge-reports`. |
| `github` | Inline failure annotations in GitHub Actions. |
| custom | Path to a module implementing `Reporter`. |

```typescript
reporter: [['list', { printSteps: true, printFailuresInline: true }]]

reporter: [['html', {
  open: 'always' | 'never' | 'on-failure',
  outputFolder: 'my-report',
  attachmentsBaseURL: 'https://external-storage.com/',
  title: 'Test Report',
  host: 'localhost',
  port: 9323,
}]]

reporter: [['json', { outputFile: 'results.json' }]]

reporter: [['junit', {
  outputFile: 'results.xml',
  includeProjectInTestName: false,
  suiteId: '',
  suiteName: '',
}]]

reporter: process.env.CI ? 'github' : 'list'
```

View / serve an HTML report:

```bash
npx playwright show-report
npx playwright show-report my-report
```

Env overrides: `PLAYWRIGHT_JSON_OUTPUT_NAME`, `PLAYWRIGHT_JUNIT_OUTPUT_NAME`, `PLAYWRIGHT_LIST_PRINT_STEPS`, `PLAYWRIGHT_FORCE_TTY`, `FORCE_COLOR`, `NO_COLOR`.

Custom reporter — implement the `Reporter` interface and point `reporter` at the file. All hooks are
optional; implement only what you need:

| Method | Fires |
|---|---|
| `onBegin(config, suite)` | Once, before any test — full test tree known. |
| `onTestBegin(test, result)` | Before each test attempt. |
| `onStepBegin(test, result, step)` / `onStepEnd(...)` | Around each `test.step` (and built-in steps). |
| `onStdOut(chunk, test?, result?)` / `onStdErr(...)` | On test/process stdout/stderr. |
| `onTestEnd(test, result)` | After each test attempt (has status, errors, attachments). |
| `onError(error, workerInfo?)` | On a global (non-test) error. |
| `onEnd(result)` | Once, after all tests — `result.status` is the run outcome; may return `{ status }` to override exit. |
| `onExit()` | Just before the runner process exits (final async flush). |
| `printsToStdio()` | Return `false` if the reporter writes only to a file (avoids stdout clashes). |

The objects passed to these hooks (from `@playwright/test/reporter`):
- **`Suite`** — the test tree: `type` (`root`/`project`/`file`/`describe`), `title`, `suites`,
  `tests`, `allTests()`, `entries()`, `project()`.
- **`TestCase`** — `title`/`titlePath()`, `location`, `tags`, `annotations`, `expectedStatus`,
  `results`, `id`, `ok()`, `outcome()` (`expected`/`unexpected`/`flaky`/`skipped`).
- **`TestResult`** — one attempt: `status`, `duration`, `retry`, `errors`, `attachments`, `stdout`,
  `stderr`, `steps`, `workerIndex`.
- **`TestStep`** — `title`, `category` (`expect`/`fixture`/`hook`/`pw:api`/`test.step`), `duration`,
  `error`, nested `steps`, `attachments`.
- **`TestError`** — `message`, `stack`, `value`, `location`, `snippet` (highlighted source), `cause`.

```typescript
import type {
  FullConfig, FullResult, Reporter, Suite, TestCase, TestResult,
} from '@playwright/test/reporter';

class MyReporter implements Reporter {
  onBegin(config: FullConfig, suite: Suite) {
    console.log(`Starting: ${suite.allTests().length} tests`);
  }
  onTestBegin(test: TestCase, result: TestResult) {
    console.log(`Starting test ${test.title}`);
  }
  onTestEnd(test: TestCase, result: TestResult) {
    console.log(`Finished: ${result.status}`);
  }
  onEnd(result: FullResult) {
    console.log(`Run finished: ${result.status}`);
  }
}

export default MyReporter;
```

Mature third-party reporters exist (Allure, Monocart, ReportPortal, GitHub Actions, mail) — search npm
before writing your own.

```typescript
reporter: './my-awesome-reporter.ts'
```

```bash
npx playwright test --reporter="./myreporter/my-awesome-reporter.ts"
```

## Env-driven config

Branch on `process.env.CI` (and custom vars) so one config serves local and CI:

```typescript
export default defineConfig({
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? 'blob' : 'html',
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

Use env vars to **parameterize** a run — point at an environment, or inject secrets without hardcoding:

```typescript
export default defineConfig({
  use: {
    baseURL: process.env.STAGING === '1' ? 'http://staging.example.test/' : 'http://example.test/',
  },
});
```

```bash
STAGING=1 USER_NAME=me PASSWORD=secret npx playwright test   # tests read process.env.USER_NAME etc.
```

**`.env` files** — load with `dotenv` at the top of the config so values are available everywhere:

```typescript
import { defineConfig } from '@playwright/test';
import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.resolve(__dirname, '.env') });   // populates process.env

export default defineConfig({
  use: { baseURL: process.env.STAGING === '1' ? 'http://staging.example.test/' : 'http://example.test/' },
});
```

Keep `.env` out of git; commit a `.env.example` instead. For credential reuse via `storageState`
instead of typing in every test, see [auth.md](auth.md); for option-fixture parameterization see
[test-organization.md](test-organization.md#parameterized-tests).

## Config validation (v1.60+)

Playwright now rejects two previously-silent mistakes at load time:

- **Fixture-override attempts in config** — you cannot override built-in fixtures through the config; do it with `test.extend` (see [fixtures.md](fixtures.md)).
- **Non-positive `workers`** — `workers: 0` or negative values are errors; use a positive number or percentage string.

## See also

- [writing-tests.md](writing-tests.md) · [test-organization.md](test-organization.md) · [fixtures.md](fixtures.md) · [auth.md](auth.md)
- [emulation.md](emulation.md) · [visual-comparisons.md](visual-comparisons.md) · [trace-viewer.md](trace-viewer.md) · [screencast.md](screencast.md)
- [network.md](network.md) · [debugging.md](debugging.md) · [whats-new.md](whats-new.md)
