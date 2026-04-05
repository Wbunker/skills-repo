---
name: claude-in-chrome quick mode
description: Quick Mode compact command language for low-latency browser actions
type: reference
---

# Quick Mode Command Language

Quick Mode provides a compact single-letter command protocol for lower-latency browser automation, avoiding full JSON tool call overhead per action.

## Enabling Quick Mode

Pass the beta flag when launching:
```
--beta fast-mode-2026-02-01
```

Or set in the session context before automation begins.

## Command Syntax

```
<COMMAND> [args]  [--effort <level>]
```

`--effort` controls how much the inner planner works: `low`, `medium` (default), `high`.

## Command Reference

| Letter | Full name | Arguments | Example |
|--------|-----------|-----------|---------|
| `C` | Click | `x y` (screen coords) | `C 540 320` |
| `T` | Type text | `<text>` | `T hello world` |
| `K` | Key press | `<key>` (xdotool names) | `K Return`, `K ctrl+a` |
| `J` | JavaScript | `<code>` | `J document.title` |
| `S` | Screenshot | — | `S` |
| `N` | Navigate | `<url>` | `N https://example.com` |
| `R` | Read page | `[filter]` | `R interactive` |
| `F` | Find element | `<description>` | `F submit button` |
| `W` | Wait | `<ms>` | `W 500` |

## Batching Commands

Send multiple commands in a single call with newline separation:
```
T search term
K Return
W 800
S
```

This executes sequentially in one round-trip.

## When to Use Quick Mode

- High-frequency, repetitive interactions (scraping, form filling loops)
- When each individual action is clear and doesn't require re-reading the page
- Scripted flows where the DOM structure is already known

## When NOT to Use Quick Mode

- Initial page exploration (use `read_page` + `find` for accuracy)
- When actions depend on dynamic ref IDs discovered at runtime
- Debugging sessions where you need full tool output for inspection

## Effort Levels

| Level | Use case |
|-------|---------|
| `low` | Simple, obvious actions with known coordinates |
| `medium` | Standard interactions (default) |
| `high` | Complex navigation, ambiguous targets, multi-step sequences |

## Example: Login Flow

```
N https://app.example.com/login
W 1000
R interactive
# From read_page output, identify email field ref_id
T user@example.com  --effort low
K Tab
T mypassword  --effort low
F submit button  --effort low
C <x> <y>
S
```
