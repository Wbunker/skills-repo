# Chrome DevTools Reference

Docs: `https://developer.chrome.com/docs/devtools`
Updates: `https://developer.chrome.com/blog/new-in-devtools-{N}`

## Table of Contents
- [Panels Overview](#panels-overview)
- [Elements Panel](#elements-panel)
- [Console Panel](#console-panel)
- [Sources Panel](#sources-panel)
- [Network Panel](#network-panel)
- [Performance Panel](#performance-panel)
- [Memory Panel](#memory-panel)
- [Recorder Panel](#recorder-panel)
- [Application Panel](#application-panel)
- [Keyboard Shortcuts](#keyboard-shortcuts)

## Panels Overview

| Panel | Purpose |
|-------|---------|
| Elements | DOM/CSS inspection, accessibility tree, animations |
| Console | JS execution, log messages, errors |
| Sources | JS debugging, breakpoints, Snippets, Workspaces |
| Network | Request monitoring, throttling, HAR export |
| Performance | Runtime/load profiling, Web Vitals, flame chart |
| Memory | Heap snapshots, allocation timelines, leak detection |
| Recorder | Record/replay/measure user flows |
| Application | Storage, service workers, manifests, cache |
| Security | Certificates, mixed content |
| Lighthouse | Automated audits for performance, accessibility, SEO |

Open DevTools: `F12` / `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows/Linux)

---

## Elements Panel

- Inspect and edit DOM in real time
- CSS pane: computed styles, box model, event listeners, CSS overview
- **Accessibility tree** (Chrome 135+): enabled by default — toggle with accessibility icon or `Ctrl+Shift+A`
- Force element state: right-click → Force state → `:hover`, `:focus`, `:active`, `:visited`
- Inspect animations: Three-dot menu → More tools → Animations
- CSS changes tracker: Three-dot menu → More tools → Changes

---

## Console Panel

```js
// Logging levels
console.log(), console.info(), console.warn(), console.error()
console.group(label) / console.groupEnd()
console.table(data)         // tabular display
console.time(label) / console.timeEnd(label)
console.assert(condition, message)
console.trace()

// DevTools-only convenience APIs (not available in extensions/web pages)
$0          // currently selected element in Elements panel
$('selector')   // like document.querySelector
$$('selector')  // like document.querySelectorAll → Array
$x('xpath')     // XPath query
inspect(elem)   // select element in Elements panel
copy(obj)       // copy to clipboard
monitorEvents(elem, ['click', 'keydown'])
```

---

## Sources Panel

- **Breakpoints:** Click line number; conditional breakpoints (right-click)
- **Logpoints:** Right-click → Add logpoint — logs without pausing
- **Snippets:** Left pane → Snippets tab — reusable JS scripts that persist
- **Workspaces:** Map network resources to local files for live editing
- **Overrides:** Override any file served by any URL with a local file (Sources → Overrides)
- **Call stack, Scope, Watch** panes during pause

Pause types:
- Line-of-code breakpoints
- Conditional breakpoints
- DOM change breakpoints (Elements panel → right-click node)
- XHR/fetch breakpoints
- Event listener breakpoints
- Exception breakpoints (pause on caught/uncaught exceptions)

---

## Network Panel

- **Filter bar:** Filter by type (JS/CSS/Img/Media/WS), status code, domain, regex
- **Throttle:** Preset (Slow 3G, Fast 4G) or custom upload/download/latency
- **HAR export:** Right-click → Save all as HAR with content
- **Block requests:** Right-click → Block request URL/domain
- Request detail tabs: Headers, Payload, Preview, Response, Initiator, Timing, Cookies

**Timing breakdown:** Queueing → Stalled → DNS Lookup → Initial connection → SSL → TTFB → Content Download

Chrome 135: Empty state guidance when no requests are captured.

---

## Performance Panel

Records runtime and load performance. Outputs a flame chart.

### Recording
- Click Record → interact → Stop
- Or: Reload + Record for full page load profile

### Tracks
- **Main thread:** Tasks, scripting, rendering, painting
- **Network:** Resource loading timeline
- **Frames:** Visual frame rendering
- **Timings:** LCP, FCP, DOMContentLoaded, Load

### Web Vitals (Chrome 135)
- **LCP** (Largest Contentful Paint): green < 2.5s, needs improvement 2.5-4s, poor > 4s
- **CLS** (Cumulative Layout Shift): green < 0.1
- **INP** (Interaction to Next Paint): green < 200ms

Chrome 135 improvements:
- **LCP phase breakdown:** TTFB, resource load delay, resource load duration, element render delay
- **Field data overlay:** Compare local LCP against Chrome UX Report data for your URL
- **Network dependency tree:** Highlights chained critical-path requests
- **Heaviest stack:** Identifies the most expensive call stack in the recording
- **Origin/script links** in Summary tab

### CPU Throttling
Simulates slower devices: 4x slowdown, 20x slowdown.

---

## Memory Panel

| Tool | Use for |
|------|---------|
| Heap snapshot | Find memory leaks — compare snapshots before/after action |
| Allocation instrumentation on timeline | Track allocations over time |
| Allocation sampling | Low-overhead memory profiling |

**Heap snapshot workflow:**
1. Take snapshot (baseline)
2. Perform action
3. Take snapshot
4. Switch to "Comparison" view
5. Sort by "# Delta" to find new allocations

---

## Recorder Panel (Chrome 97+)

Record user flows without writing code. Replays handle scroll and visibility automatically.

**Workflow:**
1. Recorder panel → Start new recording
2. Interact with page (clicks, form fills, navigation)
3. Stop recording
4. Replay: click Replay button
5. Measure: "Measure performance" → opens Performance panel with the replay

**Export formats:**
- JSON (import back to Recorder)
- Puppeteer script
- Custom via extensions

**Step editing:**
- Click any step to edit: selector, value, timeout, scroll position
- Add step: click `+` between steps
- Add selector fallbacks for resilient replay

---

## Application Panel

| Section | Contents |
|---------|----------|
| Application | Manifest, service workers, storage |
| Storage | localStorage, sessionStorage, IndexedDB, Web SQL, cookies |
| Cache | Cache Storage, Back/forward cache |
| Background services | Background fetch, sync, notifications, push |
| Frames | Resources by frame origin |

**Service Workers:** View registered SWs, force update, bypass for network, push test messages, sync test.

---

## Keyboard Shortcuts

| Action | Mac | Windows/Linux |
|--------|-----|---------------|
| Open DevTools | `Cmd+Option+I` | `Ctrl+Shift+I` |
| Open Console | `Cmd+Option+J` | `Ctrl+Shift+J` |
| Inspect element | `Cmd+Shift+C` | `Ctrl+Shift+C` |
| Command palette | `Cmd+Shift+P` | `Ctrl+Shift+P` |
| Find in Sources | `Cmd+P` | `Ctrl+P` |
| Search all files | `Cmd+Option+F` | `Ctrl+Shift+F` |
| Toggle device mode | `Cmd+Shift+M` | `Ctrl+Shift+M` |
| Next panel | `Cmd+]` | `Ctrl+]` |
| Step over (debug) | `F10` | `F10` |
| Step into (debug) | `F11` | `F11` |
| Resume (debug) | `F8` | `F8` |
