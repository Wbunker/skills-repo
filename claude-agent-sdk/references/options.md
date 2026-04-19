# ClaudeAgentOptions — Full Reference

## Python Dataclass

```python
@dataclass
class ClaudeAgentOptions:
    # Tools
    tools: list[str] | ToolsPreset | None = None
    allowed_tools: list[str] = field(default_factory=list)
    disallowed_tools: list[str] = field(default_factory=list)

    # Prompt / Model
    system_prompt: str | SystemPromptPreset | None = None
    model: str | None = None
    fallback_model: str | None = None
    max_thinking_tokens: int | None = None
    thinking: ThinkingConfig | None = None
    effort: Literal["low", "medium", "high", "max"] | None = None

    # Session
    continue_conversation: bool = False  # resume most recent in cwd
    resume: str | None = None            # resume specific session by ID
    fork_session: bool = False           # branch from resumed session
    max_turns: int | None = None
    max_budget_usd: float | None = None

    # Environment
    cwd: str | Path | None = None
    add_dirs: list[str | Path] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)

    # Permissions
    permission_mode: PermissionMode | None = None
    can_use_tool: CanUseTool | None = None  # callback for default mode

    # MCP
    mcp_servers: dict[str, McpServerConfig] | str | Path = field(default_factory=dict)

    # Output
    output_format: dict[str, Any] | None = None
    include_partial_messages: bool = False

    # Hooks
    hooks: dict[HookEvent, list[HookMatcher]] | None = None

    # Advanced
    cli_path: str | Path | None = None
    agents: dict[str, AgentDefinition] | None = None
    plugins: list[SdkPluginConfig] = field(default_factory=list)
    setting_sources: list[SettingSource] | None = None
    sandbox: SandboxSettings | None = None
    enable_file_checkpointing: bool = False
    user: str | None = None
    betas: list[SdkBeta] = field(default_factory=list)
```

## TypeScript Options (equivalent fields)

| Python | TypeScript |
|---|---|
| `allowed_tools` | `allowedTools` |
| `permission_mode` | `permissionMode` |
| `system_prompt` | `systemPrompt` |
| `continue_conversation` | `continue` |
| `fork_session` | `forkSession` |
| `max_turns` | `maxTurns` |
| `max_budget_usd` | `maxBudgetUSD` |
| `mcp_servers` | `mcpServers` |
| `setting_sources` | `settingSources` |
| `can_use_tool` | `canUseTool` |
| `include_partial_messages` | `includePartialMessages` |

TypeScript-only: `continue: true` (resume most recent), `persistSession: false` (memory only, no disk write), `auto` permission mode.

## Permission Modes

| Mode | Behavior |
|---|---|
| `"default"` | Calls `can_use_tool` callback for each unapproved tool |
| `"acceptEdits"` | Auto-approves file edits and common FS commands; prompts for others |
| `"dontAsk"` | Denies anything not in `allowed_tools` without prompting |
| `"bypassPermissions"` | All tools run without any check |
| `"auto"` (TS only) | Model classifier approves/denies per-call |
| `"plan"` | Read-only mode |

## `can_use_tool` Callback

Used when `permission_mode="default"`. Called for each tool request that isn't pre-approved:

```python
from claude_agent_sdk import PermissionResultAllow, PermissionResultDeny

async def my_tool_approver(tool_name, input_data, context):
    if tool_name == "Bash" and "rm -rf" in input_data.get("command", ""):
        return PermissionResultDeny(message="Destructive command blocked", interrupt=True)
    return PermissionResultAllow(updated_input=input_data)

options = ClaudeAgentOptions(
    permission_mode="default",
    can_use_tool=my_tool_approver,
)
```

## `thinking` Config

```python
# Adaptive (model decides)
thinking = {"type": "adaptive"}

# Enabled with explicit budget
thinking = {"type": "enabled", "budget_tokens": 20000}

# Disabled
thinking = {"type": "disabled"}
```

## `system_prompt` Presets

```python
# Custom string
system_prompt="You are a senior Python developer. Follow PEP 8."

# Claude Code preset (uses Claude Code's full system prompt)
system_prompt={"type": "preset", "preset": "claude_code"}
```

## `setting_sources`

Control which filesystem config sources are loaded. Enables CLAUDE.md, `.claude/settings.json` hooks, skills, slash commands from disk:

```python
setting_sources=["user"]            # ~/.claude/settings.json
setting_sources=["project"]         # .claude/settings.json + CLAUDE.md
setting_sources=["local"]           # .claude/settings.local.json
setting_sources=["user", "project"] # both
```

Omit to use no filesystem settings (SDK-only config).

## MCP Server Config

```python
# stdio server
mcp_servers={
    "playwright": {"command": "npx", "args": ["@playwright/mcp@latest"]},
}

# HTTP/SSE server
mcp_servers={
    "my-api": {"url": "https://my-server.example.com/sse"},
}

# SDK-defined server (using @tool decorator)
mcp_servers={"calc": create_sdk_mcp_server(name="calculator", tools=[add, subtract])}
```

MCP tools are referenced as `mcp__<key>__<tool_name>` where `<key>` is the dict key.

## AgentDefinition (Subagents)

```python
from claude_agent_sdk import AgentDefinition

agents={
    "code-reviewer": AgentDefinition(
        description="Expert code reviewer. Triggers on code change tasks.",
        prompt="You are a senior code reviewer. Analyze for security, correctness, style.",
        tools=["Read", "Glob", "Grep"],
        model="claude-haiku-4-5",  # optional cheaper model for subtask
    )
}
```

Include `"Agent"` in `allowed_tools` to enable subagent spawning.
