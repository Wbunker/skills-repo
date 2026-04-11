# Frontend Implementation
## SSE Parsing, Morphdom, Script Execution, sendToAgent Bridge, Skeleton States

---

## SSE Stream Reading

```js
const resp = await fetch('/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ messages: history }),
});

const reader = resp.body.getReader();
const decoder = new TextDecoder();
let buf = '';

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  buf += decoder.decode(value, { stream: true });
  const parts = buf.split('\n\n');
  buf = parts.pop();  // keep incomplete trailing chunk

  for (const part of parts) {
    if (!part.startsWith('data: ')) continue;
    let ev;
    try { ev = JSON.parse(part.slice(6)); } catch { continue; }

    switch (ev.type) {
      case 'text':         /* append to chat bubble */  break;
      case 'status':       /* show skeleton + status */ break;
      case 'widget_delta': scheduleRender(ev.html);     break;
      case 'widget_final': renderFinal(ev.html, ev.title); break;
      case 'done':         /* push to history */        break;
      case 'error':        /* show error bubble */      break;
    }
  }
}
```

**Why split on `\n\n`?** SSE frames are delimited by double newlines. Partial frames are kept in `buf` and prepended to the next chunk. Without this, partial events are silently dropped.

---

## Morphdom: Incremental DOM Updates

Morphdom diffs the current DOM against new HTML and patches only what changed. This prevents:
- Full innerHTML replacement (causes flicker, destroys user input in forms)
- Duplicate elements (morphdom identifies nodes by ID or position)
- Script re-execution on unchanged nodes

```html
<!-- Load morphdom from CDN -->
<script src="https://cdn.jsdelivr.net/npm/morphdom@2.7.4/dist/morphdom-umd.min.js"></script>
```

```js
function renderWidget(html) {
  clearSkeleton();

  const next = document.createElement('div');
  next.id = 'widget-root';   // must match the existing element's ID
  next.innerHTML = html;

  morphdom(widgetRoot, next, {
    onBeforeElUpdated(from, to) {
      // Skip nodes that haven't changed — avoids unnecessary DOM writes
      if (from.isEqualNode(to)) return false;
      return true;
    },
    onNodeAdded(node) {
      // Fade in genuinely new nodes
      if (node.nodeType === 1 && node.tagName !== 'STYLE' && node.tagName !== 'SCRIPT') {
        node.style.animation = '_fadeIn 0.3s ease both';
      }
      return node;
    }
  });
}
```

**Required CSS animation (define in host page):**
```css
@keyframes _fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to   { opacity: 1; transform: none; }
}
```

---

## Debounced Rendering

`widget_delta` fires on every token (~10-50ms). Calling morphdom each time causes layout thrashing. Batch into ~50ms windows:

```js
let renderTimer = null;
let pendingHTML = null;

function scheduleRender(html) {
  pendingHTML = html;
  if (renderTimer) return;   // already scheduled
  renderTimer = setTimeout(() => {
    renderTimer = null;
    if (pendingHTML) renderWidget(pendingHTML);
  }, 50);
}
```

On `widget_final`, cancel the timer and render immediately (final is authoritative):
```js
function renderFinal(html, title) {
  if (renderTimer) { clearTimeout(renderTimer); renderTimer = null; }
  widgetName.textContent = title;
  renderWidget(html);
  runScripts();
  setStatus(false, 'Ready');
}
```

---

## Script Execution

Browsers ignore `<script>` tags inserted via `innerHTML`. You must recreate each script element programmatically. **Only run this on `widget_final`** — running scripts on every `widget_delta` would execute initialization code multiple times.

```js
function runScripts() {
  widgetRoot.querySelectorAll('script').forEach(old => {
    const s = document.createElement('script');
    if (old.src) {
      s.src = old.src;
      s.async = true;
    } else {
      s.textContent = old.textContent;
    }
    old.parentNode.replaceChild(s, old);
  });
}
```

**Order matters** — If the widget includes `<script src="cdn/chart.js">` followed by initialization code, the `src` script loads async. The inline initialization code may run before Chart.js is ready. Claude should always place `<script src>` tags before inline initialization, and initialization should use event listeners if needed:

```html
<!-- Correct ordering in widget_code: -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
  // Chart.js is already loaded because it's above
  const ctx = document.getElementById('myChart');
  new Chart(ctx, { ... });
</script>
```

---

## Bidirectional Bridge: sendToAgent

Widgets call `window.sendToAgent(data)` to send interaction events back to Claude:

```js
// In host page JavaScript:
window.sendToAgent = function(data) {
  const text = `[Widget interaction] ${JSON.stringify(data)}`;
  history.push({ role: 'user', content: text });
  addBubble('user', text);
  doSend(null);  // null = history already updated, don't read textarea
};
```

**In generated widget code:**
```html
<script>
document.getElementById('filterBtn').addEventListener('click', () => {
  window.sendToAgent({ action: 'filter', period: 'weekly', metric: 'revenue' });
});
</script>
```

Claude receives `[Widget interaction] {"action": "filter", "period": "weekly", "metric": "revenue"}` as a user message and can generate an updated widget.

**Data serialization** — Always pass plain JSON-serializable objects. DOM elements, Functions, and circular references will fail silently. Serialize before passing:
```js
window.sendToAgent({ selected: Array.from(selectedItems) });
```

---

## Skeleton States

The `load_guidelines` roundtrip (Claude calls the tool → server responds → Claude processes → begins streaming) takes 500-1500ms. Show a skeleton immediately on the first `status` event:

```js
function showWidgetSkeleton() {
  if (document.getElementById('widget-skeleton')) return;
  document.getElementById('empty-state')?.remove();

  const sk = document.createElement('div');
  sk.id = 'widget-skeleton';
  sk.innerHTML = `
    <div class="sk-block" style="height:18px;width:42%"></div>
    <div class="sk-block" style="height:220px"></div>
    <div class="sk-block" style="height:12px;width:72%"></div>
    <div class="sk-block" style="height:12px;width:55%"></div>
  `;
  widgetRoot.appendChild(sk);
}

function clearSkeleton() {
  document.getElementById('widget-skeleton')?.remove();
}
```

```css
.sk-block {
  background: var(--color-surface-elevated);
  border-radius: 8px;
  animation: shimmer 1.5s ease-in-out infinite;
}
@keyframes shimmer {
  0%, 100% { opacity: 0.45; }
  50%       { opacity: 0.9;  }
}
```

`clearSkeleton()` is called at the start of `renderWidget()`. If streaming completes without a widget (text-only response), call it in the `finally` block:

```js
} finally {
  clearSkeleton();   // remove skeleton if no widget arrived
}
```

---

## Conversation History Management

The frontend manages the full conversation history and sends it on every request:

```js
let history = [];  // { role: 'user'|'assistant', content: string }[]

// On user send:
history.push({ role: 'user', content: userText });

// On stream complete (done event):
if (assistantText) {
  history.push({ role: 'assistant', content: assistantText });
}

// Send to server:
fetch('/chat', {
  body: JSON.stringify({ messages: history })
})
```

The server handles the tool use turns internally (tool_use + tool_result) — these are added to the server-side `messages` list within the request but not returned to the frontend. The frontend only tracks text turns.

---

## Status Bar Pattern

A persistent status bar gives users visibility into what's happening:

```js
function setStatus(active, text) {
  statusDot.className = 'status-dot' + (active ? ' live' : '');
  statusLabel.textContent = text;
}

// Usage through the event loop:
// status event:      setStatus(true, ev.text)    → "Loading chart guidelines..."
// widget_delta:      setStatus(true, 'Rendering...')
// widget_final:      setStatus(false, 'Ready')
// done (no widget):  setStatus(false, 'Idle')
// error:             setStatus(false, 'Error')
```

```css
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--color-text-muted); }
.status-dot.live {
  background: var(--color-success);
  animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.35; } }
```

---

## Suggestion Chips (Empty State UX)

Pre-populate example prompts so users understand the capability:

```html
<div class="chips">
  <div class="chip" onclick="quickSend('compound interest calculator')">
    Compound interest calculator
  </div>
  <div class="chip" onclick="quickSend('bar chart of monthly sales with made up data')">
    Sales bar chart
  </div>
  <div class="chip" onclick="quickSend('pomodoro timer')">Pomodoro timer</div>
  <div class="chip" onclick="quickSend('flowchart of how HTTP requests work')">
    HTTP flowchart
  </div>
</div>
```

```js
function quickSend(text) {
  inputEl.value = text;
  doSend();
}
```
