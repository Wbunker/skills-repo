# Hooks

Source: Anthropic official documentation (code.claude.com/docs/en/hooks, 2026)

## Table of Contents

- [Hooks vs. CLAUDE.md](#hooks-vs-claudemd) — when to use hooks over instructions
- [Hook Exit Code Semantics](#hook-exit-code-semantics) — exit 0 / 2 / other; blocking table by event
- [updatedInput — Rewriting Tool Parameters](#hook-exit-code-semantics) — transform what Claude was about to do
- [The /hooks Command](#the-hooks-command) — read-only browser, source locations
- [Hook Types](#hook-types) — command / http / prompt / agent; CI caveat
- [Useful Commands](#useful-commands) — /init, /memory, /hooks

---

## Hooks vs. CLAUDE.md

CLAUDE.md tells Claude what to do. It does not verify that Claude did it.

| Mechanism | Reliability | Use for |
|---|---|---|
| CLAUDE.md | Advisory — Claude may ignore | Preferences, conventions, anti-patterns, context |
| Hooks (pre-commit, agent hooks) | Deterministic — always runs | Things that must happen without exception |
| CI gates | Deterministic — blocks merge | Things that must pass before shipping |

For instructions you want enforced at the system prompt level (not advisory), use `--append-system-prompt` on the Claude Code CLI. This must be passed every invocation, so it is better suited to automation scripts than interactive use.

**CLAUDE.md-specific hooks:**

`InstructionsLoaded` — fires when any CLAUDE.md or `.claude/rules/*.md` file loads. Useful for debugging which files are loading and when:
```json
{
  "hooks": {
    "InstructionsLoaded": [
      {
        "matcher": "path_glob_match",
        "hooks": [{ "type": "command", "command": "jq -r '.file_path' >> ~/.claude/instructions-log.txt" }]
      }
    ]
  }
}
```
Matchers: `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact`

`SessionStart` with `compact` matcher — re-inject critical context after compaction (though CLAUDE.md itself survives compaction; use this for dynamic context that changes):
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [{ "type": "command", "command": "echo 'Sprint context: auth refactor. Use bun, not npm.'" }]
      }
    ]
  }
}
```

`PostToolUse` with `Edit|Write` matcher — auto-format code after every file edit (deterministic, not relying on CLAUDE.md):
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write" }]
      }
    ]
  }
}
```

See [agent-readable-lints.md](agent-readable-lints.md) for pre-commit hook integration.

---

## Hook Exit Code Semantics

Command hooks communicate decisions back to Claude Code through exit codes and JSON stdout:

| Exit code | Meaning |
|---|---|
| **0** | Success. If stdout contains JSON, it is parsed for structured output (permission decisions, modified inputs, additional context). |
| **2** | Blocking error. stdout is ignored; stderr text is fed back to Claude as an error message. Effect depends on the hook event — see table below. |
| **Any other code** | Non-blocking error. stderr shown in verbose mode; execution continues as if the hook wasn't there. |

**Which events can block on exit 2:**

| Hook event | Can block? | Effect of exit 2 |
|---|---|---|
| `PreToolUse` | Yes | Blocks the tool call |
| `PermissionRequest` | Yes | Denies the permission |
| `UserPromptSubmit` | Yes | Blocks the prompt, erases from context |
| `Stop` | Yes | Prevents the agent from stopping |
| `SubagentStop` | Yes | Prevents the subagent from stopping |
| `TeammateIdle` | Yes | Prevents teammate going idle |
| `TaskCreated` / `TaskCompleted` | Yes | Rolls back the task event |
| `ConfigChange` | Yes | Blocks the config change |
| `PostToolUse` | No | Shows stderr to Claude (tool already ran) |

For `PreToolUse`, the preferred approach is structured JSON output rather than raw exit codes — it gives you more control:

```bash
#!/bin/bash
input=$(cat)
file=$(echo "$input" | jq -r '.tool_input.file_path // empty')

# Block writes to protected files
if echo "$file" | grep -qE '(\.env|production\.config)'; then
  echo '{
    "hookSpecificOutput": {
      "hookEventName": "PreToolUse",
      "permissionDecision": "deny",
      "permissionDecisionReason": "Writes to .env and production.config are blocked"
    }
  }'
  exit 0  # Exit 0 with JSON deny — preferred over exit 2
fi
exit 0
```

**`updatedInput` — modify what Claude was about to do:**

Hooks can rewrite tool parameters before execution. This is the hook equivalent of the Context Injection pattern — transform what the agent sees rather than blocking it:

```bash
#!/bin/bash
input=$(cat)
cmd=$(echo "$input" | jq -r '.tool_input.command')

# Intercept broad test runs and filter to failures only
if [[ "$cmd" =~ ^(npm test|pytest|go test) ]]; then
  filtered="$cmd 2>&1 | grep -A 5 -E '(FAIL|ERROR|error:)' | head -100"
  echo "{
    \"hookSpecificOutput\": {
      \"hookEventName\": \"PreToolUse\",
      \"permissionDecision\": \"allow\",
      \"updatedInput\": {\"command\": \"$filtered\"}
    }
  }"
else
  echo "{}"
fi
```

This pipes a 10,000-line test output down to the 50 lines that matter before Claude ever sees it. Reduces token cost and signal-to-noise ratio simultaneously.

---

## The `/hooks` Command

Type `/hooks` in Claude Code for a read-only browser showing all configured hooks:
- All hook events with counts of handlers per event
- Matchers, filters, and full handler details (command text, type, timeout)
- Source location for each hook: User, Project, Local, Plugin, or Built-in

Useful for debugging: if a hook isn't firing, `/hooks` shows exactly what is configured and where it came from. Edit `.claude/settings.json` or `~/.claude/settings.json` directly to modify hooks; the `/hooks` view is read-only.

---

## Hook Types

Four hook types are available, not just shell commands:

| Type | How it works | Use for |
|---|---|---|
| `command` | Shell script receives JSON on stdin, returns JSON on stdout | Most harness enforcement; deterministic |
| `http` | POSTs JSON to a URL; 2xx + JSON body = structured response | External validation services, centralized audit logging |
| `prompt` | Sends a prompt to Claude for a yes/no decision | Human-language rule enforcement where scripting is impractical |
| `agent` | Spawns a subagent with tools | Complex verification requiring file reads or tool use |

For CI pipelines: note that `PermissionRequest` hooks do not fire in non-interactive (headless) mode. Use `PreToolUse` hooks for access control in automation — they fire regardless of interactive mode.

---

## Useful Commands

- **`/init`** — generate a starting CLAUDE.md automatically; Claude analyzes your codebase and creates a file with build commands, test instructions, and conventions it discovers. With `CLAUDE_CODE_NEW_INIT=1`: interactive multi-phase flow that asks which artifacts to set up (CLAUDE.md, skills, hooks)
- **`/memory`** — lists all CLAUDE.md, CLAUDE.local.md, and rules files loaded in the current session; toggle auto memory; browse and edit files
- **`/hooks`** — browse all configured hooks; shows counts per event type and hook details
