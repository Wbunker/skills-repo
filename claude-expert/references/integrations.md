# Integrations & MCP

## Table of Contents
- [MCP (Model Context Protocol)](#mcp-model-context-protocol)
- [Slack Integration](#slack-integration)
- [GitHub Actions](#github-actions)
- [GitLab CI/CD](#gitlab-cicd)
- [Other Integrations](#other-integrations)

---

## MCP (Model Context Protocol)

Open standard (JSON-RPC 2.0) for connecting AI applications to external tools and data. "USB-C for AI."

### Architecture

| Role | Description |
|---|---|
| **MCP Host** | AI application (Claude Code, Claude Desktop, VS Code, Cursor, etc.) |
| **MCP Client** | Component inside the host managing one server connection |
| **MCP Server** | Program exposing tools/resources/prompts |

Transports:
- **stdio** — local process, same machine
- **Streamable HTTP** — remote server, supports OAuth/bearer/API key auth

### Server Primitives

| Primitive | What it exposes |
|---|---|
| **Tools** | Executable functions (file ops, API calls, DB queries). `tools/list` + `tools/call` |
| **Resources** | Data sources (file contents, DB records, API responses). `resources/list` + `resources/get` |
| **Prompts** | Reusable templates and few-shot examples |

### Client Primitives

| Primitive | Purpose |
|---|---|
| **Sampling** | Server requests LLM completion from client |
| **Elicitation** | Server requests user input/confirmation |
| **Logging** | Server sends debug messages to client |

### Protocol Flow

1. Client sends `initialize` with protocol version + capabilities
2. Server responds with its capabilities
3. Client sends `notifications/initialized`
4. Client calls `tools/list` to discover tools
5. Client calls `tools/call` to invoke

### Building MCP Servers

SDKs available for Python, TypeScript, and others. Reference implementations at `github.com/modelcontextprotocol/servers`. Use MCP Inspector for development/testing.

### MCP Registry

Official listing of commercial MCP servers: `https://api.anthropic.com/mcp-registry/v0/servers`

Install plugins with MCP servers: `/plugin install <name>@<marketplace>`

### MCP Connector (API-level)

Use MCP servers directly with the Messages API (without Claude Code) via `mcp_connector` — see Anthropic platform docs.

---

## Slack Integration

Claude for Slack app (Slack App ID: `A08SF47R6P4`).

**Routing modes:**
- `Code only` — all `@Claude` mentions spawn a Claude Code web session
- `Code + Chat` — intelligent routing: coding tasks → Code session, general questions → chat

**`@Claude` mention flow:**
1. Claude Code web session is created
2. Status updates posted to the thread
3. On completion: "View Session" link + "Create PR" button appear

**Context gathered:** thread messages + recent channel messages.

**Requirements:** user must connect Claude account, GitHub connected with repos, Claude Code on the web enabled.

---

## GitHub Actions

`anthropic/claude-code-action@v1`

**Trigger on `@claude` mention:**
```yaml
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
```

**Automation mode (no trigger phrase):**
```yaml
- uses: anthropic/claude-code-action@v1
  with:
    prompt: "Review this PR for security issues"
    claude_args: "--max-turns 20"
```

**Quickstart:** run `/install-github-app` in Claude Code CLI.

**Auth options:** Direct Anthropic API key, AWS Bedrock (OIDC), Google Vertex AI (OIDC).

### Automatic Code Review

Separate from the `@claude` mention action — posts a review on every PR without needing a trigger phrase. Configured independently.

---

## GitLab CI/CD

Similar to GitHub Actions integration. Claude Code can be triggered from GitLab pipelines and MR comments.

---

## Other Integrations

Via MCP registry and plugin system, Claude Code connects to: Jira, Google Drive, Notion, databases, and hundreds of third-party services.

**Scheduled / Remote agents (Routines):** Run on Anthropic-managed infrastructure. Keep running when your computer is off. Trigger on schedule (cron), API calls, or GitHub events. Create from web UI, Desktop app, or `/schedule` CLI command.
