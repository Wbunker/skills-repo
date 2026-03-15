# Deployment & Infrastructure

VPS setup, Docker, networking, and production stack configuration.

## Table of Contents

- [Installation](#installation)
- [Model Selection](#model-selection)
- [CLI Configuration Commands](#cli-configuration-commands)
- [VPS Deployment](#vps-deployment)
- [Docker Deployment](#docker-deployment)
- [Networking & Access](#networking--access)
- [Production Stack](#production-stack)
- [Cost Reference](#cost-reference)

---

## Installation

### Via Ollama (easiest — recommended)

Requires Ollama 0.17+, Node.js, Mac/Linux (Windows via WSL).

```bash
# One command — installs OpenClaw, configures, and launches
ollama launch openclaw --model kimi-k2.5:cloud

# Or without specifying a model (shows recommended models to choose from)
ollama launch openclaw
```

Ollama detects if OpenClaw is missing and prompts for installation automatically. The whole process takes ~2 minutes.

### Via install script (manual)

```bash
# Standard install
curl -fsSL https://openclaw.ai/install.sh | bash

# First-time setup (interactive)
openclaw onboard

# Verify
openclaw --version
```

### Windows support

```bash
# Install WSL first
wsl --install    # One reboot required

# Then run Ollama or install script inside WSL
```

### Post-install structure

```
~/.openclaw/
├── openclaw.json          # Main config
├── soul/                  # SOUL.md and identity files
├── memory/                # Memory files
├── cron/                  # Cron job definitions
└── agents/                # Sub-agent configurations
```

## VPS Deployment

### Minimum specs

| Tier | RAM | CPU | Storage | Cost | Suitable for |
|------|-----|-----|---------|------|-------------|
| Minimal | 2 GB | 1 vCPU | 20 GB | ~$5/mo | Single agent, light tasks |
| Standard | 4 GB | 2 vCPU | 40 GB | ~$10-15/mo | 1-3 agents, cron jobs, memory |
| Multi-agent | 8 GB+ | 4 vCPU | 80 GB | ~$20-30/mo | 6+ agents, browser, voice |

Providers: Contabo, Hetzner, DigitalOcean, Linode.

### Initial VPS setup

```bash
# Update and secure
apt update && apt upgrade -y
adduser openclaw
usermod -aG sudo openclaw

# SSH hardening
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd

# Firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw enable
```

### Systemd service

```ini
# /etc/systemd/system/openclaw.service
[Unit]
Description=OpenClaw AI Agent
After=network.target

[Service]
Type=simple
User=openclaw
ExecStart=/usr/local/bin/openclaw serve
Restart=always
RestartSec=5
Environment=OPENCLAW_HOME=/home/openclaw/.openclaw

[Install]
WantedBy=multi-user.target
```

```bash
systemctl enable openclaw
systemctl start openclaw
```

### Model selection

Agents work best with at least **64k context length**.

| Type | Model | Description |
|------|-------|-------------|
| Cloud | kimi-k2.5:cloud | Multimodal reasoning with subagents |
| Cloud | minimax-m2.5:cloud | Fast coding and real-world productivity |
| Cloud | qbm-5:cloud | Reasoning and code generation |
| Local (~25GB VRAM) | qbm-4.7-flash | Reasoning and code generation |
| Local (~25GB VRAM) | qwen3-coder | Efficient all-purpose assistant |

Cloud models from Ollama have full context length and auto-install the web search plugin.

### CLI configuration commands

```bash
# Interactive channel setup
openclaw configure --section channels

# Web search setup (Brave API key)
openclaw configure --section web

# Set config values directly
openclaw config set telegram.botToken YOUR_BOT_TOKEN
openclaw config set telegram.allowedChatIds YOUR_CHAT_ID
openclaw config set whatsapp.enabled true
openclaw config set discord.botToken YOUR_BOT_TOKEN
openclaw config set discord.guildId YOUR_GUILD_ID

# Edit config file
openclaw config edit

# Useful commands
/help                              # See all commands
openclaw skills                    # Browse and install skills
openclaw gateway stop              # Stop the background gateway
```

## Docker Deployment

### Basic Docker Compose

```yaml
services:
  openclaw:
    image: ghcr.io/hostinger/hvps-openclaw:latest
    container_name: openclaw
    init: true
    restart: unless-stopped
    ports:
      - "127.0.0.1:18789:18789"    # Gateway (loopback only)
      - "127.0.0.1:18791:18791"    # Browser control
    volumes:
      - ./data:/data                         # Persistent workspace, config, memory
      - /dev/shm:/dev/shm                    # Required for Chromium
    shm_size: '2gb'                          # Chromium needs this
    env_file:
      - .env                                 # API keys, gateway token
    cap_add:
      - SYS_ADMIN                            # Required for Chromium sandboxing
    security_opt:
      - seccomp:unconfined                   # Chromium uses syscalls Docker blocks
```

### Browser requirements in Docker

Chromium inside Docker requires extra configuration or it will crash silently:

| Requirement | Why |
|-------------|-----|
| `/dev/shm:/dev/shm` + `shm_size: '2gb'` | Chrome tabs crash without shared memory |
| `cap_add: SYS_ADMIN` | Chrome refuses to start without sandbox capability |
| `seccomp:unconfined` | Chrome needs syscalls (clone, unshare) Docker blocks |
| Clean `SingletonLock` on startup | Stale locks from unclean shutdown block browser launch |

```bash
# Add to Docker entrypoint to clean stale Chrome locks
find /data/.openclaw/browser -name SingletonLock -delete 2>/dev/null
```

### Hardened Docker configuration

```yaml
services:
  openclaw:
    image: openclaw/openclaw:latest
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
    networks:
      - openclaw-internal
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

networks:
  openclaw-internal:
    driver: bridge
    internal: true    # No direct internet — use proxy if needed
```

## Networking & Access

### Bind to loopback (critical)

```json
// openclaw.json
{
  "gateway": {
    "http": {
      "host": "127.0.0.1",
      "port": 18789
    }
  }
}
```

**Never bind to 0.0.0.0 in production** — over 135K exposed instances have been found on the open internet.

### Secure remote access options

| Method | Complexity | Best for |
|--------|-----------|----------|
| SSH tunnel | Low | Single user, temporary access |
| Tailscale | Low | Personal/small team, always-on |
| Cloudflare Tunnel | Medium | Public-facing with auth |
| Nginx reverse proxy + auth | Medium | Custom domains, multi-service |

**SSH tunnel**:
```bash
ssh -L 18789:127.0.0.1:18789 user@your-vps
```

**Tailscale**:
```bash
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up
# Access via Tailscale IP — no port exposure needed
```

**Cloudflare Tunnel**:
```bash
cloudflared tunnel create openclaw
cloudflared tunnel route dns openclaw claw.yourdomain.com
# Configure access policies in Cloudflare Zero Trust dashboard
```

### Gateway authentication

```json
// openclaw.json
{
  "gateway": {
    "http": {
      "auth": {
        "token": "your-secret-token-here"
      }
    }
  }
}
```

## Production Stack

### Recommended production config (openclaw.json)

```json
{
  "gateway": {
    "http": {
      "host": "127.0.0.1",
      "port": 18789,
      "auth": { "token": "${OPENCLAW_AUTH_TOKEN}" },
      "endpoints": {
        "chatCompletions": { "enabled": true }
      }
    }
  },
  "memory": {
    "enabled": true,
    "provider": "local",
    "path": "~/.openclaw/memory"
  },
  "cron": {
    "enabled": true
  },
  "browser": {
    "enabled": true,
    "port": 18791
  }
}
```

### Monitoring with dashboard

```bash
# Status check
openclaw status

# Logs
journalctl -u openclaw -f

# Resource monitoring
htop  # or: docker stats openclaw
```

### Backup strategy

```bash
# Backup OpenClaw state
tar czf openclaw-backup-$(date +%Y%m%d).tar.gz ~/.openclaw/

# Automate with cron
0 3 * * * tar czf /backups/openclaw-$(date +\%Y\%m\%d).tar.gz ~/.openclaw/
```

## Cost Reference

### Single-agent stack

| Component | Monthly Cost |
|-----------|-------------|
| VPS (Contabo 4GB) | $5-10 |
| Claude API (Sonnet) | $10-30 |
| Domain (optional) | ~$1 |
| **Total** | **$16-41** |

### Multi-agent production stack

| Component | Monthly Cost |
|-----------|-------------|
| VPS (8GB) | $15-25 |
| Claude Max subscription | $200 |
| Gemini API (secondary) | $50-70 |
| ElevenLabs (voice) | $50 |
| Misc APIs | $20-50 |
| **Total** | **$335-395** |

### Cost optimization

- Use Sonnet for infrastructure/routine tasks, Opus only for complex reasoning
- Batch cron jobs to reduce API calls
- Use `availableNow` trigger patterns to avoid idle compute
- Monitor daily API costs via OpenClaw's built-in tracking
