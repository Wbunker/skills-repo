# Events

Pages, contexts, browsers, and workers emit events (network, dialogs, popups, downloads, …). Two
ways to consume them: **subscribe** with `on`/`once`, or **wait** for the next one with `waitForEvent`.

## Contents
- [Subscribe: on / once / off](#subscribe-on--once--off)
- [Wait: waitForEvent](#wait-waitforevent)
- [Start the wait before the action](#start-the-wait-before-the-action)
- [Event catalog](#event-catalog)
- [New pages, tabs & popups](#new-pages-tabs--popups)

## Subscribe: on / once / off

```typescript
// every occurrence
page.on('console', msg => console.log(msg.text()));

// just the next one
page.once('dialog', dialog => dialog.accept());

// stop listening (pass the same function reference)
const onResponse = (r: Response) => console.log(r.url());
page.on('response', onResponse);
page.off('response', onResponse);
```

Handlers may be async, but the emitter does **not** await them — don't rely on a handler finishing
before the next line. For ordered, awaited handling, prefer `waitForEvent`.

## Wait: waitForEvent

Returns a promise for the **next** matching event; accepts a predicate to filter:

```typescript
const popup = await page.waitForEvent('popup');
const download = await page.waitForEvent('download');

// predicate — wait for a specific one
const response = await page.waitForEvent('response',
  r => r.url().includes('/api/data') && r.status() === 200);
```

Network has dedicated sugar: `page.waitForRequest(urlOrPredicate)` /
`page.waitForResponse(urlOrPredicate)` (see [network.md](network.md)).

## Start the wait before the action

The event can fire before `await` resolves, so **create the wait promise first, then trigger**, then
await — otherwise you race and miss it:

```typescript
const downloadPromise = page.waitForEvent('download');   // 1. arm
await page.getByText('Download').click();                 // 2. trigger
const download = await downloadPromise;                   // 3. collect
```

## Event catalog

Common `page` events (contexts emit many equivalents, e.g. `context.on('page')`):

| Event | Fires when | See |
|-------|-----------|-----|
| `console` | Page calls `console.*` | [debugging.md](debugging.md) |
| `dialog` | `alert`/`confirm`/`prompt`/`beforeunload` opens | [actions.md](actions.md#dialogs) |
| `download` | A download starts | [actions.md](actions.md#downloads) |
| `filechooser` | A file input is activated | [actions.md](actions.md#file-uploads) |
| `popup` | A new page is opened by this page (e.g. `window.open`) | — |
| `request` / `response` / `requestfinished` | Network lifecycle | [network.md](network.md) |
| `requestfailed` | A request fails | [network.md](network.md) |
| `websocket` | A WebSocket is created | [network.md](network.md) |
| `worker` | A dedicated web worker starts | — |
| `pageerror` | An uncaught exception in the page | [debugging.md](debugging.md) |
| `crash` | The page crashes (OOM, etc.) | — |
| `close` | The page closes | — |
| `framenavigated` / `frameattached` / `framedetached` | Frame lifecycle | [actions.md](actions.md#frames--iframes) |

> To snapshot recent activity without listeners, use `page.consoleMessages()` / `page.pageErrors()` /
> `page.requests()` (v1.56+) — see [debugging.md](debugging.md).

## New pages, tabs & popups

A context can hold many pages (tabs). Pages opened by the app — `window.open`, a `target="_blank"`
link — arrive as events, not return values. Arm the wait **before** the click.

```typescript
// popup opened by THIS page (window.open / target=_blank from a link on the page)
const popupPromise = page.waitForEvent('popup');
await page.getByText('open the popup').click();
const popup = await popupPromise;
await popup.waitForLoadState();
console.log(await popup.title());
```

```typescript
// any new page in the CONTEXT (e.g. opened by a different page)
const pagePromise = context.waitForEvent('page');
await page.getByText('open new tab').click();
const newPage = await pagePromise;
await newPage.waitForLoadState();
```

```typescript
// listen continuously for every new page
context.on('page', async p => {
  await p.waitForLoadState();
  console.log(await p.title());
});
```

Enumerate open pages and switch focus:
```typescript
const all = context.pages();      // array of live pages in the context
await all[1].bringToFront();      // raise a background tab (rarely needed — pages work in background)
```

A `Page` is a single tab/popup within a [BrowserContext](library-api.md#browser-contexts); each is
independent and works without being foregrounded.
