# Integrations & MCP

## Table of Contents
- [MCP (Model Context Protocol)](#mcp-model-context-protocol)
- [Slack Integration](#slack-integration)
- [GitHub Actions](#github-actions)
- [GitLab CI/CD](#gitlab-cicd)
- [Other Integrations](#other-integrations)
- [Delegating cheap work to a worker model (token saving)](#delegating-cheap-work-to-a-worker-model-token-saving)

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

---

## Delegating cheap work to a worker model (token saving)

A pattern for stretching a Claude plan's token budget: keep Claude as the reasoner and offload its **bulk I/O** to a cheaper long-context model. Claude Code's **Bash tool runs any command on `PATH`**, so Claude can shell out to a small CLI that calls a cheap OpenAI-compatible model (Kimi, DeepSeek, Qwen, Gemini Flash, …) — **no MCP server or plugin required**, just a script in `~/bin/` and a routing rule.

**The boundary that makes it pay off — Claude = thinking, worker = I/O:**

| Delegate to the worker | Keep on Claude |
|---|---|
| Reading many/large files to answer one question → summary | Architecture & design decisions |
| Generating boilerplate (tests, config, docstrings) | Debugging, race conditions, numerical stability |
| Summarizing a session transcript into doc updates | Anything safety-critical or needing careful reasoning |
| First-draft repetitive text Claude then patches | Edits that need exact line numbers |

Typical savings: reading ~5 files (~8,000 tokens) becomes a ~400-token summary Claude reads; a doc update drops from ~5,000 tokens to ~200. The worker reads the files/transcript in full and returns a compact result; Claude spends tokens only on the reasoning and the surgical edits.

**Three tools cover most cases:** a *reader* (`--paths … --question …` → summary), a *writer* (`--spec … --context … --target …` → a generated file Claude reviews), and an *extract-chat* that strips a Claude Code JSONL transcript (`~/.claude/projects/<project>/*.jsonl`) down to clean conversation text to feed the reader for a doc pipeline.

**Routing is the key step — it lives in `CLAUDE.md` or a `.claude/rules/` file**, because Claude won't use the tools unless told when to. Include an explicit *"When NOT to delegate"* list (tasks under ~2,000 tokens where delegation overhead isn't worth it; architecture, debugging, safety-critical code; anything needing exact line numbers) — without it, Claude over-routes and you lose its reasoning where you need it. See [claude-memory.md](claude-memory.md) and [claude-rules.md](claude-rules.md) for where these instructions load.

**Gotchas:**
- **Worker "thinking" models burn the output budget silently** — set the worker's max output tokens high enough to cover internal reasoning *plus* the answer (a too-low cap returns an empty response, no error), or disable the worker's thinking for pure I/O.
- **Order for prefix-cache hits:** stable content (the file corpus) first, the varying question last, so repeated calls over the same files reuse the cached prefix at a discount (both Moonshot and Anthropic do prefix caching).
- **Never delegate reasoning** — cheap workers surface obvious issues but miss subtle bugs.

For a concrete worker implementation (CLI script, model choice, thinking-budget specifics), see the **kimi-code-expert** skill → `references/integrations.md`.
