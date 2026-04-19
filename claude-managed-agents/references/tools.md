# Tools Reference

## Built-in Tools (agent_toolset_20260401)

| Tool | Name | Description |
|---|---|---|
| Bash | `bash` | Execute bash commands in the container shell |
| Read | `read` | Read a file from the container filesystem |
| Write | `write` | Write a file to the container filesystem |
| Edit | `edit` | Perform string replacement in a file |
| Glob | `glob` | Fast file pattern matching |
| Grep | `grep` | Text search using regex patterns |
| Web fetch | `web_fetch` | Fetch content from a URL |
| Web search | `web_search` | Search the web |

## Enable Full Toolset

```python
tools=[{"type": "agent_toolset_20260401"}]
```

## Disable Specific Tools

```python
tools=[{
    "type": "agent_toolset_20260401",
    "configs": [
        {"name": "web_fetch", "enabled": False},
        {"name": "web_search", "enabled": False},
    ],
}]
```

## Enable Only Specific Tools (whitelist mode)

Start with all disabled, then enable only what you need:

```python
tools=[{
    "type": "agent_toolset_20260401",
    "default_config": {"enabled": False},
    "configs": [
        {"name": "bash", "enabled": True},
        {"name": "read", "enabled": True},
        {"name": "write", "enabled": True},
    ],
}]
```

## Custom Tools

Custom tools are defined in the agent config and executed by your code. Claude emits `agent.custom_tool_use`; you respond with `user.custom_tool_result`.

```python
tools=[
    {"type": "agent_toolset_20260401"},
    {
        "type": "custom",
        "name": "get_weather",
        "description": "Get current weather for a location. Use when the user asks about weather conditions in a specific city or region. Returns temperature, conditions, and humidity.",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name, e.g. 'San Francisco'"},
            },
            "required": ["location"],
        },
    },
]
```

**Custom tool best practices:**
- Write detailed descriptions (3-4+ sentences) — this is the most important factor in tool performance
- Group related operations into one tool with an `action` parameter rather than many separate tools
- Prefix names with the resource (`db_query`, `storage_read`) to avoid ambiguity
- Return only high-signal data; avoid bloated responses that waste context

## MCP Connector

Attach MCP servers to give the agent access to standardized third-party tools:

```python
agent = client.beta.agents.create(
    name="My Agent",
    model="claude-sonnet-4-6",
    tools=[{"type": "agent_toolset_20260401"}],
    mcp_servers=[
        {
            "type": "url",
            "url": "https://my-mcp-server.example.com/sse",
            "name": "my-service",
        }
    ],
)
```

MCP tool calls appear as `agent.mcp_tool_use` / `agent.mcp_tool_result` events in the stream.
