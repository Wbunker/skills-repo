# Claude Code Reference

## Table of Contents
- [Surfaces](#surfaces)
- [CLI Usage](#cli-usage)
- [Key CLI Flags](#key-cli-flags)
- [CLAUDE.md, Rules & Memory](#claudemd-rules--memory)
- [Settings](#settings)
- [Hooks](#hooks)
- [Subagents](#subagents)
- [Dynamic Workflows](#dynamic-workflows)
- [MCP Configuration](#mcp-configuration)
- [Plugins](#plugins)
- [Background Tasks](#background-tasks)
- [Built-in Slash Commands](#built-in-slash-commands)
- [Mobile Push Notifications](#mobile-push-notifications)
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

## CLAUDE.md, Rules & Memory

Two systems carry knowledge across sessions, both loaded at session start: **CLAUDE.md / `.claude/rules/`** (instructions you write) and **auto memory** (notes Claude writes itself). Both are *advisory context, not enforced* — use hooks for anything that must happen every time.

CLAUDE.md locations (concatenated, broadest → narrowest; narrowest read last):
- Managed policy (IT-deployed, can't be excluded) → `~/.claude/CLAUDE.md` (user) → `./CLAUDE.md` or `./.claude/CLAUDE.md` (project) → `./CLAUDE.local.md` (personal, gitignore it)
- Ancestor-directory CLAUDE.md files load in full at launch; subdirectory ones load on demand.

Effective-instruction rules of thumb: keep it **under 200 lines** (bloat → ignored rules), be specific and verifiable, group with headers/bullets, add `IMPORTANT`/`YOU MUST` to tune adherence, and run `/init` to bootstrap. Move sometimes-relevant or path-specific content to **skills** or **`.claude/rules/`** (path-scoped). `#` / "remember…" saves to auto memory; "add to CLAUDE.md" edits CLAUDE.md; `/memory` lists and edits what's loaded.

→ CLAUDE.md, `@` imports, auto memory, org/monorepo controls, troubleshooting: [claude-memory.md](claude-memory.md)
→ The `.claude/rules/` directory (always-on + path-scoped rules): [claude-rules.md](claude-rules.md)

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

Subagents cannot spawn other subagents. For parallel communicating agents, use Agent Teams (`--teammate-mode`). To orchestrate **tens to hundreds** of subagents from a rerunnable script (the plan lives in code, not the conversation), use [Dynamic Workflows](dynamic-workflows.md).

---

## Dynamic Workflows

A JavaScript orchestration script Claude writes for a task and runs in the background, coordinating dozens–hundreds of subagents across phases with cross-checking/adversarial verification — intermediate results stay in script variables, so context holds only the final answer. Trigger with the `ultracode` keyword (single task), `/effort ultracode` (session-wide autonomous, `xhigh`-capable models only), or a saved/bundled command like `/deep-research`. Manage runs in the `/workflows` TUI; save a run's script (`s`) to `.claude/workflows/` or `~/.claude/workflows/` and it becomes `/<name>`. Caps: 16 concurrent / 1,000 total agents per run. Research preview, v2.1.154+.

**Key surprise:** workflow subagents always run in `acceptEdits` mode regardless of your session's permission mode — file edits are auto-approved.

→ Full reference (triggering, approval per permission mode, TUI keys, save/reuse + `args`, limits, permissions, cost control, disabling): [dynamic-workflows.md](dynamic-workflows.md)

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
| `/ultrareview` | **[cloud]** Two-stage multi-agent review — Find fleet hunts bugs, Verify fleet reproduces each finding before reporting | ~$5–$20/run (free tier ended May 5, 2026) | v2.1.111+, Claude.ai auth, extra usage enabled |
| `/security-review` | Security-focused scan of pending changes on current branch | Normal usage | Git repo |

**`/ultrareview` details:**
- Runs in a remote cloud sandbox, not your local session
- **Two-stage architecture:** a Find fleet (5 agents for small PRs, up to 20 for 1000+ line diffs) hunts bugs by specialty — logic/off-by-ones, injection/auth gaps, N+1/unbounded reads, pattern violations, test coverage holes. A separate Verify fleet tries to independently reproduce each finding; only reproduced bugs reach your terminal. Published false-positive rate: <1%.
- Takes 10–20 min (scales with diff size) vs seconds for `/review`
- Shows a confirmation dialog (scope, estimated cost) before each run
- Not available on Amazon Bedrock, Google Cloud Vertex AI, Microsoft Foundry, or orgs with Zero Data Retention
- Team/Enterprise plans are billed immediately (no free runs)
- Free tier (3 runs for Pro/Max) ended May 5, 2026 — every run is now metered
- Setup: `claude --version` (need v2.1.111+) → `/login` → `/extra-usage` to enable billing

**Scoping:**
```
/ultrareview                    # reviews current branch vs main (not full codebase)
/ultrareview HEAD~5..HEAD       # specific commit range
/ultrareview src/auth/          # specific directory
```

**Known issues:**
- **#50029** — empty findings on branches above an unspecified diff-size ceiling (large monorepos)
- **#52780 / #55062** — rate-limit failures silently consume budget without delivering a report; do not retry immediately, and do not run two `/ultrareview` in parallel from the same account
- **#54671** — no-arg form reviews branch diff vs main, not the full codebase; developers expect a whole-repo review and are surprised by the scope

**When to use each:**
- `/review` — daily iteration, quick feedback while coding (free, seconds)
- `/ultrareview` — pre-merge gate on diffs over 1000 lines, or anything touching auth, money, or model loading; ~$14/run average
- Layer: `/review` while iterating → CodeRabbit on every push for style → `/ultrareview` selectively before high-risk merges

### Planning

| Command | What it does | Requirements |
|---|---|---|
| `/plan [description]` | Enter plan mode locally | None |
| `/ultraplan <prompt>` | **[cloud]** Draft implementation plan in a web session; review in browser then execute remotely or pull to terminal | v2.1.91+, Claude.ai auth, GitHub repo |

### Workflows (dynamic, multi-agent orchestration)

| Command | What it does | Requirements |
|---|---|---|
| `/workflows` | List running/completed [dynamic workflows](dynamic-workflows.md); open the progress TUI to drill in, pause (`p`), stop (`x`), restart (`r`), or save (`s`) a run | v2.1.154+ |
| `/deep-research <question>` | Bundled workflow: fans out web searches, cross-checks sources, votes on each claim, returns a cited report | WebSearch tool |
| `/<saved-name> [args]` | Run a workflow you saved from `/workflows` (`s`) into `.claude/workflows/` (project) or `~/.claude/workflows/` (personal) | — |

Trigger a one-off workflow with the `ultracode` keyword in a prompt, or `/effort ultracode` for session-wide autonomous orchestration. See [dynamic-workflows.md](dynamic-workflows.md).

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
| `/effort [level]` | Set effort: `low` / `medium` / `high` / `xhigh` / `max` / `ultracode` | `xhigh` is the current default across all plans; also settable via `--effort` flag. `ultracode` = `xhigh` + automatic [dynamic-workflow](dynamic-workflows.md) orchestration (xhigh-capable models only) |
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
| `/mobile` | Display QR code for downloading the Claude mobile app |
| `/autofix-pr [prompt]` | **[cloud]** Watch a PR and push fixes when CI fails or reviewers comment |
| `/desktop` / `/app` | Continue current session in Claude Code Desktop |

---

## Mobile Push Notifications

Requires Claude Code v2.1.110+ and the Claude mobile app (iOS or Android) signed in with the same account.

**How it works:** Push notifications are built on top of Remote Control — without an active Remote Control session, no pushes fire. The session stream travels through Anthropic's API (HTTPS, port 443 outbound); no inbound ports are opened on your machine.

**Two push triggers:**
1. **Task completes** — Claude finishes and is ready to report back
2. **Needs input** — Claude hits a decision point and waits for you

**Setup:**
```bash
claude --version          # must be v2.1.110+
claude update             # update if behind
```
1. Install the Claude mobile app; sign in with the same account used for Claude Code.
2. Grant notification permission (iOS: Settings → Notifications → Claude; Android: exempt Claude from battery optimization).
3. In Claude Code, run `/config` → enable **Push when Claude decides**.

**Starting Remote Control (three options):**
```bash
claude remote-control      # server mode — stays running, accepts multiple connections
claude --remote-control    # start session with remote control enabled (recommended)
/remote-control            # enable inside an active session
```
For remote control on every session without the flag: `/config` → **Enable Remote Control for all sessions → true**.

**One session per process** (outside server mode): two Claude Code instances each get their own remote session; they don't interfere and can't be viewed together from one phone view. Use `claude remote-control` (server mode) to manage parallel sessions.

**Prompt-triggered notifications:** Tell Claude exactly when to push:
```
Review calculator.py and fix all issues, then run tests.
Notify me when all tests are passing and the refactor is complete.
```
For troubleshooting, test with: `Print hello world then notify me when done` — switch to your phone immediately after submitting.

---

## Gotchas

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
