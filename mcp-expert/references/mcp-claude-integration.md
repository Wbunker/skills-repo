# MCP — Claude Code & Claude Desktop Integration

## Claude Code MCP Configuration

Claude Code acts as an MCP host. It connects to MCP servers you configure and passes their tools/resources/prompts to Claude.

### Adding Servers via CLI

```bash
# HTTP server (recommended for remote)
claude mcp add --transport http <name> <url>
claude mcp add --transport http notion https://mcp.notion.com/mcp
claude mcp add --transport http secure-api https://api.example.com/mcp \
  --header "Authorization: Bearer your-token"

# SSE server (deprecated, use HTTP instead)
claude mcp add --transport sse <name> <url>

# stdio server (local process)
claude mcp add [options] <name> -- <command> [args...]
claude mcp add --transport stdio airtable \
  --env AIRTABLE_API_KEY=YOUR_KEY \
  -- npx -y airtable-mcp-server

# Windows: wrap with cmd /c for npx
claude mcp add --transport stdio my-server -- cmd /c npx -y @some/package
```

**Important:** All options (`--transport`, `--env`, `--scope`, `--header`) MUST come BEFORE the server name. The `--` separates options from the server's command.

### Managing Servers

```bash
claude mcp list              # list all configured servers
claude mcp get github        # details for a specific server
claude mcp remove github     # remove a server
/mcp                         # within Claude Code: check server status + authenticate OAuth
```

### Scopes

| Scope | Default? | Stored In | Shared? | Available In |
|-------|----------|-----------|---------|--------------|
| `local` | yes | `~/.claude.json` | No | Current project only |
| `project` | no | `.mcp.json` in project root | Yes (commit it) | Current project only |
| `user` | no | `~/.claude.json` | No | All your projects |

```bash
claude mcp add --scope local ...    # private to you, current project (default)
claude mcp add --scope project ...  # shared with team via .mcp.json
claude mcp add --scope user ...     # personal, all projects
```

**Precedence (highest to lowest):** local → project → user → plugin-provided → claude.ai connectors.

### ~/.claude.json Format (local/user scope)

```json
{
  "projects": {
    "/path/to/your/project": {
      "mcpServers": {
        "stripe": {
          "type": "http",
          "url": "https://mcp.stripe.com"
        },
        "my-local-tool": {
          "command": "python",
          "args": ["/path/to/server.py"],
          "env": {
            "API_KEY": "abc123"
          }
        }
      }
    }
  }
}
```

### .mcp.json Format (project scope, commit this file)

```json
{
  "mcpServers": {
    "shared-server": {
      "command": "/path/to/server",
      "args": [],
      "env": {}
    },
    "database-tools": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
      "args": ["--config", "config.json"],
      "env": {
        "DB_URL": "${DB_URL}",
        "PORT": "${PORT:-5432}"
      }
    }
  }
}
```

**Environment variable expansion in .mcp.json:**
- `${VAR}` — value of env var VAR
- `${VAR:-default}` — VAR if set, otherwise "default"
- Works in: `command`, `args`, `env`, `url`, `headers`

### Claude Desktop Config Format

Location:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/alice/Desktop"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..."
      }
    },
    "remote-api": {
      "type": "http",
      "url": "https://api.example.com/mcp",
      "headers": {
        "Authorization": "Bearer your-token"
      }
    }
  }
}
```

Restart Claude Desktop completely after editing this file.

### Tool Approval Flow

1. Claude decides to use an MCP tool based on conversation context
2. Claude Code shows the tool call (name + args) to the user
3. User approves or denies
4. On approval, Claude Code calls the tool on the MCP server
5. Result is returned to Claude for processing

The `/mcp` command in Claude Code lets you:
- See connected server status
- Authenticate with OAuth 2.0 remote servers

### Environment Variables

- `MCP_TIMEOUT` — server startup timeout in ms (e.g., `MCP_TIMEOUT=10000`)
- `MAX_MCP_OUTPUT_TOKENS` — max tokens per tool output (default 10,000; e.g., `MAX_MCP_OUTPUT_TOKENS=50000`)

### Dynamic Tool Updates

Claude Code supports `list_changed` notifications. When an MCP server sends `notifications/tools/list_changed`, Claude Code automatically refreshes available capabilities without reconnecting.

### Security Warning

Prompt injection risk: Be careful with MCP servers that fetch untrusted content (web pages, user files). Malicious content could embed instructions that manipulate Claude.

---

## Authentication / OAuth Flow in Claude Code

For remote HTTP servers requiring OAuth:
1. Run `/mcp` inside Claude Code
2. Claude Code opens the OAuth authorization URL in your browser
3. Complete the login flow
4. Token is stored and used for subsequent requests

---

## Adding Your Own FastMCP Server to Claude Code

```bash
# Start the server
uv run python myserver.py  
# (runs on http://localhost:8000/mcp by default for streamable-http)

# Add to Claude Code
claude mcp add --transport http my-server http://localhost:8000/mcp

# Or for stdio:
claude mcp add my-server -- python /absolute/path/to/server.py
```

Then verify with `claude mcp list` or `/mcp` inside Claude Code.
