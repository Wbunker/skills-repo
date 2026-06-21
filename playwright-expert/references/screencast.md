# Screencast API

`page.screencast` (v1.59+) records annotated videos and streams live frames from a page — built for AI-vision pipelines and demo/narration videos. It is richer than plain test [video recording](visual-comparisons.md) and distinct from [trace](trace-viewer.md) screenshots: it can overlay action highlights, chapter titles, and custom HTML, and emit JPEG frames to a callback in real time.

## Contents

- [start / stop](#start--stop)
- [Action annotations](#action-annotations)
- [Visual overlays](#visual-overlays)
- [Frame streaming (onFrame)](#frame-streaming-onframe)
- [Config-based annotations](#config-based-annotations)
- [vs. video recording vs. trace](#vs-video-recording-vs-trace)
- [Related](#related)

## start / stop

`page.screencast.start(options?)` begins capture and returns a disposable; `page.screencast.stop()` ends it and writes the file (when `path` was given).

```js
await page.screencast.start({ path: 'video.webm', size: { width: 1280, height: 800 } });
// ... drive the page ...
await page.screencast.stop();
```

`start()` options:

| Option | Type | Notes |
| --- | --- | --- |
| `path` | `string` | Output file path for the recorded video |
| `size` | `{ width, height }` | Capture dimensions in pixels |
| `quality` | `number` | 0–100 |
| `onFrame` | `({ data, timestamp, viewportWidth, viewportHeight }) => void` | Live JPEG frame stream — see [below](#frame-streaming-onframe) |

`start()` returns a disposable, so it also works with `using` for scoped recording:

```js
{
  using const _ = await page.screencast.start({ path: 'video.webm' });
  // recording stops automatically at end of scope
}
```

This is an alternative to the `recordVideo` context option — use it when you need annotations or frame streaming.

## Action annotations

`screencast.showActions(options?)` overlays a highlight/label on each user interaction; `screencast.hideActions()` turns it off. Returns a disposable.

```js
await page.screencast.start({ path: 'demo.webm' });
await page.screencast.showActions({ position: 'top-right', duration: 750, fontSize: 28 });
// ... interactions are now annotated ...
await page.screencast.hideActions();
await page.screencast.stop();
```

`showActions()` options:

| Option | Type | Default | Notes |
| --- | --- | --- | --- |
| `position` | enum | `'top-right'` | `'top-left'` \| `'top'` \| `'top-right'` \| `'bottom-left'` \| `'bottom'` \| `'bottom-right'` |
| `duration` | `number` (ms) | `500` | How long each annotation stays visible |
| `fontSize` | `number` (px) | `24` | Label font size |
| `cursor` | `'none'` \| `'pointer'` | `'pointer'` | Cursor rendering during annotated actions |

## Visual overlays

`showChapter(title, options?)` displays a centered chapter card (title + optional description) over a backdrop — useful for sectioning a demo video.

```js
await page.screencast.showChapter('Checkout flow', {
  description: 'Adding an item and completing payment',
  duration: 2500,
});
```

- `description`: `string` (optional)
- `duration`: `number` ms (default `2000`)

`showOverlay(html, options?)` adds an arbitrary HTML overlay; returns a disposable.

```js
await page.screencast.showOverlay('<h1>Step 1</h1>', { duration: 3000 });
```

- `duration`: `number` ms — overlay persists until hidden if omitted.

`showOverlays()` / `hideOverlays()` reveal or conceal previously added overlays without removing them:

```js
await page.screencast.hideOverlays();
await page.screencast.showOverlays();
```

## Frame streaming (onFrame)

Pass `onFrame` to `start()` to receive JPEG frames as the page renders — feed them straight to a vision model instead of (or in addition to) writing a file.

```js
await page.screencast.start({
  onFrame: ({ data }) => sendToVisionModel(data),
  size: { width: 800, height: 600 },
});
```

The frame object: `{ data, timestamp, viewportWidth, viewportHeight }`.

- `data` — JPEG bytes for the frame.
- `timestamp` (v1.61+) — presentation timestamp: when the browser presented the frame, for temporal alignment of frame-processing workflows.
- `viewportWidth` / `viewportHeight` — frame dimensions.

```js
// v1.61+: use presentation timestamps to order/align frames
await page.screencast.start({
  onFrame: ({ data, timestamp }) => queue.push({ data, t: timestamp }),
});
```

## Config-based annotations

Annotations can be enabled declaratively in `playwright.config` via `use.video.show`, so recorded test videos carry action/test overlays without per-test code (v1.59+).

```js
// playwright.config.js
export default {
  use: {
    video: {
      mode: 'on',
      show: {
        actions: { position: 'top-left' },
        test: { position: 'top-right' },
      },
    },
  },
};
```

- `actions` — same positioning/annotation options as [`showActions()`](#action-annotations).
- `test` — overlays test-context info (e.g. test title) at the given position.

See [test-config.md](test-config.md) for the surrounding `video` config shape.

## vs. video recording vs. trace

- **Plain video recording** (`recordVideo` / `use.video`) just captures raw page frames to a file — no overlays, no frame callback. See [visual-comparisons.md](visual-comparisons.md).
- **Trace screenshots** ([trace-viewer.md](trace-viewer.md)) are after-the-fact snapshots embedded in a trace for the Trace Viewer — not a live stream and not annotated video.
- **Screencast** is the only one that overlays actions/chapters/HTML and streams JPEG frames live via `onFrame`.

## Related

- [visual-comparisons.md](visual-comparisons.md) — plain video recording & screenshot assertions
- [trace-viewer.md](trace-viewer.md) — trace screenshots & the Trace Viewer
- [test-config.md](test-config.md) — `use.video` configuration
- [library-api.md](library-api.md) — `page` / context APIs
- [debugging.md](debugging.md)
- [whats-new.md](whats-new.md) — v1.59–1.61 release notes
