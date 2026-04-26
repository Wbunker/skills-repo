# CloudWatch Logs Insights — CLI Reference
For service concepts, see [cloudwatch-logs-insights-capabilities.md](cloudwatch-logs-insights-capabilities.md).

```bash
# ============================================================
# RUNNING QUERIES
# ============================================================

# Start a query — single log group
aws logs start-query \
  --log-group-name "/aws/lambda/my-function" \
  --start-time 1704067200 \
  --end-time 1704154800 \
  --query-string 'fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 20'
# Returns: {"queryId": "abc123..."}

# Start a query — multiple log groups (up to 50)
aws logs start-query \
  --log-group-names "/aws/lambda/func-a" "/aws/lambda/func-b" "/myapp/api" \
  --start-time 1704067200 \
  --end-time 1704154800 \
  --query-string 'filter @message like /ERROR/ | stats count(*) by @log | sort count DESC'

# Start a query — cross-account using ARNs
aws logs start-query \
  --log-group-identifiers \
    "arn:aws:logs:us-east-1:111122223333:log-group:/aws/lambda/func-a" \
    "arn:aws:logs:us-east-1:444455556666:log-group:/myapp/prod" \
  --start-time 1704067200 \
  --end-time 1704154800 \
  --query-string 'fields @timestamp, @message, @log | filter @message like /ERROR/'

# Start a query with explicit result limit (default and max: 10000)
aws logs start-query \
  --log-group-name "/myapp/production" \
  --start-time 1704067200 \
  --end-time 1704154800 \
  --limit 100 \
  --query-string 'fields @timestamp, @message | sort @timestamp desc'

# Start a query using OpenSearch SQL
aws logs start-query \
  --log-group-name "/myapp/production" \
  --start-time 1704067200 \
  --end-time 1704154800 \
  --query-language SQL \
  --query-string "SELECT eventName, COUNT(*) as cnt FROM loggroupname GROUP BY eventName ORDER BY cnt DESC LIMIT 10"

# Start a query using OpenSearch PPL
aws logs start-query \
  --log-group-name "/myapp/production" \
  --start-time 1704067200 \
  --end-time 1704154800 \
  --query-language PPL \
  --query-string "fields timestamp, correlationId | where paymentStatus='completed' | head 10"

# ============================================================
# GET QUERY RESULTS
# ============================================================

# Get results for a completed query
aws logs get-query-results --query-id "abc123..."

# Get results with pagination (max-items per call)
aws logs get-query-results \
  --query-id "abc123..." \
  --max-items 500

# Example response structure:
# {
#   "queryLanguage": "CWLI",
#   "results": [
#     [
#       {"field": "@timestamp", "value": "2024-01-01 00:00:00.000"},
#       {"field": "@message",   "value": "ERROR ..."},
#       {"field": "@ptr",       "value": "<opaque pointer for GetLogRecord>"}
#     ]
#   ],
#   "statistics": {
#     "recordsMatched": 42,
#     "recordsScanned": 100000,
#     "bytesScanned": 1048576,
#     "estimatedRecordsSkipped": 0,
#     "estimatedBytesSkipped": 0,
#     "logGroupsScanned": 1
#   },
#   "status": "Complete"   # Scheduled | Running | Complete | Failed | Cancelled | Timeout | Unknown
# }

# ============================================================
# POLLING PATTERN (bash script)
# ============================================================

START_TIME=$(date -d '1 hour ago' +%s)   # Linux; use gdate on macOS
END_TIME=$(date +%s)

QUERY_ID=$(aws logs start-query \
  --log-group-name "/aws/lambda/my-function" \
  --start-time "$START_TIME" \
  --end-time "$END_TIME" \
  --query-string 'filter @type = "REPORT" | stats avg(@duration) by bin(5m)' \
  --output text --query 'queryId')

echo "Query ID: $QUERY_ID"

while true; do
  STATUS=$(aws logs get-query-results \
    --query-id "$QUERY_ID" \
    --output text --query 'status')
  echo "Status: $STATUS"
  if [[ "$STATUS" == "Complete" || "$STATUS" == "Failed" || "$STATUS" == "Cancelled" || "$STATUS" == "Timeout" ]]; then
    break
  fi
  sleep 3
done

aws logs get-query-results --query-id "$QUERY_ID"

# ============================================================
# STOP A RUNNING QUERY
# ============================================================

aws logs stop-query --query-id "abc123..."
# Returns: {"success": true}

# ============================================================
# DESCRIBE QUERIES (list recent / running queries)
# ============================================================

# List all recent queries for an account
aws logs describe-queries

# Filter by log group
aws logs describe-queries --log-group-name "/aws/lambda/my-function"

# Filter by status
aws logs describe-queries --status Running
aws logs describe-queries --status Complete
# Valid statuses: Scheduled | Running | Complete | Failed | Cancelled | Timeout | Unknown

# Filter by language
aws logs describe-queries --query-language CWLI
aws logs describe-queries --query-language SQL
aws logs describe-queries --query-language PPL

# Paginate results
aws logs describe-queries --max-items 20

# Output format shows per query:
# queryId, queryString, status, createTime, logGroupName, queryDuration, bytesScanned, userIdentity

# ============================================================
# SAVED QUERIES (QUERY DEFINITIONS)
# ============================================================

# Create a saved query (associates with specific log group(s))
aws logs create-query-definition \
  --name "Lambda Cold Starts" \
  --log-group-names "/aws/lambda/my-function" \
  --query-string 'filter @type = "REPORT" | parse @message /Init Duration: (?<initDuration>[\d.]+) ms/ | stats avg(initDuration) as avgInitMs, count() as coldStarts by bin(1h)'

# Create a saved query without log group (generic/reusable)
aws logs create-query-definition \
  --name "Top Errors Last Hour" \
  --query-string 'filter @message like /ERROR/ | stats count(*) as errorCount by bin(5m) | sort errorCount desc'

# List all saved queries
aws logs describe-query-definitions

# List by name prefix
aws logs describe-query-definitions --query-definition-name-prefix "Lambda"

# Delete a saved query
aws logs delete-query-definition --query-definition-id "qdef-abc123..."

# ============================================================
# SCHEDULED QUERIES
# ============================================================

# Create a scheduled query (results → S3)
aws logs create-scheduled-query \
  --name "HourlyErrorReport" \
  --query-language "CWLI" \
  --query-string "filter @message like /ERROR/ | stats count() by bin(5m)" \
  --schedule-expression "cron(0 * * * ? *)" \
  --execution-role-arn "arn:aws:iam::123456789012:role/CWLScheduledQueryRole" \
  --log-group-identifiers "/aws/lambda/my-function" "/myapp/api" \
  --state "ENABLED" \
  --query-start-time "PREVIOUS_HOUR_START" \
  --query-end-time "PREVIOUS_HOUR_END" \
  --destination-s3 '{"bucket": "my-query-results", "prefix": "hourly-errors/"}'

# Create a scheduled query (results → EventBridge)
aws logs create-scheduled-query \
  --name "DailySecurityScan" \
  --query-language "CWLI" \
  --query-string "filter eventName in [\"CreateUser\",\"DeleteUser\",\"AttachUserPolicy\"] | fields awsRegion, eventName, userIdentity.arn" \
  --schedule-expression "cron(0 6 * * ? *)" \
  --execution-role-arn "arn:aws:iam::123456789012:role/CWLScheduledQueryRole" \
  --log-group-identifiers "arn:aws:logs:us-east-1:123456789012:log-group:aws-cloudtrail-logs" \
  --state "ENABLED"

# List scheduled queries
aws logs describe-scheduled-queries

# Disable/enable a scheduled query
aws logs update-scheduled-query \
  --scheduled-query-arn "arn:aws:logs:us-east-1:123456789012:scheduled-query:HourlyErrorReport" \
  --state DISABLED

# Delete a scheduled query
aws logs delete-scheduled-query \
  --scheduled-query-arn "arn:aws:logs:us-east-1:123456789012:scheduled-query:HourlyErrorReport"

# ============================================================
# FIELD INDEX POLICIES
# ============================================================

# Create an account-level index policy (prefix-based)
aws logs put-index-policy \
  --log-group-identifier "arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/*" \
  --policy-document '{"Fields": ["requestId", "userId", "transactionId"]}'

# Create a log-group-level index policy
aws logs put-index-policy \
  --log-group-identifier "/myapp/production" \
  --policy-document '{"Fields": ["customerId", "orderId", "statusCode", "errorCode"]}'

# Describe index policies
aws logs describe-index-policies

# Delete an index policy
aws logs delete-index-policy \
  --log-group-identifier "/myapp/production"

# ============================================================
# RETRIEVE FULL LOG RECORD (using @ptr)
# ============================================================

# Use the @ptr pointer from query results to get the full log event
aws logs get-log-record \
  --log-record-pointer "<value of @ptr field from query result>"

# ============================================================
# USEFUL COMBINATIONS
# ============================================================

# Count errors in last 24 hours (epoch arithmetic with macOS date)
END=$(date +%s)
START=$((END - 86400))
aws logs start-query \
  --log-group-name "/aws/lambda/my-function" \
  --start-time $START --end-time $END \
  --query-string 'filter @message like /ERROR/ | stats count(*) as errors by bin(1h) | sort errors desc' \
  --output text --query 'queryId'

# Capture bytes scanned after query completes (cost visibility)
aws logs get-query-results \
  --query-id "$QUERY_ID" \
  --output json \
  --query 'statistics'
# Returns: {"recordsMatched": N, "recordsScanned": N, "bytesScanned": N, "estimatedBytesSkipped": N}
```
