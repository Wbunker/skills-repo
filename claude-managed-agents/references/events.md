# Events and Streaming Reference

## Event Type Index

### User Events (you → agent)

| Type | Description |
|---|---|
| `user.message` | Send a task or follow-up message |
| `user.interrupt` | Stop the agent mid-execution |
| `user.custom_tool_result` | Respond to an `agent.custom_tool_use` event |
| `user.tool_confirmation` | Approve or deny a tool call (when permission policy requires it) |
| `user.define_outcome` | Define an outcome for the agent to work toward (research preview) |

### Agent Events (agent → you)

| Type | Description |
|---|---|
| `agent.message` | Text response (has `.content[]` with text blocks) |
| `agent.thinking` | Extended thinking content (separate from messages) |
| `agent.tool_use` | Built-in tool invocation (`.name`, `.input`) |
| `agent.tool_result` | Built-in tool execution result |
| `agent.mcp_tool_use` | MCP tool invocation |
| `agent.mcp_tool_result` | MCP tool result |
| `agent.custom_tool_use` | Your custom tool invoked — respond with `user.custom_tool_result` |

### Session Status Events (agent → you)

| Type | Description |
|---|---|
| `session.status_idle` | **Agent finished — break your stream loop here** |
| `session.status_error` | Session error — check `event.error` |
| `session.budget_exceeded` | `max_budget_usd` reached |
| `session.turn_limit_reached` | `max_turns` reached |

### Span Events (observability)

Emitted to track agent reasoning phases. Usually not needed for basic applications.

## Streaming Pattern (Python)

```python
with client.beta.sessions.events.stream(session.id) as stream:
    # IMPORTANT: send user message AFTER opening stream
    client.beta.sessions.events.send(
        session.id,
        events=[{
            "type": "user.message",
            "content": [{"type": "text", "text": "your task here"}],
        }],
    )

    for event in stream:
        match event.type:
            case "agent.message":
                for block in event.content:
                    if hasattr(block, "text"):
                        print(block.text, end="", flush=True)
            case "agent.tool_use":
                print(f"\n[tool: {event.name}]")
            case "agent.tool_result":
                pass  # optional: log tool output
            case "session.status_idle":
                break
            case "session.status_error":
                raise RuntimeError(f"Session error: {event.error}")
            case "session.budget_exceeded":
                print("[WARN] Budget exceeded")
                break
            case "session.turn_limit_reached":
                print("[WARN] Turn limit reached")
                break
```

## Streaming Pattern (TypeScript)

```typescript
const stream = await client.beta.sessions.events.stream(session.id);

// Send AFTER stream opens
await client.beta.sessions.events.send(session.id, {
  events: [{
    type: "user.message",
    content: [{ type: "text", text: "your task here" }],
  }],
});

for await (const event of stream) {
  if (event.type === "agent.message") {
    for (const block of event.content) {
      process.stdout.write(block.text);
    }
  } else if (event.type === "agent.tool_use") {
    console.log(`\n[tool: ${event.name}]`);
  } else if (event.type === "session.status_idle") {
    break;
  } else if (event.type === "session.status_error") {
    throw new Error(`Session error: ${event.error}`);
  } else if (event.type === "session.budget_exceeded") {
    console.warn("Budget exceeded");
    break;
  }
}
```

## curl / bash Pattern

With curl, **send the user event first** (API buffers until stream attaches):

```bash
# 1. Send user message
curl -sS https://api.anthropic.com/v1/sessions/$SESSION_ID/events \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: managed-agents-2026-04-01" \
  -H "content-type: application/json" \
  -d '{"events": [{"type": "user.message", "content": [{"type": "text", "text": "your task"}]}]}' \
  > /dev/null

# 2. Open SSE stream
while IFS= read -r line; do
  [[ $line == data:* ]] || continue
  json=${line#data: }
  case $(jq -r '.type' <<<"$json") in
    agent.message) jq -j '.content[] | select(.type=="text") | .text' <<<"$json" ;;
    agent.tool_use) printf '\n[tool: %s]\n' "$(jq -r '.name' <<<"$json")" ;;
    session.status_idle) echo; break ;;
  esac
done < <(curl -sS -N \
  "https://api.anthropic.com/v1/sessions/$SESSION_ID/stream" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: managed-agents-2026-04-01" \
  -H "Accept: text/event-stream")
```

## Handling Custom Tool Calls

When Claude calls a custom tool, you receive `agent.custom_tool_use`. You must respond with `user.custom_tool_result`:

```python
for event in stream:
    match event.type:
        case "agent.custom_tool_use":
            # event.name = tool name, event.input = dict of arguments
            result = my_tool_executor(event.name, event.input)
            client.beta.sessions.events.send(
                session.id,
                events=[{
                    "type": "user.custom_tool_result",
                    "tool_use_id": event.id,
                    "content": [{"type": "text", "text": str(result)}],
                }],
            )
        case "session.status_idle":
            break
```

## Interrupting a Session

Send `user.interrupt` to stop the agent mid-execution:

```python
client.beta.sessions.events.send(
    session.id,
    events=[{"type": "user.interrupt"}],
)
```

After interrupting, you can send a new `user.message` to redirect the agent.

## Steering Mid-Execution

Send a `user.message` while the agent is running to provide additional context or change direction. The agent will incorporate it at the next natural pause point.

## Retrieving Full Event History

All events are persisted server-side and can be fetched:

```python
for event in client.beta.sessions.events.list(session.id):
    print(event.type, event)
```
