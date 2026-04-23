---
name: zhipuai-glm-coding-setup
description: Complete setup instructions for Z.ai GLM Coding Plan across all supported tools — Claude Code, Cline, Roo Code, Kilo Code, OpenCode, Cursor, Gemini CLI, Grok CLI, n8n, TRAE, Eigent, Factory Droid, and OpenAI-compatible integrations. Also covers manual MCP server configuration (Web Search, Web Reader, Vision, Zread) for tools that don't auto-provision them. Includes Windows/macOS/Linux variants, API key management, and troubleshooting.
type: reference
---

# Z.ai GLM Coding Plan — Setup Reference

## Prerequisites

- Node.js 18 or newer (macOS: use nvm to avoid permission issues)
- Windows: Git for Windows recommended
- A Z.ai API key from https://z.ai/manage-apikey

## Claude Code

### Automated (Recommended)

```bash
# Interactive helper — walks you through setup for any supported tool
npx @z_ai/coding-helper
```

Or use the bash script (macOS/Linux only):
```bash
curl -O "https://cdn.bigmodel.cn/install/claude_code_zai_env.sh" && bash ./claude_code_zai_env.sh
```

### Manual Configuration

Edit `~/.claude/settings.json`:
```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "<your-z.ai-api-key>",
    "ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic",
    "API_TIMEOUT_MS": "3000000"
  }
}
```

### Windows (Command Prompt)
```cmd
setx ANTHROPIC_AUTH_TOKEN "your-api-key"
setx ANTHROPIC_BASE_URL "https://api.z.ai/api/anthropic"
setx API_TIMEOUT_MS "3000000"
```

### Windows (PowerShell)
```powershell
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_AUTH_TOKEN","your-api-key","User")
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL","https://api.z.ai/api/anthropic","User")
[System.Environment]::SetEnvironmentVariable("API_TIMEOUT_MS","3000000","User")
```

### Verify Setup

Run `claude` in your project directory, then:
```
/status
```
You should see the active model (e.g. GLM-4.7 or GLM-5.1).

### Custom Model Mapping

Override the default Opus/Sonnet/Haiku model mappings in `settings.json`:
```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "<key>",
    "ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic",
    "API_TIMEOUT_MS": "3000000",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "GLM-5.1",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "GLM-4.7",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "GLM-4.5-Air"
  }
}
```

> Note: Zhipu recommends against manual model mapping as it may prevent automatic updates to newer models.

---

## Cline (VS Code Extension)

1. Open Cline settings
2. Set **API Provider** to `OpenAI-compatible`
3. Set **Base URL** to `https://api.z.ai/v1`
4. Enter your Z.ai API key
5. Set **Model** to `GLM-5.1`, `GLM-4.7`, etc.

---

## Roo Code

1. Open Roo Code settings
2. Add Z.ai as a custom provider
3. Base URL: `https://api.z.ai/v1`
4. API Key: your Z.ai key
5. Model: `GLM-4.7` or `GLM-5.1`

---

## Kilo Code

1. Open Kilo Code settings
2. Add custom OpenAI-compatible endpoint
3. Base URL: `https://api.z.ai/v1`
4. API Key: your Z.ai key
5. Select model from list

---

## OpenCode

Configuration via `opencode.json` or environment:
```json
{
  "provider": {
    "zai": {
      "baseUrl": "https://api.z.ai/v1",
      "apiKey": "<your-key>",
      "models": ["GLM-5.1", "GLM-4.7", "GLM-4.5-Air"]
    }
  }
}
```

---

## OpenAI SDK / Generic Integration

```python
from openai import OpenAI

client = OpenAI(
    api_key="<your-z.ai-api-key>",
    base_url="https://api.z.ai/v1"
)

response = client.chat.completions.create(
    model="GLM-4.7",
    messages=[{"role": "user", "content": "Write a Python function to..."}]
)
```

---

## LiteLLM Integration

```python
import litellm

response = litellm.completion(
    model="zai/GLM-4.7",
    messages=[{"role": "user", "content": "..."}],
    api_key="<your-z.ai-api-key>"
)
```

Prefix all Z.ai models with `zai/` when using LiteLLM.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Auth errors | Wrong token field | Use `ANTHROPIC_AUTH_TOKEN`, not `ANTHROPIC_API_KEY` |
| Timeouts | Default timeout too low | Set `API_TIMEOUT_MS=3000000` |
| 429 errors | Quota exhausted | Wait for 5-hour reset or switch to lower-tier model |
| Concurrent request errors | 1 in-flight request limit | Queue requests sequentially |
| Model not found | Wrong model name | Use exact names: `GLM-5.1`, `GLM-4.7`, `GLM-4.5-Air` |
| `/status` shows wrong model | Cached config | Restart Claude Code after editing settings.json |

---

## API Key Management

- Generate and manage keys at https://z.ai/manage-apikey
- Rate limit info at https://z.ai/manage-apikey/rate-limits
- Keys are scoped to your plan quota — one key per account is typical

---

## Additional Tool Integrations

All tools below use Z.ai's OpenAI-compatible endpoint: `https://api.z.ai/v1`

### Cursor

1. Open Cursor → Settings → Models
2. Add a new model provider: **OpenAI-compatible**
3. Base URL: `https://api.z.ai/v1`
4. API Key: your Z.ai key
5. Model name: `GLM-4.7` or `GLM-5.1`

### Gemini CLI

Configure via environment or `~/.gemini/config.json`:
```bash
export GEMINI_API_KEY="your-z.ai-key"
export GEMINI_BASE_URL="https://api.z.ai/v1"
```
Or pass inline: `gemini --model GLM-4.7 --base-url https://api.z.ai/v1 "your prompt"`

### Grok CLI

```bash
export XAI_API_KEY="your-z.ai-key"
export XAI_BASE_URL="https://api.z.ai/v1"
grok --model GLM-4.7 "your prompt"
```

### n8n Workflow

1. Add an **HTTP Request** node or **OpenAI** node
2. Set Base URL to `https://api.z.ai/v1/chat/completions`
3. Authentication: Header Auth → `Authorization: Bearer your-key`
4. Body: standard OpenAI chat completions JSON with `"model": "GLM-4.7"`

Alternatively, use the **OpenAI** community node with custom base URL support.

### TRAE

1. Open TRAE settings → AI Provider
2. Select **Custom / OpenAI-compatible**
3. Base URL: `https://api.z.ai/v1`
4. API Key: your Z.ai key
5. Model: `GLM-4.7`

### Eigent

1. Open Eigent → Settings → LLM Provider
2. Select **OpenAI-compatible**
3. Base URL: `https://api.z.ai/v1`
4. API Key: your Z.ai key
5. Model: `GLM-5.1` (Eigent is designed for agentic workflows — GLM-5.1 recommended)

### Factory Droid

1. Open Droid configuration
2. Set provider to **OpenAI-compatible**
3. Base URL: `https://api.z.ai/v1`
4. API Key: your Z.ai key
5. Model: `GLM-4.7` or `GLM-5.1`

---

## MCP Server Manual Configuration

The Coding Plan bundles four MCP servers. They're auto-provisioned through the Coding Plan endpoint, but if you need to configure them explicitly (e.g., for tools that don't use the Anthropic-compatible endpoint, or for PAYG API access), use the configs below.

All configs go into `.claude.json` (global) or your tool's MCP settings. Replace `your_api_key` with your Z.ai key.

### Web Search MCP

```json
{
  "mcpServers": {
    "web-search-prime": {
      "type": "http",
      "url": "https://api.z.ai/api/mcp/web_search_prime/mcp",
      "headers": { "Authorization": "Bearer your_api_key" }
    }
  }
}
```

One-command install:
```bash
claude mcp add -s user -t http web-search-prime \
  https://api.z.ai/api/mcp/web_search_prime/mcp \
  --header "Authorization: Bearer your_api_key"
```

Provides the `webSearchPrime` tool. Quota: 100/1K/4K searches per month (Lite/Pro/Max).

### Web Reader MCP

```json
{
  "mcpServers": {
    "web-reader": {
      "type": "http",
      "url": "https://api.z.ai/api/mcp/web_reader/mcp",
      "headers": { "Authorization": "Bearer your_api_key" }
    }
  }
}
```

One-command install:
```bash
claude mcp add -s user -t http web-reader \
  https://api.z.ai/api/mcp/web_reader/mcp \
  --header "Authorization: Bearer your_api_key"
```

Provides the `webReader` tool — fetches page title, content, metadata, and links.

**Cline (older versions):** Use `type: "sse"` and append the key to the URL instead of using headers.

### Vision MCP

Requires Node.js 22+. Runs as a local `stdio` process via npx.

```json
{
  "mcpServers": {
    "zai-mcp-server": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@z_ai/mcp-server"],
      "env": {
        "Z_AI_API_KEY": "your_api_key",
        "Z_AI_MODE": "ZAI"
      }
    }
  }
}
```

One-command install:
```bash
claude mcp add -s user zai-mcp-server \
  --env Z_AI_API_KEY=your_api_key Z_AI_MODE=ZAI \
  -- npx -y "@z_ai/mcp-server"
```

**Usage:** Reference images by local path — type `describe this demo.png` rather than pasting image data. Use `@latest` if the npx cache has an old version.

### Zread MCP

```json
{
  "mcpServers": {
    "zread": {
      "type": "http",
      "url": "https://api.z.ai/api/mcp/zread/mcp",
      "headers": { "Authorization": "Bearer your_api_key" }
    }
  }
}
```

One-command install:
```bash
claude mcp add -s user -t http zread \
  https://api.z.ai/api/mcp/zread/mcp \
  --header "Authorization: Bearer your_api_key"
```

Provides documentation search, repository structure access, and code reading from GitHub repos.
