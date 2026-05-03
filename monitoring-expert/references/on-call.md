# On-Call Operations
## Chapter 5: On-Call Schedules, Escalation, Runbooks, Incident Response, Postmortems

---

## On-Call Is a Practice, Not a Punishment

On-call is the operational contract by which a team commits to responding to production issues. Done poorly, it burns out engineers. Done well, it creates ownership, feedback loops, and operational knowledge.

**Julian's premise:** On-call should be sustainable. If it isn't, the monitoring and system design is broken — not the engineers.

---

## On-Call Fundamentals

### Who Should Be On-Call

- The people who built and own the system (not a separate ops team)
- Team members with sufficient context to diagnose and act
- Rotation must be large enough that no individual is on-call more than 25% of the time (recommended: ≥ 4 people per rotation)

### What On-Call Requires

Before putting someone on-call, ensure they have:
- Access to all systems they may need to touch
- Runbooks for all critical alert paths
- Escalation contacts for issues beyond their authority
- A tested communication path (can they receive pages?)

### On-Call Schedule Patterns

| Pattern | When to Use |
|---------|------------|
| **Follow-the-sun** | Geographically distributed teams; each region covers its business hours |
| **Weekly rotation** | Simplest; one person owns a full week |
| **Daily rotation** | More frequent handoffs; reduces per-person burden |
| **Primary + secondary** | Primary handles first response; secondary handles escalations |

Handoffs must include: active incidents, recent deploys, known issues, changes in progress.

---

## Runbooks

A runbook is the documented procedure for responding to an alert. It should exist before the alert is deployed.

### Minimum Runbook Content

1. **Alert name and severity** — what fired and how urgent
2. **What it means** — plain-language description of the condition
3. **Impact** — who/what is affected if this is a real problem
4. **Investigation steps** — where to look, what to check, in what order
5. **Remediation options** — common fixes; who has authority to apply them
6. **Escalation path** — who to contact if standard steps don't resolve it
7. **Links** — relevant dashboards, logs, code, deployment system

### Runbook Anti-Patterns

- **Too long** — responders skip past relevant sections under stress
- **Outdated** — runbooks that don't reflect current architecture mislead responders
- **Vague** — "check the logs" without specifying which logs or what to look for
- **Missing escalation** — leaves responders stuck when standard fixes don't work

**Practice:** Review runbooks after every incident. Update within 48 hours of any system change that affects response procedures.

### Runbook Template

```markdown
## Alert: [Alert Name]
**Severity:** Critical / Warning
**Owner:** [Team Name]

### What This Means
[Plain-language description of the condition]

### Potential Impact
[Who is affected; what functionality is degraded]

### Investigation
1. Check [dashboard link] for [specific indicators]
2. Look at [log location] for [specific patterns]
3. Verify [deployment/config change] has not occurred

### Common Causes and Fixes
- **[Cause 1]**: [Fix / command / rollback step]
- **[Cause 2]**: [Fix / command / rollback step]

### Escalation
- If unresolved in 15 minutes: contact [Name] via [channel]
- If service is down: invoke incident response process

### References
- Dashboard: [link]
- Logs: [link]
- Codebase: [link]
```

---

## Incident Response

### Incident Severity Levels

| Level | Definition | Example |
|-------|-----------|---------|
| **SEV-1** | Complete outage or severe degradation of a critical service | Checkout unavailable |
| **SEV-2** | Partial outage or degraded performance affecting many users | Latency 10x normal |
| **SEV-3** | Minor degradation; workaround available | One report type failing |
| **SEV-4** | No user impact; investigation needed | Elevated error log rate |

### Incident Roles

**Incident Commander (IC)**
- Owns communication and coordination
- Does not do technical work during the incident
- Declares severity; calls all-hands if needed
- Produces status updates on defined cadence

**Technical Lead**
- Diagnoses the problem
- Coordinates fixes
- Reports status to IC

**Communication Lead** (for major incidents)
- Updates status page
- Sends internal and external communications
- Keeps stakeholder noise away from technical responders

### Incident Response Checklist

- [ ] Severity declared
- [ ] Incident Commander assigned
- [ ] Communication channel opened (dedicated Slack channel, bridge line)
- [ ] Initial status communicated to stakeholders
- [ ] Runbook consulted
- [ ] Hypothesis formed; investigation underway
- [ ] No unnecessary changes made during active incident
- [ ] Mitigation applied; monitoring to confirm recovery
- [ ] All-clear declared; incident closed
- [ ] Postmortem scheduled

**Key rule:** Do not make changes during an incident without understanding the likely impact. One bad change can turn a partial outage into a total one.

---

## Postmortems

A postmortem is a structured review after an incident to understand what happened, why, and how to prevent recurrence. It is not a blame session.

### Blameless Postmortem Principles

- Assume engineers made the best decisions available given what they knew at the time
- Focus on **systemic causes**, not individual mistakes
- A good postmortem produces system improvements, not performance reviews

### Postmortem Template

```markdown
## Incident Postmortem: [Incident Name / ID]
**Date:** [Date of incident]
**Duration:** [Start time] to [End time] ([total duration])
**Severity:** SEV-[1-4]
**Impact:** [Users affected, revenue impact, SLA impact]

### Summary
[2-4 sentence description of what happened]

### Timeline
[Chronological events with timestamps]
- HH:MM — [Event]
- HH:MM — [Event]

### Root Cause
[Primary technical cause; trace the causal chain]

### Contributing Factors
[Secondary causes, process gaps, tooling failures]

### Detection
[How was the incident detected? How long between start and detection?]

### Resolution
[What fixed it? How long to mitigate?]

### Action Items
| Item | Owner | Due Date |
|------|-------|----------|
| [Action] | [Name] | [Date] |

### Lessons Learned
[What worked well? What didn't?]
```

### Postmortem Follow-Through

The most common postmortem failure is action item rot — items are identified but never completed. Practices to prevent this:
- Assign every action item a single named owner (not a team)
- Set a deadline at time of writing
- Track completion in the same system as other engineering work
- Review outstanding postmortem items at regular team meetings

---

## On-Call Health Metrics

Track these to identify when on-call is unsustainable:

| Metric | Healthy Target |
|--------|---------------|
| Pages per shift | < 5 (actionable only) |
| Pages outside business hours | Track trend; goal is minimizing |
| Mean Time to Acknowledge (MTTA) | < 5 minutes for critical |
| Mean Time to Resolve (MTTR) | Track trend |
| Incidents requiring escalation | Track; high rate → runbook gaps |
| Postmortem action items completed on time | > 80% |

If any metric is trending negatively, treat it as a system design problem, not a people problem.
