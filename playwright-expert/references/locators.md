# Locators

The authoritative deep dive on Playwright locators: how they work, the recommended hierarchy, every `getBy*` method, raw engines (CSS/XPath/text/id/layout), filtering, chaining, operators, list handling, and strictness. See [writing-tests.md](writing-tests.md) for the overview and [actions.md](actions.md) for what you do with a located element.

## Contents

- [What a locator is](#what-a-locator-is)
- [Recommended hierarchy](#recommended-hierarchy)
- [getByRole](#getbyrole)
- [getByText](#getbytext)
- [getByLabel](#getbylabel)
- [getByPlaceholder](#getbyplaceholder)
- [getByAltText](#getbyalttext)
- [getByTitle](#getbytitle)
- [getByTestId and testIdAttribute](#getbytestid-and-testidattribute)
- [CSS and XPath](#css-and-xpath)
- [Other engines: text, id](#other-engines-text-id)
- [CSS pseudo-classes: :has-text, :text, :has, :visible, :scope](#css-pseudo-classes)
- [Layout selectors](#layout-selectors)
- [N-th element and :nth-match](#n-th-element-and-nth-match)
- [Filtering](#filtering)
- [Chaining](#chaining)
- [Operators: and, or, first, last, nth](#operators-and-or-first-last-nth)
- [Working with lists](#working-with-lists)
- [Strictness](#strictness)
- [Shadow DOM](#shadow-dom)
- [Reading values & state](#reading-values--state)
- [Custom selector engines](#custom-selector-engines)
- [Locator tooling: pickLocator and normalize](#locator-tooling)

## What a locator is

A locator is a **lazy, re-evaluated** description of how to find element(s) — not a captured element handle. It is created without touching the DOM; the query runs fresh on every action/assertion, which is what gives Playwright auto-waiting and retry-ability.

Three defining properties:
- **Lazy** — `page.getByRole(...)` does nothing until an action/assertion consumes it.
- **Auto-retrying** — every action re-resolves the locator and waits for the element to be actionable.
- **Strict** — a single-element action throws if the locator matches more than one element (see [Strictness](#strictness)).

```typescript
const locator = page.getByRole('button', { name: 'Sign in' });
await locator.click();
```

## Recommended hierarchy

Prefer user-facing, accessibility-backed locators (resilient to DOM churn). In priority order:

1. `page.getByRole()` — accessibility role + accessible name (best default)
2. `page.getByText()` — visible text content
3. `page.getByLabel()` — form controls by their label
4. `page.getByPlaceholder()` — inputs without a label
5. `page.getByAltText()` — images / elements with alt text
6. `page.getByTitle()` — elements with a `title` attribute
7. `page.getByTestId()` — explicit `data-testid`, when nothing user-facing fits

Drop to CSS/XPath only when no `getBy*` works.

## getByRole

```typescript
page.getByRole(role: string, options?: {
  name?: string | RegExp,
  exact?: boolean,        // exact match for `name` (case-sensitive, full string); ignored for RegExp
  checked?: boolean,
  disabled?: boolean,
  expanded?: boolean,
  level?: number,         // heading level h1..h6, etc.
  pressed?: boolean,
  selected?: boolean,
  description?: string | RegExp   // (v1.60+) matches the accessible description
})
```

```typescript
await page.getByRole('button', { name: 'Sign in' }).click();
await page.getByRole('checkbox', { name: 'Subscribe' }).check();
await page.getByRole('heading', { name: 'Sign up', level: 1 });
```

- `name` matches the **accessible name** (substring + case-insensitive by default; pass `exact: true` for full case-sensitive match).
- `description` (v1.60+) matches the [accessible description](https://www.w3.org/TR/wai-aria-1.2/#dfn-accessible-description) — also available on `locator.getByRole`, `frame.getByRole`, `frameLocator.getByRole`.

## getByText

```typescript
page.getByText(text: string | RegExp, options?: { exact?: boolean })
```

```typescript
await expect(page.getByText('Welcome, John')).toBeVisible();          // substring, case-insensitive, whitespace-normalized
await expect(page.getByText('Welcome, John', { exact: true })).toBeVisible(); // exact, case-sensitive
await expect(page.getByText(/welcome, [A-Za-z]+$/i)).toBeVisible();   // regex
```

Match text for assertions/locating; for clicking prefer a role-based locator unless the element is a non-interactive text node. `exact` is ignored when a RegExp is passed.

## getByLabel

```typescript
page.getByLabel(text: string | RegExp, options?: { exact?: boolean })
```

```typescript
await page.getByLabel('Password').fill('secret');
await page.getByLabel('User Name').fill('John');
```

Resolves to the control associated with the label, not the `<label>` element itself.

## getByPlaceholder

```typescript
page.getByPlaceholder(text: string | RegExp, options?: { exact?: boolean })
```

```typescript
await page.getByPlaceholder('name@example.com').fill('playwright@microsoft.com');
```

## getByAltText

```typescript
page.getByAltText(text: string | RegExp, options?: { exact?: boolean })
```

```typescript
await page.getByAltText('playwright logo').click();
```

## getByTitle

```typescript
page.getByTitle(text: string | RegExp, options?: { exact?: boolean })
```

```typescript
await expect(page.getByTitle('Issues count')).toHaveText('25 issues');
```

## getByTestId and testIdAttribute

```typescript
page.getByTestId(testId: string | RegExp)
```

```typescript
await page.getByTestId('directions').click();
```

Default attribute is `data-testid`. Reconfigure globally:

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    testIdAttribute: 'data-pw',
  },
});
```

Or programmatically (Library API):

```typescript
await selectors.setTestIdAttribute('data-pw');
```

## CSS and XPath

```typescript
page.locator(selector: string, options?: { has?: Locator, hasNot?: Locator, hasText?: string | RegExp, hasNotText?: string | RegExp })
```

```typescript
await page.locator('css=button').click();
await page.locator('xpath=//button').click();
await page.locator('button').click();   // auto-detected as CSS
await page.locator('//button').click(); // string starting with // or .. is auto-detected as XPath
```

XPath does **not** pierce shadow DOM; all `getBy*` and CSS locators do (open shadow roots only).

## Other engines: text, id

```typescript
// Legacy text engine (prefer getByText)
await page.locator('text=Log in').click();
await page.locator('text="Log in"').click();   // quotes => exact match
await page.locator('text=/Log\\s*in/i').click(); // regex

// id / data attribute engines
await page.locator('id=username').fill('value');
await page.locator('data-test-id=submit').click();
```

> **Removed (v1.58):** the `react=` / `vue=` component selectors and the `:light` selector-engine
> suffix were removed — use standard role/text/CSS locators instead. For component-level testing use
> [components.md](components.md).

## CSS pseudo-classes

Playwright extends CSS with text and structural pseudo-classes:

```typescript
// :has-text() — element whose subtree contains the text (substring)
await page.locator('article:has-text("Playwright")').click();

// :text() — smallest element containing the text
await page.locator('#nav-bar :text("Home")').click();

// :text-is() — exact text match (case-sensitive)
await page.locator('#nav-bar :text-is("Home")').click();

// :text-matches() — regex with flags
await page.locator('#nav-bar :text-matches("reg?ex", "i")').click();

// :visible — only visible elements
await page.locator('button:visible').click();

// :has() — element containing another element
await page.locator('article:has(div.promo)').textContent();

// Multiple conditions via comma (CSS union)
await page.locator('button:has-text("Log in"), button:has-text("Sign in")').click();
```

`:scope` and `*` capture: use `*css=` to capture an intermediate match rather than the final node (see [Chaining](#chaining)).

## Layout selectors

Match by on-screen position relative to another element. Accuracy depends on rendered layout — use sparingly.

```typescript
await page.locator('input:right-of(:text("Username"))').fill('value');
await page.locator('[type=radio]:left-of(:text("Label 3"))').first().click();
await page.locator('button:near(.promo-card)').click();
await page.locator('button:near(:text("Username"), 120)').click(); // max distance in px
```

Available: `:right-of()`, `:left-of()`, `:above()`, `:below()`, `:near()`.

## N-th element and :nth-match

```typescript
// 0-based; negative counts from the end
await page.locator('button').locator('nth=0').click();
await page.locator('button').locator('nth=-1').click();

// :nth-match selects the N-th (1-based) match of a selector across the page
await page.locator(':nth-match(:text("Buy"), 3)').click();
await page.locator(':nth-match(:text("Buy"), 3)').waitFor();
```

Prefer the `.nth()` / `.first()` / `.last()` operators over `nth=` when possible (see below).

## Filtering

```typescript
locator.filter(options: {
  hasText?: string | RegExp,
  hasNotText?: string | RegExp,
  has?: Locator,
  hasNot?: Locator,
  visible?: boolean,
})
```

```typescript
// by text inside the element
await page.getByRole('listitem')
  .filter({ hasText: 'Product 2' })
  .getByRole('button', { name: 'Add to cart' })
  .click();

// negation
await expect(page.getByRole('listitem').filter({ hasNotText: 'Out of stock' }))
  .toHaveCount(5);

// by a descendant locator
await page.getByRole('listitem')
  .filter({ has: page.getByRole('heading', { name: 'Product 2' }) })
  .getByRole('button', { name: 'Add to cart' })
  .click();

// by absence of a descendant
await expect(page.getByRole('listitem')
  .filter({ hasNot: page.getByText('Product 2') }))
  .toHaveCount(1);

// only visible matches
await page.locator('button').filter({ visible: true }).click();
```

`has`/`hasNot` locators are resolved relative to the same root, so they must point at the element itself or a descendant.

## Chaining

Each `getBy*`/`locator` call on an existing locator narrows the search to that element's subtree:

```typescript
const product = page.getByRole('listitem').filter({ hasText: 'Product 2' });
await product.getByRole('button', { name: 'Add to cart' }).click();

const dialog = page.getByTestId('settings-dialog');
await dialog.locator(saveButton).click();
```

Raw selectors chain with `>>`; prefix a step with `*` to make it the captured (returned) match instead of the last step:

```
css=article >> css=.bar > .baz >> css=span[attr=value]
*css=article >> text=Hello
```

Select a parent via `filter({ has })` or XPath axis:

```typescript
const child = page.getByText('Hello');
const parent = page.getByRole('listitem').filter({ has: child });
// or
const parent2 = page.getByText('Hello').locator('xpath=..');
```

## Operators: and, or, first, last, nth

```typescript
locator.and(other: Locator)   // element must match BOTH
locator.or(other: Locator)    // element matching EITHER
locator.first()
locator.last()
locator.nth(index: number)    // 0-based
```

```typescript
const button = page.getByRole('button').and(page.getByTitle('Subscribe'));

// handle "either dialog or button appears"
const newEmail = page.getByRole('button', { name: 'New' });
const dialog = page.getByText('Confirm security settings');
await expect(newEmail.or(dialog).first()).toBeVisible();

const banana = page.getByRole('listitem').nth(1);
```

## Working with lists

```typescript
// count
await expect(page.getByRole('listitem')).toHaveCount(3);

// assert exact ordered text of all matches (array form)
await expect(page.getByRole('listitem'))
  .toHaveText(['apple', 'banana', 'orange']);

// iterate snapshot of matches
for (const row of await page.getByRole('listitem').all())
  console.log(await row.textContent());

// iterate by index
const rows = page.getByRole('listitem');
const count = await rows.count();
for (let i = 0; i < count; ++i)
  console.log(await rows.nth(i).textContent());

// evaluate all matched DOM nodes in page context
const texts = await rows.evaluateAll(
  list => list.map(element => element.textContent),
);
```

`.all()` resolves once and is not auto-retried — only use it after the list has stabilized. Prefer array assertions (`toHaveText([...])`) which auto-retry.

## Strictness

Single-element operations throw if the locator matches >1 element. Multi-element operations (`count`, `all`, array assertions) do not.

```typescript
// ❌ throws if multiple buttons exist
await page.getByRole('button').click();

// ✅ multi-element ops are fine
await page.getByRole('button').count();

// ✅ explicit disambiguation (opt out of strictness)
await page.getByRole('button').first().click();
await page.getByRole('button').last().click();
await page.getByRole('button').nth(0).click();
```

Resolve a strictness violation by making the locator more specific (better role/name, `.filter()`, chaining from a unique ancestor) rather than reaching for `.first()`.

## Shadow DOM

All built-in locators pierce **open** shadow roots by default; **XPath does not**, and **closed** roots are unsupported.

```typescript
await page.getByText('Details').click();
await page.locator('x-details', { hasText: 'Details' }).click();
await expect(page.locator('x-details')).toContainText('Details');
```

## Reading values & state

Locators have getters for pulling values out of an element. **Prefer web-first
[assertions](assertions.md)** (`toHaveText`, `toBeVisible`, …) which auto-retry — these one-shot
getters do **not** retry, so use them only for branching logic, not for waiting:

```typescript
await loc.textContent();  await loc.innerText();  await loc.innerHTML();
await loc.getAttribute('href');  await loc.inputValue();
await loc.allInnerTexts();  await loc.allTextContents();   // arrays over all matches
const ok = await loc.isVisible();   // also isHidden/isEnabled/isDisabled/isEditable/isChecked
await loc.waitFor({ state: 'visible' });   // explicit wait: 'attached'|'detached'|'visible'|'hidden'
await loc.highlight();   // debug-only: flash the element in a headed browser
```

## Custom selector engines

Extend the selector syntax with your own engine via `selectors.register()` (Library/extensibility).
A `SelectorEngine` implements `query(root, selector)` (first match) and `queryAll(root, selector)`
(all matches). **Register before creating the page**; `{ contentScript: true }` isolates the engine
from page tampering with `Node.prototype` etc.

```typescript
// register once (worker-scoped fixture or globalSetup)
const createTagNameEngine = () => ({
  query(root, selector) { return root.querySelector(selector); },
  queryAll(root, selector) { return Array.from(root.querySelectorAll(selector)); },
});
await selectors.register('tag', createTagNameEngine, { contentScript: true });
```

```typescript
// use it like any engine — composes with built-in locators
await page.locator('tag=button').click();
await page.locator('tag=div').getByText('Click me').click();
await expect(page.locator('tag=button')).toHaveCount(3);
```

## Locator tooling

For authoring/repairing locators interactively (see [debugging.md](debugging.md)):

- **`page.pickLocator()`** (v1.59+) — enters an interactive mode where hovering highlights elements and shows the corresponding locator; click an element to get its `Locator` back. Exit with `page.cancelPickLocator()`.
- **`locator.normalize()`** (v1.59+) — converts a locator to follow best practices (test ids, ARIA roles).
- **`locator.describe('label')`** (v1.57+) — attach a human-readable description used by `locator.toString()`, trace steps, and error messages; read it back with `locator.description()`.
