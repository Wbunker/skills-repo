---
name: claude-managed-agents
description: Build applications using the Claude Managed Agents API (beta) — Anthropic's hosted agent harness with cloud containers, persistent sessions, and streaming events. Use when: building autonomous agent applications with the Anthropic Python/TypeScript SDK; creating agents, environments, or sessions via the REST API; handling streaming SSE events from a running agent; setting up PR review agents, coding agents, or other long-running task agents; implementing ID persistence for agent/environment reuse; or using the `ant` CLI to manage agents. Distinct from Claude Code subagents (.claude/agents/ markdown files) — this is the REST API for managed cloud agents.
---

# Claude Managed Agents

Anthropic's hosted agent harness. Instead of building your own agent loop, you get cloud containers with pre-installed tools, persistent sessions, and real-time streaming.

**Beta header required on all requests:** `managed-agents-2026-04-01` (SDK sets it automatically)

## Core Concepts

| Concept | Description |
|---|---|
| **Agent** | Reusable config: model + system prompt + tools. Create once, reference by ID. Versioned. |
| **Environment** | Cloud container template: packages, networking. Create once, reuse across sessions. |
| **Session** | A running agent instance (agent + environment + task). Create fresh per task. |
| **Events** | Bidirectional: send `user.message` → receive `agent.message`, `agent.tool_use`, `session.status_*` |

## Workflow

### 1. Install

```bash
pip install anthropic          # Python
npm install @anthropic-ai/sdk  # TypeScript
```

### 2. Create an Agent (once, save the ID)

```python
from anthropic import Anthropic
client = Anthropic()

agent = client.beta.agents.create(
    name="PR Review Agent",
    model="claude-sonnet-4-6",
    system="You are an expert code reviewer...",
    tools=[{"type": "agent_toolset_20260401"}],  # full built-in toolset
)
# Save agent.id to config — reuse across sessions
```

`agent_toolset_20260401` enables: bash, file read/write/edit/glob/grep, web search, web fetch.

### 3. Create an Environment (once, save the ID)

```python
environment = client.beta.environments.create(
    name="review-env",
    config={
        "type": "cloud",
        "networking": {"type": "unrestricted"},
    },
)
# Save environment.id to config
```

### 4. Create a Session (fresh per task)

```python
session = client.beta.sessions.create(
    agent=agent_id,
    environment_id=environment_id,
    title=f"PR Review — {repo_name} — {timestamp}",
    max_turns=30,
    max_budget_usd=2.00,
)
```

### 5. Stream and Send Events

```python
with client.beta.sessions.events.stream(session.id) as stream:
    # Send the user message AFTER opening the stream
    client.beta.sessions.events.send(
        session.id,
        events=[{
            "type": "user.message",
            "content": [{"type": "text", "text": "Review the PR at /path/to/repo"}],
        }],
    )

    for event in stream:
        match event.type:
            case "agent.message":
                for block in event.content:
                    print(block.text, end="", flush=True)
            case "agent.tool_use":
                print(f"\n[tool: {event.name}]", flush=True)
            case "session.status_idle":
                print("\nDone.")
                break
            case "session.status_error":
                print(f"[ERROR]: {event.error}")
                break
            case "session.budget_exceeded":
                print("[WARN] Budget limit reached")
                break
```

## Key Event Types

| Event | Direction | Meaning |
|---|---|---|
| `user.message` | → agent | Send a task or follow-up |
| `user.interrupt` | → agent | Stop mid-execution |
| `agent.message` | agent → | Text response |
| `agent.tool_use` | agent → | Tool invocation (name, input) |
| `agent.tool_result` | agent → | Tool output |
| `agent.thinking` | agent → | Extended thinking content |
| `session.status_idle` | agent → | Agent finished — **break here** |
| `session.status_error` | agent → | Session error |
| `session.budget_exceeded` | agent → | Hit max_budget_usd |

See [references/events.md](references/events.md) for the full event type list and steering patterns.

## ID Persistence Pattern

Create the agent and environment once; persist their IDs:

```python
import json, os

CONFIG_FILE = "agent_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        return json.load(open(CONFIG_FILE))
    return {}

def save_config(config):
    json.dump(config, open(CONFIG_FILE, "w"), indent=2)

def get_or_create_agent(client, config, fresh=False):
    if not fresh and "agent_id" in config:
        return config["agent_id"]
    agent = client.beta.agents.create(...)
    config["agent_id"] = agent.id
    save_config(config)
    return agent.id
```

## ant CLI (quick management)

```bash
# Install (macOS)
brew install anthropics/tap/ant

# Create agent
ant beta:agents create --name "My Agent" --model '{id: claude-sonnet-4-6}' \
  --system "You are helpful." --tool '{type: agent_toolset_20260401}'

# List agents / environments
ant beta:agents list
ant beta:environments list
```

## Agent Configuration Fields

| Field | Required | Notes |
|---|---|---|
| `name` | Yes | Human-readable label |
| `model` | Yes | `claude-sonnet-4-6`, `claude-opus-4-6`, etc. All Claude 4.5+ supported |
| `system` | No | System prompt (persona/behavior, not the task) |
| `tools` | No | Array of tool configs |
| `mcp_servers` | No | MCP server connections |
| `skills` | No | Domain-specific context with progressive disclosure |
| `description` | No | For your own tracking |
| `metadata` | No | Arbitrary key-value pairs |

To use fast mode (Opus 4.6): `model={"id": "claude-opus-4-6", "speed": "fast"}`

## Session Configuration Fields

| Field | Notes |
|---|---|
| `agent` | Agent ID (required) |
| `environment_id` | Environment ID (required) |
| `title` | Human-readable label for this run |
| `max_turns` | Cap on agentic loop turns |
| `max_budget_usd` | Spend cap per session |

## Gotchas

- **Open the stream BEFORE sending the user message** (Python/TS SDK). In bash/curl, send the event first — the API buffers events until the stream attaches.
- **Always break on `session.status_idle`** — failure to break leaves your stream hanging forever.
- **Agent and environment are reusable; sessions are not.** Create a new session for each task.
- **Handle all terminal events**: `session.status_idle`, `session.status_error`, `session.budget_exceeded` — or the loop never terminates.
- **Version conflicts on update**: pass `version=agent.version` when calling `agents.update()` or the call fails.
- **Array fields on update are fully replaced** (not merged): `tools`, `mcp_servers`, `skills`. Omit to preserve.
- **Rate limits**: 60 req/min for create endpoints, 600 req/min for read/stream endpoints.
- **`anthropic>=0.49.0`** required for Managed Agents SDK support.

## Reference Files

- [references/events.md](references/events.md) — full event type list, steering/interrupt patterns, SSE raw format
- [references/tools.md](references/tools.md) — all built-in tools, per-tool config, custom tools, MCP connector
