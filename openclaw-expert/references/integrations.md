# Integrations & Voice

ElevenLabs voice, Supabase, Vercel, n8n, and third-party service patterns.

## Table of Contents

- [Voice Integration (ElevenLabs)](#voice-integration-elevenlabs)
- [Supabase Integration](#supabase-integration)
- [Vercel Integration](#vercel-integration)
- [n8n Workflow Integration](#n8n-workflow-integration)
- [Messaging Platforms](#messaging-platforms)
- [Agent Phone Number (eSIM)](#agent-phone-number-esim)
- [Content & Marketing Stack](#content--marketing-stack)

---

## Voice Integration (ElevenLabs)

### Architecture

```
Phone/Web ──→ ElevenLabs Agent ──→ OpenClaw Gateway ──→ Agent
                (speech/turn-taking)    (chatCompletions)    (reasoning/memory/tools)
```

ElevenLabs handles voice synthesis and speech recognition. OpenClaw handles reasoning, memory, and tool use. Clean separation of concerns.

### Step 1: Enable chatCompletions endpoint

```json
// openclaw.json
{
  "gateway": {
    "http": {
      "host": "127.0.0.1",
      "port": 18789,
      "endpoints": {
        "chatCompletions": {
          "enabled": true
        }
      }
    }
  }
}
```

### Step 2: Expose via ngrok (development)

```bash
ngrok http 18789
# Note the https://xxxxx.ngrok.io URL
```

For production, use Cloudflare Tunnel or a reverse proxy instead of ngrok.

### Step 3: Configure ElevenLabs Agent

1. Create an Agent at elevenlabs.io/agents
2. Set LLM to **Custom LLM**
3. Enter URL: `https://your-ngrok-url.ngrok.io/v1/chat/completions`
4. Select voice and configure conversation settings
5. Test via the web widget

### Step 4: Add phone number (optional)

1. In ElevenLabs Agent settings, go to **Phone Numbers**
2. Connect a Twilio number or buy one through ElevenLabs
3. Map the phone number to your agent
4. Incoming calls are routed: Twilio → ElevenLabs → OpenClaw

### Voice configuration tips

- Set `max_tokens` appropriately — voice responses should be shorter than text
- Add to SOUL.md: "When responding to voice, keep answers under 3 sentences"
- Use ElevenLabs' turn-taking settings to control interruption behavior
- Test with both web widget and phone before going live

## Supabase Integration

### 3-layer architecture with Supabase

```
OpenClaw (VPS) = Think + Execute
Vercel = Approve + Monitor (optional dashboard)
Supabase = All State
```

### Schema for autonomous operations

```sql
-- Mission proposals (entry point for all autonomous actions)
CREATE TABLE ops_mission_proposals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_name TEXT NOT NULL,
  proposal_type TEXT NOT NULL,
  description TEXT NOT NULL,
  status TEXT DEFAULT 'pending',     -- pending, approved, rejected
  auto_approved BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Active missions
CREATE TABLE ops_missions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  proposal_id UUID REFERENCES ops_mission_proposals(id),
  agent_name TEXT NOT NULL,
  title TEXT NOT NULL,
  status TEXT DEFAULT 'active',      -- active, completed, failed
  started_at TIMESTAMPTZ DEFAULT now(),
  completed_at TIMESTAMPTZ
);

-- Mission steps (granular execution tracking)
CREATE TABLE ops_mission_steps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mission_id UUID REFERENCES ops_missions(id),
  step_number INT NOT NULL,
  description TEXT NOT NULL,
  status TEXT DEFAULT 'pending',     -- pending, running, completed, failed
  result JSONB,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ
);

-- Agent events (audit trail)
CREATE TABLE ops_agent_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_name TEXT NOT NULL,
  event_type TEXT NOT NULL,
  payload JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Policy rules (auto-approve criteria)
CREATE TABLE ops_policy (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_name TEXT NOT NULL,
  action_type TEXT NOT NULL,
  auto_approve BOOLEAN DEFAULT false,
  max_daily_count INT,
  max_cost_per_action NUMERIC
);

-- Trigger rules (event → proposal mapping)
CREATE TABLE ops_trigger_rules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_pattern TEXT NOT NULL,
  proposal_template JSONB NOT NULL,
  cooldown_minutes INT DEFAULT 0,
  probability NUMERIC DEFAULT 1.0,
  enabled BOOLEAN DEFAULT true
);

-- Agent reactions (immediate event responses)
CREATE TABLE ops_agent_reactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_pattern TEXT NOT NULL,
  reaction_type TEXT NOT NULL,      -- notify, log, webhook
  config JSONB,
  enabled BOOLEAN DEFAULT true
);

-- Action run log
CREATE TABLE ops_action_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_name TEXT NOT NULL,
  action_type TEXT NOT NULL,
  input JSONB,
  output JSONB,
  cost NUMERIC,
  duration_ms INT,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

### RLS policies for agent scoping

```sql
-- Each agent can only read/write its own data
ALTER TABLE ops_missions ENABLE ROW LEVEL SECURITY;

CREATE POLICY agent_own_missions ON ops_missions
  FOR ALL USING (agent_name = current_setting('app.agent_name'));
```

### Common pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Race condition: VPS + Vercel both execute | Duplicate actions | Single executor (VPS only) |
| Triggers bypass approval | Unapproved actions running | Route ALL through `createProposalAndMaybeAutoApprove` |
| Queue grows when quota full | Backlog of stale proposals | Cap gates: reject at proposal entry point |
| Stale steps | Steps stuck in "running" forever | `recoverStaleSteps` cron (30min threshold) |

## Vercel Integration

### Dashboard for monitoring agents

Vercel serves as a monitoring/approval dashboard while OpenClaw (VPS) handles execution:

```
Vercel (Next.js app)
├── /dashboard         — Agent status, active missions
├── /proposals         — Pending proposals for human review
├── /missions          — Mission history and details
├── /events            — Event stream / audit log
└── /settings          — Policy rules, trigger config
```

All data comes from Supabase — Vercel never executes agent actions.

### API routes for agent interaction

```typescript
// /api/proposals/approve (Vercel serverless)
export async function POST(req: Request) {
  const { proposalId } = await req.json();
  await supabase
    .from('ops_mission_proposals')
    .update({ status: 'approved' })
    .eq('id', proposalId);
  // OpenClaw picks up approved proposals via cron
}
```

## n8n Workflow Integration

### Failure forensics automation

```yaml
- name: "n8n-failure-forensics"
  schedule: "*/15 * * * *"
  prompt: >
    Check n8n for failed workflows in last 15 minutes.
    For each failure: 1) Identify the failing node
    2) Read error message and recent execution data
    3) Determine if it's a transient error (retry) or
    persistent issue (needs fix). 4) Auto-retry transients.
    5) Create issue for persistent failures.
```

### Connecting OpenClaw to n8n

```json
// n8n webhook → OpenClaw
{
  "gateway": {
    "webhooks": {
      "n8n-failure": {
        "path": "/webhooks/n8n-failure",
        "handler": "process-n8n-failure"
      }
    }
  }
}
```

## Messaging Platforms

### Telegram setup

```bash
# 1. Create bot via @BotFather in Telegram
# 2. Get bot token
# 3. Configure in openclaw.json
```

```json
{
  "messaging": {
    "telegram": {
      "botToken": "${TELEGRAM_BOT_TOKEN}",
      "allowedUsers": ["your_telegram_user_id"],
      "defaultChat": "your_chat_id"
    }
  }
}
```

### Sending alerts from cron jobs

Reference Telegram in cron prompts:
```yaml
- name: "alert-example"
  schedule: "0 * * * *"
  prompt: >
    Check for critical issues. If found, send alert via Telegram
    with: severity, description, and suggested action.
```

### WhatsApp setup

```bash
# Interactive setup
openclaw configure --section channels
# Select WhatsApp — links to your personal WhatsApp (shows QR code)

# Or via CLI
openclaw config set whatsapp.enabled true
```

WhatsApp allowlist for multi-user (family/team):
```json
{
  "channels": {
    "whatsapp": {
      "allowFrom": ["+1yourphonenumber", "+1trustedperson"]
    }
  }
}
```

**Note**: OpenClaw may strip `allowFrom` on restart — use the config-guard pattern (see [security.md](security.md#config-guard-pattern)) to auto-restore.

### Agent bindings (multi-agent message routing)

Route different senders to different agents:

```json
{
  "bindings": [
    {
      "agentId": "main",
      "match": { "channel": "whatsapp", "peer": { "id": "+1yournumber" } }
    },
    {
      "agentId": "shared",
      "match": { "channel": "whatsapp", "peer": { "id": "+1trustedperson" } }
    },
    {
      "agentId": "main",
      "match": { "channel": "telegram", "peer": { "id": "your_telegram_id" } }
    }
  ]
}
```

The "shared" agent gets a separate workspace with no access to personal files — this is the multi-agent privacy model.

### eSIM phone number for agent ("SuperAgent")

Give the agent its own real phone number using an eSIM provider (e.g., Tello, ~$5/mo):

- Agent can make/receive calls and texts independently
- Handle MFA codes, make reservations, manage appointments
- Not bound by virtual VoIP firewalls (real carrier number)
- Useful for: true personal assistant, small business agent, outward-facing customer agent

## Content & Marketing Stack

### Multi-agent content pipeline

```
Oracle (SEO) → Flash (Content) → Alfred (Strategy) → Publish
    ↓                ↓                    ↓
  Keywords      Draft posts          Schedule/approve
  Research      Adapt per platform   Track engagement
```

### Shared brain for content agents

```
shared/
├── brand-voice.md          # Tone, style, dos/don'ts
├── content-calendar.md     # What's planned and when
├── audience-insights.md    # Who we're writing for
├── hashtag-library.md      # Curated hashtags by topic
└── competitor-notes.md     # What competitors are saying
```

### Cron schedule for content (example)

```yaml
# 5am: Research trending topics
- name: "content-research"
  schedule: "0 5 * * 1-5"
  prompt: "Research trending topics in [niche]. Save to shared/trends-today.md"

# 7am: Draft posts
- name: "content-draft"
  schedule: "0 7 * * 1-5"
  prompt: "Draft today's posts based on content calendar and trends. Save to drafts/"

# 9am: Review and schedule
- name: "content-review"
  schedule: "0 9 * * 1-5"
  prompt: "Review drafts in drafts/. Apply brand voice. Schedule approved posts."

# 11am: Engagement monitoring
- name: "content-engage"
  schedule: "0 11 * * 1-5"
  prompt: "Check engagement on recent posts. Reply to comments. Update analytics."
```
