# OpenAI Codex CLI

Agentic coding tool that runs in the terminal. Distinct from the legacy "Codex model" — this is a CLI agent product. Open source (built in Rust).

## Install

```bash
# npm (recommended)
npm i -g @openai/codex

# Homebrew
brew install --cask codex

# Binary: download from GitHub Releases for your platform
```

Platform support: macOS, Linux. Windows: experimental.

## First Run

```bash
codex
```

Launches full-screen terminal UI. Prompts for ChatGPT account sign-in or OpenAI API key on first run.

**Availability:** ChatGPT Plus, Pro, Business, Edu, Enterprise subscribers.

---

## Approval Modes

Control how much autonomy Codex has:

| Mode | Behavior |
|------|----------|
| **Auto** (default) | Read files, edit, and run commands within the working directory — no confirmation |
| **Read-only** | Browse and read files; shows plan but requires approval before making changes |
| **Full Access** | Work across entire machine with network access, no confirmation required |

Choose the mode that matches your comfort level before starting a session.

---

## Key Capabilities

**Core:**
- Read, edit, and run code in the selected directory from the terminal
- Plans actions and explains them before executing
- Full-screen terminal UI with conversational interface

**Image / multimodal:**
- Attach screenshots or design specs for context
- Paste images directly into the interactive composer
- Provide image files on the command line

**Code review mode:**
- Get your code reviewed by a separate Codex agent before commit/push

**Web search:**
- Access live web information during tasks

**Automation:**
- `codex exec "..."` — non-interactive, scriptable command execution

**Session management:**
- `codex resume` — resume from stored transcripts
- `codex resume --last` — jump to most recent session
- Transcripts stored locally

**Remote TUI mode:**
- Run Codex app server on one machine
- Connect via terminal UI from another machine
- WebSocket authentication: capability tokens or signed bearer tokens

**Model selection:**
- `/model` command to switch models (GPT-5.4, GPT-5.3-Codex, etc.)
- Adjustable reasoning levels to match task complexity

---

## Multi-Agent / Subagents

Codex can parallelize larger tasks:
- Spawns subagents in isolated Git worktrees to avoid conflicts
- Each subagent works independently on its own branch/worktree
- Only spawned when explicitly requested
- Each subagent consumes additional tokens

---

## MCP (Model Context Protocol) Support

Configure MCP servers in `~/.codex/config.toml`:
```toml
[[mcp_servers]]
name = "my-tools"
command = "npx"
args = ["-y", "@myorg/mcp-server"]

[[mcp_servers]]
name = "remote-tools"
url = "https://mcp.example.com/sse"
```

Servers launch automatically when sessions start, exposing their tools alongside built-in Codex capabilities.

---

## Agent Skills

Package instructions, resources, and optional scripts to extend Codex with domain-specific, task-specific workflows. Skills let Codex follow a reliable workflow for recurring task types.

---

## vs. Claude Code

| Feature | Codex CLI | Claude Code |
|---------|-----------|-------------|
| Language | Rust binary | Node.js |
| Session resume | `codex resume` — persistent transcripts | No built-in session resume |
| Remote TUI | Server + remote client via WebSocket | Local only |
| Multi-agent | Subagents in Git worktrees | Native subagents |
| MCP config | `~/.codex/config.toml` | `~/.claude/settings.json` |
| Approval modes | Auto / Read-only / Full Access | Explicit per-action approval |
| Skills/extensions | Agent Skills (packaged workflows) | Skills (SKILL.md files) |
| Image input | Yes (paste or CLI flag) | Yes |
| Code review | Built-in separate agent review | Manual |
| Model | OpenAI models only | Anthropic Claude models only |
| Auth | ChatGPT account or API key | Anthropic API key |
| Open source | Yes | Yes |
