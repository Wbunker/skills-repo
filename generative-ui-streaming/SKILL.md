---
name: generative-ui-streaming
description: Build systems where Claude generates interactive HTML/CSS/JS widgets via tool calls, streamed live to the browser as tokens arrive. Use when building AI-powered dashboards, copilots with visual output, no-code UI generators, data exploration tools, or any product where Claude should produce interactive interfaces rather than just text. Covers the full stack: FastAPI/SSE server, partial JSON streaming, morphdom DOM diffing, bidirectional agent bridge, and design system integration. Based on sausi-7's open-source implementation (reverse-engineered from claude.ai) plus CopilotKit, Vercel json-render, and AG-UI ecosystem patterns.
---

# Generative UI Streaming

The core insight: **Claude doesn't generate HTML as text — it generates HTML as a tool call argument**. The tool schema enforces structure; the server intercepts the streaming JSON and extracts HTML mid-stream; the browser renders it token-by-token via DOM diffing. Claude never knows the rendering infrastructure exists.

## Three Patterns — Pick One First

| Pattern | How it works | When to use |
|---------|-------------|-------------|
| **Open-ended** | Claude generates arbitrary HTML/CSS/JS inside a tool call | Maximum flexibility; custom calculators, games, charts, dashboards |
| **Declarative** | Claude returns structured JSON; your renderer maps it to components | Consistent brand; multi-framework; validated output (Vercel json-render) |
| **Static** | Claude picks from pre-built components you define | Highest polish; tightest control; use `useFrontendTool` (CopilotKit AG-UI) |

This skill covers **open-ended** in depth (it's the most complex and most flexible). For declarative, see [patterns.md](references/patterns.md).

## Quick Reference

| Task | Reference |
|------|-----------|
| Server: SSE loop, tool interception, partial JSON parser | [architecture.md](references/architecture.md) |
| Browser: morphdom, script execution, SSE parsing, sendToAgent | [frontend.md](references/frontend.md) |
| Tool schemas (show_widget, load_guidelines) and system prompt | [tool-schemas.md](references/tool-schemas.md) |
| CSS variables, streaming-safe design rules, CDN allowlist | [design-system.md](references/design-system.md) |
| Declarative (json-render), AG-UI protocol, CopilotKit patterns | [patterns.md](references/patterns.md) |

## How It Works (Open-Ended)

```
User message
    │
    ▼
FastAPI /chat endpoint
    │  streams SSE events
    ▼
Claude API (streaming)
    ├── text_delta → { type: "text", text: "..." }       → chat bubble
    └── tool_use: show_widget
            │  partial JSON streamed token by token
            ├── extract_widget_code() mid-stream
            │   → { type: "widget_delta", html: "<div..." }  → morphdom update
            └── on complete
                → { type: "widget_final", html: "...", title: "..." }
                    → morphdom + runScripts()
```

**Two-tool sequence Claude always follows:**
1. `load_guidelines(["chart"])` — pulls relevant design rules into context (lazy injection)
2. `show_widget({title, widget_code})` — emits the actual HTML artifact

## SSE Event Types

```
text          Claude's explanation text (streams word by word)
status        Tool progress ("Loading chart guidelines...")
widget_delta  Partial HTML as widget_code streams (debounced ~50ms)
widget_final  Complete HTML + title (triggers script execution)
done          Stream finished
error         Server-side error
```

## Gotchas

**Scripts don't execute via innerHTML** — Browsers ignore `<script>` tags set via innerHTML. Replace each with a freshly created element:
```js
const s = document.createElement('script');
s.textContent = old.textContent;
old.replaceWith(s);
```
Only do this on `widget_final`, never on `widget_delta`.

**Gradients, shadows, blur cause visual flashing** — morphdom patches the DOM continuously during streaming. CSS `box-shadow`, `background: linear-gradient(...)`, and `backdrop-filter` flash on every patch. Ban them globally. Design system uses flat colors only.

**Style ordering matters for progressive rendering** — Claude must emit `<style>` before HTML content before `<script>`. If the script tag arrives first, it runs before elements exist. Enforce in system prompt and tool schema description.

**widget_code must be last in the JSON schema** — JSON streams left to right. If `widget_code` is declared before `title` in the schema, `title` won't be available until the entire widget streams. Declare `title` first, `widget_code` last.

**Debounce morphdom calls** — `widget_delta` fires on every token (~10-50ms apart). Calling morphdom on each one causes layout thrashing. Batch to ~50ms with `setTimeout`.

**load_guidelines roundtrip adds 500-1500ms** — Claude makes a round-trip API call to process the tool result before widget_delta begins. Always show a skeleton state immediately on `status` event.

**Nginx/reverse proxy buffers SSE** — Add `X-Accel-Buffering: no` and `Cache-Control: no-cache` response headers. Without these, Nginx buffers SSE and the browser sees nothing until the buffer fills.

**morphdom needs a stable top-level element ID** — Pass `widgetRoot` by reference with `id="widget-root"`. The `next` div you morph into must have the same ID.

**CDN scripts load async** — If Claude uses a CDN library (`Chart.js`, etc.) and the `<script>` tag is at the bottom, the library may not be loaded when the initialization code runs. Always put CDN `<script src>` tags before initialization code, or use `DOMContentLoaded`.
