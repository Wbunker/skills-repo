# Hermes Agent Configuration

## Directory Structure

```
~/.hermes/
├── config.yaml          # All non-secret settings
├── .env                 # API keys and secrets
├── auth.json            # OAuth provider credentials
├── SOUL.md              # Agent identity (system prompt slot #1)
├── memories/            # MEMORY.md + USER.md
├── skills/              # Agent-managed and installed skills
├── cron/                # Scheduled jobs
├── sessions/            # Gateway session state
└── logs/                # Error and gateway logs (auto-redacted)
```

## Configuration Commands

```bash
hermes config                    # View current settings
hermes config edit               # Open config.yaml in editor
hermes config set KEY VAL        # Smart-route: secrets → .env, rest → config.yaml
hermes config check              # Find missing options after update
hermes config migrate            # Add missing options interactively
```

## Configuration Precedence (highest → lowest)

1. CLI arguments (per-invocation, e.g. `--model anthropic/claude-opus-4`)
2. `~/.hermes/config.yaml`
3. `~/.hermes/.env`
4. Built-in defaults

## Context File Hierarchy

Hermes loads context files in this priority order (all capped at 20,000 chars):

1. `~/.hermes/SOUL.md` — global agent identity (system prompt slot #1)
2. Project context — first match: `.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`
3. Recursive `AGENTS.md` — loaded from directory tree up to project root

SOUL.md is auto-seeded with defaults if missing. Edit it to change agent personality, rules, and constraints.

---

## config.yaml Key Sections

### Model & Provider

```yaml
model:
  provider: "openrouter"          # or anthropic, main, custom, etc.
  model: "anthropic/claude-opus-4"
  base_url: ""                    # Custom OpenAI-compatible endpoint
```

### Auxiliary Models

```yaml
auxiliary:
  vision:
    provider: "auto"             # auto, openrouter, nous, codex, main
    model: "openai/gpt-4o"
    timeout: 120
  compression:
    provider: "auto"
    model: "google/gemini-3-flash-preview"
    timeout: 120
  web_extract:
    provider: "auto"
    timeout: 360
```

### Terminal Backend

```yaml
terminal:
  backend: docker                # local, docker, ssh, modal, daytona, singularity
  persistent_shell: true         # Maintain state across commands (SSH default)
```

**Backend comparison:**

| Backend | Isolation | Best For |
|---|---|---|
| local | None | Development |
| docker | Full (namespaced) | Production, gateway |
| ssh | Network boundary | Remote hardware |
| modal | Full (cloud VM) | Ephemeral/serverless |
| daytona | Full (container) | Cloud dev environments |
| singularity | Namespaces | HPC clusters |

### Docker Config

```yaml
terminal:
  backend: docker
  docker_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  docker_forward_env:
    - "GITHUB_TOKEN"
  docker_volumes:
    - "/home/user/projects:/workspace/projects"
    - "/home/user/data:/data:ro"
  container_cpu: 1
  container_memory: 5120          # MB
  container_persistent: true
```

### SSH Config

```yaml
terminal:
  backend: ssh
  persistent_shell: true
```

Required env vars: `TERMINAL_SSH_HOST`, `TERMINAL_SSH_USER`  
Optional: `TERMINAL_SSH_PORT`, `TERMINAL_SSH_KEY`

### Memory

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200
  user_char_limit: 1375
```

### Context Compression

```yaml
compression:
  enabled: true
  threshold: 0.50                # Compress at 50% of context limit
  target_ratio: 0.20             # Preserve last 20% as recent tail
  protect_last_n: 20             # Minimum uncompressed recent messages
```

### Agent Iteration Budget

```yaml
agent:
  max_turns: 90                  # Max iterations per turn
  reasoning_effort: ""           # empty=medium; none, minimal, low, medium, high, xhigh
  tool_use_enforcement: "auto"   # auto, true, false, or list of providers
```

Budget pressure warnings fire at 70% and 90% of max_turns.

### Delegation (Subagents)

```yaml
delegation:
  max_concurrent_children: 3     # Parallel subagents per batch
  max_spawn_depth: 1             # 1=flat, 2-3=nested orchestration
  orchestrator_enabled: true
```

### Security

```yaml
security:
  redact_secrets: true
  tirith_enabled: true
  tirith_fail_open: true         # Allow execution if Tirith scan unavailable
  website_blocklist:
    enabled: false
    domains:
      - "*.internal.company.com"
```

### Approvals

```yaml
approvals:
  mode: manual                   # manual (default), smart, off
```

### Web Search Backend

```yaml
web:
  backend: firecrawl             # firecrawl, parallel, tavily, exa
```

Auto-detects from: `FIRECRAWL_API_KEY`, `PARALLEL_API_KEY`, `TAVILY_API_KEY`, `EXA_API_KEY`.

### Worktree Isolation

```yaml
worktree: true                   # Always create git worktrees for isolation
```

Each session gets an isolated branch in `.worktrees/` for parallel agent execution.

### Quick Commands (Zero-token shortcuts)

```yaml
quick_commands:
  status:
    type: exec
    command: systemctl status hermes-agent
  disk:
    type: exec
    command: df -h /
```

Usage in CLI or messaging: `/status`, `/disk`. 30-second timeout.

---

## Profiles: Multiple Independent Agents

Each profile is a separate `~/.hermes/` directory with its own config, memories, skills, sessions, and cron jobs.

```bash
hermes profile create mybot           # Blank new profile
hermes profile create work --clone    # Copy config, separate memories
hermes profile create backup --clone-all  # Full state duplicate

hermes profile use coder              # Set sticky default profile
hermes -p coder chat                  # One-off profile override
```

**Profiles do NOT sandbox filesystem access** — agents in any profile have the same file permissions as the user account unless a container backend is configured.

**Use cases:**
- Separate coding, research, and personal assistants
- Independent gateway services per agent
- Agent backups and forking for experimentation

---

## Voice Mode

```yaml
tts:
  provider: "edge"               # edge, elevenlabs, openai, minimax, mistral, gemini, xai
  speed: 1.0
  edge:
    voice: "en-US-AriaNeural"
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"
    model_id: "eleven_multilingual_v2"

stt:
  provider: "local"              # local, groq, openai, mistral

voice:
  record_key: "ctrl+b"           # Push-to-talk hotkey
  auto_tts: false
```

Enable in CLI: `/voice on`

---

## Display Settings

```yaml
display:
  tool_progress: all             # off, new, all, verbose
  streaming: false
  show_reasoning: false
  show_cost: false
  compact: false
  tool_progress_overrides:
    telegram: 'verbose'
    signal: 'off'
```
