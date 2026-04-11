# Design System Integration
## CSS Variables, Streaming-Safe Rules, CDN Allowlist, Security

---

## CSS Design Token System

Define all colors as CSS custom properties on `:root` in the host page. Claude uses `var(--token-name)` exclusively. Changing the `:root` values rebrands every generated widget instantly.

```css
/* Host page — define your brand tokens here */
:root {
  /* Backgrounds */
  --color-bg:               #f4f4f5;      /* page background */
  --color-surface:          #ffffff;      /* card/panel background */
  --color-surface-elevated: #ededf0;      /* elevated panel, skeleton blocks */

  /* Text */
  --color-text:             #18181b;      /* primary text */
  --color-text-muted:       #71717a;      /* secondary/hint text */

  /* Brand */
  --color-accent:           #7c3aed;      /* primary accent */
  --color-accent-light:     #8b5cf6;      /* lighter accent */

  /* Structural */
  --color-border:           rgba(0,0,0,0.09);

  /* Semantic */
  --color-success:          #059669;
  --color-warning:          #d97706;
  --color-danger:           #dc2626;
}
```

**Dark mode** — Define a parallel set under `@media (prefers-color-scheme: dark)` or a `.dark` class. Widget colors update automatically because they reference the variables, not hardcoded values.

```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg:               #0f0f0f;
    --color-surface:          #1a1a1a;
    --color-surface-elevated: #262626;
    --color-text:             #f4f4f5;
    --color-text-muted:       #a1a1aa;
    --color-border:           rgba(255,255,255,0.08);
  }
}
```

---

## Streaming-Safe CSS Rules

These rules exist because morphdom patches the DOM continuously while tokens stream. Some CSS properties cause visual artifacts during patching.

### Never Use

| Property | Problem |
|----------|---------|
| `box-shadow` | Flashes on every morphdom patch cycle |
| `background: linear-gradient(...)` | Repaints each patch causing gradient flash |
| `backdrop-filter: blur(...)` | Expensive repaint, flash during streaming |
| `filter: blur(...)` | Same as backdrop-filter |
| `text-shadow` | Minor but visible on rapid text updates |
| `font-weight: 600+` | FOUT (flash of unstyled text) as font weight loads |

### Safe Alternatives

| Instead of | Use |
|-----------|-----|
| `box-shadow` | `border: 1px solid var(--color-border)` |
| `linear-gradient` | Flat background color via CSS variable |
| Depth via shadow | Depth via border + slightly different background |
| Heavy font weights | Max `font-weight: 500` |

### Typography Scale

```css
/* Use these exact values — enforced in system prompt */
h1 { font-size: 22px; font-weight: 500; }
h2 { font-size: 18px; font-weight: 500; }
h3 { font-size: 16px; font-weight: 500; }
body, p { font-size: 16px; font-weight: 400; line-height: 1.6; }
small, label { font-size: 13px; font-weight: 400; }
```

Sticking to `400` and `500` only avoids font loading flashes. Bold (`700`) and semibold (`600`) require separate font files that may not be cached.

---

## Widget HTML Structure Order

Claude must always emit in this order. If the script tag arrives before elements exist, initialization code fails silently.

```html
<!-- 1. Styles first — CSS resolves immediately, no FOUC -->
<style>
  .my-widget { padding: 1rem; background: var(--color-surface); }
</style>

<!-- 2. HTML content — elements exist when script runs -->
<div class="my-widget">
  <canvas id="myChart"></canvas>
</div>

<!-- 3. CDN libraries — load before inline initialization -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<!-- 4. Inline initialization — runs after CDN script loads -->
<script>
  new Chart(document.getElementById('myChart'), { ... });
</script>
```

This ordering is enforced in both the system prompt and the `widget_code` field description.

---

## CDN Allowlist

Only these four CDNs are permitted for external scripts. They provide effectively complete coverage of charting, animation, math, and utility libraries while representing a well-audited security boundary.

| CDN | Best for |
|-----|---------|
| `cdn.jsdelivr.net` | Chart.js, D3, Alpine.js, GSAP |
| `cdnjs.cloudflare.com` | Three.js, Highcharts, Anime.js |
| `unpkg.com` | Any npm package |
| `esm.sh` | ES module imports (`import` syntax in widgets) |

**Enforcement** — Claude.ai enforces this via Content Security Policy headers. In your own implementation, add:

```python
# FastAPI middleware
from fastapi.middleware.cors import CORSMiddleware

@app.middleware("http")
async def add_csp(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "script-src 'self' 'unsafe-inline' "
        "cdn.jsdelivr.net cdnjs.cloudflare.com unpkg.com esm.sh;"
    )
    return response
```

`'unsafe-inline'` is required for the inline `<script>` blocks in widgets. This is acceptable because widget code comes from Claude (your controlled system prompt), not user input.

---

## Two-Color-Ramp Rule

Limit each widget to a maximum of 2-3 distinct color ramps. More than that causes visual noise and degrades readability, especially on charts.

```
Good:  --color-accent (primary data) + --color-surface (background) + --color-text (labels)
Bad:   Red data + blue grid + green annotations + orange highlight + purple secondary series
```

For multi-series charts: use opacity variants of the accent color rather than completely different hues:
- Series 1: `var(--color-accent)` (100% opacity)
- Series 2: `rgba(var(--color-accent-rgb), 0.6)`  
- Series 3: `rgba(var(--color-accent-rgb), 0.3)`

To enable rgba() with CSS variables, define the RGB components separately:
```css
:root {
  --color-accent-rgb: 124, 58, 237;
  --color-accent: rgb(var(--color-accent-rgb));
}
```

---

## Widget Sizing and Scrolling

Widgets live in `#widget-root` which has `overflow-y: auto`. Widgets should:
- Have a minimum height so they don't collapse to nothing before content loads
- Not set `height: 100vh` (they're inside a container, not the full page)
- Use `min-height` for charts to ensure canvas has dimensions before Chart.js initializes

```css
.widget-container {
  min-height: 200px;   /* prevent collapse during streaming */
  padding: 1rem;
  background: var(--color-surface);
  border-radius: 8px;
  border: 1px solid var(--color-border);
}

canvas#myChart {
  min-height: 250px;   /* Chart.js needs explicit dimensions */
  width: 100% !important;
}
```

---

## No HTML Comments

HTML comments (`<!-- like this -->`) waste tokens during streaming with zero user value. Every comment is tokenized, sent over the wire, and parsed by the browser — then discarded. Enforce via system prompt.

Approximate cost per comment: 3-15 tokens. Over a 200-line widget with 10 comments, that's 50-150 tokens of pure overhead.
