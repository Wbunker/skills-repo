# Business Monitoring
## Chapter 11: Business Metrics, SLOs/SLAs, Customer-Facing Indicators

---

## Why Business Metrics Matter

Technical metrics tell you whether systems are running. Business metrics tell you whether the business is working.

A system can have 100% uptime, zero errors, and excellent latency — while silently producing wrong results, failing to process orders, or losing customers. Business metrics catch what technical metrics miss.

**Julian's principle:** The goal of a technical system is to serve a business outcome. Monitor the outcome.

---

## Technical Metrics vs. Business Metrics

| Technical Metric | Corresponding Business Metric |
|-----------------|-------------------------------|
| API error rate < 1% | Orders completing successfully |
| p99 latency < 500ms | Time from "add to cart" to "order confirmed" |
| Queue depth < 1000 | Emails delivered within 5 minutes of trigger |
| Payment service uptime > 99.9% | Successful payment rate by payment method |
| Database availability | Reports generating correctly |

Business metrics are user-outcome indicators. They answer: "Did the user get what they came for?"

---

## Service Level Objectives (SLOs)

An SLO is a target for how reliable a service should be, expressed as a ratio over a time window.

### SLO Structure

```
SLO = [SLI] [comparator] [threshold] over [window]

Example: 99.9% of checkout requests complete successfully over a rolling 30-day window
```

**SLI (Service Level Indicator):** the measured ratio
- `successful_checkouts / total_checkouts`
- `requests_with_latency_under_500ms / total_requests`

**Threshold:** the target percentage (99%, 99.9%, 99.99%)

**Window:** the measurement period (30 days rolling is common)

### Error Budget

The error budget is the allowed amount of unreliability derived from the SLO:

```
Error budget = (1 - SLO) × window duration

99.9% SLO over 30 days:
Error budget = 0.001 × 30 days × 24 hours × 60 minutes = 43.2 minutes of allowed downtime
```

When error budget is healthy: deploy freely, take risks.
When error budget is depleted: freeze changes, focus on reliability.

### SLO-Based Alerting

Alert on error budget burn rate, not absolute error rate:

| Burn Rate | Meaning | Action |
|-----------|---------|--------|
| > 14.4x | Budget consumed in 2 hours | Page immediately |
| > 6x | Budget consumed in 5 hours | Page |
| > 3x | Budget consumed in 10 hours | Ticket/warning |
| > 1x | Consuming budget faster than it replenishes | Investigate |

This approach produces fewer, higher-signal alerts than raw error rate thresholds.

### SLO vs. SLA

| | SLO | SLA |
|--|-----|-----|
| **Audience** | Internal (engineering) | External (customers/contracts) |
| **Purpose** | Operational target | Contractual commitment |
| **Tightness** | Tighter than SLA | Looser (leaves room for margin) |
| **Consequence of breach** | Engineering escalation | Contract penalty, credits |

Set your SLO more aggressively than your SLA. If your SLA is 99.9%, your internal SLO should be 99.95% so you catch problems before customers do.

---

## Key Business Metrics to Monitor

### Conversion and Funnel Metrics

For any multi-step user journey, monitor completion rates at each step:

```
Sessions started
    │ (conversion rate)
    ▼
Items viewed
    │ (add-to-cart rate)
    ▼
Items added to cart
    │ (checkout initiation rate)
    ▼
Checkout started
    │ (payment success rate)
    ▼
Orders completed
```

A drop in conversion rate at any step indicates a problem — even if all technical metrics are green.

### Revenue and Transaction Metrics

- Revenue per minute / per hour (alert on unexpected drops)
- Successful transaction count (alert on absolute drop, not just rate)
- Failed transaction count by failure reason
- Average order value (unexpected changes indicate pricing or catalog issues)

### User Engagement Metrics

- Active sessions / logged-in users
- New registrations per hour
- Feature adoption rates for new releases
- User error rates (actions that result in user-facing error messages)

### Operational Business Metrics

- Email delivery rate and time-to-deliver
- Inventory sync accuracy (for e-commerce)
- Report generation success and latency
- Batch job completion (daily/weekly jobs that feed downstream processes)

---

## Connecting Technical and Business Metrics

The most powerful monitoring setup ties technical metrics to business outcomes. This requires:

1. **Instrumentation at business event boundaries** — not just HTTP layer metrics
2. **Business event counters** — `orders.placed`, `payments.processed`, `emails.sent`
3. **Correlation between technical and business layers**

### Example: Payment Failure Investigation Path

```
Alert: Payment success rate dropped from 98% to 91%
    │
    ├── Check: which payment method is failing?
    │   (metric: payment.success_rate by payment_method tag)
    │
    ├── Check: which geographic region?
    │   (metric: payment.success_rate by region tag)
    │
    ├── Check: what is the technical error?
    │   (logs: payment service ERROR logs in same time window)
    │
    └── Root cause: Visa 3DS authentication failing for EU region
        due to cert expiry on auth callback endpoint
```

Business metric alert → technical drill-down → root cause.

---

## Executive Dashboards

Executives need business outcomes, not system internals. Build separate dashboards:

### What to Include

- SLA compliance (weekly/monthly trend)
- Customer-facing success rates for core journeys
- Revenue and transaction volume trend
- Incident count and MTTR trend
- Uptime (expressed as "minutes of downtime per month," not %)

### What to Exclude

- CPU, memory, disk utilization
- Request rates and raw error counts
- Internal service latency
- Deployment counts or technical change logs

### Delivery Cadence

Consider automated weekly email/Slack summary of key business metrics to stakeholders. This reduces ad-hoc "is the system working?" questions during incidents.

---

## Anomaly Detection for Business Metrics

Business metrics have strong seasonal patterns (day-of-week, time-of-day, holiday effects). Static thresholds often fail:
- A 50% drop in orders at 3am is normal; at 3pm it's a crisis
- Black Friday traffic 5x normal is expected; 5x on a Tuesday is suspicious

For business metrics, consider:
- **Relative thresholds**: alert when metric drops > N% vs. same time last week
- **Forecast-based alerting**: compare against predicted value given historical patterns
- **Statistical bounds**: alert when value falls outside N standard deviations of the rolling baseline

Start with relative thresholds (simpler). Use statistical methods only after you've collected enough baseline data to trust the model.
