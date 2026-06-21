# Best Practices

The official Playwright recommendations, consolidated. Each links to the reference with the mechanics.

## Contents
- [Testing philosophy](#testing-philosophy)
- [Locators](#locators)
- [Web-first assertions](#web-first-assertions)
- [Tooling & debugging](#tooling--debugging)
- [Configuration](#configuration)
- [CI & scale](#ci--scale)
- [Quick checklist](#quick-checklist)

## Testing philosophy

- **Test user-visible behavior**, not implementation details. Assert on rendered text/roles a user
  perceives — not function names, CSS classes, or internal state.
- **Isolate every test.** Each test gets its own storage/cookies/data and runs independently (no
  ordering dependencies). Use `beforeEach`/[fixtures](fixtures.md) for shared setup, not shared
  *state* between tests. Playwright enforces this with per-test [contexts](writing-tests.md#test-isolation).
- **Don't test third parties.** Don't drive external sites/servers you don't control — [mock](network.md)
  their responses so data is deterministic.
- **Control test data.** Run against a known staging dataset or seed via the [API](network.md#api-testing-request-fixture);
  pin OS/browser versions for [visual comparisons](visual-comparisons.md).

## Locators

- Prefer **user-facing, role-based** locators (`getByRole`, `getByText`, `getByLabel`) over
  CSS/XPath tied to DOM structure — they survive refactors and mirror accessibility. Full
  hierarchy and rules: [locators.md](locators.md).
- **Chain and filter** to narrow scope instead of brittle `.nth()`:
  ```javascript
  const product = page.getByRole('listitem').filter({ hasText: 'Product 2' });
  ```
- **Generate** resilient locators with codegen or the VS Code "Pick locator" tool —
  see [debugging.md](debugging.md#codegen).

## Web-first assertions

- Use auto-retrying matchers (`await expect(locator).toBeVisible()`) — they wait until the condition
  holds, removing flakiness. Never `isVisible()` + a manual assert. Full list: [assertions.md](assertions.md).
- Use [soft assertions](assertions.md) (`expect.soft`) to collect multiple failures in one run when
  the test should keep going.

## Tooling & debugging

- Debug locally with **UI Mode** (`--ui`), the **VS Code extension**, and `--debug`
  ([debugging.md](debugging.md)).
- On CI, rely on **traces** (`trace: 'on-first-retry'`) over screenshots/video — full time-travel
  post-mortem ([trace-viewer.md](trace-viewer.md)).
- Lean on codegen, the trace viewer, and TypeScript support.

## Configuration

- Set `use.baseURL` so tests use relative `page.goto('/path')` ([test-config.md](test-config.md)).
- Test across **all three engines** (Chromium/Firefox/WebKit) via [projects](test-config.md#projects).
- **Lint** for missing `await`s: ESLint + `@typescript-eslint/no-floating-promises` (the most common
  Playwright bug is an un-awaited assertion — see the gotcha in [SKILL](../SKILL.md)).

## CI & scale

- Run tests on every PR/commit; prefer Linux runners for cost.
- Install only the browsers you need: `npx playwright install chromium --with-deps`.
- Keep Playwright current: `npm install -D @playwright/test@latest` (then re-run `install`).
- Use built-in **parallelism** and **[sharding](test-config.md#sharding)** (`--shard`) for speed.

## Quick checklist

```
☐ Assertions are web-first and awaited
☐ Locators are role/text/label-based, not CSS/XPath
☐ Tests are isolated — no shared state, any order
☐ Third-party calls are mocked; data is deterministic
☐ baseURL set; runs on chromium + firefox + webkit
☐ trace: 'on-first-retry'; traces uploaded as CI artifacts
☐ ESLint no-floating-promises enabled
☐ Auth done once via storageState, not per test
☐ Parallel locally; sharded on CI
```
