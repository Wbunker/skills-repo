# Testing JS drag-and-drop libraries (react-beautiful-dnd / @hello-pangea/dnd, dnd-kit, SortableJS)

`locator.dragTo()` and `page.dragAndDrop()` are built for **HTML5 drag** (and a
single mouse move). Most modern React DnD libraries are **not** HTML5 drag — they
run their own state machine on raw `pointer`/`mouse` + `keyboard` events. So the
built-in helpers silently "almost work": you see a flicker at the source and the
item snaps back, with no drop. This is the long-standing
[microsoft/playwright#13855](https://github.com/microsoft/playwright/issues/13855)
/ [#21621](https://github.com/microsoft/playwright/issues/21621).

**Diagnose the library first** — it determines the whole approach:
- **`react-beautiful-dnd` / `@hello-pangea/dnd`** (the same engine; `@hello-pangea`
  is the maintained fork). Pointer **mouse sensor** with a *drag threshold* + a
  **keyboard sensor**. Drag handles expose an aria description like *"Press space
  bar to start a drag. … use the arrow keys to move … escape to cancel"* — if you
  see that, it's this engine. **Prefer the keyboard sensor (below).**
- **`dnd-kit`** — pointer/keyboard sensors too; keyboard activation is
  configurable (Space/Enter). **More automatable than rbd**: both sensors drive
  reliably from Playwright, *including nested-tree re-parent*. See the dnd-kit
  section below for the two gotchas (keyboard rAF timing; pointer DOM-gate).
- **`SortableJS` / `react-dnd` (HTML5 backend)** — closer to native; `dragTo()`
  with `{ steps }` or `locator.drop()` may work. Test it before hand-rolling.

---

## Preferred: drive the keyboard sensor (reliable + tests accessibility)

react-beautiful-dnd / @hello-pangea/dnd ship a deterministic keyboard sensor. It
is **the** reliable automation path — no pixel math, no timing guesswork, and it
exercises the a11y story for free.

```
focus the drag handle → Space (lift) → Arrow keys (move) → Space (drop)
```

Axis rules ([keyboard sensor docs](https://github.com/hello-pangea/dnd/blob/HEAD/docs/sensors/keyboard.md)):
| List orientation | Main axis (reorder *within* a list) | Cross axis (move *between* lists) |
|---|---|---|
| Vertical (default) | `ArrowUp` / `ArrowDown` | `ArrowLeft` / `ArrowRight` |
| Horizontal | `ArrowLeft` / `ArrowRight` | `ArrowUp` / `ArrowDown` |

`Escape` cancels. **Wait on the library's own `aria-live` announcements** ("You
have lifted an item…", "…moved…", "You have dropped the item.") instead of fixed
sleeps — they track the rAF-driven state machine exactly.

```typescript
const ARROW = { up: "ArrowUp", down: "ArrowDown", left: "ArrowLeft", right: "ArrowRight" } as const;

async function liveText(page: Page) {
  return (await page.locator("[aria-live]").allTextContents()).join(" ");
}

/** Reorder a react-beautiful-dnd / @hello-pangea/dnd item by keyboard. */
export async function keyboardReorder(
  page: Page,
  handle: Locator,                                   // element with the dragHandleProps
  opts: { direction: keyof typeof ARROW; steps?: number }
) {
  await handle.focus();
  await page.keyboard.press("Space");                // lift
  await expect.poll(() => liveText(page)).toContain("lifted");
  for (let i = 0; i < (opts.steps ?? 1); i++) await page.keyboard.press(ARROW[opts.direction]);
  await page.keyboard.press("Space");                // drop
  await expect.poll(() => liveText(page)).toContain("dropped");
}
```

Use main-axis arrows to reorder within a list; cross-axis arrows to move an item
into an **adjacent** list (e.g. Kanban column → column).

### Hard limitation: nested / tree droppables
The keyboard sensor only reaches droppables laid out **along the cross axis**
(side-by-side columns). It **cannot move an item into a vertically-nested,
indented child droppable** — i.e. you can't re-parent a node in a tree by
keyboard. The docs flag trees as unsupported, and it reproduces: lifting a
top-level node and pressing the cross-axis arrow produces no "moved" announcement.
**This is also a real accessibility gap** in any such tree (keyboard users can't
re-parent), not just a test limitation — worth raising as a product issue, not
papering over with a flaky mouse test.

---

## Fallback: manual stepped mouse (when keyboard can't express the move)

Needed for moves the keyboard sensor can't do. The mouse sensor starts a drag
only **after the pointer crosses a drag threshold** ("more than a sloppy click")
and then follows `mousemove`s across animation frames
([mouse sensor docs](https://github.com/atlassian/react-beautiful-dnd/blob/master/docs/sensors/mouse.md)).
So a single jump (`dragTo`) misses the move loop. Reproduce the real sequence:

```typescript
async function mouseDragRbd(page: Page, handle: Locator, target: Locator) {
  const h = await handle.boundingBox();
  const t = await target.boundingBox();
  if (!h || !t) throw new Error("missing bounding box");
  await page.mouse.move(h.x + h.width / 2, h.y + h.height / 2);
  await page.mouse.down();
  // 1) cross the drag threshold with a small initial move…
  await page.mouse.move(h.x + h.width / 2, h.y + h.height / 2 + 8, { steps: 6 });
  // 2) …then travel to the target in many interpolated steps so every
  //    intermediate mousemove fires (rbd listens to each one).
  await page.mouse.move(t.x + t.width / 2, t.y + t.height / 2, { steps: 25 });
  await page.mouse.move(t.x + t.width / 2, t.y + t.height / 2 + 2, { steps: 6 });
  await page.mouse.up();
}
```

Key points: **two+ separate `mouse.move` calls** (threshold-cross, then travel),
high `steps`, source/target via `boundingBox()`. Even so, mouse automation of
**nested-droppable re-parent** is unreliable in practice — if you can't make it
deterministic, assert the outcome at the data layer (API/state) or document the
gap rather than commit a flaky test.

### Verified: reliable mouse cross-SECTION move (1-on-1 Issues → Next Steps, 2026-06)

Stacked sibling droppables can't be crossed by keyboard (cross-axis is horizontal;
the lists are stacked vertically). The mouse fallback flaked for **four** distinct
reasons; fixing all four made it green repeatedly in the full suite
(`e2e/dnd-helpers.ts` `mouseDragRbd`, `e2e/steps/1-on-1.steps.ts`):

1. **Attribute prefix is `rfd`, not `rbd`.** `@hello-pangea/dnd` renamed
   react-beautiful-dnd's `data-rbd-*` → **`data-rfd-*`** (`data-rfd-droppable-id`,
   `data-rfd-drag-handle-draggable-id`). `data-rbd-droppable-id` matches nothing —
   this alone made every attempt no-op. Confirm via
   `grep data-rfd node_modules/@hello-pangea/dnd/dist/dnd.cjs.js`.
2. **The lift silently fails to start under load.** Press → small threshold move →
   then **poll rbd's aria-live for "lifted"**; if absent in ~2s, `mouse.up` +
   `Escape` and **retry the whole press** (a few attempts). Biggest fix — same
   gate-on-announcement rule as the keyboard helper. Never trust a fixed sleep
   after `mouse.down`.
3. **Drop onto an item ROW, not the container's empty centre.** Re-read the target
   `boundingBox()` each pass and dwell (several interpolated moves, ~120ms pauses)
   so multiple `mousemove`s fire inside the destination; releasing over an existing
   row registers the destination far more reliably.
4. **Page length matters — use a dedicated, pristine session.** In the full suite
   the shared session had accumulated mutations (taller page) → the destination
   scrolled and the drop missed. A dedicated seeded session no other scenario
   touches keeps the page short and the drag deterministic.

Net: rbd's mouse sensor **can** be driven reliably for stacked cross-list moves —
gate on the lift announcement, retry, drop on a row, isolate the page state.
Reserve a dnd-kit migration for when even this won't converge.

---

## dnd-kit specifics (verified in this repo — Pages tree, 2026-06)

dnd-kit is **more automatable than react-beautiful-dnd**. We migrated the Pages
sidebar tree to it (`@dnd-kit/core` + `@dnd-kit/sortable`) precisely because both
its sensors drive reliably from Playwright — including **nested-tree re-parent**,
which rbd's keyboard sensor cannot express and its mouse sensor can't do reliably.
Both scenarios (keyboard reorder + drag-to-nest) run green 10/10 under the parallel
suite. Two engine-specific gotchas, both already solved in `e2e/dnd-helpers.ts`:

1. **Keyboard sensor commits the move on a rAF tick — wait for the announcement
   to *change* between each arrow and the drop.** rbd announced synchronously, so
   `Space → Arrow → Space` worked back-to-back. dnd-kit's `KeyboardSensor` updates
   coordinates asynchronously; if `Space` (drop) fires immediately after `Arrow`,
   the drop reads the *pre-move* position and the reorder is a silent no-op
   (`over === active`). Fix: after each arrow, `expect.poll(liveRegionText).not.toBe(before)`
   before the next key. dnd-kit announces both "Picked up …" and "… moved over …".

2. **Pointer/mouse sensor (`PointerSensor`, `activationConstraint.distance`) drives
   reliably, but gate the drop on a DOM signal that the drag activated.** Move once
   to cross the activation distance, then wait for the **`DragOverlay`** to mount
   (it duplicates the dragged row, so the row's title appears twice in the tree)
   before the remaining moves + `mouse.up`. Without this, under parallel-suite load
   `mouse.up` can fire before the sensor activates and `onDragEnd` never runs.
   Prefer this **DOM gate over an aria-live gate** for the pointer sensor: its
   announcement wording/timing differ from the keyboard path, and the nesting case
   (hovering over the dragged row itself, `over === active`) produces no "moved over"
   announcement to poll on. Drag right to nest — dnd-kit projects tree depth from the
   horizontal offset (`getProjection` + `getDragDepth(offsetX / indentWidth)`); a
   ref (`offsetLeftRef`) mirrors the live offset so `onDragEnd` recomputes the
   projection authoritatively rather than reading a stale render closure.

See `e2e/dnd-helpers.ts` (`keyboardReorder`, `pointerDrag`) for the canonical
implementations and `e2e/steps/pages.steps.ts` for usage.

> **Server note:** when verifying e2e locally, a stale `next start` on :3000 will
> serve a mismatched build (ChunkLoadError / "Something went wrong") and make a
> fixed code change look broken. Always (re)build through `scripts/e2e-local.sh`,
> which frees the port with `fuser -k` and waits until it's actually free before
> starting. Never `pkill -f next-server` — it matches its own command line.

---

## Rules of thumb
- **Try keyboard first.** It's the most reliable and the most maintainable.
- **Never** rely on `dragTo()`/`dragAndDrop()` for pointer-sensor libraries
  without verifying the drop actually committed (assert end state, not "no error").
- **Don't sleep** — poll the library's `aria-live` announcements (keyboard) or the
  post-drop state (mouse).
- If a move is neither keyboard-expressible nor reliably mouse-drivable, that's a
  signal about the **app's accessibility**, not just the test — flag it.

## Sources
- [@hello-pangea/dnd keyboard sensor](https://github.com/hello-pangea/dnd/blob/HEAD/docs/sensors/keyboard.md)
- [react-beautiful-dnd mouse sensor (drag threshold)](https://github.com/atlassian/react-beautiful-dnd/blob/master/docs/sensors/mouse.md)
- [Playwright #13855 — dragAndDrop not working with react-beautiful-dnd](https://github.com/microsoft/playwright/issues/13855)
- [Reflect — testing drag-and-drop in Playwright](https://reflect.run/articles/how-to-test-drag-and-drop-interactions-in-playwright/)
