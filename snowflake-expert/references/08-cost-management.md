# Managing Snowflake Account Costs and FinOps

Reference for billing, resource monitors, cost optimization, FinOps framework, budgets, chargeback/showback, and DevOps.

## Table of Contents
- [FinOps Framework for Snowflake](#finops-framework-for-snowflake)
- [Billing Components](#billing-components)
- [Storage Costs](#storage-costs)
- [Compute Costs](#compute-costs)
- [Cloud Services Layer Costs](#cloud-services-layer-costs)
- [Serverless Feature Costs](#serverless-feature-costs)
- [Data Transfer Costs](#data-transfer-costs)
- [Resource Monitors](#resource-monitors)
- [Budgets](#budgets)
- [Chargeback and Showback Models](#chargeback-and-showback-models)
- [Cost Optimization Strategies](#cost-optimization-strategies)
- [Query Acceleration Service](#query-acceleration-service)
- [Dynamic Tables Cost Management](#dynamic-tables-cost-management)
- [Replication Cost Optimization](#replication-cost-optimization)
- [Cortex AI and ML Cost Management](#cortex-ai-and-ml-cost-management)
- [Spend Anomaly Detection](#spend-anomaly-detection)
- [Object Tagging for Cost Centers](#object-tagging-for-cost-centers)
- [DevOps and Change Management](#devops-and-change-management)

## FinOps Framework for Snowflake

FinOps (Cloud Financial Operations) is a framework for managing cloud costs through collaboration between finance, engineering, and business teams. Applied to Snowflake, it follows three progressive phases:

### Phase 1: Visibility and Transparency (Inform)
- **Goal:** Understand where money is being spent
- Establish tagging and governance practices
- Implement cost monitoring dashboards
- Break down spend by team, project, and workload
- Use ACCOUNT_USAGE views for historical analysis

### Phase 2: Control and Budgeting (Control)
- **Goal:** Prevent waste and set guardrails
- Deploy resource monitors and budgets
- Set statement timeouts and queuing limits
- Implement chargeback/showback models
- Establish approval workflows for warehouse creation

### Phase 3: Optimization (Optimize)
- **Goal:** Maximize value per credit spent
- Right-size warehouses based on workload analysis
- Optimize queries, clustering, and data modeling
- Automate suspend/resume policies
- Continuously review and adjust

## Billing Components

Snowflake bills for three categories:

| Component | Billing Unit | Key Driver |
|-----------|-------------|-----------|
| **Compute** | Credits/second (60s min) | Warehouse size × runtime |
| **Storage** | $/TB/month (compressed) | Active data + Time Travel + Fail-Safe |
| **Data Transfer** | $/TB | Cross-region or cross-cloud egress |
| **Serverless** | Credits | Snowpipe, auto-clustering, replication, search optimization |

### Credit Pricing
- Credit prices vary by edition and cloud provider/region
- Standard: ~$2/credit, Enterprise: ~$3/credit, Business Critical: ~$4/credit (approximate)
- On-demand vs pre-purchased capacity (discounts for commitment)

## Storage Costs

```sql
-- Check current storage usage
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.STORAGE_USAGE
ORDER BY USAGE_DATE DESC LIMIT 30;

-- Storage breakdown by table
SELECT
  TABLE_CATALOG AS database,
  TABLE_SCHEMA AS schema,
  TABLE_NAME AS table_name,
  ACTIVE_BYTES / POWER(1024, 3) AS active_gb,
  TIME_TRAVEL_BYTES / POWER(1024, 3) AS time_travel_gb,
  FAILSAFE_BYTES / POWER(1024, 3) AS failsafe_gb,
  (ACTIVE_BYTES + TIME_TRAVEL_BYTES + FAILSAFE_BYTES) / POWER(1024, 3) AS total_gb
FROM SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS
WHERE TABLE_CATALOG = 'MY_DB'
ORDER BY total_gb DESC;

-- Stage storage
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.STAGE_STORAGE_USAGE_HISTORY
ORDER BY USAGE_DATE DESC;
```

### Reducing Storage Costs
- Use **transient tables** for staging (no fail-safe)
- Set shorter **Time Travel** retention for non-critical tables
- Purge files from stages after loading (`PURGE = TRUE`)
- Drop unused clones (clones share storage until data diverges)
- Truncate or drop unused tables

## Compute Costs

```sql
-- Warehouse credit usage
SELECT
  WAREHOUSE_NAME,
  SUM(CREDITS_USED) AS total_credits,
  SUM(CREDITS_USED_COMPUTE) AS compute_credits,
  SUM(CREDITS_USED_CLOUD_SERVICES) AS cloud_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE START_TIME >= DATEADD('DAY', -30, CURRENT_TIMESTAMP())
GROUP BY WAREHOUSE_NAME
ORDER BY total_credits DESC;

-- Serverless credit usage
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.SERVERLESS_TASK_HISTORY;
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.PIPE_USAGE_HISTORY;
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.AUTOMATIC_CLUSTERING_HISTORY;
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.SEARCH_OPTIMIZATION_HISTORY;
```

### Compute Cost Levers
```sql
-- 1. Right-size warehouses
ALTER WAREHOUSE my_wh SET WAREHOUSE_SIZE = 'SMALL';  -- downsize if over-provisioned

-- 2. Aggressive auto-suspend for batch warehouses
ALTER WAREHOUSE etl_wh SET AUTO_SUSPEND = 60;  -- 1 minute

-- 3. Moderate auto-suspend for interactive warehouses (preserve SSD cache)
ALTER WAREHOUSE analyst_wh SET AUTO_SUSPEND = 300;  -- 5 minutes

-- 4. Use multicluster economy policy for concurrency
ALTER WAREHOUSE analyst_wh SET SCALING_POLICY = 'ECONOMY';

-- 5. Set statement timeouts
ALTER WAREHOUSE analyst_wh SET STATEMENT_TIMEOUT_IN_SECONDS = 3600;  -- 1 hour max
ALTER WAREHOUSE dev_wh SET STATEMENT_TIMEOUT_IN_SECONDS = 300;       -- 5 min for dev

-- 6. Set query queuing timeout
ALTER WAREHOUSE analyst_wh SET STATEMENT_QUEUED_TIMEOUT_IN_SECONDS = 600;
```

## Cloud Services Layer Costs

The cloud services layer handles metadata operations, authentication, query parsing, optimization, and access control.

### 10% Credit Allowance
- Cloud services usage up to **10% of daily compute credits** is **free**
- Only the excess above 10% is billed
- Heavy metadata operations (SHOW, DESCRIBE, INFORMATION_SCHEMA queries) can exceed this

```sql
-- Monitor cloud services credits
SELECT
  DATE_TRUNC('DAY', START_TIME) AS day,
  SUM(CREDITS_USED_COMPUTE) AS compute_credits,
  SUM(CREDITS_USED_CLOUD_SERVICES) AS cloud_credits,
  ROUND(cloud_credits / NULLIF(compute_credits, 0) * 100, 1) AS cloud_pct,
  GREATEST(cloud_credits - compute_credits * 0.1, 0) AS billable_cloud_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE START_TIME >= DATEADD('DAY', -30, CURRENT_TIMESTAMP())
GROUP BY 1
ORDER BY 1 DESC;
```

### Reducing Cloud Services Costs
- Avoid excessive `SHOW` and `DESCRIBE` commands in automation
- Cache INFORMATION_SCHEMA results instead of re-querying
- Use ACCOUNT_USAGE views (less overhead) instead of INFORMATION_SCHEMA for monitoring
- Reduce frequency of metadata-heavy monitoring scripts

## Serverless Feature Costs

Serverless features consume credits without a user-managed warehouse.

| Feature | Credit Type | Monitoring View |
|---------|------------|----------------|
| **Snowpipe** | Serverless | `PIPE_USAGE_HISTORY` |
| **Auto-clustering** | Serverless | `AUTOMATIC_CLUSTERING_HISTORY` |
| **Materialized views** | Serverless | `MATERIALIZED_VIEW_REFRESH_HISTORY` |
| **Search optimization** | Serverless + storage | `SEARCH_OPTIMIZATION_HISTORY` |
| **Replication** | Serverless | `REPLICATION_USAGE_HISTORY` |
| **Tasks (serverless)** | Serverless | `SERVERLESS_TASK_HISTORY` |
| **Query Acceleration** | Serverless | `QUERY_ACCELERATION_HISTORY` |

```sql
-- Comprehensive serverless spend summary
SELECT 'Snowpipe' AS service, SUM(CREDITS_USED) AS credits
FROM SNOWFLAKE.ACCOUNT_USAGE.PIPE_USAGE_HISTORY
WHERE START_TIME >= DATEADD('MONTH', -1, CURRENT_TIMESTAMP())
UNION ALL
SELECT 'Auto-clustering', SUM(CREDITS_USED)
FROM SNOWFLAKE.ACCOUNT_USAGE.AUTOMATIC_CLUSTERING_HISTORY
WHERE START_TIME >= DATEADD('MONTH', -1, CURRENT_TIMESTAMP())
UNION ALL
SELECT 'Materialized Views', SUM(CREDITS_USED)
FROM SNOWFLAKE.ACCOUNT_USAGE.MATERIALIZED_VIEW_REFRESH_HISTORY
WHERE START_TIME >= DATEADD('MONTH', -1, CURRENT_TIMESTAMP())
UNION ALL
SELECT 'Search Optimization', SUM(CREDITS_USED)
FROM SNOWFLAKE.ACCOUNT_USAGE.SEARCH_OPTIMIZATION_HISTORY
WHERE START_TIME >= DATEADD('MONTH', -1, CURRENT_TIMESTAMP())
UNION ALL
SELECT 'Replication', SUM(CREDITS_USED)
FROM SNOWFLAKE.ACCOUNT_USAGE.REPLICATION_USAGE_HISTORY
WHERE START_TIME >= DATEADD('MONTH', -1, CURRENT_TIMESTAMP())
UNION ALL
SELECT 'Serverless Tasks', SUM(CREDITS_USED)
FROM SNOWFLAKE.ACCOUNT_USAGE.SERVERLESS_TASK_HISTORY
WHERE START_TIME >= DATEADD('MONTH', -1, CURRENT_TIMESTAMP())
ORDER BY credits DESC;
```

## Data Transfer Costs

- **Same region, same cloud:** Free
- **Cross-region or cross-cloud:** Billed per TB transferred
- Applies to: data sharing (cross-region), replication, COPY INTO external locations

```sql
-- Monitor data transfer
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.DATA_TRANSFER_HISTORY
ORDER BY START_TIME DESC;
```

## Resource Monitors

Resource monitors set credit usage limits and trigger alerts or suspension.

```sql
-- Create resource monitor
CREATE RESOURCE MONITOR monthly_limit
  WITH
    CREDIT_QUOTA = 5000                  -- monthly credit budget
    FREQUENCY = MONTHLY
    START_TIMESTAMP = IMMEDIATELY
    TRIGGERS
      ON 75 PERCENT DO NOTIFY           -- email alert at 75%
      ON 90 PERCENT DO NOTIFY           -- email alert at 90%
      ON 100 PERCENT DO SUSPEND         -- suspend warehouses at 100%
      ON 110 PERCENT DO SUSPEND_IMMEDIATE;  -- kill running queries at 110%

-- Assign to account
ALTER ACCOUNT SET RESOURCE_MONITOR = monthly_limit;

-- Assign to specific warehouse
ALTER WAREHOUSE analytics_wh SET RESOURCE_MONITOR = analytics_monitor;

-- Create warehouse-specific monitor
CREATE RESOURCE MONITOR etl_monitor
  WITH
    CREDIT_QUOTA = 1000
    FREQUENCY = WEEKLY
    START_TIMESTAMP = IMMEDIATELY
    TRIGGERS
      ON 90 PERCENT DO NOTIFY
      ON 100 PERCENT DO SUSPEND;

ALTER WAREHOUSE etl_wh SET RESOURCE_MONITOR = etl_monitor;
```

### Resource Monitor Actions
| Trigger Action | Behavior |
|---------------|----------|
| `NOTIFY` | Send notification (email) |
| `SUSPEND` | Suspend warehouse after current queries finish |
| `SUSPEND_IMMEDIATE` | Kill running queries and suspend immediately |

### Monitoring Resource Monitors
```sql
SHOW RESOURCE MONITORS;

SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.RESOURCE_MONITORS;
```

## Budgets

Budgets are a newer Snowflake feature that provide more granular cost tracking than resource monitors, covering warehouses, serverless features, and storage.

```sql
-- Create a budget for a specific cost center
-- (Budgets are managed through Snowsight UI or SQL)

-- Account-level budget
CREATE SNOWFLAKE.CORE.BUDGET account_budget();
CALL account_budget!SET_SPENDING_LIMIT(5000);  -- monthly limit in credits

-- Custom budget scoped to specific objects
CREATE SNOWFLAKE.CORE.BUDGET analytics_budget();
CALL analytics_budget!SET_SPENDING_LIMIT(2000);
CALL analytics_budget!ADD_RESOURCE(
  SYSTEM$REFERENCE('WAREHOUSE', 'ANALYTICS_WH')
);
CALL analytics_budget!ADD_RESOURCE(
  SYSTEM$REFERENCE('WAREHOUSE', 'REPORTING_WH')
);

-- Check budget status
CALL account_budget!GET_SPENDING_LIMIT();
CALL account_budget!GET_LINKED_RESOURCES();

-- Monitor budget usage
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.BUDGET_USAGE_HISTORY
ORDER BY USAGE_DATE DESC;
```

### Budgets vs Resource Monitors
| Feature | Resource Monitor | Budget |
|---------|-----------------|--------|
| Scope | Warehouses only | Warehouses + serverless + storage |
| Granularity | Account or warehouse | Custom groupings |
| Actions | Notify, suspend | Notify (email, webhook) |
| Serverless tracking | No | Yes |
| Storage tracking | No | Yes |

## Chargeback and Showback Models

### Showback (Visibility)
Show teams their consumption without direct billing — promotes cost awareness.

```sql
-- Showback report: credit usage by team (via tags)
SELECT
  t.TAG_VALUE AS team,
  'Compute' AS cost_type,
  SUM(wm.CREDITS_USED) AS credits,
  ROUND(credits * 3, 2) AS estimated_cost  -- adjust rate per edition
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY wm
JOIN SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES t
  ON wm.WAREHOUSE_NAME = t.OBJECT_NAME
  AND t.TAG_NAME = 'COST_CENTER'
  AND t.DOMAIN = 'WAREHOUSE'
WHERE wm.START_TIME >= DATE_TRUNC('MONTH', CURRENT_DATE())
GROUP BY t.TAG_VALUE
ORDER BY credits DESC;
```

### Chargeback (Billing)
Directly allocate costs to teams or business units based on actual usage.

```sql
-- Chargeback with blended rate (compute + storage + cloud services)
WITH compute_costs AS (
  SELECT
    t.TAG_VALUE AS cost_center,
    SUM(wm.CREDITS_USED) AS compute_credits
  FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY wm
  JOIN SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES t
    ON wm.WAREHOUSE_NAME = t.OBJECT_NAME AND t.TAG_NAME = 'COST_CENTER'
  WHERE wm.START_TIME >= DATE_TRUNC('MONTH', CURRENT_DATE())
  GROUP BY t.TAG_VALUE
),
storage_costs AS (
  SELECT
    t.TAG_VALUE AS cost_center,
    SUM(tsm.ACTIVE_BYTES) / POWER(1024, 4) AS active_tb
  FROM SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS tsm
  JOIN SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES t
    ON tsm.TABLE_NAME = t.OBJECT_NAME AND t.TAG_NAME = 'COST_CENTER'
  GROUP BY t.TAG_VALUE
)
SELECT
  c.cost_center,
  c.compute_credits,
  ROUND(c.compute_credits * 3.00, 2) AS compute_cost,
  s.active_tb,
  ROUND(s.active_tb * 23.00, 2) AS storage_cost,  -- adjust $/TB
  compute_cost + storage_cost AS total_cost
FROM compute_costs c
LEFT JOIN storage_costs s ON c.cost_center = s.cost_center
ORDER BY total_cost DESC;
```

### Implementation Best Practices
- Tag **all** warehouses, databases, and schemas with `cost_center`
- Use dedicated warehouses per team (simplifies attribution)
- Allocate shared costs (cloud services, storage) proportionally
- Publish monthly cost reports to stakeholders
- Set per-team budgets aligned to chargeback allocations

## Cost Optimization Strategies

### Top Cost-Saving Actions
1. **Right-size warehouses** — most are over-provisioned; start small, scale up
2. **Set auto-suspend** — every minute saved = credits saved
3. **Use resource monitors** — prevent runaway costs
4. **Separate workloads** — different sizes/policies per workload
5. **Kill long-running queries** — set `STATEMENT_TIMEOUT_IN_SECONDS`
6. **Use transient/temporary tables** — save on storage (no fail-safe)
7. **Optimize queries** — fewer scanned partitions = faster = cheaper
8. **Review Snowpipe frequency** — micro-batches have serverless overhead
9. **Monitor with ACCOUNT_USAGE** — identify waste regularly

### Cost Queries
```sql
-- Top 10 most expensive queries (last 30 days)
SELECT
  QUERY_ID,
  USER_NAME,
  WAREHOUSE_NAME,
  EXECUTION_TIME / 1000 AS exec_seconds,
  CREDITS_USED_CLOUD_SERVICES,
  QUERY_TEXT
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE START_TIME >= DATEADD('DAY', -30, CURRENT_TIMESTAMP())
ORDER BY EXECUTION_TIME DESC
LIMIT 10;

-- Idle warehouses (running but no queries)
SELECT
  WAREHOUSE_NAME,
  SUM(CREDITS_USED) AS total_credits,
  COUNT(DISTINCT QUERY_ID) AS query_count
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY wm
LEFT JOIN SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY qh
  ON wm.WAREHOUSE_NAME = qh.WAREHOUSE_NAME
  AND qh.START_TIME BETWEEN wm.START_TIME AND wm.END_TIME
WHERE wm.START_TIME >= DATEADD('DAY', -7, CURRENT_TIMESTAMP())
GROUP BY wm.WAREHOUSE_NAME
ORDER BY total_credits DESC;
```

## Query Acceleration Service

Offloads portions of eligible queries to shared serverless compute, improving performance without upsizing the warehouse (Enterprise+).

```sql
-- Enable Query Acceleration Service
ALTER WAREHOUSE analytics_wh SET
  ENABLE_QUERY_ACCELERATION = TRUE
  QUERY_ACCELERATION_MAX_SCALE_FACTOR = 4;  -- max 4x additional compute

-- Scale factor controls maximum serverless compute relative to warehouse size
-- Factor 0 = unlimited; Factor 8 = default max when enabled
-- Higher factor = more acceleration potential but higher cost ceiling

-- Check which queries would benefit
SELECT
  QUERY_ID,
  QUERY_TEXT,
  ELIGIBLE_QUERY_ACCELERATION_TIME / 1000 AS eligible_sec,
  UPPER_LIMIT_SCALE_FACTOR
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ACCELERATION_ELIGIBLE
WHERE START_TIME >= DATEADD('DAY', -7, CURRENT_TIMESTAMP())
  AND ELIGIBLE_QUERY_ACCELERATION_TIME > 0
ORDER BY ELIGIBLE_QUERY_ACCELERATION_TIME DESC;

-- Monitor QAS costs
SELECT
  DATE_TRUNC('DAY', START_TIME) AS day,
  WAREHOUSE_NAME,
  SUM(CREDITS_USED) AS qas_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ACCELERATION_HISTORY
WHERE START_TIME >= DATEADD('MONTH', -1, CURRENT_TIMESTAMP())
GROUP BY 1, 2
ORDER BY 1 DESC;
```

### When QAS Helps
- Queries scanning many micro-partitions with selective filters
- Queries with large sorts or aggregations on subsets of data
- Ad hoc / exploratory queries on large tables
- **Not helpful** for queries already running fast or fully utilizing the warehouse

## Dynamic Tables Cost Management

Dynamic tables auto-refresh incrementally, replacing manual task/stream pipelines.

```sql
-- Create dynamic table with target lag (how fresh data must be)
CREATE DYNAMIC TABLE customer_summary
  TARGET_LAG = '10 minutes'
  WAREHOUSE = ETL_WH
  AS
  SELECT customer_id, COUNT(*) AS order_count, SUM(amount) AS total_spend
  FROM orders
  GROUP BY customer_id;

-- Check refresh history and cost
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.DYNAMIC_TABLE_REFRESH_HISTORY
WHERE DYNAMIC_TABLE_NAME = 'CUSTOMER_SUMMARY'
ORDER BY REFRESH_START_TIME DESC;

-- Optimize cost: adjust target lag based on business needs
ALTER DYNAMIC TABLE customer_summary SET TARGET_LAG = '1 hour';  -- less frequent = cheaper

-- Suspend to stop refresh charges
ALTER DYNAMIC TABLE customer_summary SUSPEND;
ALTER DYNAMIC TABLE customer_summary RESUME;
```

### Dynamic Tables Cost Tips
- **Longer target lag = lower cost** — only refresh as frequently as business requires
- Use `DOWNSTREAM` target lag for tables consumed only by other dynamic tables
- Monitor `DYNAMIC_TABLE_REFRESH_HISTORY` for incremental vs full refresh (full = more expensive)
- Prefer incremental-friendly SQL patterns (avoid non-deterministic functions that force full refresh)

## Replication Cost Optimization

```sql
-- Monitor replication costs
SELECT
  DATABASE_NAME,
  SUM(CREDITS_USED) AS replication_credits,
  SUM(BYTES_TRANSFERRED) / POWER(1024, 3) AS gb_transferred
FROM SNOWFLAKE.ACCOUNT_USAGE.REPLICATION_USAGE_HISTORY
WHERE START_TIME >= DATEADD('MONTH', -1, CURRENT_TIMESTAMP())
GROUP BY DATABASE_NAME
ORDER BY replication_credits DESC;

-- Track database-level replication costs
SELECT
  DATABASE_NAME,
  DATE_TRUNC('DAY', START_TIME) AS day,
  SUM(CREDITS_USED) AS credits,
  SUM(BYTES_TRANSFERRED) / POWER(1024, 3) AS gb_transferred
FROM SNOWFLAKE.ACCOUNT_USAGE.REPLICATION_USAGE_HISTORY
WHERE START_TIME >= DATEADD('DAY', -30, CURRENT_TIMESTAMP())
GROUP BY 1, 2
ORDER BY 2 DESC, 3 DESC;
```

### Reducing Replication Costs
- **Replicate only what's needed** — select specific databases and schemas
- **Increase refresh interval** — less frequent replication = lower cost
- **Use transient tables** for staging data that doesn't need replication
- **Monitor secondary account storage** — replicated data incurs storage on both accounts
- **Same-region sharing** — use data sharing instead of replication when possible (zero cost)

## Cortex AI and ML Cost Management

Snowflake Cortex AI functions consume credits based on the model and token usage.

```sql
-- Monitor Cortex AI credit usage
SELECT
  DATE_TRUNC('DAY', START_TIME) AS day,
  SERVICE_TYPE,
  SUM(CREDITS_USED) AS credits
FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_DAILY_HISTORY
WHERE SERVICE_TYPE LIKE 'AI%' OR SERVICE_TYPE LIKE 'CORTEX%'
  AND START_TIME >= DATEADD('MONTH', -1, CURRENT_TIMESTAMP())
GROUP BY 1, 2
ORDER BY 1 DESC;
```

### Cortex Cost Tips
- **Choose the right model size** — smaller models (e.g., `snowflake-arctic-embed-s`) cost less than large ones
- **Batch inference** — process in bulk rather than row-by-row for better credit efficiency
- **Cache results** — store Cortex outputs in tables to avoid re-processing
- **Use COMPLETE/SUMMARIZE selectively** — apply AI functions to filtered/sampled data first
- **Monitor per-query costs** — check `QUERY_HISTORY` for credit usage of Cortex queries

## Spend Anomaly Detection

Proactively detect unexpected cost spikes before they become budget problems.

```sql
-- Daily spend trend with anomaly flag (simple z-score approach)
WITH daily_spend AS (
  SELECT
    DATE_TRUNC('DAY', START_TIME) AS day,
    SUM(CREDITS_USED) AS credits
  FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
  WHERE START_TIME >= DATEADD('DAY', -90, CURRENT_TIMESTAMP())
  GROUP BY 1
),
stats AS (
  SELECT
    AVG(credits) AS avg_credits,
    STDDEV(credits) AS stddev_credits
  FROM daily_spend
  WHERE day < DATEADD('DAY', -7, CURRENT_DATE())  -- baseline excludes recent week
)
SELECT
  d.day,
  d.credits,
  ROUND(s.avg_credits, 1) AS baseline_avg,
  ROUND((d.credits - s.avg_credits) / NULLIF(s.stddev_credits, 0), 2) AS z_score,
  CASE WHEN z_score > 2 THEN 'ANOMALY' ELSE 'NORMAL' END AS status
FROM daily_spend d, stats s
ORDER BY d.day DESC;

-- Snowflake built-in: Budget alerts and notifications
-- Configure in Snowsight under Admin → Cost Management → Budgets
-- Supports email notifications and webhook integrations for real-time alerts
```

### Automation Patterns
- Set up **Snowflake Alerts** (SQL-based) to notify on spend thresholds
- Use **tasks** to run daily spend checks and write to a monitoring table
- Integrate with Slack/PagerDuty via **external functions** or **webhooks**
- Use **budgets with notifications** for automated threshold alerts

```sql
-- Alert for daily spend exceeding threshold
CREATE ALERT high_spend_alert
  WAREHOUSE = ADMIN_WH
  SCHEDULE = 'USING CRON 0 8 * * * UTC'
  IF (EXISTS (
    SELECT 1
    FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
    WHERE START_TIME >= DATEADD('DAY', -1, CURRENT_TIMESTAMP())
    GROUP BY 1
    HAVING SUM(CREDITS_USED) > 500  -- threshold
  ))
  THEN
    CALL SYSTEM$SEND_EMAIL(
      'cost_alerts',
      'team@company.com',
      'High Snowflake Spend Alert',
      'Daily credit usage exceeded 500 credits.'
    );

ALTER ALERT high_spend_alert RESUME;
```

## Object Tagging for Cost Centers

```sql
-- Tag warehouses and databases for cost allocation
CREATE TAG cost_center;

ALTER WAREHOUSE analytics_wh SET TAG cost_center = 'analytics-team';
ALTER WAREHOUSE etl_wh SET TAG cost_center = 'data-engineering';
ALTER DATABASE marketing_db SET TAG cost_center = 'marketing';

-- Query cost by tag
SELECT
  t.TAG_VALUE AS cost_center,
  SUM(wm.CREDITS_USED) AS total_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY wm
JOIN SNOWFLAKE.ACCOUNT_USAGE.TAG_REFERENCES t
  ON wm.WAREHOUSE_NAME = t.OBJECT_NAME
  AND t.TAG_NAME = 'COST_CENTER'
WHERE wm.START_TIME >= DATEADD('MONTH', -1, CURRENT_TIMESTAMP())
GROUP BY t.TAG_VALUE
ORDER BY total_credits DESC;
```

## DevOps and Change Management

### Zero-Copy Cloning for Dev/Test
```sql
-- Instant dev environment from production (no storage cost until data changes)
CREATE DATABASE dev_db CLONE prod_db;
CREATE SCHEMA test_schema CLONE prod_schema;

-- Run tests against clone, then drop
DROP DATABASE dev_db;
```

### Database Change Management
```sql
-- Use tools like:
-- - Flyway, Liquibase (SQL migration files)
-- - dbt (models + transformations)
-- - Terraform Snowflake Provider (infrastructure as code)
-- - SchemaChange (Snowflake-specific migration tool)

-- Terraform example:
-- resource "snowflake_warehouse" "etl" {
--   name           = "ETL_WH"
--   warehouse_size = "large"
--   auto_suspend   = 60
-- }
```

### CI/CD Patterns
1. Developer creates branch with migration scripts
2. CI clones production database for testing
3. Migrations run against clone
4. Tests validate
5. PR merged → migrations applied to production
6. Clone dropped
