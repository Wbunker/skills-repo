---
name: claude-in-chrome context management
description: Token hygiene, ref ID system, session stability, CLAUDE.md patterns for Chrome plugin sessions
type: reference
---

# Context Management for Claude-in-Chrome

## The ref ID System

`read_page` returns an accessibility tree where every interactive element has a `ref_id` (e.g., `ref_42`). These IDs are stored in `window.__claudeElementMap` in the page JS context.

```javascript
// Inspect the map directly if needed
Object.keys(window.__claudeElementMap).length  // how many refs exist
window.__claudeElementMap['ref_42']            // get the DOM node
```

**Scoping with `ref_id`:** Pass a `ref_id` to `read_page` to dump only that subtree:
```
read_page(tab_id, filter="all", ref_id="ref_10")
```
This is the primary token-saving technique when a page is large.

---

## Token Hygiene Rules

### 1. Always scope `read_page` on large pages
Never call `read_page` without `filter` or `ref_id` on complex pages — it dumps the entire `<main>` tag and can consume 20k+ tokens.

**Preferred pattern:**
1. `read_page(filter="interactive")` to see the controls
2. If the target area is identified, `read_page(ref_id=<container>)` to scope further
3. Only call `read_page(filter="all")` on simple or small pages

### 2. Use `get_page_text` for read-only tasks
When you only need to read values (not interact), `get_page_text` with a CSS selector is cheaper than `read_page`.

### 3. Minimize `computer` screenshots
Each screenshot is a large image payload. Batch actions: read the tree, plan all interactions, execute them, then take one final screenshot to verify.

### 4. Use `read_console_messages` with `pattern`
Never read all console output. Always pass a regex pattern:
```
read_console_messages(tab_id, pattern="\\[MyApp\\]|error|warn")
```

### 5. Filter network requests
```
read_network_requests(tab_id, pattern="/api/", method="POST")
```

---

## Session Stability

### MV3 Service Worker Idle Timeout
The Chrome extension runs as an MV3 service worker, which Chrome terminates after ~30 seconds of inactivity. **Symptoms:** tool calls start failing silently or returning stale data.

**Mitigation:**
- Keep a background keepalive ping in long sessions
- If tools stop responding, reload the extension or re-open the panel
- Use `tabs_context_mcp` to verify the session is still alive

### Stale Tab IDs
Tab IDs from a previous session are invalid. Always call `tabs_context_mcp` at session start. If a tool returns an error about an invalid tab, call `tabs_context_mcp` again to refresh IDs.

### Cookie Banners / Modal Blocking
Cookie consent dialogs block interactions. Dismiss them first via JS before any page work:

```javascript
// Generic dismissal — adapt selector to the specific banner
javascript_tool(tab_id, `
  const btn = document.querySelector(
    '[id*="accept"], [class*="accept-all"], button[aria-label*="Accept"]'
  );
  if (btn) btn.click();
`)
```

### JS Alert/Confirm/Prompt Dialogs
**Do not trigger browser modal dialogs.** They block all subsequent extension messages. 
- Avoid clicking "Delete" buttons with JS confirmation dialogs
- Use `javascript_tool` to check for and bypass dialogs:
```javascript
window.confirm = () => true;   // auto-accept confirms
window.alert = () => {};        // suppress alerts
```

---

## CLAUDE.md Patterns for Chrome Sessions

Add these to your project's CLAUDE.md when doing browser automation work:

```markdown
## Chrome Browser Automation

- Always call `tabs_context_mcp` before any browser work — never reuse stale tab IDs
- Dismiss cookie banners via `javascript_tool` before interacting with the page
- Scope `read_page` with `filter="interactive"` first; only go broader if needed
- Do not trigger JS alert/confirm dialogs — they block the extension
- Use `gif_creator` for multi-step interactions the user should review
- When tools stop responding, check for MV3 service worker timeout and reload extension
- Permission mode for browser tasks: `ask` (default) or `follow_a_plan` for scripted flows
```

---

## Permission Modes

Set via `--permission-mode` flag or in CLAUDE.md:

| Mode | Behavior | Use when |
|------|----------|---------|
| `ask` | Prompts before each tool call | Default; exploratory work |
| `follow_a_plan` | Executes approved plan steps without re-prompting | Scripted, repeatable flows |
| `skip_all_permission_checks` | No prompts | Fully automated pipelines (use with care) |
