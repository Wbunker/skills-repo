---
name: monitoring-expert
description: Monitoring expertise covering strategy, alerting design, on-call operations, metrics, graphing, logging, distributed tracing, and business/security monitoring. Use when designing monitoring systems, building alert policies, choosing metrics frameworks, setting up dashboards, improving on-call processes, or instrumenting services. Based on Mike Julian's "Practical Monitoring" (O'Reilly, 2018).
---

# Monitoring Expert

Based on:
- "Practical Monitoring" by Mike Julian (O'Reilly, 2018)
- "Effective Monitoring and Alerting" by Slawek Ligus (O'Reilly, 2012)

## The Monitoring Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                      MONITORING SYSTEM                           │
│                                                                  │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐    │
│   │   METRICS   │  │   LOGGING   │  │      TRACING        │    │
│   │             │  │             │  │                     │    │
│   │ Time-series │  │ Structured  │  │ Distributed spans   │    │
│   │ Counters    │  │ Event logs  │  │ Request context     │    │
│   │ Gauges      │  │ Error logs  │  │ Causality chains    │    │
│   │ Histograms  │  │ Audit logs  │  │                     │    │
│   └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘    │
│          │                │                     │               │
│          └────────────────┼─────────────────────┘               │
│                           ▼                                      │
│              ┌────────────────────────┐                         │
│              │   ALERTING LAYER        │                         │
│              │  Symptom-based rules   │                         │
│              │  Thresholds + routing  │                         │
│              └───────────┬────────────┘                         │
│                          │                                       │
│              ┌───────────▼────────────┐                         │
│              │   VISUALIZATION         │                         │
│              │  Dashboards · Graphs   │                         │
│              │  Anomaly detection     │                         │
│              └────────────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Reference

| Task | Reference |
|------|-----------|
| What monitoring is, simplicity principles, building a strategy | [foundations.md](references/foundations.md) |
| Alert design, notification routing, reducing alert fatigue | [alerting.md](references/alerting.md) |
| On-call processes, runbooks, escalation, postmortems | [on-call.md](references/on-call.md) |
| Metrics collection, graphing, dashboards, anomaly classification | [metrics-graphing.md](references/metrics-graphing.md) |
| StatsD instrumentation, application metrics, tagging | [instrumentation.md](references/instrumentation.md) |
| Structured logging, log levels, log management pipelines | [logging.md](references/logging.md) |
| Distributed tracing, microservices, service maps | [distributed-systems.md](references/distributed-systems.md) |
| Business KPI monitoring, SLOs, SLAs, customer-facing metrics | [business-monitoring.md](references/business-monitoring.md) |
| Security monitoring, anomaly detection, audit logging | [security-monitoring.md](references/security-monitoring.md) |
| Measuring alert precision/recall/F-measure, detectability, feedback loop | [alert-quality.md](references/alert-quality.md) |
| Large-scale alerting, dynamic thresholds, admission control, automation | [at-scale.md](references/at-scale.md) |

## Reference Files

| File | Source | Topics |
|------|--------|--------|
| `foundations.md` | Julian 1–3 | Monitoring definition, anti-patterns, simplicity, monitoring strategy, tool selection |
| `alerting.md` | Julian 4, 7 | Alert design principles, symptom vs. cause alerting, thresholds, notification routing |
| `on-call.md` | Julian 5 | On-call schedules, escalation policies, runbooks, incident response, postmortems |
| `metrics-graphing.md` | Julian 6, Ligus 2 | Metric types, graphing, dashboards, anomaly classification, causality, flow/stock/availability |
| `instrumentation.md` | Julian 8 | StatsD protocol, counters/gauges/timers, tagging conventions, client libraries |
| `logging.md` | Julian 9 | Log levels, structured logging, log pipelines, retention, search and alerting on logs |
| `distributed-systems.md` | Julian 10 | Distributed tracing, trace context propagation, service dependency maps, microservice monitoring |
| `business-monitoring.md` | Julian 11 | Business metrics, SLOs/SLAs, customer-impacting indicators, executive dashboards |
| `security-monitoring.md` | Julian 12 | Security event monitoring, anomaly detection, audit trails, SIEM concepts |
| `alert-quality.md` | Ligus 6–7 | Precision, recall, F-measure, detectability, MTTD, false positive budget, feedback loop |
| `at-scale.md` | Ligus 4–5 | Large-scale alerting, namespacing, dynamic thresholds, breach/clear delays, admission control, automation ironies |

## Core Decision Trees

### What Should You Monitor First?

```
What are you trying to understand?
├── "Is my system up and working?" → Synthetic checks + golden signals
│   ├── Latency (how long requests take)
│   ├── Traffic (how much demand)
│   ├── Errors (rate of failures)
│   └── Saturation (how "full" the service is)
├── "Why is my system slow?" → Distributed tracing
│   ├── Find the bottleneck span → distributed-systems.md
│   └── Correlate with metrics → metrics-graphing.md
├── "What just happened?" → Logging
│   ├── Application error logs → logging.md
│   └── Audit / access logs → security-monitoring.md
├── "Are users impacted?" → Business metrics
│   └── Customer-facing SLOs → business-monitoring.md
└── "Is something attacking us?" → Security monitoring
    └── Anomaly detection + audit logs → security-monitoring.md
```

### Alert or Not?

```
Should this condition produce an alert?
├── Is a human action required right now? → YES → Page
├── Is a human action required soon? → YES → Ticket/low-priority alert
├── Is it a symptom (user-visible)? → YES → Alert
├── Is it only a cause (internal state)? → Consider NOT alerting
│   └── Let the symptom surface it
└── Is it informational only? → Dashboard / log only, no alert
```

### Pick a Metrics Method

```
What type of system are you instrumenting?
├── Infrastructure (host/VM/container)
│   └── USE Method: Utilization · Saturation · Errors
├── Service / API endpoint
│   └── RED Method: Rate · Errors · Duration
├── Any Google SRE-style service
│   └── Four Golden Signals: Latency · Traffic · Errors · Saturation
└── Business process
    └── Custom KPIs tied to user outcomes → business-monitoring.md
```

## Key Principles (Julian's Framework)

### Monitoring Is a Practice, Not a Tool

No single tool solves monitoring. Monitoring is the ongoing practice of:
1. Deciding **what** to measure
2. Deciding **when** to alert
3. Deciding **who** to notify and **how**
4. Acting on what you learn

### Symptom-Based Alerting

Alert on **symptoms** (what users experience), not **causes** (internal state):
- Bad: alert when CPU > 80%
- Good: alert when error rate > 1% or latency p99 > 500ms

Causes are infinite and unpredictable. Symptoms are what actually matter to users.

### Keep It Simple

Monitoring complexity is itself a failure mode. Prefer:
- Fewer, higher-signal alerts over many noisy ones
- Simple threshold alerts before complex ML-based anomaly detection
- Dashboards that answer a specific question over dashboards that show everything

### The Monitoring Hierarchy

```
Business outcomes (most important)
        ↑
User-facing symptoms
        ↑
Service-level indicators
        ↑
Infrastructure metrics (least important for alerting)
```

Alert higher in the hierarchy; use lower-level metrics for debugging.
