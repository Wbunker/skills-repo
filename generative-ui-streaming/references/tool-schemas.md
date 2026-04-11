# Tool Schemas and System Prompt
## show_widget, load_guidelines, SYSTEM_PROMPT

---

## Tool Definitions

```python
# tools.py
TOOLS = [
    {
        "name": "load_guidelines",
        "description": (
            "Load design guidelines before rendering your first widget. "
            "Call once silently — do NOT mention this step to the user. "
            "Pick modules that match the widget type you're about to create."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "modules": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["interactive", "chart", "diagram", "mockup"]
                    },
                    "description": "Which design modules to load. Choose all that apply."
                }
            },
            "required": ["modules"]
        }
    },
    {
        "name": "show_widget",
        "description": (
            "Render an interactive HTML widget or SVG diagram visible to the user. "
            "Use for: charts, dashboards, calculators, forms, diagrams, timers, games, visualizations. "
            "The widget appears in a panel next to the chat. "
            "Users can interact with it and send data back via window.sendToAgent(data). "
            "IMPORTANT: Always call load_guidelines before your first show_widget."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "i_have_seen_guidelines": {
                    "type": "boolean",
                    "description": "Set to true after calling load_guidelines."
                },
                "title": {
                    "type": "string",
                    "description": "Short snake_case name for this widget."
                },
                "widget_code": {
                    "type": "string",
                    "description": (
                        "HTML fragment to render. Rules: "
                        "1. No DOCTYPE, <html>, <head>, or <body> tags. "
                        "2. Order: <style> block first, then HTML content, then <script> last. "
                        "3. Use only CSS variables for colors (e.g. var(--color-accent)). "
                        "4. No gradients, shadows, or blur effects. "
                        "For SVG: start directly with <svg> tag."
                    )
                }
            },
            "required": ["i_have_seen_guidelines", "title", "widget_code"]
        }
    }
]
```

### Schema Design Decisions

**`i_have_seen_guidelines` boolean** — Forces Claude to consciously confirm it called `load_guidelines` first. Acts as a gating mechanism. Claude.ai's implementation uses `i_have_seen_read_me` for the same purpose.

**`title` declared before `widget_code`** — JSON streams left to right. `title` is short and arrives quickly. `widget_code` is long and streams slowly. This ordering ensures `title` is available early for display in the UI toolbar.

**`widget_code` description embeds constraints** — The `description` field is part of Claude's context when generating. Putting structural rules here (no DOCTYPE, style-first ordering, CSS variables only) is more reliable than system prompt alone because it's co-located with the schema at generation time.

**No `loading_messages` array** — Claude.ai's schema includes 1–4 loading messages displayed during the `load_guidelines` roundtrip. Add this to your schema if you want Claude to provide contextual skeleton text:
```python
"loading_messages": {
    "type": "array",
    "items": {"type": "string"},
    "maxItems": 4,
    "description": "1-4 short strings to display while the widget loads."
}
```

---

## System Prompt

```python
# system.py
SYSTEM_PROMPT = """You are a helpful assistant that can render interactive visual widgets alongside your responses.

When the user asks for something visual — chart, diagram, calculator, game, timer, dashboard, form, visualization — do this:
1. Call load_guidelines with the relevant modules (silently, never mention this to the user)
2. Call show_widget with the HTML/SVG content

Widget rules (mandatory):
- HTML fragments only — no DOCTYPE, no <html>/<head>/<body> wrapper tags
- Streaming order: <style> block first → HTML content → <script> tags last
- Use ONLY CSS variables for all colors. Never hardcode hex values or rgb():
    --color-bg             page background
    --color-surface        card/panel background
    --color-surface-elevated  elevated panel background
    --color-text           primary text
    --color-text-muted     secondary/hint text
    --color-accent         purple highlight (#7c3aed)
    --color-accent-light   lighter purple (#a78bfa)
    --color-border         subtle borders
    --color-success        green
    --color-warning        amber
    --color-danger         red
- Typography: headings use font-weight 500 (h1=22px, h2=18px, h3=16px), body 400/16px
- Flat design only — no gradients, box-shadows, blur, or glow effects
- No HTML comments (waste tokens during streaming)
- CDN scripts only from: cdnjs.cloudflare.com, cdn.jsdelivr.net, unpkg.com, esm.sh
- window.sendToAgent(data) sends user interaction data back to chat

Write your explanation/analysis as normal text OUTSIDE the tool call.
The widget should contain only the visual — no paragraphs of explanation inside it.
When you receive [Widget interaction] data, use it to update your response or render a new widget."""
```

### System Prompt Design Notes

**"silently, never mention this to the user"** — Without this, Claude narrates the tool call ("Let me load the chart guidelines first..."), which creates confusing UI. The tool call should be invisible.

**CSS variable list in system prompt** — Duplicates what's in the widget's CSS `:root`. Both are needed: the system prompt tells Claude what variables are available; the host page's `:root` actually defines them. If you update one, update both.

**"no HTML comments"** — Comments tokenize as real text during streaming, adding latency and context overhead with no user value.

**CDN allowlist** — Security boundary. These four CDNs cover virtually every charting, animation, and utility library Claude might use. Adding arbitrary CDNs opens you to supply chain risk.

**"[Widget interaction] data" prefix** — When `sendToAgent()` fires, the message is prefixed with `[Widget interaction]` so Claude can distinguish user input from widget events and respond appropriately.

---

## Guideline Files (Lazy Injection)

These files are NOT in the system prompt. They're loaded on demand when Claude calls `load_guidelines`.

**`guidelines/core.md`** — Always loaded alongside any module. Contains base layout rules, color system, typography scale, spacing conventions.

**`guidelines/chart.md`** — Chart.js configuration patterns, preferred chart types per data shape, axis labeling, animation settings (disable on streaming).

**`guidelines/interactive.md`** — Form patterns, input validation, slider ranges, calculator layout conventions, event handling patterns.

**`guidelines/diagram.md`** — SVG conventions, flowchart node patterns, connector routing, text wrapping in SVG.

**`guidelines/mockup.md`** — Card layouts, navigation patterns, grid systems, component hierarchy.

### Why Lazy Injection Beats Upfront Context

If all guidelines were in the system prompt (fixed overhead):
- Every message pays the token cost regardless of widget type
- Context window fills faster in long conversations
- Claude can't selectively ignore irrelevant guidelines

With `load_guidelines`:
- Core rules: ~500 tokens, always paid
- Guideline modules: ~1000-2000 tokens, paid only when building that widget type
- Net saving: significant on multi-turn conversations with mixed widget types

---

## Customizing for Your Brand

Replace the CSS variable names and values in both `SYSTEM_PROMPT` and the host page `:root`:

```python
# system.py — update variable list to match your brand
SYSTEM_PROMPT = """...
Use ONLY CSS variables:
    --brand-primary      your primary color
    --brand-bg           your background
    --brand-surface      your card background
    --brand-text         your text color
    --brand-muted        your secondary text
..."""
```

```css
/* host page :root */
:root {
  --brand-primary: #0f766e;
  --brand-bg: #f0fdf4;
  --brand-surface: #ffffff;
  --brand-text: #134e4a;
  --brand-muted: #5eead4;
}
```

Claude will now use your brand colors exclusively, and every generated widget inherits your theme automatically.
