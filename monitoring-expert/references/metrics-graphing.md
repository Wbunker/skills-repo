# Metrics and Graphing
## Chapter 6 (Julian) + Chapter 2 (Ligus): Metric Types, Graphing, Anomaly Classification

---

## Metric Types

### Counter

A value that only increases (resets to zero on restart).

- Examples: total HTTP requests, total errors, total bytes sent
- Used to calculate rates: `requests per second = delta(counter) / time_window`
- Never alert on raw counter value; always compute the rate

### Gauge

A value that can go up or down, representing a current state.

- Examples: current memory usage, number of active connections, queue depth, CPU utilization
- Can be read directly — the current value is meaningful
- Appropriate for resource saturation metrics

### Histogram / Timer

A distribution of observations across buckets, representing how often values fall in each range.

- Examples: request latency distribution, response size distribution
- Enables percentile calculations (p50, p95, p99)
- More expensive to store than counters or gauges
- Prefer histograms for any user-facing latency measurement

### Summary

A client-side pre-computed set of quantiles (p50, p95, p99).

- Cheaper to query than histograms
- Cannot be aggregated across multiple instances (limitation vs. histograms)
- Use histograms when you need to aggregate across services or instances

---

## The Four Golden Signals (Google SRE)

The four metrics that matter most for any user-facing service:

| Signal | Definition | Metric Examples |
|--------|-----------|-----------------|
| **Latency** | Time to service a request | p50/p95/p99 response time; time to first byte |
| **Traffic** | Demand on the system | Requests per second; transactions per minute |
| **Errors** | Rate of failed requests | HTTP 5xx rate; application exception rate |
| **Saturation** | How "full" the service is | CPU %; memory %; queue depth; connection pool usage |

If you instrument nothing else, instrument these four for every service.

### USE Method (Infrastructure)

For resources (hosts, containers, databases):
- **Utilization** — average time the resource is busy (e.g., CPU 60% utilized)
- **Saturation** — extra work queued because resource is at capacity (e.g., run queue length)
- **Errors** — error events (e.g., disk I/O errors, network errors)

### RED Method (Services)

For services and APIs:
- **Rate** — requests per second
- **Errors** — errors per second (or error fraction)
- **Duration** — distribution of response times

---

## Graphing Best Practices

### Match Graph Type to Data Type

| Data Type | Graph Type | Why |
|-----------|-----------|-----|
| Rate over time (requests/sec) | Line graph | Shows trend and variation |
| Distribution (latency) | Heatmap or percentile lines | Reveals tail behavior |
| Composition (% of traffic by type) | Stacked area | Shows proportion changes |
| Single current value | Gauge / stat panel | Point-in-time status |
| Count comparison across categories | Bar chart | Comparison, not trend |

Avoid pie charts for operational metrics — they are poor for comparing values and detecting change.

### Latency: Show Percentiles, Not Averages

Always graph latency as percentile lines:

```
        p99  ─── ─ ─ ─ ─────────────
        p95  ─────────────
        p50  ──────────────────────
             └─────────────────────────▶ time
```

A single average latency line hides the tail experience of a significant fraction of users.

### Consistent Time Ranges

When investigating an incident, use the same time range across all dashboards. Mismatched time ranges cause false pattern matches.

### Baseline Overlays

Overlay current behavior against the same time window from the prior week or month. This immediately reveals whether "high" values are anomalous or routine.

---

## Dashboard Design

### Dashboard Hierarchy

Organize dashboards in layers:

```
1. Overview / Home
   Service health summary: is everything green?
   High-level business metrics

2. Service Dashboards (one per service)
   Four golden signals
   Key dependencies

3. Investigation Dashboards
   Deep-dive metrics for debugging
   Broken down by host, region, version, etc.
```

### Dashboard Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Everything on one dashboard | Overwhelming; nothing actionable | Layer dashboards by audience and purpose |
| Graphs without units | "200 — is that good or bad?" | Always label axes with units |
| Graphs without time context | Can't tell if a spike is recent or historical | Lock time range; add event overlays |
| Graphs showing fine-grained data for weeks | Resolution mismatch; trends invisible | Use appropriate rollup for the time window |
| No annotations for deploys/changes | Can't correlate events to metric changes | Annotate dashboards with deploy markers |

### The Dashboard Question Test

Every dashboard panel should answer a specific question. Write the question as the panel title:

- Instead of "Error Rate" → "Are error rates below 1% for all regions?"
- Instead of "Memory" → "Is memory within safe bounds (< 80%)?"
- Instead of "Latency" → "Is checkout latency below 500ms at p99?"

If you can't phrase a panel as a question, reconsider whether it belongs.

### Dashboard Audience Discipline

| Audience | Needs | Dashboard Design |
|----------|-------|-----------------|
| On-call engineer | Fast triage, drill-down path | Traffic-light status + drill links |
| Developer | Impact of recent changes | Annotated with deploy events |
| Management | SLA compliance, trends | Simple, fewer graphs, longer time windows |
| Customer success | Is the product working for users? | Business-level indicators, not system metrics |

Never send an ops dashboard to an executive. They will not know how to interpret it and will ask questions that don't need asking.

---

## Metric Naming Conventions

Consistent naming across services makes queries and dashboards maintainable.

### Recommended Pattern

```
<namespace>.<service>.<metric_name>.<unit>

Examples:
  http.api.request_duration.milliseconds
  db.postgres.query_duration.milliseconds
  queue.payments.depth.count
  cache.redis.hit_rate.ratio
```

### Tagging / Labels

Use tags to add dimensions without creating new metric names:

```
http.request.duration{service="checkout", region="us-east-1", status="200"}
```

Common tags:
- `service` / `app` — which service emitted the metric
- `env` — environment (production, staging)
- `region` — deployment region
- `host` / `instance` — specific host (use sparingly in aggregated views)
- `status` / `outcome` — success/error classification

**Warning:** High-cardinality tags (e.g., `user_id`, `request_id`) cause storage explosion. Never use unbounded values as tag keys.

---

## Retention and Resolution

Higher resolution (more data points) costs more storage. Set retention policies per metric type:

| Data Type | Recommended Retention |
|-----------|----------------------|
| Raw metrics (1-second resolution) | 24–48 hours |
| Rolled-up (1-minute resolution) | 30 days |
| Rolled-up (1-hour resolution) | 13 months |
| Daily rollups | Indefinitely |

Ensure your storage policy is set before production traffic; retroactive downsampling loses data.

---

## Anomaly Classification

Source: Ligus, Chapter 2

When a timeseries plot looks wrong, the shape of the anomaly guides diagnosis. Recognizing common anomaly patterns reduces investigation time.

### Flattening Effect

The metric stops changing — the line goes flat.

```
Normal:    ╱╲╱╲╱╲╱╲
Flattened: ╱╲╱╲────
```

**Causes:**
- Data collection stopped (agent crashed, network partition)
- Metric is saturated at a ceiling (counter overflowed, gauge pinned at max)
- Upstream data source went silent (no events to count)

**Key distinction:** A flat line at zero vs. a flat line at an elevated value. Zero usually means no data; elevated value may mean saturation.

### Warm-Up Effect

Metric starts low and gradually rises to its normal level after a restart or deploy.

```
         ────────────
        ╱
───────╱
restart
```

**Causes:** Cache warming, connection pool filling, JIT compilation, lazy initialization.

**Implication:** Don't alert on post-deploy metric drops without accounting for warm-up time. Give the service 5–15 minutes to reach steady state before comparing against baseline.

### Regular Anomalies

Recurring spikes or drops at predictable intervals — daily, weekly, or tied to batch jobs.

```
─╱╲──╱╲──╱╲── (daily spike at midnight)
```

**Causes:** Cron jobs, daily reports, scheduled batch processing, business hours patterns.

**Implication:** These are expected, not incidents. Exclude known regular anomalies from alerting windows, or use time-aware baselines that treat these as normal.

### Spikes During Troughs

Anomalous spikes that occur only during low-traffic periods (nights, weekends).

```
During low traffic: ──────╱╲────── ← suspicious
During high traffic: ──╱╲╱╲╱╲╱╲── ← normal spikes
```

**Causes:** Batch jobs competing with reduced capacity, scheduled maintenance, cron tasks that misbehave without normal traffic load.

**Implication:** Low traffic periods need separate alert thresholds. A spike to 100 requests/second during overnight quiet time may be more alarming than the same spike during peak hours.

---

## Determining Causality Between Metrics

When two metrics move together, determine whether the relationship is causal before acting on it.

### Correlation vs. Causation

Two metrics that change at the same time may be:
- **Causally related:** Metric A causes Metric B (high CPU → high latency)
- **Common cause:** Both driven by a third metric (high traffic → high CPU AND high latency)
- **Coincidental:** No real relationship (unrelated systems happen to change simultaneously)

### Causal Analysis Approach

1. **Check timing:** Does A change before B, or simultaneously? A precedes B → A may cause B
2. **Check magnitude:** Does a large change in A produce a proportional change in B?
3. **Test intervention:** If you reduce A (e.g., shed load), does B improve?
4. **Check common drivers:** Is there a third metric that explains both A and B moving together?

### Practical Implication for Alerting

Alert on the **root cause metric** only when it has sufficient lead time to enable preventive action. Otherwise, alert on the symptom (the user-visible effect) and use causal metrics for investigation.

---

## Metric Types: Flow, Stock, Availability, Throughput

Ligus categorizes metrics by their mathematical nature, which determines how to graph and alert on them:

| Type | Definition | Examples | Graph Treatment |
|------|-----------|----------|-----------------|
| **Flow** | Rate of change (events per unit time) | Requests/sec, errors/sec, bytes/sec | Rate — use derivative/delta |
| **Stock** | Current accumulated quantity | Queue depth, active sessions, disk usage | Gauge — current value |
| **Availability** | Fraction of time system is operational | Uptime %, success rate | Ratio — use rolling window |
| **Throughput** | Capacity being utilized | CPU %, memory %, connection pool % | Utilization — compare against ceiling |

Mismatching graph type to metric type produces misleading visualizations. A stock metric graphed as a rate appears to always be zero unless it's changing; a flow metric graphed as a raw count grows monotonically and makes trends invisible.
