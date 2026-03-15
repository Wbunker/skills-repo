---
name: openclaw-expert
description: >
  OpenClaw (open-source AI agent platform, 100K+ GitHub stars) expert covering deployment,
  security hardening, memory systems, multi-agent teams, cron automation, voice integration,
  and troubleshooting. Based on 12 production guides and the official documentation. Use when:
  deploying OpenClaw on a VPS or Docker, writing SOUL.md or AGENTS.md files, designing memory
  architecture, setting up cron jobs and automations, building multi-agent teams, configuring
  voice (ElevenLabs), integrating with Supabase/Vercel/n8n, hardening security (gateway auth,
  firewall, Docker), troubleshooting agent issues, or designing closed-loop autonomous systems.
  Triggers on: /openclaw-expert, "OpenClaw", "openclaw", "SOUL.md", "AGENTS.md", "HEARTBEAT.md",
  "openclaw agent", "openclaw cron", "openclaw deploy", "openclaw security", "multi-agent",
  "agent team", "openclaw memory", "ElevenLabs agent", or "chatCompletions".
---

# OpenClaw Expert

Expert guidance for OpenClaw — the open-source AI agent platform for building autonomous agents with persistent memory, cron-driven automation, multi-agent teams, and integrations with voice, messaging, and external services.

## Architecture at a Glance

```
OpenClaw Instance
├── Gateway (port 18789)           ← HTTP API + chatCompletions endpoint
│   ├── Auth token                 ← Protect with bearer token
│   └── Bind to 127.0.0.1         ← Never expose to 0.0.0.0
├── Browser Control (port 18791)   ← Optional headless browser
├── Config: ~/.openclaw/openclaw.json
├── Identity
│   ├── SOUL.md                    ← Who the agent IS (40-60 lines)
│   ├── AGENTS.md                  ← Operational rules
│   └── IDENTITY.md                ← Display name, avatar
├── Memory
│   ├── MEMORY.md                  ← Curated long-term (< 200 lines)
│   ├── memory/YYYY-MM-DD.md       ← Daily activity logs
│   └── BOOT.md                    ← Crash recovery instructions
├── Automation
│   ├── cron/jobs.yaml             ← Scheduled tasks
│   └── HEARTBEAT.md               ← Periodic self-check
└── Agents (multi-agent)
    └── agents/
        ├── researcher/            ← Each agent has own SOUL.md,
        ├── writer/                  AGENTS.md, MEMORY.md, and
        └── monitor/                 memory/ directory
```

## Quick Reference

| Task | How | Reference |
|------|-----|-----------|
| Install (easy) | `ollama launch openclaw` (Ollama 0.17+) | [deployment.md](references/deployment.md) |
| Install (manual) | `curl -fsSL https://openclaw.ai/install.sh \| bash` | [deployment.md](references/deployment.md) |
| Deploy on VPS | Systemd service + UFW + loopback binding | [deployment.md](references/deployment.md) |
| Deploy with Docker | Compose + shm_size + SYS_ADMIN for browser | [deployment.md](references/deployment.md) |
| Choose a model | Cloud (kimi-k2.5, minimax) or local (qbm, qwen3) | [deployment.md](references/deployment.md) |
| CLI config | `openclaw config set`, `openclaw configure --section` | [deployment.md](references/deployment.md) |
| Secure the gateway | Bind 127.0.0.1, auth token, firewall | [security.md](references/security.md) |
| Docker hardening | read_only, no-new-privileges, cap_drop ALL | [security.md](references/security.md) |
| Write SOUL.md | 40-60 lines: identity, responsibilities, rules | [multi-agent.md](references/multi-agent.md) |
| Set up memory | MEMORY.md (< 200 lines) + daily logs pattern | [memory-systems.md](references/memory-systems.md) |
| Configure cron jobs | jobs.yaml with schedule + prompt | [automation.md](references/automation.md) |
| Build agent team | agents/ directory, one SOUL.md per agent | [multi-agent.md](references/multi-agent.md) |
| Voice (ElevenLabs) | Enable chatCompletions + ngrok/tunnel | [integrations.md](references/integrations.md) |
| Supabase state layer | 8-table schema for autonomous ops | [integrations.md](references/integrations.md) |
| Agent phone number | eSIM for calls, texts, reservations | [integrations.md](references/integrations.md) |
| WhatsApp multi-user | Agent bindings, allowlist, config-guard | [integrations.md](references/integrations.md) |
| Three-tier security | Personal vs Business vs Outward hardening | [security.md](references/security.md) |
| Config-guard | Protect config from OpenClaw startup rewrites | [security.md](references/security.md) |
| Replace SaaS apps | Markdown workspace (HABITS, PROJECTS, NOTES) | [memory-systems.md](references/memory-systems.md) |
| Diagnose issues | Logs, config validation, recovery patterns | [troubleshooting.md](references/troubleshooting.md) |

## Reference Files

| File | Topics |
|------|--------|
| `references/deployment.md` | Ollama install, manual install, model selection, CLI config, VPS setup, Docker compose (browser reqs), networking, systemd, costs |
| `references/security.md` | CVEs, gateway auth, firewall, Docker hardening, tool restrictions, credentials, malicious skills, three-tier security model, config-guard, env var isolation |
| `references/memory-systems.md` | Memory architecture, daily logs, MEMORY.md curation, SaaS-replacement workspace, git-backed notes, voice note workflow, external providers (QMD, Mem0, Cognee, Obsidian), context management |
| `references/multi-agent.md` | Agents vs subagents, workspace structure, SOUL.md design with templates, file-based coordination, closed-loop automation, shared brain, messaging platforms |
| `references/automation.md` | Cron system, daily schedule, 20+ production automation recipes (dev, business, monitoring, life admin), HEARTBEAT.md |
| `references/integrations.md` | ElevenLabs voice, Supabase schema, Vercel dashboard, n8n, Telegram/WhatsApp setup, agent bindings, eSIM phone number, content marketing pipeline |
| `references/troubleshooting.md` | Install failures, gateway issues, memory overflow, cron debugging, agent crashes, upgrades, recovery patterns |

## Decision Trees

### "How should I deploy?"

```
Personal/single agent?
├── yes → $5 VPS (Contabo/Hetzner) + systemd
│         └── See references/deployment.md
└── no → Multi-agent or team?
    ├── 2-3 agents → $10-15 VPS + Docker compose
    └── 6+ agents → $20-30 VPS + Docker + Supabase for state
                     └── See references/integrations.md (Supabase)
```

### "How should I structure memory?"

```
Single agent, simple tasks?
├── yes → SOUL.md + MEMORY.md + daily logs (3 files)
│         └── See references/memory-systems.md
└── no → Multiple agents or complex state?
    ├── Multiple agents → Per-agent memory directories
    │   └── See references/multi-agent.md (Workspace Structure)
    └── Semantic search needed?
        ├── yes → QMD or Mem0
        └── no → Local files with weekly compaction
            └── See references/memory-systems.md (Maintenance)
```

### "Which automation pattern?"

```
One-time task?
├── yes → Subagent (no cron needed)
└── no → Recurring?
    ├── Scheduled (time-based) → Cron job
    │   └── See references/automation.md
    ├── Event-driven → Trigger + reaction matrix
    │   └── See references/multi-agent.md (Closed-Loop)
    └── Autonomous loop → Proposal → Mission → Execution cycle
        └── See references/integrations.md (Supabase)
```

### "How to add voice?"

```
Web-only voice?
├── yes → ElevenLabs Agent + ngrok/tunnel → OpenClaw chatCompletions
└── no → Phone calls too?
    └── yes → ElevenLabs Agent + Twilio phone number
        └── See references/integrations.md (Voice)
```

## Key Principles

1. **SOUL.md is identity, not documentation** — 40-60 lines max, personality + rules + constraints
2. **MEMORY.md is curated, not appended** — Under 200 lines, update don't grow, prune weekly
3. **One-writer, many-readers** — Each shared file has exactly one agent that writes to it
4. **Gateway never on 0.0.0.0** — Always bind to 127.0.0.1, use tunnels for remote access
5. **Principle of least privilege** — Each agent gets only the tools and access it needs
6. **Start simple, add agents when recurring** — Don't pre-build a team; split off agents as patterns emerge
