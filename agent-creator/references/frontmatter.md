# Agent Frontmatter Reference

All fields except `name` and `description` are optional.

## Fields

### `name`
- **Type**: string
- **Required**: yes
- **Constraints**: lowercase letters, numbers, hyphens only; max 64 chars
- **Purpose**: Unique identifier; also how the agent is referenced from commands (`agent: my-agent`)

### `description`
- **Type**: string
- **Required**: yes (strongly)
- **Purpose**: When Claude should delegate to this agent. This is the primary auto-trigger signal — Claude reads descriptions of all available agents and delegates matching tasks automatically. Include specific trigger scenarios, task types, and input examples.

### `tools`
- **Type**: string (comma-separated) or array
- **Default**: inherits all tools if omitted
- **Purpose**: Tools the agent can use. Omit to inherit everything; list explicitly to restrict.

**Tool names**: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `WebFetch`, `WebSearch`, `Agent`

**Tool-specific restrictions** (Bash):
```yaml
tools: "Bash(git *)"          # only git subcommands
tools: "Bash(npm *), Read"    # only npm subcommands + reads
tools: "Bash(!rm *), Bash"    # all bash except rm
```

**Spawning subagents**: Include `Agent` to allow spawning agents. Restrict with `Agent(name1, name2)` to only allow specific agent names.

### `disallowedTools`
- **Type**: string or array
- **Purpose**: Denylist — removes tools from inherited or specified list
- **Example**: `disallowedTools: "Write, Edit"` (read-only agent even if tools omitted)

### `model`
- **Type**: string
- **Default**: `inherit` (same model as parent conversation)

| Value | Model |
|---|---|
| `inherit` | Same as parent (default) |
| `haiku` | claude-haiku-4-5 — fast, cheap; use for simple/mechanical tasks |
| `sonnet` | claude-sonnet-4-6 — balanced; use for most agents |
| `opus` | claude-opus-4-6 — most capable; use for complex reasoning |
| Full model ID | e.g., `claude-sonnet-4-6` |

### `permissionMode`
- **Type**: string
- **Default**: `default`

| Value | Behavior |
|---|---|
| `default` | Prompts user for permission on tool use |
| `acceptEdits` | Auto-accepts file edits without prompting |
| `dontAsk` | Auto-approves most operations |
| `bypassPermissions` | No permission checks (use only when trust is established) |
| `plan` | Read-only planning mode — no writes |

**Note**: If the parent conversation uses `bypassPermissions`, the agent inherits it regardless of this field.

### `background`
- **Type**: boolean
- **Default**: false
- **Purpose**: When `true`, agent always runs as a background task (non-blocking). Claude pre-approves permissions; agent auto-denies unapproved tools.
- **Use for**: Agents dispatched in bulk by orchestrator commands

### `maxTurns`
- **Type**: number
- **Purpose**: Maximum agentic loop iterations before the agent stops
- **Use for**: Preventing runaway agents on large inputs
- **Example**: `maxTurns: 20`

### `skills`
- **Type**: array of skill names (strings)
- **Purpose**: Loads full skill content into the agent's context at startup. Agents do NOT inherit skills from the parent conversation — you must list them explicitly here.
- **Example**:
  ```yaml
  skills:
    - css-bug-squashing
    - site-context
  ```

### `isolation`
- **Type**: string (`"worktree"`)
- **Purpose**: Runs the agent in a temporary git worktree (isolated copy of the repo). Worktree is auto-cleaned up if agent makes no changes.
- **Use for**: Parallel agents that would conflict on the same files

### `memory`
- **Type**: string
- **Purpose**: Enables persistent memory across sessions
- **Values**:
  - `user` → `~/.claude/agent-memory/<name>/` (personal, all projects)
  - `project` → `.claude/agent-memory/<name>/` (team-shared)
  - `local` → `.claude/agent-memory-local/<name>/` (local, not committed)

### `mcpServers`
- **Type**: array
- **Purpose**: MCP servers available to this agent. Each entry is either a server name (referencing an already-configured server) or an inline server definition.
- **Example**:
  ```yaml
  mcpServers:
    - slack
    - playwright
  ```

### `hooks`
- **Type**: object
- **Purpose**: Lifecycle hooks scoped to this agent (PreToolUse, PostToolUse, Stop, etc.)
- **See**: Claude Code hooks documentation for format

### `color`
- **Type**: string
- **Purpose**: UI color hint for the agent in Claude Code interface
- **Example**: `color: green`

---

## Scope Priority (highest to lowest)

1. `--agents` CLI flag (session only)
2. `.claude/agents/` (project — version-controlled)
3. `~/.claude/agents/` (user — personal, all projects)
4. Plugin agents

When two agents share the same name, the higher-priority location wins.
