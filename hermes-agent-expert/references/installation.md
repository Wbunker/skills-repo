# Hermes Agent Installation & Setup

## Quick Install

Only Git is required. The installer handles everything else automatically.

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
source ~/.bashrc   # or source ~/.zshrc
hermes
```

**What the installer provides:**
- uv (Rust-based Python package manager)
- Python 3.11 (via uv, no sudo needed)
- Node.js v22 (browser automation, WhatsApp bridge)
- ripgrep (file search)
- ffmpeg (audio conversion)

## Platform Support

| Platform | Support |
|---|---|
| Linux | Full |
| macOS | Full |
| WSL2 | Full |
| Android / Termux | Full (auto-detected) |
| NixOS | Dedicated flake-based path |
| Native Windows | Not supported — use WSL2 |

## Initial Configuration

```bash
hermes setup        # Full interactive wizard (model + config)
hermes model        # Select/change LLM provider only
hermes tools        # Enable or disable tools
```

**Critical requirement:** The model must have at least **64K context tokens**. Smaller windows cannot maintain multi-step tool-calling workflows.

## Model Providers

| Provider | Notes |
|---|---|
| Nous Portal | Least friction; includes Tool Gateway (web search, image gen, TTS, browser) |
| OpenRouter | 400+ models via single API key; recommended for flexibility |
| Anthropic | Direct Claude API |
| OpenAI | Direct GPT API |
| DeepSeek | Cost-optimized |
| Kimi / Moonshot | Good coding performance; see kimi-code-expert skill |
| NVIDIA NIM | Nemotron for enterprise |
| Xiaomi MiMo | Compact reasoning models |
| Hugging Face | Open-weights via inference API |
| Ollama | Local inference (see below) |
| Custom endpoint | Any OpenAI-compatible base_url |

Switch providers at any time: `hermes model` — no code changes, no lock-in.

## Ollama Local Inference

Zero API cost, full data privacy. Point Hermes at your local Ollama server:

```bash
ollama pull qwen2.5-coder:32b        # Primary orchestrator
```

In `~/.hermes/config.yaml`:
```yaml
model:
  provider: "custom"
  base_url: "http://localhost:11434/v1"
  model: "qwen2.5-coder:32b"
```

**Hardware note:** For deep research with parallel sub-agents, a 32B model as orchestrator + smaller quantized models for sub-agent routing is more practical on consumer hardware than running 32B for every thread simultaneously.

## Running Hermes

```bash
hermes              # Classic CLI
hermes --tui        # Modern TUI (recommended)
hermes -c           # Resume most recent session (--continue)
hermes --yolo       # Skip all command approval prompts (use carefully)
```

**Useful slash commands inside Hermes:**
- `/help` — command list
- `/tools` — enable/disable tools
- `/model` — switch model mid-session
- `/skills` — browse installed skills
- `/compress` — manually reduce context
- `/voice on` — enable voice mode (requires extras)
- `/new` or `/reset` — start fresh conversation
- `/reasoning high` — boost reasoning effort

## VPS / Server Deployment

Recommended: $5–10/month VPS (Hetzner, Contabo) + Docker backend + systemd service.

```bash
# Set Docker as terminal backend
hermes config set terminal.backend docker

# Start gateway as background service
hermes gateway start
```

Create a systemd unit at `/etc/systemd/system/hermes-agent.service`:
```ini
[Unit]
Description=Hermes Agent Gateway
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser
ExecStart=/home/youruser/.local/bin/hermes gateway start
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable hermes-agent
sudo systemctl start hermes-agent
```

## Diagnostics

```bash
hermes doctor            # Full health check
hermes config check      # Find missing config options after updates
hermes config migrate    # Add missing options interactively
hermes sessions list     # List all past sessions
```
