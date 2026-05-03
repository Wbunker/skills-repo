# Monitoring Foundations
## Chapters 1–3: What Is Monitoring, Simplicity, Building a Strategy

---

## What Is Monitoring?

Monitoring is the process of collecting, aggregating, and displaying real-time quantitative data about a system to demonstrate the system's behavior over time and enable informed decisions.

**Julian's working definition:** Monitoring is the tools and processes you use to understand what is happening in your environment.

This encompasses four categories:
- **Metrics** — quantitative measurements over time
- **Logging** — discrete event records
- **Alerting** — automated notification when conditions are met
- **Visualization** — graphical representation for human understanding

### What Monitoring Is Not

| Misconception | Reality |
|---------------|---------|
| "Monitoring is just uptime checks" | Monitoring spans health, performance, behavior, and business outcomes |
| "A monitoring tool solves monitoring" | Tools enable monitoring; practice and discipline define it |
| "More monitoring is always better" | Monitoring complexity is itself a failure mode |
| "Monitoring is ops work" | Developers must instrument their code; monitoring is shared responsibility |
| "Alerting on everything important is safe" | Alert fatigue kills response quality; fewer, higher-signal alerts are better |

---

## Anti-Patterns to Avoid

### Monitoring-as-Checkbox

Organizations that treat monitoring as a compliance activity rather than an operational practice. Symptoms:
- Dashboards nobody looks at
- Alerts nobody responds to
- No runbooks
- Metrics collected but never acted on

### Tool Sprawl

Installing every monitoring tool available without integrating them. Each tool adds cognitive overhead; partial adoption of many tools beats full adoption of none.

### Alert Carpet-Bombing

Alerting on every metric available. Consequences:
- On-call responders become desensitized
- Real problems get buried in noise
- Alert fatigue causes incidents to be missed or ignored

**Principle:** Every alert that fires and requires no action is a broken alert.

### Cargo-Cult Monitoring

Copying another company's monitoring setup without understanding why. Their system has different scale, architecture, and failure modes than yours.

---

## Keeping Monitoring Simple

### The Complexity Tax

Every unit of monitoring complexity adds:
- Maintenance burden
- Cognitive load on responders
- Risk of the monitoring system itself failing

Complex monitoring setups fail in subtle ways: queries break, thresholds drift, dashboards rot, alerts stop firing. The monitoring system must be maintained.

### Simple Thresholds First

Start with static thresholds before dynamic/ML-based alerting. Static thresholds:
- Are easy to understand and explain
- Fail predictably
- Don't require training data

Anomaly detection and dynamic thresholds are appropriate only after you understand your system's normal behavior through static monitoring.

### The Minimum Viable Monitoring Stack

For most systems, the minimum useful setup is:
1. **Uptime check** — is the service responding?
2. **Error rate** — what fraction of requests are failing?
3. **Latency** — how long are requests taking (p50, p95, p99)?
4. **Saturation** — how full are key resources (CPU, memory, disk, queue depth)?

This covers the four golden signals and catches most user-impacting problems.

---

## Building a Monitoring Strategy

A monitoring strategy answers three questions before you write a single query:

1. **What matters?** — which behaviors, if degraded, would harm users or the business
2. **How will you know?** — what measurable signal indicates degradation
3. **What will you do?** — who is notified, and what action is expected

Without answers to all three, monitoring produces data without improving outcomes.

### Stakeholder Mapping

Different stakeholders need different views:
- **On-call engineers** — real-time operational status, actionable alerts
- **Development teams** — service-level performance, error rates, deployment impact
- **Management** — SLA compliance, business KPI trends, incident summary
- **Security** — access patterns, anomalies, audit events

One dashboard or alert set cannot serve all audiences.

### Defining What "Good" Looks Like

Before you can detect problems, you need a baseline. Establish:
- **Normal latency range** (p50, p95, p99)
- **Normal error rate** (e.g., < 0.1% for a mature API)
- **Expected traffic pattern** (hourly/daily/weekly shape)
- **Resource utilization ceilings** (e.g., CPU should not sustain > 70%)

Baselines should be re-established after major changes.

### Monitoring Strategy Checklist

- [ ] Key user journeys identified and covered with synthetic checks or real-user monitoring
- [ ] Four golden signals instrumented for all public-facing services
- [ ] Alerting covers symptoms, not only causes
- [ ] Every alert has a runbook
- [ ] On-call rotation defined with escalation policy
- [ ] Dashboards organized by audience (ops / dev / exec)
- [ ] Retention policy defined for metrics and logs
- [ ] Monitoring stack itself is monitored (meta-monitoring)

---

## Tool Selection Criteria

Julian does not prescribe specific tools — the landscape changes too quickly. Evaluate tools against:

| Criterion | Questions to Ask |
|-----------|-----------------|
| **Instrumentation effort** | How much code change is required? Are client libraries available in your languages? |
| **Data model** | Does it support tags/labels? Can you query by arbitrary dimensions? |
| **Query language** | Is it expressive enough for your needs? Can team members learn it? |
| **Alerting** | Does it support multi-condition alerts? Notification routing? Silencing? |
| **Retention** | What are the default and maximum retention periods? What are the costs? |
| **Operational overhead** | Is it SaaS or self-hosted? What is the failure mode if it goes down? |
| **Integration** | Does it work with your existing stack? Can it ingest from multiple sources? |

### The Monitoring Stack Layers

```
Layer               Examples
─────────────────────────────────────────────────────
Collection          StatsD, Prometheus exporters, Fluentd, agents
Storage             Prometheus TSDB, InfluxDB, Elasticsearch, S3
Processing/Query    PromQL, InfluxQL, Elasticsearch DSL
Visualization       Grafana, Kibana, Datadog dashboards
Alerting            Alertmanager, PagerDuty, OpsGenie
Notification        Email, Slack, SMS, phone call
```

Each layer can be mixed-and-matched. Don't couple to a single vendor's full stack unless the operational simplicity is worth the lock-in.

---

## Meta-Monitoring

The monitoring system itself must be monitored. Common failure modes:
- Metrics collection agent crashes silently → gaps in data
- Alert manager misconfigured → alerts fire but don't notify
- Storage fills up → old data lost or collection stops
- Dashboard queries break after schema changes

**Practice:** Set up a "heartbeat" alert — a synthetic condition that always fires, confirming the end-to-end notification path is working. If you stop receiving the heartbeat, the monitoring pipeline is broken.
