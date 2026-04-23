---
name: claude-expert
description: >
  Expert guide covering all Claude products, surfaces, and APIs. Use when: deciding which Claude
  product or approach to use for a task; building apps with the Claude API (Messages API, Python/TS
  SDKs, tool use, streaming, prompt caching, batch API, Files API); using Claude Code CLI or IDE
  extensions; building autonomous agents with the Claude Agent SDK; using the Managed Agents REST
  API (cloud-hosted agent sessions); connecting Claude to Telegram/Discord/CI via Channels;
  automating browsers with Claude in Chrome; working with MCP servers; integrating with Slack or
  GitHub Actions; or any question about Claude model families, capabilities, and tradeoffs.
---

# Claude Expert

Reference hub for all Claude products and APIs. Use the decision matrix below to navigate to the right area, then load the reference file for details.

## Decision Matrix

| Goal | Product / Approach | Reference |
|---|---|---|
| Chat, no code | claude.ai web or mobile | — |
| Build a product with Claude | Messages API + Python/TS SDK | [api.md](references/api.md) |
| Agentic coding in terminal | Claude Code CLI | [claude-code.md](references/claude-code.md) |
| Agentic coding in editor | VS Code / JetBrains extension | [claude-code.md](references/claude-code.md) |
| Embed the agent loop in an app | Claude Agent SDK | [agent-sdk.md](references/agent-sdk.md) |
| Hosted cloud agent with streaming | Managed Agents REST API | [managed-agents.md](references/managed-agents.md) |
| Push events into a running session (Telegram/Discord/CI) | Channels | [channels.md](references/channels.md) |
| Browser automation from Claude | Claude in Chrome | [chrome.md](references/chrome.md) |
| Connect Claude to external tools/data | MCP | [integrations.md](references/integrations.md) |
| Slack/GitHub/GitLab CI integration | Platform integrations | [integrations.md](references/integrations.md) |
| Choose the right model | Model families | [models.md](references/models.md) |
| Process large volumes cheaply | Batch API (50% discount) | [api.md](references/api.md) |
| Reduce cost on repeated large contexts | Prompt Caching (~90% on hits) | [api.md](references/api.md) |

---

## Claude.ai Products

**Web app** (`claude.ai`): Multi-turn chat, file/image uploads, voice mode.
- **Projects**: Persistent workspaces with knowledge base (RAG), custom instructions, shareable with teammates (Team/Enterprise).
- **Artifacts**: Generated outputs (code, SVG, HTML, React, Markdown) that render in a side panel, shareable by link.
- **Plans**: Free (limited), Pro, Max, Team (multi-seat + shared Projects), Enterprise (SCIM, SSO, audit logs, HIPAA-ready).

**Claude Code on the web** (`claude.ai/code`): Browser-based agentic coding — no local setup, cloud sandbox, clones from GitHub. Use `claude --teleport` to pull a web session into a local terminal.

---

## Claude API

Direct programmatic access via REST. Core endpoint: `POST /v1/messages`.

Key capabilities: tool use / function calling, streaming, vision, extended thinking, structured JSON output, prompt caching, batch processing, Files API.

SDKs: Python (`pip install anthropic`), TypeScript (`npm install @anthropic-ai/sdk`), plus C#, Go, Java, PHP, Ruby.

Also available on: Amazon Bedrock, Google Vertex AI, Microsoft Azure Foundry.

→ Full reference: [api.md](references/api.md)

---

## Claude Code

Agentic coding tool. Reads codebases, edits files, runs commands, integrates with dev tools.

**Surfaces**: CLI (`claude`), VS Code extension, JetBrains plugin, desktop app, web interface, mobile via Dispatch.

**Key features**: CLAUDE.md persistent instructions, hooks (auto-run scripts on lifecycle events), subagents (`.claude/agents/`), MCP server support, scheduled tasks, GitHub Actions integration.

→ Full reference: [claude-code.md](references/claude-code.md)

---

## Developer Tools (Deeper Dives)

### Agent SDK
The Claude Code agent loop as a library — callable from Python or TypeScript. Same tools, same intelligence, no loop to implement yourself. Best for CI/CD pipelines, production automation, custom applications.

→ [agent-sdk.md](references/agent-sdk.md) · [agent-sdk-options.md](references/agent-sdk-options.md) · [agent-sdk-hooks.md](references/agent-sdk-hooks.md) · [agent-sdk-sessions.md](references/agent-sdk-sessions.md)

### Managed Agents API
Anthropic-hosted agent harness. Cloud containers with pre-installed tools, persistent sessions, real-time SSE event streaming. Create an agent + environment once, spawn sessions per task. SDK auto-handles the `managed-agents-2026-04-01` beta header.

→ [managed-agents.md](references/managed-agents.md) · [managed-agents-events.md](references/managed-agents-events.md) · [managed-agents-tools.md](references/managed-agents-tools.md)

### Channels
Turns Claude Code into a background agent that external systems push events into — Telegram, Discord, CI webhooks, monitoring alerts. Claude maintains session context across events without anyone at the terminal. Research preview; requires Claude Code 2.1.80+ and Bun runtime.

→ [channels.md](references/channels.md) · [channels-telegram.md](references/channels-telegram.md) · [channels-discord.md](references/channels-discord.md) · [channels-custom.md](references/channels-custom.md) · [channels-security.md](references/channels-security.md) · [channels-harness.md](references/channels-harness.md)

### Claude in Chrome
Browser automation extension. Claude Code connects to Chrome via native messaging to drive real browser sessions using your existing login state. Reads DOM, fills forms, takes screenshots, records GIFs.

→ [chrome.md](references/chrome.md) · [chrome-tools.md](references/chrome-tools.md) · [chrome-context.md](references/chrome-context.md) · [chrome-quick-mode.md](references/chrome-quick-mode.md)

### MCP & Integrations
MCP (Model Context Protocol) is the open standard for connecting AI applications to external tools and data. Claude Code integrates with Slack, GitHub Actions, GitLab, and hundreds of MCP servers.

→ [integrations.md](references/integrations.md)

---

## Reference Index

| File | Contents |
|---|---|
| [api.md](references/api.md) | Messages API, SDKs, tool use, streaming, caching, batch, Files API |
| [claude-code.md](references/claude-code.md) | CLI flags, IDE extensions, hooks, settings, subagents, MCP config, built-in slash commands (`/review`, `/ultrareview`, `/ultraplan`, etc.), prompting tips (`ultrathink`, evidence rule) |
| [models.md](references/models.md) | Opus/Sonnet/Haiku families, pricing, tradeoffs, selection guide |
| [integrations.md](references/integrations.md) | Slack, GitHub Actions, MCP protocol, MCP registry |
| [agent-sdk.md](references/agent-sdk.md) | `query()` API, tools, permission modes, hooks, subagents |
| [agent-sdk-options.md](references/agent-sdk-options.md) | Full `ClaudeAgentOptions` reference (Python dataclass + TS equivalents) |
| [agent-sdk-hooks.md](references/agent-sdk-hooks.md) | Hook events, callback signatures, output format, common patterns |
| [agent-sdk-sessions.md](references/agent-sdk-sessions.md) | Resume, fork, multi-turn, `ClaudeSDKClient`, session management functions |
| [managed-agents.md](references/managed-agents.md) | Agent/environment/session lifecycle, streaming pattern, `ant` CLI |
| [managed-agents-events.md](references/managed-agents-events.md) | Full event type list, streaming code (Python/TS/curl), interrupt, steering |
| [managed-agents-tools.md](references/managed-agents-tools.md) | Built-in toolset, enable/disable/whitelist, custom tools, MCP connector |
| [channels.md](references/channels.md) | Quick start, permission tradeoff, `--dangerously-skip-permissions` |
| [channels-telegram.md](references/channels-telegram.md) | BotFather setup, bot tokens, long polling mechanics, limitations |
| [channels-discord.md](references/channels-discord.md) | Developer Portal setup, Gateway vs webhooks, permissions, limitations |
| [channels-custom.md](references/channels-custom.md) | CI/CD webhooks, monitoring alerts, custom event sources, payload design |
| [channels-security.md](references/channels-security.md) | Security model, pairing auth, prompt injection, Teams/Enterprise enablement |
| [channels-harness.md](references/channels-harness.md) | CI triage, monitoring triage, async task notification patterns |
| [chrome.md](references/chrome.md) | Session startup, tool selection decision tree, token hygiene, failure modes |
| [chrome-tools.md](references/chrome-tools.md) | Full parameter schemas for all 21 `mcp__claude-in-chrome__*` tools |
| [chrome-context.md](references/chrome-context.md) | ref ID system, MV3 timeout, CLAUDE.md patterns, permission modes |
| [chrome-quick-mode.md](references/chrome-quick-mode.md) | Compact single-letter command language for high-frequency automation |
