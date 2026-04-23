---
name: openai-expert
description: >
  Expert guide covering all OpenAI products, surfaces, and APIs. Use when: deciding which OpenAI
  product or approach to use; building apps with the Chat Completions API or Responses API (the
  recommended new API for all new projects); tool use / function calling / structured outputs /
  streaming / prompt caching; using the OpenAI Agents SDK (agents, handoffs, guardrails, tracing);
  using the Codex CLI for agentic terminal coding; the Assistants API (deprecated Aug 2026 — migrate
  to Responses API); Realtime API for speech-to-speech; embeddings, fine-tuning, or batch API;
  built-in server tools (web_search_preview, code_interpreter, file_search, computer_use_preview,
  image_generation, MCP connector); GPT-4.1 / GPT-4o / o3 / o4-mini model families and tradeoffs;
  Azure OpenAI, GitHub Copilot SDK, or MCP integration with OpenAI.
---

# OpenAI Expert

Reference hub for all OpenAI products and APIs. Use the decision matrix below, then load the relevant reference file.

## Decision Matrix

| Goal | Product / Approach | Reference |
|---|---|---|
| Chat with AI, no code | ChatGPT web or mobile | — |
| New app — general conversational | Chat Completions API + GPT-4.1 | [chat-completions-api.md](references/chat-completions-api.md) |
| New app — agentic, tools, stateful | Responses API (**recommended**) | [responses-api.md](references/responses-api.md) |
| Autonomous agents in code | Agents SDK | [agents-sdk.md](references/agents-sdk.md) |
| Agentic coding in terminal | Codex CLI | [codex-cli.md](references/codex-cli.md) |
| Multi-turn without managing state | Responses API `previous_response_id` | [responses-api.md](references/responses-api.md) |
| Threads/runs/file search (legacy) | Assistants API — **DEPRECATED Aug 2026** | [assistants-api.md](references/assistants-api.md) |
| Speech-to-speech / voice apps | Realtime API | [realtime-api.md](references/realtime-api.md) |
| Semantic search / RAG | Embeddings + `file_search` tool | [embeddings-finetuning-batch.md](references/embeddings-finetuning-batch.md) |
| Domain-specific model adaptation | Fine-tuning | [embeddings-finetuning-batch.md](references/embeddings-finetuning-batch.md) |
| Large-volume async (50% off) | Batch API | [embeddings-finetuning-batch.md](references/embeddings-finetuning-batch.md) |
| Live web search in API | `web_search_preview` built-in tool | [built-in-tools.md](references/built-in-tools.md) |
| Code execution in sandbox | `code_interpreter` built-in tool | [built-in-tools.md](references/built-in-tools.md) |
| GUI / browser automation | `computer_use_preview` built-in tool | [built-in-tools.md](references/built-in-tools.md) |
| Image generation in conversation | `image_generation` built-in tool | [built-in-tools.md](references/built-in-tools.md) |
| Connect to external tools via MCP | `mcp` built-in tool or Agents SDK | [built-in-tools.md](references/built-in-tools.md) |
| Azure / enterprise deployment | Azure OpenAI (AI Foundry) | [integrations.md](references/integrations.md) |
| IDE coding assistant | GitHub Copilot / Copilot SDK | [integrations.md](references/integrations.md) |
| Choose the right model | Model families | [models.md](references/models.md) |

---

## ChatGPT Products

Consumer/business AI interface at **chatgpt.com**. Plans: Free, Go, Plus, Pro, Business, Team, Enterprise, Edu.

- **Projects**: Persistent workspaces with grouped chats, reference files, custom instructions
- **Canvas**: Collaborative doc/code editing with Python execution; all users
- **Memory**: Cross-session fact persistence (Plus+); user-editable
- **GPTs**: Custom assistants with custom instructions, tools, knowledge files, API actions
- **ChatGPT Search**: Live web results with citations
- **Agent Mode** (absorbed from Operator): Autonomous web browsing via CUA model. Pro/Plus/Team.

→ [chatgpt-products.md](references/chatgpt-products.md)

---

## OpenAI API

Two primary endpoints for LLM completions:

**Responses API** (`POST /v1/responses`) — **recommended for all new projects**. Server-managed multi-turn via `previous_response_id`, all built-in server tools, richer reasoning model support, 40–80% better cache utilization. Uses `input` + `instructions` instead of `messages` + system.

**Chat Completions API** (`POST /v1/chat/completions`) — stateless (caller resends full history). Supported indefinitely. Compatible with 100+ LLMs via OpenAI SDK.

Both support: tool use/function calling, streaming, vision, structured outputs, prompt caching.

SDKs: Python (`pip install openai`), TypeScript (`npm install openai`).

→ [responses-api.md](references/responses-api.md) · [chat-completions-api.md](references/chat-completions-api.md)

---

## Developer Tools

### Codex CLI
Open-source terminal agentic coding tool (Rust). Full-screen TUI, image inputs, MCP, isolated git worktree subagents. Comparable to Claude Code.
→ [codex-cli.md](references/codex-cli.md)

### Agents SDK
Python/TypeScript SDK for building production agents. Key differentiators: first-class `handoff()` primitive, built-in guardrails with tripwires, auto-enabled tracing dashboard.
→ [agents-sdk.md](references/agents-sdk.md)

### Assistants API ⚠️ Deprecated
Shutdown **August 26, 2026**. Migrate to Responses API: threads → `previous_response_id` chaining; runs → synchronous/streaming response.
→ [assistants-api.md](references/assistants-api.md)

### Realtime API
Low-latency bidirectional audio. WebRTC (browser/mobile) or WebSocket (server). Speech-to-speech, turn detection, interrupts.
→ [realtime-api.md](references/realtime-api.md)

---

## Reference Index

| File | Contents |
|---|---|
| [chatgpt-products.md](references/chatgpt-products.md) | Plans, Projects, Canvas, Memory, GPTs, ChatGPT Search, Agent Mode |
| [chat-completions-api.md](references/chat-completions-api.md) | Request shape, streaming, vision, function calling, structured outputs, prompt caching |
| [responses-api.md](references/responses-api.md) | Responses API shape, vs Chat Completions, server-side state, built-in tools, MCP |
| [models.md](references/models.md) | GPT-4.1, GPT-4o, o3, o4-mini — context windows, pricing, selection guide |
| [agents-sdk.md](references/agents-sdk.md) | Agents, tools, handoffs, guardrails, tracing, sessions |
| [codex-cli.md](references/codex-cli.md) | Install, approval modes, MCP, skills, remote TUI, vs Claude Code |
| [assistants-api.md](references/assistants-api.md) | ⚠️ Deprecated Aug 2026. Threads, runs, file search, migration path |
| [realtime-api.md](references/realtime-api.md) | WebRTC vs WebSocket, events, voices, turn detection |
| [embeddings-finetuning-batch.md](references/embeddings-finetuning-batch.md) | Embedding models, fine-tuning workflow, batch API |
| [built-in-tools.md](references/built-in-tools.md) | web_search_preview, code_interpreter, file_search, computer_use_preview, image_generation, MCP |
| [integrations.md](references/integrations.md) | Azure OpenAI, GitHub Copilot SDK, MCP ecosystem |
