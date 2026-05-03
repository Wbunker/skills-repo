---
name: hermes-agent-expert
description: >
  Expert guide for Hermes Agent (Nous Research) — the open-source, self-hosted AI agent with
  persistent cross-session memory and a self-improving skills loop. Use when: installing or
  configuring Hermes Agent; setting up SOUL.md, MEMORY.md, or USER.md; choosing a model
  provider (Nous Portal, OpenRouter, Ollama, Kimi, DeepSeek, etc.); configuring terminal
  backends (local, docker, ssh, modal); setting up messaging gateways (Telegram, Discord,
  Slack, WhatsApp, Signal, 16+ platforms); working with the skills system or agentskills.io;
  enabling deep research / ConductResearch / think_tool; hardening security (command approval,
  container isolation, prompt injection, credential protection); migrating from OpenClaw;
  configuring cron automation; setting up multiple agent profiles; or troubleshooting Hermes.
  Triggers on: "hermes agent", "Hermes Agent", "hermes-agent", "NousResearch agent",
  "MEMORY.md hermes", "hermes skills", "hermes gateway", "hermes claw migrate", "self-improving agent".
---

# Hermes Agent Expert

Expert guidance for Hermes Agent — the self-hosted, self-improving AI agent by Nous Research
(MIT license, 64K+ GitHub stars as of 2026). Hermes executes tasks, writes Skills from experience,
maintains four-tier persistent memory, and improves automatically the longer you use it.

**Docs:** https://hermes-agent.nousresearch.com/docs/  
**GitHub:** https://github.com/NousResearch/hermes-agent

## Architecture at a Glance

```
~/.hermes/
├── config.yaml          ← All non-secret settings
├── .env                 ← API keys and secrets
├── auth.json            ← OAuth credentials
├── SOUL.md              ← Agent identity (system prompt slot #1, max 20K chars)
├── memories/
│   ├── MEMORY.md        ← Agent notes: env facts, conventions (~800 tokens max)
│   └── USER.md          ← Your profile: prefs, style, timezone (~500 tokens max)
├── skills/              ← Agent-authored + installed skill docs
├── cron/                ← Scheduled jobs
├── sessions/            ← Gateway sessions
└── logs/                ← Auto-redacted error/gateway logs
```

**Tools vs Skills (critical distinction):**
- **Tools** = Python functions via JSON schema (deterministic, ~47 built-in)
- **Skills** = markdown docs the agent reads and follows; agent self-authors these after successful task completions

## Quick Reference

| Goal | How | Reference |
|---|---|---|
| Install Hermes | One-line installer | [installation.md](references/installation.md) |
| Choose a model/provider | `hermes model` | [installation.md](references/installation.md) |
| Run locally with Ollama | Point to `http://localhost:11434/v1` | [installation.md](references/installation.md) |
| Deploy on VPS | Systemd + docker backend | [installation.md](references/installation.md) |
| Understand memory tiers | MEMORY.md + USER.md + SQLite + plugins | [memory-system.md](references/memory-system.md) |
| Write/edit SOUL.md | Agent identity file | [configuration.md](references/configuration.md) |
| Configure config.yaml | All settings, backends, compression | [configuration.md](references/configuration.md) |
| Run multiple agents | `hermes profile create <name>` | [configuration.md](references/configuration.md) |
| Install/browse skills | `hermes skills` / agentskills.io | [skills-and-research.md](references/skills-and-research.md) |
| Enable deep research | think_tool + ConductResearch | [skills-and-research.md](references/skills-and-research.md) |
| Harden security | Command approval, Docker, gateway auth | [security.md](references/security.md) |
| Set up messaging gateway | Telegram, Discord, Slack, WhatsApp, 16+ | [integrations.md](references/integrations.md) |
| Schedule cron tasks | Built-in cron in natural language | [integrations.md](references/integrations.md) |
| Migrate from OpenClaw | `hermes claw migrate` | [integrations.md](references/integrations.md) |
| Diagnose issues | `hermes doctor` | [troubleshooting.md](references/troubleshooting.md) |

## Decision Trees

### "Which model/provider?"

```
Want zero cost + full data privacy?
├── yes → Ollama local (http://localhost:11434/v1)
│         Use qwen2.5-coder:32b for orchestrator; smaller quantized for sub-agents
│         Minimum 64K context required
└── no → Cloud?
    ├── Least friction → Nous Portal or OpenRouter (400+ models, single API key)
    ├── Cost-optimized → DeepSeek or Kimi/Moonshot
    └── Enterprise → NVIDIA NIM (Nemotron) or Anthropic direct
```

### "Which terminal backend?"

```
Development / personal use?
├── yes → local (simplest, no isolation)
└── no → Production / gateway?
    ├── VPS or server → docker (recommended: full container isolation)
    ├── Remote machine → ssh (network boundary)
    ├── Ephemeral serverless → modal (cloud VM, near-zero idle cost)
    └── HPC cluster → singularity
```

### "How to structure memory?"

```
Single agent?
├── yes → Defaults fine: SOUL.md + MEMORY.md + USER.md
└── no → Multiple independent agents?
    ├── yes → hermes profile create (full state isolation per profile)
    └── Complex semantic recall needed?
        └── Add Honcho or Mem0 as Tier 4 plugin
            See references/memory-system.md
```

### "How to add a gateway?"

```
Personal / solo?
├── yes → Telegram (BotFather + user ID, simplest setup)
└── no → Team or multi-user?
    ├── yes → Discord (require_mention + auto_thread) or Slack
    └── Mobile-first?
        └── WhatsApp or Signal
            See references/integrations.md
```

## Reference Files

| File | Contents |
|---|---|
| [installation.md](references/installation.md) | Install, prerequisites, platforms, model providers, Ollama local, VPS/Docker deploy, session commands |
| [memory-system.md](references/memory-system.md) | Four-tier architecture, MEMORY.md + USER.md limits, frozen snapshot, periodic nudge, FTS5 session search, 8 external plugins |
| [configuration.md](references/configuration.md) | config.yaml full reference, SOUL.md / context file hierarchy, profiles, terminal backends, auxiliary models, compression |
| [skills-and-research.md](references/skills-and-research.md) | Self-authoring loop, agentskills.io hub, deep research (think_tool + ConductResearch), subagent parallelization |
| [security.md](references/security.md) | Command approval modes, Docker hardening, gateway DM pairing, credential filtering, prompt injection, SSRF, Tirith |
| [integrations.md](references/integrations.md) | 16+ messaging platforms, cron, OpenClaw migration, MCP servers, Nous Portal tool gateway |
| [troubleshooting.md](references/troubleshooting.md) | hermes doctor, common failures, config validation, session recovery, upgrade path |

## Key Principles

1. **Frozen snapshot** — Memory loads once at session start; mid-session changes persist to disk but don't modify the active prompt (preserves LLM prefix cache)
2. **Skills compound** — Agent writes skill docs after successful completions; value accumulates over weeks, not sessions
3. **Tools stable, Skills are knowledge** — Don't edit Python tool files for workflow changes; create/update a skill doc instead
4. **64K context minimum** — Models below this cannot maintain multi-step tool-calling workflows
5. **Docker in production** — Container backends skip dangerous-command checks because the container IS the security boundary
6. **Profiles for multiple agents** — Profiles give full state isolation; editing SOUL.md alone shares memory and sessions
