# Session Management Reference

## When to Use Each Approach

| Use case | Approach |
|---|---|
| Single one-shot task | Plain `query()`, nothing extra |
| Multi-turn chat in one process | `ClaudeSDKClient` (Python) or `continue: true` (TypeScript) |
| Resume most recent session after restart | `continue_conversation=True` / `continue: true` |
| Resume a specific past session | Capture session ID, pass to `resume=` |
| Try an alternative approach without losing original | `fork_session=True` + `resume=session_id` |
| Stateless (no disk write) | TypeScript only: `persistSession: false` |

## ClaudeSDKClient — Multi-turn in One Process (Python)

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock

async def main():
    options = ClaudeAgentOptions(allowed_tools=["Read", "Edit", "Glob", "Grep"])

    async with ClaudeSDKClient(options=options) as client:
        # First turn
        await client.query("Analyze the auth module")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

        # Second turn — full context from first turn retained automatically
        await client.query("Now refactor it to use JWT")
        async for msg in client.receive_response():
            if isinstance(msg, ResultMessage):
                print(msg.result)

asyncio.run(main())
```

`ClaudeSDKClient` manages session IDs internally. Use as an async context manager.

## TypeScript Multi-turn: `continue: true`

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// First call: creates a new session
for await (const msg of query({
  prompt: "Analyze the auth module",
  options: { allowedTools: ["Read", "Glob", "Grep"] }
})) { /* ... */ }

// Second call: continue: true resumes the most recent session in cwd
for await (const msg of query({
  prompt: "Now refactor it to use JWT",
  options: { continue: true, allowedTools: ["Read", "Edit", "Glob"] }
})) {
  if (msg.type === "result") console.log(msg.result);
}
```

## Capturing Session ID

Session ID is on `ResultMessage.session_id` (always present):

```python
session_id = None
async for msg in query(prompt="Analyze auth.py", options=...):
    if isinstance(msg, ResultMessage):
        session_id = msg.session_id
        print(f"Session: {session_id}, cost: ${msg.total_cost_usd:.4f}")
```

TypeScript: also available earlier on the init `SystemMessage`:
```typescript
for await (const msg of query({ prompt: "..." })) {
  if (msg.type === "system" && msg.subtype === "init") {
    sessionId = msg.session_id;  // available before result
  }
}
```

## Resume by ID

```python
# Continue a specific prior session
async for msg in query(
    prompt="Implement the refactoring you suggested",
    options=ClaudeAgentOptions(
        resume=session_id,
        allowed_tools=["Read", "Edit", "Write", "Glob"],
    ),
):
    if isinstance(msg, ResultMessage):
        print(msg.result)
```

Recovers from limits by resuming with higher budget:
```python
options=ClaudeAgentOptions(
    resume=session_id,
    max_turns=50,       # was 20, ran out
    max_budget_usd=5.0, # was 1.0, exceeded
)
```

## Fork a Session

Fork creates a new session branching from `session_id`'s history. Original unchanged.

```python
# Fork: explore OAuth2 while preserving JWT thread
forked_id = None
async for msg in query(
    prompt="Try OAuth2 instead of JWT",
    options=ClaudeAgentOptions(resume=session_id, fork_session=True),
):
    if isinstance(msg, ResultMessage):
        forked_id = msg.session_id  # new ID, different from session_id

# Original session still accessible
async for msg in query(
    prompt="Continue with JWT",
    options=ClaudeAgentOptions(resume=session_id),
):
    ...
```

> Fork branches conversation history only — not the filesystem. File edits from a forked agent are real and affect the same directory.

## Continue Most Recent (no ID needed)

```python
# Resume most recent session in cwd without tracking IDs
options = ClaudeAgentOptions(continue_conversation=True)
```

Useful for simple scripts that run sequentially and don't need multiple simultaneous sessions.

## Session Management Functions

```python
from claude_agent_sdk import list_sessions, get_session_messages, get_session_info, rename_session, tag_session

# List sessions in a directory
for s in list_sessions(directory="/path/to/project", limit=10):
    print(f"{s.session_id}: {s.summary}")

# Read full transcript
msgs = get_session_messages(session_id, directory="/path/to/project")

# Get metadata
info = get_session_info(session_id)

# Organize
rename_session(session_id, "auth-refactor-attempt-1")
tag_session(session_id, "completed")
```

## Resuming Across Hosts

Session files live at `~/.claude/projects/<encoded-cwd>/<session-id>.jsonl`.

Options for cross-host resume:
1. Copy the `.jsonl` file to the same path on the new host (same `cwd` required)
2. Don't rely on resume — extract results into application state and pass context in the next prompt

## ResultMessage Subtypes

Always check `subtype` before using `result`:

| Subtype | Meaning |
|---|---|
| `success` | Task completed, `result` has output |
| `error_max_turns` | Ran out of turns — resume with `max_turns` higher |
| `error_max_budget_usd` | Budget exceeded — resume with higher `max_budget_usd` |
| `error_api_error` | API error — check `result` for details |
| `error_*` | Other errors |
