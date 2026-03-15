# Security Hardening

CVEs, access control, credential management, tool restrictions, and compliance.

## Table of Contents

- [Known Vulnerabilities](#known-vulnerabilities)
- [Network Security](#network-security)
- [Authentication & Authorization](#authentication--authorization)
- [Docker Hardening](#docker-hardening)
- [Tool & Sandbox Restrictions](#tool--sandbox-restrictions)
- [Credential Management](#credential-management)
- [Malicious Skills (ClawHub)](#malicious-skills-clawhub)
- [Three-Tier Deployment Security](#three-tier-deployment-security)
- [Config-Guard Pattern](#config-guard-pattern)
- [Environment Variable Isolation](#environment-variable-isolation)
- [Security Checklist](#security-checklist)

---

## Known Vulnerabilities

| CVE | Severity | Description | Fix |
|-----|----------|-------------|-----|
| CVE-2026-25253 | Critical | Remote code execution via gateway | Update to ≥ v0.8.2, bind to loopback |
| CVE-2025-6514 | High | Path traversal in file access | Update to ≥ v0.7.5 |

```bash
# Always run latest
openclaw update

# Check version
openclaw --version
```

## Network Security

### The exposure problem

Over **135,000 OpenClaw instances** have been found exposed on the public internet. Default gateway binds to `0.0.0.0:18789`, making it accessible to anyone.

### Mandatory: Bind to loopback

```json
{
  "gateway": {
    "http": {
      "host": "127.0.0.1",
      "port": 18789
    }
  }
}
```

### Firewall rules

```bash
# UFW (Ubuntu/Debian)
ufw default deny incoming
ufw allow ssh
ufw deny 18789    # Block gateway from outside
ufw deny 18791    # Block browser control
ufw enable

# iptables alternative
iptables -A INPUT -p tcp --dport 18789 -s 127.0.0.1 -j ACCEPT
iptables -A INPUT -p tcp --dport 18789 -j DROP
```

### DM policy

Control who can message your OpenClaw instance:

```json
{
  "security": {
    "dmPolicy": "allowlist",
    "allowedSenders": [
      "your-email@example.com",
      "+1234567890"
    ]
  }
}
```

Options: `"open"` (anyone), `"allowlist"` (specified only), `"disabled"` (no DMs).

## Authentication & Authorization

### Gateway auth token

```json
{
  "gateway": {
    "http": {
      "auth": {
        "token": "your-long-random-secret"
      }
    }
  }
}
```

Generate a strong token:
```bash
openssl rand -hex 32
```

### API key scoping

- Use separate API keys per agent when running multi-agent setups
- Set spending limits per key in the provider dashboard
- Rotate keys regularly

## Docker Hardening

### Production-grade container config

```yaml
services:
  openclaw:
    image: openclaw/openclaw:latest
    read_only: true                    # Immutable filesystem
    security_opt:
      - no-new-privileges:true         # Prevent privilege escalation
    cap_drop:
      - ALL                            # Drop all Linux capabilities
    tmpfs:
      - /tmp:noexec,nosuid,size=100m   # Temp with restrictions
    deploy:
      resources:
        limits:
          memory: 2G                   # Prevent OOM from runaway processes
          cpus: '1.0'
    volumes:
      - ./data:/home/openclaw/.openclaw:rw
    user: "1000:1000"                  # Non-root user
    networks:
      - internal
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

### Key hardening properties

| Property | Purpose |
|----------|---------|
| `read_only: true` | Prevents writing to container filesystem |
| `cap_drop: ALL` | Removes all Linux capabilities |
| `no-new-privileges` | Blocks setuid/setgid escalation |
| `tmpfs /tmp:noexec` | Temp files can't be executed |
| Memory/CPU limits | Prevents resource exhaustion |
| `user: "1000:1000"` | Runs as non-root |
| Internal network | No direct internet access |

## Tool & Sandbox Restrictions

### Restrict available tools

```json
{
  "tools": {
    "allowed": [
      "read_file",
      "write_file",
      "web_search",
      "send_message"
    ],
    "blocked": [
      "execute_command",
      "browser_navigate"
    ]
  }
}
```

### Sandbox modes

| Mode | Allows | Use case |
|------|--------|----------|
| `strict` | Read-only file access, no shell | Research agents, read-only tasks |
| `standard` | File read/write, limited shell | Most automation |
| `permissive` | Full access including shell | Development, admin tasks |

```json
{
  "sandbox": {
    "mode": "standard"
  }
}
```

### Per-agent scoping

Give each agent only the permissions it needs:

```json
{
  "agents": {
    "researcher": {
      "sandbox": "strict",
      "tools": { "allowed": ["web_search", "read_file"] }
    },
    "writer": {
      "sandbox": "standard",
      "tools": { "allowed": ["read_file", "write_file"] }
    }
  }
}
```

## Credential Management

### Environment variables (recommended)

```bash
# .env file (never commit)
ANTHROPIC_API_KEY=sk-ant-...
OPENCLAW_AUTH_TOKEN=...
TELEGRAM_BOT_TOKEN=...
SUPABASE_SERVICE_KEY=...
```

```json
// openclaw.json — reference env vars
{
  "gateway": {
    "http": {
      "auth": { "token": "${OPENCLAW_AUTH_TOKEN}" }
    }
  }
}
```

### Secret rotation

- Rotate API keys monthly or after any suspected compromise
- Use provider-managed secrets (AWS SSM, Vault) for production
- Monitor for leaked secrets with `.env leak panic button` automation

### .env leak detection automation

```yaml
# Cron job to check for exposed secrets
- name: "env-leak-check"
  schedule: "0 */6 * * *"
  prompt: >
    Search the workspace for any files that contain API keys, tokens,
    or credentials that should not be committed. Check .env files are
    in .gitignore. Report any findings immediately via Telegram.
```

## Malicious Skills (ClawHub)

~900 malicious skills have been identified on ClawHub. Before installing community skills:

1. **Read the SKILL.md** — check for suspicious shell commands or network calls
2. **Check the publisher** — verified publishers are safer
3. **Review tool permissions** — skills requesting `execute_command` need scrutiny
4. **Test in sandbox** — run new skills in strict mode first
5. **Pin versions** — don't auto-update community skills

```bash
# Install with review
openclaw skill install some-skill --dry-run    # Preview first
openclaw skill install some-skill --sandbox strict
```

## Three-Tier Deployment Security

Not every setup needs the same hardening. Match security to exposure level:

| Feature | Tier 1: Personal | Tier 2: Business/Family | Tier 3: Outward |
|---------|-----------------|------------------------|-----------------|
| Users | Just you | You + trusted people | Customers, strangers, public |
| Purpose | Productivity (notes, calendar, research) | Shared tasks, collaboration | Support, community, public info |
| Data storage | Private GitHub repo, markdown files | Separated workspaces (/shared) | No access to personal files or data |
| Infrastructure | Private VPS via secure tunnel | Shared infra, multi-agent routing | Separate phone line/gateway, sandboxed |
| Access level | Full (shell, web, files) | Restricted (no shell for shared agents) | Minimum viable (search & respond) |
| Routing | Single entry point | Bindings (WhatsApp ID → Agent) | Dedicated public gateway or number |

### Critical rules per tier

- **Tier 1**: Never give the agent `sudo` or expose it to the internet without a tunnel
- **Tier 2**: Never assume a prompt (system instructions) is a security wall — use hard tool restrictions to prevent agents from reading each other's `.env` files
- **Tier 3**: Never link personal tools (calendar, email) — treat this agent as a "stranger with a script"

## Config-Guard Pattern

**Problem**: OpenClaw rewrites `openclaw.json` on startup and during `openclaw doctor`, silently stripping custom settings — particularly `channels.whatsapp.allowFrom`, agent bindings, and rotated tokens.

**Solution**: Maintain a "golden config" and auto-restore on drift.

### Golden config in Docker entrypoint

```bash
# In docker-compose.yml entrypoint:
# 1. Clean stale Chrome locks
# 2. After gateway starts (~15s), restore golden config
find /data/.openclaw/browser -name SingletonLock -delete 2>/dev/null
( sleep 15 \
  && GOLDEN_CFG=/data/.openclaw/config-backups/openclaw.json.golden \
  && [ -f "$$GOLDEN_CFG" ] \
  && cp "$$GOLDEN_CFG" /data/.openclaw/openclaw.json \
  && echo '[config-guard] Restored golden config after startup' \
) &
exec /entrypoint.sh node /server.cjs
```

### Config-watch cron (every 1 minute)

```bash
#!/bin/bash
# config-watch.sh — auto-restores openclaw.json when drift detected
CONFIG="/data/.openclaw/openclaw.json"
GOLDEN="/data/.openclaw/config-backups/openclaw.json.golden"

[ -f "$GOLDEN" ] || exit 0   # No golden copy yet

# Validate bindings and allowlist are intact
BINDING_COUNT=$(python3 -c "
import json
cfg = json.load(open('$CONFIG'))
bindings = cfg.get('bindings', [])
# Check your expected bindings are present
print(len(bindings))
" 2>/dev/null)

if [ "$BINDING_COUNT" != "expected_count" ]; then
    cp "$CONFIG" "$CONFIG.pre-restore-$(date +%Y%m%d-%H%M%S)"
    cp "$GOLDEN" "$CONFIG"
    cd /path/to/docker && docker compose restart openclaw
fi
```

Schedule: `* * * * * /path/to/config-watch.sh`

## Environment Variable Isolation

**Risk**: In multi-agent setups, any agent with shell access can read environment variables — exposing API keys, passwords, and tokens of other agents.

**Mitigations**:
- Restrict shell access for shared/public agents (`sandbox: "strict"`)
- Use per-agent `.env` files with Docker secrets
- Never store secrets in files accessible to all agents
- Use tool restrictions to block `execute_command` for agents that don't need it

## Security Checklist

Pre-production security audit:

- [ ] Gateway bound to `127.0.0.1` (not `0.0.0.0`)
- [ ] Auth token set on gateway
- [ ] UFW/iptables blocking ports 18789, 18791 from outside
- [ ] SSH key-only auth, root login disabled
- [ ] Docker: read-only, no-new-privileges, cap-drop ALL
- [ ] API keys in env vars, not in config files
- [ ] .env in .gitignore
- [ ] DM policy set to allowlist
- [ ] Tool restrictions per agent (principle of least privilege)
- [ ] OpenClaw updated to latest version
- [ ] Secrets rotation schedule in place
- [ ] Community skills reviewed before install
- [ ] Backup automation configured
- [ ] Monitoring/alerting for failed auth attempts
