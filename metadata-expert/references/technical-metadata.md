# Technical Metadata
## Chapter 5: Schemas, Data Profiles, Lineage, Storage/Format Attributes

---

## What Is Technical Metadata?

Technical metadata describes the **structural, physical, and computational properties** of data assets. It answers:
- *How is this data organized and typed?*
- *Where does it live and in what format?*
- *What are its statistical properties?*
- *How does it flow between systems?*

Technical metadata is largely **automatable** — scanners, profilers, and crawlers generate most of it. The challenge is not capture but **integration and maintenance**: keeping technical metadata synchronized with rapidly changing data infrastructure.

---

## Schema Metadata

### Definition
Schema metadata describes the **logical structure** of a data asset — its fields, types, constraints, and relationships.

### Schema Metadata Elements

**Table/Dataset Level**
| Attribute | Example |
|-----------|---------|
| Name | `fact_orders` |
| Schema/namespace | `dw_core` |
| Description | "One row per customer order line item" |
| Row count (profile) | 4,821,033 |
| Size | 2.3 GB |
| Partitioned by | `order_date` (monthly) |
| Created | 2022-03-15 |
| Last modified | 2024-06-30 |
| Owner | Sales Engineering team |
| Access classification | Internal |

**Column Level**
| Attribute | Example |
|-----------|---------|
| Name | `customer_id` |
| Data type | INTEGER |
| Nullable | NOT NULL |
| Primary key | No (FK to dim_customer) |
| Default value | None |
| Description | "Surrogate key for the customer dimension" |
| Business term link | "Customer" |
| Sensitivity | PII-linked (indirect) |

### Schema Evolution Tracking
Technical metadata must track **schema changes over time**:

```
fact_orders schema history:
─────────────────────────────
v1 (2022-03-15): customer_id, product_id, order_date, amount
v2 (2022-11-01): + discount_pct (added)
v3 (2023-07-15): amount → gross_amount, net_amount (split)
v4 (2024-01-01): - deprecated_flag (removed)
```

Schema history enables:
- **Breaking change detection**: What downstream consumers are affected?
- **Time travel queries**: What was the schema when this report ran?
- **Audit compliance**: When was this column added and by whom?

---

## Data Profiling Metadata

### Purpose
Data profiles capture **statistical properties** of data, enabling:
- Quality assessment (completeness, uniqueness, validity)
- Query optimization (cardinality estimates, value distributions)
- Anomaly detection (sudden shifts in null rates or value ranges)
- Discovery (understand an unfamiliar dataset without reading every row)

### Profile Statistics

**Column-Level Statistics**
| Statistic | Description | Example |
|-----------|-------------|---------|
| **Row count** | Total records | 4,821,033 |
| **Null count / null %** | Missing values | 482 nulls (0.01%) |
| **Distinct count** | Cardinality | 892,441 distinct values |
| **Min / Max** | Value range | 2018-01-01 to 2024-06-30 |
| **Mean / Median** | Central tendency | $127.43 / $89.00 |
| **Std deviation** | Spread | $95.12 |
| **Top N values** | Most frequent | "USD": 94.2%, "EUR": 4.1%, "GBP": 1.7% |
| **Pattern distribution** | Format adherence | 99.8% match `###-##-####` |
| **Referential integrity** | FK validity | 99.97% of customer_ids exist in dim_customer |

**Dataset-Level Statistics**
| Statistic | Description |
|-----------|-------------|
| Total row count | Number of records |
| Duplicate row rate | % of exact duplicate rows |
| Table freshness | Age of most recent record |
| Column completeness score | Average % non-null across all columns |

### Profile Freshness
Profile statistics age — they reflect the data at the time of profiling. Good practice:
- Schedule profiling to run after major loads
- Store profile history to detect drift
- Alert when statistics shift beyond thresholds (e.g., null rate doubles)

---

## Technical Lineage

### Definition
Technical lineage traces the **physical movement and transformation** of data from source to target at the system and dataset level.

### Lineage Levels

**System Lineage** (coarsest)
```
CRM System → ETL Pipeline → Data Warehouse → BI Tool → Dashboard
```

**Dataset Lineage** (mid-level)
```
salesforce.Opportunity → staging.stg_opportunity → dw_core.fact_orders → rpt_sales_summary
```

**Column Lineage** (finest)
```
salesforce.Opportunity.Amount
    → [transformation: convert to USD using fx_rates]
    → staging.stg_opportunity.amount_usd
    → [transformation: SUM by order_id]
    → dw_core.fact_orders.gross_amount
    → [transformation: SUM filtered to current_quarter]
    → rpt_sales_summary.q_revenue
```

### Lineage Capture Methods

| Method | How | Pros | Cons |
|--------|-----|------|------|
| **SQL parsing** | Parse SQL DDL/DML to extract column references | Detailed, accurate | Complex SQL hard to parse |
| **API tracing** | Instrument ETL/pipeline APIs | Real-time, event-driven | Requires instrumentation |
| **Log analysis** | Parse query logs and access logs | Non-invasive | Incomplete for complex transforms |
| **Manual documentation** | Humans document lineage | Can capture non-technical flows | Expensive, drifts out of sync |
| **OpenLineage** | Open standard for lineage events from pipelines | Interoperable, automated | Requires pipeline adoption |

### Lineage Use Cases

| Use Case | How Lineage Helps |
|----------|-------------------|
| **Impact analysis** | "If I change this table, what downstream reports break?" |
| **Root cause analysis** | "This KPI is wrong — trace back to find the bad source data" |
| **Regulatory compliance** | "Show me every system that touches GDPR-regulated data" |
| **Data migration** | "Map all dependencies before decommissioning a legacy system" |
| **Trust building** | "Where did this number come from?" answered in seconds |

---

## Storage and Format Metadata

### File Format Metadata
| Attribute | Examples |
|-----------|---------|
| **Format** | Parquet, ORC, Avro, CSV, JSON, Delta, Iceberg |
| **Compression codec** | Snappy, GZIP, LZ4, ZSTD, uncompressed |
| **Encoding** | UTF-8, Latin-1, Base64 |
| **File count** | 1,024 Parquet files |
| **Average file size** | 128 MB |
| **Partitioning scheme** | year=2024/month=06/day=30 |

### Storage Location Metadata
| Attribute | Example |
|-----------|---------|
| **Storage system** | AWS S3, Azure ADLS, GCS, HDFS, on-prem NFS |
| **Path / URI** | `s3://data-lake-prod/dw/fact_orders/` |
| **Region** | us-east-1 |
| **Tier** | Hot / Warm / Cold / Archive |
| **Encryption** | AES-256, SSE-KMS key ARN |
| **Replication** | 3x cross-AZ |
| **Lifecycle policy** | Move to Glacier after 365 days |

### API and Service Metadata
| Attribute | Example |
|-----------|---------|
| **Endpoint** | `https://api.example.com/v2/orders` |
| **Protocol** | REST, GraphQL, gRPC |
| **Authentication** | OAuth 2.0, API key |
| **Rate limits** | 1000 req/min per client |
| **Schema** | OpenAPI 3.0 spec location |
| **Versioning** | v2 (v1 deprecated 2024-03-01) |
| **SLA** | 99.9% uptime, < 200ms p99 |

---

## Technical Metadata in the Catalog

### What Gets Auto-Discovered
Modern data catalog crawlers can automatically capture:
- Table and column names, data types, constraints
- Row counts, null rates, distinct counts
- Storage location, size, format
- Basic referential integrity stats

### What Still Requires Human Input
- Column descriptions (beyond names)
- Business term linkage
- Sensitivity classification
- Transformation business logic
- Cross-system lineage (beyond single platform)

### Technical Metadata Synchronization
Technical metadata goes stale quickly as schemas evolve. Synchronization strategies:
- **Event-driven**: DDL change events trigger immediate metadata updates
- **Scheduled crawls**: Periodic re-scans (hourly, daily)
- **On-demand**: Trigger scan on data access or pipeline completion
- **Hybrid**: Events for schema changes, scheduled for statistics

### Metadata Completeness by Asset Type

| Asset Type | Auto-captured | Human-required |
|------------|---------------|----------------|
| Database table | Schema, stats, size | Description, sensitivity, business term |
| S3 path | Location, size, format | Content meaning, ownership, classification |
| Kafka topic | Topic name, partitions | Schema meaning, producer/consumer docs |
| API endpoint | URL, HTTP methods | Business purpose, field semantics |
| ML model | Version, framework | Training data, intended use, bias assessment |
