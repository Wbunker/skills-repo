---
name: claude-in-chrome tools reference
description: Full schema reference for all mcp__claude-in-chrome__* tools with usage notes
type: reference
---

# Claude-in-Chrome Tools Reference

## Table of Contents
1. [Page Reading Tools](#1-page-reading-tools)
2. [Element Interaction Tools](#2-element-interaction-tools)
3. [JavaScript & Network Tools](#3-javascript--network-tools)
4. [Navigation & Tab Tools](#4-navigation--tab-tools)
5. [Media & Recording Tools](#5-media--recording-tools)
6. [Planning Tools](#6-planning-tools)

---

## 1. Page Reading Tools

### `read_page`
Dumps the accessibility tree (DOM snapshot) as structured text. **Primary tool for understanding page structure.**

```
Parameters:
  tab_id: number (required)
  filter: "all" | "interactive" | "content"  (default: "all")
  ref_id: string  (optional — scope to a subtree)
  depth: number   (optional — limit tree depth)
```

- `filter="interactive"` — only buttons, inputs, links; much smaller output
- `filter="content"` — text and headings only
- `ref_id` — scope to a specific element's subtree (use ref IDs from prior `read_page` output)
- Output capped at ~50k characters; use `depth` or `ref_id` to stay under it
- **Do not call without scoping on complex pages** — will dump the entire `<main>` tag

### `get_page_text`
Extracts visible text content. Lighter than `read_page` when structure isn't needed.

```
Parameters:
  tab_id: number (required)
  selector: string  (optional — CSS selector to scope extraction)
  priority_selectors: string[]  (optional — extract these sections first)
```

- Use `priority_selectors` to pull the important section before hitting size limits
- Returns plain text, no ref IDs — can't click elements from this output

### `find`
**Uses an inner LLM call** to locate elements by natural-language description. Slower but handles ambiguous targets.

```
Parameters:
  tab_id: number (required)
  description: string  (natural language, e.g., "the submit button in the login form")
```

- Returns ref ID(s) of matched elements
- Use when `read_page` output is too large to scan manually, or element identity is unclear
- Avoid for simple/obvious targets — overhead not worth it

---

## 2. Element Interaction Tools

### `form_input`
Fills form fields by ref ID. Preferred over `computer` click+type for forms.

```
Parameters:
  tab_id: number (required)
  ref_id: string (required — from read_page output)
  value: string  (required)
```

- Obtains ref IDs from `read_page` first
- Handles `<input>`, `<textarea>`, `<select>` elements
- For `<select>`, pass the option value or visible text

### `computer`
Screenshot-based pointer/keyboard control. **Last resort** — use DOM tools first.

```
Parameters:
  tab_id: number (required)
  action: "screenshot" | "click" | "type" | "key" | "scroll" | "move"
  coordinate: [x, y]   (for click/move/scroll)
  text: string          (for type)
  key: string           (for key — xdotool key names)
```

- Screenshots consume significant tokens — minimize frequency
- Use for: canvas elements, custom widgets, visual verification, drag-and-drop
- Never use for standard form inputs if `form_input` works

---

## 3. JavaScript & Network Tools

### `javascript_tool`
Executes arbitrary JS in the page context. Returns serialized result.

```
Parameters:
  tab_id: number (required)
  code: string   (JS expression or IIFE)
```

- Use for: dismissing cookie banners, reading JS state, triggering events, exposing `window.__claudeElementMap`
- Returns `JSON.stringify` of result — wrap complex returns in an object
- Errors surface as rejected promises; wrap in try/catch when needed

### `read_console_messages`
Reads browser console output.

```
Parameters:
  tab_id: number (required)
  pattern: string  (optional — regex to filter entries)
  level: "log" | "warn" | "error" | "info"  (optional)
  limit: number    (optional)
```

- Always use `pattern` when looking for specific log entries — avoids token floods
- Use `level="error"` to quickly surface JS errors

### `read_network_requests`
Inspects XHR/fetch requests and responses.

```
Parameters:
  tab_id: number (required)
  pattern: string  (optional — regex on URL)
  method: string   (optional — "GET", "POST", etc.)
  limit: number    (optional)
```

- Useful for API debugging, verifying payload structure, checking auth headers

---

## 4. Navigation & Tab Tools

### `navigate`
```
Parameters:
  tab_id: number (required)
  url: string    (required)
  wait_for: "load" | "networkidle" | "domcontentloaded"  (optional, default: "load")
```

### `tabs_context_mcp`
Returns all open tabs with IDs, URLs, and titles. **Call this first** at session start — never reuse stale tab IDs.

```
Parameters: none
```

### `tabs_create_mcp`
Opens a new tab.

```
Parameters:
  url: string  (optional)
```

### `switch_browser`
Switches between Chrome profiles/windows.

```
Parameters:
  browser_id: string
```

### `resize_window`
```
Parameters:
  tab_id: number
  width: number
  height: number
```

---

## 5. Media & Recording Tools

### `gif_creator`
Records a GIF of multi-step interactions. Captures frames automatically.

```
Parameters:
  tab_id: number (required)
  filename: string  (meaningful name, e.g., "login_flow.gif")
  duration: number  (seconds)
```

- Always capture extra frames before and after key actions
- Use for demonstrations or debugging session replays

### `upload_image`
Sends an image to the page (for file upload inputs).

```
Parameters:
  tab_id: number
  ref_id: string  (file input element)
  image_path: string
```

---

## 6. Planning Tools

### `update_plan`
Updates the visible plan/checklist in the Claude UI during long sessions.

```
Parameters:
  plan: string  (markdown)
```

---

## Quick Reference: Tool Selection Matrix

| Goal | First choice | Fallback |
|------|-------------|---------|
| Understand page structure | `read_page(filter="interactive")` | `read_page(filter="all")` |
| Read text content | `get_page_text` | `read_page(filter="content")` |
| Find a specific element | `read_page` → scan ref IDs | `find` (LLM call overhead) |
| Fill a form field | `form_input` | `computer` click+type |
| Click a button | `read_page` → ref ID → `javascript_tool` click | `computer` click |
| Run JS | `javascript_tool` | — |
| Debug network | `read_network_requests` | `read_console_messages` |
| Visual verification | `computer` screenshot | — |
| Dismiss cookie banner | `javascript_tool` | `computer` click |
