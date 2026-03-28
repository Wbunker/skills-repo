---
name: agent-creator
description: Create or update Claude Code custom subagents. Use when the user wants to build a new agent, write a .claude/agents/ markdown file, configure agent frontmatter, restrict agent tools, set permission modes, preload skills into an agent, enable agent memory, scope MCP servers to an agent, define lifecycle hooks, or understand how agents differ from commands/skills. Covers all frontmatter fields, tool access patterns, permission modes, memory scopes, hook integration, and when to use agents vs skills.
---

# Agent Creator

Subagents are specialized AI assistants defined as Markdown files with YAML frontmatter. Each runs in its own context window with a custom system prompt, specific tool access, and independent permissions. Claude auto-delegates tasks based on each agent's `description`.

**Agents vs Skills/Commands:**
- Use **agents** for isolated, self-contained tasks — no conversation history, own context window, optional persistent memory
- Use **skills/commands** for inline workflows that need conversation context and run in the main session

## File placement

| Scope | Path | Priority |
|---|---|---|
| Project | `.claude/agents/<name>.md` | 2 (high) |
| Personal | `~/.claude/agents/<name>.md` | 3 |
| Plugin | `<plugin>/agents/<name>.md` | 4 (low) |
| CLI flag | `--agents` JSON | 1 (highest, session-only) |

When multiple agents share a name, higher-priority location wins. Project agents should be committed to version control.

## Anatomy of an agent file

```markdown
---
name: code-reviewer
description: Reviews code for quality and security. Use proactively after code changes.
tools: Read, Grep, Glob, Bash
model: sonnet
permissionMode: default
maxTurns: 20
skills:
  - api-conventions
memory: user
---

You are a senior code reviewer. When invoked:
1. Run `git diff` to see recent changes
2. Review for security, readability, and correctness
3. Report issues by priority: Critical → Warnings → Suggestions
```

The **body** is the agent's entire system prompt. Agents receive only this prompt plus basic environment info (working directory) — not the full Claude Code system prompt.

## Frontmatter reference

`name` and `description` are required. All other fields are optional.

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Unique ID. Lowercase letters and hyphens only. |
| `description` | Yes | When Claude should delegate to this agent. Write detailed trigger phrases — Claude uses this to decide when to auto-delegate. Include "use proactively" to encourage automatic use. |
| `tools` | No | Allowlist of tools the agent can use. Omit to inherit all tools from the main conversation. |
| `disallowedTools` | No | Denylist — remove specific tools from the inherited or specified set. |
| `model` | No | `sonnet`, `opus`, `haiku`, a full model ID like `claude-sonnet-4-6`, or `inherit`. Defaults to `inherit`. |
| `permissionMode` | No | How the agent handles permission prompts. See [Permission modes](#permission-modes). |
| `maxTurns` | No | Max agentic turns before the agent stops. |
| `skills` | No | Skills to inject into the agent's context at startup (full content, not just available for invocation). Agents don't inherit skills from the parent conversation. |
| `mcpServers` | No | MCP servers scoped to this agent. Inline servers connect/disconnect with the agent; string refs share the parent session's connection. |
| `hooks` | No | Lifecycle hooks scoped to this agent. Cleaned up when the agent finishes. |
| `memory` | No | Persistent memory scope: `user`, `project`, or `local`. Enables cross-session learning. |
| `background` | No | `true` to always run as a background task. Default: `false`. |
| `isolation` | No | `worktree` to run in a temporary git worktree (auto-cleaned up if no changes). |

## Permission modes

| Mode | Behavior |
|---|---|
| `default` | Standard prompts for permissions |
| `acceptEdits` | Auto-accept file edits |
| `dontAsk` | Auto-deny unspecified tools |
| `bypassPermissions` | Skip all permission checks |
| `plan` | Read-only (plan mode) |

If the parent session uses `bypassPermissions`, it overrides the agent's setting.

## Tool access patterns

### Allowlist (recommended for restricted agents)
```yaml
tools: Read, Grep, Glob, Bash
```

### Denylist (block specific tools, allow rest)
```yaml
disallowedTools: Write, Edit
```

### Read-only explorer
```yaml
tools: Read, Grep, Glob
```

### Bash with tool restriction in Bash scope
```yaml
tools: Bash(npm *), Bash(gh *), Read
```

### Restrict which subagents this agent can spawn (only for `--agent` main thread)
```yaml
tools: Agent(worker, researcher), Read, Bash
```

## Memory scopes

```yaml
memory: user    # ~/.claude/agent-memory/<name>/ — across all projects
memory: project # .claude/agent-memory/<name>/ — project-specific, git-committable
memory: local   # .claude/agent-memory-local/<name>/ — project-specific, not committed
```

When `memory` is set:
- Agent gets instructions to read/write a `MEMORY.md` index file
- First 200 lines of `MEMORY.md` are injected at startup
- `Read`, `Write`, `Edit` tools are auto-enabled for memory management
- Agent builds up institutional knowledge across conversations

**Best practice:** include memory instructions in the agent body:
```markdown
Update your agent memory as you discover patterns, conventions, and architectural
decisions. Write concise notes about what you found and where.
```

## Skills preloading

```yaml
skills:
  - api-conventions
  - error-handling-patterns
```

Full skill content is injected at startup — not just made available for invocation. List skills explicitly; agents don't inherit from the parent conversation.

## MCP server scoping

```yaml
mcpServers:
  # Inline: connected only while this agent runs
  - playwright:
      type: stdio
      command: npx
      args: ["-y", "@playwright/mcp@latest"]
  # Reference: reuses parent session's already-configured server
  - github
```

Inline definitions keep MCP tools out of the main conversation context.

## Hooks in agents

Hooks in frontmatter run only while the agent is active:

```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-command.sh"
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./scripts/run-linter.sh"
```

`Stop` hooks in frontmatter are auto-converted to `SubagentStop` events.

For project-level hooks that respond to any agent starting/stopping, use `SubagentStart` / `SubagentStop` in `.claude/settings.json` instead.

## How agents are invoked — critical constraints

### How the Agent tool actually works

The `subagent_type` field only accepts **built-in** types: `general-purpose`, `Explore`, `Plan`, `claude-code-guide`, `repo-analyzer`, etc.

**Custom project agents (`.claude/agents/*.md`) cannot be invoked via `subagent_type`** — doing so errors with "Agent type 'my-agent' not found".

When `subagent_type` is omitted, the Agent tool always runs **general-purpose** — it does NOT auto-route to custom agents. Custom agent `.md` files serve as:
1. Documentation / reference for the workflow
2. Auto-delegation targets when Claude in the **main conversation** (not via Agent tool) decides to delegate a task based on description matching

```python
# WRONG — errors: "Agent type 'my-agent' not found"
Agent(subagent_type="my-agent", prompt="do the thing")

# Runs general-purpose, NOT your custom agent
Agent(prompt="<task>")

# CORRECT for background parallel work: embed full instructions in the prompt
Agent(
  prompt="<full workflow steps here>",
  run_in_background=True
)
```

**Practical implication**: For commands that dispatch background agents in parallel, embed the full workflow in the prompt. The `.claude/agents/` file remains the canonical reference — keep it in sync, but the dispatch prompt carries the executable instructions.

### Subagents cannot spawn subagents

Agents running as subagents (dispatched via the Agent tool from a command or conversation) **cannot spawn their own subagents**. The Agent tool is not available to subagents. Design workflows so the orchestrator (command or main conversation) dispatches all parallel work directly.

### `Agent(name)` syntax — only for `--agent` main thread

The `tools: Agent(worker, researcher)` syntax restricts which named agents an agent can spawn. This **only works when the agent itself is the main thread**, launched via `claude --agent my-orchestrator`. It does not work for agents dispatched as subagents.

### Experimental: parallel named-agent dispatch

With `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, orchestrator agents running as the main thread can dispatch named subagents explicitly. This is experimental and subject to change.

### Orchestrating parallel work from commands

Since subagents can't spawn subagents, commands that need parallel execution use **TaskCreate/TaskUpdate**:

```markdown
# In a command that needs parallel work:
1. Use TaskCreate to create a task for each unit of work
2. Dispatch each via Agent tool (auto-delegation, no subagent_type)
3. Wait for all agents to complete
4. Use TaskUpdate to mark each done
5. Commit results
```

### Background agents and permissions

`background: true` agents run concurrently and **cannot ask permission questions mid-run**. All required permissions must be pre-approved. Use `permissionMode: acceptEdits` or `bypassPermissions` when the agent needs to write files without prompting.

See [references/patterns.md](references/patterns.md) for complete orchestration patterns.

## Writing effective descriptions

The `description` is the only signal Claude uses to decide when to delegate. Make it specific:

- **Bad:** `"Code reviewer"`
- **Good:** `"Expert code review specialist. Use proactively after writing or modifying code. Analyzes for security vulnerabilities, readability, test coverage, and best practices."`

Add `"use proactively"` to encourage Claude to delegate automatically without being asked.

## Complete examples

### Read-only code reviewer
```markdown
---
name: code-reviewer
description: Expert code reviewer. Use proactively after any code changes. Reviews for security, readability, correctness, and test coverage.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer. When invoked:
1. Run `git diff HEAD~1` or `git diff --staged` to see changes
2. Focus only on modified files

Report by priority:
- **Critical** (must fix): security issues, data loss risks, broken logic
- **Warnings** (should fix): missing error handling, poor naming, code smell
- **Suggestions** (consider): performance, readability, test coverage

Include specific fix examples for each issue.
```

### Persistent debugger with memory
```markdown
---
name: debugger
description: Debugging specialist for errors, test failures, and unexpected behavior. Use proactively when any issue is encountered.
tools: Read, Edit, Bash, Grep, Glob
model: sonnet
memory: project
---

You are an expert debugger. Check your memory for known patterns before starting.

When invoked:
1. Capture the full error + stack trace
2. Identify reproduction steps
3. Isolate the failure location
4. Implement the minimal fix
5. Verify the fix works
6. Update your memory with the root cause and fix pattern

Focus on root cause, not symptoms.
```

### Isolated browser tester with MCP
```markdown
---
name: browser-tester
description: Tests UI features in a real browser. Use when verifying visual behavior, form flows, or UI interactions that require a real browser.
mcpServers:
  - playwright:
      type: stdio
      command: npx
      args: ["-y", "@playwright/mcp@latest"]
model: sonnet
isolation: worktree
---

You are a browser testing specialist. Use Playwright tools to navigate, interact, screenshot, and verify UI behavior.

When invoked with a URL or feature to test:
1. Navigate to the target page
2. Perform the specified interactions
3. Screenshot key states
4. Report what worked, what failed, and any visual anomalies
```

### Background research agent
```markdown
---
name: researcher
description: Deep codebase research agent. Use when thorough, isolated exploration is needed without consuming main conversation context.
tools: Read, Grep, Glob
model: haiku
background: true
---

You are a codebase research specialist. Explore thoroughly and return a structured summary.

For each research task:
1. Use Glob to map the relevant file structure
2. Use Grep to find key patterns and usages
3. Read relevant files in depth
4. Return: file locations, patterns found, key decisions, and anything surprising
```

## When to use agents vs skills vs main conversation

| Use | When |
|---|---|
| **Agent** | Self-contained task, produces verbose output, needs tool restriction, benefits from persistent memory, or should run in background |
| **Skill/Command** | Needs conversation history, inline workflow, reference knowledge, or step-by-step instructions within the current context |
| **Main conversation** | Iterative back-and-forth, multiple phases sharing context, quick targeted changes |

## CLI-defined agents (session-only)

```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer...",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  }
}'
```

Use `prompt` (not the markdown body) for the system prompt in JSON form. Supports all the same fields as file-based agents.
