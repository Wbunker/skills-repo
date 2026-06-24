# Actions & Interactions

Comprehensive reference for performing actions in Playwright: input, mouse/keyboard, uploads, drag-and-drop, dialogs, downloads, navigation, frames, actionability, and clock mocking. All actions auto-wait for [actionability](#actionability-checks) — explicit `waitFor*` is rarely needed.

## Contents

- [Text input](#text-input)
- [Checkboxes & radio](#checkboxes--radio)
- [Select options](#select-options)
- [Mouse actions](#mouse-actions)
- [page.mouse (low-level)](#pagemouse-low-level)
- [Keyboard](#keyboard)
- [page.keyboard (low-level)](#pagekeyboard-low-level)
- [Touch / tap](#touch--tap)
- [File uploads](#file-uploads)
- [Drag and drop](#drag-and-drop)
- [Dialogs](#dialogs)
- [Downloads](#downloads)
- [Navigation & auto-waiting](#navigation--auto-waiting)
- [Auto-dismissing overlays (addLocatorHandler)](#auto-dismissing-overlays-addlocatorhandler)
- [Frames & iframes](#frames--iframes)
- [Actionability checks](#actionability-checks)
- [Clock / time mocking](#clock--time-mocking)

## Text input

`fill()` focuses, clears, and sets the value in one step (fires `input`); prefer it over keyboard typing. Use `pressSequentially()` only when per-keystroke handlers (autocomplete) matter.

```typescript
// fill() — sets value directly, works for text/date/time/datetime inputs
await page.getByRole('textbox').fill('Peter');
await page.getByLabel('Birth date').fill('2020-02-02');
await page.getByLabel('Appointment time').fill('13:15');
await page.getByLabel('Local time').fill('2020-03-02T05:15');

// pressSequentially() — emits a keydown/keyup per character (autocomplete, key handlers)
await page.locator('#area').pressSequentially('Hello World!');
await page.locator('#area').pressSequentially('Hello', { delay: 100 }); // ms between keys

// clear() — empties the field
await page.getByRole('textbox').clear();
```

`fill` requires Visible + Enabled + Editable; `pressSequentially` performs no actionability checks (see [actionability](#actionability-checks)).

## Checkboxes & radio

`check()`/`uncheck()` are idempotent and assert the element is actually a checkbox/radio and ends in the target state. `setChecked(bool)` chooses based on a variable.

```typescript
await page.getByLabel('I agree to the terms above').check();
await page.getByLabel('XL').check();                 // radio
await page.getByLabel('Subscribe').uncheck();
await page.getByLabel('Subscribe').setChecked(true);

await expect(page.getByLabel('Subscribe to newsletter')).toBeChecked();
```

## Select options

`selectOption()` matches by value or label string, or `{ label }` / `{ value }` / `{ index }`, and accepts an array for `<select multiple>`. Returns the array of selected values.

```typescript
// Match by value OR label
await page.getByLabel('Choose a color').selectOption('blue');
// Match by label only
await page.getByLabel('Choose a color').selectOption({ label: 'Blue' });
// Match by index
await page.getByLabel('Choose a color').selectOption({ index: 2 });
// Multiple
await page.getByLabel('Choose multiple colors').selectOption(['red', 'green', 'blue']);
```

## Mouse actions

Locator click variants auto-scroll and wait for actionability. Coordinates in `position` are relative to the element's top-left padding box.

```typescript
await page.getByRole('button').click();
await page.getByText('Item').dblclick();
await page.getByText('Item').click({ button: 'right' });          // right click
await page.getByText('Item').click({ modifiers: ['Shift'] });     // Shift+click
await page.getByText('Item').click({ modifiers: ['ControlOrMeta'] }); // Ctrl (Win/Linux) / Meta (mac)
await page.getByText('Item').hover();
await page.getByText('Item').click({ position: { x: 0, y: 0 } }); // top-left corner
await page.getByRole('button').click({ force: true });            // skip non-essential checks
await page.getByRole('button').dispatchEvent('click');           // programmatic, no real click
await page.getByText('Footer text').scrollIntoViewIfNeeded();
```

`click()` options also include `clickCount`, `delay` (ms between down/up), `timeout`, and `steps` (v1.57+, number of intermediate mousemove events — also on `locator.dragTo()`, useful for drag-sensitive UIs). `force: true` disables hit-testing & stability checks — see [actionability](#actionability-checks).

## page.mouse (low-level)

CSS-pixel coordinates relative to the main frame viewport. Use for canvas, custom widgets, or manual drag. Prefer locator clicks otherwise.

```typescript
await page.mouse.move(x, y, { steps: 10 });           // steps interpolates intermediate moves
await page.mouse.down({ button: 'left', clickCount: 1 });
await page.mouse.up();
await page.mouse.click(x, y, { button: 'left', clickCount: 1, delay: 0 });
await page.mouse.dblclick(x, y);
await page.mouse.wheel(deltaX, deltaY);               // scroll; must hover target first
```

```typescript
// Mouse-wheel scroll within a container
await page.getByTestId('scrolling-container').hover();
await page.mouse.wheel(0, 10);
```

## Keyboard

`press()` sends a single key or chord; `pressSequentially()` (locator) types text char-by-char. Key syntax accepts logical keys (`Enter`, `ArrowLeft`), characters (`$`, `a`), `KeyA`-style codes, and `+`-joined chords.

```typescript
await page.getByText('Submit').press('Enter');
await page.getByRole('textbox').press('Control+ArrowRight');
await page.getByRole('textbox').press('$');
await page.locator('#name').press('Shift+A');
await page.locator('#name').press('Shift+ArrowLeft');
await page.locator('#area').press('ControlOrMeta+A');   // select-all, cross-platform
```

Key names: `F1`–`F12`, `Digit0`–`Digit9`, `KeyA`–`KeyZ`, `Arrow{Up,Down,Left,Right}`, `Backspace`, `Tab`, `Delete`, `Escape`, `Enter`, `Home`, `End`, `PageUp`, `PageDown`, `Insert`; modifiers `Shift`, `Control`, `Alt`, `Meta`, `ControlOrMeta`.

## page.keyboard (low-level)

For manual modifier holds and IME/text composition. Modifiers affect `down()`/`press()` but **not** `type()`/`insertText()`.

```typescript
await page.keyboard.press('Enter');
await page.keyboard.press('a', { delay: 100 });        // delay = ms between down and up
await page.keyboard.type('Hello');
await page.keyboard.type('World', { delay: 100 });
await page.keyboard.insertText('emoji 🎉');             // fires only `input`, no key events
await page.keyboard.down('Shift');
await page.keyboard.up('Shift');
```

```typescript
// Hold Shift to select then delete (manual modifier sequence)
await page.keyboard.type('Hello World!');
await page.keyboard.press('ArrowLeft');
await page.keyboard.down('Shift');
for (let i = 0; i < ' World'.length; i++)
  await page.keyboard.press('ArrowLeft');
await page.keyboard.up('Shift');
await page.keyboard.press('Backspace');
```

## Touch / tap

`tap()` emits a touchscreen tap (not a click). Requires `hasTouch: true` in the context/device, otherwise it throws.

```typescript
// In config: use({ ...devices['Pixel 7'] }) or hasTouch: true
await page.getByRole('button').tap();
await page.touchscreen.tap(100, 200);   // low-level, CSS-pixel coords
```

## File uploads

`setInputFiles()` targets an `<input type=file>` directly (no real click needed) and performs no actionability checks. Use `waitForEvent('filechooser')` when a button opens the OS picker.

```typescript
import path from 'path';

await page.getByLabel('Upload file').setInputFiles(path.join(__dirname, 'myfile.pdf'));

await page.getByLabel('Upload files').setInputFiles([
  path.join(__dirname, 'file1.txt'),
  path.join(__dirname, 'file2.txt'),
]);

await page.getByLabel('Upload directory').setInputFiles(path.join(__dirname, 'mydir')); // <input webkitdirectory>

await page.getByLabel('Upload file').setInputFiles([]);   // clear selection

// In-memory buffer — no file on disk
await page.getByLabel('Upload file').setInputFiles({
  name: 'file.txt',
  mimeType: 'text/plain',
  buffer: Buffer.from('this is test'),
});
```

```typescript
// Picker opened by a button (no <input> to target)
const fileChooserPromise = page.waitForEvent('filechooser');
await page.getByLabel('Upload file').click();
const fileChooser = await fileChooserPromise;
await fileChooser.setFiles(path.join(__dirname, 'myfile.pdf'));
```

`FileChooser` also exposes `isMultiple()` (does the input accept multiple files?), `element()`, and `page()`.

## Drag and drop

`dragTo()` drags one locator onto another (HTML5/mouse drag). `locator.drop()` (v1.60+) simulates an **external** drag — OS files or clipboard-like data — onto a drop zone via synthetic `dragenter`/`dragover`/`drop` with a `DataTransfer`.

```typescript
await page.locator('#item-to-be-dragged').dragTo(page.locator('#item-to-drop-at'));

// Manual drag (precise control / canvas)
await page.locator('#item-to-be-dragged').hover();
await page.mouse.down();
await page.locator('#item-to-drop-at').hover();
await page.mouse.up();
```

```typescript
// locator.drop() (v1.60+) — external file drop onto an upload zone
await page.locator('#dropzone').drop({
  files: { name: 'note.txt', mimeType: 'text/plain', buffer: Buffer.from('hello') },
});

// locator.drop() (v1.60+) — clipboard-like data drop
await page.locator('#dropzone').drop({
  data: {
    'text/plain': 'hello world',
    'text/uri-list': 'https://example.com',
  },
});
```

`dragTo` requires the source to pass Visible + Stable + Receives Events.

> **JS DnD libraries (react-beautiful-dnd / @hello-pangea/dnd, dnd-kit):** `dragTo()`
> usually fails — they use a pointer/keyboard state machine with a drag threshold,
> not HTML5 drag. Prefer the **keyboard sensor** (Space → arrows → Space); fall back
> to a stepped mouse sequence. See [dnd-libraries.md](dnd-libraries.md).

## Dialogs

JS dialogs (`alert`/`confirm`/`prompt`/`beforeunload`) auto-**dismiss** unless a listener handles them. Register the handler **before** the action. A handler that never calls `accept()`/`dismiss()` hangs the test.

```typescript
page.on('dialog', dialog => dialog.accept());
await page.getByRole('button').click();
```

```typescript
// WRONG — logging without accepting/dismissing stalls forever
page.on('dialog', dialog => console.log(dialog.message()));
await page.getByRole('button').click();
```

```typescript
// Inspect and answer a prompt
page.on('dialog', async dialog => {
  console.log(dialog.type());     // 'alert' | 'beforeunload' | 'confirm' | 'prompt'
  console.log(dialog.message());
  await dialog.accept('typed answer');   // promptText for prompt dialogs
});
```

```typescript
// beforeunload
page.on('dialog', async dialog => {
  assert(dialog.type() === 'beforeunload');
  await dialog.dismiss();
});
await page.close({ runBeforeUnload: true });
```

API: `dialog.accept(promptText?)`, `dialog.dismiss()`, `dialog.message()`, `dialog.type()`, `dialog.defaultValue()`.

`window.print()` isn't a dialog event — stub it with [`addInitScript`](evaluating.md#addinitscript) and
await a flag if you need to assert printing:

```typescript
await page.addInitScript(() => { (window as any).__printed = false; window.print = () => { (window as any).__printed = true; }; });
await page.getByText('Print').click();
await expect.poll(() => page.evaluate(() => (window as any).__printed)).toBe(true);
```

See [events.md](events.md) for the dialog event in the broader event model.

## Downloads

Start waiting for the `download` event **before** clicking the trigger. Files live in a temp dir and are deleted when the context closes — call `saveAs()` to persist.

```typescript
const downloadPromise = page.waitForEvent('download');
await page.getByText('Download file').click();
const download = await downloadPromise;
await download.saveAs('/path/to/save/at/' + download.suggestedFilename());
```

```typescript
// Quick logging of every download's temp path
page.on('download', download => download.path().then(console.log));
```

API: `download.saveAs(path)`, `download.path()`, `download.suggestedFilename()`, `download.url()`, `download.failure()`, `download.createReadStream()`, `download.cancel()`, `download.delete()`. Set `downloadsPath` in `browserType.launch()` to control storage location.

## Navigation & auto-waiting

`page.goto()` waits for the `load` event by default and follows client-side redirects. Locator actions auto-wait — explicit waits are needed only for navigations not tied to the action being awaited.

```typescript
await page.goto('https://example.com');
await page.getByText('Example Domain').click();   // auto-waits for visible + actionable
```

```typescript
// goto with options
await page.goto('https://example.com', {
  waitUntil: 'domcontentloaded',   // 'load' (default) | 'domcontentloaded' | 'networkidle' | 'commit'
  timeout: 30000,
});
```

```typescript
// Wait for a URL after a navigation-triggering action
await page.getByText('Click me').click();
await page.waitForURL('**/login');
```

```typescript
await page.waitForLoadState();                 // default 'load'
await page.waitForLoadState('domcontentloaded');
await page.waitForLoadState('networkidle');    // discouraged; prefer web-first assertions
```

Prefer locators + web-first assertions over `waitForSelector` — locators retry automatically, so `await expect(locator).toBeVisible()` replaces most explicit element waits. See [assertions.md](assertions.md) and [locators.md](locators.md). `'networkidle'` is discouraged for testing readiness.

**Hydration (SSR/SPA):** a server-rendered page ships static HTML first, then JS "hydrates" it into a
live app. Clicks before hydration completes are silently lost. Playwright's auto-wait covers most
cases, but the robust fix is app-side — keep interactive controls **disabled until hydrated** so the
`Enabled` actionability check naturally gates the action. For new tabs/popups opened by navigation,
see [events.md](events.md#new-pages-tabs--popups).

## Auto-dismissing overlays (addLocatorHandler)

`page.addLocatorHandler(locator, handler)` (v1.42+) registers a callback that fires **automatically
whenever the locator becomes visible** mid-action — the clean way to dismiss intermittent cookie
banners, survey modals, or "session expiring" dialogs that would otherwise break unrelated steps.

```typescript
await page.addLocatorHandler(
  page.getByRole('button', { name: 'Accept all cookies' }),
  async () => { await page.getByRole('button', { name: 'Accept all cookies' }).click(); },
  { times: 1, noWaitAfter: true },   // options: cap invocations / don't wait for actionability after
);
// ...the rest of the test ignores the banner; Playwright runs the handler when it appears
await page.removeLocatorHandler(locator);   // unregister when done
```

Prefer this over sprinkling defensive `if (visible) dismiss()` checks throughout a suite.

## Frames & iframes

Use a frame locator for chained, auto-waiting access into an `<iframe>`; use the `Frame` object (`page.frame()` / `locator.contentFrame()`) when you need frame metadata, navigation, or `evaluate`.

```typescript
// contentFrame() on a locator — the preferred way (v1.43+)
const username = page.locator('#my-frame').contentFrame().getByLabel('User Name');
await username.fill('John');

// page.frameLocator(selector) still works; on the resulting FrameLocator,
// .first()/.last()/.nth() are deprecated — use page.locator(sel).first().contentFrame() instead.
// frameLocator.owner() converts back to a Locator on the <iframe> element.
```

```typescript
// Get a Frame object by name or URL pattern
const frame = page.frame('frame-login');
const frame2 = page.frame({ url: /.*domain.*/ });
await frame.fill('#username-input', 'John');
```

```typescript
// From a locator pointing at an <iframe> element (v1.43+)
const frame = await page.locator('iframe').contentFrame();
await frame.getByRole('button').click();

// Enumerate frames
for (const f of page.frames())
  console.log(f.url(), f.name());
```

## Actionability checks

Before acting, Playwright auto-waits (until timeout) for the relevant checks. `force: true` skips the non-essential ones.

| Action | Visible | Stable | Receives Events | Enabled | Editable |
|--------|---------|--------|-----------------|---------|----------|
| `check()` / `uncheck()` / `setChecked()` | ✓ | ✓ | ✓ | ✓ | — |
| `click()` / `dblclick()` / `tap()` | ✓ | ✓ | ✓ | ✓ | — |
| `hover()` | ✓ | ✓ | ✓ | — | — |
| `dragTo()` | ✓ | ✓ | ✓ | — | — |
| `screenshot()` | ✓ | ✓ | — | — | — |
| `fill()` / `clear()` | ✓ | — | — | ✓ | ✓ |
| `selectOption()` | ✓ | — | — | ✓ | — |
| `selectText()` | ✓ | — | — | — | — |
| `scrollIntoViewIfNeeded()` | — | ✓ | — | — | — |
| `blur()` / `dispatchEvent()` / `focus()` | — | — | — | — | — |
| `press()` / `pressSequentially()` | — | — | — | — | — |
| `setInputFiles()` | — | — | — | — | — |

- **Visible** — non-empty bounding box and not `visibility:hidden`. `display:none` and zero-size are not visible; `opacity:0` **is** visible.
- **Stable** — same bounding box for two consecutive animation frames (i.e. not animating).
- **Receives Events** — element is the hit target at the action point (not covered by an overlay).
- **Enabled** — not `[disabled]`, not a disabled `<fieldset>` descendant, not `[aria-disabled=true]`.
- **Editable** — enabled and not `[readonly]` / `[aria-readonly=true]`.

`click({ force: true })` disables Stable + Receives Events hit-testing (keeps essential checks). Actions with no checks (`dispatchEvent`, `setInputFiles`, `press`) act immediately.

## Clock / time mocking

`setFixedTime` freezes `Date.now()`/`new Date()` while timers keep running in real time — simplest for time-display assertions. `install()` + `setSystemTime`/`pauseAt`/`fastForward`/`runFor` gives full control: pause time and step it deterministically. Install **before** navigation.

```typescript
// Freeze the displayed clock only
await page.clock.setFixedTime(new Date('2024-02-02T10:00:00'));
await page.goto('http://localhost:3333');
await expect(page.getByTestId('current-time')).toHaveText('2/2/2024, 10:00:00 AM');
```

```typescript
// Full control: install, then jump time and fire timers
await page.clock.install({ time: new Date('2024-02-02T08:00:00') });
await page.goto('http://localhost:3333');
await page.clock.pauseAt(new Date('2024-02-02T10:00:00'));  // pause, firing timers up to this point
await page.clock.fastForward('30:00');                      // jump 30 min, skipping intermediate timers
```

API:
- `page.clock.install({ time })` — initialize fake timers (enables pause/tick control).
- `page.clock.setFixedTime(date)` — fix `Date.now()`/`new Date()`; timers still run live.
- `page.clock.setSystemTime(date)` — set current time without pausing (advanced).
- `page.clock.pauseAt(date)` — fast-forward to `date` firing timers, then pause.
- `page.clock.fastForward(ticks)` — jump ahead (`'30:00'` or ms), skipping intermediate timers.
- `page.clock.runFor(ticks)` — tick forward firing every timer along the way (`'30:00'` or ms).
- `page.clock.resume()` — resume real-time flow after a pause.

**Caveat:** if you call `install()` at all, it **must** come before any other `clock.*` call (and
before navigation) — out-of-order calls are undefined behavior. The clock overrides `Date`,
`setTimeout`/`setInterval` (and clears), `requestAnimationFrame`/`requestIdleCallback` (and cancels),
`performance`, and `Event.timeStamp`.

---

See also: [writing-tests.md](writing-tests.md) · [locators.md](locators.md) · [assertions.md](assertions.md) · [network.md](network.md) · [emulation.md](emulation.md) · [debugging.md](debugging.md) · [whats-new.md](whats-new.md)
