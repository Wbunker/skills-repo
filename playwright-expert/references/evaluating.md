# Evaluating JavaScript in the Page

Run JavaScript **inside the browser page** with `evaluate`. The function is serialized, shipped to the
browser, and executed there — it has no access to your Node/test scope, so pass data explicitly.

## Contents
- [page.evaluate](#pageevaluate)
- [Passing arguments](#passing-arguments)
- [evaluate vs evaluateHandle](#evaluate-vs-evaluatehandle)
- [JSHandle & ElementHandle](#jshandle--elementhandle)
- [Handles vs locators](#handles-vs-locators)
- [locator.evaluate / evaluateAll](#locatorevaluate--evaluateall)
- [addInitScript](#addinitscript)
- [waitForFunction](#waitforfunction)
- [addScriptTag / addStyleTag](#addscripttag--addstyletag)
- [exposeFunction / exposeBinding](#exposefunction--exposebinding)

## page.evaluate

```typescript
const href = await page.evaluate(() => document.location.href);
const dims = await page.evaluate(() => ({ w: window.innerWidth, h: window.innerHeight }));
```

The callback runs in the **browser**, not Node — closures over test variables don't work:

```typescript
// WRONG — `data` doesn't exist in the browser context
await page.evaluate(() => { window.myApp.use(data); });

// CORRECT — pass it as the argument
await page.evaluate(data => { window.myApp.use(data); }, data);
```

Return values must be **JSON-serializable** (or `undefined`); DOM nodes and functions can't cross back
— use a handle for those (below).

## Passing arguments

A single arg (serializable value or a handle). Destructure to pass several:

```typescript
await page.evaluate(
  ({ button1, button2 }) => button1.textContent + button2.textContent,
  { button1, button2 },   // these can be ElementHandles
);
```

## evaluate vs evaluateHandle

- `evaluate(fn)` → returns the **serialized value**.
- `evaluateHandle(fn)` → returns a **JSHandle** (or **ElementHandle** for DOM nodes) — an in-browser
  reference you can pass back into later `evaluate` calls. Use it for non-serializable objects.

```typescript
const handle = await page.evaluateHandle(() => window);
await page.evaluate(w => w.location.href, handle);
await handle.dispose();   // free it when done
```

> Prefer **[locators](locators.md)** for finding/acting on elements; reach for `evaluate`/handles only
> when you need to run page logic or read values the DOM API exposes but locators don't.

## JSHandle & ElementHandle

A **JSHandle** is an in-browser reference to any JS object; an **ElementHandle** (a JSHandle subclass)
points to a DOM node. Read into them without a full `evaluate`:

```typescript
const handle = await page.evaluateHandle(() => ({ window, document }));
const props = await handle.getProperties();        // Map<string, JSHandle>
const win = props.get('window');
const docHandle = await handle.getProperty('document');

const arrHandle = await page.evaluateHandle(() => [1, 2, 3]);
const arr = await arrHandle.jsonValue();           // serialize back to Node: [1,2,3]
const asEl = arrHandle.asElement();                 // ElementHandle if it's a DOM node, else null
await arrHandle.dispose();                          // release (handles block GC until disposed)
```

`JSHandle` also has `evaluate(fn)` / `evaluateHandle(fn)` (run a function with the handle as arg).

**ElementHandle is discouraged** — get one only when you must (`page.$(selector)` /
`page.waitForSelector(selector)`), and prefer locators otherwise:

```typescript
const el = await page.waitForSelector('#node');     // ElementHandle (discouraged)
await el.click();
```

Beyond actions, an ElementHandle offers `boundingBox()`, `$()` / `$$()`, `$eval()` / `$$eval()`,
`contentFrame()` / `ownerFrame()`, `waitForElementState()`, and `selectText()` — all with Locator
equivalents you should prefer.

## Handles vs locators

> "The difference between the Locator and ElementHandle is that the latter points to a particular
> element, while Locator captures the logic of how to retrieve that element."

| | ElementHandle | Locator |
|---|---|---|
| Binds to | one resolved DOM node | a *query* re-run on each use |
| Stale after DOM changes | yes (points at a detached node) | no (re-resolves) |
| Auto-wait / retry | no | yes |
| Recommended | rarely (static DOM, bulk traversal) | **default for all actions/assertions** |

Use a locator for everything user-facing; reserve handles for passing live objects into `evaluate`.
See [locators.md](locators.md).

## locator.evaluate / evaluateAll

Run a function with the located element(s) as argument:

```typescript
// single element
const tag = await page.getByRole('button').evaluate(el => el.tagName);

// all matches → array
const widths = await page.getByRole('listitem')
  .evaluateAll(els => els.map(e => e.clientWidth));
```

## addInitScript

Inject code that runs **before any page script**, on every navigation in the context — ideal for
seeding globals or stubbing browser APIs (see [network.md](network.md#mocking-browser-apis)):

```typescript
await page.addInitScript(value => { Math.random = () => value; }, 42);
await page.addInitScript({ path: './preload.js' });   // from a file
```

## waitForFunction

Poll a JS predicate in the page until it returns truthy — for conditions no web-first assertion
covers (prefer [assertions](assertions.md) when one does):

```typescript
await page.waitForFunction(() => window.__appReady === true);
await page.waitForFunction(sel => document.querySelectorAll(sel).length > 3, '.row');
const handle = await page.waitForFunction(() => window.scrollY > 1000);  // returns a JSHandle
```

## addScriptTag / addStyleTag

Inject a `<script>` or `<style>`/`<link>` into the page (content, `url`, or `path`) — e.g. to load a
helper lib or override CSS during a test:

```typescript
await page.addScriptTag({ url: 'https://cdn.example.com/lib.js' });
await page.addScriptTag({ content: 'window.__patched = true;' });
await page.addStyleTag({ content: '* { animation: none !important; }' });
```

## exposeFunction / exposeBinding

Expose a **Node** function to page scripts (the inverse of `evaluate`) — the page calls it, it runs in
Node, and returns a value to the page:

```typescript
await page.exposeFunction('sha256', (text: string) =>
  crypto.createHash('sha256').update(text).digest('hex'));

await page.evaluate(async () => {
  document.querySelector('#out')!.textContent = await (window as any).sha256('hello');
});
```

`exposeBinding` is the same but the callback also receives a `{ page, frame, context }` source object
(and, with `{ handle: true }`, a handle to the passed element). Bindings persist across navigations.
