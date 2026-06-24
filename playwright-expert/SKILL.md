---
name: playwright-expert
description: Playwright end-to-end testing expertise covering test authoring (locators, actions, web-first assertions, Page Object Model), the fixtures system (custom/test-scoped/worker-scoped/auto/option fixtures, dependencies, boxing), authentication that is saved once and reused across tests (storageState, setup projects, multi-role, per-worker auth), running and debugging tests (UI mode, Inspector, codegen, trace viewer), BDD/Cucumber/Gherkin testing via playwright-bdd (defineBddConfig, bddgen, .feature files, step definitions), and the Playwright agent-cli (playwright-cli) for driving a browser from the shell including the "save login, skip it next time" workflow. Use when writing or debugging Playwright tests, choosing locators, structuring test suites with fixtures, persisting/reusing logins across tests or CLI sessions, setting up playwright.config.ts, writing Gherkin/Cucumber BDD tests with playwright-bdd, or automating a browser with the agent-cli.
---

# Playwright Expert

Playwright is a cross-browser (Chromium, Firefox, WebKit) end-to-end testing and browser-automation
framework. Tests are written in TypeScript/JavaScript (also Python, Java, .NET) and run fully
isolated, in parallel, with auto-waiting built in.

Two distinct surfaces, often confused:
- **`@playwright/test`** — the test runner. You write `*.spec.ts` files and run `npx playwright test`.
- **`playwright-cli`** (agent-cli) — a shell tool that drives a live browser one command at a time
  (`open`, `fill`, `click`, `snapshot`, `state-save`). Built for AI agents / interactive automation,
  not the test runner. See [agent-cli.md](references/agent-cli.md).

## Quick Start (test runner)

```bash
npm init playwright@latest          # scaffold: config, tests/, GitHub Actions, browsers
npx playwright install --with-deps  # (re)install browsers + OS deps
npx playwright test                 # run all tests, headless, across all browsers
npx playwright test --ui            # interactive UI mode (recommended while developing)
npx playwright show-report          # open the last HTML report
```

A first test (`tests/example.spec.ts`):
```typescript
import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
  await page.goto('https://playwright.dev/');
  await expect(page).toHaveTitle(/Playwright/);
});
```

`{ page }` is a built-in **fixture** — Playwright sets up a fresh, isolated browser page per test.
Fixtures are the core abstraction for setup/teardown; see [fixtures.md](references/fixtures.md).

## Quick Reference

**Authoring**
| Task | Reference |
|------|-----------|
| Test structure, the three pillars, isolation, Page Object Model | [writing-tests.md](references/writing-tests.md) |
| Locators — all engines, filtering, chaining, lists, strictness | [locators.md](references/locators.md) |
| Actions — input, mouse/keyboard, files, dialogs, downloads, frames, clock | [actions.md](references/actions.md) |
| DnD libraries — testing react-beautiful-dnd / @hello-pangea/dnd / dnd-kit (keyboard sensor, stepped-mouse fallback, tree limits) | [dnd-libraries.md](references/dnd-libraries.md) |
| Assertions — web-first matchers, soft/poll/toPass, custom, aria snapshots | [assertions.md](references/assertions.md) |
| Events — `on`/`once`/`off`/`waitForEvent`, catalog, pages/tabs/popups | [events.md](references/events.md) |
| Evaluating JS — `page.evaluate`, handles, `exposeFunction`/`Binding` | [evaluating.md](references/evaluating.md) |
| Fixtures — custom, scopes, auto, option, dependencies, boxing | [fixtures.md](references/fixtures.md) |
| Organization — describe/steps/tags/annotations, parameterization, retries | [test-organization.md](references/test-organization.md) |
| Best practices — philosophy, locators, isolation, CI (start here) | [best-practices.md](references/best-practices.md) |

**Capabilities**
| Task | Reference |
|------|-----------|
| Save login once, reuse across tests (storageState, roles, passkeys, WebStorage) | [auth.md](references/auth.md) |
| Network — routing/mocking, HAR record+replay, API testing, WebSockets | [network.md](references/network.md) |
| Emulation — devices, geolocation, permissions, locale, timezone, media | [emulation.md](references/emulation.md) |
| Visual testing — screenshots, snapshot diffs, video recording | [visual-comparisons.md](references/visual-comparisons.md) |
| Accessibility testing (`@axe-core/playwright`) | [accessibility.md](references/accessibility.md) |
| Component testing (experimental) | [components.md](references/components.md) |
| BDD / Cucumber / Gherkin on the Playwright runner (`playwright-bdd`, `bddgen`) | [playwright-bdd.md](references/playwright-bdd.md) |
| Chrome extension testing (persistent context) | [chrome-extensions.md](references/chrome-extensions.md) |
| AI Test Agents — planner/generator/healer (`init-agents --loop=claude`) | [test-agents.md](references/test-agents.md) |

**Config, tooling & debugging**
| Task | Reference |
|------|-----------|
| Full `playwright.config` — projects, parallelism, sharding, timeouts, reporters | [test-config.md](references/test-config.md) |
| Install, run, CI, Docker | [tooling.md](references/tooling.md) |
| Interactive debugging — UI mode, Inspector, codegen, `--debug=cli`, dashboard | [debugging.md](references/debugging.md) |
| Post-failure debugging — Trace Viewer (modes, panels) | [trace-viewer.md](references/trace-viewer.md) |
| Screencast API — annotated videos & frame streams | [screencast.md](references/screencast.md) |
| Library API — Playwright without the test runner | [library-api.md](references/library-api.md) |
| agent-cli (`playwright-cli`) — full command surface + save-login workflow | [agent-cli.md](references/agent-cli.md) |
| What changed in v1.59 / v1.60 / v1.61 | [whats-new.md](references/whats-new.md) |

## Core Guidance

### Locator selection (best → last resort)
Prefer user-facing, resilient locators. Full details in [writing-tests.md](references/writing-tests.md).
```
1. getByRole(role, { name })   — closest to how users/AT perceive the page
2. getByText / getByLabel / getByPlaceholder / getByAltText / getByTitle
3. getByTestId('...')          — explicit test contract (data-testid)
4. CSS / XPath                 — fragile, only when nothing above works
```

### Always use web-first assertions
Async `expect(locator).toBeVisible()` / `toHaveText()` auto-retry until the condition holds or
times out. Never `await locator.isVisible()` then assert the boolean — that doesn't retry and is
flaky. Reserve sync matchers (`toEqual`, `toContain`) for plain values.

### Don't repeat logins — save auth state
Authenticating in every test is slow and flaky. Sign in **once**, persist `storageState` (cookies +
localStorage + IndexedDB), and have every test start already logged in. This is the single biggest
reliability/speed win for authenticated apps — see [auth.md](references/auth.md). The agent-cli has
the equivalent `state-save` / `state-load` workflow — see [agent-cli.md](references/agent-cli.md).

### Debug failures with traces, not console.log
When a test fails (especially on CI), open its **trace** — a full replay with before/after DOM
snapshots, a screenshot film-strip, network, console, and the failing source line. Keep
`trace: 'on-first-retry'` in config, then `npx playwright show-trace trace.zip` (or drag it onto
<https://trace.playwright.dev>). This is the primary debugging tool — see
[trace-viewer.md](references/trace-viewer.md).

### Reach for fixtures over `beforeEach`
Fixtures are **lazy** (only run when a test names them) and **dependency-injected**, whereas a
`beforeEach` runs for every test in the file whether needed or not. Use fixtures for page objects,
seeded data, auth contexts, and network mocks. Put expensive shared setup in **worker-scoped**
fixtures, per-test isolation in **test-scoped** ones. See [fixtures.md](references/fixtures.md).

## Gotchas

- **Locators are strict**: an action throws if the locator matches >1 element. Narrow with
  `.filter()` / chaining rather than `.first()`/`.nth()` (which are fragile).
- **Auth state files contain live session secrets.** Keep them in `playwright/.auth/` and git-ignore
  that directory — they can impersonate the account.
- **`trace: 'on-first-retry'`** (the default) records nothing on a passing or first run. Use
  `--trace on` to force a trace locally while debugging.
- **agent-cli ≠ test runner.** `playwright-cli fill e3 ...` uses element refs from `snapshot`; it
  does not run `*.spec.ts`. Don't mix the two command models.
- **`npx playwright codegen --save-storage=auth.json`** records *and* persists login so you can
  resume authenticated with `--load-storage=auth.json` — the recording-time analog of storageState.
- Web-first `expect` matchers must be `await`ed; forgetting `await` silently passes.
