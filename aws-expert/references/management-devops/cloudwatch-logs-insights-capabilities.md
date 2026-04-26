# CloudWatch Logs Insights — Capabilities Reference
For CLI commands, see [cloudwatch-logs-insights-cli.md](cloudwatch-logs-insights-cli.md).

## Overview

CloudWatch Logs Insights is an interactive log query engine built into CloudWatch Logs. You pay per byte scanned. Results are available within seconds for most queries; large time ranges over petabyte-scale data may take up to the 60-minute timeout.

**Three query languages are supported:**

| Language | Best for |
|---|---|
| **Logs Insights QL (CWLI)** | AWS-native; best integration with all Insights features (filterIndex, diff, pattern, anomaly) |
| **OpenSearch PPL** | Pipe-delimited transformations; familiar to OpenSearch users |
| **OpenSearch SQL** | SELECT/FROM/WHERE/JOIN/subquery syntax; SQL-fluent teams |

Use backticks around field names with special characters in PPL and SQL: `` `@message` ``, `` `Operation.Export` ``

---

## Limits & Quotas

| Limit | Value |
|---|---|
| Concurrent CWLI queries per account | 100 (includes dashboard queries) |
| Concurrent PPL/SQL queries per account | 15 |
| Query timeout | 60 minutes |
| Query results retention | 7 days |
| Max log groups per `start-query` | 50 (via `--log-group-names` or `--log-group-identifiers`) |
| Max rows returned per query | 10,000 |
| Max scheduled queries per account | 1,000 |
| Query string max length | 10,000 characters |
| Earliest queryable data | November 5, 2018 |

---

## Auto-Generated Fields

Every log event in every log group gets these system fields automatically:

| Field | Type | Description |
|---|---|---|
| `@timestamp` | Timestamp | Event time (from the log event timestamp) |
| `@message` | String | Raw log line |
| `@logStream` | String | Name of the log stream |
| `@log` | String | Log group identifier (account-id:log-group-name) |
| `@ingestionTime` | Timestamp | When CloudWatch received the event |
| `@ptr` | String | Pointer to the raw log record; use with `GetLogRecord` API to fetch full event |

**Lambda-specific auto-parsed fields** (from REPORT log lines):

| Field | Description |
|---|---|
| `@requestId` | Lambda invocation request ID |
| `@duration` | Billed + actual invocation duration in ms |
| `@billedDuration` | Rounded-up duration billed (ms) |
| `@memorySize` | Configured memory limit (bytes) |
| `@maxMemoryUsed` | Peak memory used during invocation (bytes) |
| `@initDuration` | Cold start init time in ms (only present on cold starts) |
| `@type` | Log line type: `START`, `END`, `REPORT` |
| `@xrayTraceId` | X-Ray trace ID (when X-Ray is enabled) |
| `@xraySegmentId` | X-Ray segment ID |

**VPC Flow Logs auto-parsed fields:**

`version`, `accountId`, `interfaceId`, `srcAddr`, `dstAddr`, `srcPort`, `dstPort`, `protocol`, `packets`, `bytes`, `start`, `end`, `action`, `logStatus`, `vpcId`, `subnetId`, `instanceId`, `tcpFlags`, `type`, `pktSrcAddr`, `pktDstAddr`, `region`, `az-id`, `sublocation-type`, `sublocation-id`, `pkt-src-aws-service`, `pkt-dst-aws-service`, `flow-direction`, `traffic-path`

**CloudTrail auto-parsed fields:**

`eventVersion`, `userIdentity.type`, `userIdentity.principalId`, `userIdentity.arn`, `userIdentity.accountId`, `eventTime`, `eventSource`, `eventName`, `awsRegion`, `sourceIPAddress`, `userAgent`, `errorCode`, `errorMessage`, `requestParameters`, `responseElements`, `requestId`, `eventId`, `readOnly`, `resources`, `eventType`, `managementEvent`, `recipientAccountId`, `tlsDetails.tlsVersion`, `tlsDetails.cipherSuite`

**Route 53 Resolver auto-parsed fields:**

`version`, `account`, `region`, `vpc-id`, `query-timestamp`, `query-name`, `query-type`, `query-class`, `rcode`, `answers`, `srcaddr`, `srcport`, `transport`, `srcids`, `resolverEndpoint`, `firewall-rule-action`, `firewall-domain-list-id`

**API Gateway Access Log fields** (when configured with JSON access log format):

`requestId`, `ip`, `caller`, `user`, `requestTime`, `httpMethod`, `resourcePath`, `status`, `protocol`, `responseLength`, `integrationLatency`, `responseLatency`, `path`, `error.message`

---

## Default Field Indexes (Auto-Created)

CloudWatch automatically indexes these fields for Standard class log groups — no configuration needed:

**Universal:**
`@logStream`, `@aws.region`, `@aws.account`, `@source.log`, `traceId`, `severityText`, `attributes.session.id`

**VPC Flow Logs:** `action`, `logStatus`, `region`, `flowDirection`, `type`

**CloudTrail:** `eventSource`, `eventName`, `awsRegion`, `userAgent`, `errorCode`, `eventType`, `managementEvent`, `readOnly`, `eventCategory`, `requestId`

**Route 53 Resolver:** `query_type`, `transport`, `rcode`

**WAF:** `action`, `httpRequest.country`

*Default indexes do not count toward your quota.*

---

## Query Language — Commands

### Command pipeline syntax
```
command1 | command2 | command3
```
Commands are separated by `|`. A `#` starts a line comment.

---

### `fields`
Display specific fields; create derived fields with expressions.

```
fields @timestamp, @message
fields @timestamp, @requestId, @duration / 1000 as durationSec
fields @timestamp, ispresent(@initDuration) as isColdStart
```

---

### `filter`
Return only matching log events. Supports comparison, boolean, string, regex, and set operators.

**Comparison operators:** `=`, `!=`, `<`, `<=`, `>`, `>=`

**Boolean operators:** `and`, `or`, `not`

**String substring matching:**
```
filter @message like "ERROR"           # case-sensitive substring
filter @message not like "REPORT"
filter @message like /(?i)exception/   # case-insensitive regex
```

**Regex operator `=~`:**
```
filter @message =~ /ERROR|WARN/
```

**Set membership:**
```
filter status in [400, 401, 403, 404]
filter eventName in ["StopInstances", "TerminateInstances"]
filter @logStream not in ["my-stream"]
```

**Field presence:**
```
filter ispresent(@initDuration)        # cold starts only
filter not ispresent(errorCode)        # no error
```

**Index-accelerated patterns** (use `=` or `IN`, not `like`):
```
filter requestId = "abc-123"
filter eventName = "CreateUser"
filter eventName in ["StopInstances", "TerminateInstances"]
```
> `like` scans all events; `=` and `IN` use field indexes when available.

---

### `stats`
Aggregate over the result set. Use `by` to group.

**Aggregation functions:**

| Function | Signature | Description |
|---|---|---|
| `count()` | `count()` or `count(field)` | Count events (or non-null field values) |
| `count_distinct` | `count_distinct(field)` | Unique value count (approximate for high cardinality) |
| `sum` | `sum(numericField)` | Sum |
| `avg` | `avg(numericField)` | Mean |
| `min` | `min(field)` | Minimum value |
| `max` | `max(field)` | Maximum value |
| `pct` | `pct(field, n)` | nth percentile; e.g., `pct(@duration, 99)` for p99 |
| `stddev` | `stddev(numericField)` | Standard deviation |
| `earliest` | `earliest(field)` | Value from the earliest-timestamped event in group |
| `latest` | `latest(field)` | Value from the latest-timestamped event in group |
| `sortsFirst` | `sortsFirst(field)` | Value that sorts first in the group |
| `sortsLast` | `sortsLast(field)` | Value that sorts last in the group |

```
stats count(*) as errorCount by bin(5m)
stats avg(@duration), pct(@duration, 99), max(@duration) by bin(5m)
stats sum(bytes) as totalBytes by srcAddr, dstAddr
stats count_distinct(@requestId) as uniqueRequests
```

---

### `sort`
Order results. `desc` (default) or `asc`.

```
sort @timestamp desc
sort errorCount desc
sort @duration asc
```

---

### `limit`
Cap the number of rows returned (max 10,000).

```
limit 20
limit 100
```

---

### `parse`
Extract values from a field into new named fields.

**Glob mode** — use `*` as wildcard:
```
parse @message "user=*, method:*, latency := *" as @user, @method, @latency
```

**Regex mode** — named capturing groups:
```
parse @message /user=(?<user>.*?), method:(?<method>.*?), latency := (?<latency>.*?)/
```

**Parse Lambda REPORT line for cold start init duration:**
```
parse @message /^REPORT.*Init Duration: (?<initDuration>[\d.]+) ms/
```

**Parse structured log lines:**
```
parse @message "* [*] *" as loggingTime, loggingType, loggingMessage
```

---

### `dedup`
Remove duplicate log events by one or more field values (keeps the most recent).

```
dedup @requestId
dedup server, severity
```

---

### `pattern`
Cluster log messages into recurring text patterns automatically. Returns a table of patterns with sample counts. Useful for understanding noise vs. signal in unstructured logs.

```
pattern @message
pattern @message | anomaly
```

> Not supported for Infrequent Access log class.

---

### `diff`
Compare the current time period against the prior equal-length period. Returns new events, resolved events, and changed patterns.

```
filter @message like /ERROR/ | diff
```

> Not supported for Infrequent Access log class.

---

### `unmask`
Show full content of log events where a data protection policy has masked sensitive data (PII, credentials).

```
fields @timestamp, @message | filter @message like /customer/ | unmask
```

> Not supported for Infrequent Access log class. Requires `logs:Unmask` IAM permission.

---

### `filterIndex`
Force the query to use field indexes; scan only events containing the indexed field value. Dramatically reduces bytesScanned for high-cardinality fields.

**Root field:**
```
fields @timestamp, @message | filterIndex requestId = "abc-123-xyz"
```

**Nested JSON:**
```
fields @timestamp, @message | filterIndex requestParameters.orderStatus = "pending"
```

**Array element:**
```
fields @timestamp, @message | filterIndex requestParameters.items.0.itemId = "1234"
```

Supports queries across up to **10,000 log groups** using up to **5 log group name prefixes**.

---

### `anomaly`
Identify unusual patterns using ML. Returns fields: `@description`, `@anomalyLogSamples`, `@priority`, `@priorityScore`, `@patternString`.

```
pattern @message | anomaly
filter @type = "REPORT" | fields @duration | anomaly
```

---

### `display`
Alias for `fields` — shows specific fields in output. Both are interchangeable.

```
display @timestamp, @message, status
```

---

### `unnest`
Flatten a list/array field into multiple rows (one per element).

```
fields jsonParse(@message) as msg | unnest msg.items as item | fields item.id, item.quantity
```

---

### `lookup`
Enrich log events with reference data from a lookup table.

```
fields @timestamp, userId | lookup userId from s3://my-bucket/users.csv
```

---

### `join`
Correlate events from two log sources on a shared key.

```
# Correlate orders and payments
fields o.correlationId, o.orderId, p.paymentStatus
| join (filter source="payments" | fields correlationId, paymentStatus) on correlationId
```

---

## Operators & Functions Reference

### Arithmetic operators
`+`, `-`, `*`, `/`, `^` (exponent: `2 ^ 10` = 1024), `%` (modulus: `10 % 3` = 1)

### Numeric functions

| Function | Description | Example |
|---|---|---|
| `abs(n)` | Absolute value | `abs(-5)` → `5` |
| `ceil(n)` | Round up to integer | `ceil(2.3)` → `3` |
| `floor(n)` | Round down to integer | `floor(2.9)` → `2` |
| `sqrt(n)` | Square root | `sqrt(9)` → `3` |
| `log(n)` | Natural logarithm | `log(2.718)` → `~1` |
| `greatest(a, b, ...)` | Largest value | `greatest(3, 7, 2)` → `7` |
| `least(a, b, ...)` | Smallest value | `least(3, 7, 2)` → `2` |

### Datetime functions

| Function | Signature | Description | Example |
|---|---|---|---|
| `bin` | `bin(period)` | Round `@timestamp` down to period boundary | `bin(5m)`, `bin(1h)`, `bin(1d)` |
| `datefloor` | `datefloor(ts, period)` | Truncate timestamp to period floor | `datefloor(@timestamp, 1h)` |
| `dateceil` | `dateceil(ts, period)` | Round timestamp up to next period | `dateceil(@timestamp, 1h)` |
| `fromMillis` | `fromMillis(n)` | Epoch milliseconds → Timestamp | `fromMillis(1642195111000)` |
| `toMillis` | `toMillis(ts)` | Timestamp → epoch milliseconds | `toMillis(@timestamp)` |
| `now` | `now()` | Current time in epoch seconds | `filter toMillis(@timestamp) >= (now() * 1000 - 7200000)` |

**Period unit abbreviations:** `ms` (millisecond), `s` (second), `m` (minute), `h` (hour), `d` (day), `w` (week), `mo`/`mon` (month), `q`/`qtr` (quarter), `y`/`yr` (year)

### String functions

| Function | Signature | Description | Example |
|---|---|---|---|
| `strlen` | `strlen(str)` | Length in Unicode code points | `strlen("hello")` → `5` |
| `substr` | `substr(str, start)` | Substring from index to end | `substr("hello", 2)` → `"llo"` |
| `substr` | `substr(str, start, len)` | Substring with length | `substr("hello", 1, 3)` → `"ell"` |
| `ltrim` | `ltrim(str)` | Remove leading whitespace | `ltrim("  hi")` → `"hi"` |
| `ltrim` | `ltrim(str, chars)` | Remove leading characters | `ltrim("xyZfoo", "xyZ")` → `"foo"` |
| `rtrim` | `rtrim(str)` | Remove trailing whitespace | — |
| `rtrim` | `rtrim(str, chars)` | Remove trailing characters | `rtrim("fooxyZ", "xyZ")` → `"foo"` |
| `trim` | `trim(str)` | Remove leading and trailing whitespace | — |
| `trim` | `trim(str, chars)` | Remove leading/trailing characters | `trim("xyZfooxyZ", "xyZ")` → `"foo"` |
| `tolower` | `tolower(str)` | Lowercase | `tolower("HELLO")` → `"hello"` |
| `toupper` | `toupper(str)` | Uppercase | `toupper("hello")` → `"HELLO"` |
| `concat` | `concat(a, b, ...)` | Concatenate strings | `concat("foo", "-", "bar")` → `"foo-bar"` |
| `replace` | `replace(str, search, replace)` | Replace all occurrences | `replace(logGroup, "test_", "")` |
| `strcontains` | `strcontains(str, search)` | Returns `1` if found, `0` if not | `strcontains(@message, "ERROR")` |

### General / conditional functions

| Function | Signature | Return | Description |
|---|---|---|---|
| `ispresent` | `ispresent(field)` | Boolean | Field exists in the log event |
| `isempty` | `isempty(field)` | Number (1/0) | Field is missing or empty string |
| `isblank` | `isblank(field)` | Number (1/0) | Field is missing, empty, or whitespace-only |
| `coalesce` | `coalesce(f1, f2, ...)` | First non-null | Return first non-null/non-missing field value |

### IP address functions

| Function | Description |
|---|---|
| `isValidIp(field)` | True if valid IPv4 or IPv6 |
| `isValidIpV4(field)` | True if valid IPv4 |
| `isValidIpV6(field)` | True if valid IPv6 |
| `isIpInSubnet(field, "cidr")` | True if IP is in v4 or v6 subnet (CIDR notation) |
| `isIpv4InSubnet(field, "cidr")` | True if IPv4 is in v4 subnet |
| `isIpv6InSubnet(field, "cidr")` | True if IPv6 is in v6 subnet |

### JSON functions

| Function | Signature | Description |
|---|---|---|
| `jsonParse` | `jsonParse(field)` | Parse JSON string to map or list |
| `jsonStringify` | `jsonStringify(field)` | Serialize map or list back to JSON string |

Access parsed JSON with dot notation (`json.key`) or bracket notation (`json.users[0].name`). Use backticks for keys with special characters: `` json.`user-id` ``.

---

## Field Indexes

### What they are
Structured metadata pre-computed at ingestion time for selected fields. When a query uses `filter field = value` or `filterIndex field = value`, the engine skips events that don't match — reducing bytesScanned and cost.

### Key properties
- **Only for equality and IN checks** — `like` patterns still scan all events
- **Only for JSON logs and AWS service logs** (not arbitrary text logs)
- **Only for log events ingested after** the index policy was created (not retroactive)
- **Indexed events retained for 30 days** from ingestion time
- **Case-sensitive**: `RequestId` ≠ `requestId`
- **Up to 10x faster** for high-cardinality fields (request IDs, transaction IDs)

### System default indexes
Lambda: `@requestId`, `@type`, `@initDuration`, `@duration`, `@billedDuration`, `@memorySize`, `@maxMemoryUsed`, `@xrayTraceId`, `@xraySegmentId`

(See "Default Field Indexes" section above for the full list by service.)

### Creating index policies (CLI)
```bash
# Account-level policy (applies to all log groups with prefix /aws/lambda/)
aws logs put-index-policy \
  --log-group-identifier "arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/*" \
  --policyDocument '{"Fields": ["requestId", "userId", "transactionId"]}'

# Single log group policy
aws logs put-index-policy \
  --log-group-identifier "/myapp/production" \
  --policyDocument '{"Fields": ["customerId", "orderId", "statusCode"]}'
```

### filterIndex command
```
# Force use of the index (queries up to 10,000 log groups via 5 prefixes)
fields @timestamp, @message
| filterIndex requestId = "abc-123"

# Nested JSON field
fields @timestamp, @message
| filterIndex requestParameters.orderStatus = "pending"
```

### Cost visibility
After running a query, the `statistics` object in the response shows:
- `bytesScanned` — actual bytes scanned (what you're billed for)
- `estimatedBytesSkipped` — bytes saved by field indexes
- `estimatedRecordsSkipped` — events skipped by field indexes

---

## Pattern Analysis

The `pattern` command automatically clusters log messages into recurring text structures, replacing variable parts (numbers, IDs, timestamps) with `<*>` tokens.

```
fields @message | pattern @message
```

Returns columns: `@pattern`, `@count`, `@ratio`, `@sampleLogs`

Combine with `anomaly` to surface unusual patterns:
```
fields @message | pattern @message | anomaly
```

---

## Saved Queries

Save frequently used queries for reuse across the team.

```bash
# Create (max 500 saved queries per account)
aws logs create-query-definition \
  --name "Lambda Cold Starts" \
  --log-group-names /aws/lambda/my-function \
  --query-string 'filter @type = "REPORT" | parse @message /Init Duration: (?<initDuration>[\d.]+) ms/ | stats avg(initDuration) by bin(1h)'

# List all saved queries
aws logs describe-query-definitions

# List by name prefix
aws logs describe-query-definitions --query-definition-name-prefix "Lambda"

# Delete
aws logs delete-query-definition --query-definition-id <id>
```

---

## Scheduled Queries

Automatically run queries on a cron schedule and deliver results to S3 or EventBridge.

**Key facts:**
- All executions run in **UTC**
- Results delivered as JSON
- EventBridge results queryable via queryId for **30 days**
- Max **1,000 scheduled queries per account**
- All three query languages (CWLI, PPL, SQL) are supported

**IAM requirements:**
- Execution role: `logs:StartQuery`, `logs:GetQueryResults`, `logs:DescribeLogGroups`
- S3 destination role: `s3:PutObject`

**Schedule expression:** Standard cron format: `cron(minute hour day-of-month month day-of-week year)`

**Result delivery format (EventBridge event detail):**
```json
{
  "queryId": "2038fd57-...",
  "queryString": "fields @timestamp, @message | limit 10000",
  "logGroupIdentifiers": ["/aws/lambda/my-function"],
  "status": "Complete",
  "startTime": 1763465460,
  "statistics": {
    "recordsMatched": 1234,
    "recordsScanned": 50000,
    "estimatedRecordsSkipped": 0,
    "bytesScanned": 2097152,
    "estimatedBytesSkipped": 0,
    "logGroupsScanned": 1
  }
}
```

---

## Cross-Log-Group and Cross-Account Queries

**Cross-log-group (same account):**
```bash
aws logs start-query \
  --log-group-names /aws/lambda/func-a /aws/lambda/func-b /myapp/api \
  --start-time 1704067200 --end-time 1704154800 \
  --query-string 'filter @message like /ERROR/ | stats count(*) by @log'
```

**Cross-account:** Requires CloudWatch cross-account observability setup (monitoring + source accounts). Use `--log-group-identifiers` with full ARNs:
```bash
aws logs start-query \
  --log-group-identifiers \
    "arn:aws:logs:us-east-1:111122223333:log-group:/aws/lambda/func-a" \
    "arn:aws:logs:us-east-1:444455556666:log-group:/myapp/prod" \
  --start-time 1704067200 --end-time 1704154800 \
  --query-string 'fields @timestamp, @message, @log | filter @message like /ERROR/'
```

---

## Diff Command

Compare event patterns between the current time window and the immediately prior equal-length window.

```
filter @message like /ERROR/ | diff
stats count(*) as errors by errorCode | diff
```

Use cases: detect regressions after a deployment, find new error patterns, compare before/after traffic.

---

## Embedded Metrics Format (EMF)

EMF lets applications embed metric definitions in log events; CloudWatch auto-extracts them as real metrics with no separate API call. Properties that are NOT metrics stay in the log and are queryable here. See [cloudwatch-emf-capabilities.md](cloudwatch-emf-capabilities.md) for full reference.

```
# Query EMF property context alongside extracted metrics
filter Service = "OrderService" and ProcessingLatency > 500
| fields RequestId, UserId, OrderId, ProcessingLatency, @timestamp
| sort ProcessingLatency desc
```

---

## Performance & Cost

- **Billed per byte scanned** (compressed). Check `bytesScanned` in query statistics.
- **Field indexes** can reduce scanned bytes by orders of magnitude for equality queries.
- **Narrow time ranges** reduce scan volume — always use the shortest range that covers your question.
- **Select only needed fields** — `fields a, b` is cheaper than `fields *` when log events are large.
- **`filter` before `stats`** — push filters as early in the pipeline as possible.
- **Avoid `like` on indexed fields** — use `=` to benefit from field indexes.
- **Dashboard refresh** — Logs Insights widgets on dashboards count against the 100-query concurrency limit; use long refresh intervals.
- **Query timeout** is 60 minutes. Cancel and narrow the query if it times out.

---

## Console Features

- **Query editor**: Syntax highlighting, auto-complete for field names (from automatically discovered fields).
- **Auto-discovered fields**: Panel shows fields found in recent log events with value distributions.
- **Visualization**: Bar charts, line charts, stacked area charts from `stats ... by bin(period)` queries.
- **Export**: Download results as CSV or JSON.
- **Query history**: Re-run any previous query.
- **Saved queries**: Shared across the account; accessible in the console query library.
- **Surrounding logs**: From any row, view 5/10/20/50/100 log events before and after it.
- **Natural language query**: Describe what you want in plain English; console generates the query.
- **Dashboard widgets**: Add any Logs Insights query as a widget to a CloudWatch dashboard (bar, line, number, table).
- **Alarms**: You cannot create CloudWatch Alarms directly from a Logs Insights query. Use metric filters on log groups to generate a metric, then alarm on that metric.

---

## Example Queries

### General

```
# Most recent 25 log events
fields @timestamp, @message
| sort @timestamp desc
| limit 25

# Count exceptions per hour
filter @message like /Exception/
| stats count(*) as exceptionCount by bin(1h)
| sort exceptionCount desc

# Events without exceptions
fields @message
| filter @message not like /Exception/

# Dedup by server, keep most recent per severity
fields @timestamp, server, severity, message
| sort @timestamp desc
| dedup server, severity
```

### Lambda

```
# All Lambda errors (filter out infrastructure lines)
fields @timestamp, @message
| sort @timestamp desc
| filter @message not like 'EXTENSION'
| filter @message not like 'Lambda Insights'
| filter @message not like 'INFO'
| filter @message not like 'REPORT'
| filter @message not like 'END'
| filter @message not like 'START'

# Duration stats per 5-minute window
filter @type = "REPORT"
| stats avg(@duration), max(@duration), min(@duration), pct(@duration, 99) by bin(5m)

# Over-provisioned memory analysis
filter @type = "REPORT"
| stats max(@memorySize / 1000000) as provisionedMB,
        min(@maxMemoryUsed / 1000000) as minUsedMB,
        avg(@maxMemoryUsed / 1000000) as avgUsedMB,
        max(@maxMemoryUsed / 1000000) as maxUsedMB,
        max(@memorySize / 1000000) - max(@maxMemoryUsed / 1000000) as overProvisionedMB

# Cold start analysis — avg init duration by function and memory
filter @type = "REPORT"
| fields @memorySize / 1000000 as memoryMB
| filter @message like /(?i)(Init Duration)/
| parse @message /^REPORT.*Init Duration: (?<initDuration>[\d.]+) ms/
| parse @log /^.*\/aws\/lambda\/(?<functionName>.*)/
| stats count() as coldStarts, avg(initDuration) as avgInitMs, max(initDuration) as maxInitMs
    by functionName, memoryMB

# Cold start rate over time (% of invocations that were cold)
filter @type = "REPORT"
| stats sum(strcontains(@message, "Init Duration")) / count(*) * 100 as coldStartPct,
        avg(@duration) as avgDurationMs
    by bin(5m)

# Timeouts (identify slow invocations over threshold)
filter @type = "REPORT" and @duration > 1000
| fields @timestamp, @requestId, @duration, @logStream
| sort @timestamp desc
| dedup @requestId
| limit 20

# Most expensive invocations by billed duration
filter @type = "REPORT"
| fields @requestId, @billedDuration
| sort @billedDuration desc
| limit 25
```

### API Gateway

```
# 4xx errors — recent list
fields @timestamp, status, ip, path, httpMethod
| filter status >= 400 and status <= 499
| sort @timestamp desc
| limit 10

# Slowest requests
fields @timestamp, status, ip, path, httpMethod, responseLatency
| sort responseLatency desc
| limit 10

# Request counts by path
stats count(*) as requestCount by path
| sort requestCount desc
| limit 10

# Integration latency over time (avg/max/min per minute)
filter status = 200
| stats avg(integrationLatency), max(integrationLatency), min(integrationLatency) by bin(1m)
```

### VPC Flow Logs

```
# Top packet talkers
stats sum(packets) as packetsTransferred by srcAddr, dstAddr
| sort packetsTransferred desc
| limit 15

# Top byte consumers from a specific subnet
filter isIpv4InSubnet(srcAddr, "10.0.1.0/24")
| stats sum(bytes) as bytesTransferred by dstAddr
| sort bytesTransferred desc
| limit 15

# UDP traffic count by source
filter protocol = 17
| stats count(*) by srcAddr

# SKIPDATA events (indicates log loss due to capacity)
filter logStatus = "SKIPDATA"
| stats count(*) by bin(1h) as t
| sort t

# Recent traffic on a specific ENI with dedup
fields @timestamp, srcAddr, dstAddr, srcPort, dstPort, protocol, bytes
| filter interfaceId = "eni-0123456789abcdef0"
| sort @timestamp desc
| dedup srcAddr, dstAddr, srcPort, dstPort, protocol
| limit 20

# REJECT traffic by source IP
filter action = "REJECT"
| stats count(*) as rejectCount by srcAddr
| sort rejectCount desc
| limit 20

# Cross-AZ data transfer cost analysis
stats sum(bytes / 1048576) as trafficMB by azId as AZ_ID
| sort trafficMB desc

# Top data transfers (all directions)
stats sum(bytes / 1048576) as dataMB by srcAddr as Source_IP, dstAddr as Dest_IP
| sort dataMB desc
| limit 10
```

### CloudTrail

```
# Event counts by source, name, region
stats count(*) by eventSource, eventName, awsRegion

# EC2 start/stop events in a specific region
filter (eventName = "StartInstances" or eventName = "StopInstances")
    and awsRegion = "us-east-2"

# New IAM users created
filter eventName = "CreateUser"
| fields awsRegion, requestParameters.userName, responseElements.user.arn

# Failed UpdateTrail calls (error code)
filter eventName = "UpdateTrail" and ispresent(errorCode)
| stats count(*) by errorCode, errorMessage

# Root account activity
fields @timestamp, @message, userIdentity.type
| filter userIdentity.type = "Root"
| stats count() as RootActivity by bin(5m)

# Unauthorized API call attempts (ThrottlingException)
stats count(errorCode) as eventCount by eventSource, eventName, awsRegion, userAgent, errorCode
| filter errorCode = "ThrottlingException"
| sort eventCount desc

# Outdated TLS usage
filter tlsDetails.tlsVersion in ["TLSv1", "TLSv1.1"]
| stats count(*) as numOutdatedTlsCalls
    by userIdentity.accountId, recipientAccountId, eventSource, eventName,
       awsRegion, tlsDetails.tlsVersion, tlsDetails.cipherSuite, userAgent
| sort eventSource, eventName

# Outdated TLS — summarized by service
filter tlsDetails.tlsVersion in ["TLSv1", "TLSv1.1"]
| stats count(*) as numOutdatedTlsCalls by eventSource
| sort numOutdatedTlsCalls desc
```

### Route 53

```
# Query type distribution per hour
stats count(*) by queryType, bin(1h)

# Top resolver IPs by request volume
stats count(*) as numRequests by resolverIp
| sort numRequests desc
| limit 10

# SERVFAIL responses by query name
filter responseCode = "SERVFAIL"
| stats count(*) by queryName
```

### NAT Gateway

```
# Data transferred through NAT to a specific external IP
filter dstAddr like "203.0.113." and srcAddr like "10.0."
| stats sum(bytes) as bytesTransferred by srcAddr, dstAddr
| sort bytesTransferred desc
| limit 10

# Egress not going to internal ranges
filter srcAddr like "10.0.0.1" and dstAddr not like "10."
| stats sum(bytes) as bytesTransferred by srcAddr, dstAddr
| sort bytesTransferred desc
| limit 10
```

### Apache

```
# Recent requests to admin path
fields @timestamp, remoteIP, request, status, filename
| sort @timestamp desc
| filter filename = "/var/www/html/admin"
| limit 20

# Unique visitor count for GET 200 from a referrer
fields @timestamp, remoteIP, method, status
| filter status = "200" and method = "GET"
| stats count_distinct(remoteIP) as UniqueVisits
| limit 10
```

### EventBridge

```
# Event counts by detail-type
fields @timestamp, @message
| stats count(*) as numberOfEvents by `detail-type`
| sort numberOfEvents desc
```

### Parse examples

```
# Glob parse — extract user, method, latency
parse @message "user=*, method:*, latency := *" as @user, @method, @latency
| stats avg(@latency) by @method, @user

# Regex parse — same fields
parse @message /user=(?<user>.*?), method:(?<method>.*?), latency := (?<latency>.*?)/
| stats avg(latency) by method, user

# Structured log parse
parse @message "* [*] *" as loggingTime, loggingType, loggingMessage
| filter loggingType in ["ERROR", "INFO"]
| display loggingMessage, loggingType = "ERROR" as isError

# VPC ENI extraction
parse @message /(?<NetworkInterface>eni-.*?) /
| display NetworkInterface, @message
```

### SNS delivery failures

```
# Failure count by provider response
filter status = "FAILURE"
| stats count(*) by delivery.providerResponse as FailureReason
| sort delivery.providerResponse desc

# Invalid phone numbers
fields notification.messageId as MessageId, delivery.destination as PhoneNumber
| filter status = "FAILURE" and delivery.providerResponse = "Invalid phone number"
| limit 100
```
