# Integrations

---

## Azure OpenAI (Microsoft AI Foundry)

Azure provides OpenAI models wrapped with enterprise compliance infrastructure.

### Key Enterprise Features

- **Regional data residency** — deploy models in specific Azure regions (US, EU, etc.)
- **Private networking** — VNETs, private endpoints, no public internet required
- **Authentication** — Microsoft Entra ID (Azure AD) instead of raw API keys
- **Compliance** — SOC 2, HIPAA, GDPR-ready configurations
- **Rate limits** — higher PTU-based limits for production workloads

### Deployment Types

| Type | Description | Best For |
|------|-------------|---------|
| **Standard** (Pay-as-you-go) | Pay per token, shared capacity | Variable workloads, experimentation |
| **Provisioned** (PTUs) | Reserve model processing capacity, predictable billing | Consistent/high-volume production |
| **Batch** | Async bulk processing, 24h turnaround, 50% cost | Large offline jobs |

### Available Models (April 2026)

- GPT-4.1 series (1M context) — current flagship
- GPT-4o series (128K context)
- GPT-image-1 — image generation and editing
- GPT-4o Audio / Realtime — low-latency voice for call centers
- Reasoning models (o3, o4-mini, etc.)

### SDK Usage

API-compatible with OpenAI SDK — just change the base URL and auth:

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_key="your-azure-api-key",
    api_version="2024-12-01-preview"
)

response = client.chat.completions.create(
    model="gpt-4.1",  # your deployment name
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Azure AI Foundry

The broader platform wrapping Azure OpenAI. Includes:
- Model catalog (OpenAI + third-party models)
- AI Foundry Agent Service (replaces old Assistants API on Azure)
- Fine-tuning UI and API
- Prompt flow (orchestration)
- Content safety filters
- MCP server hosting

---

## GitHub Copilot

AI coding assistant. Powered by OpenAI models via Azure routing.

### Surfaces

- **VS Code** — inline completion, chat sidebar, inline chat
- **JetBrains IDEs** — same features
- **GitHub web** — PR summaries, code explanation, review
- **GitHub CLI** — `gh copilot suggest`, `gh copilot explain`
- **Terminal** — integrated command suggestions

### Agent Mode (IDE)

Autonomous task execution within the IDE:
- Can read files, write code, run tests, iterate
- Multi-step task completion without step-by-step prompting
- MCP tool integration for external services

### GitHub Copilot SDK (Released 2026)

Embed Copilot's engine into custom applications:

```python
from copilot_sdk import CopilotAgent

agent = CopilotAgent(model="gpt-4.1")
result = agent.run("Refactor this function for readability", context=code_context)
```

**Capabilities:**
- Function calling
- Streaming responses
- Multi-turn conversations
- Shell command execution
- File operations
- URL fetching
- MCP server integration (local stdio + remote HTTP)
- Available in .NET and Python

**BYOK (Bring Your Own Key)** — since April 7, 2026: replace GitHub-hosted model routing with your own provider (OpenAI, Azure AI Foundry, Anthropic).

---

## Operator / Agent Mode

Originally launched as "Operator" (January 2025, Pro-only, US). Absorbed into ChatGPT as "Agent Mode" by July 2025.

**Now:** Available to Pro, Plus, and Team users via the tools dropdown in the ChatGPT composer.

**Underlying technology:** CUA (Computer-Using Agent) model. Combines GPT-4o vision with reinforcement learning. Interacts with browser GUIs via screenshots and mouse/keyboard simulation.

**Developer access:** `computer_use_preview` built-in tool in the Responses API. See `built-in-tools.md` for implementation details.

---

## MCP (Model Context Protocol) Ecosystem

OpenAI has invested heavily in MCP as a standard. It appears across multiple surfaces:

### Responses API

```json
{
  "type": "mcp",
  "server_url": "https://mcp.example.com/sse",
  "server_label": "mytools",
  "require_approval": "auto"
}
```
Connects to remote MCP servers over Streamable HTTP or HTTP/SSE. See `built-in-tools.md`.

### Agents SDK

```python
# Hosted remote MCP (server-side)
from agents.tools import HostedMCPTool
tool = HostedMCPTool(server_url="https://mcp.example.com", server_label="mytools")

# Local MCP server (runs in your environment)
from agents import MCPServerStdio, MCPServerHTTP

async with MCPServerStdio(
    command="npx",
    args=["-y", "@myorg/mcp-server"]
) as server:
    agent = Agent(name="Agent", mcp_servers=[server])
    result = await Runner.run(agent, "Use the tools")
```

### Codex CLI

```toml
# ~/.codex/config.toml
[[mcp_servers]]
name = "my-tools"
command = "npx"
args = ["-y", "@myorg/mcp-server"]

[[mcp_servers]]
name = "remote"
url = "https://mcp.example.com/sse"
```
Servers auto-launch at session start.

### GitHub Copilot SDK

```python
# Connect to local or remote MCP servers in Copilot agent workflows
agent = CopilotAgent(mcp_servers=["stdio://npx -y @myorg/server"])
```

### Summary: MCP across OpenAI

| Surface | MCP Support | Transport |
|---------|-------------|-----------|
| Responses API | Remote servers | Streamable HTTP, HTTP/SSE |
| Agents SDK (hosted) | Remote servers | Streamable HTTP, HTTP/SSE |
| Agents SDK (local) | Local + remote | stdio, HTTP |
| Codex CLI | Local + remote | stdio, HTTP/SSE |
| GitHub Copilot SDK | Local + remote | stdio, HTTP |
