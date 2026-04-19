# Hooks Reference

## Available Hook Events

| Event | Python | TypeScript | Trigger |
|---|---|---|---|
| `PreToolUse` | Yes | Yes | Before a tool call — can block or modify |
| `PostToolUse` | Yes | Yes | After a tool completes |
| `PostToolUseFailure` | Yes | Yes | After a tool fails |
| `UserPromptSubmit` | Yes | Yes | When a user prompt is submitted |
| `Stop` | Yes | Yes | Agent execution stopping |
| `SubagentStart` | Yes | Yes | Subagent initializing |
| `SubagentStop` | Yes | Yes | Subagent completing |
| `PreCompact` | Yes | Yes | Conversation about to be compacted |
| `PermissionRequest` | Yes | Yes | Permission dialog would show |
| `Notification` | Yes | Yes | Agent status messages |
| `SessionStart` | No | Yes | Session init (TS only as callback; Python via settings file) |
| `SessionEnd` | No | Yes | Session end (TS only as callback) |
| `Setup` | No | Yes | Session setup/maintenance |
| `TeammateIdle` | No | Yes | Teammate idle |
| `TaskCompleted` | No | Yes | Background task done |
| `ConfigChange` | No | Yes | Config file changed |
| `WorktreeCreate` | No | Yes | Git worktree created |
| `WorktreeRemove` | No | Yes | Git worktree removed |

## Hook Structure

```python
from claude_agent_sdk import HookMatcher, ClaudeAgentOptions

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Write|Edit", hooks=[callback_fn]),
            HookMatcher(matcher="Bash", hooks=[bash_callback]),
            HookMatcher(hooks=[global_logger]),  # no matcher = all tools
        ],
        "PostToolUse": [
            HookMatcher(hooks=[audit_callback]),
        ],
        "Stop": [
            HookMatcher(hooks=[cleanup_callback]),
        ],
    }
)
```

**`HookMatcher` fields:**
- `matcher`: regex against tool name (or notification type for `Notification` hooks). Omit to match all.
- `hooks`: list of async callback functions (required)
- `timeout`: seconds before callback times out (default 60)

MCP tools: `mcp__<server>__<action>` — match with `^mcp__playwright__` etc.

## Callback Signature

```python
async def my_hook(input_data: dict, tool_use_id: str | None, context) -> dict:
    ...
    return {}
```

**`input_data` fields (always present):**
- `hook_event_name`: e.g. `"PreToolUse"`
- `session_id`: current session ID
- `cwd`: working directory
- `agent_id`: set when inside a subagent
- `agent_type`: set when inside a subagent

**`PreToolUse`/`PostToolUse` additional fields:**
- `tool_name`: e.g. `"Write"`, `"Bash"`, `"mcp__playwright__click"`
- `tool_input`: dict of tool arguments (e.g. `{"file_path": "...", "content": "..."}` for Write)
- `tool_response` (PostToolUse only): tool output

## Output Format

### Allow (no-op)
```python
return {}
```

### Deny (block the operation)
```python
return {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "Reason shown to agent",
    }
}
```

### Allow + Modify Input
```python
return {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow",   # required when using updatedInput
        "updatedInput": {
            **input_data["tool_input"],
            "file_path": f"/sandbox{input_data['tool_input']['file_path']}",
        },
    }
}
```

### Inject Context into Conversation
```python
return {
    "systemMessage": "Remember: /etc is protected.",
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "Protected directory",
    },
}
```

### Ask for Human Approval
```python
return {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
    }
}
```

### Fire-and-Forget (async side effect)
```python
async def logging_hook(input_data, tool_use_id, context):
    asyncio.create_task(send_to_log_service(input_data))
    return {"async_": True, "asyncTimeout": 30000}
```
Cannot block or modify — agent proceeds immediately.

**Priority when hooks conflict:** `deny` > `ask` > `allow`

## Common Patterns

### Block writes to sensitive paths
```python
async def protect_secrets(input_data, tool_use_id, context):
    path = input_data["tool_input"].get("file_path", "")
    for protected in [".env", "/etc/", "secrets/"]:
        if protected in path:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Protected path: {protected}",
                }
            }
    return {}

hooks={"PreToolUse": [HookMatcher(matcher="Write|Edit", hooks=[protect_secrets])]}
```

### Audit log all file changes
```python
import json, datetime

async def audit_log(input_data, tool_use_id, context):
    with open("audit.log", "a") as f:
        f.write(json.dumps({
            "ts": datetime.datetime.now().isoformat(),
            "tool": input_data["tool_name"],
            "input": input_data["tool_input"],
        }) + "\n")
    return {}

hooks={"PostToolUse": [HookMatcher(matcher="Write|Edit|Bash", hooks=[audit_log])]}
```

### Redirect all writes to sandbox
```python
async def sandbox_writes(input_data, tool_use_id, context):
    if input_data["tool_name"] == "Write":
        orig = input_data["tool_input"]["file_path"]
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "updatedInput": {**input_data["tool_input"], "file_path": f"/sandbox{orig}"},
            }
        }
    return {}
```

### Forward notifications to Slack
```python
async def slack_notify(input_data, tool_use_id, context):
    import asyncio, json, urllib.request
    msg = input_data.get("message", "")
    data = json.dumps({"text": f"Agent: {msg}"}).encode()
    req = urllib.request.Request(
        "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
        data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        await asyncio.to_thread(urllib.request.urlopen, req)
    except Exception as e:
        print(f"Slack failed: {e}")
    return {}

hooks={"Notification": [HookMatcher(hooks=[slack_notify])]}
```

### Chain multiple hooks (execute in order)
```python
hooks={
    "PreToolUse": [
        HookMatcher(hooks=[rate_limiter]),       # first
        HookMatcher(hooks=[authorization]),       # second
        HookMatcher(hooks=[sanitize_inputs]),     # third
        HookMatcher(hooks=[audit_logger]),        # last
    ]
}
```

## Gotchas

- **`matcher` filters tool names only** — use `input_data["tool_input"]["file_path"]` inside the callback to filter by path.
- **`updatedInput` needs `permissionDecision: "allow"`** — without it the modification is ignored.
- **`hookEventName` must be in `hookSpecificOutput`** — identifies which hook type the output is for.
- **Hooks don't fire at `max_turns`** — the session ends abruptly.
- **`SessionStart`/`SessionEnd` Python workaround** — use `setting_sources=["project"]` to load them from `.claude/settings.json` shell command hooks instead.
- **Async errors should be caught inside callbacks** — an uncaught exception interrupts the agent.
