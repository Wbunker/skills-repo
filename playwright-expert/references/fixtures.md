# Fixtures

Fixtures are Playwright's core abstraction for setup/teardown. Master these and most test
boilerplate disappears.

## Contents
- [What a fixture is](#what-a-fixture-is)
- [Why fixtures beat beforeEach](#why-fixtures-beat-beforeeach)
- [Built-in fixtures](#built-in-fixtures)
- [Custom fixtures](#custom-fixtures)
- [Fixtures depending on fixtures](#fixtures-depending-on-fixtures)
- [Scopes: test vs worker](#scopes-test-vs-worker)
- [Auto fixtures](#auto-fixtures)
- [Option fixtures](#option-fixtures)
- [Overriding fixtures](#overriding-fixtures)
- [Boxing, titles, timeouts](#boxing-titles-timeouts)
- [Merging fixtures](#merging-fixtures)
- [Page objects as fixtures](#page-objects-as-fixtures)
- [Reference architecture](#reference-architecture)

## What a fixture is

A fixture is setup-and-teardown code that **produces a value your test asks for by name**. When you
write `async ({ page }) => {}`, the `{ page }` argument tells Playwright to set up the `page` fixture
and inject it. `page`, `context`, `browser`, `request` are all built-in fixtures. Fixtures
"establish the environment for each test, giving the test everything it needs and nothing else," and
are isolated between tests.

## Why fixtures beat beforeEach

The mechanical difference: fixtures are **lazy** and **dependency-injected**.

- A fixture runs **only for tests that name it**. If a test doesn't request it, it never runs.
- A `beforeEach` runs for **every** test in the file whether needed or not.

That laziness is the central reason fixtures win for anything conditional — only the exact
dependencies of a given test are initialized, keeping runs fast. Fixtures are also composable
(depend on each other), reusable across files, and on-demand.

## Built-in fixtures

| Fixture | Type | What you get |
|---------|------|--------------|
| `page` | `Page` | Isolated page, fresh per test |
| `context` | `BrowserContext` | Isolated context (cookies/storage) per test |
| `browser` | `Browser` | Shared browser instance |
| `browserName` | `string` | `'chromium'` \| `'firefox'` \| `'webkit'` |
| `request` | `APIRequestContext` | Isolated context for API calls |

## Custom fixtures

Create them with `test.extend()`, conventionally in a central `fixtures.ts`, then import `test`/
`expect` from there instead of `@playwright/test`. The **`use()` call is the structural heart**:
everything before it is setup, everything after is teardown — and teardown runs **even if the test
fails**, which is why fixtures are safer than manual cleanup.

```typescript
// fixtures.ts
import { test as base } from '@playwright/test';
import { TodoPage } from './todo-page';

export const test = base.extend<{ todoPage: TodoPage }>({
  todoPage: async ({ page }, use) => {
    const todoPage = new TodoPage(page);   // setup
    await todoPage.goto();
    await use(todoPage);                    // hand the value to the test
    await todoPage.removeAll();             // teardown (runs on pass OR fail)
  },
});
export { expect } from '@playwright/test';
```

```typescript
// a test — no setup boilerplate, just name the fixture
import { test, expect } from './fixtures';

test('adds todo', async ({ todoPage }) => {
  // todoPage is already created, navigated, and will self-clean
});
```

Canonical jobs custom fixtures do beyond DRY: setting cookies/tokens for login, loading test data,
managing DB or API mocks, and injecting feature flags or config. The goal state: adding a test means
writing the test logic and nothing else.

## Fixtures depending on fixtures

A fixture's first argument is an object of **already-defined fixtures**, so you can compose chains
(`dbClient → seededData → boardPage`). When A depends on B, **B is set up before A and torn down
after A**. Fixtures are also available inside hooks and other fixtures, and are type-safe with
TypeScript.

```typescript
export const test = base.extend<{ dbClient: DbClient; seededBoard: Board }>({
  dbClient: async ({}, use) => {
    const client = await connect();
    await use(client);
    await client.end();
  },
  seededBoard: async ({ dbClient }, use) => {   // depends on dbClient
    const board = await dbClient.seedBoard();
    await use(board);
    await dbClient.deleteBoard(board.id);
  },
});
```

## Scopes: test vs worker

Scope is your **speed lever**.

- **Test-scoped** (default): created and destroyed for every test. Use when isolation matters more
  than speed (per-test data).
- **Worker-scoped**: created **once per worker process** and reused across all tests in that worker.
  Put expensive one-time setup here — a Testcontainers backend, a DB connection pool, a mock server
  — so you pay for it once per worker, not once per test.

Declare worker scope with the tuple form `[fn, { scope: 'worker' }]`:

```typescript
export const test = base.extend<{}, { apiServer: ApiServer }>({
  apiServer: [async ({}, use) => {
    const server = await ApiServer.start();   // expensive — once per worker
    await use(server);
    await server.stop();
  }, { scope: 'worker' }],
});
```

The two type params to `extend<TestFixtures, WorkerFixtures>` separate test-scoped from worker-scoped
fixture types. Splitting expensive-shared (worker) from isolated-per-test (test) is how you get
fast **and** isolated.

## Auto fixtures

`{ auto: true }` runs the fixture for **every test** using the extended `test`, without being named
— the fixture replacement for cross-cutting `beforeEach`/`afterEach`. Ideal for global logging,
starting a mock server, or installing `page.route()` network mocks so every test gets contract-pinned
mocks by default.

```typescript
export const test = base.extend<{ mockApi: void }>({
  mockApi: [async ({ page }, use) => {
    await page.route('**/api/**', route => route.fulfill({ json: fixtureData }));
    await use();
  }, { auto: true }],
});
```

Per-worker auto setup (global `beforeAll`/`afterAll`):
```typescript
forEachWorker: [async ({}, use) => {
  // ...once per worker, before any test
  await use();
  // ...after all tests in the worker
}, { scope: 'worker', auto: true }],
```

> Use auto fixtures **sparingly** — they introduce hidden dependencies that make tests harder to
> reason about.

## Option fixtures

Make configuration **declarative and type-safe** so the same test logic runs against different
fixtures per project. Mark a fixture with `{ option: true }` and a default value:

```typescript
// fixtures.ts
type MyOptions = { defaultItem: string };
export const test = base.extend<MyOptions & { todoPage: TodoPage }>({
  defaultItem: ['Something nice', { option: true }],
  todoPage: async ({ page, defaultItem }, use) => {
    const todoPage = new TodoPage(page);
    await todoPage.addToDo(defaultItem);
    await use(todoPage);
  },
});
```

```typescript
// playwright.config.ts — parameterize per project
projects: [
  { name: 'shopping', use: { defaultItem: 'Buy milk' } },
  { name: 'chores',   use: { defaultItem: 'Take out trash' } },
]
```

## Overriding fixtures

Redefine a built-in (or inherited) fixture to add behavior — e.g. auto-navigate every `page` to
`baseURL`:

```typescript
export const test = base.extend({
  page: async ({ baseURL, page }, use) => {
    await page.goto(baseURL!);
    await use(page);
  },
});
```

## Boxing, titles, timeouts

Custom fixtures show up as separate steps in the trace viewer and reports — noisy for frequently used
helpers. **Box** a fixture to hide its plumbing so the trace shows the actual behavior under test:

```typescript
auth: [async ({}, use) => { /* ... */ }, { box: true }],        // hide fixture + its steps
setup: [async ({}, use) => { /* ... */ }, { box: 'self' }],     // hide the fixture, keep inner steps
```

Other options:
```typescript
slowFixture: [async ({}, use) => { /* ... */ }, { timeout: 60_000 }],   // per-fixture timeout
named:       [async ({}, use) => { /* ... */ }, { title: 'my fixture' }],// custom report title
```

## Merging fixtures

Combine fixtures defined in separate modules:

```typescript
import { mergeTests } from '@playwright/test';
import { test as dbTest } from './db-fixtures';
import { test as a11yTest } from './a11y-fixtures';

export const test = mergeTests(dbTest, a11yTest);
```

## Page objects as fixtures

The cleanest way to use a Page Object Model — expose it as a (boxed) fixture so every test gets a
ready instance by name:

```typescript
import { test as base, type Page, type Locator } from '@playwright/test';

class AdminPage {
  readonly greeting: Locator;
  constructor(public page: Page) {
    this.greeting = page.locator('#greeting');
  }
}

export const test = base.extend<{ adminPage: AdminPage }>({
  adminPage: async ({ browser }, use) => {
    const context = await browser.newContext({ storageState: 'playwright/.auth/admin.json' });
    const adminPage = new AdminPage(await context.newPage());
    await use(adminPage);
    await context.close();
  },
});
```

## Reference architecture

A layered, fast, deterministic setup composed once in `fixtures.ts`, named à la carte per test:

- **worker-scoped `apiServer`/Testcontainers fixture** — expensive backend, started once per worker.
- **test-scoped `seededBoard` fixture** depending on it — isolated, known data per test.
- **boxed `boardPage` page-object fixture** — exposes a serialized board-state oracle and role-based
  locators; boxed so traces show behavior, not plumbing.
- **auto `mockApi` fixture** — installs schema-pinned `page.route()` handlers so optimistic-update
  branches (hold response / resolve / reject) are trivial to drive and mocks never drift silently.

This gives the fast-but-isolated balance: expensive things shared per worker, data isolated per test,
network behavior pinned by default, and tests that only contain test logic.
