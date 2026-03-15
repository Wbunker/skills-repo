# Design Considerations for Your Data Lake
## Chapter 3: Infrastructure Setup, Data Lake Zones, Governance, Cost Management

---

## Setting Up the Cloud Data Lake Infrastructure

Gopalan structures the setup lifecycle as four phases:

### Phase 1: Identify Your Goals

Before selecting tools or writing code, define:

**Business outcomes:**
- What decisions will this data lake enable?
- Which use cases have immediate business value?
- Who are the consumers and what do they need?

**Technical goals:**
- What data sources must be onboarded and at what latency?
- What query SLAs are required?
- What governance and compliance requirements apply?

**Success metrics:**
- How will you know the data lake is working? (query latency, data freshness, user adoption, cost per TB)

### Phase 2: Plan Your Architecture and Deliverables

Key planning decisions:

| Decision | Options | Considerations |
|----------|---------|---------------|
| **Cloud provider** | AWS, Azure, GCP | Existing footprint, team skills, services available |
| **Storage service** | S3, ADLS Gen2, GCS | Provider choice; all are roughly equivalent |
| **Table format** | Iceberg, Delta, Hudi, or none | Workload type, engine ecosystem |
| **Compute engine** | Spark, Athena, Trino, Databricks | Workload type, SQL vs. ML vs. streaming |
| **Orchestration** | Airflow, Step Functions, Dagster, dbt | Team familiarity, complexity |
| **Catalog** | AWS Glue, Hive Metastore, Apache Atlas, Unity | Engine compatibility |
| **Zone structure** | 3-zone, 4-zone | Complexity of transformation pipeline |

**Deliverables to plan:**
- Zone naming conventions and folder structure
- IAM and access control model
- Ingestion pipeline architecture per source type
- Tagging and cost allocation strategy
- Data governance framework (even if basic initially)

### Phase 3: Implement the Cloud Data Lake

Implementation sequence:

```
1. Provision object storage
   └── S3 buckets / ADLS containers / GCS buckets per zone
   └── Enable versioning and logging
   └── Apply lifecycle policies

2. Establish IAM and access control
   └── Service accounts for pipelines
   └── Role-based access per zone
   └── Encryption at rest and in transit

3. Implement ingestion pipelines
   └── Batch: Spark/Glue ETL jobs, scheduled
   └── CDC: Debezium → Kafka → lake
   └── Streaming: Kafka/Kinesis → Flink/Spark Streaming

4. Register metadata
   └── Configure catalog (Glue, Hive Metastore)
   └── Enable crawlers for auto-discovery
   └── Add initial business context

5. Validate and test
   └── Query data in each zone
   └── Verify access controls
   └── Test pipeline failure and recovery
```

### Phase 4: Release and Operationalize

**Go-live checklist:**
- Monitoring and alerting configured (pipeline failures, SLA breaches)
- On-call runbook documented
- Data quality checks in place
- Cost dashboards active
- Consumer onboarding guide written

**Ongoing operations:**
- Regular compaction jobs (for table-format tables)
- Schema evolution management
- Cost review cadence
- Access review and certification

---

## Organizing Data in Your Data Lake

### A Day in the Life of Data

Gopalan traces data through its lifecycle to illustrate why zones matter:

```
Source System (e.g., CRM)
       │
       ▼ [ingestion — raw copy]
Raw / Landing Zone
       │
       ▼ [quality checks, schema validation]
Staging Zone
       │
       ▼ [transform, join, aggregate, certify]
Curated / Gold Zone
       │
       ▼ [serve to consumers]
Analysts / BI Tools / ML Models / APIs
```

### Data Lake Zones

#### Zone 1: Raw / Landing Zone

**Purpose**: Immutable archive of data exactly as received from source systems.

**Characteristics:**
- **Append-only**: Never modified; source of truth for reprocessing
- **Original format**: Data stored as-is (JSON from API, CSV from file transfer, Avro from Kafka)
- **No transformation**: No cleaning, joining, or business logic applied
- **Full history**: All versions retained

**Access**: Limited — typically only ingestion pipelines write; data engineers read for debugging.

**Example path structure:**
```
s3://my-data-lake/raw/
  salesforce/
    opportunity/
      year=2024/month=06/day=30/
        sf_opportunity_20240630_143022.json
  kafka/
    orders-topic/
      year=2024/month=06/day=30/hour=14/
        part-00000.avro
```

#### Zone 2: Staging / Silver Zone

**Purpose**: Cleaned, standardized, and validated data. Data is usable but not yet aggregated for specific use cases.

**Characteristics:**
- **Schema enforced**: All data conforms to defined schemas
- **Deduplicated**: Duplicate records removed
- **PII masked or tokenized**: Sensitive data protected
- **Joined to reference data**: IDs resolved to standardized keys
- **Stored as Parquet or open table format**: Optimized for query

**Access**: Data engineers, data scientists, and ML engineers.

**Example:**
```
s3://my-data-lake/staging/
  dim_customer/
    (Parquet / Iceberg table, partitioned by region)
  fact_orders/
    (Iceberg table, partitioned by order_date)
```

#### Zone 3: Curated / Gold Zone

**Purpose**: Business-ready data products certified for consumption by analysts and applications.

**Characteristics:**
- **Aggregated and summarized**: Pre-computed for BI performance
- **Domain-specific**: Organized by business domain (sales, finance, marketing)
- **Certified**: Data steward has validated and approved
- **Documented**: Linked to business glossary terms
- **Versioned**: Breaking changes create new versions

**Access**: Broad — analysts, BI tools, applications, external consumers.

**Example:**
```
s3://my-data-lake/curated/
  sales/
    monthly_revenue_summary/   (certified by Finance steward)
    active_customer_segments/  (certified by Marketing steward)
  finance/
    gl_journal_entries/        (certified by CFO)
```

#### Zone 4: Work Zone (User Workspace)

**Purpose**: Exploration, experimentation, and data science projects. Not subject to production SLAs but governed enough to prevent sensitive data leakage.

*Term from Gorelik ("The Enterprise Big Data Lake"): "Work Zone" is the preferred enterprise term; Gopalan calls this a "Sandbox."*

**Characteristics:**
- **User-managed**: Data scientists and analysts own their workspace data and pipelines
- **Light governance**: No quality or freshness SLAs; primary control is no unmasked PII/PHI
- **Time-bounded**: Storage quotas enforced per user/team; data expires after 30–90 days unless renewed
- **Not promoted automatically**: Results require explicit promotion to the gold zone before serving consumers

**User-to-zone mapping (Gorelik):**
- Business analysts → Gold zone (read only)
- Data scientists → Work zone (read/write) + Gold/Staging (read)
- Data engineers → All zones (read/write)

#### Zone 5: Sensitive Zone (High-Risk Data)

**Purpose**: Physically separate storage for data containing PII, PHI, PCI, trade secrets, or other data requiring the strictest access controls.

*This zone is distinct from the others: it is not about data maturity but about data sensitivity. Introduced by Gorelik as a dedicated zone rather than a classification tag.*

**Why physical separation matters:**
- Prevents accidental access through misconfigured permissions on shared buckets
- Enables separate encryption key management (customer-managed keys)
- Narrows audit scope: audit everything touching this zone, not the entire lake
- Satisfies some regulatory requirements for physical data separation

**Controls required:**
- Explicit role-based access with MFA for all human access
- All access logged and audited (full query audit trail)
- Column-level masking for analytic users who need aggregated access
- Data minimization enforced: only necessary PII stored, with defined retention limits
- Separate bucket/container from all other zones

**Access pattern:**
```
Sensitive zone → de-identified/aggregated → Gold zone (for analytics)
                 derivative dataset
                 (engineer creates masked view;
                  original PII stays in sensitive zone only)
```

**Zone summary (combined model):**

| Zone | Governance | SLAs | Primary Writers | Primary Readers |
|------|-----------|------|----------------|----------------|
| Raw/Landing | Minimal | None | Ingestion pipelines | Data engineers |
| Staging/Silver | Medium | Schema | Transform pipelines | Engineers, scientists |
| Gold/Curated | Strong | Quality + freshness | Data engineers | Analysts, BI, apps |
| Work | Light | Project-specific | Analysts, scientists | Owner + team |
| Sensitive | Maximum | Strict + audited | Controlled pipelines | Privileged roles only |

### Organization Mechanisms

**Folder / path conventions:**

| Level | Pattern | Example |
|-------|---------|---------|
| Zone | `/zone/` | `/raw/`, `/staging/`, `/curated/` |
| Source or domain | `/zone/source/` | `/raw/salesforce/`, `/curated/sales/` |
| Entity | `/zone/source/entity/` | `/raw/salesforce/opportunity/` |
| Partitions | `year=YYYY/month=MM/day=DD/` | `year=2024/month=06/day=30/` |

**Naming standards:**
- Lowercase with underscores (snake_case)
- No spaces or special characters in paths
- Dates in ISO format (YYYY-MM-DD)
- Version suffixes for breaking schema changes: `customer_orders_v2/`

**Tags and metadata:**
- Source system tag on every object
- Data classification tag (public, internal, confidential, restricted)
- Owner tag (team or domain)
- Cost allocation tag (project, department)

---

## Introduction to Data Governance

### Why Governance Cannot Be an Afterthought

A data lake without governance becomes a **data swamp**: data accumulates, no one knows what it means, quality degrades, and users stop trusting it. Governance must be built in from the beginning.

### Actors Involved in Data Governance

| Role | Responsibility |
|------|---------------|
| **Data Owner** | Business executive accountable for data quality and appropriate use |
| **Data Steward** | Day-to-day management of data definitions, quality, and access requests |
| **Data Engineer** | Implements pipelines and technical controls; enforces schemas |
| **Data Consumer** | Analyst, scientist, or application using data; responsible for appropriate use |
| **Platform/Infra Team** | Provides the tooling and infrastructure for governance |

### Data Classification

Classify all data assets by sensitivity:

| Classification | Description | Examples | Controls |
|---------------|-------------|----------|---------|
| **Public** | No sensitivity; freely shareable | Published reports, open datasets | No access restriction |
| **Internal** | Business-sensitive; employees only | Sales forecasts, operational data | Authenticated access |
| **Confidential** | Sensitive; restricted to need-to-know | Financial data, PII-adjacent | Role-based + logging |
| **Restricted** | Highest sensitivity; strictly controlled | PII, PHI, PCI, trade secrets | MFA + audit + masking |

### Metadata Management, Data Catalog, and Data Sharing

**Metadata management goals in a data lake:**
- Every table/dataset has an owner, description, and classification
- Column-level documentation for curated zone tables
- Lineage tracked from source to curated layer
- Business glossary terms linked to physical columns

**Data catalog options:**

| Catalog | Best For |
|---------|---------|
| **AWS Glue Data Catalog** | AWS-native; integrates with Athena, EMR, Glue ETL |
| **Apache Atlas** | Open-source; rich lineage and governance; complex to operate |
| **Unity Catalog (Databricks)** | Databricks-centric; column-level governance |
| **Apache Polaris** | Open-source Iceberg catalog; emerging |
| **DataHub** | Open-source; multi-platform; strong lineage |
| **Alation / Atlan / Collibra** | Commercial; business-friendly UI; enterprise governance |

**Data sharing** — making curated data available to external consumers:
- AWS Lake Formation + Glue sharing
- Delta Sharing (open protocol for sharing Delta tables)
- Iceberg REST catalog (standardized sharing API)
- Snowflake Data Sharing

### Data Access Management

**Principle of least privilege**: Grant the minimum access needed for the specific role.

**Access patterns:**

```
IAM Roles / Service Principals:
  └── ingestion-pipeline-role → write to raw only
  └── transform-pipeline-role → read raw, write staging
  └── analyst-role → read staging + curated
  └── data-scientist-role → read all zones, write sandbox
  └── admin-role → full access (tightly controlled)
```

**Column-level security**: Mask PII columns from users without clearance using:
- AWS Lake Formation column masking
- Databricks Unity Catalog row/column filters
- View-based access control in Athena/Trino

### Data Quality and Observability

Data quality in a data lake requires explicit enforcement — there is no database engine enforcing constraints automatically.

**Quality dimensions to measure:**

| Dimension | Question | How to Measure |
|-----------|---------|---------------|
| **Completeness** | Are required fields populated? | % non-null on mandatory columns |
| **Accuracy** | Does the data reflect reality? | Cross-system reconciliation, business rule checks |
| **Consistency** | Is data consistent across sources? | Referential integrity checks, dedup rate |
| **Timeliness** | Is the data fresh enough? | Time since last update vs. SLA |
| **Validity** | Does data conform to expected formats/ranges? | Pattern matching, range checks |
| **Uniqueness** | Are there unexpected duplicates? | Duplicate row rate |

**Data observability tools:**
- Monte Carlo, Acceldata, Bigeye, Soda — commercial observability platforms
- Great Expectations — open-source data quality framework
- dbt tests — quality checks integrated into transformation pipelines
- Custom Spark/SQL quality jobs

---

## Manage Data Lake Costs

### Demystifying Data Lake Costs on the Cloud

Cloud data lake costs have three components:

| Cost Component | Driver | Example (AWS) |
|---------------|--------|---------------|
| **Storage** | GB stored × storage tier | $0.023/GB/month (S3 Standard) |
| **Compute** | Instance-hours or query scanned | $0.005/GB scanned (Athena) |
| **Data transfer** | Egress across regions or to internet | $0.09/GB out to internet |
| **API requests** | PUT/GET/LIST calls on object storage | $0.005/1000 PUT requests |

### Data Lake Cost Strategy

**Storage cost optimizations:**

1. **Lifecycle policies** — automatically transition data to cheaper tiers:
   ```
   Raw zone:    30 days → S3-IA → 90 days → Glacier
   Staging:     90 days → S3-IA → 365 days → Glacier
   Curated:     365 days → S3-IA (query latency acceptable)
   ```

2. **Compression** — always compress data:
   - Parquet with Snappy: 75–90% size reduction vs. uncompressed CSV
   - Avro with GZIP: good for row-oriented streaming data

3. **Right file sizing** — avoid small files (high API cost, poor query performance):
   - Target 128MB–1GB per file for Parquet/Iceberg
   - Compact small files with scheduled compaction jobs

4. **Deduplication** — don't store duplicate data; raw zone is the only copy of raw

**Compute cost optimizations:**

1. **Partition pruning** — well-partitioned tables mean queries scan less data
2. **Columnar formats** — Parquet/ORC only read queried columns; CSV reads everything
3. **Caching** — cache frequently-queried data in memory or faster storage tier
4. **Cluster autoscaling** — don't run a large Spark cluster 24/7; scale to zero when idle
5. **Spot/preemptible instances** — 60–90% cheaper for fault-tolerant batch workloads
6. **Query result caching** — Athena, BigQuery cache results; repeated queries are free

**Cost allocation and visibility:**

- Tag all resources with project, team, and environment tags
- Use AWS Cost Explorer / Azure Cost Management / GCP Billing for per-tag breakdown
- Set budget alerts before spending surprises appear on the invoice
- Regularly review unused or stale data (zero-access data older than 180 days is a candidate for archival or deletion)

### Cost vs. Performance Tradeoffs

| Decision | Cheaper | Faster |
|----------|---------|--------|
| File size | Fewer large files | Moderate-size files for parallel reads |
| Compression | GZIP (smaller) | Snappy (faster decompression) |
| Storage tier | Glacier | S3 Standard |
| Compute | Spot instances | On-demand |
| Partitioning | Fewer, coarser partitions | Fine-grained partitions matching query patterns |

The right balance depends on SLA requirements and budget constraints — Gopalan advocates measuring before optimizing.
