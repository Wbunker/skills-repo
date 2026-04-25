# Hermes Agent Integrations

## Messaging Gateways

Hermes connects to 16+ platforms from a single gateway process. Start with:

```bash
hermes gateway setup     # Interactive wizard
hermes gateway start     # Start as background service
hermes gateway status    # Check status
```

### Supported Platforms

| Platform | Notes |
|---|---|
| Telegram | Simplest setup: BotFather + @userinfobot for User ID |
| Discord | `require_mention`, `auto_thread`, `free_response_channels` options |
| Slack | Workspace bot integration |
| WhatsApp | Node.js v22 required |
| Signal | Node.js v22 required |
| SMS | Twilio or similar |
| Email | SMTP/IMAP |
| Home Assistant | Smart home integration |
| Mattermost | Self-hosted team messaging |
| Matrix | Federated protocol |
| DingTalk | Chinese enterprise |
| Feishu / Lark | Chinese enterprise |
| WeCom / Weixin | WeChat Work + consumer WeChat |
| BlueBubbles | iMessage on non-Apple servers |
| Webhook | Generic HTTP webhook adapter |
| QQBot | Added in v0.11.0 |

**Caveat:** Messaging interfaces work well for monitoring and async updates but are inherently linear. For deep collaborative work (complex codebase changes, long iterative sessions), use the CLI or TUI.

### Telegram Setup

```bash
# 1. Create bot via BotFather on Telegram → get bot token
# 2. Get your User ID via @userinfobot
# 3. Configure
hermes config set TELEGRAM_BOT_TOKEN "your-token"
hermes config set TELEGRAM_USER_ID "your-id"
hermes gateway start
```

### Discord Config (config.yaml)

```yaml
discord:
  require_mention: true                  # Require @mention in channels
  free_response_channels: "123,456"      # Channel IDs (no mention needed)
  auto_thread: true                      # Auto-create threads on mention
```

---

## Cron Automation

Built-in scheduler — write jobs in natural language, delivered to any configured platform.

```bash
# The agent sets up cron jobs via its tools — just describe what you want:
# "Every morning at 9am, check Hacker News for AI news and send a summary to Telegram"
```

Jobs live in `~/.hermes/cron/`. Delivered results go to whichever gateway platform is configured.

**Common automation patterns:**
- Daily reports (news, metrics, summaries)
- Nightly backups
- Weekly audits
- PR review digests
- API data polling

---

## MCP Servers

MCP (Model Context Protocol) servers extend Hermes's tool surface.

Configure in `~/.hermes/config.yaml`:
```yaml
mcp:
  servers:
    - name: "my-mcp-server"
      command: "npx"
      args: ["-y", "@my-org/mcp-server"]
      env:
        MY_API_KEY: "${MY_API_KEY}"
```

Only safe env vars pass to MCP subprocesses by default (`PATH`, `HOME`, `USER`, `LANG`, `SHELL`, `TMPDIR`, `XDG_*`). Explicitly configured vars in `env:` are exceptions.

---

## Nous Portal Tool Gateway

Available to Nous Portal subscribers — no additional API keys required for:
- Web search
- Image generation
- Text-to-speech
- Browser automation

Activate via `hermes model` → select Nous Portal.

---

## Ollama Integration

Use any Ollama model as the Hermes backend:

```bash
ollama pull qwen2.5-coder:32b
```

```yaml
model:
  provider: "custom"
  base_url: "http://localhost:11434/v1"
  model: "qwen2.5-coder:32b"
```

For sub-agents with delegation, use a smaller model:
```yaml
delegation:
  model: "qwen2.5-coder:7b"
  provider: "custom"
```

---

## OpenClaw Migration

Hermes auto-detects an existing OpenClaw install and offers migration:

```bash
hermes claw migrate
```

Imports automatically:
- Persona file (becomes SOUL.md)
- Memories
- Skills
- Command allowlist
- Messaging platform settings
- API keys

After migration, verify with `hermes doctor` and test a session.

---

## Atropos RL Integration

For teams training or fine-tuning models with agent trajectory data:

Hermes supports trajectory export and RL training integration with Nous Research's Atropos framework. Enables:
- Batch processing of agent runs
- Training data export from successful sessions
- Reinforcement learning from agent-generated experience

---

## Git Worktree Isolation

For parallel agent execution without branch conflicts:

```yaml
worktree: true    # Each session gets isolated branch in .worktrees/
```

Enables multiple agents to work on the same repo simultaneously without interfering with each other or the main working tree.
