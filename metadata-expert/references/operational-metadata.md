# Operational Metadata
## Chapter 6: Process Metadata, Pipeline Lineage, Job Execution, Audit Logs

---

## What Is Operational Metadata?

Operational metadata captures the **history of how data was produced and used** — the who, when, what happened, and how well it worked. It answers:
- *When was this data last updated?*
- *Did the pipeline run successfully?*
- *Who accessed this data and when?*
- *Has data volume or quality changed since last run?*
- *What SLAs were met or breached?*

Operational metadata is generated **continuously** as pipelines run, users access data, and quality checks execute. It is time-series in nature and essential for **data observability** and **trust**.

---

## Process and Pipeline Metadata

### Pipeline Metadata Elements

**Pipeline / Job Definition Level**
| Attribute | Description | Example |
|-----------|-------------|---------|
| Pipeline ID | Unique identifier | `pipeline_orders_daily_load` |
| Description | What the pipeline does | "Loads daily orders from Salesforce to DW" |
| Owner | Responsible team | Data Engineering - Sales squad |
| Schedule | Cadence | Daily at 02:00 UTC |
| Source system | Where data comes from | Salesforce CRM |
| Target system | Where data goes | `dw_core.fact_orders` |
| Technology | Tool/framework | Apache Airflow, dbt, Spark |
| SLA | Expected completion | Must complete by 06:00 UTC |
| Dependencies | Upstream prerequisites | Salesforce export must be available |
| Notification | Alert contacts | de-alerts@company.com |

**Pipeline Run / Execution Level**
| Attribute | Description | Example |
|-----------|-------------|---------|
| Run ID | Unique run identifier | `run_20240630_020005` |
| Start time | When execution began | 2024-06-30 02:00:05 UTC |
| End time | When execution completed | 2024-06-30 03:47:22 UTC |
| Duration | Total runtime | 1h 47m 17s |
| Status | Outcome | SUCCESS / FAILED / PARTIAL / SKIPPED |
| Records read | Source volume | 48,291 records |
| Records written | Target volume | 48,291 records |
| Records rejected | Validation failures | 3 records (0.006%) |
| Bytes processed | Data volume | 2.1 GB |
| Error message | If failed | "Connection timeout to Salesforce API" |
| Retry count | Automatic retries | 0 (succeeded first attempt) |
| Triggered by | Manual or scheduled | scheduled (cron) |

### Job/Task Metadata
For orchestrated pipelines, metadata is captured at each task within the DAG:

```
DAG: orders_daily_load
│
├── Task: extract_from_salesforce
│   ├── Start: 02:00:05 | End: 02:18:44 | Status: SUCCESS
│   ├── Records extracted: 48,291
│   └── API calls: 97 (500 records/page)
│
├── Task: validate_schema
│   ├── Start: 02:18:45 | End: 02:19:02 | Status: SUCCESS
│   └── Validation rules passed: 12/12
│
├── Task: transform_to_dw_format
│   ├── Start: 02:19:03 | End: 03:44:55 | Status: SUCCESS
│   ├── Input records: 48,291 | Output records: 48,288
│   └── Rejected: 3 (currency conversion failed)
│
└── Task: load_to_warehouse
    ├── Start: 03:44:56 | End: 03:47:22 | Status: SUCCESS
    └── Records inserted: 48,288 | Records updated: 0
```

---

## Data Freshness and SLA Metadata

### Freshness Metadata
| Attribute | Description | Why It Matters |
|-----------|-------------|----------------|
| **Last successful run** | When the last pipeline completed successfully | Is this data current? |
| **Last record timestamp** | Timestamp of the most recent data record | How old is the newest data? |
| **Expected update frequency** | How often data should refresh | Daily, hourly, real-time |
| **Staleness threshold** | When to alert that data is too old | Alert if no refresh in 26 hours |
| **Current staleness** | How long since last successful update | 3h 22m |

### SLA Tracking
```
Pipeline: fact_orders_daily_load
─────────────────────────────────
SLA target:    Completed by 06:00 UTC
Measurement:   Last 30 runs

Run history (last 7 days):
  2024-06-24: 03:47 ✓ (on time)
  2024-06-25: 04:12 ✓ (on time)
  2024-06-26: 07:23 ✗ (SLA breach — upstream delay)
  2024-06-27: 03:55 ✓ (on time)
  2024-06-28: 03:41 ✓ (on time)
  2024-06-29: FAILED ✗ (job failure, manual rerun 11:34)
  2024-06-30: 03:47 ✓ (on time)

30-day SLA attainment: 93.3% (28/30 runs on time)
```

---

## Data Observability Metadata

Data observability extends operational metadata to enable **proactive detection** of data problems before they reach consumers.

### The Five Pillars of Data Observability

| Pillar | What It Tracks | Example Anomaly |
|--------|---------------|-----------------|
| **Freshness** | When data was last updated | Table not updated in 36 hours (expected: daily) |
| **Volume** | How much data arrives each run | Orders table grew by 0 rows (expected: ~50K) |
| **Schema** | Structure of the data | New column appeared; column was deleted |
| **Distribution** | Statistical properties of values | Null rate on `email` jumped from 2% to 45% |
| **Lineage** | Dependencies and data flow | Upstream source not updated; downstream impacted |

### Observability Metadata Schema

```
data_quality_event:
  asset_id:         "dw_core.fact_orders"
  run_id:           "run_20240630_020005"
  check_name:       "volume_check"
  check_type:       "anomaly_detection"
  expected_range:   [40000, 60000]
  actual_value:     0
  status:           "FAILED"
  severity:         "CRITICAL"
  detected_at:      "2024-06-30T03:48:00Z"
  alert_sent_to:    ["de-alerts@company.com", "pagerduty"]
  resolution:       "Salesforce API was down; backfill completed 2024-06-30T11:34"
```

---

## Audit and Access Metadata

### Why Audit Metadata Matters
- **Regulatory compliance**: GDPR requires knowing who accessed personal data and when
- **Security**: Detect unauthorized access patterns
- **Accountability**: Trace who ran a query that caused a production incident
- **Usage analytics**: Understand which data assets are actually used

### Access Log Metadata
| Attribute | Example |
|-----------|---------|
| User/service | `analyst_jane@company.com` |
| Asset accessed | `dw_core.fact_orders` |
| Access type | SELECT query |
| Timestamp | 2024-06-30 09:14:22 UTC |
| Query | `SELECT * FROM fact_orders WHERE order_date > '2024-06-01'` |
| Rows returned | 142,840 |
| Duration | 2.3 seconds |
| IP / endpoint | 10.0.4.52 |
| Application | Tableau Desktop v2024.1 |
| Data classification touched | Internal (no PII columns selected) |

### Data Access Patterns
Aggregate access metadata reveals:
- **Hot assets**: Which tables are queried most frequently?
- **Stale assets**: What tables haven't been accessed in 180+ days? (candidates for deprecation)
- **Access by role**: Who queries which domains? (supports stewardship assignment)
- **Query efficiency**: Which users run the most expensive queries? (training opportunity)

---

## Process Lineage

Process lineage connects **business processes** (not just technical pipelines) to data assets.

### Business Process Lineage Example
```
Business Process: Monthly Revenue Close
│
├── Step 1: Sales team confirms pipeline in Salesforce [Day 1-3]
│   └── Produces: Salesforce.Opportunity (Status=Closed Won)
│
├── Step 2: ETL loads to DW [Day 3, 02:00 UTC]
│   └── Produces: dw_core.fact_orders (daily load)
│
├── Step 3: Finance runs adjustments in ERP [Day 4-7]
│   └── Produces: erp_prod.revenue_adjustments
│
├── Step 4: Revenue reconciliation job runs [Day 8]
│   └── Consumes: fact_orders + revenue_adjustments
│   └── Produces: rpt_revenue_monthly (certified)
│
└── Step 5: CFO approves and publishes to Board deck [Day 9]
    └── Consumes: rpt_revenue_monthly
    └── Produces: Board_Revenue_Report_YYYYMM.xlsx
```

This level of lineage is typically maintained manually but is critical for:
- Understanding the true origin of reported numbers
- Audit trails for financial reporting
- Impact assessment for process changes

---

## Operational Metadata in the Catalog

### What to Surface in the Catalog

For each data asset, operational metadata enables a **"health card"**:

```
fact_orders [dw_core]
─────────────────────────────────────────────────────
Last updated:    2024-06-30 03:47 UTC  ✓ Fresh
Rows:            4,821,033 (+48,288 from yesterday)
Pipeline:        orders_daily_load     ✓ Success
SLA status:      93.3% (30-day)        ⚠ Below 95% target
Quality score:   98.7%                 ✓ Good
Accessed by:     142 users in 30 days  ↑ (was 118)
Certified by:    Finance Data Steward  ✓ 2024-06-01
```

### Retention for Operational Metadata

| Metadata Type | Recommended Retention |
|---------------|----------------------|
| Pipeline run history | 2 years (longer for regulated industries) |
| Column statistics / profiles | 1 year (to detect drift trends) |
| Access logs (non-PII assets) | 90 days |
| Access logs (PII assets) | Per regulatory requirement (often 3–7 years) |
| Quality check results | 1 year |
| SLA measurements | 2 years |
