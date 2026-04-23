---
name: zhipuai-glm-coding
description: Expert knowledge for maximizing a Z.ai GLM Coding Plan subscription (Lite/Pro/Max) and the broader Z.ai platform. Covers Claude Code/Cline/Roo Code/Kilo Code/Cursor/n8n/TRAE/Eigent setup, model selection (GLM-5.1, GLM-5-Turbo, GLM-4.7, GLM-4.5-Air), quota management, MCP server configuration (Web Search, Web Reader, Vision, Zread), structured output, context caching, thinking modes, CLI/agent invocation, PAYG APIs (vision/image/audio/video/agents), and workflow best practices. Use when configuring the Coding Plan, troubleshooting quota or setup issues, choosing models, calling Z.ai APIs directly, or building agentic coding pipelines.
---

# Z.ai GLM Coding Plan Expert

Z.ai (ZhipuAI) provides AI-powered coding subscriptions built on the GLM model family. The platform is OpenAI-compatible AND Anthropic-compatible, so it works as a drop-in backend for Claude Code, Cline, Roo Code, Kilo Code, OpenCode, and others.

## Quick Setup: Claude Code

**3-step setup:**

```bash
# 1. Install Claude Code (if needed)
npm install -g @anthropic-ai/claude-code

# 2. Get API key from https://z.ai/manage-apikey

# 3a. Automated (macOS/Linux)
curl -O "https://cdn.bigmodel.cn/install/claude_code_zai_env.sh" && bash ./claude_code_zai_env.sh

# 3b. Or run the interactive helper
npx @z_ai/coding-helper
```

**Manual config** — add to `~/.claude/settings.json`:
```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "<your-z.ai-api-key>",
    "ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic",
    "API_TIMEOUT_MS": "3000000"
  }
}
```

Verify: run `claude`, then type `/status` — confirms active model.

## Model Tiers

| Model | Speed | Quota Cost | Best For |
|-------|-------|-----------|----------|
| **GLM-5.1** | Medium | 2–3× | Complex reasoning, SWE-Bench tasks, long-horizon agents |
| **GLM-5-Turbo** | Fast | 2–3× | Same capability as 5.1, optimized for speed |
| **GLM-4.7** | Fast | 1× | Daily coding: debug, refactor, implement features |
| **GLM-4.5-Air** | Fastest | 1× (Haiku slot) | Simple edits, quick lookups, low-stakes completions |

**Default Claude Code mappings:**
- Opus → `GLM-4.7`
- Sonnet → `GLM-4.7`
- Haiku → `GLM-4.5-Air`

To use GLM-5.1 as your primary model, override in `settings.json`:
```json
{
  "env": {
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "GLM-5.1",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "GLM-4.7",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "GLM-4.5-Air"
  }
}
```

## Max Plan Quota Summary

| Window | Prompts |
|--------|---------|
| Per 5 hours | ~1,600 |
| Per week | ~8,000 |
| Web searches/month | 4,000 |

**Each "prompt" triggers 15–20 model invocations** — plan accordingly for agentic loops.

## Quota Multipliers (Peak vs. Off-Peak)

GLM-5.1 and GLM-5-Turbo:
- **Peak (14:00–18:00 UTC+8):** 3× quota
- **Off-peak:** 2× (1× promotional through April 2026)

GLM-4.7 and GLM-4.5-Air: always 1×

**Implication:** For Max plan, running GLM-5.1 at peak burns through your 1,600 prompt budget ~3× faster. Schedule heavy agent runs off-peak.

## CLI & API Quick Reference

**Direct curl (OpenAI endpoint):**
```bash
curl -s https://api.z.ai/v1/chat/completions \
  -H "Authorization: Bearer $ZAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"GLM-4.7","messages":[{"role":"user","content":"..."}],"temperature":1.0}'
```

**Non-interactive Claude Code (one-shot task):**
```bash
ANTHROPIC_AUTH_TOKEN=$ZAI_API_KEY \
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic \
API_TIMEOUT_MS=3000000 \
claude -p "your task here"
```

**Community wrappers** (`z`/`glm` commands):
```bash
z "implement the feature"          # interactive
z -p "fix failing tests"           # non-interactive / scriptable
glm --model opus "hard task"       # force opus slot (GLM-4.7 or GLM-5.1)
```
Install: `bash scripts/install.sh` from `geoh/z.ai-powered-claude-code`

**Sub-agent model** (per-project `.zai.json`):
```json
{"subagentModel": "GLM-4.7", "opusModel": "GLM-5.1", "haikuModel": "GLM-4.5-Air"}
```

> The API enforces 1 concurrent request — serialize agent calls, don't fan out in parallel.

## MCP Tools Included

All plans include:
- **Web Search MCP** — live search within coding sessions
- **Web Reader MCP** — fetch and read URLs/docs inline
- **Zread MCP** — read GitHub repos and technical content
- **Vision Understanding** — analyze screenshots, diagrams, UI mockups

Max plan: 4,000 searches/month. Vision shares the 5-hour prompt pool.

## API Endpoints

| Format | Base URL |
|--------|----------|
| Anthropic-compatible | `https://api.z.ai/api/anthropic` |
| OpenAI-compatible | `https://api.z.ai/v1` |

## Platform APIs (PAYG — beyond the Coding Plan)

Same API key, separate billing. Key additions:
- **GLM-4.7-Flash / GLM-4.5-Flash** — FREE text models (PAYG, rate-limited)
- **GLM-4.6V** — multimodal vision (image/video/doc); `glm-4.6v-flash` is free
- **GLM-OCR** — PDF/document → Markdown/JSON/LaTeX at $0.03/M tokens
- **CogView-4** — text-to-image at $0.01/image
- **GLM-ASR-2512** — speech-to-text at $0.0024/min
- **Agent Services** — Translation ($3/M), Slide/Poster beta ($0.7/M)

## Reference Files

| File | Load when… |
|------|-----------|
| `references/setup.md` | Setting up any tool; MCP server configs; Cursor/n8n/TRAE/Eigent/Droid |
| `references/models.md` | Choosing a model; PAYG pricing; free model options |
| `references/quota-management.md` | Quota strategy; peak/off-peak multipliers; Max plan optimization |
| `references/capabilities.md` | Structured output; context caching; thinking modes; streaming |
| `references/mcp-tools.md` | MCP tool usage patterns and quotas |
| `references/workflows.md` | Agentic session design; long-horizon tasks; hybrid Claude+GLM |
| `references/cli-and-agents.md` | curl/Python API; non-interactive Claude Code; tool calling; multi-agent |
| `references/best-practices.md` | Task structuring; memory architecture; session management; rule writing |
| `references/platform-apis.md` | Vision/VLM; image gen; audio; video; Agent Services; PAYG vs plan |
