# AWS CloudWatch Metric Filters — Capabilities Reference
For CLI commands, see [cloudwatch-metric-filters-cli.md](cloudwatch-metric-filters-cli.md).

## What Metric Filters Are

A metric filter is a rule attached to a CloudWatch Logs log group that scans every incoming log event against a filter pattern. When an event matches, the filter publishes a value to a CloudWatch custom metric. The result is a persistent time-series metric that can be graphed, alarmed, and dashboarded — derived from log data without any code changes to the emitting service.

**Key behaviors:**
- Evaluated **at ingestion time** as events arrive; no batch job, no delay pipeline
- **Not retroactive** — only events ingested after the filter is created are evaluated
- Publishes in **one-minute periods**; if no events are ingested in a period, nothing is published (unless `defaultValue` is set)
- Supported on **Standard log class** only — not Infrequent Access or Archival
- **One metric per filter** — each filter produces exactly one CloudWatch metric; create multiple filters for multiple metrics
- **Limit: 100 metric filters per log group** (not adjustable)

**How metric filters compare to EMF and PutMetricData:**

| | Metric Filters | EMF | PutMetricData |
|---|---|---|---|
| Code change required | None | Yes (structured JSON) | Yes (API call) |
| Works on existing logs | Yes | No | No |
| Log + metric correlation | No (separate) | Yes (same event) | No |
| Retroactive analysis | No | No | No |
| Latency to metric | ~1–2 min | ~1–2 min | Near-real-time |
| Best for | Existing log formats; simple counting | Lambda/containers; need context with metrics | Direct metric pipeline; no logs needed |

---

## Filter Pattern Syntax

All patterns are **case-sensitive**.

### 1. Simple text matching

| Pattern | Matches |
|---|---|
| `ERROR` | Any event containing "ERROR" |
| `ERROR Exception` | Events containing both "ERROR" AND "Exception" (space = AND) |
| `?ERROR ?WARNING` | Events containing "ERROR" OR "WARNING" (`?` prefix = OR) |
| `ERROR -Timeout` | Events containing "ERROR" but NOT "Timeout" |
| `"connection refused"` | Events containing the exact phrase |
| `" "` | Every log event (match-all) |

### 2. Regex patterns

Delimited by `%`. Parentheses not supported. Max **2 regex** per filter pattern; max **5 regex-containing filters** per log group.

```
%ERROR|CRITICAL%                     # OR in regex (use \| to escape pipe)
%10\.10\.0\.\d+%                     # IP address range
%^ERROR%                             # anchored to start
%\d{3}%                              # exactly 3 digits
%111\.111\.111\.1[0-9]{1,2}%        # range in last octet
```

Supported operators: `.` `*` `+` `?` `[abc]` `[a-z]` `[^abc]` `{m,n}` `\d` `\D` `\s` `\w` `\W` `\xhh` `|`
Not supported: `()` grouping, multi-byte characters, lookahead/lookbehind.

### 3. JSON pattern matching

Wrap entire expression in `{ }`. Property selectors always start with `$.`.

```
{ $.eventType = "UpdateTrail" }            # string equals
{ $.eventType != "DeleteTrail" }           # string not-equals
{ $.sourceIPAddress = "10.10.*" }          # string with wildcard
{ $.statusCode = 404 }                     # numeric equals
{ $.latency > 1000 }                       # numeric greater-than
{ $.latency >= 500 }                       # numeric gte
{ $.latency < 100 }                        # numeric less-than
{ $.level = "ERROR" && $.retries > 3 }    # AND compound
{ $.level = "ERROR" || $.level = "FATAL" } # OR compound
{ $.SomeField EXISTS }                     # field presence
{ $.SomeField NOT EXISTS }                 # field absence
{ $.SomeObject IS NULL }                   # null check
{ $.array[0] = "first" }                  # array element
{ $.array[*] = "value" }                  # any array element
{ $.nested.field = "value" }              # nested field
{ $.['cluster.name'] = "prod" }           # field name containing dot
{ $.eventType = %Trail% }                 # regex within JSON pattern
```

**Compound operator precedence:** `()` > `&&` > `||`

**Wildcard selectors:** Max 1 wildcard per property selector; max 3 total in a compound expression.

### 4. Space-delimited (Apache/CLF) pattern

Use `[field1, field2, ...]` for whitespace-separated log formats.

```
# Basic — match any log with 7 fields
[ip, user, username, timestamp, request, status_code, bytes]

# Count 4xx responses
[ip, user, username, timestamp, request, status_code=4*, bytes]

# Count 5xx responses
[ip, user, username, timestamp, request, status_code=5*, bytes]

# Ignore fields with -
[ip, -, -, timestamp, request, status_code, bytes]

# OR within a field
[ip, user, username, timestamp, request, status_code=4* || status_code=5*, bytes]

# AND within a field
[w1!=ERROR && w1!=WARNING, w2, w3]

# Variable leading fields with ...
[..., status_code=4*, bytes]

# Regex in field
[logLevel, date, time, method, url=%/api/[0-9]+$%, response_time]

# Bytes threshold — only large responses
[ip, user, username, timestamp, request, status_code, bytes > 10000]
```

Named fields in space-delimited patterns can be referenced as `$fieldname` in `metricValue` and `dimensions` (e.g., `"$bytes"`, `"$status_code"`).

---

## Metric Filter Configuration

### Filter name
- 1–512 characters; no `:` or `*`

### Metric transformation fields

| Field | Required | Notes |
|---|---|---|
| `metricName` | Yes | Max 255 chars; no `:` `*` `$` |
| `metricNamespace` | Yes | Max 255 chars; no `:` `*` `$`; created if it doesn't exist |
| `metricValue` | Yes | Literal (`"1"`) or field reference (`"$.latency"`, `"$bytes"`); max 100 chars |
| `defaultValue` | No | Double; published when logs ingest but pattern doesn't match; **cannot be used with dimensions** |
| `unit` | No | Defaults to `None`; see unit list in EMF reference |
| `dimensions` | No | Max 3; JSON/space-delimited patterns only |

### Static vs. extracted metric value

**Static (counting):** `metricValue = "1"` — each match adds 1. Use `Sum` statistic.

**Extracted numeric field:**
- JSON: `"metricValue": "$.responseTime"` — publishes the field's numeric value
- Space-delimited: `"metricValue": "$bytes"` — publishes the field's numeric value
- Non-numeric values are silently ignored

### Default value

`defaultValue: 0` causes CloudWatch to publish `0` for any one-minute period where logs were ingested but no events matched. Without it, periods with no matches produce no data point, which causes alarms to enter INSUFFICIENT_DATA state.

**Rule:** Use `defaultValue: 0` for counting filters (not extraction filters), and only when no dimensions are configured.

---

## Dimensions on Metric Filters

Added May 2021. Dimension values are **extracted from log fields** at match time.

```json
{
  "metricName": "RequestCount",
  "metricNamespace": "MyApp",
  "metricValue": "1",
  "dimensions": {
    "StatusCode": "$status_code",
    "Method": "$method"
  }
}
```

- Max **3 dimensions** per filter
- Only supported for **JSON and space-delimited** patterns (not simple text)
- **Cannot combine with `defaultValue`**
- `@aws.account` and `@aws.region` are valid system field dimension values for centralized log aggregation

**High-cardinality warning:** Each unique combination of dimension values = one custom metric (~$0.30/month each). Do NOT use RequestId, IP address, userId, or any unbounded field as a dimension. AWS will **automatically disable the filter** if it generates 1,000+ unique dimension pairs within one hour.

---

## Common Patterns

### Count errors with alarm-safe default

```bash
aws logs put-metric-filter \
  --log-group-name "/aws/lambda/my-function" \
  --filter-name "ErrorCount" \
  --filter-pattern "ERROR" \
  --metric-transformations \
    metricName=ErrorCount,metricNamespace=MyApp,metricValue=1,defaultValue=0,unit=Count
```

### Count 4xx and 5xx (Apache access log)

```bash
# 4xx
aws logs put-metric-filter \
  --log-group-name "/myapp/access" \
  --filter-name "Http4xx" \
  --filter-pattern '[ip, user, username, timestamp, request, status_code=4*, bytes]' \
  --metric-transformations \
    metricName=Http4xxCount,metricNamespace=MyApp/HTTP,metricValue=1,defaultValue=0,unit=Count

# 5xx
aws logs put-metric-filter \
  --log-group-name "/myapp/access" \
  --filter-name "Http5xx" \
  --filter-pattern '[ip, user, username, timestamp, request, status_code=5*, bytes]' \
  --metric-transformations \
    metricName=Http5xxCount,metricNamespace=MyApp/HTTP,metricValue=1,defaultValue=0,unit=Count
```

### Extract latency from JSON logs

```bash
aws logs put-metric-filter \
  --log-group-name "/aws/lambda/my-api" \
  --filter-name "RequestLatency" \
  --filter-pattern '{ $.latency = * }' \
  --metric-transformations \
    metricName=RequestLatency,metricNamespace=MyApp,metricValue='$.latency',unit=Milliseconds
```
Use `Average`, `p99`, `p95` statistics on this metric.

### Lambda timeout detection

```bash
aws logs put-metric-filter \
  --log-group-name "/aws/lambda/my-function" \
  --filter-name "Timeouts" \
  --filter-pattern '"Task timed out"' \
  --metric-transformations \
    metricName=TimeoutCount,metricNamespace=MyApp,metricValue=1,defaultValue=0,unit=Count
```

### CloudTrail: unauthorized API calls

```bash
aws logs put-metric-filter \
  --log-group-name "CloudTrail/DefaultLogGroup" \
  --filter-name "UnauthorizedAPICalls" \
  --filter-pattern '{ ($.errorCode = "AccessDenied") || ($.errorCode = "UnauthorizedAccess") }' \
  --metric-transformations \
    metricName=UnauthorizedAPICalls,metricNamespace=CloudTrailMetrics,metricValue=1,defaultValue=0,unit=Count
```

### CloudTrail: root account activity

```bash
--filter-pattern '{ $.userIdentity.type = "Root" && $.userIdentity.invokedBy NOT EXISTS && $.eventType != "AwsServiceEvent" }'
```

### CloudTrail: IAM policy changes

```bash
--filter-pattern '{ ($.eventName = DeleteGroupPolicy) || ($.eventName = DeleteRolePolicy) || ($.eventName = DeleteUserPolicy) || ($.eventName = PutGroupPolicy) || ($.eventName = PutRolePolicy) || ($.eventName = PutUserPolicy) || ($.eventName = CreatePolicy) || ($.eventName = DeletePolicy) || ($.eventName = CreatePolicyVersion) || ($.eventName = DeletePolicyVersion) || ($.eventName = SetDefaultPolicyVersion) }'
```

### Request count with status code dimension (low-cardinality only)

```bash
aws logs put-metric-filter \
  --log-group-name "/myapp/access" \
  --filter-name "RequestsByStatus" \
  --filter-pattern '[ip, user, username, timestamp, request, status_code, bytes]' \
  --metric-transformations '[{
    "metricName": "RequestCount",
    "metricNamespace": "MyApp",
    "metricValue": "1",
    "dimensions": {"StatusCode": "$status_code"}
  }]'
```
Only safe if `status_code` has very few unique values.

---

## Integration with CloudWatch Alarms

Create an alarm on the metric filter output metric:

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "HighErrorRate" \
  --metric-name "ErrorCount" \
  --namespace "MyApp" \
  --statistic Sum \
  --period 60 \
  --evaluation-periods 5 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --treat-missing-data notBreaching \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:MyAlertTopic
```

**`treat-missing-data` guidance for metric filter alarms:**

| Setting | When to use |
|---|---|
| `notBreaching` | Standard choice — no logs in a period = no error |
| `breaching` | When absence of logs itself signals a problem |
| `ignore` | Expected data gaps (batch jobs, maintenance windows) |
| `missing` (default) | Avoid — causes INSUFFICIENT_DATA alerts during quiet periods |

**Best practice combination:** `defaultValue=0` on the filter (requires no dimensions) + `notBreaching` on the alarm. This ensures quiet periods publish 0 rather than no data, keeping the alarm in a clean OK state.

---

## Metric Filters vs. Logs Insights

| | Metric Filters | Logs Insights |
|---|---|---|
| Direction | Forward-looking from creation date only | Historical — any retained log data |
| Output | Persistent CloudWatch metric | Ad-hoc query results |
| Alarms | Yes | No |
| Cost | Per custom metric + log ingestion | Per GB scanned |
| Complex logic | Limited filter syntax | Full query language with functions |
| **Use when** | Always-on operational alerting | Incident investigation, historical analysis |

---

## Limits

| Constraint | Value |
|---|---|
| Max metric filters per log group | **100** |
| Filter pattern max length | 1,024 chars |
| Metric name / namespace max length | 255 chars each |
| Metric value max length | 100 chars |
| Max dimensions per filter | 3 |
| Dimension key / value max length | 255 chars each |
| Max regex patterns per filter pattern | 2 |
| Max regex-containing filters per log group | 5 |
| Max wildcard selectors in compound JSON expr | 3 |
| Auto-disable threshold (dimension cardinality) | 1,000 unique pairs/hour |
| API throttle (put/delete/describe/test) | 5 req/sec/region |
| Max messages per `test-metric-filter` | 50 |
| Supported log class | Standard only |
