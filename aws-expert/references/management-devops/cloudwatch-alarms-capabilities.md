# AWS CloudWatch Alarms — Capabilities Reference
For CLI commands, see [cloudwatch-alarms-cli.md](cloudwatch-alarms-cli.md).

## Alarm Types

| Type | API | Key Parameter |
|---|---|---|
| **Static threshold** | `PutMetricAlarm` with `MetricName` | `Threshold` + `ComparisonOperator` |
| **Metric math** | `PutMetricAlarm` with `Metrics` array | Expression returning single time series |
| **Anomaly detection** | `PutMetricAlarm` with `ThresholdMetricId` | `ANOMALY_DETECTION_BAND(m1, N)` expression |
| **Composite** | `PutCompositeAlarm` | Boolean `AlarmRule` expression |
| **Metrics Insights** | `PutMetricAlarm` with SQL in `Metrics` | Tracks contributors dynamically |
| **PromQL** | `PutMetricAlarm` with `EvaluationCriteria` | Monitors OTLP-ingested metrics |

---

## Static Threshold Alarms

**Required parameters:** `Namespace`, `MetricName`, `Period`, `EvaluationPeriods`, `Threshold`, `ComparisonOperator`, and either `Statistic` or `ExtendedStatistic`.

**ComparisonOperator values:**
- `GreaterThanOrEqualToThreshold`
- `GreaterThanThreshold`
- `LessThanThreshold`
- `LessThanOrEqualToThreshold`
- `GreaterThanUpperThreshold` / `LessThanLowerThreshold` / `LessThanLowerOrGreaterThanUpperThreshold` — anomaly detection only

**Statistics:** `SampleCount`, `Average`, `Sum`, `Minimum`, `Maximum`

**Extended statistics (percentile and trimmed):**
- Standard: `p90`, `p99`
- Trimmed mean: `tm90`, `TM(5%:95%)`
- Trimmed count/sum: `tc90`, `TC(X%:X%)`, `ts90`, `TS(X%:X%)`
- Winsorized mean: `wm90`, `WM(X%:X%)`
- Interquartile mean: `IQM`
- Percentile rank: `PR(n:m)`

**`EvaluateLowSampleCountPercentile`:** `evaluate` (default, may go to INSUFFICIENT_DATA with sparse data) | `ignore` (maintains current state when sample count is too low for percentile calculation).

**Wrong `Unit` gotcha:** Specifying `Unit` that doesn't match the metric's actual unit causes `INSUFFICIENT_DATA`. If unsure, omit `Unit`.

---

## Metric Math Alarms

- Use `Metrics` array of `MetricDataQuery` objects instead of `MetricName`/`Namespace`/etc.
- Exactly one `MetricDataQuery` must have `ReturnData: true`; that expression becomes the alarm value.
- Cannot mix `MetricName`/`Namespace`/`Statistic` with `Metrics` in the same alarm.
- `SEARCH` function cannot be the alarm expression — it returns multiple time series.
- Scalar math functions (`SUM(m1)`, `AVG(m2)`, `MAX(m2)`, `MIN(m2)`, `RUNNING_SUM`) behave unpredictably in alarm evaluation — CloudWatch retrieves extra data during evaluation. Use M-out-of-N approach instead of scalar aggregations.
- Cost: $0.10 × number of metrics referenced per month.

---

## Anomaly Detection Alarms

**Model behavior:**
- `PutAnomalyDetector` creates the ML model for a metric + statistic combination.
- Trains on up to 2 weeks of data; learns hourly, daily, and weekly seasonality automatically.
- Band appears within 15 minutes if a model exists; up to 3 hours for a new model; 2 weeks for full accuracy.
- Model continuously re-trains on new data.
- Exclude up to 10 time ranges from training (e.g., scheduled maintenance, known anomalies).
- CloudWatch constrains bands to logical values — `MemoryUtilization` stays 0–100%, `Requests` stays non-negative.

**Alarm configuration:**
- `ThresholdMetricId` must reference the ID of the `ANOMALY_DETECTION_BAND(m1, N)` expression.
- `N` is the number of standard deviations — higher = wider band = less sensitive.
- Do NOT set `Threshold` for anomaly detection alarms.
- `ComparisonOperator` must be one of the three anomaly operators above.

**Limitations:**
- `ANOMALY_DETECTION_BAND` does NOT support: high-resolution metrics, periods > 1 hour, `METRICS`/`SEARCH`/`DB_PERF_INSIGHTS` functions, or mixing different periods in the same expression.
- Auto Scaling actions NOT supported on anomaly detection alarms.
- Cross-account anomaly detection: supported via monitoring account (GA April 2024).

**`reasonData` in notifications:** includes `recentDatapoints`, `recentLowerThresholds`, `recentUpperThresholds`.

---

## Composite Alarms

**`AlarmRule` syntax:**
```
ALARM("CPUHigh") AND ALARM("DiskFull")
ALARM("CPUHigh") AND NOT ALARM("MaintenanceWindow")
NOT (ALARM("BatchJob") OR ALARM("ScheduledMaint"))
AT_LEAST(2, ALARM, (AZ1-alarm, AZ2-alarm, AZ3-alarm, AZ4-alarm))
AT_LEAST("50%", OK, (DB1, DB2, DB3, DB4))
```

**State functions:** `ALARM("name")`, `OK("name")`, `INSUFFICIENT_DATA("name")`, `TRUE`, `FALSE`

**`AT_LEAST(M, STATE_CONDITION, (list))`:**
- `STATE_CONDITION`: `ALARM`, `OK`, `INSUFFICIENT_DATA`, `NOT ALARM`, `NOT OK`, `NOT INSUFFICIENT_DATA`
- M: integer count or percentage string (e.g., `"50%"`)

**Limits:**
- Up to 100 child alarms per composite
- Up to 150 composite alarms per underlying alarm
- Up to 500 total elements in AlarmRule
- Up to 10,240 characters in AlarmRule

**Actions NOT supported:** EC2 stop/terminate/reboot/recover, Auto Scaling
**Actions supported:** SNS, Lambda, OpsItem, Incident Manager, CloudWatch Investigations

**Cross-account:** NOT supported — child alarms must be in the same account and region as the composite.

**`reasonData`:** `{"triggeringAlarms": [...]}` listing which children are in ALARM.

### Suppressor Alarms

Suppressor alarms prevent composite alarm actions from firing during known-bad periods (deployments, maintenance) without disabling monitoring.

| Parameter | Purpose |
|---|---|
| `ActionsSuppressor` | Alarm name/ARN; suppresses composite actions when this alarm is in ALARM state |
| `ActionsSuppressorWaitPeriod` | Seconds to wait for suppressor to enter ALARM after composite enters ALARM (prevents missed suppression if suppressor lags); recommended: 60s |
| `ActionsSuppressorExtensionPeriod` | Seconds to keep suppressing after suppressor returns to OK (prevents premature re-alerting); recommended: 60s |

- If suppressor changes state during a wait/extension period, the period resets.
- EventBridge `state.actionsSuppressedBy`: `WaitPeriod` or `AlarmSuppressor`.
- Mute rules take precedence over suppressor logic when both are active.

---

## Metrics Insights Alarms

- Uses CloudWatch Metrics Insights SQL to dynamically track resources matching a query.
- New resources matching the query are monitored automatically without alarm modification.
- Tag-based filtering requires "Enable resource tags on telemetry" in CloudWatch Settings.
- Standard resolution only (60-second evaluation).
- Cross-account: supported via monitoring account.
- Each matching resource (contributor) is tracked individually.
- Two EventBridge event types: `CloudWatch Alarm State Change` (alarm-level) and `CloudWatch Alarm Contributor State Change` (per-contributor).
- Cost: based on metrics analyzed by the SQL query (`MetricInsightAlarmUsage`).

---

## PromQL Alarms

- Monitors metrics ingested via CloudWatch OTLP endpoint using PromQL instant queries.
- `EvaluationCriteria` parameter is mutually exclusive with all other metric-specification parameters.
- Uses `EvaluationInterval` (10, 20, 30, or multiples of 60 up to 3600) instead of `Period` + `EvaluationPeriods`.
- Initial state is `OK` (not `INSUFFICIENT_DATA` like metric alarms).
- `TreatMissingData` does NOT apply.
- Duration-based pending/recovery periods for state transitions.
- Actions: SNS and Lambda (contributor-level); EC2, Auto Scaling, OpsItem, Incident Manager, CloudWatch Investigations NOT supported.
- Notifications do NOT include `stateReason` or `stateReasonData`.

---

## Alarm States

| State | Console Color | Meaning |
|---|---|---|
| `OK` | Gray | Metric within threshold |
| `ALARM` | Red | Threshold breached |
| `INSUFFICIENT_DATA` | Gray | Alarm just created, metric unavailable, or not enough data points |

**Internal evaluation states** (visible in `DescribeAlarms` `StateReason`, not user-facing):
- `PARTIAL_DATA` — not all data retrieved due to quota limits
- `EVALUATION_ERROR` — configuration error; check `StateReason`
- `EVALUATION_FAILURE` — temporary CloudWatch service issue

**State machine rules:**
- Actions fire ONLY on state transitions, not while a condition persists.
- Exception: Auto Scaling actions re-fire every minute while the alarm remains in ALARM state.
- `SetAlarmState` forces a temporary state; the alarm reverts at the next evaluation.
- Alarm history retained for 30 days natively.
- In rare cases, multiple notifications can occur for a single state change.
- PromQL alarm initial state: `OK`. All other alarm types initial state: `INSUFFICIENT_DATA`.
- `PutMetricAlarm` update: existing state is preserved; configuration is completely overwritten.

---

## Evaluation: Periods, Datapoints-to-Alarm, Treat-Missing-Data

### Period and Evaluation Parameters

| Parameter | Values / Notes |
|---|---|
| `Period` | 10, 20, 30 (high-resolution only) or multiples of 60; minimum 60s for standard |
| `EvaluationPeriods` | Number of most recent periods to evaluate; minimum 1 |
| `DatapointsToAlarm` | "M" in M-out-of-N; defaults to `EvaluationPeriods` if omitted; breaching points need NOT be consecutive |

**Maximum evaluation window:**
- Periods ≥ 1 hour: 604,800 seconds (7 days)
- Periods < 1 hour: 86,400 seconds (1 day)

**Evaluation frequency:**
- Standard (period ≥ 60s): evaluated every minute
- High-resolution (10/20/30s period): evaluated every 10 seconds
- Multi-day alarms (EvaluationPeriods × Period > 1 day): evaluated once per hour at `:00` — up to 1-hour delay before state changes reflect recent data.

### TreatMissingData Options

| Option | Behavior | Use when... |
|---|---|---|
| `missing` (default) | Transitions to `INSUFFICIENT_DATA` when all points are missing | General purpose |
| `breaching` | Missing points counted as breaching threshold | Alarm on missing data (heartbeat checks, required signals) |
| `notBreaching` | Missing points counted as good | No data = no errors (e.g., DynamoDB `ThrottledRequests`, 4xx count) |
| `ignore` | Maintains current alarm state when data is missing | Sporadic metrics; AWS/DynamoDB namespace always uses this regardless of setting |

**How CloudWatch resolves missing data:**
1. No missing data → uses N most recent real points; TMD is ignored
2. Some missing but enough real → backfills from farther history; TMD is ignored
3. Too few real points → fills gaps using TMD treatment; uses real points + minimum TMD fills

**FILL function as TMD alternative in metric math:**
- `FILL(m1, 0)` / `FILL(m1, 90)` — fills missing with a constant (faster alarm reaction; reduces 7-minute latency to ~2 minutes)
- `FILL(m1, REPEAT)` — repeats last known value (handles consistent ingestion delays)
- Warning: FILL can cause alarms stuck in OK/ALARM if metrics have ingestion delays; pair with M-out-of-N.

---

## Alarm Actions

### Per-State Action Lists

- `AlarmActions` — fires on transition TO ALARM
- `OKActions` — fires on transition TO OK
- `InsufficientDataActions` — fires on transition TO INSUFFICIENT_DATA
- `ActionsEnabled` — boolean that globally toggles all actions; survives `PutMetricAlarm` updates
- Maximum **5 actions** per state list

CloudWatch does NOT validate that action ARNs exist at creation time — no error if SNS topic or Lambda is later deleted.

### Action Types and Support Matrix

| Action Type | Metric Alarm | Composite | Anomaly Detection | PromQL | Metrics Insights |
|---|---|---|---|---|---|
| SNS | ✓ | ✓ | ✓ | ✓ (contributor-level) | ✓ (contributor-level) |
| Lambda | ✓ | ✓ | ✓ | ✓ (contributor-level) | ✓ (contributor-level) |
| EC2 stop/terminate/reboot/recover | ✓ | ✗ | ✗ | ✗ | ✗ |
| Auto Scaling | ✓ | ✗ | ✗ | ✗ | ✗ |
| Systems Manager OpsItem | ✓ | ✓ | ✓ | ✗ | ✓ |
| Incident Manager | ✓ | ✓ | ✓ | ✗ | ✓ |
| CloudWatch Investigations | ✓ | ✓ | ✓ | ✗ | ✓ |

OpsItem, Incident Manager, and CloudWatch Investigations only fire on transitions **TO ALARM** (not OK or INSUFFICIENT_DATA).

### EC2 Actions

| Action | ARN | Notes |
|---|---|---|
| Stop | `arn:aws:automate:{region}:ec2:stop` | EBS-backed instances only; instance is restartable |
| Terminate | `arn:aws:automate:{region}:ec2:terminate` | Cannot restart; respects termination protection |
| Reboot | `arn:aws:automate:{region}:ec2:reboot` | Preserves public DNS, private IP, instance store |
| Recover | `arn:aws:automate:{region}:ec2:recover` | Only for `StatusCheckFailed_System`; NOT for `StatusCheckFailed_Instance`; migrates to new hardware; in-memory data lost; limited instance types |

**EC2 race condition gotcha:** Never set identical evaluation periods for both reboot and recover alarms on the same instance. Recommended: reboot = 3 periods of 1 min, recover = 2 periods of 1 min.

**Required IAM:** `AWSServiceRoleForCloudWatchEvents` service-linked role; needs `iam:CreateServiceLinkedRole`.

### Auto Scaling Actions

ARN format: `arn:aws:autoscaling:{region}:{account-id}:scalingPolicy:{policy-id}:autoScalingGroupName/{group}:policyName/{name}`

Auto Scaling actions re-fire **every minute** while the alarm remains in ALARM state (unique behavior compared to all other action types).

### SNS Notification Payload

Full payload includes:
- `stateReason` — human-readable explanation
- `stateReasonData` — JSON with `version`, `queryDate`, `startDate`, `statistic`, `period`, `recentDatapoints`, `threshold`
- Composite alarms: `stateReasonData` contains `{"triggeringAlarms": [...]}`
- Anomaly detection: `reasonData` includes `recentLowerThresholds`, `recentUpperThresholds`

### Alarm Mute Rules

Temporarily suppresses alarm actions during scheduled maintenance windows while monitoring and state changes continue.

| Parameter | Format | Notes |
|---|---|---|
| Schedule | cron expression or `at(yyyy-MM-ddThh:mm)` | One-time or recurring |
| Duration | ISO-8601 (e.g., `PT2H`, `P1D`) | Min: PT1M; Max: P15D |
| Timezone | IANA timezone string | e.g., `America/Chicago` |

- Up to 100 alarms per mute rule; same account/region only.
- When mute window ends with alarm still in ALARM state, CloudWatch auto-re-triggers the muted actions.
- Mute rule status: `SCHEDULED` → `ACTIVE` → `EXPIRED`.
- API: `PutAlarmMuteRule`.
- EventBridge events for muted alarms include `muteDetail` object; events still fire even when muted.
- Mute rules take precedence over composite alarm suppressor logic when both are active.

### Repeated Notifications (Workaround)

CloudWatch fires only once per state transition. For repeated/escalating notifications: EventBridge rule → Lambda → Step Functions `wait` state loop that re-checks alarm state and re-sends to SNS. Use tag-based opt-in to control which alarms use this pattern.

---

## EventBridge Integration

CloudWatch **guarantees** delivery of alarm state change events to EventBridge.

**Event types:**
- `CloudWatch Alarm State Change` — all alarm types (alarm-level)
- `CloudWatch Alarm Contributor State Change` — Metrics Insights alarms (per-contributor)

**Key fields in event detail:**
```json
{
  "alarmName": "MyAlarm",
  "previousState": { "value": "OK", "reason": "...", "timestamp": "..." },
  "state": {
    "value": "ALARM",
    "reason": "...",
    "reasonData": "...",
    "actionsSuppressedBy": "AlarmSuppressor",
    "actionsSuppressedReason": "..."
  },
  "muteDetail": {
    "mutedByArn": "...",
    "muteWindowStart": "...",
    "muteWindowEnd": "..."
  }
}
```

**Useful filter patterns:**
```json
{"detail": {"state": {"value": ["ALARM"]}}}
{"detail": {"state": {"actionsSuppressedBy": [{"exists": true}]}}}
{"detail-type": ["CloudWatch Alarm Contributor State Change"]}
```

**Extended history pattern:** Route state change events to CloudWatch Logs for history beyond the native 30-day limit.

---

## Tags

- Alarms support up to 50 tags.
- `Tags` parameter in `PutMetricAlarm`/`PutCompositeAlarm` only applies tags on **new alarm creation** — not on updates. Use `TagResource` API to add or update tags on existing alarms.
- `cloudwatch:TagResource` IAM permission required in addition to `cloudwatch:PutMetricAlarm`.
- Tag-based IAM conditions supported for resource-level access control.
- Tag-based Metrics Insights alarm filtering: requires "Enable resource tags on telemetry" in CloudWatch Settings.

---

## Cross-Account Alarms

- Requires CloudWatch cross-account observability setup: monitoring account + source accounts linked via Sinks/Links.
- Source accounts share metrics, logs, traces, Application Signals, Application Insights.
- Max source accounts per monitoring account: 100,000. Max monitoring accounts per source account: 5.
- Cross-account metric math: supported except `ANOMALY_DETECTION_BAND`, `INSIGHT_RULE`, `SERVICE_QUOTA` functions.
- Cross-account composite alarms: **NOT supported** — child alarms must be same account/region.
- Cross-account anomaly detection alarms: supported (GA April 2024).
- Cost: no extra charge for metrics/logs/Application Signals; trace copies charged.

---

## Application Signals SLO Integration

### SLO Alarm Types

| Type | Purpose |
|---|---|
| **Attainment/threshold** | Alerts when SLO breaches its goal or warning level |
| **Burn rate** | Alerts when error budget is being consumed faster than sustainable |

**Burn rate formula:** `burn_rate = error_rate_over_window / (1 - attainment_goal)`
- Burn rate = 1: on track to just meet SLO
- Burn rate > 1: budget exhausting faster than allowed

**Multi-window burn rate strategy (composite alarm pattern):**

| Window pair | Budget threshold | Detection speed |
|---|---|---|
| 5-min + 1-hour | 2% | Fast (transient spikes) |
| 30-min + 6-hour | 5% | Medium |
| 6-hour + 3-day | 10% | Slow (sustained degradation) |

Composite rule: `ALARM("1HourBurnRate") AND ALARM("5MinBurnRate")` — both windows must breach simultaneously.

**SLO types:**
- Period-based: discrete periods marked healthy/unhealthy; fixed error budget (e.g., 432 minutes/month at 99%)
- Request-based: fraction of good/bad requests; dynamic error budget scales with traffic

**Gotchas:**
- Editing an SLO does NOT automatically update associated alarms.
- Deleting an SLO does NOT delete associated alarms.
- Up to 10 time window exclusions per SLO.

---

## Pricing

| Alarm type | Cost | Free tier |
|---|---|---|
| Standard metric alarm | $0.10/alarm-metric/month | 10 alarms/month |
| High-resolution alarm | Higher than standard | None |
| Composite alarm | $0.50/alarm/month | None |
| Anomaly detection alarm | $0.30/alarm/month (3× standard) | None |
| Metric math alarm | $0.10 × metrics referenced/month | None |
| Metrics Insights alarm | Per metric analyzed by SQL query | None |

**Cost optimization:**
- Delete alarms for deleted resources — they remain in INSUFFICIENT_DATA and continue to accrue charges.
- Use `describe-alarms --state-value INSUFFICIENT_DATA` to find orphaned alarms.
- Pre-aggregate metrics before publishing to reduce metric math fan-out costs.
- Narrow Metrics Insights query filters to minimize metrics analyzed.

---

## CloudFormation / CDK

**CloudFormation resource:** `AWS::CloudWatch::Alarm`
- `AlarmName` causes resource **replacement** on update if explicitly set — omit to use auto-generated name and avoid replacement.
- Return values: `Ref` → alarm name; `Fn::GetAtt AlarmArn` → full ARN.
- Tags via CloudFormation only applied on new alarm creation (not updates).
- Composite alarm: `AWS::CloudWatch::CompositeAlarm` is a separate resource type.

**CloudFormation anomaly detection alarm:**
```yaml
LambdaInvocationsAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    ComparisonOperator: LessThanLowerOrGreaterThanUpperThreshold
    EvaluationPeriods: 1
    Metrics:
      - Expression: ANOMALY_DETECTION_BAND(m1, 2)
        Id: ad1
      - Id: m1
        MetricStat:
          Metric:
            MetricName: Invocations
            Namespace: AWS/Lambda
          Period: 86400
          Stat: Sum
    ThresholdMetricId: ad1
    TreatMissingData: breaching
```

**CDK key constructs:**
- `aws_cdk.aws_cloudwatch.Alarm` — metric alarm
- `aws_cdk.aws_cloudwatch.CompositeAlarm` — composite alarm
- `aws_cdk.aws_cloudwatch.TreatMissingData` — enum: `BREACHING`, `NOT_BREACHING`, `IGNORE`, `MISSING`
- `aws_cdk.aws_cloudwatch.CfnCompositeAlarm` — L1 construct for full composite alarm control

---

## Common Gotchas

| Gotcha | Detail |
|---|---|
| Multi-day alarm delay | Alarms with evaluation window > 1 day evaluate hourly at `:00` — up to 1-hour delay for state changes |
| Scalar math in alarms | `SUM(m1)`, `AVG(m2)` in alarm expressions behave unpredictably — CloudWatch retrieves extra historical data during evaluation |
| FILL + ingestion delay | FILL can cause alarms stuck in OK or ALARM if metrics arrive late; pair with M-out-of-N |
| Missing `Unit` match | Specifying a `Unit` that doesn't match the metric causes `INSUFFICIENT_DATA` |
| Anomaly band not immediate | New model takes up to 3 hours to show band, 2 weeks for full seasonal accuracy |
| Orphaned action ARNs | CloudWatch does not validate action ARNs — silently no-ops if SNS topic or Lambda is deleted |
| EC2 recover scope | `ec2:recover` only for `StatusCheckFailed_System`, NOT `StatusCheckFailed_Instance`; limited instance types |
| Composite + cross-account | Cross-account composite alarms are NOT supported |
| PromQL initial state | PromQL alarms start in `OK` (not `INSUFFICIENT_DATA`) |
| CloudFormation AlarmName | Explicit `AlarmName` causes replacement on stack update |
| Tags on update | `Tags` in `PutMetricAlarm` only applied on creation; use `TagResource` to update tags |
| Mute vs EventBridge | Mute rules suppress actions but EventBridge events still fire; `muteDetail` is added to the payload |
| SEARCH in alarm | `SEARCH` function returns multiple time series; cannot be used as alarm expression |
| Auto Scaling refires | Auto Scaling actions re-fire every minute in ALARM state (unlike all other action types) |
