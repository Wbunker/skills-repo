---
name: mcp-expert
description: >
  Deep expertise on the Model Context Protocol (MCP) — architecture, all core
  primitives (tools/resources/prompts/sampling/roots), lifecycle, transports,
  building servers (Python FastMCP + TypeScript), building clients, Claude Code
  integration, OAuth 2.1 auth, and common mistakes. Use for any MCP question:
  designing servers, debugging protocol issues, configuring Claude Code, or
  understanding the spec.
triggers:
  - MCP
  - model context protocol
  - FastMCP
  - mcp server
  - mcp client
  - mcp tool
  - mcp resource
  - mcp prompt
  - sampling mcp
  - stdio transport
  - streamable http
  - mcpServers
  - .mcp.json
  - claude mcp add
---

# MCP Expert

You have deep expertise in the Model Context Protocol (MCP). You can answer questions about:

- Architecture: host/client/server model, two-layer design (data + transport)
- All five core primitives: tools, resources, prompts, sampling, roots
- Protocol lifecycle: initialize handshake, capability negotiation, ping, cancellation, progress
- Transports: stdio (subprocess), Streamable HTTP (current standard), deprecated HTTP+SSE
- Building MCP servers with Python (FastMCP high-level API and low-level SDK)
- Building MCP servers with TypeScript (McpServer + registerTool/registerResource/registerPrompt)
- Building MCP clients in Python (ClientSession, stdio_client, call_tool, read_resource)
- Claude Code MCP integration: `claude mcp add`, scopes, .mcp.json, ~/.claude.json
- Claude Desktop configuration: claude_desktop_config.json format
- OAuth 2.1 authorization for remote servers (Protected Resource Metadata, PKCE, token usage)
- Common mistakes: schema validation, transport mismatches, naming, error handling, session mgmt

## Reference Files

Load these on demand based on the question:

- **mcp-core.md** — What is MCP, architecture, all five primitives (tools/resources/prompts/sampling/roots) with full JSON examples, lifecycle, transports, JSON-RPC message format. Load for most MCP questions.
- **mcp-building.md** — Python FastMCP (decorators, Context, lifespan, structured output, low-level API, ASGI mounting), TypeScript SDK (McpServer, registerTool, registerResource, registerPrompt, stdio/HTTP transports), full client examples. Load when building servers or clients.
- **mcp-claude-integration.md** — Claude Code `claude mcp add` CLI, scopes (local/project/user), ~/.claude.json and .mcp.json format, Claude Desktop config, tool approval, OAuth flow, env vars. Load for Claude Code / Claude Desktop config questions.
- **mcp-auth-and-gotchas.md** — OAuth 2.1 full flow, PKCE, Client ID Metadata Documents, token handling, confused deputy problem, common mistakes (schema errors, transport mismatches, naming, error codes, session management, Windows quirks), all protocol methods reference. Load for auth questions or debugging.
- **mcp-security-vulnerabilities.md** — CVEs (CVE-2025-6514 mcp-remote RCE, CVSS 9.6), full attack taxonomy (tool poisoning, prompt injection via tool output, rug pull, tool shadowing, confused deputy, implicit tool call, orchestration injection, supply chain attacks, config file theft), real-world incidents (postmark-mcp npm backdoor, Shai-Hulud campaign, WhatsApp/GitHub exfiltration demos), ecosystem statistics, spec-level design weaknesses, and a complete hardening checklist. Load for any security, CVE, attack vector, or hardening question.

## Key Facts

- MCP uses JSON-RPC 2.0 over stdio or Streamable HTTP
- Current stable spec version: `2025-03-26`
- Python package: `mcp` (pip install "mcp[cli]"); FastMCP is the high-level API inside it
- TypeScript: `@modelcontextprotocol/server` (v2 pre-alpha) or `@modelcontextprotocol/sdk` (v1 stable)
- Three server primitives: tools (model-controlled), resources (app-controlled), prompts (user-controlled)
- Two client primitives: sampling (server requests LLM call), elicitation (server requests user input)
- Claude Code stores MCP config in ~/.claude.json (local/user scope) or .mcp.json (project scope)
- Tool errors: use `isError: true` in result (LLM sees it), not JSON-RPC protocol errors
- ALWAYS validate Origin header and bind to 127.0.0.1 for local Streamable HTTP servers
- Streamable HTTP replaces the old HTTP+SSE transport from 2024-11-05
- Tool descriptions are an attack surface: hidden instructions in docstrings/schema are visible to the LLM but not users (tool poisoning)
- CVE-2025-6514: mcp-remote ≤ 0.1.15 allows RCE via crafted OAuth authorization_endpoint; fix: ≥ 0.1.16
- Supply chain reality: first malicious MCP npm package (postmark-mcp) appeared September 2025; 53% of servers use unrotated static API keys
