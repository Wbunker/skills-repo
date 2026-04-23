# Kimi CLI and Agent SDK

## Kimi CLI

Terminal-based agentic coding tool, comparable to Claude Code. Requires Python 3.13+.

### Installation

```sh
# Recommended (via uv)
uv tool install --python 3.13 kimi-cli

# Upgrade
uv tool upgrade kimi-cli --no-cache
```

**Platforms:** macOS and Linux. Windows support forthcoming.  
**Note:** First launch may take 10+ seconds on macOS due to security checks.

### Basic Usage

```sh
kimi           # Launch in current directory
/setup         # Initialize session
/help          # Show available commands
```

### Core Features

**Shell Mode:** Toggle between agent and shell interfaces with `Ctrl-X` to run commands without exiting.

**Zsh Integration:**
```sh
git clone https://github.com/MoonshotAI/zsh-kimi-cli.git \
  ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/kimi-cli
# Add kimi-cli to plugins list in ~/.zshrc
```

**MCP Tools:** Supports standard MCP config convention:
```sh
kimi --mcp-config-file path/to/mcp.json
```

**ACP (Agent Client Protocol):** Native ACP support for integration with compatible editors like Zed.

### Repository
`https://github.com/MoonshotAI/kimi-cli`

---

## Kimi Agent SDK

Python, Node.js, and Go SDK for building production agents.  
Repository: `https://github.com/MoonshotAI/kimi-agent-sdk`

---

## MoonPalace Debugging Tool

Web-based request inspector for debugging Kimi API calls.  
Documentation: `platform.kimi.ai/docs/guide/use-moonpalace.md`

Use the Playground at `platform.kimi.ai` for interactive testing and prompt debugging before coding.

---

## ModelScope MCP Server

Kimi can be configured as an MCP server within ModelScope.  
Documentation: `platform.kimi.ai/docs/guide/configure-the-modelscope-mcp-server.md`

---

## K2 Vendor Verifier

Open-source tool for evaluating tool call quality across different inference vendors.  
Repository: `https://github.com/MoonshotAI/K2-Vendor-Verifier`

Useful for benchmarking Kimi API providers (Baseten, Fireworks, Ollama, etc.) before choosing an inference backend.
