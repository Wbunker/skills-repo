# Claude Code Reference

## Table of Contents
- [Surfaces](#surfaces)
- [CLI Usage](#cli-usage)
- [Key CLI Flags](#key-cli-flags)
- [CLAUDE.md — Persistent Instructions](#claudemd--persistent-instructions)
- [Settings](#settings)
- [Hooks](#hooks)
- [Subagents](#subagents)
- [MCP Configuration](#mcp-configuration)
- [Plugins](#plugins)
- [Background Tasks](#background-tasks)
- [Built-in Slash Commands](#built-in-slash-commands)
- [Gotchas](#gotchas)
- [Prompting Tips](#prompting-tips)

---

## Surfaces

| Surface | Notes |
|---|---|
| Terminal CLI | `claude` — primary interface |
| VS Code extension | `anthropic.claude-code` from Marketplace. Inline diffs, @-mentions, plan review |
| JetBrains plugin | IntelliJ, PyCharm, WebStorm. Interactive diff viewing |
| Desktop app | macOS/Windows. Multiple sessions, scheduled tasks, Dispatch (send tasks from phone) |
| Web (`claude.ai/code`) | Browser-based, cloud sandbox, no local setup. Good for mobile |
| Mobile | Via Dispatch from desktop app, or web interface |

Install CLI:
```bash
curl -fsSL https://claude.ai/install.sh | bash   # macOS/Linux/WSL
brew install --cask claude-code                   # Homebrew
irm https://claude.ai/install.ps1 | iex           # Windows PowerShell
```

---

## CLI Usage

```bash
claude                          # interactive session
claude "do something"           # start with prompt
claude -p "query"               # non-interactive (print mode), exits after response
claude -c                       # continue most recent conversation
claude -r "<session-id>"        # resume session by ID or name
claude update                   # update to latest
claude auth login               # authenticate
claude agents                   # list/manage subagents
claude mcp                      # manage MCP servers
claude /bashes                  # interactive menu of background shells
```

---

## Key CLI Flags

| Flag | Description |
|---|---|
| `--model <id>` | Specify model (`sonnet`, `opus`, or full ID) |
| `--print` / `-p` | Non-interactive mode |
| `--output-format json\|stream-json\|text` | Structured output |
| `--max-turns N` | Limit agentic turns |
| `--max-budget-usd N` | Spending cap |
| `--allowedTools "Bash,Edit"` | Pre-approve tools |
| `--disallowedTools "Write"` | Block tools |
| `--permission-mode default\|acceptEdits\|auto\|plan\|bypassPermissions` | Permission mode |
| `--system-prompt` / `--append-system-prompt` | Customize system prompt |
| `--mcp-config ./mcp.json` | Load MCP servers from file |
| `--agent <name>` | Specify subagent for session |
| `--worktree` / `-w <name>` | Isolated git worktree session |
| `--chrome` | Enable Chrome browser integration |
| `--channels` | Enable Channels (Telegram/Discord/etc.) |
| `--dangerously-skip-permissions` | Bypass all approval prompts (use in sandboxed/scoped contexts only) |
| `--bare` | Minimal mode (skip hooks/plugins/MCP) |
| `--effort low\|medium\|high\|xhigh\|max` | Reasoning effort |
| `--remote "task"` | Create new web session on claude.ai |
| `--teleport` | Pull a web session into local terminal |

---

## CLAUDE.md — Persistent Instructions

Claude reads `CLAUDE.md` at session start as always-on instructions.

Locations (all loaded, in order):
- `~/.claude/CLAUDE.md` — user-level, applies to all projects
- `<project-root>/CLAUDE.md` — project-level (committable)
- `.claude/CLAUDE.md` — alternative project location
- `CLAUDE.local.md` — personal overrides, gitignored

Auto-memory: Claude builds context automatically during sessions (build commands, patterns, etc.).

---

## Settings

Four scopes (highest → lowest precedence):
1. **Managed** — org-deployed via MDM, plist, registry, or `managed-settings.json`
2. **Command line** — session-only flags
3. **Local** — `.claude/settings.local.json` (gitignored)
4. **Project** — `.claude/settings.json` (commit to repo)
5. **User** — `~/.claude/settings.json`

Key fields:
```json
{
  "permissions": {
    "allow": ["Bash(npm run test *)", "Read(~/.zshrc)"],
    "deny": ["Bash(curl *)"]
  },
  "env": {"MY_VAR": "value"},
  "companyAnnouncements": []
}
```

MCP config: `~/.claude.json` (user/local scope), `.mcp.json` (project scope).

---

## Hooks

Shell scripts, HTTP endpoints, LLM prompts, or subagents that fire automatically at lifecycle events.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx eslint --fix",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

**Exit codes from hook scripts:**
| Code | Meaning |
|---|---|
| 0 | Allow; parse stdout JSON if present |
| 2 | Block; stderr sent to Claude as feedback |
| Other | Non-blocking error; shown in transcript |

**Key lifecycle events:** `SessionStart`, `SessionEnd`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `Stop`, `SubagentStart`, `SubagentStop`, `FileChanged`, `ConfigChange`, `CwdChanged`, `Notification`, `PreCompact`, `PostCompact`

`FileChanged` uses OS-native inotify (Linux) / FSEvents (macOS). Matcher is basename-only.

`Stop` hook with `type: "agent"` spawns a subagent quality gate. Return `{"ok": false, "reason": "..."}` to keep Claude working, `{"ok": true}` to allow stopping. Check `stop_hook_active` to prevent infinite loops.

---

## Subagents

Specialized agents defined in Markdown with YAML frontmatter.

Locations:
- `~/.claude/agents/` — user-level (all projects)
- `.claude/agents/` — project-level (committable)

Key frontmatter fields:
```yaml
name: my-agent
description: When to invoke this agent (used for routing)
tools: [Read, Glob, Grep]          # restrict available tools
disallowedTools: [Bash]
model: haiku                        # sonnet/opus/haiku/inherit/full-ID
permissionMode: acceptEdits
maxTurns: 20
skills: [my-skill]
hooks: ...
memory: [user, project, local]      # persistent memory sources
background: true                    # run in background
isolation: worktree                 # isolated git worktree
```

Subagents cannot spawn other subagents. For parallel communicating agents, use Agent Teams (`--teammate-mode`).

---

## MCP Configuration

```bash
claude mcp add <name> <command>   # add stdio server
claude mcp add --url <url>        # add HTTP server
claude mcp list
claude mcp remove <name>
```

Or in `.mcp.json`:
```json
{
  "mcpServers": {
    "playwright": {"command": "npx", "args": ["@playwright/mcp@latest"]},
    "my-api": {"url": "https://my-server.example.com/sse"}
  }
}
```

MCP tool names in hooks/settings: `mcp__<server-key>__<tool-name>`.

Official MCP registry: `https://api.anthropic.com/mcp-registry/v0/servers`

**Skills vs. MCP — when to use which:**

| Use | Why |
|---|---|
| **Skill** | Giving Claude a workflow, pattern, or domain knowledge (advisory, readable, auditable) |
| **MCP server** | Live data or actions — query current DB state, fetch open GitHub issues, post to Slack |

Prefer skills when in doubt. A skill is a markdown file you can read and audit. An MCP server is a black box. Rule of thumb: if the information could be written down once and remain valid for days, it's a skill; if it needs to be fetched fresh every time, it's MCP.

---

## Plugins

Plugins (public beta) bundle MCPs, skills, hooks, and slash commands into a single installable package. The official Anthropic marketplace (`claude-plugins-official`) is available by default; third-party plugins are also supported.

```bash
/plugin                              # browse installed plugins and Discover tab
/plugin install <name>@<publisher>   # install a plugin
/plugin list                         # list installed plugins
/plugin update --all                 # update all plugins
```

Browse the catalog at `claude.com/plugins`.

**Official setup plugin** — `claude-code-setup@claude-plugins-official` reads your project (package.json, directory structure, existing `.claude/` config) and generates tailored recommendations for MCPs, skills, hooks, subagents, and slash commands. It is read-only and makes no changes itself.

```bash
/plugin install claude-code-setup@claude-plugins-official
# Then prompt:
> recommend automations for this project
```

**Security note:** Plugins can load remote MCP servers and local software. Review what a third-party plugin installs before running it; official (`claude-plugins-official`) plugins pass Anthropic's publishing checks.

---

## Background Tasks

Run commands without blocking the session:

- Use `run_in_background: true` on Bash — returns `bash_id`
- **`/bashes`** — interactive menu of all running/completed shells
- `BashOutput(bash_id)` — read incremental output (optional `filter` regex)
- `KillShell(shell_id)` — terminate a background shell
- `Ctrl+B` during execution — move to background (press twice in tmux)

Common use: start a dev server in background, then have Claude read its logs and fix errors.

**Known issues:** Token exhaustion after `KillShell` (issues #11716, #12302); stale "running" status (#13091, #14049).

---

## Built-in Slash Commands

Type `/` in any session to see all available commands. Commands marked **[cloud]** run in a remote sandbox; all others run locally.

### Code Review

| Command | What it does | Cost | Requirements |
|---|---|---|---|
| `/review` | Single-pass local review; prompts to pick PR, branch, or files | Normal usage | Git repo |
| `/ultrareview` | **[cloud]** Multi-agent review — each agent independently reproduces and verifies findings before reporting | 3 free runs (Pro/Max), then $5–$20/review | v2.1.86+, Claude.ai auth, extra usage enabled |
| `/security-review` | Security-focused scan of pending changes on current branch | Normal usage | Git repo |

**`/ultrareview` details:**
- Runs in a remote cloud sandbox, not your local session
- Launches multiple parallel agents that each reproduce findings — reduces false positives vs `/review`
- Takes 5–10 min vs seconds for `/review`
- Shows a confirmation dialog (scope, remaining free runs, estimated cost) before any paid run
- Not available on Amazon Bedrock, Google Cloud Vertex AI, Microsoft Foundry, or orgs with Zero Data Retention
- Team/Enterprise plans get 0 free runs (billed immediately)
- Setup: `claude --version` (need v2.1.86+) → `/login` → `/extra-usage` to enable billing

**When to use each:**
- `/review` — daily iteration, quick feedback while working
- `/ultrareview` — pre-merge gate on auth, payments, API endpoints, or any high-risk change

### Planning

| Command | What it does | Requirements |
|---|---|---|
| `/plan [description]` | Enter plan mode locally | None |
| `/ultraplan <prompt>` | **[cloud]** Draft implementation plan in a web session; review in browser then execute remotely or pull to terminal | v2.1.91+, Claude.ai auth, GitHub repo |

### Session & Context

| Command | What it does |
|---|---|
| `/clear` | New conversation, empty context (previous session available via `/resume`) |
| `/compact [instructions]` | Summarize conversation to free context; pass focus instructions optionally |
| `/context` | Visualize context usage as colored grid with optimization suggestions |
| `/resume [session]` | Resume session by ID/name; opens picker without argument |
| `/branch [name]` | Fork current conversation; preserves original for `/resume` |
| `/rename [name]` | Rename current session |
| `/btw <question>` | Ask a side question without adding it to the main conversation |
| `/voice` | Enable push-to-talk input — hold space to speak, release to submit |

### Model & Performance

| Command | What it does | Notes |
|---|---|---|
| `/model [name]` | Switch model mid-session | Opens picker without argument |
| `/effort [level]` | Set effort: `low` / `medium` / `high` / `xhigh` / `max` | `xhigh` is the current default across all plans; also settable via `--effort` flag |
| `/fast [on\|off]` | Toggle Fast mode for Opus (2.5× faster, higher cost) | Requires extra usage; $30/$150 per MTok input/output |

### Configuration & Permissions

| Command | What it does |
|---|---|
| `/config` | Open settings UI (theme, model, editor mode, preferences) |
| `/permissions` | Manage allow/ask/deny rules for tools interactively |
| `/add-dir <path>` | Add a working directory for file access this session |
| `/keybindings` | Open or create keybindings config file |
| `/terminal-setup` | Configure Shift+Enter and shortcuts (needed for VS Code, Alacritty, Warp) |
| `/statusline` | Configure the status bar UI |

### Account & Billing

| Command | What it does |
|---|---|
| `/login` | Authenticate with Claude.ai account |
| `/logout` | Sign out |
| `/extra-usage` | Enable/configure extra usage budget (required for `/ultrareview`, `/fast`) |
| `/upgrade` | Open upgrade page |

### Diagnostics

| Command | What it does |
|---|---|
| `/doctor` | Diagnose installation; press `f` to auto-fix issues |
| `/status` | Show version, model, account, connectivity (works while Claude is responding) |
| `/cost` | Token usage stats for this session (API customers) |
| `/stats` | Daily usage, session history, streaks, model preferences |
| `/usage` | Plan limits and rate limit status |
| `/release-notes` | Browse changelog in interactive version picker |

### Integrations & Remote

| Command | What it does |
|---|---|
| `/plugin` | Browse, install, update, and remove plugins (MCPs + skills + hooks bundled) |
| `/mcp` | Manage MCP server connections and OAuth |
| `/ide` | Manage IDE integrations |
| `/install-github-app` | Set up Claude GitHub Actions for a repo |
| `/install-slack-app` | Install Claude Slack app (opens OAuth flow) |
| `/teleport` / `/tp` | Pull a claude.ai web session into local terminal |
| `/remote-control` / `/rc` | Make current session available for remote control from claude.ai |
| `/autofix-pr [prompt]` | **[cloud]** Watch a PR and push fixes when CI fails or reviewers comment |
| `/desktop` / `/app` | Continue current session in Claude Code Desktop |

---



- **`CLAUDE.md` is always loaded** — keep it concise; every session pays the token cost.
- **Settings scopes are additive** — `deny` rules from any scope are honored; most-specific wins for `allow`.
- **Hooks don't fire at `max_turns`** — session ends abruptly before any hook can execute.
- **`FileChanged` matcher is basename-only** — `"*.ts"` won't work; use `PostToolUse` on `Edit|Write` for file type filtering.
- **Subagents can't spawn subagents** — if you need nested delegation, restructure using Agent Teams.
- **`--dangerously-skip-permissions`** bypasses all prompts — only use in sandboxed environments or with tightly scoped task descriptions.
- **`--effort` set via `settings.json` or env vars can be silently overridden** (Issue #30726). The CLI flag is the only reliable method. Use a shell alias: `alias claude="claude --effort max"`. The `/effort` slash command is also affected.
- **Adaptive thinking (Feb 2026)**: Claude Code switched from defaulting to high-effort reasoning to "adaptive thinking" — the model self-selects how much to think per task. This caused a documented 67–75% drop in reasoning depth on complex tasks. Mitigate with `--effort max` and/or the `ultrathink` keyword.

---

## Prompting Tips

**Context management** — Do `/compact` manually at around 50% context usage rather than waiting for automatic compaction. At 50% you control what gets preserved; at 90% the automatic summarizer discards whatever it deems low-priority. Pass a focus instruction so the summary retains what matters:

```
/compact preserve: list of modified files, current test status, and any unresolved issues
```

Add a standing compaction instruction to your `CLAUDE.md` so the summarizer always knows what to keep:
```
When compacting, always preserve: the list of modified files, current test status, and any unresolved issues.
```

**`ultrathink` keyword** — Prepend `ultrathink` to any prompt in the Claude Code terminal to trigger a 31,999-token thinking budget for that turn:
```
ultrathink refactor this auth module to use parameterized queries
```
- Works in Claude Code terminal only — not the web interface or API
- Free (counts toward normal usage, not extra billing)
- Best for: architecture decisions, complex debugging, security review, any multi-file reasoning task

**CLAUDE.md evidence rule** — Add this to force read-before-claim behavior (counters shallow "edit-first" patterns):
```
For every claim or finding, quote the exact code that proves it.
If you cannot quote the actual code, say "I need to read this file first" instead of making the claim.
```
