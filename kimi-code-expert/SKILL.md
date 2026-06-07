---
name: kimi-code-expert
description: >
  Expert guide for Kimi (Moonshot AI) models, APIs, CLI, and agentic capabilities. Use when:
  building apps with the Kimi Chat Completions API (OpenAI-compatible); choosing between
  kimi-k2.6 / kimi-k2.5 / moonshot-v1 models; enabling thinking/reasoning mode; function
  calling and tool use; using official built-in tools (web-search, code_runner, memory, fetch,
  excel, rethink); setting up the Kimi CLI for agentic terminal coding; building agents with
  the agentic loop pattern; uploading files for document QA; streaming, JSON mode, partial
  mode, vision (image/video) input; batch API for async jobs; migrating from OpenAI to Kimi;
  integrating Kimi with Claude Code / Cline / RooCode / OpenClaw; rate limits and pricing;
  Kimi K2.6 benchmarks vs GPT-5.4 / Claude Opus 4.6 / Gemini 3.1 Pro.
---

# Kimi Code Expert

Reference hub for Moonshot AI's Kimi platform. Use the decision matrix below, then load the relevant reference file.

## Decision Matrix

| Goal | Approach | Reference |
|---|---|---|
| Chat app / simple completions | Chat Completions API + kimi-k2.6 | [api.md](references/api.md) |
| Agentic coding, long-horizon tasks | kimi-k2.6 (thinking enabled) | [api.md](references/api.md) |
| Terminal agentic coding (like Claude Code) | Kimi CLI | [cli.md](references/cli.md) |
| Enable deep reasoning / chain-of-thought | Thinking mode on kimi-k2.6 | [features.md](references/features.md) |
| Function calling / tool use | `tools` parameter, agentic loop | [tools-and-agents.md](references/tools-and-agents.md) |
| Live web search in responses | `$web_search` builtin tool | [tools-and-agents.md](references/tools-and-agents.md) |
| Code execution, math, analysis | `code_runner` / `quickjs` official tools | [tools-and-agents.md](references/tools-and-agents.md) |
| Build a multi-step autonomous agent | Agentic loop pattern + official tools | [tools-and-agents.md](references/tools-and-agents.md) |
| Image / video understanding | Vision models (kimi-k2.6, moonshot-v1-*-vision) | [features.md](references/features.md) |
| Document QA (PDF, Office, etc.) | File upload → extract → system prompt | [features.md](references/features.md) |
| Structured JSON output | JSON mode or partial mode | [features.md](references/features.md) |
| Real-time token streaming | `stream=True` + SSE | [features.md](references/features.md) |
| Async bulk jobs (50% off) | Batch API | [integrations.md](references/integrations.md) |
| Migrate from OpenAI | Change base_url + model ID | [integrations.md](references/integrations.md) |
| Use Kimi in Claude Code via direct API | Custom base_url config | [integrations.md](references/integrations.md) |
| Use Kimi in Claude Code via Ollama Cloud | `ollama launch claude --model kimi-k2.6:cloud` | [integrations.md](references/integrations.md) |
| Use Kimi as a cheap delegate/worker for Claude Code (token saving) | Worker CLI on `PATH` + CLAUDE.md routing | [integrations.md](references/integrations.md) |
| Choose the right model | Model families + pricing | [models.md](references/models.md) |

---

## Quick Start

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["MOONSHOT_API_KEY"],
    base_url="https://api.moonshot.ai/v1",
)

resp = client.chat.completions.create(
    model="kimi-k2.6",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(resp.choices[0].message.content)
```

**API base URL:** `https://api.moonshot.ai/v1`  
Get your key at: `https://platform.kimi.ai`

---

## Kimi K2.6 at a Glance

Moonshot AI's flagship model (as of April 2026). Open-weights. Competitive with GPT-5.4, Claude Opus 4.6, and Gemini 3.1 Pro on coding and agentic benchmarks.

**Strengths:** SWE-Bench Pro, long-horizon autonomous coding (13-hour sessions demonstrated), DeepSearchQA (+14 pts over GPT-5.4), BrowseComp with agent swarm.  
**Gaps vs closed frontier:** Hard reasoning/math olympiad tasks, vision (BabyVision ~12 pts behind Gemini 3.1 Pro).

Agent Swarm: scales to 300 concurrent sub-agents, 4,000 coordinated steps — ~4.5x speedup over single-agent execution on parallel-decomposable tasks. Preview at `kimi.com/agent-swarm`.

**K2.6 vs K2.5 improvements:** deeper reasoning chains, better swarm routing (stays parallel instead of falling back to single-agent), improved full-stack/frontend code quality, dedicated debugging sub-agent routing for cross-file bugs. See [models.md](references/models.md) for details.

---

## Reference Index

| File | Contents |
|---|---|
| [models.md](references/models.md) | All model IDs, context windows, pricing, capabilities, discontinuation dates |
| [api.md](references/api.md) | Chat completions endpoint, all parameters, response format, errors |
| [cli.md](references/cli.md) | Kimi CLI install, commands, MCP, ACP, zsh plugin, Agent SDK |
| [tools-and-agents.md](references/tools-and-agents.md) | Function calling, 12 official tools, web search, agentic loop pattern |
| [features.md](references/features.md) | Thinking mode, streaming, JSON mode, partial mode, vision, file QA |
| [integrations.md](references/integrations.md) | Migrate from OpenAI, Claude Code/Cline/RooCode, batch API, MCP, rate limits |

---

## Gotchas

- **Platform mismatch:** `platform.kimi.com` (mainland China) and `platform.kimi.ai` (international) have **completely independent** accounts and API keys — using one platform's key on the other triggers auth errors.
- **Wrong base_url:** Most `model_not_found` errors are caused by forgetting to set `base_url` in the OpenAI SDK, which routes to OpenAI's servers instead.
- **SDK retry amplification:** OpenAI SDK retries failed requests twice by default — a single rate-limited call becomes 3 requests against your quota.
- **Thinking mode temperature:** kimi-k2.6 thinking requires `temperature=1.0`; non-thinking requires `temperature=0.6`. Mismatching causes degraded output.
- **web_search + thinking:** `$web_search` builtin requires thinking to be **disabled** on kimi-k2.6.
- **Don't mix partial mode + json_object:** Using both produces unexpected responses.
- **File QA:** Pass extracted file **content** as a system message — not the `file_id`.
- **Connection timeouts:** High-token non-streaming requests can hit gateway timeouts. Enable `stream=True` as a workaround.
- **Avoid base64 for images if possible:** Dramatically increases token consumption vs file upload.
- **`tool_choice="required"` not supported** — use prompt engineering to encourage tool invocation.
- **`functions` parameter deprecated** — use `tools` only.
