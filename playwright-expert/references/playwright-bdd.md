# playwright-bdd (Cucumber/Gherkin on the Playwright runner)

`playwright-bdd` (by Vitaliy Potapov) runs **Cucumber/Gherkin BDD on top of the Playwright test
runner** — not on top of CucumberJS. You write `.feature` files + step definitions; a generator
(`bddgen`) emits plain Playwright `*.spec.js` files; `playwright test` runs them. You keep Gherkin's
collaboration layer **and** all of Playwright's tooling (parallelism, fixtures, traces, UI mode, VS
Code extension, sharding, HTML report).

> Why generation, not on-the-fly: the Playwright config is loaded many times (workers, VS Code
> extension, UI mode), so running BDD inline would regenerate constantly and risk circular
> file-watch loops. Decoupling **generation** from **execution** is the core design choice — and is
> why every run is `bddgen && playwright test`.

Docs: <https://vitalets.github.io/playwright-bdd/>. This file is the playwright-bdd layer; the rest
of this skill ([fixtures.md](fixtures.md), [auth.md](auth.md), [test-config.md](test-config.md),
[locators.md](locators.md)) applies unchanged inside step bodies.

## Contents
- [Install & first test](#install--first-test)
- [Config: defineBddConfig options](#config-definebddconfig-options)
- [The bddgen CLI](#the-bddgen-cli)
- [Writing features (Gherkin)](#writing-features-gherkin)
- [Special tags](#special-tags)
- [Writing steps — three styles](#writing-steps--three-styles)
- [BDD fixtures ($-prefixed)](#bdd-fixtures--prefixed)
- [Scoped steps & sharing data](#scoped-steps--sharing-data)
- [Data tables & doc strings](#data-tables--doc-strings)
- [Hooks](#hooks)
- [Multiple projects](#multiple-projects)
- [Authentication](#authentication)
- [Reporters](#reporters)
- [UI mode & watch](#ui-mode--watch)
- [Agent skill, AI fix, ESM](#agent-skill-ai-fix-esm)
- [Gotchas](#gotchas)

## Install & first test

```bash
npm i -D @playwright/test playwright-bdd   # add playwright-bdd; drop @playwright/test if already present
npx playwright install
```
Yarn PnP users must add a `packageExtensions` entry in `.yarnrc.yml` giving `playwright-bdd` a
`playwright`/`playwright-core` dependency.

Three files — config, feature, steps:

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';
import { defineBddConfig } from 'playwright-bdd';

const testDir = defineBddConfig({
  features: 'features/*.feature',
  steps: 'steps/*.ts',
});

export default defineConfig({ testDir, reporter: 'html' });
```

```gherkin
# features/sample.feature
Feature: Playwright site
  Scenario: Check get started link
    Given I am on home page
    When I click link "Get started"
    Then I see in title "Installation"
```

```ts
// steps/steps.ts
import { expect } from '@playwright/test';
import { createBdd } from 'playwright-bdd';

const { Given, When, Then } = createBdd();

Given('I am on home page', async ({ page }) => {
  await page.goto('https://playwright.dev');
});
When('I click link {string}', async ({ page }, name: string) => {
  await page.getByRole('link', { name }).click();
});
Then('I see in title {string}', async ({ page }, keyword: string) => {
  await expect(page).toHaveTitle(new RegExp(keyword));
});
```

Run — **always generate first**:
```bash
npx bddgen && npx playwright test          # generates .features-gen/, then runs
npx playwright show-report
```

## Config: defineBddConfig options

`defineBddConfig(opts)` returns the generated output dir; assign it to `testDir` (root) or a
project's `testDir`. **All relative paths (`features`, `steps`, `outputDir`, `featuresRoot`) resolve
from the config file's location**, not the cwd.

| Option | Type | Default | Purpose |
|--------|------|---------|---------|
| `features` | `string \| string[]` | — | Glob(s)/dirs of `.feature` files (dir → `**/*.feature`) |
| `steps` | `string \| string[]` | — | Glob(s)/dirs of step files (dir → `**/*.{js,mjs,cjs,ts,mts,cts}`) |
| `featuresRoot` | `string` | config dir | Base dir for generated paths (like tsc `rootDir`); since v8 also the default for `features` **and** `steps` |
| `outputDir` | `string` | `.features-gen` | Where generated specs go (resolved from config); **must be unique per project** |
| `language` | `string` | `en` | Default Gherkin language |
| `tags` | `string` | — | Tag expression filtering which scenarios generate, e.g. `'@desktop and not @slow'` |
| `missingSteps` | `'fail-on-gen' \| 'fail-on-run' \| 'skip-scenario'` | `fail-on-gen` | Behavior for undefined steps (v8+) |
| `matchKeywords` | `boolean` | `false` | Match steps including the Given/When/Then keyword (v8+) |
| `quotes` | `'single' \| 'double' \| 'backtick'` | `single` | Quote style in generated files |
| `examplesTitleFormat` | `string` | `Example #<_index_>` | Title template for Scenario Outline rows |
| `arityCheck` | `boolean` | `true` | Validate step fn arg count at gen time (override per step) |
| `aiFix` | `object` | — | `{ promptAttachment, promptAttachmentName, promptTemplate }` — see [AI fix](#agent-skill-ai-fix-esm) |
| `statefulPoms` | `boolean` | `false` | Stricter fixture inference for decorator steps with stateful POMs |
| `importTestFrom` | `string` | auto (v7+) | File exporting custom `test` for generated specs (rarely needed now) |
| `verbose` | `boolean` | `false` | Verbose logging |

Deprecated → replacement: `paths`→`features`, `require`→`steps` (CJS), `import`→`steps` (ESM).

## The bddgen CLI

| Command | Does |
|---------|------|
| `npx bddgen` (alias `bddgen test`) | Generate spec files from features. Needs `playwright.config.(ts\|js)` with `defineBddConfig()` |
| `npx bddgen --tags "@a and not @b"` | Generate only matching scenarios |
| `npx bddgen -c path/config.ts` | Custom config path (pass the same `-c` to `playwright test`) |
| `npx bddgen export` | Print all discovered step definitions (used by AI step grounding) |
| `npx bddgen export --unused-steps` | List steps not referenced by any feature |
| `npx bddgen env` | Platform, Node, and playwright-bdd/@playwright/@cucumber versions |

The canonical pipeline is `bddgen && playwright test` — wire it into npm scripts and CI.

## Writing features (Gherkin)

Standard Gherkin: `Feature`, `Background`, `Scenario`, `Scenario Outline` + `Examples`, `Rule`, and
`Given/When/Then/And/But`. Extras playwright-bdd adds:

**Localization (i18n)** — write keywords in any [Cucumber-supported language](https://cucumber.io/docs/gherkin/languages/)
via the `language` config or a per-file `# language:` header. Step matching follows the localized
keywords.
```gherkin
# language: es
Característica: Sitio de Playwright
  Escenario: Verificar título
    Dado que abro la url "https://playwright.dev"
    Cuando hago clic en el enlace "Get started"
    Entonces veo en el título "Playwright"
```

**Tags from path** — `@`-prefixed directories or filenames auto-apply that tag to all features
inside, equivalent to writing the tag in the file. Special tags work as dir names too:
```
features/
├── @game/                 → tags everything @game
│   ├── @slow/feature1.feature      → also @slow
│   ├── @skip/feature2.feature      → also @skip
│   └── @mode:serial/feature3.feature
└── @video-player.feature  → tags this file @video-player
```

**Custom Scenario Outline titles** — four ways, most specific wins; generated titles must be
**unique** per scenario or Playwright errors:
1. `<column>` tokens in the scenario name — `Scenario Outline: Multiply <value> by two`
2. A name after `Examples:` (with `<column>` tokens) — `Examples: positive value <value>`
3. A `# title-format: check <value>` comment directly above an `Examples:` block
4. Global `examplesTitleFormat` config (default `Example #<_index_>`)

**Auto-formatting** — format `.feature` files with **Prettier + `prettier-plugin-gherkin`** (great
for aligning data tables):
```js
// prettier.config.mjs
export default { plugins: ['prettier-plugin-gherkin'] };
```

**Authoring with ChatGPT/AI** — write step defs first (reliable locators), then ground generation in
your real steps: `npx bddgen export` lists all step patterns; feed that list to the model with a
prompt that says *"strictly use only the following step definitions"* so the output actually runs.
The [agent skill](#agent-skill-ai-fix-esm) automates this loop.

## Special tags

Tags on a `Feature` apply to every scenario inside it. playwright-bdd maps these to Playwright
runner behavior:

| Tag | Effect |
|-----|--------|
| `@only` | Run only this feature/scenario |
| `@skip` / `@fixme` | Skip it (can be made conditional via a fixture) |
| `@fail` | Mark as expected-to-fail (test passes if it fails) |
| `@slow` | Timeout ×3 |
| `@timeout:30000` | Set scenario timeout (ms); at feature level applies to each scenario |
| `@retries:2` | Retry count for the feature, or a single scenario (wraps it in a describe) |
| `@mode:parallel` / `@mode:serial` / `@mode:default` | Execution mode — **feature/outline level only**, not a single scenario |

Your own tags (`@smoke`, `@jira:123`) are readable at runtime via the `$tags` fixture and usable in
`--tags` expressions and hook filters. Tags placed on a `Feature` apply to every scenario in it.
Since Playwright 1.42, Gherkin tags also map to native **Playwright tags**, so they show in the HTML
report and work with `playwright test --grep @smoke`.

## Writing steps — three styles

All three can coexist. Doc's guidance: **playwright-style** for new BDD projects or existing
Playwright projects; **cucumber-style** when migrating a CucumberJS suite; **decorators** are
recommended for all projects (steps live on POM methods). Register steps only with
`Given`/`When`/`Then` — **there are no `And()`/`But()` functions**; `And`/`But` are Gherkin-only
keywords. By default the keyword is **ignored** in matching (a `Given` def matches a `When` step). With
`matchKeywords: true`, matching is strict: `Given/When/Then` match only their own keyword, `And`/`But`
resolve to the nearest preceding primary keyword (→ `Given` if first), a `*` step matches any keyword,
and a universal `Step('...')` definition matches regardless of keyword.

### 1. Playwright-style (default)
Fixtures arrive as the **first arg** (destructured); remaining args are step parameters. No `this`;
use arrow functions.

```ts
import { createBdd } from 'playwright-bdd';
const { Given, When, Then } = createBdd();

Given('I open url {string}', async ({ page }, url: string) => {
  await page.goto(url);
});
// regex: capture groups become params
Then(/I should see (success|error) message/, async ({ page }, status: string) => {
  await expect(page.getByRole('alert')).toHaveText(status);
});
```
Cucumber-expression params: `{string}`, `{int}`, `{float}`, `{word}`, plus custom types registered
with `defineParameterType({ name, regexp, transformer })` (from `playwright-bdd`) — e.g. a `{color}`
param that transforms to an enum. A default `world` (empty `{}`) exists only for migration — access it
with a non-arrow function if you must.

### 2. Cucumber-style (CucumberJS-compatible)
Steps get **only step params**; shared state lives on a `World` accessed via `this` (non-arrow
functions). The World is just a test-scoped fixture — **no `setWorldConstructor`** needed.

```ts
import { test as base, createBdd } from 'playwright-bdd';
import { World } from './world';

export const test = base.extend<{ world: World }>({
  world: async ({ page }, use) => use(new World(page)),
});
export const { Given, When, Then, Before, After } = createBdd(test, { worldFixture: 'world' });

// steps
Given('I am on home page', async function () {
  await this.openHomePage();   // `this` is the World
});
```

### 3. Decorators (steps inside Page Objects)
Needs TS5 decorators. Decorate POM methods; bind the class to a fixture with `@Fixture`. Register
the POM as a fixture so its steps are discoverable.

```ts
import { Fixture, Given, When, Then } from 'playwright-bdd/decorators';

export
@Fixture('todoPage')
class TodoPage {
  constructor(public page: Page) {}
  @Given('I am on todo page')
  async open() { await this.page.goto('https://demo.playwright.dev/todomvc/'); }
  @When('I add todo {string}')
  async add(text: string) { await this.page.locator('input.new-todo').fill(text); }
  @Then('visible todos count is {int}')
  async count(n: number) { await expect(this.page.getByTestId('todo-item')).toHaveCount(n); }
}
```
```ts
// fixtures.ts — register, then point `steps` at this file
export const test = base.extend<{ todoPage: TodoPage }>({
  todoPage: ({ page }, use) => use(new TodoPage(page)),
});
```
One method may carry multiple `@When(...)` decorators for alternate phrasings; child POMs may
override parent steps. To use BDD fixtures (`$tags`, `$test`) inside a POM, pass them through the
constructor and inject them in the fixture definition. `statefulPoms: true` tightens fixture
inference when POMs hold state.

### Step options, reuse & snippets
Per-step overrides: `Given('...', { arityCheck: false }, async ({}, ...args) => {})`.

**Reuse a step function** — `Given/When/Then` return the step fn; save it and call it from another
step (don't duplicate logic):
```ts
const createTodo = When('I create todo {string}', async ({ page }, text: string) => { /* ... */ });
When('I create 2 todos {string} and {string}', async ({ page }, a: string, b: string) => {
  await createTodo({ page }, a);          // playwright-style: pass fixtures explicitly
  await createTodo({ page }, b);
});
// cucumber-style: createTodo.call(this, a)  — pass the World via .call()
```
Add JSDoc param types to reusable step fns for IntelliSense at call sites.

**Missing-step snippets** — when a step has no definition, `bddgen` prints a ready-to-paste snippet
(pattern + the source `feature:line`); paste it and fill the body. Control whether generation
proceeds via [`missingSteps`](#config-definebddconfig-options) (`fail-on-gen` / `fail-on-run` /
`skip-scenario`).

## BDD fixtures ($-prefixed)

playwright-bdd injects extra fixtures (all `$`-prefixed to avoid collisions). Use them in step
bodies and hooks just like `page`:

| Fixture | Gives |
|---------|-------|
| `$test` | Playwright `test` object — `$test.skip()`, `.slow()`, `.setTimeout()` |
| `$testInfo` | Playwright `TestInfo` — `attach()`, `outputPath()`, status, etc. |
| `$step` | Current step metadata: `.title` (text minus keyword), `.docStringType`, `.error` (set in AfterStep) |
| `$tags` | `string[]` of the scenario's tags, e.g. `['@slow','@jira:123']` |
| `$workerInfo` | Worker info (worker hooks) |

```ts
Given('I do something', async ({ browserName, $test, $tags }) => {
  if (browserName === 'firefox') $test.skip();
  if ($tags.includes('@slow')) $test.slow();
});
```
Custom fixtures: define them with `base.extend(...)`, build `createBdd(test)` from that extended
`test`, and they become destructurable in every step. Keep this in one `fixtures.ts` that exports
**both** `test` and the BDD functions, then import the BDD functions in step files:

```ts
// fixtures.ts
import { test as base, createBdd } from 'playwright-bdd';
type Fixtures = { myFixture: MyFixture };
export const test = base.extend<Fixtures>({ myFixture: async ({}, use) => { /* ... */ } });
export const { Given, When, Then } = createBdd(test);   // built from the EXTENDED test
```
```ts
// steps.ts
import { Given } from './fixtures';
Given('My step', async ({ myFixture }) => { /* ... */ });
```
**You must `export` the `test` variable** — generated spec files import it. Forgetting this breaks
generation.

## Scoped steps & sharing data

**Scoped step definitions** — bind a step to specific features/scenarios by tag so the **same step
text resolves to different implementations** per domain. Scope per-step, per-`createBdd`, or by path:
```ts
// per step
When('I click the PLAY button', { tags: '@game' },         async () => { /* game */ });
When('I click the PLAY button', { tags: '@video-player' }, async () => { /* player */ });
// or set a default for every step in the file
const { When } = createBdd(test, { tags: '@game' });
```
Steps defined inside a `@game/` [tags-from-path](#writing-features-gherkin) directory auto-scope to
`@game`; unscoped steps in a shared dir match everywhere.

**Sharing data between steps (same scenario)** — use a custom **test-scoped `ctx` fixture** as a
container (the typed equivalent of Cucumber's World); avoid module-level variables (they leak across
parallel tests):
```ts
type Ctx = { newTabPromise?: Promise<Page> };
export const test = base.extend<{ ctx: Ctx }>({
  ctx: async ({}, use) => { await use({} as Ctx); },
});
// step 1 writes, step 2 reads
When('I click the link', async ({ page, context, ctx }) => {
  ctx.newTabPromise = context.waitForEvent('page');
  await page.getByRole('link').click();
});
Then('new tab is opened', async ({ ctx }) => {
  await expect(await ctx.newTabPromise).toHaveTitle(/checkout/);
});
```
Cucumber-style does the same via `this`.

**Sharing data between scenarios** — needs a **worker-scoped** fixture holding a per-file map, plus a
test-scoped accessor. Requires serial mode, which the Playwright team **discourages** — only do this
when scenarios genuinely depend on each other:
```ts
export const test = base.extend<{ ctx: Ctx }, { ctxMap: Record<string, Ctx> }>({
  ctx: async ({ ctxMap }, use, testInfo) => {
    ctxMap[testInfo.file] ||= {};
    await use(ctxMap[testInfo.file]);
  },
  ctxMap: [async ({}, use) => {
    const m: Record<string, Ctx> = {};
    await use(m);
    for (const c of Object.values(m)) await c.page?.close();   // teardown
  }, { scope: 'worker' }],
});
```

## Data tables & doc strings

**Data table** → last step argument, typed `DataTable` (imported from `playwright-bdd`):

```ts
import { createBdd, DataTable } from 'playwright-bdd';
const { When } = createBdd();

When('I fill login form with values', async ({ page }, data: DataTable) => {
  for (const { label, value } of data.hashes()) {      // [{label,value}, ...] from header row
    await page.getByLabel(label).fill(value);
  }
});
```
`DataTable` methods (Cucumber semantics): `.raw()`, `.rows()`, `.hashes()`, `.rowsHash()`.

**Doc string** → last step argument as a plain string. An optional media type after the opening
fence is exposed on `$step.docStringType` (playwright-bdd does **not** parse it for you):

```ts
When('Fill page with:', async ({ page, $step }, docString: string) => {
  if ($step.docStringType !== 'json') throw new Error('expected json');
  const data = JSON.parse(docString);
});
```

## Hooks

Hooks are exported from your `createBdd(test)` and imported where you define them. **Prefer fixtures
over hooks** — fixtures are lazy and compose better; reach for hooks only for true cross-cutting
lifecycle work. A tagged `Before`/`After` pair usually collapses into one fixture:

```ts
// instead of: Before({ tags: '@auth' }, ...) + After({ tags: '@auth' }, ...)
export const test = base.extend({
  auth: async ({}, use) => {
    /* sign in */          await use({ username: 'alice' });   /* sign out */
  },
});
// step pulls it in by name — runs only when used, no tag needed, reusable everywhere
Given('I am an authorized user', async ({ auth }) => { console.log(auth.username); });
```

| Hook (primary / alias) | Runs |
|------------------------|------|
| `BeforeWorker` / `BeforeAll` | Once per worker, before its scenarios |
| `AfterWorker` / `AfterAll` | Once per worker, after its scenarios |
| `BeforeScenario` / `Before` | Before each scenario |
| `AfterScenario` / `After` | After each scenario |
| `BeforeStep` | Before each step |
| `AfterStep` | After each invoked step (`$step.error` holds any failure) |

```ts
export const { BeforeScenario, AfterScenario, BeforeWorker } = createBdd(test);

BeforeScenario(async ({ page, $tags, $testInfo }) => { /* test-scoped fixtures available */ });
BeforeScenario({ tags: '@mobile and not @slow' }, async () => { /* tag-filtered */ });
BeforeScenario('@mobile', async () => { /* shorthand for { tags } */ });
BeforeScenario({ name: 'seed db', timeout: 5000 }, async () => { /* named + timeout */ });

BeforeWorker(async ({ $workerInfo, browser }) => { /* worker-scoped only; no World */ });
```
Default tags via `createBdd(test, { tags: '@mobile' })` AND-combine with per-hook tags. For
execution-wide setup, use Playwright **project dependencies** / global setup instead of hooks.

**Step hooks** — in `AfterStep`, detect a failed step with **`$step.error`**, never
`$testInfo.status` (which reflects the whole test, not the step). Handy for per-step screenshots/logs:
```ts
AfterStep(async ({ page, $testInfo, $step }) => {
  if ($step.error) await $testInfo.attach(`fail: ${$step.title}`,
    { contentType: 'image/png', body: await page.screenshot() });
});
```

**Running a hook truly once** (not once per worker) — `BeforeWorker` runs in *every* worker. To do
expensive setup a single time across all workers, wrap it with `@global-cache/playwright`:
```ts
import { globalCache } from '@global-cache/playwright';
BeforeWorker(async () => {
  await globalCache.get('populate-db', async () => { await populateDatabase(); });  // runs once
});
// also supports TTL, e.g. globalCache.get('auth-state', { ttl: '1 hour' }, fn)
```

## Multiple projects

**Same features, many browsers** — one root `testDir`, normal Playwright `projects`:
```ts
const testDir = defineBddConfig({ features: 'features/**/*.feature', steps: 'steps/**/*.ts' });
export default defineConfig({
  testDir,
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox',  use: { ...devices['Desktop Firefox'] } },
  ],
});
```

**Different features per project** — a `defineBddConfig` per project, each with a **unique
`outputDir`**:
```ts
projects: [
  { name: 'one', testDir: defineBddConfig({ outputDir: '.features-gen/one', features: 'one/**/*.feature', steps: 'one/steps/**/*.ts' }) },
  { name: 'two', testDir: defineBddConfig({ outputDir: '.features-gen/two', features: 'two/**/*.feature', steps: 'two/steps/**/*.ts' }) },
]
```
Or `defineBddProject({ name, features, steps })`, which auto-derives `outputDir` and returns a
project object to spread.

## Authentication

Same storageState model as plain Playwright ([auth.md](auth.md)) — just keep the login flow in a
**non-BDD setup project** so it isn't generated.

**Static (shared account):** setup project saves state, BDD project depends on it and loads via
`storageState`.
```ts
export const AUTH_FILE = 'playwright/.auth/user.json';
export default defineConfig({
  projects: [
    { name: 'auth', testDir: 'features/auth', testMatch: /setup\.ts/ },
    { name: 'chromium', testDir: defineBddConfig({ /* ... */ }),
      use: { storageState: AUTH_FILE }, dependencies: ['auth'] },
  ],
});
```
```ts
// features/auth/setup.ts  (plain Playwright, not BDD)
setup('authenticate', async ({ page }) => {
  await page.goto('https://example.com/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Log In' }).click();
  await expect(page.getByRole('link', { name: 'Sign Out' })).toBeVisible();
  await page.context().storageState({ path: AUTH_FILE });
});
```
Skip auth for a scenario by tagging it `@noauth` and overriding the `storageState` fixture to return
an empty state when the tag is present:
```ts
export const test = base.extend({
  storageState: async ({ $tags, storageState }, use) => {
    await use($tags.includes('@noauth') ? { cookies: [], origins: [] } : storageState);
  },
});
```

**Dynamic (per-user, Playwright ≥1.59):** pre-save one state file per user in setup, then load inside
a step with `context.setStorageState()`:
```ts
Given('I am logged in as {string}', async ({ context }, userName: string) => {
  await context.setStorageState(AUTH_FILE.replace('{user}', userName));
});
```

## Reporters

Use any Playwright reporter on generated specs. playwright-bdd adds Cucumber reporters via
`cucumberReporter()`:
```ts
import { defineBddConfig, cucumberReporter } from 'playwright-bdd';
export default defineConfig({
  testDir,
  reporter: [
    ['html'],                                                                  // Playwright HTML
    cucumberReporter('html', { outputFile: 'cucumber-report/index.html' }),    // Cucumber HTML
    cucumberReporter('json', { outputFile: 'cucumber-report/report.json' }),   // Cucumber JSON
  ],
});
```
Notable options: `skipAttachments` (`true` or list like `['image/png','video/webm','application/zip']`;
JSON defaults to `true`), `externalAttachments` + `attachmentsBaseURL` (write attachments to a `data/`
dir), `addProjectToFeatureName`, `addMetadata`. Allure is also supported (see docs). BDD steps show
up as real Playwright steps in traces and the HTML report.

## UI mode & watch

Generated files must be regenerated on change, so pair a `bddgen` watcher with `--ui`:
```jsonc
// package.json
"scripts": {
  "watch:bdd": "npx nodemon -w ./features -e feature,js,ts --exec \"npx bddgen\"",
  "watch:pw":  "npx playwright test --ui",
  "watch":     "run-p watch:*"        // npm-run-all
}
```
`npm run watch` runs both; edits to `.feature`/step files regenerate, and UI mode picks them up. The
VS Code Playwright extension, breakpoints on BDD steps, and single-test runs all work because the
artifacts are ordinary spec files.

## Agent skill, AI fix, ESM

- **Agent skill** — `npx skills add vitalets/playwright-bdd` installs a skill (Claude Code, Copilot,
  Cursor, Cline, Windsurf) that plans scenarios, generates features + step defs grounded in your
  actual steps (`bddgen export`), and verifies by running them.
- **AI fix** (v8.1+) — `aiFix: { promptAttachment: true }` attaches a fix-ready prompt to each failed
  test: error, scenario steps, code snippet, and an **ARIA snapshot** of the page. The Playwright HTML
  report shows a copy button; the Cucumber HTML report can copy + open ChatGPT directly. Customize
  with `promptTemplate` (placeholders `{scenarioName}`, `{steps}`, `{error}`, `{snippet}`,
  `{ariaSnapshot}`). For multi-page scenarios, set the page the prompt snapshots via the `$prompt`
  fixture: `$prompt.setPage(newPage)`.
- **Component tests** — **not supported yet** (works only in trivial cases; components must be bundled
  client-side and non-JS imports stripped from steps). Recommended instead: serve component variants
  via **Storybook** and run playwright-bdd against those.
- **ESM** — supported; see the ESM config guide. Mixed CJS/ESM step files are allowed via the
  `steps` glob extensions.

## Gotchas

- **Always `bddgen` before `playwright test`.** Stale generated specs = stale tests. Make it one npm
  script / CI step.
- **Never edit generated files** in `.features-gen/` — they're overwritten every run. Don't use
  `test.use()`; configure via tags + fixtures.
- **Gitignore the generated *specs*, not the whole dir**: `**/.features-gen/**/*.spec.js` — ignoring
  the entire folder would also drop committed visual snapshots stored beside them. (Alternatively move
  snapshots out with `snapshotPathTemplate` and ignore the whole dir.)
- **Env vars + the `&&` chain:** `USERNAME=foo npx bddgen && npx playwright test` sets the var for
  `bddgen` only. Wrap the chain in an npm script and run `USERNAME=foo npm test`, or use
  `cross-env-shell`. Load `.env` with `import 'dotenv/config'` at the top of the config.
- **ESLint `no-empty-pattern`:** a step with no fixtures still needs `async ({}, arg) => {}`
  (Playwright requires the destructure). Disable that rule for step files.
- **`@mode:*` is feature/outline-level only** — it can't go on a single scenario.
- **Worker hooks have no World** (World is per-test). Use worker-scoped fixtures / `$workerInfo`.
- **Unique `outputDir` per `defineBddConfig`** when you have multiple BDD projects, or they clobber
  each other.
- **This is not CucumberJS** — no `cucumber.js` profile, no `setWorldConstructor`; the runner is
  Playwright, so timeouts, retries, parallelism, and reporters come from `playwright.config`.
- **Run the suite against a production build, not a dev server (default to prod).** Configure
  `playwright.config`'s `webServer` to build + serve (`next build && next start`, or your framework's
  equivalent) — *not* the dev server. A dev server compiles each route on first request (seconds
  each), so under parallel e2e load the first hit to a heavy route flakes with
  `page.goto: Timeout … exceeded`. A prod build serves precompiled routes instantly and
  deterministically. Keep a dev-server option behind an opt-in env var (e.g. `E2E_DEV_SERVER=1`) for
  fast single-test local iteration only — never as the default or in CI. Corollary: a reused
  long-running prod server (`reuseExistingServer: true`) serves a *stale bundle* — app-code edits
  (components/lib) won't appear until you rebuild/restart it, though test-code edits (steps/features)
  are picked up live by `bddgen` + the runner. After changing app code, restart the server before
  trusting an e2e result.
