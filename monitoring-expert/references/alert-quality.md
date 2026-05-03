# Alert Quality Measurement
## Chapter 6–7: Precision, Recall, F-Measure, Detectability, Feedback Loop

Source: "Effective Monitoring and Alerting" by Slawek Ligus

---

## Why Measure Alert Quality?

Most organizations treat monitoring as binary — either alerts fire or they don't. Ligus applies classification theory to alerting: an alert system is a classifier that takes metric observations as input and produces binary decisions (alert / no alert). Like any classifier, it has measurable quality.

Without measuring quality, you cannot improve systematically. Reducing noise without understanding recall means you may be deleting alerts that catch real problems.

---

## The Four Alert Outcomes

Every time interval can be classified by whether a real problem existed and whether an alert fired:

|  | Problem Exists | No Problem |
|--|----------------|------------|
| **Alert fired** | True Positive (TP) | False Positive (FP) |
| **No alert** | False Negative (FN) | True Negative (TN) |

**True Positive:** Alert fired for a real problem — the ideal outcome.
**False Positive:** Alert fired when nothing was wrong — alert fatigue, wasted response effort.
**False Negative:** Problem existed but no alert fired — the most dangerous outcome.
**True Negative:** No problem, no alert — silent normal operation.

---

## Precision

**What fraction of fired alerts represent real problems?**

```
Precision = TP / (TP + FP)
```

High precision = most alerts that fire are actionable.
Low precision = most alerts are noise.

**Target:** > 90% precision. An alert system where fewer than 9 in 10 pages are real problems is broken.

**Improving precision:**
- Raise thresholds
- Add longer evaluation windows (require condition to hold for N minutes)
- Add composite conditions (alert only when A AND B are both true)
- Remove alerts that consistently produce false positives

---

## Recall

**What fraction of real problems produced an alert?**

```
Recall = TP / (TP + FN)
```

High recall = problems are reliably detected.
Low recall = incidents go undetected until users complain.

**Target:** Depends on severity. For customer-impacting issues, recall should be > 95%.

**Improving recall:**
- Lower thresholds (risk: lower precision)
- Add more alert conditions covering different failure modes
- Cover more of the solution stack (see stack coverage below)
- Conduct post-incident reviews: "would our monitoring have caught this?"

---

## The Precision-Recall Trade-Off

Precision and recall are inversely related in most alerting systems:

```
More alerts fired → Higher recall, lower precision
Fewer alerts fired → Higher precision, lower recall
```

The goal is not to maximize either in isolation but to find the right balance for your organization's risk tolerance.

---

## F-Measure

The F-measure (F1 score) combines precision and recall into a single quality metric:

```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

A score of 1.0 is perfect. Below 0.5 indicates a fundamentally broken alerting system.

**Weighted F-measure** allows trading off precision vs. recall explicitly:

```
Fβ = (1 + β²) × (Precision × Recall) / (β² × Precision + Recall)
```

- β > 1: weight recall more heavily (prefer catching all problems, accept more noise)
- β < 1: weight precision more heavily (prefer low noise, accept missing some problems)

For production monitoring on critical services, β > 1 is typically appropriate — missing a real problem is worse than a false alarm.

---

## Detectability

Detectability measures how quickly an alert fires after a problem begins.

```
Detectability = Time from problem start to alert firing
```

Measured as a distribution across incidents, not a single number. Useful metrics:
- **Median detection time** — how long before a typical problem is caught
- **p95 detection time** — how long before 95% of problems are caught
- **Miss rate** — what fraction of problems are never detected by monitoring (detected only via user reports)

### Improving Detectability

- Shorten metric collection intervals (1-minute → 30-second → 10-second)
- Use shorter alert evaluation windows (but balance against false positive risk)
- Add synthetic checks that run continuously and detect problems faster than metric accumulation
- Instrument leading indicators (causes that reliably precede symptoms) when lead time is valuable

### Detectability vs. Precision Trade-Off

Detecting problems faster typically means firing alerts on less data — which increases false positives. The optimal point depends on:
- How severe is the problem if undetected for N minutes?
- How costly is a false alarm (on-call disruption, trust erosion)?

---

## Measuring Your Alert System

### Metrics to Track

| Metric | Description | How to Calculate |
|--------|-------------|-----------------|
| **Alert volume** | Total pages per time period | Count alert firing events |
| **Actionability rate** | Fraction that required human action | TP / total alerts |
| **False positive rate** | Fraction with no action needed | FP / total alerts |
| **Miss rate** | Incidents detected only via user reports | FN / (TP + FN) |
| **MTTD** | Mean time from incident start to detection | Average across incidents |
| **MTTA** | Mean time to acknowledge | Average response latency |

### Building the Feedback Loop

Without structured data collection, quality measurement is impossible. Require on-call responders to classify every alert:

| Outcome | Classification |
|---------|---------------|
| Real problem, action taken | True Positive |
| Real problem, auto-recovered before action | True Positive (marginal) |
| No problem found after investigation | False Positive |
| Alert fired for known maintenance | Suppress (expected noise) |

Track these over rolling 30-day windows. Review monthly. Any alert with > 20% false positive rate should be modified or deleted.

---

## False Positive Budget

Ligus recommends treating false positives as a budget:

Set a maximum acceptable false positive rate per on-call shift (e.g., 2 false positives per week). When the budget is exceeded, the monitoring team must fix or remove alerts before the end of the next sprint.

This creates a forcing function that prevents alert debt from accumulating — the common failure mode where false positive alerts keep firing indefinitely because "there's never time to fix them."

---

## Alert Quality Review Process

Run a monthly alert quality review:

1. Pull alert volume by alert name for the past 30 days
2. Cross-reference with incident records to classify TP/FP
3. Identify any alert with > 20% FP rate → candidate for modification
4. Identify any incident where no alert fired → coverage gap
5. Calculate F-measure for the overall alert system
6. Set improvement targets for next month

This is the feedback loop that transforms monitoring from a static configuration into a continuously improving system.
