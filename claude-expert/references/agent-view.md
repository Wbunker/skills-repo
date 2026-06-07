# Agent View & Background Sessions

Run and manage many Claude Code sessions from one screen. Research preview; requires **Claude Code
v2.1.139+** (Pro, Max, Team, Enterprise, API). Official docs: `code.claude.com/docs/en/agent-view`.

## What it is
**Agent view** (`claude agents`) is a single terminal dashboard listing all your **background
sessions** — what's running, what needs input, what's done. A background session is a *full* Claude
Code conversation that keeps running with **no terminal attached**; you dispatch it, peek, reply, and
attach when you want the full conversation. Sessions run across all your projects by default.

## Opening it
- `claude agents` — open the dashboard (full-screen TUI; `Esc` returns to the shell, sessions keep running).
- `claude agents --cwd ~/proj` — scope the list to one directory tree (v2.1.141+).
- Press **`←` on an empty prompt** in *any* session — backgrounds it and opens agent view with that row
  selected. (Toggle via `/config` → `leftArrowOpensAgents`.)

## Dispatching background sessions (three ways, same result)
- **From agent view:** type a prompt in the bottom input, `Enter` → new session. Each prompt starts a
  *new* session (not a follow-up). `Shift+Enter` dispatches **and** attaches. `@<repo>`/agent name as
  first word targets a subagent; name it with `--name`.
- **From inside a session:** `/background` (alias `/bg`). Pass a final instruction: `/bg run the test
  suite and fix failures`. Launch flags (MCP servers, settings, fallback model, permission mode) carry
  through.
- **From the shell:** `claude --bg "investigate the flaky test"` → prints a session ID + management
  commands. Combine with `--agent code-reviewer`, `--name`, `--model`, etc.

It prints, e.g.:
```
backgrounded · 7c5dcf5d · flaky-test-fix
  claude agents             list sessions
  claude attach 7c5dcf5d    open in this terminal
  claude logs 7c5dcf5d      show recent output
  claude stop 7c5dcf5d      stop this session
```

## Reading session state
Icons combine a **process marker** with a **status color**:
- Process marker: **`✻`** = process alive (reply immediately) · **`∙`** = process exited (you can still
  peek/reply/attach — Claude restarts from where it left off) · **`✢`** = a `/loop` session sleeping
  between iterations (shows run count + countdown).
- Status: animated = working; **yellow** = needs your input (permission/answer); dimmed = idle; **green**
  = done; **red** = errored; **grey** = stopped (`Ctrl+X` or `claude stop`).
Grouping (default) by state: **Ready for review** (has an open PR) · **Needs input** · **Working** ·
**Completed** (finished/failed/stopped together). PR rows show the PR link + CI status.

## Peek & reply (the headline feature)
- Select a row, press **`Space`** → peek panel shows the session's latest output or the question it's
  blocked on (not the full transcript). `↑`/`↓` peek adjacent rows; `→` attaches.
- Type a reply + `Enter` to answer **without leaving agent view**. For multiple-choice prompts, press a
  **number key**. Press **`Tab`** to fill a suggested reply you can edit. Prefix with **`!`** to send a
  Bash command. (Voice dictation works here from v2.1.145+.)

## Attaching / detaching
- `Enter` or `→` attaches → full interactive session (always fullscreen; Claude posts a recap of what
  happened while you were away). Scroll with `PgUp`/`PgDn`; `Ctrl+O` for transcript mode.
- Detach (session keeps running): **`←` on empty prompt**, `Ctrl+Z` (if a dialog has focus),
  double `Ctrl+C`/`Ctrl+D`, or `/exit`. To **end** a session from inside it: `/stop`.

## Keyboard shortcuts
| Key | Action |
|---|---|
| `↑`/`↓` | Move selection · `Enter`/`→` attach (or dispatch if input has text) |
| `Space` | Open/close peek panel |
| `Shift+Enter` | Dispatch and attach immediately |
| `Ctrl+S` | Toggle grouping: state ↔ directory |
| `Ctrl+T` | Pin/unpin (keeps the process running while idle) |
| `Ctrl+R` | Rename session · `Ctrl+G` edit prompt in `$EDITOR` |
| `Shift+↑`/`Shift+↓` | Reorder |
| `Ctrl+X` | Stop; press again within 2 s to **delete** (on a group header: deletes the group) |
| `Esc` | Close peek / clear input / exit · `Ctrl+C` clear input, twice to exit |

## Filtering
Type in the dispatch input: **`a:<name>`** (sessions running that agent) · **`s:<state>`** (e.g.
`s:working`, `s:blocked`) · **`#<number>` or PR URL** (the session on that PR).

## Run a shell command as a job (not a Claude session)
Prefix the dispatch input with **`!`** (e.g. `! pytest -x`), or from the shell `claude --bg --exec
'pytest -x'`. Runs PTY-backed, no model invoked; output via attach/peek/`claude logs <id>`; row
auto-cleans ~5 min after exit (output is in-memory only).

## How file edits are isolated (worktrees)
Before editing files, a background session moves into an isolated git worktree under
**`.claude/worktrees/`**, so parallel sessions read the same checkout but write to their own. Skipped
when already in a linked worktree, when not a git repo (and no `WorktreeCreate` hook), or for writes
outside the working dir. Disable per-repo with `worktree.bgIsolation: "none"` in `.claude/settings.json`
(v2.1.143+).
- **Deleting a session in agent view (`Ctrl+X` twice) deletes its Claude-created worktree, including
  uncommitted changes** — merge/push first. Deleting from the shell with `claude rm` *keeps* a dirty
  worktree and prints its path. A worktree you created yourself is always left in place.

## Hosting & persistence (the supervisor)
A per-user **supervisor process** runs sessions independently of any terminal — close agent view, the
shell, or start a new session and the work continues. State persists on disk under `~/.claude/` through
auto-updates and supervisor restarts, and across machine **sleep** (processes resume on wake). A full
**shutdown stops** running sessions; recover them afterward with `claude respawn --all`. Permission
mode, model, and effort persist across supervisor restarts.

## Model, permissions, effort for dispatched sessions
- Dispatched sessions use the agent view header's model (your `model` setting) and the directory's
  `defaultMode`; backgrounding an existing session with `/bg`/`←` keeps its current mode/model.
- Override defaults when opening: `claude agents --permission-mode plan --model opus --effort high
  --agent <name>`. Per-session model: `claude --bg --model …`, or attach → `/model` → press `s`.
- Row summaries are short Haiku-class requests billed under your normal usage terms.

## Limitations (research preview)
- **Rate limits/usage:** every background session draws from the same quota as interactive ones —
  N parallel agents burn quota ~N× faster.
- **Local only:** sessions run on your machine; shutdown stops them (use `claude respawn --all`).
- **Worktree deletion is destructive** for uncommitted changes (see above).
- Interface/shortcuts may change; expect rough edges.

## Related
- Compare with subagents / agent teams / worktrees: see the Agent SDK refs and `code.claude.com/docs/en/agents`.
- Background **bash tasks** (in-session `&`/Ctrl-b) are different from background **sessions** — see the
  "Background Tasks" section of `claude-code.md`.
