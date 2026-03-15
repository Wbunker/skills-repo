# Multi-Agent Systems

Agent teams, workspace structure, coordination patterns, and closed-loop architectures.

## Table of Contents

- [Agents vs Subagents](#agents-vs-subagents)
- [Workspace Structure](#workspace-structure)
- [SOUL.md Design](#soulmd-design)
- [File-Based Coordination](#file-based-coordination)
- [Multi-Agent Architectures](#multi-agent-architectures)
- [Closed-Loop Automation](#closed-loop-automation)
- [Shared Brain Pattern](#shared-brain-pattern)
- [Messaging Interfaces](#messaging-interfaces)
- [Scaling Patterns](#scaling-patterns)

---

## Agents vs Subagents

| | Agents | Subagents |
|--|--------|-----------|
| Lifespan | Permanent team members | Temporary, task-scoped |
| Identity | Own SOUL.md, workspace, model | Inherit parent config |
| Memory | Own memory directory | No persistent memory |
| Cron | Own schedules | None |
| Cost | Dedicated resources | On-demand |
| Use case | Ongoing responsibilities | One-off delegation |

### When to use each

- **Agent**: Recurring role (research, content, monitoring, engineering)
- **Subagent**: One-time task delegation ("summarize this document", "parse this data")

## Workspace Structure

### Single agent

```
~/.openclaw/
├── openclaw.json
├── SOUL.md
├── AGENTS.md
├── MEMORY.md
├── HEARTBEAT.md
└── memory/
    ├── 2026-03-01.md
    └── 2026-02-28.md
```

### Multi-agent team

```
~/.openclaw/
├── openclaw.json              # Global config
├── SOUL.md                    # Main agent identity
├── AGENTS.md                  # Main agent rules
├── MEMORY.md                  # Main agent memory
├── agents/
│   ├── researcher/
│   │   ├── SOUL.md            # Researcher identity
│   │   ├── AGENTS.md
│   │   ├── MEMORY.md
│   │   └── memory/
│   ├── writer/
│   │   ├── SOUL.md
│   │   ├── AGENTS.md
│   │   ├── MEMORY.md
│   │   └── memory/
│   └── monitor/
│       ├── SOUL.md
│       ├── AGENTS.md
│       ├── MEMORY.md
│       └── memory/
└── shared/                    # Shared brain (optional)
    ├── brand-voice.md
    ├── client-context.md
    └── content-calendar.md
```

## SOUL.md Design

### Principles

1. **40-60 lines max** — loaded every session, every token counts
2. **Identity first** — who you are, then what you do
3. **Personality via character** — name after a TV/movie character for instant baseline
4. **Rules as constraints** — what NOT to do is often more useful than what to do
5. **Iterative refinement** — "corrective prompt-engineering" over multiple sessions

### Template structure

```markdown
# [Agent Name] — [Role Title]

## Identity
You are [Name], the [role] for [team/person].
[1-2 sentences of personality and working style.]

## Responsibilities
- [Primary responsibility]
- [Secondary responsibility]
- [Tertiary responsibility]

## Rules
- [Hard constraint 1]
- [Hard constraint 2]
- [Communication rule]
- [Quality standard]

## Tools & access
- [Available tools/APIs]
- [File paths and permissions]

## Output format
- [How to structure responses/artifacts]
- [Where to save outputs]
```

### Example: Research agent

```markdown
# Dwight — Research Director

## Identity
You are Dwight, the research director. Thorough, methodical, slightly intense.
You believe in facts over opinions and always cite your sources.

## Responsibilities
- Deep research on topics assigned by the team lead
- Competitive analysis and market monitoring
- Fact-checking content before publication

## Rules
- Always include sources with URLs
- Never speculate — if unsure, say "insufficient data"
- Save research to research/[topic]-[date].md
- Max 500 words per research brief unless asked for more

## Tools
- web_search, read_file, write_file
- No shell access, no messaging (report via files)
```

### Example: Content agent

```markdown
# Kelly — Social Media Manager

## Identity
You are Kelly, the social media manager. Creative, trend-aware, data-driven.
You write engaging posts that balance personality with professionalism.

## Responsibilities
- Draft Twitter/X posts based on content calendar
- Adapt content for different platforms
- Track engagement metrics and adjust strategy

## Rules
- Never post without approval (save drafts to drafts/)
- Include relevant hashtags (2-3 max)
- No controversial topics without explicit approval
- Morning posts (9-11am EST) perform best — schedule accordingly

## Output
- Drafts: drafts/[platform]-[date]-[topic].md
- Analytics: reports/engagement-[week].md
```

### Example: Chief of staff agent

```markdown
# Monica — Chief of Staff

## Identity
You are Monica, the chief of staff. Organized, proactive, no-nonsense.
You keep everything running smoothly and flag issues before they become problems.

## Responsibilities
- Morning briefing: calendar, tasks, priorities
- Coordinate between agents — route requests to the right agent
- Track deadlines and follow up on overdue items
- End-of-day summary

## Rules
- Brief the user by 8am every day
- Never make decisions on behalf of the user — present options
- Escalate anything involving money, legal, or public statements
- Keep all briefings under 200 words
```

## File-Based Coordination

### One-writer, many-readers pattern

**The fundamental rule**: Each file has exactly one agent that writes to it. Other agents can read.

```
content-calendar.md
  Writer: Kelly (content agent)
  Readers: Monica (chief of staff), Dwight (researcher)

research/competitive-analysis.md
  Writer: Dwight (researcher)
  Readers: Kelly (content), Monica (chief of staff)

daily-brief.md
  Writer: Monica (chief of staff)
  Readers: All agents
```

### Why this matters

- No write conflicts between agents
- Clear ownership and accountability
- Simple debugging (check the writer's logs)
- No need for locks or coordination protocols

### Handoff via files

```markdown
<!-- handoffs/research-to-content.md -->
# Research → Content Handoff

## Topic: [Topic Name]
## Research file: research/[topic].md
## Key points for content:
1. [Point 1]
2. [Point 2]
3. [Point 3]

## Suggested angle: [angle]
## Deadline: [date]
## Status: pending_content
```

## Multi-Agent Architectures

### Hub and spoke (simple)

```
         ┌──── Researcher
         │
User ──→ Chief of Staff ──── Writer
         │
         └──── Monitor
```

Chief of staff routes all requests. Agents don't communicate directly.

### Mesh (complex)

```
  Researcher ←──→ Writer
      ↑              ↑
      │              │
      ↓              ↓
  Monitor ←───→ Chief of Staff ←──→ User
```

Agents coordinate via shared files. More flexible but harder to debug.

### Pipeline

```
Ingest → Process → Review → Publish
```

Each agent handles one stage, passes output to next via files.

## Closed-Loop Automation

### Proposal → Mission → Execution cycle

For complex autonomous operations (e.g., running a business):

```
┌──────────────────────────────────────────────────┐
│                                                    │
│  Proposal → Auto-approve → Mission + Steps         │
│      ↑                         │                   │
│      │                         ↓                   │
│  Trigger/Reaction ←── Event ← Worker executes     │
│                                                    │
└──────────────────────────────────────────────────┘
```

### Key components

| Component | Purpose |
|-----------|---------|
| Proposal | Request to do something (created by trigger or agent) |
| Auto-approve | Policy check: is this within approved parameters? |
| Mission | Approved proposal becomes a mission with steps |
| Worker | Agent that executes mission steps |
| Event | Result of worker execution |
| Trigger | Event pattern that spawns new proposals |
| Reaction | Immediate response to an event (notification, log) |

### Cap gates (prevent runaway)

Reject proposals at entry when:
- Daily API budget exceeded
- Too many concurrent missions
- Agent is in cooldown period

```
createProposalAndMaybeAutoApprove()
  ├── Check cap gates → REJECT if over limits
  ├── Check policy → AUTO-APPROVE if within policy
  └── Queue for human review otherwise
```

### Trigger + Reaction matrix

| Event | Trigger | Reaction | Cooldown |
|-------|---------|----------|----------|
| New follower | Thank-you DM proposal | Log to analytics | 1 per user |
| Error spike | Diagnosis mission | Alert via Telegram | 15 min |
| Content published | Cross-post proposals | Update calendar | None |
| Invoice overdue | Reminder email proposal | Flag in dashboard | 24 hours |

### Self-healing: Recover stale steps

```yaml
- name: "recover-stale"
  schedule: "*/30 * * * *"
  prompt: >
    Check ops_mission_steps for any steps in 'running' state for more than
    30 minutes. Mark them as 'failed' with reason 'stale_timeout'.
    Create recovery proposals for critical missions.
```

## Shared Brain Pattern

Symlink a directory so multiple agents share context:

```bash
# Create shared directory
mkdir -p ~/.openclaw/shared

# Symlink into each agent's workspace
ln -s ~/.openclaw/shared ~/.openclaw/agents/researcher/shared
ln -s ~/.openclaw/shared ~/.openclaw/agents/writer/shared
ln -s ~/.openclaw/shared ~/.openclaw/agents/monitor/shared
```

Contents: brand voice guides, client context, content calendars, shared research.

**Rule**: Shared brain files should be read-only for most agents. Designate one agent as the maintainer.

## Messaging Interfaces

| Platform | Setup complexity | Cost | Best for |
|----------|-----------------|------|----------|
| Telegram | Low | Free | Primary interface, bot API |
| WhatsApp | Medium | Business API costs | Client communication |
| Discord | Low | Free | Team/community |
| Slack | Low | Free tier available | Workspace integration |
| Signal | Medium | Free | Privacy-focused |
| iMessage | High | macOS only | Apple ecosystem |

### Telegram as primary interface

Most production OpenClaw setups use Telegram because:
- Free bot API with no rate limits for personal use
- Rich formatting (markdown, buttons, media)
- Available on all platforms
- Easy to set up with BotFather

## Scaling Patterns

### Adding agents incrementally

1. Start with one agent (chief of staff / general assistant)
2. When a responsibility becomes recurring, spin it into a dedicated agent
3. Keep the chief of staff as coordinator
4. Max recommended: 6-8 agents (beyond this, coordination overhead dominates)

### Resource allocation

| Agent count | VPS RAM | Model strategy |
|-------------|---------|---------------|
| 1 | 2 GB | Single model (Sonnet or Opus) |
| 2-3 | 4 GB | Opus for lead, Sonnet for workers |
| 4-6 | 8 GB | Opus for complex, Sonnet for routine, Gemini for bulk |
| 7+ | 16 GB | Mixed models, stagger cron schedules |
