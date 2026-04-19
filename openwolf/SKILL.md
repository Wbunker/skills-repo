---
name: openwolf
description: Expert on OpenWolf, the open-source Claude Code middleware that reduces token usage via project indexing and hook-based file read interception. Use when helping users install, configure, troubleshoot, or understand OpenWolf's .wolf/ directory, hooks, anatomy.md, cerebrum.md, CLI commands, or token savings workflow.
---

# OpenWolf

OpenWolf is open-source middleware for Claude Code (github.com/cytostack/openwolf). It installs six Node.js hook scripts that intercept Claude's file read/write lifecycle, maintaining a persistent project index (`anatomy.md`) and learning memory (`cerebrum.md`) in a `.wolf/` directory. Result: 65.8% average token reduction across 20 projects by preventing redundant file reads and short-circuiting reads with cached summaries.

## Reference Files

Load on demand based on the question:

- **setup-and-architecture.md** — Install steps, Node.js requirements, what `openwolf init` does, hook registration in `.claude/settings.json`, overall data-flow diagram, token estimation methodology. Load for setup, "how does it work", or architecture questions.
- **wolf-directory.md** — Every file in `.wolf/`: purpose, format, when updated, and the markdown-vs-JSON state principle. Load when a user asks about a specific file, wants to edit `.wolf/` manually, or is debugging stale state.
- **hooks-reference.md** — All six hooks: event type, script name, behavior, inputs/outputs, timeout, and failure mode. Load for hook debugging, understanding what fires when, or customizing hook logic.
- **cli-and-config.md** — Full CLI command reference (`init`, `status`, `scan`, `dashboard`, `daemon`, `cron`, `designqc`, `bug`, `update`, `restore`), `config.json` schema, exclude patterns, cron schedules, dashboard port. Load for CLI questions or config tuning.
- **gotchas.md** — Licensing (AGPL-3.0), Node.js-only hooks, cerebrum compliance limits, token estimation accuracy, stale anatomy, large directory exclusions, Claude Code exclusivity, daemon/PM2 setup. Load when troubleshooting or evaluating adoption risk.

## Quick-Start Decision Flow

- **"How do I install?"** → setup-and-architecture.md
- **"What is anatomy.md / cerebrum.md / buglog.json?"** → wolf-directory.md
- **"How do hooks work / why didn't a hook fire?"** → hooks-reference.md
- **"What CLI commands exist / how do I configure exclusions?"** → cli-and-config.md
- **"Why isn't it saving tokens / weird behavior / licensing concern"** → gotchas.md

## Key Facts

- Install: `npm install -g openwolf` then `openwolf init` inside any project — works for any language stack
- Requires Node.js 20+ globally, even in non-JS projects
- Hooks register in `.claude/settings.json` (Claude Code's hook config file)
- `.wolf/` directory lives at the project root alongside `.claude/`
- Hooks are pure Node.js file I/O — no network calls, no extra AI inference, no external dependencies
- Hooks warn but never block operations; each has a 5–10 second timeout
- anatomy.md is the file index: one-line description + token estimate per file
- cerebrum.md has four sections: User Preferences, Key Learnings, Do-Not-Repeat, Decision Log
- 71% of file reads in measured sessions were redundant (same file, same session)
- Token estimation uses character-to-token ratios (code 3.5, prose 4.0, mixed 3.75) — accurate within ~15%
- `openwolf scan` refreshes anatomy manually; daemon rescans every 6 hours automatically
- Dashboard at `http://localhost:18791` via `openwolf dashboard`
- AGPL-3.0 license — commercial embedding requires license review
- Only works with Claude Code — not compatible with Cursor, Windsurf, or GitHub Copilot
