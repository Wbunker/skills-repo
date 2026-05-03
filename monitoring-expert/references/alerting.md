# Alerting Design
## Chapters 4 & 7: Alert Design Principles, Thresholds, Notification Routing

---

## The Purpose of an Alert

An alert exists to trigger a human action. If no action is required, the alert should not exist — it should be a dashboard entry or log event instead.

**Julian's test:** For every alert, ask "What do I do when this fires?" If the answer is "nothing" or "look at it," delete the alert.

---

## Symptom-Based vs. Cause-Based Alerting

This is Julian's most emphasized principle.

### Cause-Based Alerting (Avoid)

Alerts on internal system state:
- CPU utilization > 80%
- Disk I/O wait > 20%
- Memory usage > 90%
- Connection pool at 80% capacity

**Problem:** These causes may or may not result in user impact. A busy CPU with no latency increase is not an emergency. Alerting on causes leads to:
- High alert volume with low actionability
- Responders learning to ignore alerts
- On-call burnout

### Symptom-Based Alerting (Prefer)

Alerts on observable user impact:
- Error rate > 1% for the past 5 minutes
- p99 latency > 2 seconds for the past 3 minutes
- Successful checkout rate dropped > 10% vs. baseline
- No successful health check responses for 2 minutes

**Principle:** Causes are infinite and often unpredictable. Symptoms are finite and directly tied to what users experience. Alert on symptoms; use cause-based metrics for debugging after the alert fires.

### When Cause-Based Alerts Are Appropriate

Cause-based alerts are justified when:
- The cause reliably predicts a symptom with sufficient lead time to act preventively
- The action is well-defined and different from symptom response (e.g., capacity pre-provisioning)
- It is technically impossible to measure the symptom directly (e.g., pre-production systems)

---

## Alert Design Framework

Every alert should have answers to all five:

| Element | Description | Example |
|---------|-------------|---------|
| **Condition** | What triggers the alert | p99 latency > 500ms |
| **Window** | How long condition must hold | For 5 consecutive minutes |
| **Severity** | Urgency and escalation tier | Critical (page immediately) |
| **Owner** | Who is responsible to respond | payments-team on-call |
| **Runbook** | What to do when it fires | Link to runbook |

### Severity Tiers

| Severity | Meaning | Notification Method |
|----------|---------|---------------------|
| **Critical** | User impact occurring now; requires immediate action | Page (wake from sleep) |
| **Warning** | Degradation detected; action required within hours | Ticket or Slack |
| **Info** | Noteworthy event; no action required | Dashboard / log only |

Avoid having more than two severity levels that produce pages. "Warning pages" become ignored.

---

## Threshold Design

### Static Thresholds

Simplest form: alert when metric crosses a fixed value.

Best practices:
- Set thresholds based on measured baselines, not guesses
- Include a minimum window to avoid flapping (e.g., "for 5 minutes" not instantaneous)
- Prefer percentile-based thresholds (p95, p99) over averages for latency
- Document why the threshold is set where it is

### Avoiding False Positives

False positives erode trust in the alerting system. Common causes:
- Threshold too tight relative to natural variance
- Window too short (catching momentary spikes)
- No distinction between transient and sustained conditions

**Remediation:** When an alert fires and requires no action three times in a row, it is broken. Either raise the threshold, add a longer window, or delete it.

### Avoiding False Negatives

Alerts that should fire but don't. Common causes:
- Symptom measured at wrong percentile (p50 fine, p99 terrible)
- Threshold too loose
- Metric not capturing actual user experience

**Test for false negatives:** After every incident, ask "did our monitoring catch this?" If not, what alert would have caught it earlier?

### Percentiles vs. Averages

Averages hide tail latency. Use percentiles for user-facing latency:

```
Example: 1000 requests in a minute
  - 950 complete in 100ms
  - 49 complete in 500ms
  - 1 completes in 30,000ms

  Average: ~129ms (looks fine)
  p95:     ~500ms (elevated)
  p99:     30,000ms (terrible)
  p999:    30,000ms
```

Alert on p95 and p99, not average. Executives want average; SREs want percentiles.

---

## Alert Fatigue

Alert fatigue is the desensitization that occurs when on-call responders receive too many low-value alerts.

### Measuring Alert Fatigue

Track:
- **Alert volume per on-call shift** — how many alerts fired?
- **Actionability rate** — what fraction required a meaningful action?
- **MTTA (Mean Time to Acknowledge)** — rising MTTA indicates responders are deprioritizing alerts
- **No-action closes** — what fraction were closed without action?

Target: > 90% of pages should require a human action.

### Reducing Alert Fatigue

1. **Audit and delete** — remove any alert that hasn't fired meaningfully in 30 days, or that fires but requires no action
2. **Merge related alerts** — many low-level alerts may be symptoms of one higher-level condition
3. **Shift from cause to symptom** — consolidates many cause alerts into fewer symptom alerts
4. **Raise thresholds** — if alerts fire too often for minor conditions, raise the bar
5. **Add runbooks** — alerts without runbooks create confusion that leads to faster dismissal

---

## Notification Routing

### Routing Principles

- **Right person** — the person best positioned to respond, not the person who happens to be available
- **Right time** — immediately for critical, async for warning
- **Right channel** — phone call/SMS for critical; Slack/ticket for warning

### Escalation Policy

```
Alert fires
    │
    ▼ notify primary on-call
Wait N minutes (typically 5–15)
    │
    ├── Acknowledged? → Responder takes action
    └── Not acknowledged?
            │
            ▼ notify secondary on-call
        Wait N more minutes
            │
            ├── Acknowledged? → Responder takes action
            └── Not acknowledged?
                    │
                    ▼ notify manager / incident commander
```

### Silencing and Inhibition

During maintenance windows or known degraded states, alerts should be silenced to prevent noise. Two mechanisms:

- **Silences** — suppress matching alerts for a time window (scheduled maintenance)
- **Inhibitions** — suppress child alerts when a parent alert is active (if datacenter is down, don't page for each service in it)

**Practice:** Always create a silence before planned maintenance. Alerts firing during known maintenance train responders to ignore alerts.

---

## Alerting on Metrics (Chapter 7 content)

### Rate of Change Alerts

Sometimes the direction of change matters more than absolute value:
- Disk filling up 5x faster than usual → alert sooner than crossing a static threshold
- Error rate spiking from 0.01% to 1% → the magnitude of increase matters

Use rate-of-change or derivative functions for capacity and traffic anomalies.

### Composite Alerts

Alert when multiple conditions are simultaneously true:
- Error rate > 1% AND traffic is not near zero (avoids alerting during low-traffic quiet periods)
- Latency p99 > 1s AND deploy happened in last 30 minutes (scopes investigation)

Composite alerts reduce false positives in cases where context matters.

### SLO-Based Alerting

Alert on error budget burn rate rather than raw error rate:
- If you have a 99.9% uptime SLO and you're burning your monthly error budget in hours → critical
- If burn rate is elevated but within acceptable range → warning

This ties alerts directly to business commitments. See [business-monitoring.md](business-monitoring.md) for SLO/SLA detail.
