# Automation & Cron

Cron jobs, automation patterns, and production recipes across dev, business, and operations.

## Table of Contents

- [Cron System](#cron-system)
- [Core Cron Jobs](#core-cron-jobs)
- [Developer Automations](#developer-automations)
- [Business Automations](#business-automations)
- [Monitoring Automations](#monitoring-automations)
- [Life Admin Automations](#life-admin-automations)
- [Meta Automations](#meta-automations)
- [Automation Design Patterns](#automation-design-patterns)

---

## Cron System

### Configuration

```json
// openclaw.json
{
  "cron": {
    "enabled": true,
    "timezone": "America/New_York"
  }
}
```

### Cron job format

```yaml
# ~/.openclaw/cron/jobs.yaml
- name: "morning-brief"
  schedule: "0 8 * * *"           # 8am daily
  prompt: >
    Prepare the morning briefing: calendar, priorities, overnight alerts.
    Save to daily/$(date +%Y-%m-%d)-brief.md. Keep under 200 words.

- name: "day-wrap"
  schedule: "0 23 * * *"          # 11pm daily
  prompt: >
    Summarize today's activity. Update memory/$(date +%Y-%m-%d).md
    and flag anything that needs follow-up tomorrow.
```

### Cron schedule reference

| Pattern | Meaning |
|---------|---------|
| `0 8 * * *` | Daily at 8am |
| `0 8 * * 1-5` | Weekdays at 8am |
| `*/30 * * * *` | Every 30 minutes |
| `0 */4 * * *` | Every 4 hours |
| `0 9 * * 1` | Mondays at 9am |
| `0 3 1 * *` | First of month at 3am |

## Core Cron Jobs

### Recommended daily schedule

```yaml
- name: "morning-brief"
  schedule: "0 8 * * 1-5"
  prompt: "Morning briefing: calendar, top priorities, overnight alerts. Under 200 words."

- name: "brief-update"
  schedule: "0 13 * * 1-5"
  prompt: "Midday update: progress on morning priorities, new items, blockers."

- name: "meeting-sync"
  schedule: "*/15 9-17 * * 1-5"
  prompt: "Check calendar for meetings in next 15 min. Prepare context if any."

- name: "day-wrap"
  schedule: "0 23 * * *"
  prompt: "End of day: summarize activity, update daily log, flag tomorrow items."

- name: "heartbeat"
  schedule: "0 */6 * * *"
  prompt: "Run HEARTBEAT.md checklist. Report any failures."

- name: "weekly-compaction"
  schedule: "0 2 * * 0"
  prompt: "Compact memory: archive old daily logs, update MEMORY.md, prune."
```

### HEARTBEAT.md (self-healing)

```markdown
# Heartbeat Checklist

Run every 6 hours. For each item, check and report status.

- [ ] API key is valid (test with a simple call)
- [ ] Disk space > 20% free
- [ ] All agent processes running
- [ ] No error spikes in last 6 hours
- [ ] Memory files not corrupt
- [ ] Cron jobs executed on schedule
- [ ] Telegram bot responsive

If any check fails: attempt auto-fix, then alert via Telegram.
```

## Developer Automations

### Overnight Claude Code babysitter

```yaml
- name: "overnight-code-review"
  schedule: "0 6 * * 1-5"
  prompt: >
    Check the Claude Code session from last night. Review:
    1) Did the task complete? 2) Any errors in output?
    3) Are tests passing? 4) Code quality concerns?
    Save report to reports/overnight-$(date +%Y-%m-%d).md
```

### Context-aware PR reviewer

```yaml
- name: "pr-review"
  schedule: "*/30 9-18 * * 1-5"
  prompt: >
    Check GitHub for new PRs on [repo]. For each unreviewed PR:
    1) Read the diff 2) Check for security issues, bugs, style
    3) Post a review comment. Focus on: correctness, security,
    performance. Skip nitpicks.
```

### Dependency triage

```yaml
- name: "dependency-check"
  schedule: "0 9 * * 1"
  prompt: >
    Run dependency audit on the project. Categorize updates:
    CRITICAL (security), IMPORTANT (major version), ROUTINE (minor/patch).
    Create GitHub issues for CRITICAL. Report summary.
```

### Post-deploy sanity checker

```yaml
- name: "post-deploy"
  schedule: "on-event: deploy-complete"
  prompt: >
    Deployment detected. Run sanity checks: 1) Health endpoint returns 200
    2) Key API routes respond 3) No error spike in logs (last 5 min)
    4) Database migrations applied. Report pass/fail with details.
```

## Business Automations

### Client onboarding autopilot

```yaml
- name: "client-onboard"
  schedule: "on-event: new-client"
  prompt: >
    New client detected in CRM. Execute onboarding:
    1) Create project folder from template
    2) Send welcome email sequence
    3) Schedule kickoff meeting
    4) Create project tasks in tracker
    5) Notify team lead
```

### Invoice chaser

```yaml
- name: "invoice-chase"
  schedule: "0 10 * * 1-5"
  prompt: >
    Check invoices: 1) Any overdue > 7 days? Send polite reminder.
    2) Any overdue > 30 days? Escalate to user with draft firm email.
    3) Log all actions to finance/invoice-log.md.
```

### Payment recovery

```yaml
- name: "payment-recovery"
  schedule: "0 9 * * *"
  prompt: >
    Check Stripe for failed payments in last 24h.
    For each: 1) Identify failure reason 2) Draft appropriate
    recovery email (card expired, insufficient funds, etc.)
    3) Queue for sending after user approval.
```

### Lead qualification

```yaml
- name: "lead-qual"
  schedule: "*/30 9-18 * * 1-5"
  prompt: >
    Check inbound form submissions. For each lead:
    1) Score based on criteria (budget, timeline, fit)
    2) Research the company (size, industry, tech stack)
    3) Draft personalized response
    4) Route: hot leads → immediate alert, warm → queue, cold → nurture
```

### Competitor price monitor

```yaml
- name: "competitor-watch"
  schedule: "0 7 * * 1,4"
  prompt: >
    Check competitor pricing pages for changes.
    Compare against our pricing. Flag any significant changes.
    Save report to reports/competitive-pricing-$(date +%Y-%m-%d).md
```

## Monitoring Automations

### Error spike detector

```yaml
- name: "error-monitor"
  schedule: "*/15 * * * *"
  prompt: >
    Check application logs for error rate. If errors in last 15 min
    exceed 2x the daily average: 1) Identify error patterns
    2) Attempt root cause analysis 3) Alert via Telegram with
    summary and suggested fix. Include: error count, top error
    messages, affected endpoints.
```

### Morning stack health report

```yaml
- name: "stack-health"
  schedule: "0 7 * * *"
  prompt: >
    Full stack health check: 1) All services responding
    2) Database connections healthy 3) SSL certificates valid (warn if < 30 days)
    4) Disk usage 5) Memory usage 6) API rate limits status
    7) Backup freshness. Generate health scorecard.
```

## Life Admin Automations

### Receipt scanner → expense categorizer

```yaml
- name: "receipt-scan"
  schedule: "0 20 * * *"
  prompt: >
    Check inbox/receipts/ for new receipt images. For each:
    1) Extract: vendor, amount, date, category
    2) Append to finance/expenses-$(date +%Y-%m).csv
    3) Flag any expense over $500 for review
    4) Move processed receipts to inbox/receipts/processed/
```

### Relationship CRM

```yaml
- name: "relationship-check"
  schedule: "0 9 * * 1"
  prompt: >
    Review contacts in user/contacts.md. Flag anyone not contacted
    in 30+ days. Draft brief check-in messages for top 5 priority
    contacts. Save drafts to drafts/check-ins/.
```

### Subscription auditor

```yaml
- name: "subscription-audit"
  schedule: "0 10 1 * *"
  prompt: >
    Monthly subscription audit: 1) List all active subscriptions
    from finance/subscriptions.md 2) Check usage for each
    3) Flag unused or underused subscriptions 4) Calculate
    total monthly spend 5) Recommend cancellations.
```

## Meta Automations

### Self-monitoring OpenClaw

```yaml
- name: "self-monitor"
  schedule: "0 * * * *"
  prompt: >
    Self-check: 1) Today's total API cost so far
    2) Number of cron jobs that ran vs expected
    3) Any failed tasks? 4) Memory file sizes (warn if MEMORY.md > 200 lines)
    5) Agent uptime. Log to monitoring/hourly-$(date +%Y-%m-%d).md
```

### GitHub issue auto-triage

```yaml
- name: "issue-triage"
  schedule: "*/30 9-18 * * 1-5"
  prompt: >
    Check GitHub for new unlabeled issues. For each:
    1) Classify: bug, feature, question, docs
    2) Estimate priority: P0 (critical), P1 (important), P2 (nice-to-have)
    3) Apply labels 4) If P0, alert via Telegram immediately
    5) If question, draft a helpful response
```

### Codebase docs updater

```yaml
- name: "docs-update"
  schedule: "0 3 * * 0"
  prompt: >
    Review recent commits (last 7 days). Check if any changes
    affect documented APIs or features. Update relevant docs.
    Create PR with changes if any docs are outdated.
```

### .env leak panic button

```yaml
- name: "env-leak-check"
  schedule: "0 */6 * * *"
  prompt: >
    Scan workspace for exposed secrets: 1) Check .env files are gitignored
    2) Search recent commits for API keys/tokens 3) Check if any
    secrets are in public files. If found: IMMEDIATELY alert user
    and provide rotation instructions.
```

## Automation Design Patterns

### Prompt engineering for cron jobs

1. **Be specific** — "Check Stripe for failed payments" not "Check payments"
2. **Define output** — "Save to reports/[name].md" or "Alert via Telegram"
3. **Set boundaries** — "Keep under 200 words" or "Max 5 items"
4. **Include failure handling** — "If API unreachable, retry in 30 min then alert"
5. **Avoid overlap** — Don't have multiple jobs checking the same thing

### Cron job naming conventions

```
[frequency]-[domain]-[action]
Examples:
  daily-finance-invoice-check
  hourly-monitor-error-spike
  weekly-content-calendar-review
  monthly-subscription-audit
```

### Cost control

- Stagger cron jobs (don't cluster all at the same minute)
- Use Sonnet for routine checks, Opus only for complex analysis
- Set daily budget caps and check in self-monitor job
- Batch related checks into a single job where possible
