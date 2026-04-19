---
name: claude-agent-sdk
description: Build autonomous AI agent applications using the Claude Agent SDK (`claude-agent-sdk` Python / `@anthropic-ai/claude-agent-sdk` TypeScript). Use when: writing code that calls `query()` or `ClaudeSDKClient`; building agents that autonomously read files, run commands, edit code, or search the web; implementing hooks (PreToolUse, PostToolUse, Stop, Notification, etc.) to intercept/block/log tool calls; managing multi-turn sessions with resume/fork/continue; defining custom tools with `@tool()` or `create_sdk_mcp_server()`; spawning subagents; connecting MCP servers; or embedding the Claude Code agent loop in a CI/CD pipeline or production application. Distinct from the Managed Agents REST API (`client.beta.agents`) — this SDK runs the agent loop locally.
---

# Claude Agent SDK

The Claude Code agent loop as a library — same tools, same context management, same intelligence, callable from Python or TypeScript. Claude autonomously executes tools (Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch) without you implementing any tool loop.

**Install:**
```bash
pip install claude-agent-sdk              # Python
npm install @anthropic-ai/claude-agent-sdk  # TypeScript
export ANTHROPIC_API_KEY=your-key
```

> Formerly called "Claude Code SDK". Same package, renamed.

## Core Pattern: `query()`

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

async def main():
    async for message in query(
        prompt="Find and fix the bug in auth.py",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit", "Glob"],
            permission_mode="acceptEdits",
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"Done ({message.subtype}) — cost: ${message.total_cost_usd:.4f}")
            print(message.result)

asyncio.run(main())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Find and fix the bug in auth.py",
  options: { allowedTools: ["Read", "Edit", "Glob"], permissionMode: "acceptEdits" }
})) {
  if (message.type === "assistant") {
    for (const block of message.message?.content ?? []) {
      if ("text" in block) process.stdout.write(block.text);
    }
  } else if (message.type === "result") {
    console.log(`Done (${message.subtype}): ${message.result}`);
  }
}
```

`query()` creates a new session each time. For multi-turn conversations, use `ClaudeSDKClient` (Python) or `continue: true` (TypeScript) — see [references/sessions.md](references/sessions.md).

## Built-in Tools

| Tool | What it does |
|---|---|
| `Read` | Read any file in the working directory |
| `Write` | Create new files |
| `Edit` | Make precise string replacements in files |
| `Bash` | Run terminal commands, git, scripts |
| `Glob` | Find files by pattern (`**/*.ts`) |
| `Grep` | Search file contents with regex |
| `WebSearch` | Search the web |
| `WebFetch` | Fetch and parse a URL |
| `Monitor` | Watch a background process and react to each output line |
| `AskUserQuestion` | Ask the user a clarifying question (with multiple-choice options) |
| `Agent` | Spawn subagents (must be in `allowed_tools` for subagent dispatch) |

## Permission Modes

| Mode | Behavior | Use case |
|---|---|---|
| `acceptEdits` | Auto-approves file edits and common FS commands | Dev workflows |
| `dontAsk` | Denies anything not in `allowed_tools` | Headless locked-down agents |
| `bypassPermissions` | Runs every tool without prompts | Sandboxed CI |
| `auto` (TS only) | Model classifier approves/denies each call | Autonomous with safety |
| `default` | Requires a `can_use_tool` callback | Custom approval flows |

## Key `ClaudeAgentOptions` Fields

| Field | Notes |
|---|---|
| `allowed_tools` | Pre-approve specific tools (auto-allow without prompt) |
| `disallowed_tools` | Denylist on top of inherited tools |
| `permission_mode` | One of the modes above |
| `system_prompt` | Custom system prompt string, or `{"type": "preset", "preset": "claude_code"}` |
| `model` | Model ID string, defaults to Claude's recommended model |
| `cwd` | Working directory for the agent |
| `max_turns` | Cap agentic loop turns |
| `max_budget_usd` | Spend cap per run |
| `resume` | Session ID to resume a prior conversation |
| `fork_session` | `True` to fork (branch) from a resumed session |
| `continue_conversation` | `True` to resume the most recent session in `cwd` |
| `mcp_servers` | Dict of MCP server configs |
| `hooks` | Hook callbacks keyed by event name |
| `agents` | Dict of `AgentDefinition` for subagents |
| `thinking` | `{"type": "enabled", "budget_tokens": N}` for extended thinking |
| `effort` | `"low"` / `"medium"` / `"high"` / `"max"` — reasoning effort preset |

Full reference: [references/options.md](references/options.md)

## Message Types

| Type | When | Key fields |
|---|---|---|
| `AssistantMessage` | Each model response turn | `.content[]` → `TextBlock`, `ThinkingBlock`, `ToolUseBlock`, `ToolResultBlock` |
| `ResultMessage` | Final message always | `.subtype` (`success`/`error_*`), `.result`, `.total_cost_usd`, `.session_id`, `.num_turns` |
| `SystemMessage` | Session init | `.subtype == "init"`, `.data["session_id"]` |
| `UserMessage` | User turns (echoed) | `.content` |
| `RateLimitEvent` | Rate limit hit | — |

Check `ResultMessage.subtype` to detect errors: `error_max_turns`, `error_max_budget_usd`, `error_api_error`, etc.

## Hooks

Intercept tool calls before/after execution — block dangerous operations, log, transform inputs, require human approval.

```python
from claude_agent_sdk import HookMatcher

async def block_env_writes(input_data, tool_use_id, context):
    path = input_data["tool_input"].get("file_path", "")
    if path.endswith(".env"):
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Cannot modify .env files",
            }
        }
    return {}  # allow

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [HookMatcher(matcher="Write|Edit", hooks=[block_env_writes])]
    }
)
```

Hook outputs: return `{}` to allow, set `permissionDecision: "deny"` to block, `permissionDecision: "allow"` with `updatedInput` to modify. `systemMessage` injects context into the conversation.

Full hook event list and patterns: [references/hooks.md](references/hooks.md)

## Sessions (Resume / Fork / Multi-turn)

```python
# Capture session ID from ResultMessage
session_id = None
async for message in query(prompt="Analyze auth.py", options=...):
    if isinstance(message, ResultMessage):
        session_id = message.session_id

# Resume later
async for message in query(
    prompt="Now implement your suggestions",
    options=ClaudeAgentOptions(resume=session_id, allowed_tools=[...]),
):
    ...

# Fork to try an alternative (original unchanged)
async for message in query(
    prompt="Try OAuth2 instead of JWT",
    options=ClaudeAgentOptions(resume=session_id, fork_session=True),
):
    ...
```

Multi-turn in one process: use `ClaudeSDKClient` (Python) or `continue: true` (TypeScript).
Full session patterns: [references/sessions.md](references/sessions.md)

## Custom Tools (MCP)

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("get_weather", "Get current weather for a city", {"location": str})
async def get_weather(args):
    return {"content": [{"type": "text", "text": f"Sunny in {args['location']}"}]}

server = create_sdk_mcp_server(name="weather", tools=[get_weather])

options = ClaudeAgentOptions(
    mcp_servers={"wx": server},
    allowed_tools=["mcp__wx__get_weather"],
)
```

External MCP servers (stdio or HTTP):
```python
mcp_servers={
    "playwright": {"command": "npx", "args": ["@playwright/mcp@latest"]},
}
```

MCP tool names follow `mcp__<server-key>__<tool-name>` pattern.

## Subagents

Include `Agent` in `allowed_tools`; define agents in `ClaudeAgentOptions.agents`:

```python
from claude_agent_sdk import AgentDefinition

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Glob", "Grep", "Agent"],
    agents={
        "code-reviewer": AgentDefinition(
            description="Expert code reviewer for security and quality.",
            prompt="Analyze code quality and suggest improvements.",
            tools=["Read", "Glob", "Grep"],
        )
    },
)
```

## Gotchas

- **`allowed_tools` vs `permission_mode`**: `allowed_tools` pre-approves specific tools; `permission_mode` controls what happens for all others. Use both together for headless agents.
- **`ResultMessage.subtype`** is not always `"success"` — always check before using `.result`. Common error subtypes: `error_max_turns`, `error_max_budget_usd`, `error_api_error`.
- **Session files are local** — `resume` requires the `.jsonl` file to exist on disk at the same `cwd`. Moving hosts requires moving the file too (or don't rely on resume across machines).
- **Hook `updatedInput` requires `permissionDecision: "allow"`** — returning `updatedInput` without it has no effect.
- **MCP tool names use the options key**, not the server name: if `mcp_servers={"wx": ...}` then tool is `mcp__wx__...`, not `mcp__weather__...`.
- **`deny` beats `ask` beats `allow`** when multiple hooks conflict.
- **`SessionStart`/`SessionEnd` not in Python hooks** — only available via settings file hooks in Python. Use the first message from `receive_response()` as a proxy for session start.
- **Hooks don't fire at `max_turns`** — the session ends before hooks can execute.
- **`async_: True`** in hook output means fire-and-forget — cannot block, modify, or inject context.
- **Claude Code SDK renamed** — old import `claude_code_sdk` no longer works. Use `claude_agent_sdk`.
