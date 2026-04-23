# Claude in Chrome

Operational guide for the `mcp__claude-in-chrome__*` tool suite. Focuses on what official docs omit: tool selection, token hygiene, and session stability.

## Requirements

- Google Chrome or Microsoft Edge (not Brave, Arc, other Chromium; not WSL)
- Claude in Chrome extension (Chrome Web Store), v1.0.36+
- Claude Code v2.0.73+
- Direct Anthropic plan (Pro/Max/Team/Enterprise) — not available on Bedrock/Vertex/Foundry

Enable with `claude --chrome` or `/chrome` in session. Toggle "Enabled by default" via `/chrome`.

## Session Startup Checklist

1. Call `tabs_context_mcp` — get fresh tab IDs (never reuse IDs from prior sessions)
2. Dismiss any cookie banners via `javascript_tool` before interacting
3. Choose permission mode: `ask` (exploratory) / `follow_a_plan` (scripted) / `skip_all_permission_checks` (fully automated)
4. Pre-suppress JS dialogs if the page uses `confirm`/`alert`:
   ```javascript
   window.confirm = () => true; window.alert = () => {};
   ```

## Tool Selection — Decision Tree

```
Need to understand page structure?
  → read_page(filter="interactive")          # always start here
  → if still too large: read_page(ref_id=<container>)

Need to read text content only?
  → get_page_text(selector="main")          # cheaper than read_page

Element location unclear after reading tree?
  → find("description of element")          # uses inner LLM — has latency

Fill a form field?
  → form_input(ref_id, value)               # always prefer over computer

Click a button?
  → get ref_id from read_page → javascript_tool click
  → fallback: computer(action="click", coordinate=[x,y])

Need visual verification or canvas?
  → computer(action="screenshot")

Debug JS errors?
  → read_console_messages(pattern="error|warn")

Debug network calls?
  → read_network_requests(pattern="/api/")
```

## Core Token Hygiene Rules

- **Never** call `read_page` without `filter` or `ref_id` on complex pages — dumps entire `<main>`, 20k+ tokens
- **Always** pass `pattern` to `read_console_messages` — unfiltered console output is huge
- **Minimize** `computer` screenshots — batch actions, verify at end, not between each step
- **Scope** `get_page_text` with `selector` or `priority_selectors` on long pages

## Reference Files

Load only what's relevant:

| File | When to load |
|------|-------------|
| [chrome-tools.md](chrome-tools.md) | Full parameter schemas for all 21 tools, tool selection matrix |
| [chrome-context.md](chrome-context.md) | ref ID system internals, MV3 timeout mitigation, CLAUDE.md patterns, permission modes |
| [chrome-quick-mode.md](chrome-quick-mode.md) | Compact single-letter command language for low-latency scripted flows |

## Common Failure Modes

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Tools return stale/wrong data | MV3 service worker timed out | Reload extension or re-open panel |
| "Invalid tab ID" error | Stale tab ID from prior session | Call `tabs_context_mcp` to refresh |
| Extension stops responding | JS alert/confirm dialog is blocking | Manually dismiss in browser; pre-suppress with JS |
| `read_page` returns 50k+ chars | No scoping | Add `filter="interactive"` or `ref_id` |
| `find` is slow | Using it for obvious targets | Use `read_page` → scan ref IDs directly |
